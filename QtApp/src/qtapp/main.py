"""
Main application module for the Citation Linker Qt application.
Provides the tab host for running independent Citation Linker instances.
"""
import  os
import  sys
from    importlib.resources             import files
from    PySide6.QtCore                  import Qt
from    PySide6.QtGui                   import QFontDatabase, QPixmap
from    PySide6.QtWidgets               import (QApplication,
                                                QFileDialog,
                                                QHBoxLayout,
                                                QLabel,
                                                QMainWindow,
                                                QPushButton,
                                                QTabBar,
                                                QTabWidget,
                                                QToolButton,
                                                QVBoxLayout,
                                                QWidget)
from    qtapp.CitationLinkerInstance    import CitationLinkerInstance

class CitationLinkerApp(QMainWindow):
    """
    Main application window for Citation Linker.
    
    Parent: QMainWindow (from PySide6.QtWidgets)
    Children: PdfViewer, FileManager, DocConfig, TextHandler, Bridge
    
    """

    def __init__(self):
        """Initialize the main application window and all its components."""
        super().__init__()
        self.setWindowTitle("Citation Linker")

        container = QWidget(self)
        self.main_layout = QVBoxLayout(container)
        top_bar = QHBoxLayout()
        landing_layout = QVBoxLayout()
        

        self.new_tab_button = QPushButton("New Tab")
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabsClosable(False)
        self.tab_widget.setMovable(True)
        self.tab_widget.setDocumentMode(True)

        top_bar.setContentsMargins(50, 2, 50, 2)
        top_bar.addWidget(QLabel("Files"))
        top_bar.addStretch()
        top_bar.addWidget(self.new_tab_button)

        self.empty_tabs_placeholder  = QLabel("Citaton Linker App")
        self.empty_tabs_icon = QLabel()
        pixmap = load_pixmap("styles/icons/logo.png")
        if pixmap.isNull():
            self.empty_tabs_icon.setText("Logo unavailable")
        else:
            self.empty_tabs_icon.setPixmap(pixmap)
            """
            "--dry-sage": "#BBB385",
            "--pale-oak": "#D8CCAD",
            "--bone": "#E7D8C1",
            "--almond-cream": "#F5E4D4",
            "--ink-black": "#161C23",
            "--black": "#06080C",
            "--charcoal-blue": "#3C4048",
            "--dim-gray": "#6a6d75",
            "--pale-slate": "#C6C8CF",
            """

        self.empty_tabs_text = QLabel()
        self.empty_tabs_text.setWordWrap(True)
        self.empty_tabs_text.setMinimumWidth(600)
        self.empty_tabs_text.setText("""
<p>Citation Linker is a Qt-based application for creating hyperlinks between in-text citations and bibliography entries in PDF documents. It provides an interactive interface for marking citations, configuring document settings, and generating linked output PDFs.</p>

        """)

        self.empty_tabs_placeholder.setStyleSheet("""
                                                  font-size: 30px;
                                                  color: "#3c4048";
                                                  """)
        self.empty_tabs_text.setStyleSheet("""
                                           font-size: 18px;
                                           """)
        # landing_layout.addStretch()
        landing_layout.addWidget(self.empty_tabs_placeholder, alignment=Qt.AlignmentFlag.AlignHCenter)
        landing_layout.addWidget(self.empty_tabs_icon, alignment=Qt.AlignmentFlag.AlignHCenter)
        landing_layout.addWidget(self.empty_tabs_text, alignment=Qt.AlignmentFlag.AlignHCenter)
        # landing_layout.addStretch()

        self.main_layout.addLayout(top_bar)
        self.main_layout.addLayout(landing_layout)
        self.main_layout.addWidget(self.tab_widget)
        self.tab_widget.hide()
        self.setCentralWidget(container)

        self.new_tab_button.clicked.connect(self.add_tab_from_picker)

    def landing_page(self):
        if self.tab_widget.count() == 0:
            self.main_layout.addWidget(self.empty_tabs_placeholder)


    def add_tab_from_picker(self):
        """Open a file picker and create a tab only when a file is selected."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open PDF file",
            "",
            "PDF Files (*.pdf);;All Files (*)",
        )
        if not file_path:
            return

        instance = CitationLinkerInstance()
        if not instance.load_file(file_path):
            instance.deleteLater()
            return

        # self.main_layout.removeWidget(self.empty_tabs_placeholder)
        self.empty_tabs_placeholder.hide()
        self.empty_tabs_icon.hide()
        self.empty_tabs_text.hide()
        self.tab_widget.show()
        filename = os.path.basename(file_path)
        tab_idx = self.tab_widget.addTab(instance, filename)
        self.tab_widget.setCurrentIndex(tab_idx)
        self.attach_tab_close_button(tab_idx, instance)
        instance.close_requested.connect(self.close_instance_tab)
        instance.file_loaded.connect(self.on_instance_file_loaded)

    def attach_tab_close_button(self, tab_idx, instance):
        """Attach a visible rounded close button to the given tab."""
        close_button = QToolButton(self.tab_widget)
        close_button.setObjectName("tabCloseButton")
        close_button.setText("×")
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.clicked.connect(lambda _=False, inst=instance: self.close_instance_tab(inst))
        self.tab_widget.tabBar().setTabButton(tab_idx, QTabBar.ButtonPosition.RightSide, close_button)

    def close_instance_tab(self, instance):
        """Close the tab that owns the given instance widget."""
        index = self.tab_widget.indexOf(instance)
        if index != -1:
            self.close_tab_at(index)

    def close_tab_at(self, index):
        """Close one tab and clean up only that instance resources."""
        widget = self.tab_widget.widget(index)
        if widget is None:
            return

        if hasattr(widget, "cleanup_resources"):
            widget.cleanup_resources()

        self.tab_widget.removeTab(index)
        widget.deleteLater()

    def on_instance_file_loaded(self, file_path, filename):
        """Update tab text when an instance reports a newly loaded file."""
        del file_path
        instance = self.sender()
        index = self.tab_widget.indexOf(instance)
        if index != -1 and filename:
            self.tab_widget.setTabText(index, filename)

    def closeEvent(self, event):
        """Close all tab instances cleanly before exiting."""
        for index in range(self.tab_widget.count() - 1, -1, -1):
            self.close_tab_at(index)
        event.accept()


def load_fonts():
    """Load custom fonts from the styles/fonts directory."""
    try:
        font_db = QFontDatabase()
        fonts_loaded = []
        
        # Load Inclusive Sans fonts
        inclusive_sans_fonts = [
            "styles/fonts/Inclusive_Sans/static/InclusiveSans-Regular.ttf",
            "styles/fonts/Inclusive_Sans/static/InclusiveSans-Bold.ttf",
            "styles/fonts/Inclusive_Sans/static/InclusiveSans-Italic.ttf",
            "styles/fonts/Inclusive_Sans/static/InclusiveSans-BoldItalic.ttf",
        ]
        
        # Load Work Sans fonts
        work_sans_fonts = [
            "styles/fonts/Work_Sans/static/WorkSans-Regular.ttf",
            "styles/fonts/Work_Sans/static/WorkSans-Bold.ttf",
            "styles/fonts/Work_Sans/static/WorkSans-Italic.ttf",
            "styles/fonts/Work_Sans/static/WorkSans-Medium.ttf",
            "styles/fonts/Work_Sans/static/WorkSans-SemiBold.ttf",
        ]
        
        all_fonts = inclusive_sans_fonts + work_sans_fonts
        
        for font_path in all_fonts:
            try:
                path = files('qtapp').joinpath(font_path)
                font_data = path.read_bytes()
                font_id = font_db.addApplicationFontFromData(font_data)
                if font_id != -1:
                    families = font_db.applicationFontFamilies(font_id)
                    fonts_loaded.extend(families)
            except Exception as e:
                print(f"Could not load font {font_path}: {e}")
        
        if fonts_loaded:
            print(f"Successfully loaded fonts: {', '.join(set(fonts_loaded))}")
        return fonts_loaded
        
    except Exception as e:
        print(f"Error loading fonts: {e}")
        return []

def load_stylesheet(filename):
    try:
        path = files('qtapp').joinpath(filename)
        stylesheet =  path.read_text(encoding="utf-8")
        
        colors = {
            "--dry-sage": "#BBB385",
            "--pale-oak": "#D8CCAD",
            "--bone": "#E7D8C1",
            "--almond-cream": "#F5E4D4",
            "--ink-black": "#161C23",
            "--black": "#06080C",
            "--charcoal-blue": "#3C4048",
            "--dim-gray": "#6a6d75",
            "--pale-slate": "#C6C8CF",
        }

        for name, value in colors.items():
            stylesheet = stylesheet.replace(name, value)

        return stylesheet

    except Exception as e:
        print("couldn't load stylesheet: ", e)
        return ""

def load_pixmap(filename):
    """Load a pixmap from packaged resources."""
    try:
        path = files('qtapp').joinpath(filename)
        pixmap = QPixmap()
        if not pixmap.loadFromData(path.read_bytes()):
            print(f"Could not decode pixmap: {filename}")
        return pixmap
    except Exception as e:
        print(f"Could not load pixmap {filename}: {e}")
        return QPixmap()

def main():
    """Initialize and run the Citation Linker application."""
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication()
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    # Load custom fonts first
    load_fonts()
    
    # Then load and apply stylesheet
    stylesheet = load_stylesheet("styles/main.qss")
    print("stylesheeet:    ", stylesheet[:200])
    app.setStyleSheet(stylesheet)
    citationLinkerApp = CitationLinkerApp()
    citationLinkerApp.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
