"""
Status bar widget displaying citation linking statistics.
Shown below PDF viewers after linking completes.
"""
from    PySide6.QtCore                  import  Qt, Signal, Slot
from    PySide6.QtGui                   import  QColor
from    PySide6.QtWidgets               import  (QWidget,
                                                 QPushButton,
                                                 QHBoxLayout,
                                                 QCheckBox,
                                                 QLabel)


class LinkingStatsBar(QWidget):
    """ 
    narrow status bar showing citation linking results below the pdf viewers.

    This class displays linking statistics and a highlight control including:
    - Citations: N | Bibliography: N | Linked: N, each clickable to open the debug output on the relevant tab
    - Linked count color-coded by ratio (green >=80%, amber 50-80%, red <50%)
    - A "Highlight all" checkbox to toggle highlighting of all possible citation/bibliography entries
    - Hover tooltips showing valid-vs-total breakdowns
    """

    open_debug_tab = Signal(str)  # "citations" | "bibliography" | "linked"
    show_all_citations = Signal(bool)

    def __init__(self, parent=None):
        """Initialize the stats bar with stat labels, buttons, and the highlight checkbox."""
        super().__init__(parent)
        self.setMaximumHeight(28)
        self.setVisible(False)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(6)

        left_spacer = QWidget()
        left_spacer.setFixedWidth(0)
        layout.addWidget(left_spacer)

        self._cit_label = QLabel("Citations:")
        self._cit_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self._cit_label)

        self._cit_btn = QPushButton("0")
        self._cit_btn.setFlat(True)
        self._cit_btn.setCursor(Qt.PointingHandCursor)
        self._cit_btn.setToolTip("")
        self._cit_btn.setStyleSheet("border: none; padding: 0 4px; font-weight: bold;")
        self._cit_btn.clicked.connect(lambda: self.open_debug_tab.emit("citations"))
        layout.addWidget(self._cit_btn)

        sep1 = QLabel("|")
        sep1.setStyleSheet("color: gray;")
        layout.addWidget(sep1)

        self._bib_label = QLabel("Bibliography:")
        self._bib_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self._bib_label)

        self._bib_btn = QPushButton("0")
        self._bib_btn.setFlat(True)
        self._bib_btn.setCursor(Qt.PointingHandCursor)
        self._bib_btn.setToolTip("")
        self._bib_btn.setStyleSheet("border: none; padding: 0 4px; font-weight: bold;")
        self._bib_btn.clicked.connect(lambda: self.open_debug_tab.emit("bibliography"))
        layout.addWidget(self._bib_btn)

        sep2 = QLabel("|")
        sep2.setStyleSheet("color: gray;")
        layout.addWidget(sep2)

        self._linked_label = QLabel("Linked:")
        self._linked_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self._linked_label)

        self._linked_btn = QPushButton("0")
        self._linked_btn.setFlat(True)
        self._linked_btn.setCursor(Qt.PointingHandCursor)
        self._linked_btn.setToolTip("")
        self._linked_btn.setStyleSheet("border: none; padding: 0 4px; font-weight: bold;")
        self._linked_btn.clicked.connect(lambda: self.open_debug_tab.emit("linked"))
        layout.addWidget(self._linked_btn)

        self._show_all = QCheckBox("Highlight all")
        self._show_all.setCursor(Qt.PointingHandCursor)
        self._show_all.setToolTip("")
        self._show_all.toggled.connect(self.on_show_all_toggled)
        layout.addWidget(self._show_all)


        layout.addStretch()

        self._valid_cit = 0
        self._total_cit = 0
        self._valid_bib = 0
        self._total_bib = 0
        self._linked = 0

    @Slot(int, int, int, int, int, int, int)
    def set_stats(self, valid_cit, total_cit, valid_bib, total_bib, linked,
                  certain_cit, certain_bib):
        """Update displayed counts and show the bar."""
        self._valid_cit = valid_cit
        self._total_cit = total_cit
        self._valid_bib = valid_bib
        self._total_bib = total_bib
        self._linked = linked

        self._cit_btn.setText(str(valid_cit))
        self._bib_btn.setText(str(valid_bib))
        self._linked_btn.setText(str(linked))

        # Tooltips with breakdown
        cit_tip = f"{valid_cit} valid citations out of {total_cit} total citations found"
        if certain_cit > 0:
            cit_tip += f"\n{certain_cit} certain matches (both surname & name known)"
        self._cit_btn.setToolTip(cit_tip)

        bib_tip = f"{valid_bib} valid bibliography entries out of {total_bib} total entries found"
        if certain_bib > 0:
            bib_tip += f"\n{certain_bib} certain matches (both surname & name known)"
        self._bib_btn.setToolTip(bib_tip)

        ratio_pct = self._linked_ratio_pct()
        tip = f"{linked} citations successfully linked"
        if valid_cit > 0:
            tip += f" ({ratio_pct:.0f}% of valid citations)"
        self._linked_btn.setToolTip(tip)

        self._refresh_show_tip()

        # Color-code the linked count
        self._apply_color()

        self.setVisible(True)

    @Slot()
    def on_show_all_toggled(self, checked):
        """Emit show_all_citations when the 'Highlight all' checkbox is toggled."""
        self.show_all_citations.emit(checked)
        self._refresh_show_tip()

    def _refresh_show_tip(self):
        """Update the 'Highlight all' checkbox tooltip with its current state."""
        state = "ON" if self._show_all.isChecked() else "OFF"
        self._show_all.setToolTip(f"see all possible citations and Bibliography entries. Current state: {state}")

    def _linked_ratio_pct(self):
        """Return the percentage of valid citations that were linked."""
        if self._valid_cit == 0:
            return 0.0
        return (self._linked / self._valid_cit) * 100.0

    def _apply_color(self):
        """Color-code the linked count by ratio (green, amber, or red)."""
        ratio = self._linked_ratio_pct()
        if ratio >= 80:
            color = "#2e7d32"  # green
        elif ratio >= 50:
            color = "#e6a817"  # yellow/amber
        else:
            color = "#c62828"  # red

        # Reset all buttons to default, then set linked's color
        default_style = "border: none; padding: 0 4px; font-weight: bold;"
        self._cit_btn.setStyleSheet(default_style)
        self._bib_btn.setStyleSheet(default_style)
        self._linked_btn.setStyleSheet(f"{default_style} color: {color};")

    def hide(self):
        """Hide the stats bar."""
        super().hide()
