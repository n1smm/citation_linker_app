import  sys
from    PySide6.QtCore                  import  Slot
from    PySide6.QtWidgets               import  (QApplication,
                                                 QMessageBox,
                                                 QPushButton,
                                                 QMainWindow,
                                                 QWidget,
                                                 QHBoxLayout,
                                                 QVBoxLayout)
from    PySide6.QtPdf                   import  QPdfDocument#, QPdfPageNavigator, QPdfPageRenderer
from    qtapp.components.PdfViewer      import  PdfViewer
from    qtapp.viewerUtils.TextHandler   import  TextHandler
from    qtapp.components.DocConfig      import  DocConfig

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
        self.horizontal_bar = QHBoxLayout()
        self.setCentralWidget(container)
        self.document_config = DocConfig(self)
        self.document = QPdfDocument(self)
        self.text_handler = TextHandler(self)
        self.initial_viewer = PdfViewer(parent=self, textHandler=self.text_handler)

        self.configToggle = QPushButton("config")
        self.startProcess = QPushButton("start linking")
        self.configToggle.setMaximumWidth(200)
        self.startProcess.setMaximumWidth(200)

        ### options
        self.text_handler.set_viewer(self.initial_viewer)
        self.document_config.hide()

        ### signals
        self.configToggle.toggled.connect(self.toggle_config)
        self.startProcess.clicked.connect(self.start_linking_process)

        ### appending
        self.horizontal_bar.setContentsMargins(200, 2, 200, 2)
        self.horizontal_bar.setSpacing(20)
        self.horizontal_bar.addWidget(self.configToggle)
        self.horizontal_bar.addWidget(self.initial_viewer.zoom_selector)
        self.horizontal_bar.addWidget(self.startProcess)

        self.layout.addLayout(self.horizontal_bar)
        self.layout.addWidget(self.initial_viewer)
        self.layout.addWidget(self.document_config)
        self.configToggle.setCheckable(True)


    ### methods
    def file_upload(self):
        self.initial_viewer.open_viewer(self.upload_path)
        self.document_config.file_path = self.upload_path

    @Slot()
    def toggle_config(self, checked):
        if checked:
            self.configToggle.setText("viewer")
            self.initial_viewer.view.hide()
            update_data = self.text_handler.get_config_data()
            self.document_config.set_data_from_view(update_data)
            self.document_config.show()
        else:
            self.configToggle.setText("config")
            self.document_config.hide()
            self.initial_viewer.view.show()

    def start_linking_process(self):
        update_data = self.text_handler.get_config_data()
        print(update_data)
        self.document_config.set_data_from_view(update_data)
        reply = QMessageBox.information(self, "Are you sure?",
                                ("Are you sure?,\n"
                                 "otherwise check again\n"
                                 "if the configuration is okay."),
                                QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            print(reply)
        else:
            print(reply)
            #

        

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
