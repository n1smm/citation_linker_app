import  sys
from    PySide6.QtWidgets             import  (QApplication,
                                                 QMainWindow,
                                                 QWidget,
                                                 QVBoxLayout)
from    PySide6.QtPdf                 import  QPdfDocument#, QPdfPageNavigator, QPdfPageRenderer
from    qtapp.components.PdfViewer    import  PdfViewer

class CitationLinkerApp(QMainWindow):
    def __init__(self, file_path=None):
        super().__init__()

        ### local declarations
        container = QWidget()

        if file_path:
            self.upload_path = file_path
        else:
            self.upload_path = ""

        ### member declarations
        self.layout = QVBoxLayout(container) #main layout
        self.setCentralWidget(container)
        self.document = QPdfDocument(self)

        self.initialViewer = PdfViewer(self)




        ### appending
        self.layout.addWidget(self.initialViewer)


    ### methods
    def file_upload(self):
        self.initialViewer.open_viewer(self.upload_path)

def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = None
    print(file_path)
    app = QApplication()
    citationLinkerApp = CitationLinkerApp(file_path)
    citationLinkerApp.file_upload()
    citationLinkerApp.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
