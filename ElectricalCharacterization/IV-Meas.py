'''
This file contains IV characterization definitions from Karsten Beckmann
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

MaxSweepStatisticValues = 10


def SpotMeas(eChar, SMUs, VorI, Val, Compl, hold, delay):
    ##########
    # SMUs - SUM array - separated by ","
    # VorI -  Voltage or current array - separated by "," - use strings "V" and "I"
    # Val -  Value array - separated by "," - in V for voltage and A for current source
    # Compl -  SUM array - separated by "," - in A for voltage and V for current source
    # hold - hold before the value is forced in s (float)
    # delay - delay after the value is forced and before the measurement is taken in s (float)


    Typ = 'SpotMeasurement'
    title = "IV Spot"

    IComp = []
    VComp = []
    IRange = []

    Xlab = "Measurement #"
    if VorI:
        Ylab = "Current (A)"
    else:
        Ylab = "Voltage (V)"

    for n in range(len(Val)):
        if VorI:
            IComp.append(Compl[n])
            VComp.append(None)
        else:
            IComp.append(None)
            VComp.append(Compl[n])
        IRange.append(11)
    
    out = eChar.B1500A.SpotMeasurement(SMUs, VorI, Val, RI=IRange, VComp=VComp, IComp=IComp, hold=hold, delay=delay)
    data = out['Data']
    lat = data[0][-1]

    eChar.plotIVData({"Add": True, 'Yscale': 'log',  "Traces": lat, 'Xlabel': Xlab, "Ylabel": Ylab, 'Title': title, "MeasurementType": Typ, "ValueName": title})
    
    try: 

        header = out['Header']
        
        header.insert(0,"TestParameter,Measurement.Type,%s" %(Typ))
        header.append("Measurement,Device,%s" %(eChar.device))
        header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.localtime)))
        header.append("Measurement,Initial Delay,%d" %(delay))

        DataName = "DataName" 
        Unit = "Units"
        Dimension = "Dimension" 

        for n in range(len(VorI)):
            if VorI[n]:
                DataName = "%s, I%d" %(DataName, SMUs[n])
                Unit = "%s, A" %(Unit)
            else:
                DataName = "%s, V%d" %(DataName, SMUs[n])
                Unit = "%s, V" %(Unit)

            Dimension = "%s, %d" %(Dimension, len(data[n]))

        DataName = "%s, R%d" %(DataName, SMUs[0])
        Unit = "%s, ohm" %(Unit)

        Dimension = "%s, %d" %(Dimension, len(data[0]))
        
        header.append(DataName)
        header.append(Unit)
        header.append(Dimension)

    except UnboundLocalError as e: 
        print(eChar.ErrorQueue.put("IVmeas = %s: %s" %(Typ, e)))
        
    output = []
    if type(data) == list:
        if len(data) > 0:
            for n in range(len(data[0])):
                line = "DataValue"

                for ent in data:
                    
                    line = "%s, %e" %(line, ent[n])
                    
                    try:
                        a = ent[n]
                        b = Val[0]
                        if VorI[0]:
                            res = abs(b/a)
                        else:
                            res = abs(a/b)

                    except ZeroDivisionError:
                        res = 1e20

                    line = "%s, %e" %(line, res)

                output.append(line)

    eChar.writeDataToFile(header, output, Typ=Typ, startCyc=0, endCyc=1)
    
    values = []

    for m in range(len(data)):
        name = "R%d" %(SMUs[m])

        try:
            a = np.array(data[m])
            b = Val[0]
            if VorI[0]:
                calcRes = np.absolute(np.divide(b,a, out=np.full(len(a), 2e20, dtype=float), where=a!=0))
            else:
                calcRes = np.absolute(np.divide(a,b, out=np.full(len(a), 2e20, dtype=float), where=a!=0))

        except ZeroDivisionError:
            calcRes = 2e20
        values.append(eChar.dhValue(calcRes, name,Unit='ohm'))
    
        if VorI:
            name = "I%d" %(SMUs[m])
            unit = "A"
        else:
            name = "V%d" %(SMUs[m])
            unit = "V"

        values.append(eChar.dhValue(data[m], name, Unit=unit))
    eChar.dhAddRow(values, Typ)




def SpotMeasE5274A(eChar, SMUs, VorI, Val, Compl, delay):
    Typ = 'SpotMeasurementE5274A'

    IComp = []
    VComp = []

    if VorI:
        Xlab = "Voltage (V)"
        Ylab = "Current (A)"
    else:
        Xlab = "Current (A)"
        Ylab = "Voltage (V)"

    for n in range(len(Val)):
        if VorI:
            IComp.append(Compl[n])
            VComp.append(None)
        else:
            IComp.append(None)
            VComp.append(Compl[n])
    
    out = eChar.E5274A.SpotMeasurement(SMUs, VorI, Val, VComp=VComp, IComp=IComp)
    
    Plot = out['Data'][0]

    eChar.plotIVData({"Add": False, 'Yscale': 'lin',  "Traces": Plot, 'Xlabel': Xlab, "Ylabel": Ylab, 'Title': "IV Spot", "MeasurementType": Typ, "ValueName": 'IV Spot'})
            
    try: 

        header = out['Header']
        
        header.insert(0,"TestParameter,Measurement.Type,%s" %(Typ))
        header.append("Measurement,Device,%s" %(eChar.device))
        header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.localtime)))

        DataName = "DataName" 
        Unit = "Units" 
        Dimension = "Dimension"

        for n in range(len(VorI)):
            if VorI[n]:
                DataName = "%s, I%d" %(DataName, SMUs[n])
                Unit = "%s, A" %(Unit)
            else:
                DataName = "%s, V%d" %(DataName, SMUs[n])
                Unit = "%s, V" %(Unit)

            Dimension = "%s, %d" %(Dimension, len(out['Data'][n]))
        
        header.append(DataName)
        header.append(Unit)
        header.append(Dimension)

    except UnboundLocalError as e: 
        None

    data = []
    if type(out["Data"]) == list:
        if len(out['Data']) > 0:
            for n in range(len(out['Data'][0])):
                line = "DataValue"

                for ent in out['Data']:
                    line = "%s, %e" %(line, ent[n])
                
                data.append(line)

    eChar.writeDataToFile(header, data, Typ=Typ, startCyc=0, endCyc=1)
    
    for n in range(len(out['Data'][0])):
        name = "R%d" %(SMUs[n])
        
        try:
            if VorI[0]:
                calcRes = (Val[0]/out['Data'][0][n])
            else:
                calcRes = abs(out['Data'][0][n]/Val[0])
        except ZeroDivisionError:
            calcRes = 2e20

    
        if VorI:
            name = "I1"
            unit = "A"
        else:
            name = "V1"
            unit = "V"


        values = []
        values.append(eChar.dhValue(calcRes, name,Unit='ohm'))
        values.append(eChar.dhValue(out['Data'][0][n], name, Unit=unit))
        eChar.dhAddRow(values, Typ)


def IVsweep(eChar, SweepSMU, start, stop, steps, VorI, Compl, Double, Log, DCSMUs, DCval, DCVorI, DCCompl, hold, delay):

    Typ = 'IV-sweep'
    
    Chns = [SweepSMU]
    Chns.extend(DCSMUs)

    if len(DCSMUs) > 1:
        if len(DCval) == 1:
             DCval = [DCval[0]]*len(DCSMUs)
        if len(DCCompl) == 1:
             DCCompl = [DCCompl[0]]*len(DCSMUs)
        if len(DCVorI) == 1:
             DCVorI = [DCVorI[0]]*len(DCSMUs)

    VorI = [VorI]
    VorI.extend(DCVorI)

    Val = [0]
    Val.extend(DCval)
    
    IComp = []
    VComp = []

    step = (stop-start)/(steps-1)

    if VorI:
        Xlab = "Voltage (V)"
        Ylab = "Current (A)"
    else:
        Xlab = "Current (A)"
        Ylab = "Voltage (V)"

    for n in range(len(DCval)+1):
        if n == 0:
            if VorI[n]:
                IComp.append(Compl)
                VComp.append(None)
            else:
                IComp.append(None)
                VComp.append(Compl)
        else:
            if VorI[n]:
                IComp.append(DCCompl[n-1])
                VComp.append(None)
            else:
                IComp.append(None)
                VComp.append(DCCompl[n-1])
    
    mode = 1
    if Double == True and Log == True:
        mode = 4


    elif Double == True and Log == False:
        mode = 3
        

    elif Double == False and Log == True:
        mode = 2
    
    out = eChar.B1500A.StaircaseSweepMeasurement(Chns, VorI, SweepSMU, start, stop, steps, hold, delay, Val, VComp, IComp, Mmode=mode)
    
    try:
        if VorI[0]:
            Plot = [out['Data'][-1]]
            Plot.extend(out['Data'][0:-1])
        else:
            Plot = out['Data'][:]
    except IndexError:
        return None

    eChar.plotIVData({"Add": False, 'Xaxis': True, 'Yscale': 'lin',  "Traces": Plot, 'Xlabel': Xlab, "Ylabel": Ylab, 'Title': "IV Sweep", "MeasurementType": Typ, "ValueName": 'IV Sweep'})
            
    try: 

        header = out['Header']
        
        header.insert(0,"TestParameter,Measurement.Type,%s" %(Typ))
        header.append("Measurement,Device,%s" %(eChar.device))
        header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.localtime)))

        if VorI[0]:
            DataName = "DataName, V1, I1" 
            Unit = "Units, V, A" 
            Dimension = "Dimension, %d, %d" %(len(out['Data'][-1]), len(out['Data'][0]))
        else:
            DataName = "DataName, I1, V1" 
            Unit = "Units, V, A" 
            Dimension = "Dimension, %d, %d" %(len(out['Data'][0]), len(out['Data'][1]))

        

        for n in range(len(DCVorI)):
            if DCVorI[n]:
                DataName = "%s, I%d" %(DataName, n+2)
                Dimension = "%s, %d" %(Dimension, len(out['Data'][n+1]))
                Unit = "%s, A" %(Unit)
            else:
                DataName = "%s, V%d" %(DataName, n+2)
                Unit = "%s, V" %(Unit)
                Dimension = "%s, %d" %(Dimension, len(out['Data'][n+2]))

        
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

    iterate = createIterationRange(len(out['Data'][0]))
    values = []     
    for n in iterate:
        
        if VorI:
            name = "I%d@%.2eV" %(SweepSMU, out['Data'][-1][n])
            nameR = "R%d@%.2eV" %(SweepSMU, out['Data'][-1][n])
            unit = "A"
        else:
            name = "V%d@%.2eA" %(SweepSMU, out['Data'][-1][n])
            nameR = "R%d@%.2eA" %(SweepSMU, out['Data'][-1][n])
            unit = "V"

        try:
            if VorI:
                calcRes = (out['Data'][-1][n]/out['Data'][0][n])
            else:
                calcRes = (out['Data'][0][n]/out['Data'][-1][n])
        except ZeroDivisionError:
            calcRes = 2e20

        values.append(eChar.dhValue(out['Data'][0][n], name, Unit=unit))
        values.append(eChar.dhValue(calcRes, nameR, Unit='ohm'))

    eChar.dhAddRow(values, Typ)
    
def IVsweepE5274A(eChar, SweepSMU, start, stop, steps, VorI, Compl, Double, Log, DCSMUs, DCval, DCVorI, DCCompl, hold, delay):

    Typ = 'IV-sweepE5274A'
    
    Chns = [SweepSMU]
    Chns.extend(DCSMUs)
    
    if len(DCSMUs) > 1:
        if len(DCval) == 1:
             DCval = [DCval[0]]*len(DCSMUs)
        if len(DCCompl) == 1:
             DCCompl = [DCCompl[0]]*len(DCSMUs)
        if len(DCVorI) == 1:
             DCVorI = [DCVorI[0]]*len(DCSMUs)
             
    VorI = [VorI]
    VorI.extend(DCVorI)

    Val = [0]
    Val.extend(DCval)

    IComp = []
    VComp = []

    step = (stop-start)/(steps-1)

    if VorI:
        Xlab = "Voltage (V)"
        Ylab = "Current (A)"
    else:
        Xlab = "Current (A)"
        Ylab = "Voltage (V)"

    for n in range(len(DCval)+1):
        if n == 0:
            if VorI:
                IComp.append(Compl)
                VComp.append(None)
            else:
                IComp.append(None)
                VComp.append(Compl)
        else:
            if VorI:
                IComp.append(DCCompl[n-1])
                VComp.append(None)
            else:
                IComp.append(None)
                VComp.append(DCCompl[n-1])
    
    mode = 1
    if Double == True and Log == True:
        mode = 4


    elif Double == True and Log == False:
        mode = 3
        

    elif Double == False and Log == True:
        mode = 2
    
    out = eChar.E5274A.StaircaseSweepMeasurement(Chns, VorI, SweepSMU, start, stop, steps, hold, delay, Val, VComp, IComp, Mmode=mode)
    
    
    Plot = [out['Data'][-1]]
    Plot.extend(out['Data'][0:-1])

    n = 0
    for k in DCVorI:
        if k == VorI:
            Plot.append(out['Data'][n+1])
        n = n+1

    eChar.plotIVData({"Add": False, 'Xaxis': True, 'Yscale': 'lin',  "Traces": Plot, 'Xlabel': Xlab, "Ylabel": Ylab, 'Title': "IV Sweep", "MeasurementType": Typ, "ValueName": 'IV Sweep'})
            
    try: 

        header = out['Header']
        
        header.insert(0,"TestParameter,Measurement.Type,%s" %(Typ))
        header.append("Measurement,Device,%s" %(eChar.device))
        header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.localtime)))

        if VorI:
            DataName = "DataName,V1,I1"
            Unit = "Units,V,A" 
        else:
            DataName = "DataName,I1,V1"
            Unit = "Units,A,V" 
        Dimension = "Dimension,%d,%d" %(len(out['Data'][-1]), len(out['Data'][0]))

        for n in range(len(DCVorI)):
            if DCVorI[n]:
                DataName = "%s, I%d" %(DataName, n+2)
                Unit = "%s, A" %(Unit)
            else:
                DataName = "%s, V%d" %(DataName, n+2)
                Unit = "%s, V" %(Unit)

            Dimension = "%s, %d" %(Dimension, len(out['Data'][n+1]))
        
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

    iterate = createIterationRange(len(out['Data'][0]))
       
    values = []     
    for n in iterate:
        
        if VorI:
            name = "I%d@%.2eV" %(SweepSMU, out['Data'][-1][n])
            nameR = "R%d@%.2eV" %(SweepSMU, out['Data'][-1][n])
            unit = "A"
        else:
            name = "V%d@%.2eA" %(SweepSMU, out['Data'][-1][n])
            nameR = "R%d@%.2eA" %(SweepSMU, out['Data'][-1][n])
            unit = "V"

        try:
            if VorI:
                calcRes = (out['Data'][-1][n]/out['Data'][0][n])
            else:
                calcRes = (out['Data'][0][n]/out['Data'][-1][n])
        except ZeroDivisionError:
            calcRes = 2e20

        values.append(eChar.dhValue(out['Data'][0][n], name, Unit=unit))
        values.append(eChar.dhValue(calcRes, nameR, Unit='ohm'))

    eChar.dhAddRow(values, Typ)
    
def createIterationRange(dataLength):
    
    iterate = []
    if dataLength > MaxSweepStatisticValues:

        x = dataLength / MaxSweepStatisticValues
        x = ma.floor(x)

        y = (dataLength % MaxSweepStatisticValues) / MaxSweepStatisticValues
        
        yAdd = 0

        for n in range(MaxSweepStatisticValues - 1):
            iterate.append(int(x*n + ma.ceil(yAdd)))
            yAdd = yAdd + y

        iterate.append(dataLength-1)

    else:
        iterate = range(dataLength)

    return iterate

###########################################################################################################################

def setDCVoltages(eChar,SMUs=None, Vdc=None, DCcompl=None, WriteHeader=True):
    VorI = []
    IVal = []
    for n in range(len(SMUs)):
        VorI.append(True)
        IVal.append(0)
    
    RI=-19
    eChar.B1500A.setRemoteExecute()
    ret = eChar.B1500A.SpotMeasurement(SMUs,VorI,Vdc,IVal,IComp=DCcompl,RI=RI)
    eChar.B1500A.remoteExecute()
    eChar.B1500A.setDirectExecute()
    eChar.DCHeader = ret['Header']
    if WriteHeader:
        eChar.Combinedheader.extend(ret['Header'])

###########################################################################################################################

def setDCVoltE5274(eChar,SMUs=None, Vdc=None, DCcompl=None, WriteHeader=True):
    tm.sleep(1)
    VorI = []
    IVal = []
    for n in range(len(SMUs)):
        VorI.append(True)
        IVal.append(0)
    
    RI=-19
    eChar.E5274A.setRemoteExecute()
    ret = eChar.E5274A.SpotMeasurement(SMUs,VorI,Vdc,IVal,IComp=DCcompl,RI=RI)
    eChar.E5274A.remoteExecute()
    eChar.E5274A.setDirectExecute()
    if WriteHeader:
        eChar.Combinedheader.extend(ret['Header'])

###########################################################################################################################

def RepeatSpotMeas(eChar, SMUs, VorI, Val, Compl, delay, sleep, numOfReapeats):
    ##########
    # SMUs - SUM array - separated by ","
    # VorI -  Voltage or current array - separated by "," - use strings "V" and "I"
    # Val -  Value array - separated by "," - in V for voltage and A for current source
    # Compl -  SUM array - separated by "," - in A for voltage and V for current source
    # delay - delay before the start of the measurement
    # sleep - wait time before each repeat in s (float)
    # numOfRepeats - number of repeats (int)
    

    Typ = 'RepeatSpotMeasurement'
    title = "IV Spot Repeat"

    IComp = []
    VComp = []
    IRange = []

    Xlab = "Measurement #"
    if VorI:
        Ylab = "Current (A)"
    else:
        Ylab = "Voltage (V)"

    for n in range(len(Val)):
        if VorI:
            IComp.append(Compl[n])
            VComp.append(None)
        else:
            IComp.append(None)
            VComp.append(Compl[n])
        IRange.append(11)
    
    tm.sleep(delay)
    data = None
    for n in range(numOfReapeats):
        out = eChar.B1500A.SpotMeasurement(SMUs, VorI, Val, RI=IRange, VComp=VComp, IComp=IComp, hold=sleep)
        if data == None:
            data = out['Data']
        else:
            for d1, d2 in zip(data, out['Data']):
                d1.extend(d2)

        lat = data[0][-1]

        eChar.plotIVData({"Add": True, 'Yscale': 'log',  "Traces": lat, 'Xlabel': Xlab, "Ylabel": Ylab, 'Title': title, "MeasurementType": Typ, "ValueName": title})
        if eChar.checkStop():
            break

    try: 

        header = out['Header']
        
        header.insert(0,"TestParameter,Measurement.Type,%s" %(Typ))
        header.append("Measurement,Device,%s" %(eChar.device))
        header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.localtime)))
        header.append("Measurement,Initial Delay,%d" %(delay))

        DataName = "DataName" 
        Unit = "Units"
        Dimension = "Dimension" 

        for n in range(len(VorI)):
            if VorI[n]:
                DataName = "%s, I%d" %(DataName, SMUs[n])
                Unit = "%s, A" %(Unit)
            else:
                DataName = "%s, V%d" %(DataName, SMUs[n])
                Unit = "%s, V" %(Unit)

            Dimension = "%s, %d" %(Dimension, len(data[n]))

        DataName = "%s, R%d" %(DataName, SMUs[0])
        Unit = "%s, ohm" %(Unit)

        Dimension = "%s, %d" %(Dimension, len(data[0]))
        
        header.append(DataName)
        header.append(Unit)
        header.append(Dimension)

    except UnboundLocalError as e: 
        print(eChar.ErrorQueue.put("IVmeas = %s: %s" %(Typ, e)))
        
    output = []
    if type(data) == list:
        if len(data) > 0:
            for n in range(len(data[0])):
                line = "DataValue"

                for ent in data:
                    
                    line = "%s, %e" %(line, ent[n])
                    
                    try:
                        a = ent[n]
                        b = Val[0]
                        if VorI[0]:
                            res = abs(b/a)
                        else:
                            res = abs(a/b)

                    except ZeroDivisionError:
                        res = 1e20

                    line = "%s, %e" %(line, res)

                output.append(line)

    eChar.writeDataToFile(header, output, Typ=Typ, startCyc=0, endCyc=1)
    
    values = []

    for m in range(len(data)):
        name = "R%d" %(SMUs[m])

        try:
            a = np.array(data[m])
            b = Val[0]
            if VorI[0]:
                calcRes = np.absolute(np.divide(b,a, out=np.full(len(a), 2e20, dtype=float), where=a!=0))
            else:
                calcRes = np.absolute(np.divide(a,b, out=np.full(len(a), 2e20, dtype=float), where=a!=0))

        except ZeroDivisionError:
            calcRes = 2e20
        values.append(eChar.dhValue(calcRes, name,Unit='ohm'))
    
        if VorI:
            name = "I%d" %(SMUs[m])
            unit = "A"
        else:
            name = "V%d" %(SMUs[m])
            unit = "V"

        values.append(eChar.dhValue(data[m], name, Unit=unit))
    eChar.dhAddRow(values, Typ)

