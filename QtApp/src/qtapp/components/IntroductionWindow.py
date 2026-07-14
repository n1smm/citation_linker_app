"""
    component for displaying instruction on how to use the app.
    short introduction,
    explanations of the UI,
    parser - what it can and can't parse, how the parser works , ...
    licence and financial support
"""
import  os
import  sys
import  json
from    importlib.resources import  files
from    PySide6.QtCore      import  Qt
from    PySide6.QtGui       import  QFontDatabase, QPixmap
from    PySide6.QtWidgets   import  (QApplication,
                                                QHBoxLayout,
                                                QLabel,
                                                QPushButton,
                                                QScrollArea,
                                                QTabBar,
                                                QTabWidget,
                                                QToolButton,
                                                QVBoxLayout,
                                                QWidget)
def load_pixmap(filename):
    try:
        path = files('qtapp').joinpath(filename)
        pixmap = QPixmap()
        pixmap.loadFromData(path.read_bytes())
        if not pixmap.isNull():
            return pixmap
    except Exception:
        pass
    return None


class HelpTab(QWidget):
    """ 
        container for helptabs, which can contain
        titles, text and images

        item_positions struct:
            type = TITLE/TEXT/IMG
            data = Qlabel with data or image
            position = in which position it needs to be displayed on the layout

        parent: IntroductionWindow
    """


    def __init__(self, parent=None):
        super().__init__(parent)

        self._parent = parent

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._content = QWidget()
        self._content.setObjectName("helpContent")
        self.layout = QVBoxLayout(self._content)

        self._scroll.setWidget(self._content)
        outer_layout.addWidget(self._scroll)

        self.item_positions = []

    def insert_tab_content(self, data_list):
        """ 
            creates the full tab with all the data and initializes the layout
            passing in the list of all the data. it calls items_factory and then build_layout
        """
        for item in data_list:
            self.items_factory(item["data"], item["position"], item["type"])
        self.build_layout()

    def items_factory(self, data, position, item_type="TEXT"):
        """ 
            create the item based on its item_type and assign it position in the layout
            - top to bottom; types = TITLE, TEXT, IMG
            struct:
            type = TITLE/TEXT/IMG
            data = Qlabel with data or image
            position = in which position it needs to be displayed on the layout
        """
        
        if item_type == "TITLE":
            label = QLabel(data)
            label.setWordWrap(True)
            label.setObjectName("helpTitle")
            self.item_positions.append({
                                       "type": "TITLE",
                                       "data": label,
                                       "position": position
                                       })
        elif item_type == "TEXT":
            label = QLabel(data)
            label.setWordWrap(True)
            label.setObjectName("helpText")
            self.item_positions.append({
                                       "type": "TEXT",
                                       "data": label,
                                       "position": position
                                       })
        elif item_type == "IMG":
            image = QLabel()
            pixmap = load_pixmap(data)
            if pixmap:
                image.setPixmap(pixmap)
            else:
                image.setText(f"[Image not found: {data}]")
                image.setStyleSheet("color: gray; font-style: italic;")
            self.item_positions.append({
                                       "type": "IMG",
                                       "data": image,
                                       "position": position
                                       })
        else:
            pass

    def build_layout(self):
        """ build the layout in correct order from data in item_positions struct """

        
        self.item_positions.sort(key=lambda x: x["position"])
        for item in self.item_positions:
            # TODO: different styling (ex. title should be bold)
            if item["type"] == "TITLE":
                self.layout.addWidget(item["data"])
            elif item["type"] == "TEXT":
                self.layout.addWidget(item["data"])
            elif item["type"] == "IMG":
                self.layout.addWidget(item["data"])
            else:
                pass
        self.layout.addStretch()


class IntroductionWindow(QWidget):
    """
        class responsible for all the logic in introduction/help window

        parsed_json struct item:
        {
            tab_type: introduction / ui / parser / ...
            data_type: TITLE / TEXT / IMG
            position: int
            data: string content (if title or text)
            location: location (if image)
        }

        parent: CitationLinkerApp
        children: HelpTab
    """

    def __init__(self, parent=None):
        """ init  of the tab widget window """
        super().__init__(parent)

        main_layout = QVBoxLayout(self)

        self._parent = parent
        self.tabs = QTabWidget()
        
        self.parsed_json = self._load_help_content()



        main_layout.addWidget(self.tabs)

        #  --introduction tab -----------------
        # ------------------------------------
        self.introduction_tab = HelpTab(self) 
        self.introduction_tab.insert_tab_content(self.set_tab_data("introduction"))
        self.tabs.addTab(self.introduction_tab, "Introduction")

        #  -- ui explanation tab -------------
        # ------------------------------------
        self.ui_tab = HelpTab(self)
        self.ui_tab.insert_tab_content(self.set_tab_data("ui"))
        self.tabs.addTab(self.ui_tab, "User interface")

        # -- parser explanation tab ---------
        # ------------------------------------
        self.parser_tab = HelpTab(self)
        self.parser_tab.insert_tab_content(self.set_tab_data("parser"))
        self.tabs.addTab(self.parser_tab, "Citation parsing limits")

        # -- bibEditor tab -------------------
        # ------------------------------------
        self.bib_tab = HelpTab(self)
        self.bib_tab.insert_tab_content(self.set_tab_data("bib_editor"))
        self.tabs.addTab(self.bib_tab, "Bibliography editor")


        
    def _load_help_content(self):
        path = files('qtapp').joinpath('data/help/help_content.json')
        content = path.read_text(encoding='utf-8')
        return json.loads(content)

    def set_tab_data(self, tab_type="introduction"):
        """ 
            here we extract the correct data to insert into tabs
            in json we search for items with tab_type corresponding to it
            and create a list dictionary with the item structure:
            type = TITLE/TEXT/IMG
            data = text data or image location
            position = in which position it needs to be displayed on the layout
        """
        data_list = []
        for item in self.parsed_json:
            if item["tab_type"] == tab_type:
                list_item = {
                        "type": item.get("data_type"),
                        "data": item.get("data") or item.get("location"),
                        "position": item.get("position")
                }
                data_list.append(list_item)

            else:
                pass

        return data_list

        


