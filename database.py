"""
database.py  —  VetSync Pro  |  Supabase backend
"""
import hashlib
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os


_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_BASE_DIR, ".env"))

from supabase import create_client

_url = os.getenv("SUPABASE_URL")
_key = os.getenv("SUPABASE_KEY")
supabase = create_client(_url, _key)


def init_db():
    pass


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


class PhoneAlreadyExistsError(Exception):
    pass


# ── Ad / Soyad Formatlama ──────────────────────────────────────────────────────

def _fmt_ad(metin):
    return " ".join(w.capitalize() for w in metin.strip().split()) if metin.strip() else ""

def _fmt_soyad(metin):
    return metin.strip().upper() if metin.strip() else ""


# ── KAYIT & GİRİŞ ─────────────────────────────────────────────────────────────

def register_user(
    username, email, password,
    gender="erkek",
    role="Veteriner Hekim",
    klinik_adi="",
    sehir_ilce="",
    klinik_adresi="",
    tur="",
    telefon="",
    ad="",
    soyad="",
):
    try:
        ad_db    = _fmt_ad(ad)
        soyad_db = _fmt_soyad(soyad)

        if ad_db and soyad_db:
            username_db = f"{ad_db} {soyad_db}"
        else:
            parcalar = username.strip().split()
            if len(parcalar) >= 2:
                ad_db       = _fmt_ad(" ".join(parcalar[:-1]))
                soyad_db    = _fmt_soyad(parcalar[-1])
                username_db = f"{ad_db} {soyad_db}"
            else:
                username_db = _fmt_ad(username)

        email_db = email.strip().lower()

        if supabase.table("kullanicilar").select("id") \
                .ilike("kullanici_adi", username_db).execute().data:
            return False, "Bu kullanıcı adı zaten kullanılıyor."

        if supabase.table("kullanicilar").select("id") \
                .ilike("eposta", email_db).execute().data:
            return False, "Bu e-posta adresi zaten kullanılıyor."

        res = supabase.table("kullanicilar").insert({
            "kullanici_adi": username_db,
            "eposta":        email_db,
            "sifre":         hash_password(password),
            "cinsiyet":      gender,
            "rol":           role,
            "ad":            ad_db,
            "soyad":         soyad_db,
            "telefon":       telefon.strip(),
        }).execute()

        if not res.data:
            return False, "Kayıt sırasında beklenmeyen hata oluştu."

        uid = res.data[0]["id"]

        if role == "Klinik Sahibi":
            save_klinik(
                uid,
                klinik_adi.strip(),
                telefon.strip(),
                klinik_adresi.strip(),
                sehir_ilce.strip(),
                klinik_turu=tur.strip(),
            )

        return True, "Kayıt başarılı!"

    except Exception as e:
        return False, f"Kayıt sırasında hata: {e}"


def login_user(identifier, password):
    try:
        hashed     = hash_password(password)
        identifier = identifier.strip()

        res = supabase.table("kullanicilar").select("*") \
            .ilike("kullanici_adi", identifier) \
            .eq("sifre", hashed) \
            .execute()

        if not res.data:
            res = supabase.table("kullanicilar").select("*") \
                .ilike("eposta", identifier.lower()) \
                .eq("sifre", hashed) \
                .execute()

        if res.data:
            u = res.data[0]
            return True, {
                "id":               u["id"],
                "username":         u["kullanici_adi"],
                "email":            u["eposta"],
                "gender":           u.get("cinsiyet", "erkek"),
                "role":             u.get("rol", "Veteriner Hekim"),
                "klinik_sahibi_id": u.get("klinik_sahibi_id"),
            }

        return False, None

    except Exception:
        return False, None


# ── MÜŞTERİLER ────────────────────────────────────────────────────────────────

def add_customer(user_id, name, phone, address, klinik_id=None):
    if not phone or len(phone) < 10:
        raise PhoneAlreadyExistsError(
            "Telefon numarası zorunludur (en az 10 hane).")

    # Klinik_id yoksa hekimin klinik_sahibi_id'sini otomatik çek
    if klinik_id is None:
        u = supabase.table("kullanicilar").select("klinik_sahibi_id") \
            .eq("id", user_id).execute()
        if u.data:
            klinik_id = u.data[0].get("klinik_sahibi_id")

    if supabase.table("musteriler").select("id") \
            .eq("kullanici_id", user_id).eq("telefon", phone).execute().data:
        raise PhoneAlreadyExistsError("Bu telefon numarası zaten kayıtlı.")

    veri = {
        "kullanici_id": user_id,
        "ad":           name,
        "telefon":      phone,
        "adres":        address,
    }
    if klinik_id is not None:
        veri["klinik_id"] = klinik_id

    res = supabase.table("musteriler").insert(veri).execute()
    return res.data[0]["id"]


