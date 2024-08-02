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

    eChar.plotIVData({"Add": False, 'Xaxis': True, 'Yscale': 'lin',  "Traces": Plot, 'Xlabel': Xlab, "Ylabel": Ylab, 'Title': "Forming", "ValueName": 'IV'})
            
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

    eChar.plotIVData({"Add": False, 'Xaxis': True, 'Yscale': 'lin',  "Traces": Plot, 'Xlabel': Xlab, "Ylabel": Ylab, 'Title': "Set", "ValueName": 'IV'})
            
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

    eChar.plotIVData({"Add": False, 'Xaxis': True, 'Yscale': 'lin',  "Traces": Plot, 'Xlabel': Xlab, "Ylabel": Ylab, 'Title': "Reset", "ValueName": 'IV'})
            
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

    print(SweepSMU, GNDSMU, GateSMU, Vform, Vgate, steps, Compl, GateCompl, hold, delay, DCSMUs, Vdc, DCcompl)

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

    eChar.plotIVData({"Add": False, 'Xaxis': True, 'Yscale': 'lin',  "Traces": Plot, 'Xlabel': Xlab, "Ylabel": Ylab, 'Title': "Forming", "ValueName": 'IV'})
            
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

    eChar.plotIVData({"Add": False, 'Xaxis': True, 'Yscale': 'lin',  "Traces": Plot, 'Xlabel': Xlab, "Ylabel": Ylab, 'Title': "Set",  "ValueName": 'IV'})
            
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

    eChar.plotIVData({"Add": False, 'Xaxis': True, 'Yscale': 'lin',  "Traces": Plot, 'Xlabel': Xlab, "Ylabel": Ylab, 'Title': "Reset", "ValueName": 'IV'})
            
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
    
    PulseIVDataPrepAndExport(eChar, SepData, header, eChar.curCycle, MeasPoints)

    res = {'Header':header, 'IVdata': SepData['IVdata'], 'Vform':SepData['Vset'], 'LRS':SepData['LRS'], 'HRS':SepData['HRS'], 'ImaxSet': SepData['ImaxSet']}

    Trac = [SepData['IVdata'][2],SepData['IVdata'][3]]
    eChar.plotIVData({"Traces":Trac, 'Xaxis': True, 'Xlabel': 'Time (s)', "Ylabel": 'Current (A)', 'Title': "Forming", "ValueName": 'tI'})

    if ret[3]["Name"][0].lower() == "i":
        Trac = [SepData['IVdata'][1],SepData['IVdata'][3]] 
    else:
        Trac = [SepData['IVdata'][3],SepData['IVdata'][1]] 
        
    eChar.plotIVData({"Traces":Trac, 'Xaxis': True, 'Xlabel': 'Voltage (V)', "Ylabel": 'Current (A)', 'Title': "Forming", "ValueName": 'IV'})
    HRS = eChar.dhValue(SepData['HRS'][0], 'FirstHRS', Unit='ohm')
    LRS = eChar.dhValue(SepData['LRS'][0], 'FirstLRS', Unit='ohm')
    ImaxForm = eChar.dhValue(SepData['ImaxSet'][0], 'ImaxForm', Unit='A')
    Vform = eChar.dhValue(SepData['Vset'][0], 'Vform', Unit='V')
    
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

    PulseIVDataPrepAndExport(eChar, SepData, header, eChar.curCycle, MeasPoints)

    res = {'Header':header, 'IVdata': SepData['IVdata'], 'LRS':SepData['LRS'], 'HRS':SepData['HRS'], 'ImaxSet': SepData['ImaxSet']}

    Trac = [SepData['IVdata'][2],SepData['IVdata'][3]]
    eChar.plotIVData({"Traces":Trac, 'Xaxis': True, 'Xlabel': 'Time (s)', "Ylabel": 'Current (A)', 'Title': "Pulse IV", "ValueName": 'tI'})

    if ret[3]["Name"][0].lower() == "i":
        Trac = [SepData['IVdata'][1],SepData['IVdata'][3]] 
    else:
        Trac = [SepData['IVdata'][3],SepData['IVdata'][1]] 
    eChar.plotIVData({"Traces":Trac, 'Xaxis': True, 'Xlabel': 'Voltage (V)', "Ylabel": 'Current (A)', 'Title': "Pulse IV", "ValueName": 'IV'})

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

    PulseIVDataPrepAndExport(eChar, SepData, header, eChar.curCycle, MeasPoints)

    res = {'Header':header, 'IVdata': SepData['IVdata'], 'LRS':SepData['LRS'], 'HRS':SepData['HRS'], 'ImaxReset': SepData['ImaxReset']}


    
    Trac = [SepData['IVdata'][2],SepData['IVdata'][3]]
    eChar.plotIVData({"Traces":Trac, 'Xaxis': True, 'Xlabel': 'Time (s)', "Ylabel": 'Current (A)', 'Title': "Pulse IV", "ValueName": 'tI'})
    
    if ret[3]["Name"][0].lower() == "i":
        Trac = [SepData['IVdata'][1],SepData['IVdata'][3]] 
    else:
        Trac = [SepData['IVdata'][3],SepData['IVdata'][1]] 
    eChar.plotIVData({"Traces":Trac, 'Xaxis': True, 'Xlabel': 'Voltage (V)', "Ylabel": 'Current (A)', 'Title': "Pulse IV", "ValueName": 'IV'})

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

    PulseIVDataPrepAndExport(eChar, SepData, header, eChar.curCycle, MeasPoints)

    if ret[3]["Name"][0].lower() == "i":
        Trac = [SepData['IVdata'][1],SepData['IVdata'][3]] 
    else:
        Trac = [SepData['IVdata'][3],SepData['IVdata'][1]] 
    eChar.plotIVData({"Traces":Trac,  'Xaxis': True, 'Xlabel': 'Voltage (V)', "Ylabel": 'Current (A)', 'Title': "Pulse IV", "ValueName": 'IV'})
    
    Trac = [SepData['LRS'],SepData['HRS']]
    eChar.plotIVData({"Add": True,  "lineStyle": 'o', "lineWidth":0.5, 'Yscale': 'log', "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of cycles', "Ylabel": 'resistance (ohm)', 'Title': "HRS/LRS", "ValueName": 'HRS/LRS'})

    res = {'Header':header, 'IVdata': SepData['IVdata'], 'LRS':SepData['LRS'], 'HRS':SepData['HRS'], 'Vset':SepData['Vset'], 'Vreset':SepData['Vreset'], 'ImaxSet': SepData['ImaxSet'], 'ImaxReset': SepData['ImaxReset'], 'Type':'PulseIV'}

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

    #eChar.LogData.put("Endurance1")
    eChar.updateTime()
    CurCount = 1
    initialRead = True
    if IVIteration ==0: 
        IVcount =0

    eChar.startThread(target = saveDataEndurance, args=(eChar, WriteHeader,DoYield, eChar.getMaxRowsPerFile(), eChar.getMaxDataPerPlot()))
    eChar.LogData.put(eChar)

    stop =  False
    #Run repetitions until number of ran cycles reaches programmed count
    
    while CurCount < Count - IVcount:

        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
        if stop:
            eChar.finished.put(True)
            break

        eChar.LogData.put("HEHEHE1")
        #IV characterization + Endurance
        if IVIteration > 20:
            eChar.LogData.put("Hello1")
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
                eChar.LogData.put("Hello2")
                
                IVIteration = Count - CurCount - IVcount
                if IVIteration < 1: 
                    break
                
                #Less cycles left than in one iteration
                if IVIteration > eChar.getMaxNumSingleEnduranceRun() and ReadEndurance:
                    eChar.LogData.put("Hello3")

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
                    eChar.LogData.put("Hello4")

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
                eChar.LogData.put("Hello5")
                
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
            eChar.LogData.put("OnlyEnd")
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
                eChar.LogData.put("OnlyEnd2")
                createEndurancePulse(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
                                            Count, read=ReadEndurance, tread=10e-6, Vread=-0.2, initialRead=initialRead)

                initialRead = False

                if ReadEndurance:
                    eChar.LogData.put("OnlyEnd3")
                    ret = eChar.wgfmu.executeMeasurement()
                    eChar.LogData.put(ret)
                    ret = getSepEnduranceData(ret)
                    eChar.LogData.put(ret)
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
    eChar.LogData.put("OutsideHello")
    #eChar.LogData.put(ret)

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
            #eChar.LogData.put("True1")
            entry = eChar.SubProcessThread.get(block=True, timeout=1)
        except qu.Empty:
            #eChar.LogData.put("Empty1")
            entry = None
        eChar.LogData.put(entry)
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
    eChar.LogData.put("SaveData1")
    
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
            
            if not 'Type' in list(complData.keys()):
                eChar.LogData.put("Couldnt find key 'Type' in data from PulseEndurance.")
                continue

            if complData['Type'] == 'Endurance':
                
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
                with eChar.dataAnalysisLock:
                    if len(eChar.IVHRS) > MaxRowsPerFile or (finished and eChar.rawData.empty()): 
                        header = eChar.getHeader("Endurance")
                        header.append('Measurement,Endurance.StartPoint,%d' %(eChar.IVcyc[0]))
                        header.append('Measurement,Endurance.EndPoint,%d' %(eChar.IVcyc[-1]))
                        header.extend(eChar.getHeader("External"))
                        header.extend(eChar.getHeader("DC"))

                        header.append('DataName, Cycle, LRS, HRS, ImaxSet, ImaxReset')
                        header.append('Dimension, %d,%d,%d,%d,%d' %(len(eChar.IVcyc), len(eChar.IVLRS), len(eChar.IVHRS), len(eChar.ImaxSet), len(eChar.ImaxReset)))
                        
                        outputData = getOutputFormat([eChar.IVcyc,eChar.IVLRS,eChar.IVHRS,eChar.ImaxSet,eChar.ImaxReset])
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

            with eChar.dataAnalysisLock:
                if len(eChar.HRS) > MaxRowsPerFile or (finished and eChar.rawData.empty()): 
                    header = eChar.getHeader("Endurance")
                    header.append('Measurement,Endurance.StartPoint,%d' %(eChar.cyc[0]))
                    header.append('Measurement,Endurance.EndPoint,%d' %(eChar.cyc[-1]))
                    header.extend(eChar.getHeader("External"))
                    header.extend(eChar.getHeader("DC"))

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

            PulseGen.disableOutput(PGPulseChn)
            PulseGen.setTriggerOutputAmplitude(0)


    ################################################################################

    if not WriteHeader:
        header = eChar.getHeader("Combined")
    else:
        header = []


    header.insert(0,"TestParameter,Measurement.Type,HFanalogRetention")
    
    header.append("Instrument,Oscilloscope,%s" %(OscName.strip()))
    header.append("Instrument,PulseGenerator,%s" %(PGName.strip()))
    header.append("Measurement,Device,%s" %(eChar.getDevice()))
    header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.getLocalTime())))
    header.append("Measurement,PGPulseChannel, %s" %(PGPulseChn))
    header.append("Measurement,OscPulseChn, %s" %(OscPulseChn))
    header.append("Measurement,OscGNDChn, %s" %(OscGNDChn))
    header.append("Measurement,Vset, %.2e" %(Vset))
    header.append("Measurement,Set Pulse Width, %.2e" %(twidthSet))
    header.append("measurement,Set Resistance Step, %.2f" %( twidthReset))
    header.append("Measurement,Vreset, %.2e" %(Vreset))
    header.append("Measurement,Reset Pulse Width, %.2e" %(twidthReset))
    header.append("Measurement,Vread, %.2e" %(Vread))
    header.append("Measurement,Read Pulse Width, %.2e" %(tread))
    header.append("Measurement,Read Time Seperation, %.2e" %(tseperation))
    header.append("Measurement,Rgoal, %s" %(Rgoal))
    header.append("Measurement,MaxPulses, %s" %(MaxPulses))
    header.append("Measurement,Repetition, %s" %(Repetition))
    header.append("Measurement,PowerSplitter, %s" %(PS))

    if WriteHeader:
        eChar.extendHeader("Combined", header)

    header.extend(eChar.getHeader("External"))
    header.extend(eChar.getHeader("DC"))

    newline = [None]*3
    newline[0] = 'DataName'
    newline[1] = 'Dimension'
    newline[2] = 'Repetition'
    OutputData = []
    
    nMax = 0
    
    for n in range(RunRep):
        try:
            newline[0] = '%s, Entry #, Reset Goal (ohm), Reset Resistance (ohm), Reset Dev. (value), Reset Dev. (perc), Reset Conductance (s)' %(newline[0])
            newline[1] = '%s, %d, %d, %d, %d, %d, %d' %(newline[1],len(nReset[n]),len(Rresgoal[n]), len(Rreset[n]), len(Rresetdev[n]), len(Presetdev[n]), len(Creset))
            newline[2] = '%s, %d, %d, %d, %d, %d, %d' %(newline[2],n+1,n+1,n+1,n+1,n+1,n+1)
            
            newline[0] = '%s, time , Retention Goal (ohm), Ret. Resistance (ohm), Ret. Dev. (value), Ret. Dev. (perc), Ret. Conductance (s)' %(newline[0])
            newline[1] = '%s, %d, %d, %d, %d, %d, %d' %(newline[1],len(tret[n]),len(Rretgoal[n]), len(Rret[n]), len(Rretdev[n]), len(Pretdev[n]), len(Cret))
            newline[2] = '%s, %d, %d, %d, %d, %d, %d' %(newline[2],n+1,n+1,n+1,n+1,n+1,n+1)

        except IndexError:
            None
            
        CurMax = max([len(Rreset[n]),len(Rret[n])])

        if CurMax > nMax:
            nMax = CurMax

    OutputData = []
    for n in range(nMax):
        data = 'DataValue'
        for k in range(RunRep):
            try:
                data = "%s, %f, %f, %f, %f, %f, %f" %(data, nReset[k][n], Rresgoal[k][n], Rreset[k][n], Rresetdev[k][n], Presetdev[k][n], Creset[k][n])
            except IndexError:
                data = "%s, , , , , , " %(data)
            try:
                data = "%s, %f, %f, %f, %f, %f, %f" %(data, tret[k][n], Rretgoal[k][n], Rret[k][n], Rretdev[k][n], Pretdev[k][n], Cret[k][n])
            except IndexError:
                data = "%s, , , , , , " %(data)

        OutputData.append(data)


    header1 = cp.deepcopy(header)
    header1.extend(newline)

    eChar.writeDataToFile(header1, OutputData, Typ='Endurance', startCyc=CycStart, endCyc=eChar.curCycle-1)
            
    nMax = 0
    for n in range(RunRep):
        
        try:
            newline[0] = '%s, Res. Goal (ohm), Resistance (ohm), Res. Dev. (value), Res. Dev. (perc), Res. Conductance (s)' %(newline[0])
            newline[1] = '%s, %d, %d, %d, %d, %d' %(newline[1],len(RgoalCompl[n]), len(Rcompl[n]), len(RdeltaCompl[n]), len(PercDelCompl[n]), len(Ccompl[n]))
            newline[2] = '%s, %d, %d, %d, %d, %d' %(newline[2],n+1,n+1,n+1,n+1,n+1)
        except IndexError:
            None
        CurMax = len(Rreset)

        if CurMax > nMax:
            nMax = CurMax

    OutputData = []
    for n in range(nMax):
        data = 'DataValue'
        for k in range(RunRep):
            try:
                data = "%s, %f, %f, %f, %f, %f" %(data, RgoalCompl[k][n], Rcompl[k][n], RdeltaCompl[k][n], PercDelCompl[k][n], Ccompl[k][n])
            except IndexError:
                data = "%s, , , , , " %(data)

        OutputData.append(data)
    
    header.extend(newline)
    Typ2 = "Compl_%s" %(Typ)
    eChar.writeDataToFile(header, OutputData, Typ=Typ2, startCyc=CycStart, endCyc=eChar.curCycle-1)
    
    AvgLRS = eChar.dhValue([], 'FirstHRS', Unit='ohm')
    AvgHRS = eChar.dhValue([], 'FirstLRS', Unit='ohm')
    AvgRret = eChar.dhValue([], 'Rret', Unit='ohm')
    Avgtfail = eChar.dhValue([], 'tfail', Unit='ohm')
    
    for n in range(RunRep-1):
        if len(Rreset) > n: 
            if len(Rreset[n]) > 0: 
                AvgLRS.extend(Rreset[n][0])
                AvgHRS.extend(Rreset[n][-1])
        try:
            tfail = tret[n][-1]
            for k in range(len(Rret[n])):
                if (1-RetentionFailure/100)*Rreset[n][-1] < Rret[n][k] > (1+RetentionFailure/100)*Rreset[n][-1]:
                    tfail = tret[n][k]
                    break
            Avgtfail.extend(tfail)
        except IndexError:
            None
        AvgRret.extend(Rret[n])

    row = eChar.dhAddRow([AvgLRS,AvgHRS,AvgRret, Avgtfail])


