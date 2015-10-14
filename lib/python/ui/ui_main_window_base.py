# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ui_main_window_base.ui'
#
# Created by: PyQt5 UI code generator 5.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindowBase(object):
    def setupUi(self, MainWindowBase):
        MainWindowBase.setObjectName("MainWindowBase")
        MainWindowBase.resize(902, 506)
        MainWindowBase.setAcceptDrops(True)
        self.centralwidget = QtWidgets.QWidget(MainWindowBase)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.inputGraphicsView = OverlaidGraphicsView(self.groupBox)
        self.inputGraphicsView.setAcceptDrops(False)
        self.inputGraphicsView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.inputGraphicsView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.inputGraphicsView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.inputGraphicsView.setObjectName("inputGraphicsView")
        self.verticalLayout.addWidget(self.inputGraphicsView)
        self.videoPlaybackWidget = VideoPlaybackWidget(self.groupBox)
        self.videoPlaybackWidget.setObjectName("videoPlaybackWidget")
        self.verticalLayout.addWidget(self.videoPlaybackWidget)
        self.horizontalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.zoomedGraphicsView = OverlaidGraphicsView(self.groupBox_2)
        self.zoomedGraphicsView.setObjectName("zoomedGraphicsView")
        self.verticalLayout_2.addWidget(self.zoomedGraphicsView)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout.addWidget(self.groupBox_2)
        MainWindowBase.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindowBase)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 902, 21))
        self.menubar.setObjectName("menubar")
        MainWindowBase.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindowBase)
        self.statusbar.setObjectName("statusbar")
        MainWindowBase.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindowBase)
        QtCore.QMetaObject.connectSlotsByName(MainWindowBase)

    def retranslateUi(self, MainWindowBase):
        _translate = QtCore.QCoreApplication.translate
        MainWindowBase.setWindowTitle(_translate("MainWindowBase", "MainWindow"))
        self.groupBox.setTitle(_translate("MainWindowBase", "Tracking"))
        self.groupBox_2.setTitle(_translate("MainWindowBase", "GroupBox"))

from .overlaid_graphics_view import OverlaidGraphicsView
from .video_playback_widget import VideoPlaybackWidget
