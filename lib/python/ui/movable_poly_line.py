from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsItemGroup, QGraphicsPixmapItem, QGraphicsEllipseItem, QFrame, QFileDialog, QPushButton
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPolygonF, QColor
from PyQt5.QtCore import QPoint, QPointF, QRectF
import numpy as np

class MovablePolyLine(QGraphicsItem):
    def __init__(self, parent=None):
        super(MovablePolyLine, self).__init__(parent)
        self.setZValue(1000)
        self.polygon = QPolygonF()
        self.radius = 5.0
        self.circleList = []
        self.rect = QRectF()
        self.color = QColor(255,0,0)
        # self.setHandlesChildEvents(False)
        # self.setFlags(QGraphicsItem.ItemIsMovable)

    def setRadius(self, r):
        self.radius = r

    def setColor(self, rgb):
        self.color = QColor(*rgb)

    def getRadius(self):
        return self.radius

    def setPoints(self, ps):
        scene = self.scene()
        if scene is not None:
            for circle in self.circleList:
                scene.removeItem(circle)
                del circle
        self.circleList.clear()

        self.points = np.array(ps)

        radii = 2*self.radius
        rectList = [QRectF(-self.radius, -self.radius, radii, radii) for p in self.points]
        self.circleList = [QGraphicsEllipseItem(self) for rect in rectList]
        for circle, point, rect in zip(self.circleList, self.points[:,], rectList):
            circle.setBrush(self.color)
            circle.setRect(rect)
            circle.setPos(*point)

            circle.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsScenePositionChanges)
            circle.setAcceptHoverEvents(True)
            circle.mouseMoveEvent = self.generateCircleMouseMoveEvent(circle, point)

    def setRect(self, rect):
        self.rect = rect

    def generateCircleMouseMoveEvent(self, circle, point):
        def circleMouseMoveEvent(event):
            QGraphicsEllipseItem.mouseMoveEvent(circle, event)
            centerPos = circle.scenePos()

            point[0] = centerPos.x()
            point[1] = centerPos.y()
            self.update()
        return circleMouseMoveEvent

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget):
        painter.save()

        painter.setPen(self.color)
        qPoints = [QPointF(*p.tolist()) for p in self.points]
        polygon = QPolygonF(qPoints)
        painter.drawPolyline(polygon)

        painter.restore()
