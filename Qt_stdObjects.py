"""
This is the standard Frame that introduces the distribution of necessary variables and subclasses for the all Frames
Written by: Karsten Beckmann
Date: 7/25/2018
email: kbeckmann@sunypoly.edu
"""
import sys
from ctypes import *
import collections
import win32api
import win32con
import PlottingRoutines as PR
from matplotlib.backends.backend_agg import FigureCanvasAgg
import threading as th
import queue as qu 
import time as tm
import StdDefinitions as std
import copy as dp
import os as os
import functools
from matplotlib.figure import Figure
from PyQt5 import QtWidgets, QtCore, QtGui
import os as os
import datetime as dt


class RangeFrame(QtWidgets.QWidget):

    def __init__(self, parent, MainGI, Tool):

        self.MainGI = MainGI
        self.Configuration = self.MainGI.Configuration
        self.Inst = self.MainGI.Instruments
        self.Tool = Tool
        super().__init__(parent)
    
        self.layout = QtWidgets.QVBoxLayout(self)
        
        self.GPIBLab = QtWidgets.QLabel("GPIB: %s" %(self.Tool), self)
        self.layout.addWidget(self.GPIBLab)

        self.HS = ADCtype(self, 0)
        self.layout.addWidget(self.HS)

        self.HR = ADCtype(self, 1)
        self.layout.addWidget(self.HR)
        HRwid = self.HR.width()
        
        smus = self.Inst.getModuleInformations(Tool)
        self.SMUs = []

        n = 1
        if smus != None:
            for key, val in smus.items():

                self.SMUs.append(ADCsmu(self, self.Configuration, self.Inst, self.Tool,n))
                self.layout.addWidget(self.SMUs[-1])
                n = n+1

        self.layout.setAlignment(QtCore.Qt.AlignTop|QtCore.Qt.AlignLeft)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

class SMURangeFrame(QtWidgets.QWidget):

    def __init__(self, parent, MainGI, Tool):

        self.MainGI = MainGI
        self.Configuration = self.MainGI.Configuration
        self.Inst = self.MainGI.Instruments
        self.Tool = Tool
        super().__init__(parent)

        self.layout = QtWidgets.QVBoxLayout(self)
        
        self.GPIBLab = QtWidgets.QLabel("GPIB: %s" %(self.Tool), self)
        self.layout.addWidget(self.GPIBLab)

        smus = self.Inst.getModuleInformations(Tool)
        self.SMUs = []

        n = 1
        if smus != None:
            for key, val in smus.items():

                self.SMUs.append(rangeSMU(self, self.Configuration, self.Inst, self.Tool,n))
                self.layout.addWidget(self.SMUs[-1])
                n = n+1

        self.layout.setAlignment(QtCore.Qt.AlignTop|QtCore.Qt.AlignLeft)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

class rangeSMU(QtWidgets.QWidget):
    
    def __init__(self, parent, Configuration, Instruments, Tool, SMU):

        self.Tool = Tool
        self.MainGI = parent.MainGI
        self.Configuration = Configuration
        self.Inst = Instruments
        self.SMU = SMU
        super().__init__(parent)

        desc = self.Inst.getModuleInformation(Tool, SMU)
        for key, val in desc.items():
            self.slot = key
            self.desc = val
            break

        self.layout = QtWidgets.QHBoxLayout(self)

        self.typ = self.Configuration.getValue("$SMURange$_%s_$SMU%d$" %(self.Tool, self.SMU))

        if self.typ == None:
            self.typ = 0
        self.typ = int(self.typ)

        self.SMULabel = QtWidgets.QLabel("SMU %d" %(self.SMU), self)
        self.layout.addWidget(self.SMULabel)

        self.Mode = ADCtypComboBox(self, self.desc, self.typ)
        self.layout.addWidget(self.ADCtype)
        self.layout.setAlignment(QtCore.Qt.AlignTop|QtCore.Qt.AlignLeft)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        self.ADCtype.currentIndexChanged.connect(self.updateType)

    def updateType(self, index):

        ret = self.Inst.setADC(self.MainGI, self.Tool, index, self.SMU)
        
        if ret:

            self.Configuration.setValue("$ADC$_%s_$SMU%d$" %(self.Tool, self.SMU), index)
            self.typ = index
        else:
            self.ADCtype.currentIndexChanged.disconnect()
            self.ADCtype.setCurrentIndex(self.typ)
            self.ADCtype.currentIndexChanged.connect(self.updateType)



class ADCFrame(QtWidgets.QWidget):

    def __init__(self, parent, MainGI, Tool):

        self.MainGI = MainGI
        self.Configuration = self.MainGI.Configuration
        self.Inst = self.MainGI.Instruments
        self.Tool = Tool
        super().__init__(parent)
    
        self.layout = QtWidgets.QVBoxLayout(self)
        
        self.GPIBLab = QtWidgets.QLabel("GPIB: %s" %(self.Tool), self)
        self.layout.addWidget(self.GPIBLab)

        self.HS = ADCtype(self, 0)
        self.layout.addWidget(self.HS)

        self.HR = ADCtype(self, 1)
        self.layout.addWidget(self.HR)
        HRwid = self.HR.width()
        
        smus = self.Inst.getModuleInformations(Tool)
        self.SMUs = []

        n = 1
        if smus != None:
            for key, val in smus.items():

                self.SMUs.append(ADCsmu(self, self.Configuration, self.Inst, self.Tool,n))
                self.layout.addWidget(self.SMUs[-1])
                n = n+1

        self.layout.setAlignment(QtCore.Qt.AlignTop|QtCore.Qt.AlignLeft)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)


