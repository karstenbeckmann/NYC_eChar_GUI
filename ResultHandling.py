
import sys
from ctypes import *
import win32api
import win32con
import PlottingRoutines as PR
import threading as th
import queue as qu 
import time as tm
import StdDefinitions as std
import copy as cp
import os as os
import functools
import queue as qu
from matplotlib.figure import Figure
import matplotlib.backends as qtagg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib import lines
from matplotlib import markers
from matplotlib import colors
from PyQt5 import QtWidgets, QtCore, QtGui
import Qt_stdObjects as stdObj
import pickle as pk


class ResultHandling():

    def __init__(self, MainGI, ResultWindow):
        
        self.ResultWindow = ResultWindow
    
        self.Results = []
        self.CurDieX = ''
        self.CurDieY = ''
        self.CurDevX = ''
        self.CurDevY = ''
        self.CurMeas = ''
        self.CurVal = ''
        self.CurNum = 'Live'

        self.DieXValues = ['']
        self.DieYValues = ['']
        self.DevXValues = ['']
        self.DevYValues = ['']
        self.MeasValues = ['']
        self.VarValues = ['']
        self.NumValues = ['Live']

        self.dpi=600
        self.ErrorQu = qu.Queue()

        self.MainGI = MainGI
        self.changed = False
        self.ErrorQu = qu.Queue()
        self.CurResult = None
        self.subResultsID = []
        self.Configuration = MainGI.Configuration
        self.linestyle = self.Configuration.getValue("ResultGraphStyle")
        self.linewidth  = self.Configuration.getValue("ResultGraphWidth")
        self.linecolor = self.Configuration.getValue("ResultGraphColor")
        self.Xscale = 'lin'
        self.Yscale = 'lin'
        self.Live = True
        self.ID = 1
        self.useDumping = True
        self.CurMeasDieX = None
        self.CurMeasDieY = None
        self.CurMeasDevX = None
        self.CurMeasDevY = None
        
        self.__close = qu.Queue()
        self.thread = None

    def isFinished(self):
        if self.thread == None:
            return True
        
        return not self.thread.isAlive()

    def isAlive(self):
        return self.thread.isAlive()


    def SetChanged(self, changed):
        self.changed = changed

    def setCurDieX(self, val):
        self.CurDieX = val

    def setCurDieY(self, val):
        self.CurDieY = val

    def setCurDevX(self, val):
        self.CurDevX = val

    def setCurDevY(self, val):
        self.CurDevY = val
        
    def setCurMeas(self, val):
        self.CurMeas = val
        
    def setCurNum(self, val):
        self.CurNum = val
        if str(val).strip().lower() == 'live':
            if len(self.subResultsID) > 0:
                self.CurResult = self.subResultsID[-1]
        else:
            disCont = False
            try:
                val = int(val)
                disCont = False
            except:
                disCont = True
            if not disCont and len(self.subResultsID) > 0:
                self.CurResult = self.subResultsID[val-1]
        
    def setCurVal(self, val):
        self.CurVal = val

    def getCurDieX(self):
        return self.CurDieX

    def getCurDieY(self):
        return self.CurDieY
            
    def getCurDevX(self):
        return self.CurDevX
            
    def getCurDevY(self):
       return self.CurDevY
            
    def getCurMeas(self):
        return self.CurMeas

    def getCurNum(self):
        return self.CurNum
    
    def getCurVal(self):
         return self.CurVal

    def getResult(self):
        if self.CurResult == None:
            return None
        else:
            return self.Results[self.CurResult]

    def getTraceData(self):
        None

    def getGraphProperties(self):
        None

    def getResultSize(self):
        return len(self.subResultsID)

    def updateDieX(self):
        Xar = []
        for res in self.Results:
            X = res.getDieX()
            if not X in Xar:
                Xar.append(X)
        
        Xar.sort()
        Xar.insert(0,'')

        self.DieXValues = Xar
        return Xar

    def updateDieY(self):
        Yar = []
        for res in self.Results:
            Y = res.getDieY()
            if not Y in Yar:
                Yar.append(Y)

        Yar.sort()
        Yar.insert(0,'')
        self.DieYValues = Yar
        return Yar

    def updateDevX(self):
        
        Xar = []
        for res in self.Results:

            Xdie = res.getDieX()
            Ydie = res.getDieY()

            X = res.getDevX()
            addX = False
            addY = False
            if self.CurDieX == '':
                addX = True
            else:
                if int(self.CurDieX) == int(Xdie):
                    addX = True
            if self.CurDieY == '':
                addY = True
            else:
                if int(self.CurDieY) == int(Ydie):
                    addY = True
            
            if not X in Xar and addX and addY:
                Xar.append(X)

        Xar.sort()
        Xar.insert(0,'')
        self.DevXValues = Xar
        return Xar

    def updateDevY(self):
        
        Yar = []
        for res in self.Results:
            Xdie = res.getDieX()
            Ydie = res.getDieY()

            Y = res.getDevY()
            addX = False
            addY = False

            if self.CurDieX == '':
                addX = True
            else:
                if int(self.CurDieX) == int(Xdie):
                    addX = True

            if self.CurDieY == '':
                    addY = True
            else:
                if int(self.CurDieX) == int(Ydie):
                    addY = True
            
            if not Y in Yar and addX and addY:
                Yar.append(Y)

        Yar.sort()
        Yar.insert(0,'')
        self.DevYValues = Yar
        return Yar

    def updateMeasurements(self):
        
        Meas = []
        for res in self.Results:
            M = res.getMeasurement()

            Xdie = res.getDieX()
            Ydie = res.getDieY()
            Xdev = res.getDevX()
            Ydev = res.getDevY()

            addDieX = False
            addDieY = False
            addDevX = False
            addDevY = False

            if self.CurDieX == '':
                addDieX = True
            else:
                if int(self.CurDieX) == int(Xdie):
                    addDieX = True
                    
            if self.CurDieY == '':
                addDieY = True
            else:
                if int(self.CurDieY) == int(Ydie):
                    addDieY = True
            
            if self.CurDevX == '':
                addDevX = True
            else:
                if int(self.CurDevX) == int(Xdev):
                    addDevX = True

            if self.CurDevY == '':
                addDevY = True
            else:
                if int(self.CurDevY) == int(Ydev):
                    addDevY = True

            if not M in Meas and addDieX and addDieY and addDevX and addDevY:
                Meas.append(M)

        Meas.sort()
        Meas.insert(0,'')
        self.MeasValues = Meas
        return Meas
    
    def updateValue(self):
        Val = []
        del self.subResultsID
        self.subResultsID = []
        n = 0
        for res in self.Results:
            V = res.getValueName()

            Xdie = res.getDieX()
            Ydie = res.getDieY()
            Xdev = res.getDevX()
            Ydev = res.getDevY()
            Meas = res.getMeasurement()

            addDieX = False
            addDieY = False
            addDevX = False
            addDevY = False
            addMeas = False

            if self.CurDieX == '':
                addDieX = True
            else:
                if int(self.CurDieX) == int(Xdie):
                    addDieX = True

            if self.CurDieY == '':
                addDieY = True
            else:
                if int(self.CurDieY) == int(Ydie):
                    addDieY = True
            
            if self.CurDevX == '':
                addDevX = True
            else:
                if int(self.CurDevX) == int(Xdev):
                    addDevX = True

            if self.CurDevY == '':
                addDevY = True
            else:
                if int(self.CurDevY) == int(Ydev):
                    addDevY = True

            print(self.CurMeas.strip() == Meas, self.CurMeas.strip(), Meas)
            if self.CurMeas == '': 
                addMeas = True
            else:
                if self.CurMeas.strip() == Meas:
                    addMeas = True

            if addDieX and addDieY and addDevX and addDevY and addMeas:
                if not V in Val:
                    Val.append(V)
                    
                self.subResultsID.append(n)
                
            n = n+1

        Val.insert(0,'')
        self.VarValues = Val
        return Val

    def updateNum(self):

        Num = []
        del self.subResultsID
        self.subResultsID = []
        n = 0
        for res in self.Results:
            V = res.getValueName()

            Xdie = res.getDieX()
            Ydie = res.getDieY()
            Xdev = res.getDevX()
            Ydev = res.getDevY()
            Meas = res.getMeasurement()
            Val = res.getValueName()

            addDieX = False
            addDieY = False
            addDevX = False
            addDevY = False
            addMeas = False
            addVal = False

            if self.CurDieX == '':
                addDieX = True
            else:
                if self.CurDieX == Xdie:
                    addDieX = True

            if self.CurDieY == '':
                addDieY = True
            else:
                if self.CurDieY == Ydie:
                    addDieY = True
            
            if self.CurDevX == '':
                addDevX = True
            else:
                if self.CurDevX == Xdev:
                    addDevX = True

            if self.CurDevY == '':
                addDevY = True
            else:
                if self.CurDevY == Ydev:
                    addDevY = True

            if self.CurMeas == '': 
                addMeas = True
            else:
                if self.CurMeas.strip() == Meas:
                    addMeas = True

            if self.CurVal == '': 
                addVal = True
            else:
                if self.CurVal.strip() == Val:
                    addVal = True


            if addDieX and addDieY and addDevX and addDevY and addMeas and addVal:
                Num.append(n)
                self.subResultsID.append(n)
            n = n+1

        Num.insert(0,'Live')
        self.NumValues = Num
        return self.NumValues

    def clear(self):
        self.Results = []
        self.ID = 0
        self.setLive()
  
        self.DieXValues = ['']
        self.DieYValues = ['']
        self.DevXValues = ['']
        self.DevYValues = ['']
        self.MeasValues = ['']
        self.VarValues = ['']
        self.NumValues = ['Live']
        
        self.CurDieX = ''
        self.CurDieY = ''
        self.CurDevX = ''
        self.CurDevY = ''
        self.CurMeas = ''
        self.CurVal = ''
        self.CurNum = 'Live'

        upd = {'DieX': self.DieXValues}
        upd['DieY'] = self.DieYValues
        upd['DevX'] = self.DevXValues
        upd['DevY'] = self.DevYValues
        upd['Meas'] = self.MeasValues
        upd['Var'] = self.VarValues
        upd['Num'] = self.NumValues

        self.ResultWindow.Updates.put(upd)
        
        mydir = r"TempFiles/"

        if not os.path.exists(mydir):
            os.mkdir(mydir)

        filelist = os.listdir(mydir)
        for f in filelist:
            os.remove(os.path.join(mydir, f))

    def unsetLive(self):
        self.Live = False

    def setLive(self):
        self.Live = True

    def retrieveData(self):
        ret = False
        Result = None
        eChar = self.MainGI.geteChar()
        
        while not self.MainGI.geteChar().IVplotData.empty():

            ret = True
            
            data = cp.deepcopy(self.MainGI.geteChar().IVplotData.get())
            
            DieX = data['DieX']
            DieY = data['DieY']
            DevX = data['DevX']
            DevY = data['DevY']
            Folder = data['Folder']
            
            typ = data["MeasurementType"]
            ValueName = data["ValueName"]
            create = True
            
            if 'Add' in data.keys():
                if data['Add'] == True:
                    for Result in self.Results:
                        if Result.checkID(DieX, DieY, DevX, DevY, typ, ValueName):
                            create = False
                            break
                    if not create:
                        if not isinstance(data['Traces'], list):
                            data['Traces'] = [data['Traces']]
                        if 'Map' in data.keys():
                            Result.extend(data['Traces'], data['Map'])
                        else:
                            Result.extend(data['Traces'])

            if create:

                if self.useDumping:
                    if DieX != self.CurMeasDieX or DieY != self.CurMeasDieY or DevX != self.CurMeasDevX or DevY != self.CurMeasDevY:
                        for entry in self.Results:
                            entry.dumpData()
                        self.CurMeasDieX = DieX
                        self.CurMeasDieY = DieY
                        self.CurMeasDevX = DevX
                        self.CurMeasDevY = DevY

                dataMeas = data['MeasurementType']
                dataValName = data['ValueName']

                Xlabel = ""
                if 'Xlabel' in data:
                    Xlabel = data['Xlabel']

                Ylabel = ''
                if 'Ylabel' in data:
                    Ylabel = data['Ylabel']
                Clabel = ''
                if 'Clabel' in data:
                    Clabel = data['Clabel']
                X = False
                if 'Xaxis' in data:
                    X = data['Xaxis']
                
                dataWT = 'Measurement Data'
                if 'Title' in data:
                    dataWT = data['Title']

                MapCoordinates = [None,None]
                if 'Map' in data:
                    MapCoordinates = data['Map']

                try:
                    linestyle = data['lineStyle']
                    if not linestyle in lines.lineStyles.keys() and not linestyle in markers.MarkerStyle.markers.keys():
                        linestyle = self.linestyle
                except:
                    linestyle = self.linestyle

                try:
                    legend = data['legend']
                except:
                    legend = None

                try:
                    linewidth = data['lineWidth']
                    if not isinstance(linewidth, (int,float)):
                        linewidth = self.linewidth
                except:
                    linewidth = self.linewidth
                try:
                    linecolor = data['lineColor']
                    if not linecolor in colors.cnames.keys():
                        linecolor = self.linecolor
                except:
                    linecolor = self.linecolor
                    
                try:
                    Xscale = data['Xscale']
                    if not Xscale in ['lin', "log"]:
                        Xscale = self.Xscale
                except:
                     Xscale = self.Xscale
                     
                try:
                    Yscale = data['Yscale']
                    if not Yscale in ['lin', "log"]:
                        Yscale = self.Yscale
                except:
                     Yscale = self.Yscale

                if not isinstance(data['Traces'], list):
                    data['Traces'] = [data['Traces']]

                Result = MeasurementResult(data['Traces'], X, MapCoordinates=MapCoordinates, DieX=DieX, DieY=DieY, DevX=DevX, DevY=DevY,  Xlabel=Xlabel, Ylabel=Ylabel, Clabel=Clabel, linestyle=linestyle, 
                                    linewidth=linewidth, color=linecolor, Measurement=dataMeas, ValueName=dataValName, 
                                    WindowTitle=dataWT, Xscale=Xscale, Yscale=Yscale, Folder=Folder)
                  
                self.Results.append(Result)
                self.updateCurFile(Result)


                DieX = self.updateDieX()
                DieY = self.updateDieY()
                DevX = self.updateDevX()
                DevY = self.updateDevY()
                Meas = self.updateMeasurements()
                Num = self.updateNum()
                Val = self.updateValue()
                upd = {"DieX": DieX, "DieY": DieY,"DevX": DevX,"DevY": DevY,"Meas": Meas, "Num": Num, "Val": Val}
                self.ResultWindow.Updates.put(upd)

            self.ResultWindow.Updates.put({"Show": True})

            if self.Live and Result != None:
                self.updateCurGraphProp(Result)
                self.updateCurData(Result)
               
        return ret


    def close(self):
        self.__close.put(True)

    def start(self):
        
        self.thread = th.Thread(target=self.update)
        self.thread.start()

    def update(self):
        while True:
            if not self.__close.empty():
                break

            self.retrieveData()   
        
            while not self.ResultWindow.UpdateRequestsQu.empty():
                element = self.ResultWindow.UpdateRequestsQu.get()
                updData = False
                
                for key, item in element.items():
                    upd = None
                    if key == "DieX":
                        self.setCurDieX(item)
                        DieY = self.updateDieY()
                        DevX = self.updateDevX()
                        DevY = self.updateDevY()
                        Meas = self.updateMeasurements()
                        Num = self.updateNum()
                        Val = self.updateValue()
                        upd = {"DieY": DieY,"DevX": DevX,"DevY": DevY,"Meas": Meas, "Num": Num, "Val": Val}
                    elif key == "DieY":
                        self.setCurDieY(item)
                        DevX = self.updateDevX()
                        DevY = self.updateDevY()
                        Meas = self.updateMeasurements()
                        Num = self.updateNum()
                        Val = self.updateValue()
                        upd = {"DevX": DevX,"DevY": DevY,"Meas": Meas, "Num": Num, "Val": Val}
                    elif key == "DevX":
                        self.setCurDevX(item)
                        DevY = self.updateDevY()
                        Meas = self.updateMeasurements()
                        Num = self.updateNum()
                        Val = self.updateValue()
                        upd = {"DevY": DevY,"Meas": Meas, "Num": Num, "Val": Val}
                    elif key == "DevY":
                        self.setCurDevY(item)
                        Meas = self.updateMeasurements()
                        Num = self.updateNum()
                        Val = self.updateValue()
                        upd = {"Meas": Meas, "Num": Num, "Val": Val}
                    elif key == "Meas":
                        self.setCurMeas(item)
                        Num = self.updateNum()
                        Val = self.updateValue()
                        upd = {"Num": Num, "Val": Val}
                    elif key == "Val":
                        self.setCurNum(item)
                        Num = self.updateNum()
                        upd = {"Num": Num}
                    elif key == "Num":
                        if item == "":
                            item = "Live"
                        self.setCurNum(item)
                        updData = True
                    elif key =="Clear":
                        if item:
                            self.clear()
                    if key == "Num":
                        if item == "Live":
                            self.setLive()
                        else:
                            self.unsetLive()

                    if self.getResult() != None:
                        if key == "lineColor":
                            self.getResult().setLineColor(item)
                        elif key == 'lineStyle':
                            self.getResult().setLineStyle(item)
                        elif key == 'lineWidth':
                            self.getResult().setLineWidth(item)
                        elif key == 'lineSize':
                            self.getResult().setLineWidth(item)

                if upd != None:
                    self.ResultWindow.Updates.put(upd)
                    self.updateCurFile(self.getResult())
                
                if updData:

                    res = self.getResult()
                    self.updateCurGraphProp(res)
                    self.updateCurData(res)

            tm.sleep(0.2)

    def updateCurGraphProp(self, res):
        
        if res != None:
            print("curGraphPr",  res.createGraphProp())
            self.ResultWindow.Updates.put({"Figure": res.createGraphProp()})

    def updateCurData(self, res):
        
        if res != None:
            #print("crData", res.getData())
            self.ResultWindow.Updates.put({"Data": res.getData()})

    def updateCurFile(self, res):
        
        if res != None:
            
            folder = res.getFolder()
            fileName = res.getFileName()
            self.ResultWindow.Updates.put({'fileName': fileName, "folder":folder})


