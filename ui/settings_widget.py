from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QWidget, QComboBox, QTabWidget
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont



import styles.theme as T
import database as db
from worker import Worker



BG          = "#151D2B"
CARD_BG     = "#1C2535"
INPUT_BG    = "#1E2A3B"
INPUT_BORD  = "#2A3A55"
INPUT_FOCUS = "#7C3AED"
BEYAZ       = "#FFFFFF"
MUTED       = "#8B9BB4"
TAB_ACTIVE  = "#7C3AED"
BTN_BG      = "#1A2942"
BTN_HOVER   = "#243C6A"
DANGER      = "#EF4444"
SUCCESS     = "#10B981"




def _input(placeholder="", echo=False):
    inp = QLineEdit()
    inp.setPlaceholderText(placeholder)
    inp.setFixedHeight(52)
    inp.setFont(QFont("Segoe UI", 12))
    inp.setStyleSheet(f"""
        QLineEdit {{
            background-color: {INPUT_BG};
            border: 1.5px solid {INPUT_BORD};
            border-radius: 10px;
            padding: 0 16px;
            color: {BEYAZ};
            font-size: 13px;
        }}
        QLineEdit:focus {{
            border-color: {INPUT_FOCUS};
        }}
        QLineEdit::placeholder {{
            color: {MUTED};
        }}
    """)
    if echo:
        inp.setEchoMode(QLineEdit.EchoMode.Password)
    return inp




def _combo():
    cb = QComboBox()
    cb.setFixedHeight(52)
    cb.setFont(QFont("Segoe UI", 12))
    cb.setStyleSheet(f"""
        QComboBox {{
            background-color: {INPUT_BG};
            border: 1.5px solid {INPUT_BORD};
            border-radius: 10px;
            padding: 0 16px;
            color: {BEYAZ};
            font-size: 13px;
        }}
        QComboBox:focus {{ border-color: {INPUT_FOCUS}; }}
        QComboBox::drop-down {{ border: none; width: 30px; }}
        QComboBox::down-arrow {{ image: url(assets/down.png); width: 14px; height: 14px; }}
        QComboBox QAbstractItemView {{
            background: {CARD_BG};
            color: {BEYAZ};
            selection-background-color: {TAB_ACTIVE};
            border: 1px solid {INPUT_BORD};
        }}
    """)
    return cb




def _lbl(text):
    l = QLabel(text)
    l.setFont(QFont("Segoe UI", 11))
    l.setStyleSheet(f"color: {MUTED}; background: transparent;")
    return l




def _section(text):
    l = QLabel(text)
    l.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
    l.setStyleSheet(f"color: {BEYAZ}; background: transparent;")
    return l




def _sep():
    f = QFrame()
    f.setFixedHeight(1)
    f.setStyleSheet(f"background: {INPUT_BORD};")
    return f




def _msg():
    l = QLabel("")
    l.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
    l.setAlignment(Qt.AlignmentFlag.AlignCenter)
    l.setWordWrap(True)
    l.setStyleSheet("background: transparent;")
    l.setFixedHeight(28)
    return l




def _btn(text):
    b = QPushButton(text)
    b.setFixedHeight(52)
    b.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setStyleSheet(f"""
        QPushButton {{
            background-color: {SUCCESS};
            color: {BEYAZ};
            border-radius: 10px;
            border: none;
        }}
        QPushButton:hover {{ background-color: #0D9E82; }}
        QPushButton:disabled {{
            background-color: {INPUT_BORD};
            color: {MUTED};
        }}
    """)
    return b




