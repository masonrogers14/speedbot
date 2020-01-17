#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 26 23:21:08 2019


@author: Mason
"""
import time
import json
import numpy as np
import pyaudio
from PyQt5 import QtCore
import ddb_code as dd

fs = 44100 #audio sample rate
restWarning = 4
splitFreq = 440.0
switchFreq = 660.0
alternFreq = 880.0
stopFreq = 880.0
startFreq = 880.0
warnFreq = 330.0

p = pyaudio.PyAudio()
# for paFloat32 sample values must be in range [-1.0, 1.0]
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=fs,
                output=True)

#Produce beeps
def beep(volume, duration, f):
    # generate samples, note conversion to float32 array
    samples = (np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32)
    
    # play. May repeat with different volume values (if done interactively) 
    stream.write(volume*samples)
    
''' A speed event with specified duration and split/switch intervals.
    Can include name and number of reps for alternating setups.
'''
class Event(dd.dragDropButton):
    def __init__(self, duration = 0, splits = [], switches = [],
                 alterns = [], warnings = [], name = None, parent = None):
        self.duration = duration
        self.splits = splits
        self.switches = switches
        self.alterns = alterns
        self.warnings = warnings
        self.name = name
        super().__init__(parent)
    
    def __str__(self):
        if self.name: #give name and info about alternation/reps if needed
            return self.name
        else:
            return 'no name'
    
    ''' Run an individual event
    
        args:   lastSplit (starting time to synchronize to system clock)
                e (event owned by thread that runs workout; halts if set)
        outs:   currentTime (best approximation of ending beep time; can drift)
                -1 (if broken)
    '''
    def run(self, startTime, e = None, clicker = None, timer = None):
        #Set relevant initial time data, removing 'beeps from the past'
        tempSplits = [(s+startTime) for s in self.splits if s>0]
        tempSwitches = [(s+startTime) for s in self.switches if s>0]
        tempAlterns = [(a+startTime) for a in self.alterns if a>0]
        tempWarnings = [(w+startTime) for w in self.warnings if w>0]
        stopTime = startTime + self.duration
        tempSplits.append(stopTime)
        tempSwitches.append(stopTime)
        tempAlterns.append(stopTime)
        tempWarnings.append(stopTime)
        log = []; t = 0
        
        #Main loop        
        currentTime = time.time()
        while currentTime < stopTime:
            #Update the timer if necessary
            if timer:
                timer.show_time(currentTime, startTime)
                
            #Check if it's time for a split beep
            if currentTime > tempSplits[0]:
                t = tempSplits.pop(0)
                beep(.5, 1.0, splitFreq)
                if clicker:
                    log.append([self.name, t-startTime, clicker.count])
                    clicker.log[startTime] = log
            
            #Check if it's time for a switch beep
            if currentTime > tempSwitches[0]:
                tempSwitches.pop(0)
                beep(.5, 1.0, switchFreq)
            
            #Check if it's time for an alternation beep
            if currentTime > tempAlterns[0]:
                beep(.5, 1.0, alternFreq)
                tempAlterns.pop(0)
            
            #Check if it's time for a warning beep
            if currentTime > tempWarnings[0]:
                tempWarnings.pop(0)
                beep(.5, 8.0, warnFreq)
            
            currentTime = time.time()
            
            #Stop thread running workout if necessary
            if e:
                if e.isSet():
                    return -1
                
        #End event
        if clicker:
            log.append([self.name, stopTime-startTime, clicker.count])
            clicker.log[startTime] = log
        if timer:
            timer.show_time(currentTime, startTime)
        beep(.5, 1.0, stopFreq)
        return currentTime
    
    def write(self):
        return 'e' + json.dumps([self.duration, self.splits, self.switches,
                           self.alterns, self.warnings, self.name])
    
    def read(string):
        s = json.loads(string)
        return Event(s[0],s[1],s[2],s[3],s[4],s[5])
    
    def repeat(self, reps):
        d = self.duration
        tempDuration = d * reps
        rTimes = d * np.arange(reps)
        tempSplits = [s+t for t in rTimes for s in self.splits]
        tempSwitches = [s+t for t in rTimes for s in self.switches]
        tempAlterns = [s+t for t in rTimes for s in self.alterns]
        tempWarnings = [s+t for t in rTimes for s in self.warnings]
        self.duration = tempDuration
        self.splits = tempSplits
        self.switches = tempSwitches
        self.alterns = tempAlterns
        self.warnings = tempWarnings
        
    def duplicate(self):
        newEvent = Event(self.duration, self.splits, self.switches,
                             self.alterns, self.warnings, self.name,
                             self.parent())
        return newEvent
        
''' Subclass of event for rest
    args:   duration
'''    
class Rest(Event):
    def __init__(self, d = 0):
        super().__init__(d, [], [], [], [d - restWarning, d],
             name='rest')
    
    def __str__(self):
        if self.duration > 0:
            return('Rest \n' + str(self.duration))
        else:
            return('Rest')
            
    def set_duration(self, d):
        self.duration = d
        self.warnings = [d - restWarning, d]
        
    def write(self):
        return 'r' + json.dumps(self.duration)
    
    def read(string):
        s = json.loads(string)
        return Rest(s)
    
    def repeat(self, reps):
        self.duration *= reps
        self.__init__(self.duration)
        
    def duplicate(self):
        newEvent = Rest(self.duration)
        newEvent.setParent(self.parent())
        return newEvent
        
''' Subclass of event for speed events
    args:   duration (per repetition if repeating)
            split interval
            switch interval
            number of repetitions
            name
'''
class Speed(Event):
    def __init__(self, d, sp=-1, sw=-1, reps=1, name=None):
        self.reps = reps
        self.alternating = reps > 1
        self.switching = (sw > 0)
        self.splitting = (sp > 0)
        self.dpe = d
        self.sp = sp
        self.sw = sw
        
        if name:
            self.name = name
        else:
            if self.switching:
                self.name = str(d // self.sw) + ' x ' + str(self.sw)
            else:
                self.name = str(d)
                
        alList = [d*i for i in list(range(1, reps))]
        
        d *= reps #total duration
        spList = [sp*i for i in list(range(1, int(d/sp)))]
        swList = [sw*i for i in list(range(1, int(d/sw)))]
        
        super().__init__(d, spList, swList, alList, [], name = name)

    def __str__(self):
        out = self.name
        if self.reps > 1:
            out += ('\n(' + str(self.reps) + ')')
        return out
    
    def write(self):
        return 's' + json.dumps([self.duration, self.sp, self.sw,
                                 self.reps, self.name])
    
    def read(string):
        s = json.loads(string)
        return Speed(s[0], s[1], s[2], s[3], name = s[4])
    
    def repeat(self, reps):
        self.reps = reps
        self.__init__(self.dpe, self.sp, self.sw, self.reps, self.name)
        
    def duplicate(self):
        newEvent = Speed(self.dpe, self.sp, self.sw, self.reps, self.name)
        newEvent.setParent(self.parent())
        return newEvent
        
        
'''Subclass of event for freestyle events
'''
class Freestyle(Event):
    def __init__(self):
        super().__init__(75, [45,60,75], [], [], [], name='freestyle')
        
    def __str__(self):
        return 'FS'
    
    def write(self):
        return 'f'
    
    def read(string):
        return Freestyle()
    
    def duplicate(self):
        newEvent = Freestyle()
        newEvent.setParent(self.parent())
        return newEvent
        
''' A collection of speed events with the option to repeat
'''        
class Workout(dd.dragDropBucket):
    def __init__(self, parent = None, eventList = None, reps = 1, name = None):
        if eventList:
            self.eventList = eventList #List of events in workout
        else:
            self.eventList = []
        self.reps = reps #Number of repetitions of list
        self.dropAction = QtCore.Qt.MoveAction
        super().__init__(parent)

    def __str__(self):
        out = ''
        #Begin by listing the events
        if self.eventList:
            for event in self.eventList:
                out = out + str(event) + '\n'
        else:
            return 'workout is empty'
        
        #Specify number of full-workout repetitions
        if self.reps > 1:
            out = out + '\n' + 'do ' + str(self.reps) + ' repetitions'
        return out
    
    '''Run a workout

        args:   e (thread event to be set if workout halted)  
                ui (GUI main window reference to control GUI buttons)
    '''
    def run(self, e = None, clicker = None, nowNextLabel = None, timer = None):    
        #Generates full event list
        tempList = self.eventList * self.reps 
        
        #Prevent workout from ending in a rest
        while tempList:
            if isinstance(tempList[-1],Rest):
                tempList.pop()
            else:
                break
        
        #Ski race-style intro beeps; begins synchronizing clock
        intro = Speed(5,1)
        lastEvent = intro.run(time.time(),e)
                
        #Iterate through list of events and run each (see above)
        for event in tempList:
            #Reset clicker if one is given
            if clicker:
                clicker.count = 0
                clicker.setText(str(clicker.count))
                
            #Adjust label if one is given
            if nowNextLabel:
                try:
                    nowNextLabel.setText('Now: ' \
                                         + str(event).replace('\n',' ') \
                                         + '\n\nNext: '\
                                         + str(tempList[tempList.index(event)+1]).replace('\n',' '))
                except IndexError:
                    nowNextLabel.setText('Now: ' \
                                         + str(event).replace('\n',' ') \
                                         + '\n\nNext: Done')
                
            #Check for event set as a halt signal
            lastEvent = event.run(lastEvent,e,clicker=clicker,timer=timer)
            if lastEvent < 0:
                break
            
        #Soccer match-style outro beeps
        time.sleep(.25)
        beep(.5, 1.0, stopFreq)
        time.sleep(.25)
        beep(.5, 2.0, stopFreq)
        
        #Clear label if necessary
        if nowNextLabel:
            nowNextLabel.setText('Now: \n\nNext:')
            
        #Reset timer if necessary
        if timer:
            timer.reset()
    
    #Return total workout duration    
    def getTotalDuration(self):
        totalDuration = 0
        for event in self.eventList:
            totalDuration += event.duration
        return totalDuration
        
    #Remove events from event list
    def remove_event(self, event):
        self.eventList.remove(event)
        self.positions.pop()
        event.deleteLater()
        self.shuffle()
    
    #Signals to manipulate GUI when workout parameters change
    emptied = QtCore.pyqtSignal(bool)
    filled = QtCore.pyqtSignal(bool)
    
    def write(self):
        numEvents = len(self.eventList)
        out = 'w'+str(numEvents)+'\n'
        for event in self.eventList:
            out += event.write() + '\n'
        return out
    
    def read(stringList):
        eventList = []
        for string in stringList:
            eventList.append(Event.read(string))
        return Workout(eventList=eventList)
