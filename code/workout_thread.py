#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 27 11:00:08 2019

@author: Mason
"""

from PyQt5 import QtCore
import threading

class WThread(QtCore.QThread):
    def __init__(self, workout=None, clicker=None, nowNextLabel=None, timer=None):
        super(WThread,self).__init__()
        self.e = threading.Event()
        self.workout = workout
        self.clicker = clicker
        self.nowNextLabel = nowNextLabel
        self.timer = timer
        
    def run(self):
        e = self.e
        clicker = self.clicker
        nowNextLabel = self.nowNextLabel
        timer = self.timer
        self.workout.run(e,clicker=clicker,nowNextLabel=nowNextLabel,timer=timer)