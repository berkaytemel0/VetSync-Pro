from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QSizePolicy, QProgressBar
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPainter, QColor, QBrush, QPalette, QPen
from PyQt6.QtCharts import QChart, QChartView, QPieSeries
from datetime import datetime
import calendar
import math

import database as db
from worker import Worker

PANEL_BG    = "#1A2942"
CARD_BG     = "#212D3A"
BEYAZ       = "#FFFFFF"
GRIS        = "#94A3B8"
GRIS_KOYU   = "#4A6080"
DANGER      = "#EF4444"
ACCENT_BLUE = "#4F46E5"
ACCENT_PURP = "#7C3AED"
TEAL        = "#30A7A1"
STAT_TEAL   = "#0D9488"
STAT_DARK   = "#2D3748"
STAT_BLUE   = "#4F46E5"
STAT_RED    = "#DC2626"
STAT_GREEN  = "#059669"
ACIK_BG     = "#F1F5F9"
HEAT_1      = "#1E4D8C"
HEAT_2      = "#0D7490"
HEAT_3      = "#0D9488"
HEAT_TODAY  = "#F59E0B"

MONTHS_TR = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran",
             "Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]

_CAL_CELL = 40
_CAL_GAP  = 4

def _dark_palette(widget, bg: str):
    p = widget.palette()
    p.setColor(QPalette.ColorRole.Window, QColor(bg))
    p.setColor(QPalette.ColorRole.Base,   QColor(bg))
    widget.setPalette(p)
    widget.setAutoFillBackground(True)

def _cal_last_row(year, month):
    first_wd, num_days = calendar.monthrange(year, month)
    return (first_wd + num_days - 1) // 7


