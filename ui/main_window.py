import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QMenu, QApplication
)
from PyQt6.QtCore import Qt, QSize, QTimer, QRect
from PyQt6.QtGui import QFont, QPixmap, QAction, QIcon

import styles.theme as T

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_YOLU = os.path.join(BASE_DIR, "assets", "VetSyncicon1.png")

_RESIZE_MARGIN = 6


def _sidebar_logo():
    return _load_icon(LOGO_YOLU, 130)


def _load_icon(path, size):
    if not os.path.exists(path):
        return None
    px = QPixmap(path)
    if px.isNull():
        return None
    src_min = min(px.width(), px.height())
    if src_min < size * 2:
        px = px.scaled(
            size * 3, size * 3,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
    return px.scaled(
        size, size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


class _TopBar(QWidget):
    """Pencereyi sürüklemeye yarayan özel üst çubuk."""

    def __init__(self, win: QMainWindow):
        super().__init__()
        self._win      = win
        self._drag_pos = None
        self.setFixedHeight(54)
        self.setMouseTracking(True)
        self.setStyleSheet(T.TOPBAR)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint()
                - self._win.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            if self._win.isMaximized():
                self._win.showNormal()
                self._drag_pos = (
                    event.globalPosition().toPoint()
                    - self._win.frameGeometry().topLeft()
                )
            self._win.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._win.isMaximized():
                self._win.showNormal()
            else:
                self._win.showMaximized()


#  Ana Pencere
class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user      = user
        self.dashboard = None

        self.setWindowTitle("VetSync Pro")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window
        )
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)
        self.setStyleSheet(T.APP_STYLE + f"QMainWindow {{ background-color: {T.PRIMARY}; }}")
        self.setMouseTracking(True)

        self._resize_dir       = None
        self._resize_start_pos = None
        self._resize_start_geo = None

        self._build_ui()
        self._nav_buttons[0].click()
        QTimer.singleShot(400, self._giris_bildirimi)

    def _build_ui(self):
        central = QWidget()
        central.setMouseTracking(True)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        topbar = _TopBar(self)
        tb = QHBoxLayout(topbar)
        tb.setContentsMargins(20, 0, 4, 0)
        tb.setSpacing(10)

        app_title = QLabel("VetSync Pro")
        app_title.setObjectName("app_title")
        app_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))

        add_btn = QPushButton("+ Yeni ekle")
        add_btn.setObjectName("add_btn")
        add_btn.setFixedHeight(34)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._quick_add)

        sms_btn = QPushButton()
        sms_btn.setObjectName("sms_btn")
        sms_btn.setFixedHeight(34)
        sms_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        _sms_px = _load_icon("assets/sms.png", 24)
        if _sms_px:
            sms_btn.setIcon(QIcon(_sms_px))
            sms_btn.setIconSize(QSize(24, 24))
            sms_btn.setText(" SMS Kutusu")
        else:
            sms_btn.setText("💬 SMS Kutusu")
        sms_btn.clicked.connect(self._open_sms)

        self._user_btn = QPushButton()
        self._user_btn.setObjectName("user_btn")
        self._user_btn.setFixedHeight(34)
        self._user_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._user_btn.clicked.connect(self._show_user_menu)
        self._update_user_btn()

        # ── Pencere Kontrol Butonları ──────────────────────────────────────
        _wc_base = """
            QPushButton {
                background: transparent; border: none;
                color: #94A3B8; font-size: 15px;
                font-family: 'Segoe UI'; border-radius: 4px;
            }
            QPushButton:hover { background: rgba(255,255,255,0.12); color: white; }
        """
        _wc_close = """
            QPushButton {
                background: transparent; border: none;
                color: #94A3B8; font-size: 13px;
                font-family: 'Segoe UI'; border-radius: 4px;
            }
            QPushButton:hover { background: #E53E3E; color: white; }
        """

        self._min_btn = QPushButton("─")
        self._min_btn.setFixedSize(40, 34)
        self._min_btn.setStyleSheet(_wc_base)
        self._min_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._min_btn.setToolTip("Simge Durumuna Küçült")
        self._min_btn.clicked.connect(self.showMinimized)

        self._max_btn = QPushButton("□")
        self._max_btn.setFixedSize(40, 34)
        self._max_btn.setStyleSheet(_wc_base)
        self._max_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._max_btn.setToolTip("Ekranı Kapla")
        self._max_btn.clicked.connect(self._toggle_maximize)

        self._close_btn = QPushButton("✕")
        self._close_btn.setFixedSize(40, 34)
        self._close_btn.setStyleSheet(_wc_close)
        self._close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close_btn.setToolTip("Kapat")
        self._close_btn.clicked.connect(self.close)

        div = QFrame()
        div.setFrameShape(QFrame.Shape.VLine)
        div.setStyleSheet("color: rgba(255,255,255,0.12);")
        div.setFixedHeight(22)

        tb.addWidget(app_title)
        tb.addStretch()
        tb.addWidget(add_btn)
        tb.addWidget(sms_btn)
        tb.addWidget(self._user_btn)
        tb.addSpacing(6)
        tb.addWidget(div)
        tb.addWidget(self._min_btn)
        tb.addWidget(self._max_btn)
        tb.addWidget(self._close_btn)

        root.addWidget(topbar)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        sidebar = QWidget(objectName="sidebar")
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(T.SIDEBAR)
        sv = QVBoxLayout(sidebar)
        sv.setContentsMargins(0, 20, 0, 24)
        sv.setSpacing(4)

        logo_container = QWidget()
        logo_container.setStyleSheet("background:transparent;")
        lc_lay = QVBoxLayout(logo_container)
        lc_lay.setContentsMargins(0, 0, 0, 0)
        lc_lay.setSpacing(0)
        lc_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        px = _sidebar_logo()
        if px:
            lbl_logo = QLabel()
            lbl_logo.setPixmap(px)
            lbl_logo.setFixedSize(130, 130)
            lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_logo.setStyleSheet("background:transparent;")
            lc_lay.addWidget(lbl_logo)
        else:
            fb = QLabel("VetSync Pro")
            fb.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            fb.setStyleSheet("color:white;background:transparent;")
            fb.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lc_lay.addWidget(fb)

        sv.addWidget(logo_container)
        sv.addSpacing(14)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{T.PRIMARY_MID};margin:0px 20px;")
        sv.addWidget(sep)
        sv.addSpacing(10)

        nav_items = [
            ("assets/Home.png",      "🏠", "Anasayfa"),
            ("assets/Takvim.png",    "📋", "Randevu Merkezi"),
            ("assets/YeniKayıt.png", "➕", "Yeni Kayıt"),
            ("assets/Analiz.png",    "📊", "Analizler"),
        ]

        self._nav_buttons = []
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background:{T.BG_PAGE};")

        for idx, (png_yol, fallback, label) in enumerate(nav_items):
            btn = QPushButton()
            btn.setObjectName("nav_btn")
            btn.setFont(QFont("Segoe UI", 13))
            btn.setFixedHeight(46)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.setIconSize(QSize(30, 30))
            _px = _load_icon(png_yol, 30)
            if _px:
                btn.setIcon(QIcon(_px))
                btn.setText(f" {label}")
            else:
                btn.setText(f" {fallback} {label}")
            btn.clicked.connect(self._make_nav_handler(idx))
            sv.addWidget(btn)
            self._nav_buttons.append(btn)

        sv.addStretch()

        ver_lbl = QLabel("v1.0.0")
        ver_lbl.setFont(QFont("Segoe UI", 11))
        ver_lbl.setStyleSheet("color:#4A6080;background:transparent;")
        ver_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sv.addWidget(ver_lbl)

        body.addWidget(sidebar)
        body.addWidget(self.stack, 1)
        root.addLayout(body, 1)

        self._page_widgets = [None, None, None, None]

    #  Pencere Kontrol
    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self._max_btn.setText("□")
            self._max_btn.setToolTip("Ekranı Kapla")
        else:
            self.showMaximized()
            self._max_btn.setText("❐")
            self._max_btn.setToolTip("Önceki Boyuta Döndür")

    # Yeniden Boyutlandırma
    _CURSOR_MAP = {
        "left":         Qt.CursorShape.SizeHorCursor,
        "right":        Qt.CursorShape.SizeHorCursor,
        "top":          Qt.CursorShape.SizeVerCursor,
        "bottom":       Qt.CursorShape.SizeVerCursor,
        "top-left":     Qt.CursorShape.SizeFDiagCursor,
        "bottom-right": Qt.CursorShape.SizeFDiagCursor,
        "top-right":    Qt.CursorShape.SizeBDiagCursor,
        "bottom-left":  Qt.CursorShape.SizeBDiagCursor,
    }

    def _get_resize_dir(self, pos):
        m = _RESIZE_MARGIN
        x, y, W, H = pos.x(), pos.y(), self.width(), self.height()
        L = x < m;  R = x > W - m;  T = y < m;  B = y > H - m
        if L and T:  return "top-left"
        if R and T:  return "top-right"
        if L and B:  return "bottom-left"
        if R and B:  return "bottom-right"
        if L:        return "left"
        if R:        return "right"
        if T:        return "top"
        if B:        return "bottom"
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            d = self._get_resize_dir(event.pos())
            if d:
                self._resize_dir       = d
                self._resize_start_pos = event.globalPosition().toPoint()
                self._resize_start_geo = self.geometry()

    def mouseMoveEvent(self, event):
        if self._resize_dir and event.buttons() == Qt.MouseButton.LeftButton:
            self._do_resize(event.globalPosition().toPoint())
        else:
            d = self._get_resize_dir(event.pos())
            self.setCursor(self._CURSOR_MAP[d]) if d else self.unsetCursor()

    def mouseReleaseEvent(self, event):
        self._resize_dir = self._resize_start_pos = self._resize_start_geo = None
        self.unsetCursor()

    def _do_resize(self, gpos):
        if not self._resize_start_pos:
            return
        delta = gpos - self._resize_start_pos
        g     = QRect(self._resize_start_geo)
        d     = self._resize_dir
        mw, mh = self.minimumWidth(), self.minimumHeight()

        if "right"  in d: g.setRight(g.right()   + delta.x())
        if "bottom" in d: g.setBottom(g.bottom() + delta.y())
        if "left"   in d:
            g.setLeft(g.left() + delta.x())
            if g.width() < mw: g.setLeft(g.right() - mw)
        if "top"    in d:
            g.setTop(g.top() + delta.y())
            if g.height() < mh: g.setTop(g.bottom() - mh)

        self.setGeometry(g)

    #  Bildirimler
    def bildirim_goster(self, mesaj, tur="basarili"):
        renk = "#2E7D32" if tur == "basarili" else "#C62828"
        ikon = "✅" if tur == "basarili" else "⚠️"
        if hasattr(self, "_aktif_bildirim") and self._aktif_bildirim:
            try:
                self._aktif_bildirim.deleteLater()
            except Exception:
                pass
        b = QFrame(self.centralWidget())
        b.setStyleSheet(
            f"QFrame{{background-color:{renk};border-radius:10px;}}")
        lay = QHBoxLayout(b)
        lay.setContentsMargins(22, 10, 22, 10)
        lbl = QLabel(f"{ikon} {mesaj}")
        lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl.setStyleSheet("color:white;background:transparent;")
        lay.addWidget(lbl)
        b.adjustSize()
        cw = self.centralWidget()
        b.move((cw.width() - b.width()) // 2, 10)
        b.show()
        b.raise_()
        self._aktif_bildirim = b
        QTimer.singleShot(3000, b.deleteLater)

    def _giris_bildirimi(self):
        isim = self.user.get("username", "")
        self.bildirim_goster(f"Hoş geldiniz, {isim}!", tur="basarili")

    def _update_user_btn(self):
        gender = self.user.get("gender", "erkek") or "erkek"
        if gender.lower() in ("kadın", "kadin", "female", "f"):
            px = _load_icon("assets/profil_kadın.png", 26)
        else:
            px = _load_icon("assets/profil_erkek.png", 26)
        if px:
            self._user_btn.setIcon(QIcon(px))
            self._user_btn.setIconSize(QSize(24, 24))
        self._user_btn.setText(f" {self.user['username']} ▾")

    #  Kullanıcı Menüsü
    
    def _show_user_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #FFFFFF; border: 1px solid #E2E8F0;
                border-radius: 8px; padding: 6px 0px;
                font-family: 'Segoe UI'; font-size: 13px;
            }
            QMenu::item { padding: 9px 20px 9px 12px; color: #0F172A; background: transparent; }
            QMenu::item:selected { background-color: #F1F5F9; color: #1A2942; border-radius: 4px; }
            QMenu::separator { height: 1px; background: #E2E8F0; margin: 4px 10px; }
        """)

        act_ayarlar = QAction("Ayarlar", self)
        _ap = _load_icon("assets/ayarlar.png", 20)
        if _ap: act_ayarlar.setIcon(QIcon(_ap))
        act_ayarlar.triggered.connect(self._open_ayarlar)

        act_cikis = QAction("Çıkış Yap", self)
        _ep = _load_icon("assets/exit.png", 20)
        if _ep: act_cikis.setIcon(QIcon(_ep))
        act_cikis.triggered.connect(self._logout)

        menu.addAction(act_ayarlar)
        menu.addSeparator()
        menu.addAction(act_cikis)
        menu.exec(self._user_btn.mapToGlobal(self._user_btn.rect().bottomLeft()))


    def _make_nav_handler(self, idx):
        def handler(): self._navigate(idx)
        return handler

    def _navigate(self, idx):
        for i, btn in enumerate(self._nav_buttons):
            btn.setChecked(i == idx)
            if i == idx:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {T.PRIMARY_LITE}; color: white;
                        text-align: left; padding: 11px 18px; border: none;
                        border-left: 3px solid {T.ACCENT_TEAL};
                        font-size: 13px; font-weight: 700;
                        border-radius: 0px; margin: 2px 0px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent; color: #7A9CC0;
                        text-align: left; padding: 11px 18px; border: none;
                        font-size: 13px; font-weight: 500;
                        border-radius: 10px; margin: 2px 8px;
                    }}
                    QPushButton:hover {{
                        background-color: {T.PRIMARY_MID}; color: white;
                    }}
                """)

        if self._page_widgets[idx] is None:
            self._page_widgets[idx] = self._create_page(idx)
            self.stack.addWidget(self._page_widgets[idx])

        self.stack.setCurrentWidget(self._page_widgets[idx])

        if idx == 0 and self.dashboard:
            self.dashboard.refresh()

    def _create_page(self, idx):
        if idx == 0:
            from .dashboard_widget import DashboardWidget
            self.dashboard = DashboardWidget(self.user)
            return self.dashboard
        elif idx == 1:
            from .appointment_widget import AppointmentWidget
            return AppointmentWidget(self.user)
        elif idx == 2:
            from .new_record_widget import NewRecordWidget
            return NewRecordWidget(self.user)
        elif idx == 3:
            from .analytics_widget import AnalyticsWidget
            return AnalyticsWidget(self.user)

  
    def _quick_add(self):
        self._nav_buttons[2].click()

    def _open_sms(self):
        from .sms_widget import SmsWindow
        SmsWindow(self.user, self).exec()

    def _open_ayarlar(self):
        from .settings_widget import SettingsWindow
        SettingsWindow(self.user, self).exec()

    def _logout(self):
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Çıkış Yap",
            "Hesabınızdan çıkış yapmak istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            from .auth_window import AuthWindow
            self._auth = AuthWindow()
            self._auth.show()
            self.close()