from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, Slot
from ghost_projects.schemas.project import ProjectInfo
from ghost_projects.schemas.assessment import ProjectAssessment
from ghost_projects.ui.views.dashboard_components import (
    ProjectInfoHeader, InvestigationStats, EvidenceSidebar, 
    EvidenceDetailDialog, ObjectiveSection, ExpandableTextSection, 
    ClueCard, ResurrectionPlanSection, LimitationsSection, SectionContainer
)
from ghost_projects.ui import theme

class ResultsView(QWidget):
    back_requested = Signal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Main layout: Sidebar + Content
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Sidebar
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(260)
        self.sidebar.setStyleSheet(f"background-color: {theme.BG_SIDEBAR};")
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Logo/Title
        logo_container = QWidget()
        logo_container.setMinimumHeight(80)
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(24, 24, 24, 24)
        
        logo_label = QLabel("GHOST\nPROJECTS")
        logo_label.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-weight: 800; font-size: 20px; letter-spacing: 2px;")
        logo_layout.addWidget(logo_label)
        sidebar_layout.addWidget(logo_container)

        # Evidence Explorer
        self.evidence_sidebar = None # Set in set_results
        self.sidebar_content = QWidget()
        sidebar_content_layout = QVBoxLayout(self.sidebar_content)
        sidebar_content_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.addWidget(self.sidebar_content)

        # Footer: Back Button
        footer = QWidget()
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(20, 20, 20, 20)
        
        self.back_button = QPushButton("Return to welcome")
        self.back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_button.clicked.connect(self.on_back_clicked)
        self.back_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.BG_CHIP};
                color: {theme.TEXT_SECONDARY};
                padding: 12px;
                border-radius: 8px;
                font-size: 13px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {theme.BG_CARD_HOV};
                color: {theme.TEXT_PRIMARY};
            }}
        """)
        footer_layout.addWidget(self.back_button)
        sidebar_layout.addWidget(footer, alignment=Qt.AlignmentFlag.AlignBottom)

        self.main_layout.addWidget(self.sidebar)

        # 2. Main Content Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet(f"background-color: {theme.BG_PAGE}; border: none;")
        
        self.main_content = QWidget()
        self.main_content_layout = QVBoxLayout(self.main_content)
        self.main_content_layout.setContentsMargins(32, 32, 32, 32)
        self.main_content_layout.setSpacing(24)
        
        self.scroll_area.setWidget(self.main_content)
        self.main_layout.addWidget(self.scroll_area)

    def set_results(self, project_info: ProjectInfo, assessment: ProjectAssessment):
        # Clear previous results
        for i in reversed(range(self.main_content_layout.count())): 
            self.main_content_layout.itemAt(i).widget().setParent(None)
        
        # Clear sidebar content
        for i in reversed(range(self.sidebar_content.layout().count())):
            self.sidebar_content.layout().itemAt(i).widget().setParent(None)

        # 1. Sidebar Evidence
        self.evidence_sidebar = EvidenceSidebar(assessment)
        self.evidence_sidebar.evidence_selected.connect(self.show_evidence_detail)
        self.sidebar_content.layout().addWidget(self.evidence_sidebar)

        # 2. Project Header
        self.main_content_layout.addWidget(ProjectInfoHeader(project_info))

        # 3. Stats
        self.main_content_layout.addWidget(InvestigationStats(assessment))

        # 4. Primary Objective
        self.main_content_layout.addWidget(
            SectionContainer("Primary Objective", ObjectiveSection(assessment.original_intent))
        )

        # 5. Summary
        self.main_content_layout.addWidget(
            SectionContainer("Investigation Summary", ExpandableTextSection(assessment.investigation_summary))
        )

        # 6. Architecture
        self.main_content_layout.addWidget(
            SectionContainer("Architecture Overview", ExpandableTextSection(assessment.recovered_architecture))
        )

        # 7. Clues Found
        clues_widget = QWidget()
        clues_layout = QVBoxLayout(clues_widget)
        clues_layout.setContentsMargins(0, 0, 0, 0)
        
        self.clues_grid = QGridLayout()
        self.clues_grid.setSpacing(16)
        self.clues_grid.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        evidence_map = {ev.id: ev for ev in assessment.evidence}
        for i, clue in enumerate(assessment.clues):
            card = ClueCard(clue, evidence_map)
            card.clue_clicked.connect(self.show_evidence_detail)
            self.clues_grid.addWidget(card, i // 3, i % 3)
            
        clues_layout.addLayout(self.clues_grid)
        self.main_content_layout.addWidget(
            SectionContainer("Clues Found", clues_widget)
        )

        # 8. Resurrection Plan
        self.main_content_layout.addWidget(
            SectionContainer("Resurrection Plan", ResurrectionPlanSection(assessment.resurrection_plan))
        )

        # 9. Limitations
        self.main_content_layout.addWidget(
            SectionContainer("Limitations & Unknowns", LimitationsSection(assessment.unknowns))
        )

    def set_error(self, error_message: str):
        for i in reversed(range(self.main_content_layout.count())): 
            self.main_content_layout.itemAt(i).widget().setParent(None)
            
        err_label = QLabel(f"INVESTIGATION FAILED\n\n{error_message}")
        err_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        err_label.setStyleSheet(f"color: {theme.DANGER}; font-size: 16px; padding: 40px;")
        err_label.setWordWrap(True)
        self.main_content_layout.addWidget(err_label)

    @Slot(object)
    def show_evidence_detail(self, evidence):
        dialog = EvidenceDetailDialog(evidence, self)
        dialog.exec()

    def on_back_clicked(self):
        self.back_requested.emit()
