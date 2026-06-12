"""
AuthWindow — FramelessWindowHint, WA_TranslucentBackground (siyah köşe yok),
fade geçiş animasyonu, dekoratif sol panel.
"""
import os
import json
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QFrame, QStackedWidget, QGraphicsOpacityEffect,
    QApplication
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve,
    QParallelAnimationGroup, QTimer, QPoint
)
from PyQt6.QtGui import (
    QFont, QPixmap, QPainter, QBrush, QColor, QPen, QCursor
)

import styles.theme as T
from worker import Worker

from ui.signup import RegisterPanel, SahipAdim2Panel, SahipAdim3Panel

# ── Renk sabitleri ────────────────────────────────────────────────────────────
MAVİ_KOYU    = "#0F1C2E"
MAVİ_ANA     = "#1A2942"
MAVİ_ORTA    = "#2B4060"
BEYAZ        = "#FFFFFF"
ACIK_GRI     = "#F4F7FA"
KENARLIK_GRI = "#E2E8F0"
YAZI_GRI     = "#64748B"
KOYU_YAZI    = "#0F172A"
ANA_FONT     = "Segoe UI"

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_YOLU = os.path.join(BASE_DIR, "config.json")

OZELLIKLER = [
    ("assets/Takvim.png",    "📅", "Aşı & Randevu Takibi"),
    ("assets/YeniKayıt.png", "🐾", "Hasta Yönetimi"),
    ("assets/Analiz.png",    "📊", "Analiz & Raporlama"),
    ("assets/sms.png",       "💬", "SMS Hatırlatma"),
]


