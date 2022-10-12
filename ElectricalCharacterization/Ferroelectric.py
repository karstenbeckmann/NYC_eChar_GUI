'''
This file contains Ferroelectric characterization definitions from Karsten Beckmann
kbeckmann@sunypoly.edu
'''

import time as tm
import StdDefinitions as std
import DataHandling as dh
import threading as th
import math as ma
import numpy as np
import queue as qu


###########################################################################################################################

def FEretention(eChar, PulseChn, GroundChn, Vpulse, delay, tslope, twidth, tbase, MeasPoints, cycles, initPulse, area, WriteHeader=True, DoYield=True):
    
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
    initPulse:  execute initialization Pulse
    WriteHeader: Enable/Disable writing the header into overlaying summary output files
    DoYield:    perform Yield 
    """
    
    MeasType = "FEretention"
    
    eChar.localtime = tm.localtime()

    if cycles < 1: 
        cycles = 1

    CycStart = eChar.curCycle

    tmstart = 0
    #tmend = tbase/2 + tslope*2 + twidth
    duration = sum([tbase,tslope,tslope,twidth])
    tmend = duration

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


    if initPulse:
        eChar.wgfmu.addSequence(PulseChn, "posInit_1_%d" %(PulseChn), 1)
        eChar.wgfmu.addSequence(PulseChn, "negInit_2_%d" %(PulseChn), 1)
        eChar.wgfmu.addSequence(GroundChn, "Ground_3_%d" %(GroundChn), 1)
        eChar.wgfmu.addSequence(GroundChn, "Ground_3_%d" %(GroundChn), 1)
    
    if cycles > 0:
        #Pulse Channel
        eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn), "posInit_1_%d" %(PulseChn), "posInit_1_%d" %(PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
        eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Pulse_%d" %(PulseChn),"negInit_2_%d" %(PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
        eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Pulse_%d" %(PulseChn),"negInit_2_%d" %(PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
        eChar.wgfmu.addSequence(PulseChn, "Pulse_%d" %(PulseChn), cycles)

        #Ground Channel
        eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_3_%d" %(GroundChn),"Ground_3_%d" %(GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
        eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d" %(GroundChn),"Ground_3_%d" %(GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
        eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d" %(GroundChn),"Ground_3_%d" %(GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
        eChar.wgfmu.addSequence(GroundChn, "Ground_%d" %(GroundChn), cycles)

    eChar.wgfmu.synchronize()

    ret = eChar.wgfmu.executeMeasurement()
    eChar.curCycle = eChar.curCycle + cycles

    FEdata = calculateFEdata(eChar, ret, tslope, twidth, MeasPoints, initPulse, area)
    
    Pup = []
    Pdown = []

    P = []
    V = []
    J = []
    I = []

    for entry in FEdata: 

        Pup.append(entry['Scalar']['Pup'])
        Pdown.append(entry['Scalar']['Pdown'])

        P.append([])
        for x in entry['Pup']:
            P[-1].append(x*100)
            
        for x in entry['Pdown']:
            P[-1].append(x*100)

        J.append([])
        J[-1].extend(entry['dJup'])
        J[-1].extend(entry['dJdown'])

        I.append([])
        I[-1].extend(entry['dIup'])
        I[-1].extend(entry['dIdown'])


    FEdata[0]
    V.extend(FEdata[0]['Vup'])
    V.extend(FEdata[0]['Vdown'])
    
    eChar.LogData.put("%s: Pr+=%s, Pr-=%s" %(MeasType, Pup,Pdown))

    Trac = [V,*I]
    eChar.plotIVData({"Add": True, "lineStyle": '-', "lineWidth":1, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': True, 'Xlabel': "Voltage (V)", "Ylabel": 'Current (A)', 'Title': "sI-V", "MeasurementType": MeasType, "ValueName": 'sI-V'})
    
    Trac = [V,*P]
    eChar.plotIVData({"Add": True, "lineStyle": '-', "lineWidth":1, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': True, 'Xlabel': "Voltage (V)", "Ylabel": 'Polarization (uC/cm2)', 'Title': "P-V", "MeasurementType": MeasType, "ValueName": 'P-V'})
    
    Trac = [V,*J]
    eChar.plotIVData({"Add": True, "lineStyle": '-', "lineWidth":1, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': True, 'Xlabel': 'Voltage (V)', "Ylabel": 'Current Density (A/m2)', 'Title': "sJ-V", "MeasurementType": MeasType, "ValueName": 'sJ-V'})
    
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
    
    header = []
    header = eChar.wgfmu.getHeader()

    header.insert(0,"TestParameter,Measurement.Type,%s" %(MeasType))
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
    
    newline = [None]*2
    newline[0] = 'DataName'
    newline[1] = 'Dimension'

    n = 1
    for entry in FEdata: 
        
        for key, value in entry.items():
            if key != "Scalar":
                newline[0] = '%s,%s_%d' %(newline[0], key, n)
                newline[1] = '%s,%d' %(newline[1],len(value))
        n = n+1

    header.append(newline[0])
    header.append(newline[1])

    eChar.threads.append(th.Thread(target = FEDataPrepAndExport, args=(eChar, FEdata, header, MeasType)))
    eChar.threads[-1].start()

    valPup = dh.Value(eChar, Pup, 'Pup', DoYield=False, Unit='C/m2')
    valPdown = dh.Value(eChar, Pdown, 'Pdown', DoYield=False, Unit='C/m2')

    row = dh.Row([valPup, valPdown],eChar.DieX,eChar.DieY,eChar.DevX,eChar.DevY,MeasType,CycStart+1,eChar.curCycle)
    eChar.StatOutValues.addRow(row)

    if WriteHeader:
        eChar.Combinedheader.extend(eChar.EnduranceHeader)

    return True 

def FEDataPrepAndExport(eChar, data, header, cat):
    
    OutputData = []

    for n in range(len(data[0]["t"])):
        line = 'DataValue'

        for d in data:
            
            for key, value in d.items():
                if key != "Scalar":
                    line = "%s, %s" %(line, value[n])

        OutputData.append(line)

    eChar.writeDataToFile(header, OutputData, Typ=cat, startCyc=eChar.curCycle)

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
