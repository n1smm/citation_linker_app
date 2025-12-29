import  pymupdf
from    PySide6.QtCore                  import  QPointF, QPoint, QRect, QSize


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
