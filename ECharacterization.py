"""
Written by: Karsten Beckmann and Maximilian Liehr
Institution: SUNY Polytechnic Institute
Date: 6/12/2018

For more information please use the provided SUNY POLY python e-characterization manual.
"""

import matplotlib.pyplot as plt
import numpy as np
import csv as csv
import os
import time as tm 
import StdDefinitions as std
import threading as th 
import queue as qu
import math as ma
from decimal import Context as dc
import decimal as de
import DataHandling as dh
import numpy as np
import copy as cp
import engineering_notation as eng
import LetToArray as LtA
from datetime import datetime as dt

from Exceptions import *

import glob, imp
import os as os


class ECharacterization:
    
    #Endurance Queues
   
    EnduranceHeader = []
    Combinedheader = []
    SMUHeader = []
    curCycle = 1
    endTime = 0
    curTime = 0
    MaxDataPerPlot = 10000
    maxExecutions = 5
    MaxRowsPerFile = 500000

    #Output Avg Values
    StatOutValues = dh.batch('DeviceSummary')

    threads = []

    ErrorQueue = qu.Queue()

    wgfmu = None
    wgfmuInUse = True
    B1500A = None
    B1500Aonline = False
    B1500AInUse = False
    Mainfolder = None
    Subfolder = ''
    DateFolder = ''
    writeData = False
    Specs = None
    device = "test"
    localtime = tm.localtime()
    starttime = tm.localtime()
    WaferChar = False
    WaferID = None
    DieX = 0
    DieY = 0
    DevX = 0
    DevY = 0
    MatNormal = None
    MatBit = None
    save = True
    EnduranceData = []
    AdditionalHeader = []
    ExternalHeader = []
    MeasTypeClass = None


    maxNumSingleEnduranceRun = int(1.5e6)
    DeviceName = []
    MatDev = 0
    Header = []
    Results = []
    Configuration = None

    #Plotting Queues
    finished = qu.Queue()
    IVplotData = qu.Queue()
    LogData = qu.Queue()
    ResData = qu.Queue()
    SelectorEndurance = qu.Queue()
    SelectorHeader = []


    # API Return Value - Error Code
    WGFMU_NO_ERROR							= 0
    WGFMU_PARAMETER_OUT_OF_RANGE_ERROR		= -1
    WGFMU_ILLEGAL_STRING_ERROR				= -2
    WGFMU_CONTEXT_ERROR					    = -3
    WGFMU_FUNCTION_NOT_SUPPORTED_ERROR		= -4
    WGFMU_COMMUNICATION_ERROR				= -5
    WGFMU_FW_ERROR							= -6
    WGFMU_LIBRARY_ERROR					    = -7
    WGFMU_ERROR							    = -8
    WGFMU_CHANNEL_NOT_FOUND_ERROR			= -9
    WGFMU_PATTERN_NOT_FOUND_ERROR			= -10
    WGFMU_EVENT_NOT_FOUND_ERROR			    = -11
    WGFMU_PATTERN_ALREADY_EXISTS_ERROR		= -12
    WGFMU_SEQUENCER_NOT_RUNNING_ERROR		= -13
    WGFMU_RESULT_NOT_READY_ERROR			= -14
    WGFMU_RESULT_OUT_OF_DATE				= -15

    WGFMU_ERROR_CODE_MIN					= -9999

    # WGFMU_doSelfCaliration, WGFMU_doSelfTest
    WGFMU_PASS = 0
    WGFMU_FAIL = 1

    # WGFMU_treatWarningsAsErrors, WGFMU_setWarningLevel
    WGFMU_WARNING_LEVEL_OFFSET				= 1000
    WGFMU_WARNING_LEVEL_OFF				    = WGFMU_WARNING_LEVEL_OFFSET + 0
    WGFMU_WARNING_LEVEL_SEVERE				= WGFMU_WARNING_LEVEL_OFFSET + 1
    WGFMU_WARNING_LEVEL_NORMAL				= WGFMU_WARNING_LEVEL_OFFSET + 2
    WGFMU_WARNING_LEVEL_INFORMATION		    = WGFMU_WARNING_LEVEL_OFFSET + 3

    # WGFMU_setOperationMode
    WGFMU_OPERATION_MODE_OFFSET			    = 2000
    WGFMU_OPERATION_MODE_DC				    = WGFMU_OPERATION_MODE_OFFSET + 0
    WGFMU_OPERATION_MODE_FASTIV		    	= WGFMU_OPERATION_MODE_OFFSET + 1
    WGFMU_OPERATION_MODE_PG				    = WGFMU_OPERATION_MODE_OFFSET + 2
    WGFMU_OPERATION_MODE_SMU				= WGFMU_OPERATION_MODE_OFFSET + 3

    # WGFMU_setForceVoltageRange
    WGFMU_FORCE_VOLTAGE_RANGE_OFFSET		= 3000
    WGFMU_FORCE_VOLTAGE_RANGE_AUTO			= WGFMU_FORCE_VOLTAGE_RANGE_OFFSET + 0
    WGFMU_FORCE_VOLTAGE_RANGE_3V			= WGFMU_FORCE_VOLTAGE_RANGE_OFFSET + 1
    WGFMU_FORCE_VOLTAGE_RANGE_5V			= WGFMU_FORCE_VOLTAGE_RANGE_OFFSET + 2
    WGFMU_FORCE_VOLTAGE_RANGE_10V_NEGATIVE	= WGFMU_FORCE_VOLTAGE_RANGE_OFFSET + 3
    WGFMU_FORCE_VOLTAGE_RANGE_10V_POSITIVE	= WGFMU_FORCE_VOLTAGE_RANGE_OFFSET + 4

    # WGFMU_setMeasureMode
    WGFMU_MEASURE_MODE_OFFSET				= 4000
    WGFMU_MEASURE_MODE_VOLTAGE				= WGFMU_MEASURE_MODE_OFFSET + 0
    WGFMU_MEASURE_MODE_CURRENT				= WGFMU_MEASURE_MODE_OFFSET + 1

    # WGFMU_setMeasureVoltageRange
    WGFMU_MEASURE_VOLTAGE_RANGE_OFFSET		= 5000
    WGFMU_MEASURE_VOLTAGE_RANGE_5V			= WGFMU_MEASURE_VOLTAGE_RANGE_OFFSET + 1
    WGFMU_MEASURE_VOLTAGE_RANGE_10V		    = WGFMU_MEASURE_VOLTAGE_RANGE_OFFSET + 2

    # WGFMU_setMeasureCurrentRange
    WGFMU_MEASURE_CURRENT_RANGE_OFFSET		= 6000
    WGFMU_MEASURE_CURRENT_RANGE_1UA		    = WGFMU_MEASURE_CURRENT_RANGE_OFFSET + 1
    WGFMU_MEASURE_CURRENT_RANGE_10UA		= WGFMU_MEASURE_CURRENT_RANGE_OFFSET + 2
    WGFMU_MEASURE_CURRENT_RANGE_100UA		= WGFMU_MEASURE_CURRENT_RANGE_OFFSET + 3
    WGFMU_MEASURE_CURRENT_RANGE_1MA		    = WGFMU_MEASURE_CURRENT_RANGE_OFFSET + 4
    WGFMU_MEASURE_CURRENT_RANGE_10MA		= WGFMU_MEASURE_CURRENT_RANGE_OFFSET + 5

    # WGFMU_setMeasureEnabled
    WGFMU_MEASURE_ENABLED_OFFSET			= 7000
    WGFMU_MEASURE_ENABLED_DISABLE			= WGFMU_MEASURE_ENABLED_OFFSET + 0
    WGFMU_MEASURE_ENABLED_ENABLE			= WGFMU_MEASURE_ENABLED_OFFSET + 1

    # WGFMU_setTriggerOutMode
    WGFMU_TRIGGER_OUT_MODE_OFFSET			= 8000
    WGFMU_TRIGGER_OUT_MODE_DISABLE			= WGFMU_TRIGGER_OUT_MODE_OFFSET + 0
    WGFMU_TRIGGER_OUT_MODE_START_EXECUTION  = WGFMU_TRIGGER_OUT_MODE_OFFSET + 1
    WGFMU_TRIGGER_OUT_MODE_START_SEQUENCE	= WGFMU_TRIGGER_OUT_MODE_OFFSET + 2
    WGFMU_TRIGGER_OUT_MODE_START_PATTERN	= WGFMU_TRIGGER_OUT_MODE_OFFSET + 3
    WGFMU_TRIGGER_OUT_MODE_EVENT			= WGFMU_TRIGGER_OUT_MODE_OFFSET + 4

    WGFMU_TRIGGER_OUT_POLARITY_OFFSET		= 8100
    WGFMU_TRIGGER_OUT_POLARITY_POSITIVE	    = WGFMU_TRIGGER_OUT_POLARITY_OFFSET+ 0
    WGFMU_TRIGGER_OUT_POLARITY_NEGATIVE	    = WGFMU_TRIGGER_OUT_POLARITY_OFFSET+ 1

    # WGFMU_createMergedPattern
    WGFMU_AXIS_OFFSET						= 9000
    WGFMU_AXIS_TIME						    = WGFMU_AXIS_OFFSET + 0
    WGFMU_AXIS_VOLTAGE						= WGFMU_AXIS_OFFSET + 1

    # WGFMU_getStatus, WGFMU_getChannelStatus
    WGFMU_STATUS_OFFSET					    = 10000
    WGFMU_STATUS_COMPLETED					= WGFMU_STATUS_OFFSET + 0
    WGFMU_STATUS_DONE                       = WGFMU_STATUS_OFFSET + 1
    WGFMU_STATUS_RUNNING					= WGFMU_STATUS_OFFSET + 2
    WGFMU_STATUS_ABORT_COMPLETED			= WGFMU_STATUS_OFFSET + 3
    WGFMU_STATUS_ABORTED					= WGFMU_STATUS_OFFSET + 4
    WGFMU_STATUS_RUNNING_ILLEGAL			= WGFMU_STATUS_OFFSET + 5
    WGFMU_STATUS_IDLE						= WGFMU_STATUS_OFFSET + 6

    # WGFMU_isMeasureEventCompleted
    WGFMU_MEASURE_EVENT_OFFSET				= 11000
    WGFMU_MEASURE_EVENT_NOT_COMPLETED		= WGFMU_MEASURE_EVENT_OFFSET + 0
    WGFMU_MEASURE_EVENT_COMPLETED			= WGFMU_MEASURE_EVENT_OFFSET + 1

    # WGFMU_setMeasureEvent
    WGFMU_MEASURE_EVENT_DATA_OFFSET		    = 12000
    WGFMU_MEASURE_EVENT_DATA_AVERAGED		= WGFMU_MEASURE_EVENT_DATA_OFFSET + 0
    WGFMU_MEASURE_EVENT_DATA_RAW			= WGFMU_MEASURE_EVENT_DATA_OFFSET + 1


    def __init__(self, Instruments, Configuration, WaferChar=False, save=True, selfTest=False, writeData=False, Plotting=False):

        self.Modules = {}
        
        for path in glob.glob('ElectricalCharacterization/[!_]*.py'):
            name, ext = os.path.splitext(os.path.basename(path))
            self.Modules[name] = imp.load_source(name, path)
        
        self.Instruments = Instruments
        self.Configuration = Configuration
        self.getTools()
        self.ConfigCopy = None

        self.MeasQu = qu.Queue()
        self.MeasureLog = False
        
        self.estMultFactorB1530A = 1
        self.SubProcessThread = qu.Queue()
        self.deviceCharacterization = None
        
        '''
        only possible in PG or FastIV mode
        wgfmuStatus = self.wgfmu.getStatus()
        if not wgfmuStatus == self.WGFMU_STATUS_IDLE: 
            self.ErrorQueue.put("WGFMU: %s" %(self.wgfmu.getStatusFromCode(wgfmuStatus)))
        '''

        self.updateConfiguration(Configuration)
        self.writeData = writeData
        self.WaferChar = WaferChar
        self.save = save
        self.updateDateFolder()
        self.StatOutValues = dh.batch('DeviceSummary')
        self.rawData = qu.Queue()
        self.RDstart = qu.Queue()
        self.RDstop = qu.Queue()
        self.Selstart = qu.Queue()
        self.Selstop = qu.Queue()
        self.Stop = qu.Queue()
        self.DCHeader = []
        self.EnduranceData = []
        self.AdditionalHeader = []
        self.ExternalHeader = []
        
        self.cyc = []
        self.HRS = []
        self.LRS = []

        self.IVHRS = []
        self.IVLRS = []
        self.ImaxSet = []
        self.ImaxReset = []
        self.Vset = []
        self.Vreset = []
        self.IVcyc = []

    def checkInstrumentation(self):
        
        try:
            self.Instruments.checkInstrumentation()
            self.writeLog("Instrumentation Checked")
        except SystemError as e:
            self.Instruments.ReInitialize()
            start = tm.time()
            while not self.Instruments.ready:
                tm.sleep(0.01)
                if (tm.time() - start) > 2:
                    break
            self.getTools()


    def writeMeasLog(self, data):

        if isinstance(data, list):
            for entry in data:
                self.MeasQu.put(entry)
        else:
            self.MeasQu.put(data)

    def startMeasureLog(self):
        self.clearQu(self.MeasQu)
        self.MeasureLog = True
        self.MeasLogThread = th.Thread(target=std.writeMeasurmentLog, args=(self.deviceCharacterization, self, self.ConfigCopy, self.Instruments, self.MeasTypeClass))
        self.MeasLogThread.start()

    def getMeasLogQueue(self):
        return self.MeasQu

    def stopMeasureLog(self):
        self.MeasQu.put("Finished")
        self.MeasureLog = False

    def clearQu(self, qu):
        while not qu.empty():
            qu.get()

    def updateConfiguration(self, Configuration):

        self.Configuration = Configuration
        self.Mainfolder = self.Configuration.getMainFolder()
        self.WaferID = self.Configuration.getWaferID()
        self.Subfolder = self.Configuration.getSubfolder()
        self.DoYield = self.Configuration.getDoYield()
        self.device = self.Configuration.getDeviceName()
    
    def updateTools(self, Tools):
        Tools.ReInitialize()
        self.getTools()

    def writeDataToFile(self, header, data, Typ="", startCyc=None, endCyc=None, withDie=True, subFolder=None):
        
        filename= self.getFilename(Typ, startCyc, endCyc)
        folder = self.getFolder(withDie)
        data2 = cp.deepcopy(data)
        header2 = cp.deepcopy(header)
        thread =th.Thread(target = std.writeDataToFile , args=(header2, data2, folder, filename, self.MeasQu, subFolder))
        thread.start()
        self.threads.append(thread)

    def getPrimaryPulseGenerator(self):
        PG = self.Instruments.getPrimaryTool("PG")["Instrument"]
        return PG

    def getPrimaryOscilloscope(self):
        PG = self.Instruments.getPrimaryTool("OSC")["Instrument"]
        return PG

    def getPrimaryLeCroyOscilloscope(self):
        PG = self.Instruments.getPrimaryTool("LeCroyOsc")["Instrument"]
        return PG

    def getPrimaryB1500A(self):
        PG = self.Instruments.getPrimaryTool("B1500A")["Instrument"]
        return PG

    def getPrimaryModel(self, models):
        curRank = 1e30
        retModel = models[0]
        for mod in models:
            inst = self.Instruments.getInstrumentsByName(mod)
            if curRank > inst["Rank"] and inst['Instrument'] != None:
                retModel = mod
                curRank = inst["Rank"]
        return retModel

    def writeError(self, msg):
        self.ErrorQueue.put("Echar: %s" %(message))

    def getTools(self):
        tools = dict()
        try:
            self.B1500A = self.Instruments.getInstrumentsByName("Agilent_B1500A")[0]['Instrument']
            tools["B1500A"] = self.B1500A
        except (ValueError, TypeError, SystemError, IndexError) as message:
            self.ErrorQueue.put("Echar - getTools - B1500A - %s" %(message))
        
        try:    
            self.wgfmu = self.Instruments.getInstrumentsByName("Agilent_B1530A")[0]['Instrument']
            tools["wgfmu"] = self.wgfmu
        except (ValueError, TypeError, OSError, SystemError, IndexError) as message:
            self.ErrorQueue.put("Echar - getTools - WGFMU - %s" %(message))

        try:    
            self.Oscilloscope = self.Instruments.getPrimaryTool("OSC")["Instrument"]
            tools["Oscilloscope"] = self.Oscilloscope
        except (ValueError, TypeError, OSError, SystemError, IndexError) as message:
            self.ErrorQueue.put("Echar - getTools - Oscilloscope - %s" %(message))

        try:        
            self.PG81110A = self.Instruments.getInstrumentsByName("Agilent_PG81110A")[0]['Instrument']
            tools["PG81110A"] = self.PG81110A
        except (ValueError, TypeError, OSError, SystemError, IndexError) as message:
            self.ErrorQueue.put("Echar - getTools - PG 81110A - %s" %(message))

        try:        
            self.PGBNC765 = self.Instruments.getInstrumentsByName("BNC_Model765")[0]['Instrument']
            tools["PGBNC765"] = self.PGBNC765
        except (ValueError, TypeError, OSError, SystemError, IndexError) as message:
            self.ErrorQueue.put("Echar - getTools - PG BNC765 - %s" %(message))

        try:        
            self.E5274A = self.Instruments.getInstrumentsByName("Agilent_E5274A")[0]['Instrument']
            tools["E5274A"] = self.E5274A
        except (ValueError, TypeError, OSError, SystemError, IndexError) as message:
            self.ErrorQueue.put("Echar - getTools - E5274A - %s" %(message))

        try:
            self.Prober = self.Instruments.getProberInstrument()
            tools["Prober"] = self.Prober
        except (ValueError, TypeError, OSError, SystemError, IndexError) as message:
            self.ErrorQueue.put("Echar - getTools - Prober - %s" %(message))

        try:
            self.PulseGenerator = self.getPrimaryPulseGenerator()
            tools["PulseGenerator"] = self.PulseGenerator
        except (ValueError, TypeError, OSError, SystemError, IndexError) as message:
            self.ErrorQueue.put("Echar - getTools - PulseGenerator - %s" %(message))

        return tools

    def writeLog(self, entry):
        self.LogData.put(entry)
        if self.MeasureLog:
            self.MeasQu.put(entry)

    def setChannelParameter(self, chn, operationMode, forceVoltageRange=None, measureMode=None, measureCurrentRange=None, MeasureVoltageRange=None, ForceDelay=None, MeasureDelay=None):
        self.wgfmu.setChannelParameter(chn, operationMode, forceVoltageRange, measureMode, measureCurrentRange, MeasureVoltageRange, ForceDelay, MeasureDelay)
    
    def plotIVData(self, data):

        data['DieX'] = self.DieX
        data['DieY'] = self.DieY
        data['DevX'] = self.DevX
        data['DevY'] = self.DevY
        data['Folder'] = self.getFolder()

        self.IVplotData.put(cp.deepcopy(data))

    def dhValue(self, value, name, Unit=""):
        return dh.Value(self, value, name, self.DoYield, Unit)

    def dhAddRow(self, values, typ, cycleStart=None, cycleStop=None):
        cycles = []
        if cycleStart != None:
            cycles.append(cycleStart)
        if cycleStop != None:
            cycles.append(cycleStop)
        cycles = tuple(cycles)

        row = dh.Row(values,self.DieX,self.DieY,self.DevX,self.DevY,self.MatNormal,self.MatBit,typ, *cycles)
        self.StatOutValues.addRow(row)

    def updateDateFolder(self):
        timestamp = tm.strftime("%Y_%m_%d", self.localtime)
        self.DateFolder = timestamp
        return timestamp

    def updateTime(self):
        self.localtime = tm.localtime()

    def getChannelStatus(self):
        ret = None
        if self.wgfmuInUse: 
            ret = self.wgfmu.getMeasureStatus()
        elif self.B1500AInUse:
            ret = self.B1500A.getMeasureStatus()
        return ret
        
    def setWaferID(self, WaferID):
        if '/' in WaferID: 
            self.ValError("WaferID cannot contain '/'.")
        if '\\' in WaferID: 
            self.ValError("WaferID cannot contain '\\'.")
        self.WaferID = str(WaferID)
    
    def getConfiguration(self):
        return self.Configuration

    def deleteWaferID(self):
        self.WaferID = None

    def enableWaferCharacterization(self):
        self.WaferChar = True

    def disableWaferCharacterization(self):
        self.WaferChar = False

    def reset(self):
        self.curCycle = 1
        self.localtime = tm.localtime()
        self.starttime = tm.localtime()
        self.cyc = []
        self.HRS = []
        self.LRS = []

        self.IVHRS = []
        self.IVLRS = []
        self.ImaxSet = []
        self.ImaxReset = []
        self.Vset = []
        self.Vreset = []
        self.IVcyc = []
        self.Combinedheader = []
        self.EnduranceData = []
        self.AdditionalHeader = []
        self.Header = []
        del self.StatOutValues
        self.StatOutValues = dh.batch('DeviceSummary')
        del self.SubProcessThread
        self.SubProcessThread = qu.Queue()

        del self.rawData
        self.rawData = qu.Queue()
        del self.RDstart
        self.RDstart = qu.Queue()
        del self.RDstop
        self.RDstop = qu.Queue()
        del self.Stop
        self.Stop = qu.Queue()

        del self.AdditionalHeader 
        self.AdditionalHeader = []
        del self.Combinedheader
        self.Combinedheader = []

    def getWaferCharacterization(self):
        return self.WaferChar

    def emptyFinish(self):
        while not self.finished.empty():
            self.finished.get()

    def executeMeasurement(self, folder, name, parameters):
        try:
            func = getattr(self.Modules[folder],name)
            ret = func(self, *parameters)
            return ret
        except ToolInputError as e:
            self.ErrorQueue.put(e)
            return "stop"

