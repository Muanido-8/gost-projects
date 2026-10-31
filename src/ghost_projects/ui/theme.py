# Theme Constants
BG_PAGE = "#0B0D12"
BG_SIDEBAR = "#10131A"
BG_CARD = "#161A23"
BG_CARD_HOV = "#1C2130"
BG_CHIP = "#1A1F2B"

TEXT_PRIMARY = "#E6E9F0"
TEXT_SECONDARY = "#A3ABBD"
TEXT_MUTED = "#6B7385"

PRIMARY = "#2DD4BF"   # Teal
WARNING = "#F5B342"
DANGER = "#F0616D"
INFO = "#7C8CFF"

BADGE_DANGER_BG = "#3A1D22"
BADGE_WARNING_BG = "#3A2E14"
BADGE_PRIMARY_BG = "#14332F"

def get_stylesheet():
    return f"""
    QWidget {{
        background-color: {BG_PAGE};
        color: {TEXT_PRIMARY};
        font-family: 'Segoe UI', 'Inter', sans-serif;
    }}

    QScrollArea {{
        border: none;
        background-color: transparent;
    }}

    QScrollBar:vertical {{
        border: none;
        background: transparent;
        width: 8px;
        margin: 0px;
    }}

    QScrollBar::handle:vertical {{
        background: {BG_CHIP};
        min-height: 20px;
        border-radius: 4px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {TEXT_MUTED};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QPushButton {{
        border: none;
        border-radius: 8px;
        font-weight: 500;
    }}

    QLabel {{
        border: none;
        background: transparent;
    }}
    """