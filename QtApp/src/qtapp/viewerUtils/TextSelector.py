from    PySide6.QtCore                  import  Qt, QPointF, QPoint, QRect, QSize, QSizeF, Slot
from    PySide6.QtPdfWidgets            import  QPdfView
from    PySide6.QtPdf                   import  QPdfDocument, QPdfPageNavigator
from    PySide6.QtGui                   import  QKeyEvent, QMouseEvent
from    PySide6.QtWidgets               import  QRubberBand

from    pymupdf                         import Rect


class TextSelector:
    def __init__(self, parent=None):
        
        ### member declarations
        self.parent = parent
        self.selecting = False
        self.origin = QPoint()
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, parent)
        self.current_page = 0
        self.current_zoom_factor = 1.0
        self.current_zoom_custom = 1.0
        self.current_zoom_mode = QPdfView.ZoomMode.Custom
        self.current_viewport = QSize(0,0)
        self.current_document_size = QSizeF(0, 0)
        self.current_margins = 10
        self.h_offset = 0
        self.w_offset = 0


    ### methods
    def set_curr_state(self, stateObj):
        self.current_page = stateObj["current_page"]
        self.current_zoom_mode = stateObj["current_zoom_mode"]
        self.current_zoom_factor = stateObj["current_zoom_factor"] 
        self.current_zoom_custom = stateObj["current_zoom_custom"]
        self.current_document_size = stateObj["current_document_size"] 
        self.current_margins = stateObj["current_margins"]
        self.current_viewport = stateObj["current_viewport"]
        self.w_offset = stateObj["w_offset"]
        self.h_offset = stateObj["h_offset"]

    def handle_selection(self, geometry):
        print("curr page: ", self.current_page)
        print("curr page size: ", self.current_document_size)
        print("curr zoom factor", self.current_zoom_factor)
        print("h offset: ", self.h_offset, ", w offset: ", self.w_offset)
        rect = self.normalize_pixel_to_page(geometry)

        print(f"size: {rect.size()}, x: {rect.x()}, y: {rect.y()}")
        print(f"width: {rect.width()}, height: {rect.height()}")


    @Slot()
    def handleMousePress(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()
            self.selecting = True

    @Slot()
    def handleMouseMove(self, event):
        if self.selecting:
            rect = QRect(self.origin, event.pos()).normalized()
            self.rubberBand.setGeometry(rect)

    @Slot()
    def handleMouseRelease(self, event):
        if self.selecting:
            self.selecting = False
            self.rubberBand.hide()
            self.handle_selection(self.rubberBand.geometry())

    
    def normalize_pixel_to_page(self, geometry):
        rect = QRect(geometry)
        viewport_pos = self.parent.viewport().pos()
        viewport_x = rect.x() - viewport_pos.x()
        viewport_y = rect.y() - viewport_pos.y()

        doc_width = (self.current_document_size.width()
                        * self.current_zoom_factor)
        doc_height = (self.current_document_size.height()
                        * self.current_zoom_factor)
        view_width = self.current_viewport.width()# + 20 # + (self.current_margins * 2)
        view_height = self.current_viewport.height()# + (self.current_margins * 2)


        margin_w = (view_width - doc_width) / 2
        margin_h = (view_height - doc_height) / 2
        # if self.current_zoom_mode == QPdfView.ZoomMode.FitToWidth:
        #     margin_w += self.current_margins
            # margin_h += self.current_margins * 2

        
        normalize_x = int(viewport_x - margin_w)
        normalize_y = int(viewport_y - 10 + self.h_offset)
        # normalize_y = int(viewport_y - margin_h + self.h_offset)
        # normalize_x = int(rect.x() - margin_w) #+ (80 * self.current_zoom_factor))

        total_y = (self.h_offset + viewport_y) - self.current_margins
        page_unit = doc_height + 10
        curr_page = int(total_y // page_unit)
        scroll_pos = int(total_y % page_unit) 
        # scroll_pos = int((self.h_offset + viewport_y) % doc_height - (curr_page * self.current_margins)) - self.current_margins
        print("scroll pos: ", scroll_pos, "page calc: ", curr_page)
        normalize_y -= scroll_pos

        print("doc w: ", doc_width, "view w: ", view_width)
        print("doc h: ", doc_height, "view h: ", view_height)
        print("margin w: ", margin_w, "prev_x: ", rect.x(), "normalized_x: ", normalize_x)
        print("margin h: ", margin_h, "prev_y: ", rect.y(), "normalized_y: ", normalize_y)
        rect.setX(normalize_x)
        rect.setY(normalize_y)
        return rect

        

