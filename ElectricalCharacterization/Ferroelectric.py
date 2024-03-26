'''
This file contains Ferroelectric characterization definitions from Karsten Beckmann
kbeckmann@sunypoly.edu
'''

import time as tm
import StdDefinitions as std
import DataHandling as dh
from Exceptions import *
import threading as th
import math as ma
import numpy as np
import queue as qu
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
    Area:       Area of the device
    WriteHeader: Enable/Disable writing the header into overlaying summary output files
    DoYield:    perform Yield 
    """
    
    MeasType = "FEendurance"
    maxNumberOfMeasCycles = 100
    
    eChar.localtime = tm.localtime()

    if cycles < 1: 
        cycles = 1

    CycStart = eChar.curCycle

    tmstart = 0
    #tmend = tbase/2 + tslope*2 + twidth
    duration = sum([tbase,tslope,tslope,twidth])
    tmend = duration

    if measCycles  > cycles:
        raise B1500A_InputError("Ferroelectric Measurement: # of cycles must be larger than the measurement cycles.")
    
    if measCycles  > maxNumberOfMeasCycles:
        raise B1500A_InputError("Ferroelectric Measurement: # of measurement cycles cannot be larger than %d." %())

    waferInfo = (eChar.DieX, eChar.DieY, eChar.DevX, eChar.DevY)
    eChar.threads.append(th.Thread(target = saveEnduranceData, args=(eChar, DoYield, waferInfo, eChar.MaxRowsPerFile, eChar.MaxDataPerPlot)))
    eChar.threads[-1].start()

    curCount = 0
    header = []
    stop = False
    while curCount < iterations:

        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
        if stop:
            eChar.finished.put(True)
            break

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
            header.insert(0,"TestParameter,Measurement.Type,%s" %(MeasType))
            header.append("Measurement,WGFMU,MeasCycles")
            header.append("Measurement,WGFMU,MeasuredCycles,%d" %(measCycles))
            header.append("Measurement,WGFMU,Iterations, %d" %(iterations))
            header = eChar.wgfmu.getHeader()
            header.append("Measurement,WGFMU,FinalMeasurement,%s" %(finalMeas))
            header.append("Measurement,Device,%s" %(eChar.device))
            header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.localtime)))
            
            if not eChar.AdditionalHeader == []:
                header.extend(eChar.AdditionalHeader)
            else:
                header.append("Measurement,Type.Primary,%s" %(MeasType))

            if WriteHeader:
                eChar.Combinedheader.extend(header)

            if not eChar.ExternalHeader == []:
                header.extend(eChar.ExternalHeader)

        elif curCount != 1:
            header = []

        pulsePar = (tslope, twidth, MeasPoints, initPulse, area, measCycles)
        eChar.rawData.put({'Name': "FEendurance", 'PulseParameter': pulsePar, 'Data': ret, 'Header': header, "CurCount": curCount, 'Type':'Endurance'})
        eChar.RDstart.put(eChar.curCycle)
        eChar.curCycle = eChar.curCycle + measCycles
        eChar.RDstop.put(eChar.curCycle)

        ####################  without READ ##################

        if cycles > measCycles:

            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
            if stop:
                eChar.finished.put(True)
                break

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

            if cycles > 0:
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

            eChar.curCycle = eChar.curCycle + cycles - measCycles

        curCount+=1

    ####################  with READ ##################    

    while not eChar.Stop.empty():
        stop = eChar.Stop.get()
        if stop:
            eChar.finished.put(True)
            break

    if finalMeas:
        print("measCycles", measCycles)
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
        eChar.RDstart.put(eChar.curCycle)
        eChar.curCycle = eChar.curCycle + measCycles
        eChar.RDstop.put(eChar.curCycle)

    eChar.finished.put(True)

    while True:
        tm.sleep(0.1)
        try:
            entry = eChar.SubProcessThread.get(block=True, timeout=1)
        except qu.Empty:
            entry = None
            
        if entry != None:
            try:
                if entry['Finished'] == True:
                    break
            except:
                eChar.SubProcessThread.put(entry)
        
        while not eChar.Stop.empty():
            stop = eChar.Stop.get()

        if stop:    
            break

    return True 

def saveEnduranceData(eChar, DoYield, waferInfo, MaxRowsPerFile, MaxDataPerPlot):

    (dieX, dieY, devX, devY) = waferInfo
    #seperate data until Endurance measurement is finished
    first = True
    Typ = "Endurance"
    
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
                
        while not eChar.finished.empty():
            finished = eChar.finished.get()
        
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

                maxVoltUp = dh.Value(eChar, [max(entry['Vup'])], 'max. Vup', DoYield=False, Unit='V')
                maxVoltDown = dh.Value(eChar, [min(entry['Vdown'])], 'max. Vdown', DoYield=False, Unit='V')
                maxCurUp = dh.Value(eChar, [max(entry['dIup'])], 'max. Iup', DoYield=False, Unit='A')
                maxCurDown = dh.Value(eChar, [min(entry['dIdown'])], 'max. Idown', DoYield=False, Unit='A')
                maxCurDenUp = dh.Value(eChar, [max(entry['dJup'])], 'max. Jup', DoYield=False, Unit='A/m2')
                maxCurDenDown = dh.Value(eChar, [min(entry['dJdown'])], 'max. Jdown', DoYield=False, Unit='A/m2')
                valPup = dh.Value(eChar, [entry['Scalar']['Pup']], 'Pup', DoYield=False, Unit='C/m2')
                valPdown = dh.Value(eChar, [entry['Scalar']['Pdown']], 'Pdown', DoYield=False, Unit='C/m2')
                row = dh.Row([maxVoltUp, maxVoltDown, maxCurUp, maxCurDown, maxCurDenUp, maxCurDenDown, valPup, valPdown],dieX,dieY,devX,devY,MeasType,cycStart+n,cycStart+n)
                eChar.StatOutValues.addRow(row)

                PTemp.append([])
                for x in entry['Pup']:
                    PTemp[-1].append(x*100)
                    
                for x in entry['Pdown']:
                    PTemp[-1].append(x*100)

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

            eChar.LogData.put("%s: Pr+=%s, Pr-=%s" %(MeasType, Pup,Pdown))

            Trac = []
            for n in range(len(VTemp)):
                Trac.append([VTemp[n],ITemp[n]])
            eChar.plotIVData({"Add": True, "lineStyle": '-', "lineWidth":1, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': True, 'Xlabel': "Voltage (V)", "Ylabel": 'Current (A)', 'Title': "I-V", "MeasurementType": MeasType, "ValueName": 'sI-V'})
            
            Trac = []
            for n in range(len(VTemp)):
                Trac.append([VTemp[n],PTemp[n]])
            eChar.plotIVData({"Add": True, "lineStyle": '-', "lineWidth":1, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': True, 'Xlabel': "Voltage (V)", "Ylabel": 'Polarization (uC/cm2)', 'Title': "P-V", "MeasurementType": MeasType, "ValueName": 'P-V'})
            
            Trac = []
            for n in range(len(VTemp)):
                Trac.append([VTemp[n],JTemp[n]])
            eChar.plotIVData({"Add": True, "lineStyle": '-', "lineWidth":1, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': True, 'Xlabel': 'Voltage (V)', "Ylabel": 'Current Density (A/cm2)', 'Title': "J-V", "MeasurementType": MeasType, "ValueName": 'sJ-V'})
        
            if ret[0]["Name"][1].find("V") != -1:
                n=1
            else:
                n=3

            Trac = [ret[n-1]['Data'],np.array(ret[n]['Data'])*(-1)]
            eChar.plotIVData({"Add": True, "lineStyle": 'o', "lineWidth":1, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': True, 'Xlabel': 'Time (s)', "Ylabel": 'Current (A)', 'Title': "t-I", "MeasurementType": MeasType, "ValueName": 't-I'})
            
            if ret[0]["Name"][1].find("V") != -1:
                n=3
            else:
                n=1
                
            Trac = [ret[n-1]['Data'],np.array(ret[n]['Data'])]
            eChar.plotIVData({"Add": True, "lineStyle": 'o', "lineWidth":1, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': True, 'Xlabel': 'Time (s)', "Ylabel": 'Voltage (V)', 'Title': "t-V", "MeasurementType": MeasType, "ValueName": 't-V'})
            

            Trac = [[],[],[]]
            for n in range(len(PupTemp)):
                Trac[0] = cycStart+n
                Trac[1] = PupTemp[n]
                Trac[2] = PdownTemp[n]
            eChar.plotIVData({"Add": True, "lineStyle": 'o', "lineWidth":1, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': True, 'Xlabel': '# of cycles', "Ylabel": 'Polarization (uC/cm2)', 'Title': "P", "MeasurementType": MeasType, "ValueName": 'P'})
            

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
                            unit = "C/m2"                    
                        newline[1] = '%s,%s' %(newline[1], unit)
                        newline[2] = '%s,%d' %(newline[2],len(value))
                n = n+1

            headerTemp = cp.deepcopy(header)
            headerTemp.append(newline[0])
            headerTemp.append(newline[1])
            headerTemp.append(newline[2])


            eChar.threads.append(th.Thread(target = FEDataPrepAndExport, args=(eChar, cycStart, FEdata, headerTemp, MeasType)))
            eChar.threads[-1].start()

        except (TypeError, ValueError, IndexError, NameError, qu.Empty) as e:
            eChar.ErrorQueue.put("E-Char FE Endurance Data Analysis, Queue Empty: %s, Finished %s, Error %s" %(eChar.rawData.empty(), finished, e))

    
    
    eChar.SubProcessThread.put({'Finished': True})
    eChar.LogData.put("FE Endurance: Finished Data Storage.")

def FEDataPrepAndExport(eChar, curCycle, data, header, cat):
    
    OutputData = []

    for n in range(len(data[0]["t"])):
        line = 'DataValue'

        for d in data:
            
            for key, value in d.items():
                if key != "Scalar":
                    line = "%s, %s" %(line, value[n])

        OutputData.append(line)

    eChar.writeDataToFile(header, OutputData, Typ=cat, startCyc=curCycle)

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

        dIup = np.subtract(In1, In2)*(-1)
        dIdown = np.subtract(In3, In4)*(-1)
        
        dJup = np.array(dIup)/area
        dJdown = np.array(dIdown)/area
        Pup = np.add.accumulate(np.array(dJup)*dt)
        Pdown = np.add.accumulate(np.array(dJdown)*dt)

        PupMax = np.max(Pup)
        PupMin = np.min(Pup)

        PupMove = PupMax-(PupMax-PupMin)/2
        Pup = np.array(Pup) - PupMove

        Pdown = np.array(Pdown)+ (-Pdown[0] + Pup[-1])

        dPup = np.absolute(np.subtract(Q1,Q2))/area
        dPdown = np.absolute(np.subtract(Q3,Q4))/area

        time = np.array(tn1) - tn1[0]
        
        ret.append({"t": time, "Vup": Vn1, "Vdown": Vn3, "dIup": dIup, "dIdown": dIdown, "dJup": dJup, "dJdown": dJdown, "Pup": Pup, "Pdown": Pdown, "Scalar": {"Pup": dPup, "Pdown": dPdown}})
        
    return ret

###########################################################################################################################
