#main import
from PySide6.QtCore         import Qt, QPointF
from PySide6.QtWidgets      import (QWidget,
                                    QPushButton,
                                    QSpinBox,
                                    QLabel,
                                    QHBoxLayout)

from PySide6.QtPdf          import  QPdfPageNavigator


class PdfNavigator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        ### local declaration
        back_button = QPushButton("<")
        forward_button = QPushButton(">")
        b_history_button = QPushButton("<<")
        f_history_button = QPushButton(">>")

        total_pages = 1


        ### member declarations
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.nav = None
        self.page_display = QSpinBox()
        self.label = QLabel(f"/{total_pages}")


        ### initializations
        self.setWindowTitle("pdf-navigator")

        ### options
        self.page_display.setValue(1)
        self.page_display.setSingleStep(10)
        """ declared in set_total_pages
        self.page_display.setRange(1, total_pages)
        self.page_display.setValue(self.nav.currentPage())
        """


        ### signals
        forward_button.clicked.connect(self.page_forward)
        back_button.clicked.connect(self.page_back)

        f_history_button.clicked.connect(self.history_forward)
        b_history_button.clicked.connect(self.history_back)

        """ declared in set_view
        self.nav.currentPageChanged.connect(self.update_page_display)
        self.page_display.editingFinished.connect(self.update_nav_from_spinbox)
        """


        ### appending
        self.layout.addWidget(b_history_button)
        self.layout.addWidget(back_button)
        self.layout.addWidget(self.page_display)
        self.layout.addWidget(self.label)
        self.layout.addWidget(forward_button)
        self.layout.addWidget(f_history_button)


    ### methods

    #1 page forward
    def page_forward(self):
        if self.nav:
            page = self.nav.currentPage()
            location = self.nav.currentLocation()
            next_page = min(page + 1, self.page_display.maximum())
            self.nav.jump(next_page, location)
            self.update_page_display(next_page)

    #one page back
    def page_back(self):
        if self.nav:
            page = self.nav.currentPage()
            location = self.nav.currentLocation()
            prev_page = max(page - 1, self.page_display.minimum())
            self.nav.jump(prev_page, location)
            self.update_page_display(prev_page)

    #one forward in logged navigation history 
    def history_forward(self):
        if self.nav:
            self.nav.forward()
            page = self.nav.currentPage()
            self.update_page_display(page)

    #one back in logged navigation history 
    def history_back(self):
        if self.nav:
            self.nav.back()
            page = self.nav.currentPage()
            self.update_page_display(page)
        
    #updates the page_display according to nav
    def update_page_display(self, page_number):
        if page_number != self.page_display.value():
            self.page_display.blockSignals(True)
            self.page_display.setValue(page_number)
            self.page_display.blockSignals(False)

    #updates navigation when changed manually in spinbox widget
    def update_nav_from_spinbox(self):
        if self.nav:
            page = self.page_display.value()
            self.nav.jump(page, QPointF())


    #setter for initializing navigation
    def set_view(self, view):
        self.nav: QPdfPageNavigator = view.pageNavigator()
        self.nav.currentPageChanged.connect(self.update_page_display)
        self.page_display.editingFinished.connect(self.update_nav_from_spinbox)

    #setter for passing number of pages in document
    def set_total_pages(self, tot_pages):
            # page = self.nav.currentPage()
            self.page_display.setRange(1, tot_pages -1)
            self.label.setText(f"/{tot_pages -1}")
            # self.update_page_display(page)

    ### getters
    def get_curr_zoom(self):
        if self.nav:
            return (self.nav.currentZoom())

    def get_curr_page(self):
        if self.nav:
            return (self.nav.currentPage())

    def get_curr_location(self):
        if self.nav:
            return(self.nav.currentLocation())

        
