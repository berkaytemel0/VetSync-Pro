# ── PALETTE ───────────────────────────────────────────────────────────────────
PRIMARY      = "#1A2942"
PRIMARY_MID  = "#1F3357"
PRIMARY_LITE = "#243C6A"
ACCENT_PURP  = "#7C3AED"
ACCENT_TEAL  = "#0D9488"
ACCENT_BLUE  = "#4F46E5"
CARD_DARK    = "#2D3748"

WHITE        = "#FFFFFF"
BG_PAGE      = "#F8FAFC"
BG_INPUT     = "#EFF3F8"
BORDER       = "#D9E2EE"

TEXT_HEAD    = "#0F172A"
TEXT_BODY    = "#334155"
TEXT_MUTED   = "#94A3B8"
TEXT_LIGHT   = "#F1F5F9"

SUCCESS      = "#10B981"
WARNING      = "#F59E0B"
DANGER       = "#EF4444"

# ── GLOBAL APP STYLE ──────────────────────────────────────────────────────────
APP_STYLE = f"""
* {{
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
}}
QScrollBar:vertical {{
    background: {BG_PAGE};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    height: 0;
}}
QToolTip {{
    background-color: {TEXT_HEAD};
    color: {WHITE};
    border: none;
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 12px;
}}
"""

# ── LOGIN / REGISTER ──────────────────────────────────────────────────────────
AUTH_PANEL_LEFT = f"""
QWidget#left_panel {{
    background-color: {PRIMARY};
}}
"""

AUTH_PANEL_RIGHT = f"""
QWidget#right_panel {{
    background-color: {WHITE};
}}
"""

FIELD_LABEL = f"""
QLabel {{
    color: {TEXT_BODY};
    font-size: 13px;
    font-weight: 600;
}}
"""

LINE_EDIT = f"""
QLineEdit {{
    background-color: {BG_INPUT};
    border: 1.5px solid {BORDER};
    border-radius: 10px;
    padding: 11px 16px;
    font-size: 14px;
    color: {TEXT_HEAD};
}}
QLineEdit:focus {{
    border: 1.5px solid {ACCENT_PURP};
    background-color: {WHITE};
}}
QLineEdit::placeholder {{
    color: {TEXT_MUTED};
}}
"""

PRIMARY_BTN = f"""
QPushButton {{
    background-color: {PRIMARY};
    color: {WHITE};
    border: none;
    border-radius: 10px;
    padding: 13px;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1.2px;
}}
QPushButton:hover {{
    background-color: {PRIMARY_MID};
}}
QPushButton:pressed {{
    background-color: {PRIMARY_LITE};
}}
"""

OUTLINE_BTN = f"""
QPushButton {{
    background-color: transparent;
    color: {TEXT_HEAD};
    border: 2px solid {TEXT_HEAD};
    border-radius: 8px;
    padding: 7px 18px;
    font-size: 13px;
    font-weight: 700;
}}
QPushButton:hover {{
    background-color: {BG_INPUT};
}}
"""

LINK_BTN = f"""
QPushButton {{
    background-color: transparent;
    color: {TEXT_MUTED};
    border: none;
    font-size: 13px;
    text-decoration: underline;
    padding: 0;
}}
QPushButton:hover {{
    color: {ACCENT_PURP};
}}
"""

CHECKBOX_STYLE = f"""
QCheckBox {{
    color: {TEXT_BODY};
    font-size: 11px;
    font-family: 'Segoe UI';
    spacing: 6px;
}}
QCheckBox::indicator {{
    width: 13px;
    height: 13px;
    border-radius: 3px;
    border: 2px solid {BORDER};
    background: {WHITE};
}}
QCheckBox::indicator:hover {{
    border-color: {PRIMARY};
}}
QCheckBox::indicator:checked {{
    background-color: {PRIMARY};
    border-color: {PRIMARY};
    image: url(assets/check.png);
}}
"""