def get_customers(user_id, search=None):
    """
    Veteriner hekim:
      - Kliniğe bağlıysa → klinik_id üzerinden tüm klinik müşterileri
      - Bağımsızsa       → sadece kendi müşterileri
    """
    u = supabase.table("kullanicilar").select("klinik_sahibi_id") \
        .eq("id", user_id).execute()
    klinik_sahibi_id = u.data[0].get("klinik_sahibi_id") if u.data else None

    if klinik_sahibi_id:
        return get_klinik_customers(klinik_sahibi_id, search)

    query = supabase.table("musteriler") \
        .select("*, kullanicilar!kullanici_id(kullanici_adi)") \
        .eq("kullanici_id", user_id)
    if search:
        query = query.or_(f"ad.ilike.%{search}%,telefon.ilike.%{search}%")
    return [_norm_customer(r, klinik_gorunumu=False)
            for r in (query.execute().data or [])]


def get_klinik_customers(sahip_id, search=None):
    """Klinik sahibine bağlı tüm müşteriler — klinik_id üzerinden."""
    query = supabase.table("musteriler") \
        .select("*, kullanicilar!kullanici_id(kullanici_adi)") \
        .eq("klinik_id", sahip_id)
    if search:
        query = query.or_(f"ad.ilike.%{search}%,telefon.ilike.%{search}%")
    return [_norm_customer(r, klinik_gorunumu=True)
            for r in (query.execute().data or [])]


def get_customer_count(user_id):
    res = supabase.table("musteriler") \
        .select("id", count="exact").eq("kullanici_id", user_id).execute()
    return res.count or 0


def get_klinik_customer_count(sahip_id):
    res = supabase.table("musteriler") \
        .select("id", count="exact").eq("klinik_id", sahip_id).execute()
    return res.count or 0


def update_customer(customer_id, name, phone, address):
    supabase.table("musteriler").update({
        "ad":      name,
        "telefon": phone,
        "adres":   address,
    }).eq("id", customer_id).execute()


def delete_customer(customer_id):
    animals = supabase.table("hayvanlar").select("id") \
        .eq("musteri_id", customer_id).execute().data or []
    for a in animals:
        supabase.table("randevular").delete().eq("hayvan_id", a["id"]).execute()
        supabase.table("hayvanlar").delete().eq("id", a["id"]).execute()
    supabase.table("randevular").delete().eq("musteri_id", customer_id).execute()
    supabase.table("musteriler").delete().eq("id", customer_id).execute()


def _norm_customer(r, klinik_gorunumu=False):
    h = r.pop("kullanicilar", {}) or {}
    return {
        "id":              r["id"],
        "user_id":         r.get("kullanici_id"),
        "klinik_id":       r.get("klinik_id"),
        "name":            r.get("ad", "—"),
        "phone":           r.get("telefon", ""),
        "address":         r.get("adres", ""),
        "hekim_adi":       h.get("kullanici_adi", "—") if klinik_gorunumu else "",
        "klinik_gorunumu": klinik_gorunumu,
    }


# ── HAYVANLAR ─────────────────────────────────────────────────────────────────

def add_animal(customer_id, name, tag_no, species_breed, birth_date,
               notes="", cinsiyet="erkek", agirlik_kg=None,
               kisirlestirildi=False):
    parts = ([p.strip() for p in species_breed.split("-", 1)]
             if "-" in species_breed else [species_breed.strip(), ""])
    species = parts[0]
    breed   = parts[1] if len(parts) > 1 else ""

    res = supabase.table("hayvanlar").insert({
        "musteri_id":      customer_id,
        "ad":              name,
        "kupe_no":         tag_no,
        "tur":             species,
        "irk":             breed,
        "dogum_tarihi":    birth_date,
        "notlar":          notes,
        "cinsiyet":        cinsiyet,
        "agirlik_kg":      agirlik_kg,
        "kisirlestirildi": kisirlestirildi,
    }).execute()
    return res.data[0]["id"]


def get_animals(customer_id):
    rows = supabase.table("hayvanlar").select("*") \
        .eq("musteri_id", customer_id).execute().data or []
    return [_norm_animal(r) for r in rows]