###########################################################################################################################
def IncrementalSwitching(eChar, PGPulseChn, OscPulseChn, OscGNDChn, ExpReadCurrent, Vset, Vreset, twidthSet, twidthReset, Vread, tread, RstepSet, RstepReset, MaxResistance, MaxPulsesPerStepSet, MaxPulsesPerStepReset, Round, Repetition, PowerSplitter, WriteHeader=True):
        
    """
    Applies voltage pulses via the Agilent 81110A pulse generator and measures the pulse response via a LeCroy oscilloscope
    Both Devices must be available. RF setup is recommended for rise times below 50ns. 
    PGPulseChn:     Pulse Channel of 81110A, (1 or 2)
    OscPulseChn:    Oscilloscope Pulse Channel
    OscGNDChn:      Oscilloscope GND Channel
    Vset:           Set Voltage (V)
    Vreset:         Reset Voltage (V)
    settwidth:      Set pulse width (s)
    resettwidth:    Reset pulse width (s)
    Vread:          Read Voltage (V)
    tread:          Read pulse width(V)
    RstepSet:       Aimed resistance step per Set
    RstepReset:     Aimed resistance step per Reset
    MaxPulsesPerStepSet:    Maximum number of pulses per step until pulsing is stopped
    MaxPulsesPerStepReset:  Maximum number of pulses per step until pulsing is stopped
    Round           Round to next RstepSize
    Repetition:     Number of set/rest cycles
    PowerSplitter:  Is a power splitter in use? 
    WriteHeader: Enable/Disable writing the header into overlaying summary output files
    """

    #if a power splitter is used the input voltage gets divided by two to measure the voltage as well. 
    PS = PowerSplitter
    if PS:
        Vset = 2*Vset
        Vreset = 2*Vreset
        Vread = 2*Vread

    Typ = 'IncrementalSwitching'
    #settrise = 0.8e-9
    settrise = 2e-9
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

        nReset = []
        Rreset = []
        RresGoal = []

        nSet = []
        Rset = []
        RsetGoal = []
        Rep = []
        RdelReset = []
        PercDelReset = []
        RdelSet = []
        PercDelSet = []

        Rcompl = []
        ncompl = []
        RgoalCompl = []
        Ccompl = []
        RdeltaCompl = []
        PercDelCompl = []

        stop = False
        RunRep = 1


        if Vread < 0:
            PulseGen.invertedOutputPolarity(chn=PGPulseChn)
            posV = 0
            negV = Vread
        else:
            PulseGen.normalOutputPolarity(chn=PGPulseChn)
            posV = Vread
            negV = 0

        PulseGen.setVoltageHigh(posV, chn=PGPulseChn) 
        PulseGen.setVoltageLow(negV, chn=PGPulseChn)
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

        R0 = abs(V/I)
        R = R0
        Trac = [[R]]
        eChar.IVplotData.put({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",  "ValueName": 'R'})
        Trac = [[1/R]]  
        eChar.IVplotData.put({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",  "ValueName": 'C'})

        Rcompl.append(R)
        Ccompl.append(1/R)
        ncompl.append(0)
        RgoalCompl.append(R)
        RdeltaCompl.append(0)
        PercDelCompl.append(0)   

        for n in range(Repetition):
            print("n", n)

            nReset.append([])
            Rreset.append([])
            RresGoal.append([])
            nSet.append([])
            Rset.append([])
            RsetGoal.append([])
            RdelReset.append([])
            PercDelReset.append([])
            RdelSet.append([])
            PercDelSet.append([])

            Rplot = []
            nplot = []
            
            # Set the first goal resistance to be hit 
            if Round:
                Rgoal = ma.ceil(R/RstepReset)*RstepReset
            else: 
                Rgoal = R + RstepReset

            r = 1
            Rwrote = False

            #write first value from Previous Read
            Rreset[n].append(R)
            nReset[n].append(0)
            RresGoal[n].append(R)
            RdelReset[n].append(0)
            PercDelReset[n].append(0)

            r = 1
            
            while r <= MaxPulsesPerStepReset and float(R) <= MaxResistance:
                print("r", r)
    
                while not eChar.Stop.empty():
                    stop = eChar.Stop.get()
                if stop:    
                    eChar.finished.put(True)
                    break

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
                VertScale = abs(Vread/4)
                Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)

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
                PulseGen.turnOffOutput(chn=PGPulseChn)
                if not PS:
                    PulseGen.turnDifferentialOutputOff(PGPulseChn)
                
                if PS:
                    V = float(Oscilloscope.getMeasurementResults(1))
                else:
                    V = Vread
                I = float(Oscilloscope.getMeasurementResults(2))/50

                R = abs(V/I)
                print("rR", R, " goal ", Rgoal)

                Rcompl.append(R)
                Ccompl.append(1/R)
                ncompl.append(r)
                RgoalCompl.append(Rgoal)
                RdeltaCompl.append(abs(R-Rgoal))
                PercDelCompl.append(abs((R-Rgoal)/R))

                if R > Rgoal:
                    Rreset[n].append(R)
                    nReset[n].append(r)
                    RresGoal[n].append(Rgoal)
                    RdelReset[n].append(abs(R-Rgoal))
                    PercDelReset[n].append(abs((R-Rgoal)/R))
                    
                    r = 1
                    Rgoal = Rgoal + RstepReset
                    Trac = [[R]]
                    eChar.IVplotData.put({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",  "ValueName": 'R'})
                    Trac = [[1/R]]  
                    eChar.IVplotData.put({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",  "ValueName": 'C'})
                    Rwrote = True
                else:
                    r = r+1
            
            if not Rwrote:
                Rreset[n].append(R)
                nReset[n].append(r-1)
                RresGoal[n].append(Rgoal)
                RdelReset[n].append(abs(R-Rgoal))
                PercDelReset[n].append(abs((R-Rgoal)/R))

                Trac = [[R]]
                eChar.IVplotData.put({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",  "ValueName": 'R'})
                Trac = [[1/R]]  
                eChar.IVplotData.put({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",  "ValueName": 'C'})
                    
            s = 1
            
            if Round:
                Rgoal = ma.floor(R/RstepSet)*RstepSet
            else: 
                Rgoal = R - RstepSet


            #write first value from Previous Read
            Rset[n].append(R)
            nSet[n].append(0)
            RsetGoal[n].append(R)
            RdelSet[n].append(0)
            PercDelSet[n].append(0)
            
            Swrote = False
            while s <= MaxPulsesPerStepSet:

                while not eChar.Stop.empty():
                    stop = eChar.Stop.get()
                if stop:    
                    eChar.finished.put(True)
                    break

                ####### Set
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
                VertScale = abs(Vread/4)
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
                print("sR", R, " goal ", Rgoal)
            

                Rcompl.append(R)
                Ccompl.append(1/R)
                ncompl.append(r)
                RgoalCompl.append(Rgoal)
                RdeltaCompl.append(abs(R-Rgoal))
                PercDelCompl.append(abs((R-Rgoal)/R))

                if R < Rgoal:
                    Rset[n].append(R)
                    nSet[n].append(s)
                    RsetGoal[n].append(Rgoal)
                    RdelSet[n].append(abs(R-Rgoal))
                    PercDelSet[n].append(abs((R-Rgoal)/R))
                    
                    Trac = [[R]]
                    eChar.IVplotData.put({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",  "ValueName": 'R'})
                    Trac = [[1/R]]  
                    eChar.IVplotData.put({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",  "ValueName": 'C'})
                    s = 1
                    Rgoal = Rgoal - RstepSet
                    Swrote = True
                else:
                    s = s+1
            
            if not Swrote:
                Rset[n].append(R)
                nSet[n].append(s-1)
                RsetGoal[n].append(Rgoal)
                RdelSet[n].append(abs(R-Rgoal))
                PercDelSet[n].append(abs((R-Rgoal)/R))
                                
                Trac = [[R]]
                eChar.IVplotData.put({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",  "ValueName": 'R'})
                Trac = [[1/R]]  
                eChar.IVplotData.put({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",  "ValueName": 'C'})

            eChar.curCycle = eChar.curCycle + 1

            RunRep = RunRep + 1
            if stop:    
                eChar.finished.put(True)
                break
        
        PulseGen.turnOffOutput(chn=PGPulseChn)
        if not PS:
            PulseGen.turnDifferentialOutputOff(PGPulseChn)



    else:
        
        Oscilloscope = eChar.Oscilloscope
        PulseGen = eChar.PulseGen

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
        PulseGen.setTriggerModeExternal()
        PulseGen.setTriggerThreshold(ArmLevel)
        PulseGen.setPulsePeriod(period)
        PulseGen.setTriggerImpedanceTo50ohm()
        PulseGen.setInitDelay(0, PGPulseChn)
        PulseGen.set

        nReset = []
        Rreset = []
        RresGoal = []

        nSet = []
        Rset = []
        RsetGoal = []
        Rep = []
        RdelReset = []
        PercDelReset = []
        RdelSet = []
        PercDelSet = []

        Rcompl = []
        ncompl = []
        RgoalCompl = []
        Ccompl = []
        RdeltaCompl = []
        PercDelCompl = []

        stop = False
        RunRep = 1


        if Vread < 0:
            posV = 0
            negV = Vread
        else:
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

        R0 = abs(V/I)
        R = R0
        Trac = [[R]]
        eChar.IVplotData.put({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",  "ValueName": 'R'})
        Trac = [[1/R]]  
        eChar.IVplotData.put({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",  "ValueName": 'C'})

        Rcompl.append(R)
        Ccompl.append(1/R)
        ncompl.append(0)
        RgoalCompl.append(R)
        RdeltaCompl.append(0)
        PercDelCompl.append(0)   

        for n in range(Repetition):
            print("n", n)

            nReset.append([])
            Rreset.append([])
            RresGoal.append([])
            nSet.append([])
            Rset.append([])
            RsetGoal.append([])
            RdelReset.append([])
            PercDelReset.append([])
            RdelSet.append([])
            PercDelSet.append([])

            Rplot = []
            nplot = []
            
            # Set the first goal resistance to be hit 
            if Round:
                Rgoal = ma.ceil(R/RstepReset)*RstepReset
            else: 
                Rgoal = R + RstepReset

            r = 1
            Rwrote = False

            #write first value from Previous Read
            Rreset[n].append(R)
            nReset[n].append(0)
            RresGoal[n].append(R)
            RdelReset[n].append(0)
            PercDelReset[n].append(0)

            r = 1
            
            while r <= MaxPulsesPerStepReset and float(R) <= MaxResistance:
                print("r", r)
    
                while not eChar.Stop.empty():
                    stop = eChar.Stop.get()
                if stop:    
                    eChar.finished.put(True)
                    break

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
                PulseGen.enalbeOutput(PGPulseChn)
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
                    PulseGen.setVoltageHigh(0, PGPulseChn) 
                    PulseGen.setVoltageLow(Vread, PGPulseChn)

                Vprev = Vread
                PulseGen.setPulseWidth(tread)
                
                Oscilloscope.writeAcquisitionTrigger("C%dLevel" %(TrigChn), TriggerLevel)
                VertScale = abs(Vread/4)
                Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)

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

                PulseGen.disableOutput(PGPulseChn)
                PulseGen.setTriggerOutputAmplitude(0)
                
                if PS:
                    V = float(Oscilloscope.getMeasurementResults(1))
                else:
                    V = Vread
                I = float(Oscilloscope.getMeasurementResults(2))/50

                R = abs(V/I)
                print("rR", R, " goal ", Rgoal)

                Rcompl.append(R)
                Ccompl.append(1/R)
                ncompl.append(r)
                RgoalCompl.append(Rgoal)
                RdeltaCompl.append(abs(R-Rgoal))
                PercDelCompl.append(abs((R-Rgoal)/R))

                if R > Rgoal:
                    Rreset[n].append(R)
                    nReset[n].append(r)
                    RresGoal[n].append(Rgoal)
                    RdelReset[n].append(abs(R-Rgoal))
                    PercDelReset[n].append(abs((R-Rgoal)/R))
                    
                    r = 1
                    Rgoal = Rgoal + RstepReset
                    Trac = [[R]]
                    eChar.IVplotData.put({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",  "ValueName": 'R'})
                    Trac = [[1/R]]  
                    eChar.IVplotData.put({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",  "ValueName": 'C'})
                    Rwrote = True
                else:
                    r = r+1
            
            if not Rwrote:
                Rreset[n].append(R)
                nReset[n].append(r-1)
                RresGoal[n].append(Rgoal)
                RdelReset[n].append(abs(R-Rgoal))
                PercDelReset[n].append(abs((R-Rgoal)/R))

                Trac = [[R]]
                eChar.IVplotData.put({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",  "ValueName": 'R'})
                Trac = [[1/R]]  
                eChar.IVplotData.put({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",  "ValueName": 'C'})
                    
            s = 1
            
            if Round:
                Rgoal = ma.floor(R/RstepSet)*RstepSet
            else: 
                Rgoal = R - RstepSet


            #write first value from Previous Read
            Rset[n].append(R)
            nSet[n].append(0)
            RsetGoal[n].append(R)
            RdelSet[n].append(0)
            PercDelSet[n].append(0)
            
            Swrote = False
            while s <= MaxPulsesPerStepSet:

                while not eChar.Stop.empty():
                    stop = eChar.Stop.get()
                if stop:    
                    eChar.finished.put(True)
                    break

                ####### Set
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
                VertScale = abs(Vread/4)
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
                print("sR", R, " goal ", Rgoal)
            

                Rcompl.append(R)
                Ccompl.append(1/R)
                ncompl.append(r)
                RgoalCompl.append(Rgoal)
                RdeltaCompl.append(abs(R-Rgoal))
                PercDelCompl.append(abs((R-Rgoal)/R))

                if R < Rgoal:
                    Rset[n].append(R)
                    nSet[n].append(s)
                    RsetGoal[n].append(Rgoal)
                    RdelSet[n].append(abs(R-Rgoal))
                    PercDelSet[n].append(abs((R-Rgoal)/R))
                    
                    Trac = [[R]]
                    eChar.IVplotData.put({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",  "ValueName": 'R'})
                    Trac = [[1/R]]  
                    eChar.IVplotData.put({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",  "ValueName": 'C'})
                    s = 1
                    Rgoal = Rgoal - RstepSet
                    Swrote = True
                else:
                    s = s+1
            
            if not Swrote:
                Rset[n].append(R)
                nSet[n].append(s-1)
                RsetGoal[n].append(Rgoal)
                RdelSet[n].append(abs(R-Rgoal))
                PercDelSet[n].append(abs((R-Rgoal)/R))
                                
                Trac = [[R]]
                eChar.IVplotData.put({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",  "ValueName": 'R'})
                Trac = [[1/R]]  
                eChar.IVplotData.put({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",  "ValueName": 'C'})

            eChar.curCycle = eChar.curCycle + 1

            RunRep = RunRep + 1
            if stop:    
                eChar.finished.put(True)
                break
        
        PulseGen.disableOutput(PGPulseChn)
        PulseGen.setTriggerOutputAmplitude(0)




    if not WriteHeader:
        header = eChar.getHeader("Combined")
    else:
        header = []

    header.insert(0,"TestParameter,Measurement.Type,HFincrementalPulsing81110A")
    
    header.append("Instrument,Oscilloscope,%s" %(OscName.strip()))
    header.append("Instrument,PulseGenerator,%s" %(PGName.strip()))
    header.append("Measurement,Device,%s" %(eChar.getDevice()))
    header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.getLocalTime())))
    header.append("Measurement,Vset, %.2e" %(Vset))
    header.append("Measurement,Set Pulse Width, %.2e" %(twidthSet))
    header.append("Measurement,Set Max Pulses Per Step,  %d" %(MaxPulsesPerStepSet))
    header.append("measurement,Set Resistance Step, %.2f" %( RstepSet))
    header.append("Measurement,Vreset, %.2e" %(Vreset))
    header.append("Measurement,Reset Pulse Width, %.2e" %(twidthReset))
    header.append("Measurement,Reset Max Pulses Per Step,  %d" %(MaxPulsesPerStepReset))
    header.append("measurement,Reset Resistance Step, %.2e" %( RstepReset))
    header.append("Measurement,Vread, %.2e" %(Vread))
    header.append("Measurement,Read Pulse Width, %.2e" %(tread))
    header.append("Measurement,Round, %s" %(Round))
    header.append("Measurement,Repetition, %s" %(Repetition))
    header.append("Measurement,PowerSplitter, %s" %(PS))

    if WriteHeader:
        eChar.writeHeader("Combined", header)

    header.extend(eChar.getHeader("External"))
    header.extend(eChar.getHeader("DC"))


    newline = [None]*3
    newline[0] = 'DataName'
    newline[1] = 'Dimension'
    newline[2] = 'Repetition'
    EntryNumReset = []
    EntryNumSet = []
    OutputData = []
    
    nMax = 0
    for n in range(len(Rset)):
        CondReset = list(np.reciprocal(Rreset[n]))
        CondSet = list(np.reciprocal(Rset[n]))
        
        newline[0] = '%s,Entry #, Res. Goal, Res., # of Pulses, Res. Dev. (value), Res. Dev. (perc), Res. Conductance (s)' %(newline[0])
        newline[1] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[1],len(RresGoal[n]),len(RresGoal[n]), len(Rreset[n]), len(nReset[n]), len(RdelReset[n]), len(PercDelReset[n]), len(CondReset))
        newline[2] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[2],n+1,n+1,n+1,n+1,n+1,n+1,n+1)
        if EntryNumReset == []:
            EntryNumReset.append(list(range(1,1+len(RresGoal[n]),1)))
        else:
            EntryNumReset.append(list(range(EntryNumSet[-1][-1]+1,EntryNumSet[-1][-1]+1+len(RresGoal[n]),1)))

        newline[0] = '%s,Entry #, Set. Goal, Set., # of Pulses, Set. Dev. (value), Set. Dev. (perc), Set. Conductance (s)' %(newline[0])
        newline[1] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[1],len(RsetGoal[n]),len(RsetGoal[n]), len(Rset[n]), len(nSet[n]), len(RdelSet[n]), len(PercDelSet[n]), len(CondSet))
        newline[2] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[2],n+1,n+1,n+1,n+1,n+1,n+1,n+1)

        EntryNumSet.append(list(range(EntryNumReset[-1][-1]+1,EntryNumReset[-1][-1]+1+len(RresGoal[n]),1)))

        CurMax = max(len(RresGoal[n]), len(Rreset[n]), len(nReset[n]), len(RdelReset[n]), len(PercDelReset[n]), len(CondReset),len(RsetGoal[n]), len(Rset[n]), len(nSet[n]), len(RdelSet[n]), len(PercDelSet[n]), len(CondSet))

        if CurMax > nMax:
            nMax = CurMax

        

    OutputData = []
    for n in range(nMax):
        data = 'DataValue'
        for k in range(len(Rset)):
            try:
                CondReset = float(1/Rreset[k][n])
                data = "%s, %f, %f, %f, %f, %f, %f, %f" %(data, EntryNumReset[k][n], RresGoal[k][n], Rreset[k][n], nReset[k][n], RdelReset[k][n], PercDelReset[k][n], CondReset)
            except IndexError:
                data = "%s, , , , , , , " %(data)
            try:
                CondSet = float(1/Rset[k][n])
                data = "%s, %f, %f, %f, %f, %f, %f, %f" %(data,  EntryNumSet[k][n], RsetGoal[k][n], Rset[k][n], nSet[k][n], RdelSet[k][n], PercDelSet[k][n], CondSet)
            except IndexError:
                data = "%s, , , , , , , " %(data)
        OutputData.append(data)
        
    header1 = cp.deepcopy(header)
    header1.extend(newline)
    eChar.writeDataToFile(header1, OutputData, Typ=Typ, startCyc=CycStart, endCyc=eChar.curCycle-1)
            
    newline = [None]*2
    newline[0] = 'DataName, R Goal, R, # of Pulses, Deviation (value), Deviation (perc), Conductance (s)'
    newline[1] = 'Dimension, %d, %d, %d, %d, %d, %d' %(len(RgoalCompl), len(Rcompl), len(ncompl), len(RdeltaCompl), len(PercDelCompl), len(Ccompl))
    
    OutputData2 = []
    for n in range(len(Rcompl)):
        data = 'DataValue, %f, %f, %d, %f, %f, %f' %(RgoalCompl[n], Rcompl[n], ncompl[n], RdeltaCompl[n], PercDelCompl[n], Ccompl[n])
        OutputData2.append(data)
    
    header.extend(newline)
    Typ2 = "Compl_%s" %(Typ)
    eChar.writeDataToFile(header, OutputData2, Typ=Typ2, startCyc=CycStart, endCyc=eChar.curCycle-1)

    r0 = R0
    Rdelta = []
    Rdelta.append(Rreset[0][-1] - R0)
    for r, s in zip(Rreset, Rset):
        Rdelta.append(r[-1]-s[-1])


    AvgSetPul = eChar.dhValue([], 'FirstHRS', Unit='ohm')
    AvgResetPul = eChar.dhValue([], 'FirstLRS', Unit='ohm')

    for n in nSet:
        AvgSetPul.extend(n)

    for n in nReset:
        AvgResetPul.extend(n)

    AvgRratio = eChar.dhValue(Rdelta, 'ImaxForm', Unit='A')
    row = eChar.dhAddRow([AvgSetPul,AvgResetPul,AvgRratio],eChar.curCycle,eChar.curCycle)    
    

###########################################################################################################################

def EndurancePartialRead(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, tbase, 
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
        if IVIteration > 0:
            addHeader = []
            addHeader.append('Measurement,Type.Primary,Endurance')
            addHeader.append('Measurement,Type.Secondary,PulseIV')
            with eChar.CycleLock:
                addHeader.append('Measurement,Endurance.StartPoint,%d' %(eChar.curCycle))
                addHeader.append('Measurement,Endurance.EndPoint,%d' %(eChar.curCycle+IVcount))
            eChar.extendHeader("Additional",addHeader)


            WrHead = False
            if initialRead:
                WrHead = True
            
            with eChar.CycleLock:
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
                            with eChar.CycleLock:
                                eChar.RDstart.put(eChar.curCycle)
                                eChar.RDstop.put(eChar.curCycle + eChar.getMaxNumSingleEnduranceRun()()-1)
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
        addHeader= []
        addHeader.append('Measurement,Type.Primary,Endurance')
        addHeader.append('Measurement,Type.Secondary,PulseIV')
        addHeader.append('Measurement,Endurance.StartPoint,%d' %(eChar.curCycle))
        addHeader.append('Measurement,Endurance.EndPoint,%d' %(eChar.curCycle+IVcount))
        eChar.writeHeader("Additional", addHeader)
        
        if not stop:

            eChar.RDstart.put(eChar.curCycle)
            eChar.RDstop.put(eChar.curCycle + IVcount-1)
            eChar.rawData.put(PulseIV(eChar, PulseChn, GroundChn, Vset, Vreset, delay, triseS, tfallS, twidthS, triseR, tfallR, twidthR, 
                                tbase, MeasPoints=MeasPoints, count=IVcount, read=True, initialRead=initialRead, tread=tread, Vread=Vread, 
                                SMUs=SMUs, Vdc=Vdc, DCcompl=DCcompl,WriteHeader=False, Primary=False))
            CurCount += IVcount

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

        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
        if stop:
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
            eChar.writeHeader("Endurance",eChar.wgfmu.getHeader())
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