from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsItemGroup, QGraphicsPixmapItem, QGraphicsItem, QFrame, QFileDialog, QPushButton, QGraphicsObject, QGraphicsLineItem
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPolygonF, QColor, QPen, QBrush, QPainterPath
from PyQt5.QtCore import QPoint, QPointF, QRectF, QSizeF, Qt, QLineF, pyqtSignal, QObject

import numpy as np
import pandas as pd


def ang(v1, v2):
    cosang = np.dot(v1, v2)
    sinang = numpy.linalg.norm(np.cross(v1, v2))
    return np.arctan2(sinang, cosang)


class MovableArrow(QGraphicsLineItem):
    def __init__(self, parent=None):
        super(MovableArrow, self).__init__(parent)
        self.setZValue(1000)

        self.arrowHead = QPolygonF()
        self.begin = np.array([0.0, 0.0])
        self.end =np.array([10.0, 10.0])

        self.myColor = Qt.black
        self.setPen(QPen(self.myColor, 5))
        self.arrowSize = 7
        self.setOpacity(0.5)

        self.isMousePressed = False
        self.setFlags(QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemIsFocusable |
                      #QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemSendsGeometryChanges
                      )

        self.name = None

    def setName(self, name):
        self.name = name

    def setPosition(self, begin, end):
        self.begin = begin
        self.end = end

    def boundingRect(self):
        extra = (self.pen().width() + 20) / 2.0
        size = QSizeF(
                1.3*(self.line().p1().x() - self.line().p2().x()),
                1.3*(self.line().p1().y() - self.line().p2().y())
                )

        return QRectF(self.line().p2(), size).normalized().adjusted(-extra, -extra, extra, extra)

    def shape(self):
        path = super(MovableArrow, self).shape()
        path.addPolygon(self.arrowHead)
        return path

    def setColor(self, rgb):
        self.myColor = rgb
        self.shape()

    def updatePosition(self):
        line = QLineF(QPointF(*self.end), QPointF(*self.begin))
        self.setLine(line)
        self.shape()

    def paint(self, painter, option, widget=None):
        self.updatePosition()

        myPen = self.pen()
        myPen.setColor(self.myColor)
        painter.setPen(myPen)
        # painter.setBrush(self.myColor)

        try:
            angle = np.arccos(self.line().dx() / self.line().length())
        except ZeroDivisionError:
            angle = 0.0
        if self.line().dy() >= 0:
            angle = (np.pi * 2) - angle;

        l = self.line().length()*0.1
        arrowP0 = self.line().p1() - QPointF(self.line().dx()/l, self.line().dy()/l)

        arrowP1 = self.line().p1() + QPointF(np.sin(angle + np.pi / 6) * self.arrowSize,
                                        np.cos(angle + np.pi / 6) * self.arrowSize)
        arrowP2 = self.line().p1() + QPointF(np.sin(angle + np.pi - np.pi / 6) * self.arrowSize,
                                        np.cos(angle + np.pi - np.pi / 6) * self.arrowSize)

        self.arrowHead.clear();
        self.arrowHead.append(arrowP0)
        self.arrowHead.append(arrowP1)
        self.arrowHead.append(arrowP2)

        # painter.drawConvexPolygon(self.arrowHead)
        arrow = QPainterPath()
        arrow.addPolygon(self.arrowHead)
        painter.fillPath(arrow, QBrush(self.myColor))

        painter.drawLine(self.line())

        self.shape()

    def mousePressEvent(self, event):
        print('press')
        self.isMousePressed = True
        self.mousePressedPos = event.scenePos()
        self.end_old = self.end.copy()
        super(MovableArrow, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        mouseCursorPos = event.scenePos()
        if self.isMousePressed:
            x = mouseCursorPos.x() - self.mousePressedPos.x()
            y = mouseCursorPos.y() - self.mousePressedPos.y()

            delta = np.array([x,y])
            # angle = ang(self.begin, self.end+delta)

            self.end[:] = self.end_old + delta

            self.updatePosition()
        # super(MovableArrow, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.isMousePressed = False
        self.parentObject().edited.emit(self.name)
        super(MovableArrow, self).mouseReleaseEvent(event)


class MovableArrowGroup(QGraphicsObject):
    edited = pyqtSignal(object)

    def __init__(self, parent=None):
        super(MovableArrowGroup, self).__init__(parent)

        self.setZValue(10)
        self.df = None
        self.itemList = []
        self.rect = QRectF()

        self.num_items = 0
        self.currentFrameNo = 0

    def setDataFrame(self, df, df_orig):
        self.df = df
        self.df_orig = df_orig

        shape = self.df.shape

        self.num_items = int(shape[1]/2)
        index = (np.repeat(range(self.num_items), 2).tolist(), [0,1]*self.num_items)
        mulindex = pd.MultiIndex.from_tuples(tuple(zip(*index)))

        self.df.columns = mulindex

        if not isinstance(self.df_orig.columns, pd.core.index.MultiIndex):
            self.df_orig.index = mulindex

        self.colors = [Qt.black for rgb in range(int(shape[1]/2))]

        scene = self.scene()
        if scene is not None:
            for item in self.itemList:
                scene.removeItem(item)
                del item
        self.itemList.clear()

        for i, rgb in enumerate(self.colors):
            movableArrow = MovableArrow(self)
            movableArrow.setName(i)

            self.itemList.append(movableArrow)

    # def setItemsAreMovable(self, flag):
    #     self.areItemsMovable = flag
    #
    #     for item in self.itemList:
    #         item.setItemIsMovable(flag)

    def setPositions(self, frameNo=None):
        if frameNo is not None:
            self.currentFrameNo = frameNo

            if self.currentFrameNo in self.df.index:
                self.show()
                for i, arrow_item in enumerate(self.itemList):
                    begin = self.df_orig.loc[self.currentFrameNo, i].values
                    end = self.df.loc[self.currentFrameNo, i].values
                    arrow_item.setPosition(begin, end)
            else:
                self.hide()

    def getColors(self):
        return self.colors

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget):
        pass

    # def setLineWidth(self, w):
    #     self.lineWidth = w
    #     for item in self.itemList:
    #         item.setLineWidth(w)
    #
    # def getLineWidth(self):
    #     return self.lineWidth
    #
    # def autoAdjustLineWidth(self, shape):
    #     # TODO: かなり適当
    #     m = np.max(shape)
    #     lw = max(float(2.5*m/600), 1.0)
    #     self.setLineWidth(lw)
    #     return self.getLineWidth()

    def openColorSelectorDialog(self, parent):
        dialog = ColorSelectorDialog(parent)

        for i, rgb in enumerate(self.colors):
            dialog.addRow(i, rgb)
        dialog.colorChanged.connect(self.changeMovableArrowColor)
        dialog.show()

    def changeMovableArrowColor(self, i, color):
        self.colors[i] = color
        self.itemList[i].setColor(color)
