from typing import Optional

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget, QDialog

from qutewindow.platforms.mac.utils import merge_content_area_and_title_bar, setWindowNonResizable


class QuteDialog(QDialog):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        merge_content_area_and_title_bar(self.winId())

    def setNonResizable(self):
        setWindowNonResizable(self.winId())

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if not self.isFullScreen() and self.isTitleBarArea(event.pos()):
            self.toggleMaximized()

    def isTitleBarArea(self, pos: QPoint) -> bool:
        title_bar_height = self.titleBarHeight()
        return pos.y() <= title_bar_height

    def titleBarHeight(self) -> int:
        return 30

    def toggleMaximized(self) -> None:
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
