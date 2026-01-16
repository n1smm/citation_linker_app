from    PySide6.QtPdfWidgets            import  QPdfView
from    PySide6.QtPdf                   import  QPdfPageNavigator
from    PySide6.QtCore                  import  Qt, QMargins, QRect, QRectF, QTimer, QPoint, Slot
from    PySide6.QtGui                   import  QKeyEvent, QMouseEvent, QGuiApplication, QPainter, QPen, QColor

from    qtapp.viewerUtils.TextSelector  import  TextSelector
from    qtapp.utils.TextHandler         import  TextHandler
from    qtapp.viewerUtils.Navigator     import  PdfNavigator
from    qtapp.viewerUtils.ZoomSelector  import  ZoomSelector
from    qtapp.components.PopupWidget    import  PopupWidget
from    qtapp.utils.qtToPymuUtils       import  dpi_to_px, px_to_dpi

from    functools                       import  partial


# extended QPdfView with extra functionality:
# text selector, text_handler, navigator and zoom selector
# overridden mouse, paint events
class   ExtendedView(QPdfView):
    def __init__(self, 
                 parent=None,
                 textHandler=None,
                 textSelector=None,
                 navigator=None,
                 zoomSelector=None,
                 isOutput=False):

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
        self.prev_selection = None #only used in manual link insertion
        self.first_page = None
        self.last_page = None
        self.current_annotations = None
        self.current_links = None
        self.curr_page_rect = None
        self.curr_annot_idx = 0
        self.curr_annot_type = None
        self.is_output = isOutput
        print("dpi: ", dpi, "transform_factor: ", self.zoom_transform_factor)
        print("physical dpi: ", physical_dpi)

        ### extended functionality
        self.text_selector = textSelector
        self.text_handler = textHandler
        self.navigator = navigator
        self.zoom_selector = zoomSelector
        if self.is_output:
            self.popup = PopupWidget(self, QPoint(0,0), {"add_link", "add_destination"})
        else:
            self.popup = PopupWidget(self, QPoint(0,0), {"bibliography", "special_case"})
        self.setZoomMode(QPdfView.ZoomMode.FitInView)


        ### options
        self.selection_enabled = False
        self.setPageSpacing(0)
        self.setDocumentMargins(QMargins(10,10,10,10))
        self.popup.assign_alt_buttons({"delete", "change"})
        self.popup.switch_buttons_to(alt=False)
        self.navigator.hide()
        self.zoom_selector.hide()

        ### signals
        self.text_selector.rect_changed.connect(self.color_selection)
        if self.is_output:
            self.popup.button_objs["add_link"].clicked.connect(self.handle_link)
            self.popup.button_objs["add_destination"].clicked.connect(self.handle_destination)
        else:
            self.popup.button_objs["bibliography"].clicked.connect(self.handle_bibliography)
            self.popup.button_objs["special_case"].clicked.connect(self.handle_special_case)

        self.popup.alt_buttons["delete"].clicked.connect(partial(self.on_annot_event, "delete"))
        self.popup.alt_buttons["change"].clicked.connect(lambda: (print("change"), self.popup.hide()))


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
                for link in self.current_links:
                    screen_rect = self.text_selector.page_to_viewport_coords(link["from"])
                    if screen_rect.contains(event.pos()):
                        print("INTERSECTIOON LINK Left click")
                        print("to filed", link["to_dpi"])
                        self.navigator.jump_to(link["page"], link["to_dpi"])

        elif event.button() == Qt.RightButton:
            self.clear_selection()
            self.update_text_selector()
            if self.current_links and self.current_annotations:
                for idx, annot in enumerate(self.current_annotations):
                    screen_rect = self.text_selector.page_to_viewport_coords(annot["rect"])
                    if screen_rect.contains(event.pos()):
                        print ("INTERSECTION")
                        popup_pos = self.viewport().mapToGlobal(event.pos())
                        self.popup.show_at(popup_pos, alt=True)
                        self.curr_annot_type = "annot"
                        self.curr_annot_idx = idx
                        event.accept()
                        return
                for idx, link in enumerate(self.current_links):
                    screen_rect = self.text_selector.page_to_viewport_coords(link["from"])
                    if screen_rect.contains(event.pos()):
                        print("INTERSECTION LINK")
                        print("to field", link["to_dpi"])
                        popup_pos = self.viewport().mapToGlobal(event.pos())
                        self.popup.show_at(popup_pos, alt=True)
                        self.curr_annot_idx = idx
                        self.curr_annot_type = "link"
            event.accept()
            return
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.selection_enabled and self.text_selector.selecting:

            self.text_selector.handleMouseMove(event)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            event.accept()
            return

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

    def handle_annots(self, event, annot_idx, type="annot"):
        popup_pos = self.viewport().mapToGlobal(event.pos())
        self.popup.show_at(popup_pos, alt=True)
        self.curr_annot_idx = annot_idx
        if type == "annot":
            self.curr_annot_type = "annot"
        else:
            self.curr_annot_type = "link"

            
    def on_annot_event(self, action):
        if  self.curr_annot_type == "annot":
            print("action:", action)
            new_rect = None
            self.text_handler.annot_action(
                    self.curr_annot_idx,
                    action,
                    new_rect
                    )

            update_rect = (self.text_selector.page_to_viewport_coords
                (self.current_annotations[self.curr_annot_idx]["rect"]))
            
        elif self.curr_annot_type == "link":
            new_dest = None
            self.text_handler.link_action(self.curr_annot_idx, action, new_dest)
            update_rect = (self.text_selector.page_to_viewport_coords
                (self.current_links[self.curr_annot_idx]["from"]))
            update_rect.setHeight(update_rect.height() + 2)
            update_rect.setWidth(update_rect.width() + 2)
            update_rect.setX(update_rect.x() - 1)
            update_rect.setY(update_rect.y() -1)
        self.viewport().update(update_rect)
        self.popup.hide()


    @Slot()
    def handle_bibliography(self):
        curr_text = self.text_handler.selected_text
        self.text_handler.delimiters.append(curr_text.strip())
        self.popup.hide()
        self.clear_selection()
        if self.selection_rect:
            self.viewport().update(self.selection_rect)

    @Slot()
    def handle_special_case(self):
        curr_text = self.text_handler.selected_text
        self.text_handler.special_cases.append(curr_text.strip())
        self.popup.hide()
        self.clear_selection()
        if self.selection_rect:
            self.viewport().update(self.selection_rect)

    @Slot()
    def handle_link(self):
        curr_text = self.text_handler.selected_text
        print("curr_text: ", curr_text)
        rect = self.text_selector.normalize_pixel_to_page(self.selection_rect)
        rect_info = {
                "rect" : rect,
                "current_zoom": self.effectiveZoomFactor()
                }
        dpi_rect = px_to_dpi(rect_info)
        self.text_handler.link_creation(dpi_rect)
        self.prev_selection = QRect(self.selection_rect)
        self.popup.hide()
        self.clear_selection()
        if self.selection_rect:
            self.viewport().update(self.selection_rect)

    @Slot()
    def handle_destination(self):
        curr_text = self.text_handler.selected_text
        print("curr_text: ", curr_text)
        zoom_factor = self.effectiveZoomFactor()
        rect_info = {
                "rect" : self.selection_rect,
                "current_zoom": zoom_factor
                }
        dpi_rect = px_to_dpi(rect_info)
        self.text_handler.link_destination(dpi_rect, self.navigator.get_curr_page(), zoom_factor)
        self.popup.hide()
        self.clear_selection()
        if self.selection_rect:
            self.viewport().update(self.selection_rect)
            self.viewport().update(self.prev_selection)
            self.prev_selection = None

    def clear_selection(self):
        if self.selection_rect:
            self.viewport().update(self.selection_rect)
        self.selection_rect = None
        self.update()
        self.popup.hide()

    def set_selection_enabled(self, enabled):
        self.selection_enabled = enabled


    ### --- paint methods -----

    @Slot()
    def color_selection(self, rect):
        if self.selection_rect:
            self.viewport().update(self.selection_rect)
            # self.update()

        self.selection_rect = rect
        popup_pos = self.viewport().mapToGlobal(rect.bottomLeft())
        # popup_pos = self.viewport().mapToParent(rect.bottomLeft())
        self.popup.switch_buttons_to(alt=False)
        self.popup.show_at(popup_pos)
        if self.selection_rect:
            self.viewport().update(self.selection_rect)
        

   
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
            self.curr_page_rect = recta
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
            if scale_y > scale_x:
                scale_x = float(total_width) / page_size.width()
                scale_y = float(total_height) / page_size.height()
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
