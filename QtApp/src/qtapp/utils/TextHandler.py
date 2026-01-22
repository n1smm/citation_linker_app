import  re
import  pymupdf
from    PySide6.QtCore                  import  QPointF, QPoint, QRect, QSize, QObject, Slot

from    qtapp.utils.qtToPymuUtils       import  rect_py_to_qt, rect_qt_to_py, px_to_dpi, dpi_to_px, point_py_to_qt, point_to_px


class TextHandler(QObject):
    def _del__(self):
        if self.document:
            try:
                self.document.close()
            except Exception:
                pass

    def __init__(self, parent=None):
        super().__init__(parent)


        ### local declarations

        ### member declarations
        self.parent = parent
        self.pdfViewer = None
        self.document = ""
        self.page = 0
        self.selected_text = ""
        self.year_rect = None
        self.year_page = None
        self.translated_rect = pymupdf.Rect()
        self.article_cache = []
        self.delimiters = []
        self.special_cases = []
        self.curr_annots = []
        self.curr_links = []
        self.curr_link_selection = {}

        ### signals


    ### methods

    def set_viewer(self, viewer):
        self.pdfViewer = viewer

    def assign_document(self, doc):
        self.document = pymupdf.open(doc)

    def close_document(self):
        if self.document:
            self.document.close()
        else:
            print("no document open")

    def clear_all_config_info(self):
        self.year_page = None
        self.year_rect = None
        self. article_cache = []
        self.delimiters = []
        self.special_cases = []

    def find_text(self, page_idx, rectF):
        self.page = self.document.load_page(page_idx)
        rect_fitz = rect_qt_to_py(rectF)
        self.selected_text = self.page.get_text("text", clip=rect_fitz)
        # print("delimiters:", self.delimiters)
        # print("fitz rect: ", rect_fitz)
        # print("fitz text: ", self.selected_text)
        # print("delimiters:", self.delimiters)
        # print("special_cases", self.special_cases)

    # TODO add uri links BREAKING
    def get_all_links(self, page_idx, zoom_factor):
        doc = self.document
        page = doc[page_idx]
        self.page = page
        links = []
        self.curr_links = page.get_links()


        for link in self.curr_links:
            qt_rectF = rect_py_to_qt(link["from"])
            qt_rect = dpi_to_px({
                                "rect": qt_rectF,
                                "current_zoom": zoom_factor
                                })
            link_data = {
                "kind": link.get("kind"),
                "from": qt_rect,
                "page": link.get("page"),
                "to": point_to_px(point_py_to_qt(link["to"]), zoom_factor) if "to" in link else None,
                "to_dpi": point_py_to_qt(link["to"]) if "to" in link else qt_rectF.topLeft(),
                "uri": link.get("uri")
            }
            links.append(link_data)
        return links

    def get_all_annotations(self, page_idx, zoom_factor):
        doc = self.document
        self.curr_page_idx = page_idx
        page = doc[page_idx]
        self.page = page
        annotations = []
        self.curr_annots = page.annots()

        # print("\n" + "="*60)
        # print("page annotations")
        # print("="*60)
        for annot in self.curr_annots:
            qt_rectF = rect_py_to_qt(annot.rect)
            qt_rect = dpi_to_px({
                                "rect": qt_rectF,
                                "current_zoom": zoom_factor
                                })
            annot_data = {
                'type': annot.type[1],
                'rect': qt_rect,
                'color': annot.colors.get('stroke', None),
                'opacity': annot.opacity,
                'border': annot.border,
            }

            # For link annotations, extract destination
            if annot.type[0] == pymupdf.PDF_ANNOT_LINK:
                link = annot.link
                if link:
                    annot_data['link_type'] = link['kind']
                    annot_data['page_dest'] = link.get('page', None)
                    annot_data['uri'] = link.get('uri', None)

            annotations.append(annot_data)
            # print(annot_data)


        # print("\n" + "="*60)
        # print("="*60)


        return annotations

    def get_annot_from_idx(self, annot_idx):
        
        for idx, annot in enumerate(self.page.annots()):
            if idx == annot_idx:
                return annot
        return None


    def annot_action(self, annot_idx, action, new_rect=None):
        annot = self.get_annot_from_idx(annot_idx)

        if not annot:
            return

        if action == "delete":
            self.page.delete_annot(annot)
            # annot.delete()
            print(f"Annotation {annot_idx} deleted.")
        elif action == "toggle_type":
            if annot.type[1] == "Underline":
                annot.set_info(type=pymupdf.PDF_ANNOT_HIGHLIGHT)
                print(f"Annotation {annot_idx} changed to Highlight.")
            elif annot.type[1] == "Highlight":
                annot.set_info(type=pymupdf.PDF_ANNOT_UNDERLINE)
                print(f"Annotation {annot_idx} changed to Underline.")
            else:
                print("Annotation type is not Underline or Highlight.")
        elif action == "update_rect" and new_rect is not None:
            annot.set_rect(new_rect)
            print(f"Annotation {annot_idx} rect updated.")
        else:
            print("Invalid action or missing new_rect.")


    def link_action(self, link_idx, action, new_dest=None):
        link = self.curr_links[link_idx]

        if not link:
            return

        if action == "delete":
            self.page.delete_link(link)
        elif action == "change":
            link["to"] = new_dest
            self.page.update_link(link)


    def link_creation(self, selection):
        if not selection:
            print("nothing selected")
            return

        rect = rect_qt_to_py(selection)
        text = self.page.get_text("text", clip=rect)
        link_data = {
            "kind": pymupdf.LINK_GOTO,
            "from": rect,
            "page": 0,
            "to": None,
            "link_page": self.page
        }
        self.curr_link_selection = link_data
        # print(f"[link_creation] curr_link_selection set: {list(self.curr_link_selection.keys())}")
        year_rect = self.extract_year_rect(self.page, pymupdf.Rect(rect))
        # print(f"[link_creation] year_rect found: {year_rect is not None}")
        if year_rect:
            self.year_rect = year_rect
            self.year_page = self.page.number


    def link_destination(self, selection, page_idx, zoom_factor=None):
        if not selection:
            print("nothing selected")
            return

        # print(f"[link_destination] curr_link_selection keys before: {list(self.curr_link_selection.keys())}")
        rect = rect_qt_to_py(selection)
        point = rect.top_left
        page = self.curr_link_selection["link_page"]
        # print(f"[link_destination] link_page type: {type(page)}, number: {page.number if hasattr(page, 'number') else 'N/A'}")
        del self.curr_link_selection["link_page"]
        
        # Convert the original "from" rect to pixels for display
        from_rect = rect_py_to_qt(self.curr_link_selection["from"])
        qt_rect = dpi_to_px({
                            "rect": from_rect,
                            "current_zoom": zoom_factor
                            })

        self.curr_link_selection["to"] = point
        self.curr_link_selection["page"] = page_idx

        link = self.curr_link_selection
        link_data = {
                "kind": link.get("kind"),
                "from": qt_rect,
                "page": link.get("page"),
                "to": point_to_px(point_py_to_qt(link["to"]), zoom_factor) if "to" in link else None,
                "to_dpi": point_py_to_qt(link["to"]) if "to" in link else from_rect.topLeft(),
                "uri": link.get("uri")
            }

        # print(f"[link_destination] About to insert link: {self.curr_link_selection}")
        result = page.insert_link(self.curr_link_selection)
        # print(f"[link_destination] insert_link result: {result}, links on page: {len(page.get_links())}")

        self.curr_links.append(link_data)
        self.curr_link_selection.clear()
        if self.year_rect:
            # print(f"[link_destination] Adding year annotation on page {self.year_page.number if hasattr(self.year_page, 'number') else 'N/A'}")
            year_page_fresh = self.document[self.year_page]
            annot = year_page_fresh.add_underline_annot([self.year_rect])
            # Don't call update() immediately - let it update naturally
            # annot.update()
            # print(f"[link_destination] Annotation added (without explicit update)")

    def extract_year_annot(self, word, word_rect, rect):
        match = re.search(r"\d{4}[a-zA-Z]?", word)
        word_len = len(word)
        if  not match:
            return None
        
        start_percent = (match.start() / word_len) * 100
        end_percent = ((word_len - match.end()) / word_len) * 100

        # approximately estimate (in percentage)
        #from where to where the rect for the year should be
        width = word_rect.x1 - word_rect.x0
        new_x0 = word_rect.x0 + width * (start_percent / 100)
        new_x1 = word_rect.x1 - width * (end_percent / 100)
        new_rect = pymupdf.Rect(new_x0, word_rect.y0, new_x1, word_rect.y1)
        return new_rect

    def extract_year_rect(self, page, origin_rect):
        words = page.get_text("words")
        for word in words:
            word_rect = pymupdf.Rect(word[0], word[1], word[2], word[3])
            if word_rect.intersects(origin_rect):# and re.match(r"\d{4}[a-zA-Z]?", word[4]):
                year_rect = self.extract_year_annot(word[4], word_rect, origin_rect)
                if year_rect:
                    return year_rect
        return None


    @Slot()
    def get_config_data(self):
        return {
                "article_cache": self.article_cache,
                "special_cases": self.special_cases,
                "delimiters" : self.delimiters
                }

