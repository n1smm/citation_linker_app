"""
PDF navigation widget with page controls and navigation history.
Provides page forward/back, history navigation, and manual page jumping.
"""
from PySide6.QtCore         import Qt, QPointF, QTimer, Slot
from PySide6.QtWidgets      import (QWidget,
                                    QPushButton,
                                    QSpinBox,
                                    QLabel,
                                    QHBoxLayout)

from PySide6.QtPdf          import  QPdfPageNavigator
from PySide6.QtGui          import  QValidator, QKeyEvent


class RepeatButton(QPushButton):
    """
    Button that repeats clicks while held down.
    
    Parent: Navigator
    Children: None
    Used for page navigation buttons that auto-repeat when held.
    """
    def __init__(self, *args, **kwargs):
        """Initialize button with auto-repeat timer."""
        super().__init__(*args, **kwargs)
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.click)

    def mousePressEvent(self, event):
        """Start auto-repeat timer on button press."""
        super().mousePressEvent(event)
        self.timer.start()

    def mouseReleaseEvent(self, event):
        """Stop auto-repeat timer on button release."""
        super().mouseReleaseEvent(event)
        self.timer.stop()


class HumanReadableSpinBox(QSpinBox):
    """
    SpinBox that displays 1-based page numbers but stores 0-based indices.
    
    Parent: Navigator
    Children: None
    Converts between human-readable page numbers (1, 2, 3...) and 
    internal zero-based indices (0, 1, 2...).
    """
    def textFromValue(self, value):
        """Convert 0-based index to 1-based page number for display."""
        return str(value + 1)

    def valueFromText(self, text):
        """Convert 1-based page number to 0-based index."""
        try:
            return int(text) -1
        except ValueError:
            return 0

    def validate(self, text, pos):
        """Validate page number input."""
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
    """
    PDF navigation control panel with page navigation and history.
    
    Parent: ExtendedView
    Children: RepeatButton, HumanReadableSpinBox
    
    Provides UI controls for:
    - Forward/backward page navigation with auto-repeat
    - Navigation history (back/forward through visited pages)
    - Manual page number entry
    - Current page display with total page count
    """
    def __init__(self, parent=None):
        """Initialize navigation widget with buttons and page display."""
        super().__init__(parent)

        back_button = RepeatButton("<")
        forward_button = RepeatButton(">")
        b_history_button = QPushButton("<<")
        f_history_button = QPushButton(">>")

        total_pages = 1


        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.nav = None
        self.page_display = HumanReadableSpinBox()
        self.label = QLabel(f"/{total_pages}")

        self.setWindowTitle("pdf-navigator")

        self.page_display.setValue(0)
        self.page_display.setSingleStep(10)


        forward_button.clicked.connect(self.page_forward)
        back_button.clicked.connect(self.page_back)

        f_history_button.clicked.connect(self.history_forward)
        b_history_button.clicked.connect(self.history_back)


        self.layout.addWidget(b_history_button)
        self.layout.addWidget(back_button)
        self.layout.addWidget(self.page_display)
        self.layout.addWidget(self.label)
        self.layout.addWidget(forward_button)
        self.layout.addWidget(f_history_button)

    @Slot()
    def page_forward(self):
        """Navigate to next page."""
        if self.nav:
            page = self.nav.currentPage()
            location = self.nav.currentLocation()
            next_page = min(page + 1, self.page_display.maximum())
            self.nav.jump(next_page, location)
            self.update_page_display(next_page)

    @Slot()
    def page_back(self):
        """Navigate to previous page."""
        if self.nav:
            page = self.nav.currentPage()
            location = self.nav.currentLocation()
            prev_page = max(page - 1, self.page_display.minimum())
            self.nav.jump(prev_page, location)
            self.update_page_display(prev_page)

    @Slot()
    def history_forward(self):
        """Move forward in navigation history."""
        if self.nav:
            self.nav.forward()
            page = self.nav.currentPage()
            self.update_page_display(page)

    @Slot()
    def history_back(self):
        """Move backward in navigation history."""
        if self.nav:
            self.nav.back()
            page = self.nav.currentPage()
            self.update_page_display(page)

    @Slot()
    def jump_to(self, page_number, point=None):
        """Jump to specific page number."""
        if self.nav:
            location = point if point else self.nav.currentLocation()
            # self.nav.jump(page, point)
            self.nav.jump(page_number, location)
            self.update_page_display(page_number)
        
    @Slot()
    def update_page_display(self, page_number):
        """Update page display widget to show current page."""
        if page_number != self.page_display.value():
            self.page_display.blockSignals(True)
            self.page_display.setValue(page_number)
            self.page_display.blockSignals(False)

    @Slot()
    def update_nav_from_spinbox(self):
        """Update navigation when page number manually entered."""
        if self.nav:
            page = self.page_display.value()
            self.nav.jump(page, QPointF())

    def set_view(self, view):
        """Connect navigator to PDF view."""
        self.nav: QPdfPageNavigator = view.pageNavigator()
        self.nav.currentPageChanged.connect(self.update_page_display)
        self.page_display.editingFinished.connect(self.update_nav_from_spinbox)

    def set_total_pages(self, tot_pages):
        """Set total page count for display."""
        self.page_display.setRange(0, tot_pages -1)
        self.label.setText(f"/{tot_pages}")

    def get_curr_zoom(self):
        """Get current zoom level."""
        if self.nav:
            return (self.nav.currentZoom())

    def get_curr_page(self):
        """Get current page index."""
        if self.nav:
            return (self.nav.currentPage())

    def get_curr_location(self):
        """Get current scroll location on page."""
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

        
