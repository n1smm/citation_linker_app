from    PySide6.QtCore                  import  Qt, QFile
from    PySide6.QtWidgets               import  (QWidget,
                                             QVBoxLayout)
#qt pdf imports
from    PySide6.QtPdf                   import  QPdfDocument#, QPdfPageNavigator, QPdfPageRenderer
from    PySide6.QtPdfWidgets            import  QPdfView

#local
from    qtapp.viewerUtils.Navigator     import PdfNavigator
from    qtapp.viewerUtils.ZoomSelector  import ZoomSelector
from    qtapp.viewerUtils.TextSelector  import TextSelector
from    qtapp.viewerUtils.ExtendedView  import ExtendedView


class PdfViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        print("initing pdf viewer")

        ### local declarations        


        ### member declarations
        self.layout = QVBoxLayout() #main layout
        self.setLayout(self.layout)
        # self.view = QPdfView(self)
        self.view = ExtendedView(self)
        self.document = QPdfDocument(self)
        self.navigator = PdfNavigator(self)
        self.zoom_selector = ZoomSelector(self)
        self.text_selector = TextSelector(self)
        self.zoom_factor = 1.0

        ### initializations
        self.setWindowTitle("Viewer")
        
        ### options
        self.view.setDocument(self.document)
        self.view.setPageMode(QPdfView.MultiPage)
        self.view.hide()
        self.navigator.hide()
        self.zoom_selector.hide()
        self.view.set_selection_enabled(False)

        ### signals
        self.zoom_selector.zoom_mode_changed.connect(self.change_zoom_mode)
        self.zoom_selector.zoom_factor_changed.connect(self.change_zoom_factor)

        ### element appending
        self.layout.addWidget(self.navigator)
        self.layout.addWidget(self.zoom_selector)
        self.layout.addWidget(self.view)

    ### methods
    def open_viewer(self, file_path):
        if file_path:
            self.file_path = file_path
            self.document.load(self.file_path)
            self.navigator.set_total_pages(self.document.pageCount())
            self.navigator.set_view(self.view)
            self.navigator.show()
            self.zoom_selector.show()
            self.view.set_selection_enabled(True)
            self.view.show()

    def change_zoom_mode(self, mode):
        self.view.setZoomMode(mode)

    def change_zoom_factor(self, factor):
        self.zoom_factor = factor
        self.view.setZoomFactor(factor)




