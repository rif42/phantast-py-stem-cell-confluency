import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QDockWidget, QLabel, QPushButton, QFrame,
    QSizePolicy, QSplitter, QScrollArea
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QPixmap, QPainter, QColor

# Assuming local imports - keeping them agnostic/try-except if they don't exist yet
try:
    from .navigation import NavigationManager
except ImportError:
    class NavigationManager:
        def __init__(self, *args, **kwargs): pass
        def register_mode(self, *args, **kwargs): pass
        def switch_to(self, *args, **kwargs): pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phantast Lab")
        self.resize(1300, 850)

        # Apply tokens
        self.apply_stylesheet()

        # Core Container
        self.main_container = QWidget()
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.main_container)

        self.setup_header()

        # Splitter for the 3 columns (Left, Center, Right)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        self.main_layout.addWidget(self.splitter)

        self.setup_left_panel()
        self.setup_center_panel()
        self.setup_right_panel()

        self.setup_footer()

        # Set specific initial widths
        self.splitter.setSizes([300, 650, 350])

    def apply_stylesheet(self):
        """Applies design tokens to the UI."""
        # Tokens
        # Primary: #00B884
        # Secondary: #E8A317
        # Neutral: #121415
        # Surface: #1E2224
        # Text: #E8EAED
        # Text-muted: #9AA0A6
        # Border: #2D3336

        style = """
        QMainWindow, QWidget {
            background-color: #121415;
            color: #E8EAED;
            font-family: "Inter", "Segoe UI", sans-serif;
            font-size: 13px;
        }
        
        /* HEADER */
        #AppHeader {
            background-color: #121415;
            border-bottom: 1px solid #2D3336;
        }
        
        /* SPLITTER */
        QSplitter::handle {
            background-color: #2D3336;
        }

        /* PANELS */
        #LeftPanel, #RightPanel {
            background-color: #121415;
        }
        
        #CenterPanel {
            background-color: #0A0B0C; /* Darker purely for image focus */
        }

        /* BUTTONS */
        QPushButton {
            border: none;
            border-radius: 4px;
            color: #E8EAED;
            font-weight: 500;
        }
        .btn-primary {
            background-color: #00B884;
            color: #ffffff;
            font-weight: bold;
        }
        .btn-primary:hover {
            background-color: #00A375;
        }
        .btn-large {
            padding: 12px;
            font-size: 14px;
        }
        .btn-small {
            padding: 4px 12px;
            font-size: 12px;
        }
        .btn-outline {
            border: 1px solid #2D3336;
            background-color: transparent;
        }
        .btn-outline:hover {
            background-color: #1E2224;
        }

        /* CARDS / SURFACES */
        .surface-card {
            background-color: #1E2224;
            border: 1px solid #2D3336;
            border-radius: 6px;
            padding: 12px;
        }
        
        /* TYPOGRAPHY */
        .text-h1 {
            font-size: 15px;
            font-weight: 600;
            color: #E8EAED;
        }
        .text-h2 {
            font-size: 12px;
            font-weight: 600;
            color: #9AA0A6;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        .text-muted {
            color: #9AA0A6;
            font-size: 12px;
        }
        .text-small {
            font-size: 11px;
            color: #9AA0A6;
        }
        .text-mono {
            font-family: "JetBrains Mono", "Consolas", monospace;
            font-size: 12px;
        }
        
        /* TAGS */
        .tag-info {
            background-color: #1B2936;
            color: #4AA1FF;
            border-radius: 4px;
            padding: 2px 6px;
            font-size: 10px;
            font-weight: bold;
        }
        .tag-warning {
            background-color: #2D240E;
            color: #E8A317;
            border-radius: 4px;
            padding: 2px 6px;
            font-size: 10px;
            font-weight: bold;
        }

        /* SCROLLBAR */
        QScrollBar:vertical {
            background: #121415;
            width: 8px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #2D3336;
            border-radius: 4px;
            min-height: 20px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        /* TABLES / LISTS */
        .list-row {
            border-bottom: 1px solid #2D3336;
            padding: 8px 0px;
        }
        """
        self.setStyleSheet(style)

    def setup_header(self):
        header = QFrame()
        header.setObjectName("AppHeader")
        header.setFixedHeight(56)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # Left side
        logo = QLabel("🔬")
        logo.setStyleSheet("font-size: 20px; color: #00B884;")
        
        title = QLabel("Phantast Integration")
        title.setProperty("class", "text-h1")
        
        layout.addWidget(logo)
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Right side -> Avatar
        avatar = QLabel()
        avatar.setFixedSize(32, 32)
        avatar.setStyleSheet("background-color: #E8A317; border-radius: 16px;")
        layout.addWidget(avatar)
        
        self.main_layout.addWidget(header)

    def setup_left_panel(self):
        panel = QFrame()
        panel.setObjectName("LeftPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Project Info
        proj_layout = QVBoxLayout()
        proj_layout.setSpacing(4)
        proj_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_proj = QLabel("Untitled Project")
        lbl_proj.setProperty("class", "text-h1")
        lbl_proj.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_status = QLabel("● Draft - Unsaved")
        lbl_status.setStyleSheet("color: #E8A317; font-size: 11px;")
        lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        proj_layout.addWidget(lbl_proj)
        proj_layout.addWidget(lbl_status)
        layout.addLayout(proj_layout)
        
        # Divider
        div1 = QFrame()
        div1.setFixedHeight(1)
        div1.setStyleSheet("background-color: #2D3336;")
        layout.addWidget(div1)
        
        # Pipeline Header
        stack_hdr_layout = QHBoxLayout()
        lbl_stack = QLabel("PIPELINE STACK")
        lbl_stack.setProperty("class", "text-h2")
        
        btn_add = QPushButton("Add")
        btn_add.setProperty("class", "btn-primary btn-small")
        btn_add.setFixedWidth(50)
        
        stack_hdr_layout.addWidget(lbl_stack)
        stack_hdr_layout.addWidget(btn_add)
        layout.addLayout(stack_hdr_layout)
        
        # Nodes (Mocks)
        
        # Input Node
        node1 = QFrame()
        node1.setProperty("class", "surface-card")
        n1_lay = QHBoxLayout(node1)
        n1_lay.setContentsMargins(12, 12, 12, 12)
        
        n1_icon = QLabel("📁")
        n1_icon.setStyleSheet("font-size: 20px; color: #4AA1FF;")
        
        n1_txt_lay = QVBoxLayout()
        n1_title = QLabel("Sample Data")
        n1_title.setProperty("class", "text-h1")
        n1_desc = QLabel("200 Files")
        n1_desc.setProperty("class", "text-muted")
        n1_txt_lay.addWidget(n1_title)
        n1_txt_lay.addWidget(n1_desc)
        
        n1_right_lay = QVBoxLayout()
        n1_tag = QLabel("INPUT")
        n1_tag.setProperty("class", "tag-info")
        n1_tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Mock Switch
        n1_switch = QFrame()
        n1_switch.setFixedSize(30, 16)
        n1_switch.setStyleSheet("background-color: #00B884; border-radius: 8px;")
        n1_right_lay.addWidget(n1_tag)
        n1_right_lay.addWidget(n1_switch, alignment=Qt.AlignmentFlag.AlignRight)
        
        n1_lay.addWidget(n1_icon)
        n1_lay.addLayout(n1_txt_lay)
        n1_lay.addStretch()
        n1_lay.addLayout(n1_right_lay)
        layout.addWidget(node1)
        
        layout.addStretch() # Space between nodes
        
        # Output Node
        node2 = QFrame()
        node2.setProperty("class", "surface-card")
        # Draw a bottom border to match design active state
        node2.setStyleSheet(node2.styleSheet() + "border-bottom: 2px solid #E8A317;")
        n2_lay = QHBoxLayout(node2)
        n2_lay.setContentsMargins(12, 12, 12, 12)
        
        n2_icon = QLabel("📥")
        n2_icon.setStyleSheet("font-size: 18px; color: #E8A317;")
        
        n2_txt_lay = QVBoxLayout()
        n2_title = QLabel("PHANTAST")
        n2_title.setProperty("class", "text-h1")
        n2_desc = QLabel("Sigma: 1.4 | Epsilon: 0.03")
        n2_desc.setProperty("class", "text-small")
        n2_txt_lay.addWidget(n2_title)
        n2_txt_lay.addWidget(n2_desc)
        
        n2_tag = QLabel("OUTPUT")
        n2_tag.setProperty("class", "tag-warning")
        n2_tag.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        
        n2_lay.addWidget(n2_icon)
        n2_lay.addLayout(n2_txt_lay)
        n2_lay.addStretch()
        n2_lay.addWidget(n2_tag)
        layout.addWidget(node2)
        
        # Run Button
        layout.addSpacing(16)
        btn_run = QPushButton("Run Pipeline")
        btn_run.setProperty("class", "btn-primary btn-large")
        layout.addWidget(btn_run)
        
        self.splitter.addWidget(panel)

    def setup_center_panel(self):
        panel = QFrame()
        panel.setObjectName("CenterPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Top floating toolbar mock
        tb_container = QWidget()
        tb_lay = QHBoxLayout(tb_container)
        tb_lay.setContentsMargins(0, 20, 0, 0)
        tb_lay.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        toolbar = QFrame()
        toolbar.setStyleSheet("background-color: #1E2224; border-radius: 6px; border: 1px solid #2D3336;")
        t_lay = QHBoxLayout(toolbar)
        t_lay.setContentsMargins(8, 8, 8, 8)
        t_lay.setSpacing(12)
        
        for icon in ["✋", "📏", "📍", "—", "100%", "＋"]:
            lbl = QLabel(icon)
            lbl.setStyleSheet("color: #9AA0A6;")
            t_lay.addWidget(lbl)
            
        tb_lay.addWidget(toolbar)
        
        # Image placeholder
        img_lbl = QLabel()
        img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # We simulate the dark image from the screenshot with text or empty space
        img_lbl.setStyleSheet("background-color: transparent;")
        
        layout.addWidget(tb_container)
        layout.addWidget(img_lbl, 1) # Take remaining space
        
        self.splitter.addWidget(panel)

    def setup_right_panel(self):
        panel = QFrame()
        panel.setObjectName("RightPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(24)
        
        # Header
        lbl_prop = QLabel("⚙ PROPERTIES")
        lbl_prop.setProperty("class", "text-h2")
        layout.addWidget(lbl_prop)
        
        div1 = QFrame()
        div1.setFixedHeight(1)
        div1.setStyleSheet("background-color: #2D3336;")
        layout.addWidget(div1)
        
        # Section 1: Folder Explorer
        self._add_accordion_header(layout, "📁 Folder Explorer", right_icon="▼")
        
        # Columns
        col_lay = QHBoxLayout()
        for t in ["FILE", "SIZE", "STATUS"]:
            l = QLabel(t)
            l.setProperty("class", "text-small")
            col_lay.addWidget(l)
        layout.addLayout(col_lay)
        
        # Rows
        for file, size, icon, in [("79_0.JPG", "2.1 MB", "✅"), 
                                  ("80_-1.JPG", "2.4 MB", "👁"), 
                                  ("79_0.JPG", "2.1 MB", "✅")]:
            r_lay = QHBoxLayout()
            r_lay.addWidget(QLabel(f"🖼 {file}"))
            r_lay.addWidget(QLabel(size, property="text-mono"))
            r_lay.addWidget(QLabel(icon))
            layout.addLayout(r_lay)
        
        # Paginator
        pag_lay = QHBoxLayout()
        pag_lay.addWidget(QPushButton("< Previous", property="btn-outline btn-small"))
        lbl_page = QLabel("2 / 48")
        lbl_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_page.setProperty("class", "text-muted")
        pag_lay.addWidget(lbl_page)
        pag_lay.addWidget(QPushButton("Next >", property="btn-outline btn-small"))
        layout.addLayout(pag_lay)
        
        layout.addWidget(div1)
        
        # Section 2: Metadata
        self._add_accordion_header(layout, "ⓘ Image Metadata")
        
        meta_card = QFrame()
        meta_card.setProperty("class", "surface-card")
        m_lay = QVBoxLayout(meta_card)
        
        hdr = QLabel("IMG_001.TIFF")
        hdr.setProperty("class", "text-h1")
        m_lay.addWidget(hdr)
        
        for k, v in [("Dimensions", "1280 x 720"), ("Bit Depth", "16-bit"), ("Channels", "Grayscale (1)")]:
            r = QHBoxLayout()
            lbl_k = QLabel(k)
            lbl_k.setProperty("class", "text-muted")
            lbl_v = QLabel(v)
            lbl_v.setProperty("class", "text-mono")
            lbl_v.setAlignment(Qt.AlignmentFlag.AlignRight)
            r.addWidget(lbl_k)
            r.addWidget(lbl_v)
            m_lay.addLayout(r)
        
        layout.addWidget(meta_card)
        
        # Section 3: Histogram
        self._add_accordion_header(layout, "Histogram", right_text="Log Scale")
        
        hist_ph = QFrame()
        hist_ph.setFixedHeight(80)
        hist_ph.setStyleSheet("border: 1px solid #2D3336; border-radius: 4px; background-color: transparent;")
        layout.addWidget(hist_ph)
        
        layout.addStretch()
        
        self.splitter.addWidget(panel)

    def _add_accordion_header(self, layout, title, right_text=None, right_icon=None):
        r = QHBoxLayout()
        lbl = QLabel(title)
        lbl.setProperty("class", "text-h1")
        r.addWidget(lbl)
        if right_text:
            rt = QLabel(right_text)
            rt.setStyleSheet("color: #00B884; font-size: 11px;")
            r.addWidget(rt, alignment=Qt.AlignmentFlag.AlignRight)
        if right_icon:
            ri = QLabel(right_icon)
            ri.setStyleSheet("color: #9AA0A6;")
            r.addWidget(ri, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(r)


    def setup_footer(self):
        footer = QFrame()
        footer.setFixedHeight(30)
        footer.setStyleSheet("background-color: #121415; border-top: 1px solid #2D3336;")
        f_lay = QHBoxLayout(footer)
        f_lay.setContentsMargins(20, 0, 20, 0)
        
        v_lbl = QLabel("v2.4.1 (Stable)")
        v_lbl.setProperty("class", "text-mono text-muted")
        
        s_lbl = QLabel("● Ready")
        s_lbl.setStyleSheet("color: #00B884; font-size: 11px;")
        
        f_lay.addWidget(v_lbl)
        f_lay.addWidget(s_lbl, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.main_layout.addWidget(footer)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
