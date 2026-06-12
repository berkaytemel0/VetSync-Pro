# 🐾 VetSync Pro






**Veteriner klinikleri için geliştirilmiş, bulut tabanlı modern yönetim sistemi.**

***

## ✨ Özellikler

| 🏥 Klinik Yönetimi | 📋 Kayıt Sistemi | 📊 Analitik |
|---|---|---|
| Çok hekim desteği | Müşteri yönetimi | Aylık randevu grafikleri |
| Hekim-Klinik bağlama | Hayvan kayıtları | Tür dağılım istatistikleri |
| Rol bazlı erişim | Küpe no takibi | Durum dağılım analizi |
| Randevu onay sistemi | Adres & telefon | Kayıp müşteri raporu |

***

## 🛠️ Kullanılan Teknolojiler

| Teknoloji | Açıklama |
|---|---|
| 🐍 Python 3.10+ | Ana programlama dili |
| 🖥️ PyQt6 | Masaüstü arayüz framework |
| ☁️ Supabase | Bulut PostgreSQL veritabanı |
| 🔐 SHA-256 | Şifre hashleme |
| 📦 python-dotenv | Ortam değişkeni yönetimi |

***

## ⚙️ Kurulum

```bash
# 1. Repoyu klonla
git clone https://github.com/KULLANICI_ADIN/VetSync-Pro.git
cd VetSync-Pro

# 2. Gerekli kütüphaneleri yükle
pip install -r requirements.txt

# 3. .env dosyası oluştur
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# 4. Çalıştır
python main.py
```

***

## 👥 Kullanıcı Rolleri

```
🏥 Klinik Sahibi
   ├── Tüm hekimleri ve randevuları görür
   ├── Hekim ekler / çıkarır
   └── Klinik geneli istatistikleri inceler

👨‍⚕️ Veteriner Hekim
   ├── Kendi müşteri ve hayvanlarını yönetir
   ├── Randevu oluşturur ve takip eder
   └── Kendi istatistiklerini görür
```

***

## 🗄️ Veritabanı Yapısı

```
kullanicilar     → Tüm kullanıcı bilgileri ve roller
musteriler       → Hasta sahipleri
hayvanlar        → Hasta hayvanlar
randevular       → Tüm randevu kayıtları
klinik_bilgileri → Klinik profil bilgileri
sms_kayitlari    → SMS gönderim geçmişi
```

***

## 🔄 Uygulama Akışı

1. **Giriş Ekranı** — Kullanıcı adı / e-posta ve şifre ile giriş
2. **Rol Kontrolü** — Veteriner Hekim veya Klinik Sahibi ekranı açılır
3. **Veritabanı** — Tüm işlemler Supabase üzerinden yürütülür
4. **Klinik Sahibi** — Tüm hekimlerin randevularını ve hangi hekimin sıra verdiğini görebilir
5. **Hekim** — Klinik sahibine bağlıysa klinik verilerini, bağımsızsa kendi verilerini yönetir

***

## 🐛 Bilinen Notlar

- Şifre hashleme SHA-256 ile yapılmaktadır (salt'sız, proje kapsamında basit tutulmuştur)
- `.env` dosyası güvenlik nedeniyle repoya dahil edilmemiştir

***

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.

***

**🎓 Mersin Üniversitesi**

**Bitirme Projesi 2025–2026**

*Geliştirici: BERKAY TEMEL*
