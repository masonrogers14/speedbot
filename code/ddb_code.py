#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 20:34:19 2019

@author: Mason
"""
from PyQt5 import QtWidgets, QtCore, QtGui
import jump_classes as jc

class dragDropButton(QtWidgets.QPushButton):
    def __init__(self, parent = None):
        super().__init__(parent)
        
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.startPosition = event.pos()
            self.dragging = False
            
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit()
            self.dragging = False
                    
    def mouseMoveEvent(self, event):
        if (event.pos() - self.startPosition).manhattanLength() > 10 \
        and not(self.dragging):
            self.bin = self.parent().parent().parent() #workout object
            self.drag = QtGui.QDrag(self)
            self.drag.setHotSpot(event.pos())
            self.mimeData = QtCore.QMimeData()
            self.drag.setMimeData(self.mimeData)
            self.drag.setPixmap(self.grab())
            self.pPos = self.mapToParent(QtCore.QPoint(0,0))
            self.hide()
    
            #handle events from 'copy' bins
            if self.bin.copy:
                duplicate = self.duplicate()
                duplicate.setText(self.text())
                duplicate.move(self.pos())
                duplicate.show()
                
                #Fix reps if necessary
                if isinstance(self, jc.Speed):
                    spins = self.bin.parent().findChildren(QtWidgets.QSpinBox)
                    reps = 1
                    for spin in spins:
                        reps *= spin.value()
                    self.repeat(reps)
                    self.setText(str(self))
                
                self.bin.eventList.insert(self.bin.eventList.index(self), duplicate)
                self.bin.eventList.remove(self)
                self.bin.positions = [self.bin.indexToPos(j) for j in range(len(self.bin.eventList)+1)]
                
            #run the drag operation 
            self.dragging = True
            self.drag.exec()
            
            #protect against user dropping away from a drop zone
            if self.isHidden():
                if self.bin.copy:
                    del(self)
                else:
                    de = QtGui.QDropEvent(self.pPos,
                                          QtCore.Qt.MoveAction,
                                          self.mimeData,
                                          QtCore.Qt.LeftButton,
                                          QtCore.Qt.NoModifier,
                                          63)#drop
                    self.bin.dropEvent(de, self) 
                    
    def delete_button(self):
        self.setText("")
        self.clicked.disconnect()
        delete = QtWidgets.QPushButton(self)
        delete.setObjectName("deleteButton")
        delete.setGeometry(13,13,49,49)
        delete.clicked.connect(self.delete_me)
        delete.setText("delete")
        self.clicked.connect(self.keep_me)
        delete.show()
    
    def delete_me(self):
        self.bin.remove_event(self)
        
    def keep_me(self):
        self.setText(str(self))
        self.clicked.disconnect()
        self.clicked.connect(self.delete_button)
        delete = self.findChild(QtWidgets.QPushButton, "deleteButton")
        delete.deleteLater()
        
    def __str__(self):
        return(self.objectName())
        
class dragDropBucket(QtWidgets.QScrollArea):

    def __init__(self, parent = None, bpr = 4, ppc = 75, ppr = 75, copy = False):
        self.bpr = bpr
        self.ppc = ppc
        self.ppr = ppr
        self.positions = [self.indexToPos(j) for j in range(len(self.eventList)+1)]
        self.copy = copy
        super().__init__(parent)
        
    def dragEnterEvent(self, event):
        button = event.source()
        self.dragObj = button
        
        #get index to insert event into
        newIndex = self.posToIndex(event.pos())
        
        #add event to the END of new eventList if necessary
        if not self.copy and button not in self.eventList:
            self.eventList.insert(newIndex, button)
            self.positions = [self.indexToPos(j) for j in range(len(self.eventList)+ 1)]
            
        #update button's parent
        button.setParent(self.scroll)
            
        #render new list
        self.shuffle()
                
        #accept drag entry
        event.acceptProposedAction()
        
    def dragMoveEvent(self, event):
        button = event.source()
        
        if not self.copy:
            #get source index and current location's index equivalent
            sIndex = self.eventList.index(button)
            newIndex = self.posToIndex(event.pos())
            
            #shuffle things if necessary
            for j in range(len(self.eventList)):
                nIndex = j
                if nIndex > sIndex:
                    nIndex -= 1
                if nIndex >= newIndex:
                    nIndex += 1
                self.eventList[j].move(self.positions[nIndex])
    
    def dragLeaveEvent(self, event):
        #remove dragged object from eventList if necessary
        if not self.copy:
            self.eventList.remove(self.dragObj)
            self.positions.pop()
        
            #render new list
            self.shuffle()
                
    def dropEvent(self, event, button = None):
        if not button: #user can pass in button for forced drop event calls
            button = event.source()
        
        #move button to appropriate place in list
        newIndex = self.posToIndex(event.pos())
        try:
            self.eventList.remove(button)
            self.eventList.insert(newIndex, button)
        except ValueError:
            self.eventList.append(button)
            self.positions = [self.indexToPos(j) for j in range(len(self.eventList)+ 1)]
        
        #unhide button and rerender
        button.show()
        self.shuffle()
        
        #prepare button for next drag action
        button.bin = button.parent().parent().parent()
        
        #emit signal that drop was received
        button.clicked.connect(button.delete_button)
        
        #handle setting rest duration if necessary
        if isinstance(button, jc.Rest) and button.duration == 0:
            button.setText("")
            sb = QtWidgets.QPushButton(button)
            db = QtWidgets.QSpinBox(button)
            sb.setObjectName("setButton")
            db.setObjectName("durationBox")
            sb.setGeometry(10,40,55,30)
            db.setGeometry(10,5,55,30)
            button.clicked.disconnect()
            sb.clicked.connect(lambda: button.set_duration(db.value()))
            sb.clicked.connect(lambda: button.setText(str(button)))
            sb.clicked.connect(sb.close)
            sb.clicked.connect(db.close)
            sb.clicked.connect(lambda: button.clicked.connect(button.delete_button))
            sb.setText("set")
            db.setMaximum(1200)
            db.setSingleStep(10)
            sb.show()
            db.show()
        
        #resize scroll area window if necessary
        width = 75 * min([len(self.eventList) + 1, self.bpr])
        height = 75 * (len(self.eventList) // self.bpr + 1)
        button.parent().setGeometry(0,0,width,height)
    
    def shuffle(self):
        for i in range(len(self.eventList)):
            self.eventList[i].move(self.positions[i])
                    
    def posToIndex(self, pos):
        x = pos.x(); y = pos.y()
        r = y // self.ppr;
        r = min([r, (len(self.eventList)-1)//self.bpr]); r = max([r,0])
        c = x // self.ppc;
        c = min([c, self.bpr-1]); c = max([c, 0])
        i = min([r * self.bpr + c, len(self.eventList)-1])
        return i
    
    def indexToPos(self, index):
        r = index // self.bpr; c = index % self.bpr
        x = c * self.ppc; y = r * self.ppr
        p = QtCore.QPoint(x,y)
        return p
