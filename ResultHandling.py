
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
from matplotlib import lines
from matplotlib import markers
from matplotlib import colors
from PyQt5 import QtWidgets, QtCore, QtGui
import Qt_stdObjects as stdObj
import pickle as pk
import traceback
import numpy as np


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

        self.dieXValues = ['']
        self.dieYValues = ['']
        self.devXValues = ['']
        self.devYValues = ['']
        self.MeasValues = ['']
        self.VarValues = ['']
        self.NumValues = ['Live']

        self.dpi=600
        self.ErrorQu = qu.Queue()

        self.MainGI = MainGI
        self.changed = False
        self.CurResult = None
        self.subResultsID = {}
        self.Configuration = MainGI.Configuration
        self.linestyle = self.Configuration.getValue("ResultGraphStyle")
        self.linewidth  = self.Configuration.getValue("ResultGraphWidth")
        self.linecolor = self.Configuration.getValue("ResultGraphColor")
        self.xScale = 'lin'
        self.yScale = 'lin'
        self.legend = None
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
        
        return not self.thread.is_alive()

    def is_alive(self):
        return self.thread.is_alive()


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
            if len(list(self.subResultsID.keys())) > 0:
                self.CurResult = self.subResultsID['Live']
        else:
            disCont = False
            if not disCont and len(list(self.subResultsID.keys())) > 0:
                self.CurResult = self.subResultsID[val]
        
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
            return self.Results[self.CurResult-1]

    def getTraceData(self):
        None

    def getGraphProperties(self):
        None

    def getResultSize(self):
        return len(list(self.subResultsID.keys()))

    def updateDieX(self):
        Xar = []
        for res in self.Results:
            X = res['DieX']
            if not X in [int(x) for x in Xar]:
                Xar.append(X)
        
        Xar.sort()
        Xar.insert(0,'')

        self.dieXValues = Xar
        return Xar

    def updateDieY(self):
        Yar = []
        for res in self.Results:
            Y = res['DieY']
            if not int(Y) in [int(y) for y in Yar]:
                Yar.append(Y)

        Yar.sort()
        Yar.insert(0,'')
        self.dieYValues = Yar
        return Yar

    def updateDevX(self):
        
        Xar = []
        for res in self.Results:

            Xdie = res['DieX']
            Ydie = res['DieY']

            Xdev = res['DevX']
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
            
            if not int(Xdev) in [int(x) for x in Xar] and addX and addY:
                Xar.append(Xdev)

        Xar.sort()
        Xar.insert(0,'')
        self.devXValues = Xar
        return Xar

    def updateDevY(self):
        
        Yar = []
        for res in self.Results:
            Xdie = res['DieX']
            Ydie = res['DieY']

            Xdev = res['DevX']
            Ydev = res['DevY']
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
                    
            if not (int(Ydev) in [int(y) for y in Yar]) and addX and addY:
                Yar.append(Ydev)

        Yar.sort()
        Yar.insert(0,'')
        self.devYValues = Yar
        return Yar

    def updateMeasurements(self):
        
        Meas = []
        for res in self.Results:
            M = res['Result'].getMeasurements()

            Xdie = res['DieX']
            Ydie = res['DieY']
            Xdev = res['DevX']
            Ydev = res['DevY']

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
                Meas.extend(M)

        Meas.sort()
        Meas.insert(0,'')
        self.MeasValues = Meas
        return Meas
    
    def updateValue(self):
        Val = []
        #del self.subResultsID
        #self.subResultsID = {}
        n = 1
        for res in self.Results:
            V = res['Result'].getValueNames()
            M = res['Result'].getMeasurements()

            Xdie = res['DieX']
            Ydie = res['DieY']
            Xdev = res['DevX']
            Ydev = res['DevY']

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

            if self.CurMeas == '': 
                addMeas = True
            else:
                if self.CurMeas.strip() in [m.strip() for m in M]:
                    addMeas = True

            if addDieX and addDieY and addDevX and addDevY and addMeas:
                Val.extend(V)
                    
                #self.subResultsID.append(n)
                
            n = n+1

        Val.insert(0,'')
        self.VarValues = Val
        return Val

    def updateNum(self):

        Num = []
        del self.subResultsID
        self.subResultsID = {}
        n = 1
        for res in self.Results:

            V = res['Result'].getValueNames()
            M = res['Result'].getMeasurements()

            Xdie = res['DieX']
            Ydie = res['DieY']
            Xdev = res['DevX']
            Ydev = res['DevY']

            addDieX = False
            addDieY = False
            addDevX = False
            addDevY = False
            addMeas = False
            addVal = False

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

            if self.CurMeas == '': 
                addMeas = True
            else:
                if self.CurMeas.strip().lower() in [m.strip().lower() for m in M]:
                    addMeas = True

            if self.CurVal == '': 
                addVal = True
            else:
                if self.CurVal.strip().lower() in [v.strip().lower() for v in V]:
                    addVal = True

            if addDieX and addDieY and addDevX and addDevY and addMeas and addVal:
                txt = "Die X%d-Y%d, Dev X%d-Y%d, %d" %(Xdie, Ydie, Xdev, Ydev, n)
                #txt = n
                Num.append(txt)
                self.subResultsID[txt] = n

            n = n+1
        self.subResultsID['Live'] = 0

        Num.insert(0,'Live')
        self.NumValues = Num
        return self.NumValues

    def clear(self):
        self.Results = []
        self.ID = 0
        self.setLive()
    
        self.dieXValues = ['']
        self.dieYValues = ['']
        self.devXValues = ['']
        self.devYValues = ['']
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

        upd = {'DieX': self.dieXValues}
        upd['DieY'] = self.dieYValues
        upd['DevX'] = self.devXValues
        upd['DevY'] = self.devYValues
        upd['Meas'] = self.MeasValues
        upd['Var'] = self.VarValues
        upd['Num'] = self.NumValues

        self.ResultWindow.updates.put(upd)
        
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

    def filterData(self, data):
        newData = {}

        supportedKeys = ['DieX', 'DieY', "DevX", 'DevY', 'Folder', 'Row', 'Column', 'Rowspan', 'Colspan', 'Xscale', 'Yscale', 'X', 
                            'Measurement', 'ValueName', 'Add', 'Traces', 'Xlabel', 'Ylabel', 'Xunit', 'Yunit', "Clabel", 'Title', 'Map', 'Style', 
                            'LineStyle', 'ScatterStyle', 'LineWidth', 'Size', 'ScatterSize', 'Legend', 'LabelSize']

        equivKeys = {}
        equivKeys['Column'] = ['col']
        equivKeys['Colspan'] = ['columnspan']
        equivKeys['Measurement'] = ['measurementtype', 'type']
        equivKeys['WindowTitle'] = ['title']
        equivKeys['X'] = ['xaxis']
        equivKeys['MapCoordinates'] = ['map']
        equivKeys['ValueName'] = ['vname', "name"]
        equivKeys['Xlabel'] = ["xlab"]
        equivKeys['Ylabel'] = ["ylab", 'label', "lab"]
        equivKeys['Traces'] = ["trac", 'trace']
        equivKeys['Add'] = ['extend', "ext"]
        equivKeys['LineWidth'] = ['width']
        equivKeys['ScatterSize'] = ['size']
        equivKeys['Yunit'] = ['unit', 'units']
        equivKeys['Xunit'] = ['unit', 'units']

        for key, value in data.items():
            for supKey in supportedKeys:
                equivKey = []
                if supKey in list(equivKeys.keys()):
                    equivKey = equivKeys[supKey]
                if key.lower() == supKey.lower() or key.lower() in equivKey:
                    newData[supKey] = value

        return newData

    def retrieveData(self):
        ret = False
        res = None
        Result = None
        eChar = self.MainGI.geteChar()
        
        while not eChar.IVplotData.empty():
            res = None
            ret = True
            data = cp.deepcopy(eChar.IVplotData.get())

            data = self.filterData(data)
            
            kwargs = {}
            necKeys = ['DieX', 'DieY', "DevX", 'DevY', 'Folder', 'Measurement', 'ValueName']

            for key in necKeys:
                if key in data.keys():
                    kwargs[key] = data[key]
            
            addedKeys = ['Row', 'Column', 'Rowspan', 'Colspan']
            stdValues = [-2,-2,1,1]
            for key, value in zip(addedKeys, stdValues):
                kwargs[key] = value
                if key in data.keys():
                    kwargs[key] = data[key]

            row = kwargs['Row']
            column = kwargs['Column']

            extendGraph = False
            if 'Add' in data.keys():
                if data['Add'] == True:
                    for Result in self.Results:
                        #check if a graph exists that can be extended
                        if Result["Result"].compareDevice(row=row, column=column, **kwargs):
                            extendGraph = True
                            break
                    if extendGraph:
                        if not isinstance(data['Traces'], list):
                            data['Traces'] = [data['Traces']]
                        if 'MapCoordinates' in data.keys():
                            Result["Result"].extend(data['Traces'], data['MapCoordinates'], row=row, column=column, valueName=data['ValueName'])
                        else:
                            Result["Result"].extend(data['Traces'], row=row, column=column, valueName=data['ValueName'])
                        res = Result
                                        
            if not extendGraph:
                
                if self.useDumping:
                    #dump data to HDD if it is not the current Device
                    checks = ["CurMeasDieX", "CurMeasDieY", "CurMeasDevX", "CurMeasDevY"]
                    keys = ['DieX', 'DieY', "DevX", 'DevY']
                    for entry in self.Results:
                        if not all([entry[key]==check for check, key in zip([getattr(self, c) for c in checks],keys)]):
                            entry['Result'].dumpData()
                    for check, key in zip(checks, keys):
                        setattr(self, check, kwargs[key])
                
                necKeys = ['Xlabel', 'Ylabel', "Clabel", "LabelSize", "Title", "MapCoordinates", "X", 'ScatterSize', 'LineWidth', 'Legend']
                defaultVal = ['', '', "", None, 'Measurement Data', [None,None], False, None, None, None]
                defaultType = [str, str, str, float, str, None, bool, int, float, str]
                n = 0
                for key, default in zip(necKeys,defaultVal):
                    if key in data.keys():
                        kwargs[key] = data[key]
                    else: 
                        if default != None:
                            if defaultType[n] != None:
                                try:
                                    kwargs[key] = defaultType[n](default)
                                except ValueError:
                                    pass
                            else:
                                kwargs[key] = default
                    n +=1
                                
                key = 'LineStyle'
                if key in data:
                    kwargs[key] = data[key]
                    kwargs["Style"] = "Line"
                    style = 'Line'

                if 'LineWidth' in kwargs:
                    try:
                        kwargs['LineWidth'] = int(data[key])
                    except ValueError:
                        pass

                key = 'ScatterStyle'
                if key in data:
                    kwargs[key] = data[key]
                    kwargs["Style"] = "Scatter"
                
                try:
                    kwargs['Xscale'] = data['Xscale']
                    if not data['Xscale'] in ['lin', "log"]:
                        kwargs['Xscale'] = self.xScale
                except:
                    kwargs['Xscale'] = self.xScale
                     
                try:
                    kwargs['Yscale'] = data['Yscale']
                    if not data['Yscale'] in ['lin', "log"]:
                        kwargs['Yscale'] = self.yScale
                except:
                    kwargs['Yscale'] = self.yScale

                if not isinstance(data['Traces'], list):
                    data['Traces'] = [data['Traces']]

                for key, value in data.items():
                    if key != "Traces" and not (key in kwargs.keys()):
                        kwargs[key] = data[key]

                if row == -2 or column == -2 or len(self.Results) == 0:
                    res = {'DieX': kwargs['DieX'], 'DieY': kwargs['DieY'], "DevX": kwargs['DevX'], 'DevY': kwargs['DevY'], "Result": MeasurementResult(data['Traces'], self.ErrorQu, **kwargs)}
                    self.Results.append(res)
                else:
                    sucAdd = self.Results[-1]['Result'].add(data['Traces'], row, column, **kwargs)
                    if not sucAdd:
                        res = {'DieX': kwargs['DieX'], 'DieY': kwargs['DieY'], "DevX": kwargs['DevX'], 'DevY': kwargs['DevY'], "Result": MeasurementResult(data['Traces'], self.ErrorQu, **kwargs)}
                        self.Results.append(res)
                
                self.updateCurFile(res)

                updKwargs = {}
                necKeys = ['DieX', 'DieY', "DevX", 'DevY']
                upds = [self.updateDieX, self.updateDieY, self.updateDevX, self.updateDevY]
                for key, upd in zip(necKeys, upds):
                    updKwargs[key] = upd()
                updKwargs['Meas'] = self.updateMeasurements()
                updKwargs['Num'] = self.updateNum()
                updKwargs['Val'] = self.updateValue()
                self.ResultWindow.updates.put(updKwargs)

            self.ResultWindow.updates.put({"Show": True})

            if self.Live and res != None:
                self.updateResultWindowGraph(res['Result'])
               
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
                        dieY = self.updateDieY()
                        devX = self.updateDevX()
                        devY = self.updateDevY()
                        meas = self.updateMeasurements()
                        num = self.updateNum()
                        val = self.updateValue()
                        upd = {"DieY": dieY,"DevX": devX,"DevY": devY,"Meas": meas, "Num": num, "Val": val}
                    elif key == "DieY":
                        self.setCurDieY(item)
                        devX = self.updateDevX()
                        devY = self.updateDevY()
                        meas = self.updateMeasurements()
                        num = self.updateNum()
                        val = self.updateValue()
                        upd = {"DevX": devX,"DevY": devY,"Meas": meas, "Num": num, "Val": val}
                    elif key == "DevX":
                        self.setCurDevX(item)
                        devY = self.updateDevY()
                        meas = self.updateMeasurements()
                        num = self.updateNum()
                        val = self.updateValue()
                        upd = {"DevY": devY,"Meas": meas, "Num": num, "Val": val}
                    elif key == "DevY":
                        self.setCurDevY(item)
                        meas = self.updateMeasurements()
                        num = self.updateNum()
                        val = self.updateValue()
                        upd = {"Meas": meas, "Num": num, "Val": val}
                    elif key == "Meas":
                        self.setCurMeas(item)
                        num = self.updateNum()
                        val = self.updateValue()
                        upd = {"Num": num, "Val": val}
                    elif key == "Val":
                        self.setCurVal(item)
                        num = self.updateNum()
                        upd = {"Num": num}
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
                        if key == "LineColor":
                            self.getResult().setLineColor(item)
                        elif key == 'LineStyle':
                            self.getResult().setLineStyle(item)
                        elif key == 'LineWidth':
                            self.getResult().setLineWidth(item)
                        elif key == 'LineSize':
                            self.getResult().setLineWidth(item)

                if upd != None:
                    self.ResultWindow.updates.put(upd)
                    self.updateCurFile(self.getResult())
                
                if updData:
                    res = self.getResult()
                    if res != None:
                        self.updateResultWindowGraph(res['Result'])

            tm.sleep(0.2)

    def updateResultWindowGraph(self, resultClass):
        if resultClass != None:
            self.ResultWindow.updates.put({"GraphData": resultClass.createGraphProp()})

    def updateCurFile(self, res):
        if res != None:
            folder = res['Result'].getFolder()
            fileName = res['Result'].getFilename()
            self.ResultWindow.updates.put({'fileName': fileName, "folder":folder})


