#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 31 15:47:34 2019

@author: Mason

''' Code for the MAIN UI
'''

"""
import workout_thread as wt
import jump_classes as jc
import widget_classes as wc
import gui_manageevents as gui_me; from gui_me_code import setup_me
import gui_addspeed as gui_as; from gui_as_code import setup_as
from PyQt5 import QtCore, QtWidgets

uiDict = {} #stores manipulable UI objects/enabled state
#ui, MainWindow, events initialized on setup
ui = None; MainWindow = None; events = None;

#Prescribe how the UI interacts with the workout object
def setup_main(tempUI, tempMainWindow, tempEvents):
    #Initialize global variables
    global ui, MainWindow, events
    ui = tempUI; MainWindow = tempMainWindow; events = tempEvents
        
    #Add Pushbutton handling:
    ui.pushButton_4.clicked.connect(run_workout)
    ui.pushButton_5.clicked.connect(stop_workout)
    
    #Add Workout reps/Rest warning handling
    ui.spinBox_3.valueChanged['int'].connect(change_reps)
    ui.spinBox_4.valueChanged['int'].connect(change_rw)
    
    #Handle menu actions
    ui.actionAdd_Speed_Event.triggered.connect(popup_as)
    ui.actionManage_Events.triggered.connect(popup_me)
    ui.actionCurrent_Next_Events.triggered.connect(lambda: update_display(0))
    ui.actionTimer.triggered.connect(lambda: update_display(1))
    ui.actionClicker.triggered.connect(lambda: update_display(2))
    
    #Install event library
    update_libr()
    
    #Fix drag/drop characteristics from defaults
    ui.workout.bpr = 100
    ui.library.copy = True
    
    #Define scroll areas
    ui.workout.scroll = ui.scrollAreaWidgetContents_2
    ui.library.scroll = ui.scrollAreaWidgetContents
    
    #Initialize displays
    ui.clicker = wc.QClicker(ui.widget)
    ui.clicker.setGeometry(0,0,ui.widget.width(),ui.widget.height())
    ui.clicker.setStyleSheet("QClicker {font-size : 144pt;}")
    ui.clicker.setText('0')
    ui.timer = wc.QClock(ui.widget)
    ui.timer.setGeometry(40,10,490,460)
    ui.timer.setStyleSheet("QClock {color : rgb(2,1,53); border : 0px;}")
    ui.timer.reset()
    ui.nowNextLabel = QtWidgets.QLabel('Now: \n\nNext: ',ui.widget)
    ui.nowNextLabel.setStyleSheet("QLabel {font-size : 72pt; color : rgb(2,1,53);}")
    ui.nowNextLabel.setGeometry(10,10,550,460)
    ui.nowNextLabel.show()
    update_display(ui.comboBox.currentIndex())
    
    #Handle combobox changes
    ui.comboBox.currentIndexChanged['int'].connect(update_display)
    
def update_libr():
    #Install/update event library
    for event in ui.library.eventList:
        event.close()
    ui.library.eventList = []
    for name in events:
        event = events[name]
        duplicate = event.duplicate()
        duplicate.setParent(ui.scrollAreaWidgetContents)
        duplicate.setText(str(duplicate))
        duplicate.show()
        ui.library.eventList.append(duplicate)
    ui.library.positions = [ui.library.indexToPos(j) for j in range(len(ui.library.eventList) + 1)]
    ui.library.shuffle()
    width = 75 * min([len(ui.library.eventList) + 1, ui.library.bpr])
    height = 75 * (len(ui.library.eventList) // ui.library.bpr + 1)
    ui.scrollAreaWidgetContents.setGeometry(0,0,width,height)
        
def update_dict():
    #Update dictionary of interactive UI objects and enabled state
    for obj in ui.__dict__:
        if isinstance(ui.__dict__[obj], QtWidgets.QPushButton) \
        or isinstance(ui.__dict__[obj], QtWidgets.QCheckBox) \
        or isinstance(ui.__dict__[obj], QtWidgets.QComboBox) \
        or isinstance(ui.__dict__[obj], QtWidgets.QSpinBox) \
        or isinstance(ui.__dict__[obj], QtWidgets.QScrollArea):
            uiDict[ui.__dict__[obj]] = ui.__dict__[obj].isEnabled()

#Change repetitions of the workout    
def change_reps(reps):
    ui.workout.reps = reps
    if reps > 1:
        ui.label_3.setText('x '+str(reps))
    else:
        ui.label_3.setText('')

#Change amount of warning before end of rest
def change_rw(rw):
    jc.restWarning = rw
    for event in ui.workout.eventList:
        if isinstance(event, jc.Rest):
            event.warnings = [event.duration - rw, event.duration]

#Run the workout on separate thread    
def run_workout():
    #Update dictionary to know what to unfreeze when workout is done
    update_dict()
    
    #Set up thread to run event and thread event to halt if needed
    x = wt.WThread(ui.workout, timer=ui.timer,
                   clicker=ui.clicker, nowNextLabel=ui.nowNextLabel)
    x.setParent(QtCore.QThread.currentThread())
    
    #Freeze and unfreeze GUI when necessary
    x.started.connect(freeze_gui, type=QtCore.Qt.QueuedConnection)
    x.finished.connect(freeze_gui, type=QtCore.Qt.QueuedConnection)

    x.start()
    #I have no idea why this line of code is necessary, but it is
    QtWidgets.QApplication.processEvents()

#Stop workout thread    
def stop_workout():
    #Find the right thread
    x = QtCore.QThread.currentThread().findChild(wt.WThread)
    
    #Set its event and let it run out
    if x:
        x.e.set()
        x.wait() 
    
#Freezes GUI when running an event; lifts freeze when done
def freeze_gui():
    done = ui.pushButton_5.isEnabled()
    for obj in uiDict:
        obj.setEnabled(done and uiDict[obj])
    ui.pushButton_5.setDisabled(done)
    ui.clicker.setEnabled(True)
    ui.comboBox.setEnabled(True)
    
def update_display(option):
    if option == 0:
        ui.timer.hide()
        ui.clicker.hide()
        ui.nowNextLabel.show()
    elif option == 1:
        ui.clicker.hide()
        ui.nowNextLabel.hide()
        ui.timer.show()
    elif option == 2:
        ui.nowNextLabel.hide()
        ui.timer.hide()
        ui.clicker.show()

#Generate add speed popup
def popup_as():
    MainWindow.AS = QtWidgets.QDialog()
    uiAS = gui_as.Ui_Dialog()
    uiAS.setupUi(MainWindow.AS)
    setup_as(uiAS, MainWindow, ui, events)
    MainWindow.AS.finished.connect(ui.library.shuffle)
    MainWindow.AS.show() 

#Generate add speed popup
def popup_me():
    MainWindow.ME = QtWidgets.QDialog()
    uiME = gui_me.Ui_Dialog()
    uiME.setupUi(MainWindow.ME)
    setup_me(uiME, MainWindow, ui, events)
    MainWindow.ME.finished.connect(ui.library.shuffle)
    MainWindow.ME.show()
