import  pymupdf
from    PySide6.QtCore  import  QPointF, QPoint, QRectF, QSizeF, QRect, QSize


""" 
rect info
"rect": Qrect or QRectF,
"current_zoom": zoom factor (float)
"""


def point_py_to_qt(point_py):
    point_qt = QPointF(point_py.x, point_py.y)
    return point_qt

def point_qt_to_py(point_qt):
    point_py = pymupdf.Point(point_qt.x(), point_qt.y())
    return point_py

def rect_py_to_qt(rect_py):
    top_left = point_py_to_qt(rect_py.top_left)
    bottom_right = point_py_to_qt(rect_py.bottom_right)
    rect_qt = QRectF(top_left, bottom_right)
    return rect_qt

def rect_qt_to_py(rect_qt):
    top_left = point_qt_to_py(rect_qt.topLeft())
    bottom_right = point_qt_to_py(rect_qt.bottomRight())
    rect_py = pymupdf.Rect(top_left, bottom_right)
    return rect_py

def point_to_px(point, zoom_factor):
    new_point = QPoint(0,0)
    new_point.setX(point.x() / zoom_factor)
    new_point.setY(point.y() / zoom_factor)
    return new_point


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

