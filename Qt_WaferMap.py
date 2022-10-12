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
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from PyQt5 import QtWidgets, QtCore, QtGui
import Qt_stdObjects as stdObj

import matplotlib._pylab_helpers as plotHelper

class WaferMap(stdObj.stdFrameGrid):

    def __init__(self, parent, MainGI, columns, rows, width, height, **kwargs):


        self.dieFolder = None
        if 'dieFolder' in kwargs.keys():
            self.dieFolder = kwargs['dieFolder']
            del kwargs['dieFolder']
        else:
            try:
                self.dieFolder = MainGI.subFolder
            except ValueError:
                None

        super().__init__(parent, MainGI, columns, rows, width, height, **kwargs)

        self.Configuration = self.MainGI.getConfiguration()
        self.Entries = []
        self.WaferMap = None
        self.__Canvas_1 = None
        self.CreateCanvas()

        
        row = 1
        col = 6
        self.__SubFolder = stdObj.Entry(self, MainGI, "Subfolder", maxLength=10)
        self.addWidget(self.__SubFolder, row=row, column=col+2, columnspan=2)
        self.TxSubFolder = stdObj.Label("Sub Folder:", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxSubFolder, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        row = row + 1
        self.__WaferID = stdObj.Entry(self, MainGI, "WaferID", maxLength=15)
        self.addWidget(self.__WaferID, row=row, column=col+2, columnspan=2)
        self.TxWaferID=stdObj.Label("Wafer ID:", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxWaferID, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        row = row +1
        self.__DeviceName = stdObj.Entry(self, MainGI, "DeviceName", maxLength=15)
        self.addWidget(self.__DeviceName, row=row, column=col+2, columnspan=2)
        self.TxDeviceName= stdObj.Label("Device Name:", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxDeviceName, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        row = row + 1
        self.__WaferSize = stdObj.Entry(self, MainGI, "WaferSize", validate='all', validateNumbers="[0-9]+")
        self.addWidget(self.__WaferSize, row=row, column=col+2, columnspan=2)
        self.TxWaferSize=stdObj.Label("Wafer Size(mm):", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxWaferSize, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        row = row + 1
        self.TxY=stdObj.Label( "Y", self)
        self.TxY.setAlignment(QtCore.Qt.AlignCenter)
        self.addWidget(self.TxY, row=row, column=col+3, columnspan=1)
        self.TxY=stdObj.Label("X", self)
        self.TxY.setAlignment(QtCore.Qt.AlignCenter)
        self.addWidget(self.TxY, row=row, column=col+2, columnspan=1)

        row = row + 1
        self.DevStartX = stdObj.Entry(self, MainGI, "DeviceStartX", validate='all', validateNumbers="[0-9]+")
        self.addWidget(self.DevStartX, row=row, column=col+2, columnspan=1)
        self.DevStartY = stdObj.Entry(self, MainGI, "DeviceStartY", validate='all', validateNumbers="[0-9]+")
        self.addWidget(self.DevStartY, row=row, column=col+3, columnspan=1)
        self.TxDeviceStart=stdObj.Label("Device Start", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxDeviceStart, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        row = row + 1
        self.__DevSizeX = stdObj.Entry(self, MainGI, "DieSizeX", validate='all', validateNumbers="([0-9]+(\.[0-9]+)?|\.[0-9]+)$")
        self.addWidget(self.__DevSizeX, row=row, column=col+2, columnspan=1)
        self.__DevSizeY = stdObj.Entry(self, MainGI, "DieSizeY", validate='all', validateNumbers="([0-9]+(\.[0-9]+)?|\.[0-9]+)$")
        self.addWidget(self.__DevSizeY, row=row, column=col+3, columnspan=1)
        self.TxDieSize=stdObj.Label("Die Size (mm):", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxDieSize, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        row = row + 1
        
        self.__CenLocX = stdObj.Entry(self, MainGI, "CenterLocationX", validate='all', validateNumbers="^[-+]?([0-9]+(\.[0-9]+)?|\.[0-9]+)$")
        self.addWidget(self.__CenLocX, row=row, column=col+2, columnspan=1)
        self.__CenLocY = stdObj.Entry(self, MainGI, "CenterLocationY", validate='all', validateNumbers="^[-+]?([0-9]+(\.[0-9]+)?|\.[0-9]+)$")
        self.addWidget(self.__CenLocY, row=row, column=col+3, columnspan=1)
        self.TxCenterLocation=stdObj.Label("Cen. Location (%):", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxCenterLocation, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        row = row + 1
        
        self.__MulipleDevices = stdObj.Checkbutton(self, MainGI, "MultipleDev", command=self.CheckBoxMultDev)
        self.addWidget(self.__MulipleDevices, row=row, column=col+2, columnspan=1)
        self.TxMultDev = stdObj.Label("Multiple Devices:", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxMultDev, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        row = row + 1

        self.__NumOfXDev = stdObj.Entry(self, MainGI, "NumXdevices", validate='all', validateNumbers="[0-9]+")
        self.addWidget(self.__NumOfXDev, row=row, column=col+2, columnspan=1)
        self.__NumOfYDev = stdObj.Entry(self, MainGI, "NumYdevices", validate='all', validateNumbers="[0-9]+")
        self.addWidget(self.__NumOfYDev, row=row, column=col+3, columnspan=1)
        self.TxNumOfDev=stdObj.Label("Num. of Devices:", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxNumOfDev, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        row = row + 1

        self.__XPitch = stdObj.Entry(self, MainGI, "XPitch", validate='all', validateNumbers="^[-+]?([0-9]+(\.[0-9]+)?|\.[0-9]+)$")
        self.addWidget(self.__XPitch, row=row, column=col+2, columnspan=1)
        self.__YPitch = stdObj.Entry(self, MainGI, "YPitch", validate='all', validateNumbers="^[-+]?([0-9]+(\.[0-9]+)?|\.[0-9]+)$")
        self.addWidget(self.__YPitch, row=row, column=col+3, columnspan=1)
        self.TxDevPitch=stdObj.Label("Dev. Pitch (um):", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxDevPitch, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        
        self.TxLog=stdObj.Label("Log and Information:", self)
        self.addWidget(self.TxLog, row=row, column=1, columnspan=2, alignment=QtCore.Qt.AlignLeft)
        self.TxLogSave=stdObj.Label("save", self)
        self.addWidget(self.TxLogSave, row=row, column=3, columnspan=1, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.__LogSaveCheckbox = stdObj.Checkbutton(self, self.MainGI, "InfoLogSave")
        self.addWidget(self.__LogSaveCheckbox, row=row, column=4, columnspan=1, alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.__LogClearButton = stdObj.PushButton("Clear", self, sizePolicy=[QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding], command=self.clearLogFrame)
        self.addWidget(self.__LogClearButton, row=row, column=5, columnspan=1, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.LogFrame = stdObj.InfoLog(self, "InfoLog", MainGI=MainGI, SaveObj="InfoLogSave", maxEntries=200, sizePolicy=[QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding])
        self.addWidget(self.LogFrame, row=row+1, column=1, columnspan=5, rowspan=5)

        row = row + 1
        self.__CurrentDie = stdObj.Checkbutton(self, MainGI, "CurrentDie", command=self.CheckBoxCurDie, alignment=QtCore.Qt.AlignLeft)
        self.addWidget(self.__CurrentDie, row=row, column=col+2, columnspan=1, alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.TxCurDie=stdObj.Label("Current Die:", self)
        self.addWidget(self.TxCurDie, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        row = row + 1


        self.__DieFileButton = stdObj.fileButton(self, MainGI, "DieFile", sizePolicy=[QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding], fileFormat = "CSV file (*.csv)", subFolder=self.dieFolder, command=self.DieFileButton)

        DieMaps = self.Configuration.getAllDieMaps()
        self.__DieMaps = stdObj.ComboBox(self, MainGI, "DieMap", list(DieMaps), Type=int, sizePolicy=[QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding], command=self.CallDieMaps)
        self.addWidget(self.__DieMaps, row=row, column=col+2, columnspan=1)
        self.__DieMapUpdate = stdObj.PushButton("Update", self, sizePolicy=[QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding], command=self.MapUpdateDieMap)
        self.addWidget(self.__DieMapUpdate, row=row, column=col+3, columnspan=1)

        self.TxDieMap=stdObj.Label("Die Map:", self)
        self.TxDieMap.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxDieMap, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        row = row + 1

        self.addWidget(self.__DieFileButton, row=row, column=col+2, columnspan=2)
        self.TxDieFile=stdObj.Label("Die File:", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxDieFile, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        row = row + 1

        self.__SpecCode = stdObj.Entry(self, MainGI, "SpecCode", maxLength=20)
        self.addWidget(self.__SpecCode, row=row, column=col+2, columnspan=2)
        self.TxSpecCode=stdObj.Label("Spec Code:", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxSpecCode, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        row = row + 1
        
        self.__UseMatrix = stdObj.Checkbutton(self, MainGI, "UseMatrix", command=self.CheckBoxMatrix, alignment=QtCore.Qt.AlignLeft)
        self.addWidget(self.__UseMatrix, row=row, column=col+2, columnspan=1, alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.TxUseMatrix=stdObj.Label("Use Matrix:", self, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.addWidget(self.TxUseMatrix, row=row, column=col, columnspan=2, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        row = row + 1

        self.CheckBoxMultDev()
        self.CheckBoxCurDie()
        self.CheckBoxMatrix()
        self.updateCanvas()

        self.setLayout(self.layout)

    def DieFileButton(self):
        self.Configuration.UpdateDies()
        self.MapUpdateDieMap()
        
    def CheckBoxMatrix(self):
        self.Configuration.setUseMatrix(self.__UseMatrix.getVariable())

    def MapUpdateDieMap(self):
        if not self.MainGI.running:
            self.CreateCanvas()
        else:
            self.MainGI.WriteError("Measurement is currently running.")

    def update(self):

        if self.Instruments.getMatrixInstrument() == None:
            self.disableMatrix()
        else:
            self.enableMatrix()
        if self.Instruments.getProberInstrument() == None:
            self.disableProber()
        else:
            self.enableProber()
   
    def clearLogFrame(self):
        self.Configuration.clearLogList()
        self.MainGI.clearLogFrame()

    def CreateCanvas(self, row=1, column=1, rowspan=10, columnspan=5):

        height = int(rowspan*self.RowHeight)
        width = int(columnspan*self.ColumnWidth)
        
        self.WaferMap = PR.WaferMap(self.Configuration.getMainFolder(), self.Configuration.getDieSizeX(), self.Configuration.getDieSizeY(), 
                                        self.Configuration.getWaferSize(), self.Configuration.getCenterLocation(), self.Configuration.getNumOfDies(), 
                                        self.Configuration.getNumOfDevices(), width, height)

        dies = self.Configuration.getDies()
        self.WaferMap.update(locations=dies, value=[0]*len(dies))
        
        figure = self.WaferMap.getFigure()
        self.__Canvas_1 = FigureCanvasQTAgg(figure)
        self.__Canvas_1.setParent(self)
        self.__Canvas_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.__Canvas_1.updateGeometry()
        self.__Canvas_1.draw() 

        self.layout.addWidget(self.__Canvas_1, row, column, rowspan, columnspan)


    def updateCanvas(self):

        dies = self.Configuration.getDies()
        self.WaferMap.update(locations=dies, Folder=self.Configuration.getMainFolder(), DieSizeX=self.Configuration.getDieSizeX(), DieSizeY=self.Configuration.getDieSizeY(), 
                                        WaferSize=self.Configuration.getWaferSize(), CenterLocation=self.Configuration.getCenterLocation(), NumOfDies=self.Configuration.getNumOfDies(), 
                                        NumOfDevices=self.Configuration.getNumOfDevices())
        self.__Canvas_1.draw()

    def DrawCanvas(self):
        self.__Canvas_1.draw()

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

    def CheckBoxCurDie(self):
        if self.__CurrentDie.getVariable():
            self.__DieFileButton.setEnabled(False)
            self.__DieMaps.setEnabled(False)
            self.__DieMapUpdate.setEnabled(False)
            self.Configuration.setCurrentDie(True)
        else:
            self.__DieFileButton.setEnabled(True)
            self.__DieMaps.setEnabled(True)
            self.__DieMapUpdate.setEnabled(True)
            self.Configuration.setCurrentDie(False)

    def disableMatrix(self):
        self.__UseMatrix.setEnabled(False)

    def enableMatrix(self):
        self.__UseMatrix.setEnabled(True)

    def enableProber(self):
        self.__MulipleDevices.setEnabled(True)
        if self.__MulipleDevices.getVariable() == True:
            self.__NumOfXDev.setEnabled(True)
            self.__NumOfYDev.setEnabled(True)
            self.__XPitch.setEnabled(True)
            self.__YPitch.setEnabled(True)
        self.__CurrentDie.setEnabled(True)
        if self.__CurrentDie.getVariable() == True:
            self.__DieFileButton.setEnabled(True)
            self.__DieMaps.setEnabled(True)
            self.__DieMapUpdate.setEnabled(True)
            self.Configuration.setCurrentDie(True)

    def disableProber(self):

        self.__NumOfXDev.setEnabled(False)
        self.__NumOfYDev.setEnabled(False)
        self.__XPitch.setEnabled(False)
        self.__YPitch.setEnabled(False)
        self.__MulipleDevices.setEnabled(False)
        self.Configuration.setMultipleDev(False)
        self.__CurrentDie.setEnabled(False)
        self.__DieFileButton.setEnabled(False)
        self.__DieMaps.setEnabled(False)
        self.__DieMapUpdate.setEnabled(False)
        self.Configuration.setCurrentDie(False)
    
    def CallDieMaps(self, Map):
        
        self.Configuration.setDieFile("")
        self.__DieFileButton.setVariable("Browse")
        self.Configuration.UpdateDies()
        if not self.MainGI.running:
            self.updateCanvas()
        return True
    