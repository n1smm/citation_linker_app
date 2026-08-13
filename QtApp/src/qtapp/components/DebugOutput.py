"""
component for displaying debug output from citation-linker process
"""

from    PySide6.QtCore      import Qt, Slot, Signal
from    PySide6.QtWidgets   import (QWidget,
                                    QPushButton,
                                    QHBoxLayout,
                                    QVBoxLayout,
                                    QSizePolicy,
                                    QAbstractItemView,
                                    QComboBox,
                                    QTabWidget,
                                    QTableWidget,
                                    QTableWidgetItem,
                                    QTextEdit,
                                    QLabel,
                                    QHeaderView)


class DebugOutput(QWidget):
    """

    """

    citation_selected = Signal(dict)
    bibliography_selected = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(
                QSizePolicy.Policy.Preferred,
                QSizePolicy.Policy.Expanding
                )

        self.parent = parent
        self.debug_messages = []
        self.bib_entries = []
        self.cit_entries = []
        self.selected_bib_entry = {}
        self.selected_cit_entry = {}

        self.tabs = QTabWidget()

        #  log tab 
        self.level_selector = QComboBox()
        self.table = QTableWidget(0, 5)
        self.full_message = QTextEdit()

        #  bib tab 
        self.bib_table = QTableWidget(0, 8)

        #  cit tab 
        self.cit_table = QTableWidget(0, 7)

        self._init_ui()

        # signals
        self.table.cellClicked.connect(self.show_full_message)
        self.level_selector.currentTextChanged.connect(self.populate_table)
        self.bib_table.cellClicked.connect(self.pick_bib_entry)
        self.cit_table.cellClicked.connect(self.pick_cit_entry)

    #  ----------------
    # UI construction
    #  -----------------

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        # close button row (above tabs)
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        close_btn = QPushButton("🗙")
        close_btn.setMaximumWidth(30)
        close_btn.clicked.connect(self.close)
        top_bar.addWidget(close_btn)
        main_layout.addLayout(top_bar)

        main_layout.addWidget(self.tabs)

        self.tabs.addTab(self._build_log_tab(),  "Log")
        self.tabs.addTab(self._build_bib_tab(),  "Bibliography")
        self.tabs.addTab(self._build_cit_tab(),  "Citations")

    def _build_log_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        selector_layout = QHBoxLayout()
        selector_label = QLabel("Type: ")
        self.level_selector.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        selector_layout.addWidget(selector_label)
        selector_layout.addWidget(self.level_selector)
        selector_layout.addStretch()
        layout.addLayout(selector_layout, stretch=1)

        self.table.setHorizontalHeaderLabels(["Level",
                                              "Message",
                                              "Article number",
                                              "page in article",
                                              "page in document"])
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(False)
        layout.addWidget(self.table, stretch=6)

        self.full_message.setReadOnly(True)
        self.full_message.setPlaceholderText("Select a log entry to view full message")
        layout.addWidget(self.full_message, stretch=2)

        return widget

    def _build_bib_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.bib_table.setHorizontalHeaderLabels(
            ["Page", "Pg doc", "Surname", "Name", "Year", "Others", "Text", "Linked"])
        self.bib_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.bib_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.bib_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        bib_header = self.bib_table.horizontalHeader()
        bib_header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        bib_header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        bib_header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        bib_header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        bib_header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        bib_header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        bib_header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        bib_header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        bib_header.setStretchLastSection(False)

        layout.addWidget(self.bib_table)
        return widget

    def _build_cit_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.cit_table.setHorizontalHeaderLabels(
            ["Page", "Pg doc", "Year", "Surname", "Name", "Text", "Linked"])
        self.cit_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.cit_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.cit_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        cit_header = self.cit_table.horizontalHeader()
        cit_header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        cit_header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        cit_header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        cit_header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        cit_header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        cit_header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        cit_header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        cit_header.setStretchLastSection(False)

        layout.addWidget(self.cit_table)
        return widget

    # -----------------
    # Slots — log tab
    # ----------------



    @Slot(int, int)
    def show_full_message(self, row, column):
        full_text = self.table.item(row, 1).data(Qt.UserRole)
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
        if init:
            for msg in self.debug_messages:
                tmp_level = str(msg.get("level", "")).upper()
                if tmp_level == "WARNING" and (selected_level != "ERROR" or selected_level != "CRITICAL"):
                    selected_level = tmp_level
                if tmp_level == "ERROR" and selected_level != "CRITICAL":
                    selected_level = tmp_level
                if tmp_level == "CRITICAL":
                    selected_level = tmp_level
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

            article_num    = msg.get("article_num")
            page_in_article = msg.get("page_in_article")
            page_in_doc    = msg.get("page_in_doc")

            level_item   = QTableWidgetItem(level)
            message_item = QTableWidgetItem(short_message)
            message_item.setData(Qt.UserRole, full_message)
            article_item      = QTableWidgetItem("" if article_num is None else str(article_num))
            page_article_item = QTableWidgetItem("" if page_in_article is None else str(page_in_article))
            page_doc_item     = QTableWidgetItem("" if page_in_doc is None else str(page_in_doc))

            self.table.setItem(row, 0, level_item)
            self.table.setItem(row, 1, message_item)
            self.table.setItem(row, 2, article_item)
            self.table.setItem(row, 3, page_article_item)
            self.table.setItem(row, 4, page_doc_item)

    # ------------------------
    # Slots — bibliography tab
    # ------------------------

    @Slot(list)
    def set_bib_entries(self, entries):
        self.bib_entries = list(entries or [])
        self.bib_table.setRowCount(0)
        for entry in self.bib_entries:
            row = self.bib_table.rowCount()
            self.bib_table.insertRow(row)
            others = entry.get("others", [])
            others_str = ", ".join(o for o in others if o and o != "yyy")
            self.bib_table.setItem(row, 0, QTableWidgetItem(str(entry.get("page", ""))))
            pg_doc = entry.get("page_in_doc")
            self.bib_table.setItem(row, 1, QTableWidgetItem("" if pg_doc is None else str(pg_doc)))
            self.bib_table.setItem(row, 2, QTableWidgetItem(self._display_val(entry.get("surname"))))
            self.bib_table.setItem(row, 3, QTableWidgetItem(self._display_val(entry.get("name"))))
            self.bib_table.setItem(row, 4, QTableWidgetItem(self._display_val(entry.get("year"))))
            self.bib_table.setItem(row, 5, QTableWidgetItem(others_str))
            self.bib_table.setItem(row, 6, QTableWidgetItem(str(entry.get("text", ""))))
            linked = entry.get("linked", False)
            self.bib_table.setItem(row, 7, QTableWidgetItem("✓" if linked else ""))

    @Slot(int, int)
    def pick_bib_entry(self, row, column):
        self.selected_bib_entry = self.bib_entries[row]
        self.bibliography_selected.emit(self.selected_bib_entry)
        print(self.selected_bib_entry)

    # ---------------------
    # Slots — citations tab
    # ---------------------

    @Slot(list)
    def set_cit_entries(self, entries):
        self.cit_entries = list(entries or [])
        self.cit_table.setRowCount(0)
        for entry in self.cit_entries:
            row = self.cit_table.rowCount()
            self.cit_table.insertRow(row)
            self.cit_table.setItem(row, 0, QTableWidgetItem(str(entry.get("page", ""))))
            pg_doc = entry.get("page_in_doc")
            self.cit_table.setItem(row, 1, QTableWidgetItem("" if pg_doc is None else str(pg_doc)))
            self.cit_table.setItem(row, 2, QTableWidgetItem(self._display_val(entry.get("year"))))
            self.cit_table.setItem(row, 3, QTableWidgetItem(self._display_val(entry.get("surname"))))
            self.cit_table.setItem(row, 4, QTableWidgetItem(self._display_val(entry.get("name"))))
            self.cit_table.setItem(row, 5, QTableWidgetItem(str(entry.get("text", ""))))
            linked = entry.get("linked", False)
            self.cit_table.setItem(row, 6, QTableWidgetItem("✓" if linked else ""))

    @Slot(int, int)
    def pick_cit_entry(self, row, column):
        self.selected_cit_entry = self.cit_entries[row]
        self.citation_selected.emit(self.selected_cit_entry)
        print(self.selected_cit_entry)

    @staticmethod
    def _display_val(value):
        """Convert placeholder values to human-readable labels."""
        if value in ("xxx", "yyy"):
            return "(not found)"
        return str(value) if value else ""
