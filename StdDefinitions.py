"""
Written by: Karsten Beckmann and Maximillian Liehr
Institution: SUNY Polytechnic Institute
Date: 6/12/2018

Standard Definitions to be used in the automatic control of Probe station. 
"""

from ctypes import *
import os as os
import pathlib as path
import csv as csv
import time as tm
import numpy as np
from numpy.core.fromnumeric import trace
import pyvisa as vs
import math as ma
import sys
import statistics as stat
import threading as th
import DataHandling as dh
import datetime as dt
import queue as qu
import pickle as pk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
import imghdr
import traceback


def WGFMUSetChannelParameters(eChar, Configuration, Instruments):
    
    if Configuration.getValue("WGFMUUseGUI") and len(Instruments.getInstrumentsByType("B1530A")) != 0:
        
        for entry in Instruments.getInstrumentsByType("B1530A"):
            
            inst = entry['Instrument']
            GPIB = entry['GPIB']

            devCode = "$B1530A$_%s" %(GPIB)
            
            if inst != None:
                
                chns = inst.getChannelIDs()['Channels']
                for chn in chns:

                    inst.setChannelParameter(chn, Configuration.getValue("%s_%s_ModeList" %(devCode, chn),False), Configuration.getValue("%s_%s_ForceVoltageRange" %(devCode, chn),False), 
                                                            Configuration.getValue("%s_%s_MeasureMode" %(devCode, chn),False), Configuration.getValue("%s_%s_MeasureCurrentRange" %(devCode, chn),False), 
                                                            Configuration.getValue("%s_%s_MeasureVoltageRange" %(devCode, chn),False), Configuration.getValue("%s_%s_ForceDelay" %(devCode, chn),False), 
                                                            Configuration.getValue("%s_%s_MeasureDelay" %(devCode, chn),False))
                   

                    line = "Set WGFMU Channel Values - Channel: %s, Mode: %s, Force Voltage Range: %s, Measure Mode: %s, Current Measure Range: %s, Voltage Measure Range: %s, Force Delay: %s, Measure Delay: %s." %(chn, 
                                                            Configuration.getValue("%s_%s_ModeList" %(devCode, chn),False), Configuration.getValue("%s_%s_ForceVoltageRange" %(devCode, chn),False), 
                                                            Configuration.getValue("%s_%s_MeasureMode" %(devCode, chn),False), Configuration.getValue("%s_%s_MeasureCurrentRange" %(devCode, chn),False), 
                                                            Configuration.getValue("%s_%s_MeasureVoltageRange" %(devCode, chn),False), Configuration.getValue("%s_%s_ForceDelay" %(devCode, chn),False), 
                                                            Configuration.getValue("%s_%s_MeasureDelay" %(devCode, chn),False))

                    eChar.writeMeasLog(line)

def MesurementExecution(deviceCharacterization, eChar, Configuration, threads, GraInterface, Instruments, MeasurementSetup):
    #try:
        WGFMUSetChannelParameters(eChar, Configuration, Instruments)
        Prober =  Instruments.getProberInstrument()

        # of Experiments
        n = 0
        for entry in deviceCharacterization:
            
            if isinstance(entry["Parameters"], list):
                n = n+1


        if Prober == None: 
            Configuration.setCurrentDie(True)
            Configuration.setMultipleDev(False)
            line = "No Prober Available"
        else:
            line = "Prober %s on GPIB address %s will be used." %(Instruments.getProber()["Model"], Instruments.getProber()["GPIB"])
        eChar.writeMeasLog(line)
    
        MesurementExecutionPS(deviceCharacterization, eChar, Configuration, threads, GraInterface, Instruments)

        if Prober != None and Configuration.getMultipleDev():
            sepX = Configuration.getXPitch()
            sepY = Configuration.getYPitch()

            #dont move after Measurement finished
            if abs(sepX) > 0:
                #newDevStaX = Configuration.getDeviceStartX()+Configuration.getNumXDevices()
                Configuration.setDeviceStartX(Configuration.getDeviceStartX())
                #Prober.MoveChuckMicron(-Configuration.getXPitch(),0,"R",25)
                MeasurementSetup.DevStartX.setVariable(Configuration.getDeviceStartX())
                
            if abs(sepY) > 0:
                #newDevStaY = Configuration.getDeviceStartY()+Configuration.getNumYDevices()
                Configuration.setDeviceStartY(Configuration.getDeviceStartY())
                #Prober.MoveChuckMicron(0,-Configuration.getYPitch(),"R",25)
                MeasurementSetup.DevStartY.setVariable(Configuration.getDeviceStartY())

        
        '''
        if Prober != None and Configuration.getMultipleDev():

            sepX = Configuration.getXPitch()
            sepY = Configuration.getYPitch()

            if abs(sepX) > 0:
                newDevStaX = Configuration.getDeviceStartX()+Configuration.getNumXDevices()
                Configuration.setDeviceStartX(newDevStaX)
                Prober.MoveChuckMicron(-Configuration.getXPitch(),0,"R",25)
                MeasurementSetup.DevStartX.setVariable(newDevStaX)
                
            if abs(sepY) > 0:
                newDevStaY = Configuration.getDeviceStartY()+Configuration.getNumYDevices()
                Configuration.setDeviceStartY(newDevStaY)
                Prober.MoveChuckMicron(0,-Configuration.getYPitch(),"R",25)
                MeasurementSetup.DevStartY.setVariable(newDevStaY)
        '''
        # GraInterface.WriteError("Error during execution: %s" %(message))
        
    #except Exception as e:
    #    eChar.writeLog("Error executing measurement: %s." %(e))
    #    GraInterface.Finished()

def getBinaryList(IntIn, binSize=8):
    IntIn = int(IntIn)
    
    binIn = bin(IntIn)[2:]
    binOut = [0]*binSize
    inSize = len(binIn)

    for n in range(inSize):
        binOut[n] = int(binIn[inSize-1-n])

    return binOut

def MesurementExecutionWPS(deviceCharacterization, eChar, Configuration, threads, GraInterface, Instruments):

    eChar.DevX = Configuration.getDeviceStartX()
    eChar.DevY = Configuration.getDeviceStartY()
    eChar.WaferChar = False
    
    # of Experiments
    n = 0
    for entry in deviceCharacterization:
        k = 0
        for para in entry["Parameters"]:
            if entry["Experiment"][k] == True:
                if isinstance(para, list):
                    n = n+1
            k+=1
    if n > 0:
        raise ValueError("An Experiment cannot be performed during single device operation.")


    for entry in deviceCharacterization:
        
        ret = eChar.executeMeasurement(entry['Folder'], entry['Name'], entry['Parameters']) 
        if ret == "stop":
            break
        
    devBatch = eChar.StatOutValues
    threads.put(devBatch.WriteBatch(eChar))