def get_animal_count(user_id):
    res = supabase.table("hayvanlar") \
        .select("id, musteriler!inner(kullanici_id)", count="exact") \
        .eq("musteriler.kullanici_id", user_id).execute()
    return res.count or 0


def get_klinik_animal_count(sahip_id):
    res = supabase.table("hayvanlar") \
        .select("id, musteriler!inner(klinik_id)", count="exact") \
        .eq("musteriler.klinik_id", sahip_id).execute()
    return res.count or 0


def update_animal(animal_id, name, tag_no, species_breed, birth_date,
                  notes="", cinsiyet="erkek", agirlik_kg=None,
                  kisirlestirildi=False):
    parts = ([p.strip() for p in species_breed.split("-", 1)]
             if "-" in species_breed else [species_breed.strip(), ""])
    species = parts[0]
    breed   = parts[1] if len(parts) > 1 else ""

    supabase.table("hayvanlar").update({
        "ad":              name,
        "kupe_no":         tag_no,
        "tur":             species,
        "irk":             breed,
        "dogum_tarihi":    birth_date,
        "notlar":          notes,
        "cinsiyet":        cinsiyet,
        "agirlik_kg":      agirlik_kg,
        "kisirlestirildi": kisirlestirildi,
    }).eq("id", animal_id).execute()


def delete_animal(animal_id):
    supabase.table("randevular").delete().eq("hayvan_id", animal_id).execute()
    supabase.table("hayvanlar").delete().eq("id", animal_id).execute()


def _norm_animal(r):
    return {
        "id":              r["id"],
        "customer_id":     r.get("musteri_id"),
        "name":            r.get("ad", "—"),
        "tag_no":          r.get("kupe_no", ""),
        "species":         r.get("tur", ""),
        "breed":           r.get("irk", ""),
        "birth_date":      r.get("dogum_tarihi", ""),
        "notes":           r.get("notlar", ""),
        "cinsiyet":        r.get("cinsiyet", "erkek"),
        "agirlik_kg":      r.get("agirlik_kg"),
        "kisirlestirildi": r.get("kisirlestirildi", False),
    }


# ── RANDEVULAR ────────────────────────────────────────────────────────────────

_APPT_SELECT = (
    "*, "
    "hayvanlar(id,ad,tur,irk), "
    "musteriler(id,ad,telefon), "
    "hekim:kullanicilar!kullanici_id(kullanici_adi,rol), "
    "onaylayan:kullanicilar!onaylayan_id(kullanici_adi,rol)"
)


def add_appointment(animal_id, customer_id, user_id,
                    appointment_type, appointment_date, notes="",
                    klinik_id=None):
    veri = {
        "hayvan_id":      animal_id,
        "musteri_id":     customer_id,
        "kullanici_id":   user_id,
        "islem_turu":     appointment_type,
        "randevu_tarihi": appointment_date,
        "notlar":         notes,
        "durum":          "pending",
    }
    if klinik_id is not None:
        veri["klinik_id"] = klinik_id
    res = supabase.table("randevular").insert(veri).execute()
    return res.data[0]["id"]


def _parse_appointments(rows, today, klinik_gorunumu=False):
    result = []
    for r in rows:
        a  = r.pop("hayvanlar",  {}) or {}
        c  = r.pop("musteriler", {}) or {}
        h  = r.pop("hekim",      {}) or {}
        oy = r.pop("onaylayan",  {}) or {}

        onaylayan_adi = ""
        if oy.get("kullanici_adi"):
            rol = oy.get("rol", "")
            onaylayan_adi = "Klinik Sahibi" if rol == "Klinik Sahibi" else "Veteriner Hekim"

        # Randevuyu kimin oluşturduğunu belirle
        hekim_rol = h.get("rol", "")
        if klinik_gorunumu:
            if hekim_rol == "Klinik Sahibi":
                hekim_adi = "🏥 Klinik Sahibi"
            else:
                hekim_adi = h.get("kullanici_adi", "—")  
        else:
            hekim_adi = ""
     
       

        result.append({
            "id":               r["id"],
            "animal_id":        r.get("hayvan_id"),
            "customer_id":      r.get("musteri_id"),
            "user_id":          r.get("kullanici_id"),
            "klinik_id":        r.get("klinik_id"),
            "appointment_type": r.get("islem_turu", "—"),
            "appointment_date": r.get("randevu_tarihi", ""),
            "notes":            r.get("notlar", ""),
            "status":           r.get("durum", "pending"),
            "animal_name":      a.get("ad", "—"),
            "species":          a.get("tur", ""),
            "breed":            a.get("irk", ""),
            "customer_name":    c.get("ad", "—"),
            "customer_phone":   c.get("telefon", "—"),
            "hekim_adi":        hekim_adi,
            "onaylayan_adi":    onaylayan_adi,
            "klinik_gorunumu":  klinik_gorunumu,
            "missed": (
                r.get("durum") == "pending" and
                r.get("randevu_tarihi", "") < today
            ),
        })
    return result


