"""
dashboard_widget.py  —  VetSync Pro
"""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTabWidget, QScrollArea, QPushButton, QMenu
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPixmap, QCursor, QAction, QIcon


import database as db
from worker import Worker


TEAL     = "#30A7A1"
ALTIN    = "#B69240"
PANEL_BG = "#1A2942"
CARD_BG  = "#212D3A"
KOYU     = "#16202A"
SLATE    = "#305F82"
BEYAZ    = "#FFFFFF"
GRIS     = "#94A3B8"


STAT_TEAL = "#0D9488"
STAT_DARK = "#2D3748"
STAT_BLUE = "#4F46E5"



def _load_icon(png_path, size=40):
    if os.path.exists(png_path):
        px = QPixmap(png_path)
        if not px.isNull():
            return px.scaled(
                size, size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
    return None



class StatCard(QFrame):
    def __init__(self, title, value, icon_path, color):
        super().__init__()
        self.setStyleSheet(f"""
QFrame {{
    background-color: {color};
    border-radius: 14px;
    border: none;
}}
""")
        self.setMinimumHeight(120)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)

        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        title_lbl.setStyleSheet(
            "color: rgba(255,255,255,0.85); background: transparent;")

        bottom = QHBoxLayout()

        icon_lbl = QLabel()
        icon_lbl.setFixedSize(52, 52)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("background: transparent;")
        px = _load_icon(icon_path, 40)
        if px:
            icon_lbl.setPixmap(px)
        else:
            icon_lbl.setText("📊")
            icon_lbl.setFont(QFont("Segoe UI Emoji", 28))
            icon_lbl.setStyleSheet(
                "color: rgba(255,255,255,0.7); background: transparent;")

        self.val_lbl = QLabel(str(value))
        self.val_lbl.setFont(QFont("Segoe UI", 42, QFont.Weight.Bold))
        self.val_lbl.setStyleSheet("color: white; background: transparent;")

        bottom.addWidget(icon_lbl)
        bottom.addSpacing(12)
        bottom.addWidget(self.val_lbl)
        bottom.addStretch()

        layout.addWidget(title_lbl)
        layout.addLayout(bottom)

    def update_value(self, value):
        self.val_lbl.setText(str(value))



