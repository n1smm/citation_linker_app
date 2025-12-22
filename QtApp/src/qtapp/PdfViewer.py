from    PySide6.QtCore              import  Qt, QFile
from    PySide6.QtWidgets           import  (QWidget,
                                             QVBoxLayout)
#qt pdf imports
from    PySide6.QtPdf               import  QPdfDocument#, QPdfPageNavigator, QPdfPageRenderer
from    PySide6.QtPdfWidgets        import  QPdfView

#local
from    qtapp.viewerUtils.Navigator  import PdfNavigator

class PdfViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        print("initing pdf viewer")

        ### local declarations        


        ### member declarations
        self.layout = QVBoxLayout() #main layout
        self.setLayout(self.layout)
        self.view = QPdfView(self)
        self.document = QPdfDocument(self)
        self.navigator = PdfNavigator(self)

        ### initializations
        self.setWindowTitle("Viewer")
        
        ### options
        self.view.setDocument(self.document)
        self.view.setPageMode(QPdfView.MultiPage)
        self.view.hide()
        self.navigator.hide()

        ### events

        ### element appending
        self.layout.addWidget(self.navigator)
        self.layout.addWidget(self.view)

    ### methods
    def open_viewer(self, file_path):
        if file_path:
            self.file_path = file_path
            self.document.load(self.file_path)
            self.navigator.set_total_pages(self.document.pageCount())
            self.navigator.set_view(self.view)
            self.navigator.show()
            self.view.show()



