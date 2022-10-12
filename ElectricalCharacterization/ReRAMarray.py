'''
This file contains ReRAM array characterization definitions from Karsten Beckmann
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


def Cycle8x8(eChar, SetChn, GNDChn, GateChn, NumofCycles, Vset, Vreset, Vread, Vgate, tset, treset, tread):

    Typ = 'Cycle_8x8'
    TypR = 'Cycle_Reset_8x8'
    TypS = 'Cycle_Set_8x8'

    Chns = [SetChn, GNDChn, GateChn]
    PulseChn = SetChn
    MeasChn = GNDChn
    Pbase = 0
    M = 8
    N = 8
    VorI = [True,True,True]
    SetVal = [Vset, 0, Vgate]
    ResetVal = [Vreset, 0, Vgate]
    readVal = [Vread, 0, Vgate]
    hold = 0
    IComp = [10e-3,10e-3,10e-3]

    ReadVal = []
    ColName = []
    
    MatrixFile = CreateInternal8x8MatrixClass(SetChn, GateChn, GNDChn)
    
    Rs = dh.Value(eChar, [], 'Rset', DoYield=eChar.DoYield, Unit='ohm')
    Rr = dh.Value(eChar, [], 'Rreset', DoYield=eChar.DoYield, Unit='ohm')

    stop = False

    for k in range(NumofCycles):
        
        if not stop:
            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
        else:
            break

        ReadVal.append([])
        ColName.append('reset')

        MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), MatrixFile, True)

        MatrixHeader = MC.getHeader()
        n = 0
        m = 0
        
        Coordinates = []

        while MC.setNext():
            
            if not stop:
                while not eChar.Stop.empty():
                    stop = eChar.Stop.get()
            else:
                break

            ###### Set 
            out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, ResetVal, Pbase, VorI, hold, treset, IComp=IComp)
            if n == 0 and m ==0:
                FormingHeader = eChar.E5274A.getHeader()

            ###### Read
            out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
            
            if n == 0 and m ==0:
                ReadHeader = eChar.E5274A.getHeader()

            ResRead = []

            try:    
                ResRead.append(abs(Vread/out['Data'][0][0]))
            except ZeroDivisionError:
                ResRead.append(2e20)

            add = ResRead
            for ent in out['Data']:
                add.append(ent[0])
            ReadVal[-1].append(cp.deepcopy(add))
            
            Rr.extend(ResRead[0])
            Coordinates.append([n+1,m+1])

            eChar.plotIVData({"Add": True, "lineStyle": 'o', 'legend': ['GND', 'Vlow', 'Vhigh'], "lineWidth":0.5, 'Yscale': 'log',  "Traces":ResRead, 'Xaxis': False, 'Xlabel': "Array Device", "Ylabel": 'Resistance ($\Omega$)', 'Title': "Array Resistance", "MeasurementType": TypR, "ValueName": 'Resistance'})
            eChar.plotIVData({"Add": True, 'Yscale': 'lin',  "Traces": ResRead, 'Map': [n,m], 'Xlabel': 'X Position', "Ylabel": 'Y Position', "Clabel": 'Resistance ($\Omega$)', 'Title': "Array Resistance", "MeasurementType": TypR, "ValueName": 'Resistance Map'})
            eChar.LogData.put("Cycle 8x8 (Reset): Device %sx%s: Resistance: %s ohm." %(n+1,m+1, ResRead))
            
            n = n+1
            if n == M: 
                m = m+1
                n = 0


        MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), MatrixFile, True)

        MatrixHeader = MC.getHeader()
        n = 0
        m = 0
        
        ReadVal.append([])
        ColName.append('set')

        while MC.setNext():
            
            if not stop:
                while not eChar.Stop.empty():
                    stop = eChar.Stop.get()
            else:
                break

            ###### Set 
            out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, SetVal, Pbase, VorI, hold, tset, IComp=IComp)
            if n == 0 and m ==0:
                FormingHeader = eChar.E5274A.getHeader()

            ###### Read
            out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
            
            if n == 0 and m ==0:
                ReadHeader = eChar.E5274A.getHeader()

            ResRead = []

            try:    
                ResRead.append(abs(Vread/out['Data'][0][0]))
            except ZeroDivisionError:
                ResRead.append(2e20)

            add = ResRead
            for ent in out['Data']:
                add.append(ent[0])
                
            ReadVal[-1].append(cp.deepcopy(add))
            Rs.extend(ResRead[0])

            eChar.plotIVData({"Add": True, "lineStyle": 'o', 'legend': ['GND', 'Vlow', 'Vhigh'], "lineWidth":0.5, 'Yscale': 'log',  "Traces":ResRead, 'Xaxis': False, 'Xlabel': "Array Device", "Ylabel": 'Resistance ($\Omega$)', 'Title': "Array Resistance", "MeasurementType": TypS, "ValueName": 'Resistance'})
            eChar.plotIVData({"Add": True, 'Yscale': 'lin',  "Traces": ResRead, 'Map': [n,m], 'Xlabel': 'X Position', "Ylabel": 'Y Position', "Clabel": 'Resistance ($\Omega$)', 'Title': "Array Resistance", "MeasurementType": TypS, "ValueName": 'Resistance Map'})
            eChar.LogData.put("Cycle 8x8 (Set): Device %sx%s: Resistance: %s ohm." %(n+1,m+1, ResRead[0]))
            
            n = n+1
            if n == M: 
                m = m+1
                n = 0

        n = len(ReadVal[-1])

    try: 
        header = out['Header']
        
        header.insert(0,"TestParameter,Measurement.Type,%s" %(Typ))
        header.append("Measurement,Device,%s" %(eChar.device))
        header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.localtime)))
        
        header.append('DataName, Ignd, Irram, Igate, R')
        header.append('Dimension, %d, %d, %d, %d' %(n,n,n,n))
        header.append('SetHeader--------------')
        header.extend(FormingHeader)
        header.append('ReadHeader-----------------')
        header.extend(ReadHeader)
        header.append('Matrix-----------------')
        header.extend(MatrixHeader)
        
        CycHeader = 'Cycle, ,'
        setRes = 'Set/Reset, ,'
        Colheader = 'DataName, X, Y'
        ColDim = 'Dimension, %d, %d' %(len(Coordinates), len(Coordinates))
        
        for nam, v in zip(ColName,ReadVal):
            rName = "R%s" %(nam)
            Colheader = "%s,%s, Irram, Ignd, Igate" %(Colheader, rName)
            ColDim = "%s, %d, %d, %d, %d" %(ColDim, len(v), len(v), len(v), len(v))
            setRes = "%s, %s, %s, %s, %s" %(setRes, nam, nam, nam, nam)

        for k in range(int(len(ReadVal)/2)):
            CycHeader = "%s, %d, %d, %d, %d, %d, %d, %d, %d" %(CycHeader, k+1, k+1, k+1, k+1, k+1, k+1, k+1, k+1)

        header.append(CycHeader)
        header.append(setRes)
        header.append(Colheader)
        header.append(ColDim)

    except UnboundLocalError as e: 
        eChar.ErrorQueue.put("Error in Cycle 8x8, UnboundLocalError %s" %(e))

    data = []
    
    for l in range(len(Coordinates)):
        line = "DataValue, %s, %s" %(Coordinates[l][0], Coordinates[l][1])
        for n in range(len(ReadVal)):
            for ent in ReadVal[n][l]:
                line = "%s, %s" %(line, ent)
        data.append(line)

    eChar.writeDataToFile(header, data, Typ=Typ, startCyc=eChar.curCycle+1, endCyc=eChar.curCycle+1)
   

    row = dh.Row([Rs,Rr],eChar.DieX,eChar.DieY,eChar.DevX,eChar.DevY,Typ,eChar.curCycle,eChar.curCycle+NumofCycles)

    eChar.StatOutValues.addRow(row)
    eChar.curCycle = eChar.curCycle + NumofCycles


##########################################################################################################################

def ImageWrite8x8(eChar, ImageFile, SetChn, GNDChn, GateChn, Vset, Vread, Vgatelow, Vgatehigh, tset, tread):

    Typ = 'ImageWrite_8x8'

    Chns = [SetChn, GNDChn, GateChn]
    PulseChn = SetChn
    MeasChn = GNDChn
    Pbase = 0
    M = 8
    N = 8
    VorI = [True,True,True]
    readVal = [Vread, 0, Vgatehigh]
    hold = 0.0
    IComp = [10e-3,10e-3,10e-3]
    delGate = Vgatehigh - Vgatelow

    if ImageFile == "":
        raise ValueError("ImageFile must be a path to a file.")

    if Vgatehigh - Vgatelow < 0: 
        raise ValueError("Vgatehigh must be larger than Vgatelow.")

    print("IM", ImageFile)
    Mat=std.matrixFromImage(M,N,ImageFile)

    ReadVal = []
    
    MatrixFile = CreateInternal8x8MatrixClass(SetChn, GateChn, GNDChn)
    MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), MatrixFile, True)

    MatrixHeader = MC.getHeader()
    n = 0
    m = 0
    
    Coordinates = []

    while MC.setNext():
        
        mEl = Mat[n][m]
        Vgate = Vgatelow + mEl*delGate
        
        Val = [Vset, 0, Vgate]

        stop = False
        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
        
        if stop:
            break

        ###### Set 
        out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, Val, Pbase, VorI, hold, tset, IComp=IComp)
        if n == 0 and m ==0:
            FormingHeader = eChar.E5274A.getHeader()

        ###### Read
        out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
        if n == 0 and m ==0:
            ReadHeader = eChar.E5274A.getHeader()

        ResRead = []

        for l in range(len(out['Data'])):
            try:    
                out['Data'][l].append(Vread/out['Data'][l][0])
                ResRead.append(abs(Vread/out['Data'][l][0]))
            except ZeroDivisionError:
                out['Data'][l].append(2e20)
                ResRead.append(2e20)
            out['Data'][l].append(-1*out['Data'][l][0])
        
        add = [ResRead[0]]
        for l in range(len(out['Data'])):
            add.append(out['Data'][l][0])
        ReadVal.append(cp.deepcopy(add))
        Coordinates.append([n+1,m+1])

        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', 'legend': ['GND', 'Vlow', 'Vhigh'], "lineWidth":0.5, 'Yscale': 'log',  "Traces": ResRead, 'Xaxis': False, 'Xlabel': "Array Device", "Ylabel": 'Resistance ($\Omega$)', 'Title': "Array Resistance", "MeasurementType": Typ, "ValueName": 'Resistance'})
        eChar.IVplotData.put({"Add": True, 'Yscale': 'lin',  "Traces": ResRead, 'Map': [n,m], 'Xlabel': 'X Position', "Ylabel": 'Y Position', "Clabel": 'Resistance ($\Omega$)', 'Title': "Array Resistance", "MeasurementType": Typ, "ValueName": 'Resistance Map'})
        eChar.LogData.put("Forming 8x8: Device %sx%s: Resistance: %s ohm." %(n+1,m+1, ResRead))
        
        n = n+1
        if n == M: 
            m = m+1
            n = 0

    n = len(ReadVal)

    try: 
        header = out['Header']
        
        header.insert(0,"TestParameter,Measurement.Type,%s" %(Typ))
        header.append("Measurement,Device,%s" %(eChar.device))
        header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.localtime)))
        
        header.append('SetHeader--------------')
        header.extend(FormingHeader)
        header.append('ReadHeader-----------------')
        header.extend(ReadHeader)
        header.append('Matrix-----------------')
        header.extend(MatrixHeader)
        header.append('DataName, , , Rset, Irram, Igate, Ignd')
        header.append('Dimension, , , %d, %d, %d, %d' %(n,n,n,n))

    except UnboundLocalError as e: 
        eChar.ErrorQueue.put("Error in Reset 8x8, UnboundLocalError %s" %(e))

    data = []
    statVal = []
    for l in range(n):
        line = "DataValue, %s, %s" %(Coordinates[l][0], Coordinates[l][1])
        for ent in ReadVal[l]:
            line = "%s, %s" %(line, ent)
        statVal.append(ReadVal[l][0])
        data.append(line)


    eChar.writeDataToFile(header, data, Typ=Typ, startCyc=0, endCyc=1)
    
    R = dh.Value(eChar, statVal, 'Rset', DoYield=eChar.DoYield, Unit='ohm')
    row = dh.Row([R],eChar.DieX,eChar.DieY,eChar.DevX,eChar.DevY,Typ,eChar.curCycle+1)

    eChar.StatOutValues.addRow(row)


##########################################################################################################################


def Set8x8(eChar, SetChn, GNDChn, GateChn, Vset, Vread, Vgate, tset, tread):

    Typ = 'Set_8x8'

    Chns = [SetChn, GNDChn, GateChn]
    PulseChn = SetChn
    MeasChn = GNDChn
    Pbase = 0
    M = 8
    N = 8
    VorI = [True,True,True]
    Val = [Vset, 0, Vgate]
    readVal = [Vread, 0, Vgate]
    hold = 0.0
    IComp = [10e-3,10e-3,10e-3]

    ReadVal = []
    
    MatrixFile = CreateInternal8x8MatrixClass(SetChn, GateChn, GNDChn)
    MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), MatrixFile, True)

    MatrixHeader = MC.getHeader()
    n = 0
    m = 0
    
    Coordinates = []

    while MC.setNext():
        
        stop = False
        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
        
        if stop:
            break

        ###### Set 
        out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, Val, Pbase, VorI, hold, tset, IComp=IComp)
        if n == 0 and m ==0:
            FormingHeader = eChar.E5274A.getHeader()

        ###### Read
        out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
        if n == 0 and m ==0:
            ReadHeader = eChar.E5274A.getHeader()

        ResRead = []

        for l in range(len(out['Data'])):
            try:    
                out['Data'][l].append(Vread/out['Data'][l][0])
                ResRead.append(abs(Vread/out['Data'][l][0]))
            except ZeroDivisionError:
                out['Data'][l].append(2e20)
                ResRead.append(2e20)
            out['Data'][l].append(-1*out['Data'][l][0])
        
        add = [ResRead[0]]
        for l in range(len(out['Data'])):
            add.append(out['Data'][l][0])
        ReadVal.append(cp.deepcopy(add))
        Coordinates.append([n+1,m+1])

        eChar.plotIVData({"Add": True, "lineStyle": 'o', 'legend': ['GND', 'Vlow', 'Vhigh'], "lineWidth":0.5, 'Yscale': 'log',  "Traces": ResRead, 'Xaxis': False, 'Xlabel': "Array Device", "Ylabel": 'Resistance ($\Omega$)', 'Title': "Array Resistance", "MeasurementType": Typ, "ValueName": 'Resistance'})
        eChar.plotIVData({"Add": True, 'Yscale': 'lin',  "Traces": ResRead, 'Map': [n,m], 'Xlabel': 'X Position', "Ylabel": 'Y Position', "Clabel": 'Resistance ($\Omega$)', 'Title': "Array Resistance", "MeasurementType": Typ, "ValueName": 'Resistance Map'})
        eChar.LogData.put("Forming 8x8: Device %sx%s: Resistance: %s ohm." %(n+1,m+1, ResRead))
        
        n = n+1
        if n == M: 
            m = m+1
            n = 0

    n = len(ReadVal)

    try: 
        header = out['Header']
        
        header.insert(0,"TestParameter,Measurement.Type,%s" %(Typ))
        header.append("Measurement,Device,%s" %(eChar.device))
        header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.localtime)))
        
        header.append('SetHeader--------------')
        header.extend(FormingHeader)
        header.append('ReadHeader-----------------')
        header.extend(ReadHeader)
        header.append('Matrix-----------------')
        header.extend(MatrixHeader)
        header.append('DataName, , , Rset, Irram, Igate, Ignd')
        header.append('Dimension, , , %d, %d, %d, %d' %(n,n,n,n))

    except UnboundLocalError as e: 
        eChar.ErrorQueue.put("Error in Reset 8x8, UnboundLocalError %s" %(e))

    data = []
    statVal = []
    for l in range(n):
        line = "DataValue, %s, %s" %(Coordinates[l][0], Coordinates[l][1])
        for ent in ReadVal[l]:
            line = "%s, %s" %(line, ent)
        statVal.append(ReadVal[l][0])
        data.append(line)


    eChar.writeDataToFile(header, data, Typ=Typ, startCyc=0, endCyc=1)
    
    R = dh.Value(eChar, statVal, 'Rset', DoYield=eChar.DoYield, Unit='ohm')
    row = dh.Row([R],eChar.DieX,eChar.DieY,eChar.DevX,eChar.DevY,Typ,eChar.curCycle+1)

    eChar.StatOutValues.addRow(row)


##########################################################################################################################


def Forming8x8(eChar, FormChn, GNDChn, GateChn, Vform, Vread, Vgate, tform, tread):

    Typ = 'Forming_8x8'
    TypI = 'Forming_Initial_8x8'

    Chns = [FormChn, GNDChn, GateChn]
    PulseChn = FormChn
    MeasChn = GNDChn
    Pbase = 0
    M = 8
    N = 8
    VorI = [True,True,True]
    Val = [Vform, 0, Vgate]
    readVal = [Vread, 0, Vgate]
    hold = 0
    
    IComp = [10e-3,10e-3,10e-3]

    ReadVal = []
    
    MatrixFile = CreateInternal8x8MatrixClass(FormChn, GateChn, GNDChn)
    MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), MatrixFile, True)

    MatrixHeader = MC.getHeader()
    n = 0
    m = 0
    
    Coordinates = []

    while MC.setNext():
        stop = False
        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
        
        if stop:
            break
        ###### Read
        out1 = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
        #out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, readVal, Pbase, VorI, hold, tread, IComp=IComp)
        
        ResRead = []
        
        for l in range(len(out1['Data'])):
            try:    
                ResRead.append(abs(Vread/out1['Data'][l][0]))
            except ZeroDivisionError:
                ResRead.append(2e20)
        
        add = [ResRead[0]]
        for l in range(len(out1['Data'])):
            add.append(out1['Data'][l][0])
            

        eChar.plotIVData({"Add": True, "lineStyle": 'o', 'legend': ['GND', 'Vlow', 'Vhigh'], "lineWidth":0.5, 'Yscale': 'log',  "Traces":ResRead, 'Xaxis': False, 'Xlabel': "Array Device", "Ylabel": 'Resistance ($\Omega$)', 'Title': "Array Resistance", "MeasurementType": Typ, "ValueName": 'Inital Resistance'})
        eChar.plotIVData({"Add": True, 'Yscale': 'lin',  "Traces": ResRead, 'Map': [n,m], 'Xlabel': 'X Position', "Ylabel": 'Y Position', "Clabel": 'Resistance ($\Omega$)', 'Title': "Array Resistance", "MeasurementType": TypI, "ValueName": 'Resistance Map'})
        eChar.LogData.put("Forming 8x8: Device %sx%s: Resistance: %s ohm." %(n+1,m+1, ResRead))
        
        ###### Forming 
        out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, Val, Pbase, VorI, hold, tform, IComp=IComp)
        if n == 0 and m ==0:
            FormingHeader = eChar.E5274A.getHeader()

        ###### Read
        out2 = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
        #out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, readVal, Pbase, VorI, hold, tread, IComp=IComp)
        
        if n == 0 and m ==0:
            ReadHeader = eChar.E5274A.getHeader()

        ResRead = []
        
        for l in range(len(out1['Data'])):
            try:    
                ResRead.append(abs(Vread/out2['Data'][l][0]))
            except ZeroDivisionError:
                ResRead.append(2e20)
        
        add.append(ResRead[0])
        for l in range(len(out2['Data'])):
            add.append(out2['Data'][l][0])

        
        ReadVal.append(cp.deepcopy(add))
        Coordinates.append([n+1,m+1])

        eChar.plotIVData({"Add": True, "lineStyle": 'o', 'legend': ['GND', 'Vlow', 'Vhigh'], "lineWidth":0.5, 'Yscale': 'log',  "Traces":ResRead, 'Xaxis': False, 'Xlabel': "Array Device", "Ylabel": 'Resistance ($\Omega$)', 'Title': "Array Resistance", "MeasurementType": Typ, "ValueName": 'Forming Resistance'})
        eChar.plotIVData({"Add": True, 'Yscale': 'lin',  "Traces": ResRead, 'Map': [n,m], 'Xlabel': 'X Position', "Ylabel": 'Y Position', "Clabel": 'Resistance ($\Omega$)', 'Title': "Array Resistance", "MeasurementType": Typ, "ValueName": 'Resistance Map'})
        eChar.LogData.put("Forming 8x8: Device %sx%s: Init. Resistance: %s ohm." %(n+1,m+1, ResRead))
        
        n = n+1
        if n == M: 
            m = m+1
            n = 0

    n = len(ReadVal)

    try: 
        header = out['Header']
        
        header.insert(0,"TestParameter,Measurement.Type,%s" %(Typ))
        header.append("Measurement,Device,%s" %(eChar.device))
        header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.localtime)))
        
        header.append('SetHeader--------------')
        header.extend(FormingHeader)
        header.append('ReadHeader-----------------')
        header.extend(ReadHeader)
        header.append('Matrix-----------------')
        header.extend(MatrixHeader)
        header.append('DataName, , , Rinit, Irram, Igate, Ignd, Rform, Irram, Igate, Ignd')
        header.append('Dimension, , , %d, %d, %d, %d,  %d, %d, %d, %d' %(n,n,n,n, n,n,n,n))

    except UnboundLocalError as e: 
        eChar.ErrorQueue.put("Error in Reset 8x8, UnboundLocalError %s" %(e))

    data = []
    statVal = []
    for l in range(n):
        line = "DataValue, %s, %s" %(Coordinates[l][0], Coordinates[l][1])
        for ent in ReadVal[l]:
            line = "%s, %s" %(line, ent)
        statVal.append(ReadVal[l][0])
        data.append(line)


    eChar.writeDataToFile(header, data, Typ=Typ, startCyc=0, endCyc=1)

    R = dh.Value(eChar, statVal, 'Rform', DoYield=eChar.DoYield, Unit='ohm')
    row = dh.Row([R],eChar.DieX,eChar.DieY,eChar.DevX,eChar.DevY,Typ,0,1)

    eChar.StatOutValues.addRow(row)


##########################################################################################################################

def Reset8x8(eChar, ResetChn, GNDChn, GateChn, Vreset, Vread, Vgate, treset, tread):

    Typ = 'Reset_8x8'

    Chns = [ResetChn, GNDChn, GateChn]
    PulseChn = ResetChn
    MeasChn = GNDChn
    Pbase = 0
    M = 8
    N = 8
    VorI = [True,True,True]
    Val = [Vreset, 0, Vgate]
    readVal = [Vread, 0, Vgate]
    hold = 0.0
    IComp = [10e-3,10e-3,10e-3]

    ReadVal = []
    
    MatrixFile = CreateInternal8x8MatrixClass(ResetChn, GateChn, GNDChn)
    MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), MatrixFile, True)

    MatrixHeader = MC.getHeader()
    n = 0
    m = 0
    
    Coordinates = []

    while MC.setNext():
        
        stop = False
        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
        
        if stop:
            break

        ###### Reset 
        out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, Val, Pbase, VorI, hold, treset, IComp=IComp)
        if n == 0 and m ==0:
            FormingHeader = eChar.E5274A.getHeader()

        ###### Read
        out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
        #out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, readVal, Pbase, VorI, hold, tread, IComp=IComp)
        if n == 0 and m ==0:
            ReadHeader = eChar.E5274A.getHeader()

        ResRead = []

        for l in range(len(out['Data'])):
            try:    
                out['Data'][l].append(Vread/out['Data'][l][0])
                ResRead.append(abs(Vread/out['Data'][l][0]))
            except ZeroDivisionError:
                out['Data'][l].append(2e20)
                ResRead.append(2e20)
            out['Data'][l].append(-1*out['Data'][l][0])
        
        add = [ResRead[0]]
        for l in range(len(out['Data'])):
            add.append(out['Data'][l][0])
        ReadVal.append(cp.deepcopy(add))
        Coordinates.append([n+1,m+1])

        eChar.plotIVData({"Add": True, "lineStyle": 'o', 'legend': ['GND', 'Vlow', 'Vhigh'], "lineWidth":0.5, 'Yscale': 'log',  "Traces":ResRead, 'Xaxis': False, 'Xlabel': "Array Device", "Ylabel": 'Resistance ($\Omega$)', 'Title': "Array Resistance", "MeasurementType": Typ, "ValueName": 'Resistance'})
        eChar.plotIVData({"Add": True, 'Yscale': 'lin',  "Traces": ResRead, 'Map': [n,m], 'Xlabel': 'X Position', "Ylabel": 'Y Position', "Clabel": 'Resistance ($\Omega$)', 'Title': "Array Resistance", "MeasurementType": Typ, "ValueName": 'Resistance Map'})
        eChar.LogData.put("Forming 8x8: Device %sx%s: Resistance: %s ohm." %(n+1,m+1, ResRead))
        
        n = n+1
        if n == M: 
            m = m+1
            n = 0

    n = len(ReadVal)

    try: 
        header = out['Header']
        
        header.insert(0,"TestParameter,Measurement.Type,%s" %(Typ))
        header.append("Measurement,Device,%s" %(eChar.device))
        header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.localtime)))
        
        header.append('ResetHeader--------------')
        header.extend(FormingHeader)
        header.append('ReadHeader-----------------')
        header.extend(ReadHeader)
        header.append('Matrix-----------------')
        header.extend(MatrixHeader)
        header.append('DataName, , , Rreset, Irram, Igate, Ignd')
        header.append('Dimension, , , %d, %d, %d, %d' %(n,n,n,n))

    except UnboundLocalError as e: 
        eChar.ErrorQueue.put("Error in Reset 8x8, UnboundLocalError %s" %(e))

    data = []
    statVal = []
    for l in range(n):
        line = "DataValue, %s, %s" %(Coordinates[l][0], Coordinates[l][1])
        for ent in ReadVal[l]:
            line = "%s, %s" %(line, ent)
        statVal.append(ReadVal[l][0])
        data.append(line)

    eChar.writeDataToFile(header, data, Typ=Typ, startCyc=0, endCyc=1)
    
    R = dh.Value(eChar, statVal, 'Rreset', DoYield=eChar.DoYield, Unit='ohm')
    row = dh.Row([R],eChar.DieX,eChar.DieY,eChar.DevX,eChar.DevY,Typ, eChar.curCycle,eChar.curCycle+1)

    eChar.StatOutValues.addRow(row)
    eChar.curCycle = eChar.curCycle+1


##########################################################################################################################


def Retention8x8(eChar, Log, ReadChn, GNDChn, GateChn, Vread, Vgate, t_total, delay, MeasPoints):

    Typ = 'Retention_8x8'

    Chns = [ReadChn, GNDChn, GateChn]
    PulseChn = ReadChn
    MeasChn = GNDChn
    Pbase = 0
    M = 8
    N = 8
    VorI = [True,True,True]
    readVal = [Vread, 0, Vgate]
    hold = 0.0
    IComp = [10e-3,10e-3,10e-3]

    ReadVal = []
    
    Coordinates = []
    
    tstart = tm.time()
    tdelta_start = 30

    tdelta = t_total/MeasPoints

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

    k = 0
    ReadVal = []
    for t in tpoints:
        
        n = 0
        m = 0

        ReadVal.append([])

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
        times.append(tim)  

        MatrixFile = CreateInternal8x8MatrixClass(ReadChn, GateChn, GNDChn)
        MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), MatrixFile, True)

        MatrixHeader = MC.getHeader()

        while MC.setNext():
            
            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
            
            if stop:
                break

            ###### Read
            out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
            #out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, readVal, Pbase, VorI, hold, tread, IComp=IComp)
            
            if n == 0 and m ==0:
                ReadHeader = eChar.E5274A.getHeader()

            ResRead = []

            try:    
                ResRead.append(abs(Vread/out['Data'][0][0]))
            except ZeroDivisionError:
                ResRead.append(2e20)
            
            add = [ResRead[0]]
            for l in range(len(out['Data'])):
                add.append(out['Data'][l][0])
            ReadVal[-1].append(cp.deepcopy(add))
            if k == 0:
                Coordinates.append([n+1,m+1])

            eChar.plotIVData({"Add": True, "lineStyle": 'o', 'legend': ['GND', 'Vlow', 'Vhigh'], "lineWidth":0.5, 'Yscale': 'log',  "Traces":ResRead, 'Xaxis': False, 'Xlabel': "Array Device", "Ylabel": 'Resistance ($\Omega$)', 'Title': "Array Resistance", "MeasurementType": Typ, "ValueName": 'Resistance'})
            eChar.plotIVData({"Add": True, 'Yscale': 'lin',  "Traces": ResRead, 'Map': [n,m], 'Xlabel': 'X Position', "Ylabel": 'Y Position', "Clabel": 'Resistance ($\Omega$)', 'Title': "Array Resistance", "MeasurementType": Typ, "ValueName": 'Resistance Map'})
            eChar.LogData.put("Forming 8x8: Device %sx%s: Resistance: %s ohm." %(n+1,m+1, ResRead))
            
            n = n+1
            if n == M: 
                m = m+1
                n = 0


        k = k+1
        
    try: 
        header = out['Header']
        
        header.insert(0,"TestParameter,Measurement.Type,%s" %(Typ))
        header.append("Measurement,Device,%s" %(eChar.device))
        header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.localtime)))
        
        header.append('ReadHeader-----------------')
        header.extend(ReadHeader)
        header.append('Matrix-----------------')
        header.extend(MatrixHeader)

        IterationHead = 'Iteration, ,'
        TimeHead = 'Time (s), ,'
        Colheader = 'DataName, X, Y'
        ColDim = 'Dimension, %d, %d' %(len(Coordinates), len(Coordinates))
        
        for v, t in zip(ReadVal, times):
            Colheader = "%s, Rread, Irram, Ignd, Igate" %(Colheader)
            TimeHead = "%s, %s, %s, %s, %s" %(TimeHead,t,t,t,t)
            ColDim = "%s, %d, %d, %d, %d" %(ColDim, len(v), len(v), len(v), len(v))
            IterationHead = "%s, %d, %d, %d, %d" %(IterationHead, k+1, k+1, k+1, k+1)

        header.append(IterationHead)
        header.append(TimeHead)
        header.append(Colheader)
        header.append(ColDim)

    except UnboundLocalError as e: 
        eChar.ErrorQueue.put("Error in Retention 8x8, UnboundLocalError %s" %(e))

    data = []
    statVal = []
    
    for l in range(len(ReadVal[0])):
        line = "DataValue, %s, %s" %(Coordinates[l][0], Coordinates[l][1])
        for ent in ReadVal:
            try:
                for v in ent[l]:
                    line = "%s, %s" %(line, v)
                statVal.append(ent[l][0])
            except IndexError:
                break
        data.append(line)

    eChar.writeDataToFile(header, data, Typ=Typ, startCyc=0, endCyc=1)

    R = dh.Value(eChar, statVal, 'Rretention', DoYield=eChar.DoYield, Unit='ohm')
    row = dh.Row([R],eChar.DieX,eChar.DieY,eChar.DevX,eChar.DevY,Typ, eChar.curCycle,eChar.curCycle+1)

    eChar.StatOutValues.addRow(row)
    eChar.curCycle = eChar.curCycle+1


##########################################################################################################################


def CreateInternal8x8MatrixClass(PulseChn, GateChn, GNDChn):
    
    N = 8
    M = 8

    PCgate = [4,3,2,1,24,23,22,21]
    PCgnd = [12,11,10,9,8,7,6,5]
    PCrram = [13,14,15,16,17,18,19,20]

    MatrixData = dict()
    MatrixData['MakeBreak'] = []
    MatrixData['BreakMake'] = []
    MatrixData['BitInputs'] = []
    MatrixData['BitOutputs'] = []
    MatrixData['NormalInputs'] = []
    MatrixData['NormalOutputs'] = []

    BreakMakeEnt = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    MakeBreakEnt = []
    BitInputEnt = []
    BitOutputEnt = []
    NormalOutput = list(range(1,25,1))
    NormalInputTemp= [BreakMakeEnt[GNDChn-1] for n in range(24)]


    for n in range(N):
        for m in range(M):
            
            MatrixData['MakeBreak'].append(BreakMakeEnt)
            MatrixData['BreakMake'].append(MakeBreakEnt)
            MatrixData['BitInputs'].append(BitInputEnt)
            MatrixData['BitOutputs'].append(BitOutputEnt)

            NormalInput = cp.deepcopy(NormalInputTemp)
            NormalInput[PCgate[n]-1] = BreakMakeEnt[GateChn-1]
            NormalInput[PCrram[m]-1] = BreakMakeEnt[PulseChn-1]
            MatrixData['NormalInputs'].append(NormalInput)
            MatrixData['NormalOutputs'].append(NormalOutput)

    ReadMatrix = cp.deepcopy(MatrixData)

    return ReadMatrix


##########################################################################################################################


def WriteString8x8(eChar, string, PulseChn, GNDChn, GateChn, Vform, Vset, Vreset, Vgate, twidth, Vread, tread):

    Chns = [PulseChn, GNDChn, GateChn]
    PChn = PulseChn
    Pbase = 0
    hold = 1e-3
    VorI = [True, True, True, False]
    setVal = [Vset, 0, Vgate]
    resetVal = [Vreset, 0, Vgate]
    readVal = [Vread, 0, Vgate]
    formVal = [Vform, 0, Vgate]

    IComp = [10e-3,10e-3,1e-3, 10e-3]
    Typ = 'PulsedSpotMeasurement'
    
    MeasType = 'WriteString8x8'

    OutputData = dict()
    OutputData['Resistance'] = []
    OutputData['x'] = []
    OutputData['y'] = []
    OutputData['letter'] = []

    PCgate = [22,23,24,25,4,3,2,1]
    PCrram = list(range(13,21,1))
    PCgnd = list(range(12,4,-1))

    MatrixData = dict()
    MatrixData['MakeBreak'] = []
    MatrixData['BreakMake'] = []
    MatrixData['BitInputs'] = []
    MatrixData['BitOutputs'] = []
    MatrixData['NormalInputs'] = []
    MatrixData['NormalOutputs'] = []

    BreakMakeEnt = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    MakeBreakEnt = []
    BitInputEnt = []
    BitOutputEnt = []
    NormalOutput = list(range(24))
    NormalInputTemp= [BreakMakeEnt[GNDChn] for n in range(24)]

    for n in range(8):
        for m in range(8):
            
            MatrixData['MakeBreak'].append(BreakMakeEnt)
            MatrixData['BreakMake'].append(MakeBreakEnt)
            MatrixData['BitInputs'].append(BitInputEnt)
            MatrixData['BitOutputs'].append(BitOutputEnt)
            MatrixData['NormalInputs'].append(NormalInput)

            NormalInput = NormalInputTemp
            NormalInput[m] = BreakMakeEnt[GateChn]
            NormalInput[n] = BreakMakeEnt[PulseChn]

            MatrixData['NormalOutput'] = NormalOutput

    ReadMatrix = cp.deepcopy(MatrixData)
    CurArray = np.zeros((8,8))

    if Vform != 0: 

        MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), ReadMatrix, True)

        m = 0
        n = 0

        while MC.setNext():

            stop = False
            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
            
            if stop:
                break

            out = eChar.E5274A.PulsedSpotMeasurement(Chns, PChn, formVal, Pbase, VorI, hold, twidth, IComp=IComp)
            readForm = eChar.E5274A.PulsedSpotMeasurement(Chns, PChn, readVal, Pbase, VorI, hold, tread, IComp=IComp)

            Rform = Vread/readForm['Data'][-1][0:]
            eChar.plotIVData({"Add": True, "lineStyle": 'o', 'legend': 'Resistance', "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Rform, 'Xaxis': False, 'Xlabel': "Matrix Iteration", "Ylabel": 'current (A)', 'Title': "Resistance", "MeasurementType": Typ, "ValueName": 'Resistance'})
            eChar.plotIVData({"Add": True, 'Yscale': 'lin',  "Traces": Rform, 'Map': [n,m], 'Xlabel': 'X Position', "Ylabel": 'Y Position', "Clabel": 'Resistance ($Omega$)', 'Title': "Array Resistance", "MeasurementType": Typ, "ValueName": 'resistance'})
            
            OutputData['Resistance'].append(Rform)
            OutputData['Ignd'].append(readForm['Data'][-1][0:])
            OutputData['x'].append(n)
            OutputData['y'].append(m)
            OutputData['letter'].append("form")

            n = n+1
            if n == 8: 
                m = m+1
                n = 0

        MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), ReadMatrix, True)

        m = 0
        n = 0
        while MC.setNext():

            stop = False
            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
            
            if stop:
                break

            out = eChar.E5274A.PulsedSpotMeasurement(Chns, PChn, resetVal, Pbase, VorI, hold, twidth, IComp=IComp)
            readReset = eChar.E5274A.PulsedSpotMeasurement(Chns, PChn, readVal, Pbase, VorI, hold, tread, IComp=IComp)
            
            Rreset = Vread/readReset['Data'][-1][0:]
            eChar.plotIVData({"Add": True, "lineStyle": 'o', 'legend': 'Resistance', "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Rreset, 'Xaxis': False, 'Xlabel': "Matrix Iteration", "Ylabel": 'current (A)', 'Title': "Resistance", "MeasurementType": Typ, "ValueName": 'Resistance'})
            eChar.plotIVData({"Add": True, 'Yscale': 'lin',  "Traces": Rreset, 'Map': [n,m], 'Xlabel': 'X Position', "Ylabel": 'Y Position', "Clabel": 'Resistance ($Omega$)', 'Title': "Array Resistance", "MeasurementType": Typ, "ValueName": 'resistance'})
            
            OutputData['Resistance'].append(Rform)
            OutputData['Ignd'].append(readReset['Data'][-1][0:])
            OutputData['x'].append(n)
            OutputData['y'].append(m)
            OutputData['letter'].append("reset")

            n = n+1
            if n == 8: 
                m = m+1
                n = 0

    letArray = None

    for let in string: 
        
        letArrayPrev = letArray
        letArray = LtA.createLetterArray(let,8,8)
        

        MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), ReadMatrix, True)
        ret = []
        m = 0
        n = 0
        
        while MC.setNext():

            stop = False
            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
            
            if stop:
                break
            
            if letArrayPrev != None:
                if int(letArray[n,m]) == 1 and int(letArrayPrev[n,m]) == 0:
                    out = eChar.E5274A.PulsedSpotMeasurement(Chns, PChn, setVal, Pbase, VorI, hold, twidth, IComp=IComp)
                elif int(letArray[n,m]) == 0 and int(letArrayPrev[n,m]) == 1:
                    out = eChar.E5274A.PulsedSpotMeasurement(Chns, PChn, resetVal, Pbase, VorI, hold, twidth, IComp=IComp)
            else:
                if int(letArray[n,m]) == 1: 
                    out = eChar.E5274A.PulsedSpotMeasurement(Chns, PChn, setVal, Pbase, VorI, hold, twidth, IComp=IComp)
            

            out = eChar.E5274A.PulsedSpotMeasurement(Chns, PChn, resetVal, Pbase, VorI, hold, twidth, IComp=IComp)
            readWrite = eChar.E5274A.PulsedSpotMeasurement(Chns, PChn, readVal, Pbase, VorI, hold, tread, IComp=IComp)
            
            ret.append([i[0] for i in out['Data']])

            Rwrite = Vread/readWrite['Data'][-1][0:]
            eChar.plotIVData({"Add": True, "lineStyle": 'o', 'legend': 'Resistance', "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Rwrite, 'Xaxis': False, 'Xlabel': "Matrix Iteration", "Ylabel": 'current (A)', 'Title': "Resistance", "MeasurementType": Typ, "ValueName": 'Resistance'})
            eChar.plotIVData({"Add": True, 'Yscale': 'lin',  "Traces": Rwrite, 'Map': [n,m], 'Xlabel': 'X Position', "Ylabel": 'Y Position', "Clabel": 'Resistance ($Omega$)', 'Title': "Array Resistance", "MeasurementType": Typ, "ValueName": 'resistance'})
            
            OutputData['Resistance'].append(Rwrite)
            OutputData['Ignd'].append(readWrite['Data'][-1][0:])
            OutputData['x'].append(n)
            OutputData['y'].append(m)
            OutputData['letter'].append(let)

            n = n+1
            if n == 8: 
                m = m+1
                n = 0

    nD = len(OutputData['Resistance'])
                
    header = out['Header']


    header.insert(0,"TestParameter,Measurement.Type,%s" %(MeasType))
    header.append("Measurement,Device,%s" %(eChar.device))
    header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.localtime)))
    header.append("Measurement,Forming Voltage, %s" %(Vform))
    header.append("Measurement,Set Voltage, %s" %(Vset))
    header.append("Measurement,Reset Voltage, %s" %(Vreset))
    header.append("Measurement,Gate Voltage, %s" %(Vgate))
    header.append("Measurement,Read Voltage, %s" %(Vread))
    header.append("Measurement,Read Time, %s" %(tread))
    header.append("Measurement,Write Time, %s" %(twidth))
    header.append("Measurement,Pulse Channel, %s" %(PulseChn))
    header.append("Measurement,Ground Channel, %s" %(GNDChn))
    header.append("Measurement,Gate Channel, %s" %(GateChn))
    
    header.append('DataName, Resistance, Ignd, x, y, Letter')
    header.append('Dimension, %d, %d, %d, %d, %d' %(nD, nD,nD,nD,nD))

    out = []
    for i in ret:
        add = 'DataValue'
        for x in i: 
            add = "%s, %s" %(add, x)
        out.append(add)
        
    eChar.writeDataToFile(header, data, Typ=Typ)

    ###########################################################################################################################
    