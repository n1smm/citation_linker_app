from    PySide6.QtCore                  import  Qt, QPointF, QPoint, QRect, QSize
from    PySide6.QtPdfWidgets            import  QPdfView
from    PySide6.QtPdf                   import  QPdfDocument, QPdfPageNavigator
from    PySide6.QtGui                   import  QKeyEvent, QMouseEvent
from    PySide6.QtWidgets               import  QRubberBand



class TextSelector:
    def __init__(self, parent=None):
        
        ### member declarations
        self.parent = parent
        self.selecting = False
        self.origin = QPoint()
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, parent)


    ### methods

    def handle_selection(self, event):
        print("handling selection event:", event)


    def handleMousePress(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()
            self.selecting = True

    def handleMouseMove(self, event):
        if self.selecting:
            rect = QRect(self.origin, event.pos()).normalized()
            self.rubberBand.setGeometry(rect)

    def handleMouseRelease(self, event):
        if self.selecting:
            self.selecting = False
            self.rubberBand.hide()
            self.handle_selection(self.rubberBand.geometry())
            print("selection: ", self.rubberBand.geometry())



