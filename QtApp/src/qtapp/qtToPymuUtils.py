import  pymupdf
from    PySide6.QtCore  import  QPointF, QRectF, QSizeF, QRect, QSize


def rect_py_to_qt(rect_py):
    top_left = QPointF(rect_py.top_left.x, rect_py.top_left.y)
    bottom_right = QPointF(rect_py.bottom_right.x, rect_py.bottom_right.y)
    rect_qt = QRectF(top_left, bottom_right)
    return rect_qt

def rect_qt_to_py(rect_qt):
    top_left = pymupdf.Point(rect_qt.topLeft().x(), rect_qt.topLeft().y())
    bottom_right = pymupdf.Point(rect_qt.bottomRight().x(), rect_qt.bottomRight().y())
    rect_py = pymupdf.Rect(top_left, bottom_right)
    return rect_py

def px_to_dpi(rect_info):
    rect = rect_info["rect"]
    zoom_factor = rect_info["current_zoom"]

    page_rect = QRectF()
    page_sizeF = QSizeF()
    page_sizeF.setWidth(rect.width() / zoom_factor)
    page_sizeF.setHeight(rect.height() / zoom_factor)
    page_rect.setX(rect.x() / zoom_factor)
    page_rect.setY(rect.y() / zoom_factor)
    page_rect.setSize(page_sizeF)

    return page_rect

def dpi_to_px(rect_info):
    rect = rect_info["rect"]
    zoom_factor = rect_info["current_zoom"]

    view_rect = QRect()
    view_size = QSize()
    view_size.setWidth(rect.width() * zoom_factor)
    view_size.setHeight(rect.height() * zoom_factor)
    view_rect.setX(rect.x() * zoom_factor)
    view_rect.setY(rect.y() * zoom_factor)
    view_rect.setSize(view_size)
    
    return view_rect