###########################################################################################################################
    
    def ProbeStationTemp(self, temperature, postWait=30, margin=0.25, refreshTime=0.1):
        """ 
        set the prober temperature
        temperature: prober temperature 25C -300C 
        postWait: wait time for stabilization in seconds
        margin: temperature margin in percentage
        refreshTime: refresh check of chuck temperature
        """
        self.Prober.SetHeaterTemp(temperature)
        
        while True:

            temp = self.Prober.getHeaterTemp()

            tmargin = margin*temperature

            if temperature-tmargin < temp < temperature+tmargin:
                break

            while not self.Stop.empty():
                stop = self.Stop.get()
            if stop:    
                break
            
            tm.sleep(refreshTime)
        
        startWait = tm.time()
        while True:
            if tm.time() > startWait+postWait:
                break
            while not self.Stop.empty():
                stop = self.Stop.get()
            if stop:    
                break
            tm.sleep(refreshTime)



    def getFolder(self, withDie=True):

        if self.WaferID == None:
            folder = "%s/%s" %(self.Mainfolder,self.DateFolder)
        else:
            folder = "%s/%s/%s" %(self.Mainfolder,self.DateFolder, self.WaferID)

        if not self.Subfolder == "":
            folder = "%s/%s" %(folder, self.Subfolder)
            
        if self.WaferChar and withDie and self.Configuration.getMultipleDies():
            folder = "%s/DieX%sY%s" %(folder, str(self.DieX), str(self.DieY))

        return folder

    def getFilename(self, MeasType, startCyc=None, endCyc=None):
        
        timestamp = dt.now().strftime("%Y%m%d_%H-%M-%S-%f")
        #timestamp = tm.strftime("%Y%m%d_%H-%M-%S", tm.localtime())
        filename = "%s_%s_%s" %(MeasType,timestamp,self.device)
        if self.WaferChar:
            filename = "%s_DevX%dY%d_DieX%dY%d" %(filename,self.DevX, self.DevY, self.DieX, self.DieY)
        if self.Configuration.getUseMatrix() and self.Instruments.getMatrixInstrument() != None:
            filename = "%s_MatDev%d" %(filename, self.MatDev)

        if startCyc == None:
            filename = "%s" %(filename)
        else:
            try:
                filename = "%s_%d" %(filename, int(startCyc))
            except ValueError:
                filename = "%s" %(filename)       
        if endCyc == None:
            filename = "%s.csv" %(filename)
        else:
            try:
                filename = "%s-%d.csv" %(filename, int(endCyc))
            except ValueError:
                filename = "%s.csv" %(filename)

        return filename
        

    def checkStop(self):
        
        stop = False
        while not self.Stop.empty():
            stop = self.Stop.get()
        return stop

    def clearStop(self):
        self.clearQu(self.Stop)

    def __write(self, command):
        None
        #(command)

    def SysError(self, error):
        raise SystemError("WGFMU System Error: %s" %(error))

    def ValError(self, error):
        raise SystemError("WGFMU Value Error: %s" %(error))
    
    def TypError(self, error):
        raise SystemError("WGFMU Type Error: %s" %(error))


class SMU:

    SMUs = []
    
    def __init__(self, eChar, tools=[]):

        self.tools = tools
        self.SMUs = []

        for tool in tools:
            self.SMUs.append(tool.getNumberOfSMU())