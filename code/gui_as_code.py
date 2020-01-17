#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 10:49:34 2019

@author: Mason
"""
import jump_classes as jc
import gui_code as gc

uiAS = None; MainWindow = None; ui = None; events = None

def setup_as(tempUIAS, tempMainWindow, tempUI, tempEvents):
    #Initialize global variables
    global uiAS, MainWindow, ui, events
    uiAS=tempUIAS; MainWindow=tempMainWindow; ui=tempUI; events=tempEvents
    
    #Force the user to enter nice split values
    uiAS.spinBox_3.lineEdit().setReadOnly(True)
    
    #Handle funky switch input disabling
    uiAS.checkBox.clicked.connect(disable_switches)
    uiAS.checkBox_2.toggled['bool'].connect(default_switch)
        
    #Handle creation of new speed events and closing with buttons
    uiAS.pushButton.clicked.connect(create_speed)
    uiAS.pushButton_2.clicked.connect(MainWindow.AS.close)
    
#Create new speed event
def create_speed():
    d = uiAS.spinBox.value()
    sp = -1
    sw = -1
    if uiAS.checkBox.isChecked():
        sp = uiAS.spinBox_2.value()
        if uiAS.checkBox_2.isChecked():
            sw = uiAS.spinBox_3.value()
    name = uiAS.lineEdit.displayText()
    reps = 1
    events[name] = jc.Speed(d, sp, sw, reps, name=name)
    gc.update_libr()
    MainWindow.AS.close()

#Disable switches when splits are off
def disable_switches():
    uiAS.checkBox_2.setChecked(False)
    uiAS.spinBox_3.setValue(uiAS.spinBox.value())
    
#Set default switch value when switches are enabled
def default_switch(switches):
    if switches:
        uiAS.spinBox_3.setValue(uiAS.spinBox_2.value())
    else:
        uiAS.spinBox_3.setValue(uiAS.spinBox.value())
    