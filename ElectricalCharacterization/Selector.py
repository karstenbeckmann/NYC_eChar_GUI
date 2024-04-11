'''
This file contains Selector Characterization definitions from Karsten Beckmann
kbeckmann@sunypoly.edu
'''

import time as tm
import StdDefinitions as std
import StatisticalAnalysis as dh
import threading as th
import math as ma
import queue as qu
import numpy as np
import traceback
import copy as cp


###########################################################################################################################
    
def SelectorPulseTest(eChar, PulseChn, GroundChn, Vhigh, Vlow, delay, trise, tfall, tread, tbase, MeasPoints, IVcycles, ReadCycles, ExtractReads, Repetitions=1, WriteHeader=True, DoYield=True):
    """
    Measurement to characterize Selector devices with pulse IV
    please set the appropriate Channel properties beforehand via 'setChannelParameter()'
    GroundChn: Ground channel number
    PulseChn:  Pulse channel number
    Vhigh:      Pulse High Voltage/Read Voltage
    Vlow:       Pulse Read Low Voltage
    delay:      delay before measurement starts
    trise:      rise time
    tfall:      fall time
    tread:      Read Pulse width
    tbase:      base time
    MeasPoints: Number of Measurement points during Set and Reset
    IVcycles:    Number of IV cycles
    ReadCycles:  Number of ReadCycles after each IV cycle
    ExtractReads: Extraction of ReadCycles 
    Repetition: Number of repetitions (IVcycle + ReadCycles)
    WriteHeader: Enable/Disable writing the header into overlaying summary output files
    """
        
    eChar.updateTime()
    #count-=1
    tfallread = tread * 0.1
    triseread = tread * 0.1

    tmstart = tbase/2 + tfallread
    tmend = tbase/2 + tfallread + tread
    duration = sum([tbase,tfallread,triseread,tread])
    tbaseHalf = tbase/2
    MaxRowsPerFile = 1000000

    eChar.Selstart = qu.Queue()
    eChar.Selstop = qu.Queue()

    eChar.finished.put(False)
    eChar.startThread(target = selectorOutput, args=(eChar, WriteHeader,DoYield,MaxRowsPerFile))

    if PulseChn < GroundChn:
        chns = {'tv': 0, 'v': 1, 'ti': 2, 'i': 3}
    else:
        chns = {'tv': 2, 'v': 3, 'ti': 0, 'i': 1}
    

    for n in range(Repetitions):

        stop = False
        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
        if stop:    
            eChar.finished.put(True)
            break

        eChar.Selstart.put(eChar.curCycle)
        
        for k in range(5):
            try:
                RetPulseIV = SelectorPulseIV(eChar, PulseChn, GroundChn, Vhigh, Vlow, delay, trise, tfall, tread, tbase, MeasPoints, IVcycles, Primary=False, WriteHeader=True)
                break
            except (SystemError, ValueError, IndexError) as e:
                traceback.print_exc()
                eChar.ErrorQueue.put("SelectroPulseIV - Rerun: %s." %(e))

        eChar.Selstop.put(eChar.curCycle-1)
        
        if n == 0: 
            eChar.writeHeader("Selector", eChar.wgfmu.getHeader())

        eChar.SelectorEndurance.put({"Type": "IV", "Rlow": RetPulseIV["RlowPos"], "Rhigh": RetPulseIV["Rhigh"], "Ilow": RetPulseIV["IlowPos"], "Ihigh": RetPulseIV["Ihigh"], "VthPos": RetPulseIV["VthPos"], "VthNeg": RetPulseIV["VthNeg"]})

        if ReadCycles > 0:
        
            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
            if stop:    
                eChar.finished.put(True)
                break
            
            eChar.Selstart.put(eChar.curCycle)
            eChar.wgfmu.clearLibrary()

            eChar.wgfmu.programRectangularPulse(PulseChn, tread, tfallread, triseread, tbase, Vlow, 0, measure=ExtractReads, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="ReadLow", WriteHeader=False)
            eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Ground", WriteHeader=False)
            
            eChar.wgfmu.programRectangularPulse(PulseChn, tread, tfallread, triseread, tbase, Vhigh, 0, measure=ExtractReads, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="ReadHigh", WriteHeader=False)
            eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Ground", WriteHeader=False)
        
            #Pulse Channel
            eChar.wgfmu.createMergedPattern("Pulse_%d" %(PulseChn),"ReadLow_1_%d" %(PulseChn),"ReadHigh_3_%d" %(PulseChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.addSequence(PulseChn, "Pulse_%d" %(PulseChn), ReadCycles)

            #Ground Channel
            eChar.wgfmu.createMergedPattern("Ground_%d" %(GroundChn),"Ground_2_%d" %(GroundChn),"Ground_4_%d" %(GroundChn), eChar.wgfmu.WGFMU_AXIS_TIME)
            eChar.wgfmu.addSequence(GroundChn, "Ground_%d" %(GroundChn), ReadCycles)
    
            #pattern = eChar.wgfmu.getPatternForceValues("Pulse_201", 0)
            eChar.wgfmu.synchronize()

            for k in range(5):
                ret = eChar.wgfmu.executeMeasurement()
                lengths = LengthOfReturn(ret)

                print("length", list(lengths), len(set(lengths)))
                if len(set(lengths)) == 1:
                    break
                else:
                    print("error occured during executeMeasurement - Lengths: %s" %(lengths))

            if n == 0: 
                eChar.writeHeader("Selector", eChar.wgfmu.getHeader())

            if ExtractReads:
                low = True
                Data = []
                for r in ret:
                    Data.append(r['Data'])

                Rlow = []
                Rhigh = []
                Ilow = []
                Ihigh = []
                
                for l in range(len(Data[0])):
                    if low: 
                        Rlow.append(float(abs(Data[chns["v"]][l]/Data[chns["i"]][l])))
                        Ilow.append(-Data[chns["i"]][l])
                        low = False
                    else:
                        Rhigh.append(float(abs(Data[chns["v"]][l]/Data[chns["i"]][l])))
                        Ihigh.append(-Data[chns["i"]][l])
                        low = True

                eChar.curCycle = eChar.curCycle + ReadCycles
                eChar.Selstop.put(eChar.curCycle-1)
                eChar.SelectorEndurance.put({"Type": "Read", "Rlow": Rlow, "Rhigh": Rhigh, "Ilow": Ilow, "Ihigh": Ihigh})

    eChar.finished.put(True)

    for thr in eChar.threads:
        while thr.is_alive():
            thr.join()

    if WriteHeader:
        eChar.extendHeader('Combined',eChar.getHeader("Endurance"))

    return True 

###########################################################################################################################

def SelectorPulseIV(eChar, PulseChn, GroundChn, Vhigh, VlowMeas, delay, trise, tfall, tread, tbase, MeasPoints, Cycles, Primary=True, WriteHeader=True, DoYield=True):
    """
    Measurement to characterize Selector devices with pulse IV
    please set the appropriate Channel properties beforehand via 'setChannelParameter()'
    GroundChn: Ground channel number
    PulseChn:  Pulse channel number
    Vhigh:      Pulse High Voltage/Read Voltage
    Vlow:       Pulse Read Low Voltage
    delay:      delay before measurement starts
    trise:      rise time
    tfall:      fall time
    tread:      Read Pulse width
    tbase:      base time
    MeasPoints: Number of Measurement points during Set and Reset
    cycles:    Number of IV cycles
    WriteHeader: Enable/Disable writing the header into overlaying summary output files
    """
    
    eChar.updateTime()
    #count-=1
    tfallread = tread * 0.1
    triseread = tread * 0.1

    tmstart = tbase/2 + tfallread
    tmend = tbase/2 + tfallread + tread
    duration = sum([tbase,tfallread,triseread,tread])
    tbaseHalf = tbase/2
    
    durationPul = sum([trise,tfall,tbase])
    endTimeR = tbaseHalf+trise+tfall

    if PulseChn < GroundChn:
        chns = {'tv': 0, 'v': 1, 'ti': 2, 'i': 3}
    else:
        chns = {'tv': 2, 'v': 3, 'ti': 0, 'i': 1}

    eChar.wgfmu.clearLibrary()

    eChar.wgfmu.programTriangularPulse(PulseChn, trise, tfall, tbase, Vhigh, 0, measure=True, mPoints=MeasPoints, mStartTime=tbaseHalf, mEndTime=endTimeR, AddSequence=False, Name="Pulse")
    eChar.wgfmu.programGroundChn(GroundChn, durationPul, Vg=0, measure=True, mPoints=MeasPoints, mStartTime=tbaseHalf, mEndTime=endTimeR, AddSequence=False, Name="Ground")

    if Cycles > 0:
        #Pulse Channel
        eChar.wgfmu.addSequence(PulseChn, "Pulse_1_%d" %(PulseChn), Cycles)

        #Ground Channel
        eChar.wgfmu.addSequence(GroundChn, "Ground_2_%d" %(GroundChn), Cycles)

    #pattern = eChar.wgfmu.getPatternForceValues("Pulse_201", 0)
    eChar.wgfmu.synchronize()

    ret = eChar.wgfmu.executeMeasurement()
    SepData = getSelectorDataPulseIV(ret, MeasPoints, Cycles, VlowMeas, chns)
    header = eChar.wgfmu.getHeader()
    
    if WriteHeader:
        eChar.extendHeader("Combined", header)
    header.extend(eChar.getHeader("DC"))
    header.append("Measurement,RealMeasRlowPositive,%s" %(SepData['VmeasLowReal1'][0]))
    header.append("Measurement,RealMeasRlowNegative,%s" %(SepData['VmeasLowReal2'][0]))

    AvgRlow1  = np.mean(SepData['Rlow1'])
    AvgRlow2  = np.mean(SepData['Rlow2'])
    StdRlow1  = np.std(SepData['Rlow1'])
    StdRlow2  = np.std(SepData['Rlow2'])
    AvgRhigh  = np.mean(SepData['Rhigh'])
    StdRhigh  = np.std(SepData['Rhigh'])
    
    AvgIlow1  = np.mean(SepData['Ilow1'])
    AvgIlow2  = np.mean(SepData['Ilow2'])
    StdIlow1  = np.std(SepData['Ilow1'])
    StdIlow2  = np.std(SepData['Ilow2'])
    AvgIhigh  = np.mean(SepData['Ihigh'])
    StdIhigh  = np.std(SepData['Ihigh'])
    AvgVth1  = np.mean(SepData['Vth1'])
    AvgVth2 = np.mean(SepData['Vth2'])
    StdVth1  = np.std(SepData['Vth1'])
    StdVth2 = np.std(SepData['Vth2'])
    
    header.append('Measurement.Result,Average.Positive.LowResistance,%f' %(AvgRlow1))
    header.append('Measurement.Result,StandardDeviation.Positive.LowResistance,%f' %(StdRlow1))
    header.append('Measurement.Result,Average.Negative.LowResistance,%f' %(AvgRlow2))
    header.append('Measurement.Result,StandardDeviation.Negative.LowResistance,%f' %(StdRlow2))
    header.append('Measurement.Result,Average.HighResistance,%f' %(AvgRhigh))
    header.append('Measurement.Result,StandardDeviation.HighResistance,%f' %(StdRhigh))

    header.append('Measurement.Result,Average.Positive.LowCurrent,%f' %(AvgIlow1))
    header.append('Measurement.Result,StandardDeviation.Positive.LowCurrent,%f' %(StdIlow1))
    header.append('Measurement.Result,Average.Negative.LowCurrent,%f' %(AvgIlow2))
    header.append('Measurement.Result,StandardDeviation.Negative.LowCurrent,%f' %(StdIlow2))
    header.append('Measurement.Result,Average.HighCurrent,%f' %(AvgIhigh))
    header.append('Measurement.Result,StandardDeviation.HighCurrent,%f' %(StdIhigh))

    header.append('Measurement.Result,Average.Positive.ThresholdVoltage,%f' %(AvgVth1))
    header.append('Measurement.Result,StandardDeviation.Positive.ThresholdVoltage,%f' %(StdVth1))
    header.append('Measurement.Result,Average.Negative.ThresholdVoltage,%f' %(AvgVth2))
    header.append('Measurement.Result,StandardDeviation.Negative.ThresholdVoltage,%f' %(StdVth2))

    addHeader = eChar.getHeader("Additional")
    if not addHeader == []:
        header.extend(addHeader)
    else:
        header.append('Measurement,Type.Primary,PulseIV')
        header.append('Measurement,Endurance.StartPoint,%d' %(eChar.curCycle))
        header.append('Measurement,Endurance.EndPoint,%d' %(eChar.curCycle+Cycles))

    header.extend(eChar.getHeader("External"))

    newline = [None]*3
    newline[0] = 'DataName'
    newline[1] = 'Unit'
    newline[2] = 'Dimension'

    Data = []
    Vdata = []
    Idata  = []
    
    for n in range(Cycles):
        newline[0] = '%s,tv_%d, V_%d, ti_%d, I_%d' %(newline[0],n,n,n,n)
        newline[1] = '%s,s,V,s,I' %(newline[1])
        newline[2] = '%s,%d,%d,%d,%d' %(newline[2],len(SepData['tv'][n]),len(SepData['V'][n]),len(SepData['ti'][n]),len(SepData['I'][n]))
        Vdata.extend(SepData['V'][n])
        Idata.extend(SepData['I'][n])
    

    for k in range(MeasPoints):
        line = "DataValue"
        for n in range(Cycles):
            line = "%s,%e,%e,%e,%e" %(line, SepData['tv'][n][k],SepData['V'][n][k],SepData['ti'][n][k],SepData['I'][n][k])
        
        Data.append(line)
        

    header1 = cp.deepcopy(header)
    header1.extend(newline)
    eChar.writeDataToFile(header1, Data, startCyc=eChar.curCycle, endCyc=eChar.curCycle+Cycles-1)

    Data = []
    newline = [None]*3
    newline[0] = 'DataName, RlowUp, RlowDown, Rhigh, IlowUp, IlowDown, Ihigh, VmeasLowRealUp, VmeasLowRealDown, VthUp, VthDown'
    newline[1] = r'Unit, \g(W), \g(W), \g(W), A, A, A, V, V, V, V'
    newline[2] = 'Dimension, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d' %(len(SepData['Rlow1']), len(SepData['Rlow2']), len(SepData['Rhigh']), len(SepData['Ilow1']), len(SepData['Ilow2']), len(SepData['Ihigh']), len(SepData['VmeasLowReal1']), len(SepData['VmeasLowReal2']), len(SepData['Vth1']), len(SepData['Vth2']))

    VmeasLowReal1 = SepData['VmeasLowReal1'][n]
    if isinstance(SepData['VmeasLowReal1'][n], (float,int, np.float, np.int)):
        VmeasLowReal1 = "%e" %(SepData['VmeasLowReal1'][n])
    
    VmeasLowReal2 = SepData['VmeasLowReal2'][n]
    if isinstance(SepData['VmeasLowReal2'][n], (float,int, np.float, np.int)):
        VmeasLowReal2 = "%e" %(SepData['VmeasLowReal2'][n])
    
    for n in range(Cycles):
        line = "DataValue, %e,%e,%e,%e,%e,%e,%s,%s,%e,%e" %(SepData['Rlow1'][n],SepData['Rlow2'][n],SepData['Rhigh'][n],SepData['Ilow1'][n],SepData['Ilow2'][n],SepData['Ihigh'][n],VmeasLowReal1,VmeasLowReal2,SepData['Vth1'][n],SepData['Vth2'][n])
        Data.append(line)


    Typ = "SelectorPulseIVParam"
    header.extend(newline)
    eChar.writeDataToFile(header, Data, startCyc=eChar.curCycle, endCyc=eChar.curCycle+Cycles-1, Type=Typ)


    Trac = [Vdata,Idata]
    eChar.plotIVData({"Traces":Trac,  'Xaxis': True, 'Xlabel': 'Voltage (V)', "Yscale": "log", "Ylabel": 'Current (A)', 'Title': "Selector IV", "ValueName": 'IV'})
    
    res = None

    if Primary:

        Trac = [SepData['Rlow1'], SepData['Rlow2'],SepData['Rhigh']]
        eChar.plotIVData({"Add": False, "lineStyle": 'o', "lineWidth":0.5, 'Yscale': 'log',  "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of cycles', "Ylabel": 'resistance (ohm)', 'Title': "Rlow/Rhigh", "ValueName": 'Rlow/Rhigh'})

        Trac = [SepData['Vth1'],SepData['Vth2']]
        eChar.plotIVData({"Add": False, "lineStyle": 'o', "legend": ["Vth Positive", "Vth Negative"], "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of cycles', "Ylabel": 'voltage (V)', 'Title': "VthPos/VthNeg", "ValueName": 'VthPos/VthNeg'})

        VthNeg = eChar.dhValue(SepData['Vth1'], 'VthPos', Unit='V')
        VthPos = eChar.dhValue(SepData['Vth2'], 'VthNeg', Unit='V')
        Rlow1 = eChar.dhValue(SepData['Rlow1'], 'RlowPos', Unit='ohm')
        Rlow2 = eChar.dhValue(SepData['Rlow2'], 'RlowNeg', Unit='ohm')
        Rhigh = eChar.dhValue(SepData['Rhigh'], 'Rhigh', Unit='ohm')
        Ilow1 = eChar.dhValue(SepData['Ilow1'], 'IlowPos', Unit='A')
        Ilow2 = eChar.dhValue(SepData['Ilow2'], 'IlowNeg', Unit='A')
        Ihigh = eChar.dhValue(SepData['Ihigh'], 'Ihigh', Unit='A')

        arr = [Rlow1, Rlow2, Rhigh, Ilow1, Ilow2, Ihigh, VthNeg, VthPos]

        eChar.dhAddRow(arr,eChar.getCurCycle(),eChar.getCurCycle()+Cycles-1)


    else:
        
        res = {'Header':header, 'IVdata': [SepData['tv'],SepData['V'],SepData['ti'],SepData['I']], 'RlowPos':SepData['Rlow1'], 'RlowNeg':SepData['Rlow2'], 'Rhigh':SepData['Rhigh'], 'IlowPos':SepData['Ilow1'], 'IlowNeg':SepData['Ilow2'], 'Ihigh':SepData['Ihigh'], 'VthPos':SepData['Vth1'], 'VthNeg':SepData['Vth2']}

    eChar.curCycle = eChar.curCycle+Cycles

    return res 

def getSelectorDataPulseIV(data, MeasPoints, cycles, VlowMeas, chns):
    
    ret = dict()
    ret['Rlow1'] = []
    ret['Rhigh'] = []
    ret['Rlow2'] = []
    ret['Ilow1'] = []
    ret['Ilow2'] = []
    ret['Ihigh'] = []
    ret['Vth1'] = []
    ret['Vth2'] = []
    ret['VmeasLowReal1'] = []
    ret['VmeasLowReal2'] = []

    ret['tv'] = []
    ret['ti'] = []
    ret['V'] = []
    ret['I'] = []
    ret['R'] = []

    for i in range(cycles):
        
        k = i*MeasPoints
        l = i*MeasPoints+MeasPoints
        
        vout = data[chns['v']]['Data'][k:l]
        iout = data[chns['i']]['Data'][k:l]
        tout1 = data[chns['tv']]['Data'][k:l]
        tout2 = data[chns['ti']]['Data'][k:l]

        iout = np.multiply(-1,iout)
        rout = list(np.divide(vout,iout))
        
        ret['tv'].append(tout1)
        ret['ti'].append(tout2)
        ret['V'].append(vout)
        ret['I'].append(iout)
        ret['R'].append(rout)

        n = 0
        first = True
        VlowMeasReal1 = "NA"
        VlowMeasReal2 = "NA"
        Idif = 0
        Vth1 = 0
        Vth2 = 0
        Ihigh = 0
        Ilow1 = 0
        Ilow2 = 0
        Rhigh = 0
        Rlow1 = 0
        Rlow2 = 0
        shalf = False
        for v, i in zip(vout,iout):
            if not first:
                if Idif < abs(iout[n] - iout[n-1]):
                    Idif = abs(iout[n] - iout[n-1])
                    if shalf:
                        Vth1 = vout[n-1]
                    else:
                        Vth2 = vout[n-1]
            else:
                first = False

            if n == round(MeasPoints/2):
                try: 
                    Ihigh = i
                    Rhigh = abs(v/i)
                except ZeroDivisionError: 
                    Rhigh = 2e20

                shalf = True
                Idif = 0
            
            if v >= VlowMeas and VlowMeasReal1 == "NA":
                Ilow1 = i
                try:
                    Rlow1 = abs(v/i)
                except ZeroDivisionError: 
                    Rlow1 = 2e20
                VlowMeasReal1 = v

            if type(v) != str and v <= VlowMeas and VlowMeasReal2 == "NA" and VlowMeasReal1 != "NA":
                Ilow2 = i
                try: 
                    Rlow2 = abs(v/i)
                except ZeroDivisionError: 
                    Rlow2 = 2e20     

                VlowMeasReal2 = v     

            n = n+1

        ret['Rlow1'].append(Rlow1)
        ret['Rlow2'].append(Rlow2)
        ret['Rhigh'].append(Rhigh)
        ret['Ilow1'].append(Ilow1)
        ret['Ilow2'].append(Ilow2)
        ret['Ihigh'].append(Ihigh)
        ret['Vth1'].append(Vth1)
        ret['Vth2'].append(Vth2)
        ret['VmeasLowReal1'].append(VlowMeasReal1)
        ret['VmeasLowReal2'].append(VlowMeasReal2)

    return ret

def selectorOutput(eChar, WriteHeader, DoYield, MaxRowsPerFile=1e6):
    
    #seperate data until Endurance measurement is finished

    Typ = "SelectorEndurance"
    
    if DoYield:
        DoYield = eChar.DoYield      

    OutputStart = True
    RDcycStartOutput = 1
    RDcycStart = 1
    RDcycStop = 1

    OutResOn = []
    OutComp = []
    OutResOnStr = []
    OutCompStr = []

    StartCycComp = 1
    StartCycResOn = 1
    EndCyc = 1

    finished = False

    Rlow = eChar.dhValue([], 'RlowPos', Unit='ohm')
    Rhigh = eChar.dhValue([], 'Rhigh', Unit='ohm')
    Ilow = eChar.dhValue([], 'IlowPos', Unit='ohm')
    Ihigh = eChar.dhValue([], 'Ihigh', Unit='ohm')
    VthNeg = eChar.dhValue([], 'VthNeg', Unit='V')
    VthPos = eChar.dhValue([], 'VthPos', Unit='V')
    values = [Rlow, Rhigh, Ilow, Ihigh, VthNeg, VthPos]
    
    while not finished or not eChar.SelectorEndurance.empty:

        while not eChar.finished.empty():
            finished = eChar.finished.get()
        
        if not eChar.SelectorEndurance.empty():
            Data = eChar.SelectorEndurance.get()
            StartCyc = eChar.Selstart.get()
            EndCyc = eChar.Selstop.get()
       
            Rlow.extend(Data['Rlow'])
            Rhigh.extend(Data['Rhigh'])

            Ilow.extend(Data['Ilow'])
            Ihigh.extend(Data['Ihigh'])

            for n in range(len(Data["Rlow"])):
                k = [StartCyc+n, Data["Rlow"][n], Data["Rhigh"][n], Data["Ilow"][n], Data["Ihigh"][n]]
                OutResOn.append(k)
                string = "DataValue, %d, %f, %f, %f, %f" %(StartCyc+n, Data["Rlow"][n], Data["Rhigh"][n], Data["Ilow"][n], Data["Ihigh"][n])
                OutResOnStr.append(string)

            Vth = False
            
            try:
                Data['VthNeg']
                Vth = True
            except:
                None
            
            if Vth:
                VthPos.extend(Data['VthPos'])
                VthNeg.extend(Data['VthNeg'])
                for n in range(len(Data["Rlow"])):
                    k = [StartCyc+n, Data["Rlow"][n], Data["Rhigh"][n],  Data["Ilow"][n], Data["Ihigh"][n], Data["VthNeg"][n], Data["VthPos"][n]]
                    OutComp.append(k)
                    string = "DataValue, %d, %f, %f, %f, %f, %f, %f" %(StartCyc+n, Data["Rlow"][n], Data["Rhigh"][n], Data["Ilow"][n], Data["Ihigh"][n],Data["VthNeg"][n], Data["VthPos"][n])
                    OutCompStr.append(string)
                
                Trac = [Data['VthPos'], Data['VthNeg']]
                eChar.plotIVData({"Add": True, "lineStyle": 'o', "legend": ["Vth Positive", "Vth Negative"], "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of cycles', "Ylabel": 'voltage (V)', 'Title': "VthPos/VthNeg", "ValueName": 'VthPos/VthNeg'})
            
            Trac = [Data["Rlow"], Data["Rhigh"]]
            eChar.plotIVData({"Add": True, "lineStyle": 'o', "lineWidth":0.5, 'Yscale': 'log',  "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of cycles', "Ylabel": 'resistance (ohm)', 'Title': "Rlow/Rhigh",  "ValueName": 'Rlow/Rhigh'})


            if len(OutResOn) > MaxRowsPerFile or (finished and eChar.SelectorEndurance.empty()): 
                
                header = eChar.getHeader("Selector")
                header.extend(eChar.getHeader("DC"))
                header.append('Measurement,Endurance.StartPoint,%d' %(StartCycResOn))
                header.append('Measurement,Endurance.EndPoint,%d' %(EndCyc))

                header.extend(eChar.getHeader("External"))
                header.append('DataName, Cycle, Rhigh, Rlow, Ilow, Ihigh')
                header.append('Unit, #, ohm, ohm, A, A')
                header.append('Dimension, %d,%d,%d,%d' %(len(OutResOn[0]), len(OutResOn[1]), len(OutResOn[2]), len(OutResOn[3])))
                
                eChar.writeDataToFile(header, OutResOnStr, Typ="SelectorResistanceOnly", startCyc=StartCycResOn, endCyc=EndCyc)
                
                StartCycResOn = EndCyc

                OutResOn = []
                OutResOnStr = []

            if len(OutComp) > MaxRowsPerFile or (finished and eChar.SelectorEndurance.empty()): 
                
                header = eChar.getHeader("Selector")
                header.extend(eChar.getHeader("DC"))
                header.append('Measurement,Endurance.StartPoint,%d' %(StartCycComp))
                header.append('Measurement,Endurance.EndPoint,%d' %(EndCyc))

                header.extend(eChar.getHeader("External"))
                header.append('DataName, Cycle, Rhigh, Rlow, Ilow, Ihigh, VthPos, VthNeg')
                header.append('Unit, #, ohm, ohm, A, A, V, V')
                header.append('Dimension, %d,%d,%d,%d,%d,%d,%d' %(len(OutComp[0]), len(OutComp[1]), len(OutComp[2]), len(OutComp[3]), len(OutComp[4]), len(OutComp[5]), len(OutComp[6])))
                
                filename = "%s" %(eChar.getFilename('SelectorRes+Vth', StartCycComp, EndCyc))
                eChar.writeDataToFile(header, OutCompStr, Typ="SelectorRes+Vth'", startCyc=StartCycComp, endCyc=EndCyc)
                StartCycComp = EndCyc

                OutComp = []
                OutCompStr = []
                    

        tm.sleep(1)


    eChar.dhAddRow(values, 1, EndCyc)
    eChar.LogData.put("Selector Endurance: Finished Data Storage.")

def SelectorIV(eChar, SweepSMU, Vstop, steps, VlowMeas, Compl, DCSMU, DCCompl, Rep, hold, delay):
    
    Chns = [SweepSMU, DCSMU]
    VorI = [True, True]

    Double = True
    Log = False
    DCval = 0
    Vstart = 0
    Vstop
    stop = False

    Val = [0, DCval]

    IComp = []
    VComp = []

    errMsg = "SelectorIV - VlowMeas must be between Vstart and Vstop (start=%s; stop=%s; Vlowmeas=%s)" %(Vstart,Vstop,VlowMeas)

    if Vstop > 0:
        if VlowMeas > Vstop or VlowMeas < Vstart:
            raise ValueError(errMsg)
    else:
        if VlowMeas < Vstop or VlowMeas > Vstart:
            raise ValueError(errMsg)


    step = (Vstop-Vstart)/(steps-1)

    if VorI:
        Xlab = "Voltage (V)"
        Ylab = "Current (A)"
    else:
        Xlab = "Current (A)"
        Ylab = "Voltage (V)"

    IComp = [Compl, DCCompl]
    VComp = [None, None]
    
    mode = 1
    if Double == True and Log == True:
        mode = 4


    elif Double == True and Log == False:
        mode = 3
        

    elif Double == False and Log == True:
        mode = 2
    
    for r in range(Rep):

        while not eChar.Stop.empty():
            stop = eChar.Stop.get()

        if stop:    
            eChar.finished.put(True)
            return None
            
        out = eChar.B1500A.StaircaseSweepMeasurement(Chns, VorI, SweepSMU, Vstart, Vstop, steps, hold, delay, Val, VComp, IComp, Mmode=mode)
        
        try:
            Plot = [out['Data'][-1]]
            Plot.extend(out['Data'][0:-1])
        except IndexError:
            return None

        eChar.plotIVData({"Add": True, 'Xaxis': True, 'Yscale': 'log',  "Traces": Plot, 'Xlabel': Xlab, "Ylabel": Ylab, 'Title': "Selector IV", "ValueName": 'Selector IV'})
        
        rl1 = False
        rl2 = False
        VlowMeasReal = "NA"
        Rhigh = 1e20
        Rlow1 = 1e20
        Rlow2 = 1e20
        Ihigh = 0
        Ilow1 = 0
        Ilow2 = 0
        shalf = False
        Idif = 0
        Vth1 = 0
        Vth2 = 0

        first = True
        n = 0
        for v, i in zip(out['Data'][-1],out['Data'][0]):
            if not first:
                if Idif < abs(out['Data'][0][n] - out['Data'][0][n-1]):
                    Idif = abs(out['Data'][0][n] - out['Data'][0][n-1])
                    if shalf:
                        Vth1 = out['Data'][-1][n-1]
                    else:
                        Vth2 = out['Data'][-1][n-1]
            else:
                first = False

            if v == Vstop:
                try: 
                    Ihigh = i
                    Rhigh = v/i
                except ZeroDivisionError: 
                    Rhigh = 2e20

                shalf = True
                Idif = 0
            
            if v >= VlowMeas and VlowMeasReal == "NA":
                Ilow1 = i
                try: 
                    Rlow1 = v/i
                except ZeroDivisionError: 
                    Rlow1 = 2e20

                VlowMeasReal = v

            if v == VlowMeasReal:
                Ilow2 = i
                try: 
                    Rlow2 = v/i
                except ZeroDivisionError: 
                    Rlow2 = 2e20                
            n = n+1

        try: 

            header = out['Header']
            
            header.append("Measurement, VlowMeas, %s" %(VlowMeas))
            header.append("Measurement, VlowMeasReal, %s" %(VlowMeasReal))
            header.append("Measurement, Repetition, %d" %(r+1))
            header.append("Measurement, Rhigh, %e" %(Rhigh))
            header.append("Measurement, Rlow1, %e" %(Rlow1))
            header.append("Measurement, Rlow2, %e" %(Rlow2))
            header.append("Measurement, Vth1, %d" %(Vth1))
            header.append("Measurement, Vth2, %d" %(Vth2))

            if VorI:
                DataName = "DataName, V1, I1, R1, I2"
                Unit = "Units, V, A, ohm, A" 
            else:
                DataName = "DataName, I1, V1, R1, I2"
                Unit = "Units, A, V, ohm, V" 

            Dimension = "Dimension, %d, %d, %d, %d" %(len(out['Data'][-1]), len(out['Data'][0]),len(out['Data'][0]), len(out['Data'][1]))
            
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

        eChar.writeDataToFile(header, data, startCyc=r+1)
                
        values = []
        values.append(eChar.dhValue(Rlow1, "Rlow1", Unit='ohm'))
        values.append(eChar.dhValue(Rlow2, "Rlow2", Unit='ohm'))
        values.append(eChar.dhValue(Rhigh, "Rhigh", Unit='ohm'))
        values.append(eChar.dhValue(Vstop, "Vhigh", Unit='V'))
        values.append(eChar.dhValue(VlowMeasReal, "Vlow", Unit='V'))
        values.append(eChar.dhValue(Ilow1, "Ilow1", Unit='I'))
        values.append(eChar.dhValue(Ilow2, "Ilow2", Unit='I'))
        values.append(eChar.dhValue(Ihigh, "Ihigh", Unit='I'))
        values.append(eChar.dhValue(Ihigh, "Vth1", Unit='V'))
        values.append(eChar.dhValue(Ihigh, "Vth2", Unit='V'))

        eChar.dhAddRow(values)

def LengthOfReturn(ret):

    lengths = []
    for r in ret:
        lengths.append(len(r['Data']))
    
    return lengths