# ── TOPBAR ────────────────────────────────────────────────────────────────────
TOPBAR = f"""
QWidget#topbar {{
    background-color: {PRIMARY};
    border-bottom: 1px solid {PRIMARY_MID};
}}
QLabel#app_title {{
    color: {WHITE};
    font-size: 17px;
    font-weight: 800;
    letter-spacing: 0.5px;
}}
QPushButton#sms_btn {{
    background-color: {PRIMARY_MID};
    color: {WHITE};
    border: none;
    border-radius: 20px;
    padding: 7px 16px;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton#sms_btn:hover {{
    background-color: {PRIMARY_LITE};
}}
QPushButton#user_btn {{
    background-color: {PRIMARY_LITE};
    color: {WHITE};
    border: none;
    border-radius: 20px;
    padding: 7px 16px;
    font-size: 13px;
    font-weight: 600;
}}
QPushButton#user_btn:hover {{
    background-color: #2D4D8A;
}}
QPushButton#add_btn {{
    background-color: transparent;
    color: {WHITE};
    border: 1.5px solid rgba(255,255,255,0.5);
    border-radius: 8px;
    padding: 6px 16px;
    font-size: 13px;
}}
QPushButton#add_btn:hover {{
    background-color: {PRIMARY_MID};
    border-color: {WHITE};
}}
"""

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
SIDEBAR = f"""
QWidget#sidebar {{
    background-color: {PRIMARY};
    border-right: 1px solid {PRIMARY_MID};
}}
QPushButton#nav_btn {{
    background-color: transparent;
    color: #7A9CC0;
    text-align: left;
    padding: 11px 18px;
    border: none;
    font-size: 14px;
    font-weight: 500;
    border-radius: 10px;
    margin: 2px 8px;
}}
QPushButton#nav_btn:hover {{
    background-color: {PRIMARY_MID};
    color: {WHITE};
}}
QPushButton#nav_btn[active="true"] {{
    background-color: {PRIMARY_LITE};
    color: {WHITE};
    font-weight: 700;
}}
"""

# ── DASHBOARD CARDS ───────────────────────────────────────────────────────────
CARD_TEAL = f"""
QFrame {{
    background-color: {ACCENT_TEAL};
    border-radius: 14px;
    border: none;
}}
"""
CARD_DARK_STYLE = f"""
QFrame {{
    background-color: {CARD_DARK};
    border-radius: 14px;
    border: none;
}}
"""
CARD_BLUE = f"""
QFrame {{
    background-color: {ACCENT_BLUE};
    border-radius: 14px;
    border: none;
}}
"""

# ── TABS ──────────────────────────────────────────────────────────────────────
TAB_BAR = f"""
QTabWidget::pane {{
    border: none;
    background-color: {WHITE};
}}
QTabBar::tab {{
    background: {BG_INPUT};
    color: {TEXT_MUTED};
    padding: 10px 24px;
    border: none;
    font-size: 13px;
    font-weight: 600;
    border-radius: 8px;
    margin-right: 4px;
}}
QTabBar::tab:selected {{
    background: {PRIMARY};
    color: {WHITE};
}}
QTabBar::tab:hover:!selected {{
    background: {BORDER};
    color: {TEXT_BODY};
}}
"""

# ── APPOINTMENT / RECORD PANELS ───────────────────────────────────────────────
SEARCH_BTN = f"""
QPushButton {{
    background-color: {PRIMARY};
    color: {WHITE};
    border: none;
    border-radius: 10px;
    padding: 11px 20px;
    font-size: 13px;
    font-weight: 700;
}}
QPushButton:hover {{
    background-color: {PRIMARY_MID};
}}
"""

SEL_BTN = f"""
QPushButton {{
    background-color: {PRIMARY};
    color: {WHITE};
    border: none;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 700;
}}
QPushButton:hover {{
    background-color: {ACCENT_PURP};
}}
"""

CUSTOMER_CARD = f"""
QFrame {{
    background-color: #EEF5FF;
    border: 1.5px solid {BORDER};
    border-radius: 10px;
}}
QFrame:hover {{
    border-color: {ACCENT_BLUE};
    background-color: #E8F0FE;
}}
"""

SAVE_BTN = f"""
QPushButton {{
    background-color: {PRIMARY};
    color: {WHITE};
    border: none;
    border-radius: 10px;
    padding: 14px 40px;
    font-size: 14px;
    font-weight: 700;
}}
QPushButton:hover {{
    background-color: {PRIMARY_MID};
}}
"""

COMBO_STYLE = f"""
QComboBox {{
    background-color: {BG_INPUT};
    border: 1.5px solid {BORDER};
    border-radius: 10px;
    padding: 11px 16px;
    font-size: 14px;
    color: {TEXT_HEAD};
}}
QComboBox:focus {{
    border-color: {ACCENT_PURP};
}}
QComboBox::drop-down {{
    border: none;
    padding-right: 10px;
}}
QComboBox QAbstractItemView {{
    background-color: {WHITE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    selection-background-color: {BG_INPUT};
    color: {TEXT_HEAD};
    padding: 4px;
}}
"""

DATE_EDIT_STYLE = f"""
QDateEdit {{
    background-color: {BG_INPUT};
    border: 1.5px solid {BORDER};
    border-radius: 10px;
    padding: 11px 16px;
    font-size: 14px;
    color: {TEXT_HEAD};
}}
QDateEdit:focus {{
    border-color: {ACCENT_PURP};
}}
QDateEdit::drop-down {{
    border: none;
    padding-right: 10px;
}}
"""

# ── SMS WINDOW ────────────────────────────────────────────────────────────────
SMS_LOG_CARD = f"""
QFrame {{
    background-color: #F0FAF7;
    border: 1px solid #C6EDE6;
    border-radius: 10px;
}}
"""

SMS_WINDOW = f"""
QDialog {{
    background-color: {WHITE};
}}
"""