class ADCsmu(QtWidgets.QWidget):

    def __init__(self, parent, Configuration, Instruments, Tool, SMU):

        self.Tool = Tool
        self.MainGI = parent.MainGI
        self.Configuration = Configuration
        self.Inst = Instruments
        self.SMU = SMU
        super().__init__(parent)

        desc = self.Inst.getModuleInformation(Tool, SMU)
        for key, val in desc.items():
            self.slot = key
            self.desc = val
            break

        self.layout = QtWidgets.QHBoxLayout(self)

        self.typ = self.Configuration.getValue("$ADC$_%s_$SMU%d$" %(self.Tool, self.SMU))

        if self.typ == None:
            self.typ = 0
        self.typ = int(self.typ)

        self.SMULabel = QtWidgets.QLabel("SMU %d - " %(self.SMU), self)
        self.layout.addWidget(self.SMULabel)

        self.SlotLabel = QtWidgets.QLabel("Slot %d - " %(self.slot), self)
        self.layout.addWidget(self.SlotLabel)

        self.DescLabel = QtWidgets.QLabel("%s   " %(self.desc), self)
        self.layout.addWidget(self.DescLabel)

        self.ADCtype = ADCtypComboBox(self, self.typ)
        self.layout.addWidget(self.ADCtype)
        self.layout.setAlignment(QtCore.Qt.AlignTop|QtCore.Qt.AlignLeft)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        self.ADCtype.currentIndexChanged.connect(self.updateType)

    def updateType(self, index):

        ret = self.Inst.setADC(self.MainGI, self.Tool, index, self.SMU)
        
        if ret:

            self.Configuration.setValue("$ADC$_%s_$SMU%d$" %(self.Tool, self.SMU), index)
            self.typ = index
        else:
            self.ADCtype.currentIndexChanged.disconnect()
            self.ADCtype.setCurrentIndex(self.typ)
            self.ADCtype.currentIndexChanged.connect(self.updateType)


class ADCtype(QtWidgets.QWidget):

    def __init__(self, parent, typ):
        
        super().__init__(parent)

        self.Tool = parent.Tool
        self.MainGI = parent.MainGI
        self.Configuration = parent.Configuration
        self.Inst = parent.Inst

        self.layout = QtWidgets.QHBoxLayout(self)
        self.typ = typ
        self.txt = []     
        self.txt.append("High-speed A/D converter  ")
        self.txt.append("High-resolution A/D converter  ")

        self.Label = QtWidgets.QLabel(self.txt[typ], self)
        self.layout.addWidget(self.Label)

        if typ == 0:
            self.typName = 'HS'
        else:
            self.typName = 'HR'

        self.mode = self.Configuration.getValue("$ADC$_%s_$%s$_$Mode$" %(self.Tool, self.typName))
        if self.mode == None:
            self.mode = 0
        self.mode = int(self.mode)

        self.ADCmode = ADCmode(self, self.mode)
        self.layout.addWidget(self.ADCmode)

        self.N = self.Configuration.getValue("$ADC$_$%s$_$N$" %(self.typName))
        if self.N == None:
            self.N = 1
        self.N = int(self.N)

        self.ADCn = ADCn(self, typ, self.mode)
        self.layout.addWidget(self.ADCn)
        self.layout.setAlignment(QtCore.Qt.AlignTop|QtCore.Qt.AlignLeft)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        self.mode = 0
        self.N = int(self.ADCn.text())

        self.ADCmode.currentIndexChanged.connect(self.updateMode)
        self.ADCn.editingFinished.connect(self.updateN)

    def updateMode(self, index):

        self.mode = index
        try: 
            N = int(self.Configuration.getValue("$ADC$_%s_$%s$_$Mode%d$_$N$" %(self.Tool, self.typName, self.mode)))
        except TypeError:
            N = self.N
        ret = self.Inst.changeADC(self.MainGI, self.Tool, self.typ, self.mode, N)
        
        if ret: 
            self.Configuration.setValue("$ADC$_%s_$%s$_$Mode$" %(self.Tool, self.typName), index)
            self.ADCn.adjustEntry(self.typ, self.mode, N)
            self.mode = index
            self.N = N
        else:
            self.ADCmode.currentIndexChanged.disconnect()
            self.ADCmode.setCurrentIndex(self.mode)
            self.ADCmode.currentIndexChanged.connect(self.updateMode)


    def updateN(self):
        self.N = int(self.ADCn.text())
        ret = self.Inst.changeADC(self.MainGI, self.Tool, self.typ, self.mode, self.N)
        if ret:
            self.Configuration.setValue("$ADC$_%s_$%s$_$Mode%d$_$N$" %(self.Tool, self.typName, self.mode), self.N)
        else:
            old = self.Configuration.getValue("$ADC$_%s_$%s$_$Mode%d$_$N$" %(self.Tool, self.typName, self.mode))
            if old == None:
                self.ADCn.setDefault(self.typ, self.mode)