def update_appointment_status(appointment_id, status, onaylayan_id=None):
    veri = {"durum": status}
    if status in ("completed", "cancelled") and onaylayan_id is not None:
        veri["onaylayan_id"] = onaylayan_id
    supabase.table("randevular") \
        .update(veri).eq("id", appointment_id).execute()


def _get_klinik_sahibi_id(user_id):
    """Hekimin bağlı olduğu klinik sahibi ID'sini döner. Bağımsızsa None."""
    u = supabase.table("kullanicilar").select("klinik_sahibi_id") \
        .eq("id", user_id).execute()
    return u.data[0].get("klinik_sahibi_id") if u.data else None


def get_appointments_today(user_id):
    today = datetime.now().strftime("%Y-%m-%d")
    klinik_sahibi_id = _get_klinik_sahibi_id(user_id)

    query = supabase.table("randevular").select(_APPT_SELECT) \
        .eq("durum", "pending") \
        .like("randevu_tarihi", f"{today}%") \
        .order("randevu_tarihi")

    if klinik_sahibi_id:
        query = query.eq("klinik_id", klinik_sahibi_id)
    else:
        query = query.eq("kullanici_id", user_id)

    return _parse_appointments(
        query.execute().data or [], today,
        klinik_gorunumu=bool(klinik_sahibi_id))


def get_appointments_upcoming(user_id):
    today = datetime.now().strftime("%Y-%m-%d")
    klinik_sahibi_id = _get_klinik_sahibi_id(user_id)

    query = supabase.table("randevular").select(_APPT_SELECT) \
        .eq("durum", "pending") \
        .gt("randevu_tarihi", today) \
        .order("randevu_tarihi")

    if klinik_sahibi_id:
        query = query.eq("klinik_id", klinik_sahibi_id)
    else:
        query = query.eq("kullanici_id", user_id)

    return _parse_appointments(
        query.execute().data or [], today,
        klinik_gorunumu=bool(klinik_sahibi_id))


def get_appointments_past(user_id):
    today = datetime.now().strftime("%Y-%m-%d")
    klinik_sahibi_id = _get_klinik_sahibi_id(user_id)

    query = supabase.table("randevular").select(_APPT_SELECT) \
        .or_(f"randevu_tarihi.lt.{today},durum.in.(completed,cancelled)") \
        .order("randevu_tarihi", desc=True)

    if klinik_sahibi_id:
        query = query.eq("klinik_id", klinik_sahibi_id)
    else:
        query = query.eq("kullanici_id", user_id)

    return _parse_appointments(
        query.execute().data or [], today,
        klinik_gorunumu=bool(klinik_sahibi_id))


def get_appointment_count_today(user_id):
    today = datetime.now().strftime("%Y-%m-%d")
    klinik_sahibi_id = _get_klinik_sahibi_id(user_id)

    query = supabase.table("randevular") \
        .select("id", count="exact") \
        .eq("durum", "pending") \
        .like("randevu_tarihi", f"{today}%")

    if klinik_sahibi_id:
        query = query.eq("klinik_id", klinik_sahibi_id)
    else:
        query = query.eq("kullanici_id", user_id)

    return query.execute().count or 0


def get_appointments_by_animal(animal_id):
    res = supabase.table("randevular") \
        .select("id, islem_turu, randevu_tarihi, durum, notlar") \
        .eq("hayvan_id", animal_id) \
        .order("randevu_tarihi", desc=True) \
        .execute()
    return res.data or []


# ── KLİNİK SAHİBİ — klinik_id üzerinden ──────────────────────────────────────

def get_klinik_appointments_today(sahip_id):
    today = datetime.now().strftime("%Y-%m-%d")
    res = supabase.table("randevular") \
        .select(_APPT_SELECT) \
        .eq("klinik_id", sahip_id) \
        .eq("durum", "pending") \
        .like("randevu_tarihi", f"{today}%") \
        .order("randevu_tarihi") \
        .execute()
    return _parse_appointments(res.data or [], today, klinik_gorunumu=True)


