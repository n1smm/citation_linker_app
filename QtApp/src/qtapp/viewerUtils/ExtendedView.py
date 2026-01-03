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
        window = self.window()
        print("window screen:" ,window.screen())
        dpi = screen.logicalDotsPerInch()
        physical_dpi = screen.physicalDotsPerInch()

        ### member declarations
        self.zoom_transform_factor = dpi / 72.0
        print("dpi: ", dpi, "transform_factor: ", self.zoom_transform_factor)
        print("physical dpi: ", physical_dpi)

        ### extended functionality
        self.text_selector = TextSelector(self)
        self.navigator = PdfNavigator(self)
        self.zoom_selector = ZoomSelector(self)
        self.setZoomMode(QPdfView.ZoomMode.FitInView)


        ### options
        self.selection_enabled = False
        self.setPageSpacing(0)
        self.setDocumentMargins(QMargins(10,10,10,10))
        # self.setDocumentMargins(QMargins(5,5,5,5))
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
                "w_offset": float(self.horizontalScrollBar().value()),
                "h_offset": float(self.verticalScrollBar().value()),
                "current_margins": float(self.documentMargins().left()),
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

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ShiftModifier:
            super().wheelEvent(event)
            return
        
        if event.modifiers() & Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoom_selector.set_zoom_up_down(is_up=True)
            elif event.angleDelta().y() < 0:
                self.zoom_selector.set_zoom_up_down(is_up=False)
            else:
                super().wheelEvent(event)
            return


        if event.angleDelta().y() > 0:
            self.navigator.page_back()
        elif event.angleDelta().y() < 0:
            self.navigator.page_forward()
        elif event.angleDelta().x() > 0:
            self.navigator.history_back()
        elif event.angleDelta().x() < 0:
            self.navigator.history_forward()

        else:
            super().wheelEvent(event)

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Left:
            self.navigator.page_back()
        elif event.key() == Qt.Key_Right:
            self.navigator.page_forward()
        else:
            super().keyPressEvent(event)

    ### methods
    def set_selection_enabled(self, enabled):
        self.selection_enabled = enabled

        
    def effectiveZoomFactor(self, alternative=False):
        page_size = self.document().pagePointSize(self.navigator.get_curr_page())
        page_th = self.document().pageCount()
        marg = self.documentMargins()
        
        viewport = self.viewport().size()

        zoom_trasfrom_factor = 2.07433264754424 / 1.52
        print("zoom transform factor: ", zoom_trasfrom_factor)
        print("self zoom transform: ", self.zoom_transform_factor)
        zoom_trasfrom_factor = self.zoom_transform_factor
        

        if self.zoomMode() == QPdfView.ZoomMode.Custom:
            return self.zoomFactor() * zoom_trasfrom_factor

        elif self.zoomMode() == QPdfView.ZoomMode.FitToWidth:
            total_width = float(viewport.width()) - float(marg.left()) - float(marg.right())
            return  total_width / page_size.width()
            # return viewport.width() / page_size.width()

        elif self.zoomMode() == QPdfView.ZoomMode.FitInView:
            total_height = float(viewport.height() - float(marg.top()) - float(marg.bottom()))
            total_width = float(viewport.width()) - float(marg.left()) - float(marg.right())
            scale_x = float(viewport.width()) / page_size.width()
            scale_y = float(viewport.height()) / page_size.height()
            if alternative:
                return scale_y
            return min(scale_x, scale_y)

        return self.zoomFactor()
