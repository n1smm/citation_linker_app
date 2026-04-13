"""
Main application module for the Citation Linker Qt application.
Provides the user interface for linking citations in PDF documents to their bibliography entries.
"""
import  sys
import  os
import  time
from    importlib.resources             import  files
from    PySide6.QtCore                  import  Qt, Slot, QFile
from    PySide6.QtGui                   import  QFontDatabase
from    PySide6.QtWidgets               import  (QApplication,
                                                 QMessageBox,
                                                 QPushButton,
                                                 QMainWindow,
                                                 QWidget,
                                                 QHBoxLayout,
                                                 QVBoxLayout,
                                                 QStackedLayout,
                                                 QLabel,
                                                 QSizePolicy)
from    PySide6.QtPdf                   import  QPdfDocument
from    qtapp.CitationLinkerInstance    import  CitationLinkerInstance
from    qtapp.components.PdfViewer      import  PdfViewer
from    qtapp.components.FileManager    import  FileManager
from    qtapp.utils.TextHandler         import  TextHandler
from    qtapp.components.DocConfig      import  DocConfig
from    qtapp.components.DebugOutput    import  DebugOutput
from    qtapp.utils.Bridge              import  Bridge

class CitationLinkerApp(QMainWindow):
    """
    Main application window for Citation Linker.
    
    Parent: QMainWindow (from PySide6.QtWidgets)
    Children: PdfViewer, FileManager, DocConfig, TextHandler, Bridge
    
    """

    def __init__(self):
        super().__init__()

        container = QWidget()
        tabs_container = QWidget()
        main_layout = QStackedLayout(container)
        tabs_layout = QHBoxLayout()
        self.setCentralWidget(container)

        self.tabs = []
        self.tab_labels = []


    def add_tab(self):
        """ add a new instance of citation linker with a separate tab label """

        tmp_instance = CitationLinkerInstance()
        tmp_tab = {"instance": tmp_instance}
        tmp_instance.file_upload()
        filename = tmp_instance.upload_path
        self.create_label(filename, tmp_tab)
        self.tabs.append(tmp_instance)

    def create_label(self, name, tab):
        """ creates an element with a filename and x button to close the tab """
        tab_layout = QHBoxLayout()
        label = QLabel(name)
        btn = QPushButton("X")
        tab_layout.addWidget(label)
        tab_layout.addWidget(btn)
        tab["layout"] = tab_layout
        tab["label"] = label
        tab["button"] = btn

        
        

        
        

        
        

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

def get_checkmark_path():
    """Get the absolute path to the checkmark icon."""
    try:
        # Try to get path from package resources
        path = files('qtapp').joinpath('styles/icons/checkmark.svg')
        # Convert to string path that QSS can use
        return str(path)
    except Exception as e:
        print(f"Could not find checkmark icon: {e}")
        return ""

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
    citationLinkerApp.showMaximized()  # Start maximized

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
