# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ball.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Camshow(object):
    def setupUi(self, Camshow):
        Camshow.setObjectName("Camshow")
        Camshow.resize(1520, 1043)
        Camshow.setMouseTracking(True)
        Camshow.setTabletTracking(True)
        self.centralwidget = QtWidgets.QWidget(Camshow)
        self.centralwidget.setMouseTracking(True)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(640, 480))
        self.frame.setMaximumSize(QtCore.QSize(1280, 960))
        # self.frame.setBaseSize(QtCore.QSize(640, 360))
        self.frame.setMouseTracking(True)
        self.frame.setTabletTracking(True)
        # self.frame.setFrameShape(QtWidgets.QFrame.Box)
        # self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setText("")
        self.frame.setObjectName("frame")
        self.horizontalLayout.addWidget(self.frame)
        self.bullet_speed = QtWidgets.QFrame(self.centralwidget)
        self.bullet_speed.setMinimumSize(QtCore.QSize(209, 0))
        self.bullet_speed.setMaximumSize(QtCore.QSize(209, 16777215))
        self.bullet_speed.setFrameShape(QtWidgets.QFrame.Box)
        self.bullet_speed.setFrameShadow(QtWidgets.QFrame.Raised)
        self.bullet_speed.setObjectName("bullet_speed")
        self.distance_label = QtWidgets.QLabel(self.bullet_speed)
        self.distance_label.setGeometry(QtCore.QRect(10, 130, 141, 30))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.distance_label.setFont(font)
        self.distance_label.setObjectName("distance_label")
        self.distance = QtWidgets.QLCDNumber(self.bullet_speed)
        self.distance.setGeometry(QtCore.QRect(10, 170, 161, 51))
        self.distance.setObjectName("distance")
        self.connectButton = QtWidgets.QPushButton(self.bullet_speed)
        self.connectButton.setGeometry(QtCore.QRect(10, 900, 191, 41))
        font = QtGui.QFont()
        font.setPointSize(21)
        self.connectButton.setFont(font)
        self.connectButton.setObjectName("connectButton")
        self.Fps_lcd = QtWidgets.QLCDNumber(self.bullet_speed)
        self.Fps_lcd.setGeometry(QtCore.QRect(10, 310, 151, 51))
        self.Fps_lcd.setObjectName("Fps_lcd")
        self.Fps_label = QtWidgets.QLabel(self.bullet_speed)
        self.Fps_label.setGeometry(QtCore.QRect(10, 270, 141, 30))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.Fps_label.setFont(font)
        self.Fps_label.setObjectName("Fps_label")
        self.connectButton_2 = QtWidgets.QPushButton(self.bullet_speed)
        self.connectButton_2.setGeometry(QtCore.QRect(10, 460, 191, 41))
        font = QtGui.QFont()
        font.setPointSize(21)
        self.connectButton_2.setFont(font)
        self.connectButton_2.setObjectName("connectButton_2")
        self.connectButton_3 = QtWidgets.QPushButton(self.bullet_speed)
        self.connectButton_3.setGeometry(QtCore.QRect(10, 400, 191, 41))
        font = QtGui.QFont()
        font.setPointSize(21)
        self.connectButton_3.setFont(font)
        self.connectButton_3.setObjectName("connectButton_3")
        self.pushButton = QtWidgets.QPushButton(self.bullet_speed)
        self.pushButton.setGeometry(QtCore.QRect(0, 0, 211, 61))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(20)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.connectButton_4 = QtWidgets.QPushButton(self.bullet_speed)
        self.connectButton_4.setGeometry(QtCore.QRect(10, 530, 191, 41))
        font = QtGui.QFont()
        font.setPointSize(21)
        self.connectButton_4.setFont(font)
        self.connectButton_4.setObjectName("connectButton_4")
        self.connectButton_5 = QtWidgets.QPushButton(self.bullet_speed)
        self.connectButton_5.setGeometry(QtCore.QRect(10, 590, 191, 41))
        font = QtGui.QFont()
        font.setPointSize(21)
        self.connectButton_5.setFont(font)
        self.connectButton_5.setObjectName("connectButton_5")
        self.label = QtWidgets.QLabel(self.bullet_speed)
        self.label.setGeometry(QtCore.QRect(70, 365, 71, 31))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(18)
        self.label.setFont(font)
        self.label.setTextFormat(QtCore.Qt.AutoText)
        self.label.setObjectName("label")
        self.connectButton_6 = QtWidgets.QPushButton(self.bullet_speed)
        self.connectButton_6.setGeometry(QtCore.QRect(10, 790, 191, 41))
        font = QtGui.QFont()
        font.setPointSize(21)
        self.connectButton_6.setFont(font)
        self.connectButton_6.setObjectName("connectButton_6")
        self.connectButton_7 = QtWidgets.QPushButton(self.bullet_speed)
        self.connectButton_7.setGeometry(QtCore.QRect(10, 730, 191, 41))
        font = QtGui.QFont()
        font.setPointSize(21)
        self.connectButton_7.setFont(font)
        self.connectButton_7.setObjectName("connectButton_7")
        self.sudu = QtWidgets.QSlider(self.bullet_speed)
        self.sudu.setGeometry(QtCore.QRect(20, 650, 160, 22))
        self.sudu.setMaximum(60)
        self.sudu.setOrientation(QtCore.Qt.Horizontal)
        self.sudu.setObjectName("sudu")
        self.speed = QtWidgets.QLCDNumber(self.bullet_speed)
        self.speed.setGeometry(QtCore.QRect(20, 670, 161, 51))
        self.speed.setObjectName("speed")
        self.horizontalLayout.addWidget(self.bullet_speed)
        Camshow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Camshow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1520, 26))
        self.menubar.setObjectName("menubar")
        Camshow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(Camshow)
        self.statusbar.setObjectName("statusbar")
        Camshow.setStatusBar(self.statusbar)

        self.retranslateUi(Camshow)
        QtCore.QMetaObject.connectSlotsByName(Camshow)

    def retranslateUi(self, Camshow):
        _translate = QtCore.QCoreApplication.translate
        Camshow.setWindowTitle(_translate("Camshow", "Camshow"))
        self.distance_label.setText(_translate("Camshow", "距离基座"))
        self.connectButton.setText(_translate("Camshow", "连接相机"))
        self.Fps_label.setText(_translate("Camshow", "当前帧率"))
        self.connectButton_2.setText(_translate("Camshow", "蓝色取球"))
        self.connectButton_3.setText(_translate("Camshow", "蓝色射塔"))
        self.pushButton.setText(_translate("Camshow", "关闭界面"))
        self.connectButton_4.setText(_translate("Camshow", "红色射塔"))
        self.connectButton_5.setText(_translate("Camshow", "红色取球"))
        self.label.setText(_translate("Camshow", "1-2-3-4"))
        self.connectButton_6.setText(_translate("Camshow", "取球"))
        self.connectButton_7.setText(_translate("Camshow", "上膛"))
