from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PySide6.QtCore import QPoint, Qt, Slot


class PopupWidget(QWidget):
    def __init__(self, parent=None, position=QPoint(0, 0), buttons=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.Popup)
        self.move(position)
        layout = QVBoxLayout(self)
        self.button_objs = {}
        if buttons:
            for btn_name in buttons:
                btn = QPushButton(btn_name, self)
                layout.addWidget(btn)
                self.button_objs[btn_name.lower()] = btn
        self.hide()

    @Slot()
    def show_at(self, position):
        self.move(position)
        self.show()
        print("position popup:" , position)

    def assign_buttons(self, buttons):
        if self.button_objs:
            self.clear_buttons()
        if buttons:
            for btn_name in buttons:
                btn = QPushButton(btn_name, self)
                layout.addWidget(btn)
                self.button_objs[btn_name.lower()] = btn

    def clear_buttons(self):
        while self.layout().count():
            item = self.layout().takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.button_objs.clear()