def MesurementExecutionPS(deviceCharacterization, eChar, Configuration, threads, GraInterface, Instruments):
    
    if Instruments.getProberInstrument() == None:
        ProStat = ProberWrapper()
        initPos = [0,0]
        Configuration.setMultipleDev(False)
        Configuration.setCurrentDie(True)
    else: 
        ProStat = Instruments.getProberInstrument()
        initPos = ProStat.ReadChuckPosition("X","C")
        eChar.writeMeasLog("Initial Position (um): %s" %(initPos))


    if Configuration.getUseMatrix() and Configuration.getMatrixConfiguration() == None:
        eChar.writeLog("You selected to use the Matrix but no Matrix Configuration is specified.")
        Configuration.setUseMatrix(False)

    if Instruments.getMatrixInstrument() == None:
        Configuration.setUseMatrix(False)

    

    NumOfDev = 1
    if Configuration.getMultipleDev():
        lenXDev = Configuration.getNumXDevices()
        lenYDev = Configuration.getNumYDevices()
        NumOfDev = lenXDev*lenYDev
    else:
        lenXDev = 1
        lenYDev = 1

    eChar.writeMeasLog("Number of X Devices: %s" %(lenXDev))
    eChar.writeMeasLog("Number of Y Devices: %s" %(lenYDev))

    #running attempts after a WGFMU error
    nTry = 10
    # of Experiments
    n = 0
    l = 1
    ExpIDs = []
    ExpNames = []
    ExpParIDs = []
    ExpParNames = []
    ExpParameter = []

    if len(Instruments.getInstrumentsByType('B1530A')) != 0: 
        if Instruments.getInstrumentsByType('B1530A')[0]["Instrument"] != None:
            Instruments.getInstrumentsByType('B1530A')[0]["Instrument"].startLog()
    
    for m in range(len(deviceCharacterization)):
        for k in range(len(deviceCharacterization[m]["Parameters"])):
            if deviceCharacterization[m]["Experiment"][k] == True:
                if n == 0:
                    l = len(deviceCharacterization[m]["Parameters"][k])
                    if l > NumOfDev:
                        eChar.ErrorQueue.put("The Number of Measuring devices must be longer than the number of Experimental split!")
                        raise ValueError("The Number of Measuring devices must be longer than the number of Experimental split!")
                    if ProStat == None and l > 0:
                        eChar.ErrorQueue.put("An Experiment can only performed if a Prober is available!")
                        raise ValueError("An Experiment can only performed if a Prober is available!")

                else: 
                    if l != len(deviceCharacterization[m]["Parameters"][k]):
                        raise ValueError("The Experimental split length must match!")

                if not m in ExpIDs:
                    ExpNames = deviceCharacterization[m]["Name"]
                    ExpIDs.append(m)
                    ExpParIDs.append([])
                    ExpParIDs[len(ExpIDs)-1].append(k)
                    ExpParNames.append([])
                    ExpParNames[len(ExpIDs)-1].append(deviceCharacterization[m]["ValueNames"][k])
                    ExpParameter.append([])
                    ExpParameter[len(ExpIDs)-1].append(deviceCharacterization[m]["Parameters"][k])
                else:
                    ExpParIDs[len(ExpIDs)-1].append(k)
                    ExpParNames[len(ExpIDs)-1].append(deviceCharacterization[m]["ValueNames"][k])
                    ExpParameter[len(ExpIDs)-1].append(deviceCharacterization[m]["Parameters"][k])

                if not Configuration.getMultipleDev():
                    raise ValueError("An Experiment cannot be performed during single device operation.")
            else:
                if isinstance(deviceCharacterization[m]["Parameters"][k], list) and False == deviceCharacterization[m]["Array"][k]:
                    if deviceCharacterization[m]["Parameters"][k] == []:
                        deviceCharacterization[m]["Parameters"][k] = None
                    else:
                        deviceCharacterization[m]["Parameters"][k] = deviceCharacterization[m]["Parameters"][k][0]

    '''
    for n in range(len(ExpIDs)):
        for k in range(len(deviceCharacterization[ExpIDs[n]]["Parameters"])):
            if k in ExpParIDs[n]:
                deviceCharacterization[ExpIDs[n]]["Parameters"] = [deviceCharacterization[ExpIDs[n]]["Parameters"]]*l
    '''
    
    NumOfDev = int(NumOfDev)

    DevPerExp = int(ma.floor(NumOfDev/l))
    Left = int(NumOfDev-DevPerExp*l)

    ExpNum = []
    m = 0
    k = 0
    for n in range(NumOfDev):
        if n < (DevPerExp+1)*Left:
            Move = DevPerExp + 1
        else:
            Move = DevPerExp
        if k >= Move:
            m = m+1
            k = 0
        ExpNum.append(m)
        k = k+1

    eChar.WaferChar = True
    
    stop = False
    dies = Configuration.getDies()
    lenDies = len(dies)
    

    for n in range(4):
        eChar.ExternalHeader.append('')
    n=0

    CurrentDie = Configuration.getCurrentDie()
    
    
    die0 = []
    for x in initPos[0:2]:
        die0.append(int(round(float(x)+Configuration.getCenterLocation()[n])))
        n+=1

    if CurrentDie:
        lenDies = 1
        dies = [die0]

    ECharTime = 0
    first = True
    
    ### only create Batches for the Die if more than one wafer gets measured
    if not CurrentDie:
        dieBatchPos = dh.batch("DiePositionSummary")
        dieBatchComp = dh.batch("DieComplete")
        dieBatchSubMeas = dh.batch("DieMeasSummary")

    if Configuration.getMultipleDev():
        lenXDev = Configuration.getNumXDevices()
        lenYDev = Configuration.getNumYDevices()
    else:
        lenXDev = 1
        lenYDev = 1
    
    eChar.writeLog("%d Die/s will be measured." %(lenDies))
    stop = False

    line = ""
    for die in dies: 
        line = "%s, %s" %(line, die)
    line = "Measured Dies: %s" %(line[2:])
    eChar.writeMeasLog(line)

    for n in range(lenDies):
        
        eChar.writeLog("Die: %s will be measured" %(dies[n]))
                
        if not CurrentDie:
            
            if n == 0:
                move = indexMove([die0[0],die0[1]],dies[n])
            else:
                move = indexMove(dies[n-1],dies[n])
            
            ProStat.MoveChuckIndex(-move['Xmove'],-move['Ymove'],"R")

            eChar.DieX = dies[n][0]
            eChar.DieY = dies[n][1]
            
        else:
            eChar.DieX = die0[0]
            eChar.DieY = die0[1]
        
        if Configuration.getMultipleDev():
            deviceBatchPos = dh.batch("DevicePositionSummary")
            deviceBatchComp = dh.batch("DeviceComplete")
            deviceBatchSubMeas = dh.batch("DeviceMeasSummary")    

        devNum = 0

        for xdev in range(lenXDev):
            print("for X", xdev)
            
            eChar.DevX = xdev+Configuration.getDeviceStartX()
            
            if not GraInterface.continueExecution() or stop:
                stop = True
                break

            for ydev in range(lenYDev):
                print("for Y", ydev)
                
                eChar.DevY = ydev+Configuration.getDeviceStartY()
                if not GraInterface.continueExecution() or stop:
                    stop = True
                    break
                
                eChar.writeLog("Dev: X%s-Y%s will be measured" %(xdev, ydev))
                
                if Configuration.getUseMatrix() and Instruments.getMatrixInstrument() != None:
                    line = "Matrix will be used - UseMatrix: %s, MatrixInstrument: %s" %(Configuration.getUseMatrix(), Instruments.getMatrixInstrument())
                else:
                    line = "Matrix will not be used - UseMatrix: %s, MatrixInstrument: %s" %(Configuration.getUseMatrix(), Instruments.getMatrixInstrument())
                
                eChar.writeLog(line)

                eh = len(eChar.ExternalHeader)-4
                    
                eChar.ExternalHeader[eh+0] = ('ProbeStation,Device.X,%d' %(xdev+Configuration.getDeviceStartX()))
                eChar.ExternalHeader[eh+1] = ('ProbeStation,Device.Y,%d' %(ydev+Configuration.getDeviceStartX()))

                eChar.ExternalHeader[eh+2] = ('ProbeStation,Die.X,%d' %(dies[n][0]))
                eChar.ExternalHeader[eh+3] = ('ProbeStation,Die.Y,%d' %(dies[n][1]))

                MC = MatrixChange(Instruments.getMatrixInstrument(), Configuration.getMatrixConfiguration(), Configuration.getUseMatrix())
                if Configuration.getUseMatrix():
                    eChar.writeMeasLog("Use Matrix.")
                
                ProStat.MoveChuckContact()
                ProStat.EnableMotorQuiet()
                if Instruments.getProberInstrument() != None:
                    eChar.writeMeasLog("Move Chuck into Contact and Enable Quite Mode.")
                
                if Configuration.getUseMatrix():
                    matrixBatchPos = dh.batch("MatrixPositionSummary")
                    matrixBatchComp = dh.batch("MatrixComplete")
                    matrixBatchSubMeas = dh.batch("MatrixMeasSummary")    
                
                eChar.MatDev = 0
                
                while MC.setNext():
                    if Configuration.getUseMatrix():
                        eChar.writeMeasLog(MC.getHeader())

                    eChar.MatDev = eChar.MatDev + 1
                    
                    eChar.MatNormal = MC.getNormalConfiguration()
                    eChar.MatBit = MC.getBitConfiguration()
                    
                    if not GraInterface.continueExecution() or stop:
                        stop = True
                        break

                    devNum += 1

                    eChar.reset()

                    if first:
                        ECharTime = tm.time()

                    ### execute Measurement
                    k = 0
                    px = 0

                    for entry in deviceCharacterization:
                        print("entry", entry)
                        con = GraInterface.continueExecution() 

                        eChar.writeLog("Measurment Execution continues: %s" %(con))
                        while not eChar.Stop.empty():
                            stop = eChar.Stop.get()

                        if not GraInterface.continueExecution() or stop:
                            stop = True
                            break

                        if k in ExpIDs:
                            parList = []
                            pi = 0
                            for param in entry["Parameters"]:
                                if pi in ExpParIDs[px]:
                                    parList.append(param[ExpNum[devNum-1]])
                                else:
                                    parList.append(param)
                                pi = pi+1
                            px = px+1

                            # if an error occured in the tool, retry the measurement 'nTry' times
                            for o in range(nTry):

                                while not eChar.Stop.empty():
                                    stop = eChar.Stop.get()

                                if not GraInterface.continueExecution() or stop:
                                    stop = True
                                    break

                                try:         
                                    if len(Instruments.getInstrumentsByType('B1530A')) != 0: 
                                        if Instruments.getInstrumentsByType('B1530A')[0]["Instrument"] != None:
                                            Instruments.getInstrumentsByType('B1530A')[0]["Instrument"].startLog()
                                            print("startLog - 1, try:", o)
                                    
                                    logEntry = "execute '%s' in Folder '%s' with Parameters: %s" %(entry['Name'], entry['Folder'], parList)
                                    eChar.writeLog(logEntry)

                                    ret = eChar.executeMeasurement(entry['Folder'], entry['Name'], parList) 
                                    if ret == "stop":
                                        stop = True
                                    break
                                    
                                except (SystemError, ValueError, vs.VisaIOError, IndexError) as e:
                                    print("error after Execution 1")
                                    print(traceback.print_exc())
                                    eChar.finished.put(True)
                                    eChar.ErrorQueue.put(e)
                                    ProStat.MoveChuckSeparation()
                                    eChar.checkInstrumentation()
                                    WGFMUSetChannelParameters(eChar, Configuration, Instruments)
                                    
                                    ProStat.MoveChuckContact()
                                    ProStat.EnableMotorQuiet()

                            try: 
                                stop = ret['Stop']
                                del ret
                                break
                            except:
                                del ret               
                        else:
                            # if an error occured in the tool, retry the measurement 'nTry' times
                            for o in range(nTry):
                                
                                while not eChar.Stop.empty():
                                    stop = eChar.Stop.get()
                                    print("stop", stop)

                                if not GraInterface.continueExecution() or stop:
                                    print("stop")
                                    stop = True
                                    break
                                
                                try:                                  
                                    if len(Instruments.getInstrumentsByType('B1530A')) != 0: 
                                        if Instruments.getInstrumentsByType('B1530A')[0]["Instrument"] != None:
                                            Instruments.getInstrumentsByType('B1530A')[0]["Instrument"].startLog()
                                            print("startLog, try:", o)
                                    
                                    parList = entry["Parameters"]
                                    logEntry = "execute '%s' in Folder '%s' with Parameters: %s" %(entry['Name'], entry['Folder'], parList)
                                    eChar.writeLog(logEntry)
                                    
                                    ret = eChar.executeMeasurement(entry['Folder'], entry['Name'], parList) 
                                    if ret == "stop":
                                        stop = True
                                    break

                                except (SystemError, ValueError, vs.VisaIOError, IndexError) as e:
                                    print("error after Execution 2", e)
                                    print(traceback.print_exc())
                                    eChar.finished.put(True)
                                    eChar.ErrorQueue.put(e)
                                    ProStat.MoveChuckSeparation()
                                    eChar.checkInstrumentation()
                                    WGFMUSetChannelParameters(eChar, Configuration, Instruments)
                                    ProStat.MoveChuckContact()
                                    ProStat.EnableMotorQuiet()
                        k = k+1
                        
                    eChar.writeLog('Move to Next Measurement')

                    if first:
                        ECharTime = tm.time() - ECharTime
                        first = False
                    
                    devBatch = eChar.StatOutValues
                    devBatch.addExperiment(ExpNames, ExpParNames, ExpParameter)
                    threads.put(devBatch.WriteBatch(eChar))

                    if not GraInterface.continueExecution() or stop:
                        stop = True
                        break                    

                    if Configuration.getUseMatrix():
                        matrixBatchPos.addRow(devBatch.getCompresedRow())
                        BatchPos = matrixBatchPos
                        matrixBatchComp.addRows(devBatch.getRows())
                        BatchComp = matrixBatchComp
                        matrixBatchSubMeas.addBatch('Measurements', devBatch)
                        BatchSubMeas = matrixBatchSubMeas
                    else: 
                        BatchPos = devBatch
                        BatchComp = devBatch
                        BatchSubMeas = devBatch

                if Configuration.getMultipleDev():
                    if ydev < lenYDev-1:
                        ProStat.MoveChuckMicron(0,-Configuration.getYPitch(),"R",25)
                    else:
                        Yreturn = float(np.multiply(int(Configuration.getYPitch()),int(Configuration.getNumYDevices())))
                        ProStat.MoveChuckMicron(0,Yreturn,"R",25)

                if Configuration.getMultipleDev():
                    try:
                        deviceBatchPos.addRow(BatchPos.getCompresedRow())
                        deviceBatchComp.addRows(BatchComp.getRows())
                        deviceBatchSubMeas.addBatch('Measurements', BatchSubMeas)
                        BatchPos = deviceBatchPos
                        BatchComp = deviceBatchComp
                        BatchSubMeas = deviceBatchSubMeas
                    except UnboundLocalError as e:
                        print(traceback.print_exc())
                        None
                        
                GraInterface.InputDataWaferMap({'Die': Configuration.getDies()[n],'add':1})
                ProStat.MoveChuckSeparation()

            if not GraInterface.continueExecution() or stop:
                stop = True
                break

            if Configuration.getMultipleDev():
                if xdev  < lenXDev-1:
                    ProStat.MoveChuckMicron(-Configuration.getXPitch(),0,"R",25)
                else:
                    Xreturn = float(np.multiply(int(Configuration.getXPitch()),int(Configuration.getNumXDevices())-1))
                    ProStat.MoveChuckMicron(Xreturn,0,"R",25)

        if not GraInterface.continueExecution() or stop:
            
            stop = True
            break

        if Configuration.getMultipleDev():
            try: 
                deviceBatchPos.WriteBatch(eChar, Max=True, Min=True)
                deviceBatchComp.WriteBatch(eChar, Max=True, Min=True)
                deviceBatchSubMeas.WriteBatch(eChar, Max=True, Min=True)
            except UnboundLocalError:
                None
        
        if not CurrentDie:
            try:
                dieBatchPos.addRow(BatchPos.getCompresedRow(True))
                dieBatchComp.addRows(BatchComp.getRows())
                dieBatchSubMeas.addBatch('Measurements', BatchSubMeas)
            except UnboundLocalError:
                print(traceback.print_exc())
                BatchPos = devBatch
                BatchComp = devBatch
                BatchSubMeas = devBatch
                dieBatchPos.addRow(BatchPos.getCompresedRow(True))
                dieBatchComp.addRows(BatchComp.getRows())
                dieBatchSubMeas.addBatch('Measurements', BatchSubMeas)

    if stop: 
        eChar.writeMeasLog("stop")
    
    #Empty Stop queue in EChar
    while not eChar.Stop.empty():
        stop = eChar.Stop.get()

    #ProStat.MoveChuckMicron(-initPosMic[0],-initPosMic[1],"C")
    if not CurrentDie:

        threads.put(dieBatchPos.WriteBatch(eChar, Max=True, Min=True))
        threads.put(dieBatchComp.WriteBatch(eChar, Max=True, Min=True))
        threads.put(dieBatchSubMeas.WriteBatch(eChar, Max=True, Min=True))

    #except (ValueError, TypeError, SystemError) as message:

    if len(Instruments.getInstrumentsByType('B1530A')) != 0: 
        if Instruments.getInstrumentsByType('B1530A')[0]["Instrument"] != None:
            Instruments.getInstrumentsByType('B1530A')[0]["Instrument"].endLog()

    eChar.clearStop()

