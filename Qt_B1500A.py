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


class B1500AFrame(stdObj.stdFrame):

    def __init__(self, parent, MainGI, width, height, **kwargs):

        super().__init__(parent, MainGI, None, None, **kwargs)

        self.WGFMUParameters = {}

        self.WGFMUParameters["ModeList"] = {'PG': 2002, 'Fast IV': 2001, 'DC':2000, 'SMU':2003}
        self.WGFMUParameters["ForceVoltageRange"] = {'Auto':3000, '3V':3001, '5V':3002, '-10V':3003, '+10V':3004}
        self.WGFMUParameters["MeasureMode"] = {'Voltage':4000, 'Current':4001}
        self.WGFMUParameters["MeasureCurrentRange"] = {'1uA':6001, '10uA':6002, '100uA':6003, '1mA':6004, '10mA':6005}
        self.WGFMUParameters["MeasureVoltageRange"] = {'5V':5001, '10V':5002}

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.Mainlayout = QtWidgets.QHBoxLayout(self)
        self.Mainlayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.Mainlayout.setContentsMargins(0,0,0,0)
        self.Mainlayout.setSpacing(0)

        self.ScrollFrame = QtWidgets.QScrollArea(self)
        self.Mainlayout.addWidget(self.ScrollFrame)
        self.ScrollFrame.setWidgetResizable(True)
        self.ScrollFrame.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        self.ScrollFrame.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.ScrollLayout = QtWidgets.QHBoxLayout(self.ScrollFrame)
        self.ScrollLayout.setAlignment(QtCore.Qt.AlignLeft)
        
        self.Frame = QtWidgets.QWidget(self.ScrollFrame)
        self.Frame.setMinimumWidth(1)
        #pal = QtGui.QPalette()
        #pal.setColor( QtGui.QPalette.Background, QtCore.Qt.blue)
        self.Frame.setAutoFillBackground(True)
        self.Frame.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        
        self.layout = QtWidgets.QVBoxLayout(self.Frame)
        self.layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.ScrollFrame.setWidget(self.Frame)

        self.ScrollLayout.addWidget(self.Frame)
        self.ScrollLayout.setContentsMargins(0,0,0,0)
        self.ScrollLayout.setSpacing(0)
        

        self.topWidget = QtWidgets.QWidget(self.Frame)
