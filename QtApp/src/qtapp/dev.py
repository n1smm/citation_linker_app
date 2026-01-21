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
from    qtapp.utils.TextHandler         import  TextHandler
from    qtapp.components.DocConfig      import  DocConfig
from    qtapp.utils.Bridge              import  Bridge

class CitationLinkerApp(QMainWindow):
    def __init__(self, file_path=None):
        super().__init__()

        ### local declarations
        container = QWidget()

        if file_path:
            self.upload_path = file_path
        else:
            self.upload_path = ""

        ### layout
        self.layout = QVBoxLayout(container) #main layout
        self.horizontal_bar = QHBoxLayout()
        self.input_layout = QHBoxLayout()
        self.output_layout = QHBoxLayout()
        self.setCentralWidget(container)

        ### cross document objects
        self.view_environments = []
        self.is_input_view = True
        self.bridge = Bridge(self)
        self.document_config = DocConfig(self, self.bridge)

        ###document/viewer environments
        self.create_document_env()
        self.create_document_env("output_doc", output=True)
        self.create_document_env("output_alt", alt=True, output=True)

        ### components (input doc view env)
        self.document = next(env["document"]
                             for env in self.view_environments if 
                             env["type"] == "input_doc")
        self.text_handler = next(env["text_handler"]
                                 for env in self.view_environments if 
                                 env["type"] == "input_doc")
        self.initial_viewer = next(env["viewer"]
                                   for env in self.view_environments if 
                                   env["type"] == "input_doc")

        ### buttons
        self.configToggle = QPushButton("config")
        self.startProcess = QPushButton("start linking")
        self.switchViewers = QPushButton("output document")
        self.saveFile = QPushButton("save file")
        self.exitBtn = QPushButton("🗙")


        ### options
        self.text_handler.set_viewer(self.initial_viewer)
        self.document_config.hide()
        self.connect_viewer_signals()

        self.switchViewers.setMaximumWidth(200)
        self.configToggle.setMaximumWidth(200)
        self.startProcess.setMaximumWidth(200)
        self.exitBtn.setMaximumWidth(20)
        self.saveFile.setMaximumWidth(200)
        self.configToggle.setCheckable(True)
        self.switchViewers.setCheckable(True)

        ### signals
        self.configToggle.toggled.connect(self.toggle_config)
        self.switchViewers.toggled.connect(self.switch_views)
        self.startProcess.clicked.connect(self.start_linking_process)
        self.saveFile.clicked.connect(self.save_file_event)
        self.exitBtn.clicked.connect(QApplication.quit)
        self.bridge.linking_finished.connect(self.open_output_view)

        ### appending
        self.init_viewers_ui()
        self.horizontal_bar.setContentsMargins(50, 2, 50, 2)
        self.horizontal_bar.setSpacing(20)
        self.horizontal_bar.addStretch()
        self.horizontal_bar.addWidget(self.configToggle)
        self.horizontal_bar.addWidget(self.startProcess)
        self.horizontal_bar.addWidget(self.switchViewers)
        self.horizontal_bar.addWidget(self.saveFile)
        self.horizontal_bar.addStretch()
        self.horizontal_bar.addWidget(self.exitBtn)

        self.layout.addLayout(self.horizontal_bar)
        self.layout.addLayout(self.input_layout)
        self.layout.addLayout(self.output_layout)
        self.layout.addWidget(self.document_config)


    ### methods
    def init_viewers_ui(self):
        for env in self.view_environments:
            if env["type"] == "input_doc":
                self.input_layout.addWidget(env["viewer"])
                self.document_config.list_widget_changed.emit("ALL", None)
            else:
                self.output_layout.addWidget(env["viewer"])

        
    def create_document_env(self, view_type="input_doc", alt=False, output=False):
        if alt:
            document = self.view_environments[-1]["document"]
            text_handler = self.view_environments[-1]["text_handler"]
        else:
            document = QPdfDocument(self)
            text_handler = TextHandler(self)
        viewer = PdfViewer(parent=self, textHandler=text_handler, isAlt=alt, isOutput=output)



        self.view_environments.append({"type": view_type,
                                        "document": document,
                                        "text_handler": text_handler,
                                        "viewer": viewer})


    def connect_viewer_signals(self):
        for env in self.view_environments:
            env["viewer"].link_saved.connect(self.send_link_data)

    @Slot()
    def send_link_data(self, data):
        for env in self.view_environments:
            env["viewer"].view.prev_selection = data["rect"]
            env["viewer"].view.prev_viewport = data["viewport"]


    def open_output_view(self, output_file_path):
        for env in self.view_environments:
            if env["type"] == "input_doc":
                env["viewer"].hide()
            else:
                env["viewer"].open_viewer(output_file_path)
                env["viewer"].show()
                self.document_config.output_file_path = output_file_path
                self.set_alt_viewer(env)
            self.document_config.hide()
            self.is_input_view = False
            self.switchViewers.setChecked(True)
            self.switchViewers.setText("input document")

    def set_alt_viewer(self, env):
        viewer = env["viewer"]
        if viewer.is_alt == False:
            return

        article_list = self.document_config.article_breaks_list
        start_page = 0
        for i in range(article_list.count()):
            if i == 0:
                tokens = article_list.item(i).text().split(":")
                start_page = int(tokens[-1]) - 1
                break
        viewer.navigator.jump_to(start_page)
        for env in self.view_environments:
            if env["viewer"] != viewer:
                env["viewer"].article_changed.connect(viewer.on_article_changed)
        
        print("start_page: ", start_page)
        

    def file_upload(self, viewer=None):
        self.initial_viewer.open_viewer(self.upload_path)
        self.document_config.file_path = self.upload_path

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
            self.bridge.start_linking_process()
        else:
            pass

    @Slot()
    def switch_views(self, checked):
        if not checked:
            self.switchViewers.setText("upload document")
            for env in self.view_environments:
                if env["type"] == "input_doc":
                    env["viewer"].show()
                else:
                    env["viewer"].hide()
            self.is_input_view = True
        else:
            self.switchViewers.setText("output document")
            for env in self.view_environments:
                if env["type"] == "input_doc":
                    env["viewer"].hide()
                else:
                    env["viewer"].show()
            self.is_input_view = False
            

    @Slot()
    def toggle_config(self, checked):
        if checked:
            self.configToggle.setText("viewer")
            # self.initial_viewer.view.hide()
            for env in self.view_environments:
                env["viewer"].hide()
            update_data = self.text_handler.get_config_data()
            self.document_config.set_data_from_view(update_data)
            self.document_config.show()
        # elif not checked:
        #     self.configToggle.setText("config")
        #     self.document_config.hide()
        #     self.initial_viewer.show()

        elif not checked and self.is_input_view:
            self.configToggle.setText("config")
            self.document_config.hide()
            self.initial_viewer.show()
        else: 
            self.configToggle.setText("config")
            self.document_config.hide()
            for env in self.view_environments:
                if env["type"] != "input_doc":
                    env["viewer"].show()

    @Slot()
    def save_file_event(self):
        pymu_doc = None
        for env in self.view_environments:
            if env["type"] == "output_doc":
                pymu_doc = env["text_handler"].document
        self.bridge.save_final_doc(pymu_doc)


    def closeEvent(self, event):
        for env in self.view_environments:
            env["text_handler"].close_document()
            doc = env["document"]
            if isinstance(doc, QPdfDocument):
                doc.close()
        event.accept()




        

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
