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


class ConfigurationFrame(stdObj.stdFrameGrid):

    InstUpdate = qu.Queue()

    def __init__(self, master, MainGI, columns, rows, width, height, **kwargs):

        super().__init__(master, MainGI, columns, rows, width, height, **kwargs)
    
        self.MainGI = MainGI
        self.Entries = []
        self.width = width
        self.height = height
        self.InstUpdateQu = qu.Queue()
        self.rows = rows
        self.columns = columns
        self.TempEntryLocked = False
        self.setTemp = 0

        self.Configuration = self.MainGI.getConfiguration()
        self.Instruments = self.MainGI.getInstruments()
        self.caliThread = None
        self.resetThread = None
        
        self.row = 0
        self.col = 0
        
        self.FolderTit = Label(self, layout=self.layout, text="Folders and Files", row=self.row, column=self.col, columnspan=4)
        self.FolderTit.setFont(self.titleFont)

        self.row = self.row +1
        self.__FolderButton = stdObj.folderButton(self, MainGI, "Mainfolder", NameLength=30)
        self.layout.addWidget(self.__FolderButton, self.row, self.col+2, 1, 2)
        self.TxMainFolder=Label(self, layout=self.layout, text="Main Folder:", row=self.row, column=self.col, columnspan=2)

        self.row = self.row + 1
        self.__SpecFileButton = stdObj.fileButton(self, MainGI, "SpecFile", command=self.updateSpecs, fileFormat = "CSV file (*.csv)",  NameLength=30)
        self.layout.addWidget(self.__SpecFileButton, self.row, self.col+2, 1, 2)
        self.TxSpecFile=Label(self, layout=self.layout, text="Spec File:",row=self.row, column=self.col, columnspan = 2)
        
        self.row = self.row + 1
        self.__MatrixFileButton = stdObj.fileButton(self, MainGI, "MatrixFile", command=self.updateMatrix, fileFormat = "CSV file (*.csv)", NameLength=30)
        self.layout.addWidget(self.__MatrixFileButton, self.row, self.col+2, 1, 2)
        self.TxMatrixFile=Label(self, layout=self.layout, text="Matrix File:", row=self.row, column=self.col, columnspan = 2)
        
        self.row = 0
        self.col = 4
        self.FolderTit = Label(self, layout=self.layout, text="Configuration File:", row=self.row, column=self.col, columnspan=4)
        self.FolderTit.setFont(self.titleFont)

        self.row = self.row + 1
        self.InitButton = PushButton(self, layout=self.layout, text="Initialize Values", command=self.InitValues, row=self.row, column=self.col, columnspan=3)
        self.row = self.row + 1
        self.SaveInitButton = PushButton(self, layout=self.layout, text="Save Init. Values", command=self.SaveInitValues, row=self.row, column=self.col, columnspan=3)

        self.row = self.row + 1
        self.AutoSaveConfigCheckbox = CheckBox(self, self.MainGI, text="Auto. Save of Config.", valueName="AutoSaveConfig", layout=self.layout, row=self.row, column=self.col, columnspan=3, alignment=QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        
        self.col = 7
        self.row = 0
        self.ProberFrame = QtWidgets.QWidget(self)
        self.layout.addWidget(self.ProberFrame, self.row, self.col, 4, 3)
        self.ProberSettings()

        self.row = self.row + 10
        self.ReloadModTx = Label(self, layout=self.layout, text="Reload Modules", row=self.row, column=self.col, columnspan=3)
        self.ReloadModTx.setFont(self.titleFont)

        self.TxWarErr=stdObj.Label("Warnings and Errors:", self)
        self.addWidget(self.TxWarErr, row=self.row, column=0, columnspan=3, alignment=QtCore.Qt.AlignLeft)
        self.__ErrorClearButton = stdObj.PushButton("Clear", self, sizePolicy=[QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding], command=self.clearErrorFrame)
        self.addWidget(self.__ErrorClearButton, row=self.row, column=3, columnspan=1, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.__InstUpdButton = PushButton(self, layout=self.layout, row=self.row, column=5, columnspan=2, text="Update Instruments", command=self.UpdateInstruments)

        self.row = self.row + 1
        self.RelEChar = PushButton(self, layout=self.layout, text="E-characterization", command=self.ReloadEchar, row=self.row, column=self.col, columnspan=3)
        self.ErrorFrame = stdObj.ErrorLog(self, "ErrorLog", MainGI=MainGI, sizePolicy=[QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding])
        self.addWidget(self.ErrorFrame, row=self.row, column=0, columnspan=7, rowspan=5)

        self.row = self.row + 1
        self.RelStdDef = PushButton(self, layout=self.layout, text="Standard Definitions", command=self.ReloadStdDef, row=self.row, column=self.col, columnspan=3)

        self.row = self.row + 1
        self.RestartGUI = PushButton(self, layout=self.layout, text="Restart GUI", command=self.restartGUI, row=self.row, column=self.col, columnspan=3)
        
        self.row = self.row + 1
        self.TxReset=stdObj.Label("Resets", self)
        self.TxReset.setFont(self.titleFont)
        self.addWidget(self.TxReset, row=self.row, column=self.col, columnspan=3, alignment=QtCore.Qt.AlignLeft)
        
        
        self.row = self.row + 1
        self.SoftResetBut = PushButton(self, layout=self.layout, text="Soft", command=self.SoftReset, row=self.row, column=self.col, columnspan=1)
        self.HardResetBut = PushButton(self, layout=self.layout, text="Hard", command=self.HardReset, row=self.row, column=self.col+1, columnspan=1)

        self.CreateInstFrame()
        self.updateMatrix()
        self.updateSpecs()
    
    def SaveInitValues(self):
        self.MainGI.savePosition()
        self.Configuration.saveConfigToFile()
    
    def restartGUI(self):
        self.MainGI.on_closing(restart=True)
    
    def ReloadEchar(self):
        il.reload(eChar)
        self.MainGI.eChar = eChar.ECharacterization(self.Instruments, self.Configuration, WaferChar=True)

    def ReloadStdDef(self):
        il.reload(std)
    
    def ReloadPlotRout(self):
        il.reload(PR)
        
    def HardReset(self):
        self.MainGI.running = False
        self.MainGI.MainButtons.Finished()
        self.UpdateInstruments()
        self.TempEntryLocked = False

    def SoftReset(self):
        self.MainGI.running = False
        self.MainGI.MainButtons.Finished()
        self.TempEntryLocked = False

    def clearErrorFrame(self):
        self.Configuration.clearErrorList()
        self.MainGI.clearErrorFrames()

    def ProberSettings(self):

        if  self.Instruments.getProberInstrument() != None:
            
            self.ProberLayout = QtWidgets.QGridLayout(self.ProberFrame)
            #self.ProberLayout.setAlignment(QtCore.Qt.AlignTop)

            self.Prober = self.Instruments.getProberInstrument()

            for n in range(3):
                self.ProberLayout.setRowMinimumHeight(n+1, self.height)

            row = 1
            col = 1
            self.ProbeStationSetTx = Label(self.ProberFrame, layout=self.ProberLayout, text="Probe Station Settings", row=row, column=col, columnspan=2)
            self.ProbeStationSetTx.setFont(self.titleFont)

            row = row + 1
            self.CurChuckTempTx = Label(self.ProberFrame, layout=self.ProberLayout, text="Cur. Chuck Temp.: ", row=row, column=col, columnspan=1)
            
            self.ProberCurTemp = Label(self.ProberFrame, layout=self.ProberLayout, text="%s ℃" %(self.Instruments.getChuckTemperature()), row=row, column=col+1, columnspan=1)
    
            row = row + 1
            self.SetChuckTempTx = Label(self.ProberFrame, layout=self.ProberLayout, text="Set Chuck Temp. (℃): ", row=row, column=col, columnspan=1)
    
            self.TempEnt = LineEdit(self.ProberFrame, str(self.Instruments.getChuckTemperature()), self.ProberLayout, row, col+1, width=8, validateNumbers="[0-300]", command=self.ChangeTempReturn)
            

    def ChangeTempReturn(self):
        try:
            self.setTemp = int(self.TempEnt.text())
            self.Instruments.getProberInstrument().SetHeaterTemp(self.setTemp)
            self.MainGI.WriteLog("Chuck Temperature set to %d." %(self.setTemp))
            self.TempEntryLocked = True
        except:
            self.MainGI.WriteError("Not able to set Chuck Temperature to %d." %(self.setTemp))

    def InitValues(self):
        self.MainGI.InitializeWidgetValues()

    def updateMatrix(self):
        MatrixData = self.Configuration.UpdateMatrixConfig()
        if MatrixData != None:
            self.MainGI.MatrixTable.update(MatrixData)

    def updateSpecs(self):
        SpecsRaw = self.Configuration.getSpecs()
        if SpecsRaw != None:
            self.MainGI.SpecTable.update(SpecsRaw)

    def CreateInstFrame(self):

        cspan = 10
        self.ScrollFrame = QtWidgets.QScrollArea(self)
        #self.InstrFrame.setVerticalScrollBar()
        self.ScrollFrame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.layout.addWidget(self.ScrollFrame, 4, 0, 6, cspan)
        self.ScrollLayout = QtWidgets.QVBoxLayout(self.ScrollFrame)
        self.ScrollFrame.setContentsMargins(0,0,0,0)
        self.ScrollLayout.setContentsMargins(0,0,0,0)

        self.InstrFrame = QtWidgets.QWidget(self.ScrollFrame)
        self.ScrollLayout.addWidget(self.InstrFrame)
        self.ScrollLayout.setAlignment(QtCore.Qt.AlignTop)
        
        self.InstLayout = QtWidgets.QGridLayout(self.InstrFrame)
        #self.InstLayout.setColumnMinimumWidth()
        #FrWidth = self.layout.columnMinimumWidth(1)*cspan
        row = 0
        col = 0
        self.TypeTx=Label(self.InstrFrame, layout=self.InstLayout, text="Type", row=row, column=col)
        self.TypeTx.setFont(self.titleFont)
        
        self.ClassTx=Label(self.InstrFrame, layout=self.InstLayout, text="Class", row=row, column=col+1)
        self.ClassTx.setFont(self.titleFont)
        
        self.GPIBTitTx=Label(self.InstrFrame, layout=self.InstLayout, text="GPIB", row=row, column=col+2)
        self.GPIBTitTx.setFont(self.titleFont)
        
        
        self.GPIBTitTx=Label(self.InstrFrame, layout=self.InstLayout, text="Rank", row=row, column=col+3)
        self.GPIBTitTx.setFont(self.titleFont)

        #self.InstLayout.setColumnMinimumWidth(1, int(FrWidth*0.15))
        #self.InstLayout.setColumnMinimumWidth(2, int(FrWidth*0.2))
        #self.InstLayout.setColumnMinimumWidth(3, int(FrWidth*0.3))
        #self.InstLayout.setColumnMinimumWidth(4, int(FrWidth*0.15))
        #self.InstLayout.setColumnMinimumWidth(5, int(FrWidth*0.2))

        row = row + 1

        self.CreateInstrFrameWidgets(row, col)

    def CreateInstrFrameWidgets(self, row=1, column=1):
        
        self.InstrWidgets = []

        Probers = []
        ProberAdrs = []
        Matrixs = []
        MatrixAdrs = []
        Tools  = []

        col = column

        ProbInit = None
        MatrixInit = None
        ConfigProber = self.Configuration.getProber()
        ConfigMatrix = self.Configuration.getMatrix()

        toolOrder = self.Instruments.getToolTypes()

        tempTools = []
        for n in range(len(toolOrder[2:])):
            tempTools.append([])

        for instr in self.Instruments.getAvailableInstrumentsComplete():
            if instr['ToolType'] == "Prober":
                Probers.append(instr)
                ProberAdrs.append(instr["GPIB"])
            elif instr['ToolType'] == "Matrix":
                Matrixs.append(instr)
                MatrixAdrs.append(instr["GPIB"])
            else:
                k = 0
                for typ in toolOrder[2:]:
                    if typ == instr['ToolType']:
                        try:
                            tempTools[k].append(instr)
                        except IndexError:
                            tempTools.append([])
                            tempTools[k].append(instr)
                    k = k+1
                    
        Tools = []
        for t in tempTools:
            Tools.extend(t)


        row = row - 1
        if len(Probers) > 0:
            
            row = row + 1
            
            self.TxProber=Label(self.InstrFrame, layout=self.InstLayout, text="Prober", row=row, column=col)
            self.InstrWidgets.append(self.TxProber)

            ProbInit = Probers[0]
            if ConfigProber != None:
                for Prob in Probers:
                    if Prob['Type'] == ConfigProber[0] and Prob['GPIB'] == ConfigProber[1]:
                        ProbInit = Prob
                        ProbFound = True
                        break
            
            self.TxProberName=Label(self.InstrFrame, text=ProbInit['Class'], layout=self.InstLayout, row=row, column=col+1)
            self.InstrWidgets.append(self.TxProberName)

            self.ProberDropDown = ComboBox(self.InstrFrame, ProberAdrs, ProbInit['GPIB'], self.InstLayout, row, col+2, command=self.UpdateProberGPIB)
            self.InstrWidgets.append(self.ProberDropDown)
            

        if len(Matrixs) > 0:

            row = row + 1
            self.TxMatrix=Label(self.InstrFrame, text="Matrix", layout=self.InstLayout, row=row, column=col)
            self.InstrWidgets.append(self.TxMatrix)

            MatrixInit = Matrixs[0]
            if ConfigMatrix != None:
                for Mat in Matrixs:
                    if Mat['Type'] == ConfigMatrix[0] and Mat['GPIB'] == ConfigMatrix[1]:
                        MatrixInit = Mat
                        break
                        
            self.TxMatrixName=Label(self.InstrFrame, text=MatrixInit['Class'], layout=self.InstLayout, row=row, column=col+1)
            self.InstrWidgets.append(self.TxMatrixName)

            self.MatrixDropDown = ComboBox(self.InstrFrame, MatrixAdrs, MatrixInit['GPIB'], self.InstLayout, row, col+2, command=self.UpdateMatrixGPIB)
            self.InstrWidgets.append(self.MatrixDropDown)

            self.MatrixReset = PushButton(self.InstrFrame, layout=self.InstLayout, text="Reset", command=self.funcMatrixReset, row=row, column=col+4)
            self.InstrWidgets.append(self.MatrixReset)

        self.Txt = []
        self.ResetWid = []
        self.CalibWid = []
        self.GPIBWid = []
        self.RankWid = []
        self.TxtClass = []
        self.TxtGPIB = []
        self.TxtGPIBVar = []
        self.initTools = []
        
        #### fix tool link to lambda function. Use GPIB address

        for tool in Tools:
            
            if tool['Type'] != 'Prober' and tool['Type'] != 'Matrix':
                defRank = self.Configuration.getValue("$ToolRank$_%s" %(tool['GPIB']))
                if defRank != None:
                    self.Instruments.setToolRank(tool['GPIB'], defRank)

                RankAdr = self.Instruments.getRanksForTools(tool['Type'])

                self.initTools.append(tool)

                row = row + 1
                self.Txt.append(Label(self.InstrFrame, layout=self.InstLayout, text=tool['Type'], row=row, column=col))
                self.InstrWidgets.append(self.Txt[-1])

                self.TxtClass.append(Label(self.InstrFrame, layout=self.InstLayout, text=tool['Class'], row=row, column=col+1))
                self.InstrWidgets.append(self.TxtClass[-1])
                
                self.TxtGPIB.append(LineEdit(self.InstrFrame, layout=self.InstLayout, text=tool['GPIB'], row=row, column=col+2, state='disabled'))
                self.InstrWidgets.append(self.TxtGPIB[-1])
                
                self.RankWid.append(ComboBox(self.InstrFrame, RankAdr, tool['Rank'], self.InstLayout, row, col+3, command=self.UpdateRank, commandArgs=(tool['GPIB'],)))
                self.InstrWidgets.append(self.RankWid[-1])

                n = len(self.ResetWid)
                self.ResetWid.append(PushButton(self.InstrFrame, layout=self.InstLayout, text="Reset", command=self.instrumentReset, commandArgs=(tool['GPIB'], n), row=row, column=col+4))
                self.InstrWidgets.append(self.ResetWid[-1])

                n = len(self.CalibWid)
                self.CalibWid.append(PushButton(self.InstrFrame, layout=self.InstLayout, text="Calibration", command=self.instrumentCalibration, commandArgs=(tool['GPIB'], n), row=row, column=col+5))
                self.InstrWidgets.append(self.CalibWid[-1])


    def instrumentReset(self, gpib, n):

        if not self.MainGI.running:
            self.MainGI.running = True

            self.resetThread = self.Instruments.InstrumentReset(gpib)
                        
            pal = QtGui.QPalette()
            pal.setColor(pal.Button, QtCore.Qt.red)

            Button = self.ResetWid[n]
            Button.setAutoFillBackground(True)
            Button.setPalette(pal)
            Button.update()

    def instrumentCalibration(self, gpib, n):

        if not self.MainGI.running:
            self.MainGI.running = True

            self.caliThread = self.Instruments.InstrumentCalibration(gpib)
            
            pal = QtGui.QPalette()
            pal.setColor(pal.Button, QtCore.Qt.red)

            Button = self.CalibWid[n]
            Button.setAutoFillBackground(True)
            Button.setPalette(pal)
            Button.update()

    def funcMatrixReset(self):
        GPIB = str(self.MatrixDropDown.currentText())
        self.Instruments.InstrumentReset(GPIB)


    def funcProberReset(self):
        GPIB = str(self.ProberDropDown.currentText())
        self.Instruments.InstrumentReset(GPIB)

    def UpdateInstrFrame(self):
        for widget in self.InstrWidgets:
            self.InstLayout.removeWidget(widget)
            widget.close()
            widget.destroy()
        self.CreateInstrFrameWidgets(2,1)
        self.TempEntryLocked = False

    def UpdateProberGPIB(self, GPIB):
        self.Instruments.setCurrentProber(GPIB)

    def UpdateMatrixGPIB(self, GPIB):
        self.Instruments.setCurrentMatrix(GPIB)
    
    def UpdateRank(self, rank, gpib):
        self.Instruments.setToolRank(gpib, rank)
        n = 0
        for rw in self.RankWid:
            t = self.initTools[n]
            newRank = self.Instruments.getToolRank(t['GPIB'])
            rw.setCurrentText(str(newRank))
            self.Configuration.setValue("$ToolRank$_%s" %(t['GPIB']), newRank)

            n = n+1

    def UpdateInstruments(self):
        if not self.MainGI.running:
            self.MainGI.running = True

            pal = QtGui.QPalette()
            pal.setColor(pal.Button, QtCore.Qt.red)
            self.__InstUpdButton.setAutoFillBackground(True)
            self.__InstUpdButton.setPalette(pal)
            self.__InstUpdButton.update()
            self.__InstUpdButton.setDisabled(True)

            self.UpdInstThread = th.Thread(target=self.UpdateInstThread)
            self.UpdInstThread.start()

    def UpdateInstThread(self):
        
        self.Instruments.ReInitialize()

        start = tm.time()
        while not self.Instruments.ready:
            tm.sleep(0.01)
            if (tm.time() - start)> 2:
                break

        self.MainGI.geteChar().getTools()
        self.MainGI.Finished()
        self.MainGI.MainButtons.Finished()
        self.InstUpdateQu.put(False)


    def update(self):

        update = False
        chnRun = True
        while not self.InstUpdateQu.empty():
            
            chnRun = self.InstUpdateQu.get()
            self.__InstUpdButton.setDisabled(False)
            update = True
            
        
        if (not chnRun) and update:
            self.UpdateInstrFrame()
            self.MainGI.running = chnRun

            pal = self.MainGI.getColorPalette('','')
            self.__InstUpdButton.setAutoFillBackground(True)
            self.__InstUpdButton.setPalette(pal)
            self.__InstUpdButton.update()

        if self.caliThread != None:
            if not self.caliThread.is_alive():
                self.MainGI.running = False
                for wid in self.CalibWid:
                    pal = self.MainGI.getColorPalette('','')
                    wid.setAutoFillBackground(True)
                    wid.setPalette(pal)
                    wid.update()
                self.caliThread = None

        if self.resetThread != None:
            if not self.resetThread.is_alive():
                self.MainGI.running = False
                for wid in self.ResetWid:
                    pal = self.MainGI.getColorPalette('','')
                    wid.setAutoFillBackground(True)
                    wid.setPalette(pal)
                    wid.update()
                self.resetThread = None

        if self.MainGI.isRunning():
            self.__InstUpdButton.setDisabled(True)
            self.RelStdDef.setDisabled(True)
            self.RelEChar.setDisabled(True)
            try:
                self.ProberDropDown.setDisabled(True)
                self.MatrixDropDown.setDisabled(True)
            except AttributeError:
                None
            try:
                self.TempEnt.setDisabled(True)
            except AttributeError:
                None
            try:
                self.MatrixReset.setDisabled(True)
            except AttributeError:
                None
            for resWid in self.ResetWid:
                resWid.setDisabled(True)
            
            for resWid in self.CalibWid:
                resWid.setDisabled(True)
        else: 
            self.__InstUpdButton.setDisabled(False)
            self.RelStdDef.setDisabled(False)
            self.RelEChar.setDisabled(False)
            self.RelStdDef.setDisabled(False)
            try:
                self.ProberDropDown.setDisabled(False)
                self.MatrixDropDown.setDisabled(False)
            except AttributeError:
                None
            try:
                self.TempEnt.setDisabled(False)
            except AttributeError:
                None
            try:
                self.MatrixReset.setDisabled(False)
            except AttributeError:
                None
            for resWid in self.ResetWid:
                resWid.setDisabled(False)
            
            for resWid in self.CalibWid:
                resWid.setDisabled(False)
        

        ## to do
        if self.Instruments.getProberInstrument() != None:
            self.ProberFrame.setHidden(False)
            try:
                self.ProberCurTemp.setText("%s ℃ " %(self.Instruments.getChuckTemperature()))
            except AttributeError: 
                self.ProberSettings()
                self.ProberCurTemp.setText("%s ℃ " %(self.Instruments.getChuckTemperature()))
        else:
            self.ProberFrame.setHidden(True)


        if not self.TempEntryLocked:
            try:
                self.TempEnt.set(str(self.Instruments.getChuckTemperature()))
            except AttributeError:
                None

class PushButton(QtWidgets.QPushButton):

    def __init__(self, parent, text, layout, row, column, command=None, commandArgs=None, columnspan=1, rowspan=1, **kwargs):

        super().__init__(text, parent, **kwargs)

        self.command = command
        self.commandArgs = commandArgs
        self.layout = layout
        self.clicked.connect(self.callFunc)
        self.row = row
        self.column = column
        self.columnspan= columnspan
        self.rowspan = rowspan

        self.layout.addWidget(self, self.row, self.column, self.rowspan, self.columnspan)

    def callFunc(self):
        if self.commandArgs == None:
            self.command()
        else:
            self.command(*self.commandArgs)
            
class CheckBox(stdObj.CheckBox):

    def __init__(self, parent, MainGI, text, valueName, layout, row, column, columnspan=1, rowspan=1, **kwargs):


        self.row = row
        self.column = column
        self.columnspan= columnspan
        self.rowspan = rowspan

        self.layout = layout
        self.widget = QtWidgets.QWidget(parent)
        self.layout.addWidget(self.widget, self.row, self.column, self.rowspan, self.columnspan)
        self.layout1 =  QtWidgets.QHBoxLayout(self.widget)
        spacerLeft = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        spacerRight = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.layout1.addItem(spacerLeft)

        if text == None:
            super().__init__(parent, MainGI, valueName, **kwargs)
        else:
            super().__init__(parent, MainGI, valueName, text, **kwargs)
            
        self.stateChanged.connect(self.callFunc)
        self.layout1.addWidget(self)

        if "sizePolicy" in kwargs:
            self.setSizePolicy(kwargs['sizePolicy'])
        

        self.layout1.addItem(spacerRight)


class Label(QtWidgets.QLabel):

    def __init__(self, parent, text, layout, row=None, column=None, columnspan=1, rowspan=1, alignment=None):

        super().__init__(text, parent)

        self.layout = layout
        self.row = row
        self.column = column
        self.columnspan= columnspan
        self.rowspan = rowspan
        if row != None and column != None:
            if alignment != None:
                self.layout.addWidget(self, self.row, self.column, self.rowspan, self.columnspan, alignment)
            else:
                self.layout.addWidget(self, self.row, self.column, self.rowspan, self.columnspan)
        else:
            if alignment != None:
                self.layout.addWidget(self, alignment)
            else:
                self.layout.addWidget(self)

class LineEdit(QtWidgets.QLineEdit):

    def __init__(self, parent, text, layout, row, column, columnspan=1, rowspan=1, **kwargs):
            
        super().__init__(parent)
        self.setText(str(text))

        self.layout = layout
        self.layout.addWidget(self, row, column, rowspan, columnspan)

        if 'width' in kwargs:
            self.setMinimumWidth(int(kwargs['width']))

        self.addCommand = None
        if 'command' in kwargs:
            self.addCommand = kwargs['command']

        if 'ValidateNumbers' in kwargs:

            regEx = QtCore.QRegularExpression(kwargs['ValidateNumbers'])
            validator = QtGui.QRegularExpressionValidator(regEx, self)
            self.TempEnt.setValidator(validator)
        
        if 'state' in kwargs:
            if kwargs['state'] == 'disabled':
                self.setDisabled(True)
            else:
                self.setDisabled(False)
        
        if self.addCommand != None:
            self.returnPressed.connect(self.addCommand)
        
    def focusOutEvent(self, event):
        
        if self.addCommand != None:
            self.addCommand()
        
        super().focusOutEvent(event)


class ComboBox(QtWidgets.QComboBox):

    def __init__(self, parent, items, default, layout, row, column, commandArgs=None, columnspan=1, rowspan=1, **kwargs):
            
        super().__init__(parent)
        
        self.layout = layout
        self.layout.addWidget(self, row, column, rowspan, columnspan)

        n = 0
        for i in items:
            items[n] = str(items[n])
            n = n+1

        self.addItems(items)
        if isinstance(commandArgs, tuple):
            self.commandArgs = commandArgs
        elif isinstance(commandArgs, list):
            self.commandArgs = tuple(commandArgs)
        else:
            self.commandArgs = (commandArgs)
            
        dIndex = self.findText(str(default))
        self.setCurrentIndex(dIndex)

        if 'width' in kwargs:
            self.setMinimumWidth(int(kwargs['width']))

        if 'command' in kwargs:
            self.addCommand = kwargs['command']
            self.currentIndexChanged.connect(self.executeCommand)

        if 'sizePolicy' in kwargs:
            self.setSizePolicy(kwargs['sizePolicy'][0],kwargs['sizePolicy'][1])


    def executeCommand(self, index):
        value = self.itemText(index)
        if self.commandArgs != None:
            self.addCommand(value, *self.commandArgs)
        else:
            self.addCommand(value)
        
