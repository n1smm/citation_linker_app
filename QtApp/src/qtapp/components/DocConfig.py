"""
Document configuration management UI for citation linking settings.
Provides forms for all configuration options with load/save functionality.
"""
import  re
import  os
import  sys
import  subprocess
from    pathlib                         import  Path
from    PySide6.QtCore                  import  Qt, QFile, Slot, Signal
from    PySide6.QtWidgets               import  (QWidget,
                                                 QFileDialog,
                                                 QInputDialog,
                                                 QPushButton,
                                                 QHBoxLayout,
                                                 QVBoxLayout,
                                                 QGridLayout,
                                                 QLabel,
                                                 QMessageBox,
                                                 QLineEdit,
                                                 QCheckBox,
                                                 QComboBox,
                                                 QListWidget,
                                                 QGroupBox,
                                                 QSizePolicy,
                                                 QScrollArea,)

from    qtapp.components.FileManager    import  FileManager

class DocConfig(QWidget):
    """
    Document configuration UI for citation linking parameters.
    
    Parent: mainWindow
    Children: FileManager, QListWidget, QComboBox, QCheckBox, QPushButton
    
    Manages all citation linking configuration including:
    - Special case citations (ibid, op. cit., etc.)
    - Bibliography delimiter detection
    - Annotation type and color
    - Article break page ranges for multi-article documents
    - Search options (soft year, deep search, alternative bib format)
    - Configuration file loading and saving
    
    Configuration is synchronized with text handlers and persisted to disk.
    Provides help dialogs for each configuration field.
    """
    list_widget_changed = Signal(str, QListWidget)
    REQUIRED_CONFIG_KEYS = {
        "DEBUG",
        "SPECIAL_CASE",
        "BIBLIOGRAPHY_DELIMITER",
        "ANNOT_TYPE",
        "COLOR",
        "OFFSET",
        "ARTICLE_BREAKS",
        "SOFT_YEAR",
        "DEEP_SEARCH",
        "SEARCH_EXCLUDE",
        "ALTERNATIVE_BIB",
    }

    def __init__(self, parent=None, bridge=None):
        """Initialize configuration UI with all fields and load existing config."""
        super().__init__(parent)
        self.setSizePolicy(
                QSizePolicy.Policy.Preferred,
                QSizePolicy.Policy.Expanding
                )

        ### member declarations
        self.parent = parent
        self.bridge = bridge
        self.user_shell = bridge.get_user_shell() 
        self.config_path = bridge.get_config_path()
        self.file_path = ""
        self.output_file_path = ""

        # Config values
        self.debug = False
        self.special_cases = []
        self.delimiters = []
        self.annot_type = "underline"
        self.color = "black"
        self.offset = ""
        self.article_cache = []
        self.soft_year_search = False
        self.deep_search = False
        self.search_exclude = []
        self.alternative_bib = False

        self.file_manager = FileManager(upload=True, pdf=False, parent=self)
        self.file_manager.hide()

        # Initialize UI
        self.init_ui()

        #signals
        self.list_widget_changed.connect(self.list_widget_update)
        self.bridge.config_path_changed.connect(self.on_config_path_change)

        if self.config_path and os.path.exists(self.config_path):
            self.load_config()

    def init_ui(self):
        """Build the configuration user interface with all form fields."""
        main_layout = QVBoxLayout(self)

        # Scroll area for config fields
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(400)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # --- Text/List Fields Group ---
        text_group = QGroupBox("Configuration Fields")
        text_layout = QGridLayout()
        row = 0

        # SPECIAL_CASE
        self.add_list_field(text_layout, row, "SPECIAL_CASE",
                           "Special cases for repeated citations",
                           "List of phrases that indicate a repeated citation (e.g., 'ibid.', 'op. cit.'). "
                           "These allow referencing the same work multiple times without full citation.")
        self.special_case_list = self.current_list_widget
        row += 1

        # BIBLIOGRAPHY_DELIMITER
        self.add_list_field(text_layout, row, "BIBLIOGRAPHY_DELIMITER",
                           "Bibliography section headers",
                           "Text that marks the beginning of the bibliography/references section. "
                           "Can be multiple variants. List less common ones first, more common ones last. "
                           "E.g., 'Viri in literatura', 'Literatura'")
        self.delimiter_list = self.current_list_widget
        row += 1

        # ANNOT_TYPE
        text_layout.addWidget(QLabel("ANNOT_TYPE:"), row, 0)
        self.annot_type_combo = QComboBox()
        self.annot_type_combo.addItems(["underline", "highlight"])
        text_layout.addWidget(self.annot_type_combo, row, 1)
        help_btn = QPushButton("?")
        help_btn.setMaximumWidth(30)
        help_btn.clicked.connect(lambda: self.show_help(
            "Annotation Type",
            "How citations are visually marked in the PDF:\n"
            "- underline: Citations will be underlined\n"
            "- highlight: Citations will be highlighted with background color"))
        text_layout.addWidget(help_btn, row, 2)
        row += 1

        # COLOR
        text_layout.addWidget(QLabel("COLOR:"), row, 0)
        self.color_combo = QComboBox()
        self.color_combo.addItems(["black", "white", "gray", "blue", "red", "dark_blue"])
        text_layout.addWidget(self.color_combo, row, 1)
        help_btn = QPushButton("?")
        help_btn.setMaximumWidth(30)
        help_btn.clicked.connect(lambda: self.show_help(
            "Color",
            "Color for the citation annotations/links.\n"
            "Available colors: black, white, gray, blue, red, dark_blue"))
        text_layout.addWidget(help_btn, row, 2)
        row += 1

        # OFFSET
        text_layout.addWidget(QLabel("OFFSET:"), row, 0)
        self.offset_combo = QComboBox()
        self.offset_combo.addItem("", "")
        for i in range(-10, 11):
            if i > 0:
                self.offset_combo.addItem(f"+{i}", f"+{i}")
            elif i < 0:
                self.offset_combo.addItem(str(i), str(i))
        text_layout.addWidget(self.offset_combo, row, 1)
        help_btn = QPushButton("?")
        help_btn.setMaximumWidth(30)
        help_btn.clicked.connect(lambda: self.show_help(
            "Offset",
            "Used only for multi-article documents. Shifts article start/end pages forward or backward.\n"
            "Format: +N (forward) or -N (backward)\n"
            "Example: +2 moves each article start 2 pages forward, -5 moves 5 pages backward"))
        text_layout.addWidget(help_btn, row, 2)
        row += 1

        # ARTICLE_BREAKS
        self.add_list_field(text_layout, row, "ARTICLE_BREAKS",
                           "Article page ranges",
                           "Only for multi-article documents. Specifies where articles begin and end.\n"
                           "Format: 'start:end' where end is where the bibliography concludes.\n"
                           "Example: '1:23', '25:45' means first article is pages 1-23, second is 25-45.\n"
                           "Only needed if each article has its own bibliography.")
        self.article_breaks_list = self.current_list_widget
        row += 1

        # SEARCH_EXCLUDE
        self.add_list_field(text_layout, row, "SEARCH_EXCLUDE",
                           "Words to exclude from deep search",
                           "Words that DEEP_SEARCH should not consider as valid citation matches.\n"
                           "Use this to prevent false positives from common abbreviations.\n"
                           "Example: 'ur', 'Ur.' (editor abbreviations)")
        self.search_exclude_list = self.current_list_widget

        text_group.setLayout(text_layout)
        scroll_layout.addWidget(text_group)

        # --- Boolean Fields Group ---
        bool_group = QGroupBox("Boolean Options")
        bool_layout = QGridLayout()
        bool_row = 0

        # DEBUG
        bool_layout.addWidget(QLabel("DEBUG:"), bool_row, 0)
        self.debug_check = QCheckBox()
        bool_layout.addWidget(self.debug_check, bool_row, 1)
        help_btn = QPushButton("?")
        help_btn.setMaximumWidth(30)
        help_btn.clicked.connect(lambda: self.show_help(
            "Debug Mode",
            "Enable verbose logging and debugging information during processing.\n"
            "Useful for troubleshooting issues with citation linking."))
        bool_layout.addWidget(help_btn, bool_row, 2)
        bool_row += 1

        # SOFT_YEAR
        bool_layout.addWidget(QLabel("SOFT_YEAR:"), bool_row, 0)
        self.soft_year_check = QCheckBox()
        bool_layout.addWidget(self.soft_year_check, bool_row, 1)
        help_btn = QPushButton("?")
        help_btn.setMaximumWidth(30)
        help_btn.clicked.connect(lambda: self.show_help(
            "Soft Year Search",
            "Use more relaxed filtering for years in citations.\n"
            "Includes year ranges (e.g., 1998-2004) and checks year ±1 in case of typos.\n"
            "WARNING: May create links where they shouldn't be."))
        bool_layout.addWidget(help_btn, bool_row, 2)
        bool_row += 1

        # DEEP_SEARCH
        bool_layout.addWidget(QLabel("DEEP_SEARCH:"), bool_row, 0)
        self.deep_search_check = QCheckBox()
        bool_layout.addWidget(self.deep_search_check, bool_row, 1)
        help_btn = QPushButton("?")
        help_btn.setMaximumWidth(30)
        help_btn.clicked.connect(lambda: self.show_help(
            "Deep Search",
            "Enable more permissive matching for citations.\n"
            "Finds citations that may not exactly match the bibliography format.\n"
            "WARNING: May create links where they shouldn't be."))
        bool_layout.addWidget(help_btn, bool_row, 2)
        bool_row += 1

        # ALTERNATIVE_BIB
        bool_layout.addWidget(QLabel("ALTERNATIVE_BIB:"), bool_row, 0)
        self.alternative_bib_check = QCheckBox()
        bool_layout.addWidget(self.alternative_bib_check, bool_row, 1)
        help_btn = QPushButton("?")
        help_btn.setMaximumWidth(30)
        help_btn.clicked.connect(lambda: self.show_help(
            "Alternative Bibliography Format",
            "Handle bibliography entries that start with year followed by period, then the work.\n"
            "Format: (Year). Work title...\n"
            "WARNING: May create links where they shouldn't be."))
        bool_layout.addWidget(help_btn, bool_row, 2)

        bool_group.setLayout(bool_layout)
        scroll_layout.addWidget(bool_group)

        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll, stretch=1)

        # Bottom buttons
        button_layout = QHBoxLayout()

        load_btn = QPushButton("Load Config")
        load_btn.clicked.connect(self.load_config_dialog)
        button_layout.addWidget(load_btn)

        save_btn = QPushButton("Save Config")
        save_btn.clicked.connect(self.save_config_as)
        button_layout.addWidget(save_btn)

        new_btn = QPushButton("New Config")
        new_btn.clicked.connect(self.clear_all_fields)
        button_layout.addWidget(new_btn)

        debug_btn = QPushButton("Debug Output")
        debug_btn.clicked.connect(self.show_debug_output)
        button_layout.addWidget(debug_btn)

        main_layout.addLayout(button_layout, stretch=1)

    def add_list_field(self, layout, row, field_name, label_text, help_text):
        """Helper to add a list field with add/remove buttons"""
        layout.addWidget(QLabel(f"{field_name}:"), row, 0, Qt.AlignTop)

        list_layout = QVBoxLayout()
        list_widget = QListWidget()
        list_widget.setMinimumHeight(80)
        list_widget.setMaximumHeight(200)
        list_layout.addWidget(list_widget)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add")
        remove_btn = QPushButton("Remove")
        change_btn = QPushButton("Change")
        up_btn = QPushButton("▲")
        down_btn= QPushButton("▼")
        up_btn.setMaximumWidth(30)
        down_btn.setMaximumWidth(30)

        def add_item():
            text, ok = QInputDialog.getText(self, f"Add {label_text}", "Enter value:")
            if ok and text:
                list_widget.addItem(text)
                self.list_widget_changed.emit(field_name, list_widget)

        def remove_item():
            current = list_widget.currentRow()
            if current >= 0:
                list_widget.takeItem(current)
                self.list_widget_changed.emit(field_name, list_widget)

        def change_item():
            current = list_widget.currentRow()
            if current >= 0:
                old_text = list_widget.item(current).text()
                text, ok = QInputDialog.getText(self,
                                                f"Change {label_text}",
                                                "Edit value:",
                                                text=old_text)
                if ok and text:
                    list_widget.item(current).setText(text)
                    self.list_widget_changed.emit(field_name, list_widget)

        def move_up():
            current = list_widget.currentRow()
            if current > 0:
                item = list_widget.takeItem(current)
                list_widget.insertItem(current - 1, item)
                list_widget.setCurrentRow(current -1)
                self.list_widget_changed.emit(field_name, list_widget)

        def move_down():
            current = list_widget.currentRow()
            if 0 <= current < list_widget.count() -1:
                item = list_widget.takeItem(current)
                list_widget.insertItem(current + 1, item)
                list_widget.setCurrentRow(current + 1)
                self.list_widget_changed.emit(field_name, list_widget)
            


        add_btn.clicked.connect(add_item)
        remove_btn.clicked.connect(remove_item)
        change_btn.clicked.connect(change_item)
        up_btn.clicked.connect(move_up)
        down_btn.clicked.connect(move_down)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addWidget(change_btn)
        btn_layout.addWidget(up_btn)
        btn_layout.addWidget(down_btn)

        list_layout.addLayout(btn_layout)

        layout.addLayout(list_layout, row, 1)

        help_btn = QPushButton("?")
        help_btn.setMaximumWidth(30)
        help_btn.clicked.connect(lambda: self.show_help(label_text.title(), help_text))
        layout.addWidget(help_btn, row, 2, Qt.AlignTop)

        # Store reference for later
        self.current_list_widget = list_widget

    def show_help(self, title, message):
        """Display help dialog for a configuration field."""
        QMessageBox.information(self, title, message)

    def set_config_path(self):
        """Prompt user to select configuration file path."""
        self.file_manager.show()
        self.file_manager.open_file()
        self.config_path = self.file_manager.get_file_path()
        self.file_manager.reset_manager(upload=True, pdf=False)
        self.file_manager.hide()
        self.parent.bridge.set_paths(config_path=self.config_path)

    def set_input_dir(self):
        """Prompt user to select input directory."""
        self.file_manager.show()
        self.file_manager.open_dir()
        self.input_dir = self.file_manager.get_dir_path()
        self.file_manager.reset_manager(upload=True, pdf=False)
        self.file_manager.hide()
        self.parent.bridge.set_paths(input_dir=self.input_dir)

    def set_output_dir(self):
        """Prompt user to select output directory."""
        self.file_manager.show()
        self.file_manager.open_dir()
        self.output_dir = self.file_manager.get_dir_path()
        self.file_manager.reset_manager(upload=True, pdf=False)
        self.file_manager.hide()
        self.parent.bridge.set_paths(output_dir=self.output_dir)

    def on_config_path_change(self, path):
        """Handle configuration path change signal."""
        self.config_path = path

    def get_config_dialog_start_dir(self):
        """Get the preferred directory for config file dialogs."""
        if self.config_path:
            config_dir = Path(self.config_path).expanduser().resolve().parent
            if config_dir.exists():
                return str(config_dir)
        return str(Path.home())

    def parse_config_file(self, config_path):
        """Parse full config file into key/value mapping."""
        config_values = {}
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                key, value = self.parse_config_line(line)
                if key:
                    config_values[key] = value
        return config_values

    def validate_config_values(self, config_values):
        """Validate required config structure and key value formats."""
        missing_keys = sorted(self.REQUIRED_CONFIG_KEYS - set(config_values.keys()))
        if missing_keys:
            return False, f"Missing required keys: {', '.join(missing_keys)}"

        bool_keys = ("DEBUG", "SOFT_YEAR", "DEEP_SEARCH", "ALTERNATIVE_BIB")
        for key in bool_keys:
            value = config_values.get(key, "").strip().lower()
            if value not in ("true", "false"):
                return False, f"Invalid {key}: expected True or False."

        annot_type = config_values.get("ANNOT_TYPE", "").strip().lower()
        if annot_type not in ("underline", "highlight"):
            return False, "Invalid ANNOT_TYPE: expected underline or highlight."

        valid_colors = {
            self.color_combo.itemText(i).strip().lower()
            for i in range(self.color_combo.count())
        }
        color = config_values.get("COLOR", "").strip().lower()
        if color and color not in valid_colors:
            return False, f"Invalid COLOR: expected one of {', '.join(sorted(valid_colors))}."

        offset = config_values.get("OFFSET", "").strip()
        if offset and not re.fullmatch(r"[+-]?\d+", offset):
            return False, "Invalid OFFSET: expected empty value or signed integer (e.g., +2, -5)."

        delimiter_values = self.parse_list_value(config_values.get("BIBLIOGRAPHY_DELIMITER", ""))
        if not delimiter_values:
            return False, "BIBLIOGRAPHY_DELIMITER must contain at least one value."

        for break_item in self.parse_list_value(config_values.get("ARTICLE_BREAKS", "")):
            if not re.fullmatch(r"\d+:\d+", break_item):
                return False, f"Invalid ARTICLE_BREAKS entry: {break_item}. Expected format N:N."

        return True, ""

    def parse_config_line(self, line):
        """Parse a single line from configuration file."""
        line = line.strip()
        if not line or line.startswith("#"):
            return None, None

        if "=" not in line:
            return None, None

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        return key, value

    def parse_list_value(self, value):
        """Parse comma-separated quoted values from config."""
        if not value:
            return []

        # Match quoted strings
        matches = re.findall(r'"([^"]*)"', value)
        return matches

    def apply_loaded_config(self, config_values):
        """Apply parsed config values to UI fields."""
        self.debug_check.setChecked(config_values["DEBUG"].lower() == "true")

        self.special_case_list.clear()
        for item in self.parse_list_value(config_values["SPECIAL_CASE"]):
            self.special_case_list.addItem(item)

        self.delimiter_list.clear()
        for item in self.parse_list_value(config_values["BIBLIOGRAPHY_DELIMITER"]):
            self.delimiter_list.addItem(item)

        annot_idx = self.annot_type_combo.findText(config_values["ANNOT_TYPE"])
        if annot_idx >= 0:
            self.annot_type_combo.setCurrentIndex(annot_idx)

        color_idx = self.color_combo.findText(config_values["COLOR"])
        if color_idx >= 0:
            self.color_combo.setCurrentIndex(color_idx)

        offset_idx = self.offset_combo.findData(config_values["OFFSET"])
        if offset_idx >= 0:
            self.offset_combo.setCurrentIndex(offset_idx)

        self.article_breaks_list.clear()
        for item in self.parse_list_value(config_values["ARTICLE_BREAKS"]):
            self.article_breaks_list.addItem(item)

        self.soft_year_check.setChecked(config_values["SOFT_YEAR"].lower() == "true")
        self.deep_search_check.setChecked(config_values["DEEP_SEARCH"].lower() == "true")

        self.search_exclude_list.clear()
        for item in self.parse_list_value(config_values["SEARCH_EXCLUDE"]):
            self.search_exclude_list.addItem(item)

        self.alternative_bib_check.setChecked(config_values["ALTERNATIVE_BIB"].lower() == "true")
        self.list_widget_changed.emit("ALL", None)

    def load_config_dialog(self):
        """Open file dialog and load selected configuration file."""
        start_dir = self.get_config_dialog_start_dir()
        config_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Config File",
            start_dir,
            "Config files (*.config *.cfg *.txt);;All files (*)"
        )
        if not config_path:
            return

        self.config_path = config_path
        self.bridge.set_paths(config_path=self.config_path)
        self.load_config()

    def load_config(self):
        """Load configuration from file."""
        if not self.config_path or not os.path.exists(self.config_path):
            QMessageBox.warning(self, "Config Not Found",
                              f"Config file not found at: {self.config_path or 'unknown path'}")
            return

        try:
            config_values = self.parse_config_file(self.config_path)
            is_valid, error_message = self.validate_config_values(config_values)
            if not is_valid:
                QMessageBox.warning(
                    self,
                    "Invalid Config",
                    f"Selected config is invalid:\n{error_message}"
                )
                return
            self.apply_loaded_config(config_values)

            # QMessageBox.information(self, "Success", "Config loaded successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading config: {e}")

    def format_list_value(self, list_widget):
        """Format list widget items as comma-separated quoted strings."""
        items = []
        for i in range(list_widget.count()):
            items.append(f'"{list_widget.item(i).text()}"')
        return ", ".join(items) if items else ""

    def save_config(self):
        """Save configuration to file."""
        if not self.config_path:
            QMessageBox.warning(self, "No Config Path",
                              "Config path not set. Cannot save.")
            return

        try:
            # Build config content in correct order
            lines = []
            lines.append(f"DEBUG={self.debug_check.isChecked()}")

            special_case = self.format_list_value(self.special_case_list)
            lines.append(f"SPECIAL_CASE={special_case}")

            delimiter = self.format_list_value(self.delimiter_list)
            lines.append(f"BIBLIOGRAPHY_DELIMITER={delimiter}")

            lines.append(f"ANNOT_TYPE={self.annot_type_combo.currentText()}")
            lines.append(f"COLOR={self.color_combo.currentText()}")
            lines.append(f"OFFSET={self.offset_combo.currentData()}")

            article_breaks = self.format_list_value(self.article_breaks_list)
            lines.append(f"ARTICLE_BREAKS={article_breaks}")

            lines.append(f"SOFT_YEAR={self.soft_year_check.isChecked()}")
            lines.append(f"DEEP_SEARCH={self.deep_search_check.isChecked()}")

            search_exclude = self.format_list_value(self.search_exclude_list)
            lines.append(f"SEARCH_EXCLUDE={search_exclude}")

            lines.append(f"ALTERNATIVE_BIB={self.alternative_bib_check.isChecked()}")

            config_values = {}
            for line in lines:
                key, value = self.parse_config_line(line)
                if key:
                    config_values[key] = value
            is_valid, error_message = self.validate_config_values(config_values)
            if not is_valid:
                QMessageBox.warning(
                    self,
                    "Invalid Config",
                    f"Cannot save config:\n{error_message}"
                )
                return

            # Write to file
            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(lines))

            QMessageBox.information(self, "Success", f"Config saved to: {self.config_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving config: {e}")

    def save_config_as(self):
        """Save config using Save As dialog in active config directory."""
        if not self.config_path:
            QMessageBox.warning(self, "No Config Path", "Current config path is not set.")
            return

        current_config = Path(self.config_path).expanduser().resolve()
        suggested_name = f"{current_config.stem}_copy{current_config.suffix or '.config'}"
        suggested_path = str(current_config.parent / suggested_name)
        config_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Config As",
            suggested_path,
            "Config files (*.config *.cfg *.txt);;All files (*)"
        )
        if not config_path:
            return

        chosen_path = str(Path(config_path).expanduser().resolve())
        if chosen_path == str(current_config):
            QMessageBox.warning(
                self,
                "Choose Different Name",
                "Please choose a different filename than the currently active config."
            )
            return

        self.config_path = chosen_path
        self.bridge.set_paths(config_path=self.config_path)
        self.save_config()

    def clear_all_fields(self):
        """Clear all configuration fields."""
        self.debug_check.setChecked(False)
        self.special_case_list.clear()
        self.delimiter_list.clear()
        self.annot_type_combo.setCurrentIndex(0)
        self.color_combo.setCurrentIndex(0)
        self.offset_combo.setCurrentIndex(0)
        self.article_breaks_list.clear()
        self.soft_year_check.setChecked(False)
        self.deep_search_check.setChecked(False)
        self.search_exclude_list.clear()
        self.alternative_bib_check.setChecked(False)

        self.parent.clear_text_handlers()

        QMessageBox.information(self, "Cleared", "All fields cleared. Configure and save as needed.")

    def show_debug_output(self):
        """Toggle the debug output window visibility."""
        if self.parent and hasattr(self.parent, 'debug_output'):
            if self.parent.debug_output.isVisible():
                self.parent.debug_output.close()
            else:
                self.parent.debug_output.show()
                self.parent.debug_output.raise_()
                self.parent.debug_output.activateWindow()

    def article_cache_to_list(self, data):
        """Convert zero-based article cache to one-based string list for display."""
        full_list = []
        for pair in data:
            first = pair["first"] + 1
            last = pair["last"] + 1
            together= f"{first}:{last}"
            full_list.append(together)
        return full_list
    
    def article_list_to_cache(self, data):
        """Convert one-based string list to zero-based article cache."""
        cache = []
        for i in range(data.count()):
            tokens = data.item(i).text().split(":")
            # transform from 1 index to 0 index  count
            pair = {
                    "first": int(tokens[0]) -1,
                    "last": int(tokens[1]) -1
                    }
            cache.append(pair)
        return cache

    def set_data_from_view(self, config_data=None):
        """Update configuration from viewer data."""
        if config_data:
            if "article_cache" in config_data:
                self.article_cache = config_data["article_cache"]
                article_list = self.article_cache_to_list(self.article_cache)
                self.article_breaks_list.clear()
                self.article_breaks_list.addItems(article_list)


            if "special_cases" in config_data:
                self.special_cases = config_data["special_cases"]
                self.special_case_list.clear()
                for item in self.special_cases:
                    self.special_case_list.addItem(item)

            if "delimiters" in config_data:
                self.delimiters = config_data["delimiters"]
                self.delimiter_list.clear()
                for item in self.delimiters:
                    self.delimiter_list.addItem(item)
                     
        self.update()

    def list_widget_update(self, field_name, widget=None):
        """Update TextHandler when list widgets change."""
        text_handler = getattr(self.parent, "text_handler", None)
        if text_handler is None:
            return

        if field_name == "SPECIAL_CASE" or field_name == "ALL":
            self.special_cases.clear()
            for i in range(self.special_case_list.count()):
                self.special_cases.append(self.special_case_list.item(i).text())
            text_handler.special_cases = self.special_cases

        if field_name == "BIBLIOGRAPHY_DELIMITER" or field_name == "ALL":
            self.delimiters.clear()
            for i in range(self.delimiter_list.count()):
                self.delimiters.append(self.delimiter_list.item(i).text())
            text_handler.delimiters = self.delimiters

        if field_name == "ARTICLE_BREAKS" or field_name == "ALL":
            new_cache = self.article_list_to_cache(self.article_breaks_list)
            self.article_cache.clear()
            self.article_cache.extend(new_cache)
            text_handler.article_cache.clear()
            text_handler.article_cache.extend(new_cache)
                    


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = DocConfig()
    window.setWindowTitle("Document Configuration Manager")
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
