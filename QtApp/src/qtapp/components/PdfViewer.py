from    PySide6.QtCore                  import  Qt, QFile, Slot, Signal
from    PySide6.QtWidgets               import  (QWidget,
                                                QPushButton,
                                                QHBoxLayout,
                                                QRubberBand,
                                                QVBoxLayout)
#qt pdf imports
from    PySide6.QtPdf                   import  QPdfDocument
from    PySide6.QtPdfWidgets            import  QPdfView

#local
from    qtapp.viewerUtils.Navigator     import PdfNavigator
from    qtapp.viewerUtils.ZoomSelector  import ZoomSelector
from    qtapp.viewerUtils.TextSelector  import TextSelector
from    qtapp.viewerUtils.ExtendedView  import ExtendedView


class PdfViewer(QWidget):
    article_changed = Signal(dict, bool)

    def __init__(self, parent=None, textHandler=None, isAlt=False):
        super().__init__(parent)
        print("initing pdf viewer")


        ### member declarations/ custom components
        self.parent = parent
        self.layout = QVBoxLayout() #main layout
        self.horizontal_bar = QHBoxLayout()
        self.setLayout(self.layout)

        self.navigator = PdfNavigator(self)
        self.zoom_selector = ZoomSelector(self)
        self.text_selector = TextSelector(self)
        self.text_handler = textHandler
        self.view = ExtendedView(self,
                                 textHandler,
                                 self.text_selector,
                                 self.navigator,
                                 self.zoom_selector
                                 ) # most logic is here
        
        
        self.document = QPdfDocument(self)
        self.config_article_cache = self.parent.document_config.article_cache
        self.current_article = None
        print("config_cache: ", self.config_article_cache)
        self.zoom_factor = 1.0
        self.is_alt = isAlt


        ### options
        self.setWindowTitle("Viewer")
        self.view.setDocument(self.document)
        self.view.setPageMode(QPdfView.SinglePage)
        self.view.hide()
        self.view.set_selection_enabled(False)
        self.text_selector.rubberBand =  QRubberBand(QRubberBand.Rectangle, self.view)
        self.zoom_selector.setMaximumWidth(400)

        ### signals
        self.zoom_selector.zoom_mode_changed.connect(self.change_zoom_mode)
        self.zoom_selector.zoom_factor_changed.connect(self.change_zoom_factor)

        ### element appending
        self.horizontal_bar.addWidget(self.navigator)
        self.horizontal_bar.addWidget(self.zoom_selector)


        self.layout.addLayout(self.horizontal_bar)
        # self.layout.addWidget(self.navigator)
        self.layout.addWidget(self.view)

    ### methods
    def open_viewer(self, file_path):
        if file_path:
            self.file_path = file_path
            self.text_handler.assign_document(file_path)
            self.document.load(self.file_path)
            self.navigator.set_total_pages(self.document.pageCount())
            self.navigator.set_view(self.view)
            self.navigator.show()
            self.zoom_selector.show()
            self.zoom_selector.reset()
            self.view.set_selection_enabled(True)
            self.view.show()
            self.config_article_cache = self.parent.document_config.article_cache
            print("config_cache: ", self.config_article_cache)
            #signal
            self.navigator.nav.currentPageChanged.connect(self.on_page_change)

    @Slot()
    def on_page_change(self, page_idx):
        self.config_article_cache = self.parent.document_config.article_cache
        for article in self.config_article_cache:
            if article["first"] <= page_idx <= article["last"]:
                if self.current_article != article:
                    self.current_article = article
                    self.article_changed.emit(article, self.is_alt)
        else:
            self.current_article = None

        # page = self.document.getAllText(page_idx)
        # print(f" page: {page_idx}, has rect: {page.boundingRectangle()}")

    @Slot()
    def on_article_changed(self, article, is_alt):
        if is_alt or not self.is_alt:
            return

        last_page = article["last"]        
        self.navigator.jump_to(last_page)


    @Slot()
    def change_zoom_mode(self, mode):
        self.view.setZoomMode(mode)

    @Slot()
    def change_zoom_factor(self, factor):
        self.zoom_factor = factor
        self.view.setZoomFactor(factor)





