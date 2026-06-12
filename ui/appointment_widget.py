import os
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QScrollArea, QComboBox, QDateEdit,
    QTextEdit, QMessageBox, QDialog, QCheckBox, QTabWidget
)
from PyQt6.QtCore import Qt, QDate, QPoint, QTimer
from PyQt6.QtGui import QFont, QPixmap

import styles.theme as T
import database as db
from worker import Worker


TEAL     = "#30A7A1"
ALTIN    = "#B69240"
PANEL_BG = "#1A2942"
CARD_BG  = "#212D3A"
KOYU     = "#16202A"
SLATE    = "#305F82"
BEYAZ    = "#FFFFFF"
GRIS     = "#F1F1F1"


def _dark_input(placeholder, height=40):
    w = QLineEdit()
    w.setPlaceholderText(placeholder)
    w.setFixedHeight(height)
    w.setStyleSheet(f"""
QLineEdit {{
    background:{KOYU}; border:1.5px solid {SLATE};
    border-radius:8px; padding:0 12px;
    font-size:13px; color:{BEYAZ};
}}
QLineEdit:focus {{ border-color:{TEAL}; }}
""")
    return w


def _dlg_label(text):
    l = QLabel(text)
    l.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
    l.setStyleSheet(f"color:{GRIS}; background:transparent;")
    return l


def _tarih_input():
    w = QLineEdit()
    w.setPlaceholderText("GG.AA.YYYY")
    w.setFixedHeight(40)
    w.setMaxLength(10)
    w.setStyleSheet(f"""
QLineEdit {{
    background:{KOYU}; border:1.5px solid {SLATE};
    border-radius:8px; padding:0 12px;
    font-size:13px; color:{BEYAZ};
}}
QLineEdit:focus {{ border-color:{TEAL}; }}
""")
    busy = [False]

    def _fmt(text):
        if busy[0]: return
        busy[0] = True
        r = "".join(c for c in text if c.isdigit())[:8]
        s = ""
        if r:           s  = r[:2]
        if len(r) >= 3: s += "." + r[2:4]
        if len(r) >= 5: s += "." + r[4:8]
        w.setText(s)
        busy[0] = False

    w.textChanged.connect(_fmt)
    return w


def _get_klinik_id(user):
    """
    Kullanıcının klinik_id'sini döndürür.
    - Klinik Sahibi   → kendi id'si
    - Veteriner Hekim → klinik_sahibi_id (None ise bağımsız hekim)
    """
    if user.get("role") == "Klinik Sahibi":
        return user["id"]
    return user.get("klinik_sahibi_id")  # None → bağımsız hekim


# ══════════════════════════════════════════════════════════════════════════════
# Cinsiyet seçim
# ══════════════════════════════════════════════════════════════════════════════
class _CinsiyetSec(QWidget):
    SEL  = f"background:#30A7A1;color:white;border:none;border-radius:7px;padding:6px 0;"
    NORM = f"background:transparent;color:#F1F1F1;border:1px solid #305F82;border-radius:7px;padding:6px 0;"

    def __init__(self, default="erkek", parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        self._val = default
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)
        self.btn_e = QPushButton("♂ Erkek")
        self.btn_d = QPushButton("♀ Dişi")
        for b in (self.btn_e, self.btn_d):
            b.setFixedHeight(36)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_e.clicked.connect(lambda: self._sec("erkek"))
        self.btn_d.clicked.connect(lambda: self._sec("dişi"))
        lay.addWidget(self.btn_e)
        lay.addWidget(self.btn_d)
        self._sec(default)

    def _sec(self, v):
        self._val = v
        self.btn_e.setStyleSheet(
            f"QPushButton{{{self.SEL}}}" if v == "erkek"
            else f"QPushButton{{{self.NORM}}}")
        self.btn_d.setStyleSheet(
            f"QPushButton{{{self.SEL}}}" if v == "dişi"
            else f"QPushButton{{{self.NORM}}}")

    def deger(self):
        return self._val


