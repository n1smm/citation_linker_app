import  pymupdf
from    PySide6.QtCore                  import  QPointF, QPoint, QRect, QSize, QObject

from    qtapp.qtToPymuUtils             import  rect_py_to_qt, rect_qt_to_py, px_to_dpi, dpi_to_px, point_py_to_qt, point_to_px


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
        page = doc[page_idx]
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
                'type': annot.type[1],  # e.g., 'Underline', 'Highlight', 'Link'
                'rect': qt_rect,  # pymupdf.Rect in PDF coordinates
                'color': annot.colors.get('stroke', None),
                'opacity': annot.opacity,
                'border': annot.border,
            }

            # For link annotations, extract destination
            if annot.type[0] == pymupdf.PDF_ANNOT_LINK:
                link = annot.link
                if link:
                    annot_data['link_type'] = link['kind']  # LINK_GOTO or LINK_URI
                    annot_data['page_dest'] = link.get('page', None)
                    annot_data['uri'] = link.get('uri', None)

            annotations.append(annot_data)
            # print(annot_data)


        # print("\n" + "="*60)
        # print("="*60)


        return annotations
