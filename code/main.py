#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  2 22:04:42 2019

@author: Mason
"""

import gui; from gui_code import setup_main, stop_workout
import jump_classes as jc
import widget_classes as wc
import os, sys
from PyQt5 import QtCore, QtWidgets

events = {}

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def write_saved_events():
    with open(filename,'w') as f:
        for name in events:
            f.write(events[name].write() + '\n')    
    
if __name__ == "__main__":
    #Run the GUI
    app = QtCore.QCoreApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    
    #Load and save event file
    filename = resource_path('saved_events.txt')
    with open(filename) as f:
        fstrings = f.read().splitlines()
        for line in fstrings:
            if line.startswith('e'):
                tempEvent = jc.Event.read(line.strip('e'))
                events[tempEvent.name] = tempEvent
            elif line.startswith('r'):
                tempEvent = jc.Rest.read(line.strip('r'))
                events[tempEvent.name] = tempEvent
            elif line.startswith('s'):
                tempEvent = jc.Speed.read(line.strip('s'))
                events[tempEvent.name] = tempEvent
            elif line.startswith('f'):
                tempEvent = jc.Freestyle.read(line.strip('f'))
                events[tempEvent.name] = tempEvent
    #More GUI            
    MainWindow = wc.BigWindow()
    ui = gui.Ui_MainWindow()
    ui.setupUi(MainWindow)
    setup_main(ui, MainWindow, events)
    MainWindow.show()
    app.aboutToQuit.connect(write_saved_events)

    #Run application
    try:
        sys.exit(app.exec_())
    except SystemExit:
        stop_workout()
        app.quit()