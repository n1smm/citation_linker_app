"""
component for displaying debug output from citation-linker process
"""

from    PySide6.QtCore      import Qt, Slot, Signal 
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



    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # level selector (1/6 of height)
        selector_layout = QHBoxLayout()
        selector_label = QLabel("Type: ")
        self.level_selector.addItems(["All", "Debug", "Info", "Warning", "Error", "Critical"])
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


        

        