def _load_logo(size=170):
    candidates = [
        "assets/VetSyncicon1.png", "assets/VetSyncicon1.jpg",
        "assets/VetSyncicon1.ico", "assets/VetSyncicon1.svg",
        "assets/vetsyncicon1.png", "assets/VetSync_icon.png",
        "assets/icon.png",
    ]
    for path in candidates:
        if os.path.exists(path):
            px = QPixmap(path)
            if not px.isNull():
                return px.scaled(
                    size * 2, size * 2,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ).scaled(
                    size, size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
    return None


class BildirimWidget(QFrame):
    def __init__(self, mesaj, tur="basarili", parent=None):
        super().__init__(parent)
        renk = "#2E7D32" if tur == "basarili" else "#C62828"
        ikon = "✅" if tur == "basarili" else "⚠️"
        self.setStyleSheet(
            f"QFrame{{background-color:{renk};border-radius:10px;}}")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(22, 10, 22, 10)
        lbl = QLabel(f"{ikon} {mesaj}")
        lbl.setFont(QFont(ANA_FONT, 11, QFont.Weight.Bold))
        lbl.setStyleSheet("color:white;background:transparent;")
        lay.addWidget(lbl)
        self.adjustSize()


class DekoratifSolPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(400)
        self._build_content()

    def _build_content(self):
        lv = QVBoxLayout(self)
        lv.setContentsMargins(35, 30, 35, 30)
        lv.setSpacing(0)

        px = _load_logo(170)
        if px:
            logo = QLabel()
            logo.setPixmap(px)
            logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo.setStyleSheet("background:transparent;")
            lv.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)
        else:
            lbl = QLabel("VetSync Pro")
            lbl.setFont(QFont(ANA_FONT, 22, QFont.Weight.Bold))
            lbl.setStyleSheet(
                "color:white;background:transparent;font-style:italic;")
            lv.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        lv.addSpacing(12)

        ayirici = QFrame()
        ayirici.setFrameShape(QFrame.Shape.HLine)
        ayirici.setFixedHeight(1)
        ayirici.setStyleSheet("background-color:#2E4A72;border:none;")
        lv.addWidget(ayirici)

        lv.addSpacing(14)

        lbl_baslik = QLabel("Veteriner Klinik\nYönetim Sistemi")
        lbl_baslik.setFont(QFont(ANA_FONT, 22, QFont.Weight.Bold))
        lbl_baslik.setStyleSheet("color:white;background:transparent;")
        lv.addWidget(lbl_baslik)

        lv.addSpacing(16)

        self._anim_satirlar = []
        for png_yol, fallback_emoji, metin in OZELLIKLER:
            satir_w = QWidget()
            satir_w.setStyleSheet("background:transparent;")
            satir_lay = QHBoxLayout(satir_w)
            satir_lay.setContentsMargins(0, 0, 0, 0)
            satir_lay.setSpacing(8)

            lbl_ikon = QLabel()
            lbl_ikon.setFixedSize(30, 30)
            lbl_ikon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_ikon.setStyleSheet("background:transparent;")
            if os.path.exists(png_yol):
                _raw = QPixmap(png_yol)
                _src_min = min(_raw.width(), _raw.height())
                if _src_min < 180:
                    _raw = _raw.scaled(
                        180, 180,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                px_ikon = _raw.scaled(
                    60, 60,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ).scaled(
                    30, 30,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                lbl_ikon.setPixmap(px_ikon)
            else:
                lbl_ikon.setText(fallback_emoji)
                lbl_ikon.setFont(QFont(ANA_FONT, 13))
                lbl_ikon.setStyleSheet("background:transparent;color:white;")

            lbl_metin = QLabel(metin)
            lbl_metin.setFont(QFont(ANA_FONT, 12))
            lbl_metin.setStyleSheet("color:#B0C4DE;background:transparent;")

            satir_lay.addWidget(lbl_ikon)
            satir_lay.addWidget(lbl_metin)
            satir_lay.addStretch()

            lv.addWidget(satir_w)
            lv.addSpacing(6)
            self._anim_satirlar.append(satir_w)

        lv.addStretch()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(200, self._baslat_animasyon)

    def _baslat_animasyon(self):
        self._aktif_animlar = []
        for i, satir_w in enumerate(self._anim_satirlar):
            gecikme = i * 180
            QTimer.singleShot(gecikme,
                              lambda w=satir_w: self._satir_animasyonu(w))

    def _satir_animasyonu(self, widget):
        hedef_x     = widget.x()
        hedef_y     = widget.y()
        baslangic_x = hedef_x + self.width()

        widget.move(baslangic_x, hedef_y)

        efekt = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(efekt)
        efekt.setOpacity(0.0)

        anim_pos = QPropertyAnimation(widget, b"pos")
        anim_pos.setDuration(650)
        anim_pos.setStartValue(QPoint(baslangic_x, hedef_y))
        anim_pos.setEndValue(QPoint(hedef_x, hedef_y))
        anim_pos.setEasingCurve(QEasingCurve.Type.OutCubic)

        anim_op = QPropertyAnimation(efekt, b"opacity")
        anim_op.setDuration(550)
        anim_op.setStartValue(0.0)
        anim_op.setEndValue(1.0)
        anim_op.setEasingCurve(QEasingCurve.Type.OutCubic)

        grup = QParallelAnimationGroup(widget)
        grup.addAnimation(anim_pos)
        grup.addAnimation(anim_op)

        def _bitti():
            widget.setGraphicsEffect(None)
            widget.move(hedef_x, hedef_y)

        grup.finished.connect(_bitti)
        grup.start()
        self._aktif_animlar.append(grup)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(MAVİ_ANA)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 14, 14)
        painter.drawRect(self.width() - 14, 0, 14, self.height())

        painter.setBrush(QBrush(QColor("#3A80D2")))
        for row in range(5):
            for col in range(6):
                cx = self.width() - 120 + 10 + col * 18
                cy = 10 + row * 18
                painter.drawEllipse(cx, cy, 5, 5)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor("#2E4A72"), 2))
        painter.drawEllipse(5, self.height() - 85, 80, 80)
        painter.drawEllipse(20, self.height() - 70, 50, 50)


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
    background-color:{ACIK_GRI};
    border:1px solid {KENARLIK_GRI};
    border-radius:8px;
    padding:0 12px;
    color:{KOYU_YAZI};
}}
QLineEdit:focus {{ border:1.5px solid {MAVİ_ORTA}; }}
""")
    lay.addWidget(entry)
    parent_layout.addWidget(cerceve, alignment=Qt.AlignmentFlag.AlignCenter)
    return entry


class LoginPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background:{BEYAZ};")
        self._giris_callback = None

        rv = QVBoxLayout(self)
        rv.setContentsMargins(0, 0, 0, 0)
        rv.setSpacing(0)

        rv.addWidget(self._ust_bar_olustur())

        icerik = QWidget()
        icerik.setStyleSheet("background:transparent;")
        il = QVBoxLayout(icerik)
        il.setContentsMargins(50, 0, 50, 20)
        il.setSpacing(0)

        ls = QHBoxLayout()
        lbl_logo = QLabel("VetSync Pro")
        lbl_logo.setFont(QFont(ANA_FONT, 16, QFont.Weight.Bold))
        lbl_logo.setStyleSheet(
            f"color:{MAVİ_ANA};font-style:italic;background:transparent;")
        self.btn_to_register = QPushButton("HESAP OLUŞTUR")
        self.btn_to_register.setFixedSize(130, 30)
        self.btn_to_register.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_to_register.setFont(QFont(ANA_FONT, 9, QFont.Weight.Bold))
        self.btn_to_register.setStyleSheet(f"""