# ── Yoğunluk Takvimi ─────────────────────────────────────────────────────
class _MiniHeatmapCalendar(QWidget):
    DAYS_TR = ["Pt", "Sa", "Ça", "Pe", "Cu", "Ct", "Pz"]

    def __init__(self, daily_counts: dict):
        super().__init__()
        self._counts  = daily_counts
        self._today   = datetime.now().date()
        self._year    = self._today.year
        self._month   = self._today.month
        self._hovered = None
        _dark_palette(self, CARD_BG)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    def _prev_month(self):
        if self._month == 1:
            self._month = 12
            self._year -= 1
        else:
            self._month -= 1
        self.updateGeometry()
        self.update()

    def _next_month(self):
        now = datetime.now()
        if self._year == now.year and self._month == now.month:
            return
        if self._month == 12:
            self._month = 1
            self._year += 1
        else:
            self._month += 1
        self.updateGeometry()
        self.update()

    def _x0(self):
        W = self.width()
        return max(8, (W - (7 * _CAL_CELL + 6 * _CAL_GAP)) // 2)

    def _header_h(self):  return 30
    def _dayname_h(self): return 20
    def _cell_top(self):  return self._header_h() + self._dayname_h() + 6

    def _total_h(self):
        lr = _cal_last_row(self._year, self._month)
        return self._cell_top() + (lr + 1) * (_CAL_CELL + _CAL_GAP) + 34

    def _date_grid(self):
        first_wd, num_days = calendar.monthrange(self._year, self._month)
        grid = []
        for day in range(1, num_days + 1):
            d   = datetime(self._year, self._month, day).date()
            col = d.weekday()
            row = (first_wd + day - 1) // 7
            grid.append((row, col, d))
        return grid

    def _cell_center(self, row, col):
        x0 = self._x0()
        cx = x0 + col * (_CAL_CELL + _CAL_GAP) + _CAL_CELL // 2
        cy = self._cell_top() + row * (_CAL_CELL + _CAL_GAP) + _CAL_CELL // 2
        return cx, cy

    def mousePressEvent(self, event):
        x = event.pos().x()
        W = self.width()
        if x < 32:
            self._prev_month()
        elif x > W - 32:
            self._next_month()

    def mouseMoveEvent(self, event):
        mx, my = event.pos().x(), event.pos().y()
        hit = None
        s   = _CAL_CELL - 2
        for row, col, d in self._date_grid():
            cx, cy = self._cell_center(row, col)
            rx, ry = cx - s // 2, cy - s // 2
            if rx <= mx <= rx + s and ry <= my <= ry + s:
                hit = d.strftime("%Y-%m-%d")
                break
        if hit != self._hovered:
            self._hovered = hit
            self.update()

    def leaveEvent(self, event):
        self._hovered = None
        self.update()

    def sizeHint(self):
        return QSize(max(self.width(), 300), self._total_h())

    def minimumSizeHint(self):
        return QSize(280, self._total_h())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(CARD_BG))

        W   = self.width()
        now = datetime.now()

        painter.setPen(QColor(BEYAZ))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.drawText(0, 3, W, 26,
                         Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                         f"{MONTHS_TR[self._month - 1]}  {self._year}")

        for bx, lbl, aktif in [
            (16, "‹", True),
            (W - 16, "›", not (self._year == now.year and self._month == now.month))
        ]:
            if aktif:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor("#2A3A55")))
                painter.drawEllipse(bx - 10, 6, 20, 20)
                painter.setPen(QColor(BEYAZ))
            else:
                painter.setPen(QColor(GRIS_KOYU))
            painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            painter.drawText(bx - 10, 6, 20, 20, Qt.AlignmentFlag.AlignCenter, lbl)

        x0 = self._x0()
        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(QColor(GRIS))
        for col, name in enumerate(self.DAYS_TR):
            cx = x0 + col * (_CAL_CELL + _CAL_GAP) + _CAL_CELL // 2
            painter.drawText(cx - _CAL_CELL // 2, self._header_h(),
                             _CAL_CELL, self._dayname_h(),
                             Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                             name)

        s = _CAL_CELL - 2
        for row, col, d in self._date_grid():
            key        = d.strftime("%Y-%m-%d")
            count      = self._counts.get(key, 0)
            cx, cy     = self._cell_center(row, col)
            is_today   = (d == self._today)
            is_hovered = (key == self._hovered)

            if   is_today:   fill = QColor(HEAT_TODAY)
            elif count == 0: fill = None
            elif count <= 2: fill = QColor(HEAT_1)
            elif count <= 4: fill = QColor(HEAT_2)
            else:            fill = QColor(HEAT_3)

            if fill and is_hovered and not is_today:
                fill = fill.lighter(135)

            rx = cx - s // 2
            ry = cy - s // 2

            painter.setPen(Qt.PenStyle.NoPen)
            if fill:
                painter.setBrush(QBrush(fill))
                painter.drawRoundedRect(rx, ry, s, s, 5, 5)
            elif is_hovered:
                painter.setPen(QPen(QColor(GRIS_KOYU), 1))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(rx, ry, s, s, 5, 5)
                painter.setPen(Qt.PenStyle.NoPen)

            painter.setPen(QColor(BEYAZ) if (fill or is_today) else QColor(GRIS))
            painter.setFont(QFont("Segoe UI", 8,
                                  QFont.Weight.Bold if is_today else QFont.Weight.Normal))
            painter.drawText(rx, ry, s, s, Qt.AlignmentFlag.AlignCenter, str(d.day))

            if is_hovered and count > 0:
                tip = f"{d.strftime('%d/%m/%Y')} • {count} randevu"
                painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
                fm      = painter.fontMetrics()
                tw, th  = fm.horizontalAdvance(tip) + 16, 22
                tx      = max(4, min(cx - tw // 2, W - tw - 4))
                ty      = max(4, cy - s // 2 - th - 4)
                painter.setBrush(QBrush(QColor("#2C4A7C")))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(tx, ty, tw, th, 5, 5)
                painter.setPen(QColor(BEYAZ))
                painter.drawText(tx, ty, tw, th, Qt.AlignmentFlag.AlignCenter, tip)

        lr = _cal_last_row(self._year, self._month)
        ly = self._cell_top() + (lr + 1) * (_CAL_CELL + _CAL_GAP) + 8
        lx = (W - 3 * 120) // 2
        for color, label in [(HEAT_1, "1-2"), (HEAT_2, "3-4"), (HEAT_3, "5+")]:
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(lx, ly + 3, 18, 18, 4, 4)
            painter.setPen(QColor(GRIS))
            painter.setFont(QFont("Segoe UI", 11))
            painter.drawText(lx + 26, ly, 80, 20,
                             Qt.AlignmentFlag.AlignVCenter, label)
            lx += 120

        painter.end()


class HeatmapWidget(QFrame):
    def __init__(self, daily_counts: dict):
        super().__init__()
        _dark_palette(self, CARD_BG)
        self.setStyleSheet("QFrame { border-radius: 14px; border: none; }")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 14)
        layout.setSpacing(6)

        t = QLabel("Yoğunluk Takvimi")
        t.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {BEYAZ}; background: transparent; border: none;")
        layout.addWidget(t)

        sub = QLabel("Renk = randevu yoğunluğu  •  ‹ › ile ay gezilebilir")
        sub.setFont(QFont("Segoe UI", 8))
        sub.setStyleSheet(f"color: {GRIS}; background: transparent; border: none;")
        layout.addWidget(sub)

        self._cal = _MiniHeatmapCalendar(daily_counts)
        layout.addWidget(self._cal, 1)




# ── Durum Dağılımı ────────────────────────────────────────────────────────────
class StatusDistributionWidget(QFrame):
    def __init__(self, status_data: dict):
        super().__init__()
        _dark_palette(self, CARD_BG)
        self.setStyleSheet("QFrame { border-radius: 14px; border: none; }")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        t = QLabel("Durum Dağılımı")
        t.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {BEYAZ}; background: transparent; border: none;")
        layout.addWidget(t)

        pending   = status_data.get("pending",   0)
        completed = status_data.get("completed", 0)
        cancelled = status_data.get("cancelled", 0)
        missed    = status_data.get("missed",    0)
        total     = pending + completed + cancelled + missed or 1

        items = [
            ("⏳", "Bekliyor",          pending,   "#F59E0B", "#2A2010"),
            ("✅", "Tamamlandı",        completed, "#10B981", "#0A2A1A"),
            ("✖",  "İptal Edildi",      cancelled, "#EF4444", "#2A0A0A"),
            ("⚠️", "İşlem Yapılamamış", missed,    "#8B5CF6", "#1A0A2A"),
        ]
        for icon_txt, label, count, bar_color, row_bg in items:
            row_frame = QFrame()
            row_frame.setStyleSheet(
                f"QFrame {{ background-color: {row_bg}; border-radius: 10px; border: none; }}"
            )
            row_layout = QVBoxLayout(row_frame)
            row_layout.setContentsMargins(14, 10, 14, 10)
            row_layout.setSpacing(6)

            top = QHBoxLayout()
            ic = QLabel(icon_txt)
            ic.setFont(QFont("Segoe UI", 13))
            ic.setStyleSheet("background: transparent; border: none;")
            ic.setFixedWidth(24)

            lbl = QLabel(label)
            lbl.setFont(QFont("Segoe UI", 11))
            lbl.setStyleSheet(f"color: {BEYAZ}; background: transparent; border: none;")

            cnt = QLabel(str(count))
            cnt.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            cnt.setStyleSheet(f"color: {BEYAZ}; background: transparent; border: none;")
            cnt.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            top.addWidget(ic)
            top.addWidget(lbl)
            top.addStretch()
            top.addWidget(cnt)
            row_layout.addLayout(top)

            bar = QProgressBar()
            bar.setMinimum(0)
            bar.setMaximum(total)
            bar.setValue(count)
            bar.setTextVisible(False)
            bar.setFixedHeight(6)
            bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: rgba(255,255,255,0.08);
                    border-radius: 3px;
                    border: none;
                }}
                QProgressBar::chunk {{
                    background-color: {bar_color};
                    border-radius: 3px;
                }}
            """)
            row_layout.addWidget(bar)
            layout.addWidget(row_frame)

        layout.addStretch()


# ── Bar Aylık ─────────────────────────────────────────────────────────
class _RoundedBarCanvas(QWidget):
    def __init__(self, data_items):
        super().__init__()
        self._data    = data_items
        self._hovered = -1
        _dark_palette(self, CARD_BG)
        self.setMouseTracking(True)

    @staticmethod
    def _fmt(raw):
        s = str(raw).strip()
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y-%m"):
            try:
                dt = datetime.strptime(s, fmt)
                k  = dt.strftime("%d/%m/%Y") if "%d" in fmt else dt.strftime("%m/%Y")
                t  = dt.strftime("%d/%m/%Y  %H:%M") if ("T" in fmt or " " in fmt) else k
                return k, t
            except ValueError:
                pass
        return s, s

    def _geo(self):
        W, H = self.width(), self.height()
        pl, pr, pt, pb = 40, 20, 16, 36
        cw = W - pl - pr
        ch = H - pt - pb
        n  = len(self._data)
        mv = max(v for _, v in self._data) or 1
        gw = cw / max(n, 1)
        bw = max(8, min(28, int(gw * 0.35)))
        return bw, gw, pl, pt, pb, cw, ch, mv

    def _rects(self):
        bw, gw, pl, pt, pb, cw, ch, mv = self._geo()
        out = []
        for i, (label, value) in enumerate(self._data):
            cx = pl + int(gw * (i + 0.5))
            h  = max(int(ch * value / mv), bw)
            k, t = self._fmt(label)
            out.append((cx - bw // 2, pt + ch - h, bw, h, k, t, value, cx))
        return out

    def mouseMoveEvent(self, event):
        mx  = event.pos().x()
        hit = -1
        for i, (rx, ry, rw, rh, *_) in enumerate(self._rects()):
            if rx - 8 <= mx <= rx + rw + 8:
                hit = i
                break
        if hit != self._hovered:
            self._hovered = hit
            self.update()

    def leaveEvent(self, event):
        self._hovered = -1
        self.update()

    def paintEvent(self, event):
        if not self._data:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(CARD_BG))

        W, H = self.width(), self.height()
        pl, pr, pt, pb = 40, 20, 16, 36
        ch = H - pt - pb
        bw, gw, *_, mv = self._geo()

        for i in range(6):
            y = pt + ch - int(ch * i / 5)
            painter.setPen(QColor("#2A3A55"))
            painter.drawLine(pl, y, W - pr, y)
            painter.setPen(QColor(GRIS))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(0, y + 4, pl - 4, 12,
                             Qt.AlignmentFlag.AlignRight, str(int(mv * i / 5)))

        for i, (x, y, bw2, h, kisa, tam, value, cx) in enumerate(self._rects()):
            color = QColor("#7BA7F0") if i == self._hovered else QColor("#4F7BD4")
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawRoundedRect(x, y, bw2, h, bw2 // 2, bw2 // 2)

            painter.setPen(QColor(GRIS))
            painter.setFont(QFont("Segoe UI", 7))
            lw = int(gw * 0.9)
            painter.drawText(cx - lw // 2, H - pb + 6, lw, 20,
                             Qt.AlignmentFlag.AlignHCenter, kisa)

            if i == self._hovered:
                line2 = f"Randevu: {value}"
                painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
                fm  = painter.fontMetrics()
                tw  = max(fm.horizontalAdvance(tam), fm.horizontalAdvance(line2)) + 18
                th  = 44
                tx  = max(pl, min(cx - tw // 2, W - pr - tw))
                ty  = max(4, y - th - 8)
                painter.setBrush(QBrush(QColor("#2C4A7C")))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(tx, ty, tw, th, 7, 7)
                painter.setPen(QColor("#A8C4F0"))
                painter.setFont(QFont("Segoe UI", 8))
                painter.drawText(tx, ty + 4, tw, 18, Qt.AlignmentFlag.AlignHCenter, tam)
                painter.setPen(QColor(BEYAZ))
                painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
                painter.drawText(tx, ty + 22, tw, 18, Qt.AlignmentFlag.AlignHCenter, line2)

        painter.end()


class BarChartWidget(QFrame):
    def __init__(self, title, data_items):
        super().__init__()
        _dark_palette(self, CARD_BG)
        self.setStyleSheet("QFrame { border-radius: 14px; border: none; }")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 16)

        t = QLabel(title)
        t.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {BEYAZ}; background: transparent; border: none;")
        layout.addWidget(t)

        if not data_items:
            e = QLabel("Veri bulunamadı.")
            e.setStyleSheet(f"color: {GRIS}; background: transparent; border: none;")
            e.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(e, 1)
            return

        c = _RoundedBarCanvas(data_items)
        c.setMinimumHeight(200)
        layout.addWidget(c, 1)



class _PieCanvas(QWidget):
    COLORS = [
        QColor(ACCENT_BLUE), QColor(TEAL),      QColor(ACCENT_PURP),
        QColor("#F59E0B"),   QColor(DANGER),     QColor("#06B6D4"),
        QColor("#F97316"),   QColor("#84CC16"),
    ]

    def __init__(self, data_items):
        super().__init__()
        self._data    = data_items
        self._hovered = -1
        _dark_palette(self, CARD_BG)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)

    def _build_slices(self):
        total = sum(v for _, v in self._data) or 1
        slices, cw = [], 0.0
        for i, (label, value) in enumerate(self._data):
            span = (value / total) * 360.0
            slices.append((label, value, cw, cw + span, span, i))
            cw += span
        return slices, total

    def _geometry(self):
        W, H   = self.width(), self.height()
        leg_h  = len(self._data) * 22 + 10
        pie_h  = H - leg_h
        cx, cy = W // 2, pie_h // 2
        R      = min(W // 2 - 20, pie_h // 2 - 10)
        return W, H, cx, cy, R, pie_h, leg_h

    def _hit(self, mx, my):
        import math
        W, H, cx, cy, R, pie_h, _ = self._geometry()
        dx, dy = mx - cx, my - cy
        if math.hypot(dx, dy) > R + 12:
            return -1
        cw_angle  = (90 - math.degrees(math.atan2(-dy, dx))) % 360
        slices, _ = self._build_slices()
        for _, _, cw_s, cw_e, _, i in slices:
            if cw_s <= cw_angle < cw_e:
                return i
        return -1

    def mouseMoveEvent(self, event):
        hit = self._hit(event.pos().x(), event.pos().y())
        if hit != self._hovered:
            self._hovered = hit
            self.update()

    def leaveEvent(self, event):
        self._hovered = -1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(CARD_BG))

        W, H, cx, cy, R, pie_h, leg_h = self._geometry()
        if R < 20:
            painter.end()
            return

        slices, total = self._build_slices()

        for label, value, cw_s, cw_e, span, i in slices:
            color      = self.COLORS[i % len(self.COLORS)]
            is_hovered = (i == self._hovered)
            expand     = 9 if is_hovered else 0
            draw_color = color.lighter(130) if is_hovered else color

            painter.setBrush(QBrush(draw_color))
            painter.setPen(QPen(QColor(CARD_BG), 2))
            painter.drawPie(
                cx - R - expand, cy - R - expand,
                (R + expand) * 2, (R + expand) * 2,
                int((90 - cw_s) * 16),
                int(-span * 16)
            )

        if self._hovered >= 0:
            label, value, *_, i = slices[self._hovered]
            pct  = round(value / total * 100, 1)
            tip1 = label
            tip2 = f"{value} adet  ·  %{int(pct)}"

            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            fm  = painter.fontMetrics()
            tw  = max(fm.horizontalAdvance(tip1), fm.horizontalAdvance(tip2)) + 22
            th  = 46
            tx  = max(4, min(cx - tw // 2, W - tw - 4))
            ty  = max(4, cy - R - th - 12)

            painter.setBrush(QBrush(QColor("#2C4A7C")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(tx, ty, tw, th, 7, 7)
            painter.setPen(QColor("#A8C4F0"))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(tx, ty + 5, tw, 18, Qt.AlignmentFlag.AlignHCenter, tip1)
            painter.setPen(QColor(BEYAZ))
            painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            painter.drawText(tx, ty + 23, tw, 18, Qt.AlignmentFlag.AlignHCenter, tip2)

        ly = pie_h + 8
        for label, value, *_, i in slices:
            color = self.COLORS[i % len(self.COLORS)]
            pct   = round(value / total * 100, 1)
            bold  = i == self._hovered

            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(16, ly + 4, 12, 12, 3, 3)
            painter.setPen(QColor(BEYAZ) if bold else QColor(GRIS))
            painter.setFont(QFont("Segoe UI", 9,
                                  QFont.Weight.Bold if bold else QFont.Weight.Normal))
            painter.drawText(32, ly, W - 40, 20, Qt.AlignmentFlag.AlignVCenter,
                             f"{label}  ({value}  ·  %{int(pct)})")
            ly += 22

        painter.end()


class PieChartWidget(QFrame):
    def __init__(self, title, data_items):
        super().__init__()
        _dark_palette(self, CARD_BG)
        self.setStyleSheet("QFrame { border-radius: 14px; border: none; }")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 16)

        t = QLabel(title)
        t.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {BEYAZ}; background: transparent; border: none;")
        layout.addWidget(t)

        if not data_items:
            e = QLabel("Veri bulunamadı.")
            e.setStyleSheet(f"color: {GRIS}; background: transparent; border: none;")
            e.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(e, 1)
            return

        canvas = _PieCanvas(data_items)
        canvas.setMinimumHeight(280)
        layout.addWidget(canvas, 1)


# ── Yatay Bar (İşlem Türleri) ─────────────────────────────────────
class _HorizontalBarCanvas(QWidget):
    BAR_COLORS = [
        "#00C9C8", "#F5E642", "#FF6B6B", "#00E5A0", "#A78BFA",
        "#F97316", "#06B6D4", "#84CC16", "#FB7185", "#34D399",
    ]

    _ROW_H = 56
    _BAR_H = 38
    _PAD_L = 140
    _PAD_R = 60
    _PAD_T = 12
    _PAD_B = 40

    def __init__(self, data_items):
        super().__init__()
        self._data    = sorted(data_items, key=lambda x: x[1], reverse=True)[:10]
        self._hovered = -1
        _dark_palette(self, CARD_BG)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    def sizeHint(self):
        h = self._PAD_T + len(self._data) * self._ROW_H + self._PAD_B + 8
        return QSize(400, max(h, 100))

    def minimumSizeHint(self):
        return self.sizeHint()

    def mouseMoveEvent(self, event):
        my = event.pos().y()
        hit = -1
        for i in range(len(self._data)):
            y0 = self._PAD_T + i * self._ROW_H
            if y0 <= my < y0 + self._ROW_H:
                hit = i
                break
        if hit != self._hovered:
            self._hovered = hit
            self.update()

    def leaveEvent(self, event):
        self._hovered = -1
        self.update()

    def paintEvent(self, event):
        if not self._data:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(CARD_BG))

        W       = self.width()
        max_val = max(max(v for _, v in self._data), 20) or 1
        avail   = W - self._PAD_L - self._PAD_R
        r       = self._BAR_H // 2

        chart_bottom = self._PAD_T + len(self._data) * self._ROW_H

        for tick in range(6):
            tx = self._PAD_L + int(avail * tick / 5)
            painter.setPen(QPen(QColor("#2A3A55"), 1, Qt.PenStyle.DashLine))
            painter.drawLine(tx, self._PAD_T, tx, chart_bottom)
            painter.setPen(QColor(GRIS_KOYU))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(tx - 18, chart_bottom + 6, 36, 16,
                             Qt.AlignmentFlag.AlignHCenter,
                             str(int(max_val * tick / 5)))

        for i, (label, value) in enumerate(self._data):
            bar_color  = QColor(self.BAR_COLORS[i % len(self.BAR_COLORS)])
            is_hovered = (i == self._hovered)
            by         = self._PAD_T + i * self._ROW_H + (self._ROW_H - self._BAR_H) // 2
            filled_w   = max(int(avail * value / max_val), self._BAR_H)

            painter.setBrush(QBrush(QColor("#18243A")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(self._PAD_L, by, avail, self._BAR_H, r, r)

            draw_color = bar_color.lighter(115) if is_hovered else bar_color
            painter.setBrush(QBrush(draw_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(self._PAD_L, by, filled_w, self._BAR_H, r, r)

            painter.setPen(QColor(BEYAZ) if is_hovered else QColor(GRIS))
            painter.setFont(QFont("Segoe UI", 9,
                                  QFont.Weight.Bold if is_hovered else QFont.Weight.Normal))
            fm     = painter.fontMetrics()
            elided = fm.elidedText(label, Qt.TextElideMode.ElideRight, self._PAD_L - 10)
            painter.drawText(4, by, self._PAD_L - 10, self._BAR_H,
                             Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                             elided)

            vx = self._PAD_L + avail + 8
            painter.setPen(QColor(BEYAZ) if is_hovered else QColor(GRIS))
            painter.setFont(QFont("Segoe UI", 9,
                                  QFont.Weight.Bold if is_hovered else QFont.Weight.Normal))
            painter.drawText(vx, by, self._PAD_R - 8, self._BAR_H,
                             Qt.AlignmentFlag.AlignVCenter, str(value))

        painter.end()


class VaccineBarWidget(QFrame):
    def __init__(self, title, data_items):
        super().__init__()
        _dark_palette(self, CARD_BG)
        self.setStyleSheet("QFrame { border-radius: 14px; border: none; }")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 16)
        layout.setSpacing(8)

        header = QHBoxLayout()
        t = QLabel(title)
        t.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {BEYAZ}; background: transparent; border: none;")
        header.addWidget(t)
        header.addStretch()
        sub = QLabel(f"En çok kullanılan {min(len(data_items), 10)} işlem")
        sub.setFont(QFont("Segoe UI", 9))
        sub.setStyleSheet(f"color: {GRIS}; background: transparent; border: none;")
        header.addWidget(sub)
        layout.addLayout(header)

        if not data_items:
            e = QLabel("Veri bulunamadı.")
            e.setStyleSheet(f"color: {GRIS}; background: transparent; border: none;")
            e.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(e, 1)
            return

        canvas = _HorizontalBarCanvas(data_items)
        layout.addWidget(canvas)


# ── Müşteri Sadakati kısmı  ────────────────────────────────────────
class _LoyaltyCanvas(QWidget):
    def __init__(self, yeni: int, mevcut: int, kayip: int):
        super().__init__()
        self._yeni    = yeni
        self._mevcut  = mevcut
        self._kayip   = kayip
        self._hovered = None
        _dark_palette(self, CARD_BG)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)

    def _geometry(self):
        W, H     = self.width(), self.height()
        legend_h = 3 * 24 + 12
        donut_h  = H - legend_h
        cx       = W // 2
        cy       = donut_h // 2
        R        = min(W // 2 - 16, donut_h // 2 - 10)
        r        = R // 2
        return cx, cy, R, r, donut_h, W

    def _segments(self):
        total = (self._yeni + self._mevcut + self._kayip) or 1
        return [
            ("yeni",   self._yeni,   QColor(STAT_TEAL),   self._yeni   / total),
            ("mevcut", self._mevcut, QColor(ACCENT_BLUE), self._mevcut / total),
            ("kayip",  self._kayip,  QColor(STAT_RED),    self._kayip  / total),
        ]

    def _hit_segment(self, mx, my):
        import math
        cx, cy, R, r, *_ = self._geometry()
        dx, dy = mx - cx, my - cy
        dist   = math.hypot(dx, dy)
        if dist < r or dist > R:
            return None
        total = self._yeni + self._mevcut + self._kayip
        if total == 0:
            return None
        angle  = (90 - math.degrees(math.atan2(-dy, dx))) % 360
        cursor = 0.0
        for key, val, _, _ in self._segments():
            span = (val / total) * 360
            if cursor <= angle < cursor + span:
                return key
            cursor += span
        return None

    def mouseMoveEvent(self, event):
        hit = self._hit_segment(event.pos().x(), event.pos().y())
        if hit != self._hovered:
            self._hovered = hit
            self.update()

    def leaveEvent(self, event):
        self._hovered = None
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(CARD_BG))

        W, H  = self.width(), self.height()
        total = self._yeni + self._mevcut + self._kayip

        if total == 0:
            painter.setPen(QColor(GRIS))
            painter.setFont(QFont("Segoe UI", 11))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Henüz müşteri yok")
            painter.end()
            return

        legend_h = 3 * 24 + 12
        donut_h  = H - legend_h
        cx       = W // 2
        cy       = donut_h // 2
        R        = min(W // 2 - 16, donut_h // 2 - 10)
        r        = R // 2

        start_angle = 90 * 16
        for key, val, color, oran in self._segments():
            span   = int(oran * 360 * 16)
            expand = 6 if self._hovered == key else 0
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(color.lighter(120) if self._hovered == key else color))
            painter.drawPie(cx - R - expand, cy - R - expand,
                            (R + expand) * 2, (R + expand) * 2,
                            start_angle, -span)
            start_angle -= span

        painter.setBrush(QBrush(QColor(CARD_BG)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        painter.setPen(QColor(BEYAZ))
        painter.setFont(QFont("Segoe UI", max(10, R // 4), QFont.Weight.Bold))
        painter.drawText(cx - r, cy - r - 32, r * 2, r * 2 - 6,
                         Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom,
                         str(total))
        painter.setPen(QColor(GRIS))
        painter.setFont(QFont("Segoe UI", 8))
        painter.drawText(cx - r, cy + 2, r * 2, r,
                         Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, "Toplam")

        if self._hovered:
            labels = {
                "yeni":   ("Yeni Müşteri",   self._yeni,   self._yeni   / total),
                "mevcut": ("Mevcut Müşteri", self._mevcut, self._mevcut / total),
                "kayip":  ("Kayıp Müşteri",  self._kayip,  self._kayip  / total),
            }
            tip1, val, oran = labels[self._hovered]
            tip2 = f"{val}  ·  %{int(oran * 100)}"

            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            fm  = painter.fontMetrics()
            tw  = max(fm.horizontalAdvance(tip1), fm.horizontalAdvance(tip2)) + 20
            th  = 44
            tx  = max(4, min(cx - tw // 2, W - tw - 4))
            ty  = max(4, cy - R - th - 10)
            painter.setBrush(QBrush(QColor("#2C4A7C")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(tx, ty, tw, th, 7, 7)
            painter.setPen(QColor("#A8C4F0"))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(tx, ty + 4, tw, 18, Qt.AlignmentFlag.AlignHCenter, tip1)
            painter.setPen(QColor(BEYAZ))
            painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            painter.drawText(tx, ty + 22, tw, 18, Qt.AlignmentFlag.AlignHCenter, tip2)

        legend_labels = {"yeni": "Yeni", "mevcut": "Mevcut", "kayip": "Kayıp"}
        legend_y = donut_h + 8
        for key, val, color, oran in self._segments():
            bold = key == self._hovered
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(16, legend_y + 4, 12, 12, 3, 3)
            painter.setPen(QColor(GRIS))
            painter.setFont(QFont("Segoe UI", 9))
            painter.drawText(32, legend_y, 80, 20, Qt.AlignmentFlag.AlignVCenter,
                             legend_labels[key])
            painter.setPen(QColor(BEYAZ) if bold else QColor(GRIS))
            painter.setFont(QFont("Segoe UI", 9,
                                  QFont.Weight.Bold if bold else QFont.Weight.Normal))
            painter.drawText(112, legend_y, W - 120, 20, Qt.AlignmentFlag.AlignVCenter,
                             f"{val}  ({int(oran * 100)}%)")
            legend_y += 24

        painter.end()


class LoyaltyWidget(QFrame):
    def __init__(self, yeni: int, mevcut: int, kayip: int = 0):
        super().__init__()
        _dark_palette(self, CARD_BG)
        self.setStyleSheet("QFrame { border-radius: 14px; border: none; }")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 16)
        layout.setSpacing(8)

        t = QLabel("Müşteri Sadakati & Büyüme")
        t.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {BEYAZ}; background: transparent; border: none;")
        layout.addWidget(t)

        sub = QLabel("Yeni: 1 randevu  •  Mevcut: 2+ randevu  •  Kayıp: 90+ gün sessiz")
        sub.setFont(QFont("Segoe UI", 8))
        sub.setStyleSheet(f"color: {GRIS}; background: transparent; border: none;")
        layout.addWidget(sub)

        canvas = _LoyaltyCanvas(yeni, mevcut, kayip)
        canvas.setMinimumHeight(280)
        layout.addWidget(canvas, 1)


# ── Ana Widget ────────────────────────────────────────────────────────────────
class AnalyticsWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        _dark_palette(self, ACIK_BG)
        self.setStyleSheet(f"QWidget {{ background-color: {ACIK_BG}; }}")
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        self._outer = QVBoxLayout(self)
        self._outer.setContentsMargins(30, 30, 30, 30)
        self._outer.setSpacing(20)

        title = QLabel("Analizler & Raporlama")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #0F172A; background: transparent;")
        self._outer.addWidget(title)

        self._loading_lbl = QLabel("⏳ Veriler yükleniyor...")
        self._loading_lbl.setFont(QFont("Segoe UI", 13))
        self._loading_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._loading_lbl.setStyleSheet("color: #64748B; background: transparent;")
        self._outer.addWidget(self._loading_lbl, 1)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.hide()
        self._outer.addWidget(self._scroll, 1)

        self._err_lbl = QLabel("")
        self._err_lbl.setFont(QFont("Segoe UI", 13))
        self._err_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._err_lbl.setStyleSheet(f"color: {DANGER}; background: transparent;")
        self._err_lbl.hide()
        self._outer.addWidget(self._err_lbl)

    def _load_data(self):
        uid = self.user["id"]
        rol = self.user.get("role", "")

        def _fetch():
            if rol == "Klinik Sahibi":
                monthly   = db.get_klinik_monthly_appointments(uid)
                species   = db.get_klinik_species_distribution(uid)
                vacc      = db.get_klinik_vaccine_type_distribution(uid)
                status    = db.get_klinik_status_distribution(uid)
                total_c   = db.get_klinik_customer_count(uid)
                lost_c    = db.get_klinik_lost_customers(uid)
                daily     = db.get_klinik_daily_appointments(uid)
                loyalty   = db.get_klinik_new_vs_returning_customers(uid)
                completed = db.get_klinik_completed_appointments_count(uid)
            else:
                monthly   = db.get_monthly_appointments(uid)
                species   = db.get_species_distribution(uid)
                vacc      = db.get_vaccine_type_distribution(uid)
                status    = db.get_status_distribution(uid)
                total_c   = db.get_customer_count(uid)
                lost_c    = db.get_lost_customers(uid)
                daily     = db.get_daily_appointments(uid)
                loyalty   = db.get_new_vs_returning_customers(uid)
                completed = db.get_completed_appointments_count(uid)
            return {
                "monthly":   monthly,
                "species":   species,
                "vacc":      vacc,
                "status":    status,
                "total_c":   total_c,
                "lost_c":    lost_c,
                "completed": completed,
                "daily":     daily,
                "loyalty":   loyalty,
            }

        def _done(data):
            self._loading_lbl.hide()
            self._build_content(data)
            self._scroll.show()

        def _err(e):
            self._loading_lbl.hide()
            self._err_lbl.setText(f"❌ Veri yüklenemedi: {e}")
            self._err_lbl.show()

        self._worker = Worker(_fetch)
        self._worker.result.connect(_done)
        self._worker.error.connect(_err)
        self._worker.start()
   

    def _build_content(self, data):
        container = QWidget()
        _dark_palette(container, ACIK_BG)
        cv = QVBoxLayout(container)
        cv.setContentsMargins(0, 0, 0, 0)
        cv.setSpacing(20)

        # ── Özet kartlar ──────────────────────────────────────────────────
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)
        for label, val, color, alt in [
            ("Toplam Müşteri",      data["total_c"],   STAT_TEAL,  "Kayıtlı tüm müşteriler"),
            ("Kayıp Müşteriler",    data["lost_c"],    STAT_RED,   "Son 90 günde randevusuz"),
            ("Tamamlanan İşlemler", data["completed"], STAT_GREEN, "Durum: tamamlandı"),
        ]:
            card = QFrame()
            card.setStyleSheet(
                f"QFrame {{ background-color: {color}; border-radius: 12px; border: none; }}"
            )
            card.setMinimumHeight(110)
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 12, 16, 12)
            cl.setSpacing(2)
            lb = QLabel(label)
            lb.setFont(QFont("Segoe UI", 10))
            lb.setWordWrap(True)
            lb.setStyleSheet("color: rgba(255,255,255,0.85); background: transparent;")
            vl = QLabel(str(val))
            vl.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
            vl.setStyleSheet("color: white; background: transparent;")
            al = QLabel(alt)
            al.setFont(QFont("Segoe UI", 8))
            al.setStyleSheet("color: rgba(255,255,255,0.60); background: transparent;")
            cl.addWidget(lb)
            cl.addWidget(vl)
            cl.addWidget(al)
            stats_row.addWidget(card, 1)
        cv.addLayout(stats_row)

        
        dark_section = QFrame()
        _dark_palette(dark_section, PANEL_BG)
        dark_section.setStyleSheet(
            f"QFrame {{ background-color: {PANEL_BG}; border-radius: 16px; border: none; }}"
        )
        ds = QVBoxLayout(dark_section)
        ds.setContentsMargins(16, 16, 16, 16)
        ds.setSpacing(16)

        #Yoğunluk Takvimi + Durum Dağılımı
        row1 = QHBoxLayout()
        row1.setSpacing(16)
        row1.setAlignment(Qt.AlignmentFlag.AlignTop)
        heatmap = HeatmapWidget({r["date"]: r["count"] for r in data["daily"]})
        row1.addWidget(heatmap, 1, Qt.AlignmentFlag.AlignTop)
        status_widget = StatusDistributionWidget(data["status"])
        status_widget.setFixedHeight(320)
        row1.addWidget(status_widget, 1)
        ds.addLayout(row1)

        # Tür Dağılımı + Müşteri Sadakati
        row2 = QHBoxLayout()
        row2.setSpacing(16)
        pie_species = PieChartWidget(
            "Tür Dağılımı",
            [(r["species"] or "Bilinmiyor", r["count"]) for r in data["species"]]
        )
        pie_species.setMinimumHeight(300)
        row2.addWidget(pie_species, 1)
        loyalty = LoyaltyWidget(
            data["loyalty"].get("yeni", 0),
            data["loyalty"].get("mevcut", 0),
            data["lost_c"],
        )
        
        loyalty.setMinimumHeight(320)
        row2.addWidget(loyalty, 1)
        ds.addLayout(row2)

        # İşlem Türleri — yatay bar  
        vacc_data = sorted(
            [(r["appointment_type"] or "Diğer", r["count"]) for r in data["vacc"]],
            key=lambda x: x[1], reverse=True
        )
        vacc_bar = VaccineBarWidget("İşlem Türleri Dağılımı", vacc_data)
        ds.addWidget(vacc_bar)

        # Aylık Randevu Bar 
        bar = BarChartWidget(
            "Aylık Randevu Sayısı",
            [(r["month"], r["count"]) for r in data["monthly"]]
        )
        bar.setMinimumHeight(260)
        ds.addWidget(bar)

        cv.addWidget(dark_section)
        cv.addStretch()
        self._scroll.setWidget(container)