def get_klinik_appointments_upcoming(sahip_id):
    today = datetime.now().strftime("%Y-%m-%d")
    res = supabase.table("randevular") \
        .select(_APPT_SELECT) \
        .eq("klinik_id", sahip_id) \
        .eq("durum", "pending") \
        .gt("randevu_tarihi", today) \
        .order("randevu_tarihi") \
        .execute()
    return _parse_appointments(res.data or [], today, klinik_gorunumu=True)


def get_klinik_appointments_past(sahip_id):
    today = datetime.now().strftime("%Y-%m-%d")
    res = supabase.table("randevular") \
        .select(_APPT_SELECT) \
        .eq("klinik_id", sahip_id) \
        .or_(f"randevu_tarihi.lt.{today},durum.in.(completed,cancelled)") \
        .order("randevu_tarihi", desc=True) \
        .execute()
    return _parse_appointments(res.data or [], today, klinik_gorunumu=True)


def get_klinik_appointment_count_today(sahip_id):
    today = datetime.now().strftime("%Y-%m-%d")
    res = supabase.table("randevular") \
        .select("id", count="exact") \
        .eq("klinik_id", sahip_id) \
        .eq("durum", "pending") \
        .like("randevu_tarihi", f"{today}%") \
        .execute()
    return res.count or 0


# ── SMS ───────────────────────────────────────────────────────────────────────

def add_sms_log(user_id, customer_id, animal_id, phone, message):
    supabase.table("sms_kayitlari").insert({
        "kullanici_id": user_id,
        "musteri_id":   customer_id,
        "hayvan_id":    animal_id,
        "telefon":      phone,
        "mesaj":        message,
    }).execute()


def get_sms_logs(user_id):
    res = supabase.table("sms_kayitlari") \
        .select("*, musteriler(ad,telefon)") \
        .eq("kullanici_id", user_id) \
        .order("gonderim_tarihi", desc=True) \
        .execute()
    result = []
    for r in (res.data or []):
        c = r.pop("musteriler", {}) or {}
        result.append({
            "id":             r["id"],
            "phone":          r.get("telefon", ""),
            "message":        r.get("mesaj", ""),
            "sent_at":        str(r.get("gonderim_tarihi", "")),
            "customer_name":  c.get("ad", "—"),
            "customer_phone": c.get("telefon", "—"),
        })
    return result


# ── KLİNİK BİLGİLERİ ─────────────────────────────────────────────────────────

def get_klinik(user_id):
    res = supabase.table("klinik_bilgileri").select("*") \
        .eq("kullanici_id", user_id).execute()
    return res.data[0] if res.data else {
        "klinik_adi":  "",
        "telefon":     "",
        "adres":       "",
        "sehir":       "",
        "klinik_turu": "",
    }


def save_klinik(user_id, klinik_adi, telefon, adres, sehir, klinik_turu=""):
    mevcut = supabase.table("klinik_bilgileri").select("id") \
        .eq("kullanici_id", user_id).execute()
    veri = {
        "klinik_adi":  klinik_adi,
        "telefon":     telefon,
        "adres":       adres,
        "sehir":       sehir,
        "klinik_turu": klinik_turu,
    }
    if mevcut.data:
        supabase.table("klinik_bilgileri").update(veri) \
            .eq("kullanici_id", user_id).execute()
    else:
        veri["kullanici_id"] = user_id
        supabase.table("klinik_bilgileri").insert(veri).execute()


# ── HEKİM YÖNETİMİ ───────────────────────────────────────────────────────────

def get_klinik_hekimleri(sahip_id):
    res = supabase.table("kullanicilar") \
        .select("id, kullanici_adi") \
        .eq("klinik_sahibi_id", sahip_id) \
        .eq("rol", "Veteriner Hekim") \
        .execute()
    return res.data or []


def hekim_kliniğe_ekle(kullanici_adi, sahip_id):
    try:
        res = supabase.table("kullanicilar") \
            .select("id, rol, klinik_sahibi_id") \
            .ilike("kullanici_adi", kullanici_adi.strip()) \
            .execute()

        if not res.data:
            return False, "Bu kullanıcı adında bir hesap bulunamadı."

        u = res.data[0]

        if u.get("rol") != "Veteriner Hekim":
            return False, "Bu kullanıcı bir Veteriner Hekim değil."

        if u.get("klinik_sahibi_id") is not None:
            return False, "Bu hekim zaten başka bir kliniğe kayıtlı."

        supabase.table("kullanicilar").update({
            "klinik_sahibi_id": sahip_id
        }).eq("id", u["id"]).execute()

        return True, f"{kullanici_adi} kliniğinize eklendi."

    except Exception as e:
        return False, f"Hata: {e}"