class ADCn(QtWidgets.QLineEdit):

    def __init__(self, parent, typ, mode=None, default=None):
        
        super().__init__(parent)
        
        self.val = []
        self.val.append([1]*3)
        self.val.append([1]*3)

        self.val[0][0] = "^([1-9][0-9]{0,3})$"
        self.val[0][1] = "^([1-9][0-9]{0,3})$"
        self.val[0][2] = "^0?\d{1,2}|1([0-1]\d|2{0})$"
        self.val[1][0] = "^0?\d{1,2}|1([0-1]\d|2[0-7])$"
        self.val[1][1] = "^0?\d{1,2}|1([0-1]\d|2[0-7])$"
        self.val[1][2] = "^0?\d{1,2}|1([0-1]\d|2{0})$"

        self.default = []
        self.default.append([1]*3)
        self.default.append([1]*3)

        self.default[0][0] = 1
        self.default[0][1] = 1
        self.default[0][2] = 1
        self.default[1][0] = 6
        self.default[1][1] = 3
        self.default[1][2] = 1

        self.mode = 0
        if mode != None:
            self.mode = mode

        ndef = self.default[typ][self.mode]
        if default == None:
            default = ndef

        self.setText(str(default))
        reg_ex = QtCore.QRegExp(self.val[typ][self.mode])
        input_validator = QtGui.QRegExpValidator(reg_ex, self)
        self.setValidator(input_validator)
    
    def getDefault(self, typ, mode):
        return self.default[typ][mode]

    def adjustEntry(self, typ, mode, n=None):
        self.mode = mode
        if n != None:
            self.setText(str(n))
        else:
            self.setText(str(self.default[typ][mode]))
            
        reg_ex = QtCore.QRegExp(self.val[typ][mode])
        input_validator = QtGui.QRegExpValidator(reg_ex, self)
        self.setValidator(input_validator)

    def setDefault(self, typ, mode):
        self.setText(str(self.default[typ][mode]))
        reg_ex = QtCore.QRegExp(self.val[typ][mode])
        input_validator = QtGui.QRegExpValidator(reg_ex, self)
        self.setValidator(input_validator)

class ADCmode(QtWidgets.QComboBox):

    def __init__(self, parent, default=None):
        
        super().__init__(parent)

        self.addItem("Auto mode")
        self.addItem("Manual mode")
        self.addItem("Power line cycle (PLC) mode")

        if default != None:
            self.setCurrentIndex(default)


class ADCtypComboBox(QtWidgets.QComboBox):

    def __init__(self, parent, default=None):
        
        super().__init__(parent)

        self.addItem("High-speed A/D converter")
        self.addItem("High-resolution A/D converter.")

        if default != None:
            self.setCurrentIndex(default)

class SMURangeChangeRule(QtWidgets.QComboBox):

    def __init__(self, parent, default=None):
        
        super().__init__(parent)

        self.addItem("By FULL RANGE", 0)
        self.addItem("Go UP AHEAD",1)
        self.addItem("UP AND DOWN AHEAD",-1)

        if default != None:
            self.setCurrentIndex(default)

class SMUMode(QtWidgets.QComboBox):

    def __init__(self, parent, default=None):
        
        super().__init__(parent)

        self.addItem("AUTO", 0)
        self.addItem("LIMITED",1)
        self.addItem("FIXED",-1)

        if default != None:
            self.setCurrentIndex(default)
            
class SMURange(QtWidgets.QComboBox):

    def __init__(self, parent, desc, default=None):
        
        super().__init__(parent)

        self.enable()

        if default != None:
            self.setCurrentIndex(default)

    def enable(self, desc):
        for n in self.count():
            self.removeItem(0)
        self.setEditable(True)

        dec = [1,10,100]
        eng = []
        eng.extend(["nA","uA","mA"])
        li = []
        if desc == "HRSMU":
            li = ["10pA", "100pA"]
        elif desc == "HRSMU/ASU":
            li = ["1pA","10pA","100pA"]

        for e in eng:
            for d in dec:
                li.append("%d%s" %(d,e))
        
        for n, l in enumerate(li):
            self.addItem(l, n+8)

    def disable(self, desc):
        for n in self.count():
            self.removeItem(0)
        self.setEditable(False)

class stdFrame(QtWidgets.QWidget):

    def __init__(self, parent, MainGI, width=None, height=None, threads=None, **kwargs):

        
        super().__init__(parent)
        
        self.MainGI = MainGI
        self.eChar = self.MainGI.getEChar()
        self.Instruments = self.MainGI.getInstruments()
        self.threads = threads
        self.Configuration = self.MainGI.getConfiguration()
        self.ExecThread = None

        if isinstance(width, int):
            self.width = width
            super().setMinimumWidth(self.width)
        if isinstance(height, int):
            self.height = height
            super().setMinimumHeight(self.height)
        
        qFont = self.font()
        qFont.setPointSize=qFont.pointSize()*1.2
        qFont.setBold(True)
        self.titleFont = qFont

    def update(self):
        return None

    def __getattr__(self, item):
        return getattr(self.parent(), item)

