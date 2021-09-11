#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, six, math, json

if six.PY2:
    reload(sys)
    sys.setdefaultencoding('UTF8')

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    currentDirPath = sys._MEIPASS
    if os.name == 'nt':
        import win32api
        win32api.SetDllDirectory(sys._MEIPASS)
elif __file__:
    currentDirPath = os.getcwd()

# currentDirPath = os.path.abspath(os.path.dirname(__file__) )
sampleDataPath = os.path.join(currentDirPath,"data")
userDir        = os.path.expanduser('~')

from queue import Queue

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsItemGroup, QGraphicsPixmapItem, QGraphicsEllipseItem, QFrame, QFileDialog, QPushButton
from PyQt5.QtGui import QPixmap, QImage, QPainter, QIcon, QColor
from PyQt5.QtCore import QPoint, QPointF, QRectF, QEvent, Qt, pyqtSignal, pyqtSlot

import cv2
import numpy as np
import pandas as pd

import icon

from lib.python import misc
from lib.python.ui.ui_main_window_base import Ui_MainWindowBase
from lib.python.ui.data_swap_dialog import DataSwapDialog

# from lib.python.ui.tracking_path import TrackingPath
from lib.python.ui.tracking_path_group import TrackingPathGroup
from lib.python.ui.movable_arrow import MovableArrowGroup
from lib.python.ui.movable_line import MovableLineGroup

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

    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.setupUi(self)

        self.videoPlaybackInit()
        self.imgInit()
        self.menuInit()

        self.df = {}
        self.trackingPathGroup = None
        self.movableArrowGroup = None

        self.line_data_dict = {}
        self.line_item_dict = {}

        self.file_name_dict = {}

        self.currentFrameNo = 0

        self.colors = None

        self.overlayCheckBox.stateChanged.connect(self.overlayCheckBoxStateChanged)
        self.radiusSpinBox.valueChanged.connect(self.radiusSpinBoxValueChanged)
        self.frameNoSpinBox.valueChanged.connect(self.frameNoSpinBoxValueChanged)
        self.markDeltaSpinBox.valueChanged.connect(self.markDeltaSpinBoxValueChanged)

    def overlayCheckBoxStateChanged(self, s):
        if self.overlayCheckBox.isChecked():
            self.frameBufferItemGroup.show()
        else:
            self.frameBufferItemGroup.hide()

        self.updateInputGraphicsView()

    def markDeltaSpinBoxValueChanged(self, value):
        if self.trackingPathGroup is not None:
            self.trackingPathGroup.setMarkDelta(self.markDeltaSpinBox.value())
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
        elif ext == ".json":
            self.openJSONFile(filePath=filePath)
        elif ext == ".color":
            self.openColorFile(filePath=filePath)
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
        self.actionSaveDataFiles.triggered.connect(self.saveDataFiles)
        self.actionOpenCSVFile.triggered.connect(self.openCSVFile)
        self.actionOpenCSVFile.triggered.connect(self.openJSONFile)
        self.actionOpenCSVFile.triggered.connect(self.openJSONFile)

        self.actionPath.triggered.connect(self.actionPathTriggered)
        self.actionCircle.triggered.connect(self.actionCircleTriggered)
        self.actionIntervalMark.triggered.connect(self.actionIntervalMarkTriggered)
        self.actionShape.triggered.connect(self.actionShapeTriggered)
        self.actionSkeleton.triggered.connect(self.actionSkeletonTriggered)
        self.actionArrow.triggered.connect(self.actionArrowTriggered)

        self.actionChangeOrderOfNum.triggered.connect(self.actionChangeOrderOfNumTriggered)

        self.actionTrackingPathColor.triggered.connect(self.openTrackingPathColorSelectorDialog)

    def actionPathTriggered(self, checked):
        if self.trackingPathGroup is not None:
            self.trackingPathGroup.setDrawLine(checked)
            if not checked or self.actionIntervalMark.isChecked():
                self.trackingPathGroup.setDrawMarkItem(checked)
            self.updateInputGraphicsView()

    def actionCircleTriggered(self, checked):
        if self.trackingPathGroup is not None:
            self.trackingPathGroup.setDrawItem(checked)
            self.updateInputGraphicsView()

    def actionIntervalMarkTriggered(self, checked):
        if self.trackingPathGroup is not None:
            self.trackingPathGroup.setDrawMarkItem(checked)
            self.updateInputGraphicsView()

    def actionShapeTriggered(self, checked):
        if 'shape' in self.line_item_dict.keys():
            line_item = self.line_item_dict['shape']
            if checked:
                line_item.show()
            else:
                line_item.hide()

    def actionSkeletonTriggered(self, checked):
        if 'skeleton' in self.line_item_dict.keys():
            line_item = self.line_item_dict['skeleton']
            if checked:
                line_item.show()
            else:
                line_item.hide()

    def actionArrowTriggered(self, checked):
        if self.movableArrowGroup is not None:
            if checked:
                self.movableArrowGroup.show()
            else:
                self.movableArrowGroup.hide()

    def actionChangeOrderOfNumTriggered(self, checked):
        if len(self.df.keys())!=0 or len(self.line_data_dict.keys())!=0:
            self.videoPlaybackWidget.stop()

            dialog = DataSwapDialog(self)
            dialog.setWindowModality(Qt.WindowModal)
            dialog.setData(self.df, self.line_data_dict)
            dialog.swapAccepted.connect(self.evaluate)

            res = dialog.exec()

    def openTrackingPathColorSelectorDialog(self, activated=False):
        if self.trackingPathGroup is not None:
            self.trackingPathGroup.openColorSelectorDialog(self)

    def openVideoFile(self, activated=False, filePath = None):
        if filePath is None:
            filePath, _ = QFileDialog.getOpenFileName(None, 'Open Video File', userDir)

        if len(filePath) is not 0:
            self.filePath = filePath

            ret = self.videoPlaybackWidget.openVideo(filePath)
            if ret == False:
                return False

            self.videoPlaybackWidget.show()
            self.cv_img = self.videoPlaybackWidget.getCurrentFrame()

            self.initialize()

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
            df = pd.read_csv(filePath, index_col=0)
            name = df.index.name

            if name is None:
                name = 'position'

            self.df[name] = df
            self.file_name_dict[name] = filePath

            if name is None or name=='position':
                if self.trackingPathGroup is not None:
                    self.inputScene.removeItem(self.trackingPathGroup)

                self.trackingPathGroup = TrackingPathGroup()
                self.trackingPathGroup.setRect(self.inputScene.sceneRect())
                self.inputScene.addItem(self.trackingPathGroup)

                self.trackingPathGroup.setDrawLine(self.actionPath.isChecked())
                self.trackingPathGroup.setDrawItem(self.actionCircle.isChecked())
                self.trackingPathGroup.setDrawMarkItem(self.actionIntervalMark.isChecked())

                shape = self.df['position'].shape
                self.num_items = int(shape[1]/2)
                index = (np.repeat(range(self.num_items), 2).tolist(), [0,1]*self.num_items)
                self.df['position'].columns = pd.MultiIndex.from_tuples(tuple(zip(*index)))

                self.trackingPathGroup.setDataFrame(self.df['position'])

                delta = self.df['position'].index[1] - self.df['position'].index[0]
                self.videoPlaybackWidget.setPlaybackDelta(delta)
                self.videoPlaybackWidget.setMaxTickableFrameNo(self.df['position'].index[-1])
            elif name=='arrow':
                if self.movableArrowGroup is not None:
                    self.inputScene.removeItem(self.movableArrowGroup)

                self.movableArrowGroup = MovableArrowGroup()
                self.inputScene.addItem(self.movableArrowGroup)
                self.movableArrowGroup.edited.connect(self.arrowEdited)

                if not self.actionArrow.isChecked():
                    self.movableArrowGroup.hide()

            if 'arrow' in self.df.keys() and 'position' in self.df.keys():
                self.movableArrowGroup.setDataFrame(self.df['arrow'], self.df['position'])

            self.initialize()

    def openColorFile(self, activated=False, filePath=None):
        if filePath is None:
            filePath, _ = QFileDialog.getOpenFileName(None, 'Open Color File', userDir, 'Color files (*.color)')

        if len(filePath) is not 0:
            self.colors = pd.read_csv(filePath, index_col=0).values.tolist()
            self.colors = [QColor(*rgb) for rgb in self.colors]
            self.setColorsToGraphicsObjects()

    def openJSONFile(self, activated=False, filePath=None):
        if filePath is None:
            filePath, _ = QFileDialog.getOpenFileName(None, 'Open JSON File', userDir, 'JSON files (*.json)')

        if len(filePath) is not 0:
            with open(filePath) as f_p:
                data = json.load(f_p)

            name = data['name']
            self.line_data_dict[name] = data
            self.file_name_dict[name] = filePath

            if name in self.line_item_dict.keys():
                self.inputScene.removeItem(self.line_item_dict[name])

            lines = MovableLineGroup()
            lines.setData(data)
            lines.setRect(self.inputScene.sceneRect())

            if name=='shape' and not self.actionShape.isChecked():
                lines.hide()

            if name=='skeleton' and not self.actionSkeleton.isChecked():
                lines.hide()

            self.line_item_dict[name] = lines
            self.inputScene.addItem(lines)

            self.initialize()

    def saveDataFiles(self, activated=False, filePath = None):
        if len(self.df.keys())!=0:
            for k, v in self.df.items():
                f_name, f_ext = os.path.splitext(self.file_name_dict[k])
                candidate_file_path = '{0}-fixed{1}'.format(f_name, f_ext)
                filePath, _ = QFileDialog.getSaveFileName(None, 'Save CSV File', candidate_file_path, "CSV files (*.csv)")

                if len(filePath) is not 0:
                    logger.debug("Saving CSV file: {0}".format(filePath))
                    df = v.copy()
                    col_n = df.values.shape[1]/2

                    col_names = np.array([('x{0}'.format(i), 'y{0}'.format(i)) for i in range(int(round(col_n)))]).flatten()
                    df.columns = pd.Index(col_names)
                    df.index.name = k
                    df.to_csv(filePath)

        for k, v in self.line_data_dict.items():
            f_name, f_ext = os.path.splitext(self.file_name_dict[k])
            candidate_file_path = '{0}-fixed{1}'.format(f_name, f_ext)
            filePath, _ = QFileDialog.getSaveFileName(None, 'Save JSON File', candidate_file_path, "JSON files (*.json)")

            if len(filePath) is not 0:
                logger.debug("Saving JSON file: {0}".format(filePath))
                with open(filePath, 'w') as f_p:
                    json.dump(v, f_p)

    def updateInputGraphicsView(self):
        self.inputScene.removeItem(self.inputPixmapItem)
        qimg = misc.cvMatToQImage(self.cv_img)
        self.inputPixmap = QPixmap.fromImage(qimg)

        p = QPainter(self.inputPixmap)
        sourceRect = self.inputPixmapRenderScene.sceneRect()
        self.inputPixmapRenderScene.render(p, QRectF(sourceRect), QRectF(sourceRect), QtCore.Qt.IgnoreAspectRatio)

        self.inputPixmapItem = QGraphicsPixmapItem(self.inputPixmap)
        rect = QtCore.QRectF(self.inputPixmap.rect())
        self.inputScene.setSceneRect(rect)
        self.inputScene.addItem(self.inputPixmapItem)

        self.inputGraphicsView.viewport().update()
        self.graphicsViewResized()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel:
            self.videoPlaybackWidget.wheelEvent(event)
            return True

        if event.type() == QEvent.KeyPress:
            if Qt.Key_Home <= event.key() <= Qt.Key_PageDown:
                self.videoPlaybackWidget.keyPressEvent(event)
                return True

        return False

    def graphicsViewResized(self, event=None):
        self.inputGraphicsView.fitInView(QtCore.QRectF(self.inputPixmap.rect()), QtCore.Qt.KeepAspectRatio)

    def setColorsToGraphicsObjects(self):
        # FIXME: データセットと色リストのサイズ整合性チェックが必要
        if self.colors is not None:
            if self.trackingPathGroup is not None:
                self.trackingPathGroup.setColors(self.colors)

            for k, v in self.line_item_dict.items():
                v.setColors(self.colors)

    def initialize(self):
        if  not self.videoPlaybackWidget.isOpened():
            return

        if self.trackingPathGroup is not None:
            r = self.trackingPathGroup.autoAdjustRadius(self.cv_img.shape)
            self.radiusSpinBox.setValue(r)
            self.trackingPathGroup.autoAdjustLineWidth(self.cv_img.shape)

            self.trackingPathGroup.setItemsAreMovable(True)

            if self.movableArrowGroup is not None:
                pass

        for k, v in self.line_item_dict.items():
            v.autoAdjustLineWidth(self.cv_img.shape)
            v.autoAdjustMarkSize(self.cv_img.shape)

        self.setColorsToGraphicsObjects()

        self.evaluate()

    def evaluate(self):
        if not self.videoPlaybackWidget.isOpened():
            return

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

            if self.movableArrowGroup is not None:
                self.movableArrowGroup.setPositions(self.currentFrameNo)

        for k, v in self.line_item_dict.items():
            v.setPolyline(self.currentFrameNo)

    @pyqtSlot(object)
    def arrowEdited(self, name):
        # TODO: 方向の再推定機能の実装
        # quit_msg = "Arrow {} edited.\nRe-estimate the direction in following frames?".format(name)
        # reply = QtWidgets.QMessageBox.question(
        #         self,
        #         'Question',
        #         quit_msg,
        #         QtWidgets.QMessageBox.Yes,
        #         QtWidgets.QMessageBox.No
        #         )
        #
        # if reply == QtWidgets.QMessageBox.Yes:
        #     pass
        # else:
        #     pass
        pass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Ui_MainWindow()
    MainWindow.setWindowIcon(QIcon(':/icon/icon.ico'))
    MainWindow.setWindowTitle('UMATracker-TrackingCorrector')
    MainWindow.show()
    app.installEventFilter(MainWindow)
    sys.exit(app.exec_())