def getMeasurementLogHeader(eChar, deviceCharacterization, ConfigCopy):
    
    ret = []
    ret.append("MeasurementSequence run on %s:\n" %(ConfigCopy.getComputerName()))
    ret.append("Data will be stored under %s.\n" %(eChar.getFolder()))
    
    
    n = 1
    for entry in deviceCharacterization:

        line = "Measurement %d - Name: %s/%s - " %(n, entry["Folder"], entry["Name"])
        m = 0
        for val, par in zip(entry['ValueNames'], entry['Parameters']):

            exp = ""
            if entry['Experiment'][m]:
                exp = "(EXP)"

            ar = ""
            if entry['Array'][m]:
                ar = "(AR)"

            if isinstance(par, list):
                
                if len(par) == 0:
                    line = "%s%s%s%s: %s, " %(line, val, exp, ar, "")
                elif len(par) == 1:
                    line = "%s%s%s%s: %s, " %(line, val, exp, ar, par[0])
                else:
                    p = par[0]
                    for x in par[1:]:
                        p = "%s,%s" %(p,x)
                    line = "%s%s%s%s: %s, " %(line, val, exp, ar, p)

            else:
                line = "%s%s%s%s: %s, " %(line, val, exp, ar, par)

            m = m+1
        ret.append("%s\n" %(line[:-2]))
        n = n + 1
    
    return ret
    
