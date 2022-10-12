"""
This is the main program that governs the Electrical wafer level Characterization integrated devices
Written by: Karsten Beckmann
Date: 1/1/2019
email: kbeckmann@sunypoly.edu
"""


import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from ctypes import *
import win32api
import win32con
import time
import threading as th
import ECharacterization as EC
import ProbeStations as PS
import Keithley as KL
import datetime as dt
import Configuration as cf
import pyvisa as vs
import DataHandling as dh
import time as tm
import copy as cp
import numpy as np
import StdDefinitions as std
import queue as qu
import ToolHandle as tool
import Qt_MainButtons as Qt_MB
import screeninfo as scrInfo
import glob, imp
import os as os

import ResultHandling as RH

import Qt_WaferMap as Qt_WM
import Qt_stdObjects as stdObj
import Qt_MeasTab as Qt_MT
import Qt_Config as Qt_CF
import Qt_ResultWindow as Qt_RW
import Qt_Tables as Qt_TB
import Qt_B1500A as Qt_B1500A
import Qt_E5274A as Qt_E5274A

class MainUI(QtWidgets.QMainWindow):

    Close = qu.Queue()
    Pause = qu.Queue()
    __ErrorQu = qu.Queue()
    __logQu = qu.Queue()
    __Finished = qu.Queue()
    __MeasLogQu = qu.Queue()
    __Canvas_1 = None
    __Canvas_1_data = qu.Queue()
    __CanvasPhoto = None
    __window = None
    __TKthread = None
    __InterfaceThread = None
    __close = False
    __NumOfDevices = 0
    eChar = None
    __updateTime = 0.5
    __width = 0
    __height = 0
    __fig_x, __fig_y = 0, 0
    __initialized = False
    __start = False
    __window = False
    running = False
    __StartButton = None
    __StopButton = None
    __PauseButton = None
    __ErrorClearButton = None
    __ContinueButton = None
    __ExecThread = None
    __deviceCharacterization = None
    __threads = None
    __tab1 = None
    __tab2 = None
    __tab3 = None
    __note = None
    instClose = None
    font_row = 16
    font_column = 16
    AvailableInstruments = dict()
    __PercComp = None
    __Complete = 0
    Configuration = None
    __rm = None
    __instruments = ()
    DieMaps = [0,1,2,3,4]
    __MatrixTable = None
    ResultHandling=None
    __PlotDPI = 600
    MouseObserver = None
    __Tab7Fig = None
    updateTimeLong = 0.5
    LongCounter = 0
    updateTime = 0.5
    ErrorFrames = []
    LogFrames = []
    MeasLogThread = None
    dieFolder = "DieFiles"


    def __init__(self, app, size=None, title="Figure 1", Configuration=None, ElectricalCharacterization=None, Instruments=None ,threads=None, updateTime=0.5, icon="etc/windowIcon_SUNYPoly.gif"):

        super().__init__()
        self.app = app
        if size == None:
            size = ""
        
        self.DateFolder = ""
        self.loader = "etc/Pacman-1s-200px.gif"

        self.eChar = ElectricalCharacterization
        self.Configuration = Configuration

        self._main = QtWidgets.QWidget(self)
        self.QFont = QtGui.QFont()
        self.QPainter = QtGui.QPainter()
        self.Qpalette = QtGui.QPalette()
        self.interval = 10 #update inverval in milliseconds

        self.homeDirectory = os.getcwd()

        ID = 1

        self.WaferMapTabID = ID
        ID = ID+1
        self.MeasurementTabID = ID
        ID = ID+1
        self.B1500TabID = ID
        ID = ID+1
        self.E5274ATabID = ID
        ID = ID+1
        self.ConfigTabID = ID
        ID = ID+1
        self.MatrixTabID = ID
        ID = ID+1
        self.SpecTabID = ID
        
        if size.lower() == "small":
            self.__width = 400
            self.__height = 300
            self.QFont.setPointSize(7)
            self.QMargin = [0,0,0,0]
            self.QSpacing = 0
            
        elif size.lower() == "large":
            self.__width = 800
            self.__height = 600
            self.QFont.setPointSize(12)
            self.QMargin = [5,5,5,5]
            self.QSpacing = 5

        elif size.lower() == "extralarge":
            self.__width = 1024
            self.__height = 768
            self.QFont.setPointSize(14)
            self.QMargin = [5,5,5,5]
            self.QSpacing = 5
        
        # standard is medium
        else:
            self.__width = 600
            self.__height = 450
            self.QFont.setPointSize(10)
            self.QMargin = [5,1,5,1]
            self.QSpacing = 2
            
        self.QFont.setStyleName("Helvetica")
        self.setFont(self.QFont)
        #self.Qpalette.setColor(QtGui.QPalette.Text, self.LightBlue)
        #self.Qpalette.setColor(QtGui.QPalette.WindowText, self.Blue)
        #self.Qpalette.setColor(QtGui.QPalette.ButtonText, self.Blue)
        #self.Qpalette.setColor(QtGui.QPalette.Background, self.White)
        #self.Qpalette.setColor(QtGui.QPalette.Button, self.Grey)
        #self.setPalette(self.Qpalette)
        
        self.setCentralWidget(self._main)   
        self.setObjectName("MainWindow")
        self.setWindowTitle("Electrical Characterization")

        self.resize(self.__width, self.__height)
        self.__widthTab = int(0.96*self.__width)
        
        self.icon = QtGui.QIcon(icon)

        try: 
            self.setWindowIcon(self.icon)
        except:
            self.__ErrorQu.put("Icon not found in window %s" %(title))

        # Create a canvas
        self.eChar = ElectricalCharacterization
        self.Configuration = Configuration
        self.__deviceCharacterization = []
        self.Instruments = Instruments
        self.__threads = threads
        self.__updateTime = updateTime
        self.updateTime = updateTime
        self.ExecThread = None
        self.running = False
        self.WidgetVariables = []
        
        self.ErrorFrames = []
        self.LogFrame = []

        ###### Create Horizontal Frame with SideButtons and Tab 
        self.HorzFrame = QtWidgets.QHBoxLayout(self._main)
        self.HorzFrame.setContentsMargins(0,0,0,0)
        self.HorzFrame.setSpacing(0)
        self.HorzFrame.setAlignment(QtCore.Qt.AlignTop)
        #self.HorzFrame.addStretch()

        ###### Main Buttons + Tab
        self.LeftWidget = QtWidgets.QWidget(self._main)
        self.HorzFrame.addWidget(self.LeftWidget)

        ###### Side Buttons
        self.SideButtons = Qt_MB.sideButtons(self,self._main)
        self.HorzFrame.addWidget(self.SideButtons)
        
        ###### Create Vertical Frame with MainButtons and Tab 
        self.VertFrame = QtWidgets.QVBoxLayout(self.LeftWidget)
        self.VertFrame.setContentsMargins(2,2,2,2)
        self.VertFrame.setSpacing(0)
        self.VertFrame.setAlignment(QtCore.Qt.AlignTop)
        self.VertFrame.addStretch()

        ###### Main Buttons
        self.MainButtons = Qt_MB.MainButtons(self, self._main)
        self.VertFrame.addWidget(self.MainButtons, QtCore.Qt.AlignTop)
        
        ###### Tab Widget
        self.tabs = stdObj.TabWidget(self._main)
        self.VertFrame.addWidget(self.tabs)
        self.tabs.updateGeometry()

        ######### Matrix and Specs widget
        self.MatrixTable = Qt_TB.MatrixTable(self.tabs, self, font=self.QFont)
        self.SpecTable = Qt_TB.SpecTable(self.tabs, self, font=self.QFont)

        tabsHeight = self.__height-self.MainButtons.height()
        self.tabs.setFixedHeight(tabsHeight)
        tabHeight = self.tabs.height()-10

        ###### Create WaferMapTab and add to TabsWidget
        self.WaferMapTab = Qt_WM.WaferMap(self.tabs, self, 9, 17, self.__widthTab, tabHeight, dieFolder=self.dieFolder)
        self.WaferMapTab.layout.setContentsMargins(*(self.QMargin))
        self.WaferMapTab.layout.setSpacing(self.QSpacing)
        self.tabs.insertTab(self.WaferMapTabID, self.WaferMapTab, "Wafer Map")

        ###### Create measurement Tab and add to TabsWidget
        self.MeasurementTab = Qt_MT.MainMeasurementFrame(self.tabs, self, self.__widthTab, tabHeight)
        self.MeasurementTab.layout.setContentsMargins(*(self.QMargin))
        self.MeasurementTab.layout.setSpacing(self.QSpacing)
        self.tabs.insertTab(self.MeasurementTabID, self.MeasurementTab, "Measurement")

        self.B1500Tab = Qt_B1500A.B1500AFrame(self.tabs, self, self.__widthTab, tabHeight)
        self.B1500Tab.layout.setContentsMargins(*(self.QMargin))
        self.B1500Tab.layout.setSpacing(self.QSpacing)
        self.tabs.insertTab(self.B1500TabID,self.B1500Tab, "B1500A")
        
        self.E5274ATab = Qt_E5274A.E5274AFrame(self.tabs, self, self.__widthTab, tabHeight)
        self.E5274ATab.layout.setContentsMargins(*(self.QMargin))
        self.E5274ATab.layout.setSpacing(self.QSpacing)
        self.tabs.insertTab(self.E5274ATabID,self.E5274ATab, "E5274A")

        self.ConfigTab = Qt_CF.ConfigurationFrame(self.tabs, self, 9, 17, self.__widthTab, tabHeight)
        self.ConfigTab.layout.setContentsMargins(*(self.QMargin))
        self.ConfigTab.layout.setSpacing(self.QSpacing)
        self.tabs.insertTab(self.ConfigTabID, self.ConfigTab, "Configuration")

        self.setFixedSize(self.size())

        self.ResultWindow = Qt_RW.ResultWindow(self, self.QFont, self.QMargin, self.QSpacing, self.__widthTab, self.__height, self.icon)
        self.ResultWindow.show()
        self.setResultWindowPosition()
        self.ResultWindow.hide()

        self.tabs.addTab(self.MatrixTable, "Matrix")
        
        self.tabs.addTab(self.SpecTable, "Specs")

        self.ResultHandling = RH.ResultHandling(self, self.ResultWindow)
        self.ResultHandling.start()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.setInterval(self.interval)
        self.timer.start()

    def savePosition(self):
        self.Configuration.setValue("MainWindowX", self.pos().x())
        self.Configuration.setValue("MainWindowY", self.pos().y())
        self.Configuration.setValue("MainWindowMon", QtWidgets.QDesktopWidget().screenNumber(self))

        self.ResultWindow.savePosition()

    def setResultWindowPosition(self):

        configName = "ResultWindow"
        window = self.ResultWindow
        posX = self.Configuration.getValue("%sX" %(configName))
        posY = self.Configuration.getValue("%sY" %(configName))
        screen = self.Configuration.getValue("%sMon" %(configName))
        
        sc = QtWidgets.QDesktopWidget().screenCount()
        if screen == None or screen >= sc:
            if sc > 1: 
                screen = 1
            else: 
                screen = 0
        monSize = QtWidgets.QDesktopWidget().availableGeometry(screen).size()
        if posX == None:
            if sc > 1:
                posX = 0
            else:
                posX =  self.windowHandle().width()
            if posX+self.__width > monSize.width():
                posX = monSize.width()-self.__width
        if posY == None:
            if sc > 1:
                posY = 0
            else:
                posY = 0
        
        window.move(posX, posY)
        scList = QtGui.QGuiApplication.screens()
        window.windowHandle().setScreen(scList[screen])
        
    def show(self, *args, **kwargs):
        super().show(*args, **kwargs)
        posX = self.Configuration.getValue("MainWindowX")
        posY = self.Configuration.getValue("MainWindowY")
        screen = self.Configuration.getValue("MainWindowMon")
        if posX == None:
            posX = 0
        if posY == None:
            posY = 0
        if screen == None:
            screen = 0
    
        self.move(0, 0)
        scList = QtGui.QGuiApplication.screens()
        self.windowHandle().setScreen(scList[screen])

    def WriteError(self, value):
        self.__ErrorQu.put(value)
    
    def WriteLog(self, value):
        self.__logQu.put(value)

    def getEChar(self):
        return self.eChar
    
    def getConfiguration(self):
        return self.Configuration
    
    def getInstruments(self):
        return self.Instruments

    def setUpdateInterval(self, interval=10):
        self.interval = interval

    def updateWidgets(self):
        for element in self.WidgetVariables:
            try:
                value = self.Configuration.getValue(element[1])
                element[0].setVariable(value)
            except:
                self.__ErrorQu.put("UpdateWidget: Variable '%s' does not exist in Configuration." %(element[1]))

    def addWidgetVariables(self, variable, name):
        self.WidgetVariables.append([variable, name])

    def geteChar(self):
        return self.eChar

    def deactivateInstruments(self, tool):
        if tool == 'Prober' or tool == "all":
            None
        if tool == "Matrix" or tool == "all":
            self.WaferMapTab.disableMatrix()
        
    def activateInstruments(self, tool):
        if tool == 'Prober' or tool == "all":
            None
        if tool == "Matrix" or tool == "all":
            self.WaferMapTab.enableMatrix()
        
    def InputDataWaferMap(self, data):
        self.__Canvas_1_data.put(data)

    def getHomeDirectory(self):
        return self.homeDirectory

    def setHomeDirectory(self, folder):
        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
                return True
            except FileExistsError:
                self.__ErrorQu.put("Home Directory was not changed (Input: %s)." %(folder))
                return False

    def ListToString(self, l):
        rowEntry = ""
        for entry in l: 
            rowEntry = "%s%s" %(rowEntry,entry)
        return rowEntry

    def MatrixDataToTable(self, MatrixData):

        data = []
        f=1
        if MatrixData == None or len(MatrixData) == 0: 
            data = None
        else:
            for n in range(len(MatrixData['BreakMake'])):
                row = []
                row.append("BM: %s" %(self.ListToString(MatrixData['BreakMake'][n])))
                row.append("MB: %s" %(self.ListToString(MatrixData['MakeBreak'][n])))
                NoOut = ""
                for m in range(len(MatrixData['NormalOutputs'][n])-1):
                    NoOut = "%s%s-%s;" %(NoOut, MatrixData['NormalOutputs'][n][m], MatrixData['NormalInputs'][n][m])
                NoOut = "%s%s-%s" %(NoOut, MatrixData['NormalOutputs'][n][m+1], MatrixData['NormalInputs'][n][m+1])
                row.append(NoOut)
                row.append("BL: %s" %(MatrixData['BitInputs'][n][0]))
                row.append("BH: %s" %(MatrixData['BitInputs'][n][1]))
                row.append("BI: %s" %(self.ListToString(MatrixData['BitOutputs'][n])))

                data.append(row)

        return data

    def getThreats(self):
        th = []
        th.append(self.__TKthread)
        th.append(self.__InterfaceThread)
        return th

    def closeEvent(self, event):
        event.ignore()
        self.on_closing()

    def MsgButtonClicked(self, i):
        if "&Yes" == i.text():
            self._main.setDisabled(True)
            self.CloseLabel = QtWidgets.QLabel(self._main)
            self.CloseLabel.setAlignment(QtCore.Qt.AlignCenter)
            self.CloseMovie = QtGui.QMovie(self.loader)
            self.CloseLabel.setMovie(self.CloseMovie)
            self.CloseLabel.setMinimumSize(self.sizeHint())
            self.CloseLabel.show()
            self.CloseMovie.start()
            self.instClose = th.Thread(target=self.Instruments.close)
            self.instClose.start()
            self.__close = True
            #self.ResultWindow.close()
            self.ResultHandling.close()
            self.closeStart=tm.time()

    def on_closing(self):

        if self.instClose != None:
            return None

        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowIcon(self.icon)
        if self.running:
            msgBox.setWindowTitle("Status")
            msgBox.setText("A measurement is currently running!")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        else:
            msgBox.setText("The program is about to close.")
            msgBox.setInformativeText("Do you want to quit?")
            msgBox.setWindowTitle("Quit")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            msgBox.setDefaultButton(QtWidgets.QMessageBox.No)
            msgBox.buttonClicked.connect(self.MsgButtonClicked)

        msgBox.exec_()
    
    def getWindowWidth(self):
        return self.__width

        
    def getTabWidth(self):
        return self.__widthTab

    def getWindowHeight(self):
        return self.__height

    def InitializeWidgetValues(self):
        self.Configuration.InitializeFromConfig()
        self.updateWidgets()
        self.WaferMapTab.MapUpdateDieMap()
        self.B1500Tab.update()

    def CheckBoxAppPara(self):
        if self.__AppParaVar.get():
            self.Configuration.setAppyParametersB1530()
        else:
            self.Configuration.resetAppyParametersB1530()

    def callB1530AChn1OperMode(self, mode):
        self.Configuration.setB1530Chn1OperationalMode(self.ModeList[mode])
        ret = True
        return ret

    def callB1530AChn2OperMode(self, mode):
        self.Configuration.setB1530Chn2OperationalMode(self.ModeList[mode])
        ret = True
        return ret

    def callB1530AChn1ForceVoltRange(self, Range):
        self.Configuration.setB1530Chn1ForceVoltageRange(self.ForceVoltageRange[Range])
        ret = True
        return ret

    def callB1530AChn2ForceVoltRange(self, Range):
        self.Configuration.setB1530Chn1ForceVoltageRange(self.ForceVoltageRange[Range])
        ret = True
        return ret
    
    def callB1530AChn1MeasureMode(self, Mode):
        self.Configuration.setB1530Chn1MeasureMode(self.MeasureMode[Mode])
        if Mode == "Voltage":
            Default = self.getKeyFromVal(self.Configuration.getB1530VoltageMeasureRange()[0], self.MeasureModeVoltage)
            self.__Chn1MeasureRangeList.set_menu(Default, *list(self.MeasureModeVoltage.keys()))
        else: 
            Default = self.getKeyFromVal(self.Configuration.getB1530CurrentMeasureRange()[0], self.MeasureModeCurrent)
            self.__Chn1MeasureRangeList.set_menu(Default, *list(self.MeasureModeCurrent.keys()))
        ret = True
        return ret

    def callB1530AChn2MeasureMode(self, Mode):
        self.Configuration.setB1530Chn2MeasureMode(self.MeasureMode[Mode])
        if Mode == "Voltage":
            Default = self.getKeyFromVal(self.Configuration.getB1530VoltageMeasureRange()[1], self.MeasureModeVoltage)
            self.__Chn2MeasureRangeList.set_menu(Default, *list(self.MeasureModeVoltage.keys()))
        else: 
            Default = self.getKeyFromVal(self.Configuration.getB1530CurrentMeasureRange()[1], self.MeasureModeCurrent)
            self.__Chn2MeasureRangeList.set_menu(Default, *list(self.MeasureModeCurrent.keys()))
        ret = True
        return ret

    def callB1530AChn1MeasureRange(self, Mode):
        if self.__Chn1MeasureModeVar.get() == "Voltage":
            self.Configuration.set1530Chn1MeasureVoltageRange(self.MeasureModeVoltage[Mode])
        else:
            self.Configuration.setB1530Chn1MeasureCurrentRange(self.MeasureModeCurrent[Mode])
        ret = True
        return ret

    def callB1530AChn2MeasureRange(self, Mode):
        if self.__Chn2MeasureModeVar.get() == "Voltage":
            self.Configuration.set1530Chn2MeasureVoltageRange(self.MeasureModeVoltage[Mode])
        else:
            self.Configuration.setB1530Chn2MeasureCurrentRange(self.MeasureModeCurrent[Mode])
        ret = True
        return ret

    def updateErrorFrames(self, error):
        for frame in self.ErrorFrames:
            frame.add(error)
    
    def clearErrorFrames(self):
        for frame in self.ErrorFrames:
            frame.clear()

    def updateLogFrame(self, log):
        for frame in self.LogFrame:
            frame.add(log)

    def clearLogFrame(self):
        for frame in self.LogFrame:
            frame.clear()

    def startExecution(self, MeasType):
        self.DateFolder = self.getEChar().updateDateFolder()
        self.MainButtons.reset()
        self.WaferMapTab.CreateCanvas()
        MeasTypeClass = self.WaferMapTab
        ConfigCopy = cp.deepcopy(self.Configuration)
        self.eChar.updateConfiguration(ConfigCopy)
        measurements = self.MeasurementTab.getMeasurements()
        if len(measurements) == 0:
            self.WriteError("No Measurement has been defined.")
            self.running = False
        else:
            self.ResultHandling.clear()
            self.eChar.deviceCharacterization = measurements
            self.__deviceCharacterization = measurements
            self.eChar.ConfigCopy = ConfigCopy
            self.eChar.startMeasureLog()
            self.eChar.MeasTypeClass = MeasTypeClass
            self.ExecThread = th.Thread(target=std.MesurementExecution, args=(self.__deviceCharacterization, self.eChar, ConfigCopy, self.__threads, self, self.Instruments, MeasTypeClass))
            self.ExecThread.start()
            self.MainButtons.StartButtonStyle('green')

    def isRunning(self):
        return self.running

    def Finished(self):
        self.__Finished.put(True)

    def InstrUpdate(self):
        if not self.running:
            self.Instruments.ReInitialize()
            self.eChar.updateTools(self.Instruments)
        else:
            self.__ErrorQu.put("Instrument Update not allowed during Measurement.")

    def continueExecution(self):
        if self.Pause.empty():
            if not self.Close.empty():
                while not self.Close.empty():
                    c = self.Close.get()
                return not c
        else: 

            pause = False
            while not self.Pause.empty():
                pause = self.Pause.get()

            while pause:               
                tm.sleep(self.__updateTime)
                if not self.Pause.empty():
                    while not self.Pause.empty():
                        pause = self.Pause.get()
                    
        return True

    def update(self):

        if self.instClose != None:

            timeout = 30

            if (not self.instClose.isAlive() and self.ResultHandling.isFinished()) or self.closeStart+timeout < tm.time():
                
                self.CloseMovie.stop()
                self.app.quit()
                self.app.exit()
                super().closeEvent(QtGui.QCloseEvent())
            
            self.timer.start()
            return None

        write = False
        while not self.__Canvas_1_data.empty():
            data = self.__Canvas_1_data.get()
            self.WaferMapTab.WaferMap.writeToData(data['Die'][0],data['Die'][1],add=data['add'])
            self.MainButtons.updateComplete(data['add'])
            write = True

        if write:
            self.WaferMapTab.WaferMap.update()
            self.WaferMapTab.DrawCanvas()
        
        if self.Instruments != None:
            self.Instruments.update(self)
        
        while not self.__ErrorQu.empty():
            error = self.__ErrorQu.get()
            self.Configuration.addElementErrorList(error)
            self.updateErrorFrames(error)
        
        while not self.ResultWindow.ErrorQu.empty():
            error = self.ResultWindow.ErrorQu.get()
            self.Configuration.addElementErrorList(error)
            self.updateErrorFrames(error)
        
        while not self.Instruments.Warnings.empty():
            error = self.Instruments.Warnings.get()
            self.Configuration.addElementErrorList(error)
            self.updateErrorFrames(error)

        while not self.Instruments.Warnings.empty():
            error = self.Instruments.Warnings.get()
            self.Configuration.addElementErrorList(error)
            self.updateErrorFrames(error)

        while not self.__logQu.empty():
            log = self.__logQu.get()
            self.Configuration.addElementLogList(log)
            self.updateLogFrame(log)

        while not self.eChar.LogData.empty():
            log =self.eChar.LogData.get()
            self.Configuration.addElementLogList(log)
            self.updateLogFrame(log)

        while not self.Configuration.ErrorQueue.empty():
            error = self.Configuration.ErrorQueue.get()
            self.Configuration.addElementErrorList(error)
            self.updateErrorFrames(error)

        while not self.Instruments.Errors.empty():
            error = self.Instruments.Errors.get()
            self.Configuration.addElementErrorList(error)
            self.updateErrorFrames(error)
        
        while not self.Instruments.AvailDevices.empty():
            avDev = self.Instruments.AvailDevices.get()
            
            for key, value in avDev.items():
                try:
                    if self.AvailableInstruments[key] != value:
                        self.AvailableInstruments[key] = value
                        if value: 
                            self.activateInstruments(key)
                        else:
                            self.deactivateInstruments(key)
                        self.MeasurementTab.updateAvailDevices()
                    
                except:
                    self.AvailableInstruments[key] = value
                    self.MeasurementTab.updateAvailDevices()
                    if value: 
                        self.activateInstruments(key)
                    else:
                        self.deactivateInstruments(key)
                
                self.MeasurementTab.updateAvailDevices()

        finished = False
        if self.ExecThread != None:
            if not self.ExecThread.isAlive():
                finished = True
                self.eChar.stopMeasureLog()
                self.ExecThread = None

        if finished:
            self.running = False
            self.MainButtons.Finished()
            
        if len(self.Instruments.getInstrumentsByType("B1500A")) != 0:
            if self.Instruments.getInstrumentsByType("B1500A")[0]['Instrument'] == None:
                ID = self.tabs.indexOf(self.B1500Tab)
                if ID != -1:
                    self.tabs.removeTab(ID)
            elif self.tabs.indexOf(self.B1500Tab) == -1:
                ID = self.tabs.indexOf(self.MeasurementTab)
                if ID == -1:
                    self.B1500TabID = self.tabs.addTab(self.B1500Tab, "B1500A")
                else:
                    self.B1500TabID = self.tabs.insertTab(ID+1, self.B1500Tab, "B1500A")
        
        if len(self.Instruments.getInstrumentsByType("E5274A")) != 0:
            if self.Instruments.getInstrumentsByType("E5274A")[0]['Instrument'] == None:
                ID = self.tabs.indexOf(self.E5274ATab)
                if ID != -1:
                    self.tabs.removeTab(ID)
            elif self.tabs.indexOf(self.E5274ATab) == -1:
                ID = self.tabs.indexOf(self.MeasurementTab)
                if ID == -1:
                    self.E5274ATabID = self.tabs.addTab(self.E5274ATab, "B1500A")
                else:
                    self.E5274ATabID = self.tabs.insertTab(ID+1, self.E5274ATab, "B1500A")

        if self.Configuration.getMatrixConfiguration() == None or self.Instruments.getMatrix() == None:
            ID = self.tabs.indexOf(self.MatrixTable)
            if ID != -1:
                self.tabs.removeTab(ID)
        elif self.tabs.indexOf(self.MatrixTable) == -1:
            ID = self.tabs.indexOf(self.ConfigTab)
            if ID == -1:
                self.MatrixTableID = self.tabs.addTab(self.MatrixTable, "Matrix")
            else:
                self.MatrixTableID = self.tabs.insertTab(ID+1, self.MatrixTable, "Matrix")
        
        if self.Configuration.getSpecs() == None:
            ID = self.tabs.indexOf(self.SpecTable)
            if ID != -1:
                self.tabs.removeTab(ID)
        elif self.tabs.indexOf(self.SpecTable) == -1:
            ID = self.tabs.indexOf(self.MatrixTable)
            if ID == -1:
                ID = self.tabs.indexOf(self.ConfigTab)
                if ID == -1:
                    self.SpecTabID = self.tabs.addTab(self.SpecTable, "Specs")
            else:
                self.SpecTabID = self.tabs.insertTab(ID+1, self.SpecTable, "Specs")

        try:
            if not self.ResultHandling.isAlive():
                self.ResultHandling = RH.ResultHandling(self, self.ResultWindow)
                self.ResultHandling.start()
                
        except AttributeError as e:
            self.__ErrorQu.put("Not able to restart Result Handling. %s" %(e))

        self.MainButtons.Update()
        self.WaferMapTab.update()
        self.ConfigTab.update()
        self.B1500Tab.update()
        self.E5274ATab.update()
        self.ResultWindow.update()
        
        self.timer.start()

    def getColorPalette(self, color=None, typ=None):

        colors = dict()
        colors['white'] = QtGui.QColor(255,255,255,255)
        colors['blue'] = QtGui.QColor(0,76,147)
        colors['lightblue'] = QtGui.QColor(0,158,224)
        colors['grey'] = QtGui.QColor(132,134,135)
        colors['yellow'] = QtGui.QColor(255,229,18)
        colors['orange'] = QtGui.QColor(255,102,0)
        colors['pink'] = QtGui.QColor(236,9,141)
        colors['purple'] = QtGui.QColor(120,29,126)
        colors['green'] = QtGui.QColor(84,185,72)
        colors['black'] = QtGui.QColor(0,0,0,0)

        color = color.lower()

        try:
            c = colors[color]

        except:
            return QtGui.QGuiApplication.palette()

        pal = QtGui.QPalette()
        if typ.lower() == 'buttontext':
            pal.setColor(QtGui.QPalette.ButtonText, c)
        elif typ.lower() == 'window':
            pal.setColor(QtGui.QPalette.Window, c)
        elif typ.lower() == 'windowtext':
            pal.setColor(QtGui.QPalette.WindowText, c)
        elif typ.lower() == 'foreground':
            pal.setColor(QtGui.QPalette.Foreground, c)
        elif typ.lower() == 'base':
            pal.setColor(QtGui.QPalette.Base, c)
        elif typ.lower() == 'alternatebase':
            pal.setColor(QtGui.QPalette.AlternateBase, c)
        elif typ.lower() == 'tooltipbase':
            pal.setColor(QtGui.QPalette.ToolTipBase, c)
        elif typ.lower() == 'tooltiptext':
            pal.setColor(QtGui.QPalette.ToolTipText, c)
        elif typ.lower() == 'placeholdertext':
            pal.setColor(QtGui.QPalette.placeholdertext, c)
        elif typ.lower() == 'text':
            pal.setColor(QtGui.QPalette.Text, c)
        elif typ.lower() == 'button':
            pal.setColor(QtGui.QPalette.Button, c)
        elif typ.lower() == 'background':
            pal.setColor(QtGui.QPalette.Background, c)
        else:
            pal = QtGui.QGuiApplication.palette()
            
        return pal
