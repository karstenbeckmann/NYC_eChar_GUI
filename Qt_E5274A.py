"""
This is the main program that governs the Electrical wafer level Characterization integrated devices
Written by: Karsten Beckmann
Date: 7/25/2018
email: kbeckmann@sunypoly.edu
"""

import sys
from ctypes import *
import win32api
import win32con
import PlottingRoutines as PR
import threading as th
import queue as qu 
import time as tm
import StdDefinitions as std
import copy as dp
import os as os
import functools
import Qt_stdObjects as stdObj
import ECharacterization as eChar
import importlib as il

from PyQt5 import QtWidgets, QtGui, QtCore


class E5274AFrame(stdObj.stdFrame):

    def __init__(self, parent, MainGI, width, height, **kwargs):

        super().__init__(parent, MainGI, width, height, **kwargs)

        self.MainGI = MainGI
        self.Configuration = self.MainGI.Configuration
        self.width = width
        self.height = height
        self.Instruments = self.MainGI.Instruments
        self.SMUs = []
        self.layout = QtWidgets.QVBoxLayout(self)

        self.setFixedWidth(self.MainGI.getWindowWidth())
        self.setFixedHeight(self.MainGI.getWindowHeight())
        
        self.E5274s = self.Instruments.getInstrumentsByType("E5274A")
        self.SMUs = []
        if len(self.E5274s) != 0:
            for ent in self.E5274s:
                self.SMUs.append(stdObj.ADCFrame(self, self.MainGI, ent['GPIB']))
                self.layout.addWidget(self.SMUs[-1])

    def updateContent(self):
        for smu in self.SMUs:
            smu.close()
        for n in range(len(self.SMUs)):
            self.SMUs.pop(0)

        self.E5274s = self.Instruments.getInstrumentsByType("E5274A")
        if len(self.E5274s) != 0:
            for ent in self.E5274s:
                self.SMUs.append(stdObj.ADCFrame(self, self.MainGI, ent['GPIB']))
                self.layout.addWidget(self.SMUs[-1])
    
    def update(self):

        if self.MainGI.isRunning():
            self.setDisabled(True)
        else:
            self.setEnabled(True)
