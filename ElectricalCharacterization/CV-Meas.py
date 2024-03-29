'''
This file contains CV characterization definitions from Karsten Beckmann
kbeckmann@sunypoly.edu
'''

import time as tm
import StdDefinitions as std
import DataHandling as dh
import threading as th
import math as ma
import numpy as np
import queue as qu
import copy as cp

def C_SpotMeas(eChar, CMU, freq, Vac, Vdc, SMUs, VorI, Val, Compl, delay):
    Typ = 'SpotCMeasurement'

    IComp = []
    VComp = []


    for n in range(len(Val)):
        if VorI:
            IComp.append(Compl[n])
            VComp.append(None)
        else:
            IComp.append(None)
            VComp.append(Compl[n])

    out = eChar.B1500A.SpotCMeasurement(CMU, freq, Vac, Vdc, SMUs=SMUs, VorI=VorI, Val=Val, VComp=VComp, IComp=IComp, VMon=False)
    
    Plot = [[out['Data'][3][0]], [out['Data'][0][0]]]

    Xlab = "Voltage (V)" 
    Ylab = "%s (%s)" %(out['Name'][0], out['Unit'][0])

    eChar.plotIVData({"Add": False, 'Yscale': 'lin', 'Xaxis': True, "Traces": Plot, 'Xlabel': Xlab, "Ylabel": Ylab, 'Title': "C Spot", "MeasurementType": Typ, "ValueName": 'IV Spot'})
            
    try: 
        header = out['Header']
        
        header.insert(0,"TestParameter,Measurement.Type,%s" %(Typ))
        header.append("Measurement,Device,%s" %(eChar.device))
        header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.localtime)))

        DataName = "DataName, %s, %s, Osc_level, DC_bias" %(out['Name'][0], out['Name'][1]) 
        Unit = "Units, %s, %s, V, V" %(out['Unit'][0], out['Unit'][1]) 
        Dimension = "Dimension, %d, %d, %d, %d" %(1,1,1,1)
        
        header.append(DataName)
        header.append(Unit)
        header.append(Dimension)

    except UnboundLocalError: 
        None

    data = []
    if type(out["Data"]) == list:
        data.append("DataValue, %e, %e, %e, %e" %(out['Data'][0][0],out['Data'][1][0],out['Data'][2][0],out['Data'][3][0]))


    eChar.writeDataToFile(header, data, eChar.getFolder(), eChar.getFilename(Typ, 0, 1))
    
    resis = [None]*4
    resis[0] = eChar.dhValue(out['Data'][0][0], out['Name'][0], Unit=out['Unit'][0])
    resis[1] = eChar.dhValue(out['Data'][1][0], out['Name'][1], Unit=out['Unit'][1])
    resis[2] = eChar.dhValue(out['Data'][2][0], "Osc. Level", Unit="V")
    resis[3] = eChar.dhValue(out['Data'][3][0], "DC bias", Unit="V")

    row = eChar.dhAddRow(resis,Typ)

def CVsweep(eChar, CMU, freq, Vac, start, stop, steps, Double, Log, hold, delay, DCSMUs, DCVorI, DCval, DCCompl):

    Typ = 'CV-sweep'

    Chns = DCSMUs
    VorI = DCVorI

    Val = DCval

    IComp = []
    VComp = []

    Xlab = "Voltage (V)"

    for n in range(len(Chns)):
        if VorI:
            IComp.append(DCCompl[n])
            VComp.append(None)
        else:
            IComp.append(None)
            VComp.append(DCCompl[n])
    
    mode = 1
    if Double == True and Log == True:
        mode = 4

    elif Double == True and Log == False:
        mode = 3

    elif Double == False and Log == True:
        mode = 2
        
    out = eChar.B1500A.CVSweepMeasurement(CMU, freq, Vac, start, stop, steps, mode, hold, delay, SMUs=Chns, Val=Val, VorI=VorI, VComp=VComp, IComp=IComp, VMon=False)
    
    Plot = [out['Data'][-1]]
    Plot.append(out['Data'][0])
    Ylab = "%s (%s)" %(out['Name'][0], out['Unit'][0])
    Title = "%s-V Sweep" %(out['Name'][0])
    eChar.plotIVData({"Add": False, 'Yscale': 'lin', "Xaxis":True, "Traces": Plot, 'Xlabel': Xlab, "Ylabel": Ylab, 'Title': Title,  "MeasurementType": Typ, "ValueName": 'CV Sweep'})

    Plot2 = [out['Data'][-1]]
    Plot2.append(out['Data'][1])
    Ylab2 = "%s (%s)" %(out['Name'][1], out['Unit'][1])
    Title2 = "%s-V Sweep" %(out['Name'][1])
    eChar.plotIVData({"Add": False, 'Yscale': 'lin', "Xaxis":True,  "Traces": Plot2, 'Xlabel': Xlab, "Ylabel": Ylab2, 'Title': Title2, "MeasurementType": Typ, "ValueName": 'CV Sweep'})
    

    try: 

        header = out['Header']
        
        header.insert(0,"TestParameter,Measurement.Type,%s" %(Typ))
        header.append("Measurement,Device,%s" %(eChar.device))
        header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.localtime)))

        DataName = "DataName, V, %s, %s, Osc_level, DC_bias" %(out['Name'][0], out['Name'][1]) 
        Unit = "Units, V, %s, %s, V, V" %(out['Unit'][0], out['Unit'][1]) 
        Dimension = "Dimension, %d, %d, %d, %d, %d" %(len(out['Data'][-1]), len(out['Data'][0]), len(out['Data'][1]), len(out['Data'][2]), len(out['Data'][3]))
        
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
    
    for n in range(len(out['Data'][0])):
        if VorI:
            name = "I@%.2eV" %(out['Data'][-1][n])
        else:
            name = "V@%.2eA" %(out['Data'][-1][n])
        resis = eChar.dhValue(out['Data'][0][n], name, Unit='ohm')

    row = eChar.dhAddRow([resis],Typ)