def hekim_klinikten_cikar(hekim_id, sahip_id):
    try:
        res = supabase.table("kullanicilar") \
            .select("id, klinik_sahibi_id") \
            .eq("id", hekim_id).execute()

        if not res.data:
            return False, "Hekim bulunamadı."

        if res.data[0].get("klinik_sahibi_id") != sahip_id:
            return False, "Bu hekim kliniğinize kayıtlı değil."

        supabase.table("kullanicilar").update({
            "klinik_sahibi_id": None
        }).eq("id", hekim_id).execute()

        return True, "Hekim klinikten çıkarıldı."

    except Exception as e:
        return False, f"Hata: {e}"


# ── KULLANICI GÜNCELLEME ──────────────────────────────────────────────────────

def update_user_profile(user_id, username, email, cinsiyet):
    parcalar    = username.strip().split()
    ad_db       = _fmt_ad(" ".join(parcalar[:-1])) if len(parcalar) >= 2 else _fmt_ad(username)
    soyad_db    = _fmt_soyad(parcalar[-1])          if len(parcalar) >= 2 else ""
    username_db = f"{ad_db} {soyad_db}".strip()
    email_db    = email.strip().lower()

    if supabase.table("kullanicilar").select("id") \
            .ilike("kullanici_adi", username_db).neq("id", user_id).execute().data:
        return False, "Bu kullanıcı adı zaten kullanılıyor."

    if supabase.table("kullanicilar").select("id") \
            .ilike("eposta", email_db).neq("id", user_id).execute().data:
        return False, "Bu e-posta zaten kullanılıyor."

    supabase.table("kullanicilar").update({
        "kullanici_adi": username_db,
        "eposta":        email_db,
        "cinsiyet":      cinsiyet,
        "ad":            ad_db,
        "soyad":         soyad_db,
    }).eq("id", user_id).execute()
    return True, "Profil güncellendi."


def reset_password(username, email, new_password):
    try:
        res = supabase.table("kullanicilar").select("id") \
            .ilike("kullanici_adi", username.strip()) \
            .ilike("eposta", email.strip().lower()) \
            .execute()
        if not res.data:
            return False, "Kullanıcı adı veya e-posta hatalı."
        supabase.table("kullanicilar").update({
            "sifre": hash_password(new_password)
        }).eq("id", res.data[0]["id"]).execute()
        return True, "Şifre başarıyla güncellendi."
    except Exception as e:
        return False, f"Hata: {e}"


def update_password(user_id, current_password, new_password):
    res = supabase.table("kullanicilar").select("sifre") \
        .eq("id", user_id).execute()
    if not res.data:
        return False, "Kullanıcı bulunamadı."
    if res.data[0]["sifre"] != hash_password(current_password):
        return False, "Mevcut şifre yanlış."
    supabase.table("kullanicilar").update({
        "sifre": hash_password(new_password)
    }).eq("id", user_id).execute()
    return True, "Şifre başarıyla güncellendi."


# ── ANALİTİK ──────────────────────────────────────────────────────────────────

def get_monthly_appointments(user_id):
    res = supabase.table("randevular") \
        .select("randevu_tarihi").eq("kullanici_id", user_id).execute()
    counts = {}
    for r in (res.data or []):
        month = (r.get("randevu_tarihi") or "")[:7]
        if month:
            counts[month] = counts.get(month, 0) + 1
    return [{"month": k, "count": v}
            for k, v in sorted(counts.items(), reverse=True)][:12]


def get_species_distribution(user_id):
    res = supabase.table("hayvanlar") \
        .select("tur, musteriler!inner(kullanici_id)") \
        .eq("musteriler.kullanici_id", user_id).execute()
    counts = {}
    for r in (res.data or []):
        s = r.get("tur") or "Bilinmiyor"
        counts[s] = counts.get(s, 0) + 1
    return [{"species": k, "count": v} for k, v in counts.items()]


def get_vaccine_type_distribution(user_id):
    res = supabase.table("randevular") \
        .select("islem_turu").eq("kullanici_id", user_id).execute()
    counts = {}
    for r in (res.data or []):
        t = r.get("islem_turu") or "Diğer"
        counts[t] = counts.get(t, 0) + 1
    return [{"appointment_type": k, "count": v} for k, v in counts.items()]