class stdScrollFrame(QtWidgets.QScrollArea):

    def __init__(self, parent, MainGI, width=None, height=None, threads=None):

        self.MainGI = MainGI
        self.eChar = self.MainGI.getEChar()
        self.Instruments = self.MainGI.getInstruments()
        self.threads = threads
        self.Configuration = self.MainGI.getConfiguration()
        self.ExecThread = None
        self.width = width
        self.height = height
        
        super().__init__(parent)

        if isinstance(width, int):
            self.width = width
            super().setMinimumWidth(self.width)
        if isinstance(height, int):
            self.height = height
            super().setMinimumHeight(self.height)

        self.setFixedWidth(self.MainGI.getWindowWidth())
        self.setFixedHeight(self.MainGI.getWindowHeight())
        
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)

        qFont = self.font()
        qFont.setPointSize=qFont.pointSize()*1.2
        qFont.setBold(True)
        self.titleFont = qFont

    def update(self):
        return None

    def __getattr__(self, item):
        return getattr(self.parent(), item)
        
class stdFrameGrid(stdFrame):

    def __init__(self, parent, MainGI, columns, rows, width, height, cell=False, **kwargs):
        
        
        if not cell:
            self.ColumnWidth=int(width/columns)
            self.RowHeight=int(height/rows)
            self.width = width
            self.height= height
        else:
            self.ColumnWidth=width
            self.RowHeight=height
            self.width = self.ColumnWidth * columns
            self.height = self.RowHeight * rows

        super().__init__(parent, MainGI, self.width, self.height, **kwargs)

        self.defColor = MainGI.defColor

        self.layout = QtWidgets.QGridLayout(self)
        
        for n in range(columns):
            self.layout.setColumnMinimumWidth(n+1, self.ColumnWidth)
        
        for n in range(rows):
            self.layout.setRowMinimumHeight(n+1, self.RowHeight)

    def __getattr__(self, item):
        return getattr(self.parent(), item)
    
    def getLayout(self):
        return self.layout
    
    def getColumnWidth(self):
        return self.ColumnWidth

    def getRowHeight(self):
        return self.RowHeight

    def addWidget(self, widget, row=1, column=1, columnspan=1, rowspan=1, alignment=None):
        
        if alignment == None:
            self.layout.addWidget(widget, row, column, rowspan, columnspan)
        else:
            self.layout.addWidget(widget, row, column, rowspan, columnspan, alignment)


class Label(QtWidgets.QLabel):

    def __init__(self, text, parent, **kwargs):

        super().__init__(text, parent)

        if "alignment" in kwargs:
            self.setAlignment(kwargs['alignment'])


class TabWidget(QtWidgets.QTabWidget):

    def __init__(self, parent, **kwargs):

        super().__init__(parent)

        if "alignment" in kwargs:
            self.setAlignment(kwargs['alignment'])

class Checkbutton(QtWidgets.QCheckBox):
    
    def __init__(self, parent, MainGI, valueName, *args, **kwargs):
        
        '''
            parent: parent widget
            Configuration: private config class 
            valueName: Value name associated with configuration class 
            *args: arguments from ttk.Checkbutton
            **kwargs: keyword arguments form ttk.Checkbutton

            The validatecommand is automatically created, please use the writeFunc
        '''

        super().__init__(parent)

        self.MainGI = MainGI
        self.Configuration = MainGI.Configuration
        
        self.valueName = valueName
        self.parent = parent

        self.AddCommand = None

        if 'command' in kwargs:
            self.AddCommand = kwargs['command']

        initValue = self.Configuration.getValue(valueName)
        self.setVariable(initValue)
       
        self.MainGI.addWidgetVariables(self, self.valueName)
        self.clicked.connect(self.callFunc)
    
    def getVariable(self):
        return self.isChecked()

    def setVariable(self, value): 
        try: 
            value = bool(value)
        except:
            value = None

        if value != None:
            self.setChecked(value)
        
    def callFunc(self):
        self.Configuration.setValue(self.valueName, self.getVariable())
        if self.AddCommand != None:
            self.AddCommand()
        ret = True
        return ret

class ComboBox(QtWidgets.QComboBox):

    def __init__(self, parent, MainGI, valueName, items, Type=str, width=None, **kwargs):
        '''
            parent: parent widget
            Configuration: private config class 
            valueName: Value name associated with configuration class 
            *args: arguments from ttk.OptionMenu
            **kwargs: keyword arguments form ttk.OptionMenu

        '''
        
        super().__init__()

        self.parent = parent

        self.MainGI = MainGI
        self.Configuration = MainGI.Configuration
        self.valueName = valueName
        self.parent = parent
        self.width = width
        self.Type = Type

        self.AddCommand = None
        if 'command' in kwargs:
            self.AddCommand = kwargs['command']
        kwargs['command'] = self.callFunc
        
        if "alignment" in kwargs:
            self.setAlignment(kwargs['alignment'])

        
        self.update(items)
        initValue = self.Configuration.getValue(valueName)

        self.setVariable(initValue)
        self.MainGI.addWidgetVariables(self, self.valueName)

        if self.width != None:
            self.setFixedWidth(self.width)
        
        self.currentIndexChanged.connect(self.callFunc)

    def getVariable(self):
        return self.Type(self.currentText)

    def setVariable(self, value):
        index = self.findText(str(value))
        self.setCurrentIndex(index)
    
    def callFunc(self, index):
        value = self.itemText(index)
        try:
            self.Configuration.setValue(self.valueName, self.Type(value))
        except ValueError:
            self.MainGI.WriteError("Qt_Config - %s had value '%s' with type %s" %(self.valueName, value, self.Type))

        if self.AddCommand != None:
            self.AddCommand(value)
        ret = True
        return ret
    
    def update(self, newList=[]):
        initValue = self.Configuration.getValue(self.valueName)
        if len(newList) == 0:
            newList.append("")
        self.addItems([str(l) for l in newList])
        self.setVariable(initValue)
        if self.width != None:
            self.setFixedWidth(self.width)



