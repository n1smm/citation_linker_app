from PySide6.QtWidgets  import  QApplication
from PySide6.QtCore     import  Qt
import                          sys

from qtapp.PdfViewer    import  PdfViewer


def main():
    app = QApplication()
    viewer = PdfViewer()
    viewer.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
