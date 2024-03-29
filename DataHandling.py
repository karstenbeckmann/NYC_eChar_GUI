"""
Written by: Karsten Beckmann and Maximillian Liehr
Institution: SUNY Polytechnic Institute
Date: 6/12/2018

DataHandling provides classes that deal with the statistical evaluation of the retrieved data.  
"""

import os as os
import pathlib as path
import csv as csv
import time as tm
import numpy as np
import math as ma
import sys
import statistics as stat
import StdDefinitions as std
import threading as th
import inspect as ip
import copy as cp

class Value:

    def __init__(self, eChar, InputValue , Name, Unit=None, DoYield=False):
        
        self.Name = Name
        self.average = ""
        self.averageSq = ''
        self.averageN = 1
        self.stdDeviation = ''
        self.minimum = ''
        self.maximum = ''
        self.screened = False
        self.size = 0
        self.SpecCode = ''
        self.Unit = ""
        self.Values = []
        self.ValOverFlow = False
        self.MaxValuesLength = 1e7

        self.FailPerc = 0
        self.FailCycle = 1
        self.FailCycleSq = 0
        self.FailCycleStdDev = 0

        self.FailSpec = False

        self.ContainValues = False
        self.Spec = None

        self.DoYield = False
        self.Low = ''
        self.High = ''

        self.NumOfDevices = 0
        if isinstance(InputValue, type(None)):
            InputValue = []

        Specs = eChar.getConfiguration().getSpecs()
        self.SpecCode = eChar.getConfiguration().getSpecCode()
        self.DoYield = DoYield
        if not isinstance(Specs, type([])):
            self.DoYield = False
        else:
            if len(Specs) == 0:
                self.DoYield = False

        n=0
        if self.DoYield:
            for entry in Specs:
                if Name.strip() == entry['Name'].strip():
                    if n==0:
                        self.Spec = entry
                    else:
                        eChar.ErrorQueue.put("More than one Spec exists for SpecName %s with specCode: %s" %(Name, self.SpecCode))
                    n=n+1
            if self.Spec == None:
                self.DoYield = False
        
        if isinstance(InputValue, list) or isinstance(InputValue, np.ndarray):
            if isinstance(InputValue, np.ndarray):
                length = np.size(InputValue)
            else:
                length = len(InputValue)

            if length > 0:
                if self.DoYield:
                    n = 1
                    InValNP = np.empty(0)

                    for val in InputValue:
                        if self.Spec['YieldHigh'] < val or val < self.Spec['YieldLow']:
                            self.FailPerc = 1
                            self.FailCycle = n
                            self.FailCycleSq = n*n
                            self.FailCycleStdDev = 0
                            break
                        n+=1
                        
                        if self.Spec['SpecLow']  < val and val < self.Spec['SpecHigh']:
                            InValNP = np.append(InValNP,val)
                        else:
                            self.FailSpec = True
                            break

                        if np.size(InValNP) > 0:
                            self.size = np.size(InValNP)
                            self.average = np.average(InValNP)
                            self.averageSq = np.average(np.square(InValNP))
                            self.averageN = 1
                            self.stdDeviation = np.std(InValNP)
                            self.minimum = np.min(InValNP)
                            self.maximum = np.max(InValNP)
                            self.ContainValues = True
                            self.addValues(InputValue)


                else:
                    InValNP = np.array(InputValue[:])
                    self.size = np.size(InValNP)
                    self.average = np.average(InValNP)
                    self.averageSq = np.average(np.square(InValNP))
                    self.averageN = 1
                    self.stdDeviation = np.std(InValNP)
                    self.minimum = np.min(InValNP)
                    self.maximum = np.max(InValNP)
                    self.ContainValues = True
                    self.addValues(InputValue)

        else:
            if self.DoYield:
                if self.Spec['YieldHigh'] < InputValue or InputValue < self.Spec['YieldLow']:
                    self.FailPerc = 1
                    self.FailCycle = 1
                    self.FailCycleSq = 1
                    self.FailCycleStdDev = 0
                
                if self.Spec['SpecLow']  < InputValue and InputValue < self.Spec['SpecHigh']:
                    self.size = 1
                    self.average = InputValue
                    self.averageSq = np.square(InputValue)
                    self.averageN = 1
                    self.stdDeviation = 0
                    self.maximum = InputValue
                    self.minimum = InputValue
                    self.ContainValues = True
                    self.addValues(InputValue)
                else:
                    self.FailSpec = True

            else:
                self.size = 1
                self.average = InputValue
                self.averageSq = np.square(InputValue)
                self.averageN = 1
                self.stdDeviation = 0
                self.maximum = InputValue
                self.minimum = InputValue
                self.ContainValues = True
                self.addValues(InputValue)

        self.NumOfDevices = 1
        if Unit != None:
            print(Unit)
            self.Unit = Unit

    def addValues(self, values):

        if self.ValOverFlow:
            return False

        if not isinstance(values, list):
            values = [values]
        
        InpValLen = len(values)
        ValLen = len(self.Values)

        if (InpValLen + ValLen) > self.MaxValuesLength:
            self.Values = None
            self.ValOverFlow = True
        else:
            if isinstance(values, list):
                self.Values.extend(values)
            else:
                self.Values.append(values)
        return True

    def getName(self):
        return self.Name

    def getUnit(self):
        return self.Unit

    def get95thPercentile(self):
        if self.ValOverFlow:
            return None
        else:
            try:
                ret = float(np.percentile(self.Values, 95))
            except IndexError:
                ret = None
            return ret


    def getMedian(self):
        if self.ValOverFlow:
            return None
        else:
            try:
                ret = float(np.median(self.Values))
            except IndexError:
                ret = None
            return ret

    def get5thPercentile(self):
        if self.ValOverFlow:
            return None
        else:
            try:
                ret = float(np.percentile(self.Values, 5))
            except IndexError:
                ret = None
            return ret

    def get1thPercentile(self):
        if self.ValOverFlow:
            return None
        else:
            try:
                ret = float(np.percentile(self.Values, 1))
            except IndexError:
                ret = None
            return ret
            
    def get99thPercentile(self):
        if self.ValOverFlow:
            return None
        else:
            try:
                ret = float(np.percentile(self.Values, 99))
            except IndexError:
                ret = None
            return ret

    def getSize(self):
        return self.size

    def getAverage(self):
        try:
            return float(self.average)
        except:
            return ""

    def getAverageSquare(self):
        try:
            return float(self.averageSq)
        except:
            return ""

    def getStdDeviation(self):
        try:
            return float(self.stdDeviation)
        except:
            return ""

    def getMinimum(self):
        try:
            return float(self.minimum)
        except:
            return 0

    def getMaximum(self):
        try:
            return float(self.maximum)
        except:
            return ""

    def getNumberOfDevices(self):
        return int(self.NumOfDevices)

    def getYield(self):
        return (1 - float(self.FailPerc))
    
    def getFailedPercentage(self):
        return float(self.FailPerc)

    def getDidYield(self):
        return self.DoYield
    
    def getCycleFailedStdDev(self):
        return self.FailCycleStdDev

    def getCycleFailed(self):
        return self.FailCycle

    def getSpecHigh(self):
        return float(self.Spec['SpecHigh'])
    
    def getSpecLow(self):
        return float(self.Spec['SpecLow'])

    def getYieldHigh(self):
        return float(self.Spec['YieldHigh'])
    
    def getYieldLow(self):
        return float(self.Spec['YieldLow'])

    def getTarget(self):
        return float(self.Spec['Target'])

    def extend(self, InputValue):
        
        if self.NumOfDevices > 1: 
            return None

        if self.FailSpec:
            return False
        
        if self.DoYield:
            InValNP = np.empty(0)
            if isinstance(InputValue, list) or isinstance(InputValue, np.ndarray):
                if isinstance(InputValue, np.ndarray):
                    if len(np.shape(InputValue)) > 1:
                        return False

                n= 0
                for val in InputValue:
                    if self.Spec['YieldHigh'] < val < self.Spec['YieldLow']:
                        self.FailPerc = 1
                        self.FailCycle = n + self.size
                        self.FailCycleSq = self.FailCycle * self.FailCycle
                        self.FailCycleStdDev = 0
                        break
                    n=n+1
                        
                    if self.Spec['SpecLow'] < val < self.Spec['SpecHigh']:
                        InValNP = np.append(InValNP,val)
                    self.FailSpec = True

            else:
                if self.Spec['YieldHigh'] < InputValue < self.Spec['YieldLow']:
                    self.FailPerc = 1
                    self.FailCycle = 1+self.size
                    self.FailCycleSq = self.FailCycle*self.FailCycle
                    self.FailCycleStdDev = 0

                if self.Spec['SpecLow'] < InputValue < self.Spec['SpecHigh']:
                    InValNP = np.append(InValNP,InputValue)
                else:
                    self.FailSpec = True
                

        else: 
            if isinstance(InputValue, list) or isinstance(InputValue, np.ndarray):
                if isinstance(InputValue, np.ndarray):
                    if len(np.shape(InputValue)) > 1:
                        return False
                    InValNP = InputValue
                else:    
                    InValNP = np.array(InputValue)
            else:
                InValNP = np.array([InputValue])

        l = np.size(InValNP)
        if self.ContainValues:
            InputAvg = np.average(InValNP)
            x = np.multiply(InputAvg, l)
            y = np.multiply(self.average,self.size)
            z = np.add(self.size, l)
            self.average = np.divide(np.sum([x,y]),z)

            InputAvgSq = np.average(np.square(InValNP))
            self.averageSq  = np.add(InputAvgSq, self.averageSq)
            self.averageN = self.averageN + 1

            self.stdDeviation = np.sqrt(np.absolute(np.subtract(np.divide(self.averageSq,self.averageN), np.square(self.average))))

            self.size = self.size + l
            self.addValues(InputValue)

            try:
                newMin = np.min(InValNP)
                if self.minimum > newMin:
                    self.minimum = newMin

                newMax = np.max(InValNP)
                if self.maximum < newMax:
                    self.maximum = newMax
            except ValueError:
                None

        else:
            if l > 0:
                if isinstance(InputValue, list) or isinstance(InputValue, np.ndarray):
                    if isinstance(InputValue, np.ndarray):
                        if len(np.shape(InputValue)) > 1:
                            return False
                        InValNP = InputValue
                    else:    
                        InValNP = np.array(InputValue)
                else:
                    InValNP = np.array([InputValue])
                self.size = np.size(InValNP)
                self.average = np.average(InValNP)
                self.averageSq = np.average(np.square(InValNP))
                self.averageN = 1
                self.stdDeviation = np.std(InValNP)
                self.minimum = np.min(InValNP)
                self.maximum = np.max(InValNP)
                self.ContainValues = True
                self.addValues(InputValue)
        
        if self.FailPerc > 0: 
            return False
        else:
            return True

    def getContainValues(self):
        return self.ContainValues

    def combine(self, newVal):
        
        if newVal.getContainValues() and self.getContainValues():
            x = np.multiply(newVal.average,newVal.size)
            y = np.multiply(self.average, self.size)
            z = np.add(self.size, newVal.size)
            self.average = np.divide(np.sum([x,y]),z)
            x = np.add(newVal.averageSq, self.averageSq)
            y = np.multiply(self.averageSq,self.size)
            self.averageSq = np.divide(np.sum([x,y]),z)
            
            self.stdDeviation = np.sqrt(np.absolute(np.subtract(np.divide(self.averageSq,self.averageN), np.square(self.average))))
            #print("after: ",self.stdDeviation)
            self.size = self.size + newVal.size

            if self.minimum > newVal.minimum:
                self.minimum = newVal.minimum

            if self.maximum < newVal.maximum:
                self.maximum = newVal.maximum
            
            self.NumOfDevices += newVal.NumOfDevices
            
            self.addValues(newVal.Values)
            
        elif newVal.getContainValues():
            self.size = newVal.getSize()
            self.average = newVal.getAverage()
            self.averageSq = newVal.getAverageSquare()
            self.stdDeviation = newVal.getStdDeviation()
            self.minimum = newVal.getMinimum()
            self.maximum = newVal.getMaximum()
            self.Values = newVal.Values
            self.ContainValues = True

