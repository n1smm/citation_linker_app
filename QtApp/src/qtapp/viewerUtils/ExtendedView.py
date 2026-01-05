from    PySide6.QtPdfWidgets            import  QPdfView
from    PySide6.QtPdf                   import  QPdfPageNavigator
from    PySide6.QtCore                  import  Qt, QMargins, QRect, QRectF, QTimer, QPoint
from    PySide6.QtGui                   import  QKeyEvent, QMouseEvent, QGuiApplication, QPainter, QPen, QColor

from    qtapp.viewerUtils.TextSelector  import  TextSelector
from    qtapp.viewerUtils.TextHandler   import  TextHandler
from    qtapp.viewerUtils.Navigator     import  PdfNavigator
from    qtapp.viewerUtils.ZoomSelector  import  ZoomSelector
from    qtapp.components.PopupWidget    import  PopupWidget
from    qtapp.qtToPymuUtils             import  dpi_to_px


# extended QPdfView with extra functionality:
# text selector, text_handler, navigator and zoom selector
# overridden mouse, paint events
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
        self.selection_rect = None
        self.current_annotations = None
        self.current_links = None
        self.first_page = None
        self.last_page = None
        self.curr_page_rect = None
        print("dpi: ", dpi, "transform_factor: ", self.zoom_transform_factor)
        print("physical dpi: ", physical_dpi)

        ### extended functionality
        self.text_selector = TextSelector(self)
        self.text_handler = TextHandler(self)
        self.navigator = PdfNavigator(self)
        self.zoom_selector = ZoomSelector(self)
        self.popup = PopupWidget(self, QPoint(0,0), {"bibliography", "special_case"})
        self.setZoomMode(QPdfView.ZoomMode.FitInView)


        ### options
        self.selection_enabled = False
        self.setPageSpacing(0)
        self.setDocumentMargins(QMargins(10,10,10,10))
        # self.setDocumentMargins(QMargins(5,5,5,5))
        self.navigator.hide()
        self.zoom_selector.hide()

        ### signals
        self.text_selector.rect_changed.connect(self.color_selection)
        self.popup.button_objs["bibliography"].clicked.connect(self.handle_bibliography)
        self.popup.button_objs["special_case"].clicked.connect(self.handle_special_case)

        ### TODO do a signal that will send curr page on change to text_selector



    ### event overrides

    ### ---- paint events ------

    def paintEvent(self, event):
        super().paintEvent(event)
        self.update_text_selector()
        self.paint_annotiations()
        self.paint_pages()
        if self.selection_rect:
            painter = QPainter(self.viewport())
            color = QColor(255, 255, 0, 100)
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawRect(self.selection_rect)
            painter.end()


    ### --- interaction events ----

    def mousePressEvent(self, event):

        if self.selection_enabled and event.button() == Qt.LeftButton:
            self.clear_selection()
            self.update_text_selector()
            self.text_selector.handleMousePress(event)
            if self.current_links and self.current_annotations:
                for annot in self.current_annotations:
                    screen_rect = self.text_selector.page_to_viewport_coords(annot["rect"])
                    if screen_rect.contains(event.pos()):
                        print ("INTERSECTIOON")
                for link in self.current_links:
                    screen_rect = self.text_selector.page_to_viewport_coords(link["from"])
                    if screen_rect.contains(event.pos()):
                        print("INTERSECTIOON LINK")
                        print("to filed", link["to_dpi"])
                        self.navigator.jump_to(link["page"], link["to_dpi"])
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
        self.clear_selection()
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

        self.clear_selection()
        if event.key() == Qt.Key_Left:
            self.navigator.page_back()
        elif event.key() == Qt.Key_Right:
            self.navigator.page_forward()
        elif event.key() == Qt.Key_Space:
            self.select_page()
        else:
            super().keyPressEvent(event)

    ### methods
    def select_page(self):
      curr_page = self.navigator.get_curr_page()

      if self.first_page is None:
          self.first_page = curr_page
          print(f"First page selected: {curr_page}")

      elif curr_page == self.first_page:
          print(f"Clearing selection for page {curr_page}")
          if self.curr_page_rect:
              self.viewport().update(self.curr_page_rect)
          self.first_page = None
          self.last_page = None
          self.curr_page_rect = None

      elif curr_page > self.first_page:
          self.last_page = curr_page
          article_info = {"first": self.first_page, "last": self.last_page}
          print(f"Article saved: pages {self.first_page} to {self.last_page}")
          self.text_handler.article_cache.append(article_info)

          # Clear and reset
          if self.curr_page_rect:
              self.viewport().update(self.curr_page_rect)
          self.first_page = None
          self.last_page = None
          self.curr_page_rect = None

      else:
          print(f"Warning: page {curr_page} is lower than first page {self.first_page}")

      self.viewport().update()


    def handle_bibliography(self):
        curr_text = self.text_handler.selected_text
        self.text_handler.delimiters.append(curr_text.strip())
        self.popup.hide()
        self.clear_selection()
        pass

    def handle_special_case(self):
        curr_text = self.text_handler.selected_text
        self.text_handler.special_cases.append(curr_text.strip())
        self.popup.hide()
        self.clear_selection()
        pass


    ### --- paint methods -----

    def paint_annotiations(self):
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)

        self.current_annotations = None
        curr_page = self.navigator.get_curr_page()
        annotations = self.text_handler.get_all_annotations(curr_page, self.effectiveZoomFactor())
        links = self.text_handler.get_all_links(curr_page, self.effectiveZoomFactor())
        self.current_annotations = annotations
        self.current_links = links

        for annot in annotations:
            screen_rect = self.text_selector.page_to_viewport_coords(annot["rect"])

            if annot["type"] == "Underline":
                self.draw_underline(painter, screen_rect, annot)
            if annot["type"] == "Highlight":
                self.draw_highlight(painter, screen_rect, annot)
            if annot["type"] == "Link":
                self.draw_link(painter, screen_rect)
        for link in links:
            screen_rect = self.text_selector.page_to_viewport_coords(link["from"])
            self.draw_link(painter, screen_rect)

        painter.end()

    def paint_pages(self):
        curr_page = self.navigator.get_curr_page()
        painter = QPainter(self.viewport())
        page_size = self.document().pagePointSize(curr_page)
        zoom = self.effectiveZoomFactor()
        page_rect = QRect(0, 0, int(page_size.width() * zoom), int(page_size.height() * zoom))
        rect = self.text_selector.page_to_viewport_coords(page_rect)
        if curr_page == self.first_page or curr_page == self.last_page:
            self.curr_page_rect = rect
            color = QColor(255, 0, 0, 100)
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawRect(rect)
        for obj in self.text_handler.article_cache:
            for value in obj.values():
                if curr_page == value:
                    color = QColor(0, 255, 0, 100)
                    painter.setBrush(color)
                    painter.drawRect(rect)
        painter.end()


    def draw_underline(self, painter, rect, annot):
        color = QColor(*annot.get("color", [0,0,225]))
        pen = QPen(color, 1)
        pen.setStyle(Qt.SolidLine)
        painter.setPen(pen)

        painter.drawLine(
                rect.bottomLeft(),
                rect.bottomRight()
                )

    def draw_highlight(self, painter, rect, annot):
        color = QColor(*annot.get("color", [255,255,0]))
        color.setAlpha(int(annot.get("opacity", 0.3) * 255))
        painter.fillRect(rect, color)

    def draw_link(self, painter, rect):
        pen = QPen(QColor(0, 0, 255, 100), 1)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        painter.drawRect(rect)

    def color_selection(self, rect):
        if self.selection_rect:
            self.viewport().update(self.selection_rect)
            # self.update()

        self.selection_rect = rect
        popup_pos = self.viewport().mapToGlobal(rect.bottomLeft())
        # popup_pos = self.viewport().mapToParent(rect.bottomLeft())
        self.popup.show_at(popup_pos)
        

    def clear_selection(self):
        if self.selection_rect:
            self.viewport().update(self.selection_rect)
        self.selection_rect = None
        self.update()
        self.popup.hide()

    def set_selection_enabled(self, enabled):
        self.selection_enabled = enabled

        
    ### --- zoom factor translation ---
    def effectiveZoomFactor(self, alternative=False):
        page_size = self.document().pagePointSize(self.navigator.get_curr_page())
        page_th = self.document().pageCount()
        marg = self.documentMargins()
        
        viewport = self.viewport().size()

        zoom_trasfrom_factor = 2.07433264754424 / 1.52
        # print("zoom transform factor: ", zoom_trasfrom_factor)
        # print("self zoom transform: ", self.zoom_transform_factor)
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

    ### --- other utils ---
    def update_text_selector(self):
        curr_page = self.navigator.get_curr_page()
        if curr_page == None:
            return
        try:
            curr_doc_size = self.document().pagePointSize(curr_page)
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
