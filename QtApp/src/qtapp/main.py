import  sys
import  os
from    PySide6.QtCore                  import  Slot
from    PySide6.QtWidgets               import  (QApplication,
                                                 QMessageBox,
                                                 QPushButton,
                                                 QMainWindow,
                                                 QWidget,
                                                 QHBoxLayout,
                                                 QVBoxLayout,
                                                 QLabel)
from    PySide6.QtPdf                   import  QPdfDocument
from    qtapp.components.PdfViewer      import  PdfViewer
from    qtapp.components.FileManager    import  FileManager
from    qtapp.utils.TextHandler         import  TextHandler
from    qtapp.components.DocConfig      import  DocConfig
from    qtapp.utils.Bridge              import  Bridge

class CitationLinkerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        ### local declarations
        container = QWidget()
        self.upload_path = ""

        ### layout
        self.layout = QVBoxLayout(container)
        self.horizontal_bar = QHBoxLayout()
        self.input_layout = QHBoxLayout()
        self.output_layout = QHBoxLayout()
        self.setCentralWidget(container)

        ### cross document objects
        self.view_environments = []
        self.is_input_view = True
        self.bridge = Bridge(self)
        self.document_config = DocConfig(self, self.bridge)
        self.upload_file_manager = FileManager(upload=True, pdf=True, parent=self)
        self.save_file_manager = FileManager(upload=False, pdf=True, parent=self)

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
        
        ### filename label
        self.filenameLabel = QLabel("")
        self.filenameLabel.setStyleSheet("font-weight: bold; font-size: 14px;")

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
        self.upload_file_manager.process_finished.connect(self.file_upload)
        self.configToggle.toggled.connect(self.toggle_config)
        self.switchViewers.toggled.connect(self.switch_views)
        self.startProcess.clicked.connect(self.start_linking_process)
        self.saveFile.clicked.connect(self.save_file_event)
        self.exitBtn.clicked.connect(QApplication.quit)
        self.bridge.linking_finished.connect(self.open_output_view)
        self.save_file_manager.process_finished.connect(self.perform_save)

        ### appending - Start with file upload UI
        self.layout.addWidget(self.upload_file_manager)
        self.layout.addWidget(self.filenameLabel)
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

        # Hide main UI until file is uploaded
        self.filenameLabel.hide()
        self.configToggle.hide()
        self.startProcess.hide()
        self.switchViewers.hide()
        self.saveFile.hide()
        self.exitBtn.hide()
        self.document_config.hide()


    ### methods
    def refresh_layout(self):
        self.hide()
        self.show()
        QApplication.processEvents()
    
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
    
    def clear_text_handlers(self):
        for env in self.view_environments:
            env["text_handler"].clear_all_config_info()

    def open_output_view(self, success, output_file_path):
        if not success:
            QMessageBox.warning(self, "Linking Failed",
                              "The linking process failed.\n"
                              "Please check the configuration again\n"
                              "and ensure all settings are correct.")
            return
        
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
            self.configToggle.setChecked(False)
            self.configToggle.setText("config")
            self.switchViewers.setChecked(True)
            self.switchViewers.setText("input document")
        
        self.refresh_layout()

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
        

    def file_upload(self):
        self.upload_path = self.upload_file_manager.get_file_path()
        if not self.upload_path:
            return
        
        self.initial_viewer.open_viewer(self.upload_path)
        self.document_config.file_path = self.upload_path
        self.upload_file_manager.hide()
        
        # Update filename label
        filename = os.path.basename(self.upload_path)
        self.filenameLabel.setText(f"File: {filename}")
        self.filenameLabel.show()
        
        # Show main UI after file is loaded
        self.configToggle.show()
        self.startProcess.show()
        self.switchViewers.show()
        self.saveFile.show()
        self.exitBtn.show()
        self.init_viewers_ui()

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
    def send_link_data(self, data):
        for env in self.view_environments:
            env["viewer"].view.prev_selection = data["rect"]
            env["viewer"].view.prev_viewport = data["viewport"]

    @Slot()
    def switch_views(self, checked):
        if self.configToggle.isChecked():
            self.configToggle.setChecked(False)
            self.document_config.hide()
        
        if not checked:
            self.switchViewers.setText("output document")
            for env in self.view_environments:
                if env["type"] == "input_doc":
                    env["viewer"].show()
                else:
                    env["viewer"].hide()
            self.is_input_view = True
        else:
            self.switchViewers.setText("input document")
            for env in self.view_environments:
                if env["type"] == "input_doc":
                    env["viewer"].hide()
                else:
                    env["viewer"].show()
            self.is_input_view = False
        
        self.refresh_layout()

    @Slot()
    def toggle_config(self, checked):
        if checked:
            self.configToggle.setText("viewer")
            for env in self.view_environments:
                env["viewer"].hide()
            update_data = self.text_handler.get_config_data()
            self.document_config.set_data_from_view(update_data)
            self.document_config.show()

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
        
        self.refresh_layout()

    @Slot()
    def save_file_event(self):
        pymu_doc = None
        for env in self.view_environments:
            if env["type"] == "output_doc":
                pymu_doc = env["text_handler"].document
        
        # First: Save to output directory (original behavior)
        self.bridge.save_final_doc(pymu_doc)
        
        # Second: Ask user where to save a copy
        self.save_file_manager.save_file()
    
    @Slot()
    def perform_save(self):
        save_path = self.save_file_manager.get_file_path()
        if not save_path:
            return
        
        pymu_doc = None
        for env in self.view_environments:
            if env["type"] == "output_doc":
                pymu_doc = env["text_handler"].document
        
        if pymu_doc:
            try:
                pymu_doc.save(save_path)
                QMessageBox.information(self, "Success", 
                                      f"File saved to output directory and to:\n{save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving copy to chosen location:\n{e}")
        
        self.save_file_manager.reset_manager(upload=False, pdf=True)

    def closeEvent(self, event):
        for env in self.view_environments:
            env["text_handler"].close_document()
            doc = env["document"]
            if isinstance(doc, QPdfDocument):
                doc.close()
        event.accept()


def main():
    app = QApplication()
    citationLinkerApp = CitationLinkerApp()
    citationLinkerApp.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
