"""
Main application module for the Citation Linker Qt application.
Provides the user interface for linking citations in PDF documents to their bibliography entries.
"""
import  sys
import  os
import  time
from    PySide6.QtCore                  import  Qt, Slot
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
from    qtapp.components.PdfViewer      import  PdfViewer
from    qtapp.components.FileManager    import  FileManager
from    qtapp.utils.TextHandler         import  TextHandler
from    qtapp.components.DocConfig      import  DocConfig
from    qtapp.utils.Bridge              import  Bridge

class CitationLinkerApp(QMainWindow):
    """
    Main application window for Citation Linker.
    
    Parent: QMainWindow (from PySide6.QtWidgets)
    Children: PdfViewer, FileManager, DocConfig, TextHandler, Bridge
    
    This class orchestrates the entire citation linking workflow including:
    - PDF file upload and viewing
    - Citation configuration management
    - Document processing and link creation
    - Output file generation and saving
    
    The application manages multiple document environments (input and output views)
    and provides UI controls for switching between configuration and viewing modes.
    """
    def __init__(self):
        """Initialize the main application window and all its components."""
        super().__init__()

        container = QWidget()
        self.upload_path = ""


        self.layout = QVBoxLayout(container)
        self.horizontal_bar = QHBoxLayout()

        self.input_container = QWidget()
        self.output_container = QWidget()
        self.input_layout = QHBoxLayout(self.input_container)
        self.output_layout = QHBoxLayout(self.output_container)
        self.stacked_layout = QStackedLayout()

        self.layout.setStretchFactor(self.horizontal_bar, 0)
        self.setCentralWidget(container)


        self.view_environments = []
        self.is_input_view = True
        self.bridge = Bridge(self)
        self.document_config = DocConfig(self, self.bridge)
        self.upload_file_manager = FileManager(upload=True, pdf=True, parent=self)
        self.save_file_manager = FileManager(upload=False, pdf=True, parent=self)

        self.create_document_env()
        self.create_document_env("output_doc", output=True)
        self.create_document_env("output_alt", alt=True, output=True)


        self.document = next(env["document"]
                             for env in self.view_environments if 
                             env["type"] == "input_doc")
        self.text_handler = next(env["text_handler"]
                                 for env in self.view_environments if 
                                 env["type"] == "input_doc")
        self.initial_viewer = next(env["viewer"]
                                   for env in self.view_environments if 
                                   env["type"] == "input_doc")


        self.configToggle = QPushButton("config")
        self.startProcess = QPushButton("start linking")
        self.switchViewers = QPushButton("output document")
        self.saveFile = QPushButton("save file")
        self.exitBtn = QPushButton("🗙")
        
        self.filenameLabel = QLabel("")
        self.filenameLabel.setStyleSheet("font-weight: bold; font-size: 14px;")


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


        self.upload_file_manager.process_finished.connect(self.file_upload)
        self.configToggle.toggled.connect(self.toggle_config)
        self.switchViewers.toggled.connect(self.switch_views)
        self.startProcess.clicked.connect(self.start_linking_process)
        self.saveFile.clicked.connect(self.save_file_event)
        self.exitBtn.clicked.connect(QApplication.quit)
        self.bridge.linking_finished.connect(self.open_output_view)
        self.save_file_manager.process_finished.connect(self.perform_save)


        self.layout.addWidget(self.upload_file_manager)
        self.layout.addWidget(self.filenameLabel)
        self.horizontal_bar.setContentsMargins(50, 2, 50, 2)
        self.input_layout.setContentsMargins(0, 0, 0, 0)
        self.output_layout.setContentsMargins(0, 0, 0, 0)
        self.horizontal_bar.setSpacing(20)
        self.horizontal_bar.addStretch()
        self.horizontal_bar.addWidget(self.configToggle)
        self.horizontal_bar.addWidget(self.startProcess)
        self.horizontal_bar.addWidget(self.switchViewers)
        self.horizontal_bar.addWidget(self.saveFile)
        self.horizontal_bar.addStretch()
        self.horizontal_bar.addWidget(self.exitBtn)

        self.stacked_layout.addWidget(self.input_container) # 0
        self.stacked_layout.addWidget(self.output_container) # 1
        self.stacked_layout.addWidget(self.document_config) # 2

        self.input_idx = self.stacked_layout.indexOf(self.input_container)
        self.output_idx = self.stacked_layout.indexOf(self.output_container)
        self.config_idx = self.stacked_layout.indexOf(self.document_config)


        self.layout.addLayout(self.horizontal_bar, stretch=0)
        self.layout.addLayout(self.stacked_layout, stretch=1)
        # self.layout.addLayout(self.input_layout, stretch=1)
        # self.layout.addLayout(self.output_layout, stretch=1)
        # self.layout.addWidget(self.document_config, stretch=1)


        self.filenameLabel.hide()
        self.configToggle.hide()
        self.startProcess.hide()
        self.switchViewers.hide()
        self.saveFile.hide()
        self.exitBtn.hide()
        self.document_config.hide()


    def refresh_layout(self):
        """Force UI refresh by hiding and showing the main window."""

        self.layout.invalidate()
        self.layout.activate()
        self.centralWidget().updateGeometry()
        
        QApplication.processEvents()
        # self.hide()
        # self.show()
        # QApplication.processEvents()
    
    def init_viewers_ui(self):
        """Initialize and display all viewer widgets in their respective layouts."""
        for env in self.view_environments:
            # Set size policy for viewers to expand and fill space
            env["viewer"].setSizePolicy(QSizePolicy.Policy.Expanding,
                                        QSizePolicy.Policy.Expanding)
            
            if env["type"] == "input_doc":
                self.input_layout.addWidget(env["viewer"])
                self.document_config.list_widget_changed.emit("ALL", None)
            else:
                self.output_layout.addWidget(env["viewer"])
        
    def create_document_env(self, view_type="input_doc", alt=False, output=False):
        """
        Create a document viewing environment with associated handlers and viewers.
        
        Args:
            view_type: Type identifier for the environment ("input_doc", "output_doc", "output_alt")
            alt: Whether this is an alternative viewer (shares document with previous environment)
            output: Whether this is an output viewer (for processed documents)
        """
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
        """Connect link_saved signals from all viewers to the data handler."""
        for env in self.view_environments:
            env["viewer"].link_saved.connect(self.send_link_data)
    
    def clear_text_handlers(self):
        """Clear configuration data from all text handlers."""
        for env in self.view_environments:
            env["text_handler"].clear_all_config_info()

    def open_output_view(self, success, output_file_path):
        """
        Open the output view showing the processed PDF with linked citations.
        
        Args:
            success: Whether the linking process completed successfully
            output_file_path: Path to the generated output PDF file
        """
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
            self.stacked_layout.setCurrentIndex(self.output_idx)
            self.document_config.hide()
            self.is_input_view = False
            self.configToggle.setChecked(False)
            self.configToggle.setText("config")
            self.switchViewers.setChecked(True)
            self.switchViewers.setText("input document")
        
        self.refresh_layout()

    def set_alt_viewer(self, env):
        """
        Configure the alternative viewer to display article-specific content.
        
        Args:
            env: The viewer environment dictionary containing the viewer to configure
        """
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
        """Handle the file upload process and initialize the main viewer UI."""
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
        """Initiate the citation linking process after user confirmation."""
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
        """
        Distribute link selection data to all viewer environments.
        
        Args:
            data: Dictionary containing 'rect' and 'viewport' for link highlighting
        """
        for env in self.view_environments:
            env["viewer"].view.prev_selection = data["rect"]
            env["viewer"].view.prev_viewport = data["viewport"]

    @Slot()
    def switch_views(self, checked):
        """
        Toggle between input document and output document views.
        
        Args:
            checked: True for output view, False for input view
        """
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
            self.stacked_layout.setCurrentIndex(self.input_idx)
        else:
            self.switchViewers.setText("input document")
            for env in self.view_environments:
                if env["type"] == "input_doc":
                    env["viewer"].hide()
                else:
                    env["viewer"].show()
            self.is_input_view = False
            self.stacked_layout.setCurrentIndex(self.output_idx)
        
        self.refresh_layout()

    @Slot()
    def toggle_config(self, checked):
        """
        Toggle between configuration panel and viewer display.
        
        Args:
            checked: True to show config panel, False to show viewer
        """
        if checked:
            self.configToggle.setText("viewer")
            for env in self.view_environments:
                env["viewer"].hide()
            update_data = self.text_handler.get_config_data()
            self.stacked_layout.setCurrentIndex(self.config_idx)
            self.document_config.set_data_from_view(update_data)
            self.document_config.show()

        elif not checked and self.is_input_view:
            self.configToggle.setText("config")
            self.document_config.hide()
            self.stacked_layout.setCurrentIndex(self.input_idx)
            self.initial_viewer.show()
        else: 
            self.configToggle.setText("config")
            self.document_config.hide()
            self.stacked_layout.setCurrentIndex(self.output_idx)
            for env in self.view_environments:
                if env["type"] != "input_doc":
                    env["viewer"].show()

        
        self.refresh_layout()

    @Slot()
    def save_file_event(self):
        """Handle the file save event by saving to output directory and prompting for user location."""
        pymu_doc = None
        for env in self.view_environments:
            if env["type"] == "output_doc":
                pymu_doc = env["text_handler"].document
        
        # self.bridge.save_final_doc(pymu_doc)
        
        self.save_file_manager.save_file()
    
    @Slot()
    def perform_save(self):
        """Save a copy of the output document to a user-specified location."""
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
        """Clean up resources when the application window is closed."""
        for env in self.view_environments:
            env["text_handler"].close_document()
            doc = env["document"]
            if isinstance(doc, QPdfDocument):
                doc.close()
        event.accept()


def main():
    """Initialize and run the Citation Linker application."""
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication()
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    citationLinkerApp = CitationLinkerApp()
    citationLinkerApp.showMaximized()  # Start maximized

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