class PushButton(QtWidgets.QPushButton):

    def __init__(self, text, parent, *args, **kwargs):
    
        super().__init__(text, parent)

        if "minimumWidth" in kwargs:
            self.setMinimumWidth(kwargs["minimumWidth"])
        
        if "command" in kwargs:
            self.clicked.connect(kwargs["command"])

        if "alignment" in kwargs:
            self.setAlignment(kwargs['alignment'])
        
        if "sizePolicy" in kwargs:
            self.setSizePolicy(kwargs['sizePolicy'][0], kwargs['sizePolicy'][1])


class folderButton(QtWidgets.QPushButton):

    def __init__(self, parent, MainGI, valueName, NameLength=30, *args, **kwargs):
        
        '''
            parent: parent widget
            Configuration: private config class 
            valueName: Value name associated with configuration class 
            *args: arguments from ttk.Button
            **kwargs: keyword arguments form ttk.Button
        '''
        super().__init__(parent)
        self.NameLength = NameLength
        self.MainGI = MainGI
        self.Configuration = MainGI.Configuration
        
        self.valueName = valueName
        self.parent = parent
        
        if 'command' in kwargs:
            self.AddCommand = kwargs['command']
        else: 
            self.AddCommand = None
            
        kwargs['command'] = self.callFunc
        
        if "alignment" in kwargs:
            self.setAlignment(kwargs['alignment'])
            
        if "sizePolicy" in kwargs:
            self.setSizePolicy(kwargs['sizePolicy'][0], kwargs['sizePolicy'][1])

        initValue = str(self.Configuration.getValue(valueName))

        self.Type=str

        self.setVariable(initValue)
        self.MainGI.addWidgetVariables(self, self.valueName)
        self.clicked.connect(self.callFunc)
        self.setCheckable(True)

        
    def getVariable(self):
        return str(self.vairable)

    def setVariable(self, value):
        if len(str(value)) > self.NameLength: 
            self.variable = "...%s" %(value[-self.NameLength:])
        elif value == "":
            self.variable = "Browse"
        else:
            self.variable = value
        
        self.setText(self.variable)

    def callFunc(self):
        Folder = self.Configuration.getValue(self.valueName)
        if Folder == "":
            initDir = os.getcwd()
        else:
            initDir, foldername = os.path.split(Folder)

        options = QtWidgets.QFileDialog.ShowDirsOnly
        options |= QtWidgets.QFileDialog.DontResolveSymlinks

        foldername = QtWidgets.QFileDialog.getExistingDirectory(self,"Open Directory", initDir, options=options)
        
        if not foldername == "":
            self.Configuration.setValue(self.valueName, foldername)
            self.setVariable(foldername)

            if self.AddCommand != None:
                self.AddCommand()
            ret = True
            return ret 

class fileButton(QtWidgets.QPushButton):

    def __init__(self, parent, MainGI, valueName, NameLength=30, *args, **kwargs):
        
        '''
            parent: parent widget
            Configuration: private config class 
            valueName: Value name associated with configuration class 
            *args: arguments from ttk.Button
            **kwargs: keyword arguments form ttk.Button
        '''
        self.n = 1
        super().__init__(parent)
        self.NameLength = NameLength
        self.MainGI = MainGI
        self.Configuration = MainGI.Configuration
        self.fileFormat = None
        self.MaxTextLength = 33
        self.disFileName = True

        self.subFolder = None
        if "subFolder" in kwargs.keys():
            self.subFolder = kwargs['subFolder']
        
        self.valueName = valueName
        self.parent = parent
        
        self.setMinimumSize(1,1)

        self.AddCommand = None
        if 'command' in kwargs:
            self.AddCommand = kwargs['command']
            
        kwargs['command'] = self.callFunc
        
        if "alignment" in kwargs:
            self.setAlignment(kwargs['alignment'])
        
        if 'fileFormat' in kwargs:
            self.fileFormat = kwargs['fileFormat']
            
        if "sizePolicy" in kwargs:
            self.setSizePolicy(kwargs['sizePolicy'][0], kwargs['sizePolicy'][1])
        initValue = str(self.Configuration.getValue(valueName))
        self.Type = str

        self.setVariable(initValue)
        self.MainGI.addWidgetVariables(self, self.valueName)
        self.clicked.connect(self.callFunc)

    def setMaximumTextLengthDefault(self):
        self.MaxTextLength = 33

    def setMaximumTextLength(self, n):
        try:
            self.MaxTextLength = int(n)
        except ValueError:
            None

    def displayFileName(self):
        self.disFileName = True
    
    def displayTextName(self):
        self.disFileName = False

    def getVariable(self):
        return str(self.variable)

    def setVariable(self, value):
        if len(str(value)) > self.MaxTextLength: 
            self.variable = "...%s" %(value[-self.NameLength:])
        elif value.strip() == "" or value.strip() == 'None':
            self.variable = "Browse"
        else:
            self.variable = value
        if self.disFileName:
            self.setText(self.variable)
        self.n+=1

    def callFunc(self):

        file = self.Configuration.getValue(self.valueName)
        
        try:
            initDir, fileName = os.path.split(file)
            if initDir == "":
                raise TypeError()

        except TypeError:

            initDir = os.getcwd()

            if self.subFolder != None:
                fullPath = "%s/%s" %(os.getcwd(), self.subFolder)
                if os.path.exists(self.subFolder):
                    initDir = self.subFolder
                elif os.path.exists(fullPath):
                    initDir = fullPath
        
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog

        ff = "All Files (*)"
        if self.fileFormat != None:
            if isinstance(self.fileFormat, list):
                for ent in self.fileFormat:
                    ff = "%s;;%s" %(ent, ff)
            else:
                ff = "%s;;%s" %(self.fileFormat, ff)

        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Select file", initDir,ff, options=options)
        
        if not fileName == "" and not fileName == None:
            self.Configuration.setValue(self.valueName, fileName)
            self.setVariable(fileName)

            if self.AddCommand != None:
                self.AddCommand()
            ret = True
            return ret


