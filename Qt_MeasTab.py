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
import copy as cp
import StdDefinitions as std
import copy as dp
import os as os
import pickle as pk
import functools
from matplotlib.figure import Figure
import matplotlib.backends as qtagg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from PyQt5 import QtWidgets, QtCore, QtGui
import Qt_stdObjects as stdObj

import matplotlib._pylab_helpers as plotHelper

class MainMeasurementFrame(QtWidgets.QWidget):

    def __init__(self, parent, MainWindow, width, height, *args, **kw):
        
        super().__init__(parent)

        self.MainWindow = MainWindow
        self.Instruments = self.MainWindow.getInstruments()
        self.Configuration = self.MainWindow.getConfiguration()
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        
        self.LoadSaveWidget = QtWidgets.QWidget(self)
        self.layout.addWidget(self.LoadSaveWidget, 0)
        self.LoadSaveLayout = QtWidgets.QHBoxLayout(self.LoadSaveWidget)
        self.LoadSaveLayout.setContentsMargins(0,0,0,0)
        self.LoadSaveLayout.setSpacing(0)
        self.SaveBut = QtWidgets.QPushButton('Save', self)
        self.SaveBut.clicked.connect(self.SaveMeasurementBut)
        self.LoadSaveLayout.addWidget(self.SaveBut, 0)
        self.LoadBut = QtWidgets.QPushButton('Load', self)
        self.LoadBut.clicked.connect(self.LoadMeasurementBut)
        self.LoadSaveLayout.addWidget(self.LoadBut, 0)
        
        self.DelBut = QtWidgets.QPushButton('Delete', self)
        self.DelBut.clicked.connect(self.DelMeasurementBut)
        self.LoadSaveLayout.addWidget(self.DelBut, 0)

        
        self.ClearBut = QtWidgets.QPushButton('Clear', self)
        self.ClearBut.clicked.connect(self.clearMeasurement)
        self.LoadSaveLayout.addWidget(self.ClearBut, 0)


        LSHeight = self.LoadSaveWidget.height()
        MeasHeight = height-LSHeight
        self.MeasFrame = MeasurementFrame(self, self.MainWindow, width, MeasHeight)
        self.layout.addWidget(self.MeasFrame)


        initMeas = self.Configuration.getValue("InititalMeasurement")
        
        if initMeas != None:
            self.folder = "%s/Measurements" %(self.MainWindow.getHomeDirectory())
            if os.path.exists(self.folder):
                self.LoadMeasurement(initMeas)
        

    def SaveMeasurement(self, fileName):
        self.MeasSaveWindow.close()
        Measurements = self.MeasFrame.getMeasurements()

        self.MainWindow.setEnabled(True)

        folder = "%s/Measurements" %(self.MainWindow.getHomeDirectory())
        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except FileExistsError:
                self.MainWindow.WriteError("Could not create Measurement folder (%s)." %(folder))
                return False

        fileName = "%s/%s.mfs" %(folder, fileName)
        skip = True
        for entry in Measurements:
            if entry["Name"].lower() != "select":
                skip = False
        if not skip:
            try:
                f = open(fileName, 'wb')
            except (ValueError,TypeError) as e: 
                self.MainWindow.WriteError("Could not save Measurement file (%s)." %(e))
                return False
            pk.dump(Measurements, f, protocol=pk.HIGHEST_PROTOCOL)
            f.close()

            self.Configuration.setValue("InititalMeasurement", fileName)
        
        return True
    
    def clearMeasurement(self):

        self.MeasFrame.clearMeasurement()

    def getFileItems(self, folder, allMeas=False):

        if os.path.exists(folder):
            files = []
            for f in os.listdir(folder):

                if f.endswith(".mfs"):

                    fname = "%s\%s" %(folder, f)
                    fobj = open(fname, "rb")
                    measurements = pk.load(fobj)
                    if allMeas:
                        files.append(f[:-4])
                    else:
                        if self.checkForTools(measurements):
                            files.append(f[:-4])

            if files == []:
                return None

            return files

        return None

    def SaveMeasurementBut(self):
        
        self.folder = "%s\Measurements" %(self.MainWindow.getHomeDirectory())
        fileItems = self.getFileItems(self.folder, True)

        self.MainWindow.setEnabled(False)
        height = self.MainWindow.size().height()*0.6
        width = self.MainWindow.size().width()*0.4
        self.MeasSaveWindow = MeasurementSaveWindow(self.MainWindow, self, fileItems, width=width, height=height)
        self.MeasSaveWindow.show()

    def DelMeasurementBut(self):

        self.folder = "%s\Measurements" %(self.MainWindow.getHomeDirectory())
        fileItems = self.getFileItems(self.folder, True)

        if fileItems != None:
            height = self.MainWindow.size().height()*0.6
            width = self.MainWindow.size().width()*0.4
            self.MainWindow.setEnabled(False)
            self.MeasLoadWindow = MeasurementDeleteWindow(self.MainWindow, self, fileItems, width=width, height=height)
            self.MeasLoadWindow.show()
        else:
            msg = "No Measurement Files available in %s." %(self.folder)
            msgBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Delete Measurement", msg, QtWidgets.QMessageBox.Close, self)
            msgBox.exec()
    
    
    def LoadMeasurementBut(self):

        self.folder = os.path.join(self.MainWindow.getHomeDirectory(), "Measurements")
        fileItems = self.getFileItems(self.folder)

        if fileItems != None:
            height = self.MainWindow.size().height()*0.6
            width = self.MainWindow.size().width()*0.4
            self.MainWindow.setEnabled(False)
            self.MeasLoadWindow = MeasurementLoadWindow(self.MainWindow, self, fileItems, width=width, height=height)
            self.MeasLoadWindow.show()
        else:
            msg = "No Measurement Files available in %s." %(self.folder)
            msgBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Load Measurement", msg, QtWidgets.QMessageBox.Close, self)
            msgBox.exec()
    
    def LoadMeasurement(self, measName):
        
        measFile = os.path.join(self.folder, "%s.mfs" %(measName))
        try:
            f = open(measFile, "rb")
        except OSError as e:
            self.MainWindow.WriteError("Error loading Measurement file %s." %(measName))
            self.MainWindow.setEnabled(True)
            try:
                self.MeasLoadWindow.close()
            except AttributeError:
                None
            return None

        Measurements = pk.load(f)
        self.MeasFrame.loadMeasurement(Measurements) 
        try:
            self.MeasLoadWindow.close()
        except AttributeError:
            None
        self.Configuration.setValue("InititalMeasurement", measName)
        self.MainWindow.setEnabled(True)

        
    def DeleteMeasurement(self, measNames):
        
        for m in measNames:                
            measFile = os.path.join(self.folder, "%s.mfs" %(m))
            os.remove(measFile)
    
    def checkForTools(self, Measurements):
        avail = True
        tools = self.MainWindow.AvailableInstruments
        usedTools = []
        for m in Measurements:
            det = self.Configuration.getMeasurementDetail(m['Name'], m['Folder'])
            
            for t in det['Tools']:
                if not t in usedTools: 
                    usedTools.append(t)

        availTools = ['none']
        for key, value in tools.items():
            if value:
                availTools.append(key.strip())
        
        for t in usedTools:
            if not t.strip() in availTools:
                return False

        return avail

    def __getattr__(self, name):
        return getattr(self.MeasFrame,name)