def writeMeasurmentLog(deviceCharacterization, eChar, ConfigCopy, Instruments, MeasTypeClass):

    header = getMeasurementLogHeader(eChar, deviceCharacterization, ConfigCopy)

    withDies = False
    if ConfigCopy.getDies() != None: 
        if len(ConfigCopy.getDies()) == 1: 
            withDies = True

    folder = eChar.getFolder(withDies)
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H-%M-%S-%f")
    filename = "MeasurementLog_%s_%s.txt" %(ConfigCopy.getDeviceName(), timestamp)
    dataQu = eChar.getMeasLogQueue()

    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except FileExistsError:
            None

    CompFile = "%s/%s" %(folder,filename)

    Finish = False

    with open(CompFile, 'w') as f:

        f.writelines(header)
        while not Finish:
            
            tm.sleep(1)
            
            while not dataQu.empty():
                timestamp = dt.datetime.now().strftime("%Y-%m-%d_%H:%M:%S:%f")
                quData = dataQu.get()
                line = "%s - %s\n" %(timestamp, quData)
                f.write(line)

                if quData.strip().lower() == "finished" or quData.strip().lower() == "stop":
                    Finish = True
                    break
    
    while not dataQu.empty():
        dataQu.get()


def writeDataToFile(header, data, folder, filename, MeasQu=None, subFolder=None):

    if subFolder != None:
        folder = "%s/%s" %(folder, subFolder)

    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except FileExistsError:
            None
    CompFile = "%s/%s" %(folder,filename)

    try:
        with open(CompFile, 'w') as csvfile:
            wr = csv.writer(csvfile, delimiter=",", escapechar=' ', quoting=csv.QUOTE_NONE, lineterminator='\n',)
            for line in header:
                wr.writerow([line])
            for da in data:
                wr.writerow([da])
            #wr.writerow(data)
        csvfile.close()
    except:
        print("end thread ", filename)
        SystemError("Access to the file was unsucessful! You should probably close the file.")

    if subFolder != None:
        mes = "File Written %s/%s" %(subFolder, filename)
    else:
        mes = "File Written %s" %(filename)
        
    if MeasQu != None:
            MeasQu.put(mes)
    return 0

def getLogScale(start, stop, steps):
    
    logtst = np.log10(start)
    logttot = np.log10(stop)

    logTotal = logttot - logtst
    logDelta = logTotal/(steps-1)
    ret = []
    for m in range(steps):
        ret.append(np.power(10,(logtst+m*logDelta)))

    return ret

def writeConfigFile(config, file):

    folder, filename = os.path.split(file)
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except FileExistsError:
            None

    CompFile = "%s/%s" %(folder,filename)
    
    try:
        with open(CompFile, 'w') as f:
            for line in config:
                n = 0
                for entry in line:
                    if n == 0:
                        l = entry
                    else:
                        l = "%s,%s" %(l, str(entry)) 
                    n = n+1
                l = "%s\n" %(l)
                f.write(l)
    except:
        SystemError("Access to the file was unsucessful! You should probably close the file.")
    return 0

class Average:

    RunAverage = 0
    size = 0
    RunStdDeviation = 0
    RunAvgSq = 0

    def getAverage(self):
        return float(self.RunAverage)

    def extendAverage(self, l):
        
        l = np.array(l)

        average = getAverage(l)
        size = np.size(l)
        l2 = np.square(l)
        avg2 = getAverage(l2)

        NewAvg = np.divide(np.sum([np.multiply(self.RunAverage,self.size),np.multiply(average,size)]),np.sum([self.size,size]))
        NewAvg2 = np.divide(np.sum([np.multiply(self.RunAvgSq,self.size),np.multiply(avg2,size)]),np.sum([self.size,size]))

        NewStD = np.sqrt(np.subtract(self.RunAvgSq,np.square(self.RunAverage)))

        self.RunAverage = NewAvg
        self.RunAvgSq = NewAvg2
        self.size = np.sum([self.size,size])
        
        return {'Average': float(NewAvg), 'StdDeviation': float(NewStD)}
    
    def getStdDeviation(self):
        return float(self.RunStdDeviation)
        
    def clear(self):
        self.size=0
        self.RunAverage = 0

def getAverage(DataList):

    if isinstance(DataList, type([])):
        return sum(DataList)/(float(len(DataList)))
    if isinstance(DataList, type(np.array([0]))):
        a = np.average(DataList)
        return a

def getStdDeviation(DataList): 

    if isinstance(DataList, type([])):
        return stat.stdev(DataList)
    if isinstance(DataList, type(np.array([0]))):
        return np.std(DataList)

def isDieInWafer(wafer, n, m, x, y):
    
    n = abs(n)
    m = abs(m)

    x1 = (n + 0.55)*x
    y1 = (m + 0.55)*y
    x2 = np.multiply(x1,x1)
    y2 = np.multiply(y1,y1)

    d = np.sqrt(x2+y2)
    if d > wafer/2:
        return False
    else:
        return True

def getFile_FolderText(text, length):

    if len(text) < length:
        return text
    else: 
        return "...%s" %(text[-(length-3):])

def LoadDieFile(DieFile, waferSize, xDim, yDim):
    
    dies = []
    if os.path.exists(DieFile):
        rows = []
        with open(DieFile, newline='') as csvfile:
            csvRows = csv.reader(csvfile)
            for row in csvRows:
                rows.append(row)
        csvfile.close()
        for row in rows:
            if not row[0].strip()[0] == '#':
                die = []
                if len(row)==2:
                    for item in row:
                        try:
                            die.append(int(item.strip()))
                        except:
                            raise ValueError("The DieMap is not in the correct format!")
                    dies.append(die)
    else:
        msg.askokcancel("Die File does not exist.", "Do you want to measure only the center die?", icon='warning')
        if 'Cancel':
            sys.exit()
        else:
            dies.append([0,0])
    if dies == []:
        raise ValueError("No die entries are in the right format!")
    FilteredDies = []
    for die in dies:
        if isDieInWafer(waferSize,die[0],die[1],xDim,yDim):
             FilteredDies.append(die)

    if FilteredDies == []:
        raise ValueError("Die positions in the File do not correspond to valid positions.")
    return FilteredDies
    
def WriteErrorLog(self, LogFileDirectory=None):

    if LogFileDirectory == None:
        LogFile = "log.log"
    else:
        LogFile = "%s/log.log" %(LogFileDirectory)

    #open(LogFile, newline='') as csvfile


def HandleConfigFile(ConfigFile, ReadWrite):
    
    output = dict()
#    ConfigFile = "%s/%s" %(os.getcwd(), ConfigFile)
    if ReadWrite:
        if os.path.exists(ConfigFile):
            rows = []
            with open(ConfigFile, newline='') as csvfile:
                csvRows = csv.reader(csvfile)
                for row in csvRows:
                    rows.append(row)
            csvfile.close()
            for row in rows:
                if not len(row) == 0:
                    if not row[0].strip()[0] == '#':
                        if len(row) == 2:
                            try:
                                output[row[0].strip()] = row[1].strip()
                            except:
                                raise ValueError("The Config File is not in the correct format!")
                        elif len(row) > 2:
                            try:
                                output[row[0].strip()] = [x.strip() for x in row[1:]]
                            except:
                                raise ValueError("The Config File is not in the correct format!")
        return output
    else:
        return True

