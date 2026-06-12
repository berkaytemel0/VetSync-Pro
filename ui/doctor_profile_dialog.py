from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QWidget, QPushButton, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import database as db


class DoctorProfileDialog(QDialog):
    def __init__(self, hekim_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hekim Profili")
        self.setFixedSize(520, 680)
        self.setStyleSheet("background: #1a1a2e; color: white;")

        detay = db.get_hekim_detay(hekim_id)
        if not detay:
            QLabel("Hekim bulunamadı.", self)
            return

        ana = QVBoxLayout(self)
        ana.setContentsMargins(20, 20, 20, 20)
        ana.setSpacing(14)

        # ── Başlık ──────────────────────────────────
        baslik = QLabel(detay["ad_soyad"])
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        baslik.setStyleSheet("color: #a78bfa;")
        ana.addWidget(baslik)

        rol_lbl = QLabel("👨‍⚕️  Veteriner Hekim")
        rol_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rol_lbl.setStyleSheet("color: #888; font-size: 13px;")
        ana.addWidget(rol_lbl)

        # ── İletişim ────────────────────────────────
        self._kart_ekle(ana, "📧  E-posta", detay["eposta"])
        self._kart_ekle(ana, "📞  Telefon", detay["telefon"] or "—")

        # ── İstatistik kartları — 2x3 Grid ──────────
        istat_frame = QFrame()
        istat_frame.setStyleSheet(
            "background: #252540; border-radius: 12px; padding: 4px;")
        grid = QGridLayout(istat_frame)
        grid.setSpacing(8)
        grid.setContentsMargins(10, 10, 10, 10)

        istatler = [
            ("Müşteri",    detay["musteri_sayisi"], "#6ee7b7"),
            ("Hasta",      detay["hayvan_sayisi"],  "#93c5fd"),
            ("Randevu",    detay["toplam_randevu"], "#fcd34d"),
            ("Bugün",      detay["bugunki"],        "#f9a8d4"),
            ("Tamamlanan", detay["tamamlanan"],     "#86efac"),
            ("İptal",      detay["iptal"],          "#fca5a5"),
        ]

        for i, (baslik_txt, sayi, renk) in enumerate(istatler):
            satir = i // 3
            sutun = i % 3
            self._istat_kutu_grid(grid, satir, sutun, baslik_txt, sayi, renk)

        ana.addWidget(istat_frame)

        # ── Son Randevular ───────────────────────────
        son_lbl = QLabel("Son Randevular")
        son_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        son_lbl.setStyleSheet("color: #ccc; margin-top: 4px;")
        ana.addWidget(son_lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        ic = QWidget()
        ic.setStyleSheet("background: transparent;")
        ic_layout = QVBoxLayout(ic)
        ic_layout.setSpacing(6)

        if detay["son_randevular"]:
            for r in detay["son_randevular"]:
                hayvan  = (r.get("hayvanlar")  or {}).get("ad",  "—")
                tur     = (r.get("hayvanlar")  or {}).get("tur", "")
                musteri = (r.get("musteriler") or {}).get("ad",  "—")
                islem   = r.get("islem_turu", "—")
                tarih   = (r.get("randevu_tarihi") or "")[:10]
                durum   = r.get("durum", "pending")
                renk    = {"completed": "#86efac",
                           "cancelled": "#fca5a5",
                           "pending":   "#fcd34d"}.get(durum, "#ccc")
                ikon    = {"completed": "✅",
                           "cancelled": "❌",
                           "pending":   "⏳"}.get(durum, "—")

                satir = QFrame()
                satir.setStyleSheet("background: #2a2a3a; border-radius: 8px;")
                sl = QHBoxLayout(satir)
                sl.setContentsMargins(12, 8, 12, 8)

                sol = QVBoxLayout()
                sol.setSpacing(2)
                sol.addWidget(self._kucuk(
                    f"🐾 {hayvan} ({tur})  •  👤 {musteri}", bold=True))
                sol.addWidget(self._kucuk(f"{islem}  |  {tarih}"))
                sl.addLayout(sol, 1)

                durum_lbl = QLabel(ikon)
                durum_lbl.setStyleSheet(f"color: {renk}; font-size: 16px;")
                sl.addWidget(durum_lbl)

                ic_layout.addWidget(satir)
        else:
            bos = QLabel("Henüz randevu yok.")
            bos.setStyleSheet("color: #666; font-size: 13px;")
            bos.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ic_layout.addWidget(bos)

        ic_layout.addStretch()
        scroll.setWidget(ic)
        ana.addWidget(scroll, 1)

        # ── Kapat butonu ─────────────────────────────
        kapat = QPushButton("Kapat")
        kapat.setFixedHeight(40)
        kapat.setStyleSheet("""
            QPushButton {
                background: #3b3b5c; color: white;
                border-radius: 8px; font-size: 13px;
            }
            QPushButton:hover { background: #4c4c70; }
        """)
        kapat.clicked.connect(self.accept)
        ana.addWidget(kapat)

    # ── Yardımcılar ──────────────────────────────────────────────────────────

    def _kart_ekle(self, layout, etiket, deger):
        f = QFrame()
        f.setStyleSheet("background: #252540; border-radius: 8px;")
        hl = QHBoxLayout(f)
        hl.setContentsMargins(14, 10, 14, 10)
        lbl = QLabel(etiket)
        lbl.setStyleSheet("color: #aaa; font-size: 13px;")
        val = QLabel(deger)
        val.setStyleSheet("color: white; font-size: 13px;")
        val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        hl.addWidget(lbl)
        hl.addWidget(val, 1)
        layout.addWidget(f)

    def _istat_kutu_grid(self, grid, row, col, baslik, sayi, renk):
        f = QFrame()
        f.setStyleSheet("background: #1e1e38; border-radius: 8px;")
        vl = QVBoxLayout(f)
        vl.setContentsMargins(10, 12, 10, 12)
        vl.setSpacing(4)

        s_lbl = QLabel(str(sayi))
        s_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        s_lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        s_lbl.setStyleSheet(f"color: {renk};")

        b_lbl = QLabel(baslik)
        b_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        b_lbl.setStyleSheet("color: #888; font-size: 11px;")

        vl.addWidget(s_lbl)
        vl.addWidget(b_lbl)
        grid.addWidget(f, row, col)

    def _kucuk(self, metin, bold=False):
        lbl = QLabel(metin)
        w   = QFont.Weight.Bold if bold else QFont.Weight.Normal
        lbl.setFont(QFont("Segoe UI", 11, w))
        lbl.setStyleSheet("color: white;" if bold else "color: #ccc;")
        return lbl