class saveButton(QtWidgets.QPushButton):

    def __init__(self, parent, MainGI, valueName, NameLength=30, *args, **kwargs):
        
        '''
            parent: parent widget
            Configuration: private config class 
            valueName: Value name associated with configuration class 
            *args: arguments from ttk.Button
            **kwargs: keyword arguments form ttk.Button
        '''
        self.n = 1
        super().__init__(parent)
        self.NameLength = NameLength
        self.MainGI = MainGI
        self.Configuration = MainGI.Configuration
        self.fileFormat = None
        self.MaxTextLength = 33
        self.disFileName = True
        
        self.valueName = valueName
        self.parent = parent
        
        self.setMinimumSize(1,1)

        if 'command' in kwargs:
            self.AddCommand = kwargs['command']
        else: 
            self.AddCommand = None
            
        kwargs['command'] = self.callFunc
        
        if "alignment" in kwargs:
            self.setAlignment(kwargs['alignment'])
        
        if 'fileFormat' in kwargs:
            self.fileFormat = kwargs['fileFormat']
            
        if "sizePolicy" in kwargs:
            self.setSizePolicy(kwargs['sizePolicy'][0], kwargs['sizePolicy'][1])
        initValue = str(self.Configuration.getValue(valueName))
        self.Type = str

        self.setVariable(initValue)
        self.MainGI.addWidgetVariables(self, self.valueName)
        self.clicked.connect(self.callFunc)

    def setMaximumTextLengthDefault(self):
        self.MaxTextLength = 33

    def setMaximumTextLength(self, n):
        try:
            self.MaxTextLength = int(n)
        except ValueError:
            None

    def displayFileName(self):
        self.disFileName = True
    
    def displayTextName(self):
        self.disFileName = False

    def getVariable(self):
        return str(self.variable)

    def setVariable(self, value):
        if len(str(value)) > self.MaxTextLength: 
            self.variable = "...%s" %(value[-self.NameLength:])
        elif value.strip() == "" or value.strip() == 'None':
            self.variable = "Browse"
        else:
            self.variable = value
        if self.disFileName:
            self.setText(self.variable)
        self.n+=1

    def callFunc(self):
        DieFile = self.Configuration.getValue(self.valueName)

        try:
            initDir, fileName = os.path.split(DieFile)
        except TypeError:
            initDir = os.getcwd()
        
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog

        ff = "All Files (*)"
        if self.fileFormat != None:
            if isinstance(self.fileFormat, list):
                for ent in self.fileFormat:
                    ff = "%s;;%s" %(ent, ff)
            else:
                ff = "%s;;%s" %(self.fileFormat, ff)

        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save file", initDir,ff, options=options)
        
        if not fileName == "" and not fileName == None:
            self.Configuration.setValue(self.valueName, fileName)
            self.setVariable(fileName)

            if self.AddCommand != None:
                self.AddCommand()
            ret = True
            return ret