class MeasurementFrame(QtWidgets.QScrollArea):
    
    # Measurement Frame embedded into the main window
    # requires the following parameters:
    # 1. parent window
    # 2. MainWindow (for interactions)
    # 3. width
    # 4. height

    def __init__(self, parent, MainWindow, width, height, *args, **kw):
        
        super().__init__(parent)
        self.MainWindow = MainWindow
        self.Instruments = self.MainWindow.getInstruments()
        self.Configuration = self.MainWindow.getConfiguration()
        self.Measurements = []
        
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.ScrollLayout = QtWidgets.QHBoxLayout(self)
        self.ScrollLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.Frame = QtWidgets.QWidget(self)
        self.Frame.setMinimumWidth(1)
        pal = QtGui.QPalette()
        pal.setColor( QtGui.QPalette.Background, QtCore.Qt.blue)
        self.Frame.setAutoFillBackground(True)
        
        self.Frame.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.ScrollLayout.addWidget(self.Frame)
        self.ScrollLayout.setContentsMargins(0,0,0,0)
        self.ScrollLayout.setSpacing(0)

        self.layout = QtWidgets.QHBoxLayout(self.Frame)
        self.layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.layout.setContentsMargins(1,1,1,1)
        self.layout.setSpacing(1)
        self.setWidget(self.Frame)

        self.Measurements.append(Measurement(self, self.MainWindow, self.Configuration, self.Instruments, self))
        self.layout.addWidget(self.Measurements[-1])
        
        self.FixWidth = self.Frame.sizeHint().width()+10
        self.Frame.setFixedWidth(self.FixWidth)
        self.Measurements[-1].setPalette(pal)

    def loadMeasurement(self, measParam):
        
        for m in range(len(self.Measurements)):
            self.layout.removeWidget(self.Measurements[-1])
            self.Measurements[-1].close()
            self.Measurements.pop(-1)

        for m in measParam:
            Meas = Measurement(self, self.MainWindow, self.Configuration, self.Instruments, self, m)
            self.Measurements.append(Meas)
            self.layout.addWidget(self.Measurements[-1])
            self.Frame.setFixedWidth(self.FixWidth*len(self.Measurements))
        
        self.addMeasurement(self.Measurements[-1])

    def clearMeasurement(self):
        
        for m in range(len(self.Measurements)):
            self.layout.removeWidget(self.Measurements[-1])
            self.Measurements[-1].close()
            self.Measurements.pop(-1)

        Meas = Measurement(self, self.MainWindow, self.Configuration, self.Instruments, self)
        self.Measurements.append(Meas)
        self.layout.addWidget(self.Measurements[-1])

        self.Frame.setFixedWidth(self.FixWidth*len(self.Measurements))
    

    def addMeasurement(self, Origin):
        if Origin == self.Measurements[-1]:
            Meas = Measurement(self, self.MainWindow, self.Configuration, self.Instruments, self)
            self.Measurements.append(Meas)
            self.layout.addWidget(self.Measurements[-1])

            self.Frame.setFixedWidth(self.FixWidth*len(self.Measurements))
    
    def getMeasurements(self):
        measurements = []
        for Meas in self.Measurements:
            if Meas.getMeasName().strip().lower() != "select":
                measurements.append(Meas.getDetails())
        return measurements

    def deleteMeasurement(self, meas):
        if len(self.Measurements) > 1:
            while self.Measurements[-1].getMeasName() == "Select" and self.Measurements[-2].getMeasName() == "Select":
                self.layout.removeWidget(self.Measurements[-1])
                self.Measurements[-1].close()
                self.Measurements.pop(-1)
                if len(self.Measurements) < 2: 
                    break
            self.Frame.setFixedWidth(self.FixWidth*len(self.Measurements))
            #for meas in self.Measurements:
            #    self.layout.addWidget(meas)
    
    def updateAvailDevices(self):
        for meas in self.Measurements:
            meas.updateAvailDevices()

