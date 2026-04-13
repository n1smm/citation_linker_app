"""
Main application module for the Citation Linker Qt application.
Provides the tab host for running independent Citation Linker instances.
"""
import  os
import  sys
from    importlib.resources             import files
from    PySide6.QtCore                  import Qt
from    PySide6.QtGui                   import QFontDatabase
from    PySide6.QtWidgets               import (QApplication,
                                                QFileDialog,
                                                QHBoxLayout,
                                                QLabel,
                                                QMainWindow,
                                                QPushButton,
                                                QTabWidget,
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
        super().__init__()
        self.setWindowTitle("Citation Linker")

        container = QWidget(self)
        main_layout = QVBoxLayout(container)
        top_bar = QHBoxLayout()

        self.new_tab_button = QPushButton("New Tab")
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.setDocumentMode(True)

        top_bar.setContentsMargins(50, 8, 50, 8)
        top_bar.addWidget(QLabel("Files"))
        top_bar.addStretch()
        top_bar.addWidget(self.new_tab_button)

        main_layout.addLayout(top_bar)
        main_layout.addWidget(self.tab_widget)
        self.setCentralWidget(container)

        self.new_tab_button.clicked.connect(self.add_tab_from_picker)
        self.tab_widget.tabCloseRequested.connect(self.close_tab_at)

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

        filename = os.path.basename(file_path)
        tab_idx = self.tab_widget.addTab(instance, filename)
        self.tab_widget.setCurrentIndex(tab_idx)
        instance.close_requested.connect(self.close_instance_tab)
        instance.file_loaded.connect(self.on_instance_file_loaded)

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