class MusteriDuzenleDialog(QDialog):
    def __init__(self, customer, parent=None):
        super().__init__(parent)
        self.customer = customer
        self._deleted = False
        self.setWindowTitle("Müşteri Düzenle")
        self.setFixedWidth(420)
        self.setModal(True)
        self.setStyleSheet(f"background:{CARD_BG};")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(14)

        title = QLabel("✏️ Müşteri Bilgilerini Düzenle")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{ALTIN}; background:transparent;")
        lay.addWidget(title)

        sep = QFrame(); sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{SLATE};")
        lay.addWidget(sep)

        lay.addWidget(_dlg_label("Ad Soyad"))
        self.inp_name = _dark_input("")
        self.inp_name.setText(self.customer.get("name", ""))
        lay.addWidget(self.inp_name)

        lay.addWidget(_dlg_label("Telefon"))
        self.inp_phone = _dark_input("")
        self.inp_phone.setText(self.customer.get("phone", ""))
        lay.addWidget(self.inp_phone)

        lay.addWidget(_dlg_label("Adres"))
        self.inp_address = _dark_input("")
        self.inp_address.setText(self.customer.get("address", ""))
        lay.addWidget(self.inp_address)

        lay.addSpacing(6)
        btn_row = QHBoxLayout(); btn_row.setSpacing(10)

        btn_save = QPushButton("💾 Kaydet")
        btn_save.setFixedHeight(42)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        btn_save.setStyleSheet(f"""
QPushButton {{ background:{TEAL};color:white;border:none;border-radius:8px; }}
QPushButton:hover {{ background:#27908B; }}
""")
        btn_save.clicked.connect(self._save)

        btn_del = QPushButton("🗑 Müşteriyi Sil")
        btn_del.setFixedHeight(42)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        btn_del.setStyleSheet(f"""
QPushButton {{ background:#7F1D1D;color:white;border:none;border-radius:8px; }}
QPushButton:hover {{ background:#DC2626; }}
""")
        btn_del.clicked.connect(self._delete)

        btn_cancel = QPushButton("İptal")
        btn_cancel.setFixedHeight(42)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        btn_cancel.setStyleSheet(f"""
QPushButton {{ background:{SLATE};color:white;border:none;border-radius:8px; }}
QPushButton:hover {{ background:#3D6D8A; }}
""")
        btn_cancel.clicked.connect(self.reject)

        btn_row.addWidget(btn_save, 1)
        btn_row.addWidget(btn_del, 1)
        btn_row.addWidget(btn_cancel)
        lay.addLayout(btn_row)

        self.msg = QLabel("")
        self.msg.setStyleSheet("color:#EF4444;background:transparent;")
        self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.msg)

    def _save(self):
        name    = self.inp_name.text().strip()
        phone   = self.inp_phone.text().strip()
        address = self.inp_address.text().strip()
        if not name:
            self.msg.setText("❌ Ad zorunludur.")
            return
        cid = self.customer["id"]

        def _do():
            db.update_customer(cid, name, phone, address)

        def _done(_):
            self.accept()

        def _err(e):
            self.msg.setText(f"❌ Hata: {e}")

        self._w = Worker(_do)
        self._w.result.connect(_done)
        self._w.error.connect(_err)
        self._w.start()

    def _delete(self):
        reply = QMessageBox.question(
            self, "Müşteriyi Sil",
            f"'{self.customer['name']}' ve tüm kayıtları silinecek!\nEmin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        cid = self.customer["id"]

        def _do():
            db.delete_customer(cid)

        def _done(_):
            self._deleted = True
            self.accept()

        def _err(e):
            self.msg.setText(f"❌ Hata: {e}")

        self._w = Worker(_do)
        self._w.result.connect(_done)
        self._w.error.connect(_err)
        self._w.start()


class DetayliBilgiDialog(QDialog):
    def __init__(self, animal, parent=None):
        super().__init__(parent)
        self.animal = animal
        self.setWindowTitle(f"Detaylı Bilgi — {animal.get('name','')}")
        self.setFixedSize(560, 520)
        self.setModal(True)
        self.setStyleSheet(f"background:{CARD_BG};")
        self._build()
        self._load()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        title = QLabel(f"🐾 {self.animal.get('name','')} — Geçmiş Kayıtlar")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{ALTIN}; background:transparent;")
        lay.addWidget(title)

        sep = QFrame(); sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{SLATE};")
        lay.addWidget(sep)

        asi_hdr = QLabel("💉 Yapılan Aşılar")
        asi_hdr.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        asi_hdr.setStyleSheet(f"color:{TEAL}; background:transparent;")
        lay.addWidget(asi_hdr)

        self.asi_scroll = QScrollArea()
        self.asi_scroll.setFixedHeight(160)
        self.asi_scroll.setWidgetResizable(True)
        self.asi_scroll.setStyleSheet(
            "QScrollArea{border:1px solid #305F82;border-radius:8px;background:transparent;}")
        self.asi_container = QWidget()
        self.asi_container.setStyleSheet("background:transparent;")
        self.asi_vlay = QVBoxLayout(self.asi_container)
        self.asi_vlay.setContentsMargins(8, 8, 8, 8)
        self.asi_vlay.setSpacing(4)
        self.asi_vlay.addStretch()
        self.asi_scroll.setWidget(self.asi_container)
        lay.addWidget(self.asi_scroll)

        rdv_hdr = QLabel("📅 Geçmiş Randevular")
        rdv_hdr.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        rdv_hdr.setStyleSheet(f"color:{ALTIN}; background:transparent;")
        lay.addWidget(rdv_hdr)

        self.rdv_scroll = QScrollArea()
        self.rdv_scroll.setWidgetResizable(True)
        self.rdv_scroll.setStyleSheet(
            "QScrollArea{border:1px solid #305F82;border-radius:8px;background:transparent;}")
        self.rdv_container = QWidget()
        self.rdv_container.setStyleSheet("background:transparent;")
        self.rdv_vlay = QVBoxLayout(self.rdv_container)
        self.rdv_vlay.setContentsMargins(8, 8, 8, 8)
        self.rdv_vlay.setSpacing(4)
        self.rdv_vlay.addStretch()
        self.rdv_scroll.setWidget(self.rdv_container)
        lay.addWidget(self.rdv_scroll, 1)

        btn_close = QPushButton("Kapat")
        btn_close.setFixedHeight(40)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        btn_close.setStyleSheet(f"""
QPushButton {{ background:{SLATE};color:white;border:none;border-radius:8px; }}
QPushButton:hover {{ background:{TEAL}; }}
""")
        btn_close.clicked.connect(self.accept)
        lay.addWidget(btn_close)

    def _load(self):
        def _fetch():
            return db.get_appointments_by_animal(self.animal["id"])

        def _done(rows):
            asi_turleri = {"Aşı", "Kuduz Aşısı", "Karma Aşı",
                           "Parazit İlacı", "İç-Dış Parazit"}
            asiler = [r for r in rows if r.get("islem_turu") in asi_turleri]

            while self.asi_vlay.count() > 1:
                item = self.asi_vlay.takeAt(0)
                if item.widget(): item.widget().deleteLater()

            if not asiler:
                lbl = QLabel("Kayıtlı aşı bulunmuyor.")
                lbl.setStyleSheet(f"color:{GRIS};background:transparent;")
                lbl.setFont(QFont("Segoe UI", 11))
                self.asi_vlay.insertWidget(0, lbl)
            else:
                for i, a in enumerate(asiler):
                    tarih = a.get("randevu_tarihi", "")[:10]
                    tur   = a.get("islem_turu", "—")
                    durum = a.get("durum", "")
                    renk  = TEAL if durum == "completed" else "#F59E0B"
                    s = QLabel(
                        f"💉 {tarih}  ·  {tur}  "
                        f"[{'✅' if durum=='completed' else '⏳'}]")
                    s.setFont(QFont("Segoe UI", 11))
                    s.setStyleSheet(f"color:{renk};background:transparent;")
                    self.asi_vlay.insertWidget(i, s)

            while self.rdv_vlay.count() > 1:
                item = self.rdv_vlay.takeAt(0)
                if item.widget(): item.widget().deleteLater()

            if not rows:
                lbl = QLabel("Geçmiş randevu bulunmuyor.")
                lbl.setStyleSheet(f"color:{GRIS};background:transparent;")
                lbl.setFont(QFont("Segoe UI", 11))
                self.rdv_vlay.insertWidget(0, lbl)
            else:
                for i, r in enumerate(rows):
                    tarih = r.get("randevu_tarihi", "")[:10]
                    tur   = r.get("islem_turu", "—")
                    durum = r.get("durum", "pending")
                    not_  = r.get("notlar", "")
                    icon  = {"completed": "✅", "cancelled": "❌",
                             "pending": "⏳"}.get(durum, "⏳")
                    text  = f"{icon} {tarih}  ·  {tur}"
                    if not_: text += f"  ·  📝 {not_}"
                    s = QLabel(text)
                    s.setFont(QFont("Segoe UI", 11))
                    s.setWordWrap(True)
                    renk = {"completed": TEAL, "cancelled": "#EF4444",
                            "pending": GRIS}.get(durum, GRIS)
                    s.setStyleSheet(f"color:{renk};background:transparent;")
                    self.rdv_vlay.insertWidget(i, s)

        self._worker = Worker(_fetch)
        self._worker.result.connect(_done)
        self._worker.error.connect(
            lambda e: print(f"[DetayliBilgi] Hata: {e}"))
        self._worker.start()


# ══════════════════════════════════════════════════════════════════════════════
# Hayvan Yönetim Dialog
# ══════════════════════════════════════════════════════════════════════════════
class HayvanYonetimDialog(QDialog):
    def __init__(self, animal, customer_id, parent=None):
        super().__init__(parent)
        self.animal      = animal
        self.customer_id = customer_id
        self._deleted    = False
        self.setWindowTitle("Hayvan Yönetimi")
        self.setFixedWidth(500)
        self.setModal(True)
        self.setStyleSheet(f"background:{CARD_BG};")
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
QTabWidget::pane {{ border: none; background: {CARD_BG}; }}
QTabBar::tab {{
    background: {KOYU}; color: {GRIS};
    padding: 10px 28px; font-family: 'Segoe UI';
    font-size: 12px; font-weight: 600; border: none;
}}
QTabBar::tab:selected {{ background: {TEAL}; color: white; }}
QTabBar::tab:hover:!selected {{ background: {SLATE}; }}
""")
        self.tabs.addTab(self._build_duzenle_tab(), "✏️  Hayvanı Düzenle")
        self.tabs.addTab(self._build_ekle_tab(),    "🐾  Yeni Hayvan Ekle")
        outer.addWidget(self.tabs)

    def _build_duzenle_tab(self):
        w = QWidget()
        w.setStyleSheet(f"background:{CARD_BG};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        a = self.animal

        row1 = QHBoxLayout(); row1.setSpacing(10)
        lay.addWidget(_dlg_label("Ad / Küpe No"))
        self.d_name = _dark_input("Hayvan Adı")
        self.d_name.setText(a.get("name", ""))
        self.d_tag  = _dark_input("Küpe No")
        self.d_tag.setText(a.get("tag_no", ""))
        row1.addWidget(self.d_name, 1)
        row1.addWidget(self.d_tag, 1)
        lay.addLayout(row1)

        lay.addWidget(_dlg_label("Tür & Irk"))
        sp  = a.get("species", "")
        br  = a.get("breed", "")
        self.d_species = _dark_input("Örn: Köpek - Golden")
        self.d_species.setText(f"{sp}{' - '+br if br else ''}")
        lay.addWidget(self.d_species)

        row2 = QHBoxLayout(); row2.setSpacing(10)
        lay.addWidget(_dlg_label("Doğum Tarihi / Ağırlık (kg)"))
        self.d_bdate  = _tarih_input()
        self.d_bdate.setText(a.get("birth_date", ""))
        self.d_weight = _dark_input("Ağırlık (kg)")
        self.d_weight.setText(
            str(a["agirlik_kg"]) if a.get("agirlik_kg") else "")
        row2.addWidget(self.d_bdate, 1)
        row2.addWidget(self.d_weight, 1)
        lay.addLayout(row2)

        lay.addWidget(_dlg_label("Cinsiyet"))
        self.d_cin = _CinsiyetSec(a.get("cinsiyet", "erkek"))
        lay.addWidget(self.d_cin)

        self.d_kisir = QCheckBox("Kısırlaştırıldı")
        self.d_kisir.setChecked(a.get("kisirlestirildi", False))
        self.d_kisir.setStyleSheet(
            f"color:{GRIS};background:transparent;font-size:12px;")
        lay.addWidget(self.d_kisir)

        lay.addWidget(_dlg_label("Notlar"))
        self.d_notes = _dark_input("Notlar")
        self.d_notes.setText(a.get("notes", ""))
        lay.addWidget(self.d_notes)

        lay.addSpacing(6)
        btn_row = QHBoxLayout(); btn_row.setSpacing(10)

        btn_save = QPushButton("💾 Kaydet")
        btn_save.setFixedHeight(42)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        btn_save.setStyleSheet(f"""
QPushButton {{ background:{TEAL};color:white;border:none;border-radius:8px; }}
QPushButton:hover {{ background:#27908B; }}
""")
        btn_save.clicked.connect(self._save_duzenle)

        btn_del = QPushButton("🗑 Sil")
        btn_del.setFixedHeight(42)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        btn_del.setStyleSheet(f"""
QPushButton {{ background:#7F1D1D;color:white;border:none;border-radius:8px; }}
QPushButton:hover {{ background:#DC2626; }}
""")
        btn_del.clicked.connect(self._delete)

        btn_detay = QPushButton("📋 Geçmiş")
        btn_detay.setFixedHeight(42)
        btn_detay.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_detay.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        btn_detay.setStyleSheet(f"""
QPushButton {{ background:{ALTIN};color:white;border:none;border-radius:8px; }}
QPushButton:hover {{ background:#9A7A34; }}
""")
        btn_detay.clicked.connect(self._open_detay)

        btn_row.addWidget(btn_save, 1)
        btn_row.addWidget(btn_del)
        btn_row.addWidget(btn_detay)
        lay.addLayout(btn_row)

        self.d_msg = QLabel("")
        self.d_msg.setStyleSheet("color:#EF4444;background:transparent;")
        self.d_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.d_msg)

        return w

    def _build_ekle_tab(self):
        w = QWidget()
        w.setStyleSheet(f"background:{CARD_BG};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        row1 = QHBoxLayout(); row1.setSpacing(10)
        lay.addWidget(_dlg_label("Ad / Küpe No"))
        self.e_name = _dark_input("Hayvan Adı")
        self.e_tag  = _dark_input("Küpe No")
        row1.addWidget(self.e_name, 1)
        row1.addWidget(self.e_tag, 1)
        lay.addLayout(row1)

        lay.addWidget(_dlg_label("Tür & Irk"))
        self.e_species = _dark_input("Örn: Kedi - Tekir")
        lay.addWidget(self.e_species)

        row2 = QHBoxLayout(); row2.setSpacing(10)
        lay.addWidget(_dlg_label("Doğum Tarihi / Ağırlık (kg)"))
        self.e_bdate  = _tarih_input()
        self.e_weight = _dark_input("Ağırlık (kg)")
        row2.addWidget(self.e_bdate, 1)
        row2.addWidget(self.e_weight, 1)
        lay.addLayout(row2)

        lay.addWidget(_dlg_label("Cinsiyet"))
        self.e_cin = _CinsiyetSec("erkek")
        lay.addWidget(self.e_cin)

        self.e_kisir = QCheckBox("Kısırlaştırıldı")
        self.e_kisir.setStyleSheet(
            f"color:{GRIS};background:transparent;font-size:12px;")
        lay.addWidget(self.e_kisir)

        lay.addWidget(_dlg_label("Notlar"))
        self.e_notes = _dark_input("Notlar (isteğe bağlı)")
        lay.addWidget(self.e_notes)

        lay.addSpacing(6)
        btn_ekle = QPushButton("🐾 Hayvanı Kaydet")
        btn_ekle.setFixedHeight(44)
        btn_ekle.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ekle.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        btn_ekle.setStyleSheet(f"""
QPushButton {{ background:{TEAL};color:white;border:none;border-radius:8px; }}
QPushButton:hover {{ background:#27908B; }}
""")
        btn_ekle.clicked.connect(self._save_ekle)
        lay.addWidget(btn_ekle)

        self.e_msg = QLabel("")
        self.e_msg.setStyleSheet("background:transparent;")
        self.e_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.e_msg)

        lay.addStretch()
        return w

    # ── Aksiyonlar ────────────────────────────────────────────────────────────
    def _save_duzenle(self):
        if not self.animal.get("id"):
            self.d_msg.setText("❌ Düzenlenecek hayvan seçilmedi.")
            return

        name  = self.d_name.text().strip()
        tag   = self.d_tag.text().strip()
        sp_br = self.d_species.text().strip()
        bdate = self.d_bdate.text().strip()
        notes = self.d_notes.text().strip()
        w_raw = self.d_weight.text().strip().replace(",", ".")
        try:
            agirlik = float(w_raw) if w_raw else None
        except ValueError:
            self.d_msg.setText("❌ Ağırlık sayısal olmalıdır.")
            return
        if not name:
            self.d_msg.setText("❌ Hayvan adı zorunludur.")
            return

        aid      = self.animal["id"]
        cinsiyet = self.d_cin.deger()
        kisir    = self.d_kisir.isChecked()

        def _do():
            db.update_animal(aid, name, tag, sp_br, bdate, notes,
                             cinsiyet=cinsiyet, agirlik_kg=agirlik,
                             kisirlestirildi=kisir)

        self._dw = Worker(_do)
        self._dw.result.connect(lambda _: self.accept())
        self._dw.error.connect(lambda e: self.d_msg.setText(f"❌ Hata: {e}"))
        self._dw.start()

    def _delete(self):
        if not self.animal.get("id"):
            self.d_msg.setText("❌ Silinecek hayvan seçilmedi.")
            return

        reply = QMessageBox.question(
            self, "Hayvanı Sil",
            f"'{self.animal['name']}' ve tüm randevuları silinecek!\nEmin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        aid = self.animal["id"]

        def _do():
            db.delete_animal(aid)

        def _done(_):
            self._deleted = True
            self.accept()

        self._delw = Worker(_do)
        self._delw.result.connect(_done)
        self._delw.error.connect(lambda e: self.d_msg.setText(f"❌ Hata: {e}"))
        self._delw.start()

    def _open_detay(self):
        if not self.animal.get("id"):
            return
        dlg = DetayliBilgiDialog(self.animal, self)
        dlg.exec()

    def _save_ekle(self):
        name  = self.e_name.text().strip()
        tag   = self.e_tag.text().strip()
        sp_br = self.e_species.text().strip()
        bdate = self.e_bdate.text().strip()
        notes = self.e_notes.text().strip()
        w_raw = self.e_weight.text().strip().replace(",", ".")
        try:
            agirlik = float(w_raw) if w_raw else None
        except ValueError:
            self.e_msg.setStyleSheet("color:#EF4444;background:transparent;")
            self.e_msg.setText("❌ Ağırlık sayısal olmalıdır.")
            return
        if not name:
            self.e_msg.setStyleSheet("color:#EF4444;background:transparent;")
            self.e_msg.setText("❌ Hayvan adı zorunludur.")
            return
        cid      = self.customer_id
        cinsiyet = self.e_cin.deger()
        kisir    = self.e_kisir.isChecked()

        def _do():
            db.add_animal(cid, name, tag, sp_br, bdate, notes,
                          cinsiyet=cinsiyet, agirlik_kg=agirlik,
                          kisirlestirildi=kisir)

        def _done(_):
            self.e_msg.setStyleSheet(
                f"color:{TEAL};font-weight:600;background:transparent;")
            self.e_msg.setText(f"✅ '{name}' başarıyla eklendi!")
            for w in (self.e_name, self.e_tag, self.e_species,
                      self.e_bdate, self.e_weight, self.e_notes):
                w.clear()
            self.e_cin._sec("erkek")
            self.e_kisir.setChecked(False)
            QTimer.singleShot(800, self.accept)

        def _err(e):
            self.e_msg.setStyleSheet("color:#EF4444;background:transparent;")
            self.e_msg.setText(f"❌ Hata: {e}")

        self._ew = Worker(_do)
        self._ew.result.connect(_done)
        self._ew.error.connect(_err)
        self._ew.start()


# ══════════════════════════════════════════════════════════════════════════════
# Hayvan Bilgi Popup
# ══════════════════════════════════════════════════════════════════════════════
class HastaBilgiPopup(QDialog):
    def __init__(self, animal, parent=None):
        super().__init__(parent)
        self.animal = animal
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(300)
        self._pinned = False
        self._build(animal)

    def _build(self, a):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setStyleSheet(f"""
QFrame {{
    background:#1C2B3A; border-radius:12px;
    border:1.5px solid {ALTIN};
}}
QLabel {{ background:transparent; border:none; }}
""")
        cv = QVBoxLayout(card)
        cv.setContentsMargins(18, 16, 18, 16)
        cv.setSpacing(8)

        title = QLabel(f"🐾 Hasta — {a.get('name','—')}")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{ALTIN};")
        cv.addWidget(title)

        sep = QFrame(); sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{SLATE};")
        cv.addWidget(sep)

        def _row(label, value):
            w = QWidget(); w.setStyleSheet("background:transparent;")
            hl = QHBoxLayout(w)
            hl.setContentsMargins(0, 0, 0, 0); hl.setSpacing(6)
            lbl = QLabel(label)
            lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            lbl.setStyleSheet(f"color:{GRIS};")
            val = QLabel(str(value) if value else "—")
            val.setFont(QFont("Segoe UI", 11))
            val.setStyleSheet(f"color:{BEYAZ};")
            val.setWordWrap(True)
            hl.addWidget(lbl); hl.addWidget(val, 1)
            return w

        sp  = a.get('species', '')
        br  = a.get('breed', '')
        cin = "♂ Erkek" if a.get('cinsiyet','erkek') == "erkek" else "♀ Dişi"
        ag  = f"{a['agirlik_kg']} kg" if a.get('agirlik_kg') else "—"
        ks  = "✅ Evet" if a.get('kisirlestirildi') else "❌ Hayır"

        cv.addWidget(_row("Tür / Irk:",      f"{sp}{' - '+br if br else ''}"))
        cv.addWidget(_row("Cinsiyet:",        cin))
        cv.addWidget(_row("Ağırlık:",         ag))
        cv.addWidget(_row("Kısırlaştırıldı:", ks))
        cv.addWidget(_row("Doğum Tarihi:",    a.get('birth_date','—')))
        cv.addWidget(_row("Küpe No:",         a.get('tag_no','—')))
        cv.addWidget(_row("Notlar:",          a.get('notes','—')))

        cv.addSpacing(4)

        btn_detay = QPushButton("📋 Detaylı Bilgiler")
        btn_detay.setFixedHeight(34)
        btn_detay.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_detay.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        btn_detay.setStyleSheet(f"""
QPushButton {{ background:{ALTIN};color:white;border:none;border-radius:7px; }}
QPushButton:hover {{ background:#9A7A34; }}
""")
        btn_detay.clicked.connect(self._open_detay)
        cv.addWidget(btn_detay)

        btn_close = QPushButton("Kapat")
        btn_close.setFixedHeight(34)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        btn_close.setStyleSheet(f"""
QPushButton {{ background:{SLATE};color:white;border:none;border-radius:7px; }}
QPushButton:hover {{ background:{TEAL}; }}
""")
        btn_close.clicked.connect(self._force_close)
        cv.addWidget(btn_close)

        outer.addWidget(card)

    def _open_detay(self):
        DetayliBilgiDialog(self.animal, self.parent()).exec()

    def _force_close(self):
        self._pinned = False
        self.close()


# ══════════════════════════════════════════════════════════════════════════════
# Hayvan bilgi butonu (hover popup)
# ══════════════════════════════════════════════════════════════════════════════
class HayvanBilgiButon(QPushButton):
    def __init__(self, parent=None):
        super().__init__("🐾", parent)
        self.setFixedSize(46, 46)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(QFont("Segoe UI Emoji", 16))
        self.setToolTip("Hasta Bilgisini Görüntüle")
        self.setStyleSheet(f"""
QPushButton {{
    background:{SLATE};color:{BEYAZ};
    border:1.5px solid {ALTIN};border-radius:10px;
}}
QPushButton:hover {{ background:{ALTIN}; }}
""")
        self._popup       = None
        self._get_animal  = None
        self._leave_timer = QTimer()
        self._leave_timer.setSingleShot(True)
        self._leave_timer.timeout.connect(self._try_close)

    def enterEvent(self, e):
        super().enterEvent(e)
        self._leave_timer.stop()
        self._open_popup()

    def leaveEvent(self, e):
        super().leaveEvent(e)
        if self._popup and not self._popup._pinned:
            self._leave_timer.start(200)

    def _try_close(self):
        if self._popup and not self._popup._pinned \
                and not self._popup.underMouse():
            self._popup.close()
            self._popup = None

    def _open_popup(self):
        if not self._get_animal:
            return
        animal = self._get_animal()
        if not animal:
            return
        if self._popup and self._popup.isVisible():
            return
        if self._popup:
            self._popup.close()
        self._popup = HastaBilgiPopup(animal, self.window())
        self._popup.adjustSize()
        bg = self.mapToGlobal(QPoint(0, 0))
        self._popup.move(
            bg.x() - self._popup.width() - 8,
            bg.y() - self._popup.height() // 2 + self.height() // 2)
        self._popup.show()

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        if self._popup and self._popup.isVisible():
            self._popup._pinned = True
            self._leave_timer.stop()
        else:
            self._open_popup()
            if self._popup:
                self._popup._pinned = True


# ══════════════════════════════════════════════════════════════════════════════
# Müşteri kartı
# ══════════════════════════════════════════════════════════════════════════════
class CustomerCard(QFrame):
    def __init__(self, customer, on_select):
        super().__init__()
        self.setStyleSheet(f"""
QFrame {{
    background:#303C4B; border-radius:10px; border:1px solid {ALTIN};
}}
QLabel {{ background:transparent; }}
""")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 12, 12)

        info = QVBoxLayout(); info.setSpacing(4)

        name_row = QHBoxLayout()
        name_row.setSpacing(8); name_row.setContentsMargins(0, 0, 0, 0)
        k_lbl = QLabel()
        k_lbl.setFixedSize(20, 20)
        k_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        k_lbl.setStyleSheet("background:transparent;border:none;")
        if os.path.exists("assets/Kullanici.png"):
            k_lbl.setPixmap(QPixmap("assets/Kullanici.png").scaled(
                20, 20, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))
        else:
            k_lbl.setText("👤")
        name_lbl = QLabel(customer['name'])
        name_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        name_lbl.setStyleSheet(
            f"color:{BEYAZ};border:none;background:transparent;")
        name_row.addWidget(k_lbl); name_row.addWidget(name_lbl)
        name_row.addStretch()
        name_w = QWidget(); name_w.setStyleSheet("background:transparent;")
        name_w.setLayout(name_row)

        phone_lbl = QLabel(f"📞 {customer.get('phone','—')}")
        phone_lbl.setFont(QFont("Segoe UI", 12))
        phone_lbl.setStyleSheet(f"color:{GRIS};border:none;")

        info.addWidget(name_w)
        info.addWidget(phone_lbl)

        btn = QPushButton("Seç")
        btn.setFixedSize(64, 34)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        btn.setStyleSheet(f"""
QPushButton {{ background:{TEAL};color:{BEYAZ};border:none;border-radius:8px; }}
QPushButton:hover {{ background:#27908B; }}
""")
        btn.clicked.connect(lambda: on_select(customer))
        layout.addLayout(info, 1)
        layout.addWidget(btn)


# ══════════════════════════════════════════════════════════════════════════════
# Ana Widget
# ══════════════════════════════════════════════════════════════════════════════
class AppointmentWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user              = user
        self.selected_customer = None
        self._animals          = []
        # ── Kullanıcının klinik_id'si (None → bağımsız hekim) ────────────────
        self._klinik_id        = _get_klinik_id(user)
        self.setStyleSheet(f"background-color:{PANEL_BG};")
        self._build_ui()
        self._load_customers()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 30, 30, 30)
        root.setSpacing(20)

        title = QLabel("Randevu ve İşlem Merkezi")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color:#000000; background:transparent;")
        root.addWidget(title)

        content = QHBoxLayout(); content.setSpacing(20)

        # ── Sol panel ─────────────────────────────────────────────────────
        left_panel = QFrame()
        left_panel.setStyleSheet(f"""
QFrame {{ background:{CARD_BG};border-radius:14px;border:1px solid {ALTIN}; }}
""")
        left_panel.setMinimumWidth(360); left_panel.setMaximumWidth(420)
        lv = QVBoxLayout(left_panel)
        lv.setContentsMargins(16, 16, 16, 16); lv.setSpacing(12)

        shdr = QHBoxLayout(); shdr.setSpacing(8)
        shdr.setContentsMargins(0, 0, 0, 0)
        si = QLabel()
        si.setFixedSize(32, 32)
        si.setAlignment(Qt.AlignmentFlag.AlignCenter)
        si.setStyleSheet("background:transparent;border:none;")
        if os.path.exists("assets/Search.png"):
            si.setPixmap(QPixmap("assets/Search.png").scaled(
                32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))
        else:
            si.setText("🔍")
        st = QLabel("Müşteri Ara")
        st.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        st.setStyleSheet(f"color:{BEYAZ};background:transparent;border:none;")
        shdr.addWidget(si); shdr.addWidget(st); shdr.addStretch()
        shdr_w = QWidget(); shdr_w.setStyleSheet("background:transparent;")
        shdr_w.setLayout(shdr)

        srow = QHBoxLayout(); srow.setSpacing(8)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("İsim veya Telefon Numarası")
        self.search_input.setFixedHeight(44)
        self.search_input.setStyleSheet(f"""
QLineEdit {{
    background:{KOYU};border:1.5px solid {SLATE};border-radius:10px;
    padding:0 14px;font-size:13px;color:{BEYAZ};
}}
QLineEdit:focus {{ border-color:{TEAL}; }}
""")
        self.search_input.textChanged.connect(self._load_customers)
        sbtn = QPushButton("Ara")
        sbtn.setFixedSize(64, 44)
        sbtn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        sbtn.setStyleSheet(f"""
QPushButton {{ background:{TEAL};color:{BEYAZ};border:none;border-radius:10px; }}
QPushButton:hover {{ background:#27908B; }}
""")
        sbtn.clicked.connect(self._load_customers)
        srow.addWidget(self.search_input, 1); srow.addWidget(sbtn)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        self.cust_container = QWidget()
        self.cust_container.setStyleSheet("background:transparent;")
        self.cust_layout = QVBoxLayout(self.cust_container)
        self.cust_layout.setContentsMargins(0, 0, 0, 0)
        self.cust_layout.setSpacing(8)
        self.cust_layout.addStretch()
        scroll.setWidget(self.cust_container)

        lv.addWidget(shdr_w)
        lv.addLayout(srow)
        lv.addWidget(scroll, 1)

        # ── Sağ panel ─────────────────────────────────────────────────────
        right_panel = QFrame()
        right_panel.setStyleSheet(f"""
QFrame {{ background:{CARD_BG};border-radius:14px;border:1px solid {ALTIN}; }}
""")
        rv = QVBoxLayout(right_panel)
        rv.setContentsMargins(24, 24, 24, 24); rv.setSpacing(16)

        self.form_title = QLabel("📋 Randevu Oluşturma")
        self.form_title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        self.form_title.setStyleSheet(f"color:{ALTIN};background:transparent;")

        self.form_placeholder = QLabel("Lütfen sol taraftan bir müşteri seçin.")
        self.form_placeholder.setFont(QFont("Segoe UI", 13))
        self.form_placeholder.setStyleSheet(
            f"color:{GRIS};background:transparent;")
        self.form_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.sel_info = QLabel("")
        self.sel_info.setFont(QFont("Segoe UI", 13))
        self.sel_info.setStyleSheet(f"""
background:{SLATE};border-radius:8px;
padding:10px 14px;color:{BEYAZ};border:none;
""")
        self.sel_info.setWordWrap(True)
        self.sel_info.hide()

        self.btn_musteri_duzenle = QPushButton("✏️")
        self.btn_musteri_duzenle.setFixedSize(40, 40)
        self.btn_musteri_duzenle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_musteri_duzenle.setToolTip("Müşteri Bilgilerini Düzenle / Sil")
        self.btn_musteri_duzenle.setStyleSheet(f"""
QPushButton {{
    background:{ALTIN};color:{BEYAZ};
    border:none;border-radius:8px;font-size:16px;
}}
QPushButton:hover {{ background:#9A7A34; }}
""")
        self.btn_musteri_duzenle.clicked.connect(self._musteri_duzenle)
        self.btn_musteri_duzenle.hide()

        musteri_row = QHBoxLayout()
        musteri_row.setSpacing(8); musteri_row.setContentsMargins(0, 0, 0, 0)
        musteri_row.addWidget(self.sel_info, 1)
        musteri_row.addWidget(self.btn_musteri_duzenle)

        def _lbl(text):
            l = QLabel(text)
            l.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
            l.setStyleSheet(f"color:{GRIS};background:transparent;border:none;")
            return l

        combo_style = f"""
QComboBox {{
    background:{KOYU};border:1.5px solid {SLATE};
    border-radius:10px;padding:0 14px;
    font-size:13px;color:{BEYAZ};
}}
QComboBox:focus {{ border-color:{TEAL}; }}
QComboBox::drop-down {{ border:none;width:28px; }}
QComboBox::down-arrow {{
    image:url(assets/down.png);width:14px;height:14px;
}}
QComboBox QAbstractItemView {{
    background:{CARD_BG};color:{BEYAZ};
    selection-background-color:{TEAL};
}}
"""
        self.animal_combo = QComboBox()
        self.animal_combo.setFixedHeight(46)
        self.animal_combo.setStyleSheet(combo_style)

        animal_row = QHBoxLayout()
        animal_row.setSpacing(8); animal_row.setContentsMargins(0, 0, 0, 0)
        animal_row.addWidget(self.animal_combo, 1)

        self.btn_hayvan_bilgi = HayvanBilgiButon()
        self.btn_hayvan_bilgi._get_animal = self._get_selected_animal

        self.btn_hayvan_yonetim = QPushButton("✏️")
        self.btn_hayvan_yonetim.setFixedSize(46, 46)
        self.btn_hayvan_yonetim.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_hayvan_yonetim.setToolTip("Hayvan Düzenle / Yeni Ekle")
        self.btn_hayvan_yonetim.setStyleSheet(f"""
QPushButton {{
    background:{ALTIN};color:{BEYAZ};
    border:none;border-radius:10px;font-size:16px;
}}
QPushButton:hover {{ background:#9A7A34; }}
""")
        self.btn_hayvan_yonetim.clicked.connect(self._hayvan_yonetim)
        animal_row.addWidget(self.btn_hayvan_bilgi)
        animal_row.addWidget(self.btn_hayvan_yonetim)

        self.type_combo = QComboBox()
        self.type_combo.setFixedHeight(46)
        self.type_combo.setStyleSheet(combo_style)
        self.type_combo.setEditable(True)
        self.type_combo.addItems([
            "Kuduz Aşısı", "Karma Aşı", "Parazit İlacı",
            "İç-Dış Parazit", "Aşı", "Muayene",
            "Kısırlaştırma", "Diş Taşı", "Diğer"
        ])

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setMinimumDate(QDate.currentDate())
        self.date_edit.setFixedHeight(46)
        self.date_edit.setStyleSheet(f"""
QDateEdit {{
    background:{KOYU};border:1.5px solid {SLATE};
    border-radius:10px;padding:0 14px;
    font-size:13px;color:{BEYAZ};
}}
QDateEdit:focus {{ border-color:{TEAL}; }}
QDateEdit::drop-down {{ border:none;width:28px; }}
""")

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Randevu ile ilgili notlar...")
        self.notes_edit.setFixedHeight(80)
        self.notes_edit.setStyleSheet(f"""
QTextEdit {{
    background:{KOYU};border:1.5px solid {SLATE};
    border-radius:10px;padding:10px 14px;
    font-size:13px;color:{BEYAZ};
}}
QTextEdit:focus {{ border-color:{TEAL}; }}
""")

        btn_row = QHBoxLayout()
        self.btn_save = QPushButton("💾 Randevu Kaydet")
        self.btn_save.setFixedHeight(48)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.btn_save.setStyleSheet(f"""
QPushButton {{
    background:{TEAL};color:{BEYAZ};border:none;
    border-radius:10px;padding:0 20px;
}}
QPushButton:hover {{ background:#27908B; }}
""")
        self.btn_save.clicked.connect(self._save_appointment)

        self.btn_sms = QPushButton("💬 SMS Gönder")
        self.btn_sms.setFixedHeight(48)
        self.btn_sms.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sms.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.btn_sms.setStyleSheet(f"""
QPushButton {{
    background:{ALTIN};color:{BEYAZ};border:none;
    border-radius:10px;padding:0 20px;
}}
QPushButton:hover {{ background:#9A7A34; }}
""")
        self.btn_sms.clicked.connect(self._send_sms)

        btn_row.addWidget(self.btn_save, 1)
        btn_row.addSpacing(10)
        btn_row.addWidget(self.btn_sms, 1)

        self.msg_lbl = QLabel("")
        self.msg_lbl.setStyleSheet(
            f"color:{T.SUCCESS};font-size:13px;"
            "font-weight:600;background:transparent;")
        self.msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.form_widget = QWidget()
        self.form_widget.setStyleSheet("background:transparent;")
        fv = QVBoxLayout(self.form_widget)
        fv.setContentsMargins(0, 0, 0, 0); fv.setSpacing(10)
        fv.addLayout(musteri_row)
        fv.addWidget(_lbl("Hayvan Seç"))
        fv.addLayout(animal_row)
        fv.addWidget(_lbl("İşlem / Aşı Türü"))
        fv.addWidget(self.type_combo)
        fv.addWidget(_lbl("Randevu Tarihi"))
        fv.addWidget(self.date_edit)
        fv.addWidget(_lbl("Notlar (İsteğe Bağlı)"))
        fv.addWidget(self.notes_edit)
        fv.addSpacing(8)
        fv.addLayout(btn_row)
        fv.addWidget(self.msg_lbl)
        fv.addStretch()
        self.form_widget.hide()

        rv.addWidget(self.form_title)
        rv.addWidget(self.form_placeholder)
        rv.addWidget(self.form_widget, 1)

        content.addWidget(left_panel, 1)
        content.addWidget(right_panel, 1)
        root.addLayout(content, 1)

    # ── Hayvan Yönetimi ───────────────────────────────────────────────────────
    def _hayvan_yonetim(self):
        if not self.selected_customer:
            return
        animal = self._get_selected_animal()
        if not animal:
            dlg = HayvanYonetimDialog(
                {}, self.selected_customer["id"], self)
            dlg.tabs.setCurrentIndex(1)
            dlg.tabs.setTabEnabled(0, False)
        else:
            dlg = HayvanYonetimDialog(
                animal, self.selected_customer["id"], self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._select_customer(self.selected_customer)

    # ── Müşteri Düzenle ───────────────────────────────────────────────────────
    def _musteri_duzenle(self):
        if not self.selected_customer:
            return
        dlg = MusteriDuzenleDialog(self.selected_customer, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            if dlg._deleted:
                self.selected_customer = None
                self.form_widget.hide()
                self.form_placeholder.show()
                self.sel_info.hide()
                self.btn_musteri_duzenle.hide()
                self._load_customers()
                main = self.window()
                if hasattr(main, "bildirim_goster"):
                    main.bildirim_goster("Müşteri silindi.", tur="hata")
            else:
                self._load_customers()
                cid = self.selected_customer["id"]
                rol = self.user.get("role", "")
                uid = self.user["id"]

                def _fetch():
                    if rol == "Klinik Sahibi":
                        customers = db.get_klinik_customers(uid)
                    else:
                        customers = db.get_customers(uid)
                    return next((c for c in customers if c["id"] == cid), None)

                def _done(c):
                    if c:
                        self.selected_customer = c
                        self.sel_info.setText(
                            f"👤 {c['name']}  📞 {c.get('phone','—')}")

                self._upd_worker = Worker(_fetch)
                self._upd_worker.result.connect(_done)
                self._upd_worker.start()
           

    def _get_selected_animal(self):
        idx = self.animal_combo.currentIndex()
        if not self._animals or idx < 0 or idx >= len(self._animals):
            return None
        return self._animals[idx]

    def _load_customers(self):
        search = self.search_input.text().strip()
        uid    = self.user["id"]
        rol    = self.user.get("role", "")

        if hasattr(self, "_cust_worker") and self._cust_worker is not None:
            try:
                self._cust_worker.result.disconnect()
                self._cust_worker.error.disconnect()
            except Exception:
                pass

        def _fetch():
            if rol == "Klinik Sahibi":
                return db.get_klinik_customers(uid, search or None)  # ← klinik_id ile
            return db.get_customers(uid, search or None)

        self._cust_worker = Worker(_fetch)
        self._cust_worker.result.connect(self._apply_customers)
        self._cust_worker.error.connect(
            lambda e: print(f"[Müşteri] Yükleme hatası: {e}"))
        self._cust_worker.start()
   

    def _apply_customers(self, customers):
        while self.cust_layout.count() > 1:
            item = self.cust_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        if not customers:
            lbl = QLabel("Müşteri bulunamadı.")
            lbl.setFont(QFont("Segoe UI", 12))
            lbl.setStyleSheet(
                f"color:{GRIS};background:transparent;border:none;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cust_layout.insertWidget(0, lbl)
        else:
            for i, cust in enumerate(customers):
                self.cust_layout.insertWidget(
                    i, CustomerCard(cust, self._select_customer))

    def _select_customer(self, customer):
        self.selected_customer = customer
        self.form_placeholder.hide()
        self.sel_info.setText(
            f"👤 {customer['name']}  📞 {customer.get('phone','—')}")
        self.sel_info.show()
        self.btn_musteri_duzenle.show()
        self.form_widget.show()
        self.msg_lbl.clear()
        self.animal_combo.clear()
        self.animal_combo.addItem("Yükleniyor...")

        def _fetch():
            return db.get_animals(customer["id"])

        def _done(animals):
            self._animals = animals
            self.animal_combo.clear()
            if animals:
                for a in animals:
                    label = (f"{a['name']} "
                             f"({a.get('species','?')}"
                             f"{' - '+a.get('breed','') if a.get('breed') else ''})")
                    self.animal_combo.addItem(label, userData=a["id"])
            else:
                self.animal_combo.addItem(
                    "Hayvan kaydı bulunamadı", userData=None)

        self._animal_worker = Worker(_fetch)
        self._animal_worker.result.connect(_done)
        self._animal_worker.error.connect(
            lambda e: print(f"[Hayvan] Yükleme hatası: {e}"))
        self._animal_worker.start()

    def _save_appointment(self):
        if not self.selected_customer:
            return
        idx = self.animal_combo.currentIndex()
        if not self._animals or idx < 0 or idx >= len(self._animals):
            self.msg_lbl.setStyleSheet(f"color:{T.DANGER};font-size:13px;")
            self.msg_lbl.setText("❌ Lütfen bir hayvan seçin.")
            return

        animal = self._animals[idx]
        atype  = self.type_combo.currentText().strip()
        date   = self.date_edit.date().toString("yyyy-MM-dd")
        notes  = self.notes_edit.toPlainText().strip()

        if not atype:
            self.msg_lbl.setStyleSheet(f"color:{T.DANGER};font-size:13px;")
            self.msg_lbl.setText("❌ Lütfen işlem türünü girin.")
            return

        self.btn_save.setEnabled(False)
        _aid       = animal["id"]
        _cid       = self.selected_customer["id"]
        _uid       = self.user["id"]
        _klinik_id = self._klinik_id  # ← klinik_id burada taşınıyor

        def _do():
            db.add_appointment(
                _aid, _cid, _uid, atype, date, notes,
                klinik_id=_klinik_id  # ← Supabase'e yazılıyor
            )

        def _done(_):
            self.btn_save.setEnabled(True)
            self.notes_edit.clear()
            main = self.window()
            if hasattr(main, "bildirim_goster"):
                main.bildirim_goster(
                    "✅ Randevu başarıyla kaydedildi!", tur="basarili")
            if hasattr(main, "dashboard") and main.dashboard:
                main.dashboard.refresh()

        def _appt_err(e):
            self.btn_save.setEnabled(True)
            self.msg_lbl.setStyleSheet(
                f"color:{T.DANGER};font-size:13px;"
                "font-weight:600;background:transparent;")
            self.msg_lbl.setText("❌ Randevu kaydedilemedi, tekrar deneyin.")

        self._appt_worker = Worker(_do)
        self._appt_worker.result.connect(_done)
        self._appt_worker.error.connect(_appt_err)
        self._appt_worker.start()

    def _send_sms(self):
        if not self.selected_customer:
            return
        idx = self.animal_combo.currentIndex()
        if not self._animals or idx < 0 or idx >= len(self._animals):
            return
        animal = self._animals[idx]
        atype  = self.type_combo.currentText().strip()
        date   = self.date_edit.date().toString("dd.MM.yyyy")
        phone  = self.selected_customer.get("phone", "—")
        msg    = (
            f"Sayın {self.selected_customer['name']}, "
            f"{animal['name']} isimli hastamızın "
            f"{date} tarihli '{atype}' randevusunu hatırlatırız. "
            f"Sağlıklı günler dileriz.")
        _uid = self.user["id"]
        _cid = self.selected_customer["id"]
        _aid = animal["id"]
        _win = self.window()

        def _do_sms():
            db.add_sms_log(_uid, _cid, _aid, phone, msg)

        def _done_sms(_):
            if hasattr(_win, "bildirim_goster"):
                _win.bildirim_goster(
                    "📱 SMS başarıyla gönderildi!", tur="basarili")

        self._sms_worker = Worker(_do_sms)
        self._sms_worker.result.connect(_done_sms)
        self._sms_worker.error.connect(
            lambda e: _win.bildirim_goster("SMS gönderilemedi!", tur="hata")
            if hasattr(_win, "bildirim_goster") else None)
        self._sms_worker.start()