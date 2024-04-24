'''
This file contains Ferroelectric characterization definitions from Karsten Beckmann
kbeckmann@sunypoly.edu
'''

import time as tm
import StdDefinitions as std
import StatisticalAnalysis as dh
from Exceptions import *
import threading as th
import math as ma
import numpy as np
import queue as qu
import traceback
import copy as cp


###########################################################################################################################

def FEendurance(eChar, PulseChn, GroundChn, Vpulse, delay, tslope, twidth, tbase, MeasPoints, cycles, measCycles, iterations, finalMeas, initPulse, area, WriteHeader=True, DoYield=True):
    
    """
    Measurement to characterize Ferroelectric devices with pulse IV with a PUND measurement
    please set the appropriate Channel properties beforehand via 'setChannelParameter()'
    GroundChn:  Ground channel number
    PulseChn:   Pulse channel number
    Vpulse:     Pulse voltage
    delay:      delay before measurement starts
    tslope:     rise time
    twidth:     Read Pulse width
    tbase:      base time
    MeasPoints: Number of Measurement points during Set and Reset
    cycles:     Number of cycles 
    measCycles:  Number of measasurement cycles at the start and end
    iterations:  Iteration of cycles
    finalMeas:  execute final measurment cycles
    initPulse:  execute initialization Pulse
    Area:       Area of the device (in cm2)
    WriteHeader: Enable/Disable writing the header into overlaying summary output files
    DoYield:    perform Yield 
    """
    
    maxNumberOfMeasCycles = 100
    
    eChar.updateTime()

    if cycles < 1: 
        cycles = 1

    CycStart = eChar.getCurCycle()
    tmstart = 0
    #tmend = tbase/2 + tslope*2 + twidth
    duration = sum([tbase,tslope,tslope,twidth])
    tmend = duration

    if measCycles  > cycles:
        raise B1500A_InputError("Ferroelectric Measurement: # of cycles must be larger than the measurement cycles.")
    
    if measCycles  > maxNumberOfMeasCycles:
        raise B1500A_InputError("Ferroelectric Measurement: # of measurement cycles cannot be larger than %d." %())

    eChar.startThread(target = saveEnduranceData, args=(eChar, DoYield, eChar.getMaxRowsPerFile(), eChar.getMaxDataPerPlot()))

    curCount = 0
    header = []
    stop = False
    while curCount < iterations:
        
        if eChar.checkStop():    
            return None

        ####################  with READ ##################

        eChar.wgfmu.clearLibrary()
        if twidth > 0:
            eChar.wgfmu.programRectangularPulse(PulseChn, twidth, tslope, tslope, tbase, Vpulse, 0, measure=True, mPoints=MeasPoints, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="posInit", WriteHeader=False)
        else:
            eChar.wgfmu.programTriangularPulse(PulseChn, tslope, tslope, tbase, Vpulse, 0, measure=True, mPoints=MeasPoints, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="posInit")
            
        if twidth > 0:
            eChar.wgfmu.programRectangularPulse(PulseChn, twidth, tslope, tslope, tbase, -Vpulse, 0, measure=True, mPoints=MeasPoints, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="negInit", WriteHeader=False)
        else:
            eChar.wgfmu.programTriangularPulse(PulseChn, tslope, tslope, tbase, -Vpulse, 0, measure=True, mPoints=MeasPoints, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="negInit")
            
        eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=True, mPoints=MeasPoints, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Ground")


        if initPulse and curCount == 0:
            eChar.wgfmu.addSequence(PulseChn, "posInit_1_%d" %(PulseChn), 1)
            eChar.wgfmu.addSequence(PulseChn, "negInit_2_%d" %(PulseChn), 1)
            eChar.wgfmu.addSequence(GroundChn, "Ground_3_%d" %(GroundChn), 1)
            eChar.wgfmu.addSequence(GroundChn, "Ground_3_%d" %(GroundChn), 1)
        
        if cycles > 0:
            #Pulse Channel
            eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn), "posInit_1_%d" %(PulseChn), "posInit_1_%d" %(PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Pulse_%d" %(PulseChn),"negInit_2_%d" %(PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Pulse_%d" %(PulseChn),"negInit_2_%d" %(PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.addSequence(PulseChn, "Pulse_%d" %(PulseChn), measCycles)

            #Ground Channel
            eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_3_%d" %(GroundChn),"Ground_3_%d" %(GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d" %(GroundChn),"Ground_3_%d" %(GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d" %(GroundChn),"Ground_3_%d" %(GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.addSequence(GroundChn, "Ground_%d" %(GroundChn), measCycles)

        eChar.wgfmu.synchronize()
        ret = eChar.wgfmu.executeMeasurement()

        if curCount == 0:
            header.append("Measurement,WGFMU,MeasCycles")
            header.append("Measurement,WGFMU,MeasuredCycles,%d" %(measCycles))
            header.append("Measurement,WGFMU,Iterations, %d" %(iterations))
            header = eChar.wgfmu.getHeader()
            header.append("Measurement,WGFMU,FinalMeasurement,%s" %(finalMeas))
            header.append("Measurement,Device,%s" %(eChar.getDevice()))
            header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.getLocalTime())))
            

        elif curCount != 1:
            header = []

        pulsePar = (tslope, twidth, MeasPoints, initPulse, area, measCycles)
        eChar.rawData.put({'Name': "FEendurance", 'PulseParameter': pulsePar, 'Data': ret, 'Header': header, "CurCount": curCount, 'Type':'Endurance'})
        eChar.RDstart.put(eChar.getCurCycle())
        eChar.curCycle = eChar.getCurCycle() + measCycles
        eChar.RDstop.put(eChar.getCurCycle())

        ####################  without READ ##################
        
        if cycles > measCycles:

            if eChar.checkStop():    
                return None

            eChar.wgfmu.clearLibrary()
            if twidth > 0:
                eChar.wgfmu.programRectangularPulse(PulseChn, twidth, tslope, tslope, tbase, Vpulse, 0, measure=False, mPoints=MeasPoints, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="posInit", WriteHeader=False)
            else:
                eChar.wgfmu.programTriangularPulse(PulseChn, tslope, tslope, tbase, Vpulse, 0, measure=False, mPoints=MeasPoints, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="posInit")
                
            if twidth > 0:
                eChar.wgfmu.programRectangularPulse(PulseChn, twidth, tslope, tslope, tbase, -Vpulse, 0, measure=False, mPoints=MeasPoints, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="negInit", WriteHeader=False)
            else:
                eChar.wgfmu.programTriangularPulse(PulseChn, tslope, tslope, tbase, -Vpulse, 0, measure=False, mPoints=MeasPoints, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="negInit")
                
            eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=False, mPoints=MeasPoints, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Ground")

            #Pulse Channel
            eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn), "posInit_1_%d" %(PulseChn), "posInit_1_%d" %(PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Pulse_%d" %(PulseChn),"negInit_2_%d" %(PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Pulse_%d" %(PulseChn),"negInit_2_%d" %(PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.addSequence(PulseChn, "Pulse_%d" %(PulseChn), cycles - measCycles)

            #Ground Channel
            eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_3_%d" %(GroundChn),"Ground_3_%d" %(GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d" %(GroundChn),"Ground_3_%d" %(GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d" %(GroundChn),"Ground_3_%d" %(GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.addSequence(GroundChn, "Ground_%d" %(GroundChn), cycles - measCycles)

            eChar.wgfmu.synchronize()
            eChar.wgfmu.executeMeasurement()

            if curCount == 1:
                header.append("Measurement,WGFMU,PulseCycles")
                header.append("Measurement,WGFMU,PulseCycles,%d" %(cycles - measCycles))
                header = eChar.wgfmu.getHeader()
            eChar.addCurCycle(cycles - measCycles)

        curCount+=1

    ####################  with READ ##################    

    if eChar.checkStop():    
        return None

    if finalMeas:
        eChar.wgfmu.clearLibrary()
        if twidth > 0:
            eChar.wgfmu.programRectangularPulse(PulseChn, twidth, tslope, tslope, tbase, Vpulse, 0, measure=True, mPoints=MeasPoints, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="posInit", WriteHeader=False)
        else:
            eChar.wgfmu.programTriangularPulse(PulseChn, tslope, tslope, tbase, Vpulse, 0, measure=True, mPoints=MeasPoints, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="posInit")
            
        if twidth > 0:
            eChar.wgfmu.programRectangularPulse(PulseChn, twidth, tslope, tslope, tbase, -Vpulse, 0, measure=True, mPoints=MeasPoints, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="negInit", WriteHeader=False)
        else:
            eChar.wgfmu.programTriangularPulse(PulseChn, tslope, tslope, tbase, -Vpulse, 0, measure=True, mPoints=MeasPoints, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="negInit")
            
        eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=True, mPoints=MeasPoints, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Ground")

        if cycles > 0:
            #Pulse Channel
            eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn), "posInit_1_%d" %(PulseChn), "posInit_1_%d" %(PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Pulse_%d" %(PulseChn),"negInit_2_%d" %(PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Pulse_%d" %(PulseChn),"negInit_2_%d" %(PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.addSequence(PulseChn, "Pulse_%d" %(PulseChn), measCycles)

            #Ground Channel
            eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_3_%d" %(GroundChn),"Ground_3_%d" %(GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d" %(GroundChn),"Ground_3_%d" %(GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d" %(GroundChn),"Ground_3_%d" %(GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.addSequence(GroundChn, "Ground_%d" %(GroundChn), measCycles)

        eChar.wgfmu.synchronize()
        ret = eChar.wgfmu.executeMeasurement()
        
        pulsePar = (tslope, twidth, MeasPoints, False, area, measCycles)
        eChar.rawData.put({'Name': "FEendurance", 'PulseParameter': pulsePar, 'Data': ret, 'Header': [], "CurCount": curCount, 'Type':'Endurance'})
        eChar.RDstart.put(eChar.getCurCycle())
        eChar.addCurCycle(measCycles)
        eChar.RDstop.put(eChar.getCurCycle())

    eChar.finished.put(True)

    entry = None
    while True:
        tm.sleep(0.1)
        try:
            entry = eChar.SubProcessThread.get(timeout=1)
        except qu.Empty:
            entry = None
            
        if entry != None:
            try:
                if entry['Finished'] == True:
                    break
            except:
                eChar.SubProcessThread.put(entry)
        
        if eChar.checkStop():    
            return None

    return True 

def saveEnduranceData(eChar, DoYield, MaxRowsPerFile, MaxDataPerPlot):

    #seperate data until Endurance measurement is finished
    first = True
    
    if DoYield:
        DoYield = eChar.DoYield      

    cycStart = 1
    cycleStop = 1

    finished = False

    Pup = []
    Pdown = []

    P = []
    V = []
    J = []
    I = []
    
    header = []

    while not finished or not eChar.rawData.empty():
        
        if eChar.checkStop():    
            return None

        while not eChar.finished.empty():
            finished = eChar.finished.get()
        eChar.finished.put(finished)
        
        #print("finished: ", finished, eChar.rawData.empty())
        tm.sleep(0.5)

        try:
            complData = eChar.rawData.get(True, 0.2)
            cycStart = eChar.RDstart.get(True, 0.1)
            cycleStop = eChar.RDstop.get(True, 0.1)-1

            (tslope, twidth, MeasPoints, initPulse, area, measCycles) = complData["PulseParameter"]
            
            MeasType = complData["Name"]
            ret = complData["Data"]
            curCount = complData["CurCount"]
            if complData['Header'] != []:
                header = complData['Header']
            FEdata = calculateFEdata(eChar, ret, tslope, twidth, MeasPoints, initPulse, area)                  

            PupTemp = []
            PdownTemp = []
            PTemp = []
            JTemp = []
            ITemp = []
            VTemp = []

            for n, entry in enumerate(FEdata): 

                PupTemp.append(entry['Scalar']['Pup'])
                PdownTemp.append(entry['Scalar']['Pdown'])

                maxVoltUp = eChar.dhValue([max(entry['Vup'])], 'Vup', Unit='V')
                maxVoltDown = eChar.dhValue([min(entry['Vdown'])], 'Vdown', Unit='V')
                maxCurUp = eChar.dhValue([max(entry['dIup'])], 'max. Iup', Unit='A')
                maxCurDown = eChar.dhValue([min(entry['dIdown'])], 'max. Idown', Unit='A')
                maxCurDenUp = eChar.dhValue([max(entry['dJup'])], 'max. Jup', Unit='A/m2')
                maxCurDenDown = eChar.dhValue([min(entry['dJdown'])], 'max. Jdown', Unit='A/m2')
                valPup = eChar.dhValue([entry['Scalar']['Pup']], 'Pup', Unit='uC/cm2')
                valPdown = eChar.dhValue([entry['Scalar']['Pdown']], 'Pdown', Unit='uC/cm2')
                eChar.dhAddRow([maxVoltUp, maxVoltDown, maxCurUp, maxCurDown, maxCurDenUp, maxCurDenDown, valPup, valPdown],cycleStart=cycStart+n,cycleStop=cycStart+n)


                PTemp.append([])
                for x in entry['Pup']:
                    PTemp[-1].append(x)
                    
                for x in entry['Pdown']:
                    PTemp[-1].append(x)

                JTemp.append([])
                JTemp[-1].extend(entry['dJup'])
                JTemp[-1].extend(entry['dJdown'])

                ITemp.append([])
                ITemp[-1].extend(entry['dIup'])
                ITemp[-1].extend(entry['dIdown'])

                VTemp.append([])
                VTemp[-1].extend(entry['Vup'])
                VTemp[-1].extend(entry['Vdown'])
            

            Pup.extend(PupTemp)
            Pdown.extend(PdownTemp)

            eChar.LogData.put("%s: Pr+=%s uC/cm2, Pr-=%s uC/cm2" %(MeasType, Pup,Pdown))

            Trac = []
            for n in range(len(VTemp)):
                Trac.append([VTemp[n],ITemp[n]])
            eChar.plotIVData({"Add": True, 'Row': 0, "Column": 0, "Colspan":2, "lineStyle": '-', "lineWidth":1, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': True, 'Xunit': "V", 'Xlabel': "Voltage", 'Yunit': "A", "Ylabel": 'Current', 'Title': "I-V", "ValueName": 'sI-V'})
            
            Trac = []
            for n in range(len(VTemp)):
                Trac.append([VTemp[n],PTemp[n]])

            eChar.plotIVData({"Add": True, 'Row': 1, "Column": 0,  "lineStyle": '-', "lineWidth":1, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': True, 'Xunit': "V", 'Xlabel': "Voltage", 'Yunit': "uC/cm2", "Ylabel": 'Polarization', 'Title': "P-V", "ValueName": 'P-V'})
            
            Trac = []
            for n in range(len(VTemp)):
                Trac.append([VTemp[n],JTemp[n]])
            eChar.plotIVData({"Add": True, 'Row': 1, "Column": 1,  "lineStyle": '-', "lineWidth":1, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': True, 'Xunit': "V", 'Xlabel': 'Voltage', 'Yunit': "A/cm2", "Ylabel": 'Current Density', 'Title': "J-V", "ValueName": 'sJ-V'})
        
            if ret[0]["Name"][1].find("V") != -1:
                n=1
            else:
                n=3

            Trac = [ret[n-1]['Data'],np.array(ret[n]['Data'])*(-1)]
            eChar.plotIVData({"Add": True, 'Row': 0, "Column": 0, "lineStyle": 'o', "lineWidth":1, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': True, 'Xunit': "s", 'Xlabel': 'Time', 'Yunit': "A", "Ylabel": 'Current', 'Title': "t-I", "ValueName": 't-I'})
            
            if ret[0]["Name"][1].find("V") != -1:
                n=3
            else:
                n=1
                
            Trac = [ret[n-1]['Data'],np.array(ret[n]['Data'])]
            eChar.plotIVData({"Add": True, 'Row': 1, "Column": 0,  "lineStyle": 'o', "lineWidth":1, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': True, 'Xunit': "s", 'Xlabel': 'Time', 'Yunit': "V", "Ylabel": 'Voltage', 'Title': "t-V", "ValueName": 't-V'})
            

            Trac = [[],[],[]]
            for n in range(len(PupTemp)):
                Trac[0].append(cycStart+n)
                Trac[1].append(PupTemp[n])
                Trac[2].append(PdownTemp[n])
            legend = ["Pup", "Pdown"]
            eChar.plotIVData({"Add": True, 'Row': 0, "Column": 0,  "ScatterStyle": 'o', "ScatterSize": 5, 'Yscale': 'lin',"Legend":legend, "Traces":Trac, 'Xaxis': True, 'Xlabel': '# of cycles', 'Yunit': "uC/cm2", "Ylabel": 'Polarization', 'Title': "P", "ValueName": 'P'})
            

            newline = [None]*3
            newline[0] = 'DataName'
            newline[1] = 'Units'
            newline[2] = 'Dimension'

            n = 1
            for entry in FEdata: 
                for key, value in entry.items():
                    if key != "Scalar":
                        newline[0] = '%s,%s_%d' %(newline[0], key, n)
                        unit = ""
                        if key[0] == "t":
                            unit = "s"
                        elif key[0] == "V":
                            unit = "V"
                        elif key[0:1] == "dI":
                            unit = "A"
                        elif key[0:1] == "dJ":
                            unit = "A/m2"
                        elif key[0] == "P":
                            unit = "uC/m2"                    
                        newline[1] = '%s,%s' %(newline[1], unit)
                        newline[2] = '%s,%d' %(newline[2],len(value))
                n = n+1

            headerTemp = cp.deepcopy(header)
            headerTemp.append(newline[0])
            headerTemp.append(newline[1])
            headerTemp.append(newline[2])
            eChar.startThread(target = FEDataPrepAndExport, args=(eChar, cycStart, FEdata, headerTemp))
            

        except (TypeError, ValueError, IndexError, NameError, qu.Empty) as e:
            eChar.ErrorQueue.put("E-Char FE Endurance Data Analysis, Queue Empty: %s, Finished %s, Error %s" %(eChar.rawData.empty(), finished, e))

    eChar.SubProcessThread.put({'Finished': True})
    eChar.LogData.put("FE Endurance: Finished Data Storage.")

def FEDataPrepAndExport(eChar, curCycle, data, header):
    
    OutputData = []
    for n in range(len(data[0]["t"])):
        line = 'DataValue'

        for d in data:
            
            for key, value in d.items():
                if key != "Scalar":
                    line = "%s, %s" %(line, value[n])

        OutputData.append(line)
    eChar.writeDataToFile(header, OutputData, startCyc=curCycle)

def calculateFEdata(eChar, ret, tslope, twidth, MeasPoints, initPulse, area):
    
    for entry in ret:
        if entry["Name"][0] == "t": 
            t = entry["Data"]
        elif entry["Name"][0] == "V": 
            V = entry["Data"]
        elif entry["Name"][0] == "I": 
            I = entry["Data"]

    ret = []

    if initPulse:
        t = t[2*MeasPoints:]
        V = V[2*MeasPoints:]
        I = I[2*MeasPoints:]

    dt = t[1] - t[0]

    count = len(t)/(MeasPoints*4)
    for k in range(int(count)):
        n = k*4

        tn1 = t[n*MeasPoints:(n+1)*MeasPoints-1]
        tn2 = t[(n+1)*MeasPoints:(n+2)*MeasPoints-1]
        tn3 = t[(n+2)*MeasPoints:(n+3)*MeasPoints-1]
        tn4 = t[(n+3)*MeasPoints:(n+4)*MeasPoints-1]
        In1 = I[n*MeasPoints:(n+1)*MeasPoints-1]
        In2 = I[(n+1)*MeasPoints:(n+2)*MeasPoints-1]
        In3 = I[(n+2)*MeasPoints:(n+3)*MeasPoints-1]
        In4 = I[(n+3)*MeasPoints:(n+4)*MeasPoints-1]
        Vn1 = V[n*MeasPoints:(n+1)*MeasPoints-1]
        Vn2 = V[(n+1)*MeasPoints:(n+2)*MeasPoints-1]
        Vn3 = V[(n+2)*MeasPoints:(n+3)*MeasPoints-1]
        Vn4 = V[(n+3)*MeasPoints:(n+4)*MeasPoints-1]

        Q1 = dt*sum(In1)
        Q2 = dt*sum(In2)
        Q3 = dt*sum(In3)
        Q4 = dt*sum(In4)

        dIup = np.multiply(np.subtract(In1, In2),-1)
        dIdown = np.multiply(np.subtract(In3, In4),-1)
        
        dJup = np.divide(np.array(dIup),area)
        dJdown = np.divide(np.array(dIdown),area)
        Pup = np.add.accumulate(np.multiply(np.array(dJup),dt))
        Pdown = np.add.accumulate(np.multiply(np.array(dJdown),dt))
        
        #move from C/cm2 to uC/cm2
        Pup = np.multiply(Pup,1000000)
        Pdown = np.multiply(Pdown,1000000)

        PupMax = np.max(Pup)
        PupMin = np.min(Pup)

        PupMove = PupMax-(PupMax-PupMin)/2
        Pup = np.subtract(Pup, PupMove)

        Pdown = np.array(Pdown) + (-Pdown[0] + Pup[-1])

        dPup = np.divide(np.absolute(np.subtract(Q1,Q2)),area)
        dPdown = np.divide(np.absolute(np.subtract(Q3,Q4)),area)

        #move from C/cm2 to uC/cm2
        dPup = np.multiply(dPup,1000000)
        dPdown = np.multiply(dPdown,1000000)

        time = np.subtract(np.array(tn1),tn1[0])
        
        ret.append({"t": time, "Vup": Vn1, "Vdown": Vn3, "dIup": dIup, "dIdown": dIdown, "dJup": dJup, "dJdown": dJdown, "Pup": Pup, "Pdown": Pdown, "Scalar": {"Pup": dPup, "Pdown": dPdown}})
        
    return ret

###########################################################################################################################
