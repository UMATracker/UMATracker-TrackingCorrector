try:
    from ui_data_swap_dialog import Ui_DataSwapDialog
except ImportError:
    from .ui_data_swap_dialog import Ui_DataSwapDialog

import cv2
import numpy as np
import math

import sys, copy
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QStyle, QColorDialog, QDialog, QTableWidgetItem, QItemEditorCreatorBase, QItemEditorFactory, QStyledItemDelegate, QComboBox, QProgressDialog
from PyQt5.QtCore import pyqtProperty, pyqtSignal, pyqtSlot, QThread, Qt, QVariant

__version__ = '0.0.1'

# Log output setting.
# If handler = StreamHandler(), log will output into StandardOutput.
from logging import getLogger, NullHandler, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = NullHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

import os


class DataSwapDialog(Ui_DataSwapDialog, QDialog):
    swapAccepted = pyqtSignal()

    def __init__(self, parent=None):
        Ui_DataSwapDialog.__init__(self)
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.df = None
        self.line_data_dict = None
        self.col_n = 0
        self.row_n = 0
        self.swapButton.pressed.connect(self.swapButtonPressed)

    def setData(self, df, line_data_dict):
        self.df = df
        self.line_data_dict = line_data_dict

        if self.df is not None and len(self.df.keys())!=0:
            key = list(self.df.keys())[0]
            self.col_n = int(round(self.df[key].values.shape[1]/2))
            self.row_n = self.df[key].values.shape[0]
        elif self.line_data_dict is not None and len(self.line_data_dict.keys())!=0:
            key = list(self.line_data_dict.keys())[0]
            self.col_n = len(self.line_data_dict[key][str(0)])
            self.row_n = len(self.line_data_dict[key].keys())

        max_individual = max(self.col_n-1, 0)
        self.spinBox0.setMaximum(max_individual)
        self.spinBox1.setMaximum(max_individual)

        self.spinBox0.setMinimum(0)
        self.spinBox1.setMinimum(0)

    @pyqtSlot(QColor)
    def swapButtonPressed(self):
        n0 = self.spinBox0.value()
        n1 = self.spinBox1.value()

        n = 0
        try:
            n += len(self.df.keys())
        except:
            pass

        try:
            n += len(self.line_data_dict.keys())
        except:
            pass

        if n0!=n1:
            progress = QProgressDialog("Processing...", "Abort", 0, n, self)
            progress.setWindowModality(Qt.WindowModal)

            i = 0
            for k, v in self.df.items():
                progress.setValue(i)
                array0 = v.loc[:, n0].values
                array1 = v.loc[:, n1].values

                tmp = array0.copy()

                array0[:, :] = array1
                array1[:, :] = tmp

                i += 1

            for df_key, df in self.line_data_dict.items():
                progress.setValue(i)
                for idx, segment in df.items():
                    try:
                        idx = int(idx)
                    except:
                        continue

                    list0 = segment[n0]
                    list1 = segment[n1]

                    segment[n0] = list1
                    segment[n1] = list0
                i += 1

            progress.setValue(n)

            self.swapAccepted.emit()

    def closeEvent(self,event):
        pass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Dialog = DataSwapDialog()
    Dialog.show()
    sys.exit(app.exec_())

