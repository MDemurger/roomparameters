#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 19:36:05 2021

@author: maxime
"""

import pyqtgraph as pg
from PyQt5 import QtWidgets
from PyQt5 import QtCore as qtc

class RoomWidget(QtWidgets.QWidget):
    
    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self, parent)   
        self.plotWidget = pg.plot()
        self.vbl = QtWidgets.QVBoxLayout()
        self.vbl.addWidget(self.plotWidget)
        self.setLayout(self.vbl)
        self.setupplot()
        
    def setupplot(self):        
        self.plotWidget.setBackground("w")
        self.plotWidget.setTitle("Energy curves")
        self.plotWidget.setLabel('right', 'Level dBFS')
        self.plotWidget.showLabel('right', show=True)
        self.maxtime = 1
        #self.impulseformat = "Raw impulse"
        self.window_state = False
        
    def update_graph(self,xaxis,amp,sample_rate,colorpen):
        if colorpen ==1:
            self.plotWidget.plot(xaxis[0:len(amp)],amp,pen=(0, 0, 255))
        if colorpen==2:
            self.plotWidget.plot(xaxis[0:len(amp)],amp,pen=pg.mkPen('r', width=5))
        if colorpen==3:
            self.plotWidget.plot(xaxis[0:len(amp)],amp,pen=pg.mkPen('g', width=2))
        #self.plotWidget.plot(xaxis[0:len(amp)],amp,pen=colorpen)
        #self.plotWidget.plot(xaxis[0:len(amp3)],amp3,pen=pg.mkPen('r', width=5))
        self.time=len(amp)/sample_rate
        
        self.formatplot()
        
    def clear(self):
        self.plotWidget.clear()
        
    def formatplot(self):    
        if self.time>self.maxtime:
            self.maxtime=self.time
        range = self.plotWidget.getViewBox().viewRange() 
        
        self.plotWidget.getViewBox().setLimits(xMin=0, xMax=self.maxtime,   
                               yMin=-100, yMax=0)   
        
        self.plotWidget.getViewBox().setLimits(minYRange=100)  
        self.plotWidget.getViewBox().enableAutoRange(axis='y')
        self.plotWidget.getViewBox().setAutoVisible(y=True)




