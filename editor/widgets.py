import math
from PyQt5.QtWidgets import (
    QRadioButton,
    QVBoxLayout,
    QWidget,
    QGraphicsScene,
    QGraphicsView,
)
from PyQt5.QtCore import QLine, Qt
from PyQt5.QtGui import QColor, QPen, QKeyEvent, QPainter, QWheelEvent


class PEditorWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.initUI()

    def initUI(self):

        # vertical layout
        self.layout = QVBoxLayout()
        # reomve the default borders
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # graphics scene
        self.grahpic_scene = PGraphicsScene()

        # graphics view
        self.view = PGraphicsView(self.grahpic_scene, self)
        self.text = QRadioButton(self)
        self.text.setText("hello")
        self.text.move(150, 10)

        # self.view.setScene(self.grahpic_scene)
        self.layout.addWidget(self.view)

    # 1def addDebugContent(self):
    #     self.grahpic_scene


class PScene:
    def __init__(self) -> None:
        self.nodes = []
        self.edges = []

        # * scene height and width

        self.scene_height = 64_000
        self.scene_width = 64_000

        self.init_ui()

    def init_ui(self):
        self.grahpic_scene = PGraphicsScene()
        self.grahpic_scene.set_scene(self.scene_width, self.scene_height)

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)

    def remove_node(self, node):
        self.nodes.remove(node)

    def remove_edge(self, edge):
        self.edges.remove(edge)


class PGraphicsScene(QGraphicsScene):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        # * settings
        self.grid_size = 20
        self.grid_visible = True
        self._color_dark_background = QColor("#202225")

        self._color_light_background = QColor("#ffffff")

        self._color_light = QColor("#2F3136")

        self._color_dark = QColor("#40444B")

        self._pen_light = QPen(self._color_light)
        self._pen_light.setWidth(1)

        self._pen_dark = QPen(self._color_dark)
        self._pen_dark.setWidth(1)

        # * scene height and width
        self.scene_width, self.scene_height = 6000, 6000

        # * scene default position
        self.setSceneRect(
            self.scene_width // 2,
            self.scene_height // 2,
            self.scene_width,
            self.scene_height,
        )

        self.setBackgroundBrush(self._color_dark_background)

    # & Drawing a Grid Background in the Graphic Scene
    def drawBackground(self, painter, rect):
        """
        Creating a Grid as background
        """
        super().drawBackground(painter, rect)

        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.grid_size)
        first_top = top - (top % self.grid_size)

        lines_light, lines_dark = [], []

        for x_cordinate in range(first_left, right, self.grid_size):
            if x_cordinate % 100 == 0:
                lines_dark.append(QLine(x_cordinate, top, x_cordinate, bottom))
                continue
            lines_light.append(QLine(x_cordinate, top, x_cordinate, bottom))

        for y_cordinate in range(first_top, bottom, self.grid_size):
            if y_cordinate % 100 == 0:
                lines_dark.append(QLine(left, y_cordinate, right, y_cordinate))
                continue
            lines_light.append(QLine(left, y_cordinate, right, y_cordinate))

        if self.grid_visible:
            painter.setPen(self._pen_light)
            painter.drawLines(*lines_light)

            painter.setPen(self._pen_dark)
            painter.drawLines(*lines_dark)


