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
        self.translated_rect = pymupdf.Rect()
        self.article_cache = []
        self.delimiters = []
        self.special_cases = []
        self.curr_annots = []
        self.curr_links = []

        ### signals


    ### methods
    def set_viewer(self, viewer):
        self.pdfViewer = viewer

    def assign_document(self, doc):
        self.document = pymupdf.open(doc)

    def close_document(self):
        self.document.close()


    def find_text(self, page_idx, rectF):
        self.page = self.document.load_page(page_idx)
        rect_fitz = rect_qt_to_py(rectF)
        self.selected_text = self.page.get_text("text", clip=rect_fitz)
        print("delimiters:", self.delimiters)
        print("fitz rect: ", rect_fitz)
        print("fitz text: ", self.selected_text)
        print("delimiters:", self.delimiters)
        print("special_cases", self.special_cases)

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

    @Slot()
    def get_config_data(self):
        return {
                "article_cache": self.article_cache,
                "special_cases": self.special_cases,
                "delimiters" : self.delimiters
                }

