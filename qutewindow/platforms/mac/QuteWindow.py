from typing import Optional

from AppKit import NSView, NSMakeRect, NSWindow, NSWindowCloseButton, NSWindowMiniaturizeButton, NSWindowZoomButton
from Quartz.CoreGraphics import (CGEventCreateMouseEvent,
                                 kCGEventLeftMouseDown, kCGMouseButtonLeft)

from ctypes import c_void_p
from functools import reduce
import Cocoa
import objc

from PySide6.QtCore import Qt, QPoint, QSize
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QDialog, QFrame


class QuteWindow(QDialog):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        QDialog.__init__(self, parent)
        self.setWindowFlags(Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.createWinId()
        QuteWindow.merge_content_area_and_title_bar(self.winId())
        self.setVibrancyEffect()

    @staticmethod
    def merge_content_area_and_title_bar(win_id: int) -> None:
        viewPtr = c_void_p(win_id)
        nsview = objc.objc_object(c_void_p=viewPtr)

        nswin = nsview.window()

        styleMasks = (
            nswin.styleMask(),
            Cocoa.NSWindowStyleMaskFullSizeContentView,
            Cocoa.NSWindowTitleHidden,
            Cocoa.NSWindowStyleMaskClosable,
            Cocoa.NSWindowStyleMaskMiniaturizable,
            Cocoa.NSWindowStyleMaskResizable,
            Cocoa.NSWindowStyleMaskFullSizeContentView
        )
        nswin.setStyleMask_(reduce(lambda a, b: a | b, styleMasks, 0))

        nswin.setTitlebarAppearsTransparent_(True)
        nswin.setMovableByWindowBackground_(False)

    @staticmethod
    def setTrafficLightsPosition(win_id: int, pos = QPoint(0, 0)) -> None:
        viewPtr = c_void_p(win_id)
        nsview = objc.objc_object(c_void_p=viewPtr)
        window = nsview.window()

        box_size = QSize(72, 30)

        # Create an instance of NSView
        trafficLightsView = NSView.alloc().initWithFrame_(NSMakeRect(pos.x(), pos.y(), box_size.width(), box_size.height()))

        # Add the trafficLightsView as a subview of the window's contentView
        window.contentView().addSubview_(trafficLightsView)

        # Get the standard window buttons
        closeButton = window.standardWindowButton_(NSWindowCloseButton)
        minimizeButton = window.standardWindowButton_(NSWindowMiniaturizeButton)
        maximizeButton = window.standardWindowButton_(NSWindowZoomButton)

        # Add the buttons as subviews of the trafficLightsView
        trafficLightsView.addSubview_positioned_relativeTo_(closeButton, Cocoa.NSWindowAbove, None)
        trafficLightsView.addSubview_positioned_relativeTo_(minimizeButton, Cocoa.NSWindowAbove, None)
        trafficLightsView.addSubview_positioned_relativeTo_(maximizeButton, Cocoa.NSWindowAbove, None)

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

    def startSystemMove(self, pos) -> None:
        view = objc.objc_object(c_void_p=c_void_p(int(self.winId())))
        window = view.window()

        cgEvent = CGEventCreateMouseEvent(
            None, kCGEventLeftMouseDown, (pos.x(), pos.y()), kCGMouseButtonLeft)
        clickEvent = Cocoa.NSEvent.eventWithCGEvent_(cgEvent)

        if clickEvent:
            window.performWindowDragWithEvent_(clickEvent)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.isTitleBarArea(event.pos()):
            self.startSystemMove(event.globalPos())

    def setVibrancyEffect(self) -> None:
        new_widget = QWidget(self)
        new_widget.move(0, 0)
        new_widget.resize(self.size())
        frame = Cocoa.NSMakeRect(0, 0, new_widget.width(), new_widget.height())
        visualEffectView = Cocoa.NSVisualEffectView.alloc().initWithFrame_(frame)
        visualEffectView.setAutoresizingMask_(Cocoa.NSViewWidthSizable | Cocoa.NSViewHeightSizable)
        visualEffectView.setAllowsVibrancy_(True)
        view = objc.objc_object(c_void_p=c_void_p(int(new_widget.winId())))
        window = view.window()
        contentView = window.contentView()
        contentView.addSubview_positioned_relativeTo_(visualEffectView, Cocoa.NSWindowBelow, new_widget)
