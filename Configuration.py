"""
This file contains the Configuration class that contains and governs the initialization of the GUI
Written by: Karsten Beckmann
Date: 11/6/2018
email: kbeckmann@sunypoly.edu
"""

from ctypes import *
import os as os
import pathlib as path
import csv as csv
import time as tm
import numpy as np
import pyvisa as vs
import math as ma
import sys
import statistics as stat
from matplotlib import lines
from matplotlib import markers
from matplotlib import colors
import threading as th
import DataHandling as dh
import queue as qu
import StdDefinitions as std
from win32com.shell import shellcon, shell


class Configuration:

    ErrorQueue = qu.Queue()

    def __init__(self, configFile="config.dat"):

        self.WaferID = ""
        self.GPIBB1500 = ""
        self.GPIBProbeStation = ""
        self.GPIBMatrix = ""
        self.Mainfolder = shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)
        self.Subfolder = ""
        self.DeviceName = ""
        self.WaferID = ""
        self.FailingConditions = ""
        self.DieSizeX = 25
        self.DieSizeY = 32
        self.WaferSize = 300
        self.WaferMapVariable = ""
        self.CenterLocationX = 0
        self.CenterLocationY = 0
        self.DieFile = ""
        self.DieMap = ""
        self.XPitch = -200
        self.YPitch = 0
        self.NumXdevices = 2
        self.NumYdevices = 1
        self.DeviceStartX = 1
        self.DeviceStartY = 1
        self.MultipleDev = False
        self.Dies = []
        self.SpecFile = ""
        self.SpecCode = ""
        self.DoYield = False
        self.MeasFile = None
        self.MultipleDies = False
        self.MatrixConfiguration = None
        self.MatrixFile = ""
        self.UseMatrix = False
        self.ApplyParametersB1530 = False
        self.Measurements = None
        self.ResultGraphStyle = None
        self.ResultGraphWidth = None
        self.ResultGraphColor = None
        self.AvailableDieMaps = [0,1,2,3,4]
        self.LogOn = False
        self.MaxInfoLogFileSize = 1e9
        self.MaxErrorLogFileSize = 1e9


        self.CurrentMeasurementType = 'Full Wafer'
        
        self.Prober = None
        self.Matrix = None

        self.ErrorList = []
        self.LogList = []

        self.configFile = configFile
        self.InitializeFromConfig()

    def InitializeFromConfig(self):
        configFile =  self.configFile
        if configFile.find("/") == -1 and configFile.find("\\") == -1:
            cwd = os.getcwd()
            File = os.path.join(cwd,configFile)
        else:
            File = configFile

        wp = std.HandleConfigFile(File,True)
        for key, value in wp.items():
            if key == "Mainfolder":
                if os.path.isdir(wp[key]):
                    self.Mainfolder = wp[key]
                else:
                    self.ErrorQueue.put("ConfigurationFile: Mainfolder does not exist.")
            if key == "WaferID":
                self.WaferID = wp[key]
            if key == "Subfolder":
                self.Subfolder = wp[key]
            if key == "DeviceName":
                self.DeviceName = wp[key]
            if key == "CurrentMeasurementType":
                self.CurrentMeasurementType = wp[key]
            if key == "DieSizeX":
                try: 
                    self.DieSizeX = float(wp[key])
                except:
                    self.ErrorQueue.put("Die SizeX is not of type float.")
            if key == "DieSizeY":
                try: 
                    self.DieSizeY = float(wp[key])
                except:
                    self.ErrorQueue.put("Die Size Y is not of type float.")
            if key == "MultipleDies":
                if value.strip().lower() == "true":
                    self.MultipleDies = True
                else:
                    self.MultipleDies = False
            if key == "MultipleDev":
                if value.strip().lower() == "true":
                    self.MultipleDev = True
                else:
                    self.MultipleDev = False
            if key == "WaferSize":
                try: 
                    self.WaferSize = int(wp[key])
                except:
                    self.ErrorQueue.put("Wafer Size is not of type float.")
            if key == "WaferMapVariable":
                self.WaferMapVariable = wp[key]
            if key == "WGFMUUseGUI": 
                if value.strip().lower() == "true":
                    self.WGFMUUseGUI = True
                else:
                    self.WGFMUUseGUI = False

            if key == "CenterLocationX":
                try: 
                    self.CenterLocationX = float(wp[key])
                except:
                    self.ErrorQueue.put("Center Locaiton X is not of type float.")
            if key == "CenterLocationY":
                try: 
                    self.CenterLocationY = float(wp[key])
                except:
                    self.ErrorQueue.put("Center location Y is not of type float.")
            if key == "DieFile":
                if os.path.isfile(wp[key]):
                    self.DieFile = wp[key]
                else:
                    self.ErrorQueue.put("ConfigurationFile: Die File does not exist.")
            if key == "MeasFile":
                if os.path.isfile(wp[key]):
                    self.MeasFile = wp[key]
                else:
                    self.ErrorQueue.put("Measurements File: File does not exist.")
            if key == "ResultGraphStyle":
                if wp[key] in lines.lineStyles.keys() and not wp[key] in markers.MarkerStyle.markers.keys():
                    self.ResultGraphStyle = wp[key]
            if key == "ResultGraphWidth":
                if isinstance(wp[key], (int,float)):
                    self.ResultGraphWidth = wp[key]
            if key == "ResultGraphColor":
                if wp[key] in colors.cnames.keys():
                    self.ResultGraphColor = wp[key]
            if key == "DieMap":
                try: 
                    self.DieMap = int(wp[key])
                except:
                    self.DieMap = ""
                    self.ErrorQueue.put("Die Map is not of type int.")
            if key == "XPitch":
                try: 
                    self.XPitch = int(wp[key])
                except:
                    self.ErrorQueue.put("X Pitch is not of type int.")
            if key == "YPitch":
                try: 
                    self.YPitch = int(wp[key])
                except:
                    self.ErrorQueue.put("Y Pitch is not of type int.")
            if key == "DeviceStartX":
                try: 
                    self.DeviceStartX = int(wp[key])
                except:
                    self.ErrorQueue.put("Num of X devices is not of type int.")
            if key == "DeviceStartY":
                try: 
                    self.DeviceStartY = int(wp[key])
                except:
                    self.ErrorQueue.put("Num of Y devices is not of type int.")
            if key == "NumXdevices":
                try: 
                    self.NumXdevices = int(wp[key])
                except:
                    self.ErrorQueue.put("Num of X devices is not of type int.")
            if key == "NumYdevices":
                try: 
                    self.NumYdevices = int(wp[key])
                except:
                    self.ErrorQueue.put("Num of Y devices is not of type int.")
            if key == "SpecFile":
                if os.path.isfile(wp[key]):
                    self.SpecFile = wp[key]
                else:
                    self.ErrorQueue.put("ConfigurationFile: Die File does not exist.")
            if key == "SpecCode":
                self.setSpecCode(wp[key])
            if key == "MatrixFile":
                if os.path.isfile(wp[key]):
                    self.MatrixFile = wp[key]
                else:
                    self.ErrorQueue.put("ConfigurationFile: Die File does not exist.")
            if key == "UseMatrix":
                if value.strip().lower() == "true":
                    self.UseMatrix = True
                else:
                    self.UseMatrix = False
            if key == "ProberInit":
                self.ProberInit=wp[key]
            if key == "MatrixInit":
                self.MatrixInit=wp[key]
            if key == 'B1530Chn1OperationMode':
                try:
                    entry = int(wp[key])
                    if 2000 <= entry <= 2003:
                        self.B1530Chn1Mode = entry
                    else:
                        self.ErrorQueue.put("B1530 Operational Mode must be between 2000 and 2004")
                except:
                    self.ErrorQueue.put("B1530 Operational Mode must be between 2000 and 2004")
            if key == 'B1530Chn2OperationMode':
                try:
                    entry = int(wp[key])
                    if 2000 <= entry <= 2003:
                        self.B1530Chn2Mode = entry
                    else:
                        self.ErrorQueue.put("B1530 Operational Mode must be between 2000 and 2004")
                except:
                    self.ErrorQueue.put("B1530 Operational Mode must be between 2000 and 2004")
            #############
            if key.find("WGFMU") != -1:
                try:
                    entry = int(wp[key])
                    vars(self)[key] = entry
                except:
                    self.ErrorQueue.put("WGFMU %s state could not be loaded" %(key))
                
                
            if key == 'B1530Chn1MeasureMode':
                try:
                    entry = int(wp[key])
                    if 4000 <= entry <= 4001:
                        self.B1530Chn1MeasureMode = entry
                    else:
                        self.ErrorQueue.put("B1530 Measure Mode must be between 4001 and 4001")
                except:
                    self.ErrorQueue.put("B1530 Measure Mode must be between 4001 and 4001")
            if key == 'B1530Chn2MeasureMode':
                try:
                    entry = int(wp[key])
                    if 4000 <= entry <= 4001:
                        self.B1530Chn2MeasureMode = entry
                    else:
                        self.ErrorQueue.put("B1530 Measure Mode must be between 4001 and 4001")
                except:
                    self.ErrorQueue.put("B1530 Measure Mode must be between 4001 and 4001")
            #############
            if key == 'B1530Chn1ForceVoltageRange':
                try:
                    entry = int(wp[key])
                    if 3000 <= entry <= 3003:
                        self.B1530Chn1ForceVoltageRange = entry
                    else:
                        self.ErrorQueue.put("B1530 Force Voltage Range must be between 3001 and 3003")
                except:
                    self.ErrorQueue.put("B1530 Force Voltage Range must be between 3000 and 3003")
            if key == 'B1530Chn2ForceVoltageRange':
                try:
                    entry = int(wp[key])
                    if 3000 <= entry <= 3003:
                        self.B1530Chn2ForceVoltageRange = entry
                    else:
                        self.ErrorQueue.put("B1530 Force Voltage Range must be between 3001 and 3003")
                except:
                    self.ErrorQueue.put("B1530 Force Voltage Range must be between 3000 and 3003")
            ##############
            if key == 'B1530Chn1VoltageMeasureRange':
                try:
                    entry = int(wp[key])
                    if 5001 <= entry <= 5002:
                        self.B1530Chn1MeasureVoltage = entry
                    else:
                        self.ErrorQueue.put("B1530 Measure Voltage Range must be between 5001 and 5002")
                except:
                    self.ErrorQueue.put("B1530 Measure Voltage Range must be between 5001 and 5002")
            if key == 'B1530Chn2VoltageMeasureRange':
                try:
                    entry = int(wp[key])
                    if 5001 <= entry <= 5002:
                        self.B1530Chn2MeasureVoltage = entry
                    else:
                        self.ErrorQueue.put("B1530 Measure Voltage Range must be between 5001 and 5002")
                except:
                    self.ErrorQueue.put("B1530 Measure Voltage Range must be between 5001 and 5002")
            ##############
            if key == 'B1530Chn1CurrentMeasureRange':
                try:
                    entry = int(wp[key])
                    if 6001 <= entry <= 6005:
                        self.B1530Chn1MeasureCurrent = entry

                    else:
                        self.ErrorQueue.put("B1530 Measure Current Range must be between 6001 and 6005")
                except:
                    self.ErrorQueue.put("B1530 Measure Current Range must be between 6001 and 6005")
            if key == 'B1530Chn1CurrentMeasureRange':
                try:
                    entry = int(wp[key])
                    if 6001 <= entry <= 6005:
                        self.B1530Chn2MeasureCurrent = entry
                    else:
                        self.ErrorQueue.put("B1530 Measure Current Range must be between 6001 and 6005")
                except:
                    self.ErrorQueue.put("B1530 Measure Current Range must be between 6001 and 6005")
            if key.find('$ADC$_') == 0:
                if key.find('_$HS$_') != -1:
                    if key.find('_$Mode$') != -1:
                        vars(self)[key] = value
                    if key.find('_$N$') != -1:
                        vars(self)[key] = value
                if key.find('_$HR$_') != -1:
                    if key.find('_$Mode$') != -1:
                        vars(self)[key] = value
                    if key.find('_$N$') != -1:
                        vars(self)[key] = value
                for n in range(1,17,1):
                    if key.find('_$SMU%d$' %(n)) != -1:
                        vars(self)[key] = value
            if key.find('$ToolRank$_') != -1:
                vars(self)[key] = value
            if key.find('$B1530A$_') == 0:
                try:
                    vars(self)[key] = int(value)
                except ValueError:
                    None
            if key == "InititalMeasurement":
                vars(self)[key] = str(value)
            if key == "InfoLogSave":
                if value.strip().lower() == "true":
                    self.InfoLogSave = True
                else:
                    self.InfoLogSave = False
            if key == "MainWindowX":
                vars(self)[key] = int(value)
            if key == "MainWindowY":
                vars(self)[key] = int(value)
            if key == "MainWindowMon":
                vars(self)[key] = int(value)
            if key == "ResultWindowX":
                vars(self)[key] = int(value)
            if key == "ResultWindowY":
                vars(self)[key] = int(value)
            if key == "ResultWindowMon":
                vars(self)[key] = int(value)

            self.UpdateMultipleDev()

        self.computerName = os.environ['COMPUTERNAME']

        self.UpdateDies(self.ErrorQueue)
        self.UpdateSpecs(self.ErrorQueue)
        self.UpdateMatrixConfig(self.ErrorQueue)
        self.UpdateMeasurementFile(self.ErrorQueue)

    def setValue(self, name, value, outputError=True):

        try: 
            vars(self)[name] = value
            return True
        except:
            if outputError:
                self.ErrorQueue.put("Config Set: Variable '%s' does not exist in Configuration." %(name))
            return False
    
    def getValue(self, name, outputError=True):

        try: 
            ret = vars(self)[name.strip()]
            return ret
        except: 
            if outputError:
                self.ErrorQueue.put("Config Get: Variable '%s' does not exist in Configuration." %(name))
            return None

    def getComputerName(self):
        return self.computerName

    def UpdateMeasurementFile(self, ErrorQueue):
        
        if self.MeasFile != None:
            Measurements = None

            try: 
                Measurements = std.HandleMeasurementFile(self.MeasFile)
            except ValueError as e: 
                ErrorQueue.put(e)
            if isinstance(Measurements, type([])):
                if len(Measurements) > 0:
                    self.Measurements = Measurements
                else:
                    ErrorQueue.put("No Measurements File available!")
            else:
                ErrorQueue.put("No Measurements File available!")
        else:
            ErrorQueue.put("No Measurements File available!")        

    def UpdateMultipleDev(self):
        if self.XPitch == 0 and self.YPitch == 0:
            self.MultipleDev = False

    def getApplyParameterB1530(self):
        return self.ApplyParametersB1530

    def getMultipleDev(self):
        return self.MultipleDev

    def getMultipleDies(self):
        return self.MultipleDies

    def getMeasurementType(self):
        return self.CurrentMeasurementType
        
    def getErrorList(self):
        return self.ErrorList

    def getLogList(self):
        return self.LogList

    def clearErrorList(self):
        self.ErrorList = []
        
    def clearLogList(self):
        self.LogList = []
    
    def addElementErrorList(self, element):
        self.ErrorList.insert(0, str(element))
        if len(self.ErrorList) > 100:
            self.ErrorList.pop(100)

    def addElementLogList(self, element): 
        self.LogList.append(str(element))
        if len(self.LogList) > 100:
            self.LogList.pop(100)

    def setMultipleDev(self, MultipleDev):
        self.MultipleDev = MultipleDev 
    
    def setMultipleDies(self, MultipleDies):
        self.MultipleDies = MultipleDies

    def getMatrixConfiguration(self):
        return self.MatrixConfiguration

    def getMatrixFile(self):
        return self.MatrixFile

    def getProber(self):
        return self.Prober

    def getMatrix(self):
        return self.Matrix

    def getAvailableMeasurements(self):
        meas = dict()
        if self.Measurements != None:
            for entry in self.Measurements:
                try:
                    meas[entry['Folder']].append(entry['Name'])
                except:
                    meas[entry['Folder']] = [entry['Name']]
        return meas
    
    def getMeasurementTools(self):
        tools = dict()
        if self.Measurements != None:
            for entry in self.Measurements:
                try:
                    tools[entry['Folder']].append(entry['Tools'])
                except:
                    tools[entry['Folder']] = [entry['Tools']]
        return tools

    
    def getMeasurementDetail(self, Name, Folder):
        if Name != None: 
            
            if self.Measurements != None:
            
                for entry in self.Measurements:
                    if entry['Name'] == Name and entry['Folder'] == Folder:
                        return entry
                return None

        else:
            return None
        
    def getMeasurementFile(self):
        return self.MeasFile

    def setMeasurementFile(self, file):
        if os.path.isfile(file):
            self.MeasFile = file
        else:
            self.ErrorQueue.put("Measurement File: File does not exist.")

    def setMatrixFile(self, file):
        if os.path.isfile(file):
            self.MatrixFile = file
        else:
            self.ErrorQueue.put("ConfigurationFile: File does not exist.")
    
    def getUseMatrix(self):
        return self.UseMatrix

    def setUseMatrix(self, useMatrix):
        self.UseMatrix = useMatrix

    def getB1530OperationalMode(self):
        return [self.B1530Chn1Mode, self.B1530Chn2Mode]

    def getB1530ForceVoltageRange(self):
        return [self.B1530Chn1ForceVoltageRange, self.B1530Chn2ForceVoltageRange]
    
    def getB1530MeasureMode(self):
        return [self.B1530Chn1MeasureMode, self.B1530Chn2MeasureMode]
    
    def getB1530VoltageMeasureRange(self):
        return [self.B1530Chn1MeasureVoltage, self.B1530Chn2MeasureVoltage]

    def getB1530CurrentMeasureRange(self):
        return [self.B1530Chn1MeasureCurrent, self.B1530Chn2MeasureCurrent]

    def getDoYield(self):
        return self.DoYield

    def UpdateDies(self, ErrQu=ErrorQueue):
        if self.DieFile == "":
            if self.DieMap == -1:
                self.DieMap = 0
            self.Dies = std.CreateDiePattern(self.DieMap,self.WaferSize,self.DieSizeX,self.DieSizeY, [self.CenterLocationX,self.CenterLocationY])
        else:
            Dies = []
            try:
                Dies = std.LoadDieFile(self.DieFile,self.WaferSize,self.DieSizeX,self.DieSizeY)
                self.DieMap = -1
            except (ValueError, TypeError, IndexError) as e:
                ErrQu.put(e)
                self.DieMap = 0
            self.Dies = std.sortDies(Dies)
    
    def UpdateSpecs(self, ErrQu=ErrorQueue):
        try:
            self.Specs = std.HandleSpecFile(self.SpecFile, self.SpecCode, ErrQu)
            self.DoYield = False
            if self.Specs != None:
                if len(self.Specs) > 0: 
                    self.DoYield=True

        except (ValueError, TypeError) as e:
            ErrQu.put(e)
            
        return self.Specs

    def saveConfigToFile(self):

        output = []

        for key, item in vars(self).items():
            if key != 'configFile':
                output.append([key,item])
        
        configFile =  self.configFile
        if configFile.find("/") == -1 and configFile.find("\\") == -1:
            cwd = os.getcwd()
            File = "%s/%s" %(cwd,configFile)
        else:
            File = configFile

        std.writeConfigFile(output, File)


    def UpdateMatrixConfig(self, ErrQu=ErrorQueue):
        try: 
            self.MatrixConfiguration = std.HandleMatrixFile(self.MatrixFile)
        except (ValueError, TypeError, IndexError) as e:
            ErrQu.put(e)
            self.setUseMatrix(False)
            return None
        return self.MatrixConfiguration

    def getSpecs(self):
        return self.Specs
    
    def getDeviceID(self):
        return self.DeviceName

    def getWaferID(self):
        return self.WaferID
    
    def getSpecCode(self):
        return self.SpecCode
    
    def getGPIB_B1500(self):
        return self.GPIBB1500

    def getGPIBProbeStation(self):
        return self.GPIBProbeStation
    
    def getGPIBMatrix(self):
        return self.GPIBMatrix

    def getMainFolder(self):
        return self.Mainfolder

    def getSubfolder(self):
        return self.Subfolder

    def getDeviceName(self):
        return self.DeviceName

    def getFailingConditions(self):
        return self.FailingConditions

    def getDieSizeX(self):
        return self.DieSizeX

    def getDieSizeY(self):
        return self.DieSizeY

    def getWaferSize(self):
        return float(self.WaferSize)
    
    def getWaferVariable(self):
        return self.WaferMapVariable

    def getCenterLocation(self):
        try:
            return [float(self.CenterLocationX),float(self.CenterLocationY)]
        except:
            raise ValueError("Configuration: CenterLocation is not a Double value.")
    
    def getCenterLocationX(self):
        try:
            return float(self.CenterLocationX)
        except:
            raise ValueError("Configuration: CenterLocation X is not a Double value.")

    def getCenterLocationY(self):
        try:
            return float(self.CenterLocationY)
        except:
            raise ValueError("Configuration: CenterLocation Y is not a Double value.")

    def getDieFile(self):
        return self.DieFile

    def getDieMap(self):
        return self.DieMap
    
    def getAllDieMaps(self):
        return self.AvailableDieMaps

    def getXPitch(self):
        return int(self.XPitch)
    
    def getYPitch(self):
        return int(self.YPitch)

    def getNumXDevices(self):
        return int(self.NumXdevices)

    def getNumYDevices(self):
        return int(self.NumYdevices)

    def getDeviceStartX(self):
        return int(self.DeviceStartX)

    def getDeviceStartY(self):
        return int(self.DeviceStartY)

    def getNumOfDevices(self):
        return int(int(self.NumXdevices)*int(self.NumYdevices))

    def getNumOfDies(self):
        return len(self.Dies)
    
    def getDies(self):
        return self.Dies

    def getSpecFile(self):
        return self.SpecFile

    def setAppyParametersB1530(self):
        self.AppyParametersB1530 = True

    def resetAppyParametersB1530(self):
        self.AppyParametersB1530 = False
    
    def setB1530Chn1OperationalMode(self, mode):
        self.B1530Chn1Mode = int(mode)
            

    def setB1530Chn2OperationalMode(self, mode):
        self.B1530Chn2Mode = int(mode)

    def setB1530Chn1ForceVoltageRange(self, Range):
        self.B1530Chn1ForceVoltageRange = int(Range)

    def setB1530Chn2ForceVoltageRange(self, Range):
        self.B1530Chn2ForceVoltageRange = int(Range)

    def setB1530Chn1MeasureMode(self, mode):
        self.B1530Chn1MeasureMode = int(mode)

    def setB1530Chn2MeasureMode(self, mode):
        self.B1530Chn2MeasureMode = int(mode)

    def set1530Chn1MeasureVoltageRange(self, Range):
        self.B1530Chn1MeasureVoltage = int(Range)

    def set1530Chn2MeasureVoltageRange(self, Range):
        self.B1530Chn2MeasureVoltage = int(Range)
    
    def setB1530Chn1MeasureCurrentRange(self, Range):
        self.B1530Chn1MeasureCurrent = int(Range)

    def setB1530Chn2MeasureCurrentRange(self, Range):
        self.B1530Chn2MeasureCurrent = int(Range)

    def setSpecCode(self, SpecCode):
        if not isinstance(SpecCode, str):
            raise TypeError("SpecCode must be a string with a maximum length of 20 characters")
        if len(SpecCode) > 20: 
            raise ValueError("SpecCode must be a string with a maximum length of 20 characters")
        self.SpecCode = SpecCode.strip()
    
    def setWaferID(self, WaferID):
        if isinstance(WaferID, str):
            if len(WaferID) < 20:
                self.WaferID = WaferID
            else:
                raise ValueError("WaferID is limited to 20 charactes")
        elif type(WaferID) == int:
            self.WaferID = WaferID
        else:
            raise TypeError("WaferID must be string.")
        
    def setGPIB_B1500(self, GPIBB1500):
        if isinstance(GPIBB1500, str):
            if len(GPIBB1500) < 17:
                self.GPIBB1500 = GPIBB1500
            else:
                raise ValueError("GPIB addresses must be a string of 16 characters")
        else:
            raise TypeError("GPIB addresses must be a string of 16 characters")
                

    def setGPIBProbeStation(self,GPIBProbeStation):
        if isinstance(GPIBProbeStation, str):
            if len(GPIBProbeStation) < 17:
                self.GPIBProbeStation = GPIBProbeStation
            else:
                raise ValueError("GPIB addresses must be a string of 16 characters")
        else:
            raise TypeError("GPIB addresses must be a string of 16 characters")
    
    def setGPIBMatrix(self, GPIBMatrix):
        if isinstance(GPIBMatrix, str):
            if len(GPIBMatrix) < 17:
                self.GPIBMatrix = GPIBMatrix
            else:
                raise ValueError("GPIB addresses must be a string of 16 characters")
        else:
            raise TypeError("GPIB addresses must be a string of 16 characters")

    def setMainFolder(self, MainFolder):
        if isinstance(MainFolder, str): 
            self.Mainfolder = MainFolder
        else:
            raise TypeError("Mainfolder must be a string")
    
    def setSpecFile(self, SpecFile):
        if isinstance(SpecFile, str):
            self.SpecFile = SpecFile
        else:
            raise TypeError("Specfile must be a string")


    def setSubfolder(self, Subfolder):
        if isinstance(Subfolder, str): 
            if len(Subfolder) < 21:
                self.Subfolder = Subfolder
            else:
                raise ValueError("Subfolder must be a string of less or equal than 20 characters")
        else:
            raise TypeError("Subfolder must be a string of less or equal than 20 characters")

    def setDeviceName(self, DeviceName):
        if isinstance(DeviceName, str): 
            if len(DeviceName) < 21:
                self.DeviceName = DeviceName
            else:
                raise ValueError("Subfolder must be a string of less or equal than 20 characters")
        else:
            raise TypeError("Subfolder must be a string of less or equal than 20 characters")

    def setFailingConditions(self, FailingConditions):
        None

    def setFailureFile(self, filename):
        self.__FailureFile = filename
        self.UpdateFailureConditions()

    def UpdateFailureConditions(self):
        None

    def setDieSizeX(self, DieSizeX):
        try: 
            DieSizeX = float(DieSizeX)
        except:
            raise TypeError("Die Size must be an float or int in mm")
        if DieSizeX < 1: 
            raise TypeError("Die Size must be an float or int in mm")
        self.DieSizeX = float(DieSizeX)

    def setDieSizeY(self, DieSizeY):
        try: 
            DieSizeY = float(DieSizeY)
        except:
            raise TypeError("Die Size must be an float or int in mm")
        if DieSizeY < 1: 
            raise TypeError("Die Size must be an float or int in mm")
        self.DieSizeY = float(DieSizeY)

    def setWaferSize(self, WaferSize):
        try:
            WaferSize = int(WaferSize)
        except:
            raise TypeError("Die Size must be an Integer")
        if WaferSize < 1:
            raise TypeError("Die Size must be an Integer bigger than 1")
        self.WaferSize = int(WaferSize)
    
    def setWaferMapVariable(self, WaferMapVariable):
        if isinstance(WaferMapVariable, str): 
            if len(WaferMapVariable) < 21:
                self.WaferMapVariable = WaferMapVariable
            else:
                raise ValueError("Wafer Map Variable must be a string of less or equal than 20 characters")
        else:
            raise TypeError("Wafer Map Variable must be a string of less or equal than 20 characters")

    def setCenterLocation(self, CenterLocation):
        if not isinstance(CenterLocation, list):
            raise TypeError("CenterLocation must a list of length 2 with two floats from 0 to 1")
        if not len(CenterLocation) == 2:
            raise ValueError("CenterLocation must a list of length 2 with two floats from 0 to 1")
        try:
            CenterLocation[0] = float(CenterLocation[0])
        except:
            raise TypeError("CenterLocation must a list of length 2 with two floats from 0 to 1")
        if CenterLocation[0] < 0 or CenterLocation[0] > 1:
            raise ValueError("CenterLocation must a list of length 2 with two floats from 0 to 1")
        try:
            CenterLocation[1] = float(CenterLocation[1])
        except:
            raise TypeError("CenterLocation must a list of length 2 with two floats from 0 to 1")
        if CenterLocation[1] < 0 or CenterLocation[1] > 1:
            raise ValueError("CenterLocation must a list of length 2 with two floats from 0 to 1")
        self.CenterLocationX = CenterLocation[0]
        self.CenterLocationY = CenterLocation[1]

    def setCenterLocationX(self, CenterLocationX):
        try:
            CenterLocationX = float(CenterLocationX)
        except:
            raise TypeError("CenterLocationX must be a float from 0 to 1")
        if CenterLocationX < 0 or CenterLocationX > 1:
            raise ValueError("CenterLocationX must be a float from 0 to 1")
        self.CenterLocationX = CenterLocationX

    def setCenterLocationY(self, CenterLocationY):
        try:
            CenterLocationY = float(CenterLocationY)
        except:
            raise TypeError("CenterLocationY must be a float from 0 to 1")
        if CenterLocationY < 0 or CenterLocationY > 1:
            raise ValueError("CenterLocationY must be a float from 0 to 1")
        self.CenterLocationY = CenterLocationY

    def setDieFile(self, DieFile):
        if os.path.isfile(DieFile) or DieFile == "":
            self.DieFile = DieFile
        else:
            self.ErrorQueue.put("Die File: File does not exist.")

    def setDieMap(self, DieMap):
        try:
            DieMap = int(DieMap)
        except:
            raise ValueError("Die Map must be a positive Integer")
        if DieMap < 0: 
            raise ValueError("Die Map must be a positive Integer")
        self.DieMap = DieMap

    def setXPitch(self, XPitch):
        try:
            XPitch = int(XPitch)
        except:
            raise ValueError("XPitch must be a float (Value in um) (ERR1)")
        self.XPitch = int(XPitch)
    
    def setYPitch(self, YPitch):
        try:
            YPitch = int(YPitch)
        except:
            raise ValueError("YPitch must be a float (Value in um)")
        self.YPitch = int(YPitch)

    def setNumXDevices(self, NumXdevices):
        try:
            NumXdevices = int(NumXdevices)
        except:
            raise TypeError("NumXdevices must be a int")
        if NumXdevices < 1:
            raise ValueError("NumXdevices must be a int")
        self.NumXdevices = int(NumXdevices)

    def setNumYDevices(self, NumYDevices):
        try:
            NumYDevices = int(NumYDevices)
        except:
            raise TypeError("NumYDevices must be a int")
        if NumYDevices < 1:
            raise ValueError("NumXdevices must be a int")
        self.NumYDevices = int(NumYDevices)

    def setDeviceStartX(self, DeviceStartX):
        try:
            DeviceStartX = int(DeviceStartX)
        except:
            raise TypeError("DeviceStartX must be a int")
        if DeviceStartX < 1:
            raise ValueError("DeviceStartX must be a int")
        self.DeviceStartX = int(DeviceStartX)

    def setDeviceStartY(self, DeviceStartY):
        try:
            DeviceStartY = int(DeviceStartY)
        except:
            raise TypeError("DeviceStartY must be a int")
        if DeviceStartY < 1:
            raise ValueError("DeviceStartY must be a int")
        self.DeviceStartY = int(DeviceStartY)