def fprint(line):

    with open("log.txt", "a", newline="") as f:

        f.write(line)



def HandleMeasurementFile(MeasFile, ReadWrite=True):
    
    output = []
    MeasFile = "%s\%s" %(os.getcwd(), MeasFile)

    if ReadWrite:
        print(os.path.exists(MeasFile))
        if os.path.exists(MeasFile):
            rows = []
            with open(MeasFile, newline='') as csvfile:
                csvRows = csv.reader(csvfile)
                for row in csvRows:
                    rows.append(row)
            csvfile.close()
            nName = None
            VariableName = []
            Default = []
            DataType = []
            Tools = []
            nRow = 0
            n=0
            for row in rows:
                nRow = nRow +1
                if not len(row) == 0:
                    if not row[0].strip()[0] == '#':
                        if len(row) > 1:
                            if row[0].strip().lower() == "name":
                                if len(row) > 2: 
                                    raise ValueError("The Measurment File is not in the correct format! (Line: %d)" %(nRow))
                                Name = row[1].strip()
                                nName = n
                            if nName != None:
                                if nName + 1 == n and row[0].strip().lower() != "folder":
                                    raise ValueError("The Measurment File is not in the correct format! (Line: %d)" %(nRow))
                                if nName + 2 == n and row[0].strip().lower() != "tools":
                                    raise ValueError("The Measurment File is not in the correct format! (Line: %d)" %(nRow))
                                if nName + 3 == n and row[0].strip().lower() != "variablename":
                                    raise ValueError("The Measurment File is not in the correct format! (Line: %d)" %(nRow))
                                if nName + 4 == n and row[0].strip().lower() != "default":
                                    raise ValueError("The Measurment File is not in the correct format! (Line: %d)" %(nRow))
                                if nName + 5 == n and row[0].strip().lower() != "datatype":
                                    raise ValueError("The Measurment File is not in the correct format! (Line: %d)" %(nRow))

                                if row[0].strip().lower() == "folder":
                                    Folder = "".join(row[1:]).strip()
                                if row[0].strip().lower() == "tools":
                                    Tools = row[1:]
                                if row[0].strip().lower() == "variablename":
                                    VariableName = row[1:]
                                if row[0].strip().lower() == "default":
                                    Default = row[1:]
                                if row[0].strip().lower() == "datatype":
                                    DataType = row[1:]
                                    if not len(DataType) == len(Default) or not len(DataType) == len(VariableName):
                                        raise ValueError("The Measurment File is not in the correct format! (Line: %d)" %(nRow))
                                    
                                    for k in range(len(DataType)):
                                        
                                        Default[k] = ",".join(Default[k].split(";"))

                                        if Default[k].strip() != "":
                                            if DataType[k].strip().lower() == 'float':
                                                try:
                                                    Default[k] = float(Default[k])
                                                except ValueError:
                                                    raise ValueError("The Measurment File is not in the correct format! (Line: %d, Row: %d)" %(nRow,k+1))
                                            if DataType[k].strip().lower() == 'int':
                                                try:
                                                    Default[k] = int(Default[k])
                                                except ValueError:
                                                    raise ValueError("The Measurment File is not in the correct format! (Line: %d, Row: %d)" %(nRow,k+1))
                                            if DataType[k].strip().lower() == 'bool':
                                                try:
                                                    if Default[k].strip().lower() == "true":
                                                        Default[k] = True
                                                    else:
                                                        Default[k] = False
                                                except ValueError:
                                                    raise ValueError("The Measurment File is not in the correct format! (Line: %d, Row: %d)" %(nRow,k+1))

                                    output.append({"Name": Name, "Folder": Folder, "VariableName": VariableName, "Default": Default, "DataType": DataType, "Tools": Tools})
                                    nName = None
                            n=n+1
        return output
    else:
        return False


def HandleMatrixFile(MatrixFile, ReadWrite=True):
    
    MaxInput = 8
    
    inputs = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

    output = dict()
    BreakMake = []
    MakeBreak = []
    BitInputs = []
    BitOutputs = []
    NormalOutputs = []
    NormalInputs = []

    Entry = False

    if ReadWrite:
        if os.path.exists(MatrixFile):
            with open(MatrixFile, newline='') as mfile:
                lines = mfile.readlines()
            mfile.close()
            n = 0
            m = 0
            BreakMakeEnt = inputs
            MakeBreakEnt = None
            BitInputsEnt = None
            BitOutputsEnt = None
            NormalOutputsEnt = None
            NormalInputsEnt = None

            NumOfOutputs = 0

            for line in lines:
                line = line.strip()
                if not line == "":
                    if not line[0] == '#':
                        if line[0] == '$':
                            BreakMakeEnt = []
                            MakeBreakEnt = []
                            Spl = line[1:].split(',')
                            if len(Spl) > MaxInput:
                                raise ValueError("The Matrix File is not in the correct format. Error at line %d" %(n))
                            for l in range(8):
                                if l < len(Spl):
                                    if Spl[l].strip() == "MB":
                                        MakeBreakEnt.append(inputs[l])
                                    elif Spl[l].strip() == "BM":
                                        BreakMakeEnt.append(inputs[l])
                                    else:
                                        raise ValueError("The Matrix File is not in the correct format. Error at line %d" %(n))
                                else:
                                    BreakMakeEnt.append(inputs[l])
                        elif line[0] == '!':
                            NumOfOutputs = 0
                            BitOutputsEnt = []
                            NormalOutputsEnt = []
                            Spl1 = line[1:].split(';')
                            if len(Spl1) > 2 or len(Spl1) < 1:
                                raise ValueError("The Matrix File is not in the correct format. Error at line %d" %(n))
                            for Ent in Spl1:
                                if not Ent.strip() == "":
                                    Spl2 = Ent.strip().split(':')
                                    if len(Spl2) < 2:
                                        raise ValueError("The Matrix File is not in the correct format. Error at line %d" %(n))
                                    if Spl2[1].strip() == "Normal":
                                        Spl3 = Spl2[0].split(",")
                                        for Ent1 in Spl3:
                                            Spl4 = Ent1.split('-')
                                            if len(Spl4) > 1 and len(Spl4) < 3: 
                                                try:
                                                    Start = int(Spl4[0])
                                                    End = int(Spl4[1])
                                                except:
                                                    raise ValueError("The Matrix File is not in the correct format. Error at line %d" %(n))
                                                for k in range(Start,End+1,1):
                                                    if k in NormalOutputsEnt or k in BitOutputsEnt:
                                                        raise ValueError("The Matrix File is not in the correct format. Error at line %d. Multi use of outputs." %(n))
                                                    NormalOutputsEnt.append(k)
                                                    NumOfOutputs = NumOfOutputs + 1
                                            elif len(Spl4) == 1:
                                                try:
                                                    if int(Spl4[0]) in NormalOutputsEnt or int(Spl4[0]) in BitOutputsEnt:
                                                        raise ValueError("The Matrix File is not in the correct format. Error at line %d. Multi use of outputs." %(n))
                                                    NormalOutputsEnt.append(int(Spl4[0]))    
                                                    NumOfOutputs = NumOfOutputs + 1 
                                                except:
                                                    raise ValueError("The Matrix File is not in the correct format. Error at line %d" %(n))                                
                                            elif Spl4 > 2:
                                                raise ValueError("The Matrix File is not in the correct format. Error at line %d" %(n))
                                    elif Spl2[1].strip() == "Bit":
                                        Spl3 = Spl2[0].split(",")
                                        for Ent1 in Spl3:
                                            Spl4 = Ent1.split('-')
                                            if len(Spl4) > 1 and len(Spl4) < 3: 
                                                try:
                                                    Start = int(Spl4[0])
                                                    End = int(Spl4[1])
                                                except:
                                                    raise ValueError("The Matrix File is not in the correct format. Error at line %d" %(n))
                                                for k in range(Start,End+1,1):
                                                    if k in NormalOutputsEnt or k in BitOutputsEnt:
                                                        raise ValueError("The Matrix File is not in the correct format. Error at line %d. Multi use of outputs." %(n))
                                                    BitOutputsEnt.append(k)
                                            elif len(Spl4) == 1:
                                                try:
                                                    if int(Spl4[0]) in NormalOutputsEnt or int(Spl4[0]) in BitOutputsEnt:
                                                        raise ValueError("The Matrix File is not in the correct format. Error at line %d. Multi use of outputs." %(n))
                                                    BitOutputsEnt.append(int(Spl4[0]))     
                                                except:
                                                    raise ValueError("The Matrix File is not in the correct format. Error at line %d" %(n))                                
                                            elif Spl4 > 2:
                                                raise ValueError("The Matrix File is not in the correct format. Error at line %d" %(n))
                                        if len(BitOutputsEnt) > 0: 
                                            NumOfOutputs = NumOfOutputs + 2
                                    else:
                                        raise ValueError("The Matrix File is not in the correct format. Error at line %d" %(n))
                        else:
                            if BitOutputsEnt == None and NormalOutputsEnt == None:
                                raise ValueError("The Matrix File is not in the correct format. Error at line %d. Please define the Output configuration." %(n))
                            
                            Spl = line.split(",")
                            Spl2 = []

                            if not len(Spl) == NumOfOutputs:
                                raise ValueError("The Matrix File is not in the correct format. Error at line %d. The number of output/input definitions does not match. (%d vs. %d)" %(n, len(Spl), NumOfOutputs))
                            for Ent in Spl:
                                if not Ent.strip() in inputs:
                                    raise ValueError("The Matrix File is not in the correct format. Error at line %d. The Input must be from A to H." %(n))
                                Spl2.append(Ent.strip())
                            if len(BitOutputsEnt) > 0: 
                                NormalInputsEnt = Spl2[:-2]
                                BitInputsEnt = Spl2[-2:]
                            else:
                                NormalInputsEnt = Spl2
                            
                            BreakMake.append(BreakMakeEnt)
                            MakeBreak.append(MakeBreakEnt)
                            BitInputs.append(BitInputsEnt)
                            BitOutputs.append(BitOutputsEnt)
                            NormalOutputs.append(NormalOutputsEnt)
                            NormalInputs.append(NormalInputsEnt)
                            Entry = True
                            
                        n=n+1
        output = {'BreakMake': BreakMake, "MakeBreak": MakeBreak, 'BitInputs': BitInputs, 'BitOutputs': BitOutputs, 'NormalInputs': NormalInputs, 'NormalOutputs': NormalOutputs}
        
        if not Entry:
            output=None
        return output
    else:
        return True


