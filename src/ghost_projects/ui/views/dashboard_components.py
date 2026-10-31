from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QDialog, QGridLayout, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal, Slot
from ghost_projects.schemas.assessment import ProjectAssessment
from ghost_projects.schemas.project import ProjectInfo
from ghost_projects.schemas.evidence import Evidence
from ghost_projects.schemas.finding import Clue, ResurrectionStep, Priority
from ghost_projects.ui import theme

def apply_elevation(widget):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(24)
    shadow.setXOffset(0)
    shadow.setYOffset(4)
    shadow.setColor(Qt.GlobalColor.black) # alpha handled by QSS or effect
    # For better alpha control in PySide6, we can use QColor(0,0,0,150)
    from PySide6.QtGui import QColor
    shadow.setColor(QColor(0, 0, 0, 150))
    widget.setGraphicsEffect(shadow)

class ProjectInfoHeader(QWidget):
    def __init__(self, project_info: ProjectInfo):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Project Name
        name_label = QLabel(project_info.name)
        name_label.setStyleSheet(f"""
            font-weight: 600; 
            font-size: 26px; 
            color: {theme.PRIMARY}; 
            font-family: 'Segoe UI Semibold', 'Inter', sans-serif;
        """)
        layout.addWidget(name_label)

        # Metadata Chips
        self.add_chip(layout, f"{project_info.root_path}")
        if project_info.has_git:
            self.add_chip(layout, "Git repository")
        
        for lang in project_info.detected_languages:
            self.add_chip(layout, lang)
        
        for tech in project_info.detected_technologies:
            self.add_chip(layout, tech)

    def add_chip(self, layout, text):
        chip = QLabel(text)
        chip.setStyleSheet(f"""
            background-color: {theme.BG_CHIP};
            color: {theme.TEXT_SECONDARY};
            border-radius: 12px;
            padding: 4px 12px;
            font-size: 12px;
            font-family: 'JetBrains Mono', 'Cascadia Code', monospace;
        """)
        layout.addWidget(chip)

class InvestigationStats(QWidget):
    def __init__(self, assessment: ProjectAssessment):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        stats = [
            ("EVIDENCES", len(assessment.evidence), theme.PRIMARY),
            ("CLUES FOUND", len(assessment.clues), theme.WARNING),
            ("LIMITATIONS", len(assessment.unknowns), theme.DANGER),
            ("RESURRECTION PLAN", len(assessment.resurrection_plan), theme.INFO),
        ]

        for label, value, color in stats:
            card = self.create_stat_card(label, value, color)
            layout.addWidget(card)

    def create_stat_card(self, label, value, color):
        card = QFrame()
        card.setMinimumSize(180, 80)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.BG_CARD};
                border: none;
            }}
        """)
        apply_elevation(card)
        
        # Top color strip
        strip = QFrame(card)
        strip.setFixedSize(card.width(), 3)
        strip.setStyleSheet(f"background-color: {color}; border-radius: 12px 12px 0 0;")
        # We'll position this manually or use a layout
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)
        
        lbl = QLabel(label)
        lbl.setStyleSheet(f"border: none; color: {theme.TEXT_MUTED}; font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        val = QLabel(str(value))
        val.setStyleSheet(f"border: none; color: {color}; font-size: 28px; font-weight: 600;")
        val.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        layout.addWidget(lbl)
        layout.addWidget(val)
        
        # To make the strip work with layout, we can't easily. 
        # Let's use a custom paintEvent or just a small frame at the top.
        # Actually, a simpler way is to use a border-top in QSS.
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.BG_CARD};
                border-top: 3px solid {color};
            }}
        """)
        
        return card

