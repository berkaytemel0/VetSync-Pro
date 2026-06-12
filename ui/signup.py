"""
Kayıt (signup) formları — RegisterPanel, HekimAdim1Panel, HekimAdim2Panel,
SahipAdim2Panel, SahipAdim3Panel ve yardımcılar.
"""
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QStackedWidget, QSizePolicy, QComboBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QCursor

MAVİ_KOYU    = "#0F1C2E"
MAVİ_ANA     = "#1A2942"
MAVİ_ORTA    = "#2B4060"
BEYAZ        = "#FFFFFF"
ACIK_GRI     = "#F4F7FA"
KENARLIK_GRI = "#E2E8F0"
YAZI_GRI     = "#64748B"
KOYU_YAZI    = "#0F172A"
ANA_FONT     = "Segoe UI"

_SEL_CSS  = (f"background-color:{MAVİ_ANA};color:white;"
             f"border:2px solid {MAVİ_ANA};border-radius:8px;"
             "font-size:12px;font-family:Segoe UI;font-weight:600;padding:6px 0;")
_NORM_CSS = (f"background-color:transparent;color:{YAZI_GRI};"
             f"border:1.5px solid {KENARLIK_GRI};border-radius:8px;"
             "font-size:12px;font-family:Segoe UI;padding:6px 0;")
CIN_SEL  = "QPushButton {" + _SEL_CSS + "}"
CIN_NORM = ("QPushButton {" + _NORM_CSS + "}"
            f" QPushButton:hover {{border-color:{MAVİ_ANA};color:{MAVİ_ANA};}}")


# ── Yardımcılar ───────────────────────────────────────────────────────────────
def _etiketli_entry(parent_layout, etiket, placeholder, gizle=False, genislik=320):
    cerceve = QWidget()
    cerceve.setStyleSheet("background:transparent;")
    lay = QVBoxLayout(cerceve)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(4)
    lbl = QLabel(etiket)
    lbl.setFont(QFont(ANA_FONT, 10))
    lbl.setStyleSheet(f"color:{YAZI_GRI};background:transparent;")
    lay.addWidget(lbl)
    entry = QLineEdit()
    entry.setPlaceholderText(placeholder)
    entry.setFixedSize(genislik, 42)
    if gizle:
        entry.setEchoMode(QLineEdit.EchoMode.Password)
    entry.setFont(QFont(ANA_FONT, 11))
    entry.setStyleSheet(f"""
QLineEdit {{
    background-color:{ACIK_GRI};border:1px solid {KENARLIK_GRI};
    border-radius:8px;padding:0 12px;color:{KOYU_YAZI};
}}
QLineEdit:focus {{ border:1.5px solid {MAVİ_ORTA}; }}
""")
    lay.addWidget(entry)
    parent_layout.addWidget(cerceve, alignment=Qt.AlignmentFlag.AlignCenter)
    return entry


def _etiketli_combo(parent_layout, etiket, secenekler, genislik=320):
    cerceve = QWidget()
    cerceve.setStyleSheet("background:transparent;")
    lay = QVBoxLayout(cerceve)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(4)
    lbl = QLabel(etiket)
    lbl.setFont(QFont(ANA_FONT, 10))
    lbl.setStyleSheet(f"color:{YAZI_GRI};background:transparent;")
    lay.addWidget(lbl)
    combo = QComboBox()
    combo.addItems(secenekler)
    combo.setFixedSize(genislik, 42)
    combo.setFont(QFont(ANA_FONT, 11))
    combo.setStyleSheet(f"""
QComboBox {{
    background-color:{ACIK_GRI};border:1px solid {KENARLIK_GRI};
    border-radius:8px;padding:10px 12px;color:{KOYU_YAZI};
}}
QComboBox::drop-down {{ border:none;padding-right:10px; }}
QComboBox:focus {{ border:1.5px solid {MAVİ_ORTA}; }}
QComboBox QAbstractItemView {{
    background-color:{BEYAZ};border:1px solid {KENARLIK_GRI};
    border-radius:8px;selection-background-color:{ACIK_GRI};
    color:{KOYU_YAZI};padding:4px;
}}
""")
    lay.addWidget(combo)
    parent_layout.addWidget(cerceve, alignment=Qt.AlignmentFlag.AlignCenter)
    return combo


