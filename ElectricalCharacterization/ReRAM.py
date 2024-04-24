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
   ��6���y�Z�C%��3��ss��ᩰF�
��5�/
�?Wh$����f�����H"�>U��g:���w��M���\Ȳ�M�L�.�������@K���ៈiAPD6�n�T`P:�+gؓ��O6͇bQFF�98�Y�1�lHη,N��C-���Pu���K�N� k��Î٫�Ƴ�z���`;P+D'Kb�Q�Q�D	8A���%��[B=/e�3u��5�/ $8#jE2��ȡNTl~'�^�OԊ�_:�+'r�����TR���hd�}`y�h��8�,J��,9���7=F��[r�nu�'�3���Í^�d�����JQxh�3��37mWF�
��.�V(�E�.ׇ����;��r��t�e��'*����Y����2��q��L��9 ��₈��uݾD�_�_@?H(��B�ɮ��tV�AӺ]I!Z�zZl?���U�GJ��?q�v���/ �Y�:���
|�%���>M�M���]���XT�y��\d��p|�`�Ͼ.(�F�x�&��5�4�i�������=���Fފ�-tE`ld��zQ��y[�AQ\dx�-�d�3���<)��������%�AC�>8Nu���:;��Ajk�o�x�E� ?x(��������j\gm�N��f	J_n�X7B���^�@cHδl
6�F���L_�>�W{���;z�2R��מ�p���"��X�wu8���D��e��b?�N�N�B��!5�@��0)���ªA�xٮ��C�jq"!Џ��`Y�����y:i�gA�2�o`x� ;��W ��ԄkQ��q�m��I\?�W�ߘʷ���q��v���vnr�]���PJ�|3-������A��ImoJ�|6����e�S��p
8�PI哺l�$���/8�kb�#�����\�4��GՓ�+T�Θ֫�v��& �C+�H _ϵ���]��=k'�Ȓ��Q���f���kP��q����l�7E�	�����b����4p����p_��M��N�|�Xo@�H�+��'��珳���nޔ`WP�:�k#Wa��j�u}����hT�vڞ�q�q�T+������i.��^�@}����M�M�M���T���p�;��g{����S Xm3�`�c�+�˵�O=�鹶���,t%�c �4p/vD�3[ڜc��dSX»)�f�R��;+}�Y��͙��ŕ�v���]a'XZ2 �>A�_�_;@+H'N��A��Q��D[KCOI���X�|ezO殆1�����}6g�X�� ���<.��F�J��9�*��e@�=����G����9���7,.��C3I����P�hg�$�^�PZ;���m����Z��m���V��I��y�Z�.��:�n�N���Y�/������?S-�׺�~q��qI�A^$�|P�1�n�V��Y��j�������*�e�Q�F�|������Ҝ'S G"�clS4xm�WPDFɈ,g3o6��$7!�b�q^_y�S�3x���9F9nܻ��w�IQ�DxZ�MH���Hg��0��,d�#�V�g�ma�t�#��bԫ����M��ݘ�K��TdSz��^b7$��|�k>^#�~�pz�lՠ�}^���@r����4+�R�O�3@�d��\��-7����b���S̡\�~�A��|7��@ۣ���C��v�[��>^<�	�������9�b�ĐSDdn����Ab�IGJB�\^�p��D��mex-�;��u��_�wa�$�I+��;̤�c{���E�[��*n�p�:3���ݓ�T�C����{�n%43 �՝�\��� $eT�rb �t�u�nP��rl����V��v�G�<�(��&��5�������G��~����{0l{��p��FTj�%O_}+�K��w�n[�LAT�������<�O c�8#ؒ$�����e@��#�o�|�1?-A�n�<��������ӫ�}mZZ�;!�%6[�><S��2��rF=��Z
8����\�m�=6W������y�ҡ�T�4��"X��g+R���]� �\�a�"���l���Ш��ܛ�dF��x*,B}�ʹ�}�Gpn4x�L����{$S&2��o� D�w5uC�lׯ�rm:��$/|����1>�U�`)�|g���p����(U��s�����H><�U�,Љ{���}Ő���q�\����O�y{yr�����Gq��Bf4�;TR52�\�$�F|�
}!����uطN�q��h;��Ć�ңtw��J׹JL�u�(�S����I2y��ﳀ�3�ےm�U?te%�M�q,�T��zd	Ӱ�pQ�O�:=]��Z ���8w"��T��*�^{�g?�l�5�����Z�� ��뵈p^R����f< �.Ub����YX��\(x�����(c�+�+�_X��^f�ؙ�����
�	���=j��B�����:M�d[�/��;;.������jUS��\��2G���5O�0Q��d�\�Ev�J��D�'�����[��#�����AL4<ĭ�߬�u%d�+fg�%��	R�x��G^���0�mw�:��d�j���}�ȃ���
�Fx��ș*~}U#�ׅA�A_�p?B�{<�ߪn̤U;sk���DG���I6|� ��/����8�߾]t��nzcg`�T�'��O�k?j����쪴���^<*�*L��0ol\P�3{̦�O�;+ZL��:�D�{�ै������i,W�*���p
4S_�:���;B�>Ch��I�7�٫�,�L����kl���NI��� Kx�[�͋�j�?c�.Yܿܤ�r��� ٕ�E+�
�N��>��*]\���J�c�<�o�+'ᣍ�U�r�����zJ-����O��l�`ع5�8|*������[�{��!8�6��#m@���T�{���7�oR�rS(����f�����A�S� �?ޓH�p��<
��ґ�D�ҩ�k�k�%.k����X��ߌ�e=�V~q�jV�najj�1͖Ba��2�_u`׼�V��t��v�%{�uV�虔��8�Ǽu��P�g<eR`��Aq��q���!QT�5�m���ZY�ul����荸y�|���E,UgX����^�{�	8j�eIf����'�k-U��;u�'W���L
r�]�|��Tz�q�s����T���a��`�3|k������I�υ[*y�I)��l��e�S>��[b�7��b�Q��M�M�M���h��ߍS�����ɗv;��f +,&�g�d� !�K�? gn��������rsg�pmdΨ#X�;.��I��u��x��.$"��х�f����o�d
n��Ϸg@N�k��G�8�D D�ͮ%� ��Z[��/C�F����)�&�"�!���E&x�������e®� y�ZkL$gr��n�ڸPJ x��U���O�.Vdk쎏� sѕ�Ijc�Jo	 ��T�bc��CpL����;��/i��S�rf&���������6*�n�mY��F�o��N'J�
L�Zϯ��pG�fA��m���WF�J��z�l˦`#�l`�ޢqΡ��J���1�hR��$	����xꞄW��M�6)a��s�����{��?G���1<I"̯H�h�ɢ���hOV����0KlU�9���Bl6�B8j���wt�a��1!�r���dô�O�_�ͷ��D�����K�9S�?�J��39���t�����?�Hs�#&��&±�	��I�3�%�~�%�T�����g ������D`X_�F���cf �wS ����q�\GAʈo�u  Oۿ�*[��V��KO�C�y�����8}��&�ѵ KH���z�l��kP�3;�����S�x��o��8�Coy�⹊�Z�
���ml�|7h��ѱ��U�S�� �4Q19�q�F�k��5%'S���|
܄ڌw�wh�y��s8걷 ��䀀�yx�f&�g�]��'I�
��x�Ց��M�M�����a`]⊆d�\'���=W+�B%���>�f���\��Q�
���=�i�S���^�<'�S�ӣܳc���c6���tg_R�k�uW�u�_�3-򥽃#����e��v�%U_�ZG���r��gt��.r�,�����A�܈�ߨ�x����cq��-'�30�~j-�A2�@�}����~��M�����|��V�F�_��~` �����ޖ�~�fdc�<��&l9լ�e2���R2�c�d�*���x|������
�?)�e�<��})!���1��B���a�d!�[��k��iJל�\��k�{��I�N�Lj����ЕC��ũ��z�7n��O'c٠��Q��A�GN�
PĻ�y����&c��57�p��}4h�&�P�2��2�s�2�֐�������N�R$E1+ /���A&h� �WEc�dG�e~ky�Ƞ�vA��c��u?p�d_5�C���z���=)�����i����3�]� ,s��I%����ۅ(D&�b�Q�@;H+N�L̝ܮ̄f^ OE��"�ht_y�(5.�c���Gl
��86���>�l�J�.�$I�N��|m���U�P���N�1�j[e��&��a>��ǉ�^T�u���0�kMp|�i儉2�����~9���}��S|;G�el�t ��z�E,$����c������2f�L��5�[k9rb����m���T3`���k��y���S+E�K2�5�P�����ύ���F�J��6�.��3X-¥��R����3�?GU�G 
��85��6��G�P�!�`}��]�9��҃[��3̹����2��K��DTG7�KW�$���`q(]P��r�����*a]�e��OP��~\�r�ǡ]�|�:�\˲�hM֍�ʠ˾�L��a�/J/0%E����7�۲A|sn%�	#%��!R�thm��OC�7�]��xLL�_�^Ъ���=�L2 �ё��4E���`�n/EG�n|"�W�`Ώ,\%��(q�r�ݤa�4�Z�d�J�,Y儼{�������,��c��	Jus����6�n�Tt_z�g �ǯ�� Sxڻ#a�=SV�=N&�<�J��[P>�x����.��<�E�|�o.:�׫ն������{\�7]S!��%/o2S� �� D�}�$f ���:�Eu��ζ)8[�$i��B�yi�'�F�U�����b�O�Ǥu�_�2�-����Y>���#�Ç�3h�Y�N��L3~�\J����-�a�#i��)�Q)7���Q�4�ŭV�bxh]��ݨ(�B��har��MP����2�ok�0�؞�W(���%�H���)z�/�4~��&��V/�b���%���~�c��Y򱽌I��Ѭd�i�-ij��s"]��N��c�u�lG�ŗ+��f��ų�@�+2Ж��̗BXlɗ�3�/��KZ�s@�-[�ņ��s>��	���L
����֕����<I����~��1g�!��U�:��_�<����7p�|���	 �� r����JP^�{�'�R��vO�fg�͢큵�O�5��|�lOrLwX����xޅ�[oV,i���Fe��f�	[a�P/�D�8���*T��ß�娓�^� b���N}4������_�%*[>�x~��Sú�?Xh|��t�l�$�"�~-�C������>�w��>%c|��b�Q�J�OL?	�Y���ɞk��db^���'b3ޟ �/$�b~�s�,���PZ��]��<
Th�.���F�4@�gߪ���֏��/���o:��r��q�IY��% �E�-��*}����xW�����9�j�W �:�npd#�����C�߈�l}{�st�q�@1�,n��Cc���|Sܗn�]�HN�LSM��5��·� ��32�텵�`F(e��F�u�n	@^�ra�W�����x>��S���zg.3�>�W�1�D�t!dӮ<¶鎂�.��mb�r޹38]Y���F���o�?7�U�㔛d���rS,���^G3��A*�FF� [�l������
��|���W-����|��q���+H�j�4��9��9,����)��Y��~�`�����$��m��ܠs@�-�%؀Y�B;�L��ā�#ހb�Z@��Mo/=��<���&�(�
>9�j��n�����rn���G��M-��q�g�s.����!�~���3� <*�֘�TCGI�بn&t�l}�Tlo�j�>$��i]��?*��W��
�}��V�>�"�� �����䱙���9��WLn)j_��d�9sk)IZ�:�ۡM &X$ZO?���Da�PoDM8-^� ���QL57.}O��"ǌ��4[oCT	�~��w^���=FId8���L��/�{8j�Wƽ���h��&MY��?�c8 ��^�@b����LT�}���ڵ��n>��{�
x�&��$��C��$������=������8q��!V��ATPx�-�$���tqS���罭����c C�nJP0,;e�S7E��r&7*��)�8�Fr^<i��6����{y:����vzi�lV}�iT^�^3��*wx��S��9�j�W/�
�n$�c�����Ϡ�#���qc@�C�)��ag�>�ɺ�Yw��h��mN�Gl�k覀��@�0��*^ħ�pH&����'��?�3b_�}}ƙ���%����{
�X5��h�j����6��ݙ���U����/dr���d�k{�p;\+A�Hr���֐*D��N�}e�3�V@9�)���2�-��vLy��7L����?�%�4y�Z�?y���p��m����f���"߁@��Fc-��KLۭ
���2H�������V���xq����q��'�ͿmV�Bjf����w�_��?\�n���������!��3K/��@:����7}�[G�z�Y� ':�i��?e�����>����y�X7 lz��p1��LO5��޷b�S_�{xY�@J���/{&٠ ��sy��w~�Z��:�)Ť)��*����������H,,	O{�M�M�)+�����0lX]j��	��D1�8&dm�rF��^�H��{T=|���J鼥�j�(	4�A�ᩏWKp���|���gC�kM�~e�:�T�[¿��h����l��(�f̣��+_݁X�ݰ^��6�Q%���"PηD������=�Q?���{�4�ڈ�юJ�7�n�4�.҆Le��÷��։c�'��CO<CZ����ƃ�{ev,#s�t!HV!q�}9Pq6$��NdSu��+ `"�!�"UJ�:�Jw7.��ƔX
�ˉ�,0p�par�68�0y�l��k`��1��Id��)�s�q�a���_�)�˖�����G���菘/{,a3 ��a`qr�o%3RP`�o�%c?��$rW(�Ù�hCa�q�J\�Z0>�v��ǌY?1��4a��`�bM �<�U�|�/́�]��Ю�����Fk�,�T� L]�H��ô�i�iak,5�Ą*]F���/#F�5)�VG}�u1�,ge��iƦR��0��'"�'��G����5�iڄ�4�����&�ͪ�/r��,>	\5��G'e�.�^�w?�~�0!�����IJ��ɻ.�7,4:a�3d�gR�ŏDOd8��>1�P�s���(�?�����׳-�坳��]�2�\^��O��Y���àv��b3�[��k<i��������A�D�M��AcΎ�\&��|7o�v�;�`B�	�M�<f�ǚ���U����ɗ}�d#Sa��8aC7!ؚ�(}P�5�*@a�?�tRb��ʀgI��O��U�Uz;��z��-�e��j ��=��b���z�T�A��\
Ӆ,������&�"��Q�_Z0o\饿�걀ױ S`�hpn3��e�SE��^f%aR�$���3"�P�ug?FХ�oS�6���w+^�2�L�̕!Z�|U��"���E
�^�Z���.6�:��f�����^�)�٘b����3B�˭�=3��&Db� d�XP�x�#�h����m ������� ��V�(�Hk68������M"|U�7��T~�HwN���T�+	��Mj�w�_��ϧ=�D�~�����2�G�����[ys6�@6嫝4?{�f4��I�+T�+*��]:��ɨ
���r�/���^��Y�ҹ���mf�h�"����d[i�E�����b>@�WFǏ�jxmq�,��du�_K�njd��=��tң��)�?�޸Ɠ�
ֿV�u���XZ��S�Σ�ot�h3g�aƀmR�?��a-fā�z�y���M�"q�cЦ�#�\'ψ�"��� WǺ�>�:8��(�Ұ-�SE���|�j��wY���;�T7�׃�m�@�:W����X#(�����"F���],�r#B�Ƀ'�#���	A�%�¸�ƶy�ri���0��]I���k�e��G�~�~�'i����I����*�(4_�4�JI53e���<Jɻ��$
0O�H!�U�GJ�?{#���˜�<-��3a@�u��)t�]�?�c���~�X��͑��G�1Q��
�?$(#f��� �VR���)&]7� w�Ǜ5�o�7'�� �HK���,��q-�<���>�q*���뙑fd���3�n�޿p�m�6����;�����,�<A}�4��3~���Cں�0h��{=�i����)��{ֵf�Ӳ��Q]��M���� Ti�H�C��r��N�8���тY����[0�3Le4����6'���}+F�J��{�e���q�\���)����&���x�k ��vy(��wЯ�C�\�}&�ц�Z�p�����~�XgL���^�  F���fX�r}��?W��*��.�d~���y��G���y��0�p��U��S9�S�ٺ�=�i�E���� W���Ͳ�����D�4L�V^_@JMt�����N1R0�3U��|�+I?Vx��D�w���DK;V�]Ȭ��}z�x\r%c���4YE���/d:�k�]&����X1ی��>�Y�őkf���=���+�C�Q��{��t������\0ʹG�U�Gj��LH�x�DƢ���`�\�z�����h^{����T)x�"dN�"YO�=M��I
��RZ��Z�A�J�M�OlN��~���Ǟ���FL�����8#(c$S!�"�cPS�8(hdTQ���� v��3c/&�	?a�?��% OP��r����<|�v�0����"ܿ������35��Z�lF(p\:���c�?���H
*5�@@����8u�.9WuƟ*�'$R�-ҕ?!L�d���kg��$�O֏�E�%�c����V�.��˪�MӍ�Ʊ�d0.�܈q�*Q��k�q�w)ަ�B�Z�Y����0�2�����f��!�ǡM�b"<\��C�c���{'41�!̈1��V�2�����횒k�R,�3��r>V.��R�E��f�=�v��������ɿ4W���y9=��CO�Z�� y��3<-����B��*����!f�e' ��p�y]�q��7x�A���7z���=�
�ӝ���/�D;����8j����G�0;J�=�X�f�e	���y���������=��%{,8B=��3����ey5\0�8u�XCm�h,R��(��NJ��]Z4�P���q�"�4`5ϡ�#Vr��˃�'�g�SY �_@<,�P��+��\J��l]Ʈ�y��E�y�+�,���H̻�����D��l�N��,nktT������v�%hUh���7!k�рdXB���}�m-�"�S;4�4Ȇ���Tܫn��T�;d��B��#�.�C������e���������fǖOs1i�%�#a���Xz?!����P�^���M}�}u�6���w	�@��;<��%�w��B�`�G�4(�[���@經�﮵9���b��aWQy:��_�l�J�O4/}�J�;������]%�ޤ�syMv�7r�'?V�xT��0��y��n~�#�A�<�/	�>�h}��������U����;�=V uf/k��D~"�ъ3#
$%�.�L�^v�y:9J����H��J�4\/A�[07є���]ׅh�&��O���rr�
�����sJ�h�����:9��Z�4��1.K*�C�|����/>�(Cf恝��?ON�~��ER�2x^�h���b�!��?YV���Y.ޙǨ^�#&�F���	�@x�޶���xb���U�(m��J�i�dr�o���G�:�ϋ�`�|�����_d��+K��&-�,��2�Z�}4(��D���ՠg �5��\M|w#x�w���L�~uh&2���H\���p/si�~���9�-�d
:L���m&�����Z�X;�o�xi��[�)�B���'�=��6�n� d����݀��C� � A\�m�<1Y�ޜ\��{;����s�IG��Q�8�Tj:�W�i�Ҷ厜O>���-���}��i��q#�^Wx���7�W�M��b^�yk�����b�M�+��_
�?(2������]�6��Bm�b["QȠ۬\�~E��QT�DE,���T�d�)QY��" �g�����pu�k�m��[I1*�P�����8̆�sZ-���|3v��;�y�|�X]6�@�y�� ��X��c?냛��Z��5��r�s�pYj��a�������Y]���J��h_b=�!�$���SR��[�/,��m���y
�H���\�m��W=��dR�擟�s���)>�R�::G�յ��9��ށr;�\@,�=���C	�~��xR���tF�>q����Z�1a�g���|�����f�Қ����B	LR��K��Ʊ�|n�=� ��P�[>�hYւ���כ��E���tDKp`H��9�ݴ@>zL:X�r���f *xA4���p�#��;s�ID����k�e?*čj�W	l���o(&����	�i�7Y��+X�r��ցg�*-����|����K���_��[๥�$�;b�?���]H��D�'�����J�O%�q����[X����ڌJ1�,d%�c%��g8�>��'1��%�W�'��A�x�z�4�ߣ��������ѐdT|6��c_wwl?$�S+1S��Syuv?{ǡv����nTtsk�Q�DU�G/J�\@5u����~��F��A$�Fzp��|�%�i�Q{ȣWt�<��˪*��e���a?Oh���ѽ�="�Dj�eL$k�{��v2.ߔ\zV��J�:`H�4�O�_
���/G۔ψs��Q�9��	�C�҈�e�������Μ99��@el�e�sbN�]�m�sc����P���Η�,�# !� z�pf4~���M��.��rT,0�b�w�r��I�Zw��D�ǂ��p���rO�
��$x#Z��U%�S�� �9/5��М�dd�է'�����
n�d�e�V�oyy?���Ր3����UV5���#8!�w n�|�h@�5j�>�w����e��v����I�Ҽe��n�� yz������/��p�*S�w#b��G��Rǜ�N��-�%��Mҽ??̕J�&���H���k�i���k��Z��쪨�x"��@�� {xZ�C�����-$��<�Z >���4K�|��eN�1F�|%��Q�GڹR���Nz�+��#���������uʯ��k��M��4��TD��-�i�1�S�i�u�`����������:�ۈU::K:"Zx~"��5�
hzD(f�R���A>[Q6���5�oFe*=�@WjF���_$ #x!ڠRT�S5�{�p�C1��n��i+g֡��)�/���x_Z�qK|����B��%��;�
$��_��y�g�/�=�i������"�(�����{+[ŷ۸U#t�-61�l{U�GS�d)tg��rZ��D2�d�Lt�}��v�a��ՃY��י���կ'R�3�4sN,?G�x{����/;d+Sg7��h�/�OEX�y���b��;|q6��4f�R��{u5�z�?������!V��b���(4 �L]���a
�1����v��h	�~��Vb�ђ�U�G}���m�r�'.���j�*���œ+�wa���E�q>:�[��e���Ng��B�ɮ�n�TA�Hj��ZVǔ�+��)���9�j�W*��³)�������HӮ��_ &M����	șW�)|_W?�lA��1���jA	N��@m���N��M��כ9�j��'&������ğT�d�di`	�>�(sf؞��iI����{5�o#TQ�,9�pQx� ��!��~��wr��(�O{�"Ş@�f�-�ǀQ���}�م���xAڈ3QTa/�Ǻ]�r�]�A�[~�XY�Ǯ�����Y��!�`KPpX,�����}t3?P��ɖ�0.�fh4P';�o@ w�rԃ>\��wr���!�H>!��`�Ub���4Iq������"�g=�BA�\=i��E���[��N��dm�#��F|��
��x�m���B�	�~ͨ8����]�ՈΝ�yƪ`}r�&�@92��Z�"���0oC`�j��N�=E�
HL���-0�ӷZ~��-|�hg�)�\�n�o�&��(��Њ^ʺ�����h��dB3��-QW~Y^��Q�F�<�{?gL�8�Č#����	M���buΟ,P%�#D2�>�R�2�ϐz#��c��󃑦}�i��_��|<}A���ō���3�@�w/-!Q
���f>KĐtTGp
�PB�}:��C$(RT��G�����z$�[��q��O;�5F���z��q�3��$~�XAi�Ü�a�4�l�$��G3����a���s�&�Z7\.��XsBԏ���g;!�o��txZ�9������bI1��aq�qu+���C��N��p�Q���<ᅀţL�S���S.��[3,>���K!���G�y:*�������vv��[���]}spl�j��<�XF�=橲�ͪ�a��RVa�r; fI3����tO_L Z�t��r�/�3l-��3�����F-,-�U2�C�2Z�V>��R����c~��;�Q��SE�K=�i����>�,��;� ��R���z�a��;G�[�n/ȝ��#�^h����A��Dn�e���N�9w���O:�+�q��҈�9���ڶ���|y����1ž2��i�%�##�}��2ҭ����4����ͭlE(�v���M8w�U{R��j�dAA��qz�i�L��K;3�I�%�����p�W=Ʃ���*�7���J�fj��m��7��� �H�����D�9c�vv��x({r��?��o�JA�d>�hU��&����VP���q��Xai�C�%����s�L�<�����Vĸ�Մ�t
7/W�<�$K?�R
[��z��0cl;��g?R���l�n/2�B�4���RѴ�-ܗˏT�6o���a�?���(�9��ŷ+�B��ܾ��.Y�@��M�97T�-������OF3;��G�.��c)�h#u� �ɗ��'��)���mK����٠b��} �:�|'Y��R�Ů�j{���o)�F��v5*��O��L�{�|�͗�=������~�|2��ަХ=6���Dn�T_G@|�"�b�N��+8'j����K���U�g7�V��B��/���k7��`ʵ �H�u]�;�2��Q��ܖ�蟩��:��0|��~U��ɒ#�g;R�E�K�s��|I����q��`� p�n�EqS��I�N��m����ZP�����u�1�l��uF�[�| ���[�"�G����Zn�e��H���?s��Z���N��7\�4�[[��:�������=�P�g�g����K*H����ǐ��c8c�3y�X@I{4a�s��2��UA49���B���9.j��ϔ�`�ѣD@���,weޓ !�Fs:�+~�j=��U��*��¼i̵���|�k�}Ƹ:��>&Hs檖������%E[�0M^T��j���oɨ_8x�c��.B��]�pc^���+�����zH�gO�·+	3�@޹�p|�D{Y���L���Afk \�;o��@�F�:�[5��>��:��ᔀ�Y�@������*Vq\�Ͳ�yM	aa�Pl�wI���L��L��'/b��t:��Y�0�x=�����ϋ㙮��e�S��vO'~VfĠ�|r�{�T;GkJ�=Q�w���� RMQ��7���u�3p-�%ӧE=�]��\/s���'���O�J�O>�(]�����������[�C��<5%�����ty�Z�vv�*��v|���݆[���f�y���
S��39����?�l����(�%3b���Z�C,	���8}��`����k}�+�[u��q9�j��6���}�+������89X�����s
���4J�OI/�
��Ţ��.fSn�����gһ%�cQ�2H�L��ˆf��QMB�����f��u�L@�5}{9������:��'7b���T[G1̛y�q9�^e�jr`!����e��
��38-��GK����n�je�*|�%������>�}���ң`��gt��?��k-)q��(��H���<ki�V�����}Ħ�2v���FCv��B8�u��4|/Y��<�b��<}͖��OH7��/�;�{7[n�TY�0���Jέl7h��-���C��^� 7�V��;��s���Y���i�ƶ���,~��C"���S|w\�r��A��r��ԃ���cp��1E� M%<X`�&�b���KO|����Ȇ�`�~JP5�/+d'Sb�ћ$Sc7��e#cI�5d�YJ�H�C ��{��3?�܆�"K �ȟ7�q�[q�\i���#���ϸM
���7��DLM�M����E�#�Zgm�����Gp��˞�E!� g`�5�/dd�s��M'R����Sr�ݛS�2�B$'�@�+#�����>��J��>�3��7�[�#��Yǃ�<�V�Ԧ���l��:yȽ��!f��-�e�SE�Nm,�S�Ͱ��-*ŞYg~���`h�6�n�u�L�{r�줏�����Yt� [xZ��
��6�|��L5���w����:�*q(���
��'8"���r�Ox��O�Dt�%G�*��m�v���%�����y����bG��t����S!�S�%��F�)� �g)Ҧ����ɽ�ən�~cGQʄoT3Gmʿ�6�n�ToGT
�7S�v����er&ݍ	��R�=i�vK���	���,��I���Z�44��L�7�L/���g���ݖ��V�����;k9"N����#r(� p 
1�,p%�#!��pp1�4<��"�n� 	CE�o�Z�i�����燹���#p!� a�p4/q� %��a��@R,��m�/ڥ�f;M�M�M���]���hWV��ډ�la��pu�5!� | �2�-�%����||��������r�e�[ekd\G��;䭬E��/sd�q��C!��n�V.r���Y�B�	���HkN�LV��ީ�3Y�w���A;WkF�J֏&�"��pLUK��<ڟ��>q�1�,��6r�q��fa��m��w޲�M��=��Ɓ�	ȓ����"K���v�7(fc�:1�a���@;\T��6Yե�^N�LP�=�i�Vچ��p4�������(E��2� �TO\M8��2�����X3B�Ʌ��c{Q�DcK!�?N2�	6Y��qGv��O��Wd�p�jF�5�'W�B�����~����V�����8:��z��N_63�ip�r�t]��"f*������]����TF�Jڏ#lt��9\�<���8�Sr�e�y���m/���*���5�{H�"���&l=��6®�v�^�@q�n��+���ӍBܠ$�	�JM�A_v����߉�!֨-v�J��xr&ܝU�G����<p)�&���q�I� *���m<���SF�r�CR�9�`M���0����^����O�J��:��w}ޙ�R��;�/�o�"W����R������H[��@��#���gJ:�[�x�����y�Z�C%��.��|sY����m��;�j^�pO<x�e⽻��RV�,9M��rܢ?�w��M��}�����^�g�ْ�ձ�B�ɉ���`kPD6�;�%`t�bU16 ɀ��A'��_uS�,-�;^ �V�9F��d ��C-���}�Y�B�I�N�k}��ч���Ȓ�1y���C%W|LQ'��Q�5V+(3E����;��04,/e�3u��5�/ $8#��S#�W���JPJt%���ÿ2�'d:����� ��]u�<0)�&���1�,J��,9��bq����D�Ja�`u�k�"Q����_��b���4�+Ks0����}>GWF�
��.�$z�[�xi�ïE���0��?��~�8��Oc��	��Y�ʑ�U�x�v��R��}晲�ͥ�����u�u@?H(��B�ɮ��tk\U�:ë0m`
�?(7f���U�GJ��N[Iq� 㛟%9��7n��J�O2�-�呙M�M���]���XT�y�ʁVs��?G�i%��� i��6�.��z�[=�iك�����s����߬uwe|q��cV�� �
CI`4�i��v���<)����Դ��`�3�eru[@H9Ϊ�G5ʯ/$;>����YNP6GO��W����[x%^�p�Z}_n�X7B���^�@cH��l�]���y�Z�:��
�>�(R����L�!���/���MC0�ܴ�y��w���P.�$�9�~��7<���)������=����:�(g*c����S�����t*�g�5�o1�l~��k��ՓgU��e�$��DJ/�D�4旎ண�{���ڱRsDx;��D��P`�|3Y������:�`;�[a6ͣܠ,� Ի8Kj�W���{-�e�I��.:�9C�l����r��q��]���hX���ڰ�k��@a�n�OwL��]���^��{�ʬ����Z�` ���??Z��,����LO�y�Z�������I��5T�:��W���T�XoB�	�~֘fҒ啳�����+��`6R�s�>w��%�v����hT�vڞ�q�q�b���6�,�.��\�@W����M�M�M�����<V���ꞥ~y�� �W�O"tr�y�b�"����Xt����Ԛ�x5w�htX�q?z>+�xqڜc��dSX»)�f�R��y^n<�s��͙��ŕ�v���ot#=�|�T}�}noG��A��Q��D[KCOI�� ��O�z~&xs���w����{0gb�zq��0��Zv�y5��F�J��9�*��+2�m�ә�]��ּ�9���7,.��C3I�����;R�-�=�M-���pﬃ�o��q���J��7cW��	�*�O}���F�)��Ų��}���R�ŤP0�֥�tj��:� K�?L�a�9���.�K.���龇�%�d���%|������џ$P#n!�`oP7{n�TSGE��ibV-q��'$"�/�-$Q/��#,��ŴkW|����%�cQ�Dx{�Mn���?��S%��.I�'.�d�p�+�z�$��A�����������a��TdSz��#saݕ-�VC[�?�l2�-Ы�sa����Tb���TQ�Dj�WF�
�?-�%����=5�߁�|��a��Q�p�)0Z��^,��މ�֍�f�:�[��51}�Y��ɩ���j�W7F�ψm@Qg��^Q�D�TKGOJ��1��J��?,(%��~���0ȑI�gRb�1�I��q���rh�����~��:E�{� <���і�V�F����:�++ggR����B_%�nbsP�Ab�e�'~�d|մop��&����C��9�*��.�}�Y���饶��#����>~?v��y��@AR�,C_	�K��%�kP��']U����7�q�T1�lj��&�����hE��j�'�T�:j�B�)̞�Ξ֬HOBʁ��J#@�so�JwP�0[lU��:�7n��Kg:�[��/�^�C�0L��Y���8ϓ��,�l����"H�L���r��1�lY���)��Ѩ�����7�4KoOT}���� �Ag~6%	�tƵʻ�>HT4{'�� �\GB�bo?@W�j���y*D��@gH���O�4m�U�z�NE�;��7�Ʉ�^��s���LƳk~����0^��	� a�����}�Y�޹�J�(<&����u��Bz4�.Pa4:��	�D&ö
r!ͦ����m�=�<	�B>��VƆ���#>��@v�ް`<EA�x�,���8�@(|��ʿ���Xz�ݔ|�w![3�V�9b���[?Ch	־��rQ�D\{�=i��]@���j#/��E�S�
�Wt�&i�!�.����ƂB�����ˮp[\A��z�4SoE�Q/0�G��U�YK��x=ک����{6�n�T�y��^|�>ȁ��]��.��A���=)^��������0R���1;sk]�A��Bމ�^� hWE���B��4F���"G�y0��#��7�V*��
�H����Z��0�^����{Zuyʠ����j)m�bFN�7��U~�xj�����>�(u��w�y�f�/\���<�
�������N�)6����o?T(f����W]�<\�X<�ͪn��Xf&'Ν���F�_'M�%ƞ�*�����8���_5��y`T,#�T�^|�F�
�?3h-֥����Ư��i �]w��_!AA�"j���z�vr��!��6��|[Y�B�ɶ���%9U�Hv���ux �3
���;
�X:���'���vĺV+�G����"L���FQ���\)��r���v�.I�)��Վ�r�݌a��Q�Cx�@� 4��e���u8�����1��Tu�_*�'wq�����B����MS�vmn����C��b�-��MH�9x��V�����w��(3�W��g(�����2��5�oN�gV?����\+�Ɓ�p�CI�N�z��	�~��?*����"���ן9�*�''b����XWB�����t7�	0�/5�/3d-�e��%��:��<wiޖ��A�u��:�kQ�+�ʙ���b��� ̍G�s!yUv��u>��t���';UK�}�(���K\�lD �������1��PE�+gX����B�5��T&q]?�Rid�D�TlU��;�s]���Kr�]���3�6U�6��㿰c���a��J�3|-����� ���N&6�S#4ҁx��g1�n��Y6�<ـ/����D�ƙ�®[������xz��u��? ( &�"�!� F�
�}zmg�����FƊ��7 .�$@#8t��)'P�9z��
,��\ ��z�d�WOR��х:�Lϓ���/*�'b�ъ�_3@d�%��PA�;ad�LSM�ͫ-�e����?>�(6�Ƒ�N�h�v�s���J-o��򏃦��b���+3�W_'T]o-�,�;��POD}�Y�ʹ�
�?+h'V�����S6���4*)Q�w}QR�E�K�w,��C<	����~��f�9�A�X{m���ꁖ�d��kK�c����
mD��G�l���O:C�e�9��ѷ$N�LA��m���^\�J��-�%��1�l}�٧"¡��F�
��t�ht��C(	���}���R�E�K�> UԧR�����%��{�H�O�r}�����Ы��$���� aFU�9���;z�[Cz���13���uN�r�ݳ!��]��8]���Q �OϿ���7�K�1�_��rpk���1����1�,@%�#.��@sH�����l�5�]_}�V�)�&Ƣ���(N��B����	8GX��O��<Y <�&C}�ٮ��q�\GAʈo�s!V���kv�,�Y��mJ�O�=�酶��|q��-���+C���}�kګb�I3w�R�����q��W!Ơj�Smz�$���ڲQz�iu���������DJ�OL0�=��6�^��3Q���,
����`�g �Cq�h�R���<��c��Ŭk�{&�b�Q��C+ �N��c�����bB���^��dhV���*�'5�C�i �(g��b�(�р%��Z�-���=�i�ʶ��r,�S�Ϳ��)���'>���tg_R��;�u�_�3-���Lʙ��)��v�'h[��O~M�E�ʨo�:�k&�b֑��B�I����(ݧ�4R����]3!�� i�6�a&�s�$�����~��M�������V�6�X��ztZo��V��Ԅ��z�it*�c��SB~���>=ܤ�o�KOu�-�%�#	���x|������
�?.�$F�J��(l&���,��h�ɫ.�dj�WƷ*Χ,B�Ƀ\��#�Q��;�� j��o��ǜ+葀���z�7n��O'L"�ᝰQ�p��UK5�>!p���y����#%��0q�u��<`l�n�p�ˀ�Z�==�ز����O؉��5�}Aa;cl�$���IQpx-��KIf�5:�jO4<ޚ��T��y��CW�-�O�t�1�ԁRe���Ŋ,�ߘB�8�[�x
��	�����ۯ*6c�+��J~HH��ˑ�ц ��c�fnX�B!&�"��0Gl
��86���j�J�W�tU�+;�3��Vm�բ���M����1�,We��I��u<�����v�!��B�a�tEy�k�ָ4�����wZx��E ��^D|:�SP�=!�G�g�t/����g������Ht�t����A(p$�>���-��^�c<6Y���M��y���T'E�?{�!����
��܌��%���s�"��}Ea����K����6�k\�G,
��89��>��K�z�iv�/)��2�?�����=�靶ю�\sAݍ-��^~GJ��5���0l�o������o3T-�e�����|GYʂ��2�$�˸O>�?���ǨᙰR����{[CX{����"�Н^1TL~?�TH�`^� T8j���v�P��'	K6�p�|ٹ۸�v�b{�ݑ��@WH���K!�`lbG�dX!�X=�7��|`�� ��3�Ԏa�PY��y�Z΃,Y�m��������(�FA��5KS=A
����y�"�]^_z�3r�݅�� Sxu��`o$�"=W_�E � �X�� |��P���#��K�c��<giҖ��������)o�dNS>��VRMd�u�� 6�.�$h#V䥈+�_����8�(���	�:!n�%���MQ���
��J�(���6�_�s�d墔�z(���j�Ղ��qN!�O� c��YIk7�VA����a�g�o{���K.!�����^�OɆ�XA�{da!�bã�7���di"Ʃ�~� ���8�jb�!,����,a�՞,�����{9�j�W1Ƭjţyg�bߑ��W�8��2���s򱽌I��Ѭd �d�mEg��<k9�U����gF�P�(@���|��j�P����K�~d�����t%���8���Q�xv�}쉁��jغ���KoMӴ�,�����@@�i
����;��,+�-��!�ST������G���qA�9�⛉do�� r�k���I>|�l�|�U���$�|M�͢큵�O�5���4OEL�}���Rޅ� x(��1��{�{#[K�Pi��v�^��x\��Vؼ�����^� b���_@<)������1aXN�*v�!AѰ�LV<<��u�g��d�[}�Y������r��m���K$c|��b�Q�J�DsM�Ľ���=��4��+guҟ%�#!�c)�Q w�+���C��r��l ǅ�/V�g�(��x�>y�)�����Y���٬���_	DПD)y��=p�C	�~�X{B�I�=��c����S\�����j�W �:�+('�ו��J����b1�^7|o�[�@1�,n��C'I�ʴ���,�_��E��=�����*��32�����kV0F��Y�\�!@K�xGy�<�����x>��S���;#ka�Pf���N�}h7��W�嬤��~��pb���T(FǿJ�.í��{Ms!�N��ȿh���gGЕ�v�^� n�J�O�t������;�� �2�Gp��
��-��8���	�>�q��Z��$i�V�%��'��Q�,���CU�I��e����2�-�%����LM�K�����DҀe�9���?(1�r�ݫ!�`Z�QZ�+��~�ϔR��9]��=��K��y��s)����M������(�ZlYH�ё�TCGIʎ�t1�lc�4'-�d2�OΓ,U��3*�����}��t�|�jܗ9�瘆�⤈��u��:P4/{dSsE��!�`Dt?/=LE�Q���W1o)$C	q�ƕ)�&<@w<�"�u��LNw!̸rʝ��4[oCT	�~��;[ص�QX7a��}U�>nv�G콪ɇ.ڤcQ��z�[7Cn��.�!�z���Y�2���U���X	�k<���Pv��?Q�{��$��'�}�Y������=������~q��2Eު`_J&=�i�V�F�J�?|(�������ۼU-z_�&-^_Qxk0�#x	��}6HW@yc��4��(XA}i��6����{?[hV����bx}�]E&�ZOi�b}�I00��X	��q�w�0_�Y�a�/��XI�v���`sP�1���H_�=P(����_s�(�Zɿ B�O3�iʂ���L�6��I���X6��لb�Q�DA�H�_�פ��q��KU��>b�8[PC��}�&�*�L��<>����ԙ���U����/dr�ݏ!�u�A~%����ց8$_Z��Y�}<���S_u^�g���2�-��3-��s	ݻ��5P��4y�Z�?y���>��m��ۛO#֗�k�S�W~=��kݘ��,�L;����@�&���Ã�
9����>��xF���%�#<!�#�M�W<���kK�e�片�&�޹u�v���x1~u����zw�XD�y�Z�$9�j��<f��ƕ��Tx����?�-{O;8�_�:u�偹�_+����-�?LO�xQZ�CI���,x%ڣ#��pz�kD�'8���|�\��~��l�鎊�����A���c/.HP��o���{{s[]�A��F��_Od[c��O��(�	GK�u���:��q*I�������>�(f�ҵ��9���wO���0�IV�o�n�Tj�W����-����R��
�[��[��- IȄT����
��*�\�
ǪFX·)���B�ɰn�m� ��M=���ж6��M�'��9�A*�M%�Ӟ޷����&�b�Q�DKKOOL����Ş�_S>
#`!� d `5�/$$#ca��dF&��nn)4w�o�i&C��n&.����C)����\5i�fGi�i[�d1�le��'%�1��7&��e�i�a�1���D�8��Ǉ���K������fh#aA:��&l#RR�n,,RR?��dcSQ��k+WgF��՟'Dq�`�4\�uq>�ZW����l1��g5ү%�#a�5�U�r��ĝ2Z���������&�b���DM������:�+$'cb�єdWSF���/W6h�*�V$(� b�e+)��fڳR?��;��
a�4���O�4��I� ґ�t����G�ڈ�3)��dp\5��(t&�b��4CoI�K�?7ɉ����ED讌�|�+=I~�{*�gR�ŏ+'q�q��Ta�P�^\���p���0γ,M�ͳ-�坳��]�A���<
G��͇���v�m�&�[��ksEi�����+����$_�C\G�����\u��(`&�"�!�`B�	�>�hf��֗��C����ɟ.�$d#Sa��k$#ݍ�"�`�!|s�:~�rCj����, 1��6��X�-?z��z��-�e��e��=ۦ�6����r�]�A��\^��Xh������V�n�$�U�[Z.r}������.��l<5Q�npD%!Y���@ ��q&B$�v���`v��0gl���vZ�y��2%	�	�h��7G�5�� ���G	�^'�L�2��b�>ԝL�R慲��}�٘bґ��CI����xaڐc�t7�X&P�x�j�W5��d��^"���ч�B�o���z�?shֱ��B�ɵ��Q h�yD��P*t�	0���w�=��\Q�/�JɰƠZ^�g�&����|OY������,z)�U6ü�u(/I�3;��+S�.cF��C�V���Z��;�r�]���X^���Q�����Ll�P�n����'sXa�D�����{3$�'t6���jOlk�I1��du�_%�#(!�r�X�x��,��jm�x�翹�
ֿ&�"@OH��I����<p�jijl�3ؑKS�*��X,*Ѐ�1�[Aͷ�J�p�0c�x�\B�ɘnҔe�S���>�hq��3�������O�&��dSɿ�6�n$�߉�m�]�jf�ƅ�I5�С��A�F���_.�$X#B�ɀn�d7���O�=�٠���F�p2���0��ti���x�aį��9�*�'-⥱�Y�����ƻ�4qu�;�L^$Ea���6nԽ��R&�.��7l:�[I]��@����la��g$�u��`2�-�%�6Z³�;�V!����ހ�n���?g`m{ѵ�0�@Cֲ�2+e�S2��5�o�7'n���R|���Z��0i����>�(z���,鉆Dl��<�X�ϸ0l�z�sF���!�����V�y6�pe��3-���C
���0z��{=�<����$��{��)�ƫ��KA��7ۍ��tW�y�N��2���M}ҙ��������K:�kq��2��'�_Ɓ]	���l�o���a�\�����ϛ@c֪�8�E��3/m��w޽�I��<bلʷ�sǺ뢲1�6���	�v5=S޹�L]�*I�ڡl�GH���.�d~�XU)������:��a� ��R[��h�R����t�!��v���i����ѥü���4Q�Dt_@2���E��_t x0�3��C�=N?Zh|��W���DKXB�	����`
�WGv(���Tv�v��XN n�cA�2gګ�A�C~��^�q�R�Ŧk�q��B�ɤn�Ti�V�մS��w���X�����.� �S��PC�o�nΣ����]�w���Jx`������l@G�0s[�JN=�vxڸc
��x7Z��Y���� *M��?ё����������; +`'P"�!�`S?V�rg'(����Dq<��Q#}El�jk(�^�P�?_e��_6��F����Oh�c�n�'��(� ��ǩ����35��5�/d<c<���A�l���RA5�WY���3t�t' ��o�oj+�a��Xd�y���#&���8����^��c���z�[&�b�Ѣ�A�HM������f]2Ѐ�A�%G��!4�T�|����G�N��;��;�(��ٕ����Bʉ��0klx��r��0Eު�up	+�����Z�3Æ�4��ˀ�*�i�I��H{9,��x�E��	�~�kr�]�����ǣ��N9���c~#�M}KF�J�!� y��3<-����K��+���/1�,se��!��C0	�>��6�|��e�S���=�i���V���j�9����8��@{���|J�;�Q�b�c���}��Ӟ�����M�M�?M7KYo���3��� "V8�8u�7.�$OcL��m�U�[��\[}�M���m�O�5l ��kr���ќdQ�De�S/E�3m�G��l��J��n2��5���6�n�T~�XZ���������M��f�!��K|,sJ��B����:�&!-K�r��sp6���oZ���z�a�Pq�kq�\f���e����W:��X�6k��;��M�M����y�Zփ&������	Ú��;�]Of4}�q�`K/��N (���*B�	���`>�(T&�b����~��Fx�Řk�u���6�.�d}�Y���e�������l��g��=EZl~+��Q��%�	<|H�U�7��㨯�[r�݊�0P,%�I;Q�DwK^�@\��xJ��lF��<t)�f��5�/	�>�h}֙������J����Z�,V|H?yڻR91�ʩ*B3��T�C/�O\{m�ۢ�A��J�4\/A�s~ؔ�k�HSN��[-�e�����;=�i�Vӆ���{�&�����hJ���6��ta�M�m����fr�g%Ƃ���6Tp�p��@�>bO� h���>�g�bt��N�b�щ�^�@i����S�:^�ˬ`���xb���U�G>��_�j�bl�i��+������nꧏ2�ᶇɰ]48�c��${c[Q�DC�V�F�
�8*������ё��+S�e��[B2F+U�G2����;+wg^���W^���_Z2t�=��5�/�0Cl	���8r���R��CK�[i�$�h���|j��浲��=���q�/��<j����Á��V�5�i	�>�hx�����s9����d�C��7�:�Re2���a���Ͽt�ټb�Ѯ�DsK]�A�E��j�[{y����,��	Q��m]�41d�����{�/���_
�?(2���ř��u��b:�+} 3S����7
��H;N�LGMʍ��C�).��%k�7G�����5&�"�!��E�?}����ͬ#���\]���tm�yD�Q�D~�X_B�	�>Ҩe����bi���ʷ��t��C�~�X+��$ּf����s]���J��;Y5�ĉ�/��WR4�O�/m��P���|D�'���9�*��$r�]���hR����S�5���<�a�N=,����K
�{��օ-�W~�"쬙i	�~��xR����w=ީ�F�
�?6�.Ƥj�W)Ʀ���)����ʴC�;zh��8N��Gʱ�D=�i�V��z�8v�:W����������K͞E�/F~4F<u��3���d)5X B�c��HE�3n-_g���n�d��C8G	}�\�͠�k�e?*��j�.o㏌m2!�'��� �o�on���xi�e��F��Y\�7����k͇%�ʂ���,��\쐇�/��;�q�W��w��M������J�O&�"����@Qv���;���J1�,d%�c%��$q�\q��ha���S�{��]�r�M�2������V���͟���6VKu��}Qgqpm{�B&7�r�^Lydk4����ŨSHf9'�V�DR�j�[J3w����H��
 ��6_b�\fq��f�c� �[I��=������k��B���
q-u������xn�V&Fo�^5�:ֈ#*jt��ThV����s4�q�Oq�p�Ėg	Ҿ�s��Q�I�N�L{M�
��ͅm����[�����)%��s
"�!� X �9�*�'"����X+U������%�qUd� z� 3x-ڥ���z��hVq_�_&�"�!��A�X>��Y��ڊ�?���al�
��$x#Z�� i�����|{Y�B� �΂#9զ�uM�����_"�!� R��;+r�/��������SV7�ҍ*!�w �0J��;9�$�j��'��z��l���X�$Ҽe����s<���N��?��z�#z�Ei+��P������U-�%����Xz���rկ�d���y�D���m�C������o'�[�/�� {xZ�C�����z�q ���@9 ���L�1��O,x�F�y.���S�C��^��z�6�n��m�U��������9����%��A��x^��S�I�(�V��A�@�i���������vʞ�U|^=~}jg=���n[kLs	����V>C[Nw�����/�=QW87h�L$A���hSft!��/AS�x}�[j/<��
~��b��k`�훚R�w��H�,�F1����9�ޚSi��!�
2	��D�A�y�R��hH�1�i����Ǟ�G����|vRMCR�Ş�wt�pP1�>:�Z#1��Eh���DI�N�Lt�}��w�e����n	�ͩ��Ƌ��rP*�c�Fm�����l~7)I��)�dhP�},hBd�5���S&��*rR 1���]2� �Q�4I\v�Y`�3�����[N��7���Z2OV�	Z���^�:1��2˝�a� �$j�?��9`�ђ�#�X���D�<�hd5���@�W2���œ+�w2����T*$�G�� ����}'��!���k�/n�~k�Hj��V���j�`��G�9�j�d��J¸)��ݲ፰]���Q��'M��E���ptq�|1��b���l	q@�$�]��
�C9�����9�j��'&�����XF�؜�i�!� C`	�>�(sf��ѥ�3V����5;�:qN�&�CDc�f��"J%����fa鷉P�"�a��]�G�6���j���}�م���xA��6Rµ39IW�שW�;���F7�6�ֹ�⽈��b��m�%(AM!C�V����X~eAXB�����Ja�d4ou�Ld9n�n£ B\'��{?3̓��M7	�	�`�#-��s������`�9u�<y�~fU��u���?��N��dm�U��PiɲF��T�y���_�f�=��!��ϙK�ϝ���$��46�n�k��>�@K��ߤ_! F�e�̟b�6E	�UY���i��1��5�|a�t���9�$��B���Uʺ�����s��*|q��Qws^��Q�W�$�,g$�4�������$  G��<��%+5�*K�Pr��q�3��d&��A���ĕ�`�c�!�D��kgC���������3
	�yL!B
���sdc�tTGp
�?~�w?��S(7G��\��'���`9�Z�M�g=�68aɷ�z��l�4��5w�XAi���9�E�6��j�%��&1�ۖ���W���b�!�w8yTAҧ?&��ߢ�F ��GT�xxi�Wz����3�,Geʓ/�dp'�
�M�<�M��p8����:䂌�a�7���I�8{a��ͨQ"���DP�_Ny�_������8~��Q���@C{y�h�@�!�~I�jE{t�����⣏Z��tjQ�'uX+E��[�rc�� 	�?���R�x�103l-��3m�����Dp<.�Ul�C� ~�]5mм��ݓFk3�2��_G�i�?����j�d~���ӱ��=���e�I�� 6�[�5����j�<6����#�wU���N$�5AF���K�c�H��,r�#r�2����a�W��S��Y��,*����1��Lu��B�f�oTn��2�\�e�����XH�;����Ŏ<`N.�q���L'pEf�U~O���G.�mvA��.�$=�ȇT !�R�4������h��㒎e��L���	�o/i��m�c�en���	MA�{����K�:,�#"��pXm��6��r�/�3l�<��w��H�4�S�ҟ(4��!��t�ѧ�1�W�p�ݠ��HN����ы$_c/B�}"�D*�UKQ8����e*?X��(q1�K��I�z�I�tM���U���9 ܖ�E�u��C�Z�~~sނ�Y��9¹��gB�/֙����.[�FخW�9/T� 3������HO)v��t�#\��I �Y?�)�ϊ��̌iU���X������7��l�J�+|'Y�Ѳ�����T2u	�	d��y6�eJ��|i$�]�/A��H�{�$v�ѐ�*�Z�����~�|2��Ѽ��X[u���J9�!I�jW�y�E��djn0��l��%�˿V�`=a���ެec���,r�݃!���I�tZ�1�p���Ǵ��G����O�t��h9J��6qV峒�n�e7R�L�K�s���/
����"��d�w?�A�VO����#̀��NV�{쏅�nťZ|�Mã�0b�� �D���q4�pY�����Rj�-�����{�ڔ^���N��{�q���$!����ݠ�i�H�w�k����y����Ì��tV�:�
fCjz(���a��?FF0V��[���
�;Xb�?�˘�b�Ѵ~CyI���,weޓ U�hcy�gI�(q�=�[^~��M�� ڟ���<�O�vΩ��l_c�с���G���8CW�y)��9���G.��P#�*�4B�I��|c6���%�������hH�gC̹��bX.+�K��\�0Z�)|J���E��JmΒR�#c��K�	�T�a�}�����Ϋ
�������?^60ȃ��pl�+CP�9=�+\��H4��>��oak��&��[�{�m!￘����ə���6���hJ95Zxս�^b�Q�T;G�Z�y����5A@D���֦Vn&�Mv=h�q��	[�z��c}���+����A}�m���� ��������4D�\$5��6���ty�	�J|u�y��ow�~����Rz����c{�W�p����=�S꺓�I�i6H���Z�C,f���t1���]��@�Vh�6�Kȹm�x��4�㢈4��؅�q��r����ϒs
���4J�H_~�����
��A(f���լP��`�&Q_�A(O����+�"��ٖ�:f��u��npx,����߭�h��`r0������}�Ip�&$)�f���eɆF��T}c���W~����bz�gb��*Қ<���>�}��Ϟ�`¦M?��.��vd/d��+�W�t��K�s~y�������9���w"���oB0��F�;�Ku�x=vQ��	ڪ��}�� =_��Ѫ�G3J��P�h@�>yU=� s�Bꉷΰlg��h꥕Ce��^� y���I_�.����"���i�ƶ�΅~;��c���+.3�r�]�A�H=�XX ��Ԭ����71�� `Gm�&�b���9\
(kV��������d`P5�/Y!wS���ScE��$oc&U�8�UR�'�Q=e��>��g6���^� ގI�l�g&[�\i���f�ຐ�Oƿ�Lc��DLM�M�}���m�r�m3f����=�����o!�c(-B�5�/l�n��g'R����U>���Z�JU�$:�k�?)�ްZ�O>��1��>�(a�r�~�>������|���>�7sѺ��+ ��V�O�SE�<?�D�һ��#7ŗ>vڣ�Jh�6�n�G!�>�(>g�񜫢�A��A��"�r(G�� ��6�.��{[0�Z��s����~�BR���
��'8"���O	��� �?:�+�z)�(���%��{Ӹ�=��Փ'�1�� ��(of��u���9�e�)Ϧ�жX��ɽ�Ʉn�TcGQ��*\"3Zmڿ�6�n�To7F�:}�}����TDg?�-��I�(I�?�%�Z�ݏFc��V���Z�D��n�0�K+�����ӱٶ���p����Kn'84ȃ��# !� p jpc�zp8�Us��4Z1��|uٯw�r�G	n�x�Y�j������������#p!� a�#wUc=�O0>��o��	0Mr=�q�uԯ�V|
��O��1ԗ�$UV�����dR��yy�ks�g;eK�w�h�,����||ل�������!� �X8I>mT��&Ǉ�E��/sdr�2�n��!�Qr`�ֱ8��@���$ ������|9�M	��L�9H*
�HڏP�p���1 Y�׼y���� q�O3x�`.��<tX�&�$��<�\�>M���E�y�tڮ���	p�ݟ���Zh����p``d�:�],��rin��#o��a��n�s�C�Vچ���L(��󅋿�/ ��p�&�UYK-�M�����;^P"L�����c{Q�Dc$� G�wZ�PZs��i/��[�|�a�A�&^�w� ��ȕ��������-:��z��_@+4�K"�!�mS�H�}D#������]�����>��f��|p�2��u�KP�b�i�ơi;���j�˭�E��q�J��^5'�ç6®�v�^�@q�n��.
���؃����GE�<GH{����ü�p��yR�u��)C5'���*Y����o${�v���q�I���ly���fj��!�5�5�/�1�lM�ͧ-����U����8H��-:��w}ޙ�R�L�;r�3�6e�"������Q��
�'Z����c���R�J�d��b����<��Y��.��|sY��ᩰF�
��p�d �?h9֪�g���b��8�.M��2n��A�}��\�n�3�3���M��}�ޱ���BL��ڌ�',E+c�>� J v�N#6Z�̻�GwJ��v4�xt�sk�,�V��`��}����A/�=��(��Uc��׎������G6���cRP6Dil��M�L F����0��JUbmHn1�ra'��=�|CCVG	�	j�A���_mqk,�����u:�+'r���ט$!�o��u�<0)�&���1�`�Cj���{r����D�Ja�jx��"p����I��b���s�[,e��:�d(���WF�
��.�$z�[�;�ק<���~��z��1�l��f~��R���͌Z�b�#�`��_��}/��������PկA�g�VU/b��B�ɮ�dkBWD�2��INJ
�?(7f���H�5`��?q�㟏`p�n�E~��J�O2�-����U�$�������,Β�D��=+�X$�� k�D�u�}���~�i�������'���
���_7x`yg��0��QX}r�n���_��3>)�ԸѰ�f�cc�sw_\4Ju���G7��|Mwo"%�D���	?x*l��W������1`�<��t7_n�,e퉙^�;rGc��lO�-���<��Q4НZ�0j�i�ҎM�)ü�%��Z�Qr<���n��e贃V?�TKE��G��~y���v%����O�q����n�yr3$�ۢ������tv0�`s]�q�,HU�)~��^%����|I��(�o��CN9�C�8��Σ���>M��t�߸:*YF7�G���C�%|3Y�����E�w��:?�AStD����e�S��{'�G᪉5i�t�!��k:�k�v�ݩ�"��!ݙ�ɐar��َ��qӛ �s!�DyNݵ�	��t��{r�]�������oG���)2Q��+ԡ�@J��@�M�����(�� ��7|���:��/��	�~�XoB�F�~��/�����PH�����:��)��k#WaƐj�'v�̈�<\�t֞�[�q�b�ьd]�׍k���8�]�ɹD�M�M�����<V۔����9���B�2)& =�)�&�"�ᵰ=^In����ď�|1k�k[l�p/\$�xqڜc��!+]U��g�n�/�/�;+}�Y��͙�����F&�ۅTgi]p�0Q�u�_;@Yb�� ����K44�$��u��
�?0(,&צ�}۩���nhto�#	��l���7<.��F�J��k�N��Yw�(֛��B����y�0���7,.��C3I�·�:I�~v� � �G�S��9����*��8B���L��&@b��w�
�F`��1�F�)��Ų��}��� ���?Jy����7%�4A�Ht�2 U�f�p�.�Z��i�������)�f�R�E�|���������mp!�/.Vr('� 	��{PdrVl}��'"�a�[t_y��u6ߡ��/}|����%�cQ�DxZ�GH���H7ϕ_8��.�32�B�p�*V�3�9��v�組��M���ݜa��Td6֞#Ya��a�Ct	�~�p2�_֪�?@���H���#�/�}5F�
�?-�%����hd֋��2��5���1�G��m~��$�����:i��v���{~�����菖9�Wa�߁_mh"����Q=�&`��1��J��?,Zw��w�����J�vji���e��9���7)0��Z���n�-<ҕ�ؼ�V�F����:�++5����[h8�Ўp<e[�?B'�$E�K1�ll��'L����	��[��i�o��&�W�Y���饶�������>|i)`��{סFTj�%O_oO� ҿ%�#��@|���M����q�T1�lj��&�����hE֋&�*�]�4/Q��<թ����(��۾�17ZpD�!�,8J�BRlH��{��rT'��
Y3�4��a�I��|xڲ���7����&M�x�lQ��g+R�E���r��1�l���l������ڎG�DQ��:" Ut೻�u�_ ;x+Z�C�����(pT3sL݁�Jy�0OVwG�1���7#n��@gH���O�}+��H_`�	�T��y����(U�2ڭ���{7����`���'�����/��(޹�J�(<&�����G9ʪ�Ef� .={v�^�@e�.��O3L-�殰���4�k�h>��VƆ���#>��	0�h��3	D�=�i�X����I*=�����Hv���Pa�kt_v��0�]ֱ<zfZ�ꐇ>����CI�=]��_	���m;9��X��z�5�o=�)�f镶�B��r����$[@Q��4��B= �;r�;��U�G
��x=ک����{F�"��$֢OD�!ٔ��}��Q��Z��x}��Z������U�0R���;sk]�A���Ϡ(�E;}B����w	޾�Hp�<Q��v�^�@~�h���Hܳ���h��2�U����G Jl�����_�tQA�/��vT�xj�����>�(u�2�]�i�&~���.��������6�T>��ʄOdT#�څ�w�pK\A�y���Sɸ^-Yn��Q�DB�I�N�d=�i���V����ٹw�߸%z��jsb-��&���OTx���J�����,{e�S#E��0ol�w>���m�1-d��&�B�q�Ƹ�4SI�B��ƻ��)�"��� _x �3
���;
�X:���rڝ���X|�Z�Ȉw4��U����K}�Y�Ʒ�}�k7�D����r�݌a��Q�C{I�N�Lq��m�Հg�����aéu�_\�bKg拍�]���U���3-����O��c�v��oT�k9]УF����@�j��!%�
��g(�����2��5�o�~>���� v�����Z�CI�N�z��	�+��-�ߘ��
�ϒ�m��/W����4
Ȁ��� e�05�/5�/3d-�0�FB��4��h;�ѧ�i�n��n�&n�!����'�Ǽu���0p,%��<q��"�У,9UI�#�`����<L)�������^��	�Dx<(W����F�T�U=kV>�XB>����)�>j��9�qt���]I{�w���Tz�[�s�����O��a���g5`�����I���oq�gqҜ2ٚX �'lЭA�n��b�Q��M�M�M�͗-��O������xz��u��? ( &�"�!� F�X�xEgb������Ʀ�dca�aNrd��D�~}��A�:�E2��k�e�b*+��֒�
ϓ���/*�'b�ъ�_3@-�%��\�/N����y� ��\G��?>�(F����)�&�"�!��N�h=��􏅇��sγ�Fw�u/@$#~��@b���POD}��v���g�{nh:K���Χf���4,=Q�Ii/� �B�$x_��Hh@����*�{�u�_�7(.��B�I����j��?d�g���G(
���9���G+J�O�9ɧ��h�I��+���l�J��-�%��1�l}���w�������b�n�|Y��������&��xl��=�����j�4&�
�O�:yV}��-���缮�<�g����d(J]�Ъ�;z�[Cz���pq�O"��0+J�=���vߩ	�`�i���L��E������{�2���rHV���W�ي��1�,@%�#.��@YHα�LE��-�e�u�=�{�g�����(��B����DvF�l�
�4H/N�C}�ٮ��q�\7��*y�~Y?C���wr�%�9��<�
L�1���ƎB�9��k���dLM�Ϳ-�%��A�M37�$�����q��o���Em`����s�V�F��>�(L&��ݱ��@]�T��-�uY�r���q�B��xX���|6����v�@G/�:y��s8걷N��I����-�)c�&�O��YI�N�}�ّ��A�HB���^Ѱ1$@҃�$�ba��}�m �n��`�,���'y���FN����!=�i�ʶ��<i����,,���s���13)�Q�|W�:�W
�3hJ����L����O���w8��G
��	�r��u,�:�k&�b֑��B�I��͜m���+D����O&%��(5� �Zl=�O>�]�U��FĔP0��g�������V�F�
��?8(*��W���탑$�bdT�mѡuo#nݜ�rsꡄ5�;F&�|e�,�		���x|������
�I~�a�W��z)g���1��B�ɫ.�dj�W����i%���}����>�
�bمX����Y��ũ��z�7n��e'L"�ᝰQ�]�A�HK!�A���:�ʟ�tw��u�M ��u4`�h�p�&����y-�������H��ؤ�V�a(7<ؓ">���Wt-�e� 5�/:�+gy�߷�@V��p��|�`)�G�5���lZ��)�����i���y�5�R�?+_U�*���竂�}u�6��gu@D�<����݄f-6��b�fx)0�K[sg�g�ˁ0Gl
��86���j�W{��hk�*���9���U��*���N�R�b^OƓ*��'2�����[�u�^�p�jB*n�=ń�!�����WXl�˵v��JC52�%�^r�]��8Wj��ֳ&�����X�a�� ��|$�r�ݼa��^� sxr���@��:�ʁ]|�w�.�@ؤ]*� ��-ϋ������4�.��6}a����,����1�lKU�G,
��lj��S>��K�.�Vd�iW��2�m�Ն��=�����¡\��{��DTGJ��5���0lA��'���F���o3T-�e����;�|GY���P�_�)���tm�!����ͱܾ�@��d�*^,
@����ק5Vqt5�^~O��2�]j���v��tLM��=̱ݳ�*�y'&ϔ���2T���a!�`l�7?n�F�JΏ,\%��(q��;���%�PD� �y�Z΃,Y���)��ɲ�ʹm�U�NW��)FL�����4�:�$Bx�TJ3&�����E[q��wJ3�[,MW�<^	�k�J��\>��Xv��ِb��tB�I�\�},C����������{.�dS#��nH"*�<ƞUls�{�t=w^ѡ�?�Ds���FkU�G&����8@*�'���M:�϶��K�u����I�f�`��ǗI-���o����3m�U�
��~�F��͟-�%�#a��8�hh�����V�FΊ�_5�/($&�b�ѵd ���/Cq��|�A���4�nz�!�ǋ�i(�v��R���r0�j�W1Ƭj��+&�b��
���2�-��s򱽌I��ѬdE�K8�~T��Y?]���Nʌo�1�lB�Ɋ.��)���G�01ʛ����I���w�$��	@x�,[�h�׏��c��Q��N�LcM�ͤm�U�����M]�JF����~��"�!��U�:��_�3Α�@���?p�9����bf��r�Z���z�)�f�Rꅷ�|M��Ю����eͪ_�<=ff�}���Rޅ�[ x9��Ja��:U�>mi�_�<�v�^��xX����ݽ����Ll�A��KHn���B����po\�x��^��o_ft��c�f���q}�Y������>�w�Ȕh["^��.��T�}���Ɇ�"��NgSR�ś+guҟ%�#Q�2=�]Q� �ٝVE��p��-���]+�e� ��I��U�)�����Y���٬b���bGJ��f+x��Z�C	�~�X{B�I�N��g-����P\�����x�:�d�3�+('f�����W����#/a�=X�4�gL�m>��cA��ۜ|Q��b�Q�DN�L_M��=��ȃ�M��I㐋��_V2qѝe�`�ib�<Oi������x>��S���wQ.2��o�4�D�|`k�����ɹ�2��Zb���TGX
���2ޭ�E�{]m1�X��ߟy���=F=���S7���f�B�3/�Ȝ�N��~��a��A�W~��Z҃�����	�>�q��Z��$i�V���@��:�2�m�������m��ͨ^~�0�WڬP��G?�Y�������e����?(1�r�ݫ!�`.�BW9�j��J+׬��7I�N�a��y��a���ۆ�Bݙ߭�t�Ns{9����VYG=�۪t3�>!V�d&4�6 �De��m��40��D��H�}�!�C�|�mؗ.�򓐧������w��QqH-ad!6��u�.U|MVo�B���As!_i2R���
"�PUE0:\� R�s��JN~m��u����4[oCT	�~�w���O7}����X�p~�tJf�W'ƽ�ɇ.ڤcQ��z�[7Cn��=� �t��� i�)��G���`�|{�Ak��O4�|��$�RW�_�>�Y���A��'��Ǻ���8v��6S��gUPmi�;��	�M�=dX���ϧ���ѕT67E�:#ZP8W%<i�TC��qXu@kx0����l<}Q.��6�쌵7jB�����T3s�NDKu�_, %�#:�� wx��![W��|�w�#}� �)�&��XI�3���zYP�1�lGUʇ/�3m�պ�Y2�m���N�O}���Ž�	�~ژc���p����b���REN�W}ƙ���%����)O�:G#{��h�v�,�Y��fkM�M���ݙ���U��ȎXj+Vn|��d�dY�	a2v+A�Hr���Q��TkGWJ��_�Tn���bqm�l���@�b���-��s	���pJ��p<�(�Pz-�T����(�ц�^5����D��
y�Z�C>��^��~�b��������ô!�~2x����z��:���W�l}m����y���?=�)�����i���g�"���K:Qs��C9����4~�XD�y��Kek���p)������Wh����>�Y.+�_�s0����VB߯��a�(\H�aZ�_���+ i��fM��p}�OT�5)���9�S��h��+������ � ��vV|LOG�� ���	AH2 ���%�˺zB$&�ԉ��*�]R 	�;���:��?7h.��V�F�ʂ��(bf�iú��~9���w9ު�G0
�?�;6��8�>l��U��l餇�K��6�tͳ�O��������l�`$�k T��z���$���+�j���M��^�ֽ�ւV�u���ďs�ٷү��g�!�Q�BLCOKxD�������Lojdv#u�n'e}�aca!oa��%_0��fe%z"�B�}^J�:�+'gb����WF����,J%�#$!�`q�d1�lx��%�1��Xu)��"�a��M��}���Ҥ��F�ӹ���//d$cu��$`#"f�a'`
P{� �(,ͶdY3����.P�u�0/UU�8j�����lt��"/҅%�#a�P}��r�]���_���������Xr�2�T��neKLM������:�|vn7'���6FӋ�zfdg�/(�cvp�&~�g��a��1��~��k"�a���}���m�,ے�T�����I����c!Ѯ5G'{��i$v�,��=ioI��|r�ݒ��IRڵ��U�aU�5n�x�ŏ+'q�q��&%��C`8�P��=�[¿
Ǚ,M�ͳ-�坳����M��#@��ْ���~��0v���k<i�����f����w^�3ZA��HT��&��(`&�"�!�`B�	�v�$#���ɻ�o���߅�k�T!q 5��aCy\���`gP�5�oT5�o*�o^.���g��$̝c�W1?�KR�r���e��e�=��6֮��r�]���\C��; Cķ垙�(�g�i�:J�|<�������z��fS3Q�k>+cgQ��e�SE��?/h$�v���`v�}�q5bTܻ�l^�r����_�K�	���Hd�|U��"꡷ N��H���k6�n֔f�R慲��~�ڛaђ��Cc����xaڐc�t~�XD�O�/�W;Ƴ*��lr��ДϤL�U���z�?shֱ��B�ɵ��n�P��Wo7�#��8�I�ޏi�B�a��Q4��&����|OY������Geye�@s���4|/�C3��@�{�hyp��i�V���Z��;�r�]�����>�L���޵Pe�g�g����=oJ=������k>	�l���/,$%�c1��du�_`�jn!��7��1��p��+)�f�����
ֿ&�"��Ii��Gꋞ� y�n`!J�&��!wC�v��O3݁���ӛ:�k%�c&���q�\B�ɘn��0� Sⳕ0�-%��*��� �Z��9���oE䕈0�2v��͐m��w���N�I?.�Ë��A�F���_.�$X#B�ɀn�A.���U��ڸ���e�/L��U�x*��FU���u� ����9�*�'-⥱�Y����ʓ�y� q\�&�Km?l���:A����$;?�W(��N`�O>��I����la��t@�#��a�y�%�c���~�Xr������ �G����zpXv*�,�GN���rh-�f�Ǳ5�o�7'n��A�HV�����u�X����d?��V�,�ҳDY���7�U����_9�*�'6����h[V�6����V�bA6�GY���tM���_ݞS�|3�NA�s,�|�|���j��>֨fƒ�շ'a��ń��;ZL�[�j��"���E34�׭��G�A��~�is��0��!`�Q��W+F�J)�&���q�\���?ҕ��Gk���|�$L��3/m��w޽�I��k*����.�x�î��~�XwB���^� gx���[G�-9Ī�G?J��:��.�d~�XU)���P���u��-�e��_��s9�V����x�0�U�#���5'Wް��������^�qS�J'_6���E��_t x0�3��5�7Hohk��D�t���!-]X�	����`z�3wmޕ�W �:ʫ/s6s�Z�2&���C�"C~��^�q�R�Ōk�q�����<�������K���Xʳ�͐ ��
_��Y�i�{�튻�8�L�(���O2�퉵��l4�w4�pNN0�vxڸc
��x7Z��Y�B�I�N�LoM��}�����ե�VN��5db3fn�N�4Q�KL2��ҕ	u��0`,%�#?a�v�n�<?Yr��2-�2�ö�yF�r�7�0�����䃵���35��5�/d<���j�m���PvX�WL����2i�?Z;Ν^�nce�3�! �y���lv���q�F���o-�%�c���z�[&�b�Ѣ�A�HM΍����m"���5�"O��*�C�i)μ�B�	�>��n��~�Xf��ٕ��q�����P�c.8a����Oֲ�u#�]��5��K�4���}�����e�� e�:��C~:.����	�~�V/r�����J���S9���77n��DWKF�J�!�u5�_�vr#���A��8����x9�~6$��!Շ3eE�{��1?�.Ҥe�S���=�i������j�E|����8z������|t�r��1�,]��d��������'�H��#V8jo���zɮ��!<LSI�1u��7.�$OcL��m�U���;YC.�~��Į�m�e�3b��<~����(�'-�ZE�3m�����\J��T?w�Ǘ5���6�n�T~�XZ�������m��,�d��L[9{_żQ����{�g/'v�6��Dk,���dXB�ɏ.�$a�Pq�kq�,3́���ƽL��N�4o��V��]�M�j��*�9��/����LI���u�� 3J-�%�#a��z�3smݣ��E��ȍM!z�(T&�bڑ�A�H~��\"ԉ�.u�;��S�F�b�!
���}�����׷9���G!ʠo 87j��V�F�J�O4/}��r������K@=阄��yief�6r�>�OF��pH��Wpp��pv)�n�@�r�gG�2�/��ᗐ���C��ǻ5�oT0l:��7v��?7T
:�^�  �Cr�IJ28����A��J�4\/A�s~����� ʜ#�7��C���nt� ��ȏ��Pz�V��dJ��S�E���1~Y�G�mʩ��j7�Cf����s �1��K�.`H �sˬ�w�"��"C��F�k���=�`���N�Lxڽ�	���7���s�Im��+T�}�np�4���c�)�Ӗ�m���<�����x1ڬc��${c[>� ���E�:6Ox��H����ۍ��.O\�7��VCw~>F�0���v�uSg2eW��U����|0�2���f�nL�0^l]��q?;��SE�9�j�:���4#Ւ����=��6�n��s']ⁱ�LR����H�tp�C	�>�hx�����s9���0N�^��v�/�
+���%�E�����M(�������:��
1��/�zWr��Ċ>��Ý/�<Ci�����r�]���_
�g[mb����[� ��bBh�yM|�����7
��H;N�LGMʍ��c�+>��+7�e �����&�"�!��E�?}������?̒�hW'�̒$^P�� +�Q�~�Q�D�6۶1��[��,i���ə��5���:�k8j��ּf����s�D��`Џ;+q�\r�ݘa��U�wB6��i�2k��q���u"�Y��1�M��h!�>ɏ�BR�����v���`y��Cf!����A�|ݞ��g9�J/g�}���DE�*��=Z����w=ީ�F�
�?6�.�j�W)Ʀ���)���B���^�3v"��8N��Gʱ�D=�i�V�p�g�r�)��������
͎�1r1\	nD��8��C.8O{Q���DE�K/Od}�ٿ"�m��^jH?N�F��ɯ.�$kcWQƄ�J#0�+&�bΑ�TE�K*�g���[�~��I�g�(���� ��9�̔H���I�L����9�2�c�t��w��M������J�=&�"���6CaԽ�I���`1�,d%�c%��m?�Ts��jm��j��2��A�?�)�!�Ӫܘ�������ѐdT9muʟ/$4#oa�gt��PY`{boŴ}��̅+'{b�Q�DU�G/J�`?v����p����=P�9(5�2�-�e�S��=�*�����9�����K?Oh��ɾ��tn�T"@{�P J�{��a9'V�)K_����s4�q�Oq�m���+]�ݪ�#R���A�F�(E�@�
Ό�d���������lu��' "�d�c<eN�v�z�)c����PC�ꑂ��W�lAm�/�*x-ڥ���z��;ku�&�"�!���DB��Y���٣"��pF�
��$xQ	�{'���K�8s+�h�I���lm�է'�����_"�o�e�K�5Y{"�Ɖʑx҅��y���#8!�w �08�JQ�tx��*0��
��nѕe���c�Ҽe����s<���N����y�*U�vd��E��R�����r_�j����Xz���r�ݧ!��Y��9����z��N������&
6��A��B(p(�1J������R	Ca��n�sw]ށ�X@�9���G$
��8b���Z�C��^��;�+������������9����%��A��0Ȏ:nU��i�(��V�n�0?�-��֝������߬U'6"U_;q��5	�gPYdX#�R�}��F7HAL$����|�!45"�V;D���-aSj+u�� E�Fs�W0��D+����6tc��܀1�D��D�t_Z�uYu���tߨ�"��f�xwZ��Y��y�ʳ/�=�ߗ�����"������Q+[gCR�Ş�wt�pP1�)�-#ןL#lq��v ��A�L�0�}�K�w�-����[�����Ӊٯ |c�(�WEDfJ4l�����jwc1S`,��w�7Y^�3soZmN�;���I!$~S9u���w#�Z��w\�U�u�ݴ���)B��,�Իw6�Q���
F�:rY|��g���%�h��C$	�~��|b�ђ�U�Gʽ�	�>�BcV���j�W2���œ+�w2���
�Gbv�Y��)����yZ���B�ɿ.�$n�TA�Hj��V�ƿ=��a��M�?�}*��³)��ݲ፰]�Dѫ��KOsL��E���ptq�a1��s�ѿ$H#N��@m���N�LKM�M����9�%��Tq��ĲrF��ٟ"�!� C`	�>�Z #ɩ�تS����	<�o#T!�`j�6�nΔl&��Q��-C��4�q�p��]��xYڂ����}����U�7 ��-c��,B���^�3�T�A�[~�XY陶����7@��d�-l[,��G���y6,V�����`a�d4ou�'p"�dã05K/ՐV
|����@_:�B�=(�db���|~�۹�J��.�$u�_1�,h%֣&���q��N��dm�U��*��
�=�)���B�}�?��p����e+��͚�5��46�n�k24��T�ur��ޔhA'�s����<X�Ch[���x{�ȢPt��eA�na�!��K�>�j��a����Ѿ��﵀ ڬJS$��/]T9tR��(�E��U/KVH�4��,����2JOι�!��+J%�Qn2�&�S�4�?��o/��ֻЋ��l�g�'���=8!'潲ɍ�݄a�PSD�{[	%@Sdš�28��tT5Gp
�?�4v�^� kx��O������W9���Q��
*:�ZF���?ޛ'�1T��w|�,��e����O�}��_�&��$f�ꎔ��JŠ�_�+�U$~`��Xq;ш��F}KU�
�OD� 9Q�j����=��x ͉/�x}*���A�y�R��c8�U���욐�C�<���TM��Rim�ծ�r�]�A�3F�nU*�������%~��Sػ�ZB_mj�#��d�5
�?(=橲�ͪ��{��C(�nY7J���7�tO_L �=��U�5�03l-��3�����#a�b�r�5�F5mѭ��� ,ĝ]H�Q��SE�K=�i����l�)5��V҆����6�.��i�rx헕�(�RSc����b�0HS��hb�n"���O�0-�M�(�%N�%��֊�?� ��C�׮^��(,����8��f_��-�%�eo��}�K�f�����^K�X�ݹ���_(Hc�f��D}h"�A��o�!C��2l�j�G��or�X�"ӆ|���j�W=��o��*�Į`�O#Li��)�G�~S���G]�ٸ���K�>h�wg���5OW��?��/�9�X�&��k��@��6ޒS�i��Iq��`��v���}�Q�3������	L��ӟ�p6T�`b�N6�_L!����0fd~��	~���H�#'T��xMڍ�X���.\ؕ®[����[�99���G�|㯗�A�pG�˒��� a�@��J�9+TH�b}Ι����nUi;��P�3��e�Yx�l���&����i��� ��Ì��'�u�b��"uY��������E'+�[Jh��7�iK��Gr �Y���W]�0�|$�ʋ�,���ۻ�{�gyZ������s��`�+I�sj�}���"'j��I�����[�cz#���K��9���b&���d��R��~�{�.-��P��ՙ�����C�4��`2"Z��:yG����g�)o^� �Kj�?OX��8������M!�(9�\�cD]��@�d��m����_G�ẘ��o��ZG�jĸ�:b��2�\R���[n�<
�Q��(�hy�5��	���8l���N����X����<g��V�F�·�y�{�g�r����NH����Ó��7<b�`u�gI|,eT�6��$�Ke:��Z�w�O�~"K�I����'���6M���hg��a�Uuw�eQ�`�>���$��¹a�����&��1��^��>l]t�������x�6CK�u)BA�|��G^��F@N�n��8B�G�K�|fQ���-����60�3����oN5q�U��Q�ur�SjH���]�̙$��M���U�y�,�k5��q��6ԝ����������9h6�pM*aa�PlLP�3~�O��J|��?��jj,��1
��{�m�{9�����Ǚ����w�Q@�IL?5G.sҫ�}k�Q�Ts*��f����xM1I@��+�׎]{y�Mv1i�%��4���^&<�ЭH�Q����
l�i����E��������	GFǊNh<U��e��==��57�o��::��������2�h���Q8�J�}}���~]�n䏈�&�hj,���	�C)���v9㐝ε�@�h�k�^��1���e����8��0���J��!3X��׭�v�A�`�KB2t�Y�B�����9&V6�׀��eh��v�1Z�J(7)���ބ:Ց
kB�ڗ����_��;umi��Ҹ��~��=b���T[GC�_�>"�Va�Gyem�4�П*��C��w:!���BJ��C���+5�!w�a�+ӓՍ�q�� �����%��Ff��4��/^h<֧�F�[��K�ki�V�å���|���w?���	MI-���u��q+c�G�k��ԣ)��86Ԓ��@J���uQ�"Y#�
�ꔷe��lL͒c���-Kă� d�a��;�}��҉Ń�(��͗��,~��C"��Н$�b�]�A��BXt���ǈ���{t���)z)�&�b���K=9_\������z�*0p�f{6h#���v0 ��jj];�tj�W�Y�%hd ��#դ.eƦ��iI�ݙR�0�)"����oܒ�ոg
��?�7��DL��D����>�(`c�����E[���ʮ*r�  /S�9�]R78�n��(aR����] ~���r�`1�Q*:�=@�-#���g�>ݭ��6�m3��~�o�"��:ތ�<��Ȫ���m��s3����(	~݆$�e�SE�<q,�Z�����z��&%���$d�:�k�u�2�-*��������D��	�I=xK��F��>�|��L5���:�����+e���q��.4"���(�FY��q�B3�+J�4��[�5���kϪ���7���kg��t��8��(##��0��f�u�o�"}�蘋�񷇵͆�*�0ÍET3Gmʕ�YAa�'�U)
��`����wr�����tP�?h�Y��M��� $��D�óH��zR�N��r���F�A؆����������;;kkWW����wrx�u=RYst�,m8�X\��pp1��|u��"�o�rNX�O�z�rӣ�������ؚQd5)�,p�\5z]#�O>���Ihw��O"�!��Q�A h�g�M���]���hWV�Ȏ��Md��5&�K/�p,eW�:�d�q��_��9t|�������9��Z�18�!Bg9��f���ȸ^{i�
��>*��"�ZtE�ѓ��Gӷ�YbG�f|��ݪ�0Z�FR��t�+*k[�M��*�l���pO���w����l}�o5e� a��<b�$��	2���A�w}���M�[�qȬ���=�|������\B����54R�b;0�Gc���0T��v2ӮF�= �7@p��i�Vچ���k1���ߌ�aE��q�a�TCt	[q��>�����z_T3G�Ņ��c~Y�4�(�}D��TMn��I��V�p�'`�p�V�~�#Ϝ��Q��������4:��I4��_h1�"�d�(/�D�K	~��`�����������fHZ��u|�w���:�[n�e�%c���,}�ٳl�����p�q�M�� l8��3���2�^�}�*��I#A҈ᚃ���	�EO�mup��AȆ���*��;�t��'yl��^�N<����<p)�C���(�I���b8���mv���&�@�{�j��>���_����i��߄�EA��bRn�b"0����~�*{�w�&!�lU�����Xޖ���#�LfA��vL��m���tJ$�_�0��{����<�R�`��a��=$������x��f�{q�B
d9���|���@��R6x�\ D��~��g�$_��^0��1�W��i�1������qK�����$S6s�+�]lKt�YH"'5҄��Z:~F��U<s�= a��}�"@[��x5�J!ɩ���1�� �g}�芲��ᢄ�b��l;n
/(-��A�MQa[OCL	����3��JB]ut/{�]^4���/ $8#j�� f�\���<X<�;�Ԡ�_:�+'r�����T=���G{4�^<-)�[���1�j��M,p��vs����/�/9�*�g=���҂��1�����yFb��:��37m����C��|�j=�SM�6a�ŦB���T��z�1�lU��'~����Y����2�-�%����g3������߷]�!�N2m{K��	�����^k_W@�:ޫ G`
�?lv2��U�BTF��M?t�v���`h��2Eb���O7�/����U�A���	���p�*�ΨXX��B=�^$���o(�m�K�`��z�	x�,�������1����ϴ${}WvX�EE���
Dw@�'���L��:pjl��������)� K_�>
b9Ϊ�G5ʯ/$;&3�2�;��Sem*gH������ŋ+gp�5��P5cn�Z2���^�@oHθlCU�(���WJp�Z�:��
�>�(�ܘ��r�ݨa��Z�'y⚒�r��b��B2�J�F�]��2�!��:������=����:�+w&9���������4t/�k�9�jZ1�*r��.����S-��f�a�U�IO(�5X�������AM�%�ʓ>c@�����tPH�����C�A��O	F�}S9z꫆�.�(Fx�H8�3YJ¿� f��.ś$t�S�����r��q��]���+Fֶ����)Ď.�
D�OwL��]���^��?YO3�@�Ø�]��Z�C/I���lp��'����%�0I������5��j��&7����}^��D� �~�XoB�	�T֘f�ڠ��R_罣��>��% E�j�ck ��8�='v����)S�g�ۻD4�Xw?�K.���mw�A��M���/�M�օ�9�+���ݴ�x���ꅢcn�� ��OTUp �p�*�q����,UO ���Ş��xx%�-dr�wmj?l@�v2�� H��!rBQ/»)�f�R��;}�Y�̈��ۋЫ
�хU~5wp�~�H<�@PVH:N�� ɉ?��WK1O.�O��u��
�?n,V�t��F���fypc�)��$��Z�7Xk�����9�z��h;�m����G���A�9���0.��C}����:~�F"�a�4�FU*���9����/��8G��c	U��|�]�&���=z�hᅊ��A�q���ٷ�$N5ϖ�rk��w�8�|\�:�)�����@`�ֵ�ʋl�%��&�F_3u������Ŝ�hY*n!�`oz7{� ��{^v0lN��'4"�'�B[:7�H�}q���%%?IԪ��,�IQ�DxZ�I]���H}��H��>d�`c��0�c�}�j��*֧�Ͳ������&ޑH*ɠU^a��.�@G�r�V3}�}ݞ�]����#����
�Wo�I�za�j��B��u�������{��7�1�l\��G+�����ʂg�F�3�Z��:XZt�Y��Ƀ���j�v���sbf����J+�~KGOJ�VM�1��H��r|dZ��0�����3$-� қM7�k쾆Sh��� �K��*H�{�dr��ð2�����N�{6>����CR$ὖcqCL�Ddo�pI��5VȲDv��O����c��0� ��.��m�D���å����3����f0`U��5��BHn�eJ/�N��w�p[��Ps���@����q�Tw�>j��u����!��t�1�E�4>|��W�ٝ�с�X1̅ʯ�54O>A�iZ�q
]M�=J
��:�7f8��C?#���$�X� �4X��ʀ�y����w�:ɐl$��36U�ό�r��P�++���}�����T�9A��u:
\wzq���[�&�3vs<t+/�
V��Ѳ�|-1IsQ��'�G

�1CG�#���7#n��@U���?D�:(��IKr�#�~��y�Փ�fU��2���VįQr�]�A��WO��(�l�����8��L���C�%(<&����خm���4�#EEu2�(�0�\�g!����D՝R�<�P_4�A<#��QϬ���#l�@k�[��!I�\�-�Y���/�Kx�����߾�͙�\gA�_�y-���~fJ�셑1�ظ�YO�*m��L���8w@��V�,�y�6�l>�*�e��ꖵ��q�ޭ�sX_ B��y�7PlF�$|a���V�D	��{>٪����x5�m�Wf�P)��1�n�֞���Z�A�
���{k�������|�3Q���8phw���B����A&{S���Z��;{���@5m�}�����VR���X�������5�F����J[yj���ƿ�4`~�nGg�m��M�f��D_�M�(!��a�_�%�%X���q�ڋ�����Z�Aw���E?T(f����w�pK\A�y���o˿7+܇!���[� di�,��7�����>+�ۨN8��98'�E�&��D�/?hD���L�����^>$�6m��q!/Q�%kۤP5��bMo��i��6��|[Y�B�ɶ���lU�"���17N_�3nμJ�kF�H��n�;���T��-_�[��وQ���C ���IBg�Y��ӫ:�k(�e<��Վ�H3���3���E.��%͚"���)\G����X�|ԭ �g�iLq�������އM_�zI~���� ��-�u��^R�8/o��F���Y�l��6?�
��`S��ǃ�`���g�&_�3U(���@'�����]�_*��B?�H�?��<'ę��|�F��v�d�Do,����ٖ�n+�_0{�bw�}d-�eՆOv��r��<w�ڳ�E�{���kp�%������2���!���0p,o`��J>��7���`|�`�>�A���N	z���ĺ��\�t��PE�On3&�����p�YtzZ,�EI6��;�!B��hN�!SЁ�K&��D��Tz�[i�'������C��a��J�Ir0a������]#=�H.<��e��1�zѠ(,�n٧'�Q����܉�e����������bz��a0��k ziu�"�h�el�
�?|ng��۩�F����rt.�eoHu��)j�7.���T�u��j�~�w}n�䂗�V�����/~�fP'�ъ�_3l�`��M�b{N�L>���b�+��	{��}{�(	����h�s�g�d��N�C!s��������q�ݩu�k@VMp;��@b���}�Y�l���O�?d.'�քΡʠ�4k"�M*.�
�K�g%4��C<[����~��{��Q�rfo���Iݜ��j��m&�l���$
��N�|��+�C�uخ��$N���)���WF���-�pɰ^1�%0�է*����F�_��t�~��CiG����1��� �
S�x}
��X{��색.�4��G�27|����ɳ���heV�݌��qvU�9��C;,�S=���pq�q��|d�r��s̹]�G�K0���2N��M�ҷ�E�K�v�L��)|S_�}�ƶ�v�j%�#.Ň<M���LE���<�\]u�<=�f�j�㤂�{d��B�ˣ��nhV��B��:
�X	�����[�\GA��=}�e8���&�b���R�=H�y��[�Vq��b���:z���y�jУ\�T�R�����֓o��w�=6��
��H�޶Mj�`c̦��������
{dL�s��w�m��p2Z��9%ы��%�qF5�x<�^�!4y���I��I譍�9�>r�#�#�[�(��8�Н��"�	���
��<R���x�kz��8�%qe�S)���2�m�����Z�Ba����=�j�C���K�y+ �_�����-���-cܬ�&g�W�u�,�_�3Jh����Z����"��FX�38]��	X ��	�ʨo�r�'c���ś�����"ě�gR��͔I-%��Na�Pe�+u�{�h�k��ĔP?��>��œ�\���O� ��?8(*��¹�ْ�z�:0g�iĲUCW#iۭ�c:���E�KOu�Vk�v�lY���x|������
�\f�vH���{$c��d�6���'�dj�WƷ*Χ,B��o��H�Q��I�N�O��^��Ѝ�����G�3��7nКrcâؚQ�]�A�H�%*d���8�ӕ�#;��*[�u��<`)�&�"�%���J�.i�֙�۲�M�͊�5�/es'ԕ"\���^^w|*� �@Ug�b� ����a\��g�m
z�:�C�3ȫ1�lZ��)�����-�ӊR�$�_� =R^��a8�������f*�;��wxe
������-TJo��.�dt_u�(go�jŤ�x>��Tts��Op�WF�J�.�$I�N��|,��ʢ@�����M��$P��y��b��Չ�V�'ؑQ�;�{Mvi�&���j��MZ��Iy��|^3v�"�tr�]��8Wj��ֳ&������X�?���K'{I\�!���,̞
�e=<H���O�7��e�Nv�m�Ԕ\?�V��:ā��/�	��x�'��3X-¥�����R�-[�xO�k}x��<��O�3�U`�bq�]�Z�,���0ؙ=�靶ю�\sAݿ3��Z,�CA����0l�=�����&r_�$�-��;�|GYʂ��2��}��_>�h9�����ᙰR����{![CX	¾�vޞ�$L~�%O��#�l{Lp���v��tLM��x�ߤ��K'3ω���_e���Eb�2IV�r6D�F�JΏ,\%��(q�7���3�"=�V�)�
��$���{�������!�U�x��4Z(H����6�n�Tt_z�3X�݅�� Sxڻ#Y$�Pej�?X�7�M)��ZP>�%����n�v�;��F�0g�ӱ��`������{j�(
Işyf4!a�u��Vlz�"�p?j���f�Cd����`k�j����o	n�ol���I���rJ���2��u�_�2�-����i���f����^N,�%�ND��ez?�h	�ę�!�f�vY5���W2<Ƒ���U�2�ߩS5�aapo�.��� [���nmnפ�tU�V���~�|�%�I㜒m"���`�
�j��"bʬ@��+&�b��F�J�2�-��s򱽌I���� �=a�o,u��<r�����?Q�F�%С�o��4�%���J�|ˑ���j1����a��G
��<ʍǹ�2i�����k���G�U��굷�<I����+��0w�u��H�:���}������?�9�﹏bx��G4�H���_�l�4����W]���翉��O�5���4OoLwX����ގ�[iu;v��-��{�{#[a�Pi�P�?���9h��]��ݽ���^� b���_@_]{������aE\�x~��S���?hp��g�,�3��I9�������2���(lN1rF��/�_�A�
Jz����ɜn��dgSR�ś+g<��q�bXS�!:�TT�!�й��>ΨlF���&�"�a��F�
�j�`���̧�ǭ��0ˢ�kmܟ@5?\��4Z�C	�~�X{B�I�N��(}Ҹ��`Q����v�d�t��+('f�����W��ژw`1�st�q�@1�,n��C'I���.��H�Q�DN�L_M��>��֕�d��2�텵�|5��k�!�E@�<Bi�C����\q>��[o�~q*5�(���N�v<#��¶���~��pb���~GX
���2ޭ�E�V�I��ۘb��3d"���v��c!�Z�B�J����d��~��a��A�W~��Z��%�{���>]�q��m��@��$i�V���j��:�2�m���X��O��m�Պ�2�-�%����fM������^Ҁe����lO(r��>���m�&�W\x�j��8���S��eL����N�a��y��s)��Ჹ�d��ʼ�;�Rh=b����G�˻q5i�9-f�ycb��7��o��}"��D���8��L�l�+��l�������;�u��P4/{dH?E��H�	UY5k'N�U��
3~O&c�ݕ
&�

P^%>�E �K��5p?\(�rʝ��4[oCT	�,��{���Q*}�غ��V�711j�Wƽ�ɇ.ڤcQ��z�[q<��^�r�\���DC�u���^���+�8y��>��O6�.��a�PM��}�Y������=������8q�w޴7@A=�&�V�%��L(gI�����􁌄�ct�t`P0,;e�S7E�4_o@7~���X�sG5n�Y�8����r[hV�����74.�dDKu�_, %�j|��T8(��S/��9�j�W/F�
�)�&��XI�v���!8z7�1�lGUʇ/�3m�պ�2�m���U�I*3�L�����y�2��kW��-XF�����D&�: �o3ʙ܁�q��qS��>^�Wy��%�r�+���L?�������ۄ�t
��B|:&��m�,Q�S9c3�HX���Q��TkGWJ���3!��u�0=�)���2�-��3-��s	���pJ��4y��Pzu�_����*���D䟿,�I��M,�� {����r�J'�Ր�����ԡ�F09����z��*���S�f}e��$�_�<y���?=�)�����i���&�"��0H,��C9����4~�XD�y�Z�$9�j��<f�ҏ��N|���G�g�}W&8�h�2v�Ǒ��OL6��ݴa�P\�x{Z�Cc���,x%ڣ#��pz��t}�Y���X��n��m���̡����A��E��_{@H3N��E���{{s[���F��mNO`������2A]�n�H�2��?7h.��V�F����>�(f�ҵ��9�#9ê�dy�o`�c�/�/�NǻH��$�剳��m�����xL����^��n�w>���-q��h���钷 �Y(�O��Mńf���$���z�3�S�=�FZӆL���׷ؿ��[�b�=�
HV_��¾揑htl'^l!�D%tRg/�}apXd��%cn_u«rpbg8�D�d2G�y�,znH����WF����,`%�#$!�`q�d1�le��sm��Rɭ
{��j�c�m�*��M��}�������������//d$cu��$`#B�a9ne4e�o�0m��.H&�ɀ�DIa�d�J\�8j�����l1��g5ү%�#a�P}�\�:����K��ɨ���ٟJt�!�C��LM�n�����Fe7ܢ�*���zq%o�%�],<�f<�%Meғ%��1��~��k"�a��V��z��n�s���&�����I����c!��dp\5��(t&��P�:(�[�9*ܞǵ��MU訌�k�0g4Q�:~�zu���"6q�q��Ta�Pj�v�^��m���_��m�����T��@��@�Z��痓��8�R�U8�K��%R�����f����w^�@H��HIΎ�\u��}2E�w�u�k_�L�v�:h�ׂ��l���Ç�b�A*g3��(ae68���`gP�5�oT5�o*�'b����\g��1��\'�F{z�`�6���e��e�=��6֮��r�]�Ȉ��Xv������&�"�a�J�|<�������9��ni�hp+~g��m�R��\g)v�3���8�S�y)+^А�{C�w��"eV�Ih�	���Hd�|U��"꡷ N�J��J�{��.S�*��'����^�uĺ�#����[��ta��,A_�6�TPt�|�f�!w��o��(6��È�����u�z�]~?$nڱ������8i�EF��Bw�Dw��	�s�xmZ���2�-���=�)�&����|OY������,?e�6���4l/U�3z���/C�+&V��[<���	��;K�3�@���;���C�����K{�g�?����0�S��爩}:.�}9F���/,$%�c1��du�_%�#(!�;��t��?��~{�(��翹�
ֿ&�"@OH��I����o5�/'6g�a��GN�(όo%+�ܑ=�WѼ��8p�&kԬ�y�vB�ɘnҔe�S���>�hq֜f���e�S���9�j��we䦥0�M$�Ў�	�A�D���d�s}�١��A�F���_.�$X#B�ɀn�Q�܊�	=����Τ-�fw��*��w���:�%���J�w�o� 7����w^�����-�k4�0�XO84F-�����pd2]�	��@J�
\w9٩����lK��g$�u��`2�-�%�c���~�Xr������U�G���
�?$(#f����CC���^bo0�|ƨ�h�E�7'n��A�HV���Z��0i����>�(z��J�+���p}���|�H��ϟx�$�rd����-R|�F����1�,Oe�-��3-���C
���S2�I�n�&�X���b��v��h�Ǹ��dB�J���� 's�]�/��a��N�g}ҙ��������K:�kY["��T��db�Q��W+F�J)�&���q�\M�ͨ(��ۅq�d�i��f{(�P�$X����Z�['��ǰ�%|�����~�XwB���^� gx����79$w�E�h��m�!~�EU��|��n�����-�e��U��<j�����=�i�u�$���(h˲�������B�Q�Dt_@2���E��\15x0�3��5�oT?Gh
���d��Z�Gʻ��,)�QP?,���'UJ���ad]�$@�3E���A�[*��(��"�H^���'\�}������T=��ʄ��o���n������U�[��m�i�`Ͳ���}�[�a�ᡟ�O2�퉵��l4�w4�pDq�\xڸc
��x7Z��Y�B�I�'�%;�L�4�ו�����p��Ο�uy!ig�!�2A�oy.&^��ȞRgh��u!h%�mv5�Q:�[�4qU[��u?�����<P)�&�b�Q��H[N�LY��탵���35��5�/d<i���o�k���L9=N�	����>�kWuƟ*�'$"�a��Xd�S���#&���q�F���o-�%�*D���;�>h�7����bM΍�]���(Sf���%�c��dz�[G�#)æ�!�H�0��(��p� #�Ǎ�ϒ@�����P�8bFU��>ڨc���{'[b�Q��R�E�K�|A�����뜘0�N&�w{�e9z��R�E��	�~�kr�]����V���Z���9e/��
H��z�N8�_�)<����`��<����(R�m=+��&��u]�9��>x�k���S���z�!������m�Rw����Ef��cW����.1M�u�\�p�QQ��(M捲ݍ���Q�R�E�KOp=��v����tp\0�8u�0dw�aHyKt��8��D[��B&}������9�*�g#R�ŀkr����6_� 6�}�[f+e�v��S��	�[ w�Ǘ5���6�n�T~�XZ���������i��p�S��O_vlO��C����4�>}4=E�?��'2b���1G��g�jh�Pq�kq�\f���e����W:��I�i ����M�M����y�Zփ&�����/����2ÒN.v8h�p�fn$��/�^~6#����T&�]ˣ�I,m�!~&�bڑ�A�H~��\R�Řk�u���6�.�d}�Y���)��Ʒ���k��B��#E3*j��m��� z&/}��r�ݭ���[r�݊��eOKp�7;Z�D=7�IU��6`��5��<t)�f��z�j	�g�$8��ꗄ���N����{� Q0N8ǪC~9��PkDKv�^� a�\)�%s|���A��J�4\/k�s~��Q��A�HSN��XA�6��E���~n�%������?`�&����<��B�y���t|Y��9����/>�afष��!AI�~��U�dZ7�x���n�;��>Y��+�H7����'����
�>=L���MԬ�6!ߋ�U�G>��_�:�+"�a��Y�Q�5��º_̲�`������Yy��mB��I:;5�7 ���D�*jYd���󑀸�ՠg �5��0;l+U�G2���F�;Cc8+��U�F���I/U���5�/�0Cl	���8r���W��SAE�E9�+�P��@�t=ј^����'�=��6�n��s']ⁱ�LR�ŝ��tZ�C	�>�hx�����s9���g�@ ��v�j�tc7�P��&����ڪt��b�Ѯ�DsK]�A�E��8_j�6��̈́>��G��LF�nM����7�U�+��_
�?(2���ř��u��:�bIg/F֥���7 ��H;N�LGMʍ��1�lSU��+*�g���ϖT�"�!��E�?}����ͬm�՛'!��pF��"/�W�2�W�A�lި��I��os��ԃ��V�
�L�.lj��K��2�Ҫ��2VQ�U���77�>�ј5���Odv��\�/ ��"���|����p�~��(r�]���hR�����v���`y��33m�յ��9���� ~�@2�-���C	�~��xR���HP�wx����M�k[�v��'�g�ꯧ�m������He��y
��\���Ho�'���(�z�<�âղ�����X�T�0Hap\<��v���{t_s@�1��DE�K/Od}�ٿ"�!��D@H?N�F��ɯ.�m%*���g[脉;aUj�'�ե~E�K*�g����1��A��[.�d�B���j��)�̉^﫭Z��	����j��;�v�^�w��M�ϸŹ�J�,n�pӶ��H����˲Y!b�~!h�-q��q�\q��ha֐f��u���=�)�f֒���Y�����ʢ�41] ��aSaPb; �B" �u�07l.��W3F��ů+'{b�Q�DU�L�].x����p����+1$�V//��w�V��_��=�
���諎�s��R���~&IZ��ž�1 �  ^:�.K,wj�t��lpR��0)S���H�'O�0�]H�j���"ȹ��7Kϱ�AN�G�L{M�M�M�͘m���������lu��' g�i�rVRf�m�x�)r����;Cз�߀�|�oE(� z� 3x-ڥ���z��;ku�_&�"�d�� �*Z��֌���*���1�I��G!`��i�u��� �9/4�����"*���iF���ěP�o�)_��;+r�]����R҅��y���#8!��$E�0J��;9�j�W>��Zƃ*��"򡽀I�K��$��I��>i�������f�=D�})>��P��W���(��,h�����Xz���r�ݧ!��Y��9���i��W������(@{��M�<=O7�c��ݰ�=�F%��/�W6���r@�9���G$
��8b���Z�C���/�O6�s͑�Љ^��L���t꣜�i��F��9��!MK���i�V��:�k=�i���������?�׻Y5xm*1P*q��8�nJP?D(f�R���K{O[L�����v�q.on�WwF���_$ #x!ڠc �4z�QM/��1��'��wa
c�����W��D��VUJ���|��Rw��xD�-9R��:Y��y�ʳ/�=�i��ݦ��Y�A��ﮁe2ǆۛE;'[�53TEc�l �f)�l_G��yJ��
E�8�	 ��\�w�!����Y ���������'Pd�-�#SDT\1{�p
����|~'S3��i�oE�};;f�S���S!��k0l6���4f�R��{[z�[�r�ݶ��\|��b���KwO^� ]���
Y�s[~��)���q�m��eM���8וǶ�Hƽ�[��u7ԇ�f�!`�����yP�3;���E�v�Ұe���<H)Φ����k�`��	$��|���j��5���9�j�W*��³)��ݲ���	���2��4
P���� ʞJ�1]L$�Y1t��j���$H#N��@m���N�LKM�M����9�8��';�����ĝ�p�o�e'!]�6�m'o��ѥ�CI����{5�o#T!�`j�6�n����x��GC���*�O*�f���x�֘߳�8�����b�9��/��9S"��X�<��<�\�������ti��f�(L-D;o(����_@xC����`a�d4ou�'p"�!��Tp\:��wr���Q�W{F�J�O%�#-��txD����M��j�v4�t�qa֣&���q��N��dm�U��*��
�=�)�Ř����,����M�îҬ�;ֺEWo�"�AwW^��Z�"���_< )�&����xKZ�A���
�άC?��+=�Lj�s�#�a�z�/��-��׍M֞�����3�#a��{ws^��Q�F�J�O/LaA�8��b�ѡ�@CH	ξ�HuΟ,P%�#+a�Pr�X�9�[��n'�G��埖�D�g�7�T��kDOH���̳��-�Zn�{/[dSy���#7a�tTGp
�zr�u$��R!T���!����4_>�?����K~�X\���zқ%�c��G+�;��=���V�I�4��U�9��(f���թ�º�6�n�X#rF��XsB�ɑ��DgKR�E��7*Z�Fiw����t��\)��'P�r<��5�Q��T��C/����!���иG�u��}��W3(����&���DPZ�}%�Z钡���p��@���}<`o�*�`�u�HC�kDZ1���������5�o;T+GgJ���7�tO_L �=����z�03l-��3���̲_f- �Y-��&^�z9ݍ���F ;�� 0�ޙI �1��S���H�-?ҔV�ȬκRq���r�g�� 
�K�x����j�<6����j�W8���!*�g���O�0]���O:�bS�%����)�H��W��$��|y����1��Lu��-�%�#Qg��8�]�|�����X\�X�ݹ���_( &�"ʡ� D8j�W���K3�!?[ ��(i�i� َ[:&�p�0�����$�_4쩪��*�7���J�O#L!��m��eX���L�~����_�>k�fF��x
YV�ӌz��!�`A�d>�hUև&ڢ���	ŚO�#��< ��g�C�~����0��r������G������l-T�3t�S0}�]M?��}��0d T��3wU���N�tC�F�0J�����=U����A�pj��N��VwYނ�Y��9��ŷ+�|B�ɒ�մgR����p{\A�H}Ι�&���,`��@�6[��'�&@=�)���B�I�NΌl]���(B������#��P��[%,r�ǒ�� ǆ��g.8�IyHλ,Ke�S,��3;m�U�G��_L�v�zx����&��#�ֳ�6�Jrq̿���R;���On�"6X�kW�~O�
��+8'j����Vʆ��3?(�F�$μlI���,r�݃!��R��;	�~����Ւ��G����E�n��u6?KǵyH��~�&o�#�I�z6��|I����q��O!� m��b^M��N��mģ��^P�-ĕ��!��Xp�9���w'^��A�R���L�3�a���?�0�˺]ଂl ���<���N��{�>���&*�������=�)�&�g����fX½������c0�a;�g b9jC�aD��"��Q\w=M�����O�o+��ږ����!���weޓ U�0:�+L�{Q�8���o��O��.̂����P�xǫ��1lMt��������9T�u(i[��k��4��_@9�*�4B�I��/,���
������~H�tC����E^*�B��p�3J�N}�� ���HaΐlT�w*��B�[�=�6��1��r�ܨ�͠�����ńkWsF��ѯ$D#Ka�Pl�w;^�@GH
��~��"E��'}#�V�|��^�q�md����ə���e�SE��;kZ\6���tb�Q�T;GkJ�O�~����> D��8蔸G`%�Z~ y�-��*q�z��c}�٤b�Q��F�J�O>�{	�Ѳ�M�����_���IT��<%��6���ty�Z�09�*��vt�~����)���2�-���y��39����?�<F����k�b���Z�C,	���8}ꙷ���
D�~H�!�O˿I�&��>�ͺ�/�Y����}��d|q˹����;D��g�q�Or^~.��B�����k|E/�׽٬3C��i�o�M8o�N��Ǜ��!����D1�V�=��;<+i�V�����:��'7b���T[GCJ���0u�5�/<$)�f���e��
��3lo�������4�na�.j�x���Q���p��/��ٗ�p��
=��?��"Q-`��(�G�t��K�<?;����ʸ�/��%g��MDr��[�<�Sc�u82�K�0����o��BYV��Ѫ�G3J���;�{7[n�Y����P��>[��7���C��^� y���;�}�Y���Y�i��բ��")�w��Ƶ)P\�7��� �Q©������71�tE�K `<)�&�'���JII������m� !G=�jmSb�ћ$ScE��$ocT�tj�W��#mEk��i��3w����o@U����q�Y
�2(��������&D��Y�-��7.��C��t�>�D"(�Ɲ��P���Ͱ*o�t/go�5�KV0w�tՆ"s)����YT�ݜU�0�#_�/T�9(���H��>��J��>�(a�r��q��Y���,����蒀j��'8ͻ��!,Wøx��S �!<?i������lz��#v���`h�U�/��j�xVv������ ����3�LxZ��B��8�k��:[5,�)��q����:�
9L���_��.53��� Z�
��
�?:�+�z)�*��������y��Փ'�1��\E��(o#�Z�'��E�t�$�?l��Ǟ\������ �\��;ZIU!�Ц=6�n�ToGT
��3����x]a���
�xy�rIc��H�ВE��O����u��\�v�2n��M�M���ݖ��V�����Xs*9Y�郜oe!�=pehp�"7`�N`��%=oU��9��w�`�c	RX�5��&��ᱰLL�������Vepg�a"�p$q�sq��a��@d~��O"�bҵ�{ z�M�M���Uד�+]�Λ��dt��1-�Jl�i2gU�W�i�wȭ]��)2�������J��!� E�0?l(�q�����Uk&6\�2�m��f�w4v₄��j���H�ɥ���F	�W	��h�8~gF����"���#	o��8Ŗ�� %�U4e�_m�!mN���'��!��#N������鑶�N�Lr�ݝ���TXB����p`1�,e�"��0\,��s:���t�H�=�&����[��0}����Ӄ�=��f�3�^1 )�\�v�����iXE����miX�ncKQ�DlU�G8
��:��8��S�P�kG�t�,\��m��������V�����8:��(��0�Wc�/�g�T�}oβI����ȓ���Bӥ#!��|p�2��u��1�,I�Ρi)�ĳe�����EY�#�R	��M8|ݻ�b˄�v�^�@q�n��LgMҍ�������Y�>_|��C�����&��u�:��L` ���:���F�r>l�!��4�gN���"7���^>���0�XF�2�/O�e�k!���yʢ�ޑ�@�"J��Sg=ժX6z���U�\�~�}�n�5X�����Q��^�@wH��\L��m���Z�_�>RDstart.put(eChar.curCycle)
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