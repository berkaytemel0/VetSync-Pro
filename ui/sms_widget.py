import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QWidget, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap

import database as db
from worker import Worker

BG      = "#1A2942"   
CARD_BG = "#212D3A"   
ALTIN   = "#B69240"   
MAVI    = "#305F82"   
BEYAZ   = "#FFFFFF"   
SINIR   = "#2A3A50"   


def _fmt_tarih(raw):
    """'2026-03-08 12:25:47'  →  '08/03/2026  12:25'"""
    try:
        tarih, saat = raw[:19].split(" ")
        y, m, d = tarih.split("-")
        return f"{d}/{m}/{y}  {saat[:5]}"
    except Exception:
        return raw[:19]


def _ikon(path, size):
    """512x512 PNG'yi hedef boyuta net ölçekle; bulunamazsa None döner."""
    if os.path.exists(path):
        px = QPixmap(path)
        if not px.isNull():
            return px.scaled(size, size,
                             Qt.AspectRatioMode.KeepAspectRatio,
                             Qt.TransformationMode.SmoothTransformation)
    return None


class SmsLogCard(QFrame):
    def __init__(self, log):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border: 1px solid {SINIR};
                border-radius: 12px;
            }}
            QLabel {{ background: transparent; }}
        """)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 12, 0)
        outer.setSpacing(0)

        bar = QFrame()
        bar.setFixedWidth(4)
        bar.setStyleSheet(f"background: {ALTIN}; border-radius: 4px 0 0 4px; border: none;")

        # İçerik alanı
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        cv = QVBoxLayout(content)
        cv.setContentsMargins(16, 14, 0, 14)
        cv.setSpacing(10)

        tarih_lbl = QLabel(f"📅  {_fmt_tarih(log.get('sent_at', ''))}")
        tarih_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        tarih_lbl.setFixedHeight(26)
        tarih_lbl.setStyleSheet(f"""
            color: {BEYAZ};
            background-color: {MAVI};
            border-radius: 6px;
            padding: 3px 10px;
        """)
        tarih_row = QHBoxLayout()
        tarih_row.setContentsMargins(0, 0, 0, 0)
        tarih_row.addWidget(tarih_lbl)
        tarih_row.addStretch()

        alici_row = QHBoxLayout()
        alici_row.setContentsMargins(0, 0, 0, 0)
        alici_row.setSpacing(8)

        kullanici_lbl = QLabel()
        kullanici_lbl.setFixedSize(20, 20)
        kullanici_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        kullanici_lbl.setStyleSheet("background: transparent;")
        px = _ikon("assets/Kullanici.png", 20)
        if px:
            kullanici_lbl.setPixmap(px)
        else:
            kullanici_lbl.setText("👤")
            kullanici_lbl.setFont(QFont("Segoe UI Emoji", 11))

        c_name = log.get("customer_name", "—")
        phone  = log.get("phone") or log.get("customer_phone", "—")
        alici_lbl = QLabel(f"{c_name}     📞  {phone}")
        alici_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        alici_lbl.setStyleSheet(f"color: {BEYAZ};")

        alici_row.addWidget(kullanici_lbl)
        alici_row.addWidget(alici_lbl)
        alici_row.addStretch()

        msg_frame = QFrame()
        msg_frame.setStyleSheet(f"""
            QFrame {{ background-color: {MAVI}; border-radius: 8px; border: none; }}
            QLabel {{ background: transparent; }}
        """)
        msg_lay = QVBoxLayout(msg_frame)
        msg_lay.setContentsMargins(14, 10, 14, 10)
        msg_lbl = QLabel(log.get("message", ""))
        msg_lbl.setFont(QFont("Segoe UI", 11))
        msg_lbl.setStyleSheet(f"color: {BEYAZ};")
        msg_lbl.setWordWrap(True)
        msg_lay.addWidget(msg_lbl)

        cv.addLayout(tarih_row)
        cv.addLayout(alici_row)
        cv.addWidget(msg_frame)

        outer.addWidget(bar)
        outer.addWidget(content, 1)


class SmsWindow(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("SMS Gönderim Kayıtları")
        self.resize(640, 580)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {BG}; }}
            QScrollBar:vertical {{
                background: {CARD_BG};
                width: 6px;
                border-radius: 3px;
                margin: 4px 8px 4px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {MAVI};
                border-radius: 3px;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(20)

        title_row = QHBoxLayout()
        title_lbl = QLabel("SMS Gönderim Kayıtları")
        title_lbl.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        title_lbl.setStyleSheet(f"color: {BEYAZ}; background: transparent;")

        self._count_lbl = QLabel("  — kayıt  ")
        self._count_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self._count_lbl.setStyleSheet(f"""
            color: {BEYAZ};
            background-color: {ALTIN};
            border-radius: 10px;
            padding: 4px 10px;
        """)

        title_row.addWidget(title_lbl)
        title_row.addStretch()
        title_row.addWidget(self._count_lbl)
        layout.addLayout(title_row)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {SINIR};")
        layout.addWidget(sep)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._cv = QVBoxLayout(self._container)
        self._cv.setContentsMargins(0, 0, 0, 0)
        self._cv.setSpacing(10)

        loading = QLabel("Yükleniyor...")
        loading.setFont(QFont("Segoe UI", 13))
        loading.setStyleSheet(f"color: {BEYAZ}; background: transparent;")
        loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._cv.addWidget(loading)
        self._cv.addStretch()

        scroll.setWidget(self._container)
        layout.addWidget(scroll, 1)

        self._load_logs()

    def _load_logs(self):
        from worker import Worker
        uid = self.user["id"]
        self._sms_worker = Worker(lambda: db.get_sms_logs(uid))
        self._sms_worker.result.connect(self._apply_logs)
        self._sms_worker.error.connect(
            lambda e: print(f"[SMS] Yükleme hatası: {e}"))
        self._sms_worker.start()

    def _apply_logs(self, logs):
        while self._cv.count():
            item = self._cv.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._count_lbl.setText(f"  {len(logs)} kayıt  ")

        if not logs:
            empty = QLabel("Henüz SMS gönderim kaydı bulunmuyor.")
            empty.setFont(QFont("Segoe UI", 13))
            empty.setStyleSheet(f"color: {BEYAZ}; background: transparent;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._cv.addWidget(empty)
        else:
            for log in logs:
                self._cv.addWidget(SmsLogCard(log))
        self._cv.addStretch()