"""
Written by: Karsten Beckmann and Maximilian Liehr
Institution: SUNY Polytechnic Institute
Date: 7/15/2018

This program is a wrapper for the use of the Keysight B1530A. It extends the standard use by an offline/online mode.
A reversal of the writing of the pulsing parameters such as: 
- Voltage Range
- Measurement range
- operational mode 
- etc 
allows for the detection of wrong pattern and the identification of the exact problem, hence it is encouraged to use following control pattern: 
1. write the ranges/modes offline
2. write pulse patternf
3. turn B1530 online 
4. start execution
5. retrieve data

If started in online mode, a sychronization before the execute is highly encouraded to make sure all the set values are transported to the B1530A

For more information please use the Keysight B1530A WGFMU remote control manual.
"""

import datetime as dt
import time as tm
import traceback
import types as tp
from ctypes import *
import math as ma
import os as os
import pyvisa as vs
import traceback
import numpy as np
import queue as qu


#Keysight B1530A WGFMU: 
#The WGFMU (B1530A) instrument Library muss be installed prior to executing this programan
class Agilent_B1530A:
    
    mainframe = 'B1500A'

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

    __inst = None
    NumChn = None
    Averaging = 1
    __rdata = WGFMU_MEASURE_EVENT_DATA_AVERAGED

    #Python type values
    __VForceRange = []
    __VMeasureRange = []
    __VForceDelay = []
    __IMeasureRange = []
    __MeasureEnable = []
    __OperationMode = []
    __MeasureMode = []
    __MeasureDelay = []
    __TriggerOutMode = []
    __TriggerOutPol = []
    __Name = []
    __Timeout = None
    __rdata = None
    __ChnID = []
    UsedPattern = []
    __connected = []
    __usedChannel = []
    __GPIB = None
    
    __online = False
    __calibration = False
    __test = False

    __PatternIteration = 1
    __WarningLevel = None

    CalibrationResult = None
    TestResult = None
    __LogFile = None
    __TimeOutputSuffix = range(1,21,1)
    __CurrentOutputSuffix = range(1,21,1)
    __VoltageOutputSuffix = range(1,21,1)

    __PulseHeader = []
    __WritePulseHeader = True

    __MeasComplete = 0
    __MeasTotal = 1
    __MeasureTime = 0
    
    __delay = 0.05
    printOutput = False
    CritErrorRep = 10

    STB_REP = 10      # in iterations
    STB_REP_TIME = 10 #in seconds

    def __init__(self, GPIB, instrument=None, online=False, ChannelIDs=None, calibration=False, selfTest=False, VForceRange=None, VMeasureRange=None, 
                    IMeasureRange=None, VForceDelay=None, MeasureDelay=None, MeasureMode=None, TriggerOutputMode=None, TriggerOutputPolarity=None, B1500=None):
        
        if instrument == None:
            self.__inst = WinDLL("C:/Windows/System32/wgfmu.dll")
        else:
            self.__inst = instrument
        
        self.__B1500A = B1500
        self.__GPIB = GPIB

        self.ElapsedTime = qu.Queue()
        self.StatusQueue = qu.Queue()
        self.TotalTime = qu.Queue()
        self.LogQueue = qu.Queue()

        self.ErrQueue = qu.Queue()

        self.cwd = os.getcwd()
        self.logFileName = "logB1530A"
        self.log = False
        try:
            if os.path.isfile("%s.txt"%(self.logFileName)):
                os.remove("%s.txt"%(self.logFileName))
        except (PermissionError):
            None

        self.timeout = 60
        if not isinstance(calibration,bool):
            self.TypError("Calibration must be of type boolean")
        if not isinstance(selfTest,bool):
            self.TypError("SelfTest must be of type boolean")
        if not isinstance(online,bool):
            self.TypError("Online must be of type boolean")

        if not online:
            if calibration:
                self.__write("Calibration can only be performed if the tool is online.")
                
            if selfTest:
                self.__write("The Self Test can only be performed if the tool is online.")
        else:
            self.turnOnline()
        
        self.__inst.WGFMU_clear()
        self.__write("WGFMU_clear()")
        self.__PatternIteration = 1
        self.__connected = []
        self.__ChnIDs = []
        if ChannelIDs == None and online==True:
            self.getChannelIDs()
            Cons = []
        elif ChannelIDs == None and online==False: 
            self.ValError("Please specify the channel IDs or start the tool in online mode to retrieve them automatically.")
        else: 
            if isinstance(ChannelIDs, type([])):
                for chn in ChannelIDs:
                    self.checkChannel(chn)
            else:
                self.TypError("ChannelIDs must be a list of Channel numbers. ")
            ChnIDs = ChannelIDs
        
        Cons.append(self.__ChnIDs)

        if not VForceRange == None:
            Cons.append(VForceRange)
        if not VMeasureRange == None:
            Cons.append(VMeasureRange)
        if not IMeasureRange == None:
            Cons.append(IMeasureRange)
        if not VForceDelay == None:
            Cons.append(VForceDelay)
        if not MeasureDelay == None:
            Cons.append(MeasureDelay)
        if not MeasureMode == None:
            Cons.append(MeasureMode)
        if not TriggerOutputMode == None:
            Cons.append(TriggerOutputMode)
        if not TriggerOutputPolarity == None:
            Cons.append(TriggerOutputPolarity)

        self.checkArrayConsistancy(Cons, "All Value Arrays must have the same dimension as the number of Channels.")
        self.clearLibrary()
        if online:
            self.turnOnline(initialize=True, selfTest=selfTest,calibration=calibration)
            self.turnOffline()
        else:
            self.initialize()

    def getLogQueue(self):
        return self.LogQueue
        
    def getStatusQueue(self):
        return self.StatusQueue

    def getErrorQueue(self):
        return self.ErrQueue

    def startLog(self):
        self.log = True
        n = 0
        while True:
            try:
                self.__LogFile = open("%s.txt" %(self.logFileName), 'a')
                break
            except PermissionError as e:
                self.ErrQueue.put("B1530A Log File: %s" %(e))
                self.logFileName = "%s_v%d"%(self.logFileName, n)
                n = n+1
            if n == 10:
                self.ErrQueue.put("B1530A Log File: Not able to create Log File. New LogFile name: %s" %(self.logFileName))
                self.SysError("B1530A Log File: Not able to create Log File")

    def endLog(self):
        if self.log:
            self.__LogFile.close()
        self.log = False
    
    def reset(self):
        
        if self.__B1500A != None:
            self.__B1500A.reset()

    def isOnline(self):
        return self.__online

    #Turn the B1530A from Offline to Online mode
    def turnOnline(self, calibration=False, selfTest=False, initialize=False, synchronize=False):
        
        ret = self.__openSession()
        if ret == 0:
            self.__online = True
        elif ret == -1:
            self.__online = False

        if not isinstance(calibration, bool):
            self.TypError("Calibration marker must be of boolean type.")
        if not isinstance(selfTest, bool):
            self.TypError("Self Test marker must be of boolean type.")
        if not isinstance(initialize, bool):
            self.TypError("Initialize marker must be of boolean type.")
        if not isinstance(synchronize, bool):
            self.TypError("Sychronization marker must be of boolean type.")
        if calibration:
            self.performCalibration()
        if selfTest:
            self.doSelfTest()
        if initialize:
            self.initialize()
        if synchronize:
            self.synchronize()
            self.checkError(self.__inst.WGFMU_update())
            self.__write("WGFMU_update()")
    
    def synchronize(self):
        if self.__online:
            for chn in self.__ChnIDs:
                self.setOperationMode(chn, self.__OperationMode[self.__getChnIndex(chn)])
                self.setForceVoltageRange(chn, self.__VForceRange[self.__getChnIndex(chn)])
                self.setMeasureMode(chn, self.__MeasureMode[self.__getChnIndex(chn)])
                self.setMeasureCurrentRange(chn, self.__IMeasureRange[self.__getChnIndex(chn)])
                self.setMeasureVoltageRange(chn, self.__VMeasureRange[self.__getChnIndex(chn)])
                self.setForceDelay(chn, self.__VForceDelay[self.__getChnIndex(chn)])
                self.setMeasureDelay(chn, self.__MeasureDelay[self.__getChnIndex(chn)])
                self.setMeasureEnabled(chn, self.__MeasureEnable[self.__getChnIndex(chn)])
                self.setTriggerOutMode(chn, self.__TriggerOutMode[self.__getChnIndex(chn)], self.__TriggerOutPol[self.__getChnIndex(chn)])
            self.setTimeout(self.__Timeout)
        else: 
            self.__write("Sychronization can online be performed if B1530 is in online mode.")

    #Set all relevant Channel parameter: 
    #Operational Mode:      2000: DC mode, 2001: Fast IV mode, 2002: PG mode, 2003: SMU Mode
    #forceVoltageRange:     3000: Auto Range, 3001: +-3V fixed, 3002: +-5V fixed, 3003: -10V fixed, 3004: +10V fixed
    #measureMode:           4000: Voltage measurement mode ,4001: Current measurement mode
    #measureCurrentRange:   6001: 1uA, 6002: 10uA, 6003: 100uA, 6004: 1mA, 6005: 10mA
    #measureVoltageRange:   5001: +-5V, 5002, +-10V
    #ForceDelay:            -50e10-9 (-50 ns) to 50e10-9 (50 ns), in 625e10-12(625 ps) resolution.
    #measureDelay:          -50e10-9 (-50 ns) to 50e10-9 (50 ns), in 625e10-12(625 ps) resolution.
    #measureEnabled:        7000: Measure Disabled, 7001: Measure Enabled
    def setChannelParameter(self, chn, operationMode, forceVoltageRange=None, measureMode=None, measureCurrentRange=None, 
                                MeasureVoltageRange=None, ForceDelay=None, MeasureDelay=None, measureEnabled=None):
        
        self.setOperationMode(chn, operationMode)
        if forceVoltageRange != None:
            self.setForceVoltageRange(chn, forceVoltageRange)
        if measureMode != None:
            self.setMeasureMode(chn, measureMode)
        if measureCurrentRange != None:
            self.setMeasureCurrentRange(chn, measureCurrentRange)
        if MeasureVoltageRange != None:
            self.setMeasureVoltageRange(chn, MeasureVoltageRange)
        if ForceDelay != None:
            self.setForceDelay(chn, ForceDelay)
        if MeasureDelay != None:
            self.setMeasureDelay(chn, MeasureDelay)

    def waitUntilCompleted(self):

        self.__write("WGFMU_waitUntilCompleted()")
        ret = self.checkErrorCritical("WGFMU_waitUntilCompleted")
        self.__write("waitUntilComplete: %s" %(ret))
        return ret


    def getMeasureStatus(self):
        complete = self.__MeasComplete
        totalevent = self.__MeasTotal
        totaltime = self.__MeasureTime

        FinishedPercentage = complete/totalevent*100
        FinishedTime = FinishedPercentage/100*totaltime

        return {'TotalTime': totaltime, 'Percentage': FinishedPercentage, 'CompletedTime': FinishedTime}

    def __getChnIndex(self, chn):
        n=0
        for chnComp in self.__ChnIDs:
            if chnComp == chn:
                return n
            n+=1

    def turnOffline(self):
        ret = 0
        if self.__online:
            for n in range (len(self.__ChnIDs)):
                if self.__connected[n]:
                    self.disconnect(self.__ChnIDs[n])
                
            ret = self.__closeSession()
            self.__online = False
        return ret

    def performCalibration(self):
        if self.__online:
            res = c_int()
            detail = (c_char*256)()
            size = c_int(256)
            self.__write("WGFMU_doSelfCalibration(%s,%s,%s)" %(byref(res),byref(detail),byref(size)))
            self.checkError(self.__inst.WGFMU_doSelfCalibration(byref(res),byref(detail),byref(size)))
            self.CalibrationResult = res.value
            if res.value == self.WGFMU_NO_ERROR:
                stringRet = "WGFMU: Calibration was successfull, Mainframe and all modules passed self-calibration."
            else:
                stringRet = "WGFMU: Calibration was not successfull, Please check on the error code: %d" %(int(res))
            det = detail.value
        else: 
            stringRet = "WGFMU:  Calibration was not successfull, it can only be performed if tool in in Online mode"
            det = 0

        self.__write(stringRet)
        self.__write(res.value)
        return {'Message': stringRet, 'Detail': det}

    def doSelfTest(self):
        if self.__online:
            res = c_int()
            res.value = 1
            detail = (c_char*512)()
            size = c_int()
            size.value = 512
            self.__write("WGFMU_doSelfTest(%s,%s,%s)" %(byref(res),byref(detail),byref(size)))
            self.checkError(self.__inst.WGFMU_doSelfTest(byref(res),byref(detail),byref(size)))
            self.__write("B1530 Self Test Result: %s" %(res))
            self.TestResult = res
            if int(res.value) == self.WGFMU_NO_ERROR:
                return "%d: WGFMU Self Test was successfull, Mainframe and all modules passed self-calibration." %(int(res.value))
            else:
                return "%d: WGFMU Self Test was not successfull, Please check on the error code." %(int(res.value))
        else:
            return "0: WGFMU: cannot perform Self test in offline mode."

    def setDataOutputMode(self, mode):
        if not isinstance(mode, int):
            self.TypError("Data Output Mode must be an integer either 12000 (Averaging) or 12001 (raw data).")
        if not (mode == 12000 or mode == 12001):
            self.ValError("Data Output Mode must be an integer either 12000 (Averaging) or 12001 (raw data).")
        self.__rdata = mode
        return mode

    # sets the averaging as a percentage of the measured interval (rounds up to a resolution of 10ns)
    # 0 sets no averaging
    def setAveraging(self, averaging):
        if not isinstance(averaging, int):
            self.TypError("Averaging must be an integer between 0 and 100. (Given %s)" %(averaging))
        if averaging < 0 or averaging > 100: 
            self.ValError("Averaging must be an integer between 0 and 100. (Given %s)" %(averaging))

        self.Averaging = averaging/100

    def setTimeout(self, timeout):
        if not isinstance(timeout, (float, int)):
            self.TypError("Timeout value must be of type float and larger than 1s with a resolution of 1us. (Given %s)" %(timeout))
        if not (timeout/1e-6).is_integer():
            self.ValError("Timeout value must be of type float and larger than 1s with a resolution of 1us. (Given %s)" %(timeout))
        if timeout < 1:
            self.ValError("Timeout value must be of type float and larger than 1s with a resolution of 1us. (Given %s)" %(timeout))
        self.__Timeout = timeout
        cTimeout = c_double(timeout)
        if self.__online:
            self.__write("WGFMU_setTimeout(%s)" %(timeout))
            self.checkError(self.__inst.WGFMU_setTimeout(cTimeout))

    def setWarningLevel(self, level):
        if not isinstance(level, (int)):
            self.TypError("Warning level must be an integer from 1000 to 1003. (Given %s)" %(level))
        if not level in [1000,1001,1002,1003] :
            self.TypError("Warning level must be an integer from 1000 to 1003. (Given %s)" %(level))
        if self.__online:
            self.__write("WGFMU_setWarningLevel()" %(level))
            self.checkError(self.__inst.WGFMU_setWarningLevel(level))

    def execute(self):
        if self.__online:
            
            self.__write("WGFMU_execute()")
            self.checkError(self.__inst.WGFMU_execute())
            
            for n in range(3):
                self.waitUntilCompleted()
                tm.sleep(1)
            
            first = True

            timeout = self.timeout
            tstart = tm.time()
            while True:
                Status = None
                Status = self.getStatus()
                print(Status)

                self.ElapsedTime.put(Status['ElapsedTime'])
                self.TotalTime.put('TotalTime')
                if Status['Status'] <= 10006 and Status['Status'] >= 10000:
                    self.StatusQueue.put(self.getStatusFromCode(Status['Status']))
                    tstart = tm.time()
                else: 
                    tm.sleep(1)
                    continue

                if Status['Status']  == 10000 or Status['Status'] ==  10003:
                    break
                
                if  Status['Status'] ==  10006:
                    self.SysError("WGFMU state is Idle")

                
                if not first:
                    self.ElapsedTime.get()
                    self.TotalTime.get()
                    first = False
                
                if (tstart + timeout) < tm.time():
                    print("sysError")
                    self.SysError("Timeout to move data into buffer")

                tm.sleep(1)
                
            tm.sleep(1)
            ret = 0
        else:
            ret = "Execute can only be performed if the tool is online."
        print("ret", ret, Status)
        return ret
    
    def exportASCII(self, fname):
        if self.__online:
            if not isinstance(fname, str):
                self.TypError("the file name must be a string")
            cFname = c_char_p()
            cFname.value = fname.encode(encoding='utf-8')
            self.__write("WGFMU_exportAscii(%s)" %(fname))
            ret  = self.checkError(self.__inst.WGFMU_exportAscii(cFname))
            return ret
        else:
            return "Export ASCII file can only be performed if the tool is online."


    def getTimeout(self):
        return self.__Timeout

    def getChannelIDs(self):
        if self.__online:
            cSize = c_int()
            size = self.__getChannelIDSize()
            cSize.value = size
            ret = (c_int*size)()
            self.__write("WGFMU_getChannelIds(%s,%s)" %(byref(ret), byref(cSize)))
            self.checkError(self.__inst.WGFMU_getChannelIds(byref(ret), byref(cSize)))
            self.__ChnIDs = list(ret)
            self.__NumChn = len(list(ret))
            return {'Channels': list(ret), 'Size':cSize.value}
        else:
            return {'Channels': list(self.__ChnIDs), 'Size':len(self.__ChnIDs)}

    def __getChannelIDSize(self):
        if self.__online:
            cSize = c_int()
            self.__write("WGFMU_getChannelIdSize(%s)" %(byref(cSize)))
            self.checkError(self.__inst.WGFMU_getChannelIdSize(byref(cSize)))
            return int(cSize.value)
        else:
            return "Channel ID Size can only be retrieved in online mode."
    
    def getChannelStatus(self, chn):
        if self.__online:
            self.checkChannel(chn)
            stat = (c_int*1)()
            cElapT = (c_double*1)()
            cTotalT = (c_double*1)()
            self.__write("WGFMU_getChannelStatus(%s,%s,%s,%s)" %(chn, byref(stat), byref(cElapT), byref(cTotalT)))
            self.checkError(self.__inst.WGFMU_getChannelStatus(chn, byref(stat), byref(cElapT), byref(cTotalT)))
            return {'Status': list(stat)[0], 'ElapsedTime': list(cElapT)[0], 'TotalTime':list(cTotalT)[0]}
        else:
            return "Channel Status can only be retrieved in online mode."

    def getCompleteMeasureEventSize(self, chn):
        self.checkChannel(chn)
        cComplete = (c_int*1)()
        cTotal = (c_int*1)()
        self.__write("WGFMU_getCompletedMeasureEventSize(%s,%s,%s)" %(chn, byref(cComplete), byref(cTotal)))
        self.checkError(self.__inst.WGFMU_getCompletedMeasureEventSize(int(chn), byref(cComplete), byref(cTotal)))
        return {'CompletedEvents': list(cComplete)[0], 'TotalEvents': list(cTotal)[0]}

    def getError(self):
        cSize = c_int()
        size = self.getErrorSize()
        cSize.value = size
        ret = (c_int*size)()
        self.__write("WGFMU_getError(%s,%s)" %(byref(ret), size))
        self.checkError(self.__inst.WGFMU_getError(byref(ret), cSize))
        return ret.value

    def getErrorSize(self):
        cSize = c_int()
        self.__write("WGFMU_getErrorSize(%s)" %(byref(cSize)))
        self.checkError(self.__inst.WGFMU_getErrorSize(byref(cSize)))
        return (int(cSize.value))
    
    def getErrorSummary(self):
        cSize = c_int()
        size = self.getErrorSize()
        cSize.value = size
        ret = (c_int*size)()
        self.__write("WGFMU_getErrorSummary(%s,%s)" %(byref(ret), byref(cSize)))
        self.checkError(self.__inst.WGFMU_getErrorSummary(byref(ret), cSize))
        return ret.value

    def getErrorSummarySize(self):
        cSize = c_int()
        self.__write("WGFMU_getErrorSummarySize(%s)" %(byref(cSize)))
        self.checkError(self.__inst.WGFMU_getErrorSummarySize(byref(cSize)))
        return (int(cSize.value))

    def __getForceDelay(self, chn):
        self.checkChannel(chn)
        cDelay = c_double()
        self.__write("WGFMU_getForceDelay(%s,%s)" %(chn, byref(cDelay)))
        self.checkError(self.__inst.WGFMU_getForceDelay(chn, byref(cDelay)))
        return cDelay.value
    
    def getForceDelay(self, chn):
        self.checkChannel(chn)
        return self.__VForceDelay[self.__getChnIndex(chn)]

    #This function specifies a channel and an index of sequence data, and returns the
    #corresponding setup data (time and voltage).
    def getForceValue(self, chn, index):
        self.checkChannel(chn)
        self.checkSeqIndex(index)
        cIndex = c_double(index)
        cIndex.value = index
        cTime = c_double()
        cVolt = c_double()
        self.__write("WGFMU_getForceValue(%s,%s,%s,%s)" %(chn, index, byref(cTime), byref(cVolt)))
        self.checkError(self.__inst.WGFMU_getForceValue(chn, cIndex, byref(cTime), byref(cVolt)))
        return {'Index': index, 'Time': cTime.value, 'Voltage': cVolt.value}

    #This function specifies a channel and an index of sequence data, and returns the
    #corresponding setup data (time and voltage).
    def getForceValues(self, chn, index):
        self.checkChannel(chn)
        self.checkSeqIndex(index)
        length = self.__getForceValueSize(chn)
        cIndex = c_double(index)
        cLength = c_int()
        cLength.value = length
        cTime = c_double()*length
        cVolt = c_double()*length
        self.__write("WGFMU_getForceValues(%s,%s,%s,%s,%s)" %(chn, index, byref(cLength), byref(cTime), byref(cVolt)))
        self.checkError(self.__inst.WGFMU_getForceValues(chn, cIndex, byref(cLength), byref(cTime), byref(cVolt)))
        return {'Index': index, 'Length': cLength.value, 'Time': cTime.value, 'Voltage': cVolt.value}

    def __getForceValueSize(self, chn):
        self.checkChannel(chn)
        cSize = c_int()
        self.__write("WGFMU_getForceValueSize(%s,%s)" %(chn, byref(cSize)))
        self.checkError(self.__inst.WGFMU_getForceValueSize(chn, byref(cSize)))
        return int(cSize.value)

    def getForceVoltageRange(self, chn):
        self.checkChannel(chn)
        cRange = c_int()
        if self.__online:
            self.__write("WGFMU_getForceVoltageRange(%s,%s)" %(chn, byref(cRange)))
            self.checkError(self.__inst.WGFMU_getForceVoltageRange(chn, byref(cRange)))
            return {'Status': 'online', 'Value':int(cRange.value)}
        else:
            return {'Status': 'offline', 'Value':self.__VForceRange(self.__getChnIndex(chn))}

    def getInterpolatedForceValue(self, chn, Time):
        self.checkChannel(chn)
        self.checkTime(Time)
        cTime = c_double(Time)
        cVolt = c_int()
        self.__write("WGFMU_getInterpolatedForceValue(%s,%s,%s)" %(chn ,Time, byref(cVolt)))
        self.checkError(self.__inst.WGFMU_getInterpolatedForceValue(chn, cTime, byref(cVolt)))
        return int(cVolt.value)
    
    def getMeasureCurrentRange(self, chn):
        self.checkChannel(chn)
        cRange = c_int()
        if self.__online:
            self.__write("WGFMU_getMeasureCurrentRange(%s,%s)" %(chn, byref(cRange)))
            self.checkError(self.__inst.WGFMU_getMeasureCurrentRange(chn, byref(cRange)))
            return {'Status': 'online', 'Value':int(cRange.value)}
        else:
            return {'Status': 'offline', 'Value':self.__MeasureDelay(self.__getChnIndex(chn))}
    
    def getMeasureDelay(self, chn):
        self.checkChannel(chn)
        cDelay = c_int()
        if self.__online:
            self.__write("WGFMU_getMeasureDelay(%s,%s)" %(chn, byref(cDelay)))
            self.checkError(self.__inst.WGFMU_getMeasureDelay(chn, byref(cDelay)))
            return {'Status': 'online', 'Value':int(cDelay.value)}
        else:
            return {'Status': 'offline', 'Value':self.__MeasureDelay(self.__getChnIndex(chn))}

    def getMeasureEvents(self, chn, MeasId=0):
        self.checkChannel(chn)
        size = self.getMeasureEventSize(chn)['Size'] - MeasId


        cPattern = create_string_buffer(512)
        cEvent = create_string_buffer(512)

        cSize = c_int(size)
        cSize.value = size
        cCycle = (c_int*size)()
        cLoop = (c_double*size)()
        cCount = (c_int*size)()
        cIndex = (c_int*size)()
        cLength = (c_int*size)()

        Pattern = []
        Event = []
        cycle = []
        loop = []
        count = []
        index = []
        length = []

        for n in range (MeasId, size, 1):

            self.checkError(self.__inst.WGFMU_getMeasureEvent(chn, MeasId, cPattern, 
                            cEvent, byref(cCycle), byref(cLoop), byref(cCount), byref(cIndex), byref(cLength)))
            self.__write("WGFMU_getMeasureEvent(%s,%s,%s,%s,%s,%s,%s,%s,%s)" %(chn, MeasId, Pattern, 
                            cEvent, byref(cCycle), byref(cLoop), byref(cCount), byref(cIndex), byref(cLength)))

            Pattern.append(self.decodeBytes(cPattern))
            Event.append(self.decodeBytes(cEvent))
            cycle.append(list(cCycle)[0])
            loop.append(list(cLoop)[0])
            count.append(list(cCount)[0])
            index.append(list(cIndex)[0])
            length.append(list(cLength)[0])

        return {'Pattern': Pattern , 'Event': Event , 'Cycle': cycle, 'Loop': loop, 'Count': count, 'Index': index, 'Length': length}

    def getMeasureEventSize(self, chn):
        self.checkChannel(chn)
        cSize = (c_int*1)()
        self.__write("WGFMU_getMeasureEventSize(%s,%s)" %(chn, byref(cSize)))
        self.checkError(self.__inst.WGFMU_getMeasureEventSize(chn, byref(cSize)))
        ret = {'Size': list(cSize)[0]}
        return ret

    def decodeBytes(self, pattern):
        p = ""
        for x in pattern:
            if not x == b'\x00':
                p = "%s%s" %(p,x.decode("utf-8"))
        return str(p)

    #This function specifies a channel and a range of measurement points, and returns the
    #measurement data (time and value) for the points.
    def getMeasureValues(self, chn, index=0):
        if self.__online:
            self.checkChannel(chn)
            cIndex = self.checkSeqIndex(index)
            MVS = self.__getMeasureValuesSize(chn)
            length = MVS['Completed']-index

            if length > 0:
                cLength = c_int(length)
                cTime = (c_double*length)()
                cValue = (c_double*length)()
                self.__write("WGFMU_getMeasureValues(%s,%s,%s,%s,%s)" %(chn, cIndex, byref(cLength), byref(cTime), byref(cValue)))
                self.checkError(self.__inst.WGFMU_getMeasureValues(chn, cIndex, byref(cLength), byref(cTime), byref(cValue)))
                return {'Index': index, 'Length': cLength.value, 'Time': list(cTime), 'MeasValue': list(cValue)}
            else:
                return {'Index': index, 'Length': 0, 'Time': [], 'MeasValue': []}
        else:
            return "Measure Values can only be retrieved in online mode."

    def __getMeasureValuesSize(self, chn):
        self.checkChannel(chn)
        cComplete = (c_int*1)()
        cTotal = (c_int*1)()
        #cTotal.value = 0
        self.__write("WGFMU_getMeasureValueSize(%s,%s,%s)" %(chn, byref(cComplete), byref(cTotal)))
        self.checkError(self.__inst.WGFMU_getMeasureValueSize(chn, byref(cComplete), byref(cTotal)))
        ret = {'Completed': list(cComplete)[0], 'Total': list(cTotal)[0]}
        return ret

    def __getMeasureVoltageRange(self, chn):
        self.checkChannel(chn)
        cRange = c_int()
        self.__write("WGFMU_getMeasureVoltageRange(%s,%s)" %(chn, byref(cRange)))
        self.checkError(self.__inst.WGFMU_getMeasureVoltageRange(chn, byref(cRange)))
        return int(cRange.value)

    def __getOperationMode(self, chn):
        self.checkChannel(chn)
        cMode = c_int()
        self.__write("WGFMU_getOperationMode(%s,%s)" %(chn, byref(cMode)))
        self.checkError(self.__inst.WGFMU_getOperationMode(chn, byref(cMode)))
        return int(cMode.value)
    
    def getOperationMode(self, chn):
        self.checkChannel(chn)
        return self.__OperationMode[self.__getChnIndex(chn)]
    
    def getMeasureVoltageRange(self, chn):
        self.checkChannel(chn)
        return self.__VMeasureRange[self.__getChnIndex(chn)]

    def getStatus(self):
        if self.__online:
            cStatus = c_int()
            cElapT = c_double()
            cTotalT = c_double()
            jobDone = False
            n = 0
            
            err = ""
            for n in range(10):
                try:
                    self.checkError(self.__inst.WGFMU_getStatus(byref(cStatus), byref(cElapT), byref(cTotalT)))
                    self.__write("WGFMU_getStatus(%s,%s,%s)" %(cStatus.value, cElapT.value, cTotalT.value))
                    jobDone = True
                except SystemError as e:
                    self.ErrQueue.put(e)
                    err = str(e)
                    try:   
                        if int(str(e).split(':')[0]) == -6:
                            break
                    except ValueError:
                        None

            if not jobDone:
                self.SysError(err)
                
            return {'Status': cStatus.value, 'ElapsedTime': cElapT.value, 'TotalTime': cTotalT.value}
        else:
            return {'Status': "Status can only be read in offline mode.", 'ElapsedTime': 0, 'TotalTime':0}
    
    def initialize(self):
        
        NumChn = self.__NumChn
        self.__VForceRange =    [self.WGFMU_FORCE_VOLTAGE_RANGE_AUTO]*NumChn
        self.__VMeasureRange =  [self.WGFMU_MEASURE_VOLTAGE_RANGE_10V]*NumChn
        self.__VForceDelay =    [0]*NumChn
        self.__MeasureDelay =   [0]*NumChn
        self.__IMeasureRange =  [self.WGFMU_MEASURE_CURRENT_RANGE_10MA]*NumChn
        self.__MeasureEnable =  [self.WGFMU_MEASURE_ENABLED_DISABLE]*NumChn
        self.__OperationMode =  [self.WGFMU_OPERATION_MODE_SMU]*NumChn
        self.__MeasureMode =    [self.WGFMU_MEASURE_MODE_VOLTAGE]*NumChn
        self.__TriggerOutMode = [self.WGFMU_TRIGGER_OUT_MODE_DISABLE]*NumChn
        self.__TriggerOutPol =  [self.WGFMU_TRIGGER_OUT_POLARITY_POSITIVE]*NumChn
        self.__Timeout = 100
        self.__rdata =  self.WGFMU_MEASURE_EVENT_DATA_AVERAGED
        self.__WarningLevel = self.WGFMU_WARNING_LEVEL_NORMAL
        
        self.UsedPattern = []
        self.__PulseHeader = []

        self.__usedChannel = [False]*NumChn
        self.__connected = [False]*NumChn
        self.__Name = ['']*NumChn

        self.enableWritePulseHeader()
        ret = 0
        if self.__online:
            self.__write("WGFMU_initialize()")
            ret = self.checkError(self.__inst.WGFMU_initialize())
        return ret
    
    def isMeaureEnabled(self, chn):
        ret = self.__MeasureEnable[self.__getChnIndex(chn)]
        return ret

    def setLogfile(self, Logfile):
        if not isinstance(Logfile, str):
            self.TypError("Logfile must be a string")
        self.__LogFile = Logfile

    def openLogFile(self):
        if self.__LogFile == None:
            self.__write("Logfile name is not defined.")
        else:
            cFname = c_char_p(self.__LogFile)
            self.__write("WGFMU_openLogFile(%s)" %(self.__LogFile))
            self.checkError(self.__inst.WGFMU_openLogFile(cFname))
    
    def checkEventsNo(self, EventsNo):
        if not isinstance(EventsNo, int):
            self.TypError("Events Number of the measurement event to read setup must be an integer from 1 total number of measurement events - measId")
        if EventsNo < 1: 
            self.ValError("Events Number of the measurement event to read setup must be an integer from 1 total number of measurement events - measId")
        return 0

    def checkMeasID(self, ID):
        if not isinstance(ID, int):
            self.TypError("Index of the measurement event to read setup must be an integer from 0 to number of setup data -1")
        if ID < 0: 
            self.ValError("Index of the measurement event to read setup must be an integer from 0 to number of setup data -1")
        return 0

    def checkTime(self, Time):
        if not isinstance(Time, int):
            self.TypError("Time to read the voltage output value must be an integer from 0 to number of setup data -1")
        if Time < 0: 
            self.ValError("Time to read the voltage output value must be an integer from 0 to number of setup data -1")
        
        return 0

    def checkSeqIndex(self, index):
        if not isinstance(index, int):
            self.TypError("Index of the sequence data to read setup must be an integer from 0 to number of setup data -1")
        if index < 0: 
            self.ValError("Index of the sequence data to read setup must be an integer from 0 to number of setup data -1")
        return 0

    def checkSeqLength(self, length):
        if not isinstance(length, int):
            self.TypError("Length of the sequence data to read setup must be an integer from 0 to number of setup data -1")
        if length < 0: 
            self.ValError("Length of the sequence data to read setup must be an integer from 0 to number of setup data -1")
        return 0

    def checkChannel(self, chn):
        if not isinstance(chn, int):
            self.TypError("The Channel Number must be an Integer of the type s01 for channel 1 or s02 for channel 2 where s is the slot number from 1 to 10. (%s)" %(chn))
        if not (len(str(chn)) == 3 or len(str(chn)) == 4):
            self.TypError("The Channel Number must be an Integer of the type s01 for channel 1 or s02 for channel 2 where s is the slot number from 1 to 10. (%s)" %(chn))
        if len(str(chn)) == 4:
            if not (int(str(chn)[3]) == 1 or int(str(chn)[2]) == 2 or int(str(chn)[3]) == 0):
                self.TypError("The Channel Number must be an Integer of the type s01 for channel 1 or s02 for channel 2 where s is the slot number from 1 to 10. (%s)" %(chn))
            if int(str(chn)[0:1]) > 10 or int(str(chn)[3]) < 1: 
                self.TypError("The Channel Number must be an Integer of the type s01 for channel 1 or s02 for channel 2 where s is the slot number from 1 to 10. (%s)" %(chn))
        elif len(str(chn)) == 3:
            if not (int(str(chn)[-1]) == 1 or int(str(chn)[-1]) == 2 or int(str(chn)[-2]) == 0):
                self.TypError("The Channel Number must be an Integer of the type s01 for channel 1 or s02 for channel 2 where s is the slot number from 1 to 10. (%s)" %(chn))
            if int(str(chn)[0]) > 10 or int(str(chn)[2]) < 1: 
                self.TypError("The Channel Number must be an Integer of the type s01 for channel 1 or s02 for channel 2 where s is the slot number from 1 to 10. (%s)" %(chn))
        else:
            self.TypError("The Channel Number must be an Integer of the type s01 for channel 1 or s02 for channel 2 where s is the slot number from 1 to 10. (%s)" %(chn))
        return 0

    def setMeasureVoltageRange(self, chn, Range):
        self.checkChannel(chn)
        if not isinstance(Range, int):
            self.ValError("The voltage measurement range must be 5001 or 5002.")
        if not Range in [5001,5002]:
            self.ValError("The voltage measurement range must be 5001 or 5002.")
        chnID = self.__getChnIndex(chn)
        self.__VMeasureRange[chnID] = Range
        if self.__online and (self.__OperationMode[chnID] in [2000, 2001, 2002]):
            self.__write("WGFMU_setMeasureVoltageRange(%s,%s)"%(chn, Range))
            self.checkError(self.__inst.WGFMU_setMeasureVoltageRange(chn, Range))
        return 0

    def setMeasureCurrentRange(self, chn, Range):
        self.checkChannel(chn)
        if not isinstance(Range, int):
            self.ValError("The current measurement range must be 6001 or 5005.")
        if not Range in [6001,6002,6003,6004,6005]:
            self.ValError("The current measurement range must be 6001 or 5005.")
        chnID = self.__getChnIndex(chn)
        self.__IMeasureRange[chnID] = Range
        if self.__online and (self.__OperationMode[chnID] in [2000, 2001, 2002]):
            self.__write("WGFMU_setMeasureCurrentRange(%s,%s)"%(chn, Range))
            self.checkError(self.__inst.WGFMU_setMeasureCurrentRange(chn, Range))
        return 0

    def setForceDelay(self, chn, delay):
        self.checkChannel(chn)
        self.checkDevDelay(delay)
        self.__VForceDelay[self.__getChnIndex(chn)] = delay
        cDel = c_double(delay)
        if self.__online and (self.__OperationMode[self.__getChnIndex(chn)] == 2001 or self.__OperationMode[self.__getChnIndex(chn)] == 2002):
            self.__write("WGFMU_setForceDelay(%s,%s)"%(chn, delay))
            self.checkError(self.__inst.WGFMU_setForceDelay(chn, cDel))
        return 0

    def setMeasureDelay(self, chn, delay):
        self.checkChannel(chn)
        self.checkDevDelay(delay)
        cDel = c_double(delay)
        self.__MeasureDelay[self.__getChnIndex(chn)] = delay
        if self.__online and (self.__OperationMode[self.__getChnIndex(chn)] == 2001 or self.__OperationMode[self.__getChnIndex(chn)] == 2002):
            self.__write("WGFMU_setMeasureDelay(%s,%s)"%(chn, delay))
            self.checkError(self.__inst.WGFMU_setMeasureDelay(chn, cDel))
        return 0 

    def setMeasureMode(self, chn, mode):
        self.checkChannel(chn)
        self.checkMeasureMode(mode)
        self.__MeasureMode[self.__getChnIndex(chn)] = mode
        chnID = self.__getChnIndex(chn)
        if self.__online and (self.__OperationMode[chnID] in [2000, 2001, 2002]):
            self.__write("WGFMU_setMeasureMode(%s,%s)"%(chn, mode))
            self.checkError(self.__inst.WGFMU_setMeasureMode(chn, mode))
        return 0

    def setOperationMode(self, chn, Mode):
        self.checkChannel(chn)
        if not isinstance(Mode, int):
            self.ValError("The Mode number must be an Integer between 2000 and 2003. (%s)" %(Mode))
        if not Mode in [2000,2001,2002,2003]:
            self.ValError("The Mode number must be between 2000 and 2003. (%s)" %(Mode))
        self.__OperationMode[self.__getChnIndex(chn)] = Mode
       
        if self.__online:
            self.__write("WGFMU_setOperationMode(%s,%s)"%(chn, Mode))
            self.checkError(self.__inst.WGFMU_setOperationMode(chn, Mode))
        return 0

    def setForceVoltageRange(self,chn, Range):
        self.checkChannel(chn)
        if not isinstance(Range, int):
            self.TypError("The Force Voltage Range number must be an Integer between 3000 and 3004. (Int: %d)" %(Range))
        if Range in [3000,3001,3002,3003,3004]:
            self.__VForceRange[self.__getChnIndex(chn)] = Range
        else:
            self.ValError("The Force Voltage Range number must be between 3000 and 3004. (Int: %d)" %(Range))

        chnID = self.__getChnIndex(chn)
        if Range in [3003, 3004] and (self.__OperationMode[chnID] in [2000, 2002, 2003]):
            self.ValError("The Force Voltage Range number must be between 3000 and 3002 for Operational Mode %d. (Int: %d)" %(self.__OperationMode[chnID], Range))
        
        self.__VForceRange[chnID] = Range
        if self.__online and (self.__OperationMode[chnID] in [2000, 2001, 2002]):
            self.__write("WGFMU_setForceVoltageRange(%s,%s)" %(chn, Range))
            self.checkError(self.__inst.WGFMU_setForceVoltageRange(chn, Range))
        return 0

    def setMeasureEnabled(self,chn, state):
        self.checkChannel(chn)
        if not isinstance(state, int):
            self.TypError("The Measure enabled number must be an Integer between 7000 (Enabled) and 7001 (Disabled).")
        if state in [7000,7001]:
            self.__MeasureEnable[self.__getChnIndex(chn)] = state
        else:
            self.ValError("The Measure enabled number must be an Integer between 7000 (Enabled) and 7001 (Disabled).")
        self.__MeasureEnable[self.__getChnIndex(chn)] = state
        if self.__online and (self.__OperationMode[self.__getChnIndex(chn)] == 2001 or self.__OperationMode[self.__getChnIndex(chn)] == 2002):
            self.__write("WGFMU_setMeasureEnabled(%s,%s)"%(chn, state))
            self.checkError(self.__inst.WGFMU_setMeasureEnabled(chn, state))
        return 0

    def setTriggerOutEvent(self, pattern, TriggerEventName, time, duration):
        self.checkPatternName(pattern)
        self.checkExisPattern(pattern)

        ret = self.getPatternForceValues(pattern, 0)
        maxtime = sum(ret['Time'])

        if not isinstance(TriggerEventName, str):
            self.TypError("The Trigger Event name must be a string with a maximum of 256 letters.")
        if len(TriggerEventName) > 256:
            self.ValError("The Trigger Event name must be a string with a maximum of 256 letters.")

        if not isinstance(time, (int,float)):
            self.TypError("The Trigger output time must be in seconds from 0 to the total time of the pattern.")
        if time < 0 or (time + 1e-7) > maxtime: 
            self.ValError("The Trigger output time must be in seconds from 0 to the total time of the pattern.")

        if not isinstance(duration, (int,float)):
            self.TypError("The Trigger duration must be in seconds from 0 to the total time of the pattern.")
        if duration < 0: 
            self.ValError("The Trigger duration must be in seconds from 0 to the total time of the pattern.")
        if (duration + time) > maxtime: 
            self.ValError("The Trigger start time and duration cannot exceed the total time of the pattern.")

        cPatName = c_char_p(pattern.encode(encoding='utf-8'))
        TriggerEventName = c_char_p(TriggerEventName.encode(encoding='utf-8'))

        if self.__online:
            self.__write("WGFMU_setTriggerOutEvent(%s,%s,%s,%s)"%(pattern, TriggerEventName,time, duration))
            self.checkError(self.__inst.WGFMU_setTriggerOutEvent(cPatName, TriggerEventName, time, duration))
        return 0
    
    def setTriggerOutMode(self,chn, mode, polarity):
        self.checkChannel(chn)
        self.checkTriggerMode(mode)
        self.checkTriggerPolarity(polarity)
        self.__TriggerOutMode[self.__getChnIndex(chn)] = mode
        self.__TriggerOutPol[self.__getChnIndex(chn)] = polarity
        if self.__online and (self.__OperationMode[self.__getChnIndex(chn)] == 2001 or self.__OperationMode[self.__getChnIndex(chn)] == 2002):
            self.__write("WGFMU_setTriggerOutMode(%s,%s,%s)"%(chn, mode,polarity))
            self.checkError(self.__inst.WGFMU_setTriggerOutMode(chn, mode, polarity))
        return 0

    def checkExisPattern(self, pattern):
        contains = False
        for pat in self.UsedPattern:
            if pat == pattern:
                contains = True
                break
        if not contains:
            self.ValError("The given pattern is not defined. Please use a defined pattern only. (Pattern: %s)" %(pattern))


    def checkPatternAvail(self, pattern, pattern1='', pattern2=''):
        contains = False
        for pat in self.UsedPattern:
            if pat == pattern:
                if not pattern1==pattern and not pattern2==pattern:
                    contains = True
                    break
        if contains:
            self.ValError("The given pattern is alrady defined. Please use a non defined pattern. (Pattern: %s)" %(pattern))

    def getPatternMeasureTimes(self, pattern, StartIndex):
        self.checkPatternName(pattern)
        self.checkExisPattern(pattern)

        if not isinstance(StartIndex, int):
            self.TypError("StartIndex must be an integer from 0 to the maximum number of scalars - 1 of the given pattern")

        length = self.__getPatternMeasureTimeSize(pattern)
        if StartIndex > length -1: 
            self.ValError("StartIndex must be an integer from 0 to the maximum number of scalars - 1 of the given pattern")

        cLength = c_int(length)
        cPatName = c_char_p(pattern.encode(encoding='utf-8'))
        cTime = (c_double*length)()

        self.__write("WGFMU_getPatternMeasureTimes(%s,%s,%s,%s)"%(pattern, StartIndex,byref(cLength), byref(cTime)))
        self.checkError(self.__inst.WGFMU_getPatternMeasureTimes(cPatName, StartIndex, byref(cLength), byref(cTime)))
        return {'Name': pattern, 'Length': cLength.value, 'Time': list(cTime)}

    def __getPatternMeasureTimeSize(self, pattern):
        cSize = c_int()
        cPatName = c_char_p(pattern.encode(encoding='utf-8'))
        self.__write("WGFMU_getPatternMeasureTimeSize(%s,%s)"%(pattern, byref(cSize)))
        self.checkError(self.__inst.WGFMU_getPatternMeasureTimeSize(cPatName, byref(cSize)))
        return cSize.value

    def getPatternForceValues(self, pattern, StartIndex):
        self.checkPatternName(pattern)
        self.checkExisPattern(pattern)

        if not isinstance(StartIndex, int):
            self.TypError("StartIndex must be an integer from 0 to the maximum number of scalars - 1 of the given pattern")

        length = self.__getPatternForceValueSize(pattern)
        if StartIndex > length -1: 
            self.ValError("StartIndex must be an integer from 0 to the maximum number of scalars - 1 of the given pattern")

        cLength = c_int(length)
        cPatName = c_char_p(pattern.encode(encoding='utf-8'))
        cTime = (c_double*length)()
        cVoltage = (c_double*length)()

        self.__write("WGFMU_getPatternForceValues(%s,%s,%s,%s,%s)"%(pattern, StartIndex, byref(cLength), byref(cTime), byref(cVoltage)))
        self.checkError(self.__inst.WGFMU_getPatternForceValues(cPatName, StartIndex, byref(cLength), byref(cTime), byref(cVoltage)))
        return {'Name': pattern, 'Length': cLength.value, 'Time': list(cTime), 'Voltage': list(cVoltage)}

    def __getPatternForceValueSize(self, pattern):
        cSize = c_int()
        cPatName = c_char_p(pattern.encode(encoding='utf-8'))
        self.__write("WGFMU_getPatternForceValueSize(%s,%s)"%(pattern, byref(cSize)))
        self.checkError(self.__inst.WGFMU_getPatternForceValueSize(cPatName, byref(cSize)))
        return cSize.value

    def getMeasureEventAttribute(self, chn, measID):
        self.checkChannel(chn)
        self.checkMeasID(measID)

        cTime = (c_double)()
        cPoints = (c_int)()
        cInterval = (c_double)()
        cAverage = (c_double)()
        cRdata = (c_int)()

        self.__write("WGFMU_getMeasureEventAttribute(%s,%s,%s,%s,%s,%s,%s)" %(chn, measID, byref(cTime), byref(cPoints), byref(cInterval), byref(cAverage), byref(cRdata)))
        self.checkError(self.__inst.WGFMU_getMeasureEventAttribute(chn, measID, byref(cTime), byref(cPoints), byref(cInterval), byref(cAverage), byref(cRdata)))
        return {'Time': cTime.value , 'Points': cPoints.value , 'Interval': cInterval.value, 'Average': cInterval.value, 'rData': cRdata.value}


    def getMeasureTimes(self):

        ti = []
        for chn in self.__ChnIDs:
            self.checkChannel(chn)
            length = self.getMeasureTimeSize(chn)['Size']        
            cLength = c_int(length)
            cTime = (c_double*length)()
            self.__write("WGFMU_getMeasureTimes(%s,%s, %s, %s)"%(int(chn), int(0), byref(cLength), byref(cTime)))
            self.checkError(self.__inst.WGFMU_getMeasureTimes(int(chn), int(0), byref(cLength), byref(cTime)))
            ti.append({'Times': [ct.value for ct in list(cTime)]})
        return ti
    
    
    def getMeasureTimeSize(self, chn):
        self.checkChannel(chn)
        cSize = (c_int*1)() 
        self.__write("WGFMU_getMeasureTimeSize(%s,%s)"%(int(chn), byref(cSize)))
        self.checkError(self.__inst.WGFMU_getMeasureTimeSize(int(chn), byref(cSize)))
        return {'Size': list(cSize)[0].value}


        
    def executeMeasurement(self, GetData=True, Connect=True, Disconnect=True):
        
        noError = True
        for n in range(2):

            ### open Session
            self.turnOnline(synchronize=True)
            
            n = 0
            if Connect:
                for chn in self.__ChnIDs:
                    if self.__usedChannel:
                        self.connect(chn)
                        self.__connected[n] = True
                    n+=1

                try:
                    self.checkError(self.execute())
                except SystemError as e:
                    noError = False
                    self.__write("SystemError, repeat execution.")
                    self.ErrQueue.put("WGFMU: SystemError in execution - repeat (%s)." %(e))


            ### turn WGFMU offline after measurement concluded
            ret = []
            chns = self.__ChnIDs
            if GetData:
                for n in range(len(chns)):
                    if self.__MeasureEnable[n] == self.WGFMU_MEASURE_ENABLED_ENABLE:
                        if self.__MeasureMode[n] == self.WGFMU_MEASURE_MODE_CURRENT:
                            Name = "I%s" %(self.__CurrentOutputSuffix[n])
                        else:
                            Name = "V%s" %(self.__VoltageOutputSuffix[n])
                        self.__Name[n] = Name
                        tname = "t%s" %(self.__TimeOutputSuffix[n])
                        dataOutput = self.getMeasureValues(chns[n])
                        length = dataOutput['Length']
                        tdata = dataOutput['Time']
                        IVdata = dataOutput['MeasValue']

                        print(n, length)
                        ret.append({'Name': tname, 'Channel': chns[n], 'Length': length, 'Data': tdata})
                        ret.append({'Name': Name, 'Channel': chns[n], 'Length': length, 'Data': IVdata})
            

            self.turnOffline()

            if noError:
                break
            else:
                waitTime = 30
                self.StatusQueue.put("WGFMU: Buffer cleared, Measurement repeated.")
                self.StatusQueue.put("WGFMU: Wait %ss for retry." %(waitTime))
                for n in range(waitTime):
                    tm.sleep(1)
                    self.StatusQueue.put("WGFMU: %ss left." %(waitTime-n))
                
                
        self.StatusQueue.put("WGFMU: Measurement finished")
        return ret


    def checkError(self, ret):
        readEr = False
        try:
            if not int(ret) == self.WGFMU_NO_ERROR:
                readEr=True
        except ValueError as e:
            self.ErrQueue.put("B1530A: %s" %(e))
            readEr=True
        if readEr:
            self.getErrorText(ret)
        return ret

    def checkErrorCritical(self, definition, *args):
        lastTime = tm.time()
        #print(self.getStatus())
        n = 0
        while n < self.STB_REP:

            func = getattr(self.__inst,definition)
            ret = func(*args)

            try:
                errNum = int(ret)
            except ValueError as e:
                self.ErrQueue.put("B1530A: %s" %(e))
                self.SysError("B1530A: %s" %(e))
            
            if errNum == 0:
                return errNum

            if errNum != -5 and errNum != -6:

                self.getErrorText(ret)
                self.__write("WGFMU: Error in %s: %s" %(definition, ret))

            if lastTime + self.STB_REP_TIME < tm.time():
                lastTime = tm.time()
                n = 0
                
            n = n+1
        self.getErrorText(ret)

    def getErrorText(self, ret):
        self.__write(self.getStatusFromCode(ret))
        ErSize = (c_int*1)()
        self.__write("WGFMU_getErrorSize(%s)"%(byref(ErSize)))
        self.__inst.WGFMU_getErrorSize(byref(ErSize))
        msg = create_string_buffer(512)
        length = list(ErSize)[0]
        cLength = c_int(length)
        self.__write("WGFMU_getError(%s,%s)"%(byref(msg), length))
        self.__inst.WGFMU_getError(byref(msg), byref(cLength))

        #Repeat execution for communication, context, Firmware, Unidentified error
        if ret == -5 or ret == -6 or ret == -3 or ret == -8:
            self.SysError("%s" %(msg.value))
        else:
            self.ValError("%s" %(msg.value))

    def checkInterval(self, interval):
        if not isinstance(interval, (float,int)):
            self.TypError("The measurement Interval must be of type float from 10ns to 1.34217728s with a 10ns resolution (Float: %s)" %(interval))
        if not (round(interval/float(1e-8),5)).is_integer():
            self.ValError("The measurement Interval must be of type float from 10ns to 1.34217728s with a 10ns resolution (Float: %f)" %(interval))
        if interval > 1.34217728 or interval < 1e-8: 
            self.ValError("The measurement Interval must be of type float from 10ns to 1.34217728s with a 10ns resolution (Float: %f)" %(interval))

    def checkAverage(self, interval, average):
        if not isinstance(average, (float,int)):
            self.TypError("The measurement Average must be of type float from 10ns to 0.020971512. with a 10ns resolution (Avg: %s)" %(average))
        if not average == 0: 
            if not (round(average/float(1e-8),5)).is_integer():
                self.ValError("The measurement Average must be of type float from 10ns to 0.020971512. with a 10ns resolution (Avg: %f)" %(average))
            if average > 0.020971512 or average < 1e-8: 
                self.ValError("The measurement Average must be of type float from 10ns to 0.020971512. with a 10ns resolution (Avg: %f)" %(average))
            if average > interval:
                self.ValError("THe measurement Average must be equal or smaller than the interval (Int: %f, Avg: %f)" %(interval, average))
        return 0

    def checkStartTime(self, stime, t_total):
        if not isinstance(stime, (float,int)):
            self.TypError("The measurement start time must be of type float.")
        if not (round(stime/float(1e-8),5)).is_integer():
            self.ValError("The measurment start time must be in a resolution of 10ns and not exceed the total pattern time. (Given %s)"%(stime))
        if (stime - 10e-9) > t_total:
            self.ValError("The measurment start time must be in a resolution of 10ns and not exceed the total pattern time. (Given %s)"%(stime))

        return 0

    def checkMeasPoints(self, points):
        if not isinstance(points, (int)):
            self.TypError("The measurement points must be an Integer of 1 or bigger. (Given %s)"%(points))
        if points < 1: 
            self.ValError("The measurement points must be an Integer of 1 or bigger. (Given %s)"%(points))
        return 0

    def checkTriggerMode(self, mode):
        if not isinstance(mode, (int)):
            self.TypError("The Trigger mode must be an Integer beteen 8000 and 8004. (Given %s)"%(mode))
        if not mode in [8000,8001,8002,8003,8004]: 
            self.TypError("The Trigger mode must be an Integer beteen 8000 and 8004. (Given %s)"%(mode))
        return 0

    def checkTriggerPolarity(self, polarity):
        if not isinstance(polarity, (int)):
            self.TypError("The Trigger polarity must be an Integer beteen 8100 and 8101. (Given %s)"%(polarity))
        if polarity < 1: 
            self.TypError("The Trigger polarity must be an Integer beteen 8100 and 8101. (Given %s)"%(polarity))
        return 0

    def clearLibrary(self):
        self.__write("WGFMU_clear()")
        self.checkError(self.__inst.WGFMU_clear())
        self.__PatternIteration = 1
        self.UsedPattern = []
        self.__PulseHeader = []

    def treatWarningsAsErrors(self, level=1000):
        if not isinstance(level, int):
            self.TypError("The Error level must be a value between 1000 and 1003. (Given %s)"%(level))
        if not level in [1000,1001,1002,1003]:
            self.ValError("The Error level must be a value between 1000 and 1003. (Given %s)"%(level))
        
        self.__write("WGFMU_treatWarningsAsErrors(%s)"%(level))
        self.checkError(self.__inst.WGFMU_treatWarningsAsErrors(level))
        

    #for more than one measurement event use arrays for the measurement values
    #The Pattern name will be assembled in the following way: 
    #Name + _ + PatternIteration + _ + ChannelID
    #i.e. "Pulse_0_201"
    #This function returns three values: 
    #1. PatternName
    #1. TotalTime
    #1. MeasurementPoints
    #chn: Channel number
    #Voltages: Array of output voltages
    #dTimes: Array of incremental time values
    #Mstart: measurement start time (-1 if no measurement should occur)
    #count: number Pattern repetitions
    #Average: Array or value of averaging time
    #Interval: Array or value of measurement interval
    #Points: number of measurement points
    #AddSequence: automatically add the sequence for the created pattern if true
    def CreatePattern(self, name, chn, Voltages, dTimes, Mstart, count=1, Average=None, Interval=None, Points=None, Vinit=0, AddSequence=True):
        
        self.checkCount(count)
        self.checkChannel(chn)
        self.checkVoltage([Vinit], chn)
        t_total = sum(dTimes)
        MPtotal = 0
        if not isinstance(AddSequence,bool):
            self.TypError("AddSequene must be a boolean value, True: automatically add a sequence, False: does not add a sequence.")

        chnID = self.__getChnIndex(chn)

        if not Mstart == -1:
            
            MPtotal = count*Points
            if type([]) == type(Mstart):
                self.checkArrayConsistancy([Mstart, Average, Interval,Points], "Average, Interval and Points for %d must be of the same length." %(chn))
                
                endTime = 0
                for n in range(len(Mstart)):
                    self.checkStartTime(Mstart[n], sum(dTimes))
                    self.checkInterval(Interval[n])
                    self.checkAverage(Interval[n], Average[n])
                    self.checkPoints(Points[n])
                    if endTime < Mstart[n]:
                        self.ValError('The Start time of a measurement event must occur after the end of the previous measurement event')

                    endTime += Interval[n]+Points[n]

                MPtotal = sum(Points)
                if endTime > t_total:
                    self.ValError('The Measurement end time cannot be more then the time of the pattern.')
                
            else:
                self.checkStartTime(Mstart, sum(dTimes))
                self.checkInterval(Interval)
                self.checkAverage(Interval, Average)
                self.checkPoints(Points)
                MPtotal = Points

        self.checkDtime(dTimes)
        self.checkVoltage(Voltages, chn)
        self.checkArrayConsistancy([Voltages, dTimes], "Voltage and dTime arrays for pattern '%s' must have the same length." %(name))
        
        patName = "%s_%d_%d" %(name, self.__PatternIteration, chn)
        self.__PatternIteration += 1
        cPatName = c_char_p(patName.encode(encoding='utf-8'))
        cVinit = c_double(float(Vinit))
        self.checkPatternName(patName)
        self.checkPatternAvail(patName)
        self.UsedPattern.append(patName)

        self.__write("WGFMU_createPattern(%s,%s)" %(patName,Vinit))
        self.checkError(self.__inst.WGFMU_createPattern(cPatName, cVinit))

        for n in range(len(Voltages)):
            cVoltage = c_double(float(Voltages[n]))
            cDTime = c_double(float(dTimes[n]))
            self.__write("WGFMU_addVector(%s,%s,%s)" %(patName,float(dTimes[n]),float(Voltages[n])))
            self.checkError(self.__inst.WGFMU_addVector(cPatName, cDTime, cVoltage))

        if not Mstart == -1:
            
            if self.__MeasureEnable[chnID] == self.WGFMU_MEASURE_ENABLED_DISABLE:
                self.setMeasureEnabled(chn, self.WGFMU_MEASURE_ENABLED_ENABLE)
            
            cRData = c_int()
            cRData.value = self.__rdata
            if type([]) == type(Mstart):
                for n in range(len(Mstart)):
                    
                    EventName = "MeasEvent#%d_%d" %(n, chn)
                    cEventName = c_char_p()
                    cEventName.value = EventName.encode(encoding='utf-8')
                    cStime = c_double(Mstart[n])
                    cInterval = c_double(Interval[n])
                    cAverage = c_double(Average[n])
                    cPoints = c_double(Points[n])
                    self.__write("WGFMU_setMeasureEvent(%s,%s,%s,%s,%s,%s,%s)" %(patName,EventName,Mstart[n],cPoints.value, Interval[n],Average[n],self.__rdata))
                    self.checkError(self.__inst.WGFMU_setMeasureEvent(cPatName, cEventName, cStime, cPoints.value, cInterval, cAverage, self.__rdata))
                    ret = count*sum(Points)
            else:
                EventName = "MeasEvent_%d" %(chn)
                cEventName = c_char_p()
                cEventName.value = EventName.encode(encoding='utf-8')
                cStime = (c_double)(Mstart)
                cStime.value = Mstart
                cInterval = (c_double)(Interval)
                cInterval.value = Interval
                cAverage = (c_double)(Average)
                cAverage.value = Average
                cPoints = (c_int)(Points)
                self.__write("WGFMU_setMeasureEvent(%s,%s,%s,%s,%s,%s,%s)" %(patName,EventName,Mstart,Points, Interval,Average,self.__rdata))
                self.checkError(self.__inst.WGFMU_setMeasureEvent(cPatName, cEventName, cStime, cPoints, cInterval, cAverage, self.__rdata))
                    
        if AddSequence and count > 0:
            self.checkCount(count)
            cCount = c_double(count)
            cCount.value = count
            self.__usedChannel[self.__getChnIndex(chn)] = True
            self.__write("WGFMU_addSequence(%s,%s,%s)" %(chn,patName,count))
            self.checkError(self.__inst.WGFMU_addSequence(chn, cPatName, cCount))
            

        return {'PatternName': patName, 'TotalTime': t_total, 'MeasurementPoints': MPtotal}

    def addSequence(self, chn, name, count):
        
        self.checkChannel(chn)
        self.checkCount(count)
        self.checkPatternName(name)

        cCount = c_double(count)
        cCount.value = count

        self.checkPatternName(name)

        cPatName = c_char_p(name.encode(encoding='utf-8'))

        self.__usedChannel[self.__getChnIndex(chn)] = True
        self.__write("WGFMU_addSequence(%s,%s,%s)" %(chn,name,count))
        self.checkError(self.__inst.WGFMU_addSequence(chn, cPatName, cCount))

    def checkCount(self, count):
        if not isinstance(count, int):
            self.TypError("The sequence count must be an integer equal or larger than 1.")
        if count < 1:
            self.ValError("The sequence count must be an integer equal or larger than 1.")
        return 0
            
    def checkDevDelay(self, delay):
        if not isinstance(delay,(float,int)):
            self.TypError("The device delay must be a float values between -50ns to 50ns in 625ps resolution.")
        if delay > 50e-9 or delay < -50e-9:
            self.ValError("The device delay must be a float values between -50ns to 50ns in 625ps resolution.")
        if not (round(delay/float(625e-12),5)).is_integer():
            self.ValError("The device delay must be a float values between -50ns to 50ns in 625ps resolution.")
        return 0

    def checkMeasureMode(self, mode):
        if not isinstance(mode,int):
            self.TypError("The Measure mode must be an integer values of 4000 (voltage mode) or 4001 (current mode).")
        if not mode in [4000,4001]:
            self.TypError("The Measure mode must be an integer values of 4000 (voltage mode) or 4001 (current mode).")
        return 0

    def checkDtime(self, dtimes):
        if not isinstance(dtimes, type([])):
            self.TypError("The force voltage pattern delta times must be a list of float values between 10ns and 10995.11627775s.")
        for dtime in dtimes:
            if not isinstance(dtime,(float,int)):
                self.TypError("The force voltage pattern delta times must be a list of float values between 10ns and 10995.11627775s.")
            if dtime > 10995.11627775 or dtime < 1e-8:
                self.ValError("The force voltage pattern delta times must be a list of float values between 10ns and 10995.11627775s.")
            if not (round(dtime/float(1e-8),5)).is_integer():
                self.ValError("The force voltage pattern delta times must be a list of float values between 10ns and 10995.11627775s.")
        return 0
        

    def checkArrayConsistancy(self, Arr, message):
        l = len(Arr)
        for n in range(1,l,1):
            if not len(Arr[n]) == len(Arr[0]):
                self.ValError(message)

    def checkVoltage(self, voltages, chn):
        if not isinstance(voltages, type([])):
            self.TypError("The force voltages must be a list of float values between -10 and 10V (Maximum).")
        for voltage in voltages:
            if not isinstance(voltage, (int,float)):
                self.TypError("The force voltages must be a list of float (int) values between -10 and 10V (Maximum).")
            VFRange = self.__VForceRange[self.__getChnIndex(chn)]
            OPMode = self.__OperationMode[self.__getChnIndex(chn)]
            if OPMode == 2000:
                self.SysError("The channel is in DC mode.")
            elif OPMode == 2002:
                if VFRange == 3001:
                    if abs(voltage) > 3:
                        self.ValError("Channel 1 Voltage range is limited to +-3V.")
                else:
                    if abs(voltage) > 5:
                        self.ValError("Channel 1 Voltage range is limited to +-5V.")
                    
            elif OPMode == 2001:
                if VFRange == 3001:
                    if abs(voltage) > 3:
                        self.ValError("Channel 1 Voltage range is limited to +-3V. (Applied: %sV)" %voltage)
                elif VFRange == 3002:
                    if abs(voltage) > 5:
                        self.ValError("Channel 1 Voltage range is limited to +-5V. (Applied: %sV)" %voltage)
                elif VFRange == 3003:
                    if voltage < -10 or voltage > 0:
                        self.ValError("Channel 1 Voltage range is limited to -10V. (Applied: %sV)" %voltage)
                elif VFRange == 3004:
                    if voltage > 10 or voltage < 0:
                        self.ValError("Channel 1 Voltage range is limited to +10V. (Applied: %sV)" %voltage)
            elif OPMode == 2003:
                self.SysError("This Channel is in SMU mode.")

    def __write(self, command):
        None
        if self.printOutput:
            print(command)

        if self.log:
            currentDT = str(dt.datetime.now())
            self.__LogFile.write("%s - %s\n" %(currentDT, command))

    def SysError(self, error):
        self.__write(error)
        raise B1530A_InputError("B1530A - %s: %s" %(self.__GPIB, error))

    def ValError(self, error):
        self.__write(error)
        raise B1530A_InputError("%s: %s" %(self.__GPIB, error))
    
    def TypError(self, error):
        self.__write(error)
        raise B1530A_InputError("B1530A - %s: %s" %(self.__GPIB, error))

    def __openSession(self):
        gpib = create_string_buffer(512)
        gpib.value = self.__GPIB.encode('utf-8')
        try:
            self.__write("WGFMU_openSession(%s)" %(gpib))
            ret = self.checkError(self.__inst.WGFMU_openSession(gpib))
        except SystemError as e:
            if str(e).find("A session has already been opened") != -1:
                return 0
            self.SysError(e)

        return ret


        ret = 0
        err = None
        '''
        for n in range(10):
            try:
                self.__write("WGFMU_openSession(%s)" %(gpib))
                ret = self.checkError(self.__inst.WGFMU_openSession(gpib))
                return ret
            except SystemError as e:
                self.ErrQueue.put(e)
                err = e
                print("error", e)
                if str(e).find("A session has already been opened") != -1:
                    return 0
        
        raise SystemError(e)
        '''

    def openSession(self):
        gpib = c_char_p()
        gpib.value = self.__GPIB.encode('utf-8')
        ret = 0
        self.__write("WGFMU_openSession()%s" %(gpib))
        ret = self.checkError(self.__inst.WGFMU_openSession(gpib))
        return ret

    def __closeSession(self):
        err = None
        for n in range(10):
            try:
                self.__write("WGFMU_closeSession()")
                ret = self.checkError(self.__inst.WGFMU_closeSession())
                self.__online = False
                return ret
            except SystemError as e:
                self.ErrQueue.put(e)
                err =e
                if str(e).find("No session has been opened") != -1:
                    self.__online = False
                    return 0

        self.SysError(err)
    
    def abort(self):
        if self.__online:
            self.__write("WGFMU_abort()")
            ret = self.checkError(self.__inst.WGFMU_abort())
        else:
            ret = "Abort can only be performed if WGFMU is in online mode."
        return ret

    def abortChannel(self, chn):
        if self.__online:
            self.checkChannel(chn)
            self.__write("WGFMU_abortChanel(%s)" %(chn))
            ret = self.checkError(self.__inst.WGFMU_abortChanel(chn))
        else:
            ret = "Abort can only be performed if WGFMU is in online mode."
        return ret

    def closeLogFile(self):
        self.__write("WGFMU_closeLogFile()")
        ret = self.checkError(self.__inst.WGFMU_closeLogFile())
        return ret

    def connect(self, chn):
        self.checkChannel(chn)
        chnID = self.__getChnIndex(chn)
        ret = None
        if self.__online and (self.__OperationMode[chnID] in [2000,2001,2002]):
            self.checkChannel(chn)
            if self.__connected[chnID] == False:
                self.__write("WGFMU_connect(%s)" %(chn))
                ret = self.checkError(self.__inst.WGFMU_connect(chn))
                self.__connected[chnID] = True
        else: 
            self.__write("Channel connect can only be performed if WGFMU is in online mode when in DC, Fast IV or PG mode.")
        return ret

    def disconnect(self, chn):
        self.checkChannel(chn)
        chnID = self.__getChnIndex(chn)
        ret =None

        if self.__online and (self.__OperationMode[chnID] in [2000,2001,2002]):
            if self.__connected[chnID] == True:
                self.__write("WGFMU_disconnect(%s)" %(chn))
                ret = self.checkError(self.__inst.WGFMU_disconnect(chn))
                self.__connected[chnID] = False
        else: 
            self.__write("Channel disconnect can only be performed if WGFMU is in online mode when in DC, Fast IV or PG mode.")

        return ret
    
    #This function creates a waveform pattern by copying the waveform specified by
    #pattern1 and adding the waveform specified by pattern2
    #be careful using this, Voltages and Times won't be evaluated for accuracy
    def createMergedPattern(self, pattern, pattern1, pattern2, direction):
        
        self.checkPatternName(pattern)
        self.checkPatternAvail(pattern,pattern1,pattern2)
        self.checkPatternName(pattern1)
        self.checkExisPattern(pattern1)
        self.checkPatternName(pattern2)
        self.checkExisPattern(pattern2)
        self.checkDirection(direction)

        cPat = c_char_p()
        cPat.value = pattern.encode(encoding='utf-8')
        cPat1 = c_char_p()
        cPat1.value = pattern1.encode(encoding='utf-8')
        cPat2 = c_char_p()
        cPat2.value = pattern2.encode(encoding='utf-8')

        self.__write("WGFMU_createMergedPattern(%s,%s,%s,%s)" %(pattern, pattern1, pattern2,direction))
        ret = self.checkError(self.__inst.WGFMU_createMergedPattern(cPat, cPat1, cPat2, direction))
        self.UsedPattern.append(pattern)
        return ret

    #This function creates a waveform pattern by copying the waveform specified by
    #pattern1 and multiplying the waveform by the specified factor for each direction;
    #time and voltage
    #be careful using this, Voltages and Times won't be evaluated for accuracy
    def createMultipliedPattern(self, pattern, pattern1, factorT, factorV):
        
        self.checkPatternName(pattern)
        self.checkPatternAvail(pattern,pattern1)
        self.checkPatternName(pattern1)
        self.checkExisPattern(pattern1)
        self.checkFactor(factorT)
        self.checkFactor(factorV)
        
        cPat = c_char_p()
        cPat.value = pattern.encode(encoding='utf-8')
        cPat1 = c_char_p()
        cPat1.value = pattern1.encode(encoding='utf-8')

        cFacT = c_double(factorT)
        cFacV = c_double(factorV)

        self.__write("WGFMU_createMultipliedPattern(%s,%s,%s,%s)" %(pattern, pattern1, factorT,factorV))
        ret = self.checkError(self.__inst.WGFMU_createMultipliedPattern(cPat, cPat1, cFacT, cFacV))
        self.UsedPattern.append(pattern)
        return ret

    #This function creates a waveform pattern by copying the waveform specified by
    #pattern1 and adding the specified offset for each direction; time and voltage. 
    #be careful using this, Voltages and Times won't be evaluated for accuracy
    def createOffsetPattern(self, pattern, pattern1, offsetT, offsetV):
        self.checkPatternName(pattern)
        self.checkPatternAvail(pattern,pattern1)
        self.checkPatternName(pattern1)
        self.checkExisPattern(pattern1)
        self.checkOffset(offsetT)
        self.checkOffset(offsetV)

        cPat = c_char_p()
        cPat.value = pattern.encode(encoding='utf-8')
        cPat1 = c_char_p()
        cPat1.value = pattern1.encode(encoding='utf-8')

        cOffT = c_double(offsetT)
        cOffV = c_double(offsetV)

        self.__write("WGFMU_createOffsetPattern(%s,%s,%s,%s)" %(pattern, pattern1, offsetT,offsetV))
        ret = self.checkError(self.__inst.WGFMU_createOffsetPattern(cPat, cPat1, cOffT, cOffV))
        self.UsedPattern.append(pattern)
        return ret

    def checkFactor(self, factor):
        if not isinstance(factor, (float,int)):
            self.TypError("The factors for multiplying the Pattern must be of type float or int and not 0")
        if not factor == 0: 
            self.TypError("The factors for multiplying the Pattern must be of type float or int and not 0")
        return 0

    def checkOffset(self, offset):
        if not isinstance(offset, (float,int)):
            self.TypError("The factors for multiplying the Pattern must be of type float or int and not 0")
        return 0

    def checkDirection(self, direction):
        if not isinstance(direction, int):
            self.TypError("Merging direction must be an Interger of either 9000 (time direction) or 9001 (voltage direction).")
        if not (direction == 9000 or direction == 9001):
            self.TypError("Merging direction must be an Interger of either 9000 (time direction) or 9001 (voltage direction).")
        return 0

    def checkPatternName(self, pattern):
        if not isinstance(pattern, str):
            self.TypError("Pattern must be of String type with a maximum of 16 characters.")
        if len(pattern) > 16:
            self.ValError("Pattern must be of String type with a maximum of 16 characters.")
        return 0

    def checkPoints(self, points):
        if not isinstance(points, int):
            self.TypError("The number of measurement points must be a positive integer bigger than 1.")
        if points < 1: 
            self.ValError("The number of measurement points must be a positive integer bigger than 1.")

    def forceDCVoltage(self,chn, Voltage):
        if self.__online:
            self.checkChannel(chn)
            self.checkDCVoltage(chn, Voltage)
            cVol = c_double(Voltage)
            ret = self.checkError(self.__inst.WGFMU_dcforceVoltage(chn, cVol))
            self.__write("WGFMU_dcforceVoltage(%s,%s)" %(chn, Voltage))
        else:
            ret = "Force DC Voltage can only be performed in online mode."
        return ret

    #This function starts a sampling measurement immediately by using the specified
    #channel and returns the averaged measurement voltage or current. The measurement
    #mode is set by the WGFMU_setMeasureMode function.
    #sampling interval = interval x 5 ns
    def DCMeasureAverageValue(self, chn, points, interval):
        if self.__online:
            self.checkChannel(chn)
            self.checkPoints(points)
            self.checkDCInterval(interval)
            val = c_double()
            self.__write("WGFMU_dcmeasureAveragedValue(%s,%s,%s,%s)" %(chn, points, interval, byref(val)))
            ret = self.checkError(self.__inst.WGFMU_dcmeasureAveragedValue(chn, points, interval, byref(val)))
        else:
            ret = "DC Measurement can only be performed in online mode."
        return ret

    def performDCMeasurement(self, channels, voltages, points, interval):
        if not isinstance(channels, type([])):
            self.TypError("Channels must be a list of integers representing valid channel numbers.")
        self.checkArrayConsistancy([channels,voltages], "Channels and voltages must have the same dimension.")
        for chn, volt in zip(channels,voltages):
            self.checkVoltage(voltages,chn)
            self.checkChannel(chn)
            self.connect(chn)
        ret = []
        for chn, volt  in zip(channels,voltages):
            self.forceDCVoltage(chn, volt)
        if (points == 1):
            for chn in channels:
                ret.append(self.DCMeasureValue(chn))
        else: 
            self.checkInterval(interval)
            self.checkInterval(interval)
            ret.append(self.DCMeasureAverageValue(chn, points, interval))

        for chn in channels:
            self.disconnect(chn)

        return ret
            

    #This function starts a voltage or current measurement immediately by using the
    #specified channel and returns the measurement value.
    def DCMeasureValue(self, chn):
        if self.__online:
            self.checkChannel(chn)
            val = c_double()
            self.__write("WGFMU_dcmeasureValue(%s,%s)" %(chn, byref(val)))
            ret = self.checkError(self.__inst.WGFMU_dcmeasureValue(chn, byref(val)))
        else:
            self.SysError("DC Measurement can only be performed in online mode.")
        return ret
        
    def checkDCInterval(self, interval):
        if not isinstance(interval, int):
            self.TypError("DC: The interval must be an integer between 1 and 65535.")
        if interval < 1 or interval > 65535: 
            self.TypError("DC: The interval must be an integer between 1 and 65535.")
        cPoi = c_int()
        cPoi.value = interval
        return cPoi

    def checkDCPoints(self, points):
        if not isinstance(points, int):
            self.TypError("DC: Number of sampling points must be an integer between 1 and 65535.")
        if points < 1 or points > 65535: 
            self.TypError("DC: Number of sampling points must be an integer between 1 and 65535.")
        cPoi = c_int()
        cPoi.value = points
        return cPoi
            
    def checkDCVoltage(self, chn, voltage):
        if not isinstance(voltage, (int,float)):
            self.TypError("The force voltage must be of type float (int) and between -10 and 10V (Maximum).")
        
        VFRange = self.__VForceRange[self.__getChnIndex(chn)]
        OPMode = self.__OperationMode[self.__getChnIndex(chn)]

        if OPMode == 2000:
            if VFRange == 3001:
                if abs(voltage) > 3:
                    self.ValError("Channel 1 Voltage range is limited to +-3V.")
            elif VFRange == 3002:
                if abs(voltage) > 5:
                    self.ValError("Channel 1 Voltage range is limited to +-5V.")
            elif VFRange == 3003:
                if voltage > 10 or voltage < 0:
                    self.ValError("Channel 1 Voltage range is limited to +10V.")
            elif VFRange == 3004:
                if voltage < 10 or voltage > 0:
                    self.ValError("Channel 1 Voltage range is limited to -10V.")
        elif OPMode == 2001:
            self.SysError("Channel 1 is in FAST-IV mode")
        elif OPMode == 2002:
            self.SysError("Channel 1 is in PG mode")
        elif OPMode == 2003:
            self.SysError("This Channel is in SMU mode.")
        return 0


    def getStatusFromCode(self, code):
        dictionary = {}
        dictionary.update({10000: 'All sequences are completed and all data is ready to read'})
        dictionary.update({10001: 'All sequences are just completed'})
        dictionary.update({10002: 'Sequencer is running'})
        dictionary.update({10003: 'Sequencer is aborted and all data is ready to read.'})
        dictionary.update({10004: 'Sequencer is just aborted'})
        dictionary.update({10005: 'Illegal state'})
        dictionary.update({10006: 'Idle state'})
        dictionary.update({0: 'Self-test passed or self-calibration passed'})
        dictionary.update({1: 'Self-test failed or self-calibration failed'})
        dictionary.update({-1: 'Invalid parameter value was found. It will be out of the range. Set the effective parameter value.'})
        dictionary.update({-2: 'Invalid string value was found. It will be empty or illegal (pointer). Set the effective string value.'})
        dictionary.update({-3: 'Context error was found between relative functions. Set the effective parameter value.'})
        dictionary.update({-4: 'Specified function is not supported by this channel. Set the channel id properly.'})
        dictionary.update({-5: 'IO library error was found.'})
        dictionary.update({-6: 'Firmware error was found.'})
        dictionary.update({-7: 'WGFMU instrument library error was found.'})
        dictionary.update({-8: 'Unidentified error was found.'})
        dictionary.update({-9: 'Specified channel id is not available for WGFMU. Set the channel id properly.'})
        dictionary.update({-10: 'Unexpected pattern name was specified. Specify the effective pattern name. Or create a new pattern.'})
        dictionary.update({-11: 'Unexpected event name was specified. Specify the effective event name.'})
        dictionary.update({-12: 'Duplicate pattern name was specified. Specify the unique pattern name.'})
        dictionary.update({-13: 'Sequencer must be run to execute the specified function. Run the sequencer.'})
        dictionary.update({-14: 'Measurement is in progress. Read the result data after the measurement is completed.'})
        dictionary.update({-15: 'Measurement result data was deleted by the setup change. The result data must be read before changing the waveform setup or the measurement setup.'})
        dictionary.update({1000: 'No warning is reported. Default setting for WGFMU_treatWarningsAsErrors.'})
        dictionary.update({1001: 'WGFMU warning level as severe'})
        dictionary.update({1002: 'WGFMU warning level as normal'})
        dictionary.update({1003: 'WGFMU warning level as information'})
        dictionary.update({2000: 'Operation Mode: DC mode. DC voltage output and voltage or current measurement (VFVM or VFIM).'})
        dictionary.update({2001: 'Operation Mode: Fast IV mode. ALWG voltage output and voltage or current measurement (VFVM or VFIM).'})
        dictionary.update({2002: 'Operation Mode: PG mode. ALWG voltage output and voltage measurement (VFVM). The output voltage will be divided by the internal 50 ohm resistor and the load impedance. Faster than the Fast IV mode.'})
        dictionary.update({2003: 'Operation Mode: SMU mode, default setting.'})
        dictionary.update({3000: 'Force Voltage Range: Auto range, default setting'})
        dictionary.update({3001: 'Force Voltage Range: 3 V fixed range'})
        dictionary.update({3002: 'Force Voltage Range: 5 V fixed range'})
        dictionary.update({3003: 'Force Voltage Range: -10 V fixed range'})
        dictionary.update({3004: 'Force Voltage Range: +10 V fixed range'})
        dictionary.update({4000: 'Measure Mode: Voltage measurement mode, default setting'})
        dictionary.update({4001: 'Measure Mode: Current measurement mode'})
        dictionary.update({5001: 'Measure Voltage Range: 5V fixed range'})
        dictionary.update({5002: 'Measure Voltage Range: 10V fixed range'})
        dictionary.update({6001: 'Measure Current Range: 1 uA controlled range'})
        dictionary.update({6002: 'Measure Current Range: 10 uA controlled range'})
        dictionary.update({6003: 'Measure Current Range: 100 uA controlled range'})
        dictionary.update({6004: 'Measure Current Range: 1 mA controlled range'})
        dictionary.update({6005: 'Measure Current Range: 10 mA controlled range'})
        dictionary.update({7000: 'Measurement cannot be performed.'})
        dictionary.update({7001: 'Measurement can be performed. Default setting.'})
        dictionary.update({8000: 'Trigger Mode: No trigger output, default setting'})
        dictionary.update({8001: 'Trigger Mode: Execution trigger output mode Channel outputs trigger only when starting the first sequence output.'})
        dictionary.update({8002: 'Trigger Mode: Sequence trigger output mode Channel outputs trigger every start of the sequence output.'})
        dictionary.update({8003: 'Trigger Mode: Pattern trigger output mode Channel outputs trigger every start of the pattern output.'})
        dictionary.update({8004: 'Trigger Mode: Event trigger output mode which enables the trigger output event. Channel outputs trigger at the timing set by WGFMU_setTriggerOutEvent.'})  
        dictionary.update({8100: 'Trigger Polarity: positive, default setting'})
        dictionary.update({8101: 'Trigger Polarity: negative'})
        dictionary.update({9000: 'Merge Pattern: Time direction'})
        dictionary.update({9001: 'Merge Pattern: Voltage direction'})
        dictionary.update({11000: 'Measure Event: Not completed'})
        dictionary.update({11001: 'Measure Event: Completed. Ready to read result.'})
        dictionary.update({12000: 'Measure Event Data: Averaging data output mode'})
        dictionary.update({12001: 'Measure Event Data: Raw data output mode'})
        try:
            dic = dictionary[code]
        except KeyError:
            dic = "Code not in Dictionary - %s" %(code)
        return dic

    def __getShortStatusFromCode(self, code):
        dictionary = {}
        dictionary.update({1000: 'No warning'})
        dictionary.update({1001: 'severe'})
        dictionary.update({1002: 'normal'})
        dictionary.update({1003: 'as information'})
        dictionary.update({2000: 'DC mode'})
        dictionary.update({2001: 'Fast IV'})
        dictionary.update({2002: 'PG'})
        dictionary.update({2003: 'SMU mode, default setting.'})
        dictionary.update({3000: 'Auto'})
        dictionary.update({3001: '3 V fixed'})
        dictionary.update({3002: '5 V fixed'})
        dictionary.update({3003: '-10 V fixed'})
        dictionary.update({3004: '+10 V fixed'})
        dictionary.update({4000: 'Voltage'})
        dictionary.update({4001: 'Current'})
        dictionary.update({5001: '5V fixed range'})
        dictionary.update({5002: '10V fixed range'})
        dictionary.update({6001: '1 uA controlled'})
        dictionary.update({6002: '10 uA controlled'})
        dictionary.update({6003: '100 uA controlled'})
        dictionary.update({6004: '1 mA controlled'})
        dictionary.update({6005: '10 mA controlled'})
        dictionary.update({8000: 'No trigger'})
        dictionary.update({8001: 'first Seq.'})
        dictionary.update({8002: 'every Seq.'})
        dictionary.update({8003: 'first Pat.'})
        dictionary.update({8004: 'at Tri. Out.'})  
        dictionary.update({8100: 'pos.'})
        dictionary.update({8101: 'neg.'})
        dictionary.update({12000: 'Averaging'})
        dictionary.update({12001: 'Raw'})
        
        return dictionary[code]

    #programs a Pulse into the offline library, a measurement is optional, the measurement channel parameters are set globally. 
    #Measurement events in this pattern can be set in a list or as a single measurement event. 
    #   if set in a list, mStartTime, mPoints and mInterval must have the same length.
    #   if measure Start and End time arent used, the values will be set to the Start and end time of the pattern
    #chn:           Channel Number
    #twidth:        Pulse width (s)
    #trise:         Pulse rise time (s)
    #tfall:         Pulse fall time (s)
    #tbase:         Pulse base time (s), will be split between before and after
    #Vp:            Pulse voltage (V) 
    #Vb:            Base voltage (V)
    #count:         Number of repetitions (this)
    #measure:       Enable measurement (True), Disable measurement (False)
    #mPoints:       number of Points during pulse
    #mStartTime:    measurement Start time (s)
    #mEndTime:      measurement End time (s)
    #AddSequence:   Automatically adds a sequence (necessary to automatically execute count 2+)
    #Name:          subname for pattern "Name_x_chn", x is iterative number, chn is channel number
    #WriteHeader:   write the pulse information into the header (automatically true) 
    def programRectangularPulse(self, chn, twidth, trise, tfall, tbase, Vp, Vb, count=1, measure=True, mPoints=1, mStartTime=None, mEndTime=None, AddSequence=True, Name=None, WriteHeader=True):
        
        if not isinstance(WriteHeader,bool):
            self.TypError("WriteHeader must be of type boolean, True/False: Write/Don't write a header to the output file.")

        if Name == None:
            Name = 'Pulse'

        Voltages = [Vb,Vp,Vp,Vb,Vb]
        dTimes = [tbase/2,trise,twidth,tfall,tbase/2]
        
        t_total = sum(dTimes)
        if measure:
            if mStartTime==None:
                mStartTime = 0
            if mEndTime==None:
                mEndTime=t_total

            if isinstance(mPoints, type([])):
                self.checkArrayConsistancy([mStartTime, mEndTime, mPoints], "Measurement stat/end time and mPoints must have the same dimension")
                Interval = []
                Average = []
                for n in range(len(mStartTime)):
                    if mEndTime[n] < mStartTime[n]:
                        self.ValError("Measurement End Time must be larger than measurement Start Time")
                    self.checkPoints(mPoints[n])
                    Mstart = mStartTime
                    Interval.append(float(round((mEndTime[n]-mStartTime[n])/mPoints[n]*1e8))*1e-8)
                    Average.append(Interval[n]*self.Averaging)

            else:
                if mEndTime < mStartTime:
                    self.ValError("Measurement End Time must be larger than measurement Start Time")
                self.checkPoints(mPoints)
                Mstart = mStartTime
                Interval = float(round((mEndTime-mStartTime)/mPoints*1e8))*1e-8
                Average = Interval*self.Averaging

            self.CreatePattern(Name, chn, Voltages, dTimes, Mstart, count, Average, Interval, mPoints, Vinit=Vb, AddSequence=AddSequence)
        else:
            Mstart = -1
            self.CreatePattern(Name, chn,  Voltages, dTimes, Mstart, count, Vinit=Vb, AddSequence=AddSequence)
        
        if WriteHeader:
            header = []
            header.append('Testparameter,Measurement.Tri.%s.Channel,%d' %(Name,chn))
            header.append('Testparameter,Measurement.Tri.%s.Count,%d' %(Name,count))
            header.append('Testparameter,Measurement.Tri.%s.Width.Time,%f' %(Name,trise))
            header.append('Testparameter,Measurement.Tri.%s.Rise.Time,%f' %(Name,trise))
            header.append('Testparameter,Measurement.Tri.%s.Fall.Time,%f' %(Name,tfall))
            header.append('Testparameter,Measurement.Tri.%s.Base.Time,%f' %(Name,tbase))
            header.append('Testparameter,Measurement.Tri.%s.Rise.Time,%f' %(Name,trise))
            header.append('Testparameter,Measurement.Tri.%s.Pulse.Voltage,%f' %(Name,Vp))
            header.append('Testparameter,Measurement.Tri.%s.Base.Voltage,%f' %(Name,Vb))
            if Mstart == -1:
                header.append('Testparameter,Measurement.Tri.%s.Measuarement,%s' %(Name,'No Measurement'))
            else:
                header.append('Testparameter,Measurement.Tri.%s.Start.Time,%f' %(Name,Mstart))
                header.append('Testparameter,Measurement.Tri.%s.Interval,%f' %(Name,Interval))
                header.append('Testparameter,Measurement.Tri.%s.Average,%f' %(Name,Average))
                header.append('Testparameter,Measurement.Tri.%s.Points,%d' %(Name,mPoints))
            
            if self.__WritePulseHeader:
                self.__PulseHeader.append(header)

    #programs a triangular Pulse into the offline library, a measurement is optional, the measurement channel parameters are set globally. 
    #Measurement events in this pattern can be set in a list or as a single measurement event. 
    #   if set in a list, mStartTime, mPoints and mInterval must have the same length.
    #   if measure Start and End time arent used, the values will be set to the Start and end time of the pattern
    #chn:           Channel Number
    #trise:         Pulse rise time (s)
    #tfall:         Pulse fall time (s)
    #tbase:         Pulse base time (s), will be split between before and after
    #Vp:            Pulse voltage (V) 
    #Vb:            Base voltage (V)
    #count:         Number of repetitions (this)
    #measure:       Enable measurement (True), Disable measurement (False)
    #mPoints:       number of Points during pulse
    #mStartTime:    measurement Start time (s)
    #mEndTime:      measurement End time (s)
    #AddSequence:   Automatically adds a sequence (necessary to automatically execute count 2+)
    #Name:          subname for pattern "Name_x_chn", x is iterative number, chn is channel number
    #WriteHeader:   write the pulse information into the header (automatically true) 
    def programTriangularPulse(self, chn, trise, tfall, tbase, Vp, Vb, count=1, measure=True, mPoints=1, mStartTime=None, mEndTime=None, AddSequence=True, Name=None, WriteHeader=True):
        
        if not isinstance(WriteHeader,bool):
            self.TypError("WriteHeader must be of type boolean, True/False: Write/Don't write a header to the output file.")

        if Name == None:
            Name = 'Pulse'

        Voltages = [Vb,Vp,Vb,Vb]
        dTimes = [tbase/2,trise,tfall,tbase/2]
        t_total = sum(dTimes)
        
        if measure:
            if mStartTime==None:
                mStartTime = 0
            if mEndTime==None:
                mEndTime=t_total

            if isinstance(mPoints, type([])):
                self.checkArrayConsistancy([mStartTime, mEndTime, mPoints], "Measurement stat/end time and mPoints must have the same dimension")
                Interval = []
                Average = []
                for n in range(len(mStartTime)):
                    if mEndTime[n] < mStartTime[n]:
                        self.ValError("Measurement End Time must be larger than measurement Start Time")
                    self.checkPoints(mPoints[n])
                    Mstart = mStartTime
                    Interval.append(float(round((mEndTime[n]-mStartTime[n])/mPoints[n]*1e8))*1e-8)
                    Average.append(Interval[n]*self.Averaging)

            else:
                if mEndTime < mStartTime:
                    self.ValError("Measurement End Time must be larger than measurement Start Time")
                self.checkPoints(mPoints)
                Mstart = mStartTime
                Interval = float(round((mEndTime-mStartTime)/mPoints*1e8))*1e-8
                Average = Interval*self.Averaging

            self.CreatePattern(Name, chn, Voltages, dTimes, Mstart, count, Average, Interval, mPoints, Vinit=Vb, AddSequence=AddSequence)
        else:
            Mstart = -1
            self.CreatePattern(Name, chn,  Voltages, dTimes, Mstart, count, Vinit=Vb, AddSequence=AddSequence)

        if WriteHeader:
            header = []
            header.append('Testparameter,Measurement.Tri.%s.Channel,%d' %(Name,chn))
            header.append('Testparameter,Measurement.Tri.%s.Count,%d' %(Name,count))
            header.append('Testparameter,Measurement.Tri.%s.Rise.Time,%f' %(Name,trise))
            header.append('Testparameter,Measurement.Tri.%s.Fall.Time,%f' %(Name,tfall))
            header.append('Testparameter,Measurement.Tri.%s.Base.Time,%f' %(Name,tbase))
            header.append('Testparameter,Measurement.Tri.%s.Rise.Time,%f' %(Name,trise))
            header.append('Testparameter,Measurement.Tri.%s.Pulse.Voltage,%f' %(Name,Vp))
            header.append('Testparameter,Measurement.Tri.%s.Base.Voltage,%f' %(Name,Vb))
            if Mstart == -1:
                header.append('Testparameter,Measurement.Tri.%s.Measuarement,%s' %(Name,'No Measurement'))
            else:
                header.append('Testparameter,Measurement.Tri.%s.Start.Time,%f' %(Name,Mstart))
                header.append('Testparameter,Measurement.Tri.%s.Interval,%f' %(Name,Interval))
                header.append('Testparameter,Measurement.Tri.%s.Average,%f' %(Name,Average))
                header.append('Testparameter,Measurement.Tri.%s.Points,%d' %(Name,mPoints))

            if self.__WritePulseHeader:
                self.__PulseHeader.append(header)

    #programs a triangular Pulse into the offline library, a measurement is optional, the measurement channel parameters are set globally. 
    #Measurement events in this pattern can be set in a list or as a single measurement event. 
    #   if set in a list, mStartTime, mPoints and mInterval must have the same length.
    #   if measure Start and End time arent used, the values will be set to the Start and end time of the pattern
    #chn:           Channel Number
    #duration:      duration (s), will be split between before and after
    #Vp:            Pulse voltage (V) 
    #Vb:            Base voltage (V)
    #count:         Number of repetitions (this)
    #measure:       Enable measurement (True), Disable measurement (False)
    #mPoints:       number of Points during pulse
    #mStartTime:    measurement Start time (s)
    #mEndTime:      measurement End time (s)
    #AddSequence:   Automatically adds a sequence (necessary to automatically execute count 2+)
    #Name:          subname for pattern "Name_x_chn", x is iterative number, chn is channel number
    #WriteHeader:   write the pulse information into the header (automatically true) 
    def programGroundChn(self, chn, duration, Vg=0, count=1, measure=True, mPoints=1, mStartTime=None, mEndTime=None, AddSequence=True, Name=None, WriteHeader=True):
        
        if not isinstance(WriteHeader,bool):
            self.TypError("WriteHeader must be of type boolean, True/False: Write/Don't write a header to the output file.")

        if Name == None:
            Name = 'Ground'
        t_total = duration

        if measure:
            if mStartTime==None:
                mStartTime = 0
            if mEndTime==None:
                mEndTime=t_total

            if isinstance(mPoints, type([])):
                self.checkArrayConsistancy([mStartTime, mEndTime, mPoints], "Measurement stat/end time and mPoints must have the same dimension")
                Interval = []
                Average = []
                for n in range(len(mStartTime)):
                    if mEndTime[n] < mStartTime[n]:
                        self.ValError("Measurement End Time must be larger than measurement Start Time")
                    self.checkPoints(mPoints[n])
                    Mstart = mStartTime
                    Interval.append(float(round((mEndTime[n]-mStartTime[n])/mPoints[n]*1e8))*1e-8)
                    Average.append(Interval[n]*self.Averaging)

            else:
                if mEndTime < mStartTime:
                    self.ValError("Measurement End Time must be larger than measurement Start Time")
                self.checkPoints(mPoints)
                Mstart = mStartTime
                Interval = float(round((mEndTime-mStartTime)/mPoints*1e8))*1e-8
                Average = Interval*self.Averaging
            
            self.CreatePattern(Name, chn, [Vg], [duration], Mstart, count, Average, Interval, mPoints, Vinit=Vg, AddSequence=AddSequence)
        else:
            Mstart = -1
            self.CreatePattern(Name, chn, [Vg], [duration], Mstart, count, Vinit=Vg,  AddSequence=AddSequence)

        if WriteHeader:
            header = []
            header.append('Testparameter,Measurement.Ground.%s.Channel,%d' %(Name,chn))
            header.append('Testparameter,Measurement.Ground.%s.Count,%d' %(Name,count))
            header.append('Testparameter,Measurement.Ground.%s.Time,%f' %(Name,duration))
            
            if Mstart == -1:
                header.append('Testparameter,Measurement.Tri.%s.Measuarement,%s' %(Name,'No Measurement'))
            else:
                header.append('Testparameter,Measurement.Tri.%s.Start.Time,%f' %(Name,Mstart))
                header.append('Testparameter,Measurement.Tri.%s.Interval,%f' %(Name,Interval))
                header.append('Testparameter,Measurement.Tri.%s.Average,%f' %(Name,Average))
                header.append('Testparameter,Measurement.Tri.%s.Points,%d' %(Name,mPoints))
            
            if self.__WritePulseHeader:
                self.__PulseHeader.append(header)

    def getHeader(self):

        header = []
        header.append('TestParameter,Context.MainFrame,%s' %(self.mainframe))
        header.append('TestParameter,Context.WarningLevel,%s' %(self.__getShortStatusFromCode(self.__WarningLevel)))
        header.append('TestParameter,Channel.UnitType')
        header.append('TestParameter,Channel.ID')
        header.append('TestParameter,Channel.OperationMode')
        header.append('TestParameter,Channel.MeasureMode')
        header.append('TestParameter,Channel.Name')
        header.append('TestParameter,Channel.MeasureDelay')
        header.append('TestParameter,Channel.ForceDelay')
        header.append('TestParameter,Channel.VoltageForceRange')
        header.append('TestParameter,Channel.VoltageMeasureRange')
        header.append('TestParameter,Channel.CurrentMeasureRange')
        header.append('TestParameter,Channel.Trigger.Mode')
        header.append('TestParameter,Channel.Trigger.Polarization')
        l=2
        n=0
        for n in range(len(self.__ChnIDs)):
            if self.__MeasureEnable[n] == self.WGFMU_MEASURE_ENABLED_ENABLE:
                header[l+0] = "%s,%s" %(header[l+0],"WGFMU")
                header[l+1] = "%s,%s" %(header[l+1],self.__ChnIDs[n])
                header[l+2] = "%s,%s" %(header[l+2],self.__getShortStatusFromCode(self.__OperationMode[n]))
                header[l+3] = "%s,%s" %(header[l+3],self.__getShortStatusFromCode(self.__MeasureMode[n]))
                header[l+4] = "%s,%s" %(header[l+4],self.__Name[n])
                header[l+5] = "%s,%s" %(header[l+5],self.__MeasureDelay[n])
                header[l+6] = "%s,%s" %(header[l+6],self.__VForceDelay[n])
                header[l+7] = "%s,%s" %(header[l+7],self.__getShortStatusFromCode(self.__VForceRange[n]))
                header[l+8] = "%s,%s" %(header[l+8],self.__getShortStatusFromCode(self.__VMeasureRange[n]))
                header[l+9] = "%s,%s" %(header[l+9],self.__getShortStatusFromCode(self.__IMeasureRange[n]))
                header[l+10] = "%s,%s" %(header[l+10],self.__getShortStatusFromCode(self.__TriggerOutMode[n]))
                header[l+11] = "%s,%s" %(header[l+11],self.__getShortStatusFromCode(self.__TriggerOutPol[n]))
            n+=1
        header.append('TestParameter,Data.Output,%s' %(self.__getShortStatusFromCode(self.__rdata)))
        header.append('TestParameter,Measurement.Timeout,%s' %(self.__Timeout))

        for Pheader in self.__PulseHeader:
            header.extend(Pheader)

        return header

    def enableWritePulseHeader(self):
        self.__WritePulseHeader = True
        
    def disableWritePulseHeader(self):
        self.__WritePulseHeader = False

