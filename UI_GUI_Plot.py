# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 16:49:42 2019

@author: Victor
"""

import PyQt5
import pyqtgraph as pg
import gc
import List_Of_Servers as LoS


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(243, 306)

        self.centralwidget = PyQt5.QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frame = PyQt5.QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(PyQt5.QtCore.QRect(0, 0, 700, 500))

        self.layoutWidget = PyQt5.QtWidgets.QWidget(self.frame)
        self.layoutWidget.setGeometry(PyQt5.QtCore.QRect(10, 10, 690, 490))
        self.layoutWidget.setObjectName("layoutWidget")

        self.h_layout = PyQt5.QtWidgets.QHBoxLayout(self.layoutWidget)
        self.v_layout_1 = PyQt5.QtWidgets.QVBoxLayout()

        """ add plot to the layout """
        self.plot_T = pg.PlotWidget(self.layoutWidget)
        self.plot_T.setObjectName("plot_T")
        self.v_layout_1.addWidget(self.plot_T)

        self.v_layout_3 = PyQt5.QtWidgets.QVBoxLayout()

        """ Fill up with elements """
        self.v_layout_3.addStretch()

        self.sizePolicy = PyQt5.QtWidgets.QSizePolicy(PyQt5.QtWidgets.QSizePolicy.Preferred, PyQt5.QtWidgets.QSizePolicy.Fixed)
        self.sizePolicy.setHorizontalStretch(0)
        self.sizePolicy.setVerticalStretch(0)

        self.buttons_dict = {}
        for i in LoS.server_list.keys():
            self.button = PyQt5.QtWidgets.QPushButton(self.layoutWidget)
            self.button.setText(str(i))
            self.sizePolicy.setHeightForWidth(self.button.sizePolicy().hasHeightForWidth())
            self.button.setSizePolicy(self.sizePolicy)
            self.button.setStyleSheet(f"background-color: gray;color: {LoS.server_list[i][5]}")
            self.buttons_dict[i] = self.button
            self.v_layout_3.addWidget(self.button)
            self.button.setObjectName("button_"+i)
            print (self.button.objectName())
            self.v_layout_3.addStretch()

        """ LOAD button """
        self.load_button = PyQt5.QtWidgets.QPushButton(self.layoutWidget)
        self.load_button.setGeometry(PyQt5.QtCore.QRect(500, 300, 50, 50))
        self.v_layout_3.addWidget(self.load_button)
        self.load_button.setText("Load LOG")
        self.v_layout_3.addStretch()

        self.label_1 = PyQt5.QtWidgets.QLabel(self.layoutWidget)
        self.label_1.setText("Number of points")
        self.label_1.setGeometry(PyQt5.QtCore.QRect(500, 20, 50, 50))
        self.label_1.setFixedWidth
        self.sizePolicy.setHeightForWidth(self.label_1.sizePolicy().hasHeightForWidth())
        self.label_1.setSizePolicy(self.sizePolicy)
        self.label_1.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.v_layout_3.addWidget(self.label_1)

        self.lineEdit_1 = PyQt5.QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit_1.setText("100")
        self.lineEdit_1.setGeometry(PyQt5.QtCore.QRect(500, 20, 50, 50))
        self.lineEdit_1.setFixedWidth
        self.sizePolicy.setHeightForWidth(self.lineEdit_1.sizePolicy().hasHeightForWidth())
        self.lineEdit_1.setSizePolicy(self.sizePolicy)
        self.lineEdit_1.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.v_layout_3.addWidget(self.lineEdit_1)
        self.v_layout_3.addStretch()

        self.label_2 = PyQt5.QtWidgets.QLabel(self.layoutWidget)
        self.label_2.setText("Channel to monitor")
        self.label_2.setGeometry(PyQt5.QtCore.QRect(500, 20, 50, 50))
        self.label_2.setFixedWidth
        self.sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(self.sizePolicy)
        self.label_2.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.v_layout_3.addWidget(self.label_2)

        self.lineEdit_2 = PyQt5.QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit_2.setText("1")
        self.lineEdit_2.setGeometry(PyQt5.QtCore.QRect(500, 100, 50, 50))
        self.lineEdit_2.setFixedWidth
        self.sizePolicy.setHeightForWidth(self.lineEdit_2.sizePolicy().hasHeightForWidth())
        self.lineEdit_2.setSizePolicy(self.sizePolicy)
        self.lineEdit_2.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.v_layout_3.addWidget(self.lineEdit_2)

        self.label_3 = PyQt5.QtWidgets.QLabel(self.layoutWidget)
        self.label_3.setText("Channel name")
        self.label_3.setGeometry(PyQt5.QtCore.QRect(500, 20, 50, 50))
        self.label_3.setFixedWidth
        self.sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(self.sizePolicy)
        self.label_3.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.v_layout_3.addWidget(self.label_3)

        self.h_layout.addLayout(self.v_layout_1)
        self.h_layout.addLayout(self.v_layout_3)

        self.setLayout(self.h_layout)

        gc.collect()
