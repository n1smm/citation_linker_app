"""
BIB_STRUCTURE editor component.
Provides a UI for building and modifying bibliography structure definitions
used by the modular bibliography parser.

A "structure" is an ordered list of typed elements that describes how one
bibliography entry is laid out on the page, e.g.:
  SURNAME → SEPARATOR(,) → NAME → EXTRA_CHAR(() → YEAR → EXTRA_CHAR()) → SEPARATOR(:) → TITLE

Multiple alternative structures can coexist; the parser tries each one and
picks the best match.
"""
import  json
from    PySide6.QtCore      import  Qt, Signal, Slot
from    PySide6.QtWidgets   import  (QWidget,
                                     QPushButton,
                                     QHBoxLayout,
                                     QVBoxLayout,
                                     QLabel,
                                     QListWidget,
                                     QComboBox,
                                     QLineEdit,
                                     QGroupBox,
                                     QSizePolicy,
                                     QMessageBox)


# Types the user can pick
BIB_ELEMENT_TYPES = [
    "SURNAME",
    "NAME",
    "TITLE",
    "YEAR",
    "SEPARATOR",
    "EXTRA_CHAR",
    "OTHER_AUTHORS",
    "IGNORE",
]

# Types that carry an "options" list (chars / strings the parser looks for)
TYPES_WITH_OPTIONS = {"SEPARATOR", "EXTRA_CHAR", "OTHER_AUTHORS"}


