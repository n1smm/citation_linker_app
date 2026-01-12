import  sys
from    PySide6.QtWidgets               import  (QApplication,
                                                 QMainWindow,
                                                 QWidget,
                                                 QVBoxLayout)
from    PySide6.QtCore                  import  Qt
from    PySide6.QtPdf                   import  QPdfDocument#, QPdfPageNavigator, QPdfPageRenderer
from    PySide6.QtPdfWidgets            import  QPdfView

from    qtapp.components.PdfViewer      import  PdfViewer
from    qtapp.components.FileManager    import  FileManager
from    qtapp.utils.TextHandler         import  TextHandler
from    qtapp.components.DocConfig      import  DocConfig

class CitationLinkerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        ### local declarations
        container = QWidget()


        ### member declarations
        self.layout = QVBoxLayout(container) #main layout
        self.setCentralWidget(container)
        self.document = QPdfDocument(self)

        self.documentConfig = DocConfig(self)
        self.fileManager = FileManager(upload=True, pdf=True, parent=self)
        self.textHandler = TextHandler(self)
        self.initialViewer = PdfViewer(parent=self, textHandler=self.textHandler)

        self.upload_path = ""

        ###options
        self.textHandler.set_viewer(self.initialViewer)
        self.documentConfig.hide()


        ### signals
        self.fileManager.process_finished.connect(self.file_upload)


        ### appending
        self.layout.addWidget(self.fileManager)
        self.layout.addWidget(self.documentConfig)
        self.layout.addWidget(self.initialViewer)



    ### methods
    def file_upload(self):
        self.upload_path = self.fileManager.get_file_path()
        self.documentConfig.file_path = self.upload_path
        self.initialViewer.open_viewer(self.upload_path)
        self.fileManager.hide()

def main():
    app = QApplication()
    citationLinkerApp = CitationLinkerApp()
    citationLinkerApp.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