def BitArray(Bits, High, Low):

    output = []

    nbit = np.power(2,Bits)
    for k in range(nbit):
        row = []
        for n in range(Bits):
            nk = ma.trunc((k)/(np.power(2,n)))
            if nk % 2 != 0: 
                row.append(Low)
            else:
                row.append(High)
        output.append(row)
    return output


def HandleSpecFile(SpecFile, SpecCode, ErrQu):
    
    output = []
    
    Entry = False
    if os.path.exists(SpecFile):
        rows = []
        with open(SpecFile, newline='') as csvfile:
            csvRows = csv.reader(csvfile)
            for row in csvRows:
                rows.append(row)
        csvfile.close()
        n=1 
        for row in rows:
            spec = dict()
            if not len(row) < 5:
                if not row[0].strip()[0] == '#':
                    if row[1].strip() == SpecCode.strip():
                        if len(row) == 5:
                            try:
                                spec['Name'] = row[0].strip()
                                spec['Code'] = row[1].strip()
                                spec['Target'] = float(row[2].strip())
                                spec['SpecHigh'] = float(row[3].strip())
                                spec['SpecLow'] = float(row[4].strip())
                                spec['YieldHigh'] = float(row[3].strip())
                                spec['YieldLow'] = float(row[4].strip())
                                output.append(spec)
                                Entry = True
                            except:
                                raise ValueError("The Spec/Yield definition File is not in the correct format!")
                        elif len(row) == 7:
                            try:
                                spec['Name'] = row[0].strip()
                                spec['Code'] = row[1].strip()
                                spec['Target'] = float(row[2].strip())
                                spec['SpecHigh'] = float(row[3].strip())
                                spec['SpecLow'] = float(row[4].strip())
                                spec['YieldHigh'] = float(row[5].strip())
                                spec['YieldLow'] = float(row[6].strip())
                                output.append(spec)
                                Entry = True
                            except:
                                raise ValueError("The Spec/Yield definition File is not in the correct format!")
                        else:
                            if not ErrQu == None:
                                ErrQu.put("Problem in the Spec/Yield file in line %d." %(n))
            else:
                if not ErrQu == None:
                    ErrQu.put("Problem in the Spec/Yield file in line %d." %(n))
            n+=1
    else:
        ErrQu.put("Spec File: -%s- does not exist." %(SpecFile))

    if not Entry: 
        output = None
    return output

def CreateDiePattern(pat, waferSize, xDim, yDim, centerDie):

    xNum = ma.trunc(waferSize/xDim/2)
    yNum = ma.trunc(waferSize/yDim/2)
    dies = []
    if pat == 0:
        
        dies.append([0,0])
    elif pat == 1:
        for x in range(-xNum,xNum,1):
            for y in range(-yNum,yNum,1):
                if isDieInWafer(waferSize, x, y, xDim, yDim):
                    dies.append([x,y])
    elif pat == 2:
        for x in range(-xNum,xNum,1):
            for y in range(-yNum,yNum,1):
                frx, whx = ma.modf(float(x/2))
                fry, why  = ma.modf(float(y/2))
                if frx == 0 and fry == 0:
                    if isDieInWafer(waferSize, x, y, xDim, yDim):
                        dies.append([x,y])
    elif pat == 3:
        for x in range(-xNum,xNum,1):
            for y in range(-yNum,yNum,1):
                frx, whx = ma.modf(float(x/3))
                fry, why  = ma.modf(float(y/3))
                if frx == 0 and fry == 0:
                    if isDieInWafer(waferSize, x, y, xDim, yDim):
                        dies.append([x,y])
    elif pat == 4:
        for x in range(-xNum,xNum,1):
            for y in range(-yNum,yNum,1):
                frx, whx = ma.modf(float(x/4))
                fry, why  = ma.modf(float(y/4))
                if frx == 0 and fry == 0:
                    if isDieInWafer(waferSize, x, y, xDim, yDim):
                        dies.append([x,y])
    return dies

def sortDies(dies):

    sortDies = []
    
    diesCopy = dies[:]
    while not diesCopy == []:
        
        Xmin = float('inf')
        Ymin = float('inf')
        for die in diesCopy:
            
            if die[0] < Xmin:
                Ymin = float('inf')
                Xmin = die[0]
            if die[0] <= Xmin:
                if die[1] < Ymin:
                    Ymin = die[1]
        for n in range(len(diesCopy)):
            if diesCopy[n][0] == Xmin and diesCopy[n][1] == Ymin:
                sortDies.append(diesCopy.pop(n))
                break
                
    return sortDies

def indexMove(oldDie, newDie):
    
    x = newDie[0] - oldDie[0]
    y = newDie[1] - oldDie[1]

    return {'Xmove': x, 'Ymove':y}

def CreateExternalHeader(eChar, WaferSize, XPitch, YPitch, NumXdevices, NumYdevices, DieNum, DieFile, diePat):
    eChar.ExternalHeader = []
    eChar.ExternalHeader.append('ProbeStation,Wafer.Size,%d' %(WaferSize))
    eChar.ExternalHeader.append('ProbeStation,Device.Step.X,%d' %(XPitch))
    eChar.ExternalHeader.append('ProbeStation,Device.Step.Y,%d' %(YPitch))
    eChar.ExternalHeader.append('ProbeStation,Device.Count.X,%d' %(NumXdevices))
    eChar.ExternalHeader.append('ProbeStation,Device.Count.Y,%d' %(NumYdevices))
    eChar.ExternalHeader.append('ProbeStation,Die.Count,%d' %(DieNum))
    if not DieFile == None: 
        eChar.ExternalHeader.append('ProbeStation,Die.FileName,%s' %(DieFile))
    else:
        if diePat == 0:
            eChar.ExternalHeader.append('ProbeStation,Die.Map,CurrentDie')
        elif diePat == 1:
            eChar.ExternalHeader.append('ProbeStation,Die.Map,All')
        elif diePat == 2: 
            eChar.ExternalHeader.append('ProbeStation,Die.Map,ChessBoard')
        elif diePat == 3: 
            eChar.ExternalHeader.append('ProbeStation,Die.Map,ChessBoard_Tier3')
        elif diePat == 4: 
            eChar.ExternalHeader.append('ProbeStation,Die.Map,ChessBoard_Tier4')

