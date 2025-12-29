from    PySide6.QtPdfWidgets            import  QPdfView
from    PySide6.QtPdf                   import  QPdfPageNavigator
from    PySide6.QtCore                  import  Qt, QMargins
from    PySide6.QtGui                   import  QKeyEvent, QMouseEvent, QGuiApplication

from    qtapp.viewerUtils.TextSelector  import TextSelector
from    qtapp.viewerUtils.Navigator     import PdfNavigator
from    qtapp.viewerUtils.ZoomSelector  import ZoomSelector


# extended QPdfView with extra functionality:
# text selector, navigator and zoom selector
# overridden mouse events
class   ExtendedView(QPdfView):
    def __init__(self, parent=None):
        super().__init__(parent)

        ### local decalarations
        screen = QGuiApplication.primaryScreen()
        dpi = screen.logicalDotsPerInch()

        ### member declarations
        self.zoom_transform_factor = dpi / 72.0

        ### extended functionality
        self.text_selector = TextSelector(self)
        self.navigator = PdfNavigator(self)
        self.zoom_selector = ZoomSelector(self)


        ### options
        self.selection_enabled = False
        self.setPageSpacing(10)
        self.setDocumentMargins(QMargins(10,10,10,10))
        self.navigator.hide()
        self.zoom_selector.hide()


    ### event overrides
    def mousePressEvent(self, event):

        if self.selection_enabled and event.button() == Qt.LeftButton:
            curr_page = self.navigator.get_curr_page()
            if curr_page is None:
                print("Warning: No current page selected.")
                return

            document = self.document()
            try:
                curr_doc_size = document.pagePointSize(curr_page)
            except Exception as e:
                print(f"Error getting page size: {e}")
                curr_doc_size = None

            selector_state = {
                "current_page": curr_page,
                "current_zoom_factor": self.effectiveZoomFactor(),
                "current_zoom_custom": self.zoomFactor(),
                "current_zoom_mode": self.zoomMode(),
                "current_document_size": curr_doc_size,
                "current_viewport": self.viewport().size(),
                "w_offset": self.horizontalScrollBar().value(),
                "h_offset": self.verticalScrollBar().value(),
                "current_margins": self.documentMargins().left(),
            }
            self.text_selector.set_curr_state(selector_state)
            print("viewport: ", selector_state["current_viewport"])
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

    ### methods
    def set_selection_enabled(self, enabled):
        self.selection_enabled = enabled

        
    def effectiveZoomFactor(self):
        page_size = self.document().pagePointSize(self.navigator.get_curr_page())
        page_th = self.document().pageCount()
        
        viewport = self.viewport().size()

        zoom_trasfrom_factor = 2.07433264754424 / 1.52
        print("zoom transform factor: ", zoom_trasfrom_factor)
        print("self zoom transform: ", self.zoom_transform_factor)
        zoom_trasfrom_factor = self.zoom_transform_factor
        

        if self.zoomMode() == QPdfView.ZoomMode.Custom:
            return self.zoomFactor() * zoom_trasfrom_factor

        elif self.zoomMode() == QPdfView.ZoomMode.FitToWidth:
            marg = self.documentMargins()
            total_width = viewport.width() - marg.left() - marg.right()
            return  total_width / page_size.width()
            # return viewport.width() / page_size.width()

        elif self.zoomMode() == QPdfView.ZoomMode.FitInView:
            scale_x = viewport.width() / page_size.width()
            scale_y = viewport.height() / page_size.height()
            return min(scale_x, scale_y)

        return self.zoomFactor()
