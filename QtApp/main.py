import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtPdf import QPdfPageNavigator, QPdfPageRenderer, QPdfDocument
from PySide6.QtPdfWidgets import QPdfView

import pymupdf


class PdfViewer(QMainWindow):
    def __init__(self):
        super().__init__()


        self.setWindowTitle("Viewer")
        container = QWidget()
        self.setCentralWidget(container)
        self.layout = QVBoxLayout(container)
        self.dialog = QFileDialog() 
        file_button = QPushButton("choose a pdf file")
        file_button.clicked.connect(self.open_file)


        self.layout.addWidget(file_button)

    def open_file(self):


def main():
    app = QApplication()
    viewer = PdfViewer()
    viewer.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