def rgb2gray(rgb):
    return np.dot(rgb[...,:3],[0.2989, 0.5870, 0.1140])

def matrixFromImage(x,y,path):
 
    m=int(x)
    n=int(y)

    img = Image.open(path)
    if not img.mode == 'RGB':
      img = img.convert('RGB')
    img = img.resize((n,m),Image.ANTIALIAS)

       
    gray = rgb2gray(np.array(img))    

    d=np.zeros( (m,n) )
    for b in range(m):
        for c in range(n):
            d[b][c]=gray[b][c]/255
    return d

def getDeviceResults(eChar):
    
    DataIn = eChar.StatOutValues

    newDict = dict()
    l = len(DataIn)

    newDict['DieX'] = [eChar.DieX]*l
    newDict['DieY'] = [eChar.DieY]*l
    newDict['DevX'] = [eChar.DevX]*l
    newDict['DevY'] = [eChar.DevY]*l

    for da in DataIn: 
        for name in da:
            if not name in newDict:
                newDict[name] = [None]*l

    n = 0
    for da in DataIn:
        for name in da:
            newDict[name][n] = da[name]
        n+=1

    return newDict

def calculateThresholdVoltage(I, V):
    Idif = 0
    Vth = 0
    if sum(V) > 0: 
        for n in range(1,len(I)-1,1):
            if I[n]-I[n-1]>Idif: 
                Idif = I[n]-I[n-1]
                Vth = V[n-1]

    if sum(V) < 0:

        if len(V) > 40:
            window_size = int(ma.ceil(len(V)/25))
            stride = int(window_size/2)
            V = [ np.mean(V[i:i+window_size]) for i in range(0, len(V), stride)   if i+window_size <= len(V) ]
            I = [ np.mean(I[i:i+window_size]) for i in range(0, len(I), stride)   if i+window_size <= len(I) ]  

        for n in range(1,len(I)-1,1):
            if abs(V[n]) - abs(V[n-1]) > 0 and V[n] < -0.3: 
                Rn1 = abs(V[n]/I[n])
                Rn0 = abs(V[n-1]/I[n-1])
                
                if Rn1 - Rn0 > 0:
                    Vth = V[n]
                    break

    return Vth

def createOutputData(DataIn, header):
    
    size = 1
    header1 = header[:]

    newline = 'DataName'
    for name in DataIn:
        newline = "%s,%s" %(newline,name)
        size = len(DataIn[name])
    header1.append(newline)

    data = ['DataValue']*size

    for key in DataIn:
        for n in range(len(DataIn[key])):
            if isinstance(DataIn[key][n], (float)):
                data[n] = '%s,%.5E' %(data[n],DataIn[key][n])
            elif isinstance(DataIn[key][n], (int)):
                data[n] = '%s,%d' %(data[n],DataIn[key][n])
            else:
                data[n] = '%s,%s' %(data[n],DataIn[key][n])
                
    return {'header': header1, 'data': data}

def createDeviceOutput(eChar, devRes):
    header = []

    header = eChar.Combinedheader
    header.extend(eChar.ExternalHeader)

    ret = createOutputData(devRes,header)

    data = ret['data']
    header = ret['header']

    thread = eChar.writeDataToFile(header, data, Typ='DeviceSummary', startCyc=0)

    return thread

def createDieOutput(eChar, dieRes, dieX, dieY):
    
    header = eChar.Combinedheader
    header.extend(eChar.ExternalHeader[:-3])
    thread = []

    #Calculate the average and standard deviation from the combined device Data
    dieResultAvg = dict()
    dieResultStd = dict()
    dieResultCompl = []
    for DataName in dieRes[0]:
        l = len(dieRes[DataName])
        AvgName = "%s Avg." %(DataName)
        StdName = "%s Std." %(DataName)
        dieResultAvg[AvgName] = [None]*l
        dieResultStd[StdName] = [None]*l
        dieResultCompl[DataName] = []

    n = 0
    for dev in dieRes:
        
        for name in dev:
            dieResultCompl[name].extend(dev[name])
    
    folder = eChar.getFolder()
    filename = eChar.getFilename('DieComplete')
    ret = createOutputData(dieResultCompl,header)

    data = ret['data']
    header1 = ret['header']
    thread = eChar.writeDataToFile(header1, data, Typ='DieComplete')

    for col in dieResultAvg:
        
        for n in len(dieResultAvg[col]):
            extList = []
        
            for res in dieRes:
                extList.append(res[col[:-5]][n])
            
            dieResultAvg[col][n] = getAverage(extList)
            dieResultStd[col][n] = getStdDeviation(extList)

    dieResult = {**dieResultAvg, **dieResultStd}
    
    ret = createOutputData(dieResult,header)

    data = ret['data']
    header1 = ret['header']
    
    eChar.writeDataToFile(header1, data, Typ="Die_E-char_Avg+Std")

    #Calculate and save the average and standard deviaiton from each device
    dieResultAvg = dict()
    dieResultStd = dict()
    for DataName in dieRes[0]:
        l = len(dieRes)
        AvgName = "%s Avg." %(DataName)
        StdName = "%s Std." %(DataName)
        dieResultAvg[AvgName] = [None]*l
        dieResultStd[StdName] = [None]*l

    for deviceRes in dieRes:
        
        for col in dieResultAvg:
            extList = deviceRes[col[:-5]]
            for n in range(extList):
                if extList[n] == None:
                    extList.pop[n]

            dieResultAvg[col][n] = getAverage(extList)
            dieResultStd[col][n] = getStdDeviation(extList)
            

    dieResult = {**dieResultAvg, **dieResultStd}
    
    ret = createOutputData(dieResult,header)

    data = ret['data']
    header1 = ret['header']
    
    thread = eChar.writeDataToFile(header1, data, Typ='Die_Device_Avg+Std')
          
    return thread


def CreateAverageOfDeviceResults(deviceResults):

    None

    
