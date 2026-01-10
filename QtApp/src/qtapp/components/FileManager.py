from    pathlib                     import  Path
from    PySide6.QtCore              import  Qt, QFile, Slot, Signal
from    PySide6.QtWidgets           import  (QWidget,
                                             QFileDialog,
                                             QPushButton,
                                             QHBoxLayout,
                                             QLabel,
                                             QMessageBox,)


class FileManager(QWidget):

        ### declared signals
        process_finished = Signal()
        file_path_extracted = Signal()

        def __init__(self, upload, pdf, parent=None):
            super().__init__(parent)
            print("initig the file manager")


            ### local declarations


            ### member declarations
            self.file_button = QPushButton()
            self.layout = QHBoxLayout()
            self.setLayout(self.layout)
            self.dialog = QFileDialog()
            self.file_path = ""
            self.upload = upload
            self.pdf = pdf

            if upload:
                self.file_button = QPushButton("upload file/path")
            else:
                self.file_button = QPushButton("save file")
            if pdf:
                self.msg = "open PDF file"
                self.search_params = "PDF Files (*.pdf);;All Files (*)"
            else:
                self.msg = "open the path/file"
                self.search_params = "All Files (*)"


            ### options


            ### signals
            if self.upload:
                self.file_button.clicked.connect(self.open_file)
            else:
                self.file_button.clicked.connect(self.save_file)

            # self.process_finished.connect(self.finished_process)
            self.file_path_extracted.connect(self.finished_process)



            ###appending
            self.layout.addWidget(self.file_button)



        ### methods
        def open_file(self):
            file_path, _ = self.dialog.getOpenFileName(
                    self,
                    self.msg,
                    "",
                    self.search_params
                    )
            if file_path:
                print("upload path: ", file_path)
                self.file_path = file_path
                self.process_finished.emit()

        def save_file(self):
            file_path, _ = self.dialog.getSaveFileName(
                self,
                "Save PDF file",
                "",
                "PDF Files (*.pdf);;All Files (*)"
            )
            if file_path:
                print("save path: ", file_path)
                self.file_path = file_path
                self.process_finished.emit()

        def get_file_path(self):
            if self.file_path:
                if Path(self.file_path).exists():
                    send_path = self.file_path
                    self.file_path_extracted.emit()
                    return send_path
                
            self.file_path_extracted.emit()
            msg = QMessageBox.information(self, "error with file path", "error with file upload/saving")
        
        # switch between upload/save
        def switch_manager_status(self):
            self.upload = not self.upload
            if self.upload:
                self.file_button.setText("upload file")
                self.file_button.clicked.connect(self.open_file)
                self.file_path = ""
            else:
                self.file_button.setText("save file")
                self.file_button.clicked.connect(self.save_file)
                self.file_path = ""

        # get current status : upload/save
        def get_manager_status(self):
            return self.upload

        def reset_manager(self, upload=True, pdf=True):
            self.file_path = ""
            self.upload = upload
            self.pdf = pdf


        # resets the manager
        @Slot()
        def finished_process(self):
            self.file_path = ""