class Measurement(QtWidgets.QWidget):

    def __init__(self, parent, MainWindow, Configuration, Instruments, MeasFrame, Initialize=None, *args, **kw):
        super().__init__(parent)
        
        self.MeasFrame = MeasFrame
        self.Folder = ""
        self.Name = "Select"
        self.Labels = []
        self.Widget = []
        self.WidgetVar = []
        self.Instruments = Instruments
        self.Configuration = Configuration
        self.MainWindow = MainWindow
        self.width = int(self.MainWindow.getWindowWidth()/5)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(1,1,1,1)
        self.layout.setSpacing(1)
        self.layout.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)

        MeasNames = ['Select']
        availMeas  = self.Configuration.getAvailableMeasurements()
        if availMeas != None:
            availMeas = self.CheckTools(availMeas, self.Configuration.getMeasurementTools())
            MeasNames.extend(availMeas)

        self.Bar = QtWidgets.QMenuBar(self)
        
        self.Menu = self.Bar.addMenu("Select")
        self.createMenu(availMeas)
        

        self.Bar.setFixedWidth(self.width)
        
        self.layout.addWidget(self.Bar)

        if Initialize != None:
            self.setMeasurement(Initialize)

        self.Menu.triggered[QtWidgets.QAction].connect(self.callMeasurement)
        self.CurMeasIndex = 0

    def setMeasurement(self, m):
        for key, val in self.MenuItems.items():
            if m['Name'].lower().strip() == "select":
                self.callMeasurement(val)
            elif QtWidgets.QMenu == type(val):
                if val.title() == m['Folder']:

                    for child in val.children()[1:]:
                        if child.text() == m["Name"]:
                            
                            par = []

                            n = 0 
                            for p in m['Parameters']:
                               
                                if m['Array'][n]:
                                    try:
                                        par.append(','.join(str(x) for x in p))
                                    except TypeError:
                                        par.append(p)
                                elif m['Experiment'][n]:
                                    try:
                                        par.append('%'.join(str(x) for x in p))
                                    except TypeError:
                                        par.append(p)
                                else:
                                    try:
                                        par.append(p[0])
                                    except TypeError:
                                        par.append(p)
                                n = n + 1
                            self.callMeasurement(child, parameters=par)

    def createMenu(self, availMeas):

        self.MenuItems = dict()
        self.MeasAct = dict()

        self.MenuItems['Select'] = self.Menu.addAction('Select')

        for key, val in availMeas.items():

            if len(val) > 0:
                
                self.MenuItems[key] = self.Menu.addMenu(key)

                for x in val:

                    Qact = QtWidgets.QAction(x, self.MenuItems[key])
                    self.MenuItems[key].addAction(Qact)

                    try:
                        self.MeasAct[key] = [Qact]
                    except KeyError as e:
                        self.MeasAct[key].append(Qact)

    def destroy(self):

        self.layout.removeWidget(self.Measurement)
        self.Measurement.destroy()
        for entry in self.Labels:
            self.layout.removeWidget(entry)
            entry.close()
        self.Labels = [] 
        
        for entry in self.Widget:
            self.layout.removeWidget(entry)
            entry.close()
        self.Widget = []

        super().destroy()

    def updateAvailDevices(self):
        self.Menu.triggered[QtWidgets.QAction].disconnect()
        
        MeasNames = ['Select']
        availMeas  = self.Configuration.getAvailableMeasurements()
        if availMeas != None:
            availMeas = self.CheckTools(availMeas, self.Configuration.getMeasurementTools())
            MeasNames.extend(availMeas)
        #for n in range(self.Measurement.count()):
        #    self.Measurement.removeItem(0)
        for key, val in self.MenuItems.items():
            if key != "Select":
                val.clear()
        self.Menu.clear()

        self.createMenu(availMeas)
        #self.Measurement.addItems(MeasNames)
        #if self.CurMeasIndex < self.Measurement.count():
        #    self.Measurement.setCurrentIndex(self.CurMeasIndex)
            
        self.Menu.triggered[QtWidgets.QAction].connect(self.callMeasurement)
        

    def CheckTools(self, Measurements, Tools):
        availMeas = cp.deepcopy(Measurements)
        for key, value in Measurements.items():
            for n in range(len(value)-1,-1,-1):
                avail = True
                for tool in Tools[key][n]:
                    availT = False
                    if tool.strip().lower() == 'none':
                        availT = True
                    else:
                        for Instkey, Instvalue in self.MainWindow.AvailableInstruments.items():
                            toolTemp = tool.split("|")
                            tools = []
                            for t in toolTemp:
                                tools.append(t.strip().lower())

                            if Instkey.strip().lower() in tools or Instkey.strip().lower() == "none":
                                if Instvalue:
                                    availT = True
                                    break

                    if not availT:
                        avail = False
                        break
                
                if not avail:
                    availMeas[key].pop(n)

        return availMeas

    def getDetails(self):
        Name = self.getMeasName()

        parameters = []
        exp = []
        array = []
        VariableName = []
        n = 0
        for var in self.WidgetVar:
            para = var.get()
            parameters.append(para)
            VariableName.append(self.VariableName[n])
            exp.append(var.isExperiment())
            array.append(var.isArray())
            n = n+1
        return {'Name': Name, 'Folder': self.Folder, "ValueNames": VariableName ,"Parameters":parameters, "Experiment": exp, "Array": array}
    
    def getMeasName(self):
        return self.Name
    
    def getMeasFolder(self):
        return self.Folder

    def callMeasurement(self, index, parameters=None):

        self.Name = index.text()
        if self.Name != "Select":
            self.Folder = index.parent().title()
            self.Menu.setTitle("%s/%s" %(self.Folder, self.Name))
        else:
            self.Folder = ""
            self.Menu.setTitle("Select")
        
                
        valFloat = "^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$"
        valFloatExp = "^(([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)[%])*$"
        valFloatArray =  "^(([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)[,])*$"
        valInt = "^[0-9]+$"
        valIntExp = "^([0-9]+[%])*$"
        valIntArray = "^([0-9]+[,])*$"
        valString = "^[A-Z]+$"
        valVorI = "^[VI]$"
        valVorIAr = "^([VI]+[,])*$"

        MeasDetail = self.Configuration.getMeasurementDetail(self.Name, self.Folder)

        if MeasDetail != None and self.Name != "Select":
            
            for entry in self.Labels:
                self.layout.removeWidget(entry)
                entry.close()
            self.Labels = []
            
            for entry in self.Widget:
                self.layout.removeWidget(entry)
                entry.close()
            self.Widget = []
            
            for n in range(self.layout.count()):
                item = self.layout.itemAt(n)
                if type(item) == QtWidgets.QSpacerItem:
                    self.layout.removeItem(item)


            self.Labels = []
            self.Widget = []
            self.WidgetVar = []
            self.VariableName = []
            self.boolList = {"True": True,  "False": False}

            for n in range(len(MeasDetail['VariableName'])):
                    
                if parameters == None:
                    Value = MeasDetail['Default'][n]
                else:
                    Value = parameters[n]

                self.Labels.append(QtWidgets.QLabel(MeasDetail['VariableName'][n], self))
                self.layout.addWidget(self.Labels[-1])
                self.VariableName.append(MeasDetail['VariableName'][n])

                if MeasDetail['DataType'][n].strip().lower() == "wgfmuchannel":
                    Channels = self.Instruments.getInstrumentsByType('B1530A')[0]['Instrument'].getChannelIDs()['Channels']
                    self.WidgetVar.append(IntVar(Value))
                    self.Widget.append(ComboBox(self, self.WidgetVar[n], Channels))
                    self.layout.addWidget(self.Widget[-1])

                elif MeasDetail['DataType'][n].strip().lower() == "81110achn":
                    Channels = [1,2]
                    self.WidgetVar.append(IntVar(Value))
                    self.Widget.append(ComboBox(self, self.WidgetVar[n], Channels))
                    self.layout.addWidget(self.Widget[-1])

                elif MeasDetail['DataType'][n].strip().lower() == "bnc765chn":
                    Channels = [1,2,3,4]
                    self.WidgetVar.append(IntVar(Value))
                    self.Widget.append(ComboBox(self, self.WidgetVar[n], Channels))
                    self.layout.addWidget(self.Widget[-1])


                elif MeasDetail['DataType'][n].strip().lower() == "740zichn":
                    Channels = ["1A","1B","2A","2B","3A","3B","4A","4B"]
                    self.WidgetVar.append(StringVar(Value.strip()))
                    self.Widget.append(ComboBox(self, self.WidgetVar[n], Channels))
                    self.layout.addWidget(self.Widget[-1])

                elif MeasDetail['DataType'][n].strip().lower() == "float":
                    self.WidgetVar.append(StringVarExp(float, Value))
                    self.WidgetVar[n].setValue(Value)
                    self.Widget.append(Entry(self, self.WidgetVar[n], validateNumbers=valFloatExp))
                    self.layout.addWidget(self.Widget[-1])
                    
                elif MeasDetail['DataType'][n].strip().lower() == "string":
                    self.WidgetVar.append(StringVar(Value))
                    self.Widget.append(Entry(self, self.WidgetVar[n]))
                    self.layout.addWidget(self.Widget[-1])
                    
                elif MeasDetail['DataType'][n].strip().lower() == "smu":
                    self.WidgetVar.append(IntVar(Value, int))
                    self.WidgetVar[n].setValue(Value)
                    self.Widget.append(Entry(self, self.WidgetVar[n], validateNumbers=valInt))
                    self.layout.addWidget(self.Widget[-1])

                elif MeasDetail['DataType'][n].strip().lower() == "cmu":
                    self.WidgetVar.append(IntVar(Value, int))
                    self.WidgetVar[n].setValue(Value)
                    self.Widget.append(Entry(self, self.WidgetVar[n], validateNumbers=valInt))
                    self.layout.addWidget(self.Widget[-1])
                
                elif MeasDetail['DataType'][n].strip().lower() == "smuar":
                    self.WidgetVar.append(StringVarAr(Value, int))
                    self.WidgetVar[n].setValue(Value)
                    self.Widget.append(Entry(self, self.WidgetVar[n], validateNumbers=valIntArray))
                    self.layout.addWidget(self.Widget[-1])
                
                elif MeasDetail['DataType'][n].strip().lower() == "int":
                    self.WidgetVar.append(StringVarExp(int, Value))
                    self.WidgetVar[n].setValue(Value)
                    self.Widget.append(Entry(self, self.WidgetVar[n], validateNumbers=valIntExp))
                    self.layout.addWidget(self.Widget[-1])
                    
                elif MeasDetail['DataType'][n].strip().lower() == "bool":
                    self.WidgetVar.append(BooleanVar(Value))
                    self.Widget.append(ComboBox(self, self.WidgetVar[n], self.boolList.keys()))
                    self.layout.addWidget(self.Widget[-1])

                elif MeasDetail['DataType'][n].strip().lower() == "image":
                    self.WidgetVar.append(StringVar(Value))
                    self.Widget.append(FileDialog(self, self.WidgetVar[n], self.boolList.keys()))
                    self.layout.addWidget(self.Widget[-1])
                
                elif MeasDetail['DataType'][n].strip().lower() == "vori":
                    self.WidgetVar.append(VorIVar(Value, str))
                    self.WidgetVar[n].setValue(Value)
                    self.Widget.append(Entry(self, self.WidgetVar[n], validateNumbers=valVorI))
                    self.layout.addWidget(self.Widget[-1])
                    
                elif MeasDetail['DataType'][n].strip().lower() == "voriar":
                    self.WidgetVar.append(VorIVarAr(Value, str))
                    self.WidgetVar[n].setValue(Value)
                    self.Widget.append(Entry(self, self.WidgetVar[n], validateNumbers=valVorIAr))
                    self.layout.addWidget(self.Widget[-1])

                elif MeasDetail['DataType'][n].strip().lower() == "intar":
                    self.WidgetVar.append(StringVarAr(Value, int))
                    self.WidgetVar[n].setValue(Value)
                    self.Widget.append(Entry(self, self.WidgetVar[n], validateNumbers=valIntArray))
                    self.layout.addWidget(self.Widget[-1])
                
                elif MeasDetail['DataType'][n].strip().lower() == "floatar":
                    self.WidgetVar.append(StringVarAr(Value, float))
                    self.WidgetVar[n].setValue(Value)
                    self.Widget.append(Entry(self, self.WidgetVar[n], validateNumbers=valFloatArray))
                    self.layout.addWidget(self.Widget[-1])

                self.Widget[-1].setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
                self.Widget[-1].setFixedWidth(self.width)

            if parameters == None:
                self.MeasFrame.addMeasurement(self)
            
            self.SpacerItem = QtWidgets.QSpacerItem(self.width,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            self.layout.addSpacerItem(self.SpacerItem)
        
        elif  self.Name == "Select":
            for entry in self.Labels:
                self.layout.removeWidget(entry)
                entry.close()
            self.Labels = []
            
            for entry in self.Widget:
                self.layout.removeWidget(entry)
                entry.close()
            self.Widget = []

            for n in range(self.layout.count()):
                item = self.layout.itemAt(n)
                if type(item) == QtWidgets.QSpacerItem:
                    self.layout.removeItem(item)

            self.MeasFrame.deleteMeasurement(self)


    def BoolToString(self, val):
        if val:
            return "True"
        else:
            return "False"

class ComboBox(QtWidgets.QComboBox):

    
    def __init__(self, parent, Variable, Options, width=15):
        
        super().__init__(parent)
        self.setFixedWidth(width)
        self.addItems([str(o) for o in Options])
        self.variable = Variable
        Default = self.variable.get()
        index = self.findText(str(Default))
        self.setCurrentIndex(index)
        self.currentIndexChanged.connect(self.callFunc)
    
    def getVariable(self):
        ret = self.variable.get()
        return ret

    def setVariable(self, text):
        self.variable.setValue(text)
    
    def callFunc(self, index):
        self.setVariable(self.itemText(index))

class FileDialog(QtWidgets.QPushButton):
    
    def __init__(self, parent, Variable, Options, width=15):
        
        super().__init__(parent)
        self.setFixedWidth(width)
        self.variable = Variable
        self.Default = self.variable.get()
        self.setText("select Image")
        self.pressed.connect(self.callFunc)

    def getVariable(self):
        ret = self.variable.get()
        return ret

    def setVariable(self, text):
        self.variable.setValue(text)
    

    def callFunc(self):

        Path = self.openFileNameDialog()
        if Path != None:
            
            butText = std.getFile_FolderText(Path, 20)

            self.setText(butText)
            self.setVariable(Path)

    
    def openFileNameDialog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Select Image", "","Images (*.jpg *.jpeg *.png *.bmp);;All Files (*)", options=options)
        if fileName:
            return fileName

class Entry(QtWidgets.QLineEdit):

    def __init__(self, parent, Variable, width=15, validateNumbers=None):
        
        super().__init__(parent)
        self.setFixedWidth(width)
        self.variable = Variable
        Default = self.variable.getString()
        self.setText(str(Default))
        self.textChanged.connect(self.callFunc)
    
        if validateNumbers != None:
            self.validateNumbers = str(validateNumbers)
            reg_ex = QtCore.QRegExp(self.validateNumbers)
            input_validator = QtGui.QRegExpValidator(reg_ex, self)
            self.setValidator(input_validator)
        else:
            self.validateNumbers = None

    def focusOutEvent(self,event):
        
        if self.text() != self.variable.getString():
            self.setText(str(self.variable.getString()))

        super().focusOutEvent(event)

    def getVariable(self):
        return self.variable.get()

    def setVariable(self, text):
        self.variable.setValue(text)
    
    def callFunc(self, index):
        self.setVariable(self.text())

class StringVarAr():

    def __init__(self, array, typ=str, *args, **kwargs):
        self.typ = typ
        self.data  = []
        self.setValue(str(array))

    def setType(self, typ):
        self.typ = typ
    
    def getType(self):
        return self.typ
    
    def isExperiment(self):
        return False

    def isArray(self):
        return True
    
    def get(self):
        return self.data
    
    def getString(self):
        
        if len(self.data) > 0:
            ret = str(self.data[0])
            for n in range(1, len(self.data), 1):
                ret = "%s,%s" %(ret, self.data[n])
            return ret
        else:
            return ""
    
    def setValue(self, array):
        data = []
        save = False
        try:
            for element in array.split(','):
                if element == "":
                    continue
                if self.typ == str:
                    data.append(str(element).strip())
                elif self.typ == int:
                    data.append(int(element))
                elif self.typ == float:
                    data.append(float(element))
            save = True
        except:
            None
            #raise ValueError("At least one element was not of type %s in StringVarAr." %(self.typ))
        if save:
            self.data = data
        return True

class VorIVarAr():

    def __init__(self, array, *args, **kwargs):
        self.data  = []
        self.setValue(str(array))
        self.typ = bool

    def setType(self, typ):
        self.typ = typ
    
    def getType(self):
        return self.typ
    
    def isExperiment(self):
        return False

    def isArray(self):
        return True
    
    def get(self):
        return self.data
    
    def getString(self):
        if len(self.data) > 0:
            if self.data[0]:
                ret = "V"
            else:
                ret = "I"
            for n in range(1, len(self.data), 1):
                if self.data[n]:
                    ret = "%s,V" %(ret)
                else:
                    ret = "%s,I" %(ret)
            return ret
        else:
            return ""
    
    def setValue(self, array):
        data = []
        save = False
        try:
            for element in array.split(','):
                if element.strip() == "":
                    continue
                if element.strip().lower() == "i":
                    data.append(False)
                else: 
                    data.append(True)
            save = True
        except:
            None
            #raise ValueError("At least one element was not of type %s in StringVarAr." %(self.typ))
        if save:
            self.data = data
        return True

class StringVarExp():

    def __init__(self,  typ=str, array="" ,*args, **kwargs):
        self.typ = typ
        self.data  = []
        self.setValue(str(array))

    def setType(self, typ):
        self.typ = typ
    
    def getType(self):
        return self.typ
    
    def isExperiment(self):

        if len(self.data) > 1: 
            return True
        return False
    
    def isArray(self):
        return False

    def get(self):
        return self.data
    
    def getString(self):
        if len(self.data) > 0:
            ret = self.data[0]
            for n in range(1, len(self.data), 1):
                ret = r"%s%%%s" %(ret, self.data[n])
            return ret
        else:
            return ""
    
    def setValue(self, array):

        data = []
        save = False
        try:
            for element in str(array).split('%'):
                if element == "":
                    continue
                if self.typ == str:
                    data.append(str(element))
                elif self.typ == int:
                    data.append(int(element))
                elif self.typ == float:
                    data.append(float(element))
            save = True
        except:
            None
            #raise ValueError("At least one element was not of type %s in StringVarExp." %(self.typ))
        
        if save:
            self.data = data
        return True


class StringVar():

    variable = ""

    def __init__(self, variable, *args, **kwargs):
        self.setValue(variable)
        
    def get(self):
        return str(self.variable)

    def setValue(self, variable):
        try: 
            self.variable = str(variable)
        except:
            raise TypeError("At least one element was not of type str in StringVar.")
    
    def isExperiment(self):
        return False
    
    def isArray(self):
        return False
    
    def getString(self):
        return str(self.variable)


class VorIVar():

    variable = ""

    def __init__(self, variable, *args, **kwargs):
        self.setValue(variable)
        self.typ = bool

    def getType(self):
        return self.typ
        
    def get(self):
        return self.variable

    def setValue(self, variable):
        if isinstance(variable, bool):
            self.variable = variable
        else:
            if variable.strip().lower() == "i":
                self.variable = False
            else:
                self.variable = True
        
    
    def isExperiment(self):
        return False
    
    def isArray(self):
        return False
    
    def getString(self):
        if self.variable:
            return "V"
        else:
            return "I"

class DoubleVar():

    def __init__(self, variable, *args, **kwargs):
        self.setValue(variable)
        
    
    def get(self):
        return float(self.variable)

    def getString(self):
        return str(self.variable)

    def setValue(self, variable):
        try: 
            self.variable = float(variable)
        except:
            raise TypeError("At least one element was not of type float in DoubleVar.")
    
    def isExperiment(self):
        return False
    
    def isArray(self):
        return False


class IntVar():

    def __init__(self, variable, *args, **kwargs):

        self.setValue(variable)
        
    def get(self):
        return int(self.variable)

    def getString(self):
        return str(self.variable)
        
    def getValue(self):
        return int(self.variable)

    def setValue(self, variable):
        try: 
            if variable == "":
                self.variable = 0
            else:
                self.variable = int(variable)

        except:
            raise TypeError("At least one element was not of type int in IntVar.")
    
    def isExperiment(self):
        return False

    def isArray(self):
        return False

class BooleanVar():

    def __init__(self, variable, *args, **kwargs):
        self.setValue(variable)
        self.translate = {"true":True, "false":False}
        
    def get(self):
        return bool(self.variable)

    def setValue(self, variable):
        try:
            variable = self.translate[variable.lower()]
        except:
            None
        try: 
            self.variable = bool(variable)
        except:
            raise TypeError("At least one element was not of bool in BooleanVar.")
    
    def isExperiment(self):
        return False
    
    def isArray(self):
        return False


class MeasurementLoadWindow(QtWidgets.QMainWindow):

    def __init__(self, MainWindow, MeasFrame, fileItems, width=200, height=400):
        
        super().__init__(MainWindow)
        title = "Load Measurement"
        self.setWindowTitle(title)

        self.MainWindow = MainWindow
        self.MeasFrame = MeasFrame
        

        try: 
            self.setWindowIcon(self.MainWindow.icon)
        except:
            self.MainWindow.writeError("Icon not found in window %s" %(title))
        
        self._main = QtWidgets.QWidget(self)
        self.resize(width, height)
        self._main.resize(width, height)
        self.setFixedSize(self.size())
        self._main.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    
        self.layout = QtWidgets.QVBoxLayout(self._main)

        self.fileListWid = QtWidgets.QListWidget(self._main)
        self.fileListWid.insertItems(0, fileItems)
        self.fileListWid.setCurrentRow(0)

        self.layout.addWidget(self.fileListWid)
        self.fileListWid.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    
        self.LoadBut = QtWidgets.QPushButton("Load", self._main)
        
        self.LoadBut.clicked.connect(self.pressLoad)
        self.layout.addWidget(self.LoadBut)
        self.LoadBut.setSizePolicy(QtWidgets.QSizePolicy.Expanding , QtWidgets.QSizePolicy.Minimum)


    def pressLoad(self):
        CurItem = self.fileListWid.currentItem()
        self.MeasFrame.LoadMeasurement(CurItem.text())

    def closeEvent(self, event):
        self.MainWindow.setEnabled(True)
        super().closeEvent(event)


class MeasurementDeleteWindow(QtWidgets.QMainWindow):

    def __init__(self, MainWindow, MeasFrame, fileItems, width=200, height=400):
        
        super().__init__(MainWindow)
        title = "Delete Measurement"
        self.setWindowTitle(title)

        self.MainWindow = MainWindow
        self.MeasFrame = MeasFrame
        
        try: 
            self.setWindowIcon(self.MainWindow.icon)
        except:
            self.MainWindow.writeError("Icon not found in window %s" %(title))
        
        self._main = QtWidgets.QWidget(self)
        self.resize(width, height)
        self._main.resize(width, height)
        self.setFixedSize(self.size())
        self._main.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    
        self.layout = QtWidgets.QVBoxLayout(self._main)

        self.fileListWid = QtWidgets.QListWidget(self._main)
        self.fileListWid.insertItems(0, fileItems)
        self.fileListWid.setCurrentRow(0)
        self.fileListWid.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.layout.addWidget(self.fileListWid)
        self.fileListWid.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    
        self.DelBut = QtWidgets.QPushButton("Delete", self._main)
        
        self.DelBut.clicked.connect(self.pressDelete)
        self.layout.addWidget(self.DelBut)
        self.DelBut.setSizePolicy(QtWidgets.QSizePolicy.Expanding , QtWidgets.QSizePolicy.Minimum)

    def pressDelete(self):
        CurItems = self.fileListWid.selectedItems()
        CurItemsName = []
        for CurItem in CurItems:
            CurItemsName.append(CurItem.text())
        self.MeasFrame.DeleteMeasurement(CurItemsName)
        fileList = self.MeasFrame.getFileItems(self.MeasFrame.folder, allMeas=True)
        self.fileListWid.clear()

        self.listUpdate(fileList)

    def listUpdate(self, fileList):
        if fileList != None:
            self.fileListWid.insertItems(0, fileList)
            self.fileListWid.setCurrentRow(0)

    def closeEvent(self, event):
        self.MainWindow.setEnabled(True)
        super().closeEvent(event)


class MeasurementSaveWindow(QtWidgets.QMainWindow):

    def __init__(self, MainWindow, MeasFrame, fileItems, width=200, height=400):
       
        super().__init__(MainWindow)
        title = "Save Measurement"
        self.setWindowTitle(title)

        self.MainWindow = MainWindow
        self.MeasFrame = MeasFrame
        self.HomeDirectory = self.MainWindow.getHomeDirectory()
                
        try: 
            self.setWindowIcon(self.MainWindow.icon)
        except:
            self.MainWindow.writeError("Icon not found in window %s" %(title))
        
        self._main = QtWidgets.QWidget(self)
        self.resize(width, height)
        self._main.resize(width, height)
        self.setFixedSize(self.size())
        self._main.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    
        self.layout = QtWidgets.QVBoxLayout(self._main)
        
        valString = "^[a-zA-Z0-9]+$"
        self.fileInput = QtWidgets.QLineEdit("", self._main)
        self.validateNumbers = str(valString)
        reg_ex = QtCore.QRegExp(self.validateNumbers)
        input_validator = QtGui.QRegExpValidator(reg_ex, self.fileInput)
        self.fileInput.setValidator(input_validator)
        self.layout.addWidget(self.fileInput)
        self.fileInput.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        self.fileListWid = QtWidgets.QListWidget(self._main)
        if fileItems != None:
            self.fileListWid.insertItems(0, fileItems)
        self.fileListWid.setEnabled(False)
        self.layout.addWidget(self.fileListWid)
        self.fileListWid.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.SaveBut = QtWidgets.QPushButton("Save", self._main)
        self.SaveBut.clicked.connect(self.pressSave)
        self.layout.addWidget(self.SaveBut)
        self.SaveBut.setSizePolicy(QtWidgets.QSizePolicy.Expanding , QtWidgets.QSizePolicy.Minimum)

    def pressSave(self):
        self.MeasFrame.SaveMeasurement(self.fileInput.text())
        
    def closeEvent(self, event):
        self.MainWindow.setEnabled(True)
        super().closeEvent(event)