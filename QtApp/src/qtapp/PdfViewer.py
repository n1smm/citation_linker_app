#main import
#from PySide6.QtUiTools      import QUiLoader
from    PySide6.QtCore              import  Qt, QFile
from    PySide6.QtWidgets           import  (QApplication,
                                         QMainWindow,
                                         QFileDialog,
                                         QPushButton,
                                         QWidget,
                                         QVBoxLayout)
#qt pdf imports
from    PySide6.QtPdf               import  QPdfDocument#, QPdfPageNavigator, QPdfPageRenderer
from    PySide6.QtPdfWidgets        import  QPdfView

#local
from    qtapp.viewerUtils.navigator  import PdfNavigator

class PdfViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        ### local declarations        
        container = QWidget()
        file_button = QPushButton("choose a pdf file")


        ### member declarations
        self.layout = QVBoxLayout(container) #main layout
        self.view = QPdfView(self)
        self.document = QPdfDocument(self)
        self.dialog = QFileDialog() 
        self.navigator = PdfNavigator(self)

        ### initializations
        self.setWindowTitle("Viewer")
        self.setCentralWidget(container)
        
        # nav.back()
        # nav.forward()
        # nav.jump(page_number, QPoint())

        ### options
        self.view.setDocument(self.document)
        self.view.setPageMode(QPdfView.MultiPage)
        self.view.hide()
        self.navigator.hide()


        ### events
        file_button.clicked.connect(self.open_file)

        ### element appending
        self.layout.addWidget(file_button)
        self.layout.addWidget(self.navigator)
        self.layout.addWidget(self.view)

    ### methods
    def open_file(self):
        file_path, _ = self.dialog.getOpenFileName(
                self,
                "open PDF file",
                "",
                "PDF Files (*.pdf);;All Files (*)"
                )
        if file_path:
            print("path: ", file_path)
            self.file_path = file_path
            self.document.load(self.file_path)
            self.navigator.set_total_pages(self.document.pageCount())
            self.navigator.set_view(self.view)
            self.navigator.show()
            self.view.show()
