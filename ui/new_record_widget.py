import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QScrollArea, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap

import database as db
from worker import Worker
from .shared_widgets import TelefonInput, TarihInput


TEAL       = "#30A7A1"
PANEL_BG   = "#1A2942"
CARD_BG    = "#212D3A"
INPUT_BG   = "#1E2A3B"
INPUT_BORD = "#2A3A55"
KOYU       = "#16202A"
BEYAZ      = "#FFFFFF"
GRIS       = "#94A3B8"
DANGER     = "#EF4444"
PURP       = "#7C3AED"


_LINE_EDIT = f"""
QLineEdit {{
    background-color: {INPUT_BG};
    border: 1.5px solid {INPUT_BORD};
    border-radius: 10px;
    padding: 0 16px;
    color: {BEYAZ};
    font-size: 13px;
    font-family: 'Segoe UI';
}}
QLineEdit:focus {{ border-color: {TEAL}; }}
QLineEdit::placeholder {{ color: {GRIS}; }}
"""

_SAVE_BTN = f"""
QPushButton {{
    background-color: {TEAL};
    color: white;
    border-radius: 12px;
    border: none;
    font-size: 14px;
    font-weight: 700;
    font-family: 'Segoe UI';
}}
QPushButton:hover {{ background-color: #27908B; }}
QPushButton:disabled {{ background-color: {INPUT_BORD}; color: {GRIS}; }}
"""


def _get_klinik_id(user):
    """
    Kullanıcının klinik_id'sini döndürür.
    - Klinik Sahibi   → kendi id'si
    - Veteriner Hekim → klinik_sahibi_id (None ise bağımsız hekim)
    """
    if user.get("role") == "Klinik Sahibi":
        return user["id"]
    return user.get("klinik_sahibi_id")


class SectionHeader(QWidget):
    def __init__(self, icon, title, color=None, icon_path=None):
        super().__init__()
        self.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        icon_lbl = QLabel()
        icon_lbl.setStyleSheet("background: transparent;")
        if icon_path and os.path.exists(icon_path):
            px = QPixmap(icon_path).scaled(
                24, 24,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            icon_lbl.setPixmap(px)
            icon_lbl.setFixedSize(24, 24)
        else:
            icon_lbl.setText(icon)
            icon_lbl.setFont(QFont("Segoe UI Emoji", 18))

        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_lbl.setStyleSheet(
            f"background: transparent; color: {color or BEYAZ};")
        layout.addWidget(icon_lbl)
        layout.addWidget(title_lbl)
        layout.addStretch()


def _field(placeholder):
    inp = QLineEdit()
    inp.setPlaceholderText(placeholder)
    inp.setFixedHeight(48)
    inp.setStyleSheet(_LINE_EDIT)
    return inp


def _lbl(text):
    l = QLabel(text)
    l.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
    l.setStyleSheet("color: #A0AABF; background: transparent;")
    return l


def _fmt_isim(raw):
    parts = raw.strip().split()
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0].capitalize()
    return " ".join(p.capitalize() for p in parts[:-1]) + " " + parts[-1].upper()


# ── Cinsiyet Seçme ───────────────────────────────────────────────────────────
class CinsiyetSecici(QWidget):
    SEL  = (f"background-color: {TEAL}; color: white;"
            f"border: 2px solid {TEAL}; border-radius: 8px;"
            "font-size: 12px; font-family: Segoe UI;"
            "font-weight: 600; padding: 6px 0;")
    NORM = (f"background-color: transparent; color: {GRIS};"
            f"border: 1.5px solid {INPUT_BORD}; border-radius: 8px;"
            "font-size: 12px; font-family: Segoe UI; padding: 6px 0;")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self._secili = "erkek"
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        lay.addWidget(_lbl("Cinsiyet"))
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.setContentsMargins(0, 0, 0, 0)
        self.btn_e = QPushButton("♂ Erkek")
        self.btn_d = QPushButton("♀ Dişi")
        for b in (self.btn_e, self.btn_d):
            b.setFixedHeight(40)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_e.setStyleSheet(f"QPushButton {{ {self.SEL} }}")
        self.btn_d.setStyleSheet(f"QPushButton {{ {self.NORM} }}")
        self.btn_e.clicked.connect(lambda: self._sec("erkek"))
        self.btn_d.clicked.connect(lambda: self._sec("dişi"))
        btn_row.addWidget(self.btn_e)
        btn_row.addWidget(self.btn_d)
        lay.addLayout(btn_row)

    def _sec(self, val):
        self._secili = val
        if val == "erkek":
            self.btn_e.setStyleSheet(f"QPushButton {{ {self.SEL} }}")
            self.btn_d.setStyleSheet(f"QPushButton {{ {self.NORM} }}")
        else:
            self.btn_d.setStyleSheet(f"QPushButton {{ {self.SEL} }}")
            self.btn_e.setStyleSheet(f"QPushButton {{ {self.NORM} }}")

    def deger(self):
        return self._secili