def _kayit_form_alani():
    page = QWidget()
    page.setStyleSheet("background:transparent;")
    lay = QVBoxLayout(page)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(6)
    return page, lay


def _aksiyon_butonu(metin, on_click):
    btn = QPushButton(metin)
    btn.setFixedSize(320, 44)
    btn.setFont(QFont(ANA_FONT, 12, QFont.Weight.Bold))
    btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    btn.setStyleSheet(f"""
QPushButton {{ background-color:{MAVİ_ANA};color:white;border-radius:8px;border:none; }}
QPushButton:hover {{ background-color:{MAVİ_KOYU}; }}
""")
    btn.clicked.connect(on_click)
    return btn


def _kayit_ol_butonu(on_click):
    return _aksiyon_butonu("KAYIT OL", on_click)


def _geri_butonu():
    btn = QPushButton("← Geri")
    btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    btn.setFont(QFont(ANA_FONT, 10, QFont.Weight.Bold))
    btn.setStyleSheet(f"""
QPushButton {{
    background:transparent;color:{MAVİ_ANA};border:none;
    text-decoration:underline;font-weight:600;
}}
QPushButton:hover {{ color:{MAVİ_KOYU}; }}
""")
    return btn


def _cinsiyet_widget(parent_layout):
    """Cinsiyet seçici widget döndürür: (widget, btn_erkek, btn_kadin)"""
    cins_w = QWidget()
    cins_w.setStyleSheet("background:transparent;")
    cins_w.setFixedWidth(320)
    cins_lay = QVBoxLayout(cins_w)
    cins_lay.setContentsMargins(0, 0, 0, 0)
    cins_lay.setSpacing(4)
    cins_lbl = QLabel("Cinsiyet")
    cins_lbl.setFont(QFont(ANA_FONT, 10))
    cins_lbl.setStyleSheet(f"color:{YAZI_GRI};background:transparent;")
    cins_lay.addWidget(cins_lbl)
    btn_row = QHBoxLayout()
    btn_row.setSpacing(10)
    btn_row.setContentsMargins(0, 0, 0, 0)
    btn_erkek = QPushButton(" Erkek")
    btn_kadin = QPushButton(" Kadın")
    btn_erkek.setStyleSheet(CIN_SEL)
    btn_kadin.setStyleSheet(CIN_NORM)
    for b in (btn_erkek, btn_kadin):
        b.setFixedHeight(36)
        b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    btn_row.addWidget(btn_erkek, 1)
    btn_row.addWidget(btn_kadin, 1)
    cins_lay.addLayout(btn_row)
    parent_layout.addWidget(cins_w, alignment=Qt.AlignmentFlag.AlignCenter)
    return cins_w, btn_erkek, btn_kadin


