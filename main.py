#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, six

if six.PY2:
    reload(sys)
    sys.setdefaultencoding('UTF8')

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    currentDirPath = sys._MEIPASS
    if os.name == 'nt':
        import win32api
        win32api.SetDllDirectory(sys._MEIPASS)
        win32api.SetDllDirectory(os.path.join(sys._MEIPASS, 'dll'))
elif __file__:
    currentDirPath = os.getcwd()

# currentDirPath = os.path.abspath(os.path.dirname(__file__) )
sampleDataPath = os.path.join(currentDirPath,"data")
userDir        = os.path.expanduser('~')

from queue import Queue

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsItemGroup, QGraphicsPixmapItem, QGraphicsEllipseItem, QFrame, QFileDialog, QPushButton
from PyQt5.QtGui import QPixmap, QImage, QPainter, QIcon
from PyQt5.QtCore import QPoint, QPointF, QRectF, QEvent, Qt

import cv2
import numpy as np
import pandas as pd

import icon

from lib.python import misc
from lib.python.ui.ui_main_window_base import Ui_MainWindowBase

# from lib.python.ui.tracking_path import TrackingPath
from lib.python.ui.tracking_path_group import TrackingPathGroup

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

        self.df = None
        self.trackingPathGroup = None
        self.colors = []

        self.circleCheckBox.stateChanged.connect(self.polyLineCheckBoxStateChanged)
        self.lineCheckBox.stateChanged.connect(self.polyLineCheckBoxStateChanged)
        self.overlayCheckBox.stateChanged.connect(self.overlayCheckBoxStateChanged)
        self.radiusSpinBox.valueChanged.connect(self.radiusSpinBoxValueChanged)

        self.frameNoSpinBox.valueChanged.connect(self.frameNoSpinBoxValueChanged)

    def overlayCheckBoxStateChanged(self, s):
        if self.overlayCheckBox.isChecked():
            self.frameBufferItemGroup.show()
        else:
            self.frameBufferItemGroup.hide()

        self.updateInputGraphicsView()

    def polyLineCheckBoxStateChanged(self, s):
        overlayFrameNo = self.frameNoSpinBox.value()

        min_value = max(self.currentFrameNo-overlayFrameNo,0)
        current_pos = self.currentFrameNo - min_value

        if self.trackingPathGroup is not None:
            self.trackingPathGroup.setDrawItem(current_pos, self.circleCheckBox.isChecked())
            self.trackingPathGroup.setDrawLine(self.lineCheckBox.isChecked())

            self.updateInputGraphicsView()

    def radiusSpinBoxValueChanged(self, value):
        if self.trackingPathGroup is not None:
            self.trackingPathGroup.setRadius(self.radiusSpinBox.value())
            self.updateInputGraphicsView()

    def frameNoSpinBoxValueChanged(self, value):
        if self.trackingPathGroup is not None:
            self.trackingPathGroup.setOverlayFrameNo(self.frameNoSpinBox.value())
            self.updateInputGraphicsView()

    def dragEnterEvent(self,event):
        event.acceptProposedAction()

    def dropEvent(self,event):
        # event.setDropAction(QtCore.Qt.MoveAction)
        mime = event.mimeData()
        if mime.hasUrls():
            urls = mime.urls()
            if len(urls) > 0:
                self.processDropedFile(urls[0].toLocalFile())

        event.acceptProposedAction()

    def processDropedFile(self,filePath):
        root,ext = os.path.splitext(filePath)
        if ext == ".filter":
            # Read Filter
            self.openFilterFile(filePath=filePath)
            return
        elif ext == ".csv":
            self.openCSVFile(filePath=filePath)
        elif self.openImageFile(filePath=filePath):
            return
        elif self.openVideoFile(filePath=filePath):
            return

    def videoPlaybackInit(self):
        self.videoPlaybackWidget.hide()
        self.videoPlaybackWidget.frameChanged.connect(self.setFrame, Qt.QueuedConnection)

    def setFrame(self, frame, frameNo):
        if frame is not None:
            self.cv_img = frame
            self.currentFrameNo = frameNo
            self.updateInputGraphicsView()
            self.evaluate()

    def imgInit(self):
        self.cv_img = cv2.imread(os.path.join(sampleDataPath,"color_filter_test.png"))


        self.frameBuffer = Queue()
        self.frameBufferItemGroup = QGraphicsItemGroup()
        self.frameBufferItemGroup.hide()
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
        self.actionSaveCSVFile.triggered.connect(self.saveCSVFile)
        self.actionOpenCSVFile.triggered.connect(self.openCSVFile)

    def openVideoFile(self, activated=False, filePath = None):
        if filePath is None:
            filePath, _ = QFileDialog.getOpenFileName(None, 'Open Video File', userDir)

        if len(filePath) is not 0:
            self.filePath = filePath

            ret = self.videoPlaybackWidget.openVideo(filePath)
            if ret == False:
                return False

            self.videoPlaybackWidget.show()

            self.evaluate()

            return True
        else:
            return False

    def openImageFile(self, activated=False, filePath = None):
        if filePath == None:
            filePath, _ = QFileDialog.getOpenFileName(None, 'Open Image File', userDir)

        if len(filePath) is not 0:
            self.filePath = filePath
            img = cv2.imread(filePath)
            if img is None:
                return False

            self.cv_img = img
            self.videoPlaybackWidget.hide()
            self.updateInputGraphicsView()

            self.evaluate()

            return True
        else:
            return False

    def openCSVFile(self, activated=False, filePath=None):
        if filePath is None:
            filePath, _ = QFileDialog.getOpenFileName(None, 'Open CSV File', userDir, 'CSV files (*.csv)')

        if len(filePath) is not 0:
            self.df = pd.read_csv(filePath, index_col=0)

            if self.trackingPathGroup is not None:
                self.inputScene.removeItem(self.trackingPathGroup)

            self.trackingPathGroup = TrackingPathGroup()
            self.trackingPathGroup.setRect(self.inputScene.sceneRect())
            self.inputScene.addItem(self.trackingPathGroup)

            self.trackingPathGroup.setDataFrame(self.df)

            self.evaluate()

    def saveCSVFile(self, activated=False, filePath = None):
        if self.df is not None:
            filePath, _ = QFileDialog.getSaveFileName(None, 'Save CSV File', userDir, "CSV files (*.csv)")

            if len(filePath) is not 0:
                logger.debug("Saving CSV file: {0}".format(filePath))
                df = self.df.copy()
                col_n = df.as_matrix().shape[1]/2

                col_names = np.array([('x{0}'.format(i), 'y{0}'.format(i)) for i in range(col_n)]).flatten()
                print(col_names)

                self.df.columns = col_names
                df.to_csv(filePath)

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
        qimg = misc.cvMatToQImage(self.cv_img)
        pixmapItem = QGraphicsPixmapItem(QPixmap.fromImage(qimg))
        pixmapItem.setOpacity(0.2)

        self.frameBuffer.put(pixmapItem)
        self.frameBufferItemGroup.addToGroup(pixmapItem)
        if self.frameBuffer.qsize() > 10:
            item = self.frameBuffer.get()
            self.frameBufferItemGroup.removeFromGroup(item)

        if self.trackingPathGroup is not None:
            self.trackingPathGroup.setPoints(self.currentFrameNo)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Ui_MainWindow(currentDirPath)
    MainWindow.setWindowIcon(QIcon(':/icon/icon.ico'))
    MainWindow.show()
    sys.exit(app.exec_())