def get_status_distribution(user_id):
    today = datetime.now().strftime("%Y-%m-%d")
    res = supabase.table("randevular") \
        .select("durum, randevu_tarihi").eq("kullanici_id", user_id).execute()
    counts = {"pending": 0, "completed": 0, "cancelled": 0, "missed": 0}
    for r in (res.data or []):
        d    = r.get("durum") or "pending"
        date = (r.get("randevu_tarihi") or "")[:10]
        if d == "pending" and date < today:
            counts["missed"] += 1
        elif d in counts:
            counts[d] += 1
    return counts


def get_daily_appointments(user_id):
    res = supabase.table("randevular") \
        .select("randevu_tarihi").eq("kullanici_id", user_id).execute()
    counts = {}
    for r in (res.data or []):
        raw = (r.get("randevu_tarihi") or "")[:10]
        if raw:
            counts[raw] = counts.get(raw, 0) + 1
    return [{"date": k, "count": v} for k, v in counts.items()]


def get_new_vs_returning_customers(user_id):
    res = supabase.table("randevular") \
        .select("musteri_id").eq("kullanici_id", user_id).execute()
    appt_sayisi = {}
    for r in (res.data or []):
        mid = r.get("musteri_id")
        if mid:
            appt_sayisi[mid] = appt_sayisi.get(mid, 0) + 1
    if not appt_sayisi:
        return {"yeni": 0, "mevcut": 0}
    yeni   = sum(1 for v in appt_sayisi.values() if v == 1)
    mevcut = sum(1 for v in appt_sayisi.values() if v > 1)
    return {"yeni": yeni, "mevcut": mevcut}


def get_lost_customers(user_id, days=90):
    cutoff  = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    all_ids = {r["id"] for r in (
        supabase.table("musteriler").select("id")
        .eq("kullanici_id", user_id).execute().data or []
    )}
    if not all_ids:
        return 0
    recent_ids = {r["musteri_id"] for r in (
        supabase.table("randevular").select("musteri_id")
        .eq("kullanici_id", user_id)
        .gte("randevu_tarihi", cutoff)
        .execute().data or []
    ) if r.get("musteri_id")}
    return len(all_ids - recent_ids)


def get_completed_appointments_count(user_id):
    res = supabase.table("randevular") \
        .select("id", count="exact") \
        .eq("kullanici_id", user_id) \
        .eq("durum", "completed") \
        .execute()
    return res.count or 0


def get_klinik_monthly_appointments(sahip_id):
    res = supabase.table("randevular") \
        .select("randevu_tarihi").eq("klinik_id", sahip_id).execute()
    counts = {}
    for r in (res.data or []):
        month = (r.get("randevu_tarihi") or "")[:7]
        if month:
            counts[month] = counts.get(month, 0) + 1
    return [{"month": k, "count": v}
            for k, v in sorted(counts.items(), reverse=True)][:12]


def get_klinik_species_distribution(sahip_id):
    res = supabase.table("hayvanlar") \
        .select("tur, musteriler!inner(klinik_id)") \
        .eq("musteriler.klinik_id", sahip_id).execute()
    counts = {}
    for r in (res.data or []):
        s = r.get("tur") or "Bilinmiyor"
        counts[s] = counts.get(s, 0) + 1
    return [{"species": k, "count": v} for k, v in counts.items()]


def get_klinik_vaccine_type_distribution(sahip_id):
    res = supabase.table("randevular") \
        .select("islem_turu").eq("klinik_id", sahip_id).execute()
    counts = {}
    for r in (res.data or []):
        t = r.get("islem_turu") or "Diğer"
        counts[t] = counts.get(t, 0) + 1
    return [{"appointment_type": k, "count": v} for k, v in counts.items()]


def get_klinik_status_distribution(sahip_id):
    today = datetime.now().strftime("%Y-%m-%d")
    res = supabase.table("randevular") \
        .select("durum, randevu_tarihi").eq("klinik_id", sahip_id).execute()
    counts = {"pending": 0, "completed": 0, "cancelled": 0, "missed": 0}
    for r in (res.data or []):
        d    = r.get("durum") or "pending"
        date = (r.get("randevu_tarihi") or "")[:10]
        if d == "pending" and date < today:
            counts["missed"] += 1
        elif d in counts:
            counts[d] += 1
    return counts