# ── Randevu Satırı ────────────────────────────────────────────────────────────
class AppointmentRow(QFrame):
    def __init__(self, appt, refresh_cb=None, current_user=None):
        super().__init__()
        self.appt         = appt
        self.refresh_cb   = refresh_cb
        self.current_user = current_user or {}

        self.setStyleSheet(f"""
QFrame {{
    background-color: #2A3547;
    border: none;
    border-radius: 10px;
}}
QLabel {{ background: transparent; }}
""")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 14, 20, 14)

        info = QVBoxLayout()
        info.setSpacing(6)

        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        top_row.setContentsMargins(0, 0, 0, 0)

        pati_lbl = QLabel()
        pati_lbl.setFixedSize(32, 32)
        pati_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pati_lbl.setStyleSheet("background: transparent;")
        px = _load_icon("assets/Pati.png", 32)
        if px:
            pati_lbl.setPixmap(px)
        else:
            pati_lbl.setText("🐾")
            pati_lbl.setFont(QFont("Segoe UI Emoji", 13))

        name_lbl = QLabel(
            f"{appt.get('customer_name', '—')}  —  {appt.get('animal_name', '—')}")
        name_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        name_lbl.setStyleSheet(f"color: {BEYAZ};")

        top_row.addWidget(pati_lbl)
        top_row.addWidget(name_lbl)
        top_row.addStretch()
        top_w = QWidget()
        top_w.setStyleSheet("background: transparent;")
        top_w.setLayout(top_row)

        # ── Alt bilgi satırı ──────────────────────────────────────────────
        phone    = appt.get("customer_phone", "—")
        atype    = appt.get("appointment_type", "—")
        date_str = appt.get("appointment_date", "—")[:10]
        try:
            y, m, d  = date_str.split("-")
            date_str = f"{d}.{m}.{y}"
        except Exception:
            pass

        # Klinik sahibi görünümünde randevuyu oluşturan hekimi göster
        hekim    = appt.get("hekim_adi", "")
        klinik_g = appt.get("klinik_gorunumu", False)
        hekim_str = f"   ·   👨‍⚕️  {hekim}" if (klinik_g and hekim and hekim != "—") else ""

        # Her iki rolde de — klinik sahibi onayladıysa göster
        onaylayan     = appt.get("onaylayan_adi", "")
        onaylayan_str = f"   ·   ✅  {onaylayan}" if onaylayan else ""

        alt_lbl = QLabel(
            f"📞  {phone}   ·   💉  {atype}   ·   📅  {date_str}{hekim_str}{onaylayan_str}") 
            
        alt_lbl.setFont(QFont("Segoe UI", 11))   
        animal_name = appt.get("animal_name", "")
        alt_lbl.setStyleSheet(f"color: {GRIS};")

        info.addWidget(top_w)
        info.addWidget(alt_lbl)
        layout.addLayout(info, 1)
        layout.addSpacing(12)

        # ── Durum butonu ──────────────────────────────────────────────────
        status = appt.get("status", "pending")
        missed = appt.get("missed", False)

        if status == "completed":
            s = QLabel("✅  Tamamlandı")
            s.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            s.setStyleSheet(f"color: {TEAL};")
            layout.addWidget(s)
        elif status == "cancelled":
            s = QLabel("❌  İptal Edildi")
            s.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            s.setStyleSheet("color: #EF4444;")
            layout.addWidget(s)
        elif missed:
            s = QLabel("⚠️  İşlem Yapılmamıştır")
            s.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            s.setStyleSheet(f"color: {ALTIN};")
            layout.addWidget(s)
        else:
            btn = QPushButton("Hızlı İşlemler")
            btn.setFixedSize(170, 36)
            btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setStyleSheet(f"""
QPushButton {{
    background-color: {TEAL};
    color: {BEYAZ};
    border-radius: 18px;
    border: none;
    padding-right: 8px;
}}
QPushButton:hover {{ background-color: #27908B; }}
""")
            px_down = _load_icon("assets/down.png", 16)
            if px_down:
                btn.setIcon(QIcon(px_down))
                btn.setIconSize(QSize(16, 16))
                btn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            btn.clicked.connect(lambda checked=False: self._menu_goster(btn))
            layout.addWidget(btn)


    def _menu_goster(self, btn):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