# ══════════════════════════════════════════════════════════════════════════════
# Telefon Input
# ══════════════════════════════════════════════════════════════════════════════
class TelefonInput(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("(5XX) XXX XX XX")
        self.setFixedSize(320, 42)
        self.setFont(QFont(ANA_FONT, 11))
        self.setMaxLength(15)
        self.setStyleSheet(f"""
QLineEdit {{
    background-color:{ACIK_GRI};border:1px solid {KENARLIK_GRI};
    border-radius:8px;padding:0 12px;color:{KOYU_YAZI};letter-spacing:1px;
}}
QLineEdit:focus {{ border:1.5px solid {MAVİ_ORTA}; }}
""")
        self._busy = False
        self.textChanged.connect(self._format)

    def _format(self, text):
        if self._busy:
            return
        self._busy = True
        digits = "".join(c for c in text if c.isdigit())
        if digits.startswith("0"):
            digits = digits[1:]
        digits = digits[:10]
        result = ""
        if len(digits) >= 1:  result = "(" + digits[:3]
        if len(digits) >= 4:  result += ") " + digits[3:6]
        if len(digits) >= 7:  result += " " + digits[6:8]
        if len(digits) >= 9:  result += " " + digits[8:10]
        self.setText(result)
        self.setCursorPosition(len(result))
        self._busy = False

    def telefon(self):
        return "".join(c for c in self.text() if c.isdigit())

    def telefon_formatlı(self):
        return self.text()


# ══════════════════════════════════════════════════════════════════════════════
# Hekim Adım 1 — Kendini Tanıt
# ══════════════════════════════════════════════════════════════════════════════
class HekimAdim1Panel(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:transparent;")
        self._ileri_callback = None

        form_w = QWidget()
        form_w.setStyleSheet("background:transparent;")
        form_w.setFixedWidth(320)
        lay = QVBoxLayout(form_w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        lbl_adim = QLabel("Adım 1 / 2  —  Kendini Tanıt")
        lbl_adim.setFont(QFont(ANA_FONT, 10, QFont.Weight.Bold))
        lbl_adim.setStyleSheet(f"color:{MAVİ_ANA};background:transparent;")
        lay.addWidget(lbl_adim)
        lay.addSpacing(6)

        self.reg_ad    = _etiketli_entry(lay, "Ad",    "Adınız")
        self.reg_soyad = _etiketli_entry(lay, "Soyad", "Soyadınız")

        _, self.btn_erkek, self.btn_kadin = _cinsiyet_widget(lay)
        self._secili_cinsiyet = "erkek"
        self.btn_erkek.clicked.connect(self._sec_erkek)
        self.btn_kadin.clicked.connect(self._sec_kadin)

        lay.addSpacing(12)
        self.btn_ileri = _aksiyon_butonu("İLERİ →", self._on_ileri)
        lay.addWidget(self.btn_ileri, alignment=Qt.AlignmentFlag.AlignCenter)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(form_w, alignment=Qt.AlignmentFlag.AlignCenter)

        self.reg_ad.returnPressed.connect(lambda: self.reg_soyad.setFocus())
        self.reg_soyad.returnPressed.connect(self.btn_ileri.click)

    def _sec_erkek(self):
        self._secili_cinsiyet = "erkek"
        self.btn_erkek.setStyleSheet(CIN_SEL)
        self.btn_kadin.setStyleSheet(CIN_NORM)

    def _sec_kadin(self):
        self._secili_cinsiyet = "kadın"
        self.btn_kadin.setStyleSheet(CIN_SEL)
        self.btn_erkek.setStyleSheet(CIN_NORM)

    def _on_ileri(self):
        if self._ileri_callback:
            self._ileri_callback()


# ══════════════════════════════════════════════════════════════════════════════
# Hekim Adım 2 — İletişim Bilgileri
# ══════════════════════════════════════════════════════════════════════════════
class HekimAdim2Panel(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:transparent;")
        self._kayit_callback = None
        self._geri_callback  = None

        form_w = QWidget()
        form_w.setStyleSheet("background:transparent;")
        form_w.setFixedWidth(320)
        lay = QVBoxLayout(form_w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        ust = QHBoxLayout()
        self.btn_geri = _geri_butonu()
        self.btn_geri.clicked.connect(self._on_geri)
        ust.addWidget(self.btn_geri)
        ust.addStretch()
        lay.addLayout(ust)
        lay.addSpacing(4)

        lbl_adim = QLabel("Adım 2 / 2  —  İletişim Bilgileri")
        lbl_adim.setFont(QFont(ANA_FONT, 10, QFont.Weight.Bold))
        lbl_adim.setStyleSheet(f"color:{MAVİ_ANA};background:transparent;")
        lay.addWidget(lbl_adim)
        lay.addSpacing(6)

        self.reg_mail = _etiketli_entry(lay, "E-Posta Adresi", "ornek@email.com")

        # Telefon
        tel_w = QWidget()
        tel_w.setStyleSheet("background:transparent;")
        tel_lay = QVBoxLayout(tel_w)
        tel_lay.setContentsMargins(0, 0, 0, 0)
        tel_lay.setSpacing(4)
        tel_lbl = QLabel("Telefon")
        tel_lbl.setFont(QFont(ANA_FONT, 10))
        tel_lbl.setStyleSheet(f"color:{YAZI_GRI};background:transparent;")
        tel_lay.addWidget(tel_lbl)
        self.reg_tel = TelefonInput()
        tel_lay.addWidget(self.reg_tel)
        lay.addWidget(tel_w, alignment=Qt.AlignmentFlag.AlignCenter)

        self.reg_sifre = _etiketli_entry(lay, "Şifre", "••••••••", gizle=True)

        lay.addSpacing(12)
        self.btn_kayit = _kayit_ol_butonu(self._on_kayit)
        lay.addWidget(self.btn_kayit, alignment=Qt.AlignmentFlag.AlignCenter)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(form_w, alignment=Qt.AlignmentFlag.AlignCenter)

        self.reg_mail.returnPressed.connect(lambda: self.reg_tel.setFocus())
        self.reg_tel.returnPressed.connect(lambda: self.reg_sifre.setFocus())
        self.reg_sifre.returnPressed.connect(self.btn_kayit.click)

    def _on_geri(self):
        if self._geri_callback:
            self._geri_callback()

    def _on_kayit(self):
        if self._kayit_callback:
            self._kayit_callback()


# ══════════════════════════════════════════════════════════════════════════════
# Adım 2 — Klinik Konumu
# ══════════════════════════════════════════════════════════════════════════════
class SahipAdim2Panel(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background:{BEYAZ};")
        self._ileri_callback = None
        self._geri_callback  = None

        rv = QVBoxLayout(self)
        rv.setContentsMargins(0, 0, 0, 0)
        rv.setSpacing(0)

        spacer = QWidget()
        spacer.setFixedHeight(38)
        spacer.setStyleSheet("background:transparent;")
        rv.addWidget(spacer)

        icerik = QWidget()
        icerik.setStyleSheet("background:transparent;")
        il = QVBoxLayout(icerik)
        il.setContentsMargins(50, 0, 50, 10)
        il.setSpacing(0)

        ust = QHBoxLayout()
        self.btn_geri = _geri_butonu()
        ust.addWidget(self.btn_geri)
        ust.addStretch()
        il.addLayout(ust)
        il.addSpacing(8)

        lbl_adim = QLabel("Adım 2 / 3")
        lbl_adim.setFont(QFont(ANA_FONT, 10, QFont.Weight.Bold))
        lbl_adim.setStyleSheet(f"color:{MAVİ_ANA};background:transparent;")
        il.addWidget(lbl_adim)
        il.addSpacing(4)

        lbl_baslik = QLabel("Klinik Konumu")
        lbl_baslik.setFont(QFont(ANA_FONT, 24, QFont.Weight.Bold))
        lbl_baslik.setStyleSheet(f"color:{KOYU_YAZI};background:transparent;")
        il.addWidget(lbl_baslik)
        il.addSpacing(4)

        lbl_alt = QLabel("Klinik adı ve konum bilgilerinizi girin")
        lbl_alt.setFont(QFont(ANA_FONT, 11))
        lbl_alt.setStyleSheet(f"color:{YAZI_GRI};background:transparent;")
        il.addWidget(lbl_alt)
        il.addSpacing(20)

        form_w = QWidget()
        form_w.setStyleSheet("background:transparent;")
        form_w.setFixedWidth(320)
        lay_form = QVBoxLayout(form_w)
        lay_form.setContentsMargins(0, 0, 0, 0)
        lay_form.setSpacing(6)

        self.reg_klinik_ismi = _etiketli_entry(lay_form, "Klinik İsmi", "Kliniğinizin Adı")

        row_sehir = QWidget()
        row_sehir.setStyleSheet("background:transparent;")
        row_sehir.setFixedWidth(320)
        lay_sehir = QHBoxLayout(row_sehir)
        lay_sehir.setContentsMargins(0, 0, 0, 0)
        lay_sehir.setSpacing(10)

        iller = [
            "İstanbul","Ankara","İzmir","Adana","Adıyaman","Afyonkarahisar",
            "Ağrı","Aksaray","Amasya","Antalya","Ardahan","Artvin","Aydın",
            "Balıkesir","Bartın","Batman","Bayburt","Bilecik","Bingöl",
            "Bitlis","Bolu","Burdur","Bursa","Çanakkale","Çankırı","Çorum",
            "Denizli","Diyarbakır","Düzce","Edirne","Elazığ","Erzincan",
            "Erzurum","Eskişehir","Gaziantep","Giresun","Gümüşhane","Hakkari",
            "Hatay","Iğdır","Isparta","Kahramanmaraş","Karabük","Karaman",
            "Kars","Kastamonu","Kayseri","Kırıkkale","Kırklareli","Kırşehir",
            "Kilis","Kocaeli","Konya","Kütahya","Malatya","Manisa","Mardin",
            "Mersin","Muğla","Muş","Nevşehir","Niğde","Ordu","Osmaniye",
            "Rize","Sakarya","Samsun","Siirt","Sinop","Sivas","Şanlıurfa",
            "Şırnak","Tekirdağ","Tokat","Trabzon","Tunceli","Uşak","Van",
            "Yalova","Yozgat","Zonguldak"
        ]
        self.combo_il = _etiketli_combo(lay_sehir, "İl", iller, genislik=155)
        self.reg_ilce = _etiketli_entry(lay_sehir, "İlçe", "Örn: Kadıköy", genislik=155)
        lay_form.addWidget(row_sehir, alignment=Qt.AlignmentFlag.AlignCenter)

        self.reg_klinik_adresi = _etiketli_entry(lay_form, "Klinik Açık Adresi", "Açık Adres")

        lay_form.addSpacing(12)
        self.btn_ileri = _aksiyon_butonu("İLERİ →", self._on_ileri_clicked)
        lay_form.addWidget(self.btn_ileri, alignment=Qt.AlignmentFlag.AlignCenter)

        il.addWidget(form_w, alignment=Qt.AlignmentFlag.AlignCenter)
        il.addStretch()
        rv.addWidget(icerik, 1)

        self.btn_geri.clicked.connect(self._on_geri_clicked)
        self.reg_klinik_ismi.returnPressed.connect(lambda: self.reg_ilce.setFocus())
        self.reg_ilce.returnPressed.connect(lambda: self.reg_klinik_adresi.setFocus())
        self.reg_klinik_adresi.returnPressed.connect(self.btn_ileri.click)

    def _on_geri_clicked(self):
        if self._geri_callback:
            self._geri_callback()

    def _on_ileri_clicked(self):
        if self._ileri_callback:
            self._ileri_callback()


# ══════════════════════════════════════════════════════════════════════════════
# Adım 3 — Klinik Ayarları
# ══════════════════════════════════════════════════════════════════════════════
class SahipAdim3Panel(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background:{BEYAZ};")
        self._kayit_callback = None
        self._geri_callback  = None

        rv = QVBoxLayout(self)
        rv.setContentsMargins(0, 0, 0, 0)
        rv.setSpacing(0)

        spacer = QWidget()
        spacer.setFixedHeight(38)
        spacer.setStyleSheet("background:transparent;")
        rv.addWidget(spacer)

        icerik = QWidget()
        icerik.setStyleSheet("background:transparent;")
        il = QVBoxLayout(icerik)
        il.setContentsMargins(50, 0, 50, 10)
        il.setSpacing(0)

        ust = QHBoxLayout()
        self.btn_geri = _geri_butonu()
        ust.addWidget(self.btn_geri)
        ust.addStretch()
        il.addLayout(ust)
        il.addSpacing(8)

        lbl_adim = QLabel("Adım 3 / 3")
        lbl_adim.setFont(QFont(ANA_FONT, 10, QFont.Weight.Bold))
        lbl_adim.setStyleSheet(f"color:{MAVİ_ANA};background:transparent;")
        il.addWidget(lbl_adim)
        il.addSpacing(4)

        lbl_baslik = QLabel("Klinik Ayarları")
        lbl_baslik.setFont(QFont(ANA_FONT, 24, QFont.Weight.Bold))
        lbl_baslik.setStyleSheet(f"color:{KOYU_YAZI};background:transparent;")
        il.addWidget(lbl_baslik)
        il.addSpacing(4)

        lbl_alt = QLabel("Klinik türü ve iletişim numaranız")
        lbl_alt.setFont(QFont(ANA_FONT, 11))
        lbl_alt.setStyleSheet(f"color:{YAZI_GRI};background:transparent;")
        il.addWidget(lbl_alt)
        il.addSpacing(20)

        form_w = QWidget()
        form_w.setStyleSheet("background:transparent;")
        form_w.setFixedWidth(320)
        lay_form = QVBoxLayout(form_w)
        lay_form.setContentsMargins(0, 0, 0, 0)
        lay_form.setSpacing(6)

        self.reg_k_turu = _etiketli_combo(
            lay_form, "Klinik Türü", [
                "Sadece Kedi / Köpek",
                "Çiftlik Hayvanları",
                "Egzotik Hayvanlar",
                "Tam Teşekküllü (Tümü)"
            ])

        tel_w = QWidget()
        tel_w.setStyleSheet("background:transparent;")
        tel_lay = QVBoxLayout(tel_w)
        tel_lay.setContentsMargins(0, 0, 0, 0)
        tel_lay.setSpacing(4)
        tel_lbl = QLabel("İş Telefonu")
        tel_lbl.setFont(QFont(ANA_FONT, 10))
        tel_lbl.setStyleSheet(f"color:{YAZI_GRI};background:transparent;")
        tel_lay.addWidget(tel_lbl)
        self.reg_k_tel = TelefonInput()
        tel_lay.addWidget(self.reg_k_tel)
        lay_form.addWidget(tel_w, alignment=Qt.AlignmentFlag.AlignCenter)

        lay_form.addSpacing(12)
        self.btn_kayit = _kayit_ol_butonu(self._on_kayit_clicked)
        lay_form.addWidget(self.btn_kayit, alignment=Qt.AlignmentFlag.AlignCenter)

        il.addWidget(form_w, alignment=Qt.AlignmentFlag.AlignCenter)
        il.addStretch()
        rv.addWidget(icerik, 1)

        self.btn_geri.clicked.connect(self._on_geri_clicked)
        self.reg_k_tel.returnPressed.connect(self.btn_kayit.click)

    def _on_geri_clicked(self):
        if self._geri_callback:
            self._geri_callback()

    def _on_kayit_clicked(self):
        if self._kayit_callback:
            self._kayit_callback()


# ══════════════════════════════════════════════════════════════════════════════
# Ana Kayıt Paneli
# ══════════════════════════════════════════════════════════════════════════════
class RegisterPanel(QWidget):
    ROL_HEKIM        = "Veteriner Hekim"
    ROL_SAHIP        = "Klinik Sahibi"
    SAHIP_ADIM_TEMEL = 1

    # Stack indeksleri
    IDX_HEKIM_1 = 0
    IDX_HEKIM_2 = 1
    IDX_SAHIP_1 = 2

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background:{BEYAZ};")
        self._kayit_callback       = None
        self._sahip_adim2_callback = None
        self._auth_window          = None

        self._secili_rol      = self.ROL_HEKIM
        self._sahip_adim      = self.SAHIP_ADIM_TEMEL
        self._sahip_ad        = ""
        self._sahip_soyad     = ""
        self._sahip_mail      = ""
        self._sahip_sifre     = ""

        # Hekim ara bilgiler
        self._hekim_ad       = ""
        self._hekim_soyad    = ""
        self._hekim_cinsiyet = "erkek"

        rv = QVBoxLayout(self)
        rv.setContentsMargins(0, 0, 0, 0)
        rv.setSpacing(0)

        spacer = QWidget()
        spacer.setFixedHeight(38)
        spacer.setStyleSheet("background:transparent;")
        rv.addWidget(spacer)

        icerik = QWidget()
        icerik.setStyleSheet("background:transparent;")
        il = QVBoxLayout(icerik)
        il.setContentsMargins(50, 0, 50, 10)
        il.setSpacing(0)

        # Logo + Giriş Yap
        ls = QHBoxLayout()
        lbl_logo = QLabel("VetSync Pro")
        lbl_logo.setFont(QFont(ANA_FONT, 16, QFont.Weight.Bold))
        lbl_logo.setStyleSheet(f"color:{MAVİ_ANA};font-style:italic;background:transparent;")
        self.btn_to_login = QPushButton("GİRİŞ YAP")
        self.btn_to_login.setFixedSize(100, 30)
        self.btn_to_login.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_to_login.setFont(QFont(ANA_FONT, 9, QFont.Weight.Bold))
        self.btn_to_login.setStyleSheet(f"""
QPushButton {{
    background:transparent;color:{MAVİ_ANA};
    border:1px solid {MAVİ_ANA};border-radius:6px;
}}
QPushButton:hover {{ background:#E3F2FD; }}
""")
        ls.addWidget(lbl_logo)
        ls.addStretch()
        ls.addWidget(self.btn_to_login)
        il.addLayout(ls)
        il.addSpacing(10)

        lbl_baslik = QLabel("Hesap Oluştur")
        lbl_baslik.setFont(QFont(ANA_FONT, 24, QFont.Weight.Bold))
        lbl_baslik.setStyleSheet(f"color:{KOYU_YAZI};background:transparent;")
        il.addWidget(lbl_baslik)
        il.addSpacing(2)

        lbl_alt = QLabel("Klinik yönetim sistemine kayıt olun")
        lbl_alt.setFont(QFont(ANA_FONT, 11))
        lbl_alt.setStyleSheet(f"color:{YAZI_GRI};background:transparent;")
        il.addWidget(lbl_alt)
        il.addSpacing(10)

        # Rol seçimi
        rol_w = QWidget()
        rol_w.setStyleSheet("background:transparent;")
        rol_w.setFixedWidth(320)
        rol_lay = QVBoxLayout(rol_w)
        rol_lay.setContentsMargins(0, 0, 0, 0)
        rol_btn_row = QHBoxLayout()
        rol_btn_row.setSpacing(10)
        rol_btn_row.setContentsMargins(0, 0, 0, 0)
        self.btn_hekim = QPushButton(" Veteriner Hekim")
        self.btn_sahip = QPushButton(" Klinik Sahibi")
        self.btn_hekim.setStyleSheet(CIN_SEL)
        self.btn_sahip.setStyleSheet(CIN_NORM)
        for b in (self.btn_hekim, self.btn_sahip):
            b.setFixedHeight(36)
            b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_hekim.clicked.connect(lambda: self._rol_sec(self.ROL_HEKIM))
        self.btn_sahip.clicked.connect(lambda: self._rol_sec(self.ROL_SAHIP))
        rol_btn_row.addWidget(self.btn_hekim, 1)
        rol_btn_row.addWidget(self.btn_sahip, 1)
        rol_lay.addLayout(rol_btn_row)
        il.addWidget(rol_w, alignment=Qt.AlignmentFlag.AlignCenter)
        il.addSpacing(10)

        # Stack
        self.stack_forms = QStackedWidget()
        self.stack_forms.setStyleSheet("background:transparent;")

        # Hekim Adım 1
        self.hekim_adim1 = HekimAdim1Panel()
        self.hekim_adim1._ileri_callback = self._on_hekim_ileri
        self.stack_forms.addWidget(self.hekim_adim1)   # idx 0

        # Hekim Adım 2
        self.hekim_adim2 = HekimAdim2Panel()
        self.hekim_adim2._geri_callback  = self._on_hekim_geri
        self.hekim_adim2._kayit_callback = self._on_kayit_clicked
        self.stack_forms.addWidget(self.hekim_adim2)   # idx 1

        # Klinik Sahibi Adım 1
        self.page_sahip, lay_sahip = _kayit_form_alani()
        lbl_sahip_adim = QLabel("Adım 1 / 3")
        lbl_sahip_adim.setFont(QFont(ANA_FONT, 10, QFont.Weight.Bold))
        lbl_sahip_adim.setStyleSheet(f"color:{MAVİ_ANA};background:transparent;")
        lay_sahip.addWidget(lbl_sahip_adim)
        lay_sahip.addSpacing(4)
        self.reg_ad          = _etiketli_entry(lay_sahip, "Ad",            "Adınız")
        self.reg_soyad       = _etiketli_entry(lay_sahip, "Soyad",         "Soyadınız")
        self.reg_mail_sahip  = _etiketli_entry(lay_sahip, "E-Posta Adresi","ornek@email.com")
        self.reg_sifre_sahip = _etiketli_entry(lay_sahip, "Şifre",         "••••••••", gizle=True)
        lay_sahip.addSpacing(12)
        self.btn_devam_sahip = _aksiyon_butonu("İLERİ →", self._on_sahip_devam)
        lay_sahip.addWidget(self.btn_devam_sahip, alignment=Qt.AlignmentFlag.AlignCenter)
        self.stack_forms.addWidget(self.page_sahip)    # idx 2

        self.stack_forms.setCurrentIndex(self.IDX_HEKIM_1)
        self.stack_forms.setFixedWidth(320)
        QTimer.singleShot(0, self._stack_yukseklik_guncelle)

        il.addWidget(self.stack_forms, alignment=Qt.AlignmentFlag.AlignCenter)
        il.addStretch()
        rv.addWidget(icerik, 1)

        # Enter geçişleri — sahip adım 1
        self.reg_ad.returnPressed.connect(lambda: self.reg_soyad.setFocus())
        self.reg_soyad.returnPressed.connect(lambda: self.reg_mail_sahip.setFocus())
        self.reg_mail_sahip.returnPressed.connect(lambda: self.reg_sifre_sahip.setFocus())
        self.reg_sifre_sahip.returnPressed.connect(self.btn_devam_sahip.click)

    # ── Hekim adım yönetimi ───────────────────────────────────────────────────
    def _on_hekim_ileri(self):
        ad    = self.hekim_adim1.reg_ad.text().strip()
        soyad = self.hekim_adim1.reg_soyad.text().strip()
        if not ad or not soyad:
            if self._auth_window:
                self._auth_window.bildirim_goster("Lütfen ad ve soyadınızı girin.", tur="hata")
            return
        self._hekim_ad       = ad
        self._hekim_soyad    = soyad
        self._hekim_cinsiyet = self.hekim_adim1._secili_cinsiyet
        self.stack_forms.setCurrentIndex(self.IDX_HEKIM_2)
        QTimer.singleShot(0, self._stack_yukseklik_guncelle)

    def _on_hekim_geri(self):
        self.stack_forms.setCurrentIndex(self.IDX_HEKIM_1)
        QTimer.singleShot(0, self._stack_yukseklik_guncelle)

    # ── Rol seçimi ────────────────────────────────────────────────────────────
    def _rol_sec(self, rol):
        self._secili_rol = rol
        hekim = rol == self.ROL_HEKIM
        self.btn_hekim.setStyleSheet(CIN_SEL  if hekim else CIN_NORM)
        self.btn_sahip.setStyleSheet(CIN_NORM if hekim else CIN_SEL)
        self.stack_forms.setCurrentIndex(self.IDX_HEKIM_1 if hekim else self.IDX_SAHIP_1)
        if not hekim:
            self._sahip_adim = self.SAHIP_ADIM_TEMEL
        if self._auth_window:
            self._auth_window.sahip_wizard_sifirla()
        QTimer.singleShot(0, self._stack_yukseklik_guncelle)

    def reset_sahip_flow(self):
        self._sahip_adim  = self.SAHIP_ADIM_TEMEL
        self._sahip_ad    = ""
        self._sahip_soyad = ""
        self._sahip_mail  = ""
        self._sahip_sifre = ""

    def validate_sahip_adim1(self):
        ad    = self.reg_ad.text().strip()
        soyad = self.reg_soyad.text().strip()
        mail  = self.reg_mail_sahip.text().strip()
        sifre = self.reg_sifre_sahip.text()
        if not ad or not soyad or not mail or not sifre:
            return False, "Lütfen tüm alanları doldurun."
        if len(sifre) < 4:
            return False, "Şifre en az 4 karakter olmalıdır."
        self._sahip_ad    = ad
        self._sahip_soyad = soyad
        self._sahip_mail  = mail
        self._sahip_sifre = sifre
        self._sahip_adim  = 2
        return True, ""

    def _stack_yukseklik_guncelle(self):
        current = self.stack_forms.currentWidget()
        lay = current.layout()
        lay.activate()
        h = lay.sizeHint().height()
        current.setFixedHeight(h)
        self.stack_forms.setFixedHeight(h)

    def _on_sahip_devam(self):
        ok, mesaj = self.validate_sahip_adim1()
        if not ok:
            if self._auth_window:
                self._auth_window.bildirim_goster(mesaj, tur="hata")
            return
        if self._sahip_adim2_callback:
            self._sahip_adim2_callback()

    def _on_kayit_clicked(self):
        if self._kayit_callback:
            self._kayit_callback()

    def bind_auth_window(self, auth_window):
        self._auth_window = auth_window