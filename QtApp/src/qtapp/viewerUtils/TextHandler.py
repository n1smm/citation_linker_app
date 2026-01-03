import  pymupdf
from    PySide6.QtCore                  import  QPointF, QPoint, QRect, QSize

from    qtapp.qtToPymuUtils             import  rect_py_to_qt, rect_qt_to_py


class TextHandler:
    def __init__(self, parent=None):


        ### local declarations

        ### member declarations
        self.parent = parent
        self.document = ""
        self.page = 0
        self.selected_text = ""
        self.translated_rect = pymupdf.Rect()



        ### signals


    ### methods

    def assign_document(self, doc):
        self.document = pymupdf.open(doc)

    def close_document(self):
        self.document.close()


    def find_text(self, page_idx, rectF):
        self.page = self.document.load_page(page_idx)
        rect_fitz = rect_qt_to_py(rectF)
        selected_text = self.page.get_text("text", clip=rect_fitz)
        print("fitz rect: ", rect_fitz)
        print("fitz text: ", selected_text)

    def get_all_annotations(self, page_num):
        doc = self.document
        page = doc[page_num]
        annotations = []

        for annot in page.annots():
            annot_data = {
                'type': annot.type[1],  # e.g., 'Underline', 'Highlight', 'Link'
                'rect': annot.rect,  # pymupdf.Rect in PDF coordinates
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

        return annotations