class Entry(QtWidgets.QLineEdit):

    def __init__(self, parent, MainGI, valueName, validateNumbers=None, maxLength=None, *args, **kwargs):
        '''
            Configuration: private config class 
            valueName: Value name associated with configuration class 
            The validatecommand is automatically created, please use the validateNumbers
            Maxlength of the Entrybox
            *args: arguments from ttk.OptionMenu
            **kwargs: keyword arguments form ttk.OptionMenu
        '''
        self.parent = parent 
        self.MainGI = MainGI

        
        super().__init__(parent)

        try:
            self.maxLen = int(maxLength)
            self.setMaxLength(self.maxLen)
        except:
            self.maxLen = None

        self.valueName = valueName
        self.Configuration = self.MainGI.Configuration
        self.Instruments = self.MainGI.Instruments

        initValue = self.Configuration.getValue(self.valueName)
        
        if not "width" in kwargs:
            kwargs['width'] = int(1)

        if "alignment" in kwargs:
            self.setAlignment(kwargs['alignment'])
        
        self.AddCommand= None
        if "command" in kwargs:
            self.AddCommand = kwargs['command']
            
        if "sizePolicy" in kwargs:
            self.setSizePolicy(kwargs['sizePolicy'][0], kwargs['sizePolicy'][1])
            
        if "type" in kwargs:
            self.Type = kwargs['type']
        else:
            self.Type = type(initValue)

            
        if "default" in kwargs:
            self.default = kwargs['default']
            
        self.setMinimumWidth(kwargs['width'])

        if validateNumbers != None:
            self.validateNumbers = str(validateNumbers)
            regEx = QtCore.QRegularExpression(self.validateNumbers)
            validator = QtGui.QRegularExpressionValidator(regEx, self)
            self.setValidator(validator)
        else:
            self.validateNumbers = None

        try:
            initValue = self.Type(initValue)
        except TypeError:
            initValue = self.default
        

        self.setVariable(initValue)

        self.MainGI.addWidgetVariables(self, self.valueName)
        
    def getVariable(self):
        return self.text()

    def setVariable(self, value):
        
        if self.Type == float:
            self.variable = float(value)
        elif self.Type == bool:
            self.variable = bool(value)
        elif self.Type == int:
            self.variable = int(value)
        else:
            self.variable = str(value)
        self.setText(str(value))

    def writeError(self, error):
        self.parent.writeError(error)

    def focusOutEvent(self, event):

        ConfigValue = self.Configuration.getValue(self.valueName)

        CurContent = self.text()

        try:
            SucChange = self.Configuration.setValue(self.valueName, self.Type(CurContent))
            if SucChange:
                if self.AddCommand != None:
                    self.AddCommand()
            else:
                self.setText(str(ConfigValue))

        except ValueError:
            self.setText(str(ConfigValue))

        super().focusOutEvent(event)

class ErrorLog(QtWidgets.QListWidget):

    def __init__(self, parent, Name, MainGI=None, SaveObj=True, maxEntries=100, **kwargs):

        super().__init__(parent)

        self.parent = parent
        self.CurrentList = []
        self.maxEntries = maxEntries
        self.curList = []
        self.Name = Name
        self.LogFile = "%s.txt" %(self.Name)
        
        try:
            os.remove(self.LogFile)
        except FileNotFoundError:
            None

        self.f = None

        self.MainGI = MainGI
        self.SaveObj = SaveObj
        self.Configuration = self.MainGI.Configuration

        if "alignment" in kwargs:
            self.setAlignment(kwargs['alignment'])
            
        if "sizePolicy" in kwargs:
            self.setSizePolicy(kwargs['sizePolicy'][0], kwargs['sizePolicy'][1])
            
        self.MainGI.ErrorFrames.append(self)
        self.update()


    def saveToFile(self):
        if isinstance(self.SaveObj, bool):
            save = self.SaveObj
        elif isinstance(self.SaveObj, str):
            save = self.Configuration.getValue(self.SaveObj)
            if save == None:
                save = False
        else:
            save = False
        
        return save

    def add(self, error):
        self.insertItem(0,str(error))
        
        if self.saveToFile:
            if self.f == None:
                
                self.checkFileSize()

                c = True
                self.f = open(self.LogFile, "a")
            date = dt.datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
            self.f.write("%s - %s\n" %(date, error))
            if c:
                self.f.close()
                self.f = None

            if self.count() > self.maxEntries: 
                item = self.takeItem(self.count()-1)
                item = None
    
    def addFromQueue(self, queue):
        self.f = open(self.Logfile, "a")
        while not queue.empty():
            error = queue.get()
            self.add(error)
        self.f.close()
        self.f = None
    
    def update(self):
        newList = self.Configuration.getErrorList()
        self.clear()
        for entry in newList:
            self.add(entry)

        
    def checkFileSize(self):
        try:
            size = self.Configuration.getValue("MaxErrorLogFileSize")
            while size < os.path.getsize(self.LogFile):

                with open(self.LogFile, "r+", encoding = "utf-8") as file:

                    # Move the pointer (similar to a cursor in a text editor) to the end of the file
                    file.seek(0, os.SEEK_END)

                    # This code means the following code skips the very last character in the file -
                    # i.e. in the case the last line is null we delete the last line
                    # and the penultimate one
                    pos = file.tell() - 1

                    # Read each character in the file one at a time from the penultimate
                    # character going backwards, searching for a newline character
                    # If we find a new line, exit the search
                    while pos > 0 and file.read(1) != "\n":
                        pos -= 1
                        file.seek(pos, os.SEEK_SET)

                    # So long as we're not at the start of the file, delete all the characters ahead
                    # of this position
                    if pos > 0:
                        file.seek(pos, os.SEEK_SET)
                        file.truncate()
                                
        except FileNotFoundError:
            return True

