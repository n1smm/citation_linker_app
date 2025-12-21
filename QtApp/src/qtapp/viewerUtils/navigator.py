#main import
from PySide6.QtCore         import Qt, QPoint, QPointF, Slot
from PySide6.QtUiTools      import QUiLoader
from PySide6.QtWidgets      import (QWidget,
                                    QPushButton,
                                    QSpinBox,
                                    QHBoxLayout)

from PySide6.QtPdfWidgets   import  QPdfView
from PySide6.QtPdf          import  QPdfPageNavigator


class PdfNavigator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        ### local declaration
        back_button = QPushButton("back")
        forward_button = QPushButton("forward")

        total_pages = 1
        


        ### member declarations
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.nav = None
        self.page_display = QSpinBox()


        ### initializations
        self.setWindowTitle("pdf-navigator")
        self.page_display.setRange(1, total_pages)
        # self.page_display.setValue(self.nav.currentPage())
        self.page_display.setValue(1)


        ### signals
        back_button.clicked.connect(self.page_back)
        forward_button.clicked.connect(self.page_forward)




        


        ### appending
        self.layout.addWidget(back_button)
        self.layout.addWidget(self.page_display)
        self.layout.addWidget(forward_button)


    ### methods
    def page_forward(self):
        if self.nav:
            self.nav.forward()
            page = self.nav.currentPage()
            self.page_display.blockSignals(True)
            self.page_display.setValue(page)
            self.page_display.blockSignals(False)

    def page_back(self):
        if self.nav:
            self.nav.back()
            page = self.nav.currentPage()
            self.page_display.blockSignals(True)
            self.page_display.setValue(page)
            self.page_display.blockSignals(False)
        
    def update_page_display(self, page_number):
        if page_number != self.page_display.value():
            self.page_display.blockSignals(True)
            self.page_display.setValue(page_number)
            self.page_display.blockSignals(False)

    @Slot()
    def set_view(self, view):
        self.nav = QPdfPageNavigator(view)
        self.nav.currentPageChanged.connect(self.update_page_display)
        self.page_display.valueChanged.connect(
                                        lambda i:
                                        self.nav.jump(i, QPoint())
                                       )

    @Slot()
    def set_total_pages(self, total_pages):
        self.page_display.setRange(1, total_pages)

        
