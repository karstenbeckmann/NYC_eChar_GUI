"""
This is the standard Frame that introduces the distribution of necessary variables and subclasses for the all Frames
Written by: Karsten Beckmann
Date: 01/01/2019
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
from matplotlib.figure import Figure
from PyQt5 import QtWidgets, QtCore, QtGui
import Qt_stdObjects as stdObj


class MainButtons(QtWidgets.QWidget):

    def __init__(self, MainGI, parent, *args, **kwargs):

        super().__init__(parent)
        self.MainGI = MainGI
        self.width = self.MainGI.getWindowWidth()
        font = self.font()
        font.setBold(True)
        self.setFont(font)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.setFixedWidth(self.MainGI.getWindowWidth())
        
        self.updateGeometry()
        self.Configuration = self.MainGI.Configuration
        self.Complete = 0
        self.Instruments = self.MainGI.Instruments
        AvailMeasTypes = ["Full Wafer"]

        self.__MeasurementType = stdObj.ComboBox(self, self.MainGI, "CurrentMeasurementType", list(AvailMeasTypes), command=self.callMeasTypes, width=15)
        self.__MeasurementType.setMinimumWidth(int(0.2*self.width))
        self.layout.addWidget(self.__MeasurementType)
        
        ChuckTemp = "--"
        if self.Instruments.getProberInstrument() != None:
            try:
                ChuckTemp = self.Instruments.getProberInstrument().ReadChuckThermoValue()[0]
            except:
                self.MainGI.WriteError("GI: Main Buttons: Chuck Temperature could no be read.")

        self.__StartButton = stdObj.PushButton("Start", self, minimumWidth=1, command=self.StartButton)
        self.layout.addWidget(self.__StartButton)
        
        self.__PauseButton = stdObj.PushButton("Pause", self, minimumWidth=1, command=self.PauseButton)
        self.layout.addWidget(self.__PauseButton)
        
        self.__ContinueButton = stdObj.PushButton("Continue", self, minimumWidth=1, command=self.ContinueButton)
        self.layout.addWidget(self.__ContinueButton)
        
        self.__StopButton = stdObj.PushButton("Stop", self, minimumWidth=1, command=self.StopButton)
        self.layout.addWidget(self.__StopButton)
        
        self.ProgressBar = QtWidgets.QProgressBar(self)
        self.ProgressBar.setFixedWidth(int(self.width*0.15))
        self.ProgressBar.setValue(0)
        self.ProgressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.ProgressBar)
        self.layout.addSpacing(1)

       
        self.TxTempDisp = stdObj.Label("%s ℃ " %(ChuckTemp), self, alignment=QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)

        self.layout.addWidget(self.TxTempDisp)

        self.setLayout(self.layout)
        #self.adjustSize()
        #self.setFixedHeight(self.ProgressBar.height())

        self.layout.setContentsMargins(2,2,2,2)
        self.layout.setSpacing(2)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
       
    def StartButtonStyle(self, style):
        pal = self.MainGI.getColorPalette(style, 'button')
        self.__StartButton.setAutoFillBackground(True)
        self.__StartButton.setPalette(pal)

    def update(self):
        if self.MainGI.isRunning():
            self.__MeasurementType.setEnabled(False)
            self.__StartButton.setEnabled(False)
        else:
            self.__MeasurementType.setEnabled(True)
            self.__StartButton.setEnabled(True)

            self.TxTempDisp.setText("%s ℃ " %(self.Instruments.getChuckTemperature()))
        

    def reset(self):
        self.Complete = 0
        self.ProgressBar.setValue(0)

    def updateComplete(self, add):
        self.Complete = (self.Complete + add)
        PercCompl = self.Complete*100
        if self.Configuration.getValue("MultipleDev"):
            PercCompl = PercCompl/self.Configuration.getNumOfDevices()
        if self.Configuration.getMultipleDies():
            PercCompl = PercCompl/self.Configuration.getNumOfDies()
        self.ProgressBar.setValue(PercCompl)

    def callMeasTypes(self, value):
        None

    def StartButton(self):
        if not self.MainGI.isRunning():
            self.MainGI.running = True
            self.reset()

            msgBox = QtWidgets.QMessageBox()
            msgBox.setWindowIcon(self.MainGI.icon)
            msgBox.setStandardButtons(QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
            msgBox.setWindowTitle("Start Measurement")
            msgBox.setText("Are the probes Positioned on the First Device?")
            ret = int(msgBox.exec())
        
            if ret == 16384: 
                self.MainGI.startExecution(self.__MeasurementType.getVariable())
                self.__ContinueButton.setDisabled(True)
            else:
                self.MainGI.running = False

    def StopButton(self):
        if self.MainGI.isRunning():
            self.MainGI.Close.put(True)
            self.MainGI.eChar.Stop.put(True)
            pal = self.MainGI.getColorPalette('red', 'button')
            self.__StopButton.setAutoFillBackground(True)
            self.__StopButton.setPalette(pal)
    
    def PauseButton(self):
        if self.MainGI.isRunning():
            self.__ContinueButton.setEnabled(True)
            self.MainGI.Pause.put(True)
            pal = self.MainGI.getColorPalette('orange', 'button')
            self.__PauseButton.setAutoFillBackground(True)
            self.__PauseButton.setPalette(pal)
        
    def ContinueButton(self):
        if self.MainGI.isRunning():
            self.MainGI.Pause.put(False)
            self.MainGI.eChar.Stop.put(False)
            pal = self.MainGI.getColorPalette('','')
            self.__PauseButton.setAutoFillBackground(True)
            self.__PauseButton.setPalette(pal)
            self.__ContinueButton.setDisabled(True)

    def Finished(self):
        pal = self.MainGI.getColorPalette('','')
        tm.sleep(1)
        
        self.__PauseButton.setAutoFillBackground(True)
        self.__StopButton.setAutoFillBackground(True)
        self.__StartButton.setAutoFillBackground(True)
        self.__StartButton.setPalette(pal)
        self.__StopButton.setPalette(pal)
        self.__PauseButton.setPalette(pal)


class sideButtons(QtWidgets.QWidget):


    def __init__(self, MainGI, parent, *args, **kwargs):

        super().__init__(parent)
        self.MainGI = MainGI
        self.width = int(self.MainGI.getWindowWidth()*0.04)
        self.Configuration = MainGI.Configuration
        font = self.font()
        font.setBold(True)
        self.setFont(font)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(1,1,1,1)
        self.layout.setSpacing(1)
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.setFixedWidth(self.width)
        
        self.updateGeometry()
        self.Configuration = self.MainGI.Configuration
        self.Complete = 0
        self.Instruments = self.MainGI.Instruments

        self.__ResultButton = stdObj.PushButton("R\ne\ns\nu\nl\nt\ns", self, minimumWidth=1, command=self.ResultButton)
        self.layout.addWidget(self.__ResultButton)
        
        self.__StatButton = stdObj.PushButton("S\nt\na\nt\ni\ns\nt\ni\nc\ns", self, minimumWidth=1, command=self.StatisticsButton)
        self.layout.addWidget(self.__StatButton)
        
        self.__ProbeButton = stdObj.PushButton("P\nr\no\nb\ne\nr", self, minimumWidth=1, command=self.ProbeStationButton)
        self.layout.addWidget(self.__ProbeButton)
        self.__ProbeButton.hide()
        
    def ResultButton(self):
        if self.MainGI.ResultWindow.isVisible():
            self.MainGI.ResultWindow.hide()
        else:
            self.MainGI.ResultWindow.show()

    def StatisticsButton(self):
        None

    def ProbeStationButton(self):
        if self.MainGI.ProberWindow.isVisible():
            self.MainGI.ProberWindow.hide()
        else:
            self.MainGI.ProberWindow.show()
            self.MainGI.setProberWindowPosition()

    def HideProbeButton(self):
        self.__ProbeButton.hide()

    def ShowProbeButton(self):
        self.__ProbeButton.show()