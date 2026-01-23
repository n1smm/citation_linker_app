"""
Popup context menu widget for annotation and citation actions.
"""
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PySide6.QtCore import QPoint, Qt, Slot


class PopupWidget(QWidget):
    """
    Popup menu widget for context-sensitive actions.
    
    Parent: QWidget (with Qt.Popup flag)
    Children: QPushButton instances
    
    Provides switchable button sets for different contexts:
    - Main buttons: bibliography, special_case (input mode)
    - Main buttons: add_link, add_destination (output mode)
    - Alt buttons: delete (for existing annotations/links)
    """
    def __init__(self, parent=None, position=QPoint(0, 0), buttons=None):
        """Initialize popup with buttons at specified position."""
        super().__init__(parent)
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PySide6.QtCore import QPoint, Qt, Slot


class PopupWidget(QWidget):
    def __init__(self, parent=None, position=QPoint(0, 0), buttons=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.Popup)
        self.move(position)
        self.layout = QVBoxLayout(self)
        self.button_objs = {}
        if buttons:
            for btn_name in buttons:
                btn = QPushButton(btn_name, self)
                self.layout.addWidget(btn)
                self.button_objs[btn_name.lower()] = btn
        self.alt_buttons = {}
        self.alt = False
        self.hide()

    @Slot()
    def show_at(self, position, alt=False):
        self.switch_buttons_to(alt)
        self.move(position)
        self.show()
        # print("position popup:" , position)

    def assign_buttons(self, buttons):
        if self.button_objs:
            self.clear_buttons()
        if buttons:
            for btn_name in buttons:
                btn = QPushButton(btn_name, self)
                self.layout.addWidget(btn)
                self.button_objs[btn_name.lower()] = btn
        if self.alt_buttons:
            self.hide_buttons(True)



    def assign_alt_buttons(self, buttons):
        if self.alt_buttons:
            self.clear_buttons(True)
        if buttons:
            for btn_name in buttons:
                btn = QPushButton(btn_name, self)
                self.layout.addWidget(btn)
                self.alt_buttons[btn_name.lower()] = btn
        if self.button_objs:
            self.hide_buttons()

    def hide_buttons(self, alt=False):
        if not alt:
            for btn in self.alt_buttons.values():
                btn.hide()
            self.alt = True
        else:
            for btn in self.button_objs.values():
                btn.hide()
            self.alt = False

    @Slot()
    def switch_buttons_to(self, alt=False):
        if alt:
            self.hide_buttons(alt)
            for btn in self.alt_buttons.values():
                btn.show()
            self.alt = True
        else:
            self.hide_buttons(alt)
            for btn in self.button_objs.values():
                btn.show()
            self.alt = False

    def clear_buttons(self, alt=False):
        layout = self.layout
        if layout is None:
            return
        if alt:
            for btn in self.alt_buttons.values():
                layout.removeWidget(btn)
                btn.deleteLater()
            self.alt_buttons.clear()
        else:
            for btn in self.button_objs.values():
                layout.removeWidget(btn)
                btn.deleteLater()
            self.button_objs.clear()