class PGraphicsView(QGraphicsView):
    """
    Additional settings and Features for `QGraphicsView`
    """

    def __init__(self, graphics_scene: QGraphicsScene, parent=None) -> None:
        super().__init__(parent)
        self.graphics_scene = graphics_scene

        self.initUI()

        self.setScene(self.graphics_scene)
        self.zoom_in_factor = 1.25
        self.zoomClamp = True
        self.zoom = 10
        self.zoom_step = 1
        self.zoom_range = [0, 10]

    def initUI(self) -> None:
        self.setRenderHints(
            QPainter.Antialiasing
            | QPainter.HighQualityAntialiasing
            | QPainter.TextAntialiasing
            | QPainter.SmoothPixmapTransform
        )
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    # & Space Hold left Click to Navigate Like PhotoShop Navigation.

    def keyPressEvent(self, event: QKeyEvent) -> None:
        # * detect [space] key press event

        if event.key() == Qt.Key.Key_Space:
            self.spaceKeyPress(event)
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        # * detect [space] key release event

        if event.key() == Qt.Key.Key_Space:
            self.spaceKeyRelease(event)
        else:
            super().keyReleaseEvent(event)

    def spaceKeyPress(self, event: QKeyEvent) -> None:
        # * Cursor Changes to Hand

        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def spaceKeyRelease(self, event: QKeyEvent) -> None:

        # * on release Cursor changes to default mouse pointer
        # * since [space] is auto repating key we ignore, until it is released
        if event.isAutoRepeat():
            return
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        print("released")

    # & Zoom feature using Scroll Wheel

    def wheelEvent(self, event: QWheelEvent) -> None:
        # * calculate zoom out factor
        zoom_out_factor = 1 / self.zoom_in_factor
        zoom_factor = 0.0
        # * calculate zoom
        if event.angleDelta().y() > 0:
            zoom_factor = self.zoom_in_factor
            self.zoom += self.zoom_step
        else:
            zoom_factor = zoom_out_factor
            self.zoom -= self.zoom_step

        clamped = False
        if self.zoom < self.zoom_range[0]:
            self.zoom, clamped = self.zoom_range[0], True
        if self.zoom > self.zoom_range[1]:
            self.zoom, clamped = self.zoom_range[1], True

        if not clamped or self.zoomClamp is False:
            self.scale(zoom_factor, zoom_factor)

        return super().wheelEvent(event)

    # & Middle Mouse Button for Navigation like photoshop Navigation
    # def mousePressEvent(self, event):
    #     if event.button() == Qt.MiddleButton:
    #         self.middleMouseButtonPress(event)
    #     elif event.button() == Qt.LeftButton:
    #         self.rightMouseButtonPress(event)
    #     elif event.button() == Qt.RightButton:
    #         self.rightMouseButtonPress(event)
    #     else:
    #         super().mousePressEvent(event)

    # z def mouseReleaseEvent(self, event):
    #     if event.button() == Qt.MiddleButton:
    #         self.middleMouseButtonRelease(event)
    #     elif event.button() == Qt.LeftButton:
    #         self.leftMouseButtonRelease(event)
    #     elif event.button() == Qt.RightButton:
    #         self.rightMouseButtonRelease(event)
    #     else:
    #         super().mouseReleaseEvent(event)

    # z def middleMouseButtonPress(self, event):
    #     release_event = QMouseEvent(
    #         QEvent.MouseButtonRelease,
    #         event.localPos(),
    #         event.screenPos(),
    #         Qt.LeftButton,
    #         Qt.NoButton,
    #         event.modifiers(),
    #     )
    #     super().mouseReleaseEvent(release_event)
    #     self.setDragMode(QGraphicsView.ScrollHandDrag)
    #     fake_event = QMouseEvent(
    #         event.type(),
    #         event.localPos(),
    #         event.screenPos(),
    #         Qt.LeftButton,
    #         event.buttons() | Qt.LeftButton,
    #         event.modifiers(),
    #     )
    #     super().mousePressEvent(fake_event)

    # z def middleMouseButtonRelease(self, event):
    #     fake_event = QMouseEvent(
    #         event.type(),
    #         event.localPos(),
    #         event.screenPos(),
    #         Qt.LeftButton,
    #         event.buttons() & ~Qt.LeftButton,
    #         event.modifiers(),
    #     )
    #     super().mouseReleaseEvent(fake_event)
    #     self.setDragMode(QGraphicsView.NoDrag)

    # z def leftMouseButtonPress(self, event):
    #     return super().mousePressEvent(event)

    # z def leftMouseButtonRelease(self, event):
    #     return super().mouseReleaseEvent(event)

    # z def rightMouseButtonPress(self, event):
    #     return super().mousePressEvent(event)

    # z def rightMouseButtonRelease(self, event):
    #     return super().mouseReleaseEvent(event)
