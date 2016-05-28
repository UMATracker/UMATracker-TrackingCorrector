# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_data_swap_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DataSwapDialog(object):
    def setupUi(self, DataSwapDialog):
        DataSwapDialog.setObjectName("DataSwapDialog")
        DataSwapDialog.resize(325, 115)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DataSwapDialog.sizePolicy().hasHeightForWidth())
        DataSwapDialog.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(DataSwapDialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.spinBox1 = QtWidgets.QSpinBox(DataSwapDialog)
        self.spinBox1.setObjectName("spinBox1")
        self.horizontalLayout_2.addWidget(self.spinBox1)
        self.spinBox0 = QtWidgets.QSpinBox(DataSwapDialog)
        self.spinBox0.setObjectName("spinBox0")
        self.horizontalLayout_2.addWidget(self.spinBox0)
        self.swapButton = QtWidgets.QPushButton(DataSwapDialog)
        self.swapButton.setObjectName("swapButton")
        self.horizontalLayout_2.addWidget(self.swapButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.buttonBox = QtWidgets.QDialogButtonBox(DataSwapDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(DataSwapDialog)
        self.buttonBox.accepted.connect(DataSwapDialog.accept)
        self.buttonBox.rejected.connect(DataSwapDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(DataSwapDialog)

    def retranslateUi(self, DataSwapDialog):
        _translate = QtCore.QCoreApplication.translate
        DataSwapDialog.setWindowTitle(_translate("DataSwapDialog", "Dialog"))
        self.swapButton.setText(_translate("DataSwapDialog", "Swap"))

