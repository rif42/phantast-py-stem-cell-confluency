import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpacerItem, QSizePolicy, QFrame, QScrollArea, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal

from PyQt6.QtGui import QIcon, QPainter, QColor, QPen

class ToggleSwitch(QPushButton):
    """A custom toggle switch styled for the node."""
    def __init__(self, checked=True):
        super().__init__()
        self.setCheckable(True)
        self.setChecked(checked)
        self.setFixedSize(36, 20)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg_color = QColor("#00B884") if self.isChecked() else QColor("#2D3336")
        handle_color = QColor("#FFFFFF")
        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 10, 10)
        handle_x = self.width() - 18 if self.isChecked() else 2
        painter.setBrush(handle_color)
        painter.drawEllipse(handle_x, 2, 16, 16)
        painter.end()


class IntegrationNodeWidget(QFrame):
    def __init__(self, title, desc, ntype, border_color):
        super().__init__()
        self.setObjectName("integNode")
        self.setFixedHeight(72)
        self.setStyleSheet(f"#integNode {{ border: 1px solid {border_color}; border-radius: 8px; background-color: transparent; }}")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Icon
        icon_f = QFrame()
        icon_f.setFixedSize(32, 32)
        icon_f.setStyleSheet("background-color: #2D3336; border-radius: 4px; border: none;")
        icon_l = QVBoxLayout(icon_f)
        icon_l.setContentsMargins(0,0,0,0)
        icon_lbl = QLabel("📂" if ntype == "INPUT" else "⬇️")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_l.addWidget(icon_lbl)
        layout.addWidget(icon_f)
        
        # Text
        text_l = QVBoxLayout()
        text_l.setContentsMargins(0,0,0,0)
        text_l.setSpacing(2)
        t_lbl = QLabel(title)
        t_lbl.setStyleSheet("color: #E8EAED; font-weight: 600; font-size: 13px; border: none;")
        d_lbl = QLabel(desc)
        d_lbl.setStyleSheet("color: #9AA0A6; font-size: 11px; border: none;")
        text_l.addWidget(t_lbl)
        text_l.addWidget(d_lbl)
        layout.addLayout(text_l, stretch=1)
        
        # Actions
        act_l = QVBoxLayout()
        act_l.setContentsMargins(0,0,0,0)
        act_l.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        badge_color = "#3B82F6" if ntype == "INPUT" else "#E8A317"
        badge = QLabel(ntype)
        badge.setStyleSheet(f"background-color: {badge_color}33; color: {badge_color}; font-size: 9px; font-weight: bold; padding: 2px 4px; border-radius: 2px; border: none;")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        switch = ToggleSwitch(True)
        
        act_l.addWidget(badge, alignment=Qt.AlignmentFlag.AlignRight)
        act_l.addWidget(switch, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(act_l)


class BatchExecutionIntegrationWidget(QWidget):
    """
    The unified integration view for Batch Execution & Output.
    Combines the Pipeline Stack, Center Canvas, and Right Properties panel.
    """
    
    # Signals
    run_pipeline = pyqtSignal()
    open_folder = pyqtSignal(str)
    
    def __init__(self, data_path: str = None):
        super().__init__()
        
        # Load sample data if provided
        self.batch_job = {}
        self.results = []
        if data_path and os.path.exists(data_path):
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.batch_job = data.get('batchJob', {})
                self.results = data.get('results', [])
                
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("QSplitter::handle { background-color: #2D3336; }")

        self.left_panel = self.create_left_panel()
        splitter.addWidget(self.left_panel)

        self.canvas_area = self.create_canvas_area()
        splitter.addWidget(self.canvas_area)

        self.right_panel = self.create_right_panel()
        splitter.addWidget(self.right_panel)

        # Ratios based on screenshot
        splitter.setStretchFactor(0, 0) # left panel fixed
        splitter.setStretchFactor(1, 1) # canvas stretches
        splitter.setStretchFactor(2, 0) # right panel fixed

        main_layout.addWidget(splitter)

    def create_left_panel(self) -> QWidget:
        panel = QFrame()
        panel.setMinimumWidth(260)
        panel.setMaximumWidth(280)
        panel.setObjectName("leftPanel")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Project Header
        proj_hdr = QFrame()
        proj_hdr.setObjectName("projHdr")
        proj_hdr.setFixedHeight(64)
        ph_layout = QVBoxLayout(proj_hdr)
        ph_layout.setContentsMargins(16, 12, 16, 12)
        ph_layout.setSpacing(2)
        
        title_lbl = QLabel("Untitled Project")
        title_lbl.setStyleSheet("color: #E8EAED; font-weight: bold; font-size: 14px;")
        
        status_h = QHBoxLayout()
        status_h.setContentsMargins(0,0,0,0)
        status_h.setSpacing(4)
        dot = QLabel("●")
        dot.setStyleSheet("color: #E8A317; font-size: 10px;")
        sub_lbl = QLabel("Draft - Unsaved")
        sub_lbl.setStyleSheet("color: #9AA0A6; font-size: 11px;")
        status_h.addWidget(dot)
        status_h.addWidget(sub_lbl)
        status_h.addStretch()
        
        ph_layout.addWidget(title_lbl)
        ph_layout.addLayout(status_h)
        layout.addWidget(proj_hdr)
        
        # Pipeline Stack Header
        ps_hdr = QFrame()
        ps_hdr.setFixedHeight(48)
        ps_hdr_l = QHBoxLayout(ps_hdr)
        ps_hdr_l.setContentsMargins(16, 0, 16, 0)
        
        lbl = QLabel("PIPELINE STACK")
        lbl.setStyleSheet("color: #9AA0A6; font-size: 11px; font-weight: bold; letter-spacing: 0.5px;")
        add_btn = QPushButton("Add")
        add_btn.setObjectName("addBtn")
        add_btn.setFixedSize(50, 24)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        ps_hdr_l.addWidget(lbl)
        ps_hdr_l.addStretch()
        ps_hdr_l.addWidget(add_btn)
        layout.addWidget(ps_hdr)
        
        # Nodes area
        nodes_area = QFrame()
        nodes_l = QVBoxLayout(nodes_area)
        nodes_l.setContentsMargins(16, 0, 16, 0)
        nodes_l.setSpacing(0)
        
        node1 = IntegrationNodeWidget("Sample Data", "200 Files", "INPUT", "#3B82F6")
        
        line_f = QFrame()
        line_f.setFixedHeight(240) # Simulate space
        line_l = QVBoxLayout(line_f)
        line_l.setContentsMargins(36, 0, 0, 0)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setStyleSheet("color: #00B884; border-left: 1px solid #00B884; max-width: 1px;")
        line_l.addWidget(line)
        
        # Little arrow point at end of line (mocking with layout)
        arrow = QLabel("↓")
        arrow.setStyleSheet("color: #00B884; font-size: 10px;")
        arrow_l = QVBoxLayout()
        arrow_l.setContentsMargins(33, 0, 0, 0)
        arrow_l.addWidget(arrow)
        
        node2 = IntegrationNodeWidget("PHANTAST", "Sigma: 1.4 | Epsilon: 0.03", "OUTPUT", "#E8A317")
        
        nodes_l.addWidget(node1)
        nodes_l.addWidget(line_f)
        nodes_l.addLayout(arrow_l)
        nodes_l.addWidget(node2)
        nodes_l.addStretch()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(nodes_area)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(scroll)
        
        # Run Bottom
        run_f = QFrame()
        run_f.setFixedHeight(64)
        run_l = QVBoxLayout(run_f)
        run_l.setContentsMargins(16, 12, 16, 12)
        
        btn = QPushButton("Run Pipeline")
        btn.setObjectName("runBtn")
        btn.setFixedHeight(36)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self.run_pipeline.emit)
        
        run_l.addWidget(btn)
        layout.addWidget(run_f)
        
        return panel

    def create_canvas_area(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("canvasArea")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 16, 0, 0)
        
        # Floating Toolbar (mocked top-center)
        tb_f = QFrame()
        tb_f.setObjectName("floatingToolbar")
        tb_f.setFixedSize(200, 36)
        
        tb_l = QHBoxLayout(tb_f)
        tb_l.setContentsMargins(12, 0, 12, 0)
        tb_l.setSpacing(12)
        
        for icon in ["✋", "📏", "📍", "—", "100%", "➕"]:
            btn = QPushButton(icon)
            btn.setFixedSize(24, 24)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            if icon == "100%":
                btn.setFixedWidth(40)
                btn.setStyleSheet("color: #9AA0A6; font-size: 11px; background: transparent; border: none;")
            else:
                btn.setStyleSheet("color: #9AA0A6; font-size: 14px; background: transparent; border: none;")
            tb_l.addWidget(btn)
            
        toolbar_l = QHBoxLayout()
        toolbar_l.addStretch()
        toolbar_l.addWidget(tb_f)
        toolbar_l.addStretch()
        
        layout.addLayout(toolbar_l)
        
        # Main Canvas Placeholder
        canvas_lbl = QLabel("Image Viewer Canvas\n(Will display high-res TIFF)")
        canvas_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        canvas_lbl.setStyleSheet("color: #2D3336; font-size: 16px;")
        layout.addWidget(canvas_lbl, stretch=1)
        
        return panel

    def create_right_panel(self) -> QWidget:
        panel = QFrame()
        panel.setMinimumWidth(320)
        panel.setMaximumWidth(380)
        panel.setObjectName("rightPanel")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # PROPERTIES Header
        hdr_f = QFrame()
        hdr_f.setFixedHeight(48)
        hdr_f.setObjectName("rightHdr")
        hdr_l = QHBoxLayout(hdr_f)
        hdr_l.setContentsMargins(16, 0, 16, 0)
        
        lbl = QLabel("🛠 PROPERTIES")
        lbl.setStyleSheet("color: #9AA0A6; font-size: 11px; font-weight: bold; letter-spacing: 0.5px;")
        hdr_l.addWidget(lbl)
        hdr_l.addStretch()
        layout.addWidget(hdr_f)
        
        # --- Folder Explorer Section ---
        fe_hdr = QFrame()
        fe_hdr.setFixedHeight(40)
        fe_hdr_l = QHBoxLayout(fe_hdr)
        fe_hdr_l.setContentsMargins(16, 0, 16, 0)
        fe_lbl = QLabel("📁 Folder Explorer")
        fe_lbl.setStyleSheet("color: #E8EAED; font-weight: bold; font-size: 13px;")
        fe_hdr_l.addWidget(fe_lbl)
        fe_hdr_l.addStretch()
        layout.addWidget(fe_hdr)
        
        # Table
        table = QTableWidget(5, 3)
        table.setObjectName("fileTable")
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(1, 60)
        table.setColumnWidth(2, 60)
        table.setHorizontalHeaderLabels(["FILE", "SIZE", "STATUS"])
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        
        # Dummy data matching mockup
        data = [
            ("79_0.JPG", "2.1 MB", "ok"),
            ("80_-1.JPG", "2.4 MB", "viewing"),
            ("79_0.JPG", "2.1 MB", "ok"),
            ("79_0.JPG", "2.1 MB", "ok"),
            ("79_0.JPG", "2.1 MB", "ok"),
        ]
        
        for r, (fname, fsize, fstat) in enumerate(data):
            # File
            i_f = QTableWidgetItem(f"🖼 {fname}")
            if fstat == "viewing":
                i_f.setForeground(QColor("#FFFFFF"))
            else:
                i_f.setForeground(QColor("#E8EAED"))
            table.setItem(r, 0, i_f)
            
            # Size
            i_s = QTableWidgetItem(fsize)
            i_s.setForeground(QColor("#9AA0A6"))
            table.setItem(r, 1, i_s)
            
            # Status
            if fstat == "viewing":
                lbl_badge = QLabel("VIEWING")
                lbl_badge.setStyleSheet("background-color: #00B88433; color: #00B884; font-size: 9px; font-weight: bold; border-radius: 2px; padding: 2px 4px;")
                lbl_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
                w = QWidget()
                l = QHBoxLayout(w)
                l.setContentsMargins(0,0,0,0)
                l.addWidget(lbl_badge, alignment=Qt.AlignmentFlag.AlignCenter)
                table.setCellWidget(r, 2, w)
            else:
                i_st = QTableWidgetItem("✅")
                i_st.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                i_st.setForeground(QColor("#00B884"))
                table.setItem(r, 2, i_st)
                
        layout.addWidget(table)
        
        # Pagination
        pag_f = QFrame()
        pag_l = QHBoxLayout(pag_f)
        pag_l.setContentsMargins(16, 12, 16, 12)
        prv = QPushButton("< Previous")
        prv.setObjectName("outlineBtn")
        nxt = QPushButton("Next >")
        nxt.setObjectName("outlineBtn")
        p_lbl = QLabel("12 / 48")
        p_lbl.setStyleSheet("color: #9AA0A6; font-size: 11px;")
        pag_l.addWidget(prv)
        pag_l.addStretch()
        pag_l.addWidget(p_lbl)
        pag_l.addStretch()
        pag_l.addWidget(nxt)
        layout.addWidget(pag_f)
        
        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #2D3336;")
        layout.addWidget(sep)
        
        # --- Image Metadata Section ---
        md_hdr = QFrame()
        md_hdr.setFixedHeight(40)
        md_hdr_l = QHBoxLayout(md_hdr)
        md_hdr_l.setContentsMargins(16, 0, 16, 0)
        md_lbl = QLabel("ℹ️ Image Metadata")
        md_lbl.setStyleSheet("color: #E8EAED; font-weight: bold; font-size: 13px;")
        md_hdr_l.addWidget(md_lbl)
        md_hdr_l.addStretch()
        layout.addWidget(md_hdr)
        
        # Metadata Card
        card = QFrame()
        card.setObjectName("integNode") # Reuse styling
        card.setStyleSheet("#integNode { border: 1px solid #2D3336; border-radius: 8px; margin: 0 16px; }")
        card_l = QVBoxLayout(card)
        card_l.setContentsMargins(12, 12, 12, 12)
        
        c_top = QHBoxLayout()
        c_icon = QLabel("🖼")
        c_icon.setStyleSheet("background-color: #2D3336; padding: 8px; border-radius: 4px;")
        c_top.addWidget(c_icon)
        c_titles = QVBoxLayout()
        c_t1 = QLabel("IMG_001.TIFF")
        c_t1.setStyleSheet("color: #E8EAED; font-weight: bold; font-size: 12px;")
        c_t2 = QLabel("Source Input")
        c_t2.setStyleSheet("color: #9AA0A6; font-size: 10px;")
        c_titles.addWidget(c_t1)
        c_titles.addWidget(c_t2)
        c_top.addLayout(c_titles)
        c_top.addStretch()
        card_l.addLayout(c_top)
        
        card_l.addSpacing(8)
        
        # Grid
        stats = [("Dimensions", "1280 x 720"), ("Bit Depth", "16-bit"), ("Channels", "Grayscale (1)"), ("File Size", "1.8 MB")]
        for k, v in stats:
            h = QHBoxLayout()
            kl = QLabel(k)
            kl.setStyleSheet("color: #9AA0A6; font-size: 11px;")
            vl = QLabel(v)
            vl.setStyleSheet("color: #E8EAED; font-size: 11px; font-family: 'JetBrains Mono', monospace;")
            h.addWidget(kl)
            h.addStretch()
            h.addWidget(vl)
            card_l.addLayout(h)
            
        layout.addWidget(card)
        
        # Histogram
        hg_hdr = QHBoxLayout()
        hg_hdr.setContentsMargins(16, 16, 16, 0)
        h_lbl = QLabel("Histogram")
        h_lbl.setStyleSheet("color: #E8EAED; font-size: 11px; font-weight: bold;")
        h_bdg = QLabel("Log Scale")
        h_bdg.setStyleSheet("color: #00B884; font-size: 9px; border: 1px solid #00B884; padding: 2px 4px; border-radius: 2px;")
        hg_hdr.addWidget(h_lbl)
        hg_hdr.addStretch()
        hg_hdr.addWidget(h_bdg)
        layout.addLayout(hg_hdr)
        
        hist = HistogramWidget()
        hist.setStyleSheet("margin: 8px 16px;")
        layout.addWidget(hist)
        
        layout.addStretch()
        
        # Footer
        ftr = QFrame()
        ftr.setFixedHeight(32)
        ftr.setStyleSheet("border-top: 1px solid #2D3336;")
        ftr_l = QHBoxLayout(ftr)
        ftr_l.setContentsMargins(16, 0, 16, 0)
        v_lbl = QLabel("v2.4.1 (Stable)")
        v_lbl.setStyleSheet("color: #9AA0A6; font-size: 11px; border: none;")
        s_lbl = QLabel("● Ready")
        s_lbl.setStyleSheet("color: #00B884; font-size: 11px; font-weight: bold; border: none;")
        ftr_l.addWidget(v_lbl)
        ftr_l.addStretch()
        ftr_l.addWidget(s_lbl)
        layout.addWidget(ftr)
        
        return panel

    def apply_styles(self):
        self.setStyleSheet("""
            BatchExecutionIntegrationWidget {
                background-color: #121415;
                font-family: 'Inter';
            }
            #leftPanel, #rightPanel {
                background-color: #121415;
                border: none;
            }
            #leftPanel {
                border-right: 1px solid #2D3336;
            }
            #rightPanel {
                border-left: 1px solid #2D3336;
            }
            #canvasArea {
                background-color: #0B0D0E;
            }
            #projHdr {
                border-bottom: 1px solid #2D3336;
            }
            #addBtn {
                background-color: #00B884;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                font-weight: 600;
                font-size: 12px;
            }
            #addBtn:hover {
                background-color: #00C890;
            }
            #runBtn {
                background-color: #00B884;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                font-weight: 600;
                font-size: 14px;
            }
            #runBtn:hover {
                background-color: #00C890;
            }
            #floatingToolbar {
                background-color: #1E2224;
                border: 1px solid #2D3336;
                border-radius: 8px;
            }
            #rightHdr {
                border-bottom: 1px solid #2D3336;
            }
            #fileTable {
                background-color: transparent;
                border: none;
                color: #E8EAED;
                font-size: 11px;
            }
            #fileTable::item {
                border-bottom: 1px solid #2D3336;
                padding-left: 8px;
            }
            QHeaderView::section {
                background-color: #1E2224;
                color: #9AA0A6;
                font-size: 10px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #2D3336;
                padding-left: 8px;
            }
            #outlineBtn {
                background-color: transparent;
                color: #9AA0A6;
                border: 1px solid #2D3336;
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 11px;
            }
            #outlineBtn:hover {
                background-color: #1E2224;
                color: #E8EAED;
            }
        """)

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView

class HistogramWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(60)
        self.values = [
            2, 4, 10, 15, 25, 30, 45, 60, 80, 100, 120, 150, 180, 200, 
            210, 190, 160, 130, 90, 70, 50, 30, 40, 60, 75, 55, 35, 20, 10, 5, 2
        ]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Grid lines
        painter.setPen(QPen(QColor("#2D3336"), 1))
        painter.drawLine(0, h-15, w, h-15)
        
        # Labels
        painter.setPen(QColor("#9AA0A6"))
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        painter.drawText(0, h-2, "0")
        painter.drawText(w//2 - 10, h-2, "128")
        painter.drawText(w - 20, h-2, "255")
        
        # Bars
        bar_w = max(2, w // len(self.values))
        max_v = max(self.values)
        
        painter.setPen(Qt.PenStyle.NoPen)
        for i, val in enumerate(self.values):
            bar_h = int((val / max_v) * (h - 20))
            x = i * bar_w
            y = (h - 15) - bar_h
            
            # Highlight selected area or just use primary color
            painter.setBrush(QColor("#00B884"))
            painter.drawRect(x, y, bar_w - 1, bar_h)
            
        painter.end()
