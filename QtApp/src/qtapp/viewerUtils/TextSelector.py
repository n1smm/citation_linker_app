from    PySide6.QtCore                  import  Qt, QPointF, QPoint, QRect, QRectF, QSize, QSizeF, Slot, Signal, QObject
from    PySide6.QtPdfWidgets            import  QPdfView
from    PySide6.QtPdf                   import  QPdfDocument, QPdfPageNavigator, QPdfSelection
from    PySide6.QtGui                   import  QKeyEvent, QMouseEvent
from    PySide6.QtWidgets               import  QRubberBand

from    pymupdf                         import Rect
from    qtapp.utils.qtToPymuUtils       import px_to_dpi


class TextSelector(QObject):

    rect_changed = Signal(QRect)
    rectf_changed = Signal(QRectF)

    def __init__(self, parent=None):
        super().__init__(parent) 
        ### member declarations
        self.parent = parent
        print("selector: ", parent)
        self.selecting = False
        self.origin = QPoint()
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, parent)
        self.current_page = 0
        self.current_zoom_factor = 1.0
        self.current_zoom_custom = 1.0
        self.current_zoom_mode = QPdfView.ZoomMode.Custom
        self.current_viewport = QSize(0,0)
        self.current_document_size = QSizeF(0, 0)
        self.current_margins = 10.0
        self.current_rect = QRect()
        self.current_rectF = QRectF()
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
        # print("\n" + "="*60)
        # print("(normalize_pixel_to_page):")
        # print("="*60)
        # print(f"GEOMETRY - size: {geometry.size()}, x: {geometry.x()}, y: {geometry.y()}")
        # print(f"GEOMETRY - width: {geometry.width()}, height: {geometry.height()}")
        # print("curr page: ", self.current_page)
        # print("curr page size: ", self.current_document_size)
        # print("curr zoom factor", self.current_zoom_factor)
        # print("h offset: ", self.h_offset, ", w offset: ", self.w_offset)
        self.rect_changed.emit(geometry)
        rect = self.normalize_pixel_to_page(geometry)

        # print(f"OLD Result - size: {rect.size()}, x: {rect.x()}, y: {rect.y()}")
        # print(f"OLD Result - width: {rect.width()}, height: {rect.height()}")
        
        page_rect = px_to_dpi({
            "rect": rect,
            "current_zoom": self.current_zoom_factor,
            })

        # print(f"NEW Result - size: {page_rect.size()}, x: {page_rect.x()}, y: {page_rect.y()}")
        # print(f"NEW Result - width: {page_rect.width()}, height: {page_rect.height()}")

        self.current_rect = rect
        self.current_rectF = page_rect
        self.rectf_changed.emit(page_rect)

        new_viewport_rect = self.page_to_viewport_coords(rect)
        # print(f"VIEWPORT Result - size: {new_viewport_rect.size()}, x: {new_viewport_rect.x()}, y: {new_viewport_rect.y()}")
        # print(f"VIEWPORT Result - width: {new_viewport_rect.width()}, height: {new_viewport_rect.height()}")
        return page_rect

    @Slot()
    def handleMousePress(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()
            # print(self.parent.pageAt(self.origin))
            self.selecting = True

    @Slot()
    def handleMouseMove(self, event):
        if self.selecting:
            rect = QRect(self.origin, event.pos()).normalized()
            self.rubberBand.setGeometry(rect)

    @Slot()
    def handleMouseRelease(self, event):
        if self.selecting:
            handler = self.parent.text_handler
            self.selecting = False
            self.rubberBand.hide()
            geometry = self.rubberBand.geometry()
            if geometry.size().width() > 10 and geometry.size().height() > 10:
                page_rect = self.handle_selection(self.rubberBand.geometry())
                handler.find_text(self.current_page, page_rect)

    
    def normalize_pixel_to_page(self, geometry):
        rect = QRect(geometry)
        viewport_pos = self.parent.view.viewport().pos()
        viewport_x = float(rect.x()) - float(viewport_pos.x())
        viewport_y = float(rect.y()) - float(viewport_pos.y())

        doc_width = (self.current_document_size.width()
                        * self.current_zoom_factor)
        doc_height = (self.current_document_size.height()
                        * self.current_zoom_factor)
        view_width = float(self.current_viewport.width())
        view_height = float(self.current_viewport.height())

        if doc_width >= view_width:
            margin_w = self.current_margins
        else: 
            margin_w = (view_width - doc_width) / 2.0 - 1.0

        margin_h = (view_height - doc_height) / 2.0 - 1.0

        total_y = (self.h_offset + viewport_y) - self.current_margins
        page_unit_h = doc_height + float(self.current_margins)
        curr_page = int(total_y // page_unit_h)
        scroll_pos_y = total_y % page_unit_h

        total_x = (self.w_offset + viewport_x) - margin_w
        page_unit_w = doc_width + float(self.current_margins)
        scroll_pos_x = total_x % page_unit_w


        normalize_x = scroll_pos_x
        normalize_y = scroll_pos_y
        size = rect.size()

        page_point_x = normalize_x / self.current_zoom_factor
        page_point_y = normalize_y / self.current_zoom_factor


        # print("scroll pos: ", scroll_pos_y, "page calc: ", curr_page)
        # print("doc dpi h: ", self.current_document_size.height(),
        #       "doc dpi w: ", self.current_document_size.width())
        # print("dpi x:", page_point_x, " dpi y:", page_point_y)

        # print("doc w px: ", doc_width, "view w px: ", view_width)
        # print("doc h px: ", doc_height, "view h px: ", view_height)
        # print("margin w: ", margin_w, "prev_x: ", rect.x(), "normalized_x: ", normalize_x)
        # print("margin h: ", margin_h, "prev_y: ", rect.y(), "normalized_y: ", normalize_y)
        rect.setX(int(round(normalize_x)))
        rect.setY(int(round(normalize_y)))
        rect.setSize(size)
        return rect

    def page_to_viewport_coords(self, page_rect):
        page_x = page_rect.x()
        page_y = page_rect.y()

        doc_width = self.current_document_size.width() * self.current_zoom_factor
        doc_height = self.current_document_size.height() * self.current_zoom_factor
        view_width = float(self.current_viewport.width())
        view_height = float(self.current_viewport.height())

        if doc_width > view_width:
            margin_w = self.current_margins
        else:
            margin_w = (view_width - doc_width) / 2.0 - 1.0

        scroll_pos_x = page_x
        scroll_pos_y = page_y

        total_x = scroll_pos_x + margin_w - self.w_offset
        total_y = scroll_pos_y + self.current_margins - self.h_offset

        viewport_pos = self.parent.view.viewport().pos()
        viewport_x = total_x + viewport_pos.x()
        viewport_y = total_y + viewport_pos.y()
        size = page_rect.size()
        rect = QRect()

        rect.setX(int(round(viewport_x)))
        rect.setY(int(round(viewport_y)))
        rect.setSize(size)
        return rect