class SettingsWindow(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Ayarlar")
        self.resize(480, 620)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._drag_pos = None
        self.setStyleSheet("QDialog { background-color: transparent; }")
        self._build_ui()



    def _build_ui(self):
        self._container = QFrame(self)
        self._container.setObjectName("container")
        self._container.setStyleSheet(f"""
            QFrame#container {{
                background-color: {BG};
                border-radius: 12px;
                border: 1px solid {INPUT_BORD};
            }}
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(1, 1, 1, 1)
        outer.addWidget(self._container)

        root = QVBoxLayout(self._container)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Özel başlık çubuğu ───────────────────────────────────────────────
        titlebar = QFrame()
        titlebar.setFixedHeight(48)
        titlebar.setStyleSheet(f"""
            QFrame {{
                background-color: {BG};
                border-radius: 12px 12px 0 0;
                border-bottom: 1px solid {INPUT_BORD};
            }}
        """)
        tb_lay = QHBoxLayout(titlebar)
        tb_lay.setContentsMargins(16, 0, 12, 0)
        tb_lay.setSpacing(8)

        icon_lbl = QLabel("⚙️")
        icon_lbl.setFont(QFont("Segoe UI Emoji", 13))
        icon_lbl.setStyleSheet("background: transparent; color: white;")

        title_lbl = QLabel("Ayarlar")
        title_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title_lbl.setStyleSheet(f"color: {BEYAZ}; background: transparent;")

        tb_lay.addWidget(icon_lbl)
        tb_lay.addWidget(title_lbl)
        tb_lay.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(32, 32)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setFont(QFont("Segoe UI", 11))
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {MUTED};
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background: #EF4444;
                color: white;
            }}
        """)
        close_btn.clicked.connect(self.close)
        tb_lay.addWidget(close_btn)

        root.addWidget(titlebar)

        # ── Tab bar ───────────────────────────────────────────────────────────
        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)
        self._tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: {CARD_BG};
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }}
            QTabBar {{
                background: {BG};
            }}
            QTabBar::tab {{
                background: {BG};
                color: {MUTED};
                padding: 14px 28px;
                border: none;
                font-size: 13px;
                font-weight: 600;
                font-family: 'Segoe UI';
            }}
            QTabBar::tab:selected {{
                color: {BEYAZ};
                border-bottom: 3px solid {TAB_ACTIVE};
                background: {BG};
            }}
            QTabBar::tab:hover:!selected {{
                color: {BEYAZ};
            }}
        """)

        self._tabs.addTab(self._profil_tab(), "👤  Profil")
        self._tabs.addTab(self._sifre_tab(),  "🔒  Şifre")
        self._tabs.addTab(self._klinik_tab(), "🏥  Klinik")

        # Klinik sahibiyse Hekim Yönetimi sekmesi de ekle
        if self.user.get("role") == "Klinik Sahibi":
            self._tabs.addTab(self._hekim_tab(), "👨‍⚕️  Hekimler")

        root.addWidget(self._tabs)



    # ── PROFİL ────────────────────────────────────────────────────────────────
    def _profil_tab(self):
        w = QWidget()
        w.setStyleSheet(f"background: {CARD_BG}; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px;")
        v = QVBoxLayout(w)
        v.setContentsMargins(32, 28, 32, 28)
        v.setSpacing(12)

        v.addWidget(_section("Profil Bilgileri"))
        v.addWidget(_sep())
        v.addSpacing(4)

        v.addWidget(_lbl("Kullanıcı Adı"))
        self.p_username = _input()
        self.p_username.setText(self.user.get("username", ""))
        v.addWidget(self.p_username)

        v.addWidget(_lbl("E-posta"))
        self.p_email = _input()
        self.p_email.setText(self.user.get("email", ""))
        v.addWidget(self.p_email)

        v.addWidget(_lbl("Cinsiyet"))
        self.p_cinsiyet = _combo()
        self.p_cinsiyet.addItems(["Erkek", "Kadın"])
        self.p_cinsiyet.setCurrentText(self.user.get("gender", "erkek").capitalize())
        v.addWidget(self.p_cinsiyet)

        v.addSpacing(8)
        self.p_msg = _msg()
        btn = _btn("Profili Güncelle")
        btn.clicked.connect(self._save_profil)
        v.addWidget(btn)
        v.addWidget(self.p_msg)
        v.addStretch()
        return w



    # ── ŞİFRE ─────────────────────────────────────────────────────────────────
    def _sifre_tab(self):
        w = QWidget()
        w.setStyleSheet(f"background: {CARD_BG}; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px;")
        v = QVBoxLayout(w)
        v.setContentsMargins(32, 28, 32, 28)
        v.setSpacing(12)

        v.addWidget(_section("Şifre Değiştir"))
        v.addWidget(_sep())
        v.addSpacing(4)

        v.addWidget(_lbl("Mevcut Şifre"))
        self.s_current = _input("••••••••", echo=True)
        v.addWidget(self.s_current)

        v.addWidget(_lbl("Yeni Şifre"))
        self.s_new = _input("En az 4 karakter", echo=True)
        v.addWidget(self.s_new)

        v.addWidget(_lbl("Yeni Şifre Tekrar"))
        self.s_confirm = _input("Yeni şifreyi tekrar girin", echo=True)
        v.addWidget(self.s_confirm)

        v.addSpacing(8)
        self.s_msg = _msg()
        btn = _btn("Şifreyi Güncelle")
        btn.clicked.connect(self._save_sifre)
        v.addWidget(btn)
        v.addWidget(self.s_msg)
        v.addStretch()
        return w



    # ── KLİNİK ────────────────────────────────────────────────────────────────
    def _klinik_tab(self):
        w = QWidget()
        w.setStyleSheet(f"background: {CARD_BG}; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px;")
        v = QVBoxLayout(w)
        v.setContentsMargins(32, 28, 32, 28)
        v.setSpacing(12)

        v.addWidget(_section("Klinik Bilgileri"))
        v.addWidget(_sep())
        v.addSpacing(4)

        v.addWidget(_lbl("Klinik Adı"))
        self.k_adi = _input("Kliniğinizin adı")
        v.addWidget(self.k_adi)

        v.addWidget(_lbl("Telefon"))
        self.k_tel = _input("Klinik telefon numarası")
        v.addWidget(self.k_tel)

        v.addWidget(_lbl("Şehir"))
        self.k_sehir = _input("Şehir")
        v.addWidget(self.k_sehir)

        v.addWidget(_lbl("Adres"))
        self.k_adres = _input("Açık adres")
        v.addWidget(self.k_adres)

        # ── ROL KONTROLÜ ──────────────────────────────────────────────────────
        is_hekim = self.user.get("role") == "Veteriner Hekim"
        if is_hekim:
            for field in (self.k_adi, self.k_tel, self.k_sehir, self.k_adres):
                field.setReadOnly(True)
                field.setStyleSheet(f"""
                    QLineEdit {{
                        background-color: {BG};
                        border: 1.5px solid {INPUT_BORD};
                        border-radius: 10px;
                        padding: 0 16px;
                        color: {MUTED};
                        font-size: 13px;
                    }}
                """)
            info = QLabel("ℹ️ Klinik bilgileri yalnızca klinik sahibi tarafından düzenlenebilir.")
            info.setFont(QFont("Segoe UI", 10))
            info.setWordWrap(True)
            info.setStyleSheet(f"color: {MUTED}; background: transparent;")
            v.addWidget(info)

        v.addSpacing(8)
        self.k_msg = _msg()

        if not is_hekim:
            btn = _btn("Klinik Bilgilerini Kaydet")
            btn.clicked.connect(self._save_klinik)
            v.addWidget(btn)

        v.addWidget(self.k_msg)
        v.addStretch()

        self._load_klinik()
        return w



    # ── HEKİM YÖNETİMİ (Sadece Klinik Sahibi) ────────────────────────────────
    def _hekim_tab(self):
        w = QWidget()
        w.setStyleSheet(f"background: {CARD_BG}; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px;")
        v = QVBoxLayout(w)
        v.setContentsMargins(32, 28, 32, 28)
        v.setSpacing(12)

        v.addWidget(_section("Hekim Yönetimi"))
        v.addWidget(_sep())
        v.addSpacing(4)

        v.addWidget(_lbl("Veteriner Hekim Ekle (Kullanıcı Adı)"))
        self.h_input = _input("Hekimin kullanıcı adını girin")
        v.addWidget(self.h_input)

        self.h_msg = _msg()
        btn_ekle = _btn("Hekim Ekle")
        btn_ekle.clicked.connect(self._hekim_ekle)
        v.addWidget(btn_ekle)
        v.addWidget(self.h_msg)

        v.addSpacing(8)
        v.addWidget(_sep())
        v.addSpacing(8)

        v.addWidget(_lbl("Kliniğe Kayıtlı Hekimler"))
        self.h_list_widget = QWidget()
        self.h_list_widget.setStyleSheet("background: transparent;")
        self.h_list_layout = QVBoxLayout(self.h_list_widget)
        self.h_list_layout.setContentsMargins(0, 0, 0, 0)
        self.h_list_layout.setSpacing(8)
        v.addWidget(self.h_list_widget)

        v.addStretch()

        self._load_hekimler()
        return w



    # ── HEKİM YÜKLEME ────────────────────────────────────────────────────────
    def _load_hekimler(self):
        uid = self.user["id"]
        self._hlw = Worker(lambda: db.get_klinik_hekimleri(uid))
        self._hlw.result.connect(self._apply_hekimler)
        self._hlw.start()



    def _apply_hekimler(self, hekimler):
        # Listeyi temizle
        while self.h_list_layout.count():
            item = self.h_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not hekimler:
            bos = QLabel("Henüz kayıtlı hekim yok.")
            bos.setFont(QFont("Segoe UI", 11))
            bos.setStyleSheet(f"color: {MUTED}; background: transparent;")
            self.h_list_layout.addWidget(bos)
            return

        for h in hekimler:
            row = QFrame()
            row.setObjectName("hekimRow")
            row.setCursor(Qt.CursorShape.PointingHandCursor)
            row.setStyleSheet(f"""
                QFrame#hekimRow {{
                    background-color: {INPUT_BG};
                    border: 1px solid {INPUT_BORD};
                    border-radius: 8px;
                }}
                QFrame#hekimRow:hover {{
                    background-color: {BTN_HOVER};
                    border-color: {INPUT_FOCUS};
                }}
            """)
            rl = QHBoxLayout(row)
            rl.setContentsMargins(14, 10, 14, 10)

            name_lbl = QLabel(f"👨‍⚕️  {h['kullanici_adi']}")
            name_lbl.setFont(QFont("Segoe UI", 12))
            name_lbl.setStyleSheet(f"color: {BEYAZ}; background: transparent;")

            # Profil görüntüle butonu
            profil_btn = QPushButton("Profil")
            profil_btn.setFixedSize(64, 32)
            profil_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            profil_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            profil_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {TAB_ACTIVE};
                    color: white;
                    border-radius: 6px;
                    border: none;
                }}
                QPushButton:hover {{ background-color: #6D28D9; }}
            """)
            profil_btn.clicked.connect(
                lambda _, hid=h["id"]: self._hekim_profil_ac(hid)
            )

            cikar_btn = QPushButton("Çıkar")
            cikar_btn.setFixedSize(64, 32)
            cikar_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            cikar_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            cikar_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {DANGER};
                    color: white;
                    border-radius: 6px;
                    border: none;
                }}
                QPushButton:hover {{ background-color: #C53030; }}
            """)
            cikar_btn.clicked.connect(
                lambda _, hid=h["id"]: self._hekim_cikar(hid)
            )

            rl.addWidget(name_lbl)
            rl.addStretch()
            rl.addWidget(profil_btn)
            rl.addWidget(cikar_btn)
            self.h_list_layout.addWidget(row)



    # ── HEKİM PROFİL AÇMA ────────────────────────────────────────────────────
    def _hekim_profil_ac(self, hekim_id):
        import importlib.util, os

        _dir = os.path.dirname(os.path.abspath(__file__))
        spec = importlib.util.spec_from_file_location(
            "doctor_profile_dialog",
            os.path.join(_dir, "doctor_profile_dialog.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        dlg = mod.DoctorProfileDialog(hekim_id, parent=self)
        dlg.exec()
   



    # ── HEKİM EKLE ────────────────────────────────────────────────────────────
    def _hekim_ekle(self):
        kadi = self.h_input.text().strip()
        if not kadi:
            self._show(self.h_msg, "❌ Kullanıcı adı girin.", DANGER)
            return
        sahip_id = self.user["id"]

        def _do():
            return db.hekim_kliniğe_ekle(kadi, sahip_id)

        def _done(res):
            ok, msg = res
            if ok:
                self._show(self.h_msg, f"✅ {msg}", SUCCESS)
                self.h_input.clear()
                self._load_hekimler()
            else:
                self._show(self.h_msg, f"❌ {msg}", DANGER)

        self._hew = Worker(_do)
        self._hew.result.connect(_done)
        self._hew.error.connect(lambda e: self._show(self.h_msg, f"❌ Hata: {e}", DANGER))
        self._hew.start()



    # ── HEKİM ÇIKAR ───────────────────────────────────────────────────────────
    def _hekim_cikar(self, hekim_id):
        sahip_id = self.user["id"]

        def _do():
            return db.hekim_klinikten_cikar(hekim_id, sahip_id)

        def _done(res):
            ok, msg = res
            if ok:
                self._show(self.h_msg, f"✅ {msg}", SUCCESS)
                self._load_hekimler()
            else:
                self._show(self.h_msg, f"❌ {msg}", DANGER)

        self._hcw = Worker(_do)
        self._hcw.result.connect(_done)
        self._hcw.error.connect(lambda e: self._show(self.h_msg, f"❌ Hata: {e}", DANGER))
        self._hcw.start()



    # ── VERİ YÜKLEME ──────────────────────────────────────────────────────────
    def _load_klinik(self):
        uid      = self.user["id"]
        is_hekim = self.user.get("role") == "Veteriner Hekim"

        if is_hekim:
            sahip_id = self.user.get("klinik_sahibi_id")
            if not sahip_id:
                self._show(self.k_msg, "ℹ️ Henüz bir kliniğe bağlı değilsiniz.", MUTED)
                return
            self._kw = Worker(lambda: db.get_klinik(sahip_id))
        else:
            self._kw = Worker(lambda: db.get_klinik(uid))

        self._kw.result.connect(self._apply_klinik)
        self._kw.start()



    def _apply_klinik(self, data):
        if not data:
            return
        self.k_adi.setText(data.get("klinik_adi", ""))
        self.k_tel.setText(data.get("telefon", ""))
        self.k_sehir.setText(data.get("sehir", ""))
        self.k_adres.setText(data.get("adres", ""))



    # ── KAYDET ────────────────────────────────────────────────────────────────
    def _save_profil(self):
        username = self.p_username.text().strip()
        email    = self.p_email.text().strip()
        cinsiyet = self.p_cinsiyet.currentText().lower()
        if not username or not email:
            self._show(self.p_msg, "❌ Tüm alanları doldurun.", DANGER)
            return
        uid = self.user["id"]

        def _do():
            return db.update_user_profile(uid, username, email, cinsiyet)

        def _done(res):
            ok, msg = res
            if ok:
                self.user["username"] = username.capitalize()
                self.user["email"]    = email.lower()
                self.user["gender"]   = cinsiyet
                self._show(self.p_msg, f"✅ {msg}", SUCCESS)
                main = self.parent()
                if main and hasattr(main, "_update_user_btn"):
                    main._update_user_btn()
            else:
                self._show(self.p_msg, f"❌ {msg}", DANGER)

        self._pw = Worker(_do)
        self._pw.result.connect(_done)
        self._pw.start()



    def _save_sifre(self):
        current = self.s_current.text()
        new     = self.s_new.text()
        confirm = self.s_confirm.text()
        if not current or not new or not confirm:
            self._show(self.s_msg, "❌ Tüm alanları doldurun.", DANGER)
            return
        if len(new) < 4:
            self._show(self.s_msg, "❌ Şifre en az 4 karakter olmalı.", DANGER)
            return
        if new != confirm:
            self._show(self.s_msg, "❌ Yeni şifreler eşleşmiyor.", DANGER)
            return
        uid = self.user["id"]

        def _do():
            return db.update_password(uid, current, new)

        def _done(res):
            ok, msg = res
            if ok:
                self._show(self.s_msg, f"✅ {msg}", SUCCESS)
                self.s_current.clear()
                self.s_new.clear()
                self.s_confirm.clear()
            else:
                self._show(self.s_msg, f"❌ {msg}", DANGER)

        self._sw = Worker(_do)
        self._sw.result.connect(_done)
        self._sw.start()



    def _save_klinik(self):
        uid = self.user["id"]

        def _do():
            db.save_klinik(
                uid,
                self.k_adi.text().strip(),
                self.k_tel.text().strip(),
                self.k_adres.text().strip(),
                self.k_sehir.text().strip()
            )

        def _done(_):
            self._show(self.k_msg, "✅ Klinik bilgileri kaydedildi.", SUCCESS)

        self._kkw = Worker(_do)
        self._kkw.result.connect(_done)
        self._kkw.error.connect(
            lambda e: self._show(self.k_msg, f"❌ Hata: {e}", DANGER))
        self._kkw.start()



    def _show(self, lbl, text, color):
        lbl.setStyleSheet(
            f"color: {color}; font-size: 12px; font-weight: 600; background: transparent;")
        lbl.setText(text)



    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()



    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)



    def mouseReleaseEvent(self, event):
        self._drag_pos = None