QMenu {{
    background-color: {CARD_BG};
    border: 1px solid {ALTIN};
    border-radius: 10px;
    padding: 6px 0px;
    font-family: 'Segoe UI';
    font-size: 13px;
    color: {BEYAZ};
}}
QMenu::item {{ padding: 10px 24px 10px 16px; color: {BEYAZ}; }}
QMenu::item:selected {{ background-color: {SLATE}; border-radius: 6px; }}
QMenu::separator {{ height: 1px; background: {SLATE}; margin: 4px 10px; }}
""")
        act_tamam = QAction("✅   İşlem Tamamlandı", self)
        act_iptal = QAction("❌   İşlemi İptal Et",  self)
        act_sms   = QAction("💬   Hatırlat (SMS)",   self)
        act_tamam.triggered.connect(lambda checked=False: self._tamamla())
        act_iptal.triggered.connect(lambda checked=False: self._iptal())
        act_sms.triggered.connect(lambda checked=False: self._sms_gonder())
        menu.addAction(act_tamam)
        menu.addAction(act_iptal)
        menu.addSeparator()
        menu.addAction(act_sms)
        menu.exec(btn.mapToGlobal(btn.rect().bottomLeft()))


    def _tamamla(self):
        appt_id      = self.appt["id"]
        hayvan       = self.appt.get("animal_name", "Hasta")
        onaylayan_id = self.current_user.get("id")   # ← kim onaylıyorsa o
        win          = self.window()

        def _do():
            db.update_appointment_status(appt_id, "completed",
                                         onaylayan_id=onaylayan_id)

        def _done(_):
            if hasattr(win, "bildirim_goster"):
                win.bildirim_goster(
                    f"{hayvan} işlemi tamamlandı!", tur="basarili")
            if self.refresh_cb:
                self.refresh_cb()

        self._w = Worker(_do)
        self._w.result.connect(_done)
        self._w.error.connect(lambda e: print(f"[Tamamla] Hata: {e}"))
        self._w.start()


    def _iptal(self):
        appt_id      = self.appt["id"]
        hayvan       = self.appt.get("animal_name", "Hasta")
        onaylayan_id = self.current_user.get("id")   # ← EKLENDİ
        win          = self.window()

        def _do():
            db.update_appointment_status(appt_id, "cancelled",
                                         onaylayan_id=onaylayan_id)  # EKLENDİ
       

        def _done(_):
            if hasattr(win, "bildirim_goster"):
                win.bildirim_goster(
                    f"{hayvan} işlemi iptal edildi.", tur="hata")
            if self.refresh_cb:
                self.refresh_cb()

        self._w = Worker(_do)
        self._w.result.connect(_done)
        self._w.error.connect(lambda e: print(f"[İptal] Hata: {e}"))
        self._w.start()


    def _sms_gonder(self):
        ad     = self.appt.get("customer_name", "")
        hayvan = self.appt.get("animal_name", "")
        islem  = self.appt.get("appointment_type", "")
        tarih  = self.appt.get("appointment_date", "")[:10]
        phone  = self.appt.get("customer_phone", "")
        mesaj  = (f"Sayın {ad}, {hayvan} adlı hastamızın {tarih} tarihli "
                  f"'{islem}' randevusunu hatırlatırız. Sağlıklı günler dileriz.")
        win = self.window()

        def _do():
            db.add_sms_log(
                self.appt.get("user_id", 0),
                self.appt.get("customer_id", 0),
                self.appt.get("animal_id", 0),
                phone, mesaj)

        def _done(_):
            if hasattr(win, "bildirim_goster"):
                win.bildirim_goster(
                    f"{ad} için SMS gönderildi!", tur="basarili")

        def _err(e):
            if hasattr(win, "bildirim_goster"):
                win.bildirim_goster("SMS gönderilemedi!", tur="hata")

        self._w = Worker(_do)
        self._w.result.connect(_done)
        self._w.error.connect(_err)
        self._w.start()



# ── Ana Widget ────────────────────────────────────────────────────────────────
class DashboardWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setStyleSheet(f"background-color: {PANEL_BG};")
        self._build_ui()
        self.refresh()


    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(30, 30, 30, 30)
        main.setSpacing(24)

        self.greet_lbl = QLabel(f"Merhaba, {self.user['username']}")
        self.greet_lbl.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self.greet_lbl.setStyleSheet(
            "color: #000000; background: transparent;")

        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)
        self.card_customers = StatCard(
            "Toplam Müşteri",     0, "assets/TopMusteriler.png",    STAT_TEAL)
        self.card_animals   = StatCard(
            "Toplam Hasta",       0, "assets/pati_hasta.png",        STAT_DARK)
        self.card_today     = StatCard(
            "Bugünkü Randevular", 0, "assets/Randevu_Oluşturma.png", STAT_BLUE)
        stats_row.addWidget(self.card_customers, 1)
        stats_row.addWidget(self.card_animals,   1)
        stats_row.addWidget(self.card_today,     1)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setStyleSheet(f"""