class InfoLog(QtWidgets.QListWidget):

    def __init__(self, parent, Name, MainGI=None, SaveObj=True, maxEntries=100, **kwargs):
    
        super().__init__(parent)

        self.parent = parent
        self.Name = Name
        self.CurrentList = []
        self.maxEntries = maxEntries
        self.curList = []

        self.MainGI = MainGI
        self.Configuration = self.MainGI.Configuration
        SaveObj = self.Configuration.getValue("InfoLogSave")
        if SaveObj == None:
            self.SaveObj = SaveObj
        self.LogFile = "%s.txt" %(self.Name)

        try:
            os.remove(self.LogFile)
        except FileNotFoundError as e:
            print("logNotDeleted", e)
            
            None
        self.f = None

        if "alignment" in kwargs:
            self.setAlignment(kwargs['alignment'])
            
        if "sizePolicy" in kwargs:
            self.setSizePolicy(kwargs['sizePolicy'][0], kwargs['sizePolicy'][1])
            
        self.MainGI.LogFrame.append(self)
        self.update()

    def saveToFile(self):
        if isinstance(self.SaveObj, bool):
            save = self.SaveObj
        elif isinstance(self.SaveObj, str):
            save = self.Configuration.getValue(self.SaveObj)
            if save == None:
                save = False
        else:
            save = False
        
        return save

    def add(self, error):
        self.insertItem(0,str(error))

        if self.saveToFile:
            
            self.checkFileSize()

            if self.f == None:
                c = True
                
                for n in range(10):
                    try:
                        self.f = open(self.LogFile, "a")
                        break
                    except PermissionError as e:
                        self.Configuration.ErrorQueue.put("InfoLog Error: %s." %(e))
                        tm.sleep(0.01)
                    if n == 9:
                        self.Configuration.ErrorQueue.put("InfoLog Error: Log not written.")
            
            date = dt.datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
            self.f.write("%s - %s\n" %(date, error))
            if c:
                self.f.close()
                self.f = None
            
        if self.count() > self.maxEntries: 
            item = self.takeItem(self.count()-1)
            item = None
    
    def checkFileSize(self):
        try:
            size = self.Configuration.getValue("MaxInfoLogFileSize")
            while size < os.path.getsize(self.LogFile):

                with open(self.LogFile, "r+", encoding = "utf-8") as file:

                    # Move the pointer (similar to a cursor in a text editor) to the end of the file
                    file.seek(0, os.SEEK_END)

                    # This code means the following code skips the very last character in the file -
                    # i.e. in the case the last line is null we delete the last line
                    # and the penultimate one
                    pos = file.tell() - 1

                    # Read each character in the file one at a time from the penultimate
                    # character going backwards, searching for a newline character
                    # If we find a new line, exit the search
                    while pos > 0 and file.read(1) != "\n":
                        pos -= 1
                        file.seek(pos, os.SEEK_SET)

                    # So long as we're not at the start of the file, delete all the characters ahead
                    # of this position
                    if pos > 0:
                        file.seek(pos, os.SEEK_SET)
                        file.truncate()
                                
        except FileNotFoundError:
            return True



    def addFromQueue(self, queue):
        self.f = open(self.Logfile, "a")
        while not queue.empty():
            error = queue.get()
            self.add(error)
        self.f.close()
        self.f = None

    def update(self):
        newList = self.Configuration.getLogList()
        self.clear()
        self.curList = newList
        for entry in newList:
            self.add(entry)

class Table(QtWidgets.QTableWidget):

    def __init__(self, parent, MainGI, columns, rows, width=None, height=None, horHeader=None, vertHeader=None, content=None, **kwargs):
        
        super().__init__(parent)
        self.MainGI = MainGI
        self.columns = columns
        self.rows = rows
        self.width = width
        self.height = height
        self.content = content

        #self.resize(width, height)
        self.setColumnCount(columns)
        self.setRowCount(rows)

        if horHeader != None:
            for n in range(len(horHeader)):
                qtwi = QtWidgets.QTableWidgetItem(horHeader[n],QtWidgets.QTableWidgetItem.Type)
                self.setHorizontalHeaderItem(n, qtwi)

        if vertHeader != None:
            for n in range(len(vertHeader)):
                qtwi = QtWidgets.QTableWidgetItem(vertHeader[n],QtWidgets.QTableWidgetItem.Type)
                self.setVerticalHeaderItem(n, qtwi)

        #self.Table = QtWidgets.QTableWidget(self)
        #self.Table.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        self.font=None
        if 'font' in kwargs.keys():
            self.font = kwargs['font']

        if self.content != None:
            self.writeTable(self.content)

            
    def __getattr__(self, item):
        return getattr(self.parent(), item)

    def writeRow(self, row, content):
        n = 0
        for c in content:
            item = QtWidgets.QTableWidgetItem(str(c))
            if self.font != None:
                item.setFont(self.font)
            self.setItem(int(row),int(n), item)
            n = n + 1

    def writeColumn(self, column, content):

        n = 0
        for c in content:
            item = QtWidgets.QTableWidgetItem(str(c))
            if self.font != None:
                item.setFont(self.font)
            self.setItem(int(n),int(column), item)
            n=n+1

    def writeTable(self, content):

        n = 0
        for row in content:
            m = 0
            for st in row:
                item = QtWidgets.QTableWidgetItem(str(st))
                if self.font != None:
                    item.setFont(self.font)
                self.setItem(int(n),int(m), item)
                m = m + 1
            n = n + 1

def ListToQstring(List):
    
    if len(List) > 0:
        l = ""
        for n in range(len(List)):
            l = "%s%s;" %(l, List[n])
        return l
    else:
        return QtCore.QString("")