class MeasurementResult():

    def __init__(self, data, errorQueue, row=-1, column=-1, rowspan=1, colspan=1, MaxLength=2.5e5, **kwargs):
        
        # row or column at -2 indicates one plot per graph
        # row or column at -1 indicates automatically adding plots to graphs 

        self.maxLength = int(MaxLength)
        self.dumpFile = ""
        self.dumped = False

        self.errorQueue = errorQueue

        colspan = 1
        rowspan = 1

        self.data = []
        self.dataInfo = []
        dataInfo = {}
        dataInfo["Row"] = row
        dataInfo["Column"] = column
        dataInfo["Rowspan"] = rowspan
        dataInfo["Colspan"] = colspan

        self.commonKeys = ['DieX', 'DieY', 'DevX', 'DevY', "Measurement"]
        self.commonInfo = {}

        self.graphPropKeys = list(kwargs.keys())
        self.graphPropKeys.extend(['Row', 'Column', 'Rowspan', 'Colspan', 'Map'])
        for key, value in kwargs.items():
            if key in self.commonKeys:
                self.commonInfo[key] = value
            dataInfo[key] = value
        
        if dataInfo['MapCoordinates'][0] == None or dataInfo['MapCoordinates'][1] == None:
            dataInfo["Map"] = False
            self.data.append(np.array(data, dtype=float))
        else:
            dataInfo["Map"] = True
            dataShape = (dataInfo['MapCoordinates'][0],dataInfo['MapCoordinates'][1])
            self.data.append(np.zeros(dataShape, dtype=float))
            self.data[-1][dataInfo['MapCoordinates'][0]][dataInfo['MapCoordinates'][1]] = data[0]

        self.dataInfo.append(dataInfo)
    
    def isDataDumped(self):
        return self.dumped

    def putErrorQueue(self, msg):
        msg = "MeasurementResult: %s" %(msg)
        self.errorQueue.put(msg)
    
    def getDataInfoByCell(self, row=-1, column=-1):
        for n, d in enumerate(self.dataInfo):
            rowOcc = d['Row']
            colOcc = d['Column']
            if row == rowOcc and colOcc == column:
                return (n, d)
        return (None, None)

    def getDataByCell(self, row=-1, column=-1):
        n, d = self.getDataInfoByCell(row, column)
        if n != None:
            return cp.deepcopy(self.getData()[n])
        return None


    def getFolder(self):
        return ""

    def getMeasurementAndValueName(self):
        valNames = []
        measNames = []
        for d in self.dataInfo:
            if not d['ValueName'] in valNames:
                valNames.append(d['ValueName'])
                
            if not d['Measurement'] in measNames:
                measNames.append(d['Measurement'])

        ret = "Types_"
        for m in measNames:
            ret = "%s%s_" %(ret, m) 
        ret = "%sValNames__" %(ret) 
        for v in valNames:
            ret = "%s%s_" %(ret, v) 

        return ret

    def getFilename(self, row=-1, column=-1):
        n, dataInfo = self.getDataInfoByCell(row, column)
        if dataInfo == None:
            return ""
        ret = "%sDieX%dY%d_DevX%dY%d_%s" %(self.getMeasurementAndValueName(),  self.commonInfo['DieX'], self.commonInfo['DieY'], self.commonInfo['DevX'], self.commonInfo['DevY'], self.commonInfo['Measurement'])
        return ret
    
    def cellAvailable(self, row, column, rowspan, colspan):
        avail = True
        for d in self.dataInfo:
            avail = False
            rowOcc = d['Row']
            colOcc = d['Column']
            rowSpanOcc = d['Rowspan']
            colSpanOcc = d['Colspan']

            if rowOcc == -2 or colOcc == -2:
                return False

            if row > (rowOcc+rowSpanOcc - 1) or (row + rowspan - 1) < rowOcc:
                continue

            
            if column > (colOcc+colSpanOcc - 1) or (column + colspan - 1) < colOcc:
                continue

            return False
        
        return True

    def add(self, data, row, column, rowspan=1, colspan=1, **kwargs):
        
        if not self.compareDevice(row, column, checkValueName=False, **kwargs):
            return False
        if not self.cellAvailable(row, column, rowspan, colspan):
            return False
        
        try:
            dataInfo = {}
            dataInfo["Row"] = row
            dataInfo["Column"] = column
            dataInfo["Rowspan"] = rowspan
            dataInfo["Colspan"] = colspan

            self.graphPropKeys = list(kwargs.keys())
            self.graphPropKeys.extend(['Row', 'Column', 'Rowspan', 'Colspan', "Map"])
            for key, value in kwargs.items():
                setattr(self, key, value)
                dataInfo[key] = value
            
            if dataInfo['MapCoordinates'][0] == None or dataInfo['MapCoordinates'][1] == None:
                dataInfo["Map"] = False
                self.data.append(np.array(data, dtype=float))
            else:
                dataInfo["Map"] = True
                dataShape = (dataInfo['MapCoordinates'][0],dataInfo['MapCoordinates'][1])
                self.data.append(np.zeros(dataShape, dtype=float))
                self.data[-1][dataInfo['MapCoordinates'][0]][dataInfo['MapCoordinates'][1]] = data[0]

            self.dataInfo.append(dataInfo)

        except Exception as e:
            print(traceback.format_exc())
            self.putErrorQueue("Extend Data: Error: %s" %(e))
            return False               
        
        return True
            
    def isDataInCell(self, row, column, valueName):
        for d in self.dataInfo:
            rowOcc = d['Row']
            colOcc = d['Column']
            valueNameOcc = d['ValueName']
            if row == rowOcc and colOcc == column and valueNameOcc == valueName:
                return True

        return False

    def getOccupiedCells(self):
        cells = []
        for d in self.dataInfo:
            rowOcc = d['Row']
            colOcc = d['Column']
            rowSpanOcc = d['Rowspan']
            colSpanOcc = d['Colspan']
            cell = {}
            cell["Row"] = rowOcc
            cell["Column"] = colOcc
            cell["Rowspan"] = rowSpanOcc
            cell["Colspan"] = colSpanOcc
            cells.append(cell)
        return cells
        

    def extend(self, data, row=-1, column=-1, valueName=""):
        
        if self.isDataDumped():
            self.restoreData()

        if not self.isDataInCell(row, column, valueName):
            return False

        if not isinstance(data, np.ndarray):
            data = np.array(data, dtype=float)

        n, dataInfo = self.getDataInfoByCell(row, column)
        
        MapCoordinates = dataInfo['MapCoordinates']
        Map = dataInfo['Map']
        
        try:
            if not Map:
                orgShape = np.shape(self.data[n])
                newShape = np.shape(data)

                if len(orgShape) == 3:
                    if np.shape(data)[1] != np.shape(self.data[n])[1] or np.shape(data)[2] != np.shape(self.data[n])[2]:
                        self.putErrorQueue("Extend Data: Measurement Data can only be extended if the Data dimensions are the same. OrigShape: %s, NewShape: %s" %(orgShape, newShape))
                        return False
                    
                    self.data[n] = np.append(self.data[n], data, axis=0)

                elif len(orgShape) == 2:
                    newShape = (orgShape[0], orgShape[1] + newShape[1])
                    tempData = np.empty(newShape, dtype=float)
                    for m in range(orgShape[0]):
                        tempData[m][0:orgShape[1]] = self.data[n][m]
                        tempData[m][orgShape[1]:] = data[m]
                    self.data[n] = tempData
                else:
                    if np.shape(data)[0] > self.maxLength:
                        tempData = np.array(data[-self.maxLength:])
                    elif (np.shape(self.data[n])[0] + np.shape(data)[0]) > self.maxLength:
                        self.data[n] = np.delete(self.data[n], np.s_[:np.shape(self.data[n])[0]-(self.maxLength-np.shape(data)[0])])
                        newShape = orgShape[0] + newShape[0]
                        tempData = np.empty(newShape, dtype=float)
                        tempData[0:orgShape[0]] = self.data[n]
                        tempData[orgShape[0]:] = data
                    else:
                        newShape = orgShape[0] + newShape[0]
                        tempData = np.empty(newShape, dtype=float)
                        tempData[0:orgShape[0]] = self.data[n]
                        tempData[orgShape[0]:] = data
                    
                    self.data[n] = tempData
            else:
                if isinstance(MapCoordinates, list):
                    if MapCoordinates[0] != None and MapCoordinates[1] != None:
                        while len(self.data[n]) < MapCoordinates[0]+1:
                            self.data[n].append([])
                        
                        while len(self.data[n][MapCoordinates[0]]) < MapCoordinates[1]+1:
                            self.data[n][MapCoordinates[0]].append(None)

                        self.data[n][MapCoordinates[0]][MapCoordinates[1]] = data[0]
            
        except Exception as e:
            print(traceback.format_exc())
            self.putErrorQueue("Extend Data: Error: %s" %(e))
            return False               

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
        dataInfo= cp.deepcopy(self.dataInfo)
        ret['GraphInfo'] = dataInfo
        ret['Data'] = self.getData()
        ret['Filename'] = self.getFilename()
        ret['Folder'] = self.getFolder()
        return ret

    def restoreData(self):
        if self.dumped:
            ResultFileObj = open(self.dumpFile, "rb")
            self.data = pk.load(ResultFileObj)
            self.dumped = False

    def getDataInfo(self, row=-1, column=-1):
        return self.dataInfo

    def getData(self, row=-1, column=-1):
        if self.isDataDumped():
            self.restoreData()
            return self.data
        return self.data

    def deleteData(self):
        del self.data
        self.data = None

    def compareDevice(self, row=-1, column=-1, checkValueName=True, **kwargs):
        for key, value in self.commonInfo.items():
            if key in kwargs.keys():
                if kwargs[key] != value:
                    return False 
            else:
                return False
        if not checkValueName:
            return True

        found = False
        for d in self.dataInfo:
            if d['Row'] == row and d['Column'] == column:       
                if "ValueName" in kwargs.keys():
                    if kwargs['ValueName'] != d['ValueName']:
                        return False
                else:
                    return False
                found = True
        return found
    
    def setMaxLength(self, MaxLength = 1e5):
        try:
            self.maxLength = int(MaxLength)
        except TypeError:
            None
    
    def getValueNames(self):
        valName = []
        for dataInfo in self.dataInfo:
            if not dataInfo['ValueName'] in valName:
                valName.append(dataInfo['ValueName'])
        return valName

    def getMeasurements(self):
        meas = []
        for dataInfo in self.dataInfo:
            if not dataInfo['Measurement'] in meas:
                meas.append(dataInfo['Measurement'])
        return meas