#        self.topWidget.setFixedWidth(self.MainGI.getWindowWidth())
        self.topWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layout.addWidget(self.topWidget)

        # top Widget for B1530A

        self.topLayout = QtWidgets.QVBoxLayout(self.topWidget)
        self.topLayout.setContentsMargins(0,0,0,0)
        self.topLayout.setSpacing(0)
        if len(self.Instruments.getInstrumentsByType("B1530A")) != 0:
            
            self.B1530AuseLabel = QtWidgets.QLabel("B1530A" , self.topWidget)
            self.topLayout.addWidget(self.B1530AuseLabel)

            self.B1530Agcb = QtWidgets.QWidget(self)
            self.topLayout.addWidget(self.B1530Agcb)
            self.B1530AgcbLayout = QtWidgets.QHBoxLayout(self.B1530Agcb)
            

            self.useLabel = QtWidgets.QLabel("use GUI Parameters:" , self.B1530Agcb)
            self.B1530AgcbLayout.addWidget(self.useLabel)

            self.useCheckBox = CheckBox(self.B1530Agcb, "WGFMUUseGUI", self.Configuration)
            self.B1530AgcbLayout.addWidget(self.useCheckBox)
            self.B1530Agcb.setFixedSize(self.B1530Agcb.sizeHint())
            
            spItem = QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
            #self.B1530AgcbLayout.addSpacerItem(spItem)

            spItem = QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
            #self.B1530AgcbLayout.addSpacerItem(spItem)

            self.B1530AparWidget = QtWidgets.QWidget(self.topWidget)
            self.topLayout.addWidget(self.B1530AparWidget)
            self.B1530AparLayout = QtWidgets.QHBoxLayout(self.B1530AparWidget)
            self.initializeB1530A()


        self.bottomWidget = QtWidgets.QWidget(self.Frame)
        self.topWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layout.addWidget(self.bottomWidget)
        self.bottomLayout = QtWidgets.QVBoxLayout(self.bottomWidget)
        # bottom Widget for B1500A
        self.B1500As = self.Instruments.getInstrumentsByType("B1500A")
        self.SMUs = []
        if len(self.B1500As) != 0:
            for ent in self.B1500As:
                self.SMUs.append(stdObj.ADCFrame(self, self.MainGI, ent['GPIB']))
                self.bottomLayout.addWidget(self.SMUs[-1])

        spItem = QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.layout.addSpacerItem(spItem)


    def initializeB1530A(self):

        self.chns = []
        childs = self.B1530AparWidget.findChildren(QtWidgets.QWidget)
        for child in childs:
            self.B1530AparLayout.removeWidget(child)
            child.close()
            child.destroy()
        
        for n in range(self.B1530AparLayout.count()):
            item = self.B1530AparLayout.itemAt(n)
            if item == QtWidgets.QSpacerItem:
                self.B1530AparLayout.removeItem(item)


        insts = self.Instruments.getInstrumentsByType("B1530A")
        if len(insts) != 0:
            for Inst in insts:
                if Inst != None:
                    inst = Inst['Instrument']
                    if inst != None:
                        self.chns = inst.getChannelIDs()['Channels']
                        widgetLab = QtWidgets.QLabel("%s" %(Inst['GPIB']), self.B1530AparWidget)
                        self.B1530AparLayout.addWidget(widgetLab)

                        for chn in self.chns:
                            widg = WGFMU_ChnInputs(self.B1530AparWidget, Inst['GPIB'], chn, self.WGFMUParameters, self.Configuration)
                            self.B1530AparLayout.addWidget(widg)

                        spItem = QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
                        self.B1530AparLayout.addSpacerItem(spItem)
    
    def updateContent(self): 
        childs = self.bottomWidget.findChildren(QtWidgets.QWidget)
        for child in childs:
            child.update()

        for smu in self.SMUs:
            smu.close()

        for n in range(len(self.SMUs)):
            self.SMUs.pop(0)

        self.B1500As = self.Instruments.getInstrumentsByType("B1500A")
        if len(self.B1500As) != 0:
            for ent in self.B1500As:
                self.SMUs = stdObj.ADCFrame(self, self.MainGI, ent['GPIB'])
                self.topLayout.addWidget(self.SMUs)

    
    def update(self):

        if self.MainGI.isRunning():
            self.setDisabled(True)
        else:
            self.setEnabled(True)

