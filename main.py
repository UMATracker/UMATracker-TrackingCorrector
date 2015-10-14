#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from queue import Queue

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsItemGroup, QGraphicsPixmapItem, QGraphicsEllipseItem, QFrame, QFileDialog, QPushButton
from PyQt5.QtGui import QPixmap, QImage, QPainter
from PyQt5.QtCore import QPoint, QPointF, QRectF, QEvent

import cv2
import numpy as np

from lib.python import misc
from lib.python.ui.ui_main_window_base import Ui_MainWindowBase

from lib.python.ui.movable_poly_line import MovablePolyLine


currentDirPath = os.path.abspath(os.path.dirname(__file__) )
sampleDataPath = os.path.join(currentDirPath,"data")
userDir        = os.path.expanduser('~')

# Log file setting.
# import logging
# logging.basicConfig(filename='MainWindow.log', level=logging.DEBUG)

# Log output setting.
# If handler = StreamHandler(), log will output into StandardOutput.
from logging import getLogger, NullHandler, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = NullHandler() if True else StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

class Ui_MainWindow(QtWidgets.QMainWindow, Ui_MainWindowBase):
    def __init__(self, path):
        super(Ui_MainWindow, self).__init__()
        self.setupUi(self)

        self.videoPlaybackInit()
        self.imgInit()
        self.menuInit()

    def dragEnterEvent(self,event):
        event.accept()

    def dropEvent(self,event):
        event.setDropAction(QtCore.Qt.MoveAction)
        mime = event.mimeData()
        if mime.hasUrls():
            urls = mime.urls()
            if len(urls) > 0:
                #self.dragFile.emit()
                self.processDropedFile(urls[0].toLocalFile())
            event.accept()
        else:
            event.ignore()

    def processDropedFile(self,filePath):
        root,ext = os.path.splitext(filePath)
        if ext == ".filter":
            # Read Filter
            self.openFilterFile(filePath=filePath)
        elif ext.lower() in [".avi",".mpg",".mts",".mp4"]:
            # Read Video
            self.openVideoFile(filePath=filePath)
        elif ext.lower() in [".png",".bmp",".jpg",".jpeg"]:
            self.openImageFile(filePath=filePath)

    def videoPlaybackInit(self):
        self.videoPlaybackWidget.hide()
        self.videoPlaybackWidget.frameChanged.connect(self.setFrame)

    def setFrame(self, frame):
        if frame is not None:
            self.cv_img = frame
            self.updateInputGraphicsView()
            self.evaluate()

    def imgInit(self):
        self.cv_img = cv2.imread(os.path.join(sampleDataPath,"color_filter_test.png"))


        self.frameBuffer = Queue()
        self.frameBufferItemGroup = QGraphicsItemGroup()
        self.inputPixmapRenderScene = QGraphicsScene()
        self.inputPixmapRenderScene.addItem(self.frameBufferItemGroup)

        self.inputScene = QGraphicsScene()
        self.inputGraphicsView.setScene(self.inputScene)
        self.inputGraphicsView.resizeEvent = self.graphicsViewResized
        # self.inputScene.addItem(self.frameBufferItemGroup)

        qimg = misc.cvMatToQImage(self.cv_img)
        self.inputPixmap = QPixmap.fromImage(qimg)
        self.inputPixmapItem = QGraphicsPixmapItem(self.inputPixmap)
        self.inputScene.addItem(self.inputPixmapItem)

        self.movablePolyLine = MovablePolyLine()
        self.movablePolyLine.setRect(self.inputScene.sceneRect())
        self.inputScene.addItem(self.movablePolyLine)
        self.movablePolyLine.setPoints([[20,20],[100,100],[150,150]])

        self.rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self.inputGraphicsView)
        self.inputGraphicsView.mousePressEvent = self.inputGraphicsViewMousePressEvent
        self.inputGraphicsView.mouseMoveEvent = self.inputGraphicsViewMouseMoveEvent
        self.inputGraphicsView.mouseReleaseEvent = self.inputGraphicsViewMouseReleaseEvent

        self.inputGraphicsView.viewport().installEventFilter(self)

        self.inputGraphicsView.setMouseTracking(True)
        self.overlayScene = QGraphicsScene()
        self.inputGraphicsView.setOverlayScene(self.overlayScene)

        self.zoomedGraphicsView.setScene(self.inputScene)
        self.zoomedGraphicsView.setOverlayScene(self.overlayScene)

    def inputGraphicsViewMousePressEvent(self, event):
        self.origin = QPoint(event.pos())
        self.rubberBand.setGeometry(
            QtCore.QRect(self.origin, QtCore.QSize()))
        self.rubberBand.show()

        # Comment out to permit the view for sending the event to the child scene.
        # QGraphicsView.mousePressEvent(self.inputGraphicsView, event)

    def inputGraphicsViewMouseMoveEvent(self, event):
        if self.rubberBand.isVisible():
            self.rubberBand.setGeometry(
                QtCore.QRect(self.origin, event.pos()).normalized())
        # Comment out to permit the view for sending the event to the child scene.
        # QGraphicsView.mouseMoveEvent(self.inputGraphicsView, event)

    def inputGraphicsViewMouseReleaseEvent(self, event):
        if self.rubberBand.isVisible():
            self.rubberBand.hide()
            rect = self.rubberBand.geometry()
            sceneRect = self.inputGraphicsView.mapToScene(rect).boundingRect()
            self.zoomedGraphicsView.fitInView(QRectF(sceneRect))
            self.zoomedGraphicsView.viewport().update()
        # Comment out to permit the view for sending the event to the child scene.
        self.inputGraphicsView.viewport().update()
        # QGraphicsView.mouseReleaseEvent(self.inputGraphicsView, event)

    def menuInit(self):
        pass
        # self.actionOpenVideo.triggered.connect(self.openVideoFile)
        # self.actionOpenImage.triggered.connect(self.openImageFile)

        # self.actionOpenFilterSetting.triggered.connect(self.openFilterSettingFile)

    def openVideoFile(self, activated=False, filePath = None):
        if filePath is None:
            filePath, _ = QFileDialog.getOpenFileName(None, 'Open Video File', userDir)

        if len(filePath) is not 0:
            self.filePath = filePath
            self.videoPlaybackWidget.show()
            self.videoPlaybackWidget.openVideo(filePath)

    def openImageFile(self):
        filename, _ = QFileDialog.getOpenFileName(None, 'Open Image File', userDir)

        if len(filename) is not 0:
            self.cv_img = cv2.imread(filename)
            self.videoPlaybackWidget.hide()

            self.updateInputGraphicsView()
            self.releaseVideoCapture()

            self.evaluate()

    def updateInputGraphicsView(self):
        print("update")
        # self.inputScene.clear()
        self.inputScene.removeItem(self.inputPixmapItem)
        qimg = misc.cvMatToQImage(self.cv_img)
        self.inputPixmap = QPixmap.fromImage(qimg)

        p = QPainter(self.inputPixmap)
        sourceRect = self.inputPixmapRenderScene.sceneRect()
        targetRect = self.inputPixmap.rect()
        self.inputPixmapRenderScene.render(p, QRectF(targetRect), QRectF(sourceRect), QtCore.Qt.IgnoreAspectRatio)

        self.inputPixmapItem = QGraphicsPixmapItem(self.inputPixmap)
        rect = QtCore.QRectF(self.inputPixmap.rect())
        self.inputScene.setSceneRect(rect)
        self.inputScene.addItem(self.inputPixmapItem)

        self.movablePolyLine.setRect(self.inputScene.sceneRect())

        self.movablePolyLine.setPoints([[20,20],[100,100],[150,200]])

        # self.circle = QGraphicsEllipseItem()
        # self.circle.setRect(10, 10, 50, 50)
        # self.circle.setFlags(QGraphicsItem.ItemIsMovable)
        # self.inputScene.addItem(self.circle)

        pixmapItem = QGraphicsPixmapItem(QPixmap.fromImage(qimg))
        pixmapItem.setOpacity(0.2)
        # self.overlayScene.setSceneRect(rect)
        # self.overlayScene.addItem(pixmapItem)

        self.frameBuffer.put(pixmapItem)
        self.frameBufferItemGroup.addToGroup(pixmapItem)
        if self.frameBuffer.qsize() > 10:
            item = self.frameBuffer.get()
            self.frameBufferItemGroup.removeFromGroup(item)
            # self.overlayScene.removeItem(item)

        self.inputGraphicsView.viewport().update()
        self.graphicsViewResized()

    def eventFilter(self, obj, event):
        if obj is self.inputGraphicsView.viewport() and event.type()==QEvent.Wheel:
            return True
        else:
            return False

    def graphicsViewResized(self, event=None):
        print("resize")
        print(self.inputScene)
        self.inputGraphicsView.fitInView(QtCore.QRectF(self.inputPixmap.rect()), QtCore.Qt.KeepAspectRatio)

    def evaluate(self):
        pass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Ui_MainWindow(currentDirPath)
    MainWindow.show()
    sys.exit(app.exec_())