def get_klinik_lost_customers(sahip_id, days=90):
    cutoff  = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    all_ids = {r["id"] for r in (
        supabase.table("musteriler").select("id")
        .eq("klinik_id", sahip_id).execute().data or []
    )}
    if not all_ids:
        return 0
    recent_ids = {r["musteri_id"] for r in (
        supabase.table("randevular").select("musteri_id")
        .eq("klinik_id", sahip_id)
        .gte("randevu_tarihi", cutoff)
        .execute().data or []
    ) if r.get("musteri_id")}
    return len(all_ids - recent_ids)


def get_klinik_daily_appointments(sahip_id):
    res = supabase.table("randevular") \
        .select("randevu_tarihi").eq("klinik_id", sahip_id).execute()
    counts = {}
    for r in (res.data or []):
        raw = (r.get("randevu_tarihi") or "")[:10]
        if raw:
            counts[raw] = counts.get(raw, 0) + 1
    return [{"date": k, "count": v} for k, v in counts.items()]


def get_klinik_new_vs_returning_customers(sahip_id):
    res = supabase.table("randevular") \
        .select("musteri_id").eq("klinik_id", sahip_id).execute()
    appt_sayisi = {}
    for r in (res.data or []):
        mid = r.get("musteri_id")
        if mid:
            appt_sayisi[mid] = appt_sayisi.get(mid, 0) + 1
    if not appt_sayisi:
        return {"yeni": 0, "mevcut": 0}
    yeni   = sum(1 for v in appt_sayisi.values() if v == 1)
    mevcut = sum(1 for v in appt_sayisi.values() if v > 1)
    return {"yeni": yeni, "mevcut": mevcut}


def get_klinik_completed_appointments_count(sahip_id):
    res = supabase.table("randevular") \
        .select("id", count="exact") \
        .eq("klinik_id", sahip_id) \
        .eq("durum", "completed") \
        .execute()
    return res.count or 0


# ── HEKİM DETAY ───────────────────────────────────────────────────────────────

def get_hekim_detay(hekim_id):
    """Hekimin tüm istatistiklerini ve son randevularını döner."""

    u = supabase.table("kullanicilar").select("*") \
        .eq("id", hekim_id).execute()
    if not u.data:
        return None
    kullanici = u.data[0]

    today = datetime.now().strftime("%Y-%m-%d")

    musteri_sayisi = supabase.table("musteriler") \
        .select("id", count="exact") \
        .eq("kullanici_id", hekim_id).execute().count or 0

    hayvan_sayisi = get_animal_count(hekim_id)

    toplam_randevu = supabase.table("randevular") \
        .select("id", count="exact") \
        .eq("kullanici_id", hekim_id).execute().count or 0

    bugunki = supabase.table("randevular") \
        .select("id", count="exact") \
        .eq("kullanici_id", hekim_id) \
        .eq("durum", "pending") \
        .like("randevu_tarihi", f"{today}%").execute().count or 0

    tamamlanan = get_completed_appointments_count(hekim_id)

    iptal = supabase.table("randevular") \
        .select("id", count="exact") \
        .eq("kullanici_id", hekim_id) \
        .eq("durum", "cancelled").execute().count or 0

    # Son 5 randevu:
    # - Hekimin oluşturduğu (kullanici_id = hekim_id)
    # - Klinik sahibi müdahale etmemişse (onaylayan_id IS NULL)
    #   VEYA hekimin kendisi tamamlamışsa (onaylayan_id = hekim_id)
    son_randevular = supabase.table("randevular") \
        .select("islem_turu, randevu_tarihi, durum, hayvanlar(ad,tur), musteriler(ad)") \
        .eq("kullanici_id", hekim_id) \
        .or_(f"onaylayan_id.is.null,onaylayan_id.eq.{hekim_id}") \
        .order("randevu_tarihi", desc=True) \
        .limit(5).execute().data or []

    return {
        "id":             kullanici["id"],
        "ad_soyad":       kullanici.get("kullanici_adi", "—"),
        "eposta":         kullanici.get("eposta", "—"),
        "telefon":        kullanici.get("telefon", "—"),
        "cinsiyet":       kullanici.get("cinsiyet", "erkek"),
        "musteri_sayisi": musteri_sayisi,
        "hayvan_sayisi":  hayvan_sayisi,
        "toplam_randevu": toplam_randevu,
        "bugunki":        bugunki,
        "tamamlanan":     tamamlanan,
        "iptal":          iptal,
        "son_randevular": son_randevular,
    }