class Row:

    def __init__(self,ValueList=[],DieX=None,DieY=None,DeviceX=None,DeviceY=None, MatNormal=None, MatBit=None, MeasType=None,StCycle=None,EndCycle=None):
    
        self.ValueList = cp.deepcopy(ValueList)
        self.DieX = DieX
        self.DieY = DieY
        self.DevX = DeviceX
        self.DevY = DeviceY
        self.MatBit = MatBit
        self.MatNormal = MatNormal
        self.MeasType = MeasType

        if StCycle == None or EndCycle == None:
            self.StCycle = 0
            self.EndCycle = 0
        else:
            self.StCycle = StCycle
            self.EndCycle = EndCycle

        self.empty = True
        
        self.FailPerc = 0
        self.FailCycle = -1
        self.FailCycleSq = 0 
        self.FailCycleN  = 1
        self.FailCycleStdDev = 0

        self.NumOfDevices = 0

        self.didYield = False
        
        if not ValueList == []:
            self.empty = False

        FailCycles = []

        for value in ValueList:
            
            if value.getDidYield():
                if value.getFailedPercentage() == float(1): 
                    self.FailPerc = 1
                    FailCycles.append(value.getCycleFailed())
                    
        if len(FailCycles) > 0:
            self.didYield = True
            self.FailCycle = min(FailCycles)
            self.FailCycleSq = self.FailCycle*self.FailCycle
            self.FailCycleN = 1

    def getDidYield(self):
        dY = False
        for val in self.ValueList:
            if val.getDidYield():
                dY = True
                break
        return dY

    def CombineRow(self, addRow, MultDev=False):

        if MultDev:
            self.NumOfDevices = self.NumOfDevices + 1

        if self.empty:
            self.ValueList = cp.deepcopy(addRow.ValueList)
            self.DieX = addRow.DieX
            self.DieY = addRow.DieY
            self.DevX = addRow.DevX
            self.DevY = addRow.DevY
            self.MatBit = addRow.MatBit
            self.MatNormal = addRow.MatNormal
            self.MeasType = addRow.MeasType
            self.StCycle = addRow.StCycle
            self.EndCycle = addRow.EndCycle
            self.FailPerc = addRow.FailPerc
            self.FailCycle = addRow.FailCycle
            self.FailCycleSq = addRow.FailCycleSq
            self.FailCycleStdDev = addRow.FailCycleStdDev
            self.FailCycleN = addRow.FailCycleN
            self.empty = False
        else:
            for addVal in addRow.ValueList:
                containing = False
                for n in range(len(self.ValueList)):
                    if addVal.getName() == self.ValueList[n].getName():
                        self.ValueList[n].combine(addVal)
                        containing = True

                if containing == False:
                    self.ValueList.append(addVal)

            if not self.MeasType == addRow.MeasType:
                self.MeasType = 'Combined'
            if self.StCycle > addRow.StCycle:
                self.StCycle = addRow.StCycle
            if self.EndCycle < addRow.EndCycle:
                self.EndCycle = addRow.EndCycle
            if not self.DieX == addRow.DieX:
                self.DieX = None
            if not self.DieY == addRow.DieY:
                self.DieY = None
            if not self.DevX == addRow.DevX:
                self.DevX = None
            if not self.DevY == addRow.DevY:
                self.DevY = None
            if not self.MatBit == addRow.MatBit:
                self.MatBit = None
            if not self.MatNormal == addRow.MatNormal:
                self.MatNormal = None

            if MultDev:
                x = np.multiply(addRow.FailPerc,addRow.NumOfDevices)
                y = np.multiply(self.FailPerc, self.NumOfDevices)
                z = np.add(self.NumOfDevices, addRow.NumOfDevices)
                self.FailPerc = np.divide(np.sum([x,y]),z)
                
                x = np.multiply(addRow.FailCycle,addRow.NumOfDevices)
                y = np.multiply(self.FailCycle, self.NumOfDevices)
                z = np.add(self.NumOfDevices, addRow.NumOfDevices)
                self.FailCycle = np.divide(np.sum([x,y]),z)
                
                self.FailCycleSq = np.add(addRow.FailCycleSq, self.FailCycleSq)
                self.FailCycleN = self.FailCycleN + addRow.FailCycleN

                self.FailCycleStdDev = np.sqrt(abs(np.subtract(np.divide(self.FailCycleSq, self.FailCycleN), np.square(self.FailCycle))))

            else:
                if addRow.FailPerc == float(1):
                    self.FailPerc = 1
                if self.FailPerc == float(1):
                    if self.FailCycle == -1:
                        self.FailCycle = addRow.FailCycle
                        self.FailCycleSq = addRow.FailCycleSq
                        self.FailCycleN = addRow.FailCycleN
                        self.FailCycleStdDev = addRow.FailCycleStdDev

    def CombineRows(self, addRows, MultDev=False):
        
        for addRow in addRows:
            #print("Std. ", addRow.ValueList[0].stdDeviation)
            
            if MultDev:
                self.NumOfDevices = self.NumOfDevices + 1

            if self.empty:
                self.ValueList = addRow.ValueList
                self.DieX = addRow.DieX
                self.DieY = addRow.DieY
                self.DevX = addRow.DevX
                self.DevY = addRow.DevY
                self.MatBit = addRow.MatBit
                self.MatNormal = addRow.MatNormal
                self.MeasType = addRow.MeasType
                self.StCycle = addRow.StCycle
                self.EndCycle = addRow.EndCycle
                self.FailPerc = addRow.FailPerc
                self.FailCycle = addRow.FailCycle
                self.FailCycleSq = addRow.FailCycleSq
                self.FailCycleStdDev = addRow.FailCycleStdDev
                self.empty = False
            else:
                for addVal in addRow.ValueList:
                    containing = False
                    for n in range(len(self.ValueList)):
                        if addVal.getName() == self.ValueList[n].getName():
                            self.ValueList[n].combine(addVal)
                            containing = True

                    if containing == False:
                        ValCopy = cp.deepcopy(addVal)
                        self.ValueList.append(ValCopy)

                if not self.MeasType == addRow.MeasType:
                    self.MeasType = 'Combined'
                if self.StCycle > addRow.StCycle:
                    self.StCycle = addRow.StCycle
                if self.EndCycle < addRow.EndCycle:
                    self.EndCycle = addRow.EndCycle
                if not self.DieX == addRow.DieX:
                    self.DieX = None
                if not self.DieY == addRow.DieY:
                    self.DieY = None
                if not self.DevX == addRow.DevX:
                    self.DevX = None
                if not self.DevY == addRow.DevY:
                    self.DevY = None
                if not self.MatBit == addRow.MatBit:
                    self.MatBit = None
                if not self.MatNormal == addRow.MatNormal:
                    self.MatNormal = None
                
                if MultDev:
                    x = np.multiply(addRow.FailPerc,addRow.NumOfDevices)
                    y = np.multiply(self.FailPerc, self.NumOfDevices)
                    z = np.add(self.NumOfDevices, addRow.NumOfDevices)
                    self.FailPerc = np.divide(np.sum([x,y]),z)
                    
                    x = np.multiply(addRow.FailCycle,addRow.NumOfDevices)
                    y = np.multiply(self.FailCycle, self.NumOfDevices)
                    z = np.add(self.NumOfDevices, addRow.NumOfDevices)
                    self.FailCycle = np.divide(np.sum([x,y]),z)
                    
                    self.FailCycleSq = np.add(addRow.FailCycleSq, self.FailCycleSq)
                    self.FailCycleN = self.FailCycleN + addRow.FailCycleN
                    
                    self.FailCycleStdDev = np.sqrt(abs(np.subtract(np.divide(self.FailCycleSq, self.FailCycleN), np.square(self.FailCycle))))

                else:
                    if addRow.FailPerc == float(1):
                        self.FailPerc = 1
                    if self.FailPerc == float(1):
                        if self.FailCycle == -1:
                            self.FailCycle = addRow.FailCycle
                            self.FailCycleSq = addRow.FailCycleSq
                            self.FailCycleN = addRow.FailCycleN
                            self.FailCycleStdDev = addRow.FailCycleStdDev
    '''
    def getRowString(self,avg=True,StdDev=True,Max=False,Min=False,Yield=False):

        string = 'DataValue'

        for value in self.ValueList:
            
            if avg:
                if isinstance(value.getAverage(), (float,int)):
                    string = "%s,%.2E" %(string,value.getAverage())
                else:
                    string = "%s,%s" %(string,value.getAverage())
            if StdDev:
                if isinstance(value.getStdDeviation(), (float,int)):
                    string = "%s,%.2E" %(string,value.getStdDeviation())
                else:
                    string = "%s,%s" %(string,value.getStdDeviation())
            if Min: 
                if isinstance(value.getMinimum(), (float,int)):
                    string = "%s,%.2E" %(string,value.getMinimum())
                else:
                    string = "%s,%s" %(string,value.getMinimum())
            if Max:
                if isinstance(value.getMaximum(), (float,int)):
                    string = "%s,%.2E" %(string,value.getMaximum())
                else:
                    string = "%s,%s" %(string,value.getMaximum())
            if Yield and value.DoYield:
                string = "%s,%.2f,%.2E,%.2E,%.2E" %(string,value.getYield(),value.target(), value.getYieldHigh(),value.getYieldLow())
                string = "%s,%d,%d" %(string, int(value.getCycleFailed), int(value.getCycleFailedStdDev()))

        return string
    '''

    def getListValString(self,avg=True,StdDev=True,Med=True,perc95=True,perc5=True,perc99=False,perc1=False,Max=False,Min=False,Yield=False,):
    
        stringList = []
        NameList = []

        for value in self.ValueList:
            NameList.append(value.getName())
            string = ''
            if avg:
                if isinstance(value.getAverage(), (float,int)):
                    string = "%s,%.2E" %(string,value.getAverage())
                else:
                    string = "%s,%s" %(string,value.getAverage())
            if StdDev:
                if isinstance(value.getStdDeviation(), (float,int)):
                    string = "%s,%.2E" %(string,value.getStdDeviation())
                else:
                    string = "%s,%s" %(string,value.getStdDeviation())
            if Min: 
                if isinstance(value.getMinimum(), (float,int)):
                    string = "%s,%.2E" %(string,value.getMinimum())
                else:
                    string = "%s,%s" %(string,value.getMinimum())
            if Max:
                if isinstance(value.getMaximum(), (float,int)):
                    string = "%s,%.2E" %(string,value.getMaximum())
                else:
                    string = "%s,%s" %(string,value.getMaximum())
            if Med:
                if isinstance(value.getMedian(), (float,int)):
                    string = "%s,%.2E" %(string,value.getMedian())
                else:
                    string = "%s,NA" %(string)
            if perc95:
                if isinstance(value.get95thPercentile(), (float,int)):
                    string = "%s,%.2E" %(string,value.get95thPercentile())
                else:
                    string = "%s,NA" %(string)
            if perc5:
                if isinstance(value.get5thPercentile(), (float,int)):
                    string = "%s,%.2E" %(string,value.get5thPercentile())
                else:
                    string = "%s,NA" %(string)
            if perc99:
                if isinstance(value.get99thPercentile(), (float,int)):
                    string = "%s,%.2E" %(string,value.get99thPercentile())
                else:
                    string = "%s,NA" %(string)
            if perc1:
                if isinstance(value.get1thPercentile(), (float,int)):
                    string = "%s,%.2E" %(string,value.get1thPercentile())
                else:
                    string = "%s,NA" %(string)
        
            stringList.append(string)
        return {'Name': NameList, 'StringList': stringList}

    def getYieldString(self):
        string = ""
        if self.getDidYield():
            string = "%.1f,%d,%.2f" %(self.getYield(), self.getFailedCycle(),self.getFailedCycleStdDev())
        return string
        
    def getYield(self):
        return float(1-self.FailPerc)
    
    def getFailedCycle(self):
        return int(self.FailCycle)

    def getFailedCycleStdDev(self):
        return float(self.FailCycleStdDev)

    def getValNames(self):
        names = []
        for val in self.ValueList:
            names.append(val.getName())
        return names
    
    def getValUnits(self):
        units = []
        for val in self.ValueList:
            units.append(val.getUnit())
        return units
            
    def size(self):
        return len(self.ValueList)