###########################################################################################################################

def CFsweep(eChar, CMU, fStart, fStop, steps, Double, Log, Vac, Vdc, hold, delay, SMUs, VorI, Val, Compl):

    Typ = 'CF-sweep'

    IComp = []
    VComp = []

    Xlab = "Frequency (f)"

    for n in range(len(SMUs)):
        if VorI:
            IComp.append(Compl[n])
            VComp.append(None)
        else:
            IComp.append(None)
            VComp.append(Compl[n])
    
    mode = 1
    if Double == True and Log == True:
        mode = 4

    elif Double == True and Log == False:
        mode = 3

    elif Double == False and Log == True:
        mode = 2

    freqs = []
    if Log: 
        fStopLog = np.log10(fStop)
        fStartLog = np.log10(fStart)
        fstepLog = (fStopLog - fStartLog)/(steps-1)
        for n in range(steps):
            stepVal = fStartLog+n*fstepLog
            f = np.power(10,stepVal)
            freqs.append(f)
        xScale = "log"
    else:
        fstep = (fStop - fStart)/(steps-1)
        for n in range(steps):
            stepVal = fStart+n*fstep
            f = np.power(10,stepVal)
            freqs.append(f)
        xScale = "lin"

    n = 0
    for freq in freqs:
        outTemp = eChar.B1500A.SpotCMeasurement(CMU, freq, Vac, Vdc, SMUs=SMUs, VorI=VorI, Val=Val, VComp=VComp, IComp=IComp, VMon=False)
        
        if n == 0: 
            out = outTemp
        else:
            for n in range(4):
                out['Data'][n].append(outTemp['Data'][n][0])

        n = n +1 

    Plot = [freqs]
    Plot.append(out['Data'][0])
    Ylab = "%s (%s)" %(out['Name'][0], out['Unit'][0])
    Title = "%s-F Sweep" %(out['Name'][0])
    eChar.plotIVData({"Add": False, 'Yscale': 'lin', 'Xscale':xScale, "Xaxis":True, "Traces": Plot, 'Xlabel': Xlab, "Ylabel": Ylab, 'Title': Title,  "MeasurementType": Typ, "ValueName": 'CF Sweep'})

    Plot2 = [freqs]
    Plot2.append(out['Data'][1])
    Ylab2 = "%s (%s)" %(out['Name'][1], out['Unit'][1])
    Title2 = "%s-F Sweep" %(out['Name'][1])
    eChar.plotIVData({"Add": False, 'Yscale': 'lin', "Xaxis":True, 'Xscale': xScale,  "Traces": Plot2, 'Xlabel': Xlab, "Ylabel": Ylab2, 'Title': Title2, "MeasurementType": Typ, "ValueName": 'CF Sweep'})
    

    try: 

        header = out['Header']
        
        header.insert(0,"TestParameter,Measurement.Type,%s" %(Typ))
        header.append("Measurement,Device,%s" %(eChar.device))
        header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.localtime)))

        DataName = "DataName, F, %s, %s, Osc_level, DC_bias" %(out['Name'][0], out['Name'][1]) 
        Unit = "Units, Hz, %s, %s, V, V" %(out['Unit'][0], out['Unit'][1]) 
        Dimension = "Dimension, %d, %d, %d, %d, %d" %(len(freqs), len(out['Data'][0]), len(out['Data'][1]), len(out['Data'][2]), len(out['Data'][3]))
        
        header.append(DataName)
        header.append(Unit)
        header.append(Dimension)

    except UnboundLocalError: 
        None
        
    data = []
    
    for n in range(len(out['Data'][0])):
        line = "DataValue, %e" %(freqs[n])

        for m in range(len(out['Data'])-1):
            line = "%s, %e" %(line, out['Data'][m][n])
        
        data.append(line)

    eChar.writeDataToFile(header, data, Typ=Typ, startCyc=0, endCyc=1)
    
    for n in range(len(out['Data'][0])):
        if VorI:
            name = "I@%.2eV" %(out['Data'][-1][n])
        else:
            name = "V@%.2eA" %(out['Data'][-1][n])
        resis = eChar.dhValue( out['Data'][0][n], name, Unit='ohm')

    row = eChar.dhAddRow([resis],Typ)
    

###########################################################################################################################

def setDCVoltages(eChar,SMUs=None, Vdc=None, DCcompl=None, WriteHeader=True):
    tm.sleep(1)
    VorI = []
    IVal = []
    for n in range(len(SMUs)):
        VorI.append(True)
        IVal.append(0)
    
    eChar.B1500A.setRemoteExecute()
    ret = eChar.B1500A.SpotMeasurement(SMUs,VorI,Vdc,IVal,IComp=DCcompl)
    eChar.B1500A.remoteExecute()
    if WriteHeader:
        eChar.Combinedheader.extend(ret['Header'])
