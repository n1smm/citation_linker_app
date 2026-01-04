#main import
from PySide6.QtCore         import Qt, QPointF, QTimer, Slot
from PySide6.QtWidgets      import (QWidget,
                                    QPushButton,
                                    QSpinBox,
                                    QLabel,
                                    QHBoxLayout)

from PySide6.QtPdf          import  QPdfPageNavigator
from PySide6.QtGui          import  QValidator, QKeyEvent


class RepeatButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.click)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.timer.start()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.timer.stop()


class HumanReadableSpinBox(QSpinBox):
    def textFromValue(self, value):
        return str(value + 1)

    def valueFromText(self, text):
        try:
            return int(text) -1
        except ValueError:
            return 0

    def validate(self, text, pos):
        if text == "":
            return (QValidator.Intermediate, text, pos)
        try:
            val = int(text)
        except ValueError:
            return (QValidator.Invalid, text, pos)
        if 1 <= val <= self.maximum() + 1:
            return (QValidator.Acceptable, text, pos)
        elif val < 1:
            return (QValidator.Intermediate, text, pos)
        else:
            return (QValidator.Invalid, text, pos)




class PdfNavigator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        ### local declaration
        back_button = RepeatButton("<")
        forward_button = RepeatButton(">")
        b_history_button = QPushButton("<<")
        f_history_button = QPushButton(">>")

        total_pages = 1


        ### member declarations
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.nav = None
        self.page_display = HumanReadableSpinBox()
        self.label = QLabel(f"/{total_pages}")

        ### initializations
        self.setWindowTitle("pdf-navigator")

        ### options
        self.page_display.setValue(0)
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
    @Slot()
    def page_forward(self):
        if self.nav:
            page = self.nav.currentPage()
            location = self.nav.currentLocation()
            print("location: ", location)
            print("page: ", page)
            next_page = min(page + 1, self.page_display.maximum())
            self.nav.jump(next_page, location)
            self.update_page_display(next_page)

    #one page back
    @Slot()
    def page_back(self):
        if self.nav:
            page = self.nav.currentPage()
            location = self.nav.currentLocation()
            print("location: ", location)
            print("page: ", page)
            prev_page = max(page - 1, self.page_display.minimum())
            self.nav.jump(prev_page, location)
            self.update_page_display(prev_page)

    #one forward in logged navigation history 
    @Slot()
    def history_forward(self):
        if self.nav:
            self.nav.forward()
            page = self.nav.currentPage()
            self.update_page_display(page)

    #one back in logged navigation history 
    @Slot()
    def history_back(self):
        if self.nav:
            self.nav.back()
            page = self.nav.currentPage()
            self.update_page_display(page)

    @Slot()
    def jump_to(self, page_number, point=None):
        if self.nav:
            location = self.nav.currentLocation()
            # self.nav.jump(page, point)
            self.nav.jump(page_number, point)
            self.update_page_display(page)
        
    #updates the page_display according to nav
    @Slot()
    def update_page_display(self, page_number):
        if page_number != self.page_display.value():
            self.page_display.blockSignals(True)
            self.page_display.setValue(page_number)
            self.page_display.blockSignals(False)

    #updates navigation when changed manually in spinbox widget
    @Slot()
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
            self.page_display.setRange(0, tot_pages -1)
            self.label.setText(f"/{tot_pages}")
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

    # def keyPressEvent(self, event):
    #     print("event key", event.key())
    #     if event.key() == Qt.Key_Up:
    #         print("key up ")
    #         self.nav.jump(self.nav.currentPage() - 10, QPointF())
    #     elif event.key() == Qt.Key_Down:
    #         print("key down ")
    #         self.nav.jump(self.nav.currentPage() + 10, QPointF())
    #     else:
    #         super().keyPressEvent(event)

        