class WGFMU_ChnInputs(QtWidgets.QWidget):

    def __init__(self, parent, GPIB, chnID, parameters, Configuration):

        super().__init__(parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        
        self.layout = QtWidgets.QVBoxLayout(self)
        Labels = ["Operation Mode", "Force Voltage Range", "Measurement Mode", "Measurement Range"]
        
        self.Configuration = Configuration

        self.parameters = parameters
        self.DropDowns = []
        self.LaWid = []
        
        self.LaWid.append(QtWidgets.QLabel("Channel %s" %(chnID), parent))
        #LaWid[-1].setFont(parent.parent.titleFont)
        self.layout.addWidget(self.LaWid[-1])

        curMode = 2000
        for n in range(len(Labels)):
            
            self.LaWid.append(QtWidgets.QLabel(Labels[n], parent))
            self.layout.addWidget(self.LaWid[-1])
            if n == 0:
                self.DropDowns.append(ComboBox(self, GPIB, chnID, "ModeList", parameters['ModeList'], self.Configuration))
                curMode = self.DropDowns[-1].getValue()
            elif n == 1:
                self.DropDowns.append(ComboBox(self, GPIB, chnID, "ForceVoltageRange", parameters['ForceVoltageRange'], self.Configuration))
            elif n == 2:
                self.DropDowns.append(ComboBox(self, GPIB, chnID, "MeasureMode", parameters['MeasureMode'], self.Configuration))
            elif n == 3:
                if self.DropDowns[2].currentText() == 'Voltage':
                    self.DropDowns.append(ComboBox(self, GPIB, chnID, "MeasureVoltageRange", parameters['MeasureVoltageRange'], self.Configuration))
                else:
                    self.DropDowns.append(ComboBox(self, GPIB, chnID, "MeasureCurrentRange", parameters['MeasureCurrentRange'], self.Configuration))

            self.layout.addWidget(self.DropDowns[-1])
        
        spItem = QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.layout.addSpacerItem(spItem)
        self.DropDowns[2].addCommand(adjustMeasRange, (self.DropDowns[2],self.DropDowns[-1],parameters))
        self.DropDowns[0].addCommand(adjustMeasurementMode, (self.DropDowns, self.LaWid[1:], parameters))
        self.setFixedSize(self.sizeHint())

        adjustMeasRange(self.DropDowns[2],self.DropDowns[-1],parameters)
        adjustMeasurementMode(self.DropDowns, self.LaWid[1:], parameters)

    def update(self):

        for wid in self.DropDowns:
            wid.update()

def adjustMeasurementMode(objs, labs, parameters):

    obj = objs[0]
    objChn = objs[2]
    name = obj.currentText()

    if name == "SMU":

        for o, l in zip(objs[1:], labs[1:]):
            o.hide()
            l.hide()

        return None
    else:
        for o, l in zip(objs[1:], labs[1:]):
            o.show()
            l.show()

    objName = "MeasureMode"
    if name == "PG":
        di = {'Voltage': 4000}
        obj.parent().parameters[objName] = di
        ValName = assambleConfigName(obj.GPIB, obj.chnID, objName)
        obj.Configuration.setValue(ValName, di['Voltage'])
    else:
        obj.parent().parameters[objName] = {'Voltage':4000, 'Current':4001}

    items = parameters["MeasureMode"]
    objChn.changeName("MeasureMode", items)

    for n in range(objChn.count()):
        objChn.removeItem(0)
    
    objChn.addItems(items.keys())

    
    objChn.callFunc()

def adjustMeasRange(obj, objChn, parameters):
    
    name = obj.currentText()

    if name == "Voltage":
        key = "MeasureVoltageRange"
    else:
        key = "MeasureCurrentRange"
    items = parameters[key]
    objChn.changeName(key, items)
    for n in range(objChn.count()):
        objChn.removeItem(0)
    
    objChn.addItems(items.keys())

class ComboBox(QtWidgets.QComboBox):

    def __init__(self, parent, GPIB, chnID, name, parameter, Configuration, **kwargs):

        super().__init__(parent)

        self.chnID = chnID
        self.GPIB = GPIB
        self.parameter = parameter
        self.Configuration = Configuration
        self.name = name

        self.addItems(parameter.keys())

        self.update()

        try: 
            command = kwargs["command"]
            self.command = command
        except KeyError:
            self.command = None

        self.activated.connect(self.callFunc)

    def addCommand(self, command, arguments=()):
        self.command = command
        self.arguments = arguments

    def deleteCommand(self):
        self.command = None
        self.arguments = ()

    def update(self):
        
        updName = assambleConfigName(self.GPIB, self.chnID, self.name)
        configValue = self.Configuration.getValue(updName)
        std = {"ModeList": "Fast IV", "ForceVoltageRange": "Auto", "MeasureMode": "Voltage", "MeasureCurrentRange": "10mA", "MeasureVoltageRange": "10V"}
        
        if configValue != None:
            for key, value in self.parameter.items():
                if value == configValue:
                    self.setCurrentText(str(key))
                    break
        else:
            self.setCurrentText(std[self.name])
            ValName = assambleConfigName(self.GPIB, self.chnID, self.name)
            self.Configuration.setValue(ValName, self.parameter[std[self.name]])


    def addItems(self, items):

        super().addItems(items)

        ValName = assambleConfigName(self.GPIB, self.chnID, self.name)
        CurVal = self.Configuration.getValue(ValName)

        if CurVal != None:
            for key, value in self.parameter.items():
                if value == CurVal:
                    break
            
            self.setCurrentText(key)

    def changeName(self, name, parameter):
        self.name = name
        self.parameter = parameter

    def callFunc(self):
        
        ValName = assambleConfigName(self.GPIB, self.chnID, self.name)
        text = self.currentText()
        self.Configuration.setValue(ValName, self.parameter[text])
        

        if self.command != None:
            self.command(*(self.arguments))

    def getValue(self):
        text = self.currentText()
        ret = self.parameter[text]
        return ret

class CheckBox(QtWidgets.QCheckBox):

    def __init__(self, parent, name, Configuration):

        super().__init__(parent)

        self.Configuration = Configuration
        self.name = name
        self.setTristate(False)
        
        self.update()

        self.stateChanged.connect(self.callFunc)
    
    def callFunc(self):

        state = self.isChecked()
        self.Configuration.setValue(self.name, state)

    def update(self):

        state = self.Configuration.getValue(self.name)
        
        if state == None:
            self.Configuration.setValue(self.name, False)
            state = False
        self.setChecked(state)

def assambleConfigName(GPIB, chnID, name):
        ret = "$B1530A$_%s_%s_%s" %(GPIB, chnID, name)
        return ret