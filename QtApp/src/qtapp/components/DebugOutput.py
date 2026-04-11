"""
component for displaying debug output from citation-linker process
"""

from    PySide6.QtCore      import Qt, Slot
from    PySide6.QtWidgets   import (QWidget,
                                    QPushButton,
                                    QHBoxLayout,
                                    QVBoxLayout,
                                    QGridLayout,
                                    QSizePolicy,
                                    QAbstractItemView,
                                    QComboBox,
                                    QTableWidget,
                                    QTableWidgetItem,
                                    QTextEdit,
                                    QLabel,
                                    QListWidget,
                                    QHeaderView)


class DebugOutput(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(
                QSizePolicy.Policy.Preferred,
                QSizePolicy.Policy.Expanding
                )

        ### member declarations
        self.parent = parent
        self.debug_messages = []

        self.level_selector = QComboBox()
        self.table = QTableWidget(0,5)
        self.full_message = QTextEdit()

        #ui init
        self.init_ui()

        ### signals
        self.table.cellClicked.connect(self.show_full_message)
        self.level_selector.currentTextChanged.connect(self.populate_table)



    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # level selector (1/6 of height)
        selector_layout = QHBoxLayout()
        selector_label = QLabel("Type: ")
        self.level_selector.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        selector_layout.addWidget(selector_label)
        selector_layout.addWidget(self.level_selector)
        
        # Add close button
        close_btn = QPushButton("🗙")
        close_btn.setMaximumWidth(30)
        close_btn.clicked.connect(self.close)
        selector_layout.addStretch()
        selector_layout.addWidget(close_btn)
        
        main_layout.addLayout(selector_layout, stretch=1)

        # log table (3/6 of height)
        self.table.setHorizontalHeaderLabels(["Level",
                                              "Message",
                                              "Article number",
                                              "page in article",
                                              "page in document"
                                              ])
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Configure column resize behavior
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Level
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Message (wider, stretches)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Article number
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # page in article
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # page in document
        header.setStretchLastSection(False)
        
        main_layout.addWidget(self.table, stretch=6)

        # full log message display (2/6 of height)
        self.full_message.setReadOnly(True)
        self.full_message.setPlaceholderText("Select a log entry to view full message")
        main_layout.addWidget(self.full_message, stretch=2)

        self.setLayout(main_layout)


    @Slot(int, int)
    def show_full_message(self, row, column):
        full_text = self.table.item(row,1).data(Qt.UserRole)
        if full_text:
            self.full_message.setPlainText(full_text)
        else:
            self.full_message.setPlainText(self.table.item(row, 1).text())

    @Slot(list)
    def set_debug_messages(self, messages):
        self.debug_messages = list(messages or [])
        self.populate_table(init=True)

    @Slot()
    def populate_table(self, init=False):
                
        selected_level = self.level_selector.currentText().upper()
        if init == True:
            for msg in self.debug_messages:
                tmp_level = str(msg.get("level", "")).upper()
                if tmp_level == "WARNING" and (selected_level != "ERROR" or selected_level != CRITICAL):
                    selected_level = str(msg.get("level", "")).upper()
                if tmp_level == "ERROR" and selected_level != "CRITICAL":
                    selected_level = str(msg.get("level", "")).upper()
                if tmp_level == "CRITICAL":
                    selected_level = str(msg.get("level", "")).upper()
                    break
            self.level_selector.blockSignals(True)
            self.level_selector.setCurrentText(selected_level)
            self.level_selector.blockSignals(False)
            
        if selected_level == "ALL":
            filtered_messages = self.debug_messages
        else:
            filtered_messages = [
                msg for msg in self.debug_messages
                if str(msg.get("level", "")).upper() == selected_level
            ]

        self.table.setRowCount(0)
        for msg in filtered_messages:
            row = self.table.rowCount()
            self.table.insertRow(row)

            level = str(msg.get("level", ""))
            full_message = str(msg.get("message", ""))
            short_message = full_message if len(full_message) <= 100 else full_message[:97] + "..."

            article_num = msg.get("article_num")
            page_in_article = msg.get("page_in_article")
            page_in_doc = msg.get("page_in_doc")

            level_item = QTableWidgetItem(level)
            message_item = QTableWidgetItem(short_message)
            message_item.setData(Qt.UserRole, full_message)
            article_item = QTableWidgetItem("" if article_num is None else str(article_num))
            page_article_item = QTableWidgetItem("" if page_in_article is None else str(page_in_article))
            page_doc_item = QTableWidgetItem("" if page_in_doc is None else str(page_in_doc))

            self.table.setItem(row, 0, level_item)
            self.table.setItem(row, 1, message_item)
            self.table.setItem(row, 2, article_item)
            self.table.setItem(row, 3, page_article_item)
            self.table.setItem(row, 4, page_doc_item)


        

        

