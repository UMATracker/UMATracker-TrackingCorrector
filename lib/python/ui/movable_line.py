from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsItemGroup, QGraphicsPixmapItem, QGraphicsItem, QFrame, QFileDialog, QPushButton, QGraphicsObject, QGraphicsPathItem, QGraphicsRectItem
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPolygonF, QColor, QPen, QBrush, QPainterPath
from PyQt5.QtCore import QPoint, QPointF, QRectF, QSizeF, Qt, QLineF, pyqtSignal, QObject

import numpy as np
import pandas as pd


class MovableLineGroup(QGraphicsObject):
    edited = pyqtSignal(object)

    def __init__(self, parent=None):
        super(MovableLineGroup, self).__init__(parent)

        self.setZValue(9)
        self.data = None
        self.itemList = []
        self.rectItemsList = []
        self.rect = QRectF()

        self.isItemMovable = True
        self.drawLineFlag = True

        self.num_items = 0
        self.currentFrameNo = 0
        self.lineWidth = 2
        self.markSize = 2

    def setData(self, data):
        self.data = data

        self.num_items = len(data[str(0)])
        print(self.num_items)
        self.colors = [Qt.red for rgb in range(self.num_items)]

        scene = self.scene()
        if scene is not None:
            for item in self.itemList:
                scene.removeItem(item)
                del item
        self.itemList.clear()

        for i, rgb in enumerate(self.colors):
            self.rectItemsList.append([])

    # def setItemsAreMovable(self, flag):
    #     self.areItemsMovable = flag
    #
    #     for item in self.itemList:
    #         item.setItemIsMovable(flag)

    def setPolyline(self, frameNo=None):
        if frameNo is not None:
            self.currentFrameNo = frameNo

            key = str(self.currentFrameNo)
            if key in self.data.keys():
                self.show()

                for i, rectItems in enumerate(self.rectItemsList):
                    poly = QPolygonF()
                    line_data = self.data[key][i]

                    current_range = len(rectItems)
                    for j in range(current_range, len(line_data)):
                        rectItems.append(QGraphicsRectItem(self))

                    for p, rect_item in zip(line_data, rectItems):
                        q_pt = QPointF(*p)
                        rect_item.setPos(q_pt)
                        rect_item.mouseMoveEvent = self.generateItemMouseMoveEvent(rect_item, p)

                        rect = QRectF(-self.markSize/2, -self.markSize/2, self.markSize, self.markSize)
                        rect_item.setRect(rect)

                        rect_item.show()

                    for j in range(len(line_data), len(rectItems)):
                        rectItems[j].hide()

                self.setItemsAreMovable(self.isItemMovable)

            else:
                self.hide()

    def getColors(self):
        return self.colors

    def setRect(self, rect):
        self.rect = rect

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget):
        pass

    def setLineWidth(self, w):
        self.lineWidth = w
        self.update()

    def getLineWidth(self):
        return self.lineWidth

    def getMarkSize(self):
        return self.markSize

    def setMarkSize(self, s):
        self.markSize = s
        self.update()

    def autoAdjustLineWidth(self, shape):
        # TODO: かなり適当
        m = np.max(shape)
        lw = max(float(2.5*m/600), 1.0)
        self.setLineWidth(lw)
        self.update()
        return self.getLineWidth()

    def autoAdjustMarkSize(self, shape):
        # TODO: かなり適当
        m = np.max(shape)
        r = max(float(2.5*m/600), 1.0)
        self.setMarkSize(r)
        self.update()
        return int(self.getMarkSize())

    def changeMovableLineColor(self, i, color):
        self.colors[i] = color
        self.update()

    def setColors(self, colors):
        self.colors = colors
        self.update()

    def generateItemMouseMoveEvent(self, item, point):
        def itemMouseMoveEvent(event):
            QGraphicsRectItem.mouseMoveEvent(item, event)
            centerPos = item.scenePos()

            point[0] = centerPos.x()
            point[1] = centerPos.y()

            self.update()
        return itemMouseMoveEvent

    def setItemsAreMovable(self, flag):
        self.isItemMovable = flag

        if self.isItemMovable:
            for itemList in self.rectItemsList:
                for item in itemList:
                    item.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsScenePositionChanges)
        else:
            for itemList in self.rectItemsList:
                for item in itemList:
                    item.setFlag(QGraphicsItem.ItemIsMovable, False)
                    item.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, False)

    def setDrawLine(self, flag):
        self.drawLineFlag = flag

    def paint(self, painter, option, widget):
        if self.data is not None and self.drawLineFlag:
            painter.save()

            key = str(self.currentFrameNo)
            if key in self.data.keys():
                line_data = self.data[key]

                for line, color in zip(line_data, self.colors):
                    pen = QPen(color)
                    pen.setWidthF(self.lineWidth)

                    painter.setPen(pen)
                    qPoints = [QPointF(*p) for p in line]
                    polygon = QPolygonF(qPoints)
                    painter.drawPolyline(polygon)

            painter.restore()

