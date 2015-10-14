import sys

from PyQt5 import QtWidgets, QtCore

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene

from PyQt5.QtCore import pyqtSlot, QRectF
from PyQt5.QtGui import QPainter

__version__ = '0.0.1'
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class OverlaidGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super(OverlaidGraphicsView, self).__init__(parent)
        self.m_overlayScene = QGraphicsScene()

    def setOverlayScene(self, scene):
        if scene is self.m_overlayScene:
            return

        self.m_overlayScene = scene
        scene.changed.connect(self.overlayChanged)
        self.update()

    def overlayScene(self):
        return self.m_overlayScene

    def paintEvent(self, ev):
        super(OverlaidGraphicsView, self).paintEvent(ev)
        if self.m_overlayScene is not None:
            self.paintOverlay()

    def paintOverlay(self):
        p = QPainter(self.viewport())
        p.setRenderHints(self.renderHints())

        sourceRect = self.scene().sceneRect()
        targetRect = self.mapFromScene(sourceRect).boundingRect()

        self.m_overlayScene.render(p, QRectF(targetRect), QRectF(sourceRect), QtCore.Qt.IgnoreAspectRatio)

    @pyqtSlot()
    def overlayChanged(self):
        self.update()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    widget = OverlaidGraphicsView(MainWindow)
    MainWindow.setCentralWidget(widget)

    MainWindow.show()
    sys.exit(app.exec_())