class batch:

    def __init__(self, Name):
        self.rows = []
        self.Name = Name
        self.empty = True
        self.rows = []
        self.DieX = None
        self.DieY = None
        self.DevX = None
        self.DevY = None
        self.MatBit = None
        self.MatNormal = None
        self.ExpNames = None
        self.ExpParNames = None
        self.ExpPar = None

    def addRow(self,row):
        
        if row != None:

            newRow = cp.deepcopy(row)

            self.rows.append(newRow)

            if self.empty:
                self.DieX = newRow.DieX
                self.DieY = newRow.DieY
                self.DevX = newRow.DevX
                self.DevY = newRow.DevY
                self.MatBit = newRow.MatBit
                self.MatNormal = newRow.MatNormal
                self.empty = False
            else:
                if not self.DieX == newRow.DieX:
                    self.DieX = None
                if not self.DieY == newRow.DieY:
                    self.DieY = None
                if not self.DevX == newRow.DevX:
                    self.DevX = None
                if not self.DevY == newRow.DevY:
                    self.DevY = None
                if not self.MatBit == newRow.MatBit:
                    self.MatBit = None
                if not self.MatNormal == newRow.MatNormal:
                    self.MatNormal = None
                    
    def addExperiment(self, ExpNames, ExpParNames, ExpPar):
        self.ExpNames = ExpNames
        self.ExpParNames = ExpParNames
        self.ExpPar = ExpPar


    def getRows(self):
        return self.rows

    def getDidYield(self):
        dY = False
        for row in self.rows:
            if row.getDidYield():
                dY = True
                break
        return dY

    def getRow(self,n):
        return self.rows[n]

    def addRows(self,rows):
        
        rcp = cp.deepcopy(rows)
        for row in rcp:
            newRow = cp.deepcopy(row)

            self.rows.append(newRow)

            if self.empty:
                self.DieX = newRow.DieX
                self.DieY = newRow.DieY
                self.DevX = newRow.DevX
                self.DevY = newRow.DevY
                self.MatBit = newRow.MatBit
                self.MatNormal = newRow.MatNormal
                self.empty = False
            else:
                if not self.DieX == newRow.DieX:
                    self.DieX = None
                if not self.DieY == newRow.DieY:
                    self.DieY = None
                if not self.DevX == newRow.DevX:
                    self.DevX = None
                if not self.DevY == newRow.DevY:
                    self.DevY = None
                if not self.MatBit == newRow.MatBit:
                    self.MatBit = None
                if not self.MatNormal == newRow.MatNormal:
                    self.MatNormal = None

    def getNameLine(self):
        names = []
        units = []
        for row in self.rows:
            for valN, valU in zip(row.getValNames(), row.getValUnits()): 
                if not valN in names:
                    names.append(valN)
                    units.append(valU)

        return {"Names": names, "Units": units}
 
        
    def getNameString(self,avg=True,StdDev=True,Med=True,perc95=True,perc5=True,perc99=False,perc1=False,Max=False,Min=False):
        
        (names, units) = self.getNameLine().values()
        print(names, units)
        yi = self.getDidYield()
        stringName = "NameValue"
        stringUnit = "UnitValue"

        stringName = "%s,DieX,DieY" %(stringName)
        stringName = "%s,DevX,DevY" %(stringName)
        stringName = "%s,Mat. Normal, Mat. Bit" %(stringName)
        stringUnit = "%s,,,,,," %(stringUnit)
        
        for name, unit in zip(names, units):
            if avg:
                stringName = "%s,Avg.%s" %(stringName,name)
                stringUnit = "%s,%s" %(stringUnit,unit)
            if StdDev:
                stringName = "%s,Std.Dev.%s" %(stringName,name)
                stringUnit = "%s,%s" %(stringUnit,unit)
            if Min: 
                stringName = "%s,Min.%s" %(stringName,name)
                stringUnit = "%s,%s" %(stringUnit,unit)
            if Max:
                stringName = "%s,Max.%s" %(stringName,name)
                stringUnit = "%s,%s" %(stringUnit,unit)
            if Med:
                stringName = "%s,Med.%s" %(stringName,name)
                stringUnit = "%s,%s" %(stringUnit,unit)
            if perc95:
                stringName = "%s,95th Perc.%s" %(stringName,name)
                stringUnit = "%s,%s" %(stringUnit,unit)
            if perc5:
                stringName = "%s,5th Perc.%s" %(stringName,name)
                stringUnit = "%s,%s" %(stringUnit,unit)
            if perc99:
                stringName = "%s,1th Perc.%s" %(stringName,name)
                stringUnit = "%s,%s" %(stringUnit,unit)
            if perc1:
                stringName = "%s,1th Perc.%s" %(stringName,name)
                stringUnit = "%s,%s" %(stringUnit,unit)
            if self.ExpNames != None:
                for name in self.ExpNames:
                    None
        
        if yi:
            stringName = "%s,Yield, Failed Cycle, Failed Cycle StdDev" %(stringName)
            stringUnit = "%s,,," %(stringName)


        stringName = "%s,Cycle Start,Cycle End" %(stringName)
        stringName = "%s,Measurement Type" %(stringName)
        stringUnit = "%s,,," %(stringUnit)

        return {"Name": stringName, "Unit":stringUnit}

    def getStringOutput(self,avg=True,StdDev=True,Med=True,perc95=True,perc5=True,perc99=False,perc1=False,Max=False,Min=False):
        
        
        frame = ip.currentframe()
        args, _, _, values = ip.getargvalues(frame)

        argVal = []
        n=0

        for x in values:
            if n > 0 and n < len(values)-1:
                argVal.append(values[x])
            n +=1

        (names, units) = self.getNameString(avg,StdDev,Med,perc95,perc5,perc99,perc1,Max,Min).values()

        OutputList = [names]
        OutputList.append(units)
        Names = self.getNameLine()

        for row in self.rows:
            Line = 'DataValue'

            if not row.DieX == None and not row.DieY == None:
                Line = "%s,%d,%d" %(Line, row.DieX, row.DieY)
            else:
                Line = "%s,," %(Line)

            if not row.DevX == None and not row.DevY == None:
                Line = "%s,%d,%d" %(Line, row.DevX, row.DevY)
            else:
                Line = "%s,," %(Line)
            if not row.MatNormal == None: 
                Line = "%s,%s" %(Line, row.MatNormal)
            else:
                Line = "%s," %(Line)

            if not row.MatBit == None: 
                Line = "%s,%d" %(Line, row.MatBit)
            else:
                Line = "%s," %(Line)

            for Name in Names["Names"]:
                ValSt = row.getListValString(avg,StdDev,Med,perc95,perc5,perc99,perc1,Max,Min)
                NameList = ValSt['Name']
                StringList = ValSt['StringList']
                found = False
                for n in range(len(NameList)):
                    if Name == NameList[n]:
                        Line = "%s%s" %(Line,StringList[n])
                        found = True
                        break
                if not found:
                    for x in range(sum(argVal)):
                        Line = "%s," %(Line)
            if row.getDidYield():
                Line = "%s,%s" %(Line, row.getYieldString())
            if not row.StCycle == 0 and not row.EndCycle == 0:
                Line = "%s,%d,%d" %(Line, row.StCycle, row.EndCycle)
            else:
                Line = "%s,," %(Line)
            Line = "%s,%s" %(Line,row.MeasType)
            
            OutputList.append(Line)
        return OutputList

    def WriteBatch(self, eChar, avg=True,StdDev=True,Med=True,perc95=True,perc5=True,perc99=False,perc1=False,Max=False,Min=False):
        
        header = eChar.Combinedheader

        if self.DieX == None or self.DieY == None:
            withDie = False
        else:
            withDie = True

        data = self.getStringOutput(avg,StdDev,Med,perc95,perc5,perc99,perc1,Max,Min)

        thread = eChar.writeDataToFile(header,data,Typ=self.Name,withDie=withDie)

        return thread

    def getCompresedRow(self, MultDev=False):
        
        if len(self.rows) == 0:
            return None
        
        NewRow = cp.deepcopy(self.rows[0])
        NewRow.CombineRows(cp.deepcopy(self.rows[1:]), MultDev)
        return NewRow

    def size(self):
        return len(self.rows)

    def addBatch(self, order, batch):
        
        if order == 'Measurements':
            if self.empty:
                for n in range(batch.size()):
                    self.addRow(batch.getRow(n))
                self.empty = False
            else:
                if self.size() != batch.size():
                    return None
            for n in range(self.size()):
                newRow = cp.deepcopy(batch.getRow(n))
                self.rows[n].CombineRow(newRow, True)
                if not self.DieX == newRow.DieX:
                    self.DieX = None
                if not self.DieY == newRow.DieY:
                    self.DieY = None
                if not self.DevX == newRow.DevX:
                    self.DevX = None
                if not self.DevY == newRow.DevY:
                    self.DevY = None
                if not self.MatBit == newRow.MatBit:
                    self.MatBit = None
                if not self.MatNormal == newRow.MatNormal:
                    self.MatNormal = None

