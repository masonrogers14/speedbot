#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 22:55:13 2019

@author: Mason
"""

from PyQt5 import QtWidgets, QtGui, QtCore
import time

class BigWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
    def closeEvent(self, event):
        for child in self.__dict__:
            if isinstance(self.__dict__[child], QtWidgets.QWidget):
                self.__dict__[child].close()
        self.close()
        
class QSpinBoxPlus(QtWidgets.QSpinBox):
    def __init__(self, Dialog):
        super().__init__(Dialog)
        
class QClock(QtWidgets.QLCDNumber):
    def __init__(self, parent):
        super().__init__(parent)
        
    def show_time(self, current = 0, start = 0):
        elapsed = int(current - start)
        m = elapsed // 60
        s = elapsed % 60
        string = '{0:2d}:{1:02d}'.format(m,s)
        self.display(string)
        
    def reset(self):
        string = ("0:00")
        self.display(string)
        
class QClicker(QtWidgets.QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.count = 0
        self.released = True
        self.log = {}
        self.setMouseTracking(True)
        self.mouseMoveEvent = lambda event: self.setFocus(0)
        self.keyPressEvent = lambda event: self.increment(event)
        self.mousePressEvent = lambda event: self.increment(event)
        self.keyReleaseEvent = lambda event: self.release(event)
        self.mouseReleaseEvent = lambda event: self.release(event)
        
    def increment(self, event):
        proceed = False
        change = 1
        if isinstance(event, QtGui.QKeyEvent):
            if self.released and (event.key() == QtCore.Qt.Key_Return \
                                  or event.key() == QtCore.Qt.Key_Space \
                                  or event.key() == QtCore.Qt.Key_Up):
                proceed = True
            elif self.released and event.key() == QtCore.Qt.Key_Down:
                proceed = True
                change = -1
            elif self.released and event.key() == QtCore.Qt.Key_Backspace:
                proceed = True
                change = -1 * self.count
            elif self.released and (event.key() == QtCore.Qt.Key_Left \
                                    or event.key() == QtCore.Qt.Key_Right):
                self.display_log()
        if isinstance(event, QtGui.QMouseEvent):
            if event.button() == QtCore.Qt.LeftButton:
                proceed = True
            elif event.button() == QtCore.Qt.RightButton:
                self.display_log()
        if proceed and self.released:
            self.released = False
            self.count += change
            self.setText(str(self.count))
            
    def release(self, event):
        self.released = True
 
    def display_log(self):
        numline = 0
        estring = ''
        fstring = '{0:4d}-{1:02d}-{2:02d} {3:02d}:{4:02d} {5:>10}{6:6.0f}{7:6d}\n'
        for t in self.log:
            item = self.log[t]
            for line in item:
                lt = time.localtime(t)
                ts = [lt[0], lt[1], lt[2], lt[3], lt[4]]
                estring += fstring.format(*ts,*line)
                numline += 1
        dialog = QtWidgets.QDialog(self)
        dialog.setGeometry(0,0,400,600)
        accept = QtWidgets.QPushButton(dialog)
        accept.setText("done")
        accept.setDefault(True)
        accept.setGeometry(20,550,360,40)
        accept.clicked.connect(dialog.close)
        accept.setStyleSheet('QPushButton {background : rgb(228, 255, 255);}')
        clearl = QtWidgets.QPushButton(dialog)
        clearl.setText("clear log")
        clearl.setGeometry(20,500,360,40)
        clearl.clicked.connect(self.clear_log)
        clearl.clicked.connect(dialog.close)
        scroll = QtWidgets.QScrollArea(dialog)
        scroll.setGeometry(10,10,380,480)
        labels = QtWidgets.QLabel(estring, scroll)
        labels.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        labels.setStyleSheet("QLabel {font : 12pt Courier New;}")
        scroll.setWidget(labels)
        dialog.show()
        
    def clear_log(self):
        self.log = {}
        