class EvidenceDetailDialog(QDialog):
    def __init__(self, evidence: Evidence, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Evidence Detail - {evidence.id}")
        self.setMinimumSize(500, 400)
        self.setStyleSheet(f"background-color: {theme.BG_PAGE}; color: {theme.TEXT_PRIMARY};")
        
        layout = QVBoxLayout(self)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel(f"Evidence: {evidence.id}")
        title.setStyleSheet(f"font-size: 20px; font-weight: 600; color: {theme.PRIMARY};")
        content_layout.addWidget(title)
        
        # Source Path
        path_label = QLabel(f"Source: {evidence.source_path}")
        path_label.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-family: 'JetBrains Mono', monospace; font-size: 13px;")
        path_label.setWordWrap(True)
        content_layout.addWidget(path_label)
        
        # Description
        desc_label = QLabel("Description")
        desc_label.setStyleSheet(f"font-weight: 600; color: {theme.TEXT_MUTED}; font-size: 12px; text-transform: uppercase;")
        content_layout.addWidget(desc_label)
        
        desc_text = QLabel(evidence.description)
        desc_text.setWordWrap(True)
        desc_text.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 14px; line-height: 1.6;")
        content_layout.addWidget(desc_text)
        
        # Excerpt
        if evidence.excerpt:
            excerpt_label = QLabel("Excerpt")
            excerpt_label.setStyleSheet(f"font-weight: 600; color: {theme.TEXT_MUTED}; font-size: 12px; text-transform: uppercase;")
            content_layout.addWidget(excerpt_label)
            
            excerpt_box = QFrame()
            excerpt_box.setStyleSheet(f"background-color: {theme.BG_CARD}; border-radius: 8px; padding: 15px;")
            excerpt_layout = QVBoxLayout(excerpt_box)
            
            excerpt_text = QLabel(evidence.excerpt)
            excerpt_text.setWordWrap(True)
            excerpt_text.setStyleSheet(f"font-family: 'JetBrains Mono', monospace; color: {theme.TEXT_SECONDARY}; font-size: 13px;")
            excerpt_layout.addWidget(excerpt_text)
            content_layout.addWidget(excerpt_box)
            
        if evidence.line_start:
            lines = QLabel(f"Lines: {evidence.line_start} - {evidence.line_end or 'End'}")
            lines.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 11px;")
            content_layout.addWidget(lines)

        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        close_btn = QPushButton("CLOSE")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet(f"padding: 10px; background-color: {theme.BG_CARD}; color: white; border: 1px solid {theme.BG_CHIP};")
        layout.addWidget(close_btn)

class EvidenceSidebar(QWidget):
    evidence_selected = Signal(Evidence)

    def __init__(self, assessment: ProjectAssessment):
        super().__init__()
        self.assessment = assessment
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("EVIDENCE EXPLORER")
        title.setStyleSheet(f"font-weight: bold; color: {theme.TEXT_MUTED}; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin: 20px 10px;")
        layout.addWidget(title)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("background-color: transparent;")
        
        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(10, 0, 10, 0)
        self.list_layout.setSpacing(4)
        
        for i, ev in enumerate(self.assessment.evidence, 1):
            btn = QPushButton(ev.id)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding: 10px 12px;
                    background-color: transparent;
                    color: {theme.TEXT_SECONDARY};
                    border: none;
                    border-radius: 8px;
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background-color: {theme.BG_CHIP};
                    color: {theme.TEXT_PRIMARY};
                }}
            """)
            # We'll handle the "selected" state in the view or via a property
            btn.clicked.connect(lambda checked, e=ev: self.evidence_selected.emit(e))
            self.list_layout.addWidget(btn)
            
        self.list_layout.addStretch()
        self.scroll.setWidget(self.list_widget)
        layout.addWidget(self.scroll)

class SectionContainer(QFrame):
    def __init__(self, title: str, content_widget: QWidget):
        super().__init__()
        self.setStyleSheet(f"background-color: {theme.BG_CARD}; border-radius: 12px; border: none;")
        apply_elevation(self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Title with vertical bar
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(12)
        
        bar = QFrame()
        bar.setFixedWidth(3)
        bar.setStyleSheet(f"background-color: {theme.PRIMARY}; border-radius: 2px;")
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-weight: 600; font-size: 18px; color: {theme.TEXT_PRIMARY};")
        
        title_layout.addWidget(bar)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        layout.addWidget(title_widget)
        layout.addWidget(content_widget)

class ObjectiveSection(QWidget):
    def __init__(self, objective: str):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        text = QLabel(objective)
        text.setWordWrap(True)
        text.setStyleSheet(f"font-size: 15px; color: {theme.TEXT_PRIMARY}; line-height: 1.6;")
        layout.addWidget(text)

class ExpandableTextSection(QWidget):
    def __init__(self, text: str, collapsed=True):
        super().__init__()
        self.collapsed = collapsed
        self.full_text = text
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.text_label = QLabel()
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 14px; line-height: 1.6;")
        self.layout.addWidget(self.text_label)
        
        self.toggle_btn = QPushButton("Read more →" if self.collapsed else "Show less")
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setStyleSheet(f"color: {theme.PRIMARY}; background: transparent; border: none; text-align: left; font-size: 13px; font-weight: 500;")
        self.toggle_btn.clicked.connect(self.toggle)
        self.layout.addWidget(self.toggle_btn)
        
        self.update_text()

    def toggle(self):
        self.collapsed = not self.collapsed
        self.toggle_btn.setText("Read more →" if self.collapsed else "Show less")
        self.update_text()

    def update_text(self):
        if self.collapsed:
            first_line = self.full_text.split('\\n')[0]
            if len(first_line) > 150:
                first_line = first_line[:147] + "..."
            self.text_label.setText(first_line)
        else:
            self.text_label.setText(self.full_text)

class ClueCard(QFrame):
    clue_clicked = Signal(Evidence)

    def __init__(self, clue: Clue, evidence_map: dict):
        super().__init__()
        self.clue = clue
        self.evidence_map = evidence_map
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.BG_CARD};
                border: none;
                border-radius: 12px;
            }}
            QFrame:hover {{
                background-color: {theme.BG_CARD_HOV};
            }}
        """)
        apply_elevation(self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Severity Badge
        severity = self.derive_severity()
        badge = QLabel(severity['label'])
        badge.setFixedWidth(70)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(f"""
            background-color: {severity['bg']}; 
            color: {severity['text']}; 
            font-size: 10px; 
            font-weight: bold; 
            border-radius: 12px; 
            padding: 2px;
        """)
        layout.addWidget(badge, alignment=Qt.AlignmentFlag.AlignLeft)
        
        title = QLabel(self.clue.title)
        title.setStyleSheet(f"font-weight: 600; color: {theme.TEXT_PRIMARY}; font-size: 14px;")
        title.setWordWrap(True)
        layout.addWidget(title)
        
        desc = QLabel(self.clue.description)
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 13px; line-height: 1.5;")
        layout.addWidget(desc)
        
        # Evidence links
        if self.clue.evidence_ids:
            ev_layout = QHBoxLayout()
            ev_layout.setSpacing(8)
            ev_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            
            for ev_id in self.clue.evidence_ids:
                ev = self.evidence_map.get(ev_id)
                if ev:
                    btn = QPushButton(ev.id)
                    btn.setCursor(Qt.CursorShape.PointingHandCursor)
                    btn.setStyleSheet(f"color: {theme.PRIMARY}; background: transparent; border: none; font-size: 12px; font-family: 'JetBrains Mono', monospace; text-decoration: underline;")
                    btn.clicked.connect(lambda checked, e=ev: self.clue_clicked.emit(e))
                    ev_layout.addWidget(btn)
                else:
                    lbl = QLabel("Evidence unavailable")
                    lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 12px;")
                    ev_layout.addWidget(lbl)
            
            layout.addLayout(ev_layout)
            
        layout.addStretch()

    def derive_severity(self):
        title = self.clue.title.lower()
        desc = self.clue.description.lower()
        
        if any(x in title or x in desc for x in ["mismatch", "critical", "error", "broken"]):
            return {"label": "Critical", "bg": theme.BADGE_DANGER_BG, "text": theme.DANGER}
        if any(x in title or x in desc for x in ["redundant", "hardcoded", "warning", "deprecated"]):
            return {"label": "Warning", "bg": theme.BADGE_WARNING_BG, "text": theme.WARNING}
        return {"label": "Info", "bg": theme.BADGE_PRIMARY_BG, "text": theme.PRIMARY}

class ResurrectionPlanSection(QWidget):
    def __init__(self, plan: list[ResurrectionStep]):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        for step in plan:
            card = QFrame()
            card.setStyleSheet(f"background-color: {theme.BG_CARD}; border: none; border-radius: 12px; margin-bottom: 12px;")
            apply_elevation(card)
            
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(16, 16, 16, 16)
            
            # Priority Tag
            priority_color = {
                Priority.HIGH: theme.DANGER,
                Priority.MEDIUM: theme.WARNING,
                Priority.LOW: theme.PRIMARY
            }.get(step.priority, theme.TEXT_MUTED)
            
            tag = QLabel(step.priority.value.upper())
            tag.setFixedWidth(60)
            tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tag.setStyleSheet(f"background-color: {theme.BG_CHIP}; color: {priority_color}; font-size: 10px; font-weight: bold; border-radius: 12px; padding: 4px;")
            
            # Content
            content = QWidget()
            content_layout = QVBoxLayout(content)
            content_layout.setContentsMargins(0, 0, 0, 0)
            content_layout.setSpacing(4)
            
            step_title = QLabel(step.title)
            step_title.setStyleSheet(f"font-weight: 600; color: {theme.TEXT_PRIMARY}; font-size: 14px;")
            
            step_action = QLabel(f"Action: {step.concrete_action}")
            step_action.setStyleSheet(f"color: {theme.PRIMARY}; font-size: 13px; font-weight: 500;")
            step_action.setWordWrap(True)
            
            step_desc = QLabel(step.description)
            step_desc.setWordWrap(True)
            step_desc.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 13px;")
            
            content_layout.addWidget(step_title)
            content_layout.addWidget(step_action)
            content_layout.addWidget(step_desc)
            
            card_layout.addWidget(tag)
            card_layout.addWidget(content)
            layout.addWidget(card)

class LimitationsSection(QWidget):
    def __init__(self, unknowns: list[str]):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if not unknowns:
            lbl = QLabel("No explicit limitations were reported.")
            lbl.setWordWrap(True)
            lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-style: italic; font-size: 14px;")
            layout.addWidget(lbl)
        else:
            for unknown in unknowns:
                item = QLabel(f"⚠ {unknown}")
                item.setWordWrap(True)
                item.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 14px; padding: 6px 0;")
                layout.addWidget(item)
