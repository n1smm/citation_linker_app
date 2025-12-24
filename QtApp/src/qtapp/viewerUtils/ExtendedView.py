from    PySide6.QtPdfWidgets            import  QPdfView
from    PySide6.QtCore                  import  Qt
from    PySide6.QtGui                   import  QKeyEvent, QMouseEvent

from    qtapp.viewerUtils.TextSelector  import TextSelector


class   ExtendedView(QPdfView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.text_selector = TextSelector(self)
        self.selection_enabled = False


    ### event overrides
    def mousePressEvent(self, event):
        if self.selection_enabled and event.button() == Qt.LeftButton:
            self.text_selector.handleMousePress(event)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.selection_enabled and self.text_selector.selecting:
            self.text_selector.handleMouseMove(event)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.selection_enabled and self.text_selector.selecting:
            self.text_selector.handleMouseRelease(event)
        else:
            super().mouseReleaseEvent(event)

    def set_selection_enabled(self, enabled):
        self.selection_enabled = enabled

