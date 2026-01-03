from    PySide6.QtCore                  import  Qt, QPointF, QPoint, QRect, QRectF, QSize, QSizeF, Slot, Signal, QObject
from    PySide6.QtPdfWidgets            import  QPdfView
from    PySide6.QtPdf                   import  QPdfDocument, QPdfPageNavigator, QPdfSelection
from    PySide6.QtGui                   import  QKeyEvent, QMouseEvent
from    PySide6.QtWidgets               import  QRubberBand

from    pymupdf                         import Rect
from    qtapp.qtToPymuUtils             import px_to_dpi


class TextSelector(QObject):

    rect_changed = Signal(QRect)
    rectf_changed = Signal(QRectF)

    def __init__(self, parent=None):
        super().__init__(parent) 
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
        print("\n" + "="*60)
        print("(normalize_pixel_to_page):")
        print("="*60)
        print("curr page: ", self.current_page)
        print("curr page size: ", self.current_document_size)
        print("curr zoom factor", self.current_zoom_factor)
        print("h offset: ", self.h_offset, ", w offset: ", self.w_offset)
        self.rect_changed.emit(geometry)
        rect = self.normalize_pixel_to_page(geometry)

        print(f"OLD Result - size: {rect.size()}, x: {rect.x()}, y: {rect.y()}")
        print(f"OLD Result - width: {rect.width()}, height: {rect.height()}")
        
        page_rect = px_to_dpi({
            "rect": rect,
            "current_zoom": self.current_zoom_factor,
            })

        print(f"NEW Result - size: {page_rect.size()}, x: {page_rect.x()}, y: {page_rect.y()}")
        print(f"NEW Result - width: {page_rect.width()}, height: {page_rect.height()}")

        self.current_rect = rect
        self.current_rectF = page_rect
        self.rectf_changed.emit(page_rect)

        new_viewport_rect = self.page_to_viewport_coords(rect)
        print(f"VIEWPORT Result - size: {new_viewport_rect.size()}, x: {new_viewport_rect.x()}, y: {new_viewport_rect.y()}")
        print(f"VIEWPORT Result - width: {new_viewport_rect.width()}, height: {new_viewport_rect.height()}")
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
            page_rect = self.handle_selection(self.rubberBand.geometry())
            handler.find_text(self.current_page, page_rect)

    
    def normalize_pixel_to_page(self, geometry):
        rect = QRect(geometry)
        viewport_pos = self.parent.viewport().pos()
        viewport_x = float(rect.x()) - float(viewport_pos.x())
        viewport_y = float(rect.y()) - float(viewport_pos.y())

        doc_width = (self.current_document_size.width()
                        * self.current_zoom_factor)
        doc_height = (self.current_document_size.height()
                        * self.current_zoom_factor)
        view_width = float(self.current_viewport.width())
        view_height = float(self.current_viewport.height())

        if doc_width > view_width:
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
        print("doc dpi h: ", self.current_document_size.height(),
              "doc dpi w: ", self.current_document_size.width())
        # print("dpi x:", page_point_x, " dpi y:", page_point_y)

        print("doc w px: ", doc_width, "view w px: ", view_width)
        print("doc h px: ", doc_height, "view h px: ", view_height)
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

        # margin_h is not used in the original function for x/y
        # To get scroll positions, just use the page_x/page_y as normalized_x/y
        scroll_pos_x = page_x
        scroll_pos_y = page_y

        total_x = scroll_pos_x + margin_w - self.w_offset
        total_y = scroll_pos_y + self.current_margins - self.h_offset

        viewport_pos = self.parent.viewport().pos()
        viewport_x = total_x + viewport_pos.x()
        viewport_y = total_y + viewport_pos.y()
        size = page_rect.size()
        rect = QRect()

        rect.setX(int(round(viewport_x)))
        rect.setY(int(round(viewport_y)))
        rect.setSize(size)
        return rect

    # def get_text_selection(self, page_rect):
    #     document = self.parent.document()
    #     page_idx = self.parent.navigator.get_curr_page()
    #     selection = document.getSelection(page_idx, page_rect.topLeft(), page_rect.bottomRight())
    #     print("selection:", selection, "bounding rect:", selection.boundingRectangle())

        

    # def viewport_rect_to_pdf_points(self, geometry):
    #     """
    #     Convert viewport rectangle (pixels) to page-relative rectangle (PDF points).
    #     Returns tuple: (page_number, QRectF in PDF coordinate system)

    #     This properly converts:
    #     1. Viewport pixels → Page pixels (removes margins/offsets)
    #     2. Page pixels → PDF points (divides by zoom)
    #     3. Qt Y-axis → PDF Y-axis (flips from top-left to bottom-left origin)
    #     """
    #     rect = QRect(geometry)
    #     viewport_pos = self.parent.viewport().pos()

    #     # Step 1: Convert widget coordinates to viewport coordinates
    #     viewport_x = float(rect.x()) - float(viewport_pos.x())
    #     viewport_y = float(rect.y()) - float(viewport_pos.y())

    #     # Document dimensions in pixels (at current zoom)
    #     doc_width_pixels = self.current_document_size.width() * self.current_zoom_factor
    #     doc_height_pixels = self.current_document_size.height() * self.current_zoom_factor

    #     # Viewport dimensions
    #     view_width = float(self.current_viewport.width())

    #     # Calculate centering margins (when doc is smaller than viewport)
    #     margin_w = (view_width - doc_width_pixels) / 2.0

    #     # Step 2: Convert to page-relative pixels (remove horizontal margin)
    #     page_pixel_x = viewport_x - margin_w

    #     # Step 3: Calculate which page we're on
    #     page_spacing = float(self.parent.pageSpacing())  # Get actual spacing from parent
    #     page_unit = doc_height_pixels + page_spacing  # Total height per page including spacing

    #     total_y_pixels = (self.h_offset + viewport_y) - self.current_margins
    #     curr_page = int(total_y_pixels // page_unit)
    #     scroll_pos_pixels = total_y_pixels % page_unit

    #     # Make Y coordinate relative to current page (not document)
    #     page_relative_y_pixels = scroll_pos_pixels

    #     print(f"=== viewport_rect_to_pdf_points Debug ===")
    #     print(f"Input rect: x={rect.x()}, y={rect.y()}, w={rect.width()}, h={rect.height()}")
    #     print(f"Viewport Y: {viewport_y:.2f}, H-offset: {self.h_offset:.2f}")
    #     print(f"Total Y (pixels): {total_y_pixels:.2f}")
    #     print(f"Page unit: {page_unit:.2f} (doc_height: {doc_height_pixels:.2f} + spacing: {page_spacing:.2f})")
    #     print(f"Calculated page: {curr_page}")
    #     print(f"Scroll pos (pixels within page): {scroll_pos_pixels:.2f}")

    #     # Step 4: Convert from pixels to PDF points
    #     page_point_x = page_pixel_x / self.current_zoom_factor
    #     page_point_y = page_relative_y_pixels / self.current_zoom_factor
    #     page_point_width = float(rect.width()) / self.current_zoom_factor
    #     page_point_height = float(rect.height()) / self.current_zoom_factor

    #     print(f"Page-relative (pixels): X={page_pixel_x:.2f}, Y={page_relative_y_pixels:.2f}")
    #     print(f"Page-relative (points): X={page_point_x:.2f}, Y={page_point_y:.2f}")

    #     # Step 5: Flip Y-axis (Qt: top-left origin → PDF: bottom-left origin)
    #     page_height_points = self.current_document_size.height()
    #     pdf_y = page_height_points - page_point_y - page_point_height

    #     print(f"After Y-flip (PDF coords): X={page_point_x:.2f}, Y={pdf_y:.2f}")
    #     print(f"Page height (points): {page_height_points:.2f}")
    #     print(f"Zoom factor: {self.current_zoom_factor:.6f}")
    #     print("=========================================\n")

    #     # Create QRectF with PDF coordinates (float precision)
    #     pdf_rect = QRectF(page_point_x, pdf_y, page_point_width, page_point_height)

    #     return (curr_page, pdf_rect)

    # def get_text_selection_qt(self, geometry):
    #     """
    #     Get text selection using Qt's native QPdfDocument.getSelection().
    #     Uses proper coordinate transformation to PDF points.

    #     Returns: (page_number, selected_text, QPdfSelection object) or None
    #     """
    #     # Convert viewport rectangle to PDF coordinates
    #     page_num, pdf_rect = self.viewport_rect_to_pdf_points(geometry)

    #     # Get the document
    #     document = self.parent.document()

    #     if document is None:
    #         print("Error: No document loaded")
    #         return None

    #     # Create selection using Qt's method
    #     # getSelection expects start and end points in PDF coordinate system
    #     start_point = QPointF(pdf_rect.left(), pdf_rect.top())
    #     end_point = QPointF(pdf_rect.right(), pdf_rect.bottom())

    #     print(f"Getting selection on page {page_num}")
    #     print(f"Start point: ({start_point.x():.2f}, {start_point.y():.2f})")
    #     print(f"End point: ({end_point.x():.2f}, {end_point.y():.2f})")

    #     selection = document.getSelection(page_num, start_point, end_point)

    #     if selection.isValid():
    #         text = selection.text()
    #         print(f"✓ Valid selection found!")
    #         print(f"  Text: '{text}'")
    #         print(f"  Start index: {selection.startIndex()}")
    #         print(f"  End index: {selection.endIndex()}")
    #         print(f"  Bounding rect: {selection.boundingRectangle()}")
    #         return (page_num, text, selection)
    #     else:
    #         print("✗ No valid text selection in this region")
    #         return None