# ── Ana widget ────────────────────────────────────────────────────────────────
class NewRecordWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user       = user
        self._klinik_id = _get_klinik_id(user)  # ← klinik_id hesaplanıyor
        self._prefilled_cid = None
        self.setStyleSheet("background-color: transparent;")
        self._build_ui()

    # ── Randevu sayfasından yeni hayvan ekleme ───────────────────────────────
    def prefill_customer(self, customer: dict):
        self._prefilled_cid = customer.get("id")
        self._clear_form()
        self.name_input.setText(customer.get("name", ""))
        self.phone_input.setText(customer.get("phone", ""))
        self.address_input.setText(customer.get("address", ""))
        for w in (self.name_input, self.phone_input, self.address_input):
            w.setReadOnly(True)
            w.setStyleSheet(
                _LINE_EDIT +
                f"QLineEdit {{ background-color: {KOYU}; color: {GRIS}; }}")
        self.btn_save.setText("Hayvanı Kaydet")
        self.msg_lbl.setStyleSheet(
            f"color: {TEAL}; font-size: 12px; font-weight: 600;")
        self.msg_lbl.setText(
            f"ℹ️ {customer.get('name', '')} için yeni hayvan ekleniyor.")
        self.animal_name_input.setFocus()

    def _release_prefill(self):
        self._prefilled_cid = None
        for w in (self.name_input, self.phone_input, self.address_input):
            w.setReadOnly(False)
            w.setStyleSheet(_LINE_EDIT)
        self.btn_save.setText("Sisteme Kaydet")
        self.msg_lbl.clear()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(30, 30, 30, 30)
        outer.setSpacing(0)

        title = QLabel("Yeni Kayıt Oluştur")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #0F172A;")
        outer.addWidget(title)
        outer.addSpacing(20)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background: transparent; }}"
            f"QScrollBar:vertical {{ background: {KOYU}; width: 6px; border-radius: 3px; }}"
            f"QScrollBar::handle:vertical {{ background: {INPUT_BORD}; border-radius: 3px; }}"
            f"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}")

        form_card = QFrame()
        form_card.setStyleSheet(f"""
QFrame {{
    background: {CARD_BG};
    border-radius: 16px;
    border: none;
}}
""")
        fl = QVBoxLayout(form_card)
        fl.setContentsMargins(36, 32, 36, 32)
        fl.setSpacing(18)

        # Müşteri bilgileri
        fl.addWidget(SectionHeader(
            "", "Müşteri (Sahip) Bilgileri",
            icon_path="assets/kayitolustur.png"))
        fl.addWidget(self._sep())

        row1 = QHBoxLayout()
        row1.setSpacing(16)
        self.name_input  = _field("Ad Soyad")
        self.phone_input = TelefonInput()
        row1.addWidget(self.name_input)
        row1.addWidget(self.phone_input)
        fl.addLayout(row1)

        self.address_input = _field("Açık Adres")
        fl.addWidget(self.address_input)
        fl.addSpacing(8)

        # Hayvan bilgileri
        fl.addWidget(SectionHeader(
            "", "Hasta (Hayvan) Bilgileri",
            icon_path="assets/add.png"))
        fl.addWidget(self._sep())

        row2 = QHBoxLayout()
        row2.setSpacing(16)
        self.animal_name_input = _field("Hayvan Adı / Küpe No")
        self.species_input     = _field("Tür & Irk (Örn: Köpek - Golden)")
        row2.addWidget(self.animal_name_input)
        row2.addWidget(self.species_input)
        fl.addLayout(row2)

        row3 = QHBoxLayout()
        row3.setSpacing(16)
        bdate_col = QVBoxLayout()
        bdate_col.setSpacing(6)
        bdate_col.addWidget(_lbl("Doğum Tarihi"))
        self.birthdate_input = TarihInput()
        bdate_col.addWidget(self.birthdate_input)
        agirlik_col = QVBoxLayout()
        agirlik_col.setSpacing(6)
        agirlik_col.addWidget(_lbl("Ağırlık (kg)"))
        self.agirlik_input = _field("Örn: 4.5")
        agirlik_col.addWidget(self.agirlik_input)
        row3.addLayout(bdate_col)
        row3.addLayout(agirlik_col)
        fl.addLayout(row3)

        row4 = QHBoxLayout()
        row4.setSpacing(24)
        row4.setContentsMargins(0, 4, 0, 0)
        self.cinsiyet_input = CinsiyetSecici()
        row4.addWidget(self.cinsiyet_input, 1)
        kisir_col = QVBoxLayout()
        kisir_col.setSpacing(6)
        kisir_col.addWidget(_lbl("Kısırlaştırıldı"))
        self.chk_kisir = QCheckBox("Evet, kısırlaştırıldı")
        self.chk_kisir.setFont(QFont("Segoe UI", 11))
        self.chk_kisir.setStyleSheet(f"""
QCheckBox {{
    color: {BEYAZ}; background: transparent;
    spacing: 6px; font-size: 11px;
}}
QCheckBox::indicator {{
    width: 13px; height: 13px; border-radius: 3px;
    border: 1.5px solid {INPUT_BORD}; background: {INPUT_BG};
}}
QCheckBox::indicator:checked {{
    background: {TEAL}; border-color: {TEAL};
    image: url(assets/check.png);
}}
""")
        kisir_col.addWidget(self.chk_kisir)
        kisir_col.addStretch()
        row4.addLayout(kisir_col, 1)
        fl.addLayout(row4)

        self.animal_notes_input = _field("Hayvan Notu (İsteğe Bağlı)")
        fl.addWidget(self.animal_notes_input)
        fl.addSpacing(10)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_save = QPushButton("Sisteme Kaydet")
        self.btn_save.setFixedSize(260, 52)
        self.btn_save.setStyleSheet(_SAVE_BTN)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.clicked.connect(self._save)
        btn_row.addWidget(self.btn_save)
        btn_row.addStretch()
        fl.addLayout(btn_row)

        self.msg_lbl = QLabel("")
        self.msg_lbl.setFont(QFont("Segoe UI", 13))
        self.msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.msg_lbl.setWordWrap(True)
        fl.addWidget(self.msg_lbl)

        scroll.setWidget(form_card)
        outer.addWidget(scroll, 1)

    def _sep(self):
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background: {INPUT_BORD};")
        return line

    # ── Kayıt Ekle ────────────────────────────────────────────────────────────
    def _save(self):
        name         = _fmt_isim(self.name_input.text())
        phone        = self.phone_input.deger()
        address      = self.address_input.text().strip()
        a_name       = self.animal_name_input.text().strip()
        species      = self.species_input.text().strip()
        bdate        = self.birthdate_input.text().strip()
        animal_notes = self.animal_notes_input.text().strip()
        cinsiyet     = self.cinsiyet_input.deger()
        kisir        = self.chk_kisir.isChecked()
        agirlik_raw  = self.agirlik_input.text().strip().replace(",", ".")

        try:
            agirlik_kg = float(agirlik_raw) if agirlik_raw else None
        except ValueError:
            self._show_msg("❌ Ağırlık sayısal olmalıdır.", DANGER)
            return

        if not name:
            self._show_msg("❌ Müşteri adı zorunludur.", DANGER)
            return
        if not phone or len(phone) < 10:
            self._show_msg("❌ Telefon numarası zorunludur.", DANGER)
            return
        if not a_name:
            self._show_msg("❌ Hayvan adı zorunludur.", DANGER)
            return

        parts        = a_name.split("/", 1)
        a_name_clean = parts[0].strip()
        tag_no       = parts[1].strip() if len(parts) > 1 else ""

        self.btn_save.setEnabled(False)

        # ── Mevcut müşteriye hayvan ekleme ───────────────────────────────────
        if self._prefilled_cid:
            cid = self._prefilled_cid

            def _do_prefill():
                db.add_animal(
                    cid, a_name_clean, tag_no, species, bdate, animal_notes,
                    cinsiyet=cinsiyet,
                    agirlik_kg=agirlik_kg,
                    kisirlestirildi=kisir,
                )
                return a_name_clean

            def _done_prefill(saved_name):
                self.btn_save.setEnabled(True)
                self._release_prefill()
                self._clear_form()
                main = self.window()
                if hasattr(main, "_page_widgets") \
                        and main._page_widgets[1] is not None:
                    appt = main._page_widgets[1]
                    if appt.selected_customer \
                            and appt.selected_customer.get("id") == cid:
                        appt._select_customer(appt.selected_customer)
                if hasattr(main, "bildirim_goster"):
                    main.bildirim_goster(
                        f"{saved_name} başarıyla eklendi!", tur="basarili")

            self._save_worker = Worker(_do_prefill)
            self._save_worker.result.connect(_done_prefill)
            self._save_worker.error.connect(lambda e: (
                self.btn_save.setEnabled(True),
                self._show_msg(f"❌ Hata: {e}", DANGER)
            ))
            self._save_worker.start()
            return

        # ── Yeni müşteri + hayvan kaydı ──────────────────────────────────────
        _uid       = self.user["id"]
        _klinik_id = self._klinik_id  # ← klinik_id taşınıyor

        def _do_save():
            cid = db.add_customer(
                _uid, name, phone, address,
                klinik_id=_klinik_id  # ← Supabase'e yazılıyor
            )
            db.add_animal(
                cid, a_name_clean, tag_no, species, bdate, animal_notes,
                cinsiyet=cinsiyet,
                agirlik_kg=agirlik_kg,
                kisirlestirildi=kisir,
            )
            return a_name_clean

        def _done(saved_name):
            self.btn_save.setEnabled(True)
            self._clear_form()
            main = self.window()
            if hasattr(main, "dashboard") and main.dashboard:
                main.dashboard.refresh()
            if hasattr(main, "_page_widgets") \
                    and main._page_widgets[1] is not None:
                main._page_widgets[1]._load_customers()
            if hasattr(main, "bildirim_goster"):
                main.bildirim_goster(
                    f"{saved_name or 'Hasta'} başarıyla kayıt edildi!",
                    tur="basarili")

        def _err(e):
            self.btn_save.setEnabled(True)
            if "telefon" in e.lower() or "kayıtlı" in e.lower():
                self._show_msg("⚠️ Bu numara daha önce kullanıldı.", DANGER)
            else:
                self._show_msg(f"❌ Hata: {e}", DANGER)

        self._save_worker = Worker(_do_save)
        self._save_worker.result.connect(_done)
        self._save_worker.error.connect(_err)
        self._save_worker.start()

    def _show_msg(self, text, color):
        self.msg_lbl.setStyleSheet(
            f"color: {color}; font-size: 13px; font-weight: 600;")
        self.msg_lbl.setText(text)

    def _clear_form(self):
        for inp in [
            self.name_input, self.phone_input, self.address_input,
            self.animal_name_input, self.species_input,
            self.birthdate_input, self.agirlik_input,
            self.animal_notes_input,
        ]:
            inp.clear()
        self.cinsiyet_input._sec("erkek")
        self.chk_kisir.setChecked(False)
        self.msg_lbl.clear()