#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 10:17:50 2019

@author: Mason
"""
from PyQt5 import QtCore, QtWidgets
import gui_code as gc
import jump_classes as jc

uiME = None; MainWindow = None; ui = None; events = None

def setup_me(tempUIME, tempMainWindow, tempUI, tempEvents):
    #Initialize global variables
    global uiME, MainWindow, ui, events
    uiME=tempUIME; MainWindow=tempMainWindow; ui=tempUI; events=tempEvents
    
    #Prepare Pushbutton handling
    uiME.pushButton.clicked.connect(reorder_events)
    uiME.pushButton_2.clicked.connect(delete_event)

    #Initialize event list widget
    _translate = QtCore.QCoreApplication.translate
    for name in events:
        item = QtWidgets.QListWidgetItem()
        item.setText(_translate("Dialog", name))
        uiME.listWidget.addItem(item)
        if isinstance(events[name], jc.Rest) or isinstance(events[name], jc.Freestyle):
            item.setFlags(QtCore.Qt.ItemFlags(4))
        
#Delete event from directory
def delete_event():
    name = uiME.listWidget.currentItem().text()
    for i, eventName in enumerate(events):
        if eventName == name:
            del events[eventName]
            uiME.listWidget.takeItem(i)
            break   
    gc.update_libr()
        
#Reorder event list
def reorder_events():
    while uiME.listWidget.item(0):
        name = uiME.listWidget.takeItem(0).text()
        event = events.pop(name)
        events[name] = event
    gc.update_libr()
    MainWindow.ME.close()
    