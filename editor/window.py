from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QAction,
    QDesktopWidget,
    QMainWindow,
)

from editor.widgets import PEditorWidget
import globals


class PWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.window_position()
        self.p_menuBar()

        self.peditor_widget = PEditorWidget()

        self.setCentralWidget(self.peditor_widget)

        # * set window title
        self.setWindowTitle("proi")
        self.setFont(QFont(globals.DEFAULT_FONT))
        # * display the UI
        self.show()

    def p_menuBar(self) -> None:

        menubar = self.menuBar()
        filemenu = menubar.addMenu("View")

        # New Option
        action_new = QAction("Show Grid", self)
        action_new.setFont(QFont(globals.DEFAULT_FONT))
        # action_new.setShortcut("Ctrl+N")
        action_new.setToolTip("Show Grid in the Editor")
        action_new.triggered.connect(self.onClickNew)
        filemenu.addAction(action_new)

    def onClickNew(self):
        self.peditor_widget.graphic_scene.grid_visible = (
            not self.peditor_widget.graphic_scene.grid_visible
        )
        self.peditor_widget.graphic_scene.update()
        print("clicked ")

    def window_position(self) -> None:
        # * get the display size.
        display_resolution = QDesktopWidget().screenGeometry(-1)
        # * set the initial window size and position
        self.setGeometry(
            0, 0, display_resolution.width() / 2, display_resolution.height() / 2
        )
        # * set the window in the middle
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
