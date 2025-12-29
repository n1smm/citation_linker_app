from    PySide6.QtPdfWidgets    import QPdfView
from    PySide6.QtWidgets       import QComboBox
from    PySide6.QtCore          import Signal, Slot



class ZoomSelector(QComboBox):
    
    zoom_mode_changed = Signal(QPdfView.ZoomMode)
    zoom_factor_changed = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        
        self.setEditable(True)


        self.addItem("Fit Width") # 0
        self.addItem("Fit Page") # 1
        self.addItem("12%") # 2
        self.addItem("25%") # 3
        self.addItem("33%") # 4
        self.addItem("50%") # 5
        self.addItem("66%") # 6
        self.addItem("75%") # 7
        self.addItem("100%") # 8
        self.addItem("125%") # 9
        self.addItem("150%") # 10
        self.addItem("200%") # 11
        self.addItem("400%") # 12
        self.addItem("152%") # 13


        self.currentTextChanged.connect(self.on_current_text_changed)
        self.lineEdit().editingFinished.connect(self.editing_finished)

    @Slot()
    def set_zoom_factor(self, zoomFactor):
        percent = int(zoomFactor * 100)
        self.setCurrentText(f"{percent}%")

    @Slot()
    def reset(self):
        self.setCurrentIndex(8)

    @Slot()
    def on_current_text_changed(self, text):
        if text == "Fit Width":
            self.zoom_mode_changed.emit(QPdfView.ZoomMode.FitToWidth)
        elif text == "Fit Page":
            self.zoom_mode_changed.emit(QPdfView.ZoomMode.FitInView)
        elif text.endswith("%"):
            factor = 1.0
            zoom_level = int(text[:-1])
            factor = zoom_level / 100.0
            self.zoom_mode_changed.emit(QPdfView.ZoomMode.Custom)
            self.zoom_factor_changed.emit(factor)

    @Slot()
    def editing_finished(self):
        self.on_current_text_changed(self.lineEdit().text())