class MeasurementResult():

    def __init__(self, data, X, MaxLength=2.5e5, DieX='X', DieY='X', DevX='X', DevY='X',  Xlabel="", MapCoordinates=[None,None], Folder='', Clabel='', Xscale="lin", Ylabel="", Yscale="lin", linestyle='o', linewidth='1', color='b', Measurement='', ValueName='', WindowTitle='XY Plot'):
        
        self.DieX = DieX
        self.DieY = DieY
        self.DevX = DevX
        self.DevY = DevY
        self.Folder = Folder
        self.data = data
        self.dumped = False
        self.Measurement = Measurement
        self.MaxLength = int(MaxLength)
        self.X = X
        self.Xlabel = Xlabel
        self.Ylabel = Ylabel
        self.Clabel = Clabel
        self.Xscale = Xscale
        self.Yscale = Yscale
        self.linestyle = linestyle
        self.linewidth = linewidth
        self.color = color
        self.ValueName = ValueName
        self.dumpFile = ""
        self.WindowTitle = WindowTitle
        self.MapCoordinates = MapCoordinates
        if MapCoordinates[0] == None or MapCoordinates[1] == None:
            
            self.Map = False
            self.data = data
            
        else:
            self.Map = True
            self.data = []
            
            while len(self.data) < MapCoordinates[0]+1:
                self.data.append([])
  
            while len(self.data[MapCoordinates[0]]) < MapCoordinates[1]+1:
                self.data[MapCoordinates[0]].append(None)

            self.data[MapCoordinates[0]][MapCoordinates[1]] = data[0]
    
    def getFileName(self):

        ret = "%s_%s_DieX%dY%d_DevX%dY%d" %(self.Measurement, self.ValueName, self.DieX, self.DieY, self.DevX, self.DevY)
        return ret

    def extend(self, data, MapCoordinates=None):
        if not self.Map:
            if isinstance(self.data[0], list):

                if len(data) != len(self.data):
                    raise ValueError("Measurement Data can only be extended if the Data dimensions are the same.")

                for n in range(len(data)):
                    if len(self.data[n]) > self.MaxLength:
                        self.data[n] = data[n][-self.MaxLength:]
                    else:
                        self.data[n].extend(data[n])

                if len(self.data[0]) > self.MaxLength:
                    for n in range(len(self.data)):
                        self.data[n] = self.data[n][-self.MaxLength:]
            else:
                
                if len(self.data) > self.MaxLength:
                    self.data = data[-self.MaxLength:]
                else:
                    self.data.extend(data)

                if len(data) > self.MaxLength:
                    self.data = self.data[-self.MaxLength:]
        else:
            if isinstance(MapCoordinates, list):
                if MapCoordinates[0] != None and MapCoordinates[1] != None:
                    while len(self.data) < MapCoordinates[0]+1:
                        self.data.append([])
                    
                    while len(self.data[MapCoordinates[0]]) < MapCoordinates[1]+1:
                        self.data[MapCoordinates[0]].append(None)

                    self.data[MapCoordinates[0]][MapCoordinates[1]] = data[0]

        return True
    
    def dumpData(self):
        if not self.dumped:
            self.dumpFile = 'TempFiles/mr-%d.p' %(id(self))
            ResultFileObj = open(self.dumpFile, "wb")
            std.fastDump(self.data, ResultFileObj)
            self.dumped = True
            del self.data

    def createGraphProp(self):

        ret = dict()

        ret['lineStyle'] = self.linestyle
        ret['lineSize'] = self.linewidth
        ret['lineColor'] = self.color
        ret['xLabel'] = self.Xlabel
        ret['yLabel'] = self.Ylabel
        ret['cLabel'] = self.Clabel
        ret['title'] = self.WindowTitle
        ret['x'] = self.X
        ret['map'] = self.Map
        ret['xScale'] = self.Xscale
        ret['yScale'] = self.Yscale
        ret['valueName'] = self.ValueName

        return ret

    def restoreData(self):
        if self.dumped:
            ResultFileObj = open(self.dumpFile, "rb")
            self.data = pk.load(ResultFileObj)
            self.dumped = False

    def getData(self):
        if self.dumped:
            self.restoreData()
            return self.data
        else:
            return self.data

    def deleteData(self):
        self.data = None
        
    def setLineColor(self, color):
        self.color = color
    
    def setLineStyle(self, style):
        self.linestyle = style
    
    def setLineWidth(self, width):
        self.linewidth = width

    def getYlabel(self):
        return self.Ylabel

    def getXlabel(self):
        return self.Xlabel

    def getYscale(self):
        return self.Yscale

    def getXscale(self):
        return self.Xscale

    def getWindowTitle(self):
        return self.WindowTitle

    def getX(self):
        return self.X

    def getDieX(self):
        return self.DieX
        
    def getDieY(self):
        return self.DieY
    '''
    def getXMax(self):
        return self.xMax

    def getYMax(self):
        return self.yMax
    '''
    def getMap(self):
        return self.Map

    def getDevX(self):
        return self.DevX

    def getDevY(self):
        return self.DevY

    def getMeasurement(self):
        return self.Measurement

    def getValueName(self):
        return self.ValueName

    def getFolder(self):
        return self.Folder

    def checkID(self, DieX, DieY, DevX, DevY, Typ, ValueName):
        check = True
        if DieX != self.DieX:
            check = False
        if DieY != self.DieY:
            check = False
        if DevY != self.DevY:
            check = False
        if DevX != self.DevX:
            check = False
        if Typ != self.Measurement:
            check = False
        if ValueName != self.ValueName:
            check = False
        return check
    
    def setMaxLength(self, MaxLength = 1e5):
        try:
            self.MaxLength = int(MaxLength)
        except TypeError:
            None
