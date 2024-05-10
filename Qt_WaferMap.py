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
import math as ma
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import darkdetect
import copy as cp

import PyQt5
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette, QColor
from PyQt5 import QtGui
from PyQt5 import QtCore
import Qt_stdObjects as stdObj

from pyqtgraph import PlotWidget
import pyqtgraph as pg

import matplotlib._pylab_helpers as plotHelper

class WaferMap(stdObj.stdFrameGrid):

    def __init__(self, parent, MainGI, columns, rows, width, height, **kwargs):

        self.dieFolder = None
        self.MainGI = MainGI
        self.Instruments = self.MainGI.Instruments
        if 'dieFolder' in kwargs:
            self.dieFolder = kwargs['dieFolder']
            del kwargs['dieFolder']
        else:
            try:
                self.dieFolder = MainGI.subFolder
            except ValueError:
                None

        super().__init__(parent, MainGI, columns, rows, width, height, **kwargs)
        
        self.Configuration = self.MainGI.getConfiguration()
        self.CurChuckPosition = cp.deepcopy(self.Instruments.getProberChuckPosition())
        self.Entries = []

        self.Rotations = {}
        self.Rotations["Down"] = 180
        self.Rotations["Left"] = 270
        self.Rotations["Up"] = 0
        self.Rotations["Right"] = 90
        
        self.curProberState = True

        mapVLayout = QtWidgets.QHBoxLayout()
        mapVLayout.addStretch()

        plotRowSpan = 10
        plotColSpan = 5
        wMwidth = int(plotColSpan*width/columns*0.95)
        wMheight = int(plotRowSpan*height/rows*0.95)

        if wMwidth > wMheight:
            wMsize = wMheight
        else:
            wMsize = wMwidth

        self.WaferMap = PlotWidget(self, config=self.Configuration, name="WaferMapPlotWidget", backgroundColor=self.MainGI.getBackgroundColor(True), ringColor=self.MainGI.getLabelColor(True), title="Wafer Map")
        self.WaferMap.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.WaferMap.setMinimumWidth(wMsize)
        self.WaferMap.setMinimumHeight(wMsize)

        mapVLayout.addWidget(self.WaferMap)
        mapVLayout.addStretch()

        self.centralWaferMapWidget = QtWidgets.QWidget(self)
        self.centralWaferMapWidget.setLayout(mapVLayout)

        row = 0
        col = 0
        self.addWidget(self.centralWaferMapWidget, row=row, column=col, columnspan=plotColSpan,  rowspan=plotRowSpan)

        self.darkMode = darkdetect.isDark()
        
        col = 5
        self.__SubFolder = stdObj.Entry(self, MainGI, "Subfolder", maxLength=10, sizePolicy=(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.addWidget(self.__SubFolder, row=row, column=col+2, columnspan=2)
        self.TxSubFolder = stdObj.Label("Sub Folder:", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxSubFolder, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        row = row + 1
        self.__WaferID = stdObj.Entry(self, MainGI, "WaferID", maxLength=15, sizePolicy=(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.addWidget(self.__WaferID, row=row, column=col+2, columnspan=2)
        self.TxWaferID=stdObj.Label("Wafer ID:", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxWaferID, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        row = row +1
        self.__DeviceName = stdObj.Entry(self, MainGI, "DeviceName", maxLength=15, sizePolicy=(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.addWidget(self.__DeviceName, row=row, column=col+2, columnspan=2)
        self.TxDeviceName= stdObj.Label("Device Name:", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxDeviceName, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        row = row + 1
        self.__WaferSize = stdObj.Entry(self, MainGI, "WaferSize", validate='all', validateNumbers="[0-9]+", command=self.MapUpdateDieMap, sizePolicy=(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.addWidget(self.__WaferSize, row=row, column=col+2, columnspan=1)
        
        self.__WaferRotation = stdObj.ComboBox(self, MainGI, "WaferRotation", self.Rotations, initValue=list(self.Rotations.values())[0], Type=int, sizePolicy=[QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding], command=self.CallWaferRotation)
        self.addWidget(self.__WaferRotation, row=row, column=col+3, columnspan=1)

        self.TxWaferSize=stdObj.Label("Wafer Size (mm) / Rot.:", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxWaferSize, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        row = row + 1
        self.TxY=stdObj.Label( "Y", self)
        self.TxY.setAlignment(QtCore.Qt.AlignCenter)
        self.addWidget(self.TxY, row=row, column=col+3, columnspan=1)
        self.TxY=stdObj.Label("X", self)
        self.TxY.setAlignment(QtCore.Qt.AlignCenter)
        self.addWidget(self.TxY, row=row, column=col+2, columnspan=1)

        row = row + 1
        self.DevStartX = stdObj.Entry(self, MainGI, "DeviceStartX", validate='all', validateNumbers="[0-9]+", sizePolicy=(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.addWidget(self.DevStartX, row=row, column=col+2, columnspan=1)
        self.DevStartY = stdObj.Entry(self, MainGI, "DeviceStartY", validate='all', validateNumbers="[0-9]+", sizePolicy=(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.addWidget(self.DevStartY, row=row, column=col+3, columnspan=1)
        self.TxDeviceStart=stdObj.Label("Device Start", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxDeviceStart, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        row = row + 1
        self.__DieSizeX = stdObj.Entry(self, MainGI, "DieSizeX", validate='all', validateNumbers="([0-9]+(\.[0-9]+)?|\.[0-9]+)$", command=self.MapUpdateDieMap, sizePolicy=(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.addWidget(self.__DieSizeX, row=row, column=col+2, columnspan=1)
        self.__DieSizeY = stdObj.Entry(self, MainGI, "DieSizeY", validate='all', validateNumbers="([0-9]+(\.[0-9]+)?|\.[0-9]+)$", command=self.MapUpdateDieMap, sizePolicy=(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.addWidget(self.__DieSizeY, row=row, column=col+3, columnspan=1)
        self.TxDieSize=stdObj.Label("Die Size (mm):", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxDieSize, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        row = row + 1
        
        self.__CenLocX = stdObj.Entry(self, MainGI, "CenterLocationX", validate='all', validateNumbers="^[-+]?([0-9]+(\.[0-9]+)?|\.[0-9]+)$", command=self.MapUpdateDieMap, sizePolicy=(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.addWidget(self.__CenLocX, row=row, column=col+2, columnspan=1)
        self.__CenLocY = stdObj.Entry(self, MainGI, "CenterLocationY", validate='all', validateNumbers="^[-+]?([0-9]+(\.[0-9]+)?|\.[0-9]+)$", command=self.MapUpdateDieMap, sizePolicy=(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.addWidget(self.__CenLocY, row=row, column=col+3, columnspan=1)
        self.TxCenterLocation=stdObj.Label("Cen. Location (%):", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxCenterLocation, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        row = row + 1
        
        self.__MulipleDevices = stdObj.CheckBox(self, MainGI, "MultipleDev", command=self.CheckBoxMultDev, alignment=QtCore.Qt.AlignLeft, sizePolicy=(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.addWidget(self.__MulipleDevices, row=row, column=col+2, columnspan=1, alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.TxMultDev = stdObj.Label("Multiple Devices:", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxMultDev, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        row = row + 1

        self.__NumOfXDev = stdObj.Entry(self, MainGI, "NumXdevices", validate='all', validateNumbers="[0-9]+", sizePolicy=(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.addWidget(self.__NumOfXDev, row=row, column=col+2, columnspan=1)
        self.__NumOfYDev = stdObj.Entry(self, MainGI, "NumYdevices", validate='all', validateNumbers="[0-9]+", sizePolicy=(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.addWidget(self.__NumOfYDev, row=row, column=col+3, columnspan=1)
        self.TxNumOfDev=stdObj.Label("Number of Devices:", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxNumOfDev, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        row = row + 1

        self.__XPitch = stdObj.Entry(self, MainGI, "XPitch", validate='all', validateNumbers="^[-+]?([0-9]+(\.[0-9]+)?|\.[0-9]+)$", sizePolicy=(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.addWidget(self.__XPitch, row=row, column=col+2, columnspan=1)
        self.__YPitch = stdObj.Entry(self, MainGI, "YPitch", validate='all', validateNumbers="^[-+]?([0-9]+(\.[0-9]+)?|\.[0-9]+)$", sizePolicy=(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.addWidget(self.__YPitch, row=row, column=col+3, columnspan=1)
        self.TxDevPitch=stdObj.Label("Dev. Pitch (um):", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxDevPitch, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        
        self.TxLog=stdObj.Label("Log and Information:", self)
        self.addWidget(self.TxLog, row=row, column=0, columnspan=2, alignment=QtCore.Qt.AlignLeft)
        self.TxLogSave=stdObj.Label("save", self)
        self.addWidget(self.TxLogSave, row=row, column=2, columnspan=1, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.__LogSaveCheckbox = stdObj.CheckBox(self, self.MainGI, "InfoLogSave", sizePolicy=(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.addWidget(self.__LogSaveCheckbox, row=row, column=3, columnspan=1, alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.__LogClearButton = stdObj.PushButton("Clear", self, sizePolicy=[QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding], command=self.clearLogFrame)
        self.addWidget(self.__LogClearButton, row=row, column=4, columnspan=1, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.LogFrame = stdObj.InfoLog(self, "InfoLog", MainGI=MainGI, SaveObj="InfoLogSave", maxEntries=200, sizePolicy=[QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding])
        self.addWidget(self.LogFrame, row=row+1, column=0, columnspan=5, rowspan=5)

        row = row + 1
        self.__MultipleDies = stdObj.CheckBox(self, MainGI, "MultipleDies", command=self.CheckBoxMultDies, alignment=QtCore.Qt.AlignLeft, sizePolicy=(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.addWidget(self.__MultipleDies, row=row, column=col+2, columnspan=1, alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.TxMultDies=stdObj.Label("Multiple Dies:", self)
        self.addWidget(self.TxMultDies, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        row = row + 1


        self.__DieFileButton = stdObj.fileButton(self, MainGI, "DieFile", sizePolicy=[QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding], fileFormat = "CSV file (*.csv)", subFolder=self.dieFolder, command=self.DieFileButton)

        DieMaps = self.Configuration.getAllDieMaps()
        self.__DieMaps = stdObj.ComboBox(self, MainGI, "DieMap", list(DieMaps), Type=int, sizePolicy=(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding), command=self.CallDieMaps)
        self.addWidget(self.__DieMaps, row=row, column=col+2, columnspan=1)
        self.__DieMapUpdate = stdObj.PushButton("Update", self, sizePolicy=(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding), command=self.MapUpdateDieMap)
        self.addWidget(self.__DieMapUpdate, row=row, column=col+3, columnspan=1)

        self.TxDieMap=stdObj.Label("Die Map:", self)
        self.TxDieMap.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxDieMap, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        row = row + 1

        self.addWidget(self.__DieFileButton, row=row, column=col+2, columnspan=2)
        self.TxDieFile=stdObj.Label("Die File:", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxDieFile, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        row = row + 1

        self.__SpecCode = stdObj.Entry(self, MainGI, "SpecCode", maxLength=20, sizePolicy=(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.addWidget(self.__SpecCode, row=row, column=col+2, columnspan=2)
        self.TxSpecCode=stdObj.Label("Spec Code:", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxSpecCode, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        row = row + 1
        
        self.__UseMatrix = stdObj.CheckBox(self, MainGI, "UseMatrix", command=self.CheckBoxMatrix, alignment=QtCore.Qt.AlignLeft)
        self.addWidget(self.__UseMatrix, row=row, column=col+2, columnspan=1, alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.TxUseMatrix=stdObj.Label("Use Matrix:", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxUseMatrix, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        row = row + 1

        self.CheckBoxMultDev()
        self.CheckBoxMultDies()
        self.CheckBoxMatrix()

        self.setLayout(self.layout)
        self.update()
        self.MapUpdateDieMap()

        self.CallWaferRotation(self.Configuration.getWaferRotation())

    def DieFileButton(self):
        self.__DieMaps.setCurrentIndex(-1)

        self.Configuration.UpdateDies()
        self.MapUpdateDieMap()
        
    def CheckBoxMatrix(self):
        self.Configuration.setUseMatrix(self.__UseMatrix.getVariable())

    def MapUpdateDieMap(self):
        if not self.MainGI.running and self.curProberState and self.__MultipleDies.getVariable():
            self.Configuration.UpdateDies()
            self.WaferMap.update(locations=self.Configuration.getDies(), Folder=self.Configuration.getMainFolder(), DieSizeX=self.Configuration.getDieSizeX(), DieSizeY=self.Configuration.getDieSizeY(), 
                                        WaferSize=self.Configuration.getWaferSize(), CenterLocation=self.Configuration.getCenterLocation(), NumOfDies=self.Configuration.getNumOfDies(), 
                                        NumOfDevices=self.Configuration.getNumOfDevices(), NumOfXDevices=self.Configuration.getNumXDevices(), NumOfYDevices=self.Configuration.getNumYDevices(), WaferRotation=self.Configuration.getWaferRotation())
        else:
            self.MainGI.WriteError("Measurement is currently running.")

    def CallWaferRotation(self, rot):
        self.WaferMap.updateWaferRotation(rot)
                
        
    def update(self,**kwargs):

        if self.Instruments.getMatrixInstrument() == None:
            self.hideMatrix()
            self.disableMatrix()
        else:
            self.showMatrix()
            self.enableMatrix()

        if (self.Instruments.getProberInstrument() == None) and self.curProberState:
            self.disableProber()
            self.WaferMap.setBlank(True)
            self.curProberState = False

        if (self.Instruments.getProberInstrument() != None) and not self.curProberState:
            self.enableProber()
            self.WaferMap.setBlank(False)
            self.curProberState = True
        
        if self.MainGI.Instruments.getProberChuckPosition() != self.CurChuckPosition:
            self.CurChuckPosition = cp.deepcopy(self.MainGI.Instruments.getProberChuckPosition())
            self.WaferMap.update(ChuckPosition=self.CurChuckPosition)
        
        if "BackgroundColor" in kwargs:
            self.WaferMap.updateBackground(kwargs["BackgroundColor"])
            
        if "LabelColor" in kwargs:
            self.WaferMap.changeRingColor(kwargs["LabelColor"])

    def clearLogFrame(self):
        self.Configuration.clearLogList()
        self.MainGI.clearLogFrame()


    def CheckBoxMultDev(self):
        if not self.__MulipleDevices.getVariable():
            self.__NumOfXDev.setEnabled(False)
            self.__NumOfYDev.setEnabled(False)
            self.__XPitch.setEnabled(False)
            self.__YPitch.setEnabled(False)
            self.Configuration.setValue("MultipleDev",False)
        else:
            if self.Instruments.getProberInstrument() != None:
                self.__NumOfXDev.setEnabled(True)
                self.__NumOfYDev.setEnabled(True)
                self.__XPitch.setEnabled(True)
                self.__YPitch.setEnabled(True)
                self.Configuration.setValue("MultipleDev",True)

    def CheckBoxMultDies(self):
        if self.__MultipleDies.getVariable():
            self.__DieFileButton.setEnabled(True)
            self.__DieMaps.setEnabled(True)
            self.__DieMapUpdate.setEnabled(True)
            self.Configuration.setMultipleDies(True)
            self.WaferMap.update(Blank=False)
            self.MapUpdateDieMap()
        else:
            self.__DieFileButton.setEnabled(False)
            self.__DieMaps.setEnabled(False)
            self.__DieMapUpdate.setEnabled(False)
            self.Configuration.setMultipleDies(False)
            self.WaferMap.update(Blank=True)

    def showMatrix(self):
        self.__UseMatrix.show()
        self.TxUseMatrix.show()

    def hideMatrix(self):
        self.__UseMatrix.hide()
        self.TxUseMatrix.hide()
        
    def showProber(self):
        self.__MulipleDevices.show()
        self.__NumOfXDev.show()
        self.__NumOfYDev.show()
        self.__XPitch.show()
        self.__YPitch.show()
        self.__MultipleDies.show()
        self.__DieFileButton.show()
        self.__DieMaps.show()
        self.__DieMapUpdate.show()
        
        self.TxDeviceStart.show()
        self.TxMultDies.show()
        self.TxDevPitch.show()
        self.TxDieMap.show()
        self.TxMultDev.show()
        self.TxNumOfDev.show()
        self.TxDieFile.show()

    def hideProber(self):
        self.__MulipleDevices.hide()
        self.__NumOfXDev.hide()
        self.__NumOfYDev.hide()
        self.__XPitch.hide()
        self.__YPitch.hide()
        self.__MultipleDies.hide()
        self.__DieFileButton.hide()
        self.__DieMaps.hide()
        self.__DieMapUpdate.hide()
        
        self.TxDevPitch.hide()
        self.TxDieMap.hide()
        self.TxMultDev.hide()
        self.TxMultDies.hide()
        self.TxNumOfDev.hide()
        self.TxDieFile.hide()
        self.TxMultDies.hide()


    def disableMatrix(self):
        self.__UseMatrix.setEnabled(False)
        self.__UseMatrix.setCheckState(False)

    def enableMatrix(self):
        self.__UseMatrix.setEnabled(True)
        state = self.Configuration.getUseMatrix()
        self.__UseMatrix.setCheckState(state)

    def enableProber(self):
        self.__MulipleDevices.setEnabled(True)
        if self.__MulipleDevices.getVariable() == True:
            self.__NumOfXDev.setEnabled(True)
            self.__NumOfYDev.setEnabled(True)
            self.__XPitch.setEnabled(True)
            self.__YPitch.setEnabled(True)
        self.__MultipleDies.setEnabled(True)
        if self.__MultipleDies.getVariable() == True:
            self.__DieFileButton.setEnabled(True)
            self.__DieMaps.setEnabled(True)
            self.__DieMapUpdate.setEnabled(True)
            self.Configuration.setMultipleDies(True)

    def disableProber(self):
        self.__NumOfXDev.setEnabled(False)
        self.__NumOfYDev.setEnabled(False)
        self.__XPitch.setEnabled(False)
        self.__YPitch.setEnabled(False)
        self.__MulipleDevices.setEnabled(False)
        self.Configuration.setMultipleDev(False)
        self.__MultipleDies.setEnabled(False)
        self.__DieFileButton.setEnabled(False)
        self.__DieMaps.setEnabled(False)
        self.__DieMapUpdate.setEnabled(False)
        self.Configuration.setMultipleDies(False)
    
    def CallDieMaps(self, Map):
        self.Configuration.setDieFile("")
        self.__DieFileButton.setVariable("Browse")
        if not self.MainGI.running:
            self.Configuration.UpdateDies()
            self.WaferMap.update(locations=self.Configuration.getDies(), Folder=self.Configuration.getMainFolder(), DieSizeX=self.Configuration.getDieSizeX(), DieSizeY=self.Configuration.getDieSizeY(), 
                                        WaferSize=self.Configuration.getWaferSize(), CenterLocation=self.Configuration.getCenterLocation(), NumOfDies=self.Configuration.getNumOfDies(), 
                                        NumOfDevices=self.Configuration.getNumOfDevices(), NumOfXDevices=self.Configuration.getNumXDevices(), NumOfYDevices=self.Configuration.getNumYDevices(), WaferRotation=self.Configuration.getWaferRotation())
        return True
    

class PlotWidget(pg.PlotWidget):

    xticks = []
    yticks = []

    xlow = 0
    ylow = 0

    xhigh = 0
    yhigh = 0

    xcenter = 0
    ycenter = 0

    Type = 'WafProgress'
    initValue = None
    title = None

    data = np.array([[]])
    
    ticks = 15

    def __init__(self, parent=None, config=None, backgroundColor='default', ringColor='r', name=None, labels=None, title=0, initValue=0, ValueName="", **kwargs):

        super().__init__(parent, background=backgroundColor, *kwargs)

        self.Configuration = config
        self.valueName = ValueName
        self.dieSizeX = float(self.Configuration.getDieSizeX())
        self.dieSizeY = float(self.Configuration.getDieSizeY())
        self.waferSize = float(self.Configuration.getWaferSize())
        self.numOfDev = float(self.Configuration.getNumOfDevices())
        self.numOfXDev = float(self.Configuration.getNumXDevices())
        self.numOfYDev = float(self.Configuration.getNumYDevices())
        self.mainFolder = self.Configuration.getMainFolder()
        self.centerLocX = float(self.Configuration.getCenterLocation()[0])/100
        self.centerLocY = float(self.Configuration.getCenterLocation()[1])/100
        self.numOfDies = float(self.Configuration.getNumOfDies())
        self.waferRotation = int(self.Configuration.getWaferRotation())
        
        self.initValue = initValue
        self.ringColor = ringColor
        self.currentLocation = None
        self.storedData = None

        self.start()
        self.plotItem.addItem(self.img)

    def getTicks(self, axis):
        radius = float(self.waferSize)/2
        if axis == 'X':
            self.xhigh = int(ma.floor((radius-self.dieSizeX/2-self.centerLocX)/self.dieSizeX))
            self.xlow = -int(ma.floor((radius-self.dieSizeX/2+self.centerLocX)/self.dieSizeX))
            Rng = list(range(self.xlow,self.xhigh+1,1))
        elif axis == 'Y':
            self.yhigh = int(ma.floor((radius-self.dieSizeY/2-self.centerLocY)/self.dieSizeY))
            self.ylow = -int(ma.floor((radius-self.dieSizeY/2+self.centerLocY)/self.dieSizeY))
            Rng = list(range(self.ylow,self.yhigh+1,1))
        return Rng
    
    def start(self):
            
        c = ["darkred","red", "tomato","orange","green","darkgreen"]
        v = [0,0.2,.4,0.6,0.8,1.]

        self.colorMap = pg.ColorMap(v, c)

        self.l = list(zip(v,c))

        self.vmin=0
        self.vmax=self.numOfDev
        #self.argb = pg.makeARGB(self.data, levels=[self.vmin, self.vmax], lut=self.colorMap.getLookupTable())

        self.xticks = self.getTicks('X')
        self.yticks = self.getTicks('Y')
        self.xlow = self.xticks[0]
        self.ylow = self.yticks[0]
        
        self.data = np.empty((len(self.xticks), len(self.yticks)), np.longdouble)
        self.data[:] = np.nan

        if not self.initValue == None:
            for x in range(abs(self.xlow)*2+1):
                for y in range(abs(self.ylow)*2+1):
                    #if std.isDieInWafer(self.waferSize, x+self.xlow, y+self.ylow, 12, 15):
                    self.data[x][y] = self.initValue

        self.img = pg.ImageItem()
        self.img.setColorMap(self.colorMap)
        self.img.setImage(self.data, levels=(0,1))
        tr = QtGui.QTransform()
        self.img.setTransform(tr)
        self.axisPrep()

    def calcProp(self):
        self.vmin=0
        self.vmax=self.numOfDies
        self.xticks = self.getTicks('X')
        self.yticks = self.getTicks('Y')
        self.xlow = self.xticks[0]
        self.ylow = self.yticks[0]
    
    def update(self, **kwargs):
        
        calcUpdate = False
        for key, value in kwargs.items():

            if key == "Folder":
                self.Folder = value
            if key == "DieSizeX":
                self.dieSizeX = value
                calcUpdate = True
            if key == "DieSizeY":
                self.dieSizeY = value
                calcUpdate = True
            if key == "WaferSize":
                self.waferSize = value
                calcUpdate = True
            if key == "CenterLocation":
                self.centerLocX = value[0]/100
                self.centerLocY = value[1]/100
                calcUpdate = True
            if key == "NumOfDies":
                self.numOfDies = value
                calcUpdate = True
            if key == "NumOfDevices":
                self.numOfDev = value
                calcUpdate = True
            if key == "WaferRotation":
                self.waferRotation = value
                calcUpdate = True
            if key == "Blank":
                if value:
                    self.storedData = cp.deepcopy(self.data)
                    calcUpdate = True
                else:
                    if not isinstance(self.storedData, type(None)):
                        self.data = cp.deepcopy(self.storedData)
                        self.storedData = None
            if key =="ChuckPosition":
                self.currentLocation = value
                self.updateChuckLocation()
        if calcUpdate:
            self.calcProp()
            self.data = np.empty((len(self.xticks), len(self.yticks)), np.longdouble)
            self.data[:] = np.nan

            if "locations" in kwargs:
                if "value" in kwargs:
                    vals = kwargs['value']
                else:
                    vals = [0]*len(kwargs['locations'])
                for loc, val in zip(kwargs["locations"], vals):
                    self.writeToData(loc[0], loc[1], value=val)


            ratio = self.dieSizeX/self.dieSizeY
            if ratio > 1:
                scX = 1/ratio
                scY = 1
            else:
                scY = 1/ratio
                scX = 1


            self.img.setImage(self.data, levels=(0,1))
            tr = QtGui.QTransform()
            self.img.setTransform(tr)
            #self.plotItem.addItem(self.img)
            self.axisPrep()

        
    def writeToData(self, xDie, yDie, add=0, value=None):
        if value==None:
            newData = self.data[xDie-self.xlow,-yDie-self.ylow] + float(add)
            self.data[xDie-self.xlow,-yDie-self.ylow] = float(newData)
        else:
            self.data[xDie-self.xlow,-yDie-self.ylow] = float(value)
            
    def axisPrep(self):

        if self.valueName == "":
            self.valueName = "Measured Dies"

        # We want to show all ticks...
        xlen = len(self.xticks)
        ylen = len(self.yticks)

        xSep = int(ma.ceil(xlen/self.ticks))
        ySep = int(ma.ceil(ylen/self.ticks))

        PrXticks = []
        PrYticks = []

        for x in self.xticks:
            if x % xSep:
                PrXticks.append('')
            else:
                PrXticks.append(x)
        
        for y in self.yticks:
            if y % ySep:
                PrYticks.append('')
            else:
                PrYticks.append(-y)

        labelStyle = {'font-size': '11pt', 'font-weight': 'bold', 'color':self.ringColor}
        self.plotItem.setLabel('left', "Y Die Number", **labelStyle) 
        self.plotItem.setLabel('bottom', "X Die Number", **labelStyle)

        self.plotItem.showAxis("top", False)
        self.plotItem.showAxis("left")
        self.plotItem.showAxis("bottom")
        self.plotItem.showAxis("right", False)

        axisStyle = {'color':self.ringColor}
        leftAxis = self.plotItem.getAxis("left")
        leftTicks = self.getTicks("Y")
        ticksY = [[]]
        for n,t in enumerate(PrYticks):
            ticksY[0].append((n+0.5,"%s" %(t)))
            if t == 0:
                self.centDieY = n+0.5
        leftAxis.setTicks(ticksY)
        leftAxis.setTextPen(self.ringColor)

        botAxis = self.plotItem.getAxis("bottom")
        botTicks = self.getTicks("X")
        
        ticksX = [[]]
        for n,t in enumerate(PrXticks):
            ticksX[0].append((n+0.5,"%s" %(t)))
            if t == 0:
                self.centDieX = n+0.5
        botAxis.setTicks(ticksX)
        botAxis.setTextPen(self.ringColor)

        self.xOrg = self.centDieX-self.waferSize/self.dieSizeX/2
        self.yOrg = self.centDieY-self.waferSize/self.dieSizeY/2

        try:
            self.plotItem.removeItem(self.roi_circle)
        except AttributeError:
            pass
        
        self.roi_circle = pg.CircleROI([self.xOrg-self.centerLocX, self.yOrg-self.centerLocY], [self.waferSize/self.dieSizeX, self.waferSize/self.dieSizeY], movable=False, rotatable=False,  resizable=False, pen=pg.mkPen(self.ringColor,width=3))
        self.plotItem.addItem(self.roi_circle)
        self.roi_circle.removeHandle(0)
        self.updateChuckLocation()
    
    def updateChuckLocation(self):
        if isinstance(self.currentLocation, list):
            if len(self.currentLocation) > 1:

                try:
                    self.plotItem.removeItem(self.roi_LocDot)
                except AttributeError:
                    pass

                x = self.currentLocation[0]/self.dieSizeX/1000 + self.waferSize/self.dieSizeX/2
                y = self.currentLocation[1]/self.dieSizeY/1000 + self.waferSize/self.dieSizeY/2
                d = 0.5
                w = d
                h = d *self.dieSizeX / self.dieSizeY
                color = QtGui.QColor(0,27,173,60)
                borCol = QtGui.QColor(0,39,250,120)
                self.roi_LocDot = LocationDot(x,y,w,h,color=color, borderColor=borCol)
                self.plotItem.addItem(self.roi_LocDot)

        self.updateWaferRotation(self.waferRotation)


    def updateBackground(self, background): 
        self.setBackground(background)

    def updateWaferRotation(self, rot):

        nSiz = [self.waferSize/self.dieSizeX/15,self.waferSize/self.dieSizeY/15]
        if rot == 180:
            nLoc = [self.centDieX-self.centerLocX,self.yOrg-self.centerLocY]
            nLoc[0] = nLoc[0] - nSiz[0]/2
            nLoc[1] = nLoc[1] - nSiz[1]/2
            stAng=180*16
        elif rot == 90:
            nLoc = [self.xOrg + self.waferSize/self.dieSizeX-self.centerLocX, self.centDieY-self.centerLocY]
            nLoc[0] = nLoc[0] - nSiz[0]/2
            nLoc[1] = nLoc[1] - nSiz[1]/2
            stAng=90*16
        elif rot == 270:
            nLoc = [self.xOrg-self.centerLocX, self.centDieY-self.centerLocY]
            nLoc[0] = nLoc[0] - nSiz[0]/2
            nLoc[1] = nLoc[1] - nSiz[1]/2
            stAng=270*16
        else: 
            nLoc = [self.centDieX-self.centerLocX, self.yOrg+self.waferSize/self.dieSizeY-self.centerLocY]
            nLoc[0] = nLoc[0] - nSiz[0]/2  
            nLoc[1] = nLoc[1] - nSiz[1]/2
            stAng=0*16
        
        try:
            self.plotItem.removeItem(self.roi_Notch)
        except AttributeError:
            pass
        
        self.roi_Notch = NotchItem(*nLoc, *nSiz, startAngle=stAng,spanAngle=2880, color=self.ringColor)
        self.plotItem.addItem(self.roi_Notch)

    def changeRingColor(self, ringColor):
        if ringColor != None:
            self.ringColor = ringColor
            self.axisPrep()

    def setBlank(self, blank):
        self.update(Blank=blank)


        
class LocationDot(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, x, y, w,h, parent=None, **kwargs):
        super().__init__(x,y,w,h, parent)

        for key, value in kwargs.items():
            if key == "color":
                if value != None:
                    self.color = value
                else:
                    self.color = 'b'
            else:
                self.color = 'b'
            if key == "borderColor":
                if value != None:
                    self.borderColor = value
                else:
                    self.borderColor = 'g'
            else:
                self.borderColor = 'g'

        #super().setStyleSheet("background: transparent; border-width: 0px")

        self.setPen(pg.mkPen(color=self.borderColor, width=3))
        self.setBrush(pg.mkBrush(self.color))

        
class NotchItem(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, x, y, w, h, parent=None, **kwargs):
        super().__init__(x,y,w,h, parent)

        for key, value in kwargs.items():
            if key == "startAngle":
                self.setStartAngle(value)
            if key == "spanAngle":
                self.setSpanAngle(value)
            if key == "color":
                if value != None:
                    self.color = value
                else:
                    self.color = 'r'
            else:
                self.color = 'r'

        self.setPen(pg.mkPen((0, 0, 0, 100)))
        self.setBrush(pg.mkBrush(self.color))