QPushButton {{
    background:transparent;color:{MAVİ_ANA};
    border:1px solid {MAVİ_ANA};border-radius:6px;
}}
QPushButton:hover {{ background:#E3F2FD; }}
""")
        ls.addWidget(lbl_logo)
        ls.addStretch()
        ls.addWidget(self.btn_to_register)
        il.addLayout(ls)
        il.addSpacing(18)

        lbl_baslik = QLabel("Giriş Yap")
        lbl_baslik.setFont(QFont(ANA_FONT, 24, QFont.Weight.Bold))
        lbl_baslik.setStyleSheet(f"color:{KOYU_YAZI};background:transparent;")
        il.addWidget(lbl_baslik)
        il.addSpacing(4)

        lbl_alt = QLabel("Hesabınıza giriş yapın")
        lbl_alt.setFont(QFont(ANA_FONT, 11))
        lbl_alt.setStyleSheet(f"color:{YAZI_GRI};background:transparent;")
        il.addWidget(lbl_alt)
        il.addSpacing(24)

        # ── DEĞİŞİKLİK 1: Label ve placeholder güncellendi ───────────────────
        self.entry_kadi  = _etiketli_entry(
            il,
            "E-Posta Adresi",
            "ornek@email.com"
        )
   
        # ─────────────────────────────────────────────────────────────────────
        il.addSpacing(12)
        self.entry_sifre = _etiketli_entry(il, "Şifre", "••••••••", gizle=True)
        il.addSpacing(10)

        chk_w = QWidget()
        chk_w.setStyleSheet("background:transparent;")
        chk_w.setFixedWidth(320)
        chk_lay = QHBoxLayout(chk_w)
        chk_lay.setContentsMargins(0, 0, 0, 0)
        self.chk_hatirla = QCheckBox("Beni Hatırla")
        self.chk_hatirla.setFont(QFont(ANA_FONT, 11))
        self.chk_hatirla.setStyleSheet(T.CHECKBOX_STYLE)
        chk_lay.addWidget(self.chk_hatirla)
        chk_lay.addStretch()
        il.addWidget(chk_w, alignment=Qt.AlignmentFlag.AlignCenter)
        il.addSpacing(16)

        btn_giris = QPushButton("GİRİŞ YAP")
        btn_giris.setFixedSize(320, 44)
        btn_giris.setFont(QFont(ANA_FONT, 12, QFont.Weight.Bold))
        btn_giris.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_giris.setStyleSheet(f"""
QPushButton {{
    background-color:{MAVİ_ANA};color:white;
    border-radius:8px;border:none;
}}
QPushButton:hover {{ background-color:{MAVİ_KOYU}; }}
""")
        btn_giris.clicked.connect(self._on_giris_clicked)
        il.addWidget(btn_giris, alignment=Qt.AlignmentFlag.AlignCenter)
        il.addSpacing(8)

        self.btn_forgot = QPushButton("Şifrenizi mi unuttunuz?")
        self.btn_forgot.setFont(QFont(ANA_FONT, 10))
        self.btn_forgot.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_forgot.setStyleSheet(f"""
QPushButton {{
    background:transparent;color:{KOYU_YAZI};
    border:none;text-decoration:underline;font-weight:600;
}}
QPushButton:hover {{ color:{MAVİ_KOYU}; }}
""")
        il.addWidget(self.btn_forgot, alignment=Qt.AlignmentFlag.AlignCenter)
        il.addStretch()

        rv.addWidget(icerik, 1)

        self.entry_kadi.returnPressed.connect(lambda: self.entry_sifre.setFocus())
        self.entry_sifre.returnPressed.connect(btn_giris.click)

    def _ust_bar_olustur(self):
        bar = QWidget()
        bar.setFixedHeight(38)
        bar.setStyleSheet("background:transparent;")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(8, 4, 8, 0)
        lay.addStretch()
        self._btn_min   = QPushButton("—")
        self._btn_kapat = QPushButton("✕")
        for btn, hover in [(self._btn_min, ACIK_GRI),
                           (self._btn_kapat, "#FDECEA")]:
            btn.setFixedSize(32, 32)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setStyleSheet(f"""
QPushButton {{
    background:transparent;color:{YAZI_GRI};
    font-size:16px;font-weight:bold;
    border:none;border-radius:6px;
}}
QPushButton:hover {{ background:{hover}; }}
""")
            lay.addWidget(btn)
        return bar

    def _on_giris_clicked(self):
        if self._giris_callback:
            self._giris_callback()


class AuthWindow(QMainWindow):
    FADE_MS        = 280
    SAHIP_PAGE_MS  = 340
    SAHIP_SLIDE_PX = 36

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VetSync Pro")
        self.setFixedSize(980, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        ekran = QApplication.primaryScreen().geometry()
        self.move((ekran.width() - 980) // 2,
                  (ekran.height() - 600) // 2)

        self._tasima_baslangic = None
        self.aktif_bildirim    = None
        self._animating        = False
        self._page_animating   = False

        self._build_ui()
        self._ayarlari_yukle()

    def _build_ui(self):
        merkez = QWidget()
        merkez.setStyleSheet(f"""
QWidget {{
    background-color:{BEYAZ};
    border-radius:14px;
}}
""")
        self.setCentralWidget(merkez)
        self._merkez = merkez

        merkez_lay = QVBoxLayout(merkez)
        merkez_lay.setContentsMargins(0, 0, 0, 0)
        merkez_lay.setSpacing(0)

        self._merkez_stack = QStackedWidget()
        self._merkez_stack.setStyleSheet("background:transparent;border:none;")
        merkez_lay.addWidget(self._merkez_stack)

        # ── Sayfa 0: Giriş / Hekim Kayıt ──────────────────────────────────────
        self._auth_page = QWidget()
        self._auth_page.setStyleSheet("background:transparent;")
        auth_root = QHBoxLayout(self._auth_page)
        auth_root.setContentsMargins(0, 0, 0, 0)
        auth_root.setSpacing(0)

        self._left = DekoratifSolPanel()
        auth_root.addWidget(self._left)

        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background:{BEYAZ};border-radius:0px;")
        self._login_panel    = LoginPanel()
        self._register_panel = RegisterPanel()
        self._register_panel.bind_auth_window(self)
        self._stack.addWidget(self._login_panel)
        self._stack.addWidget(self._register_panel)
        self._stack.setCurrentIndex(0)
        auth_root.addWidget(self._stack, 1)

        # ── Sayfa 1: Klinik Sahibi Adım 2 ─────────────────────────────────────
        self._sahip_page = QWidget()
        self._sahip_page.setStyleSheet("background:transparent;")
        sahip_root = QHBoxLayout(self._sahip_page)
        sahip_root.setContentsMargins(0, 0, 0, 0)
        sahip_root.setSpacing(0)

        self._left_adim2 = DekoratifSolPanel()
        sahip_root.addWidget(self._left_adim2)

        self._sahip_adim2_panel = SahipAdim2Panel()
        sahip_root.addWidget(self._sahip_adim2_panel, 1)

        # ── Sayfa 2: Klinik Sahibi Adım 3 ─────────────────────────────────────
        self._sahip_page_3 = QWidget()
        self._sahip_page_3.setStyleSheet("background:transparent;")
        sahip_root_3 = QHBoxLayout(self._sahip_page_3)
        sahip_root_3.setContentsMargins(0, 0, 0, 0)
        sahip_root_3.setSpacing(0)

        self._left_adim3 = DekoratifSolPanel()
        sahip_root_3.addWidget(self._left_adim3)

        self._sahip_adim3_panel = SahipAdim3Panel()
        sahip_root_3.addWidget(self._sahip_adim3_panel, 1)

        # Merkez Stack Atamaları
        self._merkez_stack.addWidget(self._auth_page)    # index 0
        self._merkez_stack.addWidget(self._sahip_page)   # index 1
        self._merkez_stack.addWidget(self._sahip_page_3) # index 2
        self._merkez_stack.setCurrentIndex(0)

        # Sinyal Bağlantıları
        self._login_panel._btn_min.clicked.connect(self.showMinimized)
        self._login_panel._btn_kapat.clicked.connect(self.close)

        self._login_panel.btn_to_register.clicked.connect(
            lambda: self._fade_to(1))
        self._register_panel.btn_to_login.clicked.connect(self._kayitten_girise)

        self._login_panel._giris_callback          = self._on_login
        self._register_panel._kayit_callback       = self._on_register_hekim
        self._register_panel._sahip_adim2_callback = self._sahip_adim2_ac
        self._sahip_adim2_panel._ileri_callback    = self._sahip_adim3_ac
        self._sahip_adim2_panel._geri_callback     = self._sahip_adim1_don
        self._sahip_adim3_panel._kayit_callback    = self._on_register_sahip_final
        self._sahip_adim3_panel._geri_callback     = self._sahip_adim2_don

        self._login_panel.btn_forgot.clicked.connect(self._open_forgot)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._tasima_baslangic = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft())

    def mouseMoveEvent(self, event):
        if self._tasima_baslangic and \
                event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._tasima_baslangic)

    def mouseReleaseEvent(self, event):
        self._tasima_baslangic = None

    def bildirim_goster(self, mesaj, tur="basarili"):
        if self.aktif_bildirim:
            try:
                self.aktif_bildirim.deleteLater()
            except Exception:
                pass
        b = BildirimWidget(mesaj, tur, self._merkez)
        b.adjustSize()
        b.move((self.width() - b.width()) // 2, 12)
        b.show()
        b.raise_()
        self.aktif_bildirim = b
        QTimer.singleShot(3000, b.deleteLater)

    def _fade_to(self, index):
        if self._animating or self._stack.currentIndex() == index:
            return
        self._animating = True
        outgoing = self._stack.currentWidget()
        incoming = self._stack.widget(index)

        fx_out = QGraphicsOpacityEffect(outgoing)
        fx_in  = QGraphicsOpacityEffect(incoming)
        outgoing.setGraphicsEffect(fx_out)
        incoming.setGraphicsEffect(fx_in)
        fx_in.setOpacity(0.0)
        self._stack.setCurrentIndex(index)

        anim_out = QPropertyAnimation(fx_out, b"opacity")
        anim_out.setDuration(self.FADE_MS)
        anim_out.setStartValue(1.0)
        anim_out.setEndValue(0.0)
        anim_out.setEasingCurve(QEasingCurve.Type.OutCubic)

        anim_in = QPropertyAnimation(fx_in, b"opacity")
        anim_in.setDuration(self.FADE_MS)
        anim_in.setStartValue(0.0)
        anim_in.setEndValue(1.0)
        anim_in.setEasingCurve(QEasingCurve.Type.InCubic)

        group = QParallelAnimationGroup(self)
        group.addAnimation(anim_out)
        group.addAnimation(anim_in)

        def _done():
            outgoing.setGraphicsEffect(None)
            incoming.setGraphicsEffect(None)
            self._animating = False

        group.finished.connect(_done)
        group.start()
        self._anim_group = group

    def sahip_wizard_sifirla(self):
        if self._merkez_stack.currentIndex() != 0:
            self._merkez_stack.setCurrentIndex(0)
        self._register_panel.reset_sahip_flow()
        self._sahip_adim2_panel.reg_klinik_ismi.clear()
        self._sahip_adim2_panel.combo_il.setCurrentIndex(0)
        self._sahip_adim2_panel.reg_ilce.clear()
        self._sahip_adim2_panel.reg_klinik_adresi.clear()
        self._sahip_adim3_panel.reg_k_turu.setCurrentIndex(0)
        self._sahip_adim3_panel.reg_k_tel.clear()

    def _kayitten_girise(self):
        self.sahip_wizard_sifirla()
        self._fade_to(0)

    def _sahip_adim2_ac(self):
        if self._page_animating: return
        self._full_page_gecis(1, ileri=True)

    def _sahip_adim3_ac(self):
        if self._page_animating: return
        p2 = self._sahip_adim2_panel
        if not p2.reg_klinik_ismi.text().strip() or \
           not p2.reg_ilce.text().strip() or \
           not p2.reg_klinik_adresi.text().strip():
            self.bildirim_goster(
                "Lütfen klinik adını, ilçenizi ve adresinizi girin.", tur="hata")
            return
        self._full_page_gecis(2, ileri=True)

    def _sahip_adim1_don(self):
        if self._page_animating: return
        self._full_page_gecis(0, ileri=False)

    def _sahip_adim2_don(self):
        if self._page_animating: return
        self._full_page_gecis(1, ileri=False)

    def _full_page_gecis(self, index, ileri=True):
        if self._page_animating or self._merkez_stack.currentIndex() == index:
            return
        self._page_animating = True
        outgoing = self._merkez_stack.currentWidget()
        incoming = self._merkez_stack.widget(index)

        fx_out = QGraphicsOpacityEffect(outgoing)
        fx_in  = QGraphicsOpacityEffect(incoming)
        outgoing.setGraphicsEffect(fx_out)
        incoming.setGraphicsEffect(fx_in)
        fx_in.setOpacity(0.0)

        off       = self.SAHIP_SLIDE_PX if ileri else -self.SAHIP_SLIDE_PX
        out_end   = QPoint(-off, 0)
        in_start  = QPoint(off, 0)
        out_start = outgoing.pos()
        in_end    = incoming.pos()

        incoming.move(in_start)
        self._merkez_stack.setCurrentIndex(index)

        anim_out_op = QPropertyAnimation(fx_out, b"opacity")
        anim_out_op.setDuration(self.SAHIP_PAGE_MS)
        anim_out_op.setStartValue(1.0)
        anim_out_op.setEndValue(0.0)
        anim_out_op.setEasingCurve(QEasingCurve.Type.OutCubic)

        anim_in_op = QPropertyAnimation(fx_in, b"opacity")
        anim_in_op.setDuration(self.SAHIP_PAGE_MS)
        anim_in_op.setStartValue(0.0)
        anim_in_op.setEndValue(1.0)
        anim_in_op.setEasingCurve(QEasingCurve.Type.InCubic)

        anim_out_pos = QPropertyAnimation(outgoing, b"pos")
        anim_out_pos.setDuration(self.SAHIP_PAGE_MS)
        anim_out_pos.setStartValue(out_start)
        anim_out_pos.setEndValue(out_start + out_end)
        anim_out_pos.setEasingCurve(QEasingCurve.Type.OutCubic)

        anim_in_pos = QPropertyAnimation(incoming, b"pos")
        anim_in_pos.setDuration(self.SAHIP_PAGE_MS)
        anim_in_pos.setStartValue(in_start)
        anim_in_pos.setEndValue(in_end)
        anim_in_pos.setEasingCurve(QEasingCurve.Type.OutCubic)

        group = QParallelAnimationGroup(self)
        group.addAnimation(anim_out_op)
        group.addAnimation(anim_in_op)
        group.addAnimation(anim_out_pos)
        group.addAnimation(anim_in_pos)

        def _done():
            outgoing.setGraphicsEffect(None)
            incoming.setGraphicsEffect(None)
            outgoing.move(out_start)
            incoming.move(in_end)
            self._page_animating = False

        group.finished.connect(_done)
        group.start()
        self._page_anim_group = group

    def _ayarlari_yukle(self):
        if os.path.exists(CONFIG_YOLU):
            try:
                with open(CONFIG_YOLU, "r") as f:
                    ayarlar = json.load(f)
                if ayarlar.get("hatirla"):
                    self._login_panel.chk_hatirla.setChecked(True)
                    self._login_panel.entry_kadi.setText(
                        ayarlar.get("kadi", ""))
            except Exception:
                pass

    def _ayarlari_kaydet(self, kadi):
        hatirla = self._login_panel.chk_hatirla.isChecked()
        ayarlar = {
            "hatirla": hatirla,
            "kadi":    kadi if hatirla else "",
        }
        with open(CONFIG_YOLU, "w") as f:
            json.dump(ayarlar, f)

    def _open_forgot(self):
        from .forgot_password_dialog import ForgotPasswordDialog
        dlg = ForgotPasswordDialog(self)
        dlg.exec()

    def _on_login(self):
        from database import login_user
        # ── DEĞİŞİKLİK 2: identifier = kullanıcı adı VEYA e-posta ──────────
        identifier = self._login_panel.entry_kadi.text().strip()
        sifre      = self._login_panel.entry_sifre.text()
        if not identifier or not sifre:
            self.bildirim_goster(
                "Lütfen e-posta ve şifreyi doldurun.", tur="hata")
            return
       
        # ─────────────────────────────────────────────────────────────────────
        self._login_panel.setEnabled(False)
        self.bildirim_goster("Giriş yapılıyor...", tur="basarili")

        def _do():
            return login_user(identifier, sifre)

        def _done(result):
            self._login_panel.setEnabled(True)
            ok, user = result
            if ok:
                self._ayarlari_kaydet(identifier)
                from .main_window import MainWindow
                self._main = MainWindow(user)
                self._main.show()
                self.close()
            else:
                self.bildirim_goster(
                    "Kullanıcı adı / e-posta veya şifre yanlış!", tur="hata")

        def _err(e):
            self._login_panel.setEnabled(True)
            self.bildirim_goster("Bağlantı hatası!", tur="hata")

        self._login_worker = Worker(_do)
        self._login_worker.result.connect(_done)
        self._login_worker.error.connect(_err)
        self._login_worker.start()

    def _on_register_hekim(self):
        from database import register_user
        rp = self._register_panel

        ad       = rp._hekim_ad
        soyad    = rp._hekim_soyad
        cinsiyet = rp._hekim_cinsiyet
        mail     = rp.hekim_adim2.reg_mail.text().strip()
        tel      = rp.hekim_adim2.reg_tel.telefon()
        sifre    = rp.hekim_adim2.reg_sifre.text()
        kadi     = f"{ad.lower()}.{soyad.lower()}"

        if not ad or not soyad:
            self.bildirim_goster("Lütfen adım 1'i tamamlayın.", tur="hata")
            return

        if not mail or not sifre:
            self.bildirim_goster("Lütfen tüm alanları doldurun.", tur="hata")
            return

        if len(sifre) < 4:
            self.bildirim_goster("Şifre en az 4 karakter olmalıdır.", tur="hata")
            return

        rp.setEnabled(False)
        self.bildirim_goster("Kayıt oluşturuluyor...", tur="basarili")

        def _do():
            return register_user(
                kadi, mail, sifre,
                gender=cinsiyet,
                role="Veteriner Hekim",
                ad=ad, soyad=soyad, telefon=tel
            )

        def _done(result):
            rp.setEnabled(True)
            ok, msg = result
            if ok:
                self.bildirim_goster("Kayıt tamamlandı! Giriş yapabilirsiniz.", tur="basarili")
                QTimer.singleShot(1400, self._kayitten_girise)
            else:
                self.bildirim_goster(msg, tur="hata")

        def _err(e):
            rp.setEnabled(True)
            self.bildirim_goster("Bağlantı hatası!", tur="hata")

        self._reg_worker = Worker(_do)
        self._reg_worker.result.connect(_done)
        self._reg_worker.error.connect(_err)
        self._reg_worker.start()
   

    def _on_register_sahip_final(self):
        from database import register_user
        rp = self._register_panel
        p2 = self._sahip_adim2_panel
        p3 = self._sahip_adim3_panel

        # Adım 1
        kadi   = f"{rp._sahip_ad} {rp._sahip_soyad}".strip()
        mail   = rp._sahip_mail
        sifre  = rp._sahip_sifre
        gender = "Belirtilmedi"

        # Adım 2
        sehir_ilce    = f"{p2.combo_il.currentText()} / {p2.reg_ilce.text().strip()}"
        klinik_adi    = p2.reg_klinik_ismi.text().strip()
        klinik_adresi = p2.reg_klinik_adresi.text().strip()

        # Adım 3
        tur = p3.reg_k_turu.currentText().strip()
        # ── DEĞİŞİKLİK 3: .telefon() ile temiz format ────────────────────────
        telefon = p3.reg_k_tel.telefon()
        # ─────────────────────────────────────────────────────────────────────

        if not telefon:
            self.bildirim_goster("Lütfen iletişim numarasını girin.", tur="hata")
            return

        rp.setEnabled(False)
        p2.setEnabled(False)
        p3.setEnabled(False)
        self.bildirim_goster("Kayıt oluşturuluyor...", tur="basarili")

        def _do():
            return register_user(
                kadi, mail, sifre, gender=gender, role="Klinik Sahibi",
                klinik_adi=klinik_adi, sehir_ilce=sehir_ilce,
                klinik_adresi=klinik_adresi, tur=tur, telefon=telefon
            )

        def _done(result):
            rp.setEnabled(True)
            p2.setEnabled(True)
            p3.setEnabled(True)
            ok, msg = result
            if ok:
                self.bildirim_goster("Kayıt tamamlandı! Giriş yapabilirsiniz.", tur="basarili")
                QTimer.singleShot(1400, self._kayitten_girise)
            else:
                self.bildirim_goster(msg, tur="hata")

        def _err(e):
            rp.setEnabled(True)
            p2.setEnabled(True)
            p3.setEnabled(True)
            self.bildirim_goster("Bağlantı hatası!", tur="hata")

        self._reg_worker = Worker(_do)
        self._reg_worker.result.connect(_done)
        self._reg_worker.error.connect(_err)
        self._reg_worker.start()