class MatrixChange:

    bit = None
    nbit = 0
    CurBit = 0
    lbit = 0
    useMatrix = False
    last = False
    stMatNormal = None
    stMatBit = None

    def __init__(self, inst, MatrixData, useMatrix=False):
        
        self.MatrixData = MatrixData
        self.inst = inst
        if inst == None:
            self.useMatrix = False
            self.length = 0
        else:
            self.useMatrix = useMatrix
            if MatrixData != None:
                self.length = len(MatrixData["BreakMake"])
            else:
                self.length = 0
            self.inst.initialize()  
        
        self.n = 0
        self.bit = None

    def getNormalConfiguration(self):
        return self.stMatNormal

    def getBitConfiguration(self):
        return self.stMatBit

    def setNext(self):
        
        if not self.useMatrix:
            n = self.n
            self.n = 1
            if n == 0:
                return True
            else:
                return False

        if self.last:
            self.inst.initialize()
            return False 
            
        if self.useMatrix:

            if self.last and self.bit == None:
                return False

            if self.bit != None:
                self.bit = self.bit + 1
                self.setBits(self.MatrixData['BitOutputs'][self.n-1],self.bit)
                self.stMatBit = decimalToBinary(self.bit)
            else:
                if self.n == 0:
                    self.BM = self.MatrixData["BreakMake"][self.n]
                    self.MB = self.MatrixData["MakeBreak"][self.n]
                    
                    self.inst.setMakeBreak(self.BM)
                    self.inst.setBreakMake(self.MB)
                    self.lbit = len(self.MatrixData["BitOutputs"][self.n])
                    if self.lbit > 0: 
                        self.BitAr = BitArray(self.lbit, self.MatrixData['BitInputs'][self.n][1], self.MatrixData['BitInputs'][self.n][0])
                        self.setBits(self.MatrixData['BitOutputs'][self.n],0)
                        self.bit = 1
                    for Inp, Out in zip(self.MatrixData["NormalInputs"][self.n], self.MatrixData["NormalOutputs"][self.n]):
                        self.inst.CloseCrosspoint(Inp, Out)

                else:
                    if self.BM != self.MatrixData["BreakMake"][self.n]:
                        self.inst.setMakeBreak(self.BM)
                    if self.MB != self.MatrixData["MakeBreak"][self.n]:
                        self.inst.setBreakMake(self.MB)
                    for m in range(len(self.MatrixData["NormalOutputs"][self.n-1])):
                        if not (self.MatrixData["NormalOutputs"][self.n-1][m] in self.MatrixData["NormalOutputs"][self.n]):
                            self.inst.OpenCrosspoint(self.MatrixData["NormalInputs"][self.n-1][m], self.MatrixData["NormalOutputs"][self.n-1][m])

                    for m in range(len(self.MatrixData["NormalInputs"][self.n])):
                        if self.MatrixData["NormalInputs"][self.n][m] != self.MatrixData["NormalInputs"][self.n-1][m] or self.MatrixData["NormalOutputs"][self.n][m] != self.MatrixData["NormalOutputs"][self.n-1][m]:
                            self.inst.OpenCrosspoint(self.MatrixData["NormalInputs"][self.n-1][m], self.MatrixData["NormalOutputs"][self.n-1][m])
                            self.inst.CloseCrosspoint(self.MatrixData["NormalInputs"][self.n][m], self.MatrixData["NormalOutputs"][self.n][m])
                    
                    self.lbit = len(self.MatrixData["BitOutputs"][self.n])
                    if self.lbit > 0: 
                        self.BitAr = BitArray(self.lbit, self.MatrixData['BitInputs'][self.n][1], self.MatrixData['BitInputs'][self.n][0])
                        self.setBits(self.MatrixData['BitOutputs'][self.n], 0)
                        self.bit = 0


                temp = ""
                for m in range(len(self.MatrixData["NormalOutputs"][self.n-1])):
                    temp = "%s.%s%s" %(temp,self.MatrixData["NormalInputs"][self.n-1][m], self.MatrixData["NormalOutputs"][self.n-1][m])
                self.stMatNormal = temp
                
                self.n = self.n + 1
            
            if self.n == self.length and self.bit == None:
                self.last = True

        else:
            self.last = True

        return True

    def setPrevious(self):
        
        if not self.useMatrix:
            n = self.n
            self.n = 1
            if n == 0:
                return True
            else:
                return False

        if self.last:
            self.last = False
            
        if self.useMatrix:

            if self.last and self.bit == None:
                return False

            if self.bit != None:
                self.bit = self.bit - 1
                self.setBits(self.MatrixData['BitOutputs'][self.n-1],self.bit)
                self.stMatBit = decimalToBinary(self.bit)

            else:
                if self.n == 0:
                    self.BM = self.MatrixData["BreakMake"][self.n]
                    self.MB = self.MatrixData["MakeBreak"][self.n]
                    
                    self.inst.setMakeBreak(self.BM)
                    self.inst.setBreakMake(self.MB)
                    self.lbit = len(self.MatrixData["BitOutputs"][self.n])
                    if self.lbit > 0: 
                        self.BitAr = BitArray(self.lbit, self.MatrixData['BitInputs'][self.n][1], self.MatrixData['BitInputs'][self.n][0])
                        self.setBits(self.MatrixData['BitOutputs'][self.n],0)
                        self.bit = 1
                    for Inp, Out in zip(self.MatrixData["NormalInputs"][self.n], self.MatrixData["NormalOutputs"][self.n]):
                        self.inst.CloseCrosspoint(Inp, Out)

                else:
                    if self.BM != self.MatrixData["BreakMake"][self.n]:
                        self.inst.setMakeBreak(self.BM)
                    if self.MB != self.MatrixData["MakeBreak"][self.n]:
                        self.inst.setBreakMake(self.MB)
                    for m in range(len(self.MatrixData["NormalOutputs"][self.n-1])):
                        if not (self.MatrixData["NormalOutputs"][self.n-1][m] in self.MatrixData["NormalOutputs"][self.n]):
                            self.inst.OpenCrosspoint(self.MatrixData["NormalInputs"][self.n-1][m], self.MatrixData["NormalOutputs"][self.n-1][m])

                    for m in range(len(self.MatrixData["NormalInputs"][self.n])):
                        if self.MatrixData["NormalInputs"][self.n][m] != self.MatrixData["NormalInputs"][self.n-1][m] or self.MatrixData["NormalOutputs"][self.n][m] != self.MatrixData["NormalOutputs"][self.n-1][m]:
                            self.inst.OpenCrosspoint(self.MatrixData["NormalInputs"][self.n-1][m], self.MatrixData["NormalOutputs"][self.n-1][m])
                            self.inst.CloseCrosspoint(self.MatrixData["NormalInputs"][self.n][m], self.MatrixData["NormalOutputs"][self.n][m])
                    
                    self.lbit = len(self.MatrixData["BitOutputs"][self.n])
                    if self.lbit > 0: 
                        self.BitAr = BitArray(self.lbit, self.MatrixData['BitInputs'][self.n][1], self.MatrixData['BitInputs'][self.n][0])
                        self.setBits(self.MatrixData['BitOutputs'][self.n], 0)
                        self.bit = 0

                temp = ""
                for m in range(len(self.MatrixData["NormalOutputs"][self.n-1])):
                    temp = "%s.%s%s" %(temp,self.MatrixData["NormalInputs"][self.n-1][m], self.MatrixData["NormalOutputs"][self.n-1][m])
                self.stMatNormal = temp

                self.n = self.n - 1
            
            if self.n == self.length and self.bit == None:
                self.last = True

        else:
            self.last = True

        return True

    def setBits(self, Outputs, n):
        
        if self.inst==None:
            return False 
            
        if n == 0: 
            for m in range(len(self.BitAr[n])):
                self.inst.CloseCrosspoint(self.BitAr[n][m], Outputs[m])
        else:
            for m in range(len(self.BitAr[n])):
                if self.BitAr[n][m] != self.BitAr[n-1][m]:
                    self.inst.OpenCrosspoint(self.BitAr[n-1][m], Outputs[m])
                    self.inst.CloseCrosspoint(self.BitAr[n][m], Outputs[m])
            if n >= (len(self.BitAr) - 1):
                self.bit = None
    
    def getHeader(self):
        
        head = []
        line = ""
        for n in range(len(self.MatrixData["BreakMake"])):
            m = 0
            for key, value in self.MatrixData.items():
                x = ""
                if len(value[n]) == 0:
                    x = "- "
                else: 
                    for v in value[n]:
                        x = "%s %s" %(x, v)
                if m == 0:
                    line = "%s: %s" %(key, x) 
                else:
                    line = "%s; %s: %s" %(line, key, x) 
                
                m = m+1

            head.append(line)

        return head

def decimalToBinary(n): 
    return bin(n).replace("0b","") 

def get90percOfmax(Vin, Vcomp):

    n = 0
    for v in Vin:

        if abs(v) > abs(Vcomp)*0.9:
            return n
        n = n+1
    
    return 0


def CalcOscReadValues(V, I, HorStep, tread, Vthres):
    AvgDataPoints = tread/HorStep * 0.8


    AcqLen = len(V)

    V = V[int(AcqLen/2):]
    I = I[int(AcqLen/2):]
    dp90perc = get90percOfmax(V, Vthres)
    AvgDataStart = dp90perc+tread/HorStep*0.1
    AvgDataPoints = int(tread/HorStep * 0.8)

    AvgDataStart = int(dp90perc+tread/HorStep*0.1)

    V = V[AvgDataStart:AvgDataStart+AvgDataPoints]
    I = I[AvgDataStart:AvgDataStart+AvgDataPoints]
    
    V = np.average(V)
    I = np.average(I)

    R = V/I
    C = 1/R

    return {"R": R, "V":V, "I":I, "C":C}

def fastDump(obj, file):
    p = pk.Pickler(file)
    p.fast = True
    p.dump(obj)



class ProberWrapper:

    def __getattr__(self, name):

        def method(*args):
            return None

        return (method)


def equalizeArray(data):
    maxLength = 0

    for ent in data: 
        if len(ent)>maxLength:
            maxLength = len(ent)

    m = 0
    for ent in data:

        curLen = len(ent)
        for n in range(maxLength):

            if n >= curLen:
                data[m].append(None)

        m = m+1

    return data

