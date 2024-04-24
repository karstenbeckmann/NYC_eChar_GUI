'''
This file contains ReRAM characterization definitions from Karsten Beckmann
kbeckmann@sunypoly.edu
'''

import time as tm
import StdDefinitions as std
import StatisticalAnalysis as dh
import threading as th
import math as ma
import numpy as np
import queue as qu
import copy as cp


def FormingDCE5274A(eChar, SweepSMU, GNDSMU, GateSMU, Vform, Vgate, steps, Compl, GateCompl, hold, delay, DCSMUs, Vdc, DCcompl):

    Chns = [SweepSMU, GNDSMU, GateSMU]
    Chns.extend(DCSMUs)
    VorI = [True, True, True]
    VorI.extend([True]*len(DCSMUs))
    mode = 3

    Val = [0,0,Vgate]
    Val.extend(Vdc)

    IComp = []
    VComp = []

    step = (Vform)/(steps-1)

    if VorI:
        Xlab = "Voltage (V)"
        Ylab = "Current (A)"
    else:
        Xlab = "Current (A)"
        Ylab = "Voltage (V)"

    IComp = [Compl, Compl, GateCompl]
    VComp = [None, None, None]
    
    IComp.extend(DCcompl)
    VComp.extend([None]*len(DCcompl))
        
    out = eChar.E5274A.StaircaseSweepMeasurement(Chns, VorI, SweepSMU, 0, Vform, steps, hold, delay, Val, VComp, IComp, Mmode=mode)
    
    # fix for first value 1e101
    out['Data'][0][0] = 1e-12
    out['Data'][0][-1] = 1e-12

    Plot = [out['Data'][-1]]
    Plot.extend([out['Data'][0]])

    eChar.plotIVData({"Add": False, 'Xaxis': True, 'Yscale': 'lin',  "Traces": Plot, 'Xlabel': Xlab, "Ylabel": Ylab, 'Title': "Forming", "ValueName": 'Forming'})
            
    try: 

        header = out['Header']
        
        header.insert(0,"TestParameter,Measurement.Type,%s" %(Typ))
        header.append("Measurement,Device,%s" %(eChar.getDevice()))
        header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.getLocalTime())))
        
        DataName = "DataName, Vform, Iform, Ignd, Igate"
        Unit = "Units, V, A, A, A" 
        
        Dimension = "Dimension, %d, %d, %d, %d" %(len(out['Data'][-1]), len(out['Data'][0]), len(out['Data'][0]), len(out['Data'][0]))

        header.append(DataName)
        header.append(Unit)
        header.append(Dimension)

    except UnboundLocalError: 
        None

    data = []
    
    for n in range(len(out['Data'][0])):
        line = "DataValue, %e" %(out['Data'][-1][n])

        for m in range(len(out['Data'])-1):
            line = "%s, %e" %(line, out['Data'][m][n])
        
        data.append(line)

    eChar.writeDataToFile(header, data, Typ=Typ, startCyc=0, endCyc=1)


    
def SetDCE5274A(eChar, SweepSMU, GNDSMU, GateSMU, Vset, Vgate, steps, Compl, GateCompl, hold, delay, DCSMUs, Vdc, DCcompl):
    
    Chns = [SweepSMU, GNDSMU, GateSMU]
    VorI = [True, True, True]
    Val = [0,0,Vgate]
    if DCSMUs != None:
        Chns.extend(DCSMUs)
        VorI.extend([True]*len(DCSMUs))
        Val.extend(Vdc)
    CycStart = eChar.curCycle
    mode = 3

    IComp = []
    VComp = []

    step = (Vset)/(steps-1)

    if VorI:
        Xlab = "Voltage (V)"
        Ylab = "Current (A)"
    else:
        Xlab = "Current (A)"
        Ylab = "Voltage (V)"

    IComp = [Compl, Compl, GateCompl]
    VComp = [None, None, None]
    
    IComp.extend(DCcompl)
    VComp.extend([None]*len(DCcompl))
        
    out = eChar.E5274A.StaircaseSweepMeasurement(Chns, VorI, SweepSMU, 0, Vset, steps, hold, delay, Val, VComp, IComp, Mmode=mode)
        
    # fix for first value 1e101
    out['Data'][0][0] = 1e-12
    out['Data'][0][-1] = 1e-12
    
    Plot = [out['Data'][-1]]
    Plot.extend([out['Data'][0]])

    eChar.plotIVData({"Add": False, 'Xaxis': True, 'Yscale': 'lin',  "Traces": Plot, 'Xlabel': Xlab, "Ylabel": Ylab, 'Title': "Set", "ValueName": 'Set'})
            
    try: 

        header = out['Header']
        
        DataName = "DataName, Vreset, Ireset, Ignd, Igate"
        Unit = "Units, V, A, A, A" 
        
        Dimension = "Dimension, %d, %d, %d, %d" %(len(out['Data'][-1]), len(out['Data'][0]), len(out['Data'][0]), len(out['Data'][0]))

        header.append(DataName)
        header.append(Unit)
        header.append(Dimension)

    except UnboundLocalError: 
        None

    data = []
    
    for n in range(len(out['Data'][0])):
        line = "DataValue, %e" %(out['Data'][-1][n])

        for m in range(len(out['Data'])-1):
            line = "%s, %e" %(line, out['Data'][m][n])
        
        data.append(line)

    eChar.writeDataToFile(header, data, startCyc=CycStart, endCyc=eChar.curCycle-1)
           
    #resis = []
    #resis.append(eChar.dhValue(calcRes, name, DoYield=eChar.DoYield, Unit='ohm'))

    #row = eChar.dhAddRow(resis,eChar.DieX,eChar.DieY,eChar.DevX,eChar.DevY,Typ)
    #eChar.StatOutValues.addRow(row)

def ResetDCE5274A(eChar, SweepSMU, GNDSMU, GateSMU, Vreset, Vgate, steps, Compl, GateCompl, hold, delay, DCSMUs, Vdc, DCcompl):
    
    Chns = [SweepSMU, GNDSMU, GateSMU]
    VorI = [True, True, True]
    Val = [0,0,Vgate]
    if DCSMUs != None:
        Chns.extend(DCSMUs)
        VorI.extend([True]*len(DCSMUs))
        Val.extend(Vdc)
    CycStart = eChar.curCycle
    mode = 3

    IComp = []
    VComp = []

    step = (Vreset)/(steps-1)

    if VorI:
        Xlab = "Voltage (V)"
        Ylab = "Current (A)"
    else:
        Xlab = "Current (A)"
        Ylab = "Voltage (V)"

    IComp = [Compl, Compl, GateCompl]
    VComp = [None, None, None]
    
    IComp.extend(DCcompl)
    VComp.extend([None]*len(DCcompl))
        
    out = eChar.E5274A.StaircaseSweepMeasurement(Chns, VorI, SweepSMU, 0, Vreset, steps, hold, delay, Val, VComp, IComp, Mmode=mode)
        
    # fix for first value 1e101
    out['Data'][0][0] = 1e-12
    out['Data'][0][-1] = 1e-12
    

    Plot = [out['Data'][-1]]
    Plot.extend([out['Data'][0]])

    eChar.plotIVData({"Add": False, 'Xaxis': True, 'Yscale': 'lin',  "Traces": Plot, 'Xlabel': Xlab, "Ylabel": Ylab, 'Title': "Reset", "ValueName": 'Reset'})
            
    try: 

        header = out['Header']
        
        DataName = "DataName, Vreset, Ireset, Ignd, Igate"
        Unit = "Units, V, A, A, A" 
        
        Dimension = "Dimension, %d, %d, %d, %d" %(len(out['Data'][-1]), len(out['Data'][0]), len(out['Data'][0]), len(out['Data'][0]))

        header.append(DataName)
        header.append(Unit)
        header.append(Dimension)

    except UnboundLocalError: 
        None

    data = []
    
    for n in range(len(out['Data'][0])):
        line = "DataValue, %e" %(out['Data'][-1][n])

        for m in range(len(out['Data'])-1):
            line = "%s, %e" %(line, out['Data'][m][n])
        
        data.append(line)

    eChar.writeDataToFile(header, data, startCyc=CycStart)
           
def FormingDC(eChar, SweepSMU, GNDSMU, GateSMU, Vform, Vgate, steps, Compl, GateCompl, hold, delay, DCSMUs, Vdc, DCcompl):

    Chns = [SweepSMU, GNDSMU, GateSMU]
    Chns.extend(DCSMUs)
    VorI = [True, True, True]
    VorI.extend([True]*len(DCSMUs))
    mode = 3

    Val = [0,0,Vgate]
    Val.extend(Vdc)

    IComp = []
    VComp = []

    step = (Vform)/(steps-1)

    if VorI:
        Xlab = "Voltage (V)"
        Ylab = "Current (A)"
    else:
        Xlab = "Current (A)"
        Ylab = "Voltage (V)"

    IComp = [Compl, Compl, GateCompl]
    VComp = [None, None, None]
    
    IComp.extend(DCcompl)
    VComp.extend([None]*len(DCcompl))
    print("here2")
    out = eChar.B1500A.StaircaseSweepMeasurement(Chns, VorI, SweepSMU, 0, Vform, steps, hold, delay, Val, VComp, IComp, Mmode=mode)

    # fix for first value 1e101
    out['Data'][0][0] = 1e-12
    out['Data'][0][-1] = 1e-12

    Plot = [out['Data'][-1]]
    Plot.extend([out['Data'][0]])

    eChar.plotIVData({"Add": False, 'Xaxis': True, 'Yscale': 'lin',  "Traces": Plot, 'Xlabel': Xlab, "Ylabel": Ylab, 'Title': "Forming", "ValueName": 'Forming'})
            
    try: 

        header = out['Header']
        
        DataName = "DataName, Vform, Iform, Ignd, Igate"
        Unit = "Units, V, A, A, A" 
        
        Dimension = "Dimension, %d, %d, %d, %d" %(len(out['Data'][-1]), len(out['Data'][0]), len(out['Data'][0]), len(out['Data'][0]))

        header.append(DataName)
        header.append(Unit)
        header.append(Dimension)

    except UnboundLocalError: 
        None

    data = []
    
    for n in range(len(out['Data'][0])):
        line = "DataValue, %e" %(out['Data'][-1][n])

        for m in range(len(out['Data'])-1):
            line = "%s, %e" %(line, out['Data'][m][n])
        
        data.append(line)

    V = np.array(out['Data'][-1])
    I = np.array(out['Data'][0])
    R = np.divide(V,I)

    l = len(out['Data'][-1])

    Idif = np.diff(I[:int(l/2)])
    indMax = np.argmax(Idif)
    Vform = V[indMax]

    HRS = abs(R[2])
    LRS = abs(R[-2])

    val1 = eChar.dhValue(Vform, "Vform", Unit="V")
    val2 = eChar.dhValue(HRS, "FirstHRS", Unit="V")
    val3 = eChar.dhValue(LRS, "FirstLRS", Unit="V")
    
    eChar.dhAddRow([val1, val2, val3])

    eChar.writeDataToFile(header, data, startCyc=0, endCyc=1)
    
def SetDC(eChar, SweepSMU, GNDSMU, GateSMU, Vset, Vgate, steps, Compl, GateCompl, hold, delay, DCSMUs, Vdc, DCcompl):

    
    Chns = [SweepSMU, GNDSMU, GateSMU]
    VorI = [True, True, True]
    Val = [0,0,Vgate]
    if DCSMUs != None:
        Chns.extend(DCSMUs)
        VorI.extend([True]*len(DCSMUs))
        Val.extend(Vdc)
    CycStart = eChar.curCycle
    mode = 3

    IComp = []
    VComp = []

    step = (Vset)/(steps-1)

    if VorI:
        Xlab = "Voltage (V)"
        Ylab = "Current (A)"
    else:
        Xlab = "Current (A)"
        Ylab = "Voltage (V)"

    IComp = [Compl, Compl, GateCompl]
    VComp = [None, None, None]
    
    IComp.extend(DCcompl)
    VComp.extend([None]*len(DCcompl))
        
    out = eChar.B1500A.StaircaseSweepMeasurement(Chns, VorI, SweepSMU, 0, Vset, steps, hold, delay, Val, VComp, IComp, Mmode=mode)
        
    # fix for first value 1e101
    out['Data'][0][0] = 1e-12
    out['Data'][0][-1] = 1e-12
    
    Plot = [out['Data'][-1]]
    Plot.extend([out['Data'][0]])

    eChar.plotIVData({"Add": False, 'Xaxis': True, 'Yscale': 'lin',  "Traces": Plot, 'Xlabel': Xlab, "Ylabel": Ylab, 'Title': "Set",  "ValueName": 'Set'})
            
    try: 

        header = out['Header']
                
        DataName = "DataName, Vreset, Ireset, Ignd, Igate"
        Unit = "Units, V, A, A, A" 
        
        Dimension = "Dimension, %d, %d, %d, %d" %(len(out['Data'][-1]), len(out['Data'][0]), len(out['Data'][0]), len(out['Data'][0]))

        header.append(DataName)
        header.append(Unit)
        header.append(Dimension)

    except UnboundLocalError: 
        None

    data = []
    
    for n in range(len(out['Data'][0])):
        line = "DataValue, %e" %(out['Data'][-1][n])

        for m in range(len(out['Data'])-1):
            line = "%s, %e" %(line, out['Data'][m][n])
        
        data.append(line)

    V = np.array(out['Data'][-1])
    I = np.array(out['Data'][0])
    R = np.divide(V,I)

    l = len(out['Data'][-1])

    Idif = np.diff(I[:int(l/2)])
    indMax = np.argmax(Idif)
    Vset = V[indMax]

    HRS = abs(R[2])
    LRS = abs(R[-2])

    val1 = eChar.dhValue(Vset, "Vset", Unit="V")
    val2 = eChar.dhValue(HRS, "HRS", Unit="V")
    val3 = eChar.dhValue(LRS, "LRS", Unit="V")
    
    eChar.dhAddRow([val1, val2, val3])

    eChar.writeDataToFile(header, data, startCyc=CycStart, endCyc=eChar.curCycle-1)
           
    #resis = []
    #resis.append(eChar.dhValue(calcRes, name, DoYield=eChar.DoYield, Unit='ohm'))

    #row = eChar.dhAddRow(resis,Typ)

def ResetDC(eChar, SweepSMU, GNDSMU, GateSMU, Vreset, Vgate, steps, Compl, GateCompl, hold, delay, DCSMUs, Vdc, DCcompl):
    
    Chns = [SweepSMU, GNDSMU, GateSMU]
    VorI = [True, True, True]
    Val = [0,0,Vgate]
    if DCSMUs != None:
        Chns.extend(DCSMUs)
        VorI.extend([True]*len(DCSMUs))
        Val.extend(Vdc)
    CycStart = eChar.curCycle
    mode = 3

    IComp = []
    VComp = []

    step = (Vreset)/(steps-1)

    if VorI:
        Xlab = "Voltage (V)"
        Ylab = "Current (A)"
    else:
        Xlab = "Current (A)"
        Ylab = "Voltage (V)"

    IComp = [Compl, Compl, GateCompl]
    VComp = [None, None, None]
    
    IComp.extend(DCcompl)
    VComp.extend([None]*len(DCcompl))
        
    out = eChar.B1500A.StaircaseSweepMeasurement(Chns, VorI, SweepSMU, 0, Vreset, steps, hold, delay, Val, VComp, IComp, Mmode=mode)
        
    # fix for first value 1e101
    out['Data'][0][0] = 1e-12
    out['Data'][0][-1] = 1e-12
    

    Plot = [out['Data'][-1]]
    Plot.extend([out['Data'][0]])

    eChar.plotIVData({"Add": False, 'Xaxis': True, 'Yscale': 'lin',  "Traces": Plot, 'Xlabel': Xlab, "Ylabel": Ylab, 'Title': "Reset", "ValueName": 'Reset'})
            
    try: 
        header = out['Header']
        
        DataName = "DataName, Vreset, Ireset, Ignd, Igate"
        Unit = "Units, V, A, A, A" 
        
        Dimension = "Dimension, %d, %d, %d, %d" %(len(out['Data'][-1]), len(out['Data'][0]), len(out['Data'][0]), len(out['Data'][0]))

        header.append(DataName)
        header.append(Unit)
        header.append(Dimension)

    except UnboundLocalError: 
        None

    data = []
    
    for n in range(len(out['Data'][0])):
        line = "DataValue, %e" %(out['Data'][-1][n])

        for m in range(len(out['Data'])-1):
            line = "%s, %e" %(line, out['Data'][m][n])
        
        data.append(line)

    V = np.array(out['Data'][-1])
    I = np.array(out['Data'][0])
    R = np.divide(V,I)

    l = len(out['Data'][-1])

    Idif = np.diff(I[:int(l/2)])
    indMax = np.argmin(Idif)
    Vreset = V[indMax]

    HRS = abs(R[2])
    LRS = abs(R[-2])

    val1 = eChar.dhValue(Vreset, "Vreset", Unit="V")
    val2 = eChar.dhValue(HRS, "HRS", Unit="V")
    val3 = eChar.dhValue(LRS, "LRS", Unit="V")
    
    eChar.dhAddRow([val1, val2, val3])

    eChar.writeDataToFile(header, data, startCyc=CycStart)
           
           
def PulseRead(eChar, PulseChn, GroundChn, Vread, delay, tread, tbase, WriteHeader=True):
    """
    Recommendation: Pulsed Forming, forming times should be in the ms regime
    please set the appropriate Channel properties beforehand via 'setChannelParameter()'
    GroundChn: Ground channel number
    PulseChn:  Pulse channel number
    Vread:     Read Voltage (V)
    delay:     delay before measurement starts (s)
    trise:     Forming rise time (s)
    tfall:     Forming fall time (s)
    twidth:    Forming pulse width (s)
    tbase:     base time   (s)
    WriteHeader: Enable/Disable writing the header into overlaying summary output files
    """
    tfall = tread * 0.1
    trise = tread * 0.1
    eChar.updateTime()

    tmstart = tbase/2 + trise*2
    tmend = tbase/2 + trise + tread-tfall
    duration = tread+tbase+tfall+trise
    
    print("PulseRead")

    eChar.wgfmu.clearLibrary()

    eChar.wgfmu.programRectangularPulse(PulseChn, tread, trise, tfall, tbase, Vread, 0, count=1, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=True, Name="Read")
    eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, count=1, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=True, Name="Ground")
    
    print("1")
    eChar.wgfmu.synchronize()
    print("2")
    ret = eChar.wgfmu.executeMeasurement()
    print("3")
    
    resistance = ret[1]['Data'][0]/-ret[3]['Data'][0]

    header = []
    header = eChar.wgfmu.getHeader()

    header.append("Measurement,Device,%s" %(eChar.getDevice()))
    header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.getLocalTime())))
    
    header.append('MeasurmentResult,Resistance,%f' %(resistance))

    newline = [None]*2
    newline[0] = 'DataName, Cycle'
    newline[1] = 'Dimension, %d' %(ret[0]['Length'])

    for x in range(4):
        newline[0] = '%s,%s' %(newline[0],ret[x]['Name'])
        newline[1] = '%s,%s' %(newline[1],ret[x]['Length'])

    newline[0] = '%s,%s' %(newline[0],'R')
    newline[1] = '%s,%s' %(newline[1],ret[3]['Length'])

    data =  [ret[1]['Data'],ret[3]['Data']]

    dataStr = "DataValue, %d" %(eChar.curCycle)
    
    for n in range(len(ret)):
        if n==3:
            dataStr = "%s,%.2E" %(dataStr,-ret[n]['Data'][0])
        else:
            dataStr = "%s,%.2E" %(dataStr,ret[n]['Data'][0])

    dataStr = "%s,%.2E" %(dataStr,resistance)

    header.extend(newline)

    eChar.writeDataToFile(header, [dataStr])
           
    res = {'Header':header, 'IVdata':data}


    resis = eChar.dhValue(resistance, 'Resistance', Unit='ohm')
    row = eChar.dhAddRow([resis],eChar.curCycle)


    eChar.curCycle = eChar.curCycle+1

    return res

###########################################################################################################################


###########################################################################################################################
    
def PulseForming(eChar, PulseChn, GroundChn, Vform, delay, trise, tfall, twidth, tbase, MeasPoints, read=True, tread=10e-6, Vread=-0.2, SMUs=None, Vdc=None, DCcompl=None, WriteHeader=True):
    """
    Pulsed Forming, forming times should be in the ms regime
    please set the appropriate Channel properties beforehand via 'setChannelParameter()'
    GroundChn: Ground channel number
    PulseChn:  Pulse channel number
    Vform:     Forming Voltage (V)
    delay:     delay before measurement starts (s)
    trise:     Forming rise time (s)
    tfall:     Forming fall time (s)
    twidth:    Forming pulse width (s)
    tbase:     base time   (s)
    MeasPoints:Number of Measurement points during Set and Reset
    read:      Read enable, True for enalbed, False for disabled
    tread:     Read pulse time, (read pulse rise and fall time are 10% of tread), minimum tread is 1us. 
    Vread:     Read voltage (V)
    SMUs:      Array of SMU's
    Vdc:       Array of DC voltages    (V)
    DCcompl:   Array of DC comliances (A)
    WriteHeader: Enable/Disable writing the header into overlaying summary output files
    """
    
    eChar.updateTime()
    tfallread = tread * 0.1
    triseread = tread * 0.1

    tmstart = tbase/2 + tfallread
    tmend = tbase/2 + tfallread + tread
    duration = sum([tbase,tfallread,triseread,tread])
    

    eChar.wgfmu.clearLibrary()

    if read:
        eChar.wgfmu.programRectangularPulse(PulseChn, tread, tfallread, triseread, tbase, Vread, 0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Read", WriteHeader=False)
        eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Ground", WriteHeader=False)

    durationF = sum([trise,twidth,tfall,tbase])
    endTime = tbase/2+trise+tfall+twidth
    if twidth == 0: 
        eChar.wgfmu.programTriangularPulse(PulseChn, trise, tfall, tbase, Vform, 0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Form")
        eChar.wgfmu.programGroundChn(GroundChn, durationF, Vg=0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Ground")
    else: 
        eChar.wgfmu.programRectangularPulse(PulseChn, twidth, trise, tfall, tbase, Vform, 0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Form")
        eChar.wgfmu.programGroundChn(GroundChn, durationF, Vg=0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Ground")

    paItstart = 1

    if read:
        eChar.wgfmu.addSequence(PulseChn, "Read_1_%d" %(PulseChn), 1)
        eChar.wgfmu.addSequence(GroundChn, "Ground_2_%d" %(GroundChn), 1)
        paItstart = 3

    eChar.wgfmu.addSequence(PulseChn, "Form_%d_%d" %(paItstart,PulseChn), 1)
    eChar.wgfmu.addSequence(GroundChn, "Ground_%d_%d" %(paItstart+1,GroundChn), 1)

    if read:
        eChar.wgfmu.addSequence(PulseChn, "Read_1_%d" %(PulseChn), 1)
        eChar.wgfmu.addSequence(GroundChn, "Ground_2_%d" %(GroundChn), 1)
    
    eChar.wgfmu.synchronize()

    for n in range(eChar.maxExecutions):

        ret = eChar.wgfmu.executeMeasurement()
        if len(ret[1]['Data']) == len(ret[3]['Data']) and len(ret[0]['Data']) == len(ret[1]['Data']) and len(ret[2]['Data']) == len(ret[3]['Data']):
            break


    #can be used but 
    SepData = getSepDataPulseIV(eChar, ret, MeasPoints, read, True, False)

    header = []
    header = eChar.wgfmu.getHeader()

    if read:
        header.append('MeasurmentResult,HRS,%f' %(SepData['HRS'][0]))
        header.append('MeasurmentResult,LRS,%f' %(SepData['LRS'][0]))
    header.append('MeasurmentResult,AvgImaxForm,%f' %(SepData['ImaxSet'][0]))

    if WriteHeader:
        eChar.extendHeader("Combined", header)


    newline = [None]*2
    newline[0] = 'DataName, Cycle'
    newline[1] = 'Dimension, %d' %(ret[0]['Length'])

    for x in range(4):
        newline[0] = '%s,%s' %(newline[0],ret[x]['Name'])
        newline[1] = '%s,%s' %(newline[1],ret[x]['Length'])
    
    header.extend(newline)
    
    PulseIVDataPrepAndExport(eChar, SepData, header, eChar.curCycle, MeasPoints, 'PulseForming')

    res = {'Header':header, 'IVdata': SepData['IVdata'], 'Vform':SepData['Vset'], 'LRS':SepData['LRS'], 'HRS':SepData['HRS'], 'ImaxSet': SepData['ImaxSet']}

    if ret[3]["Name"][0].lower() == "i":
        Trac = [SepData['IVdata'][1],SepData['IVdata'][3]] 
    else:
        Trac = [SepData['IVdata'][3],SepData['IVdata'][1]] 
        
    eChar.plotIVData({"Traces":Trac, 'Xaxis': True, 'Xlabel': 'Voltage (V)', "Ylabel": 'Current (A)', 'Title': "Forming", "ValueName": 'IV'})
    HRS = eChar.dhValue(eChar, SepData['HRS'][0], 'FirstHRS', Unit='ohm')
    LRS = eChar.dhValue(eChar, SepData['LRS'][0], 'FirstLRS', Unit='ohm')
    ImaxForm = eChar.dhValue(eChar, SepData['ImaxSet'][0], 'ImaxForm', Unit='A')
    Vform = eChar.dhValue(eChar, SepData['Vset'][0], 'Vform', Unit='V')
    
    row = eChar.dhAddRow([HRS,LRS,ImaxForm,Vform], eChar.curCycle,eChar.curCycle)

    eChar.curCycle = eChar.curCycle+1
    return res

    
###########################################################################################################################

def PulseSet(eChar, PulseChn, GroundChn, Vform, delay, trise, tfall, twidth, tbase, MeasPoints, read=True,  initialRead=True, tread=10e-6, Vread=-0.2, SMUs=None, Vdc=None, DCcompl=None,WriteHeader=True):
    
    """
    Pulsed Set, forming times should be in the ms regime
    please set the appropriate Channel properties beforehand via 'setChannelParameter()'
    GroundChn: Ground channel number
    PulseChn:  Pulse channel number
    Vset:      Set Voltage (V)
    delay:     delay before measurement starts (s)
    trise:     Set rise time (s)
    tfall:     Set fall time (s)
    twidth:    Set pulse width (s)
    tbase:     base time   (s)
    MeasPoints:Number of Measurement points during Set and Reset
    read:      Read enable, True for enalbed, False for disabled
    tread:     Read pulse time, (read pulse rise and fall time are 10% of tread), minimum tread is 1us. 
    Vread:     Read voltage (V)
    initialRead:Starts an initial Read before the Set operation
    SMUs:      Array of SMU's
    Vdc:       Array of DC voltages    (V)
    DCcompl:   Array of DC comliances (A)
    WriteHeader: Enable/Disable writing the header into overlaying summary output files
    """
    
    eChar.updateTime()
    tfallread = tread * 0.1
    triseread = tread * 0.1

    tmstart = tbase/2 + tfallread
    tmend = tbase/2 + tfallread + tread
    duration = sum([tbase,tfallread,triseread,tread])
    
    eChar.wgfmu.clearLibrary()

    if read:
        eChar.wgfmu.programRectangularPulse(PulseChn, tread, tfallread, triseread, tbase, Vread, 0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Read", WriteHeader=False)
        eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Ground", WriteHeader=False)

    durationF = sum([trise,twidth,tfall,tbase])
    endTime = tbase/2+trise+tfall+twidth
    if twidth == 0: 
        eChar.wgfmu.programTriangularPulse(PulseChn, trise, tfall, tbase, Vform, 0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Set")
        eChar.wgfmu.programGroundChn(GroundChn, durationF, Vg=0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Ground")
    else: 
        eChar.wgfmu.programRectangularPulse(PulseChn, twidth, trise, tfall, tbase, Vform, 0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Set")
        eChar.wgfmu.programGroundChn(GroundChn, durationF, Vg=0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Ground")

    paItstart = 3

    if read and initialRead:
        eChar.wgfmu.addSequence(PulseChn, "Read_1_%d" %(PulseChn), 1)
        eChar.wgfmu.addSequence(GroundChn, "Ground_2_%d" %(GroundChn), 1)

    eChar.wgfmu.addSequence(PulseChn, "Set_%d_%d" %(paItstart,PulseChn), 1)
    eChar.wgfmu.addSequence(GroundChn, "Ground_%d_%d" %(paItstart+1,GroundChn), 1)

    if read:
        eChar.wgfmu.addSequence(PulseChn, "Read_1_%d" %(PulseChn), 1)
        eChar.wgfmu.addSequence(GroundChn, "Ground_2_%d" %(GroundChn), 1)
    
    eChar.wgfmu.synchronize()
    
    ret = eChar.wgfmu.executeMeasurement()
    
    #can be used but 
    SepData = getSepDataPulseIV(eChar, ret, MeasPoints, read, initialRead, False)
    header = eChar.wgfmu.getHeader()


    if read:
        if initialRead:
            header.append('MeasurmentResult,HRS,%f' %(SepData['HRS'][0]))
        header.append('MeasurmentResult,LRS,%f' %(SepData['LRS'][0]))
    
    header.append('MeasurmentResult,AvgImaxSet,%f' %(SepData['ImaxSet'][0]))


    if WriteHeader:
        eChar.extendHeader("Combined", header)

    newline = [None]*2
    newline[0] = 'DataName, Cycle'
    newline[1] = 'Dimension, %d' %(ret[0]['Length'])

    for x in range(4):
        newline[0] = '%s,%s' %(newline[0],ret[x]['Name'])
        newline[1] = '%s,%s' %(newline[1],ret[x]['Length'])
    
    header.extend(newline)

    PulseIVDataPrepAndExport(eChar, SepData, header, eChar.curCycle, MeasPoints, 'PulseSet')

    res = {'Header':header, 'IVdata': SepData['IVdata'], 'LRS':SepData['LRS'], 'HRS':SepData['HRS'], 'ImaxSet': SepData['ImaxSet']}

    if ret[3]["Name"][0].lower() == "i":
        Trac = [SepData['IVdata'][1],SepData['IVdata'][3]] 
    else:
        Trac = [SepData['IVdata'][3],SepData['IVdata'][1]] 
    eChar.plotIVData({"Traces":Trac, 'Xaxis': True, 'Xlabel': 'Voltage (V)', "Ylabel": 'Current (A)', 'Title': "Set", "ValueName": 'IV'})

    LRS = eChar.dhValue(SepData['LRS'][0], 'LRS', Unit='ohm')
    ImaxSet = eChar.dhValue(SepData['ImaxSet'][0], 'ImaxSet', Unit='A')
    Vset = eChar.dhValue(SepData['Vset'][0], 'Vset', Unit='V')

    if initialRead:
        HRS = eChar.dhValue(SepData['HRS'][0], 'HRS', Unit='ohm')
        row = eChar.dhAddRow([HRS,LRS,ImaxSet,Vset],eChar.curCycle,eChar.curCycle)
    else:
        row = eChar.dhAddRow([LRS,ImaxSet,Vset],eChar.curCycle,eChar.curCycle)

    eChar.curCycle = eChar.curCycle+1

    return res

###########################################################################################################################

def PulseReset(eChar, PulseChn, GroundChn, Vform, delay, trise, tfall, twidth, tbase, MeasPoints, read=True,initialRead=True, tread=10e-6, Vread=-0.2, SMUs=None, Vdc=None, DCcompl=None,WriteHeader=True):
    """
    Pulsed Set, forming times should be in the ms regime
    please set the appropriate Channel properties beforehand via 'setChannelParameter()'
    GroundChn: Ground channel number
    PulseChn:  Pulse channel number
    Vreset:    Reset Voltage (V)
    delay:     delay before measurement starts (s)
    trise:     Reset rise time (s)
    tfall:     Reset fall time (s)
    twidth:    Reset pulse width (s)
    tbase:     base time   (s)
    MeasPoints:Number of Measurement points during Set and Reset
    read:      Read enable, True for enalbed, False for disabled
    tread:     Read pulse time, (read pulse rise and fall time are 10% of tread), minimum tread is 1us. 
    Vread:     Read voltage (V)
    initialRead:Sets a read before the measurement
    SMUs:      Array of SMU's
    Vdc:       Array of DC voltages    (V)
    DCcompl:   Array of DC comliances (A)
    WriteHeader: Enable/Disable writing the header into overlaying summary output files
    """

    eChar.updateTime()
    tfallread = tread * 0.1
    triseread = tread * 0.1

    tmstart = tbase/2 + tfallread
    tmend = tbase/2 + tfallread + tread
    duration = sum([tbase,tfallread,triseread,tread])
    
    eChar.wgfmu.clearLibrary()

    if read and initialRead:
        eChar.wgfmu.programRectangularPulse(PulseChn, tread, tfallread, triseread, tbase, Vread, 0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Read", WriteHeader=False)
        eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Ground", WriteHeader=False)
        paReadID = 1

    durationF = sum([trise,twidth,tfall,tbase])
    endTime = tbase/2+trise+tfall+twidth
    if twidth == 0: 
        eChar.wgfmu.programTriangularPulse(PulseChn, trise, tfall, tbase, Vform, 0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Form")
        eChar.wgfmu.programGroundChn(GroundChn, durationF, Vg=0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Ground")
    else: 
        eChar.wgfmu.programRectangularPulse(PulseChn, twidth, trise, tfall, tbase, Vform, 0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Form")
        eChar.wgfmu.programGroundChn(GroundChn, durationF, Vg=0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Ground")

    paItstart = 1

    if read and not initialRead:
        eChar.wgfmu.programRectangularPulse(PulseChn, tread, tfallread, triseread, tbase, Vread, 0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Read", WriteHeader=False)
        eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Ground", WriteHeader=False)
        paItstart = 1
        paReadID = 3

    if read and initialRead:
        eChar.wgfmu.addSequence(PulseChn, "Read_%d_%d" %(paReadID,PulseChn), 1)
        eChar.wgfmu.addSequence(GroundChn, "Ground_%d_%d" %(paReadID+1,GroundChn), 1)
        paItstart = 3

    eChar.wgfmu.addSequence(PulseChn, "Form_%d_%d" %(paItstart,PulseChn), 1)
    eChar.wgfmu.addSequence(GroundChn, "Ground_%d_%d" %(paItstart+1,GroundChn), 1)

    if read:
        eChar.wgfmu.addSequence(PulseChn, "Read_%d_%d" %(paReadID,PulseChn), 1)
        eChar.wgfmu.addSequence(GroundChn, "Ground_%d_%d" %(paReadID+1,GroundChn), 1)
    
    eChar.wgfmu.synchronize()
    
    ret = eChar.wgfmu.executeMeasurement()
    #can be used but 
    SepData = getSepDataPulseIV(eChar, ret, MeasPoints, read, initialRead, True)
    header = eChar.wgfmu.getHeader()

    if read:
        if initialRead:
            header.append('MeasurmentResult,HRS,%f' %(SepData['LRS'][0]))
        header.append('MeasurmentResult,LRS,%f' %(SepData['HRS'][0]))
    
    header.append('MeasurmentResult,AvgImaxReset,%f' %(SepData['ImaxReset'][0]))

    if WriteHeader:
        eChar.extendHeader("Combined", header)

    newline = [None]*2
    newline[0] = 'DataName, Cycle'
    newline[1] = 'Dimension, %d' %(ret[0]['Length'])

    for x in range(4):
        newline[0] = '%s,%s' %(newline[0],ret[x]['Name'])
        newline[1] = '%s,%s' %(newline[1],ret[x]['Length'])
    
    header.extend(newline)

    PulseIVDataPrepAndExport(eChar, SepData, header, eChar.curCycle, MeasPoints, 'PulseReset')

    res = {'Header':header, 'IVdata': SepData['IVdata'], 'LRS':SepData['LRS'], 'HRS':SepData['HRS'], 'ImaxReset': SepData['ImaxReset']}


    if ret[3]["Name"][0].lower() == "i":
        Trac = [SepData['IVdata'][1],SepData['IVdata'][3]] 
    else:
        Trac = [SepData['IVdata'][3],SepData['IVdata'][1]] 
    eChar.plotIVData({"Traces":Trac, 'Xaxis': True, 'Xlabel': 'Voltage (V)', "Ylabel": 'Current (A)', 'Title': "Reset", "ValueName": 'IV'})
    
    Trac = [SepData['IVdata'][2],SepData['IVdata'][3]]
    eChar.plotIVData({"Traces":Trac, 'Xaxis': True, 'Xlabel': 'Time (s)', "Ylabel": 'Current (A)', 'Title': "Reset: t-I", "ValueName": 'tI'})
    
    HRS = eChar.dhValue(SepData['HRS'][0], 'HRS', Unit='ohm')
    ImaxReset = eChar.dhValue(SepData['ImaxReset'][0], 'ImaxReset', Unit='A')
    Vreset = eChar.dhValue(SepData['Vreset'][0], 'Vreset', Unit='V')

    if initialRead:
        LRS = eChar.dhValue(SepData['LRS'][0], 'LRS', Unit='ohm')
        row = eChar.dhAddRow([HRS,LRS,ImaxReset,Vreset],eChar.curCycle,eChar.curCycle)
    else:
        row = eChar.dhAddRow([HRS,ImaxReset,Vreset],eChar.curCycle,eChar.curCycle)
    eChar.curCycle = eChar.curCycle+1

    return res

###########################################################################################################################


def PulseIV(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, MeasPoints, count, read=True, initialRead=True, tread=10e-6, Vread=-0.2, SMUs=None, Vdc=None, DCcompl=None,WriteHeader=True,Primary=True):
    """
    Standard measurement for PulseIV up to 100 cycles
    please set the appropriate Channel properties beforehand via 'setChannelParameter()'
    GroundChn: Ground channel number
    PulseChn:  Pulse channel number
    Vset:      Set Voltage
    Vreset:    Reset Voltage
    delay:     delay before measurement starts
    triseS:    Set rise time
    tfallS:    Set fall time
    twidthS:   Set pulse width
    triseR:    Reset rise time`
    tfallR:    Reset fall time
    twidthR:   Reset pulse width
    tbase:     base time
    MeasPoints:Number of Measurement points during Set and Reset
    Count:     Number of repetitions (maximum of 100)
    read:      Read enable, True for enalbed, False for disabled
    tread:     Read pulse time, (read pulse rise and fall time are 10% of tread), minimum tread is 1us. 
    Vread:     Read voltage
    SMUs:      Array of SMU's
    Vdc:       Array of DC voltages
    DCcompl:   Array of DC comliances
    WriteHeader: Enable/Disable writing the header into overlaying summary output files
    Primary:   Flag if PulseIV is used from within Echaracterization or externally
    """
    
    if count > 100:
        eChar.ValError("Maximum of 100 for standard PulseIV, use endurance for more cycles")

    #count-=1
    tfallread = tread * 0.1
    triseread = tread * 0.1

    tmstart = tbase/2 + tfallread
    tmend = tbase/2 + tfallread + tread
    duration = sum([tbase,tfallread,triseread,tread])
    
    eChar.wgfmu.clearLibrary()


    if read and initialRead:
        
        eChar.wgfmu.programRectangularPulse(PulseChn, tread, tfallread, triseread, tbase, Vread, 0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Read", WriteHeader=False)
        eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Ground", WriteHeader=False)
    
    tbaseHalf = tbase/2
    durationR = sum([triseR,twidthR,tfallR,tbase])
    endTimeR = tbaseHalf+triseR+tfallR+twidthR


    if twidthR == 0: 
        eChar.wgfmu.programTriangularPulse(PulseChn, triseR, tfallR, tbase, Vreset, 0, measure=True, mPoints=MeasPoints, mStartTime=tbaseHalf, mEndTime=endTimeR, AddSequence=False, Name="Reset")
        eChar.wgfmu.programGroundChn(GroundChn, durationR, Vg=0, measure=True, mPoints=MeasPoints, mStartTime=tbaseHalf, mEndTime=endTimeR, AddSequence=False, Name="Ground")
    else: 
        eChar.wgfmu.programRectangularPulse(PulseChn, twidthR, triseR, tfallR, tbase, Vreset, 0, measure=True, mPoints=MeasPoints, mStartTime=tbaseHalf, mEndTime=endTimeR, AddSequence=False, Name="Reset")
        eChar.wgfmu.programGroundChn(GroundChn, durationR, Vg=0, measure=True, mPoints=MeasPoints, mStartTime=tbaseHalf, mEndTime=endTimeR, AddSequence=False, Name="Ground")

    if read:
        eChar.wgfmu.programRectangularPulse(PulseChn, tread, tfallread, triseread, tbase, Vread, 0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Read")
        eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Ground")

    durationS = sum([triseS,twidthS,tfallS,tbase])
    endTimeS = tbaseHalf+triseS+tfallS+twidthS
    #("Vset", Vset)
    if twidthS == 0:
        eChar.wgfmu.programTriangularPulse(PulseChn, triseS, tfallS, tbase, Vset, 0, measure=True, mPoints=MeasPoints, mStartTime=tbaseHalf, mEndTime=endTimeS, AddSequence=False, Name="Set")
        eChar.wgfmu.programGroundChn(GroundChn, durationS, Vg=0, measure=True, mPoints=MeasPoints, mStartTime=tbaseHalf, mEndTime=endTimeS, AddSequence=False, Name="Ground")
    else:
        eChar.wgfmu.programRectangularPulse(PulseChn, twidthS, triseS, tfallS, tbase, Vset, 0, measure=True, mPoints=MeasPoints, mStartTime=tbaseHalf, mEndTime=endTimeS, AddSequence=False, Name="Set")
        eChar.wgfmu.programGroundChn(GroundChn, durationS, Vg=0, measure=True, mPoints=MeasPoints, mStartTime=tbaseHalf, mEndTime=endTimeS, AddSequence=False, Name="Ground")
    
    if read:
        
        Rid=1
        readid=3
        Sid=5

        if initialRead:
            Rid+=2
            readid+=2
            Sid+=2

            #("count", count)
            eChar.wgfmu.addSequence(PulseChn, "Read_%d_%d" %(readid,PulseChn), 1)
            eChar.wgfmu.addSequence(GroundChn, "Ground_%d_%d" %(readid+1,GroundChn), 1)

        if count > 0:
            #Pulse Channel
            eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Reset_%d_%d" %(Rid, PulseChn),"Read_%d_%d" %(readid, PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Pulse_%d" %(PulseChn),"Set_%d_%d" %(Sid, PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Pulse_%d" %(PulseChn),"Read_%d_%d" %(readid, PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.addSequence(PulseChn, "Pulse_%d" %(PulseChn), count)

            #Ground Channel
            eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d_%d" %(Rid+1,GroundChn),"Ground_%d_%d" %(readid+1,GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d" %(GroundChn),"Ground_%d_%d" %(Sid+1,GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d" %(GroundChn),"Ground_%d_%d" %(readid+1,GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.addSequence(GroundChn, "Ground_%d" %(GroundChn), count)
    
    else:
        if count > 0:
            #Pulse Channel
            eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Reset_1_%d" %(PulseChn),"Set_3_%d" %(PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.addSequence(PulseChn, "Pulse_%d" %(PulseChn), count)

            #Ground Channel
            eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_2_%d" %(GroundChn),"Ground_4_%d" %(GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.addSequence(GroundChn, "Ground_%d" %(GroundChn), count)

    #pattern = eChar.wgfmu.getPatternForceValues("Pulse_201", 0)
    eChar.wgfmu.synchronize()

    ret = eChar.wgfmu.executeMeasurement()
    SepData = getSepDataPulseIV(eChar, ret, MeasPoints, read, initialRead, True)
    
    header = eChar.wgfmu.getHeader()
    
    if WriteHeader:
        eChar.extendHeader("Combined", header)

    if read:
        AvgHRS  = sum(SepData['HRS'])/float(len(SepData['HRS']))
        AvgLRS  = sum(SepData['LRS'])/float(len(SepData['LRS']))
        header.append('MeasurmentResult,Average.HRS,%f' %(AvgHRS))
        header.append('MeasurmentResult,Average.LRS,%f' %(AvgLRS))

    AvgImSet= sum(SepData['ImaxSet'])/float(len(SepData['ImaxSet']))
    AvgImReset= sum(SepData['ImaxReset'])/float(len(SepData['ImaxReset']))

    header.append('MeasurmentResult,Average.AvgImaxSet,%f' %(AvgImSet))
    header.append('MeasurmentResult,Average.AvgImaxReset,%f' %(AvgImReset))

    header.append('Measurement,Endurance.StartPoint,%d' %(1))
    header.append('Measurement,Endurance.EndPoint,%d' %(count))

    newline = [None]*2
    newline[0] = 'DataName, Cycle'
    newline[1] = 'Dimension, %d' %(ret[0]['Length'])

    for x in range(4):
        newline[0] = '%s,%s' %(newline[0],ret[x]['Name'])
        newline[1] = '%s,%s' %(newline[1],ret[x]['Length'])
    
    header.extend(newline)

    PulseIVDataPrepAndExport(eChar, SepData, header, eChar.curCycle, MeasPoints, 'PulseIV')

    if ret[3]["Name"][0].lower() == "i":
        Trac = [SepData['IVdata'][1],SepData['IVdata'][3]] 
    else:
        Trac = [SepData['IVdata'][3],SepData['IVdata'][1]] 
    eChar.plotIVData({"Traces":Trac,  'Xaxis': True, 'Xlabel': 'Voltage (V)', "Ylabel": 'Current (A)', 'Title': "Pulse IV", "ValueName": 'IV'})
    
    Trac = [SepData['LRS'],SepData['HRS']]
    eChar.plotIVData({"Add": True,  "lineStyle": 'o', "lineWidth":0.5, 'Yscale': 'log', "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of cycles', "Ylabel": 'resistance (ohm)', 'Title': "HRS/LRS", "ValueName": 'HRS/LRS'})

    res = {'Header':header, 'IVdata': SepData['IVdata'], 'LRS':SepData['LRS'], 'HRS':SepData['HRS'], 'Vset':SepData['Vset'], 'Vreset':SepData['Vreset'], 'ImaxSet': SepData['ImaxSet'], 'ImaxReset': SepData['ImaxReset']}

    if Primary:
        HRS = eChar.dhValue(SepData['HRS'], 'HRS', Unit='ohm')
        LRS = eChar.dhValue(SepData['LRS'], 'LRS', Unit='ohm')
        ImaxReset = eChar.dhValue(SepData['ImaxReset'], 'ImaxReset', Unit='A')
        ImaxSet = eChar.dhValue(SepData['ImaxSet'], 'ImaxSet', Unit='A')
        Vreset = eChar.dhValue(SepData['Vreset'], 'Vreset', Unit='V')
        Vset = eChar.dhValue(SepData['Vset'], 'Vset', Unit='V')

        row = eChar.dhAddRow([HRS,LRS,ImaxReset,ImaxSet,Vreset,Vset],eChar.curCycle,eChar.curCycle+count-1)

    eChar.curCycle = eChar.curCycle+count

    return res 

def PulseIVDataPrepAndExport(eChar, SepData, header, PulseStart, MeasPoints):
    
    OutputData = []
    SepData2 = cp.deepcopy(SepData)
    for n in range(len(SepData2['IVdata'][0])):
        frac,whole = ma.modf(float(n)/MeasPoints)
        OutputData.append('DataValue,%d' %(whole+1))
        for da in SepData2['IVdata']:
            OutputData[n] = '%s,%.2E' %(OutputData[n],da[n])
    #print("OD", OutputData)
    eChar.writeDataToFile(header, OutputData, startCyc=eChar.curCycle)

###########################################################################################################################

def DyChar(eChar, SMUs, Vdc, DCcompl, PulseChn, GroundChn, Vset, Vreset, delay, trise, tfall, twidth, tbase, MeasPoints, 
                    Specs, read=True, tread=10e-6, Vread=-0.2, initialRead=True):

    # PulseChn, GroundChn, Vform, delay, trise, tfall, twidth, tbase, MeasPoints,
    # Take 
    # Original format:
        #eChar.setDCVoltages(SMUs=[3], Vdc=[-0.5], DCcompl=[1e-3]) --- (Will stay the same)
        #eChar.PulseForming(201,202,4,1000e3,100e-3,100e-3,0,1000e-3,100, Vread=0.2) --- (Will stay the same)
            # May need to add variable to save output data to be used for inputs to new code ***
        #eChar.setDCVoltages(SMUs=[3], Vdc=[-0.1], DCcompl=[1e-3]) --- (First DC voltage set for 1st reset)
        #eChar.PulseReset(201,202,-1.7, 100e-3, 1000e-3, 1000e-3,0,100e-3,10000) --- (First reset, Initial param from testing)
            # May need to add variable to save output data to be used for inputs to new code ***
        # ********* Where the new code will start ********
        #eChar.PulseSet(201,202, 2.5, 1e-5, 100e-6, 100e-6, 0, 10e-6, 100)
        #eChar.PulseReset(201,202,-1.5, 100e-3, 10e-3, 10e-3,0,100e-3,100)
        #eChar.PulseSet(201,202, 2.5, 1e-5, 100e-6, 100e-6, 0, 10e-6, 100) etc.
    # 
    # Inputs for code:
        # Use setDCVoltages(SMUs=[3], Vdc=[-0.1], DCcompl=[1e-3]) as input (Vdc Will be adjusted throughout code)
        # Set original value for Vresetmax (-1.7V in this case) as variable that can be used for input to this def
            # Example eChar.PulseReset(201,202, Vresetmax, 100e-3, 1000e-3, 1000e-3,0,100e-3,10000)
        # StatOutValues used for HRS, LRS, ImaxReset, Vreset (for Set and Reset)
            # These are the outputs from froming and reset.
        # Initial times should be given the same as for Endurance and will adjust other parameters first before time.
    # Code:
        # Have 2 for loops running:
            # 1. Apply initial Vreset and adjust if 2nd for loop doesn't work.
            # 2. Run Reset/Set iteration for n times checking variables compared to Specs.
            # If nothing works return statement "failed" and do not run endurance. Move to next device.

        # For possible future work:
            # Run 3 Reset/Set iterations with initial cond. Taking the avg. of HRS, LRS, ImaxReset, V (Set/Reset)
            # Compare results with given Specs.
            # If results outside of specs:
                # 1. Adjust Vdc.
                    # Repeat until within specs or hit max/min Vdc allowed.
                    # If works return parameters and run Endurance. ***
                    # If not move to next adjustment parameter.
                # 2. Adjust Vresetmax/Vsetmax and repeat 1.
                    # Repeat until hit max/min of Vresetmax.
                # 3. Adjust time variables to large rise/fall specs and repeat 1 and 2.
                # 4. If nothing works return statement "failed" and do not run endurance. Move to next device.
    n = 0
    s = 10
    DontWork = 0
    Setret = []
    Resret = []
    change = 0
    SepOutput = {'HRS': [], 'LRS': [], 'ImaxSet': [], 'ImaxReset': [], 'IVdata': [], 'Vset': [], 'Vreset': []}
    ImaxReset = []
    ImaxSet = []
    HRS = []
    LRS = []
    IV  = []
    setnum = 0

    for iteratable in np.arange(-1.0, -2.1, -0.1):
        for n in range(0,s):
            Vreset = float(iteratable)
            # Reset Measurement
            eChar.updateTime()
            tfallread = tread * 0.1
            triseread = tread * 0.1

            tmstart = tbase/2 + tfallread
            tmend = tbase/2 + tfallread + tread
            duration = sum([tbase,tfallread,triseread,tread])
            
            eChar.wgfmu.clearLibrary()

            if read and initialRead:
                eChar.wgfmu.programRectangularPulse(PulseChn, tread, tfallread, triseread, tbase, Vread, 0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Read", WriteHeader=False)
                eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Ground", WriteHeader=False)
                paReadID = 1

            durationF = sum([trise,twidth,tfall,tbase])
            endTime = tbase/2+trise+tfall+twidth
            if twidth == 0: 
                eChar.wgfmu.programTriangularPulse(PulseChn, trise, tfall, tbase, Vreset, 0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Form")
                eChar.wgfmu.programGroundChn(GroundChn, durationF, Vg=0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Ground")
            else: 
                eChar.wgfmu.programRectangularPulse(PulseChn, twidth, trise, tfall, tbase, Vreset, 0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Form")
                eChar.wgfmu.programGroundChn(GroundChn, durationF, Vg=0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Ground")

            paItstart = 1

            if read and not initialRead:
                eChar.wgfmu.programRectangularPulse(PulseChn, tread, tfallread, triseread, tbase, Vread, 0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Read", WriteHeader=False)
                eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Ground", WriteHeader=False)
                paItstart = 1
                paReadID = 3

            if read and initialRead:
                eChar.wgfmu.addSequence(PulseChn, "Read_%d_%d" %(paReadID,PulseChn), 1)
                eChar.wgfmu.addSequence(GroundChn, "Ground_%d_%d" %(paReadID+1,GroundChn), 1)
                paItstart = 3

            eChar.wgfmu.addSequence(PulseChn, "Form_%d_%d" %(paItstart,PulseChn), 1)
            eChar.wgfmu.addSequence(GroundChn, "Ground_%d_%d" %(paItstart+1,GroundChn), 1)

            if read:
                eChar.wgfmu.addSequence(PulseChn, "Read_%d_%d" %(paReadID,PulseChn), 1)
                eChar.wgfmu.addSequence(GroundChn, "Ground_%d_%d" %(paReadID+1,GroundChn), 1)
            
            eChar.wgfmu.synchronize()
            
            initialRead=False

            ret = eChar.wgfmu.executeMeasurement()
            ResetRet = getSepDataPulseIV(eChar, ret, MeasPoints, read, initialRead, True)
            
            
            SepOutput['HRS'].extend(ResetRet['HRS'])
            SepOutput['LRS'].extend(ResetRet['LRS'])
            SepOutput['Vset'].extend(ResetRet['Vset'])
            SepOutput['Vreset'].extend(ResetRet['Vreset'])
            SepOutput['ImaxSet'].extend(ResetRet['ImaxSet'])
            SepOutput['ImaxReset'].extend(ResetRet['ImaxReset'])

            for k in range(4):
                    SepOutput['IVdata'][k].extend(ResetRet['IVdata'][k])

            # Compare Specs with output data.
            eChar.CompareSpecs(Setret, Resret, Specs)


            if change == 0:
                #eChar.Vreset = Vreset  # Change endurance and pulse IV Vreset to this variable
                #break   # saves Vreset and breaks out of def and then we will run Pulse IV and then Endurance

                # Set Measurement
                eChar.updateTime()
                tfallread = tread * 0.1
                triseread = tread * 0.1

                tmstart = tbase/2 + tfallread
                tmend = tbase/2 + tfallread + tread
                duration = sum([tbase,tfallread,triseread,tread])
                
                eChar.wgfmu.clearLibrary()

                if read:
                    eChar.wgfmu.programRectangularPulse(PulseChn, tread, tfallread, triseread, tbase, Vread, 0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Read", WriteHeader=False)
                    eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Ground", WriteHeader=False)

                durationF = sum([trise,twidth,tfall,tbase])
                endTime = tbase/2+trise+tfall+twidth
                if twidth == 0: 
                    eChar.wgfmu.programTriangularPulse(PulseChn, trise, tfall, tbase, Vset, 0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Form")
                    eChar.wgfmu.programGroundChn(GroundChn, durationF, Vg=0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Ground")
                else: 
                    eChar.wgfmu.programRectangularPulse(PulseChn, twidth, trise, tfall, tbase, Vset, 0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Form")
                    eChar.wgfmu.programGroundChn(GroundChn, durationF, Vg=0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Ground")

                paItstart = 1

                if read and initialRead:
                    eChar.wgfmu.addSequence(PulseChn, "Read_1_%d" %(PulseChn), 1)
                    eChar.wgfmu.addSequence(GroundChn, "Ground_2_%d" %(GroundChn), 1)
                    paItstart = 3

                eChar.wgfmu.addSequence(PulseChn, "Form_%d_%d" %(paItstart,PulseChn), 1)
                eChar.wgfmu.addSequence(GroundChn, "Ground_%d_%d" %(paItstart+1,GroundChn), 1)

                if read:
                    eChar.wgfmu.addSequence(PulseChn, "Read_1_%d" %(PulseChn), 1)
                    eChar.wgfmu.addSequence(GroundChn, "Ground_2_%d" %(GroundChn), 1)
                
                eChar.wgfmu.synchronize()
                
                ret = eChar.wgfmu.executeMeasurement()
                SetRet = getSepDataPulseIV(eChar, ret, MeasPoints, read, initialRead, True)
                
                SepOutput['HRS'].extend(SetRet['HRS'])
                SepOutput['LRS'].extend(SetRet['LRS'])
                SepOutput['Vset'].extend(SetRet['Vset'])
                SepOutput['Vreset'].extend(SetRet['Vreset'])
                SepOutput['ImaxSet'].extend(SetRet['ImaxSet'])
                SepOutput['ImaxReset'].extend(SetRet['ImaxReset'])

                for k in range(4):
                    SepOutput['IVdata'][k].extend(SetRet['IVdata'][k])
                
                n = 0
                setnum = setnum + 1

                if setnum == 20:
                    eChar.Vreset = Vreset  # Change endurance and pulse IV Vreset to this variable
                    eChar.DontWork = 0
                    return Vreset   # saves Vreset and breaks out of def and then we will run Pulse IV and then Endurance
        
    DontWork = 1
    return DontWork 

# Needs to know which ret data represents LRS and HRS.***************************
def CompareSpecs(eChar, Setret, Resret, Specs):
    change = 0
    if Setret == []:
        if Resret['HRS'] > Specs[2] or Resret['HRS'] < Specs[3]:
            change = 1
    else:
        if Setret['LRS'] > Specs[0] or Setret['LRS'] < Specs[1]:
            change = 1

        if Resret['HRS'] > Specs[2] or Resret['HRS'] < Specs[3]:
            change = 1

    return change

###########################################################################################################################

def PulseRetention(eChar, PulseChn, GroundChn, Vread, delay, tread,  tbase, t_total, MeasPoints, Log=False, tdelta_start=1e-1,  WriteHeader=True):
    """
    please set the appropriate Channel properties beforehand via 'setChannelParameter()'
    GroundChn: Ground channel number
    PulseChn:   Pulse channel number
    Vread:      Read Voltage (V)
    delay:      delay before measurement starts (s)
    tread:      read pulse width (s)
    tbase:      base time   (s)
    t_total:    total retention measurement time (s)
    MeasPoints: total number of measurement points(s)
    Log:        Use a logarithmic scale
    tdelta_start: first delta between measurement points
    WriteHeader: Enable/Disable writing the header into overlaying summary output files
    """

    tfall = tread * 0.1
    trise = tread * 0.1
    eChar.updateTime()
    
    tdelta = t_total/MeasPoints
    
    if tdelta_start < 2e-3 or tdelta  < 2e-3:
        raise ValueError("the minimum delta time is 200us.")

    tmstart = tbase/2 + trise*2
    tmend = tbase/2 + trise + tread-tfall
    duration = tread+tbase+tfall+trise
    
    eChar.wgfmu.clearLibrary()

    eChar.wgfmu.programRectangularPulse(PulseChn, tread, trise, tfall, tbase, Vread, 0, count=1, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=True, Name="Read")
    eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, count=1, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=True, Name="Ground")
    
    eChar.wgfmu.synchronize()

    tstart = tm.time()

    if Log:
        
        logtst = np.log10(tdelta_start)
        logttot = np.log10(t_total)

        logTotal = logttot - logtst

        logDelta = logTotal/(MeasPoints-2)

        tpoints = []
        tpoints.append(delay)
        for m in range(MeasPoints-1):

            tpoints.append(delay + np.power(10,(logtst+m*logDelta)))

        Xscale = "log"

    else:

        tpoints = [tdelta*n for n in range(1,MeasPoints+1)]
        Xscale = "lin"

    resistances = []
    times = []

    stop = False
    connect = False
    for t in tpoints:

        slTime = t - (tstart - tm.time()) 
        if slTime < 0.1:
            tm.sleep(slTime)
        else:
            while t - (tm.time() - tstart) > 0:
                while not eChar.Stop.empty():
                    stop = eChar.Stop.get()
                if stop:    
                    return {'Stop': True}
                slTime = t - (tm.time() - tstart)
                if 0 < slTime < 0.1:
                    tm.sleep(slTime)
                elif 0 >=slTime:
                    break
                else:
                    tm.sleep(0.1)
                
        if stop:
            break

        tim = tm.time() - tstart
        
        if not connect:
            ret = eChar.wgfmu.executeMeasurement(Connect=True)
        else:
            ret = eChar.wgfmu.executeMeasurement()

        resis = abs(ret[1]['Data'][0]/-ret[3]['Data'][0])
        resistances.append(resis)
        times.append(tim)
        Trac = [[tim], [resis]]
        eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': True, 'Xlabel': 'Time (s)', "Xscale": Xscale, "Ylabel": 'Resistance (ohm)', "Yscale": 'log', 'Title': "Retention", "ValueName": 'Rt'})

            

    eChar.wgfmu.disconnect(PulseChn)
    eChar.wgfmu.disconnect(GroundChn)

    header = []
    header = eChar.wgfmu.getHeader()

    if WriteHeader:
        eChar.extendHeader("Combined", header)
    
    newline = [None]*2
    newline[0] = 'DataName'
    newline[1] = 'Dimension'

    newline[0] = '%s,%s,%s' %(newline[0],'Time','Resistance')
    newline[1] = '%s,%s,%s' %(newline[1],len(times), len(resistances))

    dataStr = []
    for n in range(len(resistances)):
        dataStr.append("DataValue, %.2E, %.2E" %(times[n],resistances[n]))
    
    header.extend(newline)

    eChar.writeDataToFile(header, dataStr)
           
    res = {'Header':header, 'Rtdata':[times,resistances]}


    resis = eChar.dhValue(resistances, 'Resistance', Unit='ohm')
    row = eChar.dhAddRow([resis],eChar.curCycle,eChar.curCycle)

    eChar.curCycle = eChar.curCycle+1
    return res


###########################################################################################################################

def performEndurance(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
                        Count, MeasPoints=50, tread=10e-6, Vread=-0.2, IVIteration=0, IVcount=10, ReadEndurance=True, SMUs=None, 
                        Vdc=None, DCcompl=None, WriteHeader=True, DoYield=True):
    
    """
    Standard measurement for Endurance measurements, this part relies on 
    please set the appropriate Channel properties beforehand via 'setChannelParameter()'
    GroundChn: Ground channel number
    PulseChn:  Pulse channel number
    Vset:      Set Voltage
    Vreset:    Reset Voltage
    delay:     delay before measurement starts
    triseS:    Set rise time
    tfallS:    Set fall time
    twidthS:   Set pulse width
    triseR:    Reset rise time
    tfallR:    Reset fall time
    twidthR:   Reset pulse width
    tbase:     base time
    MeasPoints:Number of Measurement points during Set and Reset
    Count:     Number of repetitions (maximum of 100)
    read:      Read enable, True for enalbed, False for disabled
    tread:     Read pulse time, (read pulse rise and fall time are 10% of tread), minimum tread is 1us. 
    Vread:     Read voltage
    SMUs:      Array of SMU's
    Vdc:       Array of DC voltages
    DCcompl:   Array of DC comliances
    """

    eChar.updateTime()
    CurCount = 1
    initialRead = True
    if IVIteration ==0: 
        IVcount =0

    eChar.startThread(target = saveDataEndurance, args=(eChar, WriteHeader,DoYield, eChar.getMaxRowsPerFile(), eChar.getMaxDataPerPlot()))
    

    stop =  False
    #Run repetitions until number of ran cycles reaches programmed count
    
    while CurCount < Count - IVcount:

        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
        if stop:
            eChar.finished.put(True)
            break

        #IV characterization + Endurance
        if IVIteration > 20:
            addHeader= []
            addHeader.append('Measurement,Type.Primary,Endurance')
            addHeader.append('Measurement,Type.Secondary,PulseIV')
            addHeader.append('Measurement,Endurance.StartPoint,%d' %(eChar.curCycle))
            addHeader.append('Measurement,Endurance.EndPoint,%d' %(eChar.curCycle+IVcount))

            WrHead = False
            if initialRead:
                WrHead = True
            
            eChar.RDstart.put(eChar.curCycle)
            eChar.RDstop.put(eChar.curCycle + IVcount-1)
            ret = PulseIV(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
                                MeasPoints=MeasPoints, count=IVcount, read=True, initialRead=initialRead, tread=tread, Vread=Vread, SMUs=SMUs, 
                                Vdc=Vdc, DCcompl=DCcompl,WriteHeader=WrHead, Primary=False)
            eChar.rawData.put(ret)

            if CurCount == 0: 
                eChar.wgfmu.disableWritePulseHeader()
            CurCount += IVcount

            if initialRead:
                CurCount += 1
                eChar.writeHeader("Endurance", eChar.wgfmu.getHeader())
                initialRead = False
            
            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
            if stop:    
                break
            #Pulsing]
            if (Count - CurCount) < (IVIteration - IVcount):
                
                IVIteration = Count - CurCount - IVcount
                if IVIteration < 1: 
                    break
                
                #Less cycles left than in one iteration
                if IVIteration > eChar.getMaxNumSingleEnduranceRun() and ReadEndurance:
                    sol = IVIteration/eChar.getMaxNumSingleEnduranceRun()
                    frac, whole = ma.modf(sol)
                    for n in range(int(whole)):
                        
                        while not eChar.Stop.empty():
                            stop = eChar.Stop.get()
                        if stop:    
                            break

                        createEndurancePulse(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, 
                                                        tbase, eChar.getMaxNumSingleEnduranceRun(), read=ReadEndurance, tread=tread, Vread=Vread, 
                                                        initialRead=initialRead)
                        
                        if ReadEndurance:
                            ret = eChar.wgfmu.executeMeasurement()
                            ret = getSepEnduranceData(ret)
                            eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 'Type':'Endurance'})
                            eChar.RDstart.put(eChar.curCycle)
                            eChar.RDstop.put(eChar.curCycle + eChar.getMaxNumSingleEnduranceRun()-1)
                        else:
                            eChar.wgfmu.executeMeasurement(GetData=False)

                        eChar.curCycle += eChar.getMaxNumSingleEnduranceRun()
                        CurCount += eChar.getMaxNumSingleEnduranceRun()
                        initialRead = False

                    if frac > 0:
                        count_Last = int(frac*eChar.getMaxNumSingleEnduranceRun())
                        createEndurancePulse(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, 
                                                        tbase, count_Last, read=ReadEndurance, tread=tread, Vread=Vread)

                        if ReadEndurance:
                            ret = eChar.wgfmu.executeMeasurement()
                            ret = getSepEnduranceData(ret)
                            eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 
                                                'Type':'Endurance'})
                            eChar.RDstart.put(eChar.curCycle)
                            eChar.RDstop.put(eChar.curCycle + count_Last-1)
                        else:
                            eChar.wgfmu.executeMeasurement(GetData=False)
                        eChar.curCycle += count_Last
                        CurCount += count_Last
                else:
                    createEndurancePulse(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
                                                IVIteration, read=ReadEndurance, tread=tread, Vread=Vread, initialRead=initialRead)
                    
                    initialRead = False
                    
                    if ReadEndurance:
                        ret = eChar.wgfmu.executeMeasurement()
                        ret = getSepEnduranceData(ret)
                        eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 
                                            'Type':'Endurance'})
                        eChar.RDstart.put(eChar.curCycle)
                        eChar.RDstop.put(eChar.curCycle - 1 + IVIteration)
                    else:
                        eChar.wgfmu.executeMeasurement(GetData=False)
                    
                    eChar.curCycle += IVIteration
                    CurCount += IVIteration

            #more cycles left than in one iteration
            else:
                
                #Less cycles left than in one iteration
                if IVIteration > eChar.getMaxNumSingleEnduranceRun() and ReadEndurance:
                    sol = IVIteration/eChar.getMaxNumSingleEnduranceRun()
                    frac, whole = ma.modf(sol)
                    for n in range(int(whole)):
                        
                        while not eChar.Stop.empty():
                            stop = eChar.Stop.get()
                        if stop:    
                            break

                        createEndurancePulse(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, 
                                                        tbase, eChar.getMaxNumSingleEnduranceRun(), read=ReadEndurance, tread=tread, Vread=Vread, 
                                                        initialRead=initialRead)
                        if ReadEndurance:
                            ret = eChar.wgfmu.executeMeasurement()
                            ret = getSepEnduranceData(ret)
                            eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 'Type':'Endurance'})
                            eChar.RDstart.put(eChar.curCycle)
                            eChar.RDstop.put(eChar.curCycle + eChar.getMaxNumSingleEnduranceRun()-1)
                        else:
                            eChar.wgfmu.executeMeasurement(GetData=False)
                        eChar.curCycle += eChar.getMaxNumSingleEnduranceRun()
                        CurCount += eChar.getMaxNumSingleEnduranceRun()
                        initialRead = False

                    if frac > 0:
                        count_Last = int(frac*eChar.getMaxNumSingleEnduranceRun())
                        createEndurancePulse(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, 
                                                        tbase, count_Last, read=ReadEndurance, tread=tread, Vread=Vread)

                        if ReadEndurance:
                            ret = eChar.wgfmu.executeMeasurement()
                            ret = getSepEnduranceData(ret)
                            eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 
                                                'Type':'Endurance'})
                            eChar.RDstart.put(eChar.curCycle)
                            eChar.RDstop.put(eChar.curCycle + count_Last-1)
                        else:
                            eChar.wgfmu.executeMeasurement(GetData=False)
                        eChar.curCycle += count_Last
                        CurCount += count_Last
                else:
                    createEndurancePulse(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
                                                IVIteration, read=ReadEndurance, tread=tread, Vread=Vread, initialRead=initialRead)
                    
                    initialRead = False
                    if ReadEndurance:
                        ret = eChar.wgfmu.executeMeasurement()
                        ret = getSepEnduranceData(ret)
                        eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 
                                            'Type':'Endurance'})
                        eChar.RDstart.put(eChar.curCycle)
                        eChar.RDstop.put(eChar.curCycle - 1 + IVIteration)
                    else:
                        eChar.wgfmu.executeMeasurement(GetData=False)
                    CurCount += IVIteration
                    eChar.curCycle += IVIteration

        #only endurance
        else:
            #Run as many 2e6 cycles as you need to get to IVIteration
            if Count > eChar.getMaxNumSingleEnduranceRun() and ReadEndurance:
                sol = Count/eChar.getMaxNumSingleEnduranceRun()
                frac, whole = ma.modf(sol)
                
                for n in range(int(whole)):
                    
                    while not eChar.Stop.empty():
                        stop = eChar.Stop.get()
                    if stop:    
                        break

                    createEndurancePulse(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, 
                                                    tbase, eChar.getMaxNumSingleEnduranceRun(), read=ReadEndurance, tread=10e-6, Vread=-0.2, initialRead=initialRead)

                    if ReadEndurance:
                        ret = eChar.wgfmu.executeMeasurement()
                        ret = getSepEnduranceData(ret)
                        eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 'Type':'Endurance'})
                        eChar.RDstart.put(eChar.curCycle)
                        eChar.RDstop.put(eChar.curCycle + eChar.getMaxNumSingleEnduranceRun()-1)
                    else:
                        eChar.wgfmu.executeMeasurement(GetData=False)
                    CurCount += eChar.getMaxNumSingleEnduranceRun()
                    eChar.curCycle += eChar.getMaxNumSingleEnduranceRun()

                if frac > 0:
                    count_Last = int(frac*eChar.getMaxNumSingleEnduranceRun())
                    createEndurancePulse(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, 
                                                    tbase, count_Last, read=ReadEndurance, tread=10e-6, Vread=-0.2)

                    if ReadEndurance:
                        ret = eChar.wgfmu.executeMeasurement()
                        ret = getSepEnduranceData(ret)
                        eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 'Type':'Endurance'})
                        eChar.RDstart.put(eChar.curCycle)
                        eChar.RDstop.put(eChar.curCycle + count_Last-1)
                    else:
                        eChar.wgfmu.executeMeasurement(GetData=False)
                    CurCount += count_Last
                    eChar.curCycle += count_Last

            else:
                createEndurancePulse(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
                                            Count, read=ReadEndurance, tread=10e-6, Vread=-0.2, initialRead=initialRead)

                initialRead = False

                if ReadEndurance:
                    ret = eChar.wgfmu.executeMeasurement()
                    ret = getSepEnduranceData(ret)
                    eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 'Type':'Endurance'})
                    eChar.RDstart.put(eChar.curCycle)
                    eChar.RDstop.put(eChar.curCycle + Count-1)
                else:
                    eChar.wgfmu.executeMeasurement(GetData=False)
                CurCount += Count
                eChar.curCycle += Count

        if initialRead:
            CurCount+=1
            eChar.writeHeader("Endurance", eChar.wgfmu.getHeader())
            initialRead = False

    if IVIteration > 0:
        addHeader = []
        addHeader.append('Measurement,Type.Primary,Endurance')
        addHeader.append('Measurement,Type.Secondary,PulseIV')
        addHeader.append('Measurement,Endurance.StartPoint,%d' %(eChar.curCycle))
        addHeader.append('Measurement,Endurance.EndPoint,%d' %(eChar.curCycle+IVcount))
        eChar.extendHeader("Additional",addHeader)
        
        if not stop:

            eChar.RDstart.put(eChar.curCycle)
            eChar.RDstop.put(eChar.curCycle + IVcount-1)
            eChar.rawData.put(PulseIV(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, 
                                tbase, MeasPoints=MeasPoints, count=IVcount, read=True, initialRead=initialRead, tread=tread, Vread=Vread, 
                                SMUs=SMUs, Vdc=Vdc, DCcompl=DCcompl,WriteHeader=False, Primary=False))
            CurCount += IVcount

    print("finished put True")
    eChar.finished.put(True)

    for thr in eChar.threads:
        while thr.is_alive():
            thr.join()
            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
            if stop:    
                break

    eChar.LogData.put("Endurance: Finished Measurement.")

    while True:
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

    if WriteHeader:
        eChar.extendHeader("Combined",eChar.getHeader("Endurance"))

    return True 

def getSepEnduranceData(ret):
    
    Name = []
    Channel = []
    Length = []
    Data = []
    n = 0
    for da in ret: 
        Name.append(da['Name'])
        Channel.append(da['Channel'])
        Length.append(da['Length'])
        if n ==3:
            Data.append([-x for x in da['Data']])
        else:
            Data.append(da['Data'])
        n+=1

    return {'Name': Name, 'Channel': Channel, 'Length': Length, 'Data':Data}


def saveDataEndurance(eChar, WriteHeader, DoYield, MaxRowsPerFile, MaxDataPerPlot):
    
    #seperate data until Endurance measurement is finished
    first = True
    usedPulsedIV = False
    Typ = "Endurance"
    
    if DoYield:
        DoYield = eChar.DoYield      

    HRSVal = eChar.dhValue([], 'HRS', Unit='ohm')
    LRSVal = eChar.dhValue([], 'LRS', Unit='ohm')
    ImaxResetVal = eChar.dhValue([], 'ImaxReset', Unit='A')
    ImaxSetVal = eChar.dhValue([], 'ImaxSet', Unit='A')
    VresetVal = eChar.dhValue([], 'Vreset', Unit='V')
    VsetVal = eChar.dhValue([], 'Vset', Unit='V')

    OutputStart = True
    RDcycStartOutput = 1

    RDcycStart = 1
    RDcycStop = 1

    finished = False
    while not finished or not eChar.rawData.empty():
                
        while not eChar.finished.empty():
            finished = eChar.finished.get()
        
        #print("finished: ", finished, eChar.rawData.empty())
        tm.sleep(0.5)

        try:
            complData = eChar.rawData.get(True, 0.2)
            RDcycStart = eChar.RDstart.get(True, 0.1)
            RDcycStop = eChar.RDstop.get(True, 0.1)

            if OutputStart:
                RDcycStartOutput = RDcycStart
                OutputStart = False


            HRS = []
            LRS = []
            if (complData['Type'] == 'Endurance'):
                
                data = np.array(complData['Data'])

                if complData['Name'][1][0].lower() == "i":
                    ni = 1
                    nv = 3
                else:
                    ni = 3
                    nv = 1                
                res = list(np.divide(np.absolute(data[nv:]),np.absolute(data[ni:]))[0])
                
                m = 0
                c = 0
                for n in range(len(res)):
                    if first:
                        if m == 0:
                            eChar.LRS.append(res[n])
                            LRS.append(res[n])
                            eChar.cyc.append(RDcycStart + c)
                            c+=1
                            m+=1
                        else:
                            eChar.HRS.append(res[n])
                            HRS.append(res[n])
                            m = 0
                    else:
                        if m == 0:
                            eChar.HRS.append(res[n])
                            HRS.append(res[n])
                            eChar.cyc.append(RDcycStart + c)
                            c+=1
                            m+=1
                        else:
                            eChar.LRS.append(res[n])
                            LRS.append(res[n])
                            m = 0
                            
                HRSVal.extend(HRS)
                LRSVal.extend(LRS)

            elif complData['Type'] == 'PulseIV':
                usedPulsedIV = True
                
                for n in range(max([len(complData['LRS']),len(complData['HRS'])])):
                    eChar.IVcyc.append(RDcycStart + n)
                    eChar.cyc.append(RDcycStart + n)

                for n in range(len(complData['LRS'])):
                    eChar.LRS.append(complData['LRS'][n])
                    eChar.IVLRS.append(complData['LRS'][n])
                for n in range(len(complData['HRS'])):
                    eChar.HRS.append(complData['HRS'][n])
                    eChar.IVHRS.append(complData['HRS'][n])
                for n in range(len(complData['ImaxSet'])):
                    eChar.ImaxSet.append(complData['ImaxSet'][n])
                    eChar.Vset.append(complData['Vset'][n])
                for n in range(len(complData['ImaxReset'])):
                    eChar.ImaxReset.append(complData['ImaxReset'][n])
                    eChar.Vreset.append(complData['Vreset'][n])

                HRSVal.extend(complData['HRS'])
                LRSVal.extend(complData['LRS'])
                ImaxResetVal.extend(complData['ImaxReset'])
                ImaxSetVal.extend(complData['ImaxSet'])
                VresetVal.extend(complData['Vreset'])
                VsetVal.extend(complData['Vset'])

            if len(HRS) > MaxDataPerPlot:
                Trac = [LRS[-MaxDataPerPlot:],HRS[-MaxDataPerPlot:]]
            else:
                Trac = [LRS,HRS]

            eChar.plotIVData({"Add": True, "lineStyle": 'o', "lineWidth":0.5, 'Yscale': 'log',  "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of cycles', "Ylabel": 'resistance (ohm)', 'Title': "HRS/LRS",  "ValueName": 'HRS/LRS'})
            
        except (TypeError, ValueError, IndexError, NameError, qu.Empty) as e:
            eChar.ErrorQueue.put("E-Char Endurance Data Analysis, Queue Empty: %s, Finished %s, Error %s" %(eChar.rawData.empty(), finished, e))
        
        try:
            if usedPulsedIV:
                with eChar.DataAnalysisLock:
                    if len(eChar.IVHRS) > MaxRowsPerFile or (finished and eChar.rawData.empty()): 
                        header = eChar.getHeader("Endurance")
                        header.append('Measurement,Endurance.StartPoint,%d' %(eChar.IVcyc[0]))
                        header.append('Measurement,Endurance.EndPoint,%d' %(eChar.IVcyc[-1]))

                        header.append('DataName, Cycle, LRS, HRS, ImaxSet, ImaxReset')
                        header.append('Dimension, %d,%d,%d,%d,%d' %(len(eChar.IVcyc), len(eChar.IVLRS), len(eChar.IVHRS), len(eChar.ImaxSet), len(eChar.ImaxReset)))
                        
                        outputData = getOutputFormat([eChar.IVcyc,eChar.IVLRS,eChar.IVHRS,eChar.ImaxSet,eChar.ImaxReset])
                        print("writeEnd")
                        eChar.writeDataToFile(header, outputData, subFolder="Endurance", Typ="IVSummaryEndurance", startCyc=1)

                        eChar.IVLRS = []
                        eChar.IVHRS = []
                        eChar.ImaxReset = []
                        eChar.ImaxSet = []
                        eChar.Vset = []
                        eChar.Vreset = []

            if first:
                first = False

            tm.sleep(0.1)

            with eChar.DataAnalysisLock:
                if len(eChar.HRS) > MaxRowsPerFile or (finished and eChar.rawData.empty()): 
                    header = eChar.getHeader("Endurance")
                    header.append('Measurement,Endurance.StartPoint,%d' %(eChar.cyc[0]))
                    header.append('Measurement,Endurance.EndPoint,%d' %(eChar.cyc[-1]))

                    header.append('DataName, Cycle, LRS, HRS')
                    header.append('Dimension, %d,%d,%d' %(len(eChar.cyc), len(eChar.LRS), len(eChar.HRS)))
                    
                    outputData = getOutputFormat([eChar.cyc,eChar.LRS,eChar.HRS])
                
                    eChar.writeDataToFile(header, outputData, startCyc=RDcycStartOutput, endCyc=RDcycStop, subFolder="Endurance")

                    eChar.cyc = []
                    eChar.LRS = []
                    eChar.HRS = []

                    OutputStart = True

        except (TypeError, ValueError, IndexError, NameError) as e:
            eChar.ErrorQueue.put("E-Char Endurance Data Analysis, Queue Empty: %s, Finished %s, Error %s" %(eChar.rawData.empty(), finished, e))
        
    RDcycStop = eChar.curCycle
    if usedPulsedIV:
        row = eChar.dhAddRow([HRSVal,LRSVal,ImaxResetVal,ImaxSetVal,VresetVal,VsetVal],RDcycStart,RDcycStop)
    else:
        row = eChar.dhAddRow([HRSVal,LRSVal],RDcycStart,RDcycStop)

    eChar.SubProcessThread.put({'Finished': True})
    eChar.LogData.put("Endurance: Finished Data Storage.")
    

def getOutputFormat(ar):
    
    outputData = []
    length = []
    for el in ar: 
        length.append(len(el))
    mlength = max(length)

    for n in range(mlength):
        outputData.append('DataValue')
        if n >= len(ar[0]):
            outputData[n] = '%s,' %(outputData[n])
        else:
            outputData[n] = '%s,%d' %(outputData[n],ar[0][n])
        if n == 0: 
            if n >= len(ar[1]):
                outputData[n] = '%s,' %(outputData[n])
            else:
                outputData[n] = '%s,%.2E' %(outputData[n],ar[1][n])
                for m in ar[2:]:
                    outputData[n] = '%s,' %(outputData[n])
        else:
            if n >= len(ar[1]):
                outputData[n] = '%s,' %(outputData[n])
            else:
                outputData[n] = '%s,%.2E' %(outputData[n],ar[1][n])
        
        if not n == 0: 
            for el in ar[2:]:
                if n >= len(el)+1:
                    outputData[n] = '%s,' %(outputData[n])
                else:
                    outputData[n] = '%s,%.2E' %(outputData[n],el[n-1])

    return outputData

def createEndurancePulse(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
                            count, read=True, tread=10e-6, Vread=-0.2, initialRead=True):

    tfallread = tread * 0.1
    triseread = tread * 0.1

    tmstart = tbase/2 + tfallread
    tmend = tbase/2 + tfallread + tread
    duration = sum([tbase,tfallread,triseread,tread])

    eChar.wgfmu.clearLibrary()   

    if read  and initialRead:
        eChar.wgfmu.programRectangularPulse(PulseChn, tread, tfallread, triseread, tbase, Vread, 0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Read", WriteHeader=False)
        eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Ground", WriteHeader=False)

    durationR = sum([triseR,twidthR,tfallR,tbase])
    if twidthR == 0: 
        eChar.wgfmu.programTriangularPulse(PulseChn, triseR, tfallR, tbase, Vreset, 0, measure=False, mPoints=-1, AddSequence=False, Name="Reset")
        eChar.wgfmu.programGroundChn(GroundChn, durationR, Vg=0, measure=False, AddSequence=False, Name="Ground")
    else: 
        eChar.wgfmu.programRectangularPulse(PulseChn, twidthR, triseR, tfallR, tbase, Vreset, 0, measure=False, AddSequence=False, Name="Reset")
        eChar.wgfmu.programGroundChn(GroundChn, durationR, Vg=0, measure=False, AddSequence=False, Name="Ground")
    
    if read:
        eChar.wgfmu.programRectangularPulse(PulseChn, tread, tfallread, triseread, tbase, Vread, 0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Read", WriteHeader=False)
        eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Ground", WriteHeader=False)

    duration = sum([triseS,twidthS,tfallS,tbase])

    if twidthS == 0:
        eChar.wgfmu.programTriangularPulse(PulseChn, triseS, tfallS, tbase, Vset, 0, measure=False, mPoints=-1, AddSequence=False, Name="Set")
        eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=False, AddSequence=False, Name="Ground")
    else:
        eChar.wgfmu.programRectangularPulse(PulseChn, twidthS, triseS, tfallS, tbase, Vset, 0, measure=False, AddSequence=False, Name="Set")
        eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=False, AddSequence=False, Name="Ground")

    if read:
        Rid=1
        readid=3
        Sid=5

        if initialRead:
            Rid+=2
            readid+=2
            Sid+=2
        
            eChar.wgfmu.addSequence(PulseChn, "Read_%d_%d" %(readid,PulseChn), 1)
            eChar.wgfmu.addSequence(GroundChn, "Ground_%d_%d" %(readid+1,GroundChn), 1)

        if count > 0:
            #Pulse Channel
            eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Reset_%d_%d" %(Rid, PulseChn),"Read_%d_%d" %(readid, PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Pulse_%d" %(PulseChn),"Set_%d_%d" %(Sid, PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Pulse_%d" %(PulseChn),"Read_%d_%d" %(readid, PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.addSequence(PulseChn, "Pulse_%d" %(PulseChn), count)

            #Ground Channel
            eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d_%d" %(Rid+1,GroundChn),"Ground_%d_%d" %(readid+1,GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d" %(GroundChn),"Ground_%d_%d" %(Sid+1,GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d" %(GroundChn),"Ground_%d_%d" %(readid+1,GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.addSequence(GroundChn, "Ground_%d" %(GroundChn), count)
    else:
        
        Rid=1
        Sid=3
        
        if count > 0:
            #Pulse Channel
            eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Reset_%d_%d" %(Rid, PulseChn),"Set_%d_%d" %(Sid, PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.addSequence(PulseChn, "Pulse_%d" %(PulseChn), count)

            #Ground Channel
            eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d_%d" %(Rid+1,GroundChn),"Ground_%d_%d" %(Sid+1,GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.addSequence(GroundChn, "Ground_%d" %(GroundChn), count)

    eChar.wgfmu.synchronize()
    
    header = eChar.wgfmu.getHeader()
    header.append("Measurement,Type.Primary,Endurance")

    eChar.writeHeader("Endurance", header)
    
    return header

def getSepDataPulseIV(eChar, InputData, MeasPoints, read, initialRead, SorRfirst=False):

    LRS = []
    HRS = []
    Vset = []
    Vreset = []
    ImaxSet = []
    ImaxReset = []
    OutputData = []*4

    for n in range(4):
        OutputData.append([])

    s=0

    if InputData[3]["Name"][0].lower() == "i":
        print("in If")
        InputData[3]['Data'] = [ -x for x in InputData[3]['Data']]
        nV = 1
        nI = 3
    else:
        InputData[1]['Data'] = [ -x for x in InputData[1]['Data']]
        nV = 3
        nI = 1

    
    if initialRead:
        if SorRfirst:
            LRS.append(abs(InputData[nV]['Data'][0]) / abs(InputData[nI]['Data'][0]))
        else:
            HRS.append(abs(InputData[nV]['Data'][0]) / abs(InputData[nI]['Data'][0]))
        s=1

    m=0
    MP = 1
    IonePulse = []
    VonePulse = []

    for n in range(s,len(InputData[nV]['Data']),1):
        if MP > MeasPoints:
            if m == 0:
                if SorRfirst:
                    HRS.append(abs(InputData[nV]['Data'][n]) / abs(InputData[nI]['Data'][n]))
                    ImaxReset.append(min(IonePulse))
                    Vreset.append(std.calculateThresholdVoltage(IonePulse, VonePulse))
                else:
                    LRS.append(abs(InputData[nV]['Data'][n]) / abs(InputData[nI]['Data'][n]))
                    ImaxSet.append(max(IonePulse))
                    Vset.append(std.calculateThresholdVoltage(IonePulse, VonePulse))
                m=1
            elif m == 1:
                if SorRfirst:
                    LRS.append(abs(InputData[nV]['Data'][n]) / abs(InputData[nI]['Data'][n]))
                    ImaxSet.append(max(IonePulse))
                    Vset.append(std.calculateThresholdVoltage(IonePulse, VonePulse))
                else:
                    HRS.append(abs(InputData[nV]['Data'][n]) / abs(InputData[nI]['Data'][n]))
                    ImaxReset.append(min(IonePulse))
                    Vreset.append(std.calculateThresholdVoltage(IonePulse, VonePulse))
                m=0
            IonePulse=[]
            VonePulse=[]
            MP = 0
        else:

            
            for x in range(4):
                OutputData[x].append(InputData[x]['Data'][n])
                IonePulse.append(InputData[nI]['Data'][n])
                VonePulse.append(InputData[nV]['Data'][n])
        MP+=1
        
    return {'IVdata': OutputData, 'Vreset': Vreset, 'Vset': Vset, 'LRS': LRS, 'HRS': HRS, 'ImaxSet': ImaxSet, 'ImaxReset': ImaxReset}

'''
def getDCValues(eChar, InputData, steps, Vread):



    std.calculateThresholdVoltage(IonePulse, VonePulse)
    
        
    return {'Vth': Vth, 'R1': R1, 'R2': R2, 'Imax': Imax}
'''

###########################################################################################################################

def AnalogRetention(eChar, PGPulseChn, OscPulseChn, OscGNDChn, ExpReadCurrent, Vset, Vreset, twidthSet, twidthReset, Vread, tread, duration, tseperation, Rgoal, MaxPulses, Repetition, RetentionFailure, PowerSplitter, WriteHeader=True):
    
    """
    Applies voltage pulses via the Agilent 81110A pulse generator and measures the pulse response via a LeCroy oscilloscope
    Both Devices must be available. RF setup is recommended for rise times below 50ns. 
    PGPulseChn:     Pulse Channel of 81110A, (1 or 2)
    OscPulseChn:    Oscilloscope Pulse Channel
    OscGNDChn:      Oscilloscope GND Channel
    Vset:           Set Voltage (V)
    Vreset:         Reset Voltage (V)
    twidthSet:      Set pulse width (s)
    twidthReset:    Reset pulse width (s)
    Vread:          Read Voltage (V)
    tread:          Read pulse width(V)
    duration:       retention duration (s)
    tseperation:    Retention seperation time (s)
    Rgoal:          Aimed resistance step per Set
    MaxPulses:      Maximum number of pulses per step until pulsing is stopped
    Repetition:     Number of Retention repetitions
    RetentionFailure: Failure in percentage from Rgoal
    PowerSplitter:  Is a power splitter in use? 
    WriteHeader: Enable/Disable writing the header into overlaying summary output files
    """

    #if a power splitter is used the input voltage gets divided by two to measure the voltage as well. 
    PS = PowerSplitter
    if PS:
        Vset = 2*Vset
        Vreset = 2*Vreset
        Vread = 2*Vread

    settrise = 0.8e-9
    #settrise = 2e-9
    NumOfPul = int(duration/tseperation)
    VertScale = max([Vset,Vreset,Vread])*3
    VertScale2 = 50*ExpReadCurrent/2
    HorScale = tread/2
    TriggerLevel = 0.25*Vread
    ArmLevel = 0.7
    ExtInpImpedance = 10000
    OscInpImpedance = 50
    OscPulChn = OscPulseChn
    timeout = 2
    refresh = 1e-1
    period = 100*tread
    CycStart = eChar.curCycle
    
    supportedModels = ['BNC_Model765', 'Agilent_81110A']
    PulseGenModel = eChar.getPrimaryModel(supportedModels)
    

    ################ PulseGen #######################################

    if PulseGenModel == supportedModels[1]:

        Oscilloscope = eChar.Oscilloscope
        PulseGen = eChar.PulseGen

        OscName = Oscilloscope.getModel()
        PGName = PulseGen.getModel()

        OscPulAcInput = OscPulChn.strip()[1]
        OscGNDAcInput = OscGNDChn.strip()[1]
        OscPulChn = int(OscPulChn.strip()[0])
        OscGNDChn = int(OscGNDChn.strip()[0])

        Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
        Oscilloscope.writeAcquisitionChn(OscGNDChn, "View", 1)
        Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale2)
        Oscilloscope.writeAcquisitionChn(OscGNDChn, "Coupling", "DC50")
        Oscilloscope.writeAcquisitionChn(OscGNDChn, "EnhanceResType", "3bits")
        Oscilloscope.writeAcquisitionChn(OscGNDChn, "ActiveInput", "Input%s" %(OscGNDAcInput))

        Oscilloscope.writeAcquisitionChn(OscPulChn, "ClearSweeps")
        Oscilloscope.writeAcquisitionChn(OscPulChn, "View", 1)
        Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)
        Oscilloscope.writeAcquisitionChn(OscPulChn, "Coupling", "DC50")
        Oscilloscope.writeAcquisitionChn(OscPulChn, "EnhanceResType", "3bits")
        Oscilloscope.writeAcquisitionChn(OscPulChn, "ActiveInput", "Input%s" %(OscPulAcInput))

        Oscilloscope.writeAcquisitionHoriz("HorScale", HorScale)
        Oscilloscope.writeAcquisitionHoriz("MaxSamples", 250000)

        Oscilloscope.writeAcquisitionAuxOut("Amplitude", 2)
        Oscilloscope.writeAcquisitionAuxOut("AuxMode", "TriggerEnabled")

        TrigChn = OscPulChn
        Oscilloscope.writeAcquisitionTrigger("Edge.Source", "C%d" %(TrigChn))
        if Vread > 0: 
            Oscilloscope.writeAcquisitionTrigger("Edge.Slope", "Positive")
        else:
            Oscilloscope.writeAcquisitionTrigger("Edge.Slope", "Negative")   

        Oscilloscope.writeAcquisitionTrigger("C%dLevel" %(TrigChn), TriggerLevel)

        # set measurements 
        Oscilloscope.clearAllMeasurements()
        Oscilloscope.clearAllMeasurementSweeps()
        Oscilloscope.setMeasurement(1, "Amplitude", OscPulChn)
        Oscilloscope.setMeasurement(2, "Amplitude", OscGNDChn)

        PulseGen.reset()
        PulseGen.disableDigitalPatternMode()
        PulseGen.setTriggeredPulses(arming="external")
        PulseGen.setLevelArm()
        PulseGen.setArmLevel(ArmLevel)
        PulseGen.setTriggerCount(1)
        PulseGen.setPulsePeriod(period)
        PulseGen.setExtInputImpedance(ExtInpImpedance)
        PulseGen.setTransistionTimeOfLeadingEdge(settrise, PGPulseChn)
        PulseGen.setPulseDelay(0, PGPulseChn)
        PulseGen.turnDisplayOn()

        Rret = []
        Cret = []
        tret = []
        Rretdev = []
        Pretdev = []
        Rretgoal = []

        Rreset = []
        nReset = []
        Creset = []
        Rresgoal = []
        Rresetdev = []
        Presetdev = []

        Rcompl = []
        Ccompl = []
        RgoalCompl = []
        RdeltaCompl = []
        PercDelCompl = []

        stop = False
        RunRep = 0


        for n in range(Repetition):

            Rreset.append([])
            Creset.append([])
            nReset.append([])
            Rresgoal.append([])
            Rresetdev.append([])
            Presetdev.append([])

            Rcompl.append([])
            Ccompl.append([])
            RgoalCompl.append([])
            RdeltaCompl.append([])
            PercDelCompl.append([])

            if Vread < 0:
                PulseGen.invertedOutputPolarity(PGPulseChn)
                posV = 0
                negV = Vread
            else:
                PulseGen.normalOutputPolarity(PGPulseChn)
                posV = Vread
                negV = 0

            PulseGen.setVoltageHigh(posV, PGPulseChn) 
            PulseGen.setVoltageLow(negV, PGPulseChn)
            Vprev = Vread
            PulseGen.setPulseWidth(tread)
            Oscilloscope.writeAcquisitionTrigger("C%dLevel" %(TrigChn), TriggerLevel)
            VertScale = abs(Vread/4)
            Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)

            Oscilloscope.writeAcquisition("TriggerMode", "Stop")
            PulseGen.turnOnOutput(PGPulseChn)
            if not PS:
                PulseGen.turnDifferentialOutputOn(PGPulseChn)

            Oscilloscope.writeAcquisition("TriggerMode", "Single")

            tstart = tm.time()
            while True:
                tm.sleep(refresh)
                try: 
                    TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                except:
                    TrigMode = "" 
                if TrigMode.strip() == "Stopped" or tm.time()>tstart+timeout:
                    break
            PulseGen.turnOffOutput(PGPulseChn)
            if not PS:
                PulseGen.turnDifferentialOutputOff(PGPulseChn)
            
            #V = Oscilloscope.queryDataArray(OscPulChn)
            #I = np.divide(Oscilloscope.queryDataArray(OscGNDChn),OscInpImpedance)

            if PS:
                V = float(Oscilloscope.getMeasurementResults(1))
            else:
                V = Vread
            I = float(Oscilloscope.getMeasurementResults(2))/50

            R = abs(V/I)
            Trac = [[1/R]]  
            eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change", "ValueName": 'C'})
            Trac = [[R]]
            eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change", "ValueName": 'R'})
            
            C = 1/R
            Pdev = (abs(R-Rgoal)/Rgoal)
            Rdev = (abs(R-Rgoal))
            print("rR", R, " goal ", Rgoal)
            '''
            Rreset[-1].append(R)
            nReset[-1].append(0)
            Creset[-1].append(C)
            Rgoal[-1].append(Rgoal)
            Rresetdev[-1].append(Rdev)
            Presetdev[-1].append(Pdev)
            '''

            Rcompl[-1].append(R)
            Ccompl[-1].append(1/R)
            RgoalCompl[-1].append(Rgoal)
            RdeltaCompl[-1].append(Rdev)
            PercDelCompl[-1].append(Pdev)

            # set operation
            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
            if stop:    
                eChar.finished.put(True)
                break

            k = 0

            if Vset > 0 and Vprev > 0:
                PulseGen.setVoltageHigh(Vset, chn=PGPulseChn) 
            elif Vset < 0 and Vprev < 0:
                PulseGen.setVoltageLow(Vset, chn=PGPulseChn)
            elif Vset > 0:
                PulseGen.normalOutputPolarity(chn=PGPulseChn)
                PulseGen.setVoltageHigh(Vset, chn=PGPulseChn) 
                PulseGen.setVoltageLow(0, chn=PGPulseChn)
                PulseGen.setVoltageHigh(Vset, chn=PGPulseChn) 
                PulseGen.setVoltageLow(0, chn=PGPulseChn)
            else:
                PulseGen.invertedOutputPolarity(chn=PGPulseChn)
                PulseGen.setVoltageLow(Vset, chn=PGPulseChn)
                PulseGen.setVoltageHigh(0, chn=PGPulseChn) 
                PulseGen.setVoltageLow(Vset, chn=PGPulseChn)
                PulseGen.setVoltageHigh(0, chn=PGPulseChn)

            Vprev = Vset
            PulseGen.setPulseWidth(twidthSet)

            PulseGen.turnOnOutput(chn=PGPulseChn)
            if not PS:
                PulseGen.turnDifferentialOutputOn(PGPulseChn)
            Oscilloscope.writeAcquisition("TriggerMode", "Single") 

            tstart = tm.time()
            while True:
                try: 
                    TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                except AttributeError:
                    TrigMode = "" 
                if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                    break

            PulseGen.turnOffOutput(chn=PGPulseChn)
            if not PS:
                PulseGen.turnDifferentialOutputOff(PGPulseChn)
            Oscilloscope.writeAcquisition("TriggerMode", "Stop")
            
            if Vread > 0 and Vprev > 0:
                PulseGen.setVoltageHigh(Vread, chn=PGPulseChn) 
            elif Vread < 0 and Vprev < 0:
                PulseGen.setVoltageLow(Vread, chn=PGPulseChn)
            elif Vread > 0:
                PulseGen.normalOutputPolarity(chn=PGPulseChn)
                PulseGen.setVoltageHigh(Vread, chn=PGPulseChn) 
                PulseGen.setVoltageLow(0, chn=PGPulseChn)
                PulseGen.setVoltageHigh(Vread, chn=PGPulseChn) 
                PulseGen.setVoltageLow(0, chn=PGPulseChn)
            else:
                PulseGen.invertedOutputPolarity(chn=PGPulseChn)
                PulseGen.setVoltageLow(Vread, chn=PGPulseChn)
                PulseGen.setVoltageHigh(0, chn=PGPulseChn) 
                PulseGen.setVoltageLow(Vread, chn=PGPulseChn)
                PulseGen.setVoltageHigh(0, chn=PGPulseChn) 
            
            Vprev = Vread
            PulseGen.setPulseWidth(tread)
            
            Oscilloscope.writeAcquisitionTrigger("C%dLevel" %(TrigChn), TriggerLevel)
            Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)

            PulseGen.turnOnOutput(chn=PGPulseChn)
            if not PS:
                PulseGen.turnDifferentialOutputOn(PGPulseChn)
            Oscilloscope.writeAcquisition("TriggerMode", "Single")

            tstart = tm.time()
            while True:
                try: 
                    TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                except AttributeError:
                    TrigMode = "" 
                if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                    break

            PulseGen.turnOffOutput(chn=PGPulseChn)
            if not PS:
                PulseGen.turnDifferentialOutputOff(PGPulseChn)
            
            if PS:
                V = float(Oscilloscope.getMeasurementResults(1))
            else:
                V = Vread
            I = float(Oscilloscope.getMeasurementResults(2))/50

            R = abs(V/I)
            
            C = 1/R
            Pdev = (abs(R-Rgoal)/Rgoal)
            Rdev = (abs(R-Rgoal))
            print("rR", R, " goal ", Rgoal)

            Rreset[-1].append(R)
            Creset[-1].append(C)
            nReset[-1].append(0)
            Rresgoal[-1].append(Rgoal)
            Rresetdev[-1].append(Rdev)
            Presetdev[-1].append(Pdev)

            Rcompl[-1].append(R)
            Ccompl[-1].append(1/R)
            RgoalCompl[-1].append(Rgoal)
            RdeltaCompl[-1].append(Rdev)
            PercDelCompl[-1].append(Pdev)
            
            Trac = [[1/R]]  
            eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change", "ValueName": 'C'})
            Trac = [[R]]
            eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change", "ValueName": 'R'})
            

            r = 1
            while r <= MaxPulses:
                
                while not eChar.Stop.empty():
                    stop = eChar.Stop.get()
                if stop:    
                    eChar.finished.put(True)
                    break

                if R > Rgoal: 
                    break

                print("r", r)

                ####### Reset
                if Vreset > 0 and Vprev > 0:
                    PulseGen.setVoltageHigh(Vreset, chn=PGPulseChn) 
                elif Vreset < 0 and Vprev < 0:
                    PulseGen.setVoltageLow(Vreset, chn=PGPulseChn)
                elif Vreset > 0:
                    PulseGen.normalOutputPolarity(chn=PGPulseChn)
                    PulseGen.setVoltageHigh(Vreset, chn=PGPulseChn) 
                    PulseGen.setVoltageLow(0, chn=PGPulseChn)
                    PulseGen.setVoltageHigh(Vreset, chn=PGPulseChn)
                    PulseGen.setVoltageLow(0, chn=PGPulseChn)
                else:
                    PulseGen.invertedOutputPolarity(chn=PGPulseChn)
                    PulseGen.setVoltageLow(Vreset, chn=PGPulseChn)
                    PulseGen.setVoltageHigh(0, chn=PGPulseChn) 
                    PulseGen.setVoltageLow(Vreset, chn=PGPulseChn)
                    PulseGen.setVoltageHigh(0, chn=PGPulseChn)
                
                #posV = 0
                #negV = Vreset
                
                Vprev = Vreset
                PulseGen.setPulseWidth(twidthReset)
                #tm.sleep(0.1)
                PulseGen.turnOnOutput(chn=PGPulseChn)
                if not PS:
                    PulseGen.turnDifferentialOutputOn(PGPulseChn)
                #tm.sleep(1e-2)
                Oscilloscope.writeAcquisition("TriggerMode", "Single") 
                tstart = tm.time()
                while True:
                    try: 
                        TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                    except AttributeError:
                        TrigMode = "" 
                    if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                        break
                    tm.sleep(refresh)
                PulseGen.turnOffOutput(chn=PGPulseChn)
                if not PS:
                    PulseGen.turnDifferentialOutputOff(PGPulseChn)

                Oscilloscope.writeAcquisition("TriggerMode", "Stop")
                
                if Vread > 0 and Vprev > 0:
                    PulseGen.setVoltageHigh(Vread, chn=PGPulseChn) 
                elif Vread < 0 and Vprev < 0:
                    PulseGen.setVoltageLow(Vread, chn=PGPulseChn)
                elif Vread > 0:
                    PulseGen.setVoltageHigh(Vread, chn=PGPulseChn) 
                    PulseGen.setVoltageLow(0, chn=PGPulseChn)
                    PulseGen.setVoltageHigh(Vread, chn=PGPulseChn) 
                    PulseGen.setVoltageLow(0, chn=PGPulseChn)
                    PulseGen.normalOutputPolarity(chn=PGPulseChn)
                else:
                    PulseGen.setVoltageLow(Vread, chn=PGPulseChn)
                    PulseGen.setVoltageHigh(0, chn=PGPulseChn) 
                    PulseGen.setVoltageLow(Vread, chn=PGPulseChn)
                    PulseGen.setVoltageHigh(0, chn=PGPulseChn) 
                    PulseGen.invertedOutputPolarity(chn=PGPulseChn)

                Vprev = Vread
                PulseGen.setPulseWidth(tread)
                
                Oscilloscope.writeAcquisitionTrigger("C%dLevel" %(TrigChn), TriggerLevel)
                Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)

                PulseGen.turnOnOutput(chn=PGPulseChn)
                if not PS:
                    PulseGen.turnDifferentialOutputOn(PGPulseChn)
                    
                Oscilloscope.writeAcquisition("TriggerMode", "Single")

                tstart = tm.time()
                while True:
                    try: 
                        TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                    except AttributeError:
                        TrigMode = "" 
                    if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                        break
                PulseGen.turnOffOutput(chn=PGPulseChn)
                if not PS:
                    PulseGen.turnDifferentialOutputOff(PGPulseChn)
                
                if PS:
                    V = float(Oscilloscope.getMeasurementResults(1))
                else:
                    V = Vread
                I = float(Oscilloscope.getMeasurementResults(2))/50

                R = abs(V/I)
                C = 1/R
                Pdev = (abs(R-Rgoal)/Rgoal)
                Rdev = (abs(R-Rgoal))
                print("rR", R, " goal ", Rgoal)

                Rreset[-1].append(R)
                Creset[-1].append(C)
                nReset[-1].append(r)
                Rresgoal[-1].append(Rgoal)
                Rresetdev[-1].append(Rdev)
                Presetdev[-1].append(Pdev)

                Rcompl[-1].append(R)
                Ccompl[-1].append(1/R)
                RgoalCompl[-1].append(Rgoal)
                RdeltaCompl[-1].append(Rdev)
                PercDelCompl[-1].append(Pdev)

                Trac = [[1/R]]  
                eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change", "ValueName": 'C'})
                Trac = [[R]]
                eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change", "ValueName": 'R'})
                r = r+1
            

            Rret.append([])
            Cret.append([])
            tret.append([])
            Rretgoal.append([])
            Rretdev.append([])
            Pretdev.append([])

            tmstart = tm.time()
            for ret in range(NumOfPul):
                
                while not eChar.Stop.empty():
                    stop = eChar.Stop.get()
                if stop:    
                    eChar.finished.put(True)
                    break

                tloop = tm.time()

                PulseGen.turnOnOutput(chn=PGPulseChn)
                if not PS:
                    PulseGen.turnDifferentialOutputOn(PGPulseChn)
                    
                Oscilloscope.writeAcquisition("TriggerMode", "Single")

                tstart = tm.time()
                while True:
                    try: 
                        TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                    except AttributeError:
                        TrigMode = "" 
                    if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                        break
                PulseGen.turnOffOutput(chn=PGPulseChn)
                if not PS:
                    PulseGen.turnDifferentialOutputOff(PGPulseChn)
                
                if PS:
                    V = float(Oscilloscope.getMeasurementResults(1))
                else:
                    V = Vread
                I = float(Oscilloscope.getMeasurementResults(2))/50

                R = abs(V/I)
                C = 1/R
                t = tm.time()-tmstart
                Pdev = (abs(R-Rgoal)/Rgoal)
                Rdev = (abs(R-Rgoal))
                print("retR", R, " goal ", Rgoal)

                Rret[-1].append(R)
                Cret[-1].append(C)
                tret[-1].append(t)
                Rretgoal[-1].append(Rreset[-1][-1])
                Rretdev[-1].append(Rdev)
                Pretdev[-1].append(Pdev)

                Rcompl[-1].append(R)
                Ccompl[-1].append(1/R)
                RgoalCompl[-1].append(Rgoal)
                RdeltaCompl[-1].append(Rdev)
                PercDelCompl[-1].append(Pdev)

                Trac = [[1/R]]  
                eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",  "ValueName": 'C'})
                Trac = [[R]]
                eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",  "ValueName": 'R'})
                r = r+1
                while True:

                    if tloop+tseperation < tm.time():
                        break
                    
                    tm.sleep(0.01)
            
            eChar.curCycle = eChar.curCycle + 1

            RunRep = RunRep + 1
                
        PulseGen.turnOffOutput(chn=PGPulseChn)
        if not PS:
            PulseGen.turnDifferentialOutputOff(PGPulseChn)


    ################ New BNC Model 765 #######################################
    else:
        
        Oscilloscope = Oscilloscope
        PulseGen = eChar.PGBNC765

        PulseGen.setTriggerOutputSource(PGPulseChn)
        PulseGen.setTriggerOutputDelay(0)
        PulseGen.setTriggerOutputPolarityPositive()
        PulseGen.setTriggerOutputAmplitude(0)
        
        OscName = Oscilloscope.getModel()
        PGName = PulseGen.getModel()

        OscPulAcInput = OscPulChn.strip()[1]
        OscGNDAcInput = OscGNDChn.strip()[1]
        OscPulChn = int(OscPulChn.strip()[0])
        OscGNDChn = int(OscGNDChn.strip()[0])

        Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
        Oscilloscope.writeAcquisitionChn(OscGNDChn, "View", 1)
        Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale2)
        Oscilloscope.writeAcquisitionChn(OscGNDChn, "Coupling", "DC50")
        Oscilloscope.writeAcquisitionChn(OscGNDChn, "EnhanceResType", "3bits")
        Oscilloscope.writeAcquisitionChn(OscGNDChn, "ActiveInput", "Input%s" %(OscGNDAcInput))

        Oscilloscope.writeAcquisitionChn(OscPulChn, "ClearSweeps")
        Oscilloscope.writeAcquisitionChn(OscPulChn, "View", 1)
        Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)
        Oscilloscope.writeAcquisitionChn(OscPulChn, "Coupling", "DC50")
        Oscilloscope.writeAcquisitionChn(OscPulChn, "EnhanceResType", "3bits")
        Oscilloscope.writeAcquisitionChn(OscPulChn, "ActiveInput", "Input%s" %(OscPulAcInput))

        Oscilloscope.writeAcquisitionHoriz("HorScale", HorScale)
        Oscilloscope.writeAcquisitionHoriz("MaxSamples", 250000)

        Oscilloscope.writeAcquisitionAuxOut("Amplitude", 2)
        Oscilloscope.writeAcquisitionAuxOut("AuxMode", "TriggerEnabled")

        TrigChn = OscPulChn
        Oscilloscope.writeAcquisitionTrigger("Edge.Source", "C%d" %(TrigChn))
        if Vread > 0: 
            Oscilloscope.writeAcquisitionTrigger("Edge.Slope", "Positive")
        else:
            Oscilloscope.writeAcquisitionTrigger("Edge.Slope", "Negative")   

        Oscilloscope.writeAcquisitionTrigger("C%dLevel" %(TrigChn), TriggerLevel)

        # set measurements 
        Oscilloscope.clearAllMeasurements()
        Oscilloscope.clearAllMeasurementSweeps()
        Oscilloscope.setMeasurement(1, "Amplitude", OscPulChn)
        Oscilloscope.setMeasurement(2, "Amplitude", OscGNDChn)

        PulseGen.reset()
        PulseGen.clearTrigger()
        PulseGen.setTriggerModeExternal()
        PulseGen.setLevelArm()
        PulseGen.setTriggerThreshold(ArmLevel)
        PulseGen.setTriggerCount(1)
        PulseGen.setPulsePeriod(PGPulseChn, period)
        PulseGen.setTriggerImpedanceTo50ohm()
        PulseGen.PGPulseChn(PGPulseChn, 0)

        Rret = []
        Cret = []
        tret = []
        Rretdev = []
        Pretdev = []
        Rretgoal = []

        Rreset = []
        nReset = []
        Creset = []
        Rresgoal = []
        Rresetdev = []
        Presetdev = []

        Rcompl = []
        Ccompl = []
        RgoalCompl = []
        RdeltaCompl = []
        PercDelCompl = []

        stop = False
        RunRep = 0


        for n in range(Repetition):

            Rreset.append([])
            Creset.append([])
            nReset.append([])
            Rresgoal.append([])
            Rresetdev.append([])
            Presetdev.append([])

            Rcompl.append([])
            Ccompl.append([])
            RgoalCompl.append([])
            RdeltaCompl.append([])
            PercDelCompl.append([])

            if Vread < 0:
                PulseGen.invertedOutputPolarity(PGPulseChn)
                posV = 0
                negV = Vread
            else:
                PulseGen.normalOutputPolarity(PGPulseChn)
                posV = Vread
                negV = 0

            PulseGen.setVoltageHigh(posV, PGPulseChn) 
            PulseGen.setVoltageLow(negV, PGPulseChn)
            Vprev = Vread
            PulseGen.setPulsePeriod(tread)
            Oscilloscope.writeAcquisitionTrigger("C%dLevel" %(TrigChn), TriggerLevel)
            VertScale = abs(Vread/4)
            Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)

            Oscilloscope.writeAcquisition("TriggerMode", "Stop")
            PulseGen.enableOutput(PGPulseChn)
            PulseGen.setTriggerOutputAmplitude(1.5)

            Oscilloscope.writeAcquisition("TriggerMode", "Single")

            tstart = tm.time()
            while True:
                tm.sleep(refresh)
                try: 
                    TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                except:
                    TrigMode = "" 
                if TrigMode.strip() == "Stopped" or tm.time()>tstart+timeout:
                    break
                
            PulseGen.disableOutput(PGPulseChn)
            PulseGen.setTriggerOutputAmplitude(0)
            
            #V = Oscilloscope.queryDataArray(OscPulChn)
            #I = np.divide(Oscilloscope.queryDataArray(OscGNDChn),OscInpImpedance)

            if PS:
                V = float(Oscilloscope.getMeasurementResults(1))
            else:
                V = Vread
            I = float(Oscilloscope.getMeasurementResults(2))/50

            R = abs(V/I)
            Trac = [[1/R]]  
            eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",  "ValueName": 'C'})
            Trac = [[R]]
            eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",  "ValueName": 'R'})
            
            C = 1/R
            Pdev = (abs(R-Rgoal)/Rgoal)
            Rdev = (abs(R-Rgoal))
            print("rR", R, " goal ", Rgoal)
            '''
            Rreset[-1].append(R)
            nReset[-1].append(0)
            Creset[-1].append(C)
            Rgoal[-1].append(Rgoal)
            Rresetdev[-1].append(Rdev)
            Presetdev[-1].append(Pdev)
            '''

            Rcompl[-1].append(R)
            Ccompl[-1].append(1/R)
            RgoalCompl[-1].append(Rgoal)
            RdeltaCompl[-1].append(Rdev)
            PercDelCompl[-1].append(Pdev)

            # set operation
            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
            if stop:    
                eChar.finished.put(True)
                break

            k = 0

            if Vset > 0 and Vprev > 0:
                PulseGen.setVoltageHigh(Vset, PGPulseChn) 
            elif Vset < 0 and Vprev < 0:
                PulseGen.setVoltageLow(Vset, PGPulseChn)
            elif Vset > 0:
                PulseGen.setVoltageHigh(Vset, PGPulseChn) 
                PulseGen.setVoltageLow(0, PGPulseChn)
            else:
                PulseGen.setVoltageLow(Vset, PGPulseChn)
                PulseGen.setVoltageHigh(0, PGPulseChn) 

            Vprev = Vset
            PulseGen.setPulseWidth(twidthSet)

            PulseGen.enableOutput(PGPulseChn)
            PulseGen.setTriggerOutputAmplitude(1.5)

            Oscilloscope.writeAcquisition("TriggerMode", "Single") 

            tstart = tm.time()
            while True:
                try: 
                    TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                except AttributeError:
                    TrigMode = "" 
                if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                    break

            PulseGen.disableOutput(PGPulseChn)
            PulseGen.setTriggerOutputAmplitude(0)

            Oscilloscope.writeAcquisition("TriggerMode", "Stop")
            
            if Vread > 0 and Vprev > 0:
                PulseGen.setVoltageHigh(Vread, PGPulseChn) 
            elif Vread < 0 and Vprev < 0:
                PulseGen.setVoltageLow(Vread, PGPulseChn)
            elif Vread > 0:
                PulseGen.setVoltageHigh(Vread, PGPulseChn) 
                PulseGen.setVoltageLow(0, PGPulseChn)
            else:
                PulseGen.setVoltageLow(Vread, PGPulseChn)
                PulseGen.setVoltageHigh(0, PGPulseChn) 
            
            Vprev = Vread
            PulseGen.setPulseWidth(tread)
            
            Oscilloscope.writeAcquisitionTrigger("C%dLevel" %(TrigChn), TriggerLevel)
            Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)

            PulseGen.enableOutput(PGPulseChn)
            PulseGen.setTriggerOutputAmplitude(1.5)
            Oscilloscope.writeAcquisition("TriggerMode", "Single")

            tstart = tm.time()
            while True:
                try: 
                    TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                except AttributeError:
                    TrigMode = "" 
                if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                    break

            PulseGen.disableOutput(PGPulseChn)
            PulseGen.setTriggerOutputAmplitude(0)
            
            if PS:
                V = float(Oscilloscope.getMeasurementResults(1))
            else:
                V = Vread
            I = float(Oscilloscope.getMeasurementResults(2))/50

            R = abs(V/I)
            
            C = 1/R
            Pdev = (abs(R-Rgoal)/Rgoal)
            Rdev = (abs(R-Rgoal))
            print("rR", R, " goal ", Rgoal)

            Rreset[-1].append(R)
            Creset[-1].append(C)
            nReset[-1].append(0)
            Rresgoal[-1].append(Rgoal)
            Rresetdev[-1].append(Rdev)
            Presetdev[-1].append(Pdev)

            Rcompl[-1].append(R)
            Ccompl[-1].append(1/R)
            RgoalCompl[-1].append(Rgoal)
            RdeltaCompl[-1].append(Rdev)
            PercDelCompl[-1].append(Pdev)
            
            Trac = [[1/R]]  
            eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",  "ValueName": 'C'})
            Trac = [[R]]
            eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",  "ValueName": 'R'})
            

            r = 1
            while r <= MaxPulses:
                
                while not eChar.Stop.empty():
                    stop = eChar.Stop.get()
                if stop:    
                    eChar.finished.put(True)
                    break

                if R > Rgoal: 
                    break

                print("r", r)

                ####### Reset
                if Vreset > 0 and Vprev > 0:
                    PulseGen.setVoltageHigh(Vreset, PGPulseChn) 
                elif Vreset < 0 and Vprev < 0:
                    PulseGen.setVoltageLow(Vreset, PGPulseChn)
                elif Vreset > 0:
                    PulseGen.setVoltageHigh(Vreset, PGPulseChn) 
                    PulseGen.setVoltageLow(0, PGPulseChn)
                else:
                    PulseGen.setVoltageLow(Vreset, PGPulseChn)
                    PulseGen.setVoltageHigh(0, PGPulseChn) 
                
                #posV = 0
                #negV = Vreset
                
                Vprev = Vreset
                PulseGen.setPulseWidth(twidthReset)
                #tm.sleep(0.1)
                
                PulseGen.enableOutput(PGPulseChn)
                PulseGen.setTriggerOutputAmplitude(1.5)
                #tm.sleep(1e-2)
                Oscilloscope.writeAcquisition("TriggerMode", "Single") 
                tstart = tm.time()
                while True:
                    try: 
                        TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                    except AttributeError:
                        TrigMode = "" 
                    if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                        break
                    tm.sleep(refresh)

                PulseGen.disableOutput(PGPulseChn)
                PulseGen.setTriggerOutputAmplitude(0)

                Oscilloscope.writeAcquisition("TriggerMode", "Stop")
                
                if Vread > 0 and Vprev > 0:
                    PulseGen.setVoltageHigh(Vread, PGPulseChn) 
                elif Vread < 0 and Vprev < 0:
                    PulseGen.setVoltageLow(Vread, PGPulseChn)
                elif Vread > 0:
                    PulseGen.setVoltageHigh(Vread, PGPulseChn) 
                    PulseGen.setVoltageLow(0, PGPulseChn)
                else:
                    PulseGen.setVoltageLow(Vread, PGPulseChn)
                    PulseGen.setVoltageHigh(0, PGPulseChn) 

                Vprev = Vread
                PulseGen.setPulseWidth(tread)
                
                Oscilloscope.writeAcquisitionTrigger("C%dLevel" %(TrigChn), TriggerLevel)
                Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)

                PulseGen.enableOutput(PGPulseChn)
                PulseGen.setTriggerOutputAmplitude(1.5)
                    
                Oscilloscope.writeAcquisition("TriggerMode", "Single")

                tstart = tm.time()
                while True:
                    try: 
                        TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                    except AttributeError:
                        TrigMode = "" 
                    if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                        break
                    
                PulseGen.disableOutput(PGPulseChn)
                PulseGen.setTriggerOutputAmplitude(0)
                
                if PS:
                    V = float(Oscilloscope.getMeasurementResults(1))
                else:
                    V = Vread
                I = float(Oscilloscope.getMeasurementResults(2))/50

                R = abs(V/I)
                C = 1/R
                Pdev = (abs(R-Rgoal)/Rgoal)
                Rdev = (abs(R-Rgoal))
                print("rR", R, " goal ", Rgoal)

                Rreset[-1].append(R)
                Creset[-1].append(C)
                nReset[-1].append(r)
                Rresgoal[-1].append(Rgoal)
                Rresetdev[-1].append(Rdev)
                Presetdev[-1].append(Pdev)

                Rcompl[-1].append(R)
                Ccompl[-1].append(1/R)
                RgoalCompl[-1].append(Rgoal)
                RdeltaCompl[-1].append(Rdev)
                PercDelCompl[-1].append(Pdev)

                Trac = [[1/R]]  
                eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",  "ValueName": 'C'})
                Trac = [[R]]
                eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",  "ValueName": 'R'})
                r = r+1
            

            Rret.append([])
            Cret.append([])
            tret.append([])
            Rretgoal.append([])
            Rretdev.append([])
            Pretdev.append([])

            tmstart = tm.time()
            for ret in range(NumOfPul):
                
                while not eChar.Stop.empty():
                    stop = eChar.Stop.get()
                if stop:    
                    eChar.finished.put(True)
                    break

                tloop = tm.time()

                PulseGen.enableOutput(PGPulseChn)
                PulseGen.setTriggerOutputAmplitude(1.5)
                    
                Oscilloscope.writeAcquisition("TriggerMode", "Single")

                tstart = tm.time()
                while True:
                    try: 
                        TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                    except AttributeError:
                        TrigMode = "" 
                    if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                        break
                PulseGen.disableOutput(PGPulseChn)
                PulseGen.setTriggerOutputAmplitude(0)
                
                if PS:
                    V = float(Oscilloscope.getMeasurementResults(1))
                else:
                    V = Vread
                I = float(Oscilloscope.getMeasurementResults(2))/50

                R = abs(V/I)
   éç6ò®ı„y›ZÓC%ªã3ñõssİÂá©°FÌ
íÿ5¸/
¤?Wh$Öş«Éf£àò‡¶H"›>Uÿøg:’«‡w³Mô¿Ì\È²ÍM¬LÁ.‘«Ÿ’şæ@K²»ÎáŸˆiAPD6‹nßT`P:„+gØ“‘¶O6Í‡bQFF 98–Yô1¿lHÎ·,N¥ÌC-™·ç½Puùş¹K£N¶ k×éÃÙ«®Æ³í§zƒ„õ`;P+D'KbQœQûD	8A°ğ¬è%ÏÑ[B=/eä3uíß5 / $8#jÂ…E2ÃÛÈ¡NTl~'¯^”OÔŠø_:€+'r¢‘˜TRÓßßhd}`y©h±ê«8’,J¥Ï,9åêó7=î©´F½©[r³nuŸ'â3“ùõÃ^ád¸½¼àÂJQxhè®3Ïë37mî•´WF¼
Éÿ.øV(æE†.×‡°¦¬;·œrßtÅeÕÇ'*¢§‚¸YŠ‚ß 2°íqÂæLºş9 èØâ‚ˆëé‹uİ¾Dò_‘_@?H(¦¼BÉÉ®îÄtVÄAÓº]I!ZÀzZl?§¸ÄU«GJº?qèv±½/ €Yß:·•·
|È%Œêãº>M÷M¾ˆ]XT‡yšè”\d¹€p|¸`¨Ï¾.(°Fµx¸&‹£5²4éi©ÖÆæêò÷=¾©ˆFŞŠà-tE`ld‰ìzQ¢Ãy[âAQ\dx¡-¼d‹3ºßğ<)ò¦ı‚ù™ºÒË%¯AC¸>8Nuµ§ı:;‹ÿAjk’o¡xßE  ?x(¦³Íù­º±Ùj\gmçN€àf	J_nªX7B®‰„^Û@cHÎ´l
6„Fôõ÷L_‰>¹W{±°–;zš2RÒ××£pµé"ÃÃXÎwu8¡–ñ”D±eí´÷b?÷NNäB¾!5Ô@åÄ0)¢ õÂªAëxÙ®“ÒC¨jq"!Ğ¥`Y÷²Ÿ½»y:iÚgA½2ƒo`x£ ;’ÂW åîÔ„kQ§õqmÌÅI\?±WÃß˜Ê·ŸŸâqëÒvéıóvnr¿]ˆ¸PJ„|3-¿ƒ¶©¢³AœÖImoJ”|6™îÒôe¿S»Øp
8PIå“ºl$«¤¼/8kbÅ#“’æÒ¶\ğ4ŞŞGÕ“Á+T…Î˜Ö«v»Ü& „C+¸H _Ïµ»‰ÿ]úÏ=k'ÿÈ’š¤Q„ıšfãÔğkPŠ¾qªàöˆlµ7Eì	µ•­b¬“§¹4pş¤Ép_­MüµNş|ÇXo@âHÛ+“ö'Ÿ×ç³ñà·ãˆnŞ”`WP„:Ûk#WaÆÂjÉu}³´ÁhT‡vÚãqôqT+ı”Œ†¿âi.‰ä^ó@}È®²ÄM«M‡Mš“TÓñÃpæ–Í¾¹²g{üéÄßS Xm3´`ıcÄ+÷Ëµ°O=ıé¹¶ÊÎï,t%ßc à4p/vD¢3[ÚœcÑôdSXÂ»)‹fßRàš;+}çY²‚Í™­’Å•«vºŸ]a'XZ2 Œ>Aı_û_;@+H'N¢ŒAâQ®„D[KCOIÌí¹ñXî|ezOæ®†1´ì–‚¾}6gñX‘ô Š˜Ú<.©äFóJıÏ9¬*·²e@â=‚ˆ™åG˜ÇãŸç9¤Àå7,.¥äC3IíÎõ¬P”hgÌ$É^ÍPZ;¿’–mù¿’ÿZ™×mùÌäV”¹Iıôy¿ZÈ.¹ä:¦n‰Nè¨Ëá®YÃ/ÇŞÛƒªñ?S-§×ºŸ~q»çqIÿA^$µ|PÄ1èn´V„Y²ÀjşÕú¥ùÁø*¸eÈQìF·|ñ±şº‰Òœ'S G"ÈclS4xm˜WPDFÉˆ,g3o6Öì$7!¬b‡q^_yÀS®3xâºÅÃ9F9nÜ»–¾w¡IQÿDxZ¿MHºûªHgŞ0—Ò,dƒ#ÑV‘g¯maÛtÕ#˜ÒbÔ«ÌÁ²èMóÁİ˜†K‘ĞTdSz…“^b7$Ğ|¤k>^#õ~àpzÙlÕ Æ}^¥ÄìŒ@r‚“è“4+ÙRäO3@­dåö\„±-7‚”’Šb áÛSÌ¡\ø~ÈA„¹|7éÖ@Û£¥ÃCôÿv°[»ô>^<£	øŒ¡¬¯Š9¿bëÄSDdnÂîÏ˜Ab¾IGJBã\^’pô©D¦›mex-ïª;ëí¨u†×_‘waí$áƒI+¹Û;Ì¤c{»ë±«EÈ[†ï*n‘p¢:3ÂÒÄİ“·TóCõºÁ{‰n%43 ÛÕ’\µŞÏ $eT¤rb ít¦uÇnP”¤rlçåÈÜVºÆv£Gü<ï(Éâ&·Ç5Â—…—½Áó•Gª¹~ğ×óÊ{0l{¬ƒpø¡FTjş%O_}+İKêwÍn[ï¤LAT»¾ı¸Ë<O c8#Ø’$³ÛÃÄáe@’ô#·oå|½1?-A¡nû<ß×Úç…íëı€Ó«Ø}mZZÜ;!£%6[Ö><S·ƒ2èÆrF=ïÆZ
8Ø­—é\±m·=6WŸşï´®y˜Ò¡ÄT¯4­Ô"XÜîg+R§ÇÊ]Ú Ş\ôaÆ"İÀŠlóõ˜Ğ¨ÔğÜ›ÃdFîx*,B}ÿÊ¹Î}ÀGpn4xÄL€ğ´úĞ{$S&2˜–oê DÏw5uCÿl×¯–rm:­»$/|êÖÔÌ1>íU±`)ÿ|g—µ–p«°Á“(U®ÂsèñÀ«H><ßU‘,Ğ‰{Ôá†}Å½· q¿\†›» OÈy{yr ëìñªüGqë«Bf4î;TR52“\¾$›F|ğ©
}!¾ ù³uØ·Nşqüˆh;˜ºÄ†ïÒ£twå¼ÍJ×¹JLôuú(ÌSŒ¸¡ I2yÑëï³€í½3ÃÛ’m·U?te%ÉMŒq,ïT…‡zd	Ó°ôpî˜¼QÛO·:=]ßèZ ïşë8w"ÛÖTæ*¼^{·g?¹læ5—À¬Øó™ZêÊ Œëµˆp^RûÈæíf< €.Ub˜’üÎYX¿¾\(x”í«¬¿©(cÉ++“_XÀ´^f³Ø™ÎâõıÛ
Ğ	¤ğÒ=j“»Bš¿©ê½ú:Mİd[¥/…û;;.“ô†Ùå„jUSëå’\¯ñ2GŠ²–5OØ0QìÊd®\÷EvşJóÄD‘'’½•‰ß[—ô#¬¥åúAL4<Ä­¥ß¬šu%dÄ+fgö%à	R‚xÓÓG^¹öÊ0şmwæš:„ádÇjûòä}³Èƒ™ìóˆ
¸FxıæÈ™*~}U#÷×…A£A_ÿp?Bü{<®ßªnÌ¤U;sk“Æ¥DGƒÌ€I6|‡ ê˜Ê/Ãâöñ¾´8Šß¾]t•¿nzcg`ùTÖ'ÍOªk?j™äêÏìª´úËó^<*š*LËË0ol\P¶3{Ì¦ÔO•;+ZL‡á:ÕD{§à¥ˆ³¥šó½Âôi,WØ*×àÓp
4S_ë:‡ÿ¸;Bî>ChŒêI×7”Ù«ì±,ÊLßû›Ükl×àØNI³şõ Kxœ[¬Í‹îj‚?cÃ.YÜ¿Ü¤çr±•É Ù•ªE+•
ëNˆ>ô‡Å*]\æ¹ıÀJÙcâ¼<“oÒ+'á£…Uèr›± ‡°zJ-Š·ğçO¥ºlü`Ø¹5ğ8|*™ç·ÖõÎ[’{‰¼!8×6#m@®·á€Tî{‹¨ï7‹oRÑrS(¤œ”ıf¾’€ïÃAµSº ¼?Ş“Hñp†<
ÓĞÒ‘ïD—Ò©ÚkŞk˜%.kˆ‘”XÇÍßŒİe=´V~qäjV¬najj–1Í–Ba¼±2ó_u`×¼ÊVğüt¼¼v¾%{—uVíè™”£8âÇ¼u‰ßP¥g<eR`ŠóAqôÜq…Ÿ¤!QT±5Õm¸ŠùZYüul¶÷²è¸yÁ|Ûâ‹E,UgX‚ûÜØ^•{ä”	8j·eIføº€à'€k-Uú‡;uş'W®åúL
r’]ç|»øTz‡qƒs“Ÿ å°TŒ÷üa¹Ğ`ä3|k–·¢½ô¶IèÏ…[*y¦I)—Ìl‹ùe÷S>…è[bÑ7ÃşbçQ²„M›M“M•ÍÙhÁéßS’æ‹şãøÉ—v;¡f +,&Òg“dü !ïKŒ? gnë«ÎÁÛíƒŞê­rsgópmdÎ¨#XÁ;.ÜáI«ºuõ‰xì….$"ÔäÑ…¨fƒï¤ÊÏoöd
n¹£Ï·g@N‡kêöGº8›D DÂÍ®%É ÍßZ[°Œ/C¡F¦ŠÂß) &À"è!øåŒE&x­¸ÛÆßêî²eÂ®é yËZkL$gr¡İnˆÚ¸PJ x÷ıU†ğáO¿.Vdkìè­ sÑ••Ijc‘Jo	 ŞÔTƒbc¬üCpL§ö„ª;©İ/iÕšSŒrf&ÔöıŠƒº»ª6*¨nƒï¢°mYãëFoÕä¹N'Jë
L„ZÏ¯‚òpGªfAÍÈm®•„WF³JƒŠzàlË¦`#l`ÕŞ¢qÎ¡¬ÄJØ¦³1hR¥Å$	ãúşÈxê„WÓæM†6)a‡sı¸²ˆÃ{âÙ?G£Ïç1<I"Ì¯HŠhÙÉ¢îÁ´hOVŒİĞá»0KlUü9úªµBl6âB8jôÛãwta¥™1!ßr—˜çdÃ´ÿOŒ_«Í·úÁD‘ÍãèÀK—9SÜ?J ¾39¾º±tµÙø§‹? HsÆ#&÷¥&Â±Ş	ÃËIê3Š%¶~É%¨TƒöäÁÔg âÙ‰ˆïí…D`X_¸FÍ úcf áwS Àó®âÄq«\GAÊˆoÚu  OÛ¿¬*[«ÇV¯×KO÷CÉy¡é€ò×æ8}ÙÙ&íÑµ KHıƒúzÄlĞækP‰3;ÖàÀÙàSîx™oÎÒ8…Coyçâ¹Š¢ZÇ
¯Äÿmlõ|7hğëÑ±íÉUºSëì İ4Q19ìqğ§‡Fkµ 5%'S¼ø¤|
Ü„ÚŒwñwhÖyôÿs8ê±· ø›ä€€×yx×f&œg€]¥Á'Iâ
şŒxÙÕ‘§M§M‚‰™ÖÀa`]âŠ†d©\'Ÿ£=W+ÈB%‹íú>¹f¯™Æ\ŠşQİ
Óåºó=ÿi¸S’õª^ <'œSºÓ£Ü³cëÚèc6‘îÔtg_R€k×uWu‡_€3-ò¥½ƒ#™şÒøeº“vª%U_ò°ZGü§ÃrægtÆ„.rì,«˜ª˜©AÀÜˆÈß¨xœ…ÛcqÑÜ-'Ó30–~j-çA2Î@Ù}ˆ‰÷~²˜M’•Ù|×ìVÒF_§’~` ¦§ÂÖüŞ–Š~„fdc¬<…›&l9Õ¬¨e2à­Í›R2‰cdä*Ëşğx|™ó¹´íş
Õ?)Ìeâ<€ƒ})!¿â×1¦¬BÅÉía•d!“[Æåk€àiJ×œÍ\œ´ké{½ÄI«NÇLj×¦åĞ•C‡ÂÅ©«Çzê›7nµÔO'cÙ ­Q÷A¾GNŠ
PÄ»¤yƒÜÖÓ&cíã57îpù›}4hÜ&ªP¶2ø„2ïs¸2ÕÖ´´á»øñ¦âNŞR$E1+Â‘ /ñËâA&hŒ ôWEcƒdGße~ky¢È ÀvA©²cÅäu?pöd_5ÒC‹¶ĞzúèÊ=)ö¦şÂøiº–Ëï3¬]º ,sÿ·I%˜‹ëí˜Û…(D&‹bßQ @;H+N§LÌÜ®Ì„f^ OEÅË"ïht_yÀ(5.èc‘ ¢Gl
•ÿ86ª®Ç>él¿JÈ.¼$IãNñÌ|mÙÕæ¦Uó¸PŠšNœ1‘j[eÃÕ&Õâa>¢¨Ç‰˜^Tuœ™à0¸kMp|ïiå„‰2–™ˆŞñ~9Œø½}ÅêS|;Gçelët ÍÄzßE,$û›¤ác™¦¨çÎÇ2f‚L¡ì5ç[k9rb¨Š“Ám‰³¡T3`¡ÿŞkıÈy®šÄS+EçK2Ê5ßPÁ£ùÚéÏƒ³FÃJéÏ6ì.õä3X-Â¥íÂR˜úÿû3¾?GUÃG 
©ÿ85ê¨÷6şéG†Pö!ó`}Ğ¤]–9ù€Òƒ[¦ò3Ì¹ÍóŸÊì2œÁK„ºDTG7ÙKWî$‰ò·`q(]P¢ôrŞğ””‹ *a]Çeª“OP»ó~\ºrÇ¡]¼|Š:à\Ë²™hMÖã¾Ê Ë¾Lù¾aú/J/0%E‡¶¡Í7šÛ²A|sn%»	#%ŸÜ!RthmßÙOCí7†]«·xLL±_è^Ğªƒ•‰=—L2 ÉÑ‘äÚ4E“ÿ¿`n/EG—n|"íW¾`Î,\%Áã(qæœrûİ¤aƒ4…Zëd·Jäƒ,Yå„¼{½¨Éû Íæ,ÁÙc¯ú	JusùÂúé»6ËnÅTt_z€g ôÇ¯¡› SxÚ»#aÿ=SVò=N&ï<¸J¹Š[P>ó­x‚ù–Ñ.Ôè<–E|‘o.:†×«Õ¶õ¹±óóÄ{\Ş7]S!€%/o2Sß ĞÖ Då}Î$f ¯ÆÈ:­Eu¿¢Î¶)8[×$iÄæŠBôyiÍ'ñ¹FŒU°ÄïÌÊbŒOØÇ¤uƒ_À2è-¶¥Y>½Ÿ²#‚Ã‡å¦3h¬Y¸N¶¿L3~­\J²‰“-•a“#i¸Õ)˜Q)7éŒèÛQ¿4‰Å­Vbxh]íÈİ¨(İB§ŒharéšÍMPà¹¼ñ2ºokë0ğØ›W(ØÛÏ%å¦HùŠ¹)z¿/¯4~‹ü&¾™V/«bÔçœ%”«ß~§cÜì‰Yò±½ŒIÎÑ¬d–i†-ij÷‰s"]ïå´NÏÈcÑu«lGÑÅ—+’¨fÆîÅ³ã@²+2Ğ–™—Ì—BXlÉ— 3Ë/¡KZ¦s@“-[ƒÅ†ë÷s>­	õÁL
•ˆüÑÖ•Àµ·¼<IéÎöì~›—1g²!’ U€:Ñş_ê<Â™™°é7pú|ÕïÎ	 ¡ç r¸Š±ÖJP^‘{Æ'ŸRô…ùvOëfgÙÍ¢íµ˜OŒ5¡|õlOrLwX¥ÿÁ¢xŞ… [oV,iş‡Fe»¬f 	[aÃP/‹Dë8÷°€*TÅöÃŸœå¨“ª^Ø b¸Š´N}4ş¡œ®ÈÍ_‡%*[>÷x~š˜SÃºÉ?Xh|˜¯t…l¬$¿"Ê~-ÊCƒÂÆéªöÇ>ê¨wî‚>%c|ÙôbÿQ¸J»OL?	©Y÷½“Ék‚Ødb^…Àİ'b3ŞŸ Ö/$±b~•sÓ,–•áPZ·û]å<
îªThÙ.ÃêŸ´Fˆ4@£gßªÁğ¬úÖºã/•Ğo:ìÃr­ãqÌIY·°% æE“-–ƒ*}ŞîşxW„ûĞı»9‹jßW  :Ànpd#òÆÁüæCŞßˆ™l}{Îstßq @1È,n¥ÔCc¶Ïñ|SÜ—në]·HN‡LSMÂ­5ÂèÎ‡Ú Ïç32­í…µ›`F(eŒ»Fµuşn	@^ñraˆW¹·ü”ÿx>°¨S…²zg.3Ù>ĞW•1«D—t!dÓ®<Â¶é‚….óØmbrŞ¹38]Y€¿€F‡ı©o€?7ËUÇã”›d‘ ÏrS,Úİ^G3·A*ıFF· [Øl½¥÷¼úŒ
„ˆ|ÖÉ†W-ÒÙ†à|Úşq¨¶Ï+HŠjî¨4ÈØ9ˆ€9,€°”ò)¬…Y¿è~‚`»œ­¶³$Íüm¹´Ü s@Ã-‘%Ø€Yğ¦B;®LîèÄã#Ş€bşZ@æ¡çMo/=æÙ<Œ‰¶&È(—
>9÷jşönÂô´÷³rn¦üæGËªM-¨•qßgÏs.»¯³á¤!Î~ñŒŞ3€ <*ĞÖ˜TCGI«Ø¨n&t‹l}•Tloñj›>$‚Æi]º?*ª•W÷ï
‡}êÙVÉ>è" ¼¦ÖÂæˆä±™ø¬Á9‚WLn)j_‘d§9sk)IZ¿:ÊÛ¡M &X$ZO?¤®ÜDaáPoDM8-^Ö öØúQL57.}O”ı"ÇŒ¦®4[oCT	Ç~£Şw^Ûû˜=FId8º´LÏ¶/ÿ{8j³WÆ½ªÉÎhÚè&MY‹–?¸c8 ôİ^ù@b’´±LTÇ}ª™‡Úµ£n>†è„{í¼
xÈ&¯¶$à¿CÖ—$“¨Ó¥òÃ=©é†öÚşã8qêı!V¶ÆATPxµ-³$™¼ tqS÷Ïûç½­‰…Ûc C†nJP0,;eëS7Eîßr&7*üİ)Å8äFr^<iğü6ùîúô{y:¹„ê½vziêlV}½iT^¶^3¨ñ*wxš°Sıû9»jËW/â
Ën$ªc¶ç¿Õõ¤Ï Ğ#ƒ›ëqc@ÎCù)üagß>ùÉº•YwëÆhåümNªGlÇkè¦€óÿ@È0¼Ù*^Ä§ÑpH&‹¤«Ö'ˆ÷?¶3b_é}}Æ™ªÒÇ%ª£ú¸{
›X5–éhÍjÛããª6íğ¨İ™¡’ÀU¨ººË/drµŸİdİk{àp;\+AçHrıÖ*DÃ×N™}eå´3ñV@9ì)µæÏ2ì-ğ½ÌvLyñŒò7L…›³ê?†%ü4yïZô?yè˜üpˆÂm¶•×f±³š"ß@ñõFc-®³KLÛ­
ÎÑ2H²‘”Ø–•V›å¨¢xqˆ®²…q© 'ÌÍ¿mVüBjf’üªw¾_¡ÿ?\¾nâà‹ ¼üåï!öâ¼3K/¦ÿ@:Êéíô7}¬[GˆzœYÓ ':àiòÔ?eªÑÅæ©ğ>ùª¸ÈyìX7 lz×äp1î’¶—LO5íŞ·bŒS_ø{xY˜@JöÍü/{&Ù  âûsyŸğw~ÜZ£Ã:«)Å¤)Á¤*¨âœÄâ°ÿáàúÊH,,	O{ã‹Mè¨Mî)+ì« †ô0lX]jíç«	à„D1Ø8&dmğrF©ª^¼H°ª{T=|Äá—Jé¼¥ªjø(	4İA—á©WKpµ¾´|Š¦àgCèkMš~eî:ËTÕ[Â¿™¡hü¡…³l¤(ìfÌ£şÂ+_İXî´İ°^¤6šQ%şšÁ"PÎ·DÏş¬­šõ=¼Q?„û×{ê4¿ÚˆöÑJß7–nÿ4×.Ò†Leòä²Ã·ÒöÖ‰c«'¯ïCO<CZ¸¯ÊéÆƒ‹{ev,#s™t!HV!q•}9Pq6$ØÊNdSuÅß+ `"!–"UJ:ÔJw7.ÛÔÆ”X
âË‰š,0pœparã68‘0y–l’šk`¬÷1™ıIdÒş)Às˜q¢aõÕÑ_Ö)ÙË–“˜¡¦¾G¼ªìè˜/{,a3 Œa`qr”o%3RP`ÍoÛ%c?¦–$rW(ÑÃ™ÓhCaûqÊJ\ôZ0>ĞvóãÇŒY?1˜¹4aÒí`„bM º<†Uî|Ç/ÌÔ]çÓĞ®’«Ğù˜Fkú,ŒTê´ L]¯H¹©Ã´ÚiĞiak,5‘Ä„*]F¯ÊÛ/#F£5)ƒVG}­u1Ô,ge¢ÆiÆ¦R¾í0‹'"Ø'–ˆGÅ÷ş›5‚iÚ„×4ïˆòÁ½¨&ÕÍª‰/r”ƒ,>	\5ÁïG'eÖ.œ^÷w?Ô~²0!Üİñ©ÔşIJ—úÉ».¤7,4:a¤3dgRµÅDOd8®Ğ>ÂŸ1‚Pêsûƒ(ä?†·ÎÅ±×³-å³ô]¿2Í\^ÈÏOÅùY´×Ã vÀb3ÿ[‘êk<iö–şÖø¿Á¾A»DëM¶ÊAcÎì\&„‹|7oÔvœ;§`B	”M’<fÆÇš†ãçU»ıéÂÉ—}Ùd#Sa—•8aC7!Øš€(}P„5é*@aÇ?ØtRbáØÊ€gIO“U‚Uz;ì³zÍÛ-£eÓj ³×=ã¦Ûb—é£ÄzTAˆ\
Ó…,–¹–ÊÖï&ô"ÿıQ´_Z0o\é¥¿¹ê±€×± S`¢hpn3†e›SEõË^f%aR£$„¡3"ÑP—ug?FĞ¥—oSú6µë¾îw+^§2ÜLÎÌ•!Z‰|UÙÇ"‹èúE
¸^î†Zø‹«.6Ä:“Äf‡´…À^æ)«Ù˜bÒüäÌ3B¥Ë­¬=3©Ä&Db² dŸXPéxÃ#hÆíŒ¥m ¦ÒÄÑÉñ úËVª(ôHk68ƒÿò…í™àâœM"|U¢7úÀT~ÁHwNá´Tç+	úÆMj¤w¬_ü¶Ï§=ğDı~€¯»¼´2G¿ùúüÏ[ys6­@6å«4?{´f4ù’I£+T—+*ÖÃ]:÷ªÉ¨
¿Çër÷/ñÔÆ^‚€Y˜Ò¹¥ŠÃmf¥h¸"­®º¾d[iE­³ª²b>@›WFÇŸjxmqª,ËìduÓ_K•njd´ =†ûtÒ£€)¤?±Ş¸Æ“—
Ö¿V‡u«óÇXZø®S¹Î£¿otÔh3gÁaÆ€mR÷?“Ûa-fÄ‘z§y…ù›M"q’cĞ¦‘#½\'ÏˆÚ"—›Ş WÇº>´:8‚Õ(–Ò°-öSE€¼ï|Õj“ÙwY¡¹–;ºT7ë×ƒ×mÇ@Ú:WÌïĞ±X#(‰ÙçëŒû"F¾ŠÈ],‚r#B¡Éƒ'#·ÁÓ	A%‡Â¸§Æ¶yøriçïÓ0šÊ]I ¦ÿk÷eŞç˜Gà~õ~Ÿ'i«óøÇIı€ ©î‘„*»(4_ê4×JI53e„åş<JÉ»–ş$
0O‰H!õU‘GJ¿?{#½˜áËœ¯<-œ„3a@‰uß)t]ç?½c‘öÔ~çXÑØÍ‘ÔG­1QÏíµ
Ğ?$(#f¡¤’ ûVRµçÏ)&]7¢ wÑÇ›5“oÔ7'ğÑ ÓHK”Ö,³†q-Æ<õöÿ>Œq*¦†Ôë™‘fd¤¨¤3°nî¸Ş¿pmï6¢®Á‡;×™§ï,´<A}‰4ßå¿3~»ñìCÚºå0héÙ{=ÛiÕ“’›)·Û{Öµf‹Ó²İÌQ]çèMÿš½Å TiõHÈCÔârœNÔ8€ÍÖÑ‚Yìåãºí[0ê3Le4·Ø„Š6'İšÖ}+F§JªÀ{ïe®¡q®\“ˆé)‰‡°×&µ–xëk ·§vy(¨®wĞ¯µCö\}&ƒÑ†äZ’p¥¬ø³ˆ~öXgL‰£^Ô  FóûÃfX¬r}¯ä·?W¨¬*ÙÁ.÷d~ü«ÉyóëƒG¡¸ıyˆë0·p¹UñÇS9ê§SªÙº…=²iëE˜¶¢… Wü²æÍ²¹ÄøØÀDÈ4LïV^_@JMtìèÛ–N1R0¬3U¨©|ô+I?VxœëDwª„ôDK;VÏ]È¬Šø}zÕx\r%cÀò4YEôà/d:“k×]&¢ĞñX1ÛŒ¦í>ÜYâÅ‘kfĞÈÿ=¼†à+CÒQæ†ğ{¹út¤ÙÈŸ \0Ê¹G«U‡GjßÿLH—xòDÆ¢›¾à`°\ïzœ¿¯òÅh^{ğ¬Ûìó€T)x¼"dNà"YO°=M‰±I
‘ÿRZ®ƒZøAøJ¸MÈOlN×¤~™éÇ†àÀFL¹ú‰ùÜ8#(c$S!‡"˜cPSÇ8(hdTQ…†™Ø vâÜ3c/&Ş	?aè?ò¿% OP–²ræœ®Šì‚<|”v¤0£úéÏ"Ü¿÷ƒŸ†Ïì35íïZçlF(p\:¶™¯cø?úäØH
*5ï@@µ²µ«8uË.9WuÆŸ*Ğ'$Rö-Ò•?!L“d•Ÿ´kgóì°$äOÖ‚EÔ%§c‘ù”„VÖ.¸’ËªæMÓÃÆ±Îd0.ËÜˆqñ*QÙñkîqÃw)Ş¦àBŸZÿY§Œµı0‡2‚Ùúñ”fÈÜ!‚Ç¡Mb"<\–Cğ¨c‘úÔ{'41À!Ìˆ1£·VÆ2®¡«ãÕíš’kò‡R,¨3Îûr>V.™äRóE½Ëfü=£vß–œ–‘¶É¿4W¡‰£y9=úÆCOôZ¡Ö yàğ3<-†¶õºB±³*ú•š¦!f¶e' ¼pğ©y]¥q»‹7xAçí7z¼ç=µ
ÂÓ’‘µ/¬D;ÿ€şÇ8jª—ÕåˆG£0;Jœ=°X¾fŞe	  ğy¯Şû‰ÄîÓãÖ=èì%{,8B=óŸõ3Üâàey5\0ì8uêŸXCmıh,R‚¤(±ÚNJÿÑ]Z4¯Pí»…³ÌqÊ"´4`5Ï¡ã#Vr´ëËƒï'ŸgÇSY ¶_@<,”P°¾+¸\JÏl]Æ®ŞyÚàE‡y»+ù,ÎãÀHÌ»´ñğÌDº·lğNéã,nktT¥óµ¬ëv‚%hUh‘¶Î7!k‹Ñ€dXBµÉà}Ÿm-¯"‡S;4Ù4È†áÂTÜ«nÏäT¤;d•ˆBñÓ#ë.ÔCı–Ù—Íeœ§¢ÅåÏÂí®fÇ–Os1iĞ%¤#aùĞ·Xz?!’†âèP¶^Ø÷‹M}Á}uÎ6“Şíw	¹@İÛ;<å¦Ğ%—w÷ÜB™`¡G½4(‡[©ÂÁ@ç¶“¦ï®µ9‹¢³b­ÎaWQy:ûÃ_‘lËJïO4/}‹Jğ;‘âòÆÏ]%ë”Ş¤şsyMv²7r¥'?VàxT²Û0–y´®n~š#°Aò<–/	ä>óh}Ööõ‘‹©åüUµ½ş;Ü=V uf/kÀ¢D~"çÑŠ3#
$%Ì.‰L°^v´y:9JÛı¢íH“ÈJî4\/A‹[07Ñ”ñÇË]×…h¢&ø†O¶³§rr¥
ÿÆé¿…–sJ hú¢ü·ı:9ÕÎZ™4íî†1.K*³C°|°ÀÊ÷/>¤(Cfæ¬ì?ON»~êéER2x^°hŒºâb!¤÷?YVÙÓ¨Y.Ş™Ç¨^Á#&F¢ÿº	ı@x¾Ş¶ƒ÷òxbš‘“U÷(mÉáJÏi›drâoÕÂÀG¶:÷Ï‹€`ñ¯Œ|Š¥øıá¬_d–Ï+Kİû&-,¹¼2­Zº}4(¡åDÖî›€¸ŞÕ g ¸5åü\M|w#x¨w„úÍLÄ~uh&2ÁÉÑH\ÙıÅp/si¹~–¥ñ9ˆ-çd
:L¼°·m&¨‘‡óúZùX;ÿoğxiõÛ[‹)ğ™B³á»Æ'†=…é›6Ónå» d®ÍşËİ€“üCÎ ş A\½m¶<1YÔŞœ\¬¦{;µ¥³ÄsàIGñËQà8·Tj:âWè€i˜Ò¶åœO>¸•ğ-š’á´}†éi¯Şq#Ô^WxÚáŸÍ7“WşM¹öb^èykÅÖüóäbïM±+ ¸_
€?(2ÉşÁŒÕç]”6åÏBmæb["QÈ Û¬\ì~EàŞQTÿDE,‡İãTĞdß)QYÅÕ" §g’¹•Š×puók€mâ³ÿ[I1*ºPâ÷¯ı8Ì†ÒsZ-û°Ú|3véÊ;Äy³|‡X]6Ò@ßy—ú ÈÒX™¶c?ëƒ›†ÌZíÃ5©ïr¦s¸pYj«—a…ÿœ­úY]ü¹øJúàh_b=«!Â’È$œÇİSRõÊ[š/,šm«•áy
«Hçõ\Øm”éW=öÂ„šdR”æ“Ÿãsùª®)>³Rª::GíÕµ§¼9À¬Şr;á\@,ˆ=„¥ºC	÷~ş˜xRš…“tF°>q’æóZ­1aúg’á€|õ£–¾fğÒš©ÎñÇB	LR»¹KåÜÆ±­|n‚=æ âP÷[>ƒhYÖ‚£•á§×›­ŒEË¯tDKp`H¥´9©İ´@>zL:X©rÿù‚f *xA4²úpÀ#Ëä;søID±ÊËÁkƒe?*ÄjÛW	l¡ÊÀo(&·Òå	ˆiÀ7Yæ§Å+X¹róùÖgÌ*-¢ö|Åæ¶á‚Kïı…_µ·[à¹¥°$ó›;bù?€¯Ò]H÷üD¦'ı‘¹”J×O%Œq˜µ¡ı[X¬øõÄÚŒJ1Ğ,d%Óc%¾°g8¯>’Ÿ'1“%˜W¦'ÓÓAıxÕzÂ4“ß£›æ´»—‰ÑdT|6ƒÓc_wwl?$ÚS+1SÍÜSyuv?{Ç¡vù¹’ênTtsk±Q“DUËG/JË\@5u•¥±´~îéF‹ßA$“Fzp«ê|%ºi‡Q{È£Wt§<ù“Ëªî­§*Ï„e¦ôıa?Oh½öÉÑ½‹="ÓDjÎeL$kÙ{‚¾v2.ß”\zV¸ç†J£:`H«4¶OŸ_
Ÿ±ß/GÛ”ÏˆsğQ¼9®¨	•CñÒˆÌe›¿•—¶¶ÎÎœ99†š@el®eÉsbNå]Ém‘scîÑÀÔPÌÔÖÎ—×,Š# !ø z pf4~ŸÂæMª½.ÉrT,0…bğw”rçóIÁZwÌïD„Ç‚æp ärO¶
Ñÿ$x#Z¡³U%«Sóµ ¨9/5¦ĞœddÿÕ§'¢¹Š¨
nÓdÿe®VÅoyy?ËÔÄÕ3€ÈÉŞUV5üğÿ#8!ê w ní|éh@²5j®>ƒwÁï”àeŒ©vú°´ªI˜Ò¼e‰Ón°¼ yz¬¿¸¯­¼/¡ˆpÓ*Sw#bÂÒGßøRÇœìNõÌ-Ø%ÒöMÒ½??Ì•JÖ&°…óHÌğÔk•içî€Ék®æZìª¨öx"ÎŸ@¨Ñ {xZ³C¹¨âªÁ-$¤<¥Z >ŠÈï4KÅ|ñì¼eNê1F½|%ï™ÔQãGÚ¹Rù°˜Nzà+®œ#®‚‡š²Ó¥ÖuÊ¯µ²k°ğMİ4ßäTD«³-‡iï1 S¨i¶u™`Œ–ÂÖé¦öÂş™í:™ÛˆU::K:"Zx~"¾Ğ5°
hzD(f¿RÈàÉA>[Q6„çºí‹5ŸoFe*=Ñ@WjFå÷ú_$ #x!Ú RT«S5î{¦pÉC1ÉìnõÔi+gÖ¡„€)¥/¢»‹x_Z€qK|¦ªà‡Bç€Ó%ú£;ë
$Êä_¸âyÃgà³/ä=³i¤˜öáŸğ"Á(Éù®úÄ{+[Å·Û¸U#tŸ-61ûl{UÛGSóŒd)tg¯ärZ®¡D2¶dïLtß} òvaÑàÕƒY‰ÿ×™¹’ÊÕ¯'Rş3È4sN,?G¨x{“ĞÊû/;d+Sg7‘ÄhÏ/ôOEX·yšÜbŠ­;|q6î“ı4f¯RÄ«{u5ÂzŒ?¹‘¶ü‹!VÙøbú‘»(4 ÜL]åÁÅa
1ò¬Áœ×v’êh	ş~Š¥Vb™Ñ’äU³G}ïìmÁr¸'.İÆÉjœ*¬­šÅ“+çwaÊâÀE‰q>:Ë[ø°eŒõñ¿Ng¼ã¼BèÉ®ân£TAÇHjŞZVÇ”‰+©×)¦¿î9«jÇW*†§Â³)ı³‘á¤êõ‚HÓ®èĞ_ &M˜¥İó	È™W»)|_W?ílAŒ 1°²÷jA	N¡Ì@mÈ®·N»¹M±•×›9“jÕ×'&¢¢ÁæôŠÄŸT‚dådi`	Ğ>ä(sfØ‚à¾iIùÎúì{5Ûo#TQ’,9ÕpQx¹ Æ!©Ò~ŠòwrîµÁ(‘O{»"Å@Ôfó-‰Ç€Qÿûæ}­Ù…¢Û£xAÚˆ3QÂ†Ta/¨Çº]‘rË]¯A„[~ƒXYŒÇ®ï¶ÏÎõ†Yİû!»`KPpX,˜¶©ÿ¯}t3?PŞÀÉ–Ô0.ƒfh4P';Éo@ wĞrÔƒ>\ëwr!ÁH>!Şİ`˜Ub­±ñ4Iq²¦±ò¹"ìg=­BA§\=i…æE‰¬á[¶œNÑÌdmÓ#õ•F|¹ú
„íxÉm´¦ĞBä	³~Í¨8îÆÄğ]¼ÕˆÎÆyÆª`}rû&Ì@92ªZØ"¹áŠğ0oC`´jµñ¸Në=Eİ
HL½­-0‰Ó·Z~»˜-|Ÿhgö)\”n¡oö&Ï×(®ÑĞŠ^Êºˆô¦ùóh“ìdB3–Õ-QW~Y^ÀQ¨F»<{?gL¯8±ÄŒ#Ÿ‚©Ò	MÁªåbuÎŸ,P%Ä#D2¤>ÈRÈ2ÜÏz#òÒc•èóƒ‘¦}ıi¤_½›|<}A…õüÅ¬«Á3è@Éw/-!Q
†›§f>KÄtTGp
œPB«}:ã—C$(RTáÑG¹º€ï­z$ƒ[¥õqìòO;İ5FÄû”zĞèqÜ3Øİ$~£XAÂˆiîÃœ¡a¶4ólñ$®™G3òÂ—¡×a²ï¥Øs¼&®Z7\.äXsBÔ‘à›g;!•oœÿtxZ°9¿µä©îbI1ŸÁaq­qu+ÿ‘óCÃÉN¦p­QÁ¥¼<á…€Å£LşS”šÈS.…ä[3,>Šœâ«K!øÛ‘GĞy:*’ •¿¾·¸vv¨ì[ÍòÚ]}splíjôŒ<öXFõ=æ©²ÆÍªí‡aÉûRVaûr; fI3ßÊ•î´tO_L Z°töì‹r/¥3l-Õå§3­ù…ºF-,-U2¼CÊ2Z¸V>™èRö…¾Ûc~‘Œ;Q°„SEóK=Ïi¬Åöë>÷,ßß;Â šîR¦ªöz„a½ç;G‘[­n/È—µ#£^hæ Îö­AïèªDnúeíáÚN„9wìµøO:Œ+çq²ÙÒˆÄ9–‡Ú¶ãñü|yÙÚâã1Å¾2 iå%##òŠ}€˜2Ò­¥…ƒº4ı©ëèÍ­lE(ëv˜èÿM8w¿U{Rñê˜jdAA¡…qzÑi«LŸŸK;3ÆIœ%ßÑ“°pÙW=Æ©ªÆÇ*ê§7®¹„J™fjçàm°Œ7îÁá «HãóÑìÉD¼9c·vvñ´Ôx({räµß?¾“oªJAĞd>“hUŸÁ&”í·Á‹VPÛ£qÜXaÂiäC›%£ù·sğLÑ<½”ä§ÄâVÄ¸ÑÕ„ßt
7/W<È$K?ìR
[ùÜzáÛ0cl;Õôg?R¨†¸lËn/2·Bú4•ŞàRÑ´–-Ü—ËTã6oÌîÌa¸?’á¨¹(Ì9­êÅ·+¤B„ÉÜ¾Ûğ.Yø@”M¸97T°-‹—ı€—òOF3;óÉGÒ.±äc)Îh#u† ¢É—‚ç'ƒÜ)”ämKŒ£‚ŞÙ bÀ¨} ¯:·|'Yâ‚ñ™¼RÉÅ®j{×¡èo)ƒFª«v5*®ÚOÙéL{¦|ãÍ—œ=÷Òàôöà~ğ|2™¨Ş¦Ğ¥=6¾®ÈDn‹T_G@|ˆ"ŞbíNïÿ+8'j¢—ÿ¸KÊÀ£Uµg7»VÿûBï/…‹ék7ñ°Æ`Êµ µHùu]™;¤2ÖËQ€‹Ü–²èŸ©Ü:áë0|ˆğ~U¡ŒÉ’#Ñg;R«E‡Kısƒá–|IÙÎâìqµ¨` pànËEqS—äI³NÍÌm­æïZP½ûŠ‘ìuå¡1ÌlÅâuFæ‚[˜| ëÀ„[÷"ŸG²ûªZnÿeº«Hı·?sêğ¶Z­óôNıô7\™4ï[[ÁÏ:ÓÆƒ©ÄõÓ=¢PÌgšg®£«€K*H‘ôúİÇ™¥c8cå3yïX@I{4a¹s¯½2óÃUA49ú¸²Büùû9.jòìÏ”Ù`ËÑ£D@ïÎë,weŞ“ !²Fs:±+~œj=éîU•í*¶§Â¼iÌµ–§²|™kì}Æ¸:´”>&Hsæª–ƒÌÜ‘ë%E[¸0M^T¾²j¼°¼oÉ¨_8xc½ .BÉÈ]pc^©¥+öÊÜí­œÓzHégOâ´Â·+	3Ú@Ş¹‹p|şD{Y«óôL¶AfÂk \“;o™½@×FÁ:‰[5³Ş>Ñô:—Óá”€èY³@»ˆáû€ê*Vq\Í²¨yM	aaÏPlûwIäÏïLŠ¤LÿË'/b¤ƒt:œ­Yü0x=£Ûöß©Ï‹ã™®ÒÄe«S¹ÄvO'~VfÄ œ|r–{T;GkJ—=QÃw‘®ù RMQ­½7ş’¹uä3p-Ü%Ó§E=¬]ş–\/s‰ô'¡ÔOÁJ÷O>Œ(]æñ÷ŠÆÈÍş×ÂÈ[ÚCû‹<5%éãÛîütyßZàvv¾*»çv|¨Çëİ†[°¶ºf±yóêÅ
Sğü39íêõ·?¨là„’ç(º%3bæ¬ZÏC,	åşó8}ê™ù`‹æék}®+ó[uøõq9Ãjé×6æ®òÄ}«+Õ‰Ì÷€ 89Xİş©ƒì’s
ÿ¸4J¯OI/®
ĞÅ¢•.fSnÍïÇÿ¬gÒ»%‹cQğ2H¿L¶îË†fú©QMB’‰•×f´ÏuŞL@¤5}{9¢¶†çğ¹:Õë'7b®‘„T[G1Ì›y£q9â^e jr`!˜øøüe¹Ó
åÿ38-ê¥ÅGKõªŠnâje·*|Ğ%ìŸ¹Õöç>ò¨}†™šÒ£`÷ gtµ?¦k-)q†å(„“H¿…Ä<ki×Væ†òÚıÑ}Ä¦«2vàÀFCvÁåB8uœğ4|/Yäƒ<ï™­æb²¡<}Í–”ä OH7¤å/¬;ë{7[nƒTYÇ0ºÅøJÎ­l7hç÷-¾¥ˆC‰ğ^ü 7¨Vµç;ëÊs‚ÜY¡ÂÀi¨Æ¶ÀÎ÷,~¥ØC"‰áğS|w\¯r¯şAÍÔrƒå©Ôƒ‰£°cp ï1E‹ M%<X` &Õbøº´KO|ı»¿½È†Ş`›~JP5Ä/+d'Sb…Ñ›$Sc7–„e#cIŠ5dÜYJ¼HÀC ¦á{†­3?˜Ü†Ğ"K öÈŸ7¯q„[qÃ\iÁÖè#ºÁ»Ï¸M
’¿ˆ7®°DLMÿM¸ÍòŞE#ÔZgm’à†ÁâGpóêËöE!Ô g`5”/dd“sÕÅM'R¢…›Sr…İ›SÄ2„B$'£@›+#°¸Ó¥÷>¹èJö>ß3¯Ä7Ô[î#ÑÈYÇƒ˜<âV„Ô¦×ö£l ¾:yÈ½ÑÆ!fÍû-»e‹SEğNm,»S¢Í°³ö-*ÅYg~Ó×ê`h´6Ïnìu÷LÅ{rùì¤ãˆçÆ–˜Yt„ [xZ¹Ã
éÿ6Š|¿÷L5¸”Íw¹¾³º:÷*q(š¹“
Õÿ'8"ª¡‡rıOxü¬O¬DtÕ%G÷*‡Õm›vÜøç%²£ı˜y’šÕãbG¡ÓtÂŞ„ŸS!šS‡%ãÑFØ)­ ég)Ò¦å‚ó½òÉ½üÉ™nÊ~cGQÊ„oT3GmÊ¿¯6»nËToGT
Ğ7SÔvÿõ™¢er&İ	ñÎRï=iĞvK¶ø“	ëğƒ,òØI¶ôÁZò44®†Lì7›L/ü×g––İ–á–ğVüùúúû;k9"N„ØØÓ#r(Ê p 
1à,p%Ü#!áàpp1ñ»4<•š"®nä 	CE¡o¾ZØiì¤üàÄç‡¹…ŠÛ#p!Ü aàp4/qä %’Œa¼Ğ@R,»«mÜ/Ú¥¸f;MëM·Mœ]‘Á”hWVÏÀÚ‰·laûìpuÜ5!ğ | à2ğ-¼%‰ãñğ||œ‘ª¼ã·Ê“†räeî[ekd\G³ò;ä­¬E…Ë/sdÓq¥ÜC!ÉànğV.r¥¨ŞY¿BÈ	®¾ÄHkN—LVÆŞ©â„3Y¯w¼¨¯A;WkF—JÖ&Ü"áá°pLUKñ‹î<ÚŸŠã>qğ1˜,µ‚6rıq¡ÆfaÍĞm¤ƒwŞ²àM°Œ=é‘Æ´	È““òÔÔ"KûÎÎv–7(fc±:1Ôaı¯’@;\T©«6YÕ¥·^NŸLPÄ=«i‡VÚ†ãñ¶p4¯ÙÀ°‹¢é(EÅË2ï úTO\M8¦ 2Ù÷„õ„X3B­É…®Ûc{QÛDcK!š?N2º	6YïëqGvêêOÅÏWdÒpËjF¨5À'WÉB€çÙŞÒ~ŞÿŸæVíÆõªÿ8:ª«zº›N_63ØipõrÉt]ş "f*ç²±Œ]Á‘¨TF‡JÚ#lt½³9\’<¯¢â8ÍSr¥eìy•¿m/¬ê*©ã­5ë{H³"ıÿÆ&l=Õé§6Â®é„vÛ^ã@qÈn±¤+—êàÓBÜ $°	ìJMúA_vºŞÃŞß‰Ÿ!Ö¨-vËJ§xr&ÜU½GŠ¶ßà<p)Ü&áâğq¼Iñ¾© *½¢m<ò¨Ô×SFñrÉCR³9£`M–…é0òÂéÖ^Š°Á·O±Jª:±ëw}Ş™ RÀ¨;Û/‹oä"WÜá ÙÅRÁ¥Üûá£H[İõ@°#§åìgJ:ã[¯x§îò®ı„y›ZÓC%Éã.ñä|sYİÂ‘üü‰m¨±;ëj^ÒpO<x‘ïŠˆeâ½»ÍóRV¨,9M†½rÜ¢?‡w³Mô¿}ˆ²Ğè^Æg³Ù’âÕ±§B½É‰®ŞÄ`kPD6û;“%`tŠbU16 É€ÕÄA'Êÿ_uS¦,-Ü;^ „VÏ9F‹Ôd ¬æC-Éå®ó}ûY»BËI¯NÄk}§êÑ‡¾ììÈ’ï¼1yÆúC%W|LQ'ÜÈQ¸5V+(3E»ğ;ƒµ04,/eä3uíß5 / $8#ô›S#ßW„»üJPJt%¿°–Ã¿2'd:ì€ñöèÔ ùÃ]uÚ<0)ì&õâÿ1¸,J¥Ï,9åêƒbq½ìÓD¿JaŠ`u°k´"Qş­ğ‘_º¶bñîºü4Ò+Ks0µ€†£}>Gî•´WF¼
Éÿ.ø$z£[ÃxiªÃ¯E´‘¹0÷‹?¶í~ß8’‚Ocåï	’´YÉÊ‘ĞU°xävÃÀRú}æ™²ÒÍ¥­ƒ™ûûu»u@?H(¦¼BÉÉ®îÄtk\Uş:Ã«0m`
?(7f®’ÄU«GJ¹ÁN[Iqõ ã›Ÿ%9ú¤7n¹ÔJçO2Œ-å‘™M÷M¾ˆ]XT‡yìÊVsõş?Gºi%àŠé iàğ6ü.ùäzó[=ÃiÙƒŠµ¯•²s°úÍ®ß¬uwe|q¢«cV§ü í
CI`4Åi´Ïvìõğ<)ò¦ı­Ô´‡`ê3õeru[@H9ÎªìG5Ê¯/$;>„ÎÑõYNP6GOòãW™ñîò‹–[x%^Ïpò§Z}_n€X7B®‰„^Û@cH‡òl˜]‰¿‘yÿZø:¹ë
÷>˜(R¦…‚«Lï!„ºí/ˆÄ†MC0¤Ü´Áy½w¦Á¢P.î$‡9û~„°7<°«Ê)íæõ²ÿ¸=Š©ŸĞ:ä(g*cÙàÒS¨³Çìæt*Ÿg´5o1÷l~ú‹kÊíÕ“gU£µe™$ûåDJ/úD—4æ—à®£ê{¬š¡Ú±RsDx;ñÄDœ±P`„|3YíÂõ©¿È:î«`;Æ[a6Í£Ü ,ò Ô»8KjW±úÌ{-Ûe£IŒ´.:ã9CÒlüæĞrä³qÜ]¡Á€hX‚¶ÙÚ°…k¡ö@aÈn´OwLğ]¼‰ø^ú€{áÊ¬Òì†™Z´` ­‚¿??Z‰²,¯ôıéLOéy¥Z¼³ÚêäÚI’¹5Tî …:ş§Wô«²TËXoB”	—~Ö˜fÒ’å•³ö½û‘Ë+À`6RÖs™>w”Â%†v¢ÁhT‡vÚãqôqØb±Ñø6”,êŒ.”ä\ñ@WÈ®²ÄM«M‡Mš“•ñ—<V©€ê¥~yÃç ‹WÂO"tr°yõbÎ"¢³µäXt°¬±¿Ôš¼x5w‹htX­q?z>+ãxqÚœcÑôdSXÂ»)‹fßRà°y^n<¬s²‚Í™­’Å•«vºËot#=Ï|©T}©}noGˆŒAÈQ®„D[KCOIÌíŒ õŒO‡z~&xs÷¬¬wïƒ¡šª{0gbízqµÈ0ÆÀZv¸y5©äFóJıÏ9¬*Åç+2§mËÓ™Ù]‚µÖ¼Æ9µêÏ7,.¥äC3IíÎõ¬Ø;Rş-Ô=ÁM-¦³§pï¬ƒ¥o°óqææÒJŠå7cW»ü	Ø*O}ü‡½Fæ)­æÅ²ë·}™œRÑÅ¤P0ŠÖ¥€tj¾æ:½ Kş?La¢9şÀ.ãŠK.¸„”é¾‡ù%»d¸ ¶%|ò²ı¹ŠÑŸ$P#n!Ë`oP7{n›TSGEÊÂibV-qÕñ'$"î/À-$Q/Àè#,‡îÅ´kW|™úÒû%»cQÿDx{óMn»ğö?ÚíS%„›.I'.˜d†pæ+”zß$ËçA¦÷ª’÷‹ø„÷œa‘ĞTdSz…Û#saİ•-íVC[š?¤l2Œ-Ğ«Ğsa¤ÄèØTb‹¶TQÇDj‹WF°
Ì?-è%¶£ÁŒ=5…ß–|ë¾öaû QàpÈ)0Z–ÿ^,ãÙŞ‰æÖ“fª:«[™ø51}óY½ÂÉ©®ÆÄjëW7F®Ïˆm@QgÏåœ^QØD»TKGOJŒü1¹ìJõÏ?,(%–ö~’¨Ï0È‘I•gRb¯1ğ”I´”q­œ‘rhªªô·¥~­Ì:E‡{„ <Ÿ¼Ñ–äVóFıÊù¯:Ä++ggR’…•ëB_%ğ¹ŠnbsP´Abøe¦'~˜d|Õ´op¿Ø&öİÆC®Ú9¼*Éç.ò¤}ƒY™ÂÒé¥¶ÃéŒ#µ¿‡>~?v›ˆyşî@ARò,C_	İK–³%ËkP¼€']U­÷›ô„‹7ŸqT1Çlj•×&¶¢ÎÁ¬hE¦ŞjŒ'‡Tş:j’Bÿ)ÌØÎÖ¬HOBÊĞó J#@¿soâJwP„0[lUùÇ:ê«7nº”Kg:ß[ºµ/²^¦C¾0Lâ¶YÁ²À8Ï“…ú,«l¾û™—"HéL¨‹ŸrĞ¤1ƒlYÕÂç)²ãÑ¨ƒŸ’Ï¬7î»4KoOT}ú™»» ãAg~6%	âtÆµÊ»—>HT4{' ï\GBÅbo?@WàjÀ‰“y*D¡Ô@gHµœOÌ4mïU´zÌNE ;š7¬É„Ç^ªÓsèËLÆ³k~›Ûˆ¸0^Óè	† a‡ïîØô}¿YˆŞ¹ JÀ(<&©âÆñªŒu™ïˆBz4ü.Pa4:Ï”	‡D&Ã¶
r!Í¦åııœmî=Ø<	B>–¨VÆ†êÚ÷#>¡è@vˆŞ°`<EA§xØ,Æó´8¿@(|¬Ê¿†öàXzİ”|´w![3ãV–9b†…ô[?Ch	Ö¾æÈrî´QD\{³=ißò]@‹¨®j#/ÚøEäS›
£Wt¡&i!ä.Œ™òÆ‚Bµù“§Ë®p[\AùÈzî›4SoEÔQ/0İG’©UùYKõÕx=Ú©£Áúè{6›nÓT’yÀ€^|½>Èíò]Ññ.ÆˆA©ª’=)^Ÿ™Íöí¾õˆ˜0R¬…û1;sk]×A¦ˆBŞ‰ ^À hWEéÿ‹B¥ï4Fûî"GÈy0ª•#¢¾7ÇV*àÉ
ßHÀµ—ê’Zºõ0‰^ïõ°·{ZuyÊ ÿ†ş«j)m×bFNò7ËÜU~Çxjš—µöÏ>ì(uæéw‚y×fÂ/\Ñïä<ñ
…´ìàÂÏNá)6¹îÊôo?T(fº’Ë¯W]ò<\³X<ğÍªnÀŠXf&'ÎîèÑF¿_'M†%Æ*éà€´ì8‚ßî_5³ªy`T,#ØT^|ŸFĞ
ä?3h-Ö¥¦ÃéùÆ¯‚¨i •]w³…_!AA§"j–ë™z¼vr‡Ã!Îò6â®ñ„|[YÃBéÉ¶îÎô%9U–HvºÑøux ¸3
­ÿ¸;
«X:‚«÷'–ÎævÄºV+ÊGö÷“Î"L×şÅFQ•äï\) ¤r¢‰şv”.Iß)¸¶Õçr±İŒaĞQ¤Cx–@° 4ˆŒe°u8²µœ1‘ìTuÇ_*€'wqñèÁÌËBİè„ĞMSävmn¬°ğàC™¶bö-ˆ×MH·9xô¨V··±ïwŸ¯(3‘Wÿêg(¦µ‚Ï¬2Åí«5‡oNÇgV?¢•£×\+°Æëp»CIÿNøz½Û	£~ÁØ?*ßİÓÔ"µ·×Ÿ9*Ô''b¢‘”XWB†‰šŞÓt7¹	0ì/5ä/3d-Óe¥Ó%ùã:ñë<wiŞ–”¹A‘u½®:êkQÄ+ÚÊ™‰¥¬b´ãí ÌGs!yUv¸·u>§Ôt•Œ¹';UK™}»(º„äK\ùlD çæí²õ¿ˆ1¬PEÄ+gXÇíÚÊBˆ5À»T&q]?äRidï¡›®DÏTlUú‡;«s]ú»Kr]œ‘Œ3À6UÇ6Àòã¿°cŒİüa¹ĞJä3|-Ùå¢ó½ø ü¿N&6¹S#4Òx‘Ñg1¸nÀ¬Y6Ì<Ù€/éûÉ“DÆ™ÖÂ®ÂŠ[¬¹£ªäÒxzš›uõß? ( & "À!¨ F 
À}zmgíˆÂÁ©¨FÆŠêß7 . $@#8t‚ó)'P†9zûö
, ¸\ ©×zèdİWORóíÑ…:àLÏ“ªÊÇ/*¤'b¹ÑŠä_3@d%àìPA‹;ad›LSMÅÍ«-‡eš“õ÷?>¨(6óÆ‘šNåhÎv½søÄ†J-o“çòƒ¦†âbû¸+3W_'T]o-ä»,;´POD}ÿY¸Ê¹¯
î?+h'V¢†ÁšèS6…îÛ4*)Q¤w}QR›E“KÏw,¥ğC<	éşöø~Œ˜fİ9ÜAÈX{mïèŒê–©d²’kKíc•ôø…
mDòÍG›lâş—O:C®eŒ9êÑ·$N£LAÍÈm®ĞÈ^\™JÍÏ-¬%…ã1ól}ÕÙ§"Â¡©öFÅ
”ítÉht¥ÀC(	æ¾òÈ}®™„RÛEÊKÏ> UÔ§R¥ê÷Š„%½Ô{êHƒO¿r}×öÎ—Ğ«’á$„Ôóî® aFUü9úªû;z«[CzûÛã13ş¹uNÓråİ³!à]°Œ8]êÑåQ æ„OÏ¿“¡”7›K1“_­ğrpk¶½½1°ó âß1 ,@%È#.¡ä@sH¼òãÅlÿ5Á]_}VÀ)¨&Æ¢êÁ·(N¦ŒBİÉÂí	8GXş˜O û<Y <­&C}ÉÙ®âÄq«\GAÊˆoÚs!VÙô–kvî,ƒYømJ³OÌ=­é…¶Ûã|q«›- Ó+CûŒï}ÍkÚ«b»I3w²R²…›“q•ÜW!Æ j²Smzòï¡‹$ûÉºÚ²Qz¸iu…ĞÃæÃÁ„¸DJ‹OL0ì=µé6Ü^¤¶3Q¢¾å,
—‹‚¿`úg ¾CqühòR«ı¾<´Åc‡ÎÅ¬k×{&›bÓQ¥ÄC+ ¡N€Œc«Öí•½bB‰œ^ÑÀdhVµÆÏ*ì'5â¯CÖi —(g¸èªb§(ğÑ€%¬°ZÌ-ùåºó=ÿi¸Ê¶ïôr,‹S¶Í¿óò)‘Ÿ¦'>Ãçştg_R€˜;«u‡_€3-ò¥ÏÑLÊ™¹)Áİv¾'h[äôO~Mò¾E±Ê¨o”:×k&—bÖ‘¦ÔBçI²¿Ø(İ§Ñ4RÍËóÕ]3!”’ i’6Ìa& sÌ$‘’£÷~²˜M’•—–´VÏ6©X¶›ztZoõâV¹÷Ô„‡z¥it*ícÖèSB~š««>=Ü¤o›KOuÌ-ğ%¼#	áşğx|™Ùıõ¹¿
È?.¨$F£JÁÏ(l&•°×,¦½hÅÉ«.Çdj“WÆ·*Î§,B¥Éƒ\«#¿Q Ä;ì† j†×oõåÇœ+è‘€ıÇzê›7nµÔO'L"á°QŒpº»UK5ô>!pëı¨y†šÚÓ#%áã0qìuñß<`l³n¥pıË€ëZ§==˜Ø²³¥º§OØ‰Îï…5ä}Aa;clå†$ˆŸëIQpx-ØáKIfÿ5:ÂjO4<ŞšâëT¯²y¹µCWß-ÔO—tå§1…ÔReô¼şÅŠ,éß˜B®8·[ÿx
½ó	´õçÍÛ¯*6cØ+ŒáJ~HHæÈË‘®Ñ† §ŠcªfnXÇB!&¬"Åá«0Gl
•ÿ86ª®ÇjÏJ¿WÈtU­+;3ñÌVmÙÕ¢ç²¸MŠŸ1”,WeÆÖI¦u<ËÛÑÉ×vÂ!ØÑBµa¸tEy§k«Ö¸4¸—ù¥½wZx½ï«E şù^D|:›SP¿=!˜GgÕt/Š—®ÿg§¡¶¯ŒHt˜tÿ­ü„A(p$š>°Ÿù-‹Ê^ãc<6Yò÷M¾y¦ÉÍT'Eà?{Û!Ù‹÷ø
×ÏÜŒ’ì¤%‹§ˆsî"õä}Ea—àÇÂKœøøû6Øk\åG,
¥ÿ89êª÷>º¨KzÜiv¡/)•¹2·?ü¬çò³=é¶Ñä\sAİ-ıÕ^~GJ˜¼5‰ïô0lò·o´œÚÛÎo3T-Çeª“ú·«|GYÊ‚ï´2Ï$êË¸O>Á?™ÙãÇ¨á™°RÌ­û»{[CX{ûºÍ"¥Ğ^1TL~?¯THôˆ`^ T8jº—¿vÈPœõ'	K6¾p²|Ù¹Û¸”v¶b{·İ‘¡”@WHºÜK!Ï`lbG±dX!éX=ù7ÀÎ|`§ ¡Ó3ÔaƒPYÄëy·ZÎƒ,YåÂmøª»÷½ˆàÁ(’FAªñ5KS=A
ñ°÷›üyŠ"æ]^_z€3r­İ…¡› SxuŸé`o$³"=W_ïE ñ èXğË |ÒàPìß#˜¨K–cºÔ<giÒ–å–óıöù¾ú¼)oØdNS>¾¹VRMd“u•ß 6 .À$h#Vä¥ˆ+º_Àş‚‹8ƒ(Ú÷‹	û:!nÌ%¢ÄÙMQşƒÌ
ÁÊJ(¥¿å6_¸s°då¢”Ãz(½…¹jùÕ‚©úqN!øO¸ cîúYIk7çVA¾ŠÏæaÑgÑo{ö—‘K.!ÆÜÛÒÒ^ÅOÉ†ìXA‰{da!¹bÃ£í7À”di"Æ©Â~© ùù¿8¾jbò!,ÒĞÌÍ,a×Õ,ƒãñúü{9ÛjãW1Æ¬jÅ£ygäbß‘ÒïWØ8›ò2Ü¡å€sò±½ŒIÎÑ¬d °dmEgµ¸<k9©U÷¶ŸØgFÖPã(@Éã|ƒájÃP—÷¨K¤~díŠ¡‰±œt%ŒŠ¬8ÇëÜQ·xvÔ}ì‰ñğjØºâÍ•KoMÓ´è,ÁÕÅê²Ô@@øi
½¸¯;õĞ,+Ÿ-’§!ÉSTµ±…Õ××G–¡æqAí9åâ›‰do£ë rºkËıÊI>|‰l©|ÇU‰‚ê$³|MÙÍ¢íµ˜OŒ5ï´4OEL÷}¾™ˆRŞ…  x(ğªã1ú¬{Û{#[KÃPiÄëv÷^ş€x\‚ÁVØ¼™§‹‰€^Ø b¸Š´_@<)Œá·¶‰¦†1aXN¸*vè—!AÑ°ËLV<<Üİug»òd„[}ÃY©ÂÆéªö‚r¹ím´ºĞK$c|ÙôbÿQ¸JÉDsMõÄ½ƒÉî=…‘4¯ï±+guÒŸ%#!÷c)ÂQ w‡+ÓÇÀC ör›íl Ç…š/Vög•(æ…äx¶>yò)¢¦Á‚èY¶‚ÎÙ¬–”ÿ_	DĞŸD)yæõ=p¯C	û~ûX{B›Iİ=˜c¯«äÓS\·¶òí²‹jßW  :À+('ñ×•òçJıô§Åb1¡^7|oÖ[ @1È,n¥ÔC'IÊ´Ğ¿,–_öÎEĞ‚=†©šÆÓ*åç32­ÀçØkV0Fœ»Yº\±!@KúxGyÅ<íöõ¾ÿx>š¨S¯úÛ;#ka×Pf„ÛôN”}h7–ÁWå¬¤öÜ~áØpbœ‘ôT(FÇ¿Jˆ.Ã­ÍØ{Ms!íNöôÈ¿h•–îgGĞ•»v¿^È n¸J·OÛt¥„¶¦¢Œ;¾ ğ2ÀGpÃÕ
†Ú-ù8ñõ¼	Ø>â¨q†œZÑÃ$iãVñ•¨%©×'æîQ,ø›ôCUæ½Iˆ¨e°ÿŠç2°-Œ%ã±ôLM‘K¢îÕÆÈDÒ€e˜9µõ?(1æ¬rÅİ«!‡`ZQZ¿+¬™~äÏ”R¯÷9]»é¼=İ™KıĞy¤Ãs)İæá²ğM¼‰ıùÒ(‘ZlYHÑ‘¤TCGIÊït1ßlcÓ4'- d2–OÎ“,UåÇ3*­ç²»‹}Öt‡|ójÜ—9–ç˜†æŸâ¤ˆèí–u…:P4/{dSsEİË!¯`Dt?/=LEıQàáW1o)$C	qËÆ•)Ã&<@w<Ö"ßuß÷LNw!Ì¸rÊ¯„4[oCT	Ç~êİ;[ØµæQX7aî‰´¬}U­>nv³Gì½ªÉ‡.Ú¤cQùÄzë[7Cn‰Ô.²!ÍzÛÿY±2æÍÆUŸÙìX	Šk<¾–÷Pvûõ?Qü{‘·$ĞÍ'«}‡Yš‚Ó¥òÃ=©é†öŸ²ª~qœÏ2EŞª`_J&=ûi»VËFïJô?|(æ²òÍÍøÅÖÛ¼U-z_&-^_Qxk0¿#x	¯Ù}6HW@ycŞÿ4ÇÚ(XA}iğü6ùîúô{?[hV¹ÆÊêŸbx}ê]E&ŠZOi¬b}äƒI00ìãX	ı¸qõw»0_èY†a–/âˆñ¼XIÂéœvÑŞä`sPÄ1«™ÂH_ê=P(­£õ«_sø(äZÉ¿ B´O3ÑiÊ‚ñøLä6”‘I‘õ”X6‚®Ù„bÛQ£DAËHØ_ƒ×¤‚qÜìKU»ÿ>bÒ8[PC‘ê}ˆ&˜*­LÁ£<>„ÅÅÌÔ™‹’ÀU¨ººË/drµİ!ìu³A~%¢ÁÑÈÖ8$_ZŠY”}<‡åS_u^¤g¼ÌÏ2ì-µå3-ñå¼s	İ»­ë5P¶ü4yïZô?yèö³>Íèm¶åÛ›O#Ö—‚käSà©W~=„£kİ˜ºÁ,‘L;ºÒÅÚ@ç&æİÃƒ¾
9éêö÷>ş¨xFšŠÓ%ğ#<!é#¼M¹W<¢¦¶kK§eâç‰‡€&âŞ¹u©vùáüx1~ÂŒuš¯¿zw…XD‹yŸZĞ$9ãjñ×<f©ÒÆ•ÿ¿Txìõ˜?»-{O;8“_:uÕå¹”_+ı‰­á-Ü?LOòxQZ›CIõÎÿ,x%Ú£#áøpzœkD¿'8¸î“|ü\‰ë~ƒàlîéŠ”ŠôöÀAî€³ûc/.HPãÅo­Ë¯{{s[]ÃA©ÈFîŠô_Od[cÙç†OıÍ(Ä	GKĞuáÇà:¶£q*IæñŠ‚¸æ>Ş(f˜Òµ¥9ñêüwOø¥0¬IV­o«nÇTj‡W†³Íó-½åùæRµ
ù[‡¤[ªÀ- IÈ„Tù¥Á´
‰*¼\ò
ÇªFXÂ·)¦ÜBáÉ°nÌm‡ òÔM=ûÍ«Ğ¶6ôíMÿ'è9ÉA*æ³M%¡ÓŞ·ŸĞÖû&ûbûQ»DKKOOL´»¹÷Åß_S>
#`!Ğ d `5Ğ/$$#caÑĞdF&€¸nn)4wÂoği&CÂšn&.ıÄÁÄC)ø‚¾¸\5iƒfGi­i[Ğd1ÓleÕÓ'%â£1ì7&ÖeÜi‡a¨1÷ÆDÃ8÷ÚÇ‡Ÿ¶ï§K²·±¸¾™fh#aA:•š&l#RRn,,RR?„ñdcSQÅÄk+WgF’ŠÕŸ'Dqà`İ4\ uq>ÑZW¾¼¤Ïl1Õìg5Ò¯%„#aó5Uîr³ÿÄ2Z²ƒ™ı’ù•º×&¿bÈ®´DMÖ¹ıŠùŸ:Ğ+$'cb‘Ñ”dWSF…ÊÛ/W6h”*”V$(ã b—e+)ÀfÚ³R?§ù;—
aÆ4ßÃ€O¨4ú™IÁ Ò‘’t‹í¶„¿¡GÕÚˆ•3)ØÊdp\5Áï(t&ŸbĞ¤4CoIÔK¿?7É‰’€ÁäEDè®ŒŞ|™+=I~Ç{*›gRµÅ+'qâœq‘ÜTaÇPÖ^\üˆÀp¨„·0Î³,MåÍ³-å³ô]¿Aˆø€<
GÅÑÍ‡Şô½vÂm¼&ü[òksEi¢Ûğ‚±+¿šòï$_íC\Góùš”Æ\uÁß(`&"Ô!§`B	”>×hf–’Ö—ô¢C¹“½ŠÉŸ.Ğ$d#SaÅĞk$#İ‘"Ğ`É!|s¨:~ÄrCjõÙÀÉ, 1‡Ä6ÛğXı-?z¨³zÍÛ-£eÓe»Õ=Û¦Ã6¦İüîrë]·Aˆ\^ÀXh–¹–ÊÖïV¡n¬$ßUº[Z.r} ´°¸ì¼Æ.—Úl<5Q€npD%!Y¢ãÎ@ –ƒq&B$£vÁŞè`vÔ0glú¦ÔvZäy•í¥”2%	õ	Íhİï…7GÇ5—Ï óşG	ı^'ò‹L®2ÅêbØ>ÔL×Ræ…²Û£}Ù˜bÒ‘¥¾CIöşÜxaÚc÷t7ÙX&PÁxßjÍW5Æâd…ç^"ôØÔÑ‡¤BÙo©Ëïzô?shÖ±¦ÌBíÉµ®¿Q hŒyDıÊP*t¿	0öÅÌwù=†ƒ\Q¾/ŒJÉ°Æ Z^¸gµ&ãâîñ´|OYÌíùµºÏ,z)¡U6Ã¼Šu(/Iä3;ãŸÕ+S.cF‘ÓC÷Vş†øZúƒ;ër÷]¾ˆX^‚ğÔQ—ŞàÄÍLl¤P³n­ ıµ'sXaŠD¼·¾òû{3$†'t6à†œjOlkêI1ÑìduÓ_%À#(!æ rÀXäxÀ¬,—†jmçxò‚ç¿¹—
Ö¿&È"î¡´@OH½üI¹¾Ÿ <p³jijlÜ3Ø‘KS÷*”X,*Ğ€1ş[AÍ·†J´p›0còªšx\BÉ˜nÒ”e—S…öÛ>ãhqÖì3¡ö–¸ÿOÈ&ÖdSÉ¿‡6àn$÷ß‰œm×]ÙjfùÆ…·I5“Ğ¡ˆÀA¨F¾ŠÈ_.€$X#B¡É€nØd7ûËãO=¸Ù ´ºF·p2²§Ä0‡óti ¾¬xÛaÄ¯õà9°*Ì'-â¥±ƒYıÂù©ºÆ»£4quê;ŠL^$Ea•¤ï6nÔ½™³R&À.³¦7l:ê[I]õ¦@¶¤ÎÜlaÕĞg$£uß`2-”%ç6ZÂ³³;©V!ÇÉïŞŞ€ànÅî—Ü?g`m{Ñµ°0ä@CÖ²2+eçS2…í›5“oÔ7'nçØÒR|†ÜZáÃ0iìõöÿ>ø(z¦›£,é‰†Dl¯è¹<ªXë¥Ï¸0l”z½sFíâ€Ö!‹‘„ÿŸVÄy6‰pe»ì•3-ş¥¸C
‰ÿø0z¬ó{=«<ï„¡­$øÄ{‚Ş)ŠÆ«’òKAõ´7ÛªŒtW­yëNˆ¤2óóšM}Ò™¥’Ã©÷şºøK:kq†É2‚'İ_Æ]	ëƒÈlôo–ªìa¿\‰ƒµáåÏ›@cÖª8¬EåË3/mä³wŞ½ I€Ø<bÙ„Ê·”sÇºë¢²1§6Ûåß	Üv5=SŞ¹“L]²*I‰Ú¡lËGHµÉë.÷d~“XUÂ‡)š¦Óåù³:½¾aä éÖR[¢‚hæ›R§ı·£tè!Œ×v ¿İiƒşµˆÑ¥Ã¼¥œ4QïDt_@2¾­¢E‹_t x0¬3íûCë=N?Zh|ÄúWŒî®ôDKXB¼	‰şŞø`
ÅWGv(›óTvív™îXN nÛcA…2gÚ«úA¤C~‰Ø^â€q˜R±Å¦k×q¦œBÑÉ¤nÃTiÇV…Õ´S²ÿw©ÂçX€æÎˆ¥.ú ÎSŞúPC„oõnÎ£Œúâµ]àw‹¨í·€Jx`ôªêıĞÆl@G¦0s[ıJN=övxÚ¸c
‘ÿx7Z®ƒY©ÈŠ *MÉæ?Ñ‘ïÀ—”á¨“ùŠúß; +`'P"„!›`S?V‡rg'(ÉÕßÕDq<µšQ#}El§jk(§^üPÇ?_e¤»_6çÔFàü´ÍOhˆcén÷'ûÖ(Â ÄèÇ©µ†Ïì35íï5´/d<c<¹…ºA½lôõîRA5éWY¬ªò»3t†t' ŠÌo³oj+‰aĞXd“y•Ú×#&¡âÀ8îşÌ^Î§c‘ù”z×[&ƒbÙÑ¢äA³HM¾ØàÀ¦Şf]2Ğ€•Aê%G”ª!4ÇT|ŠöµŸG´N®˜;ºÇ;´(‹¸Ù•¢×¦¸BÊ‰¯Ä0klxµÎr–ç0EŞª‘up	+×ø‡¾äZÆ3Ã†º4ñŞË€±*å–iøIü¥H{9,ÎxóE½Ë	¯~Äkr—]––Œ¶Ç£ÎüN9‘§åc~#ëœM}KFJÜ!ü yàğ3<-¾­ÿ¿Kıˆ+ìŸĞÉ/1ä,seİÓ!¥àC0	ì>õè6Ì|‹¾e©SÅòë=·i–ÜVáÆğjü9öªşÇ8øŞ@{õòò|Jœ;¬QÿbÏc Ïâ}´ÔÓÜôÔÓÌMõM‰?M7KYoœ¦ø3Ë×à³ "V8Æ8uêŸ7.´$OcLÍôm¿Uˆ[âó\[}Mí ƒ¿úmÁO‰5l »ï€kr¶ÑœdQÓDeËS/Eä3m¬GëğlÁüJœÏn2¿í—5–¯Ä6ën÷T~‡XZ‚ƒ™»”ıÑëÊM´°f½!§½K|,sJù¶Bÿú¶é:Ÿ&!-KÖrÜÅsp6àƒÔoZğ†ÚzÆaãPqÄkq×\fÒØe¢“•øW:†«X•6kÖÍ;²´MMœ‘ı”y—ZÖƒ&©·®¢ôÛ	Ãš¸ş;ê™]Of4}…q¬`K/ä ”N (¾ï®*B¸	Š¾ß`>(T&‡bÚØå¸~şëFxÅ˜k—u–ŸĞ6ä.ód}ÓY¥²–eú£¡·¤óãlÜä¸gŒå=EZl~+âøQëŸ%©	<|H±Uà7®•ã¨¯€[r¹İŠáŸ0P,%ûI;QëDwK^@\ş¸xJÓÉlFëÅ<t)ßfàğ5¼/	ä>óh}Ö™¦¤Âø©õJ‚»¹³ZØ,V|H?yÚ»R91ëÊ©*B3Â’T½C/øO\{mĞÛ¢üA¹ÈJî4\/Aäs~Ø”çk›HSN…Ì[-Ãe©Óåúó;=ëiÁVÓ†š°‚{è&ö¢şÁ¸hJ–Ü6áî™ta¼M½m±…™´frèg%Æ‚›ëç6Tp½péù@‚>bO¶ h‰½ø>Õgã›btœ€NØb½Ñ‰¤^Ã@iÈîÄôSÿ:^ÒË¬`ˆÔØxbš‘“U÷G>Š¨_€jŠblói€Ã+–×ªšÀÓnê§2ëá¶‡É°]48ğ¬cÑû${c[QÃDCáVïFô
ÿ8*²§‚½™ûÑ‘˜ğ+SèeÏá[B2F+UçG2Š­Ÿ;+wg^ñÃÕW^´ôÛ_Z2tı=‡ä•5ˆ/¤0Cl	Õşç8rªÉRÕùCK½[iº$¼h¿Ç|j™×æµ²Ï¬=…ééqœ/©·<j®ğÈÃ•ÙVÈ5–i	ô>ÿhxš¶Óåüs9¯®¤ûdÏC­‡7î:”Re2¯€Óaê ñªÏ¿tÛÙ¼bÉÑ®äDsK]ÏA¬EÎjÅ[{yÿşŠ,ËÖ	QÂöm]¬41d»‘¡§¸{ğ/± ’_
€?(2¦­‚Å™«ÇuãÙb:¨+} 3SÕï¸ÿ¸7
®¿H;N«LGMÊ¯„CÈ).‹º%k÷7GÜıøŞ5&°"Ì!­àE°?}è¶²ÎÍ¬#öÏ\]»ßtmé›yDœQ÷D~‹X_B€	˜>Ò¨e†“§ bi…æğÊ·Ítù¿Cº~÷X+ú$Ö¼fÉÒîå´s]ü¹øJú;Y5¢Ä‰ã/ïÄWR4ò“O‘/m«ŞP¢®ò|Då'µı9œ*Ñç$r£]Á˜hR–…–«S±5•›°<„aªN=,½…ğéK
ı{ÚâÖ…-çW~"ì¬™i	÷~ş˜xRš…“ów=Ş© Fê
è?6¨.Æ¤jÃW)Æ¦êÂ÷)¾¦¼¯Ê´CÏ;zhƒ8NªŒGÊ±¯D=Ëi¯VÄëz²8vÂ:W¿ô¶•ı¶©ğùÍKÍE§/F~4F<u»­3öùd)5X B¼cïïHEÌ3n-_gõ¿şn›d¢ C8G	}ä\½Í ûk–e?*ÁˆjÙ.oãŒm2!Å'Øÿ ‰oon¶ùŒxi‘eîéFŸÈY\Æ7€¤‡ğkÍ‡%òÊ‚¦±‡,ü\ì‡µ/ø;ÙqšWÀ€w²°MŒı‘¹”J×O&Œ"©³àó@Qv…¬·;÷óßJ1Ğ,d%Óc%Ñã$qã\qÁÜhaÖÕœSµ{Ûé]ÜrÀMÖ2—œ¶€æïV°ÜÉÍŸ„Ñä6VKuÈë}Qgqpm{ B&7Ÿrè^Lydk4•‚èÆÅ¨SHf9'×V‰DR¢jå[J3wŞæâõHòí
 ‚‰6_b£\fq³ìf…cè ‡[IŒô=ôô‚…ãéØôkÜ†B»ù 
q-uõ·‡ù«ÊxnŸV&FoÎ^5†:Öˆ#*jt‘ÀThVº†Ëïs4ïq´OqŸpñÄ–g	Ò¾åˆsğQ¼IûNûL{M©
ìÍÍ…màÒÚÖ[»¶¼¸)%¦šs
" !€ X  9€*Ø'"¢¡€X+UĞöÍÏÒÂ%ÔqUdÒ z  3x-Ú¥£ùøz¿×hVq_×_&€"Ø!¢ A€X>‚¨Y†‚ÚŠ£?Á²£alœ
Ñÿ$x#Z¡Ã iÒú¶ûû|{YÛBã ÷Î‚#9Õ¦ğuMöü› Ø_"€!˜ R €;+r§/ÑÄÍã¯‹äËSV7±Ò*!ê w ¸0J¬ü;9ë$„jıæ'ÈÂz‰¢l¶©îX‘$Ò¼e‰Óåğs<éñ¶üN‹Ÿ?¹¼zâ#zšEi+ÂÇPØó¼ñ£¹ÅU-Ø%¢£øXz‚›“rÕ¯ãdÎÓÔy–D¬ë‘×mâ‹C›ªªˆÌÉo'Ã[Õ/¡û {xZ³CÉı®ù„z«q Œœ¡@9 ĞÀğLÌ1ßèƒO,x®F—y.£õSC‰ü^ùÀzè6³nÍÔm§U‚‡š²Ó¥ıƒ9™êÒİ%¾£Aşˆx^š€Sò»IÙ(ÜVÍŸA@ıi¦–ÂÖé¦öÂşé¸vÊïU|^=~}jg=¡È‹n[kLs	ûÊ®ÏV>C[Nw¸ÿ¾‰/ë=QW87hÕL$A„Š¶hSft!İØ/AS½x}µ[j/<‰·
~‡ëbõÖk`Çí›šRßwçèHØ,ÃF1€£ú‹9ŞšSi¿¤!é
2	×ĞDºAºyÛR‹ıhHæ1³i œê´ÇñGËã®ı¶|vRMCR‰ÅëwtŸpP1>:ÛZ#1ÚŞEhê·®¼DIËNïLtß} €w»eã÷ên	¾Í©ıøÆ‹ÛÿrP*àcêFmí»˜ºl~7)I“È)ŸdhP¬},hBdö5İßĞS&½¬*rR 1îĞ]2ê …Qâ4I\vƒY`3«˜úã”ğ[N—¼7¹ÅúZ2OVß	Zô½Ì^Ã:1ğÏ2ËÎa‡ ë“$j«?¿Ÿ9`•Ñ’æ#òXÓîDÁ<Áhd5–›İ@ÍW2†­šÅ“+çw2ÛÎØÆT*$ûG‘ü Œ°’÷}'ó¾!¬ŠókÈ/n²~kÇHj—V±ÆÌjí¥`èİG”9¶jµdôâJÂ¸)œÌİ²á°]ŒøQºÍ'M×ñ­¼E£Ëïptqğ|1Ùìbõ”Ül	q@ç…$›]ëó
îC9é¯ı›9“jÕ×'&¢¢Á¨XFÀØœŞiú!¤ C`	Ğ>Î(sfÒÑ¥¤3Vª‹©5;:qN&ÅCDcãfÜ"J%¡÷–ôfaé·‰PØ"³aĞ]íGƒ6‚“j«ØÌ}­Ù…¢Û£xAÚø6RÂµ39IW®×©Wß;êÁF7Â6—Ö¹Ìâ½ˆ£¤b­®mè%(AM!CÕVøúÿ·X~eAXB¶‰ŞÜJaĞd4ou»Ld9nĞnÂ£ B\'®{?3Ì“ÿ×M7	È	œ`æ#-áå°s¤õï®Š`ì9u¦<y~fUƒïu„…­?œ¶NÑÌdmÓU¥¨PiÉ²F“üTÆyËòĞ_äfà=½!ÁİÏ™KàÏ’äè$èÅ46¯nÄkáî>¹@K÷±ß¤_! F«eÌŸbó6E	ÛUYù÷‡iğšã1õì5·|aÔtÏù9ú$™ßBõæò–UÊºˆóù­ÕsŠ£*|q‡™Qws^ÀQÇWÜ$¯,g$ã4ÿ„’ÆÊ$  GÀí¸<—%+5¹*KçPr„›q“3‚d&éÄA™éãÄ•½`àc®!½Dü§kgC…õüÁâıãÿ3
	ËyL!B
’Ÿ®sdcçºtTGp
œ?~»w?ã‹S(7G¸Ô\¨'˜’ë±`9…Zã”Mğ³g=è68aÉ·”zĞílÖ4İ÷5w‰XAÂˆi–Ğ9·Eº6±”jà%‘’&1ôÛ–ÈäW—óºÂb–!®w8yTAÒ§?&şß¢ÔF üİGTıxxiâWz¼¦¼¥3ä«,GeÊ“/‹dp'á˜
ôMß<’Mƒºp8‚à—…:ä‚Œé¥a¿7¶õ›Ië€8{aÉ×Í¨Q"÷ÅDPà_NyÁ_ÃÆöêş÷8~ª÷QÃùÓ@C{yªh£@¶!ı~IájE{t²àıˆ®â£ZÉìtjQ˜'uX+EÚÎ[ßrc«ç 	ø?©ëÂRŒxé103l-Õå§3mşºÌö—Dp<.ˆUlãCÆ ~¡]5mĞ¼¹Ëİ“FkÂ›3ã2ÒÊ_G’i†?é‹¦¾jõd~”ñ‚Ó±Ÿ =ğáĞe‹I€À 6[¼5ƒôÆàjğ<6©•·#³wUéõ—N$è5AFûÔËKÅc¸Hú¶,rÂ#r´2ÂÉò…Úa—WõËS›äY´¹,*ÛÓÈã1±ìLuÍßBófÉoTn¡ã2Ğ\–e€äñÀâXH¦;®”íèÅ<`N.×q‰ÑúL'pEf¿U~OûíÊG.mvAõÈ.˜$=ğÈ‡T !×RÇ4˜Ë˜’¡°húã’e¤ÄL¦Ö×	«o/iƒìm²cÉen­ğø	MAÌ{è¯ÑÊØKŸ:,ò#"¡á€pXmâºÅ6‘”rà/•3lÚ<·Äwë°Hå±4î“S«ÒŸ(4ó!Ú×t…Ñ§€1íWÄpÕİ …â¥HN§ùºÑ‹$_c/B‹}"ãD*ÊUKQ8­™¢Še*?X½(q1àKÔIˆz‡IıtMØèíUÀ¿Û9 Ü–æ²Eòu¾CZ¸~~sŞ‚àY°Ì9Â¹†şgBè/Ö™×à‚æ.[İFØ®W¨9/T 3ÆöÿµçHO)v’™tĞ#\ˆòI ğY?Ä)¬ÏŠ¾²ÌŒiUº’äXêèÁ·—ğ7”¡l¯JÄ+|'YÑ²Ğğ†–í¤T2u	É	dêy6†eJ«“|i$±]µ/AØÏHŒ{ê$vÎÑ£*åZ†ÃŞöà~ğ|2ö¾Ñ¼ÙóX[uñşJ9Ù!IÙjWûyåE‹—djn0ª•l×à%‹Ë¿V±`=aè£§Ş¬ecÿÎç,r¥İƒ!ö³¹IğtZ¨1§pÕÊÆÇ´ÚöG‹æàÛO“t€¾h9Jò6qVå³’®n¾e7R¹L­KsññÓ/
‚®£"ö“dÂw?©AõVOè­ú„ƒ#Ì€İÈNV»{ì…ÎnÅ¥Z|MÃ£“0bÇÎ ÚDú‡q4ƒpYÜáù°Rj-óÓ¥‘{¿Ú”^°œøNúŒ{ÛqÌˆ„$!Å×‡èİ –iåHÃwk±èåÉyôîÎÃŒÒâtV©: 
fCjz(¡™úa¿˜?FF0V×ù[Ö¹û
û;Xb§?ĞË˜ØbÏÑ´~CyIÅÎë,weŞ“ UàhcyågI¨(qÔ=Ö[Â•^~óÆM“é ÚŸŠ¯¯<„OõvÎ©ıÂl_c¼ÑÎıİG‹ï8CWày)×÷9¾ªÈG.ŠáP#â*î§4B¯I„Û|c6‚­%ÿ…¢ú°‰hHágCÌ¹”îbX.+×Kæé\Ì0Z¸)|J¯³ÄEÁî™JmÎ’R†#cÈâK´	Töaò}”—…ŞïÎ«
ğŒ£ù—Í?^60Èƒ‚æpl+CP©9=®+\ËóH4ÆØ>’¨oak¨÷&˜¥[Ü{šm!ï¿˜×¦½‚É™®ÑÄ6î¿ÊhJ95ZxÕ½Ø^bŸQT;GÔZÀy­®ä5A@D¼ªöÖ¦Vn&±Mv=h’qòë	[øz±Ûc}¾Šç+æ—¤²A}Àm´àş” çÌÒÈÊßÁÏ4DğŸ\$5éã6ñîüty°	£J|u£y¶¨ow¦~Ãñ÷†Rz ´º½cî­š{‘W¬p¹¿±ò=¨Sêº“£I¼i6H¨†´ZÏC,f¶½ºt1¥Êô]ğ¢@˜Vhª6âKÈ¹mËxå×4‡ã¢ˆ4ÿÃØ…£q’³rú¾œ÷Ï’s
ÿ¸4JßH_~®¹‹Úé
ÍÉA(f¶’ÎÕ¬Pè`ì&Q_£A(O¢°ìã‡+äŒ"ÜÈÙ–Ş:f´Ïu¬€npx,€¼ˆ®ß­çhœ¬`r0ÚÙÖÍÇ¾}©Ip¼&$)ãfñÒüeÉ†F¶ºT}cäöòW~ì°¼¿¾bz£gbÑŞ*Òš<Õöç>ò¨}†éÏ€`Â¦M?ª©.‰vd/d„É+W¬tøìK°s~y˜«ûğı£9êØw"îôÜoB0´ËFæ;ÕKuµx=vQôó	Úªœï}„‡ =_·ÆÑªäG3J­¿Pàh@Œ>yU=Æ síBê‰·Î°lgˆ¤hê¥•CeôÚ^ü yøú³I_®.òŸÜ"ÜèÀi¨Æ¶êÎ…~;ö¿cÅáƒğ+.3ûrû]»A‹H=ÅXX ÂÒÔ¬ÆÚêã71î¬š `Gmô&ÿbøº´9\
(kV¼¾ù º²ößd`P5Ä/Y!wS…ªæScEÑË$oc&U‚8ÚUR´'ÏQ=eö“>Õèg6âë‡Ç^Á ŞI¯l„g&[Ã\iÁÖèföàºôOÆ¿ˆLc„°DLMÿM¸}ÏïÜmÕr§m3f’®è=¶¹ÊÜo!¦c(-BÜ5‰/l“nÕÔg'R¢ËÂÔU>…À›ZîJUĞ$:£k¥?)ÛŞ°Zè§O>¤è1‹¥>Ü(aærÔ~ä>ÏÌ‘ßÔÚ|Â†éšöÓ>åš7sÑº×+ ĞûVÆO‹SEğ<?­DµÒ»‚›#7Å—>vÚ£êJh´6ÏnìG!¸>(>gÎñœ«¢ØA¢ˆAˆ"Êr(G¹Ò ÃÕ6ø.ú¤{[0…ZŸ‘s¨ªöè~ïBRš¹“
Õÿ'8"ª¡×O	Î¹ï ø?:¨+§zÂ›)“(•‘%¯£{Ó¸Ù=¸šÕ“'â·1Ëà Ûá(of”×u¦ŸĞ9ôe)Ï¦“Ğ¶XùØÉ½®É„nÛTcGQÊÊ*\"3ZmÚ¿…6»nËTo7FÔ:}İ}ş°ÑÉTDg?ê-ëÌI—(Iò?”%è‹ZïİFc¾½V¾†ÈZîƒD£±nú0ÆK+æâÛ×ÊÓ±Ù¶¾»põúŠœKn'84Èƒğß# !à p jpc¥zp8ÜUs¤¡4Z1ñì|uÙ¯w¬rõG	n³xäYÙj§–øô™¯èøÁƒñ#p!Ü aà#wUc=«O0>™oö‚	0Mr=äqÅuÔ¯ÄV|
®¿OíˆØ1Ô—Ñ$UVƒ®ˆªdR©¢yyÜks¹g;eKŒw¦hğ,£ãñğ||Ù„§¯åÊÏ‘Š!± ¢X8I>mT¢¸&Ç‡¬E…Ë/sdr€2ìnš£! Qr`§Ö±8ü@ı÷$ ô…©é‘Ò|9äM	ùùL¾9H*
ÒHÚP™pµ’ó1 YÛ×¼y‰ÚŞã qO3x`.¶“<tXí&ã•$¬“<ñ\Ğ>M—ı®E²yŞtÚ®Ôä¹£	pİŸÒÅÏZhº‰‹ßp``d¸:],ğ¯Îrin°¬#oÉãaĞÓnŒs¢C‡VÚ†ãñóL(¥Šó…‹¿¢/ ¿p¦&óUYK-¥Mİ™¡ç¡Ñ;^P"L¸À¯„Ûc{QÛDc$Œ G¬wZï±PZsêîi/ßÑ[Ô|×a¦AÑ&^“wµ ıÑÈ•–³å…ªŠ°¨ö-:ª«zº›_@+4ŠK"­!ØmS´Hı}D#§ç²±Œ]–Ùá‡>ˆÚfñà|pÜ2áí°uŒKPşbğiµÆ¡i;·œàjÄË­°EŒÿq¸J±›^5'ÕÃ§6Â®é„vÛ^ã@qÈn± .
¿ÂáØƒ™›¼ôGEì<GH{¼ùÃßÃ¼ĞpÀ©yRåu‹ã)C5'ÕÓÅ*YÎóİîo${•véëÚq¼IñÎülyÕÚçfjâ¨Ğ!‚5°5Œ/ä1³lMÕÍ§-‚ÑËÊU´ºæº¥8H¨-:±ëw}Ş™ RÀLî;rù3€6eÇ"æ·Äã„ñ€¡Q‹·
¤'ZŒ°™µcîÜÆR®JŸd¨µbùú´É<Ô‡YÉã.ñä|sYİÂá©°FÌ
¯­pùd ¤?h9Öªæ·g¦şòbËõ8œ.M—2nÂşA}îæ\±n÷33²ĞM¤ƒ}éŒŞ±ÖâBLîŒİÚŒ',E+cß>Š J vÍN#6ZÌ»«GwJv4ïxtŸskô,¿V‡û`ö}Œëÿ¦A/¢=úŠ(ı…Uc„Ö×ºáìÏëªèG6Š®ßcRP6DilËÊM¾L F½¢è0„ÎJUbmHn1¥ra'¬†=Ï|CCVG	é™	j×A‰Üá_mqk,¯¹»ƒÒu:€+'r¢È×˜$!oš‹uğ<0)ì&ƒââ1ş`ä›Cj¦£¿{r½êûŠD«Ja‘jx·¡"p—çñô†I¼¿b®æè½så[,eùÓ:å®d(ô¿´WF¼
Éÿ.ø$zÕ[Ã;Ÿ×§<ñöü~ùØzâò1l™ˆf~ªÈRÁñÆÍŒZïb…#ï`ÒÎ_€ }/£Ô÷œ™×èĞPÕ¯Aóg²VU/b¦¼BÉÉ®î¶dkBWDÛ2¨¤INJ
?(7f®àÄH«5`º?qèãŸ`pĞnßE~“ÔJçO2Œ- òûUù$ÈİÄÊåÑ×,Î’ˆD±§=+èX$ğ›Ï k”D±u¹}ûş¡~Ïi®®‡¾£¡ğ'¾ÏÉ
Ïì_7x`yg¯ï0î¿ÚQX}r¡n¸Í _·µ3>)õÔ¸Ñ°Êî“…fêccòsw_\4Ju‹­öG7¸ê|Mwo"%’DÃ‘å	?x*lçÿWˆ—ì÷€‰1`Á<»ït7_n€,eí‰™^ ;rGc³ÉlOÌ-ú¥»<œ¹Q4ĞZ»0jüiç‹ÒM«)Ã¼ì%„ŠZ Qr<îšóçnª‚eè´ƒV?øTKE÷ÄG‚û~yµ©v%íáş¾Oıq³Ÿ¹n¡yr3$Û¢›Àº‹¼ªtv0Ÿ`s]úqÚ,HU´)~‹^%Š¡´|I£¼(ËoÌÊCN9çC€8©ºÎ£”¶æ>MéÈt˜ß¸:*YF7½Gˆı¿C®%|3YíÂõ©ÍE‡w¾ç:?ÑAStDÄÒôe¿SşØ{'ßGáª‰5iÓt¬!ïøk:—k—v˜İ©"¨ò!İ™åÉar‚¶ÙâÜqÓ› „s!ùDyNİµø	ûñtú€{r³]ÿ…ØäÇç–oG  )2QÑç+Ô¡¸@Jˆ¼@¾M‘¹±§(æß ”¬7|œîí—:­ó/—û	»~ËXoBÒFÅ~˜˜/œ’·ÔıPHşÏû™Í:—À)Ûk#WaÆjÔ'vòÌˆŞ<\ÉtÖ­[ŞqØb±ÑŒd]Ó×kİê£8†]¦É¹DM‡Mš“•ñ—<VÛ”ƒ¹¯£9şøÏB¤2)& =à)°&Ì"íáµ°=^Inš¦øúÄ¿|1k›k[lép/\$ãxqÚœcŸ‡!+]U’şgÏn¤/é/°;+}çY²‚Í™­à–ĞÿF&êÛ…Tgi]pœ0Qìuû_;@YbÅÃ ÑÆşÔK44Å$íüu¹ß
à?0(,&×¦†}Û©°ñnhtoí#	©Ål “ğ7<.©äFóJŠkïN€«Ywô(Ö›ØÇB“ûâÇy‘0ŸêÏ7,.¥äC3IíÎ‡è:I«~v¥ × ÊGS×Ã9©êÆ÷*ş§8BªùÂL™Ô&@b¸ wş
˜F`ıì1Fæ)­æÅ²ë·}™œ ‰ë?Jy½çÀÓ7%î£4AïHtŸ2 U‹fëp·.ó­Z±ÃiıÖù¦úÂÑ)»fËRïE´|÷©íÕÏÑÙmp!Œ/.Vr('È 	‹{PdrVl}œ»'"¯a„[t_yÀ¡u6ß¡ú/}|™úÒû%»cQÿDxZÍGH²¾åH7Ï•_8‰Ô.¥32ÕB¦pô*V3å9‚Òv¤çµ„æÂM¶İœa‘ĞTd6Ö#YaİĞa¤Ct	ß~àp2œ_ÖªÕ?@öó¾ÓHİÅÙ#‚/ß}5F°
Ì?-è%¶£Á®hdÖ‹ÌÓ2åí³5ï´1G£m~»˜$“ÅöÛé:iôÿvøú°{~¤ô–Œ©è–9¿Waâß_mh"şóÙ‡Q=»&`Œü1¹ìJõÏ?,Zw£ğw•–æˆŞJ€vjië¸ùeıÓ9¥êÃ7)î¦º0ºıZ±ò•n·-<Ò•†Ø¼äVóFıÊù¯:Ä++5ÁâÚÚ[h8ÈĞp<e[¤?B'†$EãK1ÏllÕ÷'LæíôÍ	›×[±iìo‡£&â­WƒY™ÂÒé¥¶Ãéü¼Œ¹„>|i)`¹¼{×¡FTjş%O_oO² Ò¿%ˆ#¡ğ@|¬²åM«§‹ŸqT1Çlj•ı&¶¢ÎÁ¬hEÖ‹&ˆ*©]õ4/QùŞ<Õ©Èî‚Ä÷(úÛ¾¢17ZpD’!­,8JŒBRlHùª{²ÙrT'éÀ
Y3–4İğa¼Iôÿ|xÚ²ãá¯Å7ÉÒÓñ&MãxäœlQÕîg+R§E‚‹ŸrĞ¤1ƒl‹«l²è‚ÖíÜÖÚG¢DQ¡ë:" Utà³»Ëu¯_ ;x+Z§C‰ùúĞ(pT3sLİãJyß0OVwGø1ŒÀÛ7#n¡Ô@gHµœOÌ}+ïàH_`¼	óTıØy¢šÁ“(Uæ‡2Ú­£û{7øÒ›`Ï÷†'™³ºú€/ê(Ş¹ JÀ(<&©âÆñªüG9ÊªïEfî .={v›^Ó@eÈ.µäO3L-Îæ®°øÉ4ØkÀh>–¨VÆ†êÚ÷#>¡è	0ˆhŒõ3	Dê=¯iÉXš¶–¢I*=Çé²ìë¾èHvÜPaÄkt_v€Ø0ù]Ö±<zfZ“ê‡>ºÜóçCI‰=]ßè_	µ™›m;9ÛôX½åzì5óo=Ô)§fÂ’é•¶’B¯úr¿ë²Á$[@Qù‰4ª›B= ‚;r‚;’´UG
±ÿx=Ú©£Áúè{FÎ"€‚$Ö¢ODü!Ù”Úâ}ÍãQù™ZäªÌx}ææZ³ö»U˜0R¬…û;sk]×A¦Í—Ï (’E;}Bª¨Çğ–w	Ş¾àHpœ<QéÄvë^÷@~ˆhşÓÿHÜ³ÆÌÃh™ü2U¨üøG Jlì»¢†ş¯_ÜtQAÿ/‡vTÇxjš—µöÏ>ì(uæŸ2Ğ]ñiĞ&~”¼ê.öû‘ıàÁ…6§T>©âÊ„OdT#ÙÚ……w»pK\AüyşšøSÉ¸^-YnÔQ§DB‹IŸNĞd=Ói¥ÖÃV¼®¥´Ù¹wß¸%z‰»jsb-Ãá&Ì„äOTxšöã J§ğœúÎû,{eÛS#EáË0ol÷w>îıÁm1-d–Ö&ÌB™q§Æ¸Ã4SIÏB™®Æ»‚§)–"¡‹ _x ¸3
­ÿ¸;
X:‚«‡rÚ£ôX|×Zä¾Èˆw4’°UŒú±»K}ÏY¬Æ·î}±k7—D×åÚÍr±İŒaĞQ¤C{IÛNÉLqÍÜm¡Õ€g²µêaÃ©uÚ_\ÒbKgæ‹€]˜’¸UŠ‡°3-°õàOªºc¶vÏ÷oT¼k9]Ğ£Fº½éØ@Øj™š!%Ö
Üêg(¦µ‚Ï¬2Åí«5‡oÀ~>ºĞû‡ v°ƒÁ®‡Z»CIÿNøz½Û	Ó+‹-Óß˜‘¦
°Ï’ÊmÀ€/WÒÄÍÇ4
È€°ŞÓ eà05ì/5ä/3d-£0é€FB¼­4¢®h;—Ñ§¢i©n©¾n–&nÛ!ÃÂ“Ò÷í'øÇ¼u‰ßà0p,%ñã<qéß"¬Ğ£,9UIü#º`ª ·°<L)Íæí²õ¿ˆ^Íï	ˆDx<(WŒâËÆF™Tâ¾U=kV>ùXB>¿š›ı)ˆ>j¾Â9«qt´Æ÷]I{wœ‘øTz‡[ƒsİòá½äØO¨a¤Ğ©g5`œí«Ù½øIºËoqÔgqÒœ2ÙšX ÷'lĞ­AƒnÙÔbçQ²„M›M“M•Í—-–¥Â‘OóöÜşşøxzš›uõß? ( & "À!¨ FÔX‰xEgbã¢ßÁÆûÆ¦dcağaNrdœùD~}çğAÍ:¾E2ºškÍe„b*+¨òÖ’ø
Ï“ªÊÇ/*¤'b¹ÑŠä_3@-È%®æ\¾/NúŒşyÂ ÈÁ\Gïİ?>¨(F¦ŠÂß) &À"è!¶ NÀh=Öİô…‡¦ósÎ³ìFwËu/@$#~¡Ø@bˆ´POD}¶¸v˜ğèg‹{nh:K¢„²Î§fÀªÙ4,=Q€Ii/Ö ›B›$x_÷¤Hh@¤»¹­*à²{›u“_À7(.¦¤BÃI©ÎÆìjõ×?dúg‡ê€ÀG(
¦¿È9®ªÄG+J§OŒ9É§ßähæIŸ+üĞ×l³JÍÏ-¬%…ã1ól}ÕÙ×wòìç–¦öbÉnà¯|Y³êú¸ŞÌÈ&ëåxl•ó=ö©¾ÆÈjî—4&ú
—OŒ:yV}Çğ-Ñç¼®á<Øgª­òd(J]ìĞªû;z«[Cz‰Ûãpq³O"¸œ0+J=µ˜½vß©	õ`Ïi£ÒşLıÂEŸ¹ÃäÓÒ{À2™íğrHV¡ğõW¹ÙŠâß1 ,@%È#.¡ä@YHÎ±¬LEÍË-¯e„uº=¶{íg‚¢ôÁ§(èÈB«™óë–DvF¥lÈ
î¿4H/N¤C}ÉÙ®âÄq«\7†Û*yÑ~Y?CÁŒ˜wrê%‚9ãÃ<á
Lˆ1­™âÆB°9‘’káû°dLMõÍ¿-ˆ%£AôM37Ş$àÀÌßq…Üo‚ Em`¦²ÂÔsVÇFêŠ÷>°(L&âİ±¡Œ@]¸Tâë-ÎuYšrù½Îq™B®³xX€µ¤|6şº‡£vñ@G/õ:yôÿs8ê±·N½ÌI­‹‰å-¡)cÚ&ÓO¥ÔYIçNòŒ}Ù‘¢ÔA§HB‰œ^Ñ°1$@Òƒ$¿ba”à}Ğm «nî`²,ú™ˆ'yöåŸFN±«³ó!=ÿi¸Ê¶ïô<iØâ¶ñü,,‰­sßà‡13)ÌQÙ|WÇ:ĞW
Œ3hJ‚ğñĞLú¶œñOº“ÿw8ª°G
½ÿ	ır™íu,”:×k&—bÖ‘¦ÔBçI²Íœm‘¥Á+DÑÀÀÕO&%§“(5’ ¬Zl=ïO>€]ÿUÇïFÄ”P0»˜g’•—–´VÏFì
õÿ?8(*¦×Wêìíƒ‘$³bdTãmÑ¡uo#nİœµrsê¡„5ü;F&‰|e¾,–		áşğx|™óıõ¹¿
ÈI~úa£WÁ¹z)gÑÈ×1¦¬BÅÉ«.Çdj“WÆÇ‚ôi%à‡}œ°¦î>â
“bÙ…Xçõ‹æY­ÂÅ©«Çzê›7nµÔe'L"á°QŒ]ûA»HK!ÜA²û:ÉÊŸİtw¨·u¯M ¸Œu4`Ÿhpº&ú•¬ y-µ“´£½°üH±¹Ø¤ØVØa(7<Ø“">ÏÓÚWt-ße  5ø/:¤+gy¤ß·Ç@V¬»p¾²|Ø`)ÅGœ5ö¢‡lZ•Ã)ö¦şÂøiº–Ëy¼5½R³?+_Uá¶*¯íç«‚ş}uÂ6–îgu@Dä<ÁªÕàİ„f-6ŠŠbªfx)0’K[sgàgÌË0Gl
•ÿ86ª®Çj»W{óhkò*­³€9Œò²UºÈ*úØÓNÕRÜb^OÆ“*Õç'2¢­…˜[ƒuéŠ^³p×jB*n¦=Å„…!ª—§ÊêWXlªËµvÃÿJC52%î^rŸ]”8Wj†—Ö³&Íá¹ü»ßX‰a¥ı ¸Ù|$ãrñİ¼a‰Ğ^ä sxr‰òê@²›:áÊ]|®wî.Í@Ø¤]*ş Š-Ï‹–îá®­Š4à.÷—6}a‡§ ©,Ùúâû1»lKUÏG,
¥ÿlj¾ë¥S>§¨K.•VdûiWĞ¤2Ãm©Õ†çò³=éÊş˜Â¡\ˆ{„DTGJ˜¼5‰ïô0lA î'ƒœFÑÊäo3T-Çeª“ú·;«|GYÊö½Pó_€)é˜÷tmğ!šÂõÍ±Ü¾™@ÿ¢dø*^,
@ğáŠŒ×§5Vqt5®^~OÜ2À]jº—¿vÈî°tLMğ¼=Ì±İ³€*äy'&Ï”ÓôÀ2TÁèÆa!Ï`lô7?n¨F·JÎ,\%Áã(q’Î;–°ë%ÆPDÄ éyZÎƒ,YåÂó)½æÉ²îÍ´mUœNWúÀ)FL¼Âçô»4¸: $Bx€TJ3&àÓÑèÖE[qèwJ3«[,MWş<^	åk¸J¾\>èXv‚ÙbÔ§tBŸIÒ\‘},Cø–å–óıöù¾úÈ{.›dS#‰˜nH"*×<ÆUlsÏ{”t=w^Ñ¡°?¤DsÕæ€ÍFkU×G&Š¢ß 8@*ˆ'ÒåßM:»Ï¶ÖûKÕu–¨öÖI•f‰`æéÇ—I-´ŞìoÓÒúå»3mÿU¸
º¿~¨F²ŠÍŸ-%”#aöÙ8Ôhh¸•‘—V·FÎŠì_5À/($&£b·Ñµd ß”›/Cqæ¨Ï|¿Aº©ú4nzÊ!ÀÇ‹ši(ñ †vü¯R¢òír0ñjãW1Æ¬jÅ×+&§bÂ‘©Ñ
„ü¥2Ü-¡å€sò±½ŒIÎÑ¬dE¥K8Ï~T¤°Y?]è¶¸NÊŒoÔ1§lBüÉŠ.è)‚áªå¨G»01Ê›²À¿ÜI€˜øw•$çÕ	@xò,[Ôh¡×ââc·èQ¶„NÛLcMÑÍ¤mƒU™µ÷µöM]´JF€ÇÜì~õØ"˜!’ U€:²û_Î3Î‘‘@§÷«?p¤9„ªˆbf¡årÊZÅğÓzÄ)«fÇRê…·³|MÙÍĞ®ÎøÈÍeÍª_ğ<=ff÷}¾™ˆRŞ… [ x9¹é¬Ja¶¢:U‹>miÒ_Í<ëv÷^ş€xX‚³òİ½ïÊÏˆLlùAÚñKHnş¦øBú‰»Ëpo\÷xİ×^æºÖo_ft†ÿcŠfãğÈq}ÃY©ÂÆéªöÇ>ê¨wÈ”h["^”¤.ñèTõ}à»ÏÉ†İ"ØİNgSR…Å›+guÒŸ%#Q²2=ô]QÈ ÊÙVE¦òpŠ -ÆÂß]+ÖeŒ åÙI–úUØ)¢¦Á‚èY¶‚ÎÙ¬bÅÑâbGJÏf+x¢Z¯C	û~ûX{B›I“NÕÌg-Ò×÷ÆP\­‰´€µxÛ:šdÒ3ê+('f¢’Á•¨W†ºÚË#/aä=XŒ4ôgLÆm>õ‘cA°‡Ûœ|QÙÄbëQ·DN‹L_MÀ¨=†ÛÈƒ€Mª¦Iã‹ôË_V2qÑe»`óib´<OiÌíöõ¾ÿx>š¨S÷¾wQ.2’ÊoÕ4óD|`kÔô°»›É¹2èÑZbœ‘ôTGX
‚¿ˆ2Ş­ E€{]m1ÌXÊÃßŸy¾«Ö=F=ªĞõS7ıÀµføB…3/àÈœèNöŒ~İØa¢A”W~†˜ZÒƒ™ãñõ¼	Ø>â¨q†œZÑÃ$i±VìÆí@ù×:æ«2Çmª•‡¶³Íüm¹§Í¨^~°0ŒWÚ¬PıôG?‹YçíóÌË†ªe˜µõ?(1æ¬rÅİ«!‡`.ÂBW9êj…ìJ+×¬Çê³7î½´INÜaıĞy¤†aœ´ïÛ†ğBİ™ß­Ñt„Ns{9Ÿ°ÕàVYG=˜Ûªt3«>!V•d&4×6 DeÉëm¬”40­DşèH‡}˜!ÜC–|ëmØ—.ÿò“§½û¹ƒ¹áˆwçÓQqH-ad!6”˜uî.U|MVo¿Bƒú£As!_i2Rİú
"PUE0:\” RºsË÷JN~mü¸u¸šò®4[oCT	Ç~ê˜wµO7}šËõÏX¬p~îtJf³W'Æ½ªÉ‡.Ú¤cQùÄzë[7Cn‰‘=¯ †tèáÜ i†)ë—×G½ø`¸|{ğšƒAkğäO4ø|œ§$àRW°_ê>‹Yú’Aì¡Ä'©Çº‰»ï8v’Ğ6S›øgUPmi¾;ú‚	¡Mø=dX¤÷¾Ï§­æÑ•T67E:#ZP8W%<iëTCºÇqXu@kx0êÍÊÜl<}Q.µğ6ùìŒµ7jBüÄĞêèT3s¦NDKuÏ_, %ø#:¡ë wxš°![W²¯|»wË#}á Ã)Ø&â¢ñ¼XIÂéœ3¡zYPÄ1«lGUÊ‡/¤3mùÕºçY2¢mÚN´O}Ì­òÅ½	‡~Ú˜c‘õ”p‚à–Ğb©ñREN”W}Æ™ªÒÇ%ª£úÊ)OÈ:G#{¿¡hÔv,§YÃÍfkM×M¦‚İ™¡’ÀU¨ôÈXj+Vn|ôßdÒdY²	a2v+AçHrœQ‘ÄTkGWJôİ_Tn¬¬şbqm¼lû¢Ç@«bô©†-ñå¼s	İşá¸pJœp<£(±Pz-“T‹½¸(øÑ†–^5¹ ÁêœDéò
yëZ÷C>‰è^ö€~Øb²áÈÆóÚúÃ´!¾~2x¹º³¹zöé:’‚¡W·l}màïùÖyìõó?=è)¶¦ÎÂìiµ¢g¯"èáÄK:QsüC9Éêî÷4~¯XD‹yŸ³Kekí‡‡p)ı¶‡±ëıWh®¡àª>«Y.+_ës0é¿ĞöÑVBß¯¸aˆ(\H¨aZı_°Âÿ+ i›áfMæâp}õOT¡5)–îÌ9ªSŠæh‡ë+˜¦Şğ§Šøñ˜ ã‹ ®ƒvV|LOGù€ ªÑ­	AH2 ìÈ%¦ËºzB$&¼Ô‰ûÍ*Æ]R 	Ê; åì:õë?7h.–¤VÃFéÊ‚½·(bfãiÃº×ò~9Ûêüw9ŞªàG0
¬?è;6î8‰>lÖÿU™—lé¤‡ãK™ø6¾tÍ³ä°OÈÿ¿…ÛıŒ“lò`$öÂ€k Tšşz‰¼Ü$ …ã+ÀjÿÅM¹™^—Ö½ûÖ‚VáuÈ©ËÄsò‘Ù·Ò¯•¯gµ!¾Q³BLCOKxD©±ü¾ÊİLojdv#u‘n'e}‘aca!oaÑÒ%_0«fe%z"—B“}^J:Ô+'gb’‘•”WF¶ŠÎß,J%Ğ#$!ã`qĞd1€lxÕÂ%â£1ìXuÂŸ)Ô"ça²M”—}–ĞĞÒ¤ªó½FçÓ¹ºÊË//d$cuÑß$`#"f‹a'`
P{Å (,Í¶dY3ÂùË.PçuÊ0/UUŞ8j˜¶µÏlt™¿"/Ò…%„#aóP}Ä«rÇ]ªõ_óÏ„ıàù˜º¥Xrú2»TúneKLMü¹ıŠùŸ:Ó|vn7'‘—İ6FÓ‹—zfdg/(Ğcvpµ&~g—Òa¿ã1ö¬~ÅØk"—aäÃ€}©üÚmÃ,Û’ßTïˆòÁ½¨I†ÚÜc!Ñ®5G'{¼ái$vÚ,”´=ioIÔç|r™İ’á•ÂIRÚµˆ÷U…aU‚5n“xµÅ+'qâœq‘Ü&%‚ÁC`8ÎPŒ=í[Â¿
Ç™,MåÍ³-å³„íìMÍÅ#@ÿ²Ù’›§ä~ĞÂ0v¬Åğk<iö–ÔÖøfú’û»w^¿3ZAêùHTÎè­&„õ(`&"Ô!§`B	Ãv$#–ÁÖÉ»ço³áÍß…ÌkƒT!q 5€€aCy\»ŞÔ`gP„5›oT5Ço*Ão^.ó‘À›g±À$Ìc»W1?åKRêrÄÁ£eÓeò“=•é—6Ö®æÄrë]äÁØ\C…; CÄ·å™¿(³g«i±:J´|<éòöı¾ùˆzŞÒfS3QŸk>+cgQø„e›SEõË?/h$£vÁŞè`vÕ}œq5bTÜ»Şl^írÈş¿_òK¢	¾ĞHd“|UÙÇ"ê¡· N¸ïŠHçïèk6—nÖ”f×Ræ…²Û£~‚Ú›aÑ’¥çCcöşÜxaÚc÷t~ŸXD„OÈ/‡W;Æ³*€©lrĞÍĞ”Ï¤LÃU³áïzô?shÖ±¦ÌBíÉµ®Ïn¸PàWo7¤#ÙÉ8ƒI£Şi—B©aê é»Q4ğ¼&Éâîñ´|OYÌíùµºŠGeye@sáîÓ4|/ªC3ı‰@õ{Ûhyp‘Ãi÷Vş†øZúƒ;ër÷]¾øÑÅ>İLÜêàŞµPe¤g»g•®íø=oJ=ğ‰‘Š«·k>	ÓlµÊÏ/,$%ãc1ÑìduÓ_`Œjn!ó7”¶1–¶pÅÃ+)çfò’ı•¹—
Ö¿&È"î¡ÄIiø²Gê‹š y€n`!JÚ&İØ!wC÷vÁ«O3İ‘ï…Ó›:Ók%×c&‘âÔq§\BÉ˜nÒä0Û Sâ³•0°-% Ó*…“£ ßZÍí§9÷ªÂoEä•ˆ0á2v²Ím”—w¶ĞNäI?.˜Ã‹¢ÀA¨F¾ŠÈ_.€$X#B¡É€n¨A.äéÁU†Ú¸²ƒ“e¯/LñîU‹x*ıóFU¦·œuö  ¦ßà9°*Ì'-â¥±ƒYıÂù©Ê“‡yª q\¡&ÁKm?l† À:AÕòÁ·$;?€W(˜õN`¿O>½èI¶ÎÜlaÕĞt@æ#ÂaÕy¾%—c‘öÔ~çXr‚™‘’¤ ëGíüÑƒzpXv*ò—·,ìGN½®˜rh-”fŒÇ±5“oÔ7'n¢”A—HV†¬­u©Xû³±ºd?ÉÎVƒ,ñÒ³DY´ª£7ŸU÷ø ü_9À*è'6¢®Á„h[Vƒ6Œ†±ªVñbA6‰GY§¬øtM‘ğì_İS¨|3øNA¶s,Õ|ª|ÁÆèjö—>Ö¨fÆ’êÕ·'añÿÅ„½Ã;ZLç[Åj˜‰"çÅ‡E34×­·Gà°A»è•~Êis…Õ0–”!`šQ¿îW+F§JÂ)œ&Ñâäq³\’™é?Ò•‡×Gk»¶†|é$LÏË3/mä³wŞ½ I€Øk*àÃä.¡xÓÃ®öÄ~ëXwB‰^Ô gxšµ“[G¥-9ÄªôG?J¨¼:Éë.÷d~“XUÂ‡)š¦§P¬¾Şu‰®-ªeáÀ_½‹s9ê˜V£´£xı0åUŠ#ª¸”5'WŞ°’ŸûªÊğÏâ^ØqSæJ'_6¾­ˆE‹_t x0¬3íû5ş7HohkÂëDt»ú±!-]X–	‰şŞø`z3wmŞ• W ¸:Ê«/s6sÔZ“2&ƒ¢ÒC¤"C~‰Ø^â€q˜R±ÅŒk×q¦œ—ÉĞ<Šˆ¯†êş±K¥İçXÊ³œÍ ¥Î
_‚ºY£iı{İíŠ»­8ÿLØ(÷í¡µ€O2½í‰µÏl4ïw4¯pNN0´vxÚ¸c
‘ÿx7Z®ƒYûBûI‘NËLoMÔ§}‚™™’ÒÕ¥×VNê¼í¿‘5db3fnÁNÎ4QÌKL2ÃæÒ•	uáß0`,%ô#?aèv´nš<?Yr´¹2-ìŒ2°Ã¶ØyF‘r»7£0óÔÖÅÒäƒµ†Ïì35íï5´/d<¦•¶j´m©âôPvXõWL˜½«­2iÒ?Z;Î^‚nceæ3ìŸ! Ÿy—©ƒlv£ëêq¨F±ÊÌo-Ô%§c‘ù¾z×[&ƒbÙÑ¢äA³HMÎå…·Ém"…ÌÛ5£"O•ø*ÁCÃi)Î¼ÊBğ	¼>Éènö”~×Xf‚’Ù•¢×qóôîêPÊc.8aºÓíOÖ²Üu#Ç]™´5›ûKì4ÁØè}¶™ÒÜe¡Ó eø:µ®C~:.ï¶²½×	¿~…V/ráÄÄÀØJâ–ë°üS9Åêë77n®”DWKFJÜ!Œu5³_—vr#º â…A±¨8şŸ¦¬x9’~6$™ß!Õ‡3eE¿{– 1?².Ò¤eƒSÅòë=·i–Ü­¶jŠE|·îşÙ8z°½º¶Ëï|tßrà°1Œ,]å±æd£ê÷“ƒòØÔ'×HúÎ#V8jo´¨øzÉ®‰!<LSI¢1uÀŸ7.´$OcLÍôm¿Uˆº°;YC.¹~ü¼Ä®êmòe—3bä©Ï<~¶íé¡É(–'-…ZEä3mØ¢·¸\JŠT?wÇ—5–¯Ä6ën÷T~‡XZ‚ƒ™ò¢¨éêÆmœ±,«dîÖL[9{_Å¼QõŒ«ş{g/'vÆ6†Dk,¨û€dXBµÉ.Ü$aãPqÄkq×,3ÍçİÆ½LÉçN†4oõ®Vú¼]ƒMìjá¨Ø*Ò9Í/ÙÈâñ±¼LIÍÎí¬u…ß 3J-Ğ%¤#aùĞzä3smİ£ñõE¸ŠÈM!zº(T&‡bÚ‘£A÷H~˜\"Ô‰Ë.uÒ;˜ÌS„F±b !
šñŠË}û£‡¶ã×·9ªÜG!Ê o 87j®½V»FËJïO4/}ä³r¢îèÉÌK@=é˜„¶Íyiefª6r¢>ûOF»êpHùŠWpp§ªpv)Ún”@¹rßgGí2ó/ŸŞá—‰ìåCóÇ»5‹oT0l:•ë7v®è?7T
:Ê^Á  ºCrÂIJ28ÍøˆüA¹ÈJî4\/Aäs~·áÍ× Êœ#”7à‡C„¹¢nt¸ ãÈ»ËPz«V£î‰ödJ”ùSE¢¯¼1~Y†G®mÊ©‹»j7Cf‰ÒŞå s ø1º¬K¿.`H ”sË¬åw…"¯û"CãÔF¨kèÚá=‹`âî¶ôNÿLxÚ½£	şØ7ÖÂÖs¹ImÏü+TÉ}ŸnpÈ4ÖÀÀcš)êÓ–†màîÒ<üäœõÿx1Ú¬cÑû${c[> ‡ ·E¯:6OxûóHãşÈÜÛœô.O\°7şıVCw~>F£0†­vÙuSg2eW¸ªU˜ºµ‹|0ì2õíëfÜnLğ0^l]˜ğ³q?ï•;š´SEü9ÿjø:¶«4#Õ’’ççŠ†=…é›6ÓnåÔs']â±˜LRÅÉùHtpŸC	ô>ÿhxš¶Óåüs9İêá·0NØ^º¦vë/Ä
+ô‹Ì%×E‘ùµËıM(´‹åŠ€û­:€¤
1¬Â/ÒzWr÷¬ÄŠ>ÏÚÃ/¤<CiÉÖîæôrÿ]¸Š¸_
Åg[mbò­ã‘Íù[… şÚbBhûyM|™õ’ÿ¸7
®¿H;N«LGMÊ¯ğcÒ+>‚+7§e ’“•Š×&°"Ì!­àE°?}è¶ûˆÍØ?Ì’öhW'µÌ’$^P®˜ +ØQ¸~ßQÉDİ6Û¶1ÕÇ[‡§,i«äôÉ™÷é5©ïô:ÿk8j¶—Ö¼fÉÒîå´s®Dø³`Ğ;+qç\rİ˜a’U”wB6åŞi–2kšq¤£ÿu"¹Yå¨Û1ìM¡²h!æ>É‘BR–…–ÛãvñŞü`yĞäCf!¾ÒâAï|İŒ¾g9åJ/gÜ}ËññDE¾*«Ü=ZŠŒ¹ów=Ş© FÀ
è?6¨.ì¤jÃW)Æ¦êÂ÷)¾¦ÈBîÀò^¿3v"ş·8NªŒGÊ±¯D=Ëi¯VÄpëg÷rÌ)Şíµšû®şşÏ
Íè1r1\	nD¤½8®ì¾C.8O{QÁ®¬DEËK/Od}õÙ¿"mıå^jH?N¨F½ÊÉ¯.Ä$kcWQÆ„ÛJ#0ó+&·bÎ‘¬TEÇK*gØõ‘[”~ãøIê›gÏ(€ª™ö Š¡9ŞÌ”HøôÊIé±Lú«Š¬9ò…2¤c×tÀ€w²°MŒı‘¹”J×=&‘"œ£ò¸6CaÔ½¸IŠß`1Ğ,d%Óc%±m?·Ts’®jmÖâjÔç2ıŞA?˜)å!™ÓªÜ˜ç²½‰ÑdT9muÊŸ/$4#oaÔgtŸÓPY`{boÅ´}¥¸Ì…+'{b›Q“DUËG/J¤`?v”º®ùpîüŠƒ=PÉ9(5æ¯2Ä-«e‡S…ó=½*ò›™êàƒ¤9úŒ¼³ŞK?Oh½öÉ¾îÈtnŸT"@{ÇP J’{»a9'Vã‡)K_†Ëïs4ïq´OqÌmƒ‘ù+]“İªÅ#R“±ìA¿Fº(E©@Ñ
ÎŒÔd›¿•—¶¶ÎÎìluÕß' "ĞdÒc<eNÃvÍz”)còñÄÎPCÀê‘‚ ÒWçlAmñ/©*x-Ú¥£ùøzú›;ku&ò"Ä!ĞçÁDB‚¨Y†‚ÚÙ£"Áá¨pFœ
Ñÿ$xQ	ä—{'…»æ«Kµ8s+ÒhãI±ÎÌlmÕÕ§'¢¹ŠØ_"€oëeÛKı5Y{"âÆ‰Ê‘xÒ…¥›yõÚÿ#8!ê w ¸08ÿJQ›tx§¹*0Çø
ƒÍnÑ•e½àñ‰c˜Ò¼e‰Óåğs<éñ¶üNùÌ©yĞ*U¯vdÓÇEÓùRÆ÷®ı¾r_ŸjãïˆÒXz‚›“rÕİ§!‚ Y€Ø9¢ª±ÂzÂÆNª¼öÆ&
6ß’A©ºB(p(¾1J†¼âğ‹ÒR	CaÉĞnäsw]Ş X@ˆ9ªúG$
£Ø8bª‘‡Z·C‰ü^’;«+³¶¦Ú‚‡š²Ó¥ıƒ9™êÒ÷%¾£A»ë0È:nU¾ôiï(ËŞV±nû0?¶-â”ØÖô£‡òéº˜ß¬U'6"U_;qéä5	–gPYdX#³RÏ}âúF7HAL$­ˆè¬ß|Ğ!45"ÕV;D„Š×-aSj+u›î EğFs¨W0¦D+Éî°‡6tcÌâÜ€1DìüD‰t_Z‚uYu§ï“Ætß¨É"ˆ¤fÁxwZƒYôÿy¸Ê³/ä=³ß—¦ü‚‹"­»„ÓúÄQ+[gCR‰ÅëwtŸpP1û)š-#×ŸL#lq«ãv şéAL0Å}ÔKÕwÔ- ÑÓÂ[¡€çíëÓ‰Ù¯ |cã(ØWEDfJ4l¤Á¶‹¹jwc1S`,†ÎwŞ7Y^º3soZmNö;ËÖŞI!Âƒ$~S9uÁ¯™w#¯Z—¬w\ÊU†uóİ´‚Á¾)B¹,¹Ô»w6ÉQø¸Î
FÚ:rY|·®g…Şø%hĞC$	ã~ñØ|b™Ñ’äU³GÊ½ü	™>ÊBcV‘ÆÔjçW2†­šÅ“+çw2ß×
ÕGbvêYñ)Œ‡¢ëyZ‹òÆBõÉ¿.È$n£TAÇHj—V±Æ¿=¿˜aã¯ÄMù?‚}*†§Â³)æİ²á°]ŒDÑ« ®KOsLÍñ­¼E‰Ëïptq£a1ŠçsßÑ¿$H#N¡Ì@mÈ„·N»LKMÏM¬…´İ9İ%×Tqğí•Ä²rF‚ŠÙŸ"Ğ!¤ C`	Ğ>äZ #É©ŸØªS¼€¾ä	<ño#T!Ç`j6·nÎ”l&ƒÓQ”Ú-Cñ©Å4œq¾p„ú]¤ƒxYÚ‚ã±òÌ}­Ù÷ñUÄ7 –ó-cŸ±,B¾Š‰^ô3‡T…A„[~ƒXYÂ‚é™¶ÒÎåŞ7@‘ˆdï-l[,±ğG¸éóy6,V¿€¤ŞÜ`aĞd4ouÔ'p"ìdÃ£05K/ÕV
|ßÍÀÚ@_:ÈBÛ=(¾db ©¹|~ôÛ¹¼JÉÏ.ì$uã_1À,h%Ö£&Áâèq¶œNÑÌdmÓUÇ*¹ç
ò¿=ˆ)¦ĞBä}á?Øp¢îúåe+˜†Íší“5•ï46¯nÄk24ÇÒT±urõ®Ş”hA'¨s®ª Ú<X•Ch[¤»ğx{®È¢Pt¦îeAŠna¨!„ˆK·>©j«–aõàÃÑ¾‡¿ïµ€ Ú¬JS$¨Ñ/]T9tRÂ(äEşÉU/KVH°4âÍ,”¡¬2JOÎ¹˜!‚Ú+J%ÆQn2®&ÅSØ4“?€‰o/¤›Ö»Ğ‹ºlÚg‚'îµó=8!'æ½²É®İ„a›PSDË{[	%@SdÅ¡28“ítT5Gp
œ?è4v¯^Ä kxÕËO‹òö«W9ı¢Q¶à
*:ËZFõ«Í?Ş›'ç1T’²w|¹,ƒËe‘¨¼O }çÛ_â&’’$f¡ê”ëâJÅ éŒ_‹+²U$~`†èXq;ÑˆÓë˜F}KUì
ÒOD¼ 9Qõjôíõ·=ºâx Í‰/‡x}*ø—æAÊyÿR½c8áU±ÂÎìšã…Cº<¼€ÈTM‚¹RimÉÕ®çr»]‹AŸ3FÅnU*–ŠŸµ¦»÷%~ïûSØ»ÜZB_mj£#ôÿd’5
°?(=æ©²ÆÍªŸÒ{èêC(ûnY7J™¶7î´tO_L ø=óï‹U‹5°03l-ÿå§3­ù…ºÛ#aØbñrÇ5¹F5mÑ­øÕë ,Ä]H‡Qš„SEóK=Ïi¬Åö©l²)5¼˜VÒ†åšóõé¿6È.î¤…i­rxí—•¡(¼RScı¾“ b0HSæé‚hbñn"¾µˆOŒ0-¹Mæ½(Â%N¢%ÆÎÖŠÑ?ø Â×C×®^½µ(,Ÿêó8›Æf_çß- %Éeo½ô}÷KÑf—ÅàÄÇ^KéXıİ¹¡ŠÀ_(Hcùfó¯D}h"şAûî oË!C–‡2lÑjçGˆáor”XÛ"Ó†|ÑÆäjóW=Æáï‡ƒo¸§*ÕÄ®`ÛO#Liˆ¡)õG‚~S½ôæG]ÀÙ¸ÖíëK>hwgóíí5OWã¼Á?“/×9•XÚ&„ÂkŸì·@ıˆ6Ş’SäiÍIq£’`¾×væ´òĞ}¤QÆ3˜ğïÀà	LÉñŸÓŸØp6T†`bÀN6À_L!¼Ğ²Ù0fd~†·	~íÕïH‚#'Tí™xMÚëXÀµİ.\Ø•Â®[ó÷ò–[¦99ÒòµãG«|ã¯—öAõpGÊË’ëİÄ añ@‡¨J©9+THúb}Î™¬€„ïnUi;ÂËPİ3ÜÚeóYx…làòÈ&®ş‹€i×Á¢ ÅÁÃŒ×ç'”uíbìÌ"uYâ‚ñÑù€üåE'+Õ[Jh‹ú7ŠiK±÷Gr ®Y²Š¹W]0»|$àÊ‹,¬ÆäÛ»í{´gyZ”èÿøÌsİæ‰`Ì+IÉsjá}¤Ìö"'j¢—IÓùÔá[¤cz#¬´ÚKï9ƒ¢b&©«ĞdÍìRõ®~ë{ÿ.-ÇÌP›¨Õ™§ŠğèËC4 »`2"Zò:yGú¯”¾g¾)o^Ø ÓKjÚ?OXñ†õ8‘Ââé§™M!É(9·\ôcD]ø°@ºdÍÌm­Àæ_GáwÌŠæoÅèZGİjÄ¸‘:böŒ2İ\RÓÄĞ[nÖ<
™Qá‰õ(Ìhy¶5±Ó	 ºÁ8lâû¶Nã´¿ßX‰÷²<gŸ¾V×FæÂ·yå{gˆr§ïõˆNHƒîüÛÃ“Ÿ®7<b©`ugI|,eTà6®¬$êœKe:™õZüwê¯O«~"KI‚ÙÔ'•á6M•‹¥hg³ÖaµUuwéeQë`Ş>Ö™Ç$¤âÂ¹aÿ„›µ¥&ù–1‰ì^½…>l]t¼ãÑèÖš‰xÚ6CKæu)BAñ…|íïœG^ßèF@Nnºï8BªG–KÙ|fQ…•­-ç¿ƒ¾ï¡60¨3­²€úoN5qÈU×õQƒurñSjH§øù]‚Ì™$šMÇÒôU´yÊ,Ük5·Àq”’6Ô£Ùï¥ÃšèıµÁ9h6ï‚êpM*aaÏPlLPº3~¥OÀûJ|‹í?‡jj,ğñ1
šà{õm…{9§Ûñ’ÕéÇ™•®×ÊwîQ@ò‹IL?5G.sÒ«Œ}kµQTs*ÒÍf«¯ğxM1I@®­+ÿ×]{y’Mv1iĞ%¤í4ú¹­^&<•Ğ­HÃQ©Ä®³
l‚i¶ÄüœE àÄÜËÀÁŞ	GFÇŠNh<U¼¯e´î‹==‹ì57şo÷ç::üÃäŞÊõæÿ2°hûáÎQ8 J¹}}åè˜ò~]ınäˆ»&†hj,ì†±	ÍC)—±¦v9ãÎµ¬@h¹kö^À²1Á¬–e³ü·‰8å‹0ŸÙæJˆ¤!3X•ö×­ç¸vïºAı`ûKB2tÁY·BÎÁé…9&V6æ×€‘¤eh—úvŞ1ZµJ(7)¤²ÍŞ„:Õ‘
kB—Ú—ÒÇÆ_†ğ;umi»Ò¸ò¼Ò~¹=b®‘„T[GCê‡_¾>"¾VaµGyem¦4ùĞŸ*ô‘C«ºw:!êíòBJü®CÓåì+5ç!wÃaŞ+Ó“Õ‰q¼í ŒŠ°ÒÓ%¥­Ffµ¥4° /^h<Ö§F©[÷âKÃki×V¨Ã¥–´í|úû¥w?¦ô	MI-ó×¥uœ¾q+cªGˆkÀÚÔ£)³¡86Ô’˜åª@J­ÏÉuQ¹"Y#ñ
‚ê”·e³šlLÍ’cê÷Ñ-KÄƒ¨ døa‡™;ë}ØÚÒ‰Åƒ”(¨ÆÍ—ä÷,~¥òC"‰áĞ$ûbÑ]»A‹€BXtŒ©ûÇˆ¯ë{t ¤š)z)ô&ÿbøÙûK=9_\©òä½ö€Øz×*0p‡f{6h#ÉÙév0 …°jj];ÇtjŸW´Y€%hd ¢“#Õ¤.eÆ¦›ÔiIğİ™Rì0È)"†«áoÜ’şÕ¸g
’¿?ˆ7®°DLºôDÄøäí>É(`cÁ°ÛóE[¶º‚Ê®*rÚ  /SÜ9”]R78ŸnÖÔ(aRÒĞÍÈ] ~…¯Şr`1•Q*:«=@›-#“Ógà¤>İ­ø6Œm3¥™~Ôoâ"Œœ:ŞŒ<äƒÈªßöÛmìïs3• ”ã(	~İ†$‘e‹SEğ<q,¿Z¿ø»µézˆÛ&%­ŞÅ$dğ:Ïk¨uò2€-*‚§¢İ¥ˆD–Æ	ÈI=xKÄÏF¬±>Š|¿÷L5¸”Ê:¥«¸ü­+eÕøßq›‚.4"æäÉ(êFYü«q¶B3¤+Jâ4ÊÕ[Ö5†œkÏª±İ7šè‘Ökg§ätÚ×8ÈÇ(##Ú§0ôÜf•uÖo"}©è˜‹ÿñ·‡µÍ†Ê*©0ÃET3GmÊ•¯YAa÷'…U)
š`­ğÁ³wr­İ®‹ÛtPÀ?h·Y½ÂM­¾Â $ûÀDğÃ³H“zRşNº®r†¾ÚF†AØ†‡ÑØê‡ü÷ğĞúû;;kkWWÀŠ¿‘wrxu=RYst´,m8ÜX\ûÊpp1ñì|uÙß"…oärNX­OõzÉrÓ£±áõ´şíØšQd5)Í,pë\5z]#¡O>œï­Ihw¼òO"Œ!àQ°A hñg·Mœ]‘Á”hWVãÈˆºMd¬5&™K/±p,eW¤:¼dïq±_¿·9t|—¦°¤ßìÁ9˜›Z¡18›!Bg9ƒùfœôÂÈ¸^{i®
¨Í>*Øë"µZtE«Ñ“ş³GÓ·ÈYbGf|Æİªá‡0ZâFRµ²t¾+*k[—MÓÜ*¹lµ³épO‚¸èw‰½‘¢l}ào5eÒ aæĞ<b“$ı	2ÁĞáAw}›äîM¸[ÍqÈ¬˜ºÔ=¢|¹Ø÷Ÿ€\Bù€‡¬54R»b;0›Gcû¢Ê0Tâøv2Ó®Fû= Ú7@pÍ«i‡VÚ†ã¿¶k1 —ó™ßŒ¬aEŞÎqãa±TCt	[qğø>Éèêù„z_T3GéÅ…«Ÿc~Y•4(ó}D¢ÍTMnÙäIÄåVÌpÖ'`÷p×V•~œ#Ïœ—QÓÿ¾¨’ä‚4:æîI4ÉŞ_h1Ñ"üdÂ(/¤DüK	~ö©`»½ÀÓÉáíã–üfHZ¿u|w¯åÓ:Â[nµeµ%cåÎó,}åÙ³lˆ¶áùÉp‚q¥M´œ l8‘å§3†¢é2×^æ}È*½ÔI#AÒˆášƒ‘º¨	ñEOÄmup¹¹AÈ†‹Ñİ*„ì; tÎú'ylÚ^†N< ¶ßà<p)ÜC¯¶¢(ÒI‚‹¨b8…Š¢mv©¡É&Ì@ñ{Ëjç>»˜ê_ÇöÜ×iÔäß„©EA»ƒbRnã²b"0¬Üó”~¥*{ĞwÖ&!’lU—üíÿáXŞ–ÒıòŠ#âLfA‡švLÍømº•‹tJ$İ_”0ôç{³öõÈ<ÕR¡`š„a°¨=$ÔÎáåõÄx¿ºfı{qêB
d9šï¨Ï|˜èä@ÚÀR6xÃ\ D›ğ~×çgÂ$_ÊÈ^0ı¿1ÍW–Â•çiÆ1ëœÁ§ÊéqK±ÉÅëÌ$S6sØ+‹]lKtŒYH"'5Ò„İĞZ:~FÃU<s¼= aÑô}ú"@[½òx5ë±J!É©ë½¿÷1Ô ¹g}›èŠ²œûá¢„æ›bñà¢l;n
/(-ÁïAòMQa[OCL	Íşíñ3ŠüJB]ut/{ä]^4µÅ / $8#j¡× f¸\§ô÷<X<¹;¶Ô ø_:€+'rˆ·‘˜T=ÒÊŞG{4¤^<-)—[ßâÿ1¸j÷ÏM,p«ê¡vs©ì¼¢´/Ö/9ä*óg=ÒíäÒ‚ôó1™¯­õyFbÓÓ:åë37mîÓû¼C‡ÿ|¹j=æSM†6a¨Å¦BøÿæTùØzâ›1“lUÕÇ'~ğş¨¸YŠ‚ß 2À-¨%†£Ág3¢ë÷ˆñ­ß·]º!³N2m{KòÇ	´²à“Í^k_W@ˆ:Ş« G`
?lv2ï’ÙU©BTFºŠM?t®v´˜À`h–¤2Eb¹ÑëO7Ê/à™÷U¶A¾èÆ	ÌØşpÂ*ßÎ¨XX­B=è^$à¤o(¬m»K‡`„èz	x,ı­›‘¼Š1¾çúÏ´${}WvXæ£EE«ôÌ
Dw@”'ÉÏ©L¶”:pjl¡ã©ù²äÁœ¶)¯ K_¿>
b9ÎªìG5Ê¯/$;&3’2‹;‘åSem*gH¼™Íù­ºÅ‹+gpœ5‘ïP5cnZ2¢‰ˆ^×@oHÎ¸lCUÎ(òáúWJpÕZø:¹ë
÷>˜(ôÜ˜ñ£rÁİ¨a†ZÔ'yâš’Ürš‚bê³÷B2ôJFî]”¨2®!«¾:íæõ²ÿ¸=Š©ŸĞ:ä+w&9“•¸—êúÊû©4t/Ùkò9jZ1ò*r•İ.†¤ÜÂS-¢úfŠa¯UáIO(ê5Xìı©§ŠíAMéº%«Ê“>c@ÄõÊĞtPHÎõçÌCœA¥ÖO	F”}S9zê«†.Â(Fxò»H8Ì3YJÂ¿˜ f¦í.Å›$tÓSÃüæĞrä³qÜ]¡„Ø+FÖ¶°À¦™)Ä.š
D´OwLğ]¼‰ø^ú€?YO3³@Ã˜û]†ˆZ×C/IíÎülpÛ÷'öåù%¼0Iìõü®‡¼5ãÇj”¨&7“úµÂ}^¥·Déº ‘~ËXoB”	—TÖ˜fÒÚ Ô÷R_ç½£ÉË>ĞĞ% EËj‚ck ‚Õ8İ='v¢‰Õ)SÕgÔÛ»D4ºXw?K.øŸÉmwÓA¥ÈMÁ¥ı/MëÖ…ê9È+ÓÁÖİ´Öxû×Êê…¢cnûü ßÓOTUp ”pà*Ìq¹ çä,UO °úÅ½xx%š-dr¹wmj?l@±v2Î H’¸!rBQ/Â»)‹fßRà°;}çY²ÌˆÎáÛ‹Ğ«
ÔÑ…U~5wpœ~»H<µ@PVH:N¥è É‰?ïÉWK1O.ƒO¡ğuËÓ
ã?n,Vğ®túàF‘©fypcì)Úî$ÆÆZü7Xkÿ­§²9¤z€µh;«máÚ×ÓG•áçA©9½¹Æ0.¥äC}º‚¼â:~ÉF"¶a€4ÉFU*º³Ï9¬®Ê÷/º«8Gî…‡¼c	Uñô|û]È&õ¡û=zƒhá…Šÿ»A¾qÕÙÙ·ç$N5Ï–êŸrkæíw¢8“|\Š:™)òÚÆü“@`ñÖµã´Ê‹lé%¯£&ûF_3u¾÷³…ÚŞÅœÏhY*n!Ë`oz7{Î ®Ê{^v0lN¨Å'4"¯'ËB[:7ÀH©}qèæ‰ñ%%?IÔªò,¡IQÿDxZ¿I]¿¾åH}êÚH„>dÛ`cÖÔ0ác‘}›jÓÑ*Ö§ Í²í±‹Õî&Ş‘H*É U^a¯“.é@G¢ràV3}Ñ}İÚ]„Åû”#íŞÑ¼
‡WoâI¨za‹jûóBº²uÖù¥œµ¡È{ğæ7´1l\Á÷G+òÈ†íäÊ‚gµF¯3¶Zòô:XZtÙY½ÂÉƒ®ÆÄj£vëØÊsbf†ïÙJ+²~KGOJøVMî1¤ìH–€r|dZãğ0Áè ßÏú3$-ã Ò›M7ó„kì¾†Shºç€™ ôKÂô*H{µdrùÈÂÃ°2²¼Øõ¯N{6>€‰•ÈCR$á½–cqCL£DdoşpIã‹5VÈ²DvãúOÅİ½Úc¥á0– Éç.òömƒD™°ÂÃ¥¶Ã›¸3µŠ»àf0`UíÇ5ØëBHnúeJ/ÖNÚÍwÍp[õ‹PsïÏø@ºÿ›µqTwˆ>jÇÛu¶ë€Áö!Şùtš1¥E¼4>|°©WÙ¢Ñ¤X1Ì…Ê¯Ş54O>AÔiZæq
]Mÿ=J
Óí:ê«7f8ıçC?#ÀÀğ$ßX¦ »4X–ç¦Ê€€yš¼˜ñw‹:Él$›36UèÏŒµrĞ¤PÕ++‘¢}Âó‚ğ™ğñ‡Tş9A¦Íu:
\wzqúİ[™&û3vs<t+/é
V”şÑ²|-1IsQİÄ'äG

Â1CGø#¯êÛ7#n¡Ô@UığÈ?D€:(·ñIKrò#Ù~ıØyäÕ““fU¯É2”ßæVÄ¯Qr›]“A•ÈWOĞã(†l–»¾ú8çÍLš±îCê%(<&©ƒ¶Ø®mƒåï4Ì#EEu2Ó(’0\ñ¡g!ÍâÄşDÕRé<ŒP_4A<#‘ÉQÏ¬êÚ÷#lî¿@kˆ[½ø!I¼\û-úY‰¾›/¦Kx™÷ºÍß¾ËÍ™‘\gAÒ_Œy-ÑÀ—~fJƒì…‘1¢Ø¸ìYO¼*mÃÿLÌşë8w@—V,Ìyï6ğl>×*¤eÁ‘ê–µÔå¿qÊŞ­â‡sX_ BúËyí˜7PlF×$|a›‘·VŒD	²ü{>Ùª Âùëx5˜mĞWfÄP)†ä1°nÖ¤·ZŒAß
¢ıÃ{k•°Îõî½ö‹|›3Q¯†ø8phwıãÎB»Çä’A&{SÚ÷•Z£ı;{›ÿ¤@5mÔ}åÄ¾¤ÀVR²ç×XÜùöÁÙÖÆ5‰FáõÃíJ[yj¥è³Æ¿†4`~ÂnGgÄmÄM‹fšÃD_ñ¢‡Mà(!´Öa•_¨%×%X¾–q³Ú‹™ıéôÌZ¼Awê«ÆôE?T(fº’Ë¯w»pK\Aüyşš›oË¿7+Ü‡!èß‚[À di,ä’Ş7ù§ûç²ü>+‹Û¨N8Õá98'ıEÒ&ËŸDù/?hD æé–L½ä§êÂû^>$Ÿ6m´™q!/Qƒ%kÛ¤P5éˆbMo‡¬iªØ6â®ñ„|[YÃBéÉ¶îÎôlUØ"ÌåÈ17N_´3nÎ¼JõkF¶H«nÕ;ØËTÀ°-_ì[ÇûÙˆQëùÀC ãîIBgåY¬ÅÓ«:Çk(•e<’¶Õ”H3ÿ™Í3ÙĞáE.¦%Íš"óÕå)\GàôÃÌXœ|Ô­ •gÅiLq¾¡ÙÈËÂùŞ‡M_üzI~ıª÷³ Íÿ-¸uÆæ^Rµ8/oÍçFºğ½ÎYÌl¸6?Ò
À`SèûÇƒü`Š½îgÓ&_Ç3U(°Úì’@'ğÖÈçÆ]è_*·¶B?ñ«Hñ?Œ<'Ä™ŸÓ|çFòŠšÍvÅdDo,¸‘æÆÂ‰Ù–’n+¥_0{¹bw¡}d-ÓeÕ†Ov¼€r¿ñ<w‹Ú³ğE´{·¥»kpÂ%ÓÔüÚæã2‡¾ù!“ßà0p,o`¥ãJ>¥ˆ7¦›Ú`|‚`º>ıA·°N	zˆ²íÄºÁë\Ït´¬PEÄOn3&‚µ™˜pí®YtzZ,ÿEI6ğ«ˆç;!B®‡hNê!SĞ»K&İÏDââTz‡[iÆ'»²ø°ÅC˜Öa¹ĞJ°Ir0aªÿ¢ó½‹î]#=ÔH.<—¶e‘Ó1 zÑ (,ƒnÙ§'³QâÑÈ“Ü‰Ãe¼¥–Ã½¤¿­»Šbzš›a0¦šk ziuå"”håel 
À?|ngêî°Û©¨FÆø¯Œrt.æeoHu‡í)jÈ7.úó½Tìušjå~Àw}nõä‚—ìV“ªÊÇ/~æfP'£ÑŠä_3l›`®÷M¾b{N›L>„ÛbÎ+ÎÀ	{ º}{ú(	àŠ¯šhós’g¥døôNC!s‚ú¦‚—¸ ùqÎİ©uŠk@VMp;õò@bˆıû}ÿY¸lŸôíO–?d.'çÖ„Î¡Ê ˆ4k"ŒM*.›
ÕKßg%4¥ğC<[¬¿²â~ú˜{›ÖQÀrfoäèÏIİœ“©j³˜m&íl‡íè…$
ÀşN›|®ì‹+îCÎuØ®û·$N£ˆ‰)´•„WFÁŒ‹-üpÉ°^1§%0Õ§*äèÄFˆ_®ìtˆ~ö…CiG¢¾´‰1â™Ğ– £
SŠx}
óX{öıìƒ‰.ç›4æG¾27|ÇåƒŠÉ³»’ºheVŒİŒ³şqvUü9ˆïºC;,äS=Ìñãpq¯q¢Ê|dÓrå¼ásÌ¹]ÿGŒK0Ÿ†ä2N²ŒMë‰Ò·”E—Kv½L³±)|S_ñ–Ÿ}ï–Æ¶våj%È#.Å‡<M‚«¬LE¬™î<„\]u—<=ƒfåjã¤‚ò{d¦ŒBİË£¬ênhV¿«B¯í:
åX	€”ëêÍ[«\GA©İ=}Ûe8ˆúÆ&«bÇäÍRÿ=Hy­ô…Â‰[¦VqÙÜb¨—°:z°ŸşyÁjĞ£\äT˜R²…›úÖ“o’ wĞ=6¦®Â
ã•H¹Ş¶MjÄ`cÌ¦ÕåàŞœ³¸İ
{dL‰sñ¼İw’m¤èp2Z’ì 9%Ñ‹€ã%ÃqF5¹x<µ^º!4y¥ÈşIùÀIè­í9>rö#‹#ê“[µ(»À8•Ğ¢‘"ï	€ÎÙ
¼<Rô¶Šxœkz¶§8%qeÃS)ïÌë2÷míÁÇ›°ZªBaª ó=ÿjÊC„¶½K¤y+ Œ_­ø¢©-ˆ–è-cÜ¬‘&g€WÙuè,Ä_Ó3Jh³æõÆZ™®€·"èÒFXº38]åå	X ½ÿ	¸Ê¨oÃr'c—ƒÃÅ›©²’Íÿ"Ä›ÀgRßóÍ”I-%ËöNaÓPeÄ+u°{Ìh˜kİ÷Ä”P?à–>ÆÂÅ“Ò\ÆàÇOö õÿ?8(*¦§Â¹©Ù’zà:0gÏiÄ²UCW#iÛ­¢c:§‡„E›KOuÌVkğvèlYûÔğx|™óıõ¹¿
\févHå†{$cÑì‡dò¤6—œî'ídj“WÆ·*Î§,Bç›Æo’ÎHóQ½ÄI«NÇOû×^îğĞù‡—àñG“3¥Õ7nĞšrcÃ¢ØšQŒ]ûA»H%*d•¸ú8ÒÓ•#;áó*[ìuñß<`)Ğ&ä"²%ù¸åJ†.iÄÖ™›Û²üM¹ÍŠíŸ5/es'Ô•"\ËÕÏ^^w|*² á@Ug½bê ‚ßëãa\ ¶gç£m
zŞ:ÃCß3È«1‡lZ•Ã)ö¦şƒ¼-ÒÓŠRª$ú_¯ =R^¹ôa8¼ŠìğŒêf*ÿ;®wxe
æ¹Èâ‚Á-TJoÉË.ïdt_uÀ(goøjÅ¤Èx>ö¦TtsÆá„Op‘WF¿JÈ.¼$IãNñÌ|,‘Ê¢@öı„ÌÏMÕĞ$PƒÒy€µbçãÕ‰ıVÖ'Ø‘Q¥;Ã{Mvi“&ø˜˜jè–ò¥ºMZ¶ëªIyßù|^3vÙ"ÍtrŸ]”8Wj†—Ö³&Œ¦©ÙğÍX?ì¼ğ…K'{I\¢!¤ù,Ì
èe=<HˆğíOó­7êê‹eëNvˆm™Ô”\?åV×Ş:Äì¯/µ	¦šx¸'üÎ3X-Â¥©ƒÙúâ¾Ró-[ŠxOë»k}x®ï¥<ÛìOÛ3“U`¿bq‘]àZ†,íÔî0Ø™=é¶Ñä\sAİ¿3ÆÕZ,ÙCAù‰ïô0lò·=ÇïœŸƒ°&r_‚$î‰-ú·;«|GYÊ‚ï´2Ïş}À¶_>®h9„Øã÷‚á™°RÌ­û»{![CX	Â¾éˆvŞ·$L~£%O½Ñ#Õl{Lp—¿vÈî°tLMğ¼xê¡ß¤Ş€K'3Ï‰ŸñÁ_eÆûEbš2IV¸r6D¨F·JÎ,\%Áã(qæœ7²•å3"=—V¤)¹
›×$†Š²{³¥œà”÷!ÊU—xŒ÷4Z(Hğèúé»6ËnïTt_z€3X­İ…¡› SxÚ»#Y$«Pejî?X–7°M)öÎZP>ñ½%Çı‘ŞnÔvõ;ÑóFš0gÓ±šó`¯³ªû®Ä{jŞ(
IÅŸyf4!aŸuÁ™VlzÓ"Àp?jõ³fèCdÿı‹¶`k‘jÆĞÓôo	nÜol®°ÎI»¸rJ‚œ2Ñí¤uƒ_À2è-¶¥ÃiñÖüfùÒúå»^N,¬%÷NDîìez?ûh	ûÄ™Ì!fÛvY5ëù—W2<Æ‘•ÃÒUª2œß©S5‰aapoâ.³”é [Úœ›nmn×¤ÂtUìV§¼ş~Õ|â%ŸIãœ’m"¸¤‘`è§
ñ‰‘jÆ"bÊ¬@Å×+&§bÂ‘©”F×Jæ2Ü-¡å€sò±½ŒIÎÑÚ Î=aŒo,u†·<r¤ÒÛ…Á?QØFõ%Ğ¡Òo’á4Ş%»­óªJû|Ë‘£×è†j1–œ¢ÇaªG
·˜<ÊÇ¹¥2iù©÷Šk”™­G©U™Çêµ·¼<I ˆö+§»0wÖu’½H€:˜«‡}š™“Õõ§?¨9†ï¹bx¯°G4õH„õÖ_ˆlÜ4¯õâW]ö˜‰ç¿‰¼²OŒ5ï´4OoLwX¥ñÌÆŞ½[iu;vä·-ú¬{Û{#[aÃPiPë?¹ªÉ9hÇò]—Øİ½¡‰€^Ø b¸Š´_@_]{é­®‰°ËaE\÷x~š˜S…õ›?hpµçg–,¼3şìI9†¡À£§î£•¤ë2’º•(lN1rF²/ª_ÿAÓ
Jzà¿—ÉœnÑÔdgSR…Å›+g<œÖqÙbXS²!:TTÆ!ÉĞ¹ö·>Î¨lF•Ê×&¤"Ãa©ĞFä
ój`îãÁÌ§¶Ç­‘í0Ë¢ÿkmÜŸ@5?\ô­4Z¯C	û~ûX{B›I“N†˜(}Ò¸¥Æ`Q¸ ôïvÛd˜t©À+('f¢’Á•¨WÏüÚ˜w`1şstõq @1È,n¥ÔC'IâñŞ.˜HëQ·DN‹L_MÀ¨>öüÖ•šd¢š2­í…µ›|5Ùïk²!·E@à<Bi¯C¿•ºë±\q>†¨[oó“~q*5(„ÛÕN•v<#ŒÂ¶éöÜ~áØpbœ‘ô~GX
‚¿ˆ2Ş­ E€VÁIÃãÛ˜b‹å¶3d"¯ÛïvÜšc!íZ·BåJ¦”ø¼döŒ~İØa¢A”W~†˜Z›Å%ğ•{¥°î>]‘q¬¨m†@Ñé$iãVñÆüjù×:æ«2Çmª•‡XäöO†Öm¹ÕŠç2°-Œ%ã±ôfMØ¢½‰˜^Ò€e˜¶™ÊlO(r¿ï>€«mÂ&W\x¹j·Ù8äÃÇS¾öeLºôû¥NÜaıĞy¤Ãs)İæá²¹¼dÿ”Ê¼Â;€Rh=bƒÑÔÇGË»q5i±9-f™ycbæ—7İo—’}"¤çDüÿù8ŞõLlõ+ŒÔlŒŒÖÂæé²öÍ¾íˆuŸP4/{dH?EÀËHÙ	UY5k'NıU‚ï½
3~O&cÃİ•
&‡

P^%>ÛE íK‚²5p?\(æ¸rÊ¯„4[oCT	,«Û{ÉıßQ*}£Øº€êV°711j³WÆ½ªÉ‡.Ú¤cQùÄzë[q<‰š^®rÚ\ĞöÕDC“uıÑÈ^Ÿ¼ª+ü8yêš÷>µèO6Œ.İäa³PMÄ«}­Yš‚Ó¥òÃ=©é†öÚşã8qêœwŞ´7@A=µ&ïV%§¦L(gIè÷¿éôŒ„ñctßt`P0,;eëS7Eî‹4_o@7~ıÌ‹XŸsG5n¤Y¬8¾«®ür[hV¹ÆÊêï74.¯dDKuÏ_, %øj|¡¸T8(š°S/ıû9»jËW/F¤
Ã)Ø&â¢ñ¼XIÂéœv“Œ¡!8z7Ä1«lGUÊ‡/¤3mùÕºç2¿mˆİåUàI*3ˆLÿ³‹şîyÒ2‰İkWò½Õ-XF×âŠÁ“¯D&™: Ğo3Ê™Ü‚q¦£qS¿ë>^—Wyƒö%„r‰+°ÂÈL?–êşİÍöÛ„àt
ºî™B|:&óœÃmî,Q´S9c3ëHXœQ‘ÄTkGWJ†Ü3!íàu°0=ì)µæÏ2ì-µå3-ñå¼s	İşá¸pJœü4y»µPzuè_•ûŸæ*óÁã–DäŸ¿,ã”IàM,¹¹ {û½ş‰rØJ'óÕæÖóÆ‹Ô¡³F09½¸³¶zãü*ÛÎßS¢f}eô–$µ_¸<yÆõó?=è)¶¦ÎÂìiµÖÏ&ì"õá¿0H,¥üC9Éêî÷4~¯XD‹yŸZĞ$9ãjñ×<f©Ò«ã§N|¶ÛşGg¦}W&8˜h¢2v”Ç‘µ”OL6îİ´aP\ûx{Z›CcõÎÿ,x%Ú£#áøpzœót}ßY ‰¨Xƒæn§ém×ô˜Ì¡œ«ˆÌA­ÈE®‹_{@H3N­ÌE­Ë¯{{s[†©ÕF«é¼mNO`ó÷ÆöÍß2A]ínäŠH¸2üÁ?7h.–¤VÃFéÊöï>ô(f˜Òµ¥9ñ¸¹#9Ãª§dyéo`¦cù/‰/ãNÇ»Hˆ§$—å‰³Íğm¼‰÷ş°xLó½ñ‰¼^ÉÀn­w>öÀÒ-qƒãh€ö‰é’· Y(ğO¾ÕMÅ„f³Çÿ$¶‚Ìzç3ŠSî=€FZÓ†Lõõµ×·Ø¿šü[÷bü=ş
HV_¸©Â¾æ‘htl'^l!×D%tRg/Ğ}apXd„%cn_uÂ«rpbg8—DÚd2GŞy‘,znH’‘•”WF¶ŠÎß,`%Ğ#$!ã`qĞd1Óle‚šsmâæRÉ­
{¡ÆjÜc¸m¤*¨ºM”—}–™–ÒÖå¦óıù¹ºÊË//d$cuÑß$`#BŒa9ne4eĞo‰0m‘Ì.H&œÉ€ÍDIaød†J\ô8j˜¶µÏl1Õìg5Ò¯%„#aóP}Ä\È:†¤óãKıÓÉ¨ÆñĞÙŸJt±!CÍíLM¹nñ¼Ø÷Ø„Fe7Ü¢İ*à„Ÿzq%o%…],<ëf<Å%MeÒ“%•ã1ö¬~ÅØk"—a–VÔçz·×nÖs¿Ö×&æ¢òÁ½¨I†ÚÜc!Ñàdp\5Áï(t&Ú˜Pö:(™[é9*ÜÇµĞİMUè¨Œök…0g4Q£:~Úzuù–Ê"6qâœq‘ÜTaÇPj„v³^ÍÀm¨†·_­ûmëæî¼ŞÿTÿ@¿ë@ìZïıç—“šé8‡R­U8èK—±%R£ØößÒfú’û»w^¿@H¾¼HIÎì\uÁ¼}2Eßwšu§k_L÷v–:hÑ×‚¸ç¿l§ôÎÃ‡Øb•A*g3„(ae68™×ş`gP„5›oT5Ço*”'b¶‘Ô\gœÁ1×Ò\'±F{zµ`ò6‰eÓeò“=•é—6Ö®æÄrë]·ÈˆÀƒXv†£¼ÊÖï&ô"ÿa¸J´|<éòöı¾ùˆ9‘Îni‘hp+~gœĞmİRÿ\g)vä3•³©8ÅS§y)+^ĞÙ{Cúwˆí¯¶"eV®Ihˆ	¾ĞHd“|UÙÇ"ê¡· N¸J½ÏJş{„¼.SÙ*ƒÆ'™£õç—^æuÄºĞ#€¥ä[³í¶’ta½Â,A_³6ÑTPt×|ÏfÓ!wƒğo•ë(6ãÑÃˆ•¤‘úuãz ]~?$nÚ±ò›©ıİÃ8i¸EF®ÛBw™DwÉÅ	Œs§xmZŠƒğ2ü-¹åŠó=ğ)¼&Éâîñ´|OYÌíùµºÏ,?eè6µîÏ4l/Uä3z­Û£/Cš+&V‘€[<¹ê¹	®;K®3³@ÌÄÉ;ÌÄÊCœúà†ÃK{µg¸?­³ÿ±0®S¸²çˆ©}:.’}9FµÊÏ/,$%ãc1ÑìduÓ_%À#(!æ ;†ÚtÇè?‹‡~{¦(±×ç¿¹—
Ö¿&È"î¡´@OH½üI¹ÎÊìo5Ô/'6gÇaˆĞGNâ(ÏŒo%+ÄÜ‘=âWÑ¼ö’8p…&kÔ¬€y®vBÉ˜nÒ”e—S…öÛ>ãhqÖœfÑÒäe³S—¸ÿ9šjÒweä¦¥0¬M$óĞÕ	ÕAÖDÛâÙdäs}İÙ¡¢ÀA¨F¾ŠÈ_.€$X#B¡É€nØQÿÜŠ§	=˜¼¡Î¤-–fwç¬‡*Îøw´¿º:Å%Š¡¼J¡wşo€ 7â÷ô×w^Š¸çôƒ‡-’k4Ã0ÊXO84F-“ üñ¿Ÿüpd2]Ì	ºú@Jí
\w9Ù©÷‰³ĞlKÕĞg$£uß`2-”%—c‘öÔ~çXr‚™‘’ÔU§GŠ¹Ÿ
Ğ?$(#f¡ÒÇñCC²àÈ^bo0µ|Æ¨œhšEÔ7'n¢”A—HV†ÜZáÃ0iìõöÿ>ø(zãøJ’+«¨§p} ´¤|¬HíùÏŸx’$«rdÁ÷‚È-R|ƒFÙÊâï1´,OeÌ-õå¿3-ş¥¸C
‰ÿ½S2íIn&óX‘“¼b³ôv—úh…Ç¸¶îdBç¼J‰‹»Î 'sã]/ÔÂa¶NÔg}Ò™¥’Ã©÷şºøK:kY["³†TÑØdb“Q•ÄW+F§JÂ)œ&Ñâäq³\MÁÍ¨(åİÛ…qò¤‚d¢i ˆf{(‰Pò$XŒøíÎZĞ['ıµÇ°î%|…ºëÿî~ëXwB‰^Ô gxšµ“ü79îª±$wúEéhª²m»!~˜EUÈ|Ôò¬n¤ªçÍë-·e“UñÇ<j©×æºòË=¯i„u$€¤(hË²¥‚ç£ÙÊñÎBÈQïDt_@2¾­ˆEÎ\15x0¬3íû5»oT?Gh
–¿‹d«ï ZıGÊ»®­,)ÕQP?,Œ™ 'UJë©ãad]Á$@™3EÖìÜAÒ[*…Ø(°Å"İH^±É'\}¦È˜šáÏT=¦Ê„şço®Ùÿn‚±È§UÓ[Æÿmğië`Í²–€ì}ä[Ía˜á¡Ÿ€O2½í‰µÏl4ïw4¯pDqÿ\xÚ¸c
‘ÿx7Z®ƒYûBûI»'½%;†Ló4Í×•’€äãpü¸ÎŸ‘uy!igˆ!Ï2AÙoy.&^†óÈRgh—u!h%½mv5¡Q:Æ[4qU[¸£u?åª£Îøµ<P)Ä&ëb÷Q¾„H[NƒLYÍÂíƒµ†Ïì35íï5´/d<iõÖÿo¶k®èúL9=N¼	Ÿ¿¶«>›kWuÆŸ*Ğ'$"£aĞXd“S•Ú×#&¡âÀq¨F±ÊÌo-Ô%§*D‘‹Ñ;“>hÇ7‹ì§©bMÎ¬]…Á›(Sf…ÒÛ%£cÑødz“[G†#)Ã¦¥!¸Hî0¯(»Áp’ #ÁÇĞÏ’@õíÄêP8bFUö‡>Ú¨c‘úÔ{'[bƒQ™ÄRëE·KÛ|A†·¼óÉëœ˜0ó’N&½w{áªe9zÎRóE½Ë	¯~Äkr—]––ØVâ†ñšüZ«¹9e/ùğ
HßˆzûN8­_÷)<¬±Íô`¼±<¾§Æã(R¬m=+˜Ÿ&¿àu]—9– >xÖk£S©·¥zã!‰ŒÜ¤’‹mRw±ş¶ÀEfªcWî÷Ìï.1M¤u„\äp‹QQåë³(Mæ²İ¡€Q˜R»E‹KOp=ñé¼vÉŞîàtp\0ì8uêŸ0dwäaHyKtƒ°8íÆD[½íB&}ü¹òÊı¯9„*Ûg#R¡Å€kr¶Øí™İ6_¡ 6Ÿ}ê[f+evêöS€û	â–[ wœÇ—5–¯Ä6ën÷T~‡XZ‚ƒ™òÒı¥¹Æi‘¾pöSŞóO_vlOıûC²¸é4ˆ>}4=Eß?ÕÖ'2bªÑé1GçˆÛg“jhÉPqÄkq×\fÒØe¢“•øW:ÃçI‚i ç²´MMœ‘ı”y—ZÖƒ&Ùââñ±ù/Œœãû2Ã’N.v8h“pğfn$¸ƒ/¶^~6#‰İÆâT&ù]Ë£¹I,mÕ!~&‡bÚ‘£A÷H~˜\RÅ˜k½u–ŸĞ6ä.ód}ÓY¥ÂÃ)©æÆ·‰µök€é‰B“ã#E3*jÇámşŠ¦ z&/}ä³rÍİ­¡…€[r¹İŠáüeOKpµ7;ZöD=7ÛIU·÷6`°5ñï<t)ßfà½zîj	§g°$8…™ê—„±©çNŒ´íò{‹ Q0N8ÇªC~9à´ÄPkDKv^Ü a½\)ñ%s|Ùñ¢üA¹ÈJî4\/käs~ØQ¢„A›HSN…ÌXA†6úÓE¼¹¿~në%òš†¸´?`¦&¹ì»Áñ<ÄÎB•y¯Äğt|Yğü9¹êÊ÷/>¤afà¤·±å!AI±~ô¬UŠdZ7ıx‘„ên©;§ç>YúÅ+–H7ïÇç±'Àî÷º
ÿ>=LØíMÔ¬™6!ß‹¹U÷G>Š¨_€:Ø+"§a‚Y”Q˜5¦‡Âº_Ì²†`¨¹ÿºÀğYy›şmB”¯I:;57 …£‘D»*jYdñâ×ó‘€¸ŞÕ g ¸5Š¯0;l+UçG2ÌÿŞFœ;Cc8+’UÕF÷úÏI/Uåõí¿5ˆ/¤0Cl	Õşç8rª‡WÕæSAEµE9­+¶P¾â@“t=Ñ˜^£¼»Õ'¬=…é›6ÓnåÔs']â±˜LRÅ«­tZŸC	ô>ÿhxš¶Óåüs9İêá·gå@ ı…vûjtc7õP±Ô&È—ûµÚªtëó¼bÉÑ®äDsK]ÏA¬Eş‹8_j€6²®Í„>ÏÃGÊòLFånM™¾è³7«U±+Š¸_
€?(2¦­‚Å™«ÇuªŸ:´bIg/FÖ¥ˆÿ¸7 ®¿H;N«LGMÊ¯„1›lSUÅÇ+*§g’ûÇÏ–Tš"Ì!­àE°?}è¶²ÎÍ¬m…Õ›'!ç”ÎpF¥"/ÒW‡2ØWãAÙlŞ¨ÓßIosî©ÖÔƒ£‡Vá¡
ôL¬.ljÀÅK…ù2ÅÒª ø2VQüUë±¿ü77¦>òÑ˜5ÅÙÀOdv¶Ï\š/ «ß"±§ò|µ©ØpØ~™•(r‰]Á˜hR–…–ÛãvñŞü`yĞä33míÕµ§¼9‰êŞ÷ ~ @2ˆ-¥C	÷~ş˜xRÎÇÒHPÿwx½ááÎM­k[év¨ñ'°gê¯§¹mëô‰­ÌÆHe¬òy
·ş\ÔáHoŠ'ìÈ¿(²z<“Ã¢Õ²”ŸôìÈXë™Tî0Hap\<éøvúû{t_s@È1®¬DEËK/Od}õÙ¿"È!® D@H?N¨F½ÊÉ¯.Äm%*‡Èg[è„‰;aUjÅ'Õ¥~EÇK*g±õŒØ1¢¬A…È[.ƒd•B—Œòj¨ª)æÌ‰^ï«­Z½Ã	©şÆøjú—;«vÇ^ê€w²°MŒÏ¸Å¹‰J’,nÍpÓ¶æöH¦øûŞË²Y!b…~!h–-qÙêqã\qÁÜhaÖfÔçu²Ÿ=”)—fÖ’æÕà¢Y² ÎØÊ¢Õ41] ˜ŞaSaPb; ÜB" µu07l.•äW3F­ÊÅ¯+'{b›Q“DUËLå].x££p°üÆĞ+1$V//æıwV¬Æ_‚=ô
õ—‡è«ós¿R•½—~&IZº‹Å¾é¤1 Ø  ^:Ù.K,wjÙt–¿lpR‘Ç0)S½œËHª'O‹0à]HÀj…Œì"È¹€Æ7KÏ±ÿAN¦GÑL{MÛM£MÍ˜m’••—¶¶ÎÎìluÕß' gÃiÁrVRfómÁxŒ)r÷õ‰Å;CĞ·Úß€¼|ãoE(Ò z  3x-Ú¥£ùøzú›;ku×_&€"ØdÁè Ò*ZÑüÖŒŠŒ÷*„‚à1’I„­G!`äÃi½u²÷© ¼9/4šü½…"*™ÂiF÷ëÀÄ›PÕo)_±ª;+r§]‚™˜RÒ…¥›yõÚÿ#8!¯ì$E’0J¬ü;9ëj÷W>†¨ZÆƒ*Ùç"ò¡½€I˜K±ô$ÛİI¢¶>i¬©ó¿­‰¨šfö=D™})>šğPÂÓWš÷ñ(´€,hÑ¢£øXz‚›“rÕİ§!‚ Y€Ø9¢ï¢Ïi¨ÀW‹šû¹ş(@{¿Mà©<=O7òcœ°İ°Ê=—F%œ‚/ªW6‰©r@ˆ9ªĞG$
£Ø8bª‘‡Z·Cê©š/¦O6¸sÍ‘ïĞ‰^ßæ¾Lı“Ötê£œ°iûÆF«Ú9ÙÅ!MKú²‹iŸVĞä:ók=×i¦–ÂÖé¦öÂşé¸?„×»Y5xm*1P*qˆİ8šnJP?D(f¿RÈ®»K{O[L¿Íü¿ÊvŸq.on”WwFŠĞ_$ #x!Ú c ø4zìQM/·°1Ôì'»€wa
cÁ«Üã™W¬üDßîVUJ»äºË|ÿä—Rw»íxD™-9R—Š:Yôÿy¸Ê³/ä=³iÖİ¦á‚ğY¼A›¼ï®e2Ç†Û›E;'[—53TEc÷l —f)él_G¥âyJÍô
EË8¼	 ßò\ÓwŒ!¢áÄÏY ş‚©ËğÁ¦£'Pdú-Ç#SDT\1{àp
¹®˜²|~'S3“ÇiíoE£};;f·SšÜS!Åàk0l6•î×4f¯RÄ«{[zƒ[Ãréİ¶áğ\|Ùøbú‘»KwO^Œ ]øîú
YÊs[~§â)úµÚq‡m¥‚eMş´™8×•Ç¶ıHÆ½û[ÁŸu7Ô‡fç!`ÃìŞØåyP¦3;´‡E”v˜Ò°eŒõñ¿<H)Î¦ì³ÉÍk‰`í•	$ÍÒ|±ÆÌjí×5¦¯Ä9«jÇW*†§Â³)æİ²áßõ	Œ½2òÅ4
P˜ÿèä ÊJª1]L$¢Y1t—¸jüû¿$H#N¡Ì@mÈ®·N»LKMÏM¬…ı›9“8ƒ';¢å„ÕÛçÄÊp‘oçe'!]‘6¶m'o·ÒÑ¥¤CIùÎúì{5Ûo#T!Ç`j6·nÎÑ”‰x›ğGCõ¸*O*èfã‘á™xŸÖ˜ß³8ª¤‰¢Übë9”Í/‹ğ9S"ıá³Xõ<¨<ˆ\Æ–Êîƒ¶€‹±×ti˜µfï(L-D;o(«ÿúè¾_@xC±ô‚Şö`aĞd4ouÔ'p"œ!‘àTp\:ëwrQ”W{F›JÓO%Ì#-áå°txD­´¾¦M¬j¹v4­tÇqaÖ£&Áâèq¶œNÑÌdmÓU¥Ç*¹ç
ò¿=ˆ)ÛÅ˜¶ÁŒ,ğÁÇMºÃ®Ò¬Á;ÖºEWoì"AwW^†€ZØ"¹áŠğ_< )ø&ú¢û»xKZA°¬ò
‰Î¬C?¥¹+=Ljås#‚a½zÿ/ÍÜ-åê×MÖ‡®şô–3ğ«#aú{ws^ÀQ¨F»JËO/LaA°8«óŒbİÑ¡¤@CH	Î¾ìHuÎŸ,P%Ä#+açPr„Xø9Ò[–€n'ó™GüåŸ–ªDñgœ7¾Tø±kDOH²ÙóÌ³»Å-ÈZnË{/[dSyÅÚë#7aîtTGp
œzr u$¡‘R!TóƒÄü!¶„ô°4_>˜?­÷¾»K~X\ù˜zÒ›%“cÑ÷G+ñ;—Æ=ÍV§I¦4©¤Uâ9•ı(f¦’ÂÕ©§Âºé‹6ßn¥X#rFäXsBÉ‘®ÔDgKREœÿ7*ZäFiw¹¿«ötî\)™Ö'P‡r<¡Ô5òQÊÔTİóC/¬ÿ†¯!ãÚÅĞ¸G£u¾ìš}À°W3(…”÷ë&éØìDPZÂ}%°Zé’¡£º£p¦˜@ÃæÚ}<`o®*¸`óuìHCôkDZ1æığ‡ïá‡š¯5ûo;T+GgJ’œ7î´tO_L ø=º©‹ßzà03l-Õå§3­ùìÌ²_f- ŒY-ú&^íz9İ²ĞìšF ;Ø 0ÂŞ™I ²1ÏşS„²öH¥-?Ò”V›È¬ÎºRq‡¬şrÕg í 
²K©xƒŞÆàjğ<6©îÆôjÿW8ªºÇ!*¿g¾µˆOŒ0]ìµøO:ŒbS®%ûİãˆÕ)—H–áW–å¦$ñü|yÙÚâã1±ìLuÍß- %€#QgòÒ8Á]ı|–ø÷ÄÍX\éXıİ¹¡ŠÀ_( &¸"Ê¡¯ D8j¿WìÿœK3!?[ §Æ(iŞi­ Ù[:&ÑpÒ0ÅÉ”‹¡$§_4ì©ªÆÇ*ê§7®¹„JÛO#L!Íàm°ŒeXº±©L˜~è­à÷ß_>k›fFàµÁx
YV¸ÓŒzİÛ!£`AĞd>“hUÖ‡&Ú¢ã±ø	ÅšO­#À‹< –ÑgÄCƒ~½™œ‘0á™r‹˜öš†ŞGŠ„‘ºÖèl-T„3t¯S0}ì]M?¼}œ×0d T›³3wU²ÔşN°tCªFç0J§£å°Ì=UƒÅÀ®AÌpjßèN¹ëVwYŞ‚àY°Ì9­êÅ·+§|B™É’îÕ´gR¼‰ûûp{\AóH}Î™«&œ•î,`Üß@Á6[ò'©&@=È)®¦ÄBëI·NÎŒl]ÕÁ§(B¦‰‚›ºè#’ÚPû–[%,rêÇ’Ñı Ç†û¹g.8ŞIyHÎ»,KeÏS,åû3;mëU·GŠ¼_L£v©zxÔú‘„&ô“#½Ö³ƒ6±JrqÌ¿ñ¬ÖóR;¾¿ÈOnâ"6XÉkWç~O†
Åÿ+8'j¢—–¸VÊ†ïô3?(¤Fó­$Î¼lIÕÎç,r¥İƒ!™àRğ¼;	ë~÷ÊÙœÕ’ßêGÌğñÊE‰n¤†u6?KÇµyHıò¡¾~Ÿ&o¶#ÆIÊz6ññ¼|IÙÎâìqµÜO!Ì màÓb^Mò±çNÆÑmÄ£ìó^Pò-Ä•“‰!àXpœ9‘êÔw'^¢€A˜RûæÀL3a¸ºü?Ì0óËº]à¬‚l ¥Øİ<ş¶øNúŒ{Ø>íÁ&*ÃÆ™£ òß= )€&Øg®òôšfXÂ½©‰†ŞÚàc0a;ïg b9jC£aDËø"ãÓQ\w=M™©©÷¾O¿o+â‚Ú–œ§¸ğ!Œ¥weŞ“ Uà0:¬+L¡{QÔ8İ•ÙoÕïO².Ì‚³§¸¥PÏxÇ«°¥1lMtóìÄßÍš‚Ş9TÆu(i[¹¢kÿä‹4 ¤_@9È*î§4B¯I„Û/,Ñßä
üƒ’âï–Ï~H¦tCù—„ãE^*ÖBŞşpÅ3JñN}¿ó¿ ¤¾ÜHaÎlTÇw*§Bò[Î=Ğ6ºß1ÑŠr›Ü¨œÍ »‚…¤„Å„kWsFÊÑ¯$D#KaåPlûw;^«@GH
¿~œ¬"Eœ…'}#êVÆ|‘è^øq€mdï˜×¦½‚É™®ÒÄe«SEú‹;kZ\6îØtbŸQT;GkJ—OÛ~”¢¤´> D°8è”¸G`%êZ~ y…-¨ù*qøz±Ûc}ÑÙ¤bÃQ©ÄFëJ÷O>Œ{	©Ñ²ÅMçîÉÜÊ_áĞËITáÇ<%éã6ñîütyßZà09ì*õçvt¨~ÒêÊÙ)õæÕ2ø-º¥‹yğü39íêõ·?¨<F©ˆ”ªk¿b¨†´ZÏC,	åşó8}ê™·Îöş
D˜~H¥!âOË¿I–&º’>£Íº…/§Y÷–Úæ}‰¾d|qË¹‡°¡Û;D‘ÿgëq£Or^~.®»BŠÌàœÌk|E/å×½Ù¬3C“÷iøo§M8o˜N÷ìÇ›Ô!ŞÅç’×D1ıV›=ŞÚ;<+içVò†ıšù“:Õë'7b®‘„T[GCJ‰Ïì0uì5ğ/<$)ãfñÒüe¹Ó
åÿ3lo«öòüŸ¸4«naŠ.júxÚßİQ™³‚p¶ı/Ç×Ù—¡pëë
=ù¾?´Ÿ"Q-`’Å(„GºtøìKÈ<?;’¢›ãÊ¸®/ê®%gßåMDrºÑ[Û<İScµu82ªK§0ü–»æo…íBYVÆÑªäG3J­Ï¬;ë{7[nÊYµ«ÍÒPŠå>[²7”¥ˆC‰ğ^ü yøú³;ë}·Y‚ÜYó‡”iµƒÕ¢¥")âw‡¤Æµ)P\–7ºîÎ ÔQÂ©©†ÆÚêã71î¬tEßK `<)ô&­'¬§´JII˜¼½èèˆÅmš !G=–jmSb…Ñ›$ScEÑË$ocTÇtjŸW´¬#mEk¤Òi±©3wœş€Ğo@UİÀµqÖY
Ä2(Œ“ïú’ù¶ğ&DÜúY-üõ7.·öCÏñ˜tœ>ÓD"(ÕÆ’½PóíõÍ°*o“t/goœ5“KV0w”tÕ†"s)¥áÀÏYT‰İœUÊ0×#_í/T…9(Ù×ÔH¬İ>¹èJö>Ü(aærÔ§q‚œY‘ÂÔ,ÄƒÔçè’€j¤º'8Í»…¼!,WÃ¸xéÒS ù!<?ièö¶şÎølz•Û#v¡ŞÀ`hñU‡/¾“jÏxVv×öÑÄÁ ğ†ËÚ3ÇLxZü B¨­8¿k®É:[5,) q¥«“º:ª
9LÙüá_›÷.53£‹‡ Z¸
¹ÿ
ø?:¨+§zÂ›)Ö*†—ı²£ı˜y’šÕ“'â·1¬\EÁË(o#÷Z–'¨ÈE–tñ$†?l‘ó±Ç\ü¡œïë„Á \®Å;ZIU!™Ğ¦=6»nËToGT
‡˜3­õ…¿x]aâö‹
‚xyÌrIc´éªHòĞ’E÷ÙOûã†»Ñu¬†\ñvÁ2n²”M—M––İ–á–ğVüùúú¾Xs*9YÔéƒœoe!ë=pehp²"7`ˆN`¹%=oU¶ 9—›w²`şc	RX®5¹¦&İâá±°LLÍı­¹…ŠÛVepga"àp$qäsqİÜa¡Ğ@d~µØO"ŒbÒµä{ z¿MªMÇÃÈU×“Õ+]åÎ›ˆídtµ1-²Jlƒi2gU¥W¾iéwÈ­]´‚)2ĞûÈı±¹ŒJİÏ!¬ Eà0?l(æ·qœèíÀ®Uk&6\2à¬mš¥fµw4vâ‚„ójæğÈHØÉ¥•äí‡F	éW	ùh¾8~gFÓšÎĞ"µ³ù#	oñ©ú8Å–­ï %·U4e”_må„!mN¦½Ü'Œœ!Öƒ#N—ö´ÂŒé‘¶ÔNçLrİ¡‘€TXBº‰‹ßp`1ô,eØ"µá0\,åøs:ë·tİHÈ=è&Òù[¢§0}»œ÷¦Óƒé=¼…fº3õ^1 )¢\ıvÔü¾°‰iXEèˆÁ³ÖmiXñncKQÏDlUÿG8
ª¿:¾«8ŠêSÄPÖkGötÍ,\Îçm²•—–±–ÌVíÆõªÿ8:ª«(ÿÏ0»Wcâ/Ûg­T¾}oÎ²I÷ÜÈÍÈ“ÔåÓBÓ¥#!ñà|pÜ2áí°uŒğ1¼,IåÎ¡i)åÄ³eˆµŞõéEYª#ùR	ô«M8|İ»âbË„é„vÛ^ã@qÈn±ÔLgMÒ¥ƒ™ôœùYí>_|æéCÖØÎÕÈ&û¡u¶:—®L` ÓÙ:Š±¼F¡r>l!ûâ¢4ègN’†½"7–à^>¡êì0ÖXFø2–/O¡eÈk!ƒàyÊ¢äŞ‘ã«@¿"JøÊSg=ÕªX6z£• U´\ø~±}¢nÖ5Xœñ Šî§ñ¼Q‰Ä^ë@wH°\LÍømº•‹Zø_>RDstart.put(eChar.curCycle)
                        eChar.RDstop.put(eChar.curCycle + count_Last-1)
                    else:
                        eChar.wgfmu.executeMeasurement(GetData=False)
                    CurCount += count_Last
                    eChar.curCycle += count_Last

            else:
                createEndurancePulse(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
                                            Count, read=ReadEndurance, tread=10e-6, Vread=-0.2, initialRead=initialRead)

                initialRead = False

                if ReadEndurance:
                    ret = eChar.wgfmu.executeMeasurement()
                    ret = getSepEnduranceData(ret)
                    eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 'Type':'Endurance'})
                    eChar.RDstart.put(eChar.curCycle)
                    eChar.RDstop.put(eChar.curCycle + Count-1)
                else:
                    eChar.wgfmu.executeMeasurement(GetData=False)
                CurCount += Count
                eChar.curCycle += Count

        if initialRead:
            CurCount+=1
            eChar.writeHeader("Endurance", eChar.wgfmu.getHeader())
            initialRead = False

    if IVIteration > 0:
        addHeader= []
        addHeader.append('Measurement,Type.Primary,Endurance')
        addHeader.append('Measurement,Type.Secondary,PulseIV')
        addHeader.append('Measurement,Endurance.StartPoint,%d' %(eChar.curCycle))
        addHeader.append('Measurement,Endurance.EndPoint,%d' %(eChar.curCycle+IVcount))
        eChar.writeHeader("Additional", addHeader)
        
        if not stop:
            eChar.RDstart.put(eChar.curCycle)
            eChar.RDstop.put(eChar.curCycle + IVcount-1)
            ret = eChar.executeSubMeasurement("ReRAM", "PulseIV", PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, 
                                tbase, MeasPoints=MeasPoints, count=IVcount, read=True, initialRead=initialRead, tread=tread, Vread=Vread, 
                                SMUs=SMUs, Vdc=Vdc, DCcompl=DCcompl,WriteHeader=False, Primary=False)
            eChar.rawData.put(ret)
            CurCount += IVcount

    eChar.finished.put(True)

    for thr in eChar.threads:
        while thr.is_alive():
            thr.join()
            if eChar.checkStop():
                break

    eChar.LogData.put("Endurance: Finished Measurement.")

    while True:
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
        
        
        if eChar.checkStop():
            break

    if WriteHeader:
        eChar.extendHeader('Combined',eChar.getHeader("Endurance"))

    return True 


def AnalogEndurance(eChar, PulseChn, GroundChn, SMUs, Vg, NumLevels, Vgstep, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
                        Count, tread=10e-6, Vread=-0.2, ReadEndurance=True, 
                        Vdc=None, DCcompl=None, WriteHeader=True, DoYield=True):
    
    """
    Standard measurement for Endurance measurements, this part relies on 
    please set the appropriate Channel properties beforehand via 'setChannelParameter()'
    GroundChn: Ground channel number
    PulseChn:  Pulse channel number
    Vset:      Set Voltage
    Vreset:    Reset Voltage
    delay:     delay before measurement starts
    triseS:    Set rise time
    tfallS:    Set fall time
    twidthS:   Set pulse width
    triseR:    Reset rise time
    tfallR:    Reset fall time
    twidthR:   Reset pulse width
    tbase:     base time
    MeasPoints:Number of Measurement points during Set and Reset
    Count:     Number of repetitions (maximum of 100)
    read:      Read enable, True for enalbed, False for disabled
    tread:     Read pulse time, (read pulse rise and fall time are 10% of tread), minimum tread is 1us. 
    Vread:     Read voltage
    SMUs:      Array of SMU's
    Vdc:       Array of DC voltages
    DCcompl:   Array of DC comliances
    """

    eChar.updateTime()
    CurCount = 1
    initialRead = True
    #DCcompl = 0.01

    TotCount = Count*NumLevels

    VgLevels = []
    #print(Vg)
    #print(Vgfloat)
    for i in range(NumLevels):
        j = Vg + i*Vgstep
        VgLevels.append(j)
    print("Vg all: ", VgLevels)

    eChar.startThread(target = saveDataEndurance, args=(eChar, WriteHeader,DoYield, eChar.getMaxRowsPerFile(), eChar.getMaxDataPerPlot()))
    

    stop =  False
    #Run repetitions until number of ran cycles reaches programmed count
    
    lvlaa = 0
    Analevel = 0

    VorI = []
    IVal = []

    VorI.append(True)
    IVal.append(0)
    

    while CurCount < TotCount:

        
        if eChar.checkStop():
            eChar.finished.put(True)
            break
        
        print("VG: ", VgLevels[lvlaa])
        VgAna = []
        VgAna.append(VgLevels[lvlaa])
        #print("1: ", SMUs)
        #print("2: ", VorI)
        #print("3: ", VgLevels[lvlaa])
        #print("4: ", IVal)
        #print("5: ", DCcompl)
        eChar.B1500A.setRemoteExecute()
        eChar.B1500A.SpotMeasurement(SMUs,VorI,VgAna,IVal,IComp=DCcompl)
        eChar.B1500A.remoteExecute()
        eChar.B1500A.setDirectExecute()

        #only endurance
        #Run as many 2e6 cycles as you need to get to IVIteration
        if Count > eChar.getMaxNumSingleEnduranceRun() and ReadEndurance:
            sol = Count/eChar.getMaxNumSingleEnduranceRun()
            frac, whole = ma.modf(sol)
            
            for n in range(int(whole)):
                
                
                if eChar.checkStop():
                    break

                createEndurancePulse(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, 
                                                tbase, eChar.getMaxNumSingleEnduranceRun(), read=ReadEndurance, tread=10e-6, Vread=-0.2, initialRead=initialRead)

                if ReadEndurance:
                    ret = eChar.wgfmu.executeMeasurement()
                    ret = getSepEnduranceData(ret)
                    eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 'Type':'Endurance'})
                    eChar.RDstart.put(eChar.curCycle)
                    eChar.RDstop.put(eChar.curCycle + eChar.getMaxNumSingleEnduranceRun()-1)
                else:
                    eChar.wgfmu.executeMeasurement(GetData=False)
                CurCount += eChar.getMaxNumSingleEnduranceRun()
                eChar.curCycle += eChar.getMaxNumSingleEnduranceRun()

            if frac > 0:
                count_Last = int(frac*eChar.getMaxNumSingleEnduranceRun())
                createEndurancePulse(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, 
                                                tbase, count_Last, read=ReadEndurance, tread=10e-6, Vread=-0.2)

                if ReadEndurance:
                    ret = eChar.wgfmu.executeMeasurement()
                    ret = getSepEnduranceData(ret)
                    eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 'Type':'Endurance'})
                    eChar.RDstart.put(eChar.curCycle)
                    eChar.RDstop.put(eChar.curCycle + count_Last-1)
                else:
                    eChar.wgfmu.executeMeasurement(GetData=False)
                CurCount += count_Last
                eChar.curCycle += count_Last

        else:

            createEndurancePulse(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
                                        Count, read=ReadEndurance, tread=10e-6, Vread=-0.2, initialRead=initialRead)

            initialRead = False

            if ReadEndurance:
                ret = eChar.wgfmu.executeMeasurement()
                ret = getSepEnduranceData(ret)
                eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 'Type':'Endurance'})
                eChar.RDstart.put(eChar.curCycle)
                eChar.RDstop.put(eChar.curCycle + Count-1)
            else:
                eChar.wgfmu.executeMeasurement(GetData=False)
            CurCount += Count
            eChar.curCycle += Count

        if initialRead:
            CurCount+=1
            eChar.writeHeader("Endurance",eChar.wgfmu.getHeader())
            initialRead = False
        lvlaa += 1

    eChar.finished.put(True)

    for thr in eChar.threads:
        while thr.is_alive():
            thr.join()
            
            if eChar.checkStop():
                break

    eChar.LogData.put("Endurance: Finished Measurement.")

    while True:
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

    if WriteHeader:
        eChar.extendHeader('Combined',eChar.getHeader("Endurance"))

    return True 

############################################################################################################

def AnalogEnduranceVreset(eChar, PulseChn, GroundChn, Vreset, NumLevels, Vresetstep, Vset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
                        Count, MeasPoints, IVcount, IVIteration, tread=10e-6, Vread=-0.2, ReadEndurance=True,
                        Vdc=None, DCcompl=None, WriteHeader=True, DoYield=True, SMUs=None):
    
    """
    Standard measurement for Endurance measurements, this part relies on 
    please set the appropriate Channel properties beforehand via 'setChannelParameter()'
    GroundChn: Ground channel number
    PulseChn:  Pulse channel number
    Vset:      Set Voltage
    Vreset:    Reset Voltage
    delay:     delay before measurement starts
    triseS:    Set rise time
    tfallS:    Set fall time
    twidthS:   Set pulse width
    triseR:    Reset rise time
    tfallR:    Reset fall time
    twidthR:   Reset pulse width
    tbase:     base time
    MeasPoints:Number of Measurement points during Set and Reset
    Count:     Number of repetitions (maximum of 100)
    read:      Read enable, True for enalbed, False for disabled
    tread:     Read pulse time, (read pulse rise and fall time are 10% of tread), minimum tread is 1us. 
    Vread:     Read voltage
    SMUs:      Array of SMU's
    Vdc:       Array of DC voltages
    DCcompl:   Array of DC comliances
    """

    eChar.updateTime()
    CurCount = 1
    #initialRead = True
    initialRead = False
    #DCcompl = 0.01

    TotCount = Count*NumLevels

    VresetLevels = []
    #print(Vg)
    #print(Vgfloat)
    for i in range(NumLevels):
        j = Vreset + i*Vresetstep
        VresetLevels.append(j)
    print("Vreset all: ", VresetLevels)

    eChar.startThread(target = saveDataEndurance, args=(eChar, WriteHeader,DoYield, eChar.getMaxRowsPerFile(), eChar.getMaxDataPerPlot()))
    

    stop =  False
    #Run repetitions until number of ran cycles reaches programmed count
    
    lvlaa = 0
    Analevel = 0

    VorI = []
    IVal = []

    VorI.append(True)
    IVal.append(0)
    

    while CurCount < TotCount:

        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
        if stop:
            eChar.finished.put(True)
            break
        '''
        print("VresetLevels[lvlaa]: ", VresetLevels[lvlaa])
        VresetAna = []
        VresetAna.append(VresetLevels[lvlaa])    
        print("VresetAna: ", VresetAna)
        VresetAna = float(VresetAna)
        print("VresetAna: ", VresetAna)
        '''
        '''
        print("VG: ", VgLevels[lvlaa])
        VgAna = []
        VgAna.append(VgLevels[lvlaa])
        #print("1: ", SMUs)
        #print("2: ", VorI)
        #print("3: ", VgLevels[lvlaa])
        #print("4: ", IVal)
        #print("5: ", DCcompl)
        eChar.B1500A.setRemoteExecute()
        eChar.B1500A.SpotMeasurement(SMUs,VorI,VgAna,IVal,IComp=DCcompl)
        eChar.B1500A.remoteExecute()
        eChar.B1500A.setDirectExecute()
        '''
        #only endurance
        #Run as many 2e6 cycles as you need to get to IVIteration
        if Count > eChar.getMaxNumSingleEnduranceRun() and ReadEndurance:
            sol = Count/eChar.getMaxNumSingleEnduranceRun()
            frac, whole = ma.modf(sol)
            
            for n in range(int(whole)):
                
                while not eChar.Stop.empty():
                    stop = eChar.Stop.get()
                if stop:    
                    break

                createEndurancePulse(eChar, PulseChn, GroundChn, Vset, VresetLevels[lvlaa], delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, 
                                                tbase, eChar.getMaxNumSingleEnduranceRun(), read=ReadEndurance, tread=10e-6, Vread=-0.2, initialRead=initialRead)

                if ReadEndurance:
                    ret = eChar.wgfmu.executeMeasurement()
                    ret = getSepEnduranceData(ret)
                    eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 'Type':'Endurance'})
                    eChar.RDstart.put(eChar.curCycle)
                    eChar.RDstop.put(eChar.curCycle + eChar.getMaxNumSingleEnduranceRun()-1)
                else:
                    eChar.wgfmu.executeMeasurement(GetData=False)
                CurCount += eChar.getMaxNumSingleEnduranceRun()
                eChar.curCycle += eChar.getMaxNumSingleEnduranceRun()

            if frac > 0:
                count_Last = int(frac*eChar.getMaxNumSingleEnduranceRun())
                createEndurancePulse(eChar, PulseChn, GroundChn, Vset, VresetLevels[lvlaa], delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, 
                                                tbase, count_Last, read=ReadEndurance, tread=10e-6, Vread=-0.2)

                if ReadEndurance:
                    ret = eChar.wgfmu.executeMeasurement()
                    ret = getSepEnduranceData(ret)
                    eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 'Type':'Endurance'})
                    eChar.RDstart.put(eChar.curCycle)
                    eChar.RDstop.put(eChar.curCycle + count_Last-1)
                else:
                    eChar.wgfmu.executeMeasurement(GetData=False)
                CurCount += count_Last
                eChar.curCycle += count_Last
            
            if IVIteration == True:
                addHeader= []
                #addHeader.append('Measurement,Type.Primary,Endurance')
                addHeader.append('Measurement,Type.Secondary,PulseIV')
                #addHeader.append('Measurement,Endurance.StartPoint,%d' %(eChar.curCycle))
                #addHeader.append('Measurement,Endurance.EndPoint,%d' %(eChar.curCycle+IVcount))
                eChar.writeHeader("Additional", addHeader)

            if not stop:

                #eChar.RDstart.put(eChar.curCycle)
                #eChar.RDstop.put(eChar.curCycle + IVcount-1)
                eChar.rawData.put(PulseIV(eChar, PulseChn, GroundChn, Vset, VresetLevels[lvlaa], delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, 
                                    tbase, MeasPoints=MeasPoints, count=IVcount, read=False, initialRead=initialRead, tread=tread, Vread=Vread, 
                                    SMUs=SMUs, Vdc=Vdc, DCcompl=DCcompl,WriteHeader=False, Primary=False))
                #CurCount += IVcount
                #eChar.curCycle += IVcount

        else:
            initialRead = False
            createEndurancePulse(eChar, PulseChn, GroundChn, Vset, VresetLevels[lvlaa], delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
                                        Count, read=ReadEndurance, tread=10e-6, Vread=-0.2, initialRead=initialRead)
            #initialRead = False

            if ReadEndurance:
                ret = eChar.wgfmu.executeMeasurement()
                ret = getSepEnduranceData(ret)
                eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 'Type':'Endurance'})
                eChar.RDstart.put(eChar.curCycle)
                eChar.RDstop.put(eChar.curCycle + Count-1)
            else:
                eChar.wgfmu.executeMeasurement(GetData=False)
            CurCount += Count
            eChar.curCycle += Count

        if initialRead:
            CurCount+=1
            eChar.writeHeader("Endurance", eChar.wgfmu.getHeader())
            initialRead = False

        if IVIteration == True:
            addHeader= []
            #addHeader.append('Measurement,Type.Primary,Endurance')
            addHeader.append('Measurement,Type.Secondary,PulseIV')
            #addHeader.append('Measurement,Endurance.StartPoint,%d' %(eChar.curCycle))
            #addHeader.append('Measurement,Endurance.EndPoint,%d' %(eChar.curCycle+IVcount))
            eChar.writeHeader("Additional", addHeader)

            if not stop:

                #eChar.RDstart.put(eChar.curCycle)
                #eChar.RDstop.put(eChar.curCycle + IVcount-1)
                initialRead = True
                eChar.rawData.put(PulseIV(eChar, PulseChn, GroundChn, Vset, VresetLevels[lvlaa], delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, 
                                    tbase, MeasPoints=MeasPoints, count=IVcount, read=False, initialRead=initialRead, tread=tread, Vread=Vread, 
                                    SMUs=SMUs, Vdc=Vdc, DCcompl=DCcompl,WriteHeader=False, Primary=False))
                initialRead = False
                #CurCount -= (IVcount)
                #eChar.curCycle -= (IVcount)
        lvlaa += 1

    eChar.finished.put(True)

    for thr in eChar.threads:
        while thr.is_alive():
            thr.join()
            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
            if stop:    
                break

    eChar.LogData.put("Endurance: Finished Measurement.")

    while True:
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

    if WriteHeader:
        eChar.extendHeader('Combined',eChar.getHeader("Endurance"))

    return True 

############################################################################################################

def AnalogEnduranceVset(eChar, PulseChn, GroundChn, Vset, NumLevels, Vsetstep, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
                        Count, MeasPoints, IVcount, IVIteration, tread=10e-6, Vread=-0.2, ReadEndurance=True, 
                        Vdc=None, DCcompl=None, WriteHeader=True, DoYield=True, SMUs=None):
    
    """
    Standard measurement for Endurance measurements, this part relies on 
    please set the appropriate Channel properties beforehand via 'setChannelParameter()'
    GroundChn: Ground channel number
    PulseChn:  Pulse channel number
    Vset:      Set Voltage
    Vreset:    Reset Voltage
    delay:     delay before measurement starts
    triseS:    Set rise time
    tfallS:    Set fall time
    twidthS:   Set pulse width
    triseR:    Reset rise time
    tfallR:    Reset fall time
    twidthR:   Reset pulse width
    tbase:     base time
    MeasPoints:Number of Measurement points during Set and Reset
    Count:     Number of repetitions (maximum of 100)
    read:      Read enable, True for enalbed, False for disabled
    tread:     Read pulse time, (read pulse rise and fall time are 10% of tread), minimum tread is 1us. 
    Vread:     Read voltage
    SMUs:      Array of SMU's
    Vdc:       Array of DC voltages
    DCcompl:   Array of DC comliances
    """

    eChar.updateTime()
    CurCount = 1
    #initialRead = True
    initialRead = False
    #DCcompl = 0.01

    TotCount = Count*NumLevels

    VsetLevels = []
    #print(Vg)
    #print(Vgfloat)
    for i in range(NumLevels):
        j = Vset + i*Vsetstep
        VsetLevels.append(j)
    print("Vset all: ", VsetLevels)

    eChar.startThread(target = saveDataEndurance, args=(eChar, WriteHeader,DoYield, eChar.getMaxRowsPerFile(), eChar.getMaxDataPerPlot()))
    

    stop =  False
    #Run repetitions until number of ran cycles reaches programmed count
    
    lvlaa = 0
    Analevel = 0

    VorI = []
    IVal = []

    VorI.append(True)
    IVal.append(0)
    

    while CurCount < TotCount:

        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
        if stop:
            eChar.finished.put(True)
            break
        '''
        print("VresetLevels[lvlaa]: ", VresetLevels[lvlaa])
        VresetAna = []
        VresetAna.append(VresetLevels[lvlaa])    
        print("VresetAna: ", VresetAna)
        VresetAna = float(VresetAna)
        print("VresetAna: ", VresetAna)
        '''
        '''
        print("VG: ", VgLevels[lvlaa])
        VgAna = []
        VgAna.append(VgLevels[lvlaa])
        #print("1: ", SMUs)
        #print("2: ", VorI)
        #print("3: ", VgLevels[lvlaa])
        #print("4: ", IVal)
        #print("5: ", DCcompl)
        eChar.B1500A.setRemoteExecute()
        eChar.B1500A.SpotMeasurement(SMUs,VorI,VgAna,IVal,IComp=DCcompl)
        eChar.B1500A.remoteExecute()
        eChar.B1500A.setDirectExecute()
        '''
        #only endurance
        #Run as many 2e6 cycles as you need to get to IVIteration
        if Count > eChar.getMaxNumSingleEnduranceRun() and ReadEndurance:
            sol = Count/eChar.getMaxNumSingleEnduranceRun()
            frac, whole = ma.modf(sol)
            
            for n in range(int(whole)):
                
                while not eChar.Stop.empty():
                    stop = eChar.Stop.get()
                if stop:    
                    break

                createEndurancePulse(eChar, PulseChn, GroundChn, VsetLevels[lvlaa], Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, 
                                                tbase, eChar.getMaxNumSingleEnduranceRun(), read=ReadEndurance, tread=10e-6, Vread=-0.2, initialRead=initialRead)

                if ReadEndurance:
                    ret = eChar.wgfmu.executeMeasurement()
                    ret = getSepEnduranceData(ret)
                    eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 'Type':'Endurance'})
                    eChar.RDstart.put(eChar.curCycle)
                    eChar.RDstop.put(eChar.curCycle + eChar.getMaxNumSingleEnduranceRun()-1)
                else:
                    eChar.wgfmu.executeMeasurement(GetData=False)
                CurCount += eChar.getMaxNumSingleEnduranceRun()
                eChar.curCycle += eChar.getMaxNumSingleEnduranceRun()

            if frac > 0:
                count_Last = int(frac*eChar.getMaxNumSingleEnduranceRun())
                createEndurancePulse(eChar, PulseChn, GroundChn, VsetLevels[lvlaa], Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, 
                                                tbase, count_Last, read=ReadEndurance, tread=10e-6, Vread=-0.2)

                if ReadEndurance:
                    ret = eChar.wgfmu.executeMeasurement()
                    ret = getSepEnduranceData(ret)
                    eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 'Type':'Endurance'})
                    eChar.RDstart.put(eChar.curCycle)
                    eChar.RDstop.put(eChar.curCycle + count_Last-1)
                else:
                    eChar.wgfmu.executeMeasurement(GetData=False)
                CurCount += count_Last
                eChar.curCycle += count_Last
            
            if IVIteration == True:
                addHeader= []
                #addHeader.append('Measurement,Type.Primary,Endurance')
                addHeader.append('Measurement,Type.Secondary,PulseIV')
                #addHeader.append('Measurement,Endurance.StartPoint,%d' %(eChar.curCycle))
                #addHeader.append('Measurement,Endurance.EndPoint,%d' %(eChar.curCycle+IVcount))
                eChar.writeHeader("Additional", addHeader)

            if not stop:

                #eChar.RDstart.put(eChar.curCycle)
                #eChar.RDstop.put(eChar.curCycle + IVcount-1)
                eChar.rawData.put(PulseIV(eChar, PulseChn, GroundChn, VsetLevels[lvlaa], Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, 
                                    tbase, MeasPoints=MeasPoints, count=IVcount, read=False, initialRead=initialRead, tread=tread, Vread=Vread, 
                                    SMUs=SMUs, Vdc=Vdc, DCcompl=DCcompl,WriteHeader=False, Primary=False))
                #CurCount += IVcount
                #eChar.curCycle += IVcount

        else:

            createEndurancePulse(eChar, PulseChn, GroundChn, VsetLevels[lvlaa], Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
                                        Count, read=ReadEndurance, tread=10e-6, Vread=-0.2, initialRead=initialRead)

            initialRead = False

            if ReadEndurance:
                ret = eChar.wgfmu.executeMeasurement()
                ret = getSepEnduranceData(ret)
                eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 'Type':'Endurance'})
                eChar.RDstart.put(eChar.curCycle)
                eChar.RDstop.put(eChar.curCycle + Count-1)
            else:
                eChar.wgfmu.executeMeasurement(GetData=False)
            CurCount += Count
            eChar.curCycle += Count

            if IVIteration == True:
                addHeader= []
                #addHeader.append('Measurement,Type.Primary,Endurance')
                addHeader.append('Measurement,Type.Secondary,PulseIV')
                #addHeader.append('Measurement,Endurance.StartPoint,%d' %(eChar.curCycle))
                #addHeader.append('Measurement,Endurance.EndPoint,%d' %(eChar.curCycle+IVcount))
                eChar.writeHeader("Additional", addHeader)
            
            if not stop:

                #eChar.RDstart.put(eChar.curCycle)
                #eChar.RDstop.put(eChar.curCycle + IVcount-1)
                eChar.rawData.put(PulseIV(eChar, PulseChn, GroundChn, VsetLevels[lvlaa], Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, 
                                    tbase, MeasPoints=MeasPoints, count=IVcount, read=False, initialRead=initialRead, tread=tread, Vread=Vread, 
                                    SMUs=SMUs, Vdc=Vdc, DCcompl=DCcompl,WriteHeader=False, Primary=False))
                #CurCount += IVcount
                #eChar.curCycle += IVcount

        if initialRead:
            CurCount+=1
            eChar.writeHeader("Endurance", eChar.wgfmu.getHeader())
            initialRead = False
        lvlaa += 1

    eChar.finished.put(True)

    for thr in eChar.threads:
        while thr.is_alive():
            thr.join()
            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
            if stop:    
                break

    eChar.LogData.put("Endurance: Finished Measurement.")

    while True:
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

    if WriteHeader:
        eChar.extendHeader('Combined',eChar.getHeader("Endurance"))

    return True 

############################################################################################################

############################################################################################################

def AnalogStepEnduranceIV(eChar, PulseChn, GroundChn, Cycles, Vset, Vsetstep, Vreset, Vresetstep, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
                        tread=10e-6, Vread=-0.2, ReadEndurance=True, 
                        Vdc=None, DCcompl=None, WriteHeader=True, DoYield=True, SMUs=None):
    
    """
    Standard measurement for Endurance measurements, this part relies on 
    please set the appropriate Channel properties beforehand via 'setChannelParameter()'
    GroundChn: Ground channel number
    PulseChn:  Pulse channel number
    Vset:      Set Voltage
    Vreset:    Reset Voltage
    delay:     delay before measurement starts
    triseS:    Set rise time
    tfallS:    Set fall time
    twidthS:   Set pulse width
    triseR:    Reset rise time
    tfallR:    Reset fall time
    twidthR:   Reset pulse width
    tbase:     base time
    MeasPoints:Number of Measurement points during Set and Reset
    Count:     Number of repetitions (maximum of 100)
    read:      Read enable, True for enalbed, False for disabled
    tread:     Read pulse time, (read pulse rise and fall time are 10% of tread), minimum tread is 1us. 
    Vread:     Read voltage
    SMUs:      Array of SMU's
    Vdc:       Array of DC voltages
    DCcompl:   Array of DC comliances
    """

    eChar.updateTime()
    CurCount = 1
    Count = 1
    #initialRead = True
    initialRead = False
    #DCcompl = 0.01

    Setnum = Vset/Vsetstep
    Resetnum = Vreset/Vresetstep

    TotCount = Cycles*Setnum*Resetnum

    VsetLevels = []
    #print(Vg)
    #print(Vgfloat)
    for i in range(Setnum):
        j = i*Vsetstep
        VsetLevels.append(j)
    print("Vset all: ", VsetLevels)

    VresetLevels = []
    for i in range(Resetnum):
        j = i*Vresetstep
        VresetLevels.append(j)
    print("Vreset all: ", VresetLevels)

    eChar.startThread(target = saveDataEndurance, args=(eChar, WriteHeader,DoYield, eChar.getMaxRowsPerFile(), eChar.getMaxDataPerPlot()))
    

    stop =  False
    #Run repetitions until number of ran cycles reaches programmed count
    
    lvlaa = 0
    Analevel = 0

    VorI = []
    IVal = []

    VorI.append(True)
    IVal.append(0)
    

    while lvlaa < Cycles:

        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
        if stop:
            eChar.finished.put(True)
            break
        '''
        print("VresetLevels[lvlaa]: ", VresetLevels[lvlaa])
        VresetAna = []
        VresetAna.append(VresetLevels[lvlaa])    
        print("VresetAna: ", VresetAna)
        VresetAna = float(VresetAna)
        print("VresetAna: ", VresetAna)
        '''
        '''
        print("VG: ", VgLevels[lvlaa])
        VgAna = []
        VgAna.append(VgLevels[lvlaa])
        #print("1: ", SMUs)
        #print("2: ", VorI)
        #print("3: ", VgLevels[lvlaa])
        #print("4: ", IVal)
        #print("5: ", DCcompl)
        eChar.B1500A.setRemoteExecute()
        eChar.B1500A.SpotMeasurement(SMUs,VorI,VgAna,IVal,IComp=DCcompl)
        eChar.B1500A.remoteExecute()
        eChar.B1500A.setDirectExecute()
        '''
        #only endurance
        #Run as many 2e6 cycles as you need to get to IVIteration
        if Count > eChar.getMaxNumSingleEnduranceRun() and ReadEndurance:
            sol = Count/eChar.getMaxNumSingleEnduranceRun()
            frac, whole = ma.modf(sol)
            
            for n in range(int(whole)):
                
                while not eChar.Stop.empty():
                    stop = eChar.Stop.get()
                if stop:    
                    break

                createEndurancePulse(eChar, PulseChn, GroundChn, VsetLevels[lvlaa], Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, 
                                                tbase, eChar.getMaxNumSingleEnduranceRun(), read=ReadEndurance, tread=10e-6, Vread=-0.2, initialRead=initialRead)

                if ReadEndurance:
                    ret = eChar.wgfmu.executeMeasurement()
                    ret = getSepEnduranceData(ret)
                    eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 'Type':'Endurance'})
                    eChar.RDstart.put(eChar.curCycle)
                    eChar.RDstop.put(eChar.curCycle + eChar.getMaxNumSingleEnduranceRun()-1)
                else:
                    eChar.wgfmu.executeMeasurement(GetData=False)
                CurCount += eChar.getMaxNumSingleEnduranceRun()
                eChar.curCycle += eChar.getMaxNumSingleEnduranceRun()

            if frac > 0:
                count_Last = int(frac*eChar.getMaxNumSingleEnduranceRun())
                createEndurancePulse(eChar, PulseChn, GroundChn, VsetLevels[lvlaa], Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, 
                                                tbase, count_Last, read=ReadEndurance, tread=10e-6, Vread=-0.2)

                if ReadEndurance:
                    ret = eChar.wgfmu.executeMeasurement()
                    ret = getSepEnduranceData(ret)
                    eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 'Type':'Endurance'})
                    eChar.RDstart.put(eChar.curCycle)
                    eChar.RDstop.put(eChar.curCycle + count_Last-1)
                else:
                    eChar.wgfmu.executeMeasurement(GetData=False)
                CurCount += count_Last
                eChar.curCycle += count_Last
            
            if IVIteration == True:
                eChar.writeHeader("Additional", [])
                eChar.appendHeader("Additional", 'Measurement,Type.Secondary,PulseIV')
            
            if not stop:

                #eChar.RDstart.put(eChar.curCycle)
                #eChar.RDstop.put(eChar.curCycle + IVcount-1)
                eChar.rawData.put(PulseIV(eChar, PulseChn, GroundChn, VsetLevels[lvlaa], Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, 
                                    tbase, MeasPoints=MeasPoints, count=IVcount, read=False, initialRead=initialRead, tread=tread, Vread=Vread, 
                                    SMUs=SMUs, Vdc=Vdc, DCcompl=DCcompl,WriteHeader=False, Primary=False))
                #CurCount += IVcount
                #eChar.curCycle += IVcount

        else:
            
            createEndurancePulse(eChar, PulseChn, GroundChn, VsetLevels[lvlaa], Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
                                        Count, read=ReadEndurance, tread=10e-6, Vread=-0.2, initialRead=initialRead)

            initialRead = False

            if ReadEndurance:
                ret = eChar.wgfmu.executeMeasurement()
                ret = getSepEnduranceData(ret)
                eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 'Type':'Endurance'})
                eChar.RDstart.put(eChar.curCycle)
                eChar.RDstop.put(eChar.curCycle + Count-1)
            else:
                eChar.wgfmu.executeMeasurement(GetData=False)
            CurCount += Count
            eChar.curCycle += Count

            if IVIteration == True:
                addHeader= []
                #addHeader.append('Measurement,Type.Primary,Endurance')
                addHeader.append('Measurement,Type.Secondary,PulseIV')
                #addHeader.append('Measurement,Endurance.StartPoint,%d' %(eChar.curCycle))
                #addHeader.append('Measurement,Endurance.EndPoint,%d' %(eChar.curCycle+IVcount))
                eChar.writeHeader("Additional", addHeader)
            
            if not stop:

                #eChar.RDstart.put(eChar.curCycle)
                #eChar.RDstop.put(eChar.curCycle + IVcount-1)
                eChar.rawData.put(PulseIV(eChar, PulseChn, GroundChn, VsetLevels[lvlaa], Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, 
                                    tbase, MeasPoints=MeasPoints, count=IVcount, read=False, initialRead=initialRead, tread=tread, Vread=Vread, 
                                    SMUs=SMUs, Vdc=Vdc, DCcompl=DCcompl,WriteHeader=False, Primary=False))
                #CurCount += IVcount
                #eChar.curCycle += IVcount

        if initialRead:
            CurCount+=1
            eChar.writeHeader("Endurance", eChar.wgfmu.getHeader())
            initialRead = False
        lvlaa += 1

    eChar.finished.put(True)

    for thr in eChar.threads:
        while thr.is_alive():
            thr.join()
            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
            if stop:    
                break

    eChar.LogData.put("Endurance: Finished Measurement.")

    while True:
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

    if WriteHeader:
        eChar.extendHeader('Combined',eChar.getHeader("Endurance"))

    return True 

############################################################################################################

def ShortIntermittentReadEndurance(eChar, PulseChn, GroundChn, SMUs, Vg, NumReads, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
                        Count, tread=10e-6, Vread=-0.2, ReadEndurance=True, 
                        Vdc=None, DCcompl=None, WriteHeader=True, DoYield=True):
    
    """
    Standard measurement for Endurance measurements, this part relies on 
    please set the appropriate Channel properties beforehand via 'setChannelParameter()'
    GroundChn: Ground channel number
    PulseChn:  Pulse channel number
    Vset:      Set Voltage
    Vreset:    Reset Voltage
    delay:     delay before measurement starts
    triseS:    Set rise time
    tfallS:    Set fall time
    twidthS:   Set pulse width
    triseR:    Reset rise time
    tfallR:    Reset fall time
    twidthR:   Reset pulse width
    tbase:     base time
    MeasPoints:Number of Measurement points during Set and Reset
    Count:     Number of repetitions (maximum of 100)
    read:      Read enable, True for enalbed, False for disabled
    tread:     Read pulse time, (read pulse rise and fall time are 10% of tread), minimum tread is 1us. 
    Vread:     Read voltage
    SMUs:      Array of SMU's
    Vdc:       Array of DC voltages
    DCcompl:   Array of DC comliances
    """

    eChar.updateTime()
    CurCount = 1
    initialRead = True
    #DCcompl = 0.01

    InterCount = int(Count/NumReads)
    print("InterCount: ", InterCount)
    if NumReads > eChar.getMaxNumSingleEnduranceRun():
        raise ValueError("Can't have more than 2e6 data points")

    CountIter = []

    for i in range(NumReads+1):
        if i == 0:
            a = 1
        else:
            j = InterCount*i
            CountIter.append(j)
    print("CountIter: ", CountIter)

    eChar.startThread(target = saveDataEndurance, args=(eChar, WriteHeader,DoYield, eChar.getMaxRowsPerFile(), eChar.getMaxDataPerPlot()))
    

    stop =  False
    #Run repetitions until number of ran cycles reaches programmed count
    
    lvlaa = 0
    Analevel = 0

    VorI = []
    IVal = []

    VorI.append(True)
    IVal.append(0)

    eChar.B1500A.setRemoteExecute()
    eChar.B1500A.SpotMeasurement(SMUs,VorI,Vg,IVal,IComp=DCcompl)
    eChar.B1500A.remoteExecute()
    eChar.B1500A.setDirectExecute()
    

    while CurCount < Count:

        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
        if stop:
            eChar.finished.put(True)
            break

        initialRead = False

        #only endurance
        if InterCount == 1:
            createEndurancePulse(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
                                        Count, read=ReadEndurance, tread=10e-6, Vread=-0.2, initialRead=initialRead)

            initialRead = False

            if ReadEndurance:
                ret = eChar.wgfmu.executeMeasurement()
                ret = getSepEnduranceData(ret)
                eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 'Type':'Endurance'})
                eChar.RDstart.put(eChar.curCycle)
                eChar.RDstop.put(eChar.curCycle + Count-1)
            else:
                eChar.wgfmu.executeMeasurement(GetData=False)
            CurCount += Count
            eChar.curCycle += Count

        else:    
            createEndurancePulse(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
                                        Count, read=True, tread=10e-6, Vread=-0.2, initialRead=initialRead)
            
                                    
            ret = eChar.wgfmu.executeMeasurement()
            ret = getSepEnduranceData(ret)
            #print("ret['Data']0: ", ret['Data'])
            ret1 = ret
            ret2 = ret
            #print("ret['Data']1: ", ret1['Data'])
            app0 = []
            app1 = []
            app2 = []
            app3 = []
            app0.append(ret1['Data'][0][0])
            app0.append(ret1['Data'][0][1])
            app1.append(ret1['Data'][1][0])
            app1.append(ret1['Data'][1][1])
            app2.append(ret1['Data'][2][0])
            app2.append(ret1['Data'][2][1])
            app3.append(ret1['Data'][3][0])
            app3.append(ret1['Data'][3][1])
            #print("ret['Data']123456: ", ret1['Data'])
            #print("app0: ", app0)
            #print("app1: ", app1)
            #print("app2: ", app2)
            #print("app3: ", app3)
            '''
            ret2['Data'][0] = app0
            ret2['Data'][1] = app1
            ret2['Data'][2] = app2
            ret2['Data'][3] = app3

            print("ret['Data']111111111111: ", ret['Data'])
            print("ret2['Data']: ", ret2['Data'])
            ret2['Length'] = [2, 2, 2, 2]
            print(" ret2['Length']: ",  ret2['Length'])
            
            eChar.rawData.put({'Name': ret2['Name'], 'Channel': ret2['Channel'], 'Length': ret2['Length'], 'Data': ret2['Data'], 'Type':'Endurance'})
            eChar.RDstart.put(eChar.curCycle)
            eChar.RDstop.put(eChar.curCycle)
            '''
            #print("ret['Data']22222222: ", ret1['Data'])
            

            for e in range(NumReads):
                #print("ret['Data']6645645747: ", ret1['Data'])
                #print("CountIter[e]*2: ", CountIter[e]*2)
                app0.append(ret1['Data'][0][(CountIter[e]*2)-2])
                app0.append(ret1['Data'][0][(CountIter[e]*2)-1])
                app1.append(ret1['Data'][1][(CountIter[e]*2)-2])
                app1.append(ret1['Data'][1][(CountIter[e]*2)-1])
                app2.append(ret1['Data'][2][(CountIter[e]*2)-2])
                app2.append(ret1['Data'][2][(CountIter[e]*2)-1])
                app3.append(ret1['Data'][3][(CountIter[e]*2)-2])
                app3.append(ret1['Data'][3][(CountIter[e]*2)-1])
                #print("app0: ", app0)
                #print("app1: ", app1)
                #print("app2: ", app2)
                #print("app3: ", app3)



            ret2['Data'][0] = app0
            ret2['Data'][1] = app1
            ret2['Data'][2] = app2
            ret2['Data'][3] = app3
            #print("ret1['Data']111111111111111: ", ret1['Data'])
            ret2['Length'] = [len(app0), len(app1), len(app2), len(app3)]
            #print(" ret1['Length']444444444444444: ",  ret1['Length'])

            #CurCount += InterCount
            #eChar.curCycle += InterCount
            
            eChar.rawData.put({'Name': ret2['Name'], 'Channel': ret2['Channel'], 'Length': ret2['Length'], 'Data': ret2['Data'], 'Type':'Endurance'})
            eChar.RDstart.put(eChar.curCycle)
            eChar.RDstop.put(eChar.curCycle+NumReads)

                

            CurCount += Count
            eChar.curCycle += Count
        
        if initialRead:
            CurCount+=1
            eChar.writeHeader("Endurance", eChar.wgfmu.getHeader())
            initialRead = False
        lvlaa += 1

    eChar.finished.put(True)

    for thr in eChar.threads:
        while thr.is_alive():
            thr.join()
            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
            if stop:    
                break

    eChar.LogData.put("Endurance: Finished Measurement.")

    while True:
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

    if WriteHeader:
        eChar.extendHeader("Combined", eChar.getHeader("Endurance"))

    return True 


def LongIntermittentReadEndurance(eChar, PulseChn, GroundChn, SMUs, Vg, NumReads, ReadsPerIter, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
                        Count, tread=10e-6, Vread=-0.2, ReadEndurance=True, 
                        Vdc=None, DCcompl=None, WriteHeader=True, DoYield=True):
    
    """
    Standard measurement for Endurance measurements, this part relies on 
    please set the appropriate Channel properties beforehand via 'setChannelParameter()'
    GroundChn: Ground channel number
    PulseChn:  Pulse channel number
    Vset:      Set Voltage
    Vreset:    Reset Voltage
    delay:     delay before measurement starts
    triseS:    Set rise time
    tfallS:    Set fall time
    twidthS:   Set pulse width
    triseR:    Reset rise time
    tfallR:    Reset fall time
    twidthR:   Reset pulse width
    tbase:     base time
    MeasPoints:Number of Measurement points during Set and Reset
    Count:     Number of repetitions (maximum of 100)
    read:      Read enable, True for enalbed, False for disabled
    tread:     Read pulse time, (read pulse rise and fall time are 10% of tread), minimum tread is 1us. 
    Vread:     Read voltage
    SMUs:      Array of SMU's
    Vdc:       Array of DC voltages
    DCcompl:   Array of DC comliances
    """

    eChar.updateTime()
    CurCount = 1
    initialRead = True
    #DCcompl = 0.01

    InterCount = int(Count/NumReads)
    print("InterCount: ", InterCount)
    if NumReads > eChar.getMaxNumSingleEnduranceRun():
        raise ValueError("Can't have more than 2e6 data points")

    CountIter = []

    for i in range(NumReads+1):
        if i == 0:
            a = 1
        else:
            j = InterCount*i
            CountIter.append(j)
    #print("CountIter: ", CountIter)

    if ReadsPerIter > InterCount-1:
        raise ValueError("ReadsPerIter must be smaller than Interation Count")



    eChar.startThread(target = saveDataEndurance, args=(eChar, WriteHeader,DoYield, eChar.getMaxRowsPerFile(), eChar.getMaxDataPerPlot()))
    

    stop =  False
    #Run repetitions until number of ran cycles reaches programmed count
    
    lvlaa = 0
    Analevel = 0

    VorI = []
    IVal = []

    VorI.append(True)
    IVal.append(0)

    eChar.B1500A.setRemoteExecute()
    eChar.B1500A.SpotMeasurement(SMUs,VorI,Vg,IVal,IComp=DCcompl)
    eChar.B1500A.remoteExecute()
    eChar.B1500A.setDirectExecute()
    

    while CurCount < Count:

        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
        if stop:
            eChar.finished.put(True)
            break

        initialRead = False

        #only endurance
        if InterCount == 1:
            createEndurancePulse(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
                                        Count, read=ReadEndurance, tread=10e-6, Vread=-0.2, initialRead=initialRead)

            initialRead = False

            if ReadEndurance:
                ret = eChar.wgfmu.executeMeasurement()
                ret = getSepEnduranceData(ret)
                eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 'Type':'Endurance'})
                eChar.RDstart.put(eChar.curCycle)
                eChar.RDstop.put(eChar.curCycle + Count-1)
            else:
                eChar.wgfmu.executeMeasurement(GetData=False)
            CurCount += Count
            eChar.curCycle += Count

        else:    
            # run no read pulse train
            createEndurancePulse(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
                                        InterCount-ReadsPerIter, read=False, tread=10e-6, Vread=-0.2, initialRead=False)

            ret = eChar.wgfmu.executeMeasurement(GetData=False)
            #ret = getSepEnduranceData(ret)

            # run read pulse train
            createEndurancePulse(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
                                        ReadsPerIter, read=True, tread=10e-6, Vread=-0.2, initialRead=initialRead)
            
                                    
            ret = eChar.wgfmu.executeMeasurement()
            ret = getSepEnduranceData(ret)
            #print("ret['Data']0: ", ret['Data'])
            '''
            ret1 = ret
            ret2 = ret
            #print("ret['Data']1: ", ret1['Data'])
            app0 = []
            app1 = []
            app2 = []
            app3 = []
            app0.append(ret1['Data'][0][0])
            app0.append(ret1['Data'][0][1])
            app1.append(ret1['Data'][1][0])
            app1.append(ret1['Data'][1][1])
            app2.append(ret1['Data'][2][0])
            app2.append(ret1['Data'][2][1])
            app3.append(ret1['Data'][3][0])
            app3.append(ret1['Data'][3][1])
            #print("ret['Data']123456: ", ret1['Data'])
            #print("app0: ", app0)
            #print("app1: ", app1)
            #print("app2: ", app2)
            #print("app3: ", app3)
            '''
            '''
            ret2['Data'][0] = app0
            ret2['Data'][1] = app1
            ret2['Data'][2] = app2
            ret2['Data'][3] = app3

            print("ret['Data']111111111111: ", ret['Data'])
            print("ret2['Data']: ", ret2['Data'])
            ret2['Length'] = [2, 2, 2, 2]
            print(" ret2['Length']: ",  ret2['Length'])
            
            eChar.rawData.put({'Name': ret2['Name'], 'Channel': ret2['Channel'], 'Length': ret2['Length'], 'Data': ret2['Data'], 'Type':'Endurance'})
            eChar.RDstart.put(eChar.curCycle)
            eChar.RDstop.put(eChar.curCycle)
            '''
            '''
            #print("ret['Data']22222222: ", ret1['Data'])
            

            for e in range(NumReads):
                #print("ret['Data']6645645747: ", ret1['Data'])
                #print("CountIter[e]*2: ", CountIter[e]*2)
                app0.append(ret1['Data'][0][(CountIter[e]*2)-2])
                app0.append(ret1['Data'][0][(CountIter[e]*2)-1])
                app1.append(ret1['Data'][1][(CountIter[e]*2)-2])
                app1.append(ret1['Data'][1][(CountIter[e]*2)-1])
                app2.append(ret1['Data'][2][(CountIter[e]*2)-2])
                app2.append(ret1['Data'][2][(CountIter[e]*2)-1])
                app3.append(ret1['Data'][3][(CountIter[e]*2)-2])
                app3.append(ret1['Data'][3][(CountIter[e]*2)-1])
                #print("app0: ", app0)
                #print("app1: ", app1)
                #print("app2: ", app2)
                #print("app3: ", app3)



            ret2['Data'][0] = app0
            ret2['Data'][1] = app1
            ret2['Data'][2] = app2
            ret2['Data'][3] = app3
            #print("ret1['Data']111111111111111: ", ret1['Data'])
            ret2['Length'] = [len(app0), len(app1), len(app2), len(app3)]
            #print(" ret1['Length']444444444444444: ",  ret1['Length'])

            #CurCount += InterCount
            #eChar.curCycle += InterCount
            '''
            
            #eChar.rawData.put({'Name': ret2['Name'], 'Channel': ret2['Channel'], 'Length': ret2['Length'], 'Data': ret2['Data'], 'Type':'Endurance'})
            #eChar.RDstart.put(eChar.curCycle)
            #eChar.RDstop.put(eChar.curCycle+NumReads)

            eChar.rawData.put({'Name': ret['Name'], 'Channel': ret['Channel'], 'Length': ret['Length'], 'Data': ret['Data'], 'Type':'Endurance'})
            eChar.RDstart.put(eChar.curCycle)
            eChar.RDstop.put(eChar.curCycle+InterCount)

                

            CurCount += InterCount
            eChar.curCycle += InterCount
        
        if initialRead:
            CurCount+=1
            eChar.writeHeader("Endurance", eChar.wgfmu.getHeader())
            initialRead = False
        lvlaa += 1

    eChar.finished.put(True)

    for thr in eChar.threads:
        while thr.is_alive():
            thr.join()
            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
            if stop:    
                break

    eChar.LogData.put("Endurance: Finished Measurement.")

    while True:
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

    if WriteHeader:
        eChar.extendHeader("Combined", eChar.getHeader("Endurance"))

    return True 


def createInterEndurancePulse(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
                            count, NumReads, read=True, tread=10e-6, Vread=-0.2, initialRead=False):

    tfallread = tread * 0.1
    triseread = tread * 0.1
    InterCounts = int(count/NumReads)

    tmstart = tbase/2 + tfallread
    tmend = tbase/2 + tfallread + tread
    duration = sum([tbase,tfallread,triseread,tread])

    eChar.wgfmu.clearLibrary()   

    if read  and initialRead:
        eChar.wgfmu.programRectangularPulse(PulseChn, tread, tfallread, triseread, tbase, Vread, 0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Read", WriteHeader=False)
        eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Ground", WriteHeader=False)

    durationR = sum([triseR,twidthR,tfallR,tbase])
    if twidthR == 0: 
        eChar.wgfmu.programTriangularPulse(PulseChn, triseR, tfallR, tbase, Vreset, 0, measure=False, mPoints=-1, AddSequence=False, Name="Reset")
        eChar.wgfmu.programGroundChn(GroundChn, durationR, Vg=0, measure=False, AddSequence=False, Name="Ground")
    else: 
        eChar.wgfmu.programRectangularPulse(PulseChn, twidthR, triseR, tfallR, tbase, Vreset, 0, measure=False, AddSequence=False, Name="Reset")
        eChar.wgfmu.programGroundChn(GroundChn, durationR, Vg=0, measure=False, AddSequence=False, Name="Ground")
    
    if read:
        eChar.wgfmu.programRectangularPulse(PulseChn, tread, tfallread, triseread, tbase, Vread, 0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Read", WriteHeader=False)
        eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Ground", WriteHeader=False)

    duration = sum([triseS,twidthS,tfallS,tbase])

    if twidthS == 0:
        eChar.wgfmu.programTriangularPulse(PulseChn, triseS, tfallS, tbase, Vset, 0, measure=False, mPoints=-1, AddSequence=False, Name="Set")
        eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=False, AddSequence=False, Name="Ground")
    else:
        eChar.wgfmu.programRectangularPulse(PulseChn, twidthS, triseS, tfallS, tbase, Vset, 0, measure=False, AddSequence=False, Name="Set")
        eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=False, AddSequence=False, Name="Ground")

            
    # Creating the sequence for entire pulse train
    
    
    if count > 0:
        Rid=1
        Sid=3
        #Pulse Channel
        eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Reset_%d_%d" %(Rid, PulseChn),"Set_%d_%d" %(Sid, PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
        #eChar.wgfmu.addSequence(PulseChn, "Pulse_%d" %(PulseChn), InterCounts-1)
        
        #Ground Channel
        eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d_%d" %(Rid+1,GroundChn),"Ground_%d_%d" %(Sid+1,GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
        #eChar.wgfmu.addSequence(GroundChn, "Ground_%d" %(GroundChn), InterCounts-1)

        Rid += 4
        Sid += 4
        
        for x in range(InterCounts-2):
            #Pulse Channel Reset
            eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Pulse_%d" %(PulseChn),"Reset_%d_%d" %(Rid, PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            #Ground Channel Reset
            eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d" %(GroundChn),"Ground_%d_%d" %(Rid+1,GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
        
            Rid += 4


            #Pulse Channel Set
            eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Pulse_%d" %(PulseChn),"Set_%d_%d" %(Sid, PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            #Ground Channel Set
            eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d" %(GroundChn),"Ground_%d_%d" %(Sid+1,GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)


            Sid += 4

        
        Rid = int(InterCounts*4)+1
        readid = int(InterCounts*4)+3
        Sid = int(InterCounts*4)+5

        #Rid = 1
        #readid = 5
        #Sid = 3

        #Pulse Channel Reset
        eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Pulse_%d" %(PulseChn),"Reset_%d_%d" %(Rid, PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
        #Ground Channel Reset
        eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d" %(GroundChn),"Ground_%d_%d" %(Rid+1,GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
    

        #Pulse Channel Read
        eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Pulse_%d" %(PulseChn),"Read_%d_%d" %(readid, PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
        #Ground Channel Read
        eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d" %(GroundChn),"Ground_%d_%d" %(readid+1,GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
        

        #Pulse Channel Set
        eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Pulse_%d" %(PulseChn),"Set_%d_%d" %(Sid, PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
        #Ground Channel Set
        eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d" %(GroundChn),"Ground_%d_%d" %(Sid+1,GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)

        #readid += 4

        #Pulse Channel Read
        eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Pulse_%d" %(PulseChn),"Read_%d_%d" %(readid, PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
        #Ground Channel Read
        eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d" %(GroundChn),"Ground_%d_%d" %(readid+1,GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
        

        
        #Pulse Channel Read Section
        #eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Reset_%d_%d" %(Rid, PulseChn),"Read_%d_%d" %(readid, PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
        #eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Pulse_%d" %(PulseChn),"Set_%d_%d" %(Sid, PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
        #eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"Pulse_%d" %(PulseChn),"Read_%d_%d" %(readid, PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
        eChar.wgfmu.addSequence(PulseChn, "Pulse_%d" %(PulseChn), NumReads)

        #Ground Channel Section
        #eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d_%d" %(Rid+1,GroundChn),"Ground_%d_%d" %(readid+1,GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
        #eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d" %(GroundChn),"Ground_%d_%d" %(Sid+1,GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
        #eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_%d" %(GroundChn),"Ground_%d_%d" %(readid+1,GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
        eChar.wgfmu.addSequence(GroundChn, "Ground_%d" %(GroundChn), NumReads)
            


    eChar.wgfmu.synchronize()
    
    header = eChar.wgfmu.getHeader()
    header.append("Measurement,Device,%s" %(eChar.getDevice()))
    header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.getLocalTime())))
    header.append("Measurement,Type.Primary,Endurance")

    eChar.writeHeader("Endurance", header)
    
    return header