class BibStructureEditor(QWidget):
    """
    Standalone window for editing BIB_STRUCTURE config values.

    Parent: CitationLinkerInstance (set as Qt.Window child)

    Top section   — list of all saved structures; click one to load it.
    Bottom-left   — ordered list of elements in the current structure.
    Bottom-right  — type selector + options field to add or edit elements.

    Public API used by DocConfig:
        get_structures_json()   → str   (JSON, write to config)
        set_structures(data)    → None  (load from parsed config value)
        has_structures()        → bool
    """

    structures_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle("Bib Structure Editor")
        self.resize(750, 580)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        self._structures = []           # list[list[dict]]
        self._current_struct_idx = None

        self._init_ui()
        self._wire_signals()

    # ─────────────────────────────────────────────
    # UI construction
    # ─────────────────────────────────────────────

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        # close button row
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        close_btn = QPushButton("🗙")
        close_btn.setMaximumWidth(30)
        close_btn.clicked.connect(self.close)
        top_bar.addWidget(close_btn)
        main_layout.addLayout(top_bar)

        # ── top: existing structures ──────────────
        struct_group = QGroupBox("Existing Structures  (click to edit)")
        struct_layout = QVBoxLayout(struct_group)

        self.structures_list = QListWidget()
        self.structures_list.setMaximumHeight(120)
        self.structures_list.setToolTip("Click a structure to load it into the editor below")
        struct_layout.addWidget(self.structures_list)

        struct_btn_row = QHBoxLayout()
        self.new_struct_btn = QPushButton("New Structure")
        self.remove_struct_btn = QPushButton("Remove Structure")
        struct_btn_row.addWidget(self.new_struct_btn)
        struct_btn_row.addWidget(self.remove_struct_btn)
        struct_btn_row.addStretch()
        struct_layout.addLayout(struct_btn_row)

        main_layout.addWidget(struct_group)

        # ── bottom: element editor ────────────────
        editor_group = QGroupBox("Structure Elements")
        editor_layout = QHBoxLayout(editor_group)

        # left — element list
        elem_list_col = QVBoxLayout()
        elem_list_col.addWidget(QLabel("Elements (in order):"))

        self.elements_list = QListWidget()
        elem_list_col.addWidget(self.elements_list, stretch=1)

        elem_btn_row = QHBoxLayout()
        self.move_up_btn   = QPushButton("▲")
        self.move_down_btn = QPushButton("▼")
        self.remove_elem_btn = QPushButton("Remove")
        self.move_up_btn.setMaximumWidth(36)
        self.move_down_btn.setMaximumWidth(36)
        elem_btn_row.addWidget(self.move_up_btn)
        elem_btn_row.addWidget(self.move_down_btn)
        elem_btn_row.addWidget(self.remove_elem_btn)
        elem_btn_row.addStretch()
        elem_list_col.addLayout(elem_btn_row)

        editor_layout.addLayout(elem_list_col, stretch=3)

        # right — input fields
        input_col = QVBoxLayout()

        input_col.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(BIB_ELEMENT_TYPES)
        input_col.addWidget(self.type_combo)

        self.options_label = QLabel("Options  (use  |  to separate multiple values):")
        self.options_input = QLineEdit()
        self.options_input.setPlaceholderText(
            "SEPARATOR → ,   or   :   or   .  |  :\n"
            "EXTRA_CHAR → (   or   )\n"
            "OTHER_AUTHORS → , | and | in"
        )
        input_col.addWidget(self.options_label)
        input_col.addWidget(self.options_input)

        input_col.addStretch()

        self.add_elem_btn    = QPushButton("Add Element  ↓")
        self.update_elem_btn = QPushButton("Update Selected Element")
        input_col.addWidget(self.add_elem_btn)
        input_col.addWidget(self.update_elem_btn)

        input_col.addStretch()

        self.save_struct_btn = QPushButton("Save Structure")
        self.save_struct_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        font = self.save_struct_btn.font()
        font.setBold(True)
        self.save_struct_btn.setFont(font)
        input_col.addWidget(self.save_struct_btn)

        editor_layout.addLayout(input_col, stretch=2)

        main_layout.addWidget(editor_group, stretch=1)

    def _wire_signals(self):
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        self._on_type_changed(self.type_combo.currentText())

        self.structures_list.currentRowChanged.connect(self._on_structure_selected)
        self.elements_list.currentRowChanged.connect(self._on_element_selected)

        self.new_struct_btn.clicked.connect(self._on_new_structure)
        self.remove_struct_btn.clicked.connect(self._on_remove_structure)

        self.add_elem_btn.clicked.connect(self._on_add_element)
        self.update_elem_btn.clicked.connect(self._on_update_element)
        self.remove_elem_btn.clicked.connect(self._on_remove_element)
        self.move_up_btn.clicked.connect(self._on_move_up)
        self.move_down_btn.clicked.connect(self._on_move_down)
        self.save_struct_btn.clicked.connect(self._on_save_structure)

    # ─────────────────────────────────────────────
    # Internal helpers
    # ─────────────────────────────────────────────

    def _structure_summary(self, struct):
        """Short one-line label shown in the structures list."""
        parts = []
        for elem in struct:
            typ = elem.get("type", "?")
            opts = elem.get("options", [])
            parts.append(f"{typ}({','.join(opts)})" if opts else typ)
        return "  →  ".join(parts) if parts else "(empty)"

    def _element_label(self, elem):
        typ  = elem.get("type", "?")
        opts = elem.get("options", [])
        return f"{typ}  [ {' | '.join(opts)} ]" if opts else typ

    def _elem_from_inputs(self):
        """Build an element dict from the current type/options fields."""
        typ  = self.type_combo.currentText()
        elem = {"type": typ}
        if typ in TYPES_WITH_OPTIONS:

            raw = self.options_input.text()
            if raw:
                if raw.strip():
                    opts = [o.strip() for o in raw.split("|") if o.strip()]
                else:
                    opts = [raw[0]]
                if opts:
                    elem["options"] = opts
        return elem

    def _load_elem_into_inputs(self, elem):
        """Populate type/options fields from an existing element dict."""
        typ = elem.get("type", "IGNORE")
        idx = self.type_combo.findText(typ)
        if idx >= 0:
            self.type_combo.setCurrentIndex(idx)
        opts = elem.get("options", [])
        self.options_input.setText(" | ".join(opts))

    def _repopulate_elements_list(self, struct):
        self.elements_list.clear()
        for elem in struct:
            self.elements_list.addItem(self._element_label(elem))

    def _refresh_structures_list(self, keep_row=None):
        self.structures_list.blockSignals(True)
        self.structures_list.clear()
        for i, struct in enumerate(self._structures):
            self.structures_list.addItem(
                f"Structure {i + 1}:   {self._structure_summary(struct)}"
            )
        self.structures_list.blockSignals(False)
        if keep_row is not None and 0 <= keep_row < self.structures_list.count():
            self.structures_list.setCurrentRow(keep_row)

    # ─────────────────────────────────────────────
    # Slots — structure list
    # ─────────────────────────────────────────────

    @Slot(str)
    def _on_type_changed(self, typ):
        visible = typ in TYPES_WITH_OPTIONS
        self.options_label.setVisible(visible)
        self.options_input.setVisible(visible)
        if not visible:
            self.options_input.clear()

    @Slot(int)
    def _on_structure_selected(self, row):
        if row < 0 or row >= len(self._structures):
            return
        self._current_struct_idx = row
        self._repopulate_elements_list(self._structures[row])

    def _on_new_structure(self):
        self._structures.append([])
        self._current_struct_idx = len(self._structures) - 1
        self._refresh_structures_list(keep_row=self._current_struct_idx)
        self.elements_list.clear()

    def _on_remove_structure(self):
        row = self.structures_list.currentRow()
        if row < 0 or row >= len(self._structures):
            return
        self._structures.pop(row)
        self._current_struct_idx = None
        self._refresh_structures_list()
        self.elements_list.clear()
        self.structures_changed.emit()

    # ─────────────────────────────────────────────
    # Slots — element editor
    # ─────────────────────────────────────────────

    @Slot(int)
    def _on_element_selected(self, row):
        if self._current_struct_idx is None:
            return
        struct = self._structures[self._current_struct_idx]
        if row < 0 or row >= len(struct):
            return
        self._load_elem_into_inputs(struct[row])

    def _on_add_element(self):
        if self._current_struct_idx is None:
            QMessageBox.information(self, "No Structure",
                                    "Create or select a structure first.")
            return
        elem = self._elem_from_inputs()
        self._structures[self._current_struct_idx].append(elem)
        self.elements_list.addItem(self._element_label(elem))

    def _on_update_element(self):
        if self._current_struct_idx is None:
            return
        row = self.elements_list.currentRow()
        struct = self._structures[self._current_struct_idx]
        if row < 0 or row >= len(struct):
            return
        elem = self._elem_from_inputs()
        struct[row] = elem
        self.elements_list.item(row).setText(self._element_label(elem))

    def _on_remove_element(self):
        if self._current_struct_idx is None:
            return
        row = self.elements_list.currentRow()
        struct = self._structures[self._current_struct_idx]
        if row < 0 or row >= len(struct):
            return
        struct.pop(row)
        self.elements_list.takeItem(row)

    def _on_move_up(self):
        if self._current_struct_idx is None:
            return
        row = self.elements_list.currentRow()
        struct = self._structures[self._current_struct_idx]
        if row <= 0 or row >= len(struct):
            return
        struct[row], struct[row - 1] = struct[row - 1], struct[row]
        self._repopulate_elements_list(struct)
        self.elements_list.setCurrentRow(row - 1)

    def _on_move_down(self):
        if self._current_struct_idx is None:
            return
        row = self.elements_list.currentRow()
        struct = self._structures[self._current_struct_idx]
        if row < 0 or row >= len(struct) - 1:
            return
        struct[row], struct[row + 1] = struct[row + 1], struct[row]
        self._repopulate_elements_list(struct)
        self.elements_list.setCurrentRow(row + 1)

    def _on_save_structure(self):
        if self._current_struct_idx is None:
            QMessageBox.information(self, "No Structure",
                                    "Create or select a structure first.")
            return
        self._refresh_structures_list(keep_row=self._current_struct_idx)
        self.structures_changed.emit()

    # ─────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────

    def get_structures_json(self):
        """Return JSON string ready to be written as BIB_STRUCTURE= in the config."""
        return json.dumps(self._structures)

    def set_structures(self, data):
        """
        Load structures from a parsed config value.
          data = list[list[dict]]  — multiple structures
          data = list[dict]        — single structure (flat)
          data = []                — nothing configured
        """
        if not isinstance(data, list) or not data:
            self._structures = []
        elif isinstance(data[0], dict):
            self._structures = [data]
        else:
            self._structures = [s for s in data if isinstance(s, list)]

        self._current_struct_idx = None
        self._refresh_structures_list()
        self.elements_list.clear()

    def has_structures(self):
        """True when at least one non-empty structure exists."""
        return any(len(s) > 0 for s in self._structures)
