"""
ui/shared_widgets.py
Ortak yeniden kullanılabilir input widget'ları.
"""
from PyQt6.QtWidgets import QLineEdit

_INPUT_BG   = "#1E2A3B"
_INPUT_BORD = "#2A3A55"
_TEAL       = "#30A7A1"
_BEYAZ      = "#FFFFFF"
_GRIS       = "#94A3B8"

_STYLE = f"""
QLineEdit {{
    background-color: {_INPUT_BG};
    border: 1.5px solid {_INPUT_BORD};
    border-radius: 10px;
    padding: 0 16px;
    color: {_BEYAZ};
    font-size: 13px;
    font-family: 'Segoe UI';
}}
QLineEdit:focus {{ border-color: {_TEAL}; }}
QLineEdit::placeholder {{ color: {_GRIS}; }}
"""


class TelefonInput(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("(5XX) XXX XX XX")
        self.setFixedHeight(48)
        self.setStyleSheet(_STYLE)
        self.setMaxLength(15)
        self._busy = False
        self.textChanged.connect(self._formatla)

    def _formatla(self, text):
        if self._busy:
            return
        self._busy = True
        r = "".join(c for c in text if c.isdigit())[:10]
        s = ""
        if r:           s = "(" + r[:3]
        if len(r) >= 3: s += ") " + r[3:6]
        if len(r) >= 6: s += " " + r[6:8]
        if len(r) >= 8: s += " " + r[8:10]
        self.setText(s)
        self._busy = False

    def deger(self):
        return "".join(c for c in self.text() if c.isdigit())


class TarihInput(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("GG.AA.YYYY")
        self.setFixedHeight(48)
        self.setStyleSheet(_STYLE)
        self.setMaxLength(10)
        self._busy = False
        self.textChanged.connect(self._formatla)

    def _formatla(self, text):
        if self._busy:
            return
        self._busy = True
        r = "".join(c for c in text if c.isdigit())[:8]
        s = ""
        if r:           s = r[:2]
        if len(r) >= 3: s += "." + r[2:4]
        if len(r) >= 5: s += "." + r[4:8]
        self.setText(s)
        self._busy = False