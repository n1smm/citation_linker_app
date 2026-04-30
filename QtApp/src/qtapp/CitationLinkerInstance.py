"""
Citation Linker tab instance widget.
Each instance is independent and can run in a separate tab.
"""
import  os
from    PySide6.QtCore                  import  QObject, QThread, Qt, Signal, Slot
from    PySide6.QtWidgets               import  (QApplication,
                                                 QDialog,
                                                 QMessageBox,
                                                 QProgressBar,
                                                 QPushButton,
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
from    qtapp.components.DebugOutput            import  DebugOutput
from    qtapp.components.BibStructureEditor     import  BibStructureEditor
from    qtapp.utils.Bridge              import  Bridge
from    citation_linker.io_safe         import  atomic_replace_save, normalize_path, FileLockError

class LinkingWorker(QObject):
    """Runs the linking process in a worker thread."""
    finished = Signal()

    def __init__(self, bridge, cmd_in=None):
        super().__init__()
        self.bridge = bridge
        self.cmd_in = cmd_in

    @Slot()
    def run(self):
        try:
            self.bridge.start_linking_process(cmd_in=self.cmd_in, skip_ui_prep=True)
        finally:
            self.finished.emit()

class CitationLinkerInstance(QWidget):
    """ 
    instance of citationLinker app. main window can open those as separate tabs.
    each instance is independent and doesn't communicate with others

    This class orchestrates the entire citation linking workflow including:
    - PDF file upload and viewing
    - Citation configuration management
    - Document processing and link creation
    - Output file generation and saving
    
    The application manages multiple document environments (input and output views)
    and provides UI controls for switching between configuration and viewing modes.
    """

    close_requested = Signal(object)
    file_loaded = Signal(str, str)

    def __init__(self):
        """Initialize the main application window and all its components."""
        super().__init__()

        self.upload_path = ""
        self._viewers_initialized = False
        self._resources_cleaned = False

        self.main_layout = QVBoxLayout(self)
        self.horizontal_bar = QHBoxLayout()

        self.input_container = QWidget()
        self.output_container = QWidget()
        self.input_layout = QHBoxLayout(self.input_container)
        self.output_layout = QHBoxLayout(self.output_container)
        self.stacked_layout = QStackedLayout()

        self.main_layout.setStretchFactor(self.horizontal_bar, 0)


        self.view_environments = []
        self.is_input_view = True
        self.bridge = Bridge(self)
        self.debug_output = DebugOutput(parent=self)
        self.debug_output.setWindowFlags(Qt.Window)
        self.debug_output.setWindowTitle("Debug Output")
        self.debug_output.resize(800, 600)
        self.bib_structure_editor = BibStructureEditor(parent=self)
        self.document_config = DocConfig(self, self.bridge)
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
        self._linking_thread = None
        self._linking_worker = None
        self.loading_window = None
        self.loading_bar = None


        self.configToggle = QPushButton("config")
        self.startProcess = QPushButton("start linking")
        self.switchViewers = QPushButton("output document")
        self.saveFile = QPushButton("save file")
        self.exitBtn = QPushButton("🗙")
        
        self.filenameLabel = QLabel("")
        self.filenameLabel.setStyleSheet("font-weight: bold; font-size: 14px;")


        self.text_handler.set_viewer(self.initial_viewer)
        if self.document_config.config_path and os.path.exists(self.document_config.config_path):
            self.document_config.load_config()
        self.document_config.hide()
        self.connect_viewer_signals()

        self.switchViewers.setMaximumWidth(200)
        self.configToggle.setMaximumWidth(200)
        self.startProcess.setMaximumWidth(200)
        self.exitBtn.setMaximumWidth(20)
        self.saveFile.setMaximumWidth(200)
        self.configToggle.setCheckable(True)
        self.switchViewers.setCheckable(True)


        self.configToggle.toggled.connect(self.toggle_config)
        self.switchViewers.toggled.connect(self.switch_views)
        self.startProcess.clicked.connect(self.start_linking_process)
        self.saveFile.clicked.connect(self.save_file_event)
        self.exitBtn.clicked.connect(self.request_close)
        self.bridge.linking_finished.connect(self.on_linking_finished_ui)
        self.bridge.linking_finished.connect(self.open_output_view)
        if hasattr(self.bridge, "log_messages_ready"):
            self.bridge.log_messages_ready.connect(self.debug_output.set_debug_messages)
        if hasattr(self.bridge, "bib_entries_ready"):
            self.bridge.bib_entries_ready.connect(self.debug_output.set_bib_entries)
        if hasattr(self.bridge, "cit_entries_ready"):
            self.bridge.cit_entries_ready.connect(self.debug_output.set_cit_entries)
        self.save_file_manager.process_finished.connect(self.perform_save)


        self.main_layout.addWidget(self.filenameLabel)
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


        self.main_layout.addLayout(self.horizontal_bar, stretch=0)
        self.main_layout.addLayout(self.stacked_layout, stretch=1)
        self.filenameLabel.hide()
        self.configToggle.hide()
        self.startProcess.hide()
        self.switchViewers.hide()
        self.saveFile.hide()
        self.exitBtn.hide()
        self.document_config.hide()


    def setup_loading_window(self):
        """Create a small modeless progress window."""
        if self.loading_window is not None:
            return
        self.loading_window = QDialog(self, Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.loading_window.setObjectName("loadingWindow")
        self.loading_window.setWindowTitle("Processing")
        self.loading_window.setModal(False)
        self.loading_window.setFixedSize(260, 90)

        layout = QVBoxLayout(self.loading_window)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        label = QLabel("Linking citations...")
        label.setObjectName("loadingWindowLabel")
        self.loading_bar = QProgressBar()
        self.loading_bar.setObjectName("loadingProgressBar")
        self.loading_bar.setRange(0, 0)
        self.loading_bar.setTextVisible(False)

        layout.addWidget(label)
        layout.addWidget(self.loading_bar, alignment=Qt.AlignmentFlag.AlignHCenter)

    def show_loading_window(self):
        """Show and activate processing indicator window."""
        self.setup_loading_window()
        self.loading_window.show()
        self.loading_window.raise_()
        self.loading_window.activateWindow()

    def hide_loading_window(self):
        """Hide processing indicator window if visible."""
        if self.loading_window is not None:
            self.loading_window.hide()

    def refresh_layout(self):
        """Force UI refresh by hiding and showing the main window."""

        self.main_layout.invalidate()
        self.main_layout.activate()
        self.updateGeometry()
        self.input_container.updateGeometry()
        self.output_container.updateGeometry()
        
        QApplication.processEvents()
        # self.hide()
        # self.show()
        # QApplication.processEvents()
    
    def init_viewers_ui(self):
        """Initialize and display all viewer widgets in their respective layouts."""
        if self._viewers_initialized:
            return

        for env in self.view_environments:
            # Set size policy for viewers to expand and fill space
            env["viewer"].setSizePolicy(QSizePolicy.Policy.Expanding,
                                        QSizePolicy.Policy.Expanding)
            
            if env["type"] == "input_doc":
                self.input_layout.addWidget(env["viewer"])
                self.document_config.list_widget_changed.emit("ALL", None)
            else:
                self.output_layout.addWidget(env["viewer"])
        self._viewers_initialized = True
        
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
        

    def load_file(self, file_path):
        """Load a selected file into this tab instance."""
        if not file_path:
            return False

        self.upload_path = file_path
        
        self.initial_viewer.open_viewer(self.upload_path)
        self.document_config.file_path = self.upload_path
        
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
        self.file_loaded.emit(self.upload_path, filename)
        return True

    def file_upload(self):
        """Compatibility wrapper for previous upload-manager flow."""
        return self.load_file(self.upload_path)

    @Slot()
    def request_close(self):
        """Ask the host window to close this instance tab."""
        self.close_requested.emit(self)

    def start_linking_process(self):
        """Initiate the citation linking process after user confirmation."""
        if self._linking_thread is not None and self._linking_thread.isRunning():
            return

        update_data = self.text_handler.get_config_data()
        print(update_data)
        self.document_config.set_data_from_view(update_data)
        reply = QMessageBox.information(self, "Are you sure?",
                                ("Are you sure?,\n"
                                 "otherwise check again\n"
                                 "if the configuration is okay."),
                                QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.document_config.save_config()
            self.bridge.input_file_path = self.upload_path
            self.startProcess.setEnabled(False)
            self.show_loading_window()

            self._linking_thread = QThread(self)
            self._linking_worker = LinkingWorker(self.bridge)
            self._linking_worker.moveToThread(self._linking_thread)

            self._linking_thread.started.connect(self._linking_worker.run)
            self._linking_worker.finished.connect(self._linking_thread.quit)
            self._linking_worker.finished.connect(self._linking_worker.deleteLater)
            self._linking_thread.finished.connect(self._linking_thread.deleteLater)
            self._linking_thread.finished.connect(self.on_linking_worker_finished)

            self._linking_thread.start()
        else:
            pass

    @Slot(bool, str)
    def on_linking_finished_ui(self, success, output_file_path):
        """Reset UI state when linking completes."""
        del success, output_file_path
        self.hide_loading_window()
        self.startProcess.setEnabled(True)

    @Slot()
    def on_linking_worker_finished(self):
        """Release worker/thread references after completion."""
        self._linking_thread = None
        self._linking_worker = None

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
                target_path = normalize_path(save_path)
                atomic_replace_save(target_path, lambda temp_path: pymu_doc.save(temp_path))
                QMessageBox.information(self, "Success", 
                                      f"File saved to output directory and to:\n{target_path}")
            except FileLockError as e:
                QMessageBox.critical(
                    self,
                    "File Locked",
                    f"Cannot save because the destination file is in use:\n{e}",
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving copy to chosen location:\n{e}")
        
        self.save_file_manager.reset_manager(upload=False, pdf=True)

    def cleanup_resources(self):
        """Release document resources used by this instance."""
        if self._resources_cleaned:
            return

        closed_handlers = set()
        closed_documents = set()
        for env in self.view_environments:
            text_handler = env["text_handler"]
            handler_id = id(text_handler)
            if handler_id not in closed_handlers:
                text_handler.close_document()
                closed_handlers.add(handler_id)

            doc = env["document"]
            if isinstance(doc, QPdfDocument):
                doc_id = id(doc)
                if doc_id not in closed_documents:
                    try:
                        doc.close()
                    except RuntimeError:
                        pass
                    closed_documents.add(doc_id)
        self.hide_loading_window()
        self._resources_cleaned = True

    def closeEvent(self, event):
        """Clean up resources when the instance widget is closed."""
        self.cleanup_resources()
        event.accept()
