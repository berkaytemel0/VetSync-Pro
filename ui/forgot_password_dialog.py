"""
ForgotPasswordDialog — Şifremi Unuttum ekranı.
"""
from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QWidget, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPainter, QBrush, QColor, QPen

import styles.theme as T
import database as db
from worker import Worker


class _MiniDekorPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(220)
        self._build()

    def _build(self):
        lv = QVBoxLayout(self)
        lv.setContentsMargins(28, 36, 28, 28)
        lv.setSpacing(0)

        icon = QLabel("🔐")
        icon.setFont(QFont("Segoe UI Emoji", 52))
        icon.setStyleSheet("background:transparent;color:white;")
        icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        lv.addWidget(icon, alignment=Qt.AlignmentFlag.AlignHCenter)
        lv.addSpacing(20)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{T.PRIMARY_MID};")
        lv.addWidget(sep)
        lv.addSpacing(20)

        title = QLabel("Şifre\nSıfırlama")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color:white;background:transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        lv.addWidget(title)
        lv.addSpacing(16)

        desc = QLabel(
            "Kayıtlı kullanıcı adınızı\n"
            "ve e-posta adresinizi\n"
            "girerek yeni şifre\n"
            "belirleyebilirsiniz."
        )
        desc.setFont(QFont("Segoe UI", 11))
        desc.setStyleSheet("color:#A8C4DC;background:transparent;")
        desc.setWordWrap(True)
        lv.addWidget(desc)
        lv.addStretch()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor(T.PRIMARY)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRect(0, 0, self.width(), self.height())
        p.setBrush(QBrush(QColor("#3A80D2")))
        for row in range(4):
            for col in range(4):
                cx = self.width() - 80 + col * 16
                cy = 8 + row * 16
                p.drawEllipse(cx, cy, 4, 4)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor("#2E4A72"), 2))
        p.drawEllipse(4, self.height() - 75, 70, 70)
        p.drawEllipse(18, self.height() - 60, 42, 42)


class ForgotPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("VetSync Pro — Şifre Sıfırlama")
        self.setFixedSize(660, 420)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowCloseButtonHint
        )
        self.setStyleSheet(T.APP_STYLE + "QDialog{background:white;}")
        self._build_ui()
        self._show_step(0)

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(_MiniDekorPanel())

        right = QWidget()
        right.setStyleSheet("background:white;")
        rv = QVBoxLayout(right)
        rv.setContentsMargins(40, 32, 40, 32)
        rv.setSpacing(0)

        title = QLabel("Şifremi Unuttum")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{T.TEXT_HEAD};")

        sub = QLabel("Hesabınıza bağlı bilgileri girin.")
        sub.setFont(QFont("Segoe UI", 11))
        sub.setStyleSheet(f"color:{T.TEXT_MUTED};margin-bottom:24px;")

        ul = QLabel("Kullanıcı Adı")
        ul.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        ul.setStyleSheet(T.FIELD_LABEL)

        self.inp_username = QLineEdit()
        self.inp_username.setPlaceholderText("kullanici_adi")
        self.inp_username.setFixedHeight(44)
        self.inp_username.setStyleSheet(T.LINE_EDIT)

        el = QLabel("E-Posta Adresi")
        el.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        el.setStyleSheet(T.FIELD_LABEL)
        el.setContentsMargins(0, 12, 0, 0)

        self.inp_email = QLineEdit()
        self.inp_email.setPlaceholderText("ornek@email.com")
        self.inp_email.setFixedHeight(44)
        self.inp_email.setStyleSheet(T.LINE_EDIT)

        nl = QLabel("Yeni Şifre")
        nl.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        nl.setStyleSheet(T.FIELD_LABEL)
        nl.setContentsMargins(0, 12, 0, 0)

        self.inp_new_pass = QLineEdit()
        self.inp_new_pass.setPlaceholderText("••••••••")
        self.inp_new_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_new_pass.setFixedHeight(44)
        self.inp_new_pass.setStyleSheet(T.LINE_EDIT)

        self.msg_lbl = QLabel("")
        self.msg_lbl.setFont(QFont("Segoe UI", 11))
        self.msg_lbl.setStyleSheet(f"color:{T.DANGER};")
        self.msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.msg_lbl.setWordWrap(True)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.btn_reset = QPushButton("ŞİFREYİ SIFIRLA")
        self.btn_reset.setFixedHeight(46)
        self.btn_reset.setStyleSheet(T.PRIMARY_BTN)
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_cancel = QPushButton("İptal")
        btn_cancel.setFixedHeight(46)
        btn_cancel.setStyleSheet(T.OUTLINE_BTN)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)

        btn_row.addWidget(self.btn_reset, 2)
        btn_row.addWidget(btn_cancel, 1)

        self._form_widget = QWidget()
        self._form_widget.setStyleSheet("background:transparent;")
        fv = QVBoxLayout(self._form_widget)
        fv.setContentsMargins(0, 0, 0, 0)
        fv.setSpacing(0)
        fv.addWidget(title)
        fv.addWidget(sub)
        fv.addWidget(ul)
        fv.addSpacing(5)
        fv.addWidget(self.inp_username)
        fv.addWidget(el)
        fv.addSpacing(5)
        fv.addWidget(self.inp_email)
        fv.addWidget(nl)
        fv.addSpacing(5)
        fv.addWidget(self.inp_new_pass)
        fv.addSpacing(14)
        fv.addWidget(self.msg_lbl)
        fv.addSpacing(10)
        fv.addLayout(btn_row)
        fv.addStretch()

        self._success_widget = QWidget()
        self._success_widget.setStyleSheet("background:transparent;")
        sv = QVBoxLayout(self._success_widget)
        sv.setContentsMargins(0, 0, 0, 0)
        sv.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ok_icon = QLabel("✅")
        ok_icon.setFont(QFont("Segoe UI Emoji", 48))
        ok_icon.setStyleSheet("background:transparent;")
        ok_icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        ok_title = QLabel("Şifre Güncellendi!")
        ok_title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        ok_title.setStyleSheet(f"color:{T.TEXT_HEAD};background:transparent;")
        ok_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        ok_sub = QLabel("Şifreniz başarıyla değiştirildi.\nYeni şifrenizle giriş yapabilirsiniz.")
        ok_sub.setFont(QFont("Segoe UI", 12))
        ok_sub.setStyleSheet(f"color:{T.TEXT_MUTED};background:transparent;")
        ok_sub.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        ok_sub.setWordWrap(True)

        btn_close = QPushButton("Giriş Ekranına Dön")
        btn_close.setFixedHeight(46)
        btn_close.setFixedWidth(220)
        btn_close.setStyleSheet(T.PRIMARY_BTN)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(self.accept)

        sv.addStretch()
        sv.addWidget(ok_icon)
        sv.addSpacing(12)
        sv.addWidget(ok_title)
        sv.addSpacing(8)
        sv.addWidget(ok_sub)
        sv.addSpacing(24)
        sv.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignHCenter)
        sv.addStretch()

        rv.addWidget(self._form_widget)
        rv.addWidget(self._success_widget)
        root.addWidget(right, 1)

        self.btn_reset.clicked.connect(self._on_reset)
        self.inp_username.returnPressed.connect(lambda: self.inp_email.setFocus())
        self.inp_email.returnPressed.connect(lambda: self.inp_new_pass.setFocus())
        self.inp_new_pass.returnPressed.connect(self.btn_reset.click)

    def _show_step(self, step):
        self._form_widget.setVisible(step == 0)
        self._success_widget.setVisible(step == 1)

    def _on_reset(self):
        username = self.inp_username.text().strip()
        email    = self.inp_email.text().strip()
        new_pass = self.inp_new_pass.text()

        if not username or not email or not new_pass:
            self._set_msg("Lütfen tüm alanları doldurun.", T.DANGER)
            return
        if len(new_pass) < 4:
            self._set_msg("Yeni şifre en az 4 karakter olmalıdır.", T.DANGER)
            return

        self.btn_reset.setEnabled(False)

        def _do():
            return db.reset_password(username, email, new_pass)

        def _done(result):
            self.btn_reset.setEnabled(True)
            ok, msg = result
            if ok:
                self._fade_to_success()
            else:
                self._set_msg(msg, T.DANGER)

        def _err(e):
            self.btn_reset.setEnabled(True)
            self._set_msg(f"Bir hata oluştu: {e}", T.DANGER)

        self._worker = Worker(_do)
        self._worker.result.connect(_done)
        self._worker.error.connect(_err)
        self._worker.start()

    def _fade_to_success(self):
        fx = QGraphicsOpacityEffect(self._form_widget)
        self._form_widget.setGraphicsEffect(fx)
        anim = QPropertyAnimation(fx, b"opacity")
        anim.setDuration(220)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        def _swap():
            self._form_widget.setGraphicsEffect(None)
            self._show_step(1)
            fx2 = QGraphicsOpacityEffect(self._success_widget)
            self._success_widget.setGraphicsEffect(fx2)
            fx2.setOpacity(0.0)
            anim2 = QPropertyAnimation(fx2, b"opacity")
            anim2.setDuration(220)
            anim2.setStartValue(0.0)
            anim2.setEndValue(1.0)
            anim2.setEasingCurve(QEasingCurve.Type.InCubic)
            anim2.finished.connect(
                lambda: self._success_widget.setGraphicsEffect(None))
            anim2.start()
            self._anim2 = anim2

        anim.finished.connect(_swap)
        anim.start()
        self._anim = anim

    def _set_msg(self, text, color):
        self.msg_lbl.setStyleSheet(f"color:{color};font-size:11px;font-family:'Segoe UI';")
        self.msg_lbl.setText(text)