QTabWidget::pane {{
    border: none;
    background: {CARD_BG};
    border-bottom-left-radius: 12px;
    border-bottom-right-radius: 12px;
}}
QTabBar {{
    background: {PANEL_BG};
    border-bottom: 1px solid #1E2E42;
}}
QTabBar::tab {{
    background: transparent;
    color: {GRIS};
    padding: 14px 32px;
    border: none;
    border-bottom: 3px solid transparent;
    font-size: 13px;
    font-weight: 600;
    font-family: 'Segoe UI';
    min-width: 150px;
}}
QTabBar::tab:selected {{
    color: {TEAL};
    border-bottom: 3px solid {TEAL};
    background: rgba(48, 167, 161, 0.08);
}}
QTabBar::tab:hover:!selected {{
    color: #CBD5E1;
    background: rgba(255, 255, 255, 0.05);
    border-bottom: 3px solid #304E6A;
}}
""")

        self.tab_today    = self._make_scroll_tab()
        self.tab_upcoming = self._make_scroll_tab()
        self.tab_past     = self._make_scroll_tab()

        self.tabs.addTab(self.tab_today,    "Bugünkü Randevular")
        self.tabs.addTab(self.tab_upcoming, "Yaklaşan Randevular")
        self.tabs.addTab(self.tab_past,     "Geçmiş Randevular")

        main.addWidget(self.greet_lbl)
        main.addLayout(stats_row)
        main.addWidget(self.tabs, 1)


    def _make_scroll_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
QScrollArea {{ border: none; background: transparent; border-radius: 12px; }}
QScrollBar:vertical {{
    background: {KOYU};
    width: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {SLATE};
    border-radius: 3px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
""")
        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        vbox = QVBoxLayout(inner)
        vbox.setContentsMargins(16, 16, 16, 16)
        vbox.setSpacing(10)
        vbox.addStretch()
        scroll.setWidget(inner)
        scroll._inner_layout = vbox
        return scroll


    def _populate_tab(self, scroll, rows, empty_msg):
        layout = scroll._inner_layout
        while layout.count() > 1:
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not rows:
            lbl = QLabel(empty_msg)
            lbl.setFont(QFont("Segoe UI", 13))
            lbl.setStyleSheet(f"color: {GRIS}; background: transparent;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.insertWidget(0, lbl)
        else:
            for i, appt in enumerate(rows):
                row = AppointmentRow(
                    appt,
                    refresh_cb=self.refresh,
                    current_user=self.user)   # ← current_user iletiliyor
                layout.insertWidget(i, row)


    def refresh(self):
        uid = self.user["id"]
        rol = self.user.get("role", "")

        def _fetch():
            if rol == "Klinik Sahibi":
                return {
                    "customers":   db.get_klinik_customer_count(uid),  # ✅ klinik_id ile
                    "animals":     db.get_klinik_animal_count(uid),     # ✅ klinik_id ile
             
                    "today_count": db.get_klinik_appointment_count_today(uid),
                    "today":       db.get_klinik_appointments_today(uid),
                    "upcoming":    db.get_klinik_appointments_upcoming(uid),
                    "past":        db.get_klinik_appointments_past(uid),
                }
            else:
                return {
                    "customers":   db.get_customer_count(uid),
                    "animals":     db.get_animal_count(uid),
                    "today_count": db.get_appointment_count_today(uid),
                    "today":       db.get_appointments_today(uid),
                    "upcoming":    db.get_appointments_upcoming(uid),
                    "past":        db.get_appointments_past(uid),
                }

        self._refresh_worker = Worker(_fetch)
        self._refresh_worker.result.connect(self._apply_refresh)
        self._refresh_worker.error.connect(
            lambda e: print(f"[Dashboard] Yükleme hatası: {e}"))
        self._refresh_worker.start()


    def _apply_refresh(self, data):
        self.card_customers.update_value(data["customers"])
        self.card_animals.update_value(data["animals"])
        self.card_today.update_value(data["today_count"])
        self._populate_tab(
            self.tab_today, data["today"],
            "Bugün için planlanmış bir randevu bulunmuyor.")
        self._populate_tab(
            self.tab_upcoming, data["upcoming"],
            "Yaklaşan randevu bulunmuyor.")
        self._populate_tab(
            self.tab_past, data["past"],
            "Geçmiş randevu bulunmuyor.")