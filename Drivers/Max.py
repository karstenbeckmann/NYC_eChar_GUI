'''
This file contains definitons from Maximilian Liehr
'''

import time as tm
import StdDefinitions as std
import StatisticalAnalysis as dh
import threading as th
import math as ma
import numpy as np
import queue as qu
import csv as csv
import copy as cp
import matplotlib.pyplot as plt
import statistics as stat


def Meas_8x81T1RForm_UTK(eChar, test1):

    # A-Vprog(GND), B-Vform, C-Vpin(Reset), D-Vpin(Read), E-VDDH, F-Vprog(3.3V), G-GND for testing
    Chns = [1,2,3,4,5,6,7]
    #will the channel be aiming to set a voltage or a current? the other property will be measured. 
    # i.e. True = Set Voltage, Measure current - False = Set Current, Measure Voltage
    VorI = [True, True, True, True, True, True, True]
    # if we're setting a voltage, what will it be?
    Val = [0, 3.3, 4, 0.2, 3.3, 3.3, 0]
    # if we're setting a current, what will it be?
    # what is the compliance current?
    IComp = [1e-3,1e-3,1e-3, 1e-3, 1e-3, 1e-3, 1e-3]
    
    #this sets up the parameter analyzer
    ret1 = eChar.E5274A.SpotMeasurement(Chns, VorI, Val, IComp=IComp)

    #this will control the matrix
    MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), eChar.Configuration.getMatrixConfiguration(), True)

    ret = []
    n = 0
    #for each line in the matrix config we've generated, set the connections
    while MC.setNext():

        stop = False
        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
            tm.sleep(1)
        
        if stop:
            break
        
        #do the measurement we've defined
        out = eChar.E5274A.SpotMeasurement(Chns, VorI, Val, IComp=IComp)
        # resis=abs(-0.2/out[0])
        # print("Output %s", out)
        # out.append(resis)
        # print("Output Resist %s", out)


        #append the measurement to our output log
        ret.append([i[0] for i in out['Data']])

        #update the plots  A-Gnd, B-form/gate2, C-gate1, D-set, E-rd, F-gate3, G-reset 
        Trac = ret[-1][0:7]
        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', 'legend': ['Iprog(GND)','Iform', 'Ipin(Reset)', 'Ipin(Read)','IDDH','Iprog(3.3V)','Ignd', 'Resistance'], "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': "Matrix Iteration", "Ylabel": 'Current (A)', 'Title': "input current", "ValueName": 'Current'})

        Trac = ret[-1][0]
        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Matrix Iteration', "Ylabel": 'current (A)', 'Title': "output current", "ValueName": 'Current'})
        n = n+1

    # write a header to our output file
    header = out['Header']
    header.append('DataName, Iprog(GND), Iform, Ipin(Reset), Ipin(Read), IDDH, Iprog(3.3V), Ignd, Resistance')
    header.append('Dimension, %d, %d, %d, %d, %d, %d, %d, %d' %(n,n,n,n,n,n,n,n))

    out = []
    for i in ret:
        add = 'DataValue'
        for x in i: 
            add = "%s, %s" %(add, x)

        try:
            resis=abs(-0.2/i[6])
            print('resistance',resis,'current',i[6])
            add="%s,%s" %(add,str(resis))
        except ZeroDivisionError:
            add="%s,%s" %(add,'error')

        out.append(add)
        
    #pass the data in RAM to a process which will write it out
    eChar.startThread(target = std.writeDataToFile , args=(cp.deepcopy(header), out, eChar.getFolder(), eChar.getFilename()))

def Meas_8x81T1RNeuron_Test1a(eChar, test1):

    # A-Vlow(0V), B-Vhigh(1.2V), C-Domlow(0V), D-Ref(0.4V), E-Fpost(GND) F-Fpost(GND)(Voltage Output) G-MR(Midrail-0.6V) 
    # for testing (C and D are not really necessary but I have the SMUs so whatever)
    Chns = [1,2,3,4,5,6,7]
    #will the channel be aiming to set a voltage or a current? the other property will be measured. 
    # i.e. True = Set Voltage, Measure current - False = Set Current, Measure Voltage
    VorI = [True, True, True, True, True, False, True]
    # if we're setting a voltage, what will it be?
    Val = [0, 1.2, 0, 0.4, 0, 0, 0.6]
    # if we're setting a current, what will it be?
    # what is the compliance current?
    #IComp = [1e-3,1e-3,1e-3,1e-3,1e-3,1e-3]

    #this sets up the parameter analyzer
    #ret1 = eChar.E5274A.SpotMeasurement(Chns, VorI, Val, IComp=IComp)
    ret1 = eChar.E5274A.SpotMeasurement(Chns, VorI, Val)

    #this will control the matrix
    MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), eChar.Configuration.getMatrixConfiguration(), True)

    ret = []
    n = 0
    #for each line in the matrix config we've generated, set the connections
    while MC.setNext():

        stop = False
        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
            tm.sleep(1)
        
        if stop:
            break
        
        #do the measurement we've defined
        #out = eChar.E5274A.SpotMeasurement(Chns, VorI, Val, IComp=IComp)
        out = eChar.E5274A.SpotMeasurement(Chns, VorI, Val)
        # resis=abs(-0.2/out[0])
        # print("Output %s", out)
        # out.append(resis)
        # print("Output Resist %s", out)


        #append the measurement to our output log
        ret.append([i[0] for i in out['Data']])

        #update the plots  A-Gnd, B-form/gate2, C-gate1, D-set, E-rd, F-gate3, G-reset 
        Trac = ret[-1][0:7]
        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', 'legend': ['Iprog(GND)','Iform', 'Ipin(Reset)', 'Ipin(Read)','IDDH'], "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': "Matrix Iteration", "Ylabel": 'Current (A)', 'Title': "input current", "ValueName": 'Current'})

        Trac = ret[-1][0]
        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Matrix Iteration', "Ylabel": 'current (A)', 'Title': "output current", "ValueName": 'Current'})
        n = n+1

    # write a header to our output file
    header = out['Header']
    
    header.append('DataName, Ilow, Ihigh, IDomlow, IDomhigh, IFpost(GND), VFpost(GND), IMR(Midrail 0.6V)')
    header.append('Dimension, %d, %d, %d, %d, %d, %d, %d' %(n,n,n,n,n,n,n))

    out = []
    for i in ret:
        add = 'DataValue'
        for x in i: 
            add = "%s, %s" %(add, x)

        #try:
        #    resis=abs(-0.2/i[6])
        #    print('resistance',resis,'current',i[6])
        #    add="%s,%s" %(add,str(resis))
        #except ZeroDivisionError:
        #    add="%s,%s" %(add,'error')

        out.append(add)
        
    #pass the data in RAM to a process which will write it out
    eChar.startThread(target = std.writeDataToFile , args=(cp.deepcopy(header), out, eChar.getFolder(), eChar.getFilename()))
    


def Meas_UTKDCNeuron_Test_Sagar(eChar, test1):

    # A-Vlow(0V), B-VSS_0.2(0.4V), C-MR(Midrail-0.6V) , D-VDD_0.2(0.8V), E-Vhigh(1.2V), F-Output1 (Voltage) G-Output2 (Voltage) H-Output3 (Voltage)
    # for testing (C and D are not really necessary but I have the SMUs so whatever)
    Chns = [1,2,3,4,5,6,7]
    #will the channel be aiming to set a voltage or a current? the other property will be measured. 
    # i.e. True = Set Voltage, Measure current - False = Set Current, Measure Voltage
    VorI = [True, True, True, True, True, False, False]
    # if we're setting a voltage, what will it be?
    Val = [0, 0.4, 0.6, 0.8, 1.2, 0, 0]
    # if we're setting a current, what will it be?
    # what is the compliance current?
    #IComp = [1e-3,1e-3,1e-3,1e-3,1e-3,1e-3]
    
    #this sets up the parameter analyzer
    #ret1 = eChar.E5274A.SpotMeasurement(Chns, VorI, Val, IComp=IComp)
    ret1 = eChar.E5274A.SpotMeasurement(Chns, VorI, Val)

    #this will control the matrix
    MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), eChar.Configuration.getMatrixConfiguration(), True)

    ret = []
    n = 0
    #for each line in the matrix config we've generated, set the connections
    while MC.setNext():

        stop = False
        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
            tm.sleep(1)
        
        if stop:
            break
        
        #do the measurement we've defined
        #out = eChar.E5274A.SpotMeasurement(Chns, VorI, Val, IComp=IComp)
        out = eChar.E5274A.SpotMeasurement(Chns, VorI, Val)
        # resis=abs(-0.2/out[0])
        # print("Output %s", out)
        # out.append(resis)
        # print("Output Resist %s", out)


        #append the measurement to our output log
        ret.append([i[0] for i in out['Data']])

        #update the plots  A-Gnd, B-form/gate2, C-gate1, D-set, E-rd, F-gate3, G-reset 
        Trac = ret[-1][0:7]
        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', 'legend': ['Iprog(GND)','Iform', 'Ipin(Reset)', 'Ipin(Read)','IDDH'], "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': "Matrix Iteration", "Ylabel": 'Current (A)', 'Title': "input current", "ValueName": 'Current'})

        Trac = ret[-1][0]
        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Matrix Iteration', "Ylabel": 'current (A)', 'Title': "output current", "ValueName": 'Current'})
        n = n+1

    # write a header to our output file
    header = out['Header']
    header.append('DataName, Ilow, IVSS_0.2(0.4V), IMR(Midrail 0.6V), IVDD_0.2(0.8V), Ihigh(1.2V), VOutput1, VOutput2, VOutput3')
    header.append('Dimension, %d, %d, %d, %d, %d, %d, %d' %(n,n,n,n,n,n,n))

    out = []
    for i in ret:
        add = 'DataValue'
        for x in i: 
            add = "%s, %s" %(add, x)

        #try:
        #    resis=abs(-0.2/i[6])
        #    print('resistance',resis,'current',i[6])
        #    add="%s,%s" %(add,str(resis))
        #except ZeroDivisionError:
        #    add="%s,%s" %(add,'error')

        out.append(add)
        
    #pass the data in RAM to a process which will write it out
    eChar.startThread(target = std.writeDataToFile , args=(cp.deepcopy(header), out, eChar.getFolder(), eChar.getFilename()))
    

def Meas_UTKDCNeuron_Test_Sagar_3Voltages(eChar, test1):

    # A-Vlow(0V), B-MR(Midrail-0.6V), C-Vhigh(1.2V) , D-Output1 (Voltage), E-Output2 (Voltage) F-Output3 (Voltage) G-Output4 (Voltage)
    # for testing (C and D are not really necessary but I have the SMUs so whatever)
    Chns = [1,2,3,4,5,6,7]
    #will the channel be aiming to set a voltage or a current? the other property will be measured. 
    # i.e. True = Set Voltage, Measure current - False = Set Current, Measure Voltage
    VorI = [True, True, True, False, False, False, False]
    # if we're setting a voltage, what will it be?
    Val = [0, 0.6, 1.2, 0, 0, 0, 0]
    # if we're setting a current, what will it be?
    # what is the compliance current?
    #IComp = [1e-3,1e-3,1e-3,1e-3,1e-3,1e-3]
    
    #this sets up the parameter analyzer
    #ret1 = eChar.E5274A.SpotMeasurement(Chns, VorI, Val, IComp=IComp)
    ret1 = eChar.E5274A.SpotMeasurement(Chns, VorI, Val)

    #this will control the matrix
    MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), eChar.Configuration.getMatrixConfiguration(), True)

    ret = []
    n = 0
    #for each line in the matrix config we've generated, set the connections
    while MC.setNext():

        stop = False
        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
            tm.sleep(1)
        
        if stop:
            break
        
        #do the measurement we've defined
        #out = eChar.E5274A.SpotMeasurement(Chns, VorI, Val, IComp=IComp)
        out = eChar.E5274A.SpotMeasurement(Chns, VorI, Val)
        # resis=abs(-0.2/out[0])
        # print("Output %s", out)
        # out.append(resis)
        # print("Output Resist %s", out)


        #append the measurement to our output log
        ret.append([i[0] for i in out['Data']])

        #update the plots  A-Gnd, B-form/gate2, C-gate1, D-set, E-rd, F-gate3, G-reset 
        Trac = ret[-1][0:7]
        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', 'legend': ['Iprog(GND)','Iform', 'Ipin(Reset)', 'Ipin(Read)','IDDH'], "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': "Matrix Iteration", "Ylabel": 'Current (A)', 'Title': "input current", "ValueName": 'Current'})

        Trac = ret[-1][0]
        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Matrix Iteration', "Ylabel": 'current (A)', 'Title': "output current", "ValueName": 'Current'})
        n = n+1

    # write a header to our output file
    header = out['Header']
    
    header.append('DataName, Ilow, IMR(Midrail 0.6V), Ihigh(1.2V), VOutput1, VOutput2, VOutput3, VOutput4')
    header.append('Dimension, %d, %d, %d, %d, %d, %d, %d' %(n,n,n,n,n,n,n))

    out = []
    for i in ret:
        add = 'DataValue'
        for x in i: 
            add = "%s, %s" %(add, x)

        #try:
        #    resis=abs(-0.2/i[6])
        #    print('resistance',resis,'current',i[6])
        #    add="%s,%s" %(add,str(resis))
        #except ZeroDivisionError:
        #    add="%s,%s" %(add,'error')

        out.append(add)
        
    #pass the data in RAM to a process which will write it out
    eChar.startThread(target = std.writeDataToFile , args=(cp.deepcopy(header), out, eChar.getFolder(), eChar.getFilename()))
    

def Meas_UTKDCNeuron_Test_Sam(eChar, test1):

    # A-Vlow(0V), B-MR(Midrail-0.6V), C-Vhigh(1.2V) , D-Output1 (Voltage), E-Output2 (Voltage) F-Output3 (Voltage) G-Vth1 (0.55V)
    # for testing (C and D are not really necessary but I have the SMUs so whatever)
    Chns = [1,2,3,4,5,6,7]
    #will the channel be aiming to set a voltage or a current? the other property will be measured. 
    # i.e. True = Set Voltage, Measure current - False = Set Current, Measure Voltage
    VorI = [True, True, True, False, False, False, True]
    # if we're setting a voltage, what will it be?
    Val = [0, 0.6, 1.2, 0, 0, 0, 0.55]
    # if we're setting a current, what will it be?
    # what is the compliance current?
    #IComp = [1e-3,1e-3,1e-3,1e-3,1e-3,1e-3]
    #this sets up the parameter analyzer
    #ret1 = eChar.E5274A.SpotMeasurement(Chns, VorI, Val, IComp=IComp)
    ret1 = eChar.E5274A.SpotMeasurement(Chns, VorI, Val)

    #this will control the matrix
    MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), eChar.Configuration.getMatrixConfiguration(), True)

    ret = []
    n = 0
    #for each line in the matrix config we've generated, set the connections
    while MC.setNext():

        stop = False
        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
            tm.sleep(1)
        
        if stop:
            break
        
        #do the measurement we've defined
        #out = eChar.E5274A.SpotMeasurement(Chns, VorI, Val, IComp=IComp)
        out = eChar.E5274A.SpotMeasurement(Chns, VorI, Val)
        # resis=abs(-0.2/out[0])
        # print("Output %s", out)
        # out.append(resis)
        # print("Output Resist %s", out)


        #append the measurement to our output log
        ret.append([i[0] for i in out['Data']])

        #update the plots  A-Gnd, B-form/gate2, C-gate1, D-set, E-rd, F-gate3, G-reset 
        Trac = ret[-1][0:7]
        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', 'legend': ['Iprog(GND)','Iform', 'Ipin(Reset)', 'Ipin(Read)','IDDH'], "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': "Matrix Iteration", "Ylabel": 'Current (A)', 'Title': "input current", "ValueName": 'Current'})

        Trac = ret[-1][0]
        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Matrix Iteration', "Ylabel": 'current (A)', 'Title': "output current", "ValueName": 'Current'})
        n = n+1

    # write a header to our output file
    header = out['Header']    
    header.append('DataName, Ilow, IMR(Midrail 0.6V), Ihigh(1.2V), VOutput1, VOutput2, VOutput3, Vth1(0.55V)')
    header.append('Dimension, %d, %d, %d, %d, %d, %d, %d' %(n,n,n,n,n,n,n))

    out = []
    for i in ret:
        add = 'DataValue'
        for x in i: 
            add = "%s, %s" %(add, x)

        #try:
        #    resis=abs(-0.2/i[6])
        #    print('resistance',resis,'current',i[6])
        #    add="%s,%s" %(add,str(resis))
        #except ZeroDivisionError:
        #    add="%s,%s" %(add,'error')

        out.append(add)
        
    #pass the data in RAM to a process which will write it out
    eChar.startThread(target = std.writeDataToFile , args=(cp.deepcopy(header), out, eChar.getFolder(), eChar.getFilename())))
    


def Meas_UTK_Adnan(eChar, test1):

    # A-Vlow(0V), B-MR(Midrail-0.6V), C-Vhigh(1.2V) , D-Output1 (Voltage), E-Output2 (Voltage) F-Output3 (Voltage) G-OUtput4 (Current)
    # for testing (C and D are not really necessary but I have the SMUs so whatever)
    Chns = [1,2,3,4,5,6,7]
    #will the channel be aiming to set a voltage or a current? the other property will be measured. 
    # i.e. True = Set Voltage, Measure current - False = Set Current, Measure Voltage
    VorI = [True, True, True, False, False, False, True]
    # if we're setting a voltage, what will it be?
    Val = [0, 0.6, 1.2, 0, 0, 0, 0]
    # if we're setting a current, what will it be?
    # what is the compliance current?
    #IComp = [1e-3,1e-3,1e-3,1e-3,1e-3,1e-3]

    #this sets up the parameter analyzer
    #ret1 = eChar.E5274A.SpotMeasurement(Chns, VorI, Val, IComp=IComp)
    ret1 = eChar.E5274A.SpotMeasurement(Chns, VorI, Val)

    #this will control the matrix
    MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), eChar.Configuration.getMatrixConfiguration(), True)

    ret = []
    n = 0
    #for each line in the matrix config we've generated, set the connections
    while MC.setNext():

        stop = False
        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
            tm.sleep(1)
        
        if stop:
            break
        
        #do the measurement we've defined
        #out = eChar.E5274A.SpotMeasurement(Chns, VorI, Val, IComp=IComp)
        out = eChar.E5274A.SpotMeasurement(Chns, VorI, Val)
        # resis=abs(-0.2/out[0])
        # print("Output %s", out)
        # out.append(resis)
        # print("Output Resist %s", out)


        #append the measurement to our output log
        ret.append([i[0] for i in out['Data']])

        #update the plots  A-Gnd, B-form/gate2, C-gate1, D-set, E-rd, F-gate3, G-reset 
        Trac = ret[-1][0:7]
        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', 'legend': ['Iprog(GND)','Iform', 'Ipin(Reset)', 'Ipin(Read)','IDDH'], "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': "Matrix Iteration", "Ylabel": 'Current (A)', 'Title': "input current", "ValueName": 'Current'})

        Trac = ret[-1][0]
        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Matrix Iteration', "Ylabel": 'current (A)', 'Title': "output current", "ValueName": 'Current'})
        n = n+1

    # write a header to our output file
    header = out['Header']
    
    header.append('DataName, Ilow, IMR(Midrail 0.6V), Ihigh(1.2V), VOutput1, VOutput2, VOutput3, Vth1(0.55V)')
    header.append('Dimension, %d, %d, %d, %d, %d, %d, %d' %(n,n,n,n,n,n,n))

    out = []
    for i in ret:
        add = 'DataValue'
        for x in i: 
            add = "%s, %s" %(add, x)

        #try:
        #    resis=abs(-0.2/i[6])
        #    print('resistance',resis,'current',i[6])
        #    add="%s,%s" %(add,str(resis))
        #except ZeroDivisionError:
        #    add="%s,%s" %(add,'error')

        out.append(add)
        
    #pass the data in RAM to a process which will write it out
    eChar.startThread(target = std.writeDataToFile , args=(cp.deepcopy(header), out, eChar.getFolder(), eChar.getFilename()))
    

def Meas_SPERO_VMM_Test(eChar, Vgate):

    # A-VGate, B-Vgnd (D pad), C-Vinput1 (0.4 V) , D-Vinput2 (0.2 V), E-Vinput3 (0 V) F-Vinput4 (-0.2 V) G-Vinput5 (-0.4 V)
    # for testing (C and D are not really necessary but I have the SMUs so whatever)
    Chns = [1,2,3,4,5,6,7]
    #will the channel be aiming to set a voltage or a current? the other property will be measured. 
    # i.e. True = Set Voltage, Measure current - False = Set Current, Measure Voltage
    VorI = [True, True, True, True, True, True, True]
    # if we're setting a voltage, what will it be?
    #Val = [Vgate, 0, 0.04, 0.02, 0, -0.02, -0.04]
    Val = [Vgate, 0, 0.4, 0.2, 0, -0.2, 0]
    # if we're setting a current, what will it be?
    # what is the compliance current?
    #IComp = [1e-3,1e-3,1e-3,1e-3,1e-3,1e-3]
    #this sets up the parameter analyzer
    #ret1 = eChar.E5274A.SpotMeasurement(Chns, VorI, Val, IComp=IComp)
    ret1 = eChar.E5274A.SpotMeasurement(Chns, VorI, Val)

    #this will control the matrix
    MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), eChar.Configuration.getMatrixConfiguration(), True)

    ret = []
    n = 0
    #for each line in the matrix config we've generated, set the connections
    while MC.setNext():

        stop = False
        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
            tm.sleep(1)
        
        if stop:
            break
        
        #do the measurement we've defined
        #out = eChar.E5274A.SpotMeasurement(Chns, VorI, Val, IComp=IComp)
        out = eChar.E5274A.SpotMeasurement(Chns, VorI, Val)
        # resis=abs(-0.2/out[0])
        # print("Output %s", out)
        # out.append(resis)
        # print("Output Resist %s", out)


        #append the measurement to our output log
        ret.append([i[0] for i in out['Data']])

        #update the plots  A-Gnd, B-form/gate2, C-gate1, D-set, E-rd, F-gate3, G-reset 
        Trac = ret[-1][0:7]
        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', 'legend': ['Iprog(GND)','Iform', 'Ipin(Reset)', 'Ipin(Read)','IDDH'], "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': "Matrix Iteration", "Ylabel": 'Current (A)', 'Title': "input current", "ValueName": 'Current'})

        Trac = ret[-1][0]
        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Matrix Iteration', "Ylabel": 'current (A)', 'Title': "output current", "ValueName": 'Current'})
        n = n+1

    # write a header to our output file
    header = out['Header']
    
    header.append('DataName, Igate, IOutput, IC, ID, IE, IF, IG')
    header.append('Dimension, %d, %d, %d, %d, %d, %d, %d' %(n,n,n,n,n,n,n))

    out = []
    for i in ret:
        add = 'DataValue'
        for x in i: 
            add = "%s, %s" %(add, x)

        #try:
        #    resis=abs(-0.2/i[6])
        #    print('resistance',resis,'current',i[6])
        #    add="%s,%s" %(add,str(resis))
        #except ZeroDivisionError:
        #    add="%s,%s" %(add,'error')

        out.append(add)
        
    #pass the data in RAM to a process which will write it out
    eChar.startThread(target = std.writeDataToFile , args=(cp.deepcopy(header), out, eChar.getFolder(), eChar.getFilename()))
    

def Meas_8x81T1R_SPERO(eChar, Vgate1, Vgate2, Vset, Vreset):

    # A-Gnd, B-form/gate2(low), C-gate1(high), D-set, E-rd, F-reset, G-Gnd for testing
    Chns = [1,2,3,4,5,6,7]
    #will the channel be aiming to set a voltage or a current? the other property will be measured. 
    # i.e. True = Set Voltage, Measure current - False = Set Current, Measure Voltage
    VorI = [True, True, True, True, True,True,True]
    # if we're setting a voltage, what will it be?
    Val = [0, Vgate1, Vgate2, Vset, -0.2, Vreset, 0]
    # if we're setting a current, what will it be?
    # what is the compliance current?
    #IComp = [1e-3,1e-3,1e-3, 1e-3, 1e-3,1e-3,1e-3]

    #this sets up the parameter analyzer
    ret1 = eChar.E5274A.SpotMeasurement(Chns, VorI, Val)

    #this will control the matrix
    MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), eChar.Configuration.getMatrixConfiguration(), True)

    ret = []
    n = 0
    #for each line in the matrix config we've generated, set the connections
    while MC.setNext():

        stop = False
        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
            tm.sleep(1)
        
        if stop:
            break
        
        #do the measurement we've defined
        out = eChar.E5274A.SpotMeasurement(Chns, VorI, Val)
        # resis=abs(-0.2/out[0])
        # print("Output %s", out)
        # out.append(resis)
        # print("Output Resist %s", out)


        #append the measurement to our output log
        ret.append([i[0] for i in out['Data']])

        #update the plots  A-Gnd, B-form/gate2, C-gate1, D-set, E-rd, F-gate3, G-reset 
        Trac = ret[-1][0:7]
        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', 'legend': ['Ignd','Ivg1(1.3V)', 'Ivg2(1.9V)', 'Iset','Iread','Ireset','Ignd2'], "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': "Matrix Iteration", "Ylabel": 'Current (A)', 'Title': "input current", "ValueName": 'Current'})

        Trac = ret[-1][0]
        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Matrix Iteration', "Ylabel": 'current (A)', 'Title': "output current", "ValueName": 'Current'})
        n = n+1

    # write a header to our output file
    header = out['Header']
    
    header.append('DataName, Ignd (Output), Ivg1(1.3V), Ivg2(1.9V), Iset, Iread, Ireset, Ignd2')
    header.append('Dimension, %d, %d, %d, %d, %d, %d, %d' %(n,n,n,n,n,n,n))

    out = []
    for i in ret:
        add = 'DataValue'
        for x in i: 
            add = "%s, %s" %(add, x)

        #try:
        #    resis=abs(-0.2/i[0])
        #    print('resistance',resis,'current',i[0])
        #    add="%s,%s" %(add,str(resis))
        #except ZeroDivisionError:
        #    add="%s,%s" %(add,'error')

        out.append(add)
        
    #pass the data in RAM to a process which will write it out
    eChar.startThread(target = std.writeDataToFile , args=(cp.deepcopy(header), out, eChar.getFolder(), eChar.getFilename()))
    

##########################################################################################################################

def ImageWrite8x8_SPERO(eChar, MatrixFile, SetChn, GNDChn, GateChn, Vset, Vread, Vgatelow, Vgatehigh, tset, tread):

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

    if MatrixFile == "":
        raise ValueError("MatrixFile must be a path to a file.")

    if Vgatehigh - Vgatelow < 0: 
        raise ValueError("Vgatehigh must be larger than Vgatelow.")


    print("HELLO WORLD")
    print("IM", MatrixFile)
    #print("DASDLASJDLAJSDLKJSAD", data_array[0][0])

    Mat = ArrayStr2Int(MatrixFile)
    Mat = Mat.transpose()
    print("NEW Data_array", Mat)
       # data_array=np.array(MatrixFile[1:])
    #print("Data_array", data_array)

    ######
    '''
    with open("your_file.csv",'r') as f:
        data_list = list(csv.reader(f, delimiter=";"))
    data_array=np.array(data_list[1:])
    '''
    

    #Mat=std.matrixFromImage(M,N,ImageFile)

    
    ReadVal = []
    
    MatrixFile = CreateInternal8x8MatrixClass(SetChn, GateChn, GNDChn, N, M)
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

        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', 'legend': ['GND', 'Vlow', 'Vhigh'], "lineWidth":0.5, 'Yscale': 'log',  "Traces": ResRead, 'Xaxis': False, 'Xlabel': "Array Device", "Ylabel": 'Resistance ($\Omega$)', 'Title': "Array Resistance", "ValueName": 'Resistance'})
        eChar.IVplotData.put({"Add": True, 'Yscale': 'lin',  "Traces": ResRead, 'Map': [n,m], 'Xlabel': 'X Position', "Ylabel": 'Y Position', "Clabel": 'Resistance ($\Omega$)', 'Title': "Array Resistance", "ValueName": 'Resistance Map'})
        eChar.LogData.put("Forming 8x8: Device %sx%s: Resistance: %s ohm." %(n+1,m+1, ResRead))
        
        n = n+1
        if n == M: 
            m = m+1
            n = 0

    n = len(ReadVal)

    try: 
        header = out['Header']
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


    eChar.startThread(target = std.writeDataToFile , args=(cp.deepcopy(header), data, eChar.getFolder(), eChar.getFilename(0, 1)))
    
    
    R = eChar.dhValue(eChar, statVal, 'Rset', DoYield=eChar.DoYield, Unit='ohm')
    row = eChar.dhAddRow([R], StCycle=eChar.curCycle+1)



##########################################################################################################################

def ImageWrite8x8_SPERO_Single_Row(eChar, MatrixFile, SetChn, GNDChn, GateChn, Vset, Vread, Vgatelow, Vgatehigh, tset, tread):

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

    if MatrixFile == "":
        raise ValueError("MatrixFile must be a path to a file.")

    if Vgatehigh - Vgatelow < 0: 
        raise ValueError("Vgatehigh must be larger than Vgatelow.")

    print("HELLO WORLD")
    print("IM", MatrixFile)

    Mat = ArrayStr2Int(MatrixFile)
    #Mat = Mat.transpose()
    print("NEW Data_array", Mat)
    Mat1 = np.transpose(Mat)
    print("NEW Data_array Transpose", Mat1)
    ########################################### MAY NEED TO CHANGE MAT TO MAT1 IN CODE LATER!!!!!!!!!!!!!!!
       # data_array=np.array(MatrixFile[1:])
    #print("Data_array", data_array)

    ######
    '''
    with open("your_file.csv",'r') as f:
        data_list = list(csv.reader(f, delimiter=";"))
    data_array=np.array(data_list[1:])
    '''
    #print("Array 0_7", Mat[0][7])
    #print("Array 0_0", Mat[0][0])
    #print("Array 0_1", Mat[0][1])

    #Mat=std.matrixFromImage(M,N,ImageFile)

    
    ReadVal = []
    
    MatrixFile = CreateInternal8x8MatrixClass(SetChn, GateChn, GNDChn, N, M)

    print("MatrixFile", MatrixFile)
    MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), MatrixFile, True)

    print("MMMCCCCCC", MC)

    MatrixHeader = MC.getHeader()
    n = 0
    m = 0
    
    Coordinates = []

    while MC.setNext():
        Vset1 = Vset

        #if m == N:
        #    break
        mEl = Mat[n][m]
        Vgate = Vgatelow + mEl*delGate
        
        # If the value in the array is 99 that means it is to remain whatever teh value it had before.
        if mEl == 99:
            Vgate = 0
            Vset1 = 0
        
        Val = [Vset1, 0, Vgate]

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

        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', 'legend': ['GND', 'Vlow', 'Vhigh'], "lineWidth":0.5, 'Yscale': 'log',  "Traces": ResRead, 'Xaxis': False, 'Xlabel': "Array Device", "Ylabel": 'Resistance ($\Omega$)', 'Title': "Array Resistance", "ValueName": 'Resistance'})
        eChar.IVplotData.put({"Add": True, 'Yscale': 'lin',  "Traces": ResRead, 'Map': [n,m], 'Xlabel': 'X Position', "Ylabel": 'Y Position', "Clabel": 'Resistance ($\Omega$)', 'Title': "Array Resistance", "ValueName": 'Resistance Map'})
        eChar.LogData.put("Forming 8x8: Device %sx%s: Resistance: %s ohm." %(n+1,m+1, ResRead))
        
        print(n)
        print(m)

        n = n+1
        if n == M: 
            m = m+1
            n = 0

    n = len(ReadVal)

    try: 
        header = out['Header']        
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


    eChar.startThread(target = std.writeDataToFile , args=(cp.deepcopy(header), data, eChar.getFolder(), eChar.getFilename(0, 1)))
    
    
    R = eChar.dhValue(eChar, statVal, 'Rset', DoYield=eChar.DoYield, Unit='ohm')
    row = eChar.dhAddRow([R],eChar.curCycle+1)

    ################################################################################################
    
def CreateInternal8x8MatrixClass(PulseChn, GateChn, GNDChn, N, M):
    
    #N = 8
    #M = 8

    #PCgate = [4,3,2,1,24,23,22,21]
    PCgate = [21,22,23,24,1,2,3,4] 
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
    #print("sadfhasfhalsjdhflkajdhsflk:    ", NormalInputTemp)


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

def Meas_SPERO_VMM_Test1111111111(eChar, test1):

    # A-Vlow(0V), B-MR(Midrail-0.6V), C-Vhigh(1.2V) , D-Output1 (Voltage), E-Output2 (Voltage) F-Output3 (Voltage) G-OUtput4 (Current)
    # for testing (C and D are not really necessary but I have the SMUs so whatever)
    Chns = [1,2,3,4,5,6,7]
    #will the channel be aiming to set a voltage or a current? the other property will be measured. 
    # i.e. True = Set Voltage, Measure current - False = Set Current, Measure Voltage
    VorI = [True, True, True, True, True, True, True]
    # if we're setting a voltage, what will it be?
    Val = [1.2, 0, 1.2, 0, 0, 0, 0]
    # if we're setting a current, what will it be?
    # what is the compliance current?
    #IComp = [1e-3,1e-3,1e-3,1e-3,1e-3,1e-3]
    
    #if len(Vinput) != 8:
    #    print("Vinput is not the correct length!")
    #else:

    #this sets up the parameter analyzer
    #ret1 = eChar.E5274A.SpotMeasurement(Chns, VorI, Val, IComp=IComp)
    ret1 = eChar.E5274A.SpotMeasurement(Chns, VorI, Val)

    #this will control the matrix
    MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), eChar.Configuration.getMatrixConfiguration(), True)

    ret = []
    n = 0
    #for each line in the matrix config we've generated, set the connections
    while MC.setNext():

        stop = False
        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
            tm.sleep(1)
        
        if stop:
            break
        
        #do the measurement we've defined
        #out = eChar.E5274A.SpotMeasurement(Chns, VorI, Val, IComp=IComp)
        out = eChar.E5274A.SpotMeasurement(Chns, VorI, Val)
        # resis=abs(-0.2/out[0])
        # print("Output %s", out)
        # out.append(resis)
        # print("Output Resist %s", out)


        #append the measurement to our output log
        ret.append([i[0] for i in out['Data']])

        #update the plots  A-Gnd, B-form/gate2, C-gate1, D-set, E-rd, F-gate3, G-reset 
        Trac = ret[-1][0:7]
        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', 'legend': ['Iprog(GND)','Iform', 'Ipin(Reset)', 'Ipin(Read)','IDDH'], "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': "Matrix Iteration", "Ylabel": 'Current (A)', 'Title': "input current", "ValueName": 'Current'})

        Trac = ret[-1][0]
        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Matrix Iteration', "Ylabel": 'current (A)', 'Title': "output current", "ValueName": 'Current'})
        n = n+1

    # write a header to our output file
    header = out['Header']   
    header.append('DataName, Ilow, IMR(Midrail 0.6V), Ihigh(1.2V), VOutput1, VOutput2, VOutput3, Vth1(0.55V)')
    header.append('Dimension, %d, %d, %d, %d, %d, %d, %d' %(n,n,n,n,n,n,n))

    out = []
    for i in ret:
        add = 'DataValue'
        for x in i: 
            add = "%s, %s" %(add, x)

        #try:
        #    resis=abs(-0.2/i[6])
        #    print('resistance',resis,'current',i[6])
        #    add="%s,%s" %(add,str(resis))
        #except ZeroDivisionError:
        #    add="%s,%s" %(add,'error')

        out.append(add)
        
    #pass the data in RAM to a process which will write it out
    eChar.startThread(target = std.writeDataToFile , args=(cp.deepcopy(header), out, eChar.getFolder(), eChar.getFilename()))
    


##########################################################################################################################

def Meas_OnChipPulse(eChar, Vinput, Iinput, RRAMinput):
    
    # A-Gnd, B-form/gate2(low), C-gate1(high), D-set, E-rd, F-reset, G-Gnd for testing
    Chns = [1,2,3,4,5,6]
    #will the channel be aiming to set a voltage or a current? the other property will be measured. 
    # i.e. True = Set Voltage, Measure current - False = Set Current, Measure Voltage
    VorI = [True, True, False, True, False, True]
    # if we're setting a voltage, what will it be?
    Val = [3.3, 1.2, 0, Vinput, Iinput, RRAMinput]
    # if we're setting a current, what will it be?
    # what is the compliance current?
    #IComp = [1e-3,1e-3,1e-3, 1e-3, 1e-3,1e-3,1e-3]

    #this sets up the parameter analyzer
    ret1 = eChar.E5274A.SpotMeasurement(Chns, VorI, Val)

    #this will control the matrix
    MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), eChar.Configuration.getMatrixConfiguration(), True)

    ret = []
    n = 0
    #for each line in the matrix config we've generated, set the connections
    while MC.setNext():

        stop = False
        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
            tm.sleep(1)
        
        if stop:
            break
        
        #do the measurement we've defined
        out = eChar.E5274A.SpotMeasurement(Chns, VorI, Val)
        # resis=abs(-0.2/out[0])
        # print("Output %s", out)
        # out.append(resis)
        # print("Output Resist %s", out)


        #append the measurement to our output log
        ret.append([i[0] for i in out['Data']])

        #update the plots  A-Gnd, B-form/gate2, C-gate1, D-set, E-rd, F-gate3, G-reset 
        Trac = ret[-1][0:7]
        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', 'legend': ['Ignd','Ivg1(1.3V)', 'Ivg2(1.9V)', 'Iset','Iread','Ireset','Ignd2'], "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': "Matrix Iteration", "Ylabel": 'Current (A)', 'Title': "input current", "ValueName": 'Current'})

        Trac = ret[-1][0]
        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Matrix Iteration', "Ylabel": 'current (A)', 'Title': "output current", "ValueName": 'Current'})
        n = n+1

    # write a header to our output file
    header = out['Header']    
    header.append('DataName, IHigh (3.3V), ILow(1.2V), Ignd(0V)/Vgnd(OA)**, Ig(Varied), Vref(Varied), IRRAM (Varied)')
    header.append('Dimension, %d, %d, %d, %d, %d, %d' %(n,n,n,n,n,n))

    out = []
    for i in ret:
        add = 'DataValue'
        for x in i: 
            add = "%s, %s" %(add, x)

        #try:
        #    resis=abs(-0.2/i[0])
        #    print('resistance',resis,'current',i[0])
        #    add="%s,%s" %(add,str(resis))
        #except ZeroDivisionError:
        #    add="%s,%s" %(add,'error')

        out.append(add)
        
    #pass the data in RAM to a process which will write it out
    eChar.startThread(target = std.writeDataToFile , args=(cp.deepcopy(header), out, eChar.getFolder(), eChar.getFilename()))
    

##########################################################################################################################

##########################################################################################################################

def ImageSimilaritySearchSPERO_1(eChar, MatrixFile, VMMFile, Numberofpics, LRSComparison, Sigma_LRS, NumCycles, SetChn, GNDChn, GateChn, Vgate, Vset, Vreset, Vread, VMMVgate, posVMMVoltage, negVMMVoltage, tset, treset, SingleLRS, SingleHRS):

    # LRSComparison can be (1-LRS/LRS Comparison 2-MultiLRS/HRS Comparison 3-Single Case Using Array of Values Seen below Other-Single Case using values put in program)
    
    Chns = [SetChn, GNDChn, GateChn]
    PulseChn = SetChn
    MeasChn = GNDChn
    Pbase = 0
  
    VorI = [True,True,True]
    SetVal = [Vset, 0, Vgate]
    ResetVal = [Vreset, 0, Vgate]
    readVal = [Vread, 0, Vgate]
    hold = 0.0
    IComp = [1e-3,1e-3,1e-3]
    #delGate = Vgatehigh - Vgatelow

    # A-VGate, B-Vgnd (D pad), C-Vinput1 (0.2 V) , D-Vinput2 (-0.2 V), E-Other Gnd for setting all others to zero
    Chns2 = [1,2,3,4,5]
    #will the channel be aiming to set a voltage or a current? the other property will be measured. 
    # i.e. True = Set Voltage, Measure current - False = Set Current, Measure Voltage
    VorI2 = [True, True, True, True, True]
    # if we're setting a voltage, what will it be?
    Val2 = [VMMVgate, 0, posVMMVoltage, negVMMVoltage, 0]


    Rs = eChar.dhValue(eChar, [], 'Rset', DoYield=eChar.DoYield, Unit='ohm')
    Rr = eChar.dhValue(eChar, [], 'Rreset', DoYield=eChar.DoYield, Unit='ohm')
    Cycamnt = eChar.dhValue(eChar, [], 'Num. of Switches', DoYield=eChar.DoYield, Unit='ohm')
    VMM1 = eChar.dhValue(eChar, [], 'IVMM1', DoYield=eChar.DoYield, Unit='Amps')
    VMM2 = eChar.dhValue(eChar, [], 'IVMM2', DoYield=eChar.DoYield, Unit='Amps')
    VMM3 = eChar.dhValue(eChar, [], 'IVMM3', DoYield=eChar.DoYield, Unit='Amps')
    VMM4 = eChar.dhValue(eChar, [], 'IVMM4', DoYield=eChar.DoYield, Unit='Amps')
    VMM5 = eChar.dhValue(eChar, [], 'IVMM5', DoYield=eChar.DoYield, Unit='Amps')
    VMM6 = eChar.dhValue(eChar, [], 'IVMM6', DoYield=eChar.DoYield, Unit='Amps')
    VMM7 = eChar.dhValue(eChar, [], 'IVMM7', DoYield=eChar.DoYield, Unit='Amps')
    VMM8 = eChar.dhValue(eChar, [], 'IVMM8', DoYield=eChar.DoYield, Unit='Amps')

    '''
    # Values from Analyzed Data
    #Vgate_possible = [1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4, 1.45, 1.5, 1.55, 1.6, 1.65, 1.7, 1.75, 1.8, 1.85, 1.9, 1.95, 2.0, 2.05, 2.1, 2.15, 2.2, 2.25, 2.3]
    #LRS_Avg = [25091.0, 19762.0, 15511.0, 12562.0, 10946.0, 9543.0, 8590.0, 7257.0, 6474.0, 5935.0, 5467.0, 5072.0, 4703.0, 4359.0, 4019.0, 3747.0, 3505.0, 3303.0, 3135.0, 2984.0, 2853.0, 2759.0, 2641.0, 2521.0, 2435.0, 2365.0, 2296.0]
    #HRS_Avg = [196670.0, 211612.0, 224050.0, 226366.0, 226243.0, 226151.0, 221720.0, 207595.0, 198469.0, 193413.0, 192413.0, 195023.0, 197297.0, 191550.0, 201369.0, 197259.0, 193015.0, 182261.0, 174479.0, 165457.0, 158233.0, 153604.0, 142507.0, 133328.0, 125317.0, 117812.0, 108270.0]
    #LRS_std = [5059.0, 3944.0, 2537.0, 1541.0, 1293.0, 972.0, 698.0, 462.0, 348.0, 277.0, 216.0, 216.0, 182.0, 198.0, 169.0, 168.0, 138.0, 152.0, 125.0, 134.0, 119.0, 117.0, 130.0, 106.0, 86.0, 81.0, 79.0]
    #HRS_std = [73354.0, 75412.0, 74610.0, 70432.0, 73967.0, 72158.0, 70584.0, 69755.0, 69994.0, 69285.0, 68192.0, 67092.0, 70041.0, 70204.0, 75179.0, 72876.0, 71932.0, 66634.0, 64767.0, 58319.0, 56922.0, 55483.0, 49939.0, 44951.0, 43297.0, 38840.0, 37913.0]

    #LRS_Limit_Low_3sig = []
    #LRS_Limit_High_3sig = []
    #LRS_Limit_Low_2sig = []
    #LRS_Limit_High_2sig = []
    #LRS_Limit_Low_1sig = []
    #LRS_Limit_High_1sig = []
    #HRS_Limit_Low = []
    #HRS_Limit_High = []
    '''

    ###### Box And Whisker Plot Values ##############
    Vgate_possible = [1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4, 1.45, 1.5, 1.55, 1.6, 1.65, 1.7, 1.75, 1.8]
    LRS_Avg = [24706.0, 18917.0, 14082.0, 11386.0, 9569.0, 8413.0, 7435.0, 7145.0, 6283.0, 5911.0, 5440.0, 5043.0, 4685.0, 4356.0, 4023.0, 3774.0, 3536.0]
    #HRS_Avg = [196670.0, 211612.0, 224050.0, 226366.0, 226243.0, 226151.0, 221720.0, 207595.0, 198469.0, 193413.0, 192413.0, 195023.0, 197297.0, 191550.0, 201369.0, 197259.0, 193015.0]
    LRS_std = []
    #HRS_std = [73354.0, 75412.0, 74610.0, 70432.0, 73967.0, 72158.0, 70584.0, 69755.0, 69994.0, 69285.0, 68192.0, 67092.0, 70041.0, 70204.0, 75179.0, 72876.0, 71932.0]

    LRS_Limit_Low_3sig = []
    LRS_Limit_High_3sig = []
    LRS_Limit_Low_2sig = []
    LRS_Limit_High_2sig = []
    LRS_Limit_Low_1sig = [23100.0, 16928.0, 12976.0, 10574.0, 8785.0, 7575.0, 6870.0, 6240.0, 5768.0, 5844.0, 5049.0, 4803.0, 4541.0, 4212.0, 3850.0, 3599.0, 3375.0]
    LRS_Limit_High_1sig = [27333.0, 22091.0, 17325.0, 13357.0, 11609.0, 9940.0, 8707.0, 7684.0, 6931.0, 6205.0, 5719.0, 5281.0, 4872.0, 4533.0, 4187.0, 3907.0, 3681.0]
    ### HRS Values from Averages ###
    #HRS_Median = [196267.0, 211074.0, 217430.0, 234333.0, 230556.0, 233469.0, 229312.0, 217170.0, 201344.0, 187643.0, 188200.0, 182200.0, 191389.0, 189900.0, 198855.0, 185621.0, 202453.0]
    #HRS_Limit_Low = [(HRS_Avg[0]-HRS_std[0]),(HRS_Avg[1]-HRS_std[1]),(HRS_Avg[2]-HRS_std[2]),(HRS_Avg[3]-HRS_std[3]),(HRS_Avg[4]-HRS_std[4]),(HRS_Avg[5]-HRS_std[5]),(HRS_Avg[6]-HRS_std[6]),(HRS_Avg[7]-HRS_std[7]),(HRS_Avg[8]-HRS_std[8]),(HRS_Avg[9]-HRS_std[9]),(HRS_Avg[10]-HRS_std[10]),(HRS_Avg[11]-HRS_std[11]),(HRS_Avg[12]-HRS_std[12]),(HRS_Avg[13]-HRS_std[13]),(HRS_Avg[14]-HRS_std[14]),(HRS_Avg[15]-HRS_std[15]),(HRS_Avg[16]-HRS_std[16])]
    #HRS_Limit_High = [(HRS_Avg[0]+HRS_std[0]),(HRS_Avg[1]+HRS_std[1]),(HRS_Avg[2]+HRS_std[2]),(HRS_Avg[3]+HRS_std[3]),(HRS_Avg[4]+HRS_std[4]),(HRS_Avg[5]+HRS_std[5]),(HRS_Avg[6]+HRS_std[6]),(HRS_Avg[7]+HRS_std[7]),(HRS_Avg[8]+HRS_std[8]),(HRS_Avg[9]+HRS_std[9]),(HRS_Avg[10]+HRS_std[10]),(HRS_Avg[11]+HRS_std[11]),(HRS_Avg[12]+HRS_std[12]),(HRS_Avg[13]+HRS_std[13]),(HRS_Avg[14]+HRS_std[14]),(HRS_Avg[15]+HRS_std[15]),(HRS_Avg[16]+HRS_std[16])]
    ### HRS Values From Box and Whisker Plot ###
    HRS_Limit_Low = [109705.0, 132367.0, 142867.0, 130100.0, 121950.0, 128271.0, 134657.0, 117230.0, 120422.0, 101138.0, 103159.0, 94646.0, 105136.0, 99810.0, 103989.0, 124739.0, 114318.0]
    HRS_Limit_High = [263852.0, 287893.0, 289666.0, 307202.0, 314890.0, 317572.0, 310000.0, 287976.0, 267754.0, 275470.0, 265475.0, 275887.0, 262490.0, 250833.0, 266771.0, 264956.0, 271067.0]

    '''
    # Sigma Data
    for a in range(len(Vgate_possible)):
        LRS3L = LRS_Avg[a] - 3*LRS_std[a]
        LRS3H = LRS_Avg[a] + 3*LRS_std[a]
        LRS2L = LRS_Avg[a] - 2*LRS_std[a]
        LRS2H = LRS_Avg[a] + 2*LRS_std[a]
        LRS1L = LRS_Avg[a] - 1*LRS_std[a]
        LRS1H = LRS_Avg[a] + 1*LRS_std[a]
        HRSH = HRS_Avg[a] + HRS_std[a]

        LRS_Limit_Low_3sig.append(LRS3L)
        LRS_Limit_High_3sig.append(LRS3H)
        LRS_Limit_Low_2sig.append(LRS2L)
        LRS_Limit_High_2sig.append(LRS2H)
        LRS_Limit_Low_1sig.append(LRS1L)
        LRS_Limit_High_1sig.append(LRS1H)
        m = HRS_Avg[a] - HRS_std[a]
        if m < 20000:
            m = 20000
        HRS_Limit_Low.append(m)

        HRS_Limit_High.append(HRSH)
    
    print("LRS_Limit_Low_3sig: ", LRS_Limit_Low_3sig)
    print("LRS_Limit_High_3sig: ", LRS_Limit_High_3sig)
    print("LRS_Limit_Low_2sig: ", LRS_Limit_Low_2sig)
    print("LRS_Limit_High_2sig: ", LRS_Limit_High_2sig)
    print("LRS_Limit_Low_1sig: ", LRS_Limit_Low_1sig)
    print("LRS_Limit_High_1sig: ", LRS_Limit_High_1sig)
    print("HRS_Limit_Low: ", HRS_Limit_Low)
    print("HRS_Limit_High: ", HRS_Limit_High)
    '''
    '''
    Vgate_possible = [1.1, 1.25, 1.4, 1.55, 1.7, 1.85, 2.0, 2.15, 2.3]
    LRS_Limit_Low_2sig = [7370, 5195, 3414, 2568, 1995, 1635, 1406, 1215, 1097]
    LRS_Limit_High_2sig = [11161, 6168, 4233, 3346, 2651, 2216, 1878, 1745, 1625]
    LRS_Limit_Low_1sig = [8317, 5439, 3618, 2752, 2139, 1782, 1524, 1346, 1229]
    LRS_Limit_High_1sig = [10213, 5925, 4028, 3120, 2427, 2076, 1760, 1612, 1493]

    HRS_Limit_Low = [41000, 69000, 65000, 65000, 58000, 23000, 20000, 20000, 20000]
    HRS_Limit_High = [586000, 537000, 465000, 459000, 251000, 85000, 88000, 54000]
    '''

    if len(np.unique(Vgate)) != len(Vgate):
        raise ValueError("There are duplicate Vgate values!")

    Vgate.sort()
    print("Vgate: ", Vgate)

    if LRSComparison != 1 and LRSComparison != 2 and LRSComparison != 3 and len(Vgate) > 1:
        raise ValueError("Can't have Vgate array larger than 1 in Single Case mode!")
    
    if len(SingleLRS) != 2 or  len(SingleHRS) != 2:
        raise ValueError("Number of ranges outside allowed amount of 2!")

    if (SingleLRS[0] > SingleLRS[1]) or (SingleHRS[0] > SingleHRS[1]):
        raise ValueError("First range needs to be smaller than second range in either LRS or HRS single Range Case!")

    valarray = []
    p = 0

    #print("LComp: ", LRSComparison)

    if LRSComparison == 1 or LRSComparison == 2 or LRSComparison == 3:
        for i in Vgate:
            for a in Vgate_possible:
                if i == a:
                    valarray.append(p)
                    break
                p += 1
            p = 0
        if valarray == []:
            raise ValueError("Vgate Values are wrong!")
         

    print("ValArray: ", valarray)

    stop = False

    ReadVal = []
    ColName = []
    ICurr = []
    
    z = 0
    
    if MatrixFile == "":
        raise ValueError("MatrixFile must be a path to a file.")

    if VMMFile == "":
        raise ValueError("VMMFile must be a path to a file.")

    #if Vgatehigh - Vgatelow < 0: 
    #    raise ValueError("Vgatehigh must be larger than Vgatelow.")

    print("Matrix File", MatrixFile)

    # Opens csv as float np.array (Need to change to int during while loop)
    Mat = ArrayStr2Int(MatrixFile)

    #print("Matrix File After: ", Mat)

    print("VMM File", VMMFile)

    MatVMM = ArrayStr2Int(VMMFile)

    print("MDASMASD: ", len(Mat))
    print("Mghsrthrth: ", len(MatVMM))
    print("iyosfdgrtyj: ", Numberofpics)

    if len(Mat) != len(MatVMM)*Numberofpics:
        raise ValueError("Length of Matrix File, VMM File, or input into Number of pics is incorrect. Please Check!")

    # Number of columns
    M = 8
    # Number of Rows
    N = len(MatrixFile)
    # Number of rows VMM applied per row of VMMFile
    X = Numberofpics
    
    Matrix2 = CreateInternal8x8MatrixClass(SetChn, GateChn, GNDChn, X, M)
    #print("MC2", Matrix2)
    

    n = 0
    m = 0
    q = 0
    L = 0
    
    Coordinates = []

    NumofCycles = len(MatVMM)



    for k in range(NumofCycles):
        
        n = 0
        m = 0

        MC1 = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), Matrix2, True)
        #print("DAFDSFSDFSDFSDF:  ", len(Matrix2['NormalInputs']))

        MatrixHeader = MC1.getHeader()

        MatX = Mat[:][L:L+Numberofpics]
        print("MatX: ", MatX)
        MatVMMX = MatVMM[:][k]
        L = ((k+1)*Numberofpics)

        '''
        ReadVal.append([])
        ColName.append('reset')
        Coordinates = []
        
        ################################## Reset Operation ###########################
        while MC1.setNext():
                
            if not stop:
                while not eChar.Stop.empty():
                    stop = eChar.Stop.get()
            else:
                break

            ###### Reset #######
            out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, ResetVal, Pbase, VorI, hold, treset, IComp=IComp)
            if n == 0 and m ==0:
                FormingHeader = eChar.E5274A.getHeader()

            ###### Read #######
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
            #print("REadVal Reset Updating:  ", ReadVal)
            Rr.extend(ResRead[0])
            Coordinates.append([m+1,n+1])

            #eChar.plotIVData({"Add": True, "lineStyle": 'o', 'legend': ['GND', 'Vlow', 'Vhigh'], "lineWidth":0.5, 'Yscale': 'log',  "Traces":ResRead, 'Xaxis': False, 'Xlabel': "Array Device", "Ylabel": 'Resistance ($\Omega$)', 'Title': "Array Resistance", "ValueName": 'Reset Resistance'})
            eChar.plotIVData({"Add": True, 'Yscale': 'lin',  "Traces": ResRead, 'Map': [m,n], 'Xlabel': 'X Position', "Ylabel": 'Y Position', "Clabel": 'Resistance ($\Omega$)', 'Title': "Array Resistance", "ValueName": 'Reset Resistance Map'})
            
            eChar.LogData.put("Image Similarity RRAM (Reset): Device %sx%s: Resistance: %s ohm." %(m+1,n+1, ResRead))
            
            n = n+1
            if n == M: 
                m = m+1
                n = 0
        '''
        ################################
    
        Matrix2 = CreateInternal8x8MatrixClass(SetChn, GateChn, GNDChn, X, M)
        #print("MC2", Matrix2)
        MC2 = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), Matrix2, True)
        #print("DAFDSFSDFSDFSDF:  ", len(Matrix2['NormalInputs']))
        
        n = 0
        m = 0
        
        ReadVal.append([])
        ColName.append('set')
        Coordinates = []

        ############################### Set Operation ############################
        
        while MC2.setNext():
                
            MatXVal = int(MatX[m][n])
            #print("DFKJHSDFLKHDSFLKJHSDLKFHSLKDJFLKJSDFLKJSDF: ", MatXVal)

            if not stop:
                while not eChar.Stop.empty():
                    stop = eChar.Stop.get()
            else:
                break

            ###### Set 
            
            if MatXVal == 1:
                #out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, SetVal, Pbase, VorI, hold, tset, IComp=IComp)
                if n == 0 and m == 0 and k == 0:
                    FormingHeader = eChar.E5274A.getHeader()
            '''
            else:
                a = 1
            
            ###### Read
            out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
            '''
    
            abc = 0
            loopa = 0
            ############ Compare Results of Wanted input resistances to actual resitances For LRS vs. LRS Comparison #################

            if LRSComparison == 1:
                for a in range(len(valarray)):
                    if MatXVal == a:
                        SetVal = [Vset, 0, Vgate_possible[valarray[a]]]
                        print("SetVal: ", SetVal)
                        ResetVal = [Vreset, 0, Vgate_possible[valarray[a]]]
                        print("ResetVal: ", ResetVal)
                        readVal = [Vread, 0, Vgate_possible[valarray[a]]]
                        print("ReadVal: ", readVal)
                        out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
                        try:    
                            abs(Vread/out['Data'][0][0])
                        except ZeroDivisionError:
                            out['Data'][0][0] = 1e-21
                        if Sigma_LRS == 1:
                            print("LRS Low: ",  LRS_Limit_Low_1sig[valarray[a]])
                            print("LRS High: ",  LRS_Limit_High_1sig[valarray[a]])
                            if (Vread/out['Data'][0][0] > LRS_Limit_High_1sig[valarray[a]]) or (Vread/out['Data'][0][0] < LRS_Limit_Low_1sig[valarray[a]]):
                                for loopa in range(NumCycles):
                                    out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, ResetVal, Pbase, VorI, hold, treset, IComp=IComp)
                                    out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, SetVal, Pbase, VorI, hold, tset, IComp=IComp)
                                    out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
                                    try:    
                                        abs(Vread/out['Data'][0][0])
                                    except ZeroDivisionError:
                                        out['Data'][0][0] = 1e-21
                                    print("OUTloop1: ", Vread/out['Data'][0][0])
                                    if (Vread/out['Data'][0][0] < LRS_Limit_High_1sig[valarray[a]]) and (Vread/out['Data'][0][0] > LRS_Limit_Low_1sig[valarray[a]]):
                                        abc += 1
                                        break
                                    else:
                                        abc += 1
                            else:
                                abc = 0

                        elif Sigma_LRS == 2:
                            print("LRS Low: ",  LRS_Limit_Low_2sig[valarray[a]])
                            print("LRS High: ",  LRS_Limit_High_2sig[valarray[a]])
                            if (Vread/out['Data'][0][0] > LRS_Limit_High_2sig[valarray[a]]) or (Vread/out['Data'][0][0] < LRS_Limit_Low_2sig[valarray[a]]):
                                for loopa in range(NumCycles):
                                    out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, ResetVal, Pbase, VorI, hold, treset, IComp=IComp)
                                    out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, SetVal, Pbase, VorI, hold, tset, IComp=IComp)
                                    out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
                                    try:    
                                        abs(Vread/out['Data'][0][0])
                                    except ZeroDivisionError:
                                        out['Data'][0][0] = 1e-21
                                    print("OUTloop1: ", Vread/out['Data'][0][0])
                                    if (Vread/out['Data'][0][0] < LRS_Limit_High_2sig[valarray[a]]) and (Vread/out['Data'][0][0] > LRS_Limit_Low_2sig[valarray[a]]):
                                        abc += 1
                                        break
                                    else:
                                        abc += 1
                            else:
                                abc = 0
                        
                        elif Sigma_LRS == 3:
                            if Sigma_LRS == 1:
                                print("LRS Low: ",  LRS_Limit_Low_3sig[valarray[a]])
                                print("LRS High: ",  LRS_Limit_High_3sig[valarray[a]])
                                if (Vread/out['Data'][0][0] > LRS_Limit_High_3sig[valarray[a]]) or (Vread/out['Data'][0][0] < LRS_Limit_Low_3sig[valarray[a]]):
                                    for loopa in range(NumCycles):
                                        out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, ResetVal, Pbase, VorI, hold, treset, IComp=IComp)
                                        out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, SetVal, Pbase, VorI, hold, tset, IComp=IComp)
                                        out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
                                        try:    
                                            abs(Vread/out['Data'][0][0])
                                        except ZeroDivisionError:
                                            out['Data'][0][0] = 1e-21
                                        print("OUTloop1: ", Vread/out['Data'][0][0])
                                        if (Vread/out['Data'][0][0] < LRS_Limit_High_3sig[valarray[a]]) and (Vread/out['Data'][0][0] > LRS_Limit_Low_3sig[valarray[a]]):
                                            abc += 1
                                            break
                                        else:
                                            abc += 1
                            else:
                                abc = 0

                        else:
                            out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
                            if (Vread/out['Data'][0][0] > LRS_Limit_High_2sig[valarray[a]]) and (Vread/out['Data'][0][0] < LRS_Limit_Low_2sig[valarray[a]]):
                                out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, ResetVal, Pbase, VorI, hold, treset, IComp=IComp)
                                out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, SetVal, Pbase, VorI, hold, tset, IComp=IComp)
                                out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
                                try:    
                                    abs(Vread/out['Data'][0][0])
                                except ZeroDivisionError:
                                    out['Data'][0][0] = 1e-21
                                abc = 1
                            else:
                                abc = 0

                loopa = 0


            ############ Compare Results of Wanted input resistances to actual resitances (HRS/MultiLRS) #################
            elif LRSComparison == 2:
                for a in range(len(valarray)+1):
                    if MatXVal == 0:
                        SetVal = [Vset, 0, Vgate_possible[valarray[a]]]
                        ResetVal = [Vreset, 0, Vgate_possible[valarray[a]]]
                        readVal = [Vread, 0, Vgate_possible[valarray[a]]]
                        out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
                        try:    
                            abs(Vread/out['Data'][0][0])
                        except ZeroDivisionError:
                            out['Data'][0][0] = 1e-21
                        if (Vread/out['Data'][0][0] < HRS_Limit_Low[valarray[a]]) or (Vread/out['Data'][0][0] > HRS_Limit_High[valarray[a]]):
                            for loopa in range(NumCycles):
                                out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, SetVal, Pbase, VorI, hold, tset, IComp=IComp)
                                out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, ResetVal, Pbase, VorI, hold, treset, IComp=IComp)
                                out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
                                try:    
                                    abs(Vread/out['Data'][0][0])
                                except ZeroDivisionError:
                                    out['Data'][0][0] = 1e-21
                                print("OUTloop2: ", Vread/out['Data'][0][0])
                                if (Vread/out['Data'][0][0] > HRS_Limit_Low[valarray[a]]) and (Vread/out['Data'][0][0] < HRS_Limit_High[valarray[a]]):
                                    abc += 1
                                    break
                                else:
                                    abc += 1
                        else:
                            abc = 0

                    elif (MatXVal == a and MatXVal != 0):
                        if Sigma_LRS == 1:
                            print("LRS Low: ",  LRS_Limit_Low_1sig[valarray[a]])
                            print("LRS High: ",  LRS_Limit_High_1sig[valarray[a]])
                            SetVal = [Vset, 0, Vgate_possible[valarray[a-1]]]
                            ResetVal = [Vreset, 0, Vgate_possible[valarray[a-1]]]
                            readVal = [Vread, 0, Vgate_possible[valarray[a-1]]]
                            if (Vread/out['Data'][0][0] > LRS_Limit_High_1sig[valarray[a]]) or (Vread/out['Data'][0][0] < LRS_Limit_Low_1sig[valarray[a]]):
                                for loopa in range(NumCycles):
                                    out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, ResetVal, Pbase, VorI, hold, treset, IComp=IComp)
                                    out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, SetVal, Pbase, VorI, hold, tset, IComp=IComp)
                                    out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
                                    try:    
                                        abs(Vread/out['Data'][0][0])
                                    except ZeroDivisionError:
                                        out['Data'][0][0] = 1e-21
                                    print("OUTloop1: ", Vread/out['Data'][0][0])
                                    if (Vread/out['Data'][0][0] < LRS_Limit_High_1sig[valarray[a]]) and (Vread/out['Data'][0][0] > LRS_Limit_Low_1sig[valarray[a]]):
                                        abc += 1
                                        break
                                    else:
                                        abc += 1
                            else:
                                abc = 0

                        elif Sigma_LRS == 2:
                            print("LRS Low: ",  LRS_Limit_Low_2sig[valarray[a]])
                            print("LRS High: ",  LRS_Limit_High_2sig[valarray[a]])
                            SetVal = [Vset, 0, Vgate_possible[valarray[a-1]]]
                            ResetVal = [Vreset, 0, Vgate_possible[valarray[a-1]]]
                            readVal = [Vread, 0, Vgate_possible[valarray[a-1]]]
                            if (Vread/out['Data'][0][0] > LRS_Limit_High_2sig[valarray[a]]) or (Vread/out['Data'][0][0] < LRS_Limit_Low_2sig[valarray[a]]):
                                for loopa in range(NumCycles):
                                    out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, ResetVal, Pbase, VorI, hold, treset, IComp=IComp)
                                    out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, SetVal, Pbase, VorI, hold, tset, IComp=IComp)
                                    out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
                                    try:    
                                        abs(Vread/out['Data'][0][0])
                                    except ZeroDivisionError:
                                        out['Data'][0][0] = 1e-21
                                    print("OUTloop1: ", Vread/out['Data'][0][0])
                                    if (Vread/out['Data'][0][0] < LRS_Limit_High_2sig[valarray[a]]) and (Vread/out['Data'][0][0] > LRS_Limit_Low_2sig[valarray[a]]):
                                        abc += 1
                                        break
                                    else:
                                        abc += 1
                            else:
                                abc = 0

                        else:
                            out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
                            if (Vread/out['Data'][0][0] > LRS_Limit_High_2sig[valarray[a]]) and (Vread/out['Data'][0][0] < LRS_Limit_Low_2sig[valarray[a]]):
                                out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, ResetVal, Pbase, VorI, hold, treset, IComp=IComp)
                                out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, SetVal, Pbase, VorI, hold, tset, IComp=IComp)
                                out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
                                try:    
                                    abs(Vread/out['Data'][0][0])
                                except ZeroDivisionError:
                                    out['Data'][0][0] = 1e-21
                                abc = 1
                            else:
                                abc = 0

            ############ Single LRS/HRS Comparison Switching Case Using Array in Code #################
            elif LRSComparison == 3:
                if MatXVal == 1:
                    if Sigma_LRS == 1:
                        print("LRS Low: ",  LRS_Limit_Low_1sig[valarray[0]])
                        print("LRS High: ",  LRS_Limit_High_1sig[valarray[0]])
                        SetVal = [Vset, 0, Vgate_possible[valarray[0]]]
                        ResetVal = [Vreset, 0, Vgate_possible[valarray[0]]]
                        readVal = [Vread, 0, Vgate_possible[valarray[0]]]
                        out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
                        try:    
                            abs(Vread/out['Data'][0][0])
                        except ZeroDivisionError:
                            out['Data'][0][0] = 1e-21
                        if (Vread/out['Data'][0][0] > LRS_Limit_High_1sig[valarray[0]]) or (Vread/out['Data'][0][0] < LRS_Limit_Low_1sig[valarray[0]]):
                            for loopa in range(NumCycles):
                                out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, ResetVal, Pbase, VorI, hold, treset, IComp=IComp)
                                out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, SetVal, Pbase, VorI, hold, tset, IComp=IComp)
                                out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
                                try:    
                                    abs(Vread/out['Data'][0][0])
                                except ZeroDivisionError:
                                    out['Data'][0][0] = 1e-21
                                print("OUTloop1: ", Vread/out['Data'][0][0])
                                if (Vread/out['Data'][0][0] < LRS_Limit_High_1sig[valarray[0]]) and (Vread/out['Data'][0][0] > LRS_Limit_Low_1sig[valarray[0]]):
                                    abc += 1
                                    break
                                else:
                                    abc += 1
                        else:
                            abc = 0
                    elif Sigma_LRS == 2:
                        print("LRS Low: ",  LRS_Limit_Low_2sig[valarray[0]])
                        print("LRS High: ",  LRS_Limit_High_2sig[valarray[0]])
                        SetVal = [Vset, 0, Vgate_possible[valarray[0]]]
                        ResetVal = [Vreset, 0, Vgate_possible[valarray[0]]]
                        readVal = [Vread, 0, Vgate_possible[valarray[0]]]
                        out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
                        try:    
                            abs(Vread/out['Data'][0][0])
                        except ZeroDivisionError:
                            out['Data'][0][0] = 1e-21
                        if (Vread/out['Data'][0][0] > LRS_Limit_High_2sig[valarray[0]]) or (Vread/out['Data'][0][0] < LRS_Limit_Low_2sig[valarray[0]]):
                            for loopa in range(NumCycles):
                                out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, ResetVal, Pbase, VorI, hold, treset, IComp=IComp)
                                out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, SetVal, Pbase, VorI, hold, tset, IComp=IComp)
                                out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
                                try:    
                                    abs(Vread/out['Data'][0][0])
                                except ZeroDivisionError:
                                    out['Data'][0][0] = 1e-21
                                print("OUTloop1: ", Vread/out['Data'][0][0])
                                if (Vread/out['Data'][0][0] < LRS_Limit_High_2sig[valarray[0]]) and (Vread/out['Data'][0][0] > LRS_Limit_Low_2sig[valarray[0]]):
                                    abc += 1
                                    break
                                else:
                                    abc += 1
                        else:
                            abc = 0
                                

                loopa = 0
                if MatXVal == 0:
                    print("HRS Low: ",  HRS_Limit_Low[valarray[0]])
                    print("HRS High: ",  HRS_Limit_High[valarray[0]])
                    SetVal = [Vset, 0, Vgate_possible[valarray[0]]]
                    ResetVal = [Vreset, 0, Vgate_possible[valarray[0]]]
                    readVal = [Vread, 0, Vgate_possible[valarray[0]]]
                    out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
                    try:    
                        abs(Vread/out['Data'][0][0])
                    except ZeroDivisionError:
                        out['Data'][0][0] = 1e-21
                    if (Vread/out['Data'][0][0] < HRS_Limit_Low[valarray[0]]) or (Vread/out['Data'][0][0] > HRS_Limit_High[valarray[0]]):
                        for loopa in range(NumCycles):
                            out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, SetVal, Pbase, VorI, hold, tset, IComp=IComp)
                            out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, ResetVal, Pbase, VorI, hold, treset, IComp=IComp)
                            out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
                            try:    
                                abs(Vread/out['Data'][0][0])
                            except ZeroDivisionError:
                                out['Data'][0][0] = 1e-21
                            print("OUTloop2: ", Vread/out['Data'][0][0])
                            if (Vread/out['Data'][0][0] > HRS_Limit_Low[valarray[0]]) and (Vread/out['Data'][0][0] < HRS_Limit_High[valarray[0]]):
                                abc += 1
                                break
                            else:
                                abc += 1
                    else:
                        abc = 0



            ############ Single LRS/HRS Comparison Switching Case Using Program Values #################
            else:
                if MatXVal == 1:
                    out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
                    try:    
                        abs(Vread/out['Data'][0][0])
                    except ZeroDivisionError:
                        out['Data'][0][0] = 1e-21
                    if (Vread/out['Data'][0][0] > SingleLRS[1]) or (Vread/out['Data'][0][0] < SingleLRS[0]):
                        for loopa in range(NumCycles):
                            out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, ResetVal, Pbase, VorI, hold, treset, IComp=IComp)
                            out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, SetVal, Pbase, VorI, hold, tset, IComp=IComp)
                            out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
                            try:    
                                abs(Vread/out['Data'][0][0])
                            except ZeroDivisionError:
                                out['Data'][0][0] = 1e-21
                            print("OUTloop1: ", Vread/out['Data'][0][0])
                            if (Vread/out['Data'][0][0] < SingleLRS[1]) and (Vread/out['Data'][0][0] > SingleLRS[0]):
                                abc += 1
                                break
                            else:
                                abc += 1
                    else:
                        abc = 0
                                

                loopa = 0
                if MatXVal == 0:
                    out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
                    if (Vread/out['Data'][0][0] < SingleHRS[0]) or (Vread/out['Data'][0][0] > SingleHRS[1]):
                        for loopa in range(NumCycles):
                            out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, SetVal, Pbase, VorI, hold, tset, IComp=IComp)
                            out = eChar.E5274A.PulsedSpotMeasurement(Chns, PulseChn, MeasChn, ResetVal, Pbase, VorI, hold, treset, IComp=IComp)
                            out = eChar.E5274A.SpotMeasurement(Chns, VorI, readVal, IComp=IComp)
                            try:    
                                abs(Vread/out['Data'][0][0])
                            except ZeroDivisionError:
                                out['Data'][0][0] = 1e-21
                            print("OUTloop2: ", Vread/out['Data'][0][0])
                            if (Vread/out['Data'][0][0] > SingleHRS[0]) and (Vread/out['Data'][0][0] < SingleHRS[1]):
                                abc += 1
                                break
                            else:
                                abc += 1
                    else:
                        abc = 0
            
            print("ABC = ", abc)

            
            if n == 0 and m == 0 and k == 0:
                ReadHeader = eChar.E5274A.getHeader()

            ResRead = []

            
            if Vread/out['Data'][0][0] == -1.0000000000000001e-21:
                out['Data'][0][0] = 5e-7
                
            try:    
                ResRead.append(abs(Vread/out['Data'][0][0]))
            except ZeroDivisionError:
                ResRead.append(2e20)

            add = ResRead
            for ent in out['Data']:
                add.append(ent[0])
            add.append(abc)
                
            ReadVal[-1].append(cp.deepcopy(add))
            #print("ReadVal Set Updating:  ", ReadVal)
            #ABC = []
            #ABCarray.append(abc)
            Cycamnt.extend(abc)
            Rs.extend(ResRead[0])
            Coordinates.append([m+1,n+1])

            #eChar.plotIVData({"Add": True, "lineStyle": 'o', 'legend': ['GND', 'Vlow', 'Vhigh'], "lineWidth":0.5, 'Yscale': 'log',  "Traces":ResRead, 'Xaxis': False, 'Xlabel': "Array Device", "Ylabel": 'Resistance ($\Omega$)', 'Title': "Array Resistance", "ValueName": 'Resistance'})
            eChar.plotIVData({"Add": True, 'Yscale': 'lin',  "Traces": ResRead, 'Map': [m,n], 'Xlabel': 'X Position', "Ylabel": 'Y Position', "Clabel": 'Resistance ($\Omega$)', 'Title': "Array Resistance", "ValueName": 'Set Resistance Map'})
            eChar.LogData.put("Image Similarity RRAM (Set): Device %sx%s: Resistance: %s ohm." %(m+1,n+1, ResRead[0]))

            
            
            n = n+1
            if n == M: 
                m = m+1
                n = 0
        
  
        #eChar.plotIVData.clear()

        ######################## VMM Operation #########################

        n = 0
        m = 0 
        #outval = []
        print("VMM ACTIVE! ")
        Matrix3 = VMM_Matrix_Create(PulseChn, GateChn, GNDChn, MatVMMX, Numberofpics)

        #print("MATRIX3 = ", Matrix3)

        #this will control the matrix
        #MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), eChar.Configuration.getMatrixConfiguration(), True)


        MC3 = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), Matrix3, True)
        #print("MC = ", MC)

        z += 1
        l = 0


        while MC3.setNext():
            

            #MatVMMXVal = MatVMMX[m][n]
            #mEl = MatX[n][m]
            #Vgate = Vgatelow + mEl*delGate
            
            #Val1 = [Vset, 0, Vgate]

            stop = False
            zero = False
            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
            
            if stop:
                break
            #if MatX[n][m] == 1:
                    
                ###### Set 
              #  out = eChar.E5274A.PulsedSpotMeasurement(Chns2, PulseChn, MeasChn, Val1, Pbase, VorI2, hold, tset, IComp=IComp)
               # if n == 0 and m ==0:
                #    FormingHeader = eChar.E5274A.getHeader()
            
            #if MatX[n][m] == 0:
               # a = 1

            ###### Read
            # Can adjust the range to maybe find the solution to auto ranging issue.
            #out2 = eChar.E5274A.SpotMeasurement(Chns2, VorI2, Val2,RI=14)
            #out3 = eChar.E5274A.SpotMeasurement(Chns2, VorI2, Val2,RI=13)
            #out2 = eChar.E5274A.SpotMeasurement(Chns2, VorI2, Val2)
            #outval.append(out2)
            #if n == 0 and m == 0 and k == 0:
            #    ReadHeader = eChar.E5274A.getHeader()

            # Run X number of spot measurements and take the avg value. If value shows specific values when measuring then set to zero. Do 3sigma to remove outliers
            DATAseta = []
            for q in range(10):
                out3 = eChar.E5274A.SpotMeasurement(Chns2, VorI2, Val2)
                #if abs(out3['Data'][1][0]) == 5e-6:
                #    zero = True
                if abs(out3['Data'][1][0]) == 0.0:
                    zero = True
                if abs(out3['Data'][1][0]) == 1.99999e+101:
                    zero = True
                #if abs(out3['Data'][1][0]) == 0.0:
                #    zero == True
                DATAseta.append(out3['Data'][1][0])
                #print("Out3:   ", out3)
            print("ZERO: ", zero)    
            if zero == True:
                value1 = 0.0
            else:  
                value1 = stat.median_low(DATAseta)
                print("VALUE1: ", value1)

            zero = False
            print("DATAseta: ", DATAseta)
            #value1 = stat.median_grouped(DATAseta)
            
            ResRead = []
            #print("Out2:   ", out2)
            
            #print("Out4:   ", out4)
            #print("Out5:   ", out5)
            #print("Out6:   ", out6)
            #print("l: ", l) 
            #print("Output2Data:    ", out2['Data'][1][0])
            #out2['Data'][l].append(-1*out2['Data'][l][1])
            #DATA1 = out2['Data'][1][0]
            #if abs(DATA1) == 5e-6:
            #    DATA1 = 0.0
            ICurr.append(value1)
            print("I Current: ", ICurr)
            #ArrayCurr = np.array(ICurr)
                
            

            #ArrayCurr = np.array(ICurr)
            
            
            #add = [ResRead[0]]
            #ReadVal.append(cp.deepcopy(add))
            #Coordinates.append([m+1,n+1])

            n = n+1
            l = l+1

            #eChar.LogData.put("Forming 8x8: Device %sx%s: Resistance: %s ohm." %(m+1,n+1, ResRead))
  

            #dfg
        n = len(ReadVal[-1])




        
    
    n = len(ReadVal)
    print("ReadVal Length: ", n)

    try: 
        header = out['Header']       
        header.append('DataName, Ignd, Irram, Igate, R')
        header.append('Dimension, %d, %d, %d, %d' %(n,n,n,n))
        header.append('SetHeader--------------')
        header.extend(FormingHeader)
        header.append('ReadHeader-----------------')
        header.extend(ReadHeader)
        #header.append('Matrix-----------------')
        #header.extend(MatrixHeader)
        
        CycHeader = 'VMM Operation, ,'
        setRes = 'Set/Reset, ,'
        Colheader = 'DataName, X, Y'
        ColDim = 'Dimension, %d, %d' %(len(Coordinates), len(Coordinates))
        
        for nam, v in zip(ColName,ReadVal):
            rName = "R%s" %(nam)
            Colheader = "%s, %s, Irram, Ignd, Igate, Cyc Amount" %(Colheader, rName)
            ColDim = "%s, %d, %d, %d, %d, %d" %(ColDim, len(v), len(v), len(v), len(v), len(v))
            setRes = "%s, %s, %s, %s, %s, %s" %(setRes, nam, nam, nam, nam, nam)

        for k in range(len(MatVMM)):
            CycHeader = "%s, %d, %d, %d, %d, %d" %(CycHeader, k+1, k+1, k+1, k+1, k+1)

        header.append(CycHeader)
        header.append(setRes)
        header.append(Colheader)
        header.append(ColDim)

    except UnboundLocalError as e: 
        eChar.ErrorQueue.put("Error in Cycle 8x8, UnboundLocalError %s" %(e))

    data = []

    
    for l in range(len(Coordinates)):
        line = "DataValue, %s, %s" %(Coordinates[l][1], Coordinates[l][0])
        for n in range(len(ReadVal)):
            for ent in ReadVal[n][l]:
                #print("ReadVal[n][l]:  ", ReadVal[n][l])
                #print("ent: ", ent)
                line = "%s, %s" %(line, ent)
        data.append(line)

    eChar.startThread(target = std.writeDataToFile , args=(cp.deepcopy(header), data, eChar.getFolder(), eChar.getFilename(eChar.curCycle, eChar.curCycle+1)))
    
    

    row = eChar.dhAddRow([Rs,Cycamnt], eChar.curCycle,eChar.curCycle+NumofCycles)

    eChar.curCycle = eChar.curCycle + NumofCycles



    '''
    ####### VMM Measurement Section ########
    
    '''

    CurrPlotVal1 = []
    CurrPlotVal2 = []
    CurrPlotVal3 = []
    CurrPlotVal4 = []
    CurrPlotVal5 = []
    CurrPlotVal6 = []
    CurrPlotVal7 = []
    CurrPlotVal8 = []
    VMMcom = []

    for f in range(len(MatVMM)):
        if Numberofpics == 1:
            if f == 0:
                CurrPlotVal1.append(ICurr[f*Numberofpics])
                
                VMM1.extend(CurrPlotVal1[0])

            else:
                Sum1 = ICurr[f*Numberofpics] +  CurrPlotVal1[f-1]
                
                VMM1.extend(Sum1)
                
                CurrPlotVal1.append(Sum1)
                
                print("CurrentPlotValue1:   ", CurrPlotVal1)
                

        elif Numberofpics == 2:
            CurrPlotVal2.append({'I1': ICurr[f*Numberofpics], 'I2': ICurr[(f*Numberofpics)+1]})

        elif Numberofpics == 3:
            CurrPlotVal3.append({'I1': ICurr[f*Numberofpics], 'I2': ICurr[(f*Numberofpics)+1], 'I3': ICurr[(f*Numberofpics)+2]})

        elif Numberofpics == 4:
            if f == 0:
                CurrPlotVal1.append(ICurr[f*Numberofpics])
                CurrPlotVal2.append(ICurr[(f*Numberofpics)+1])
                CurrPlotVal3.append(ICurr[(f*Numberofpics)+2])
                CurrPlotVal4.append(ICurr[(f*Numberofpics)+3])
                #print("CurrentPlotValue1:   ", CurrPlotVal1)
                #print("CurrentPlotValue2:   ", CurrPlotVal2)
                #print("CurrentPlotValue3:   ", CurrPlotVal3)
                #print("CurrentPlotValue4:   ", CurrPlotVal4)
                VMM1.extend(CurrPlotVal1[0])
                #print("VMM1:   ", VMM1)
                VMM2.extend(CurrPlotVal2[0])
                VMM3.extend(CurrPlotVal3[0])
                VMM4.extend(CurrPlotVal4[0])



            else:
                Sum1 = ICurr[f*Numberofpics] +  CurrPlotVal1[f-1]
                Sum2 = ICurr[(f*Numberofpics)+1] + CurrPlotVal2[f-1]
                Sum3 = ICurr[(f*Numberofpics)+2] + CurrPlotVal3[f-1]
                Sum4 = ICurr[(f*Numberofpics)+3] + CurrPlotVal4[f-1]

                VMM1.extend(Sum1)
                VMM2.extend(Sum2)
                VMM3.extend(Sum3)
                VMM4.extend(Sum4)

                CurrPlotVal1.append(Sum1)
                CurrPlotVal2.append(Sum2)
                CurrPlotVal3.append(Sum3)
                CurrPlotVal4.append(Sum4)
                print("CurrentPlotValue1:   ", CurrPlotVal1)
                print("CurrentPlotValue2:   ", CurrPlotVal2)
                print("CurrentPlotValue3:   ", CurrPlotVal3)
                print("CurrentPlotValue4:   ", CurrPlotVal4)

        elif Numberofpics == 5:
            if f == 0:
                CurrPlotVal1.append(ICurr[f*Numberofpics])
                CurrPlotVal2.append(ICurr[(f*Numberofpics)+1])
                CurrPlotVal3.append(ICurr[(f*Numberofpics)+2])
                CurrPlotVal4.append(ICurr[(f*Numberofpics)+3])
                CurrPlotVal5.append(ICurr[(f*Numberofpics)+4])
                #print("CurrentPlotValue1:   ", CurrPlotVal1)
                #print("CurrentPlotValue2:   ", CurrPlotVal2)
                #print("CurrentPlotValue3:   ", CurrPlotVal3)
                #print("CurrentPlotValue4:   ", CurrPlotVal4)
                VMM1.extend(CurrPlotVal1[0])
                #print("VMM1:   ", VMM1)
                VMM2.extend(CurrPlotVal2[0])
                VMM3.extend(CurrPlotVal3[0])
                VMM4.extend(CurrPlotVal4[0])
                VMM5.extend(CurrPlotVal5[0])



            else:
                Sum1 = ICurr[f*Numberofpics] +  CurrPlotVal1[f-1]
                Sum2 = ICurr[(f*Numberofpics)+1] + CurrPlotVal2[f-1]
                Sum3 = ICurr[(f*Numberofpics)+2] + CurrPlotVal3[f-1]
                Sum4 = ICurr[(f*Numberofpics)+3] + CurrPlotVal4[f-1]
                Sum5 = ICurr[(f*Numberofpics)+4] + CurrPlotVal5[f-1]

                VMM1.extend(Sum1)
                VMM2.extend(Sum2)
                VMM3.extend(Sum3)
                VMM4.extend(Sum4)
                VMM5.extend(Sum5)


                CurrPlotVal1.append(Sum1)
                CurrPlotVal2.append(Sum2)
                CurrPlotVal3.append(Sum3)
                CurrPlotVal4.append(Sum4)
                CurrPlotVal5.append(Sum5)
                print("CurrentPlotValue1:   ", CurrPlotVal1)
                print("CurrentPlotValue2:   ", CurrPlotVal2)
                print("CurrentPlotValue3:   ", CurrPlotVal3)
                print("CurrentPlotValue4:   ", CurrPlotVal4)
                print("CurrentPlotValue5:   ", CurrPlotVal5)

        elif Numberofpics == 6:
            CurrPlotVal6.append({'I1': ICurr[f*Numberofpics], 'I2': ICurr[(f*Numberofpics)+1], 'I3': ICurr[(f*Numberofpics)+2], 'I4': ICurr[(f*Numberofpics)+3], 'I5': ICurr[(f*Numberofpics)+4], 'I6': ICurr[(f*Numberofpics)+5]})

        elif Numberofpics == 7:
            CurrPlotVal7.append({'I1': ICurr[f*Numberofpics], 'I2': ICurr[(f*Numberofpics)+1], 'I3': ICurr[(f*Numberofpics)+2], 'I4': ICurr[(f*Numberofpics)+3], 'I5': ICurr[(f*Numberofpics)+4], 'I6': ICurr[(f*Numberofpics)+5], 'I7': ICurr[(f*Numberofpics)+6]})

        elif Numberofpics == 8:
            if f == 0:
                CurrPlotVal1.append(ICurr[f*Numberofpics])
                CurrPlotVal2.append(ICurr[(f*Numberofpics)+1])
                CurrPlotVal3.append(ICurr[(f*Numberofpics)+2])
                CurrPlotVal4.append(ICurr[(f*Numberofpics)+3])
                CurrPlotVal5.append(ICurr[(f*Numberofpics)+4])
                CurrPlotVal6.append(ICurr[(f*Numberofpics)+5])
                CurrPlotVal7.append(ICurr[(f*Numberofpics)+6])
                CurrPlotVal8.append(ICurr[(f*Numberofpics)+7])
                #print("CurrentPlotValue1:   ", CurrPlotVal1)
                #print("CurrentPlotValue2:   ", CurrPlotVal2)
                #print("CurrentPlotValue3:   ", CurrPlotVal3)
                #print("CurrentPlotValue4:   ", CurrPlotVal4)
                VMM1.extend(CurrPlotVal1[0])
                #print("VMM1:   ", VMM1)
                VMM2.extend(CurrPlotVal2[0])
                VMM3.extend(CurrPlotVal3[0])
                VMM4.extend(CurrPlotVal4[0])
                VMM5.extend(CurrPlotVal5[0])
                VMM6.extend(CurrPlotVal6[0])
                VMM7.extend(CurrPlotVal7[0])
                VMM8.extend(CurrPlotVal8[0])



            else:
                Sum1 = ICurr[f*Numberofpics] +  CurrPlotVal1[f-1]
                Sum2 = ICurr[(f*Numberofpics)+1] + CurrPlotVal2[f-1]
                Sum3 = ICurr[(f*Numberofpics)+2] + CurrPlotVal3[f-1]
                Sum4 = ICurr[(f*Numberofpics)+3] + CurrPlotVal4[f-1]

                VMM1.extend(Sum1)
                VMM2.extend(Sum2)
                VMM3.extend(Sum3)
                VMM4.extend(Sum4)

                CurrPlotVal1.append(Sum1)
                CurrPlotVal2.append(Sum2)
                CurrPlotVal3.append(Sum3)
                CurrPlotVal4.append(Sum4)
                print("CurrentPlotValue1:   ", CurrPlotVal1)
                print("CurrentPlotValue2:   ", CurrPlotVal2)
                print("CurrentPlotValue3:   ", CurrPlotVal3)
                print("CurrentPlotValue4:   ", CurrPlotVal4)

    
    if Numberofpics == 1:
        #CurrPlotVal4.append({'I1': ICurr[f*Numberofpics], 'I2': ICurr[(f*Numberofpics)+1], 'I3': ICurr[(f*Numberofpics)+2], 'I4': ICurr[(f*Numberofpics)+3]})
        Trac = [CurrPlotVal1]
        eChar.plotIVData({"Add": True, "lineStyle": 'o', 'legend': ['Picture2','Picture3','Picture4','Picture5'], "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': "VMM Iteration", "Ylabel": 'Current (A)', 'Title': "Output Current", "ValueName": 'Current'})


        #header.append('Current Values, %d, %d, %d, %d' %(2,3,4,5))


        #print("MatVMM: ", MatVMM)
        #print("Length of MatVMM: ", len(MatVMM))
        
        for j in range(len(MatVMM)):
            #VMMcom1 = CurrPlotVal1[j] + CurrPlotVal2[j] + CurrPlotVal3[j] + CurrPlotVal4[j]
            #print("VMMcom1:   ", VMMcom1)
            VMMcom.append(CurrPlotVal1[j])

        #print("VMMcom:   ", VMMcom)
        #print("VMMcom[0]:   ", VMMcom[0])
        for l in range(len(CurrPlotVal1)):
            line = "DataCurrentValue, %s" %(l+1)
            m = l*Numberofpics

            for n in range(Numberofpics):
                k = m + n
                print("VMMcom[k]:   ", VMMcom[k])
                ent = VMMcom[k]
                line = "%s, %s" %(line, ent)
                    
            data.append(line)

        line = "DataVgates, Vgates(Comp)" 
        for a in range(len(Vgate)):
            line = "%s, %s" %(line, Vgate[a])
        data.append(line)
        line = "DataVMMVgates, Vgates(VMM), %s" %(VMMVgate)
        data.append(line)

        

        eChar.startThread(target = std.writeDataToFile , args=(cp.deepcopy(header), data, eChar.getFolder(), eChar.getFilename(eChar.curCycle, eChar.curCycle+1)))
        
        
        #row = eChar.dhAddRow([CurrPlotVal1,CurrPlotVal2,CurrPlotVal3,CurrPlotVal4])
        row = eChar.dhAddRow([VMM1], eChar.curCycle,eChar.curCycle+NumofCycles)
        eChar.curCycle = eChar.curCycle + NumofCycles

    elif Numberofpics == 2:
        #CurrPlotVal2.append({'I1': ICurr[f*Numberofpics], 'I2': ICurr[(f*Numberofpics)+1]})
        Trac = ['I1','I2']
        eChar.plotIVData({"Add": True, "lineStyle": 'o', 'legend': ['Picture2','Picture3'], "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': "VMM Iteration", "Ylabel": 'Current (A)', 'Title': "Output Current", "ValueName": 'Current'})


    elif Numberofpics == 3:
        #CurrPlotVal3.append({'I1': ICurr[f*Numberofpics], 'I2': ICurr[(f*Numberofpics)+1], 'I3': ICurr[(f*Numberofpics)+2]})
        Trac = ['I1','I2','I3']
        eChar.plotIVData({"Add": True, "lineStyle": 'o', 'legend': ['Picture2','Picture3','Picture4'], "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': "VMM Iteration", "Ylabel": 'Current (A)', 'Title': "Output Current", "ValueName": 'Current'})


    elif Numberofpics == 4:
        #CurrPlotVal4.append({'I1': ICurr[f*Numberofpics], 'I2': ICurr[(f*Numberofpics)+1], 'I3': ICurr[(f*Numberofpics)+2], 'I4': ICurr[(f*Numberofpics)+3]})
        Trac = [CurrPlotVal1,CurrPlotVal2,CurrPlotVal3,CurrPlotVal4]
        eChar.plotIVData({"Add": True, "lineStyle": 'o', 'legend': ['Picture2','Picture3','Picture4','Picture5'], "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': "VMM Iteration", "Ylabel": 'Current (A)', 'Title': "Output Current", "ValueName": 'Current'})


        #header.append('Current Values, %d, %d, %d, %d' %(2,3,4,5))


        #print("MatVMM: ", MatVMM)
        #print("Length of MatVMM: ", len(MatVMM))
        
        for j in range(len(MatVMM)):
            #VMMcom1 = CurrPlotVal1[j] + CurrPlotVal2[j] + CurrPlotVal3[j] + CurrPlotVal4[j]
            #print("VMMcom1:   ", VMMcom1)
            VMMcom.append(CurrPlotVal1[j])
            VMMcom.append(CurrPlotVal2[j])
            VMMcom.append(CurrPlotVal3[j])
            VMMcom.append(CurrPlotVal4[j])

        #print("VMMcom:   ", VMMcom)
        #print("VMMcom[0]:   ", VMMcom[0])
        for l in range(len(CurrPlotVal1)):
            line = "DataCurrentValue, %s" %(l+1)
            m = l*Numberofpics

            for n in range(Numberofpics):
                k = m + n
                print("VMMcom[k]:   ", VMMcom[k])
                ent = VMMcom[k]
                line = "%s, %s" %(line, ent)
                    
            data.append(line)

        line = "DataVgates, Vgates(Comp)" 
        for a in range(len(Vgate)):
            line = "%s, %s" %(line, Vgate[a])
        data.append(line)
        line = "DataVMMVgates, Vgates(VMM), %s" %(VMMVgate)
        data.append(line)

        

        eChar.startThread(target = std.writeDataToFile , args=(cp.deepcopy(header), data, eChar.getFolder(), eChar.getFilename(eChar.curCycle, eChar.curCycle+1)))
        
        
        #row = eChar.dhAddRow([CurrPlotVal1,CurrPlotVal2,CurrPlotVal3,CurrPlotVal4])
        row = eChar.dhAddRow([VMM1,VMM2,VMM3,VMM4],eChar.curCycle,eChar.curCycle+NumofCycles)
        
        eChar.curCycle = eChar.curCycle + NumofCycles


    elif Numberofpics == 5:
         #CurrPlotVal4.append({'I1': ICurr[f*Numberofpics], 'I2': ICurr[(f*Numberofpics)+1], 'I3': ICurr[(f*Numberofpics)+2], 'I4': ICurr[(f*Numberofpics)+3]})
        Trac = [CurrPlotVal1,CurrPlotVal2,CurrPlotVal3,CurrPlotVal4,CurrPlotVal5]
        eChar.plotIVData({"Add": True, "lineStyle": 'o', 'legend': ['Picture2','Picture3','Picture4','Picture5','Picture6'], "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': "VMM Iteration", "Ylabel": 'Current (A)', 'Title': "Output Current", "ValueName": 'Current'})


        #header.append('Current Values, %d, %d, %d, %d' %(2,3,4,5))


        #print("MatVMM: ", MatVMM)
        #print("Length of MatVMM: ", len(MatVMM))
        
        for j in range(len(MatVMM)):
            #VMMcom1 = CurrPlotVal1[j] + CurrPlotVal2[j] + CurrPlotVal3[j] + CurrPlotVal4[j]
            #print("VMMcom1:   ", VMMcom1)
            VMMcom.append(CurrPlotVal1[j])
            VMMcom.append(CurrPlotVal2[j])
            VMMcom.append(CurrPlotVal3[j])
            VMMcom.append(CurrPlotVal4[j])
            VMMcom.append(CurrPlotVal5[j])


        #print("VMMcom:   ", VMMcom)
        #print("VMMcom[0]:   ", VMMcom[0])
        for l in range(len(CurrPlotVal1)):
            line = "DataCurrentValue, %s" %(l+1)
            m = l*Numberofpics

            for n in range(Numberofpics):
                k = m + n
                print("VMMcom[k]:   ", VMMcom[k])
                ent = VMMcom[k]
                line = "%s, %s" %(line, ent)
                    
            data.append(line)

        line = "DataVgates, Vgates(Comp)" 
        for a in range(len(Vgate)):
            line = "%s, %s" %(line, Vgate[a])
        data.append(line)
        line = "DataVMMVgates, Vgates(VMM), %s" %(VMMVgate)
        data.append(line)

        

        eChar.startThread(target = std.writeDataToFile , args=(cp.deepcopy(header), data, eChar.getFolder(), eChar.getFilename(eChar.curCycle, eChar.curCycle+1)))
        
        
        #row = eChar.dhAddRow([CurrPlotVal1,CurrPlotVal2,CurrPlotVal3,CurrPlotVal4])
        row = eChar.dhAddRow([VMM1,VMM2,VMM3,VMM4,VMM5], eChar.curCycle,eChar.curCycle+NumofCycles)
        
        eChar.curCycle = eChar.curCycle + NumofCycles

    elif Numberofpics == 6:
        #CurrPlotVal6.append({'I1': ICurr[f*Numberofpics], 'I2': ICurr[(f*Numberofpics)+1], 'I3': ICurr[(f*Numberofpics)+2], 'I4': ICurr[(f*Numberofpics)+3], 'I5': ICurr[(f*Numberofpics)+4], 'I6': ICurr[(f*Numberofpics)+5]})
        Trac = ['I1','I2','I3','I4','I5','I6']
        eChar.plotIVData({"Add": True, "lineStyle": 'o', 'legend': ['Picture2','Picture3','Picture4','Picture5','Picture6','Picture7'], "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': "VMM Iteration", "Ylabel": 'Current (A)', 'Title': "Output Current", "ValueName": 'Current'})


    elif Numberofpics == 7:
        CurrPlotVal7.append({'I1': ICurr[f*Numberofpics], 'I2': ICurr[(f*Numberofpics)+1], 'I3': ICurr[(f*Numberofpics)+2], 'I4': ICurr[(f*Numberofpics)+3], 'I5': ICurr[(f*Numberofpics)+4], 'I6': ICurr[(f*Numberofpics)+5], 'I7': ICurr[(f*Numberofpics)+6]})
        Trac = ['I1','I2','I3','I4','I5','I6','I7']
        eChar.plotIVData({"Add": True, "lineStyle": 'o', 'legend': ['Picture2','Picture3','Picture4','Picture5','Picture6','Picture7','Picture8'], "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': "VMM Iteration", "Ylabel": 'Current (A)', 'Title': "Output Current", "ValueName": 'Current'})


    elif Numberofpics == 8:
         #CurrPlotVal4.append({'I1': ICurr[f*Numberofpics], 'I2': ICurr[(f*Numberofpics)+1], 'I3': ICurr[(f*Numberofpics)+2], 'I4': ICurr[(f*Numberofpics)+3]})
        Trac = [CurrPlotVal1,CurrPlotVal2,CurrPlotVal3,CurrPlotVal4,CurrPlotVal5,CurrPlotVal6,CurrPlotVal7,CurrPlotVal8]
        eChar.plotIVData({"Add": True, "lineStyle": 'o', 'legend': ['Picture2','Picture3','Picture4','Picture5','Picture6','Picture7','Picture8'], "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': "VMM Iteration", "Ylabel": 'Current (A)', 'Title': "Output Current", "ValueName": 'Current'})


        #header.append('Current Values, %d, %d, %d, %d' %(2,3,4,5))


        #print("MatVMM: ", MatVMM)
        #print("Length of MatVMM: ", len(MatVMM))
        
        for j in range(len(MatVMM)):
            #VMMcom1 = CurrPlotVal1[j] + CurrPlotVal2[j] + CurrPlotVal3[j] + CurrPlotVal4[j]
            #print("VMMcom1:   ", VMMcom1)
            VMMcom.append(CurrPlotVal1[j])
            VMMcom.append(CurrPlotVal2[j])
            VMMcom.append(CurrPlotVal3[j])
            VMMcom.append(CurrPlotVal4[j])
            VMMcom.append(CurrPlotVal5[j])
            VMMcom.append(CurrPlotVal6[j])
            VMMcom.append(CurrPlotVal7[j])
            VMMcom.append(CurrPlotVal8[j])


        #print("VMMcom:   ", VMMcom)
        #print("VMMcom[0]:   ", VMMcom[0])
        for l in range(len(CurrPlotVal1)):
            line = "DataCurrentValue, %s" %(l+1)
            m = l*Numberofpics

            for n in range(Numberofpics):
                k = m + n
                print("VMMcom[k]:   ", VMMcom[k])
                ent = VMMcom[k]
                line = "%s, %s" %(line, ent)
                    
            data.append(line)

        line = "DataVgates, Vgates(Comp)" 
        for a in range(len(Vgate)):
            line = "%s, %s" %(line, Vgate[a])
        data.append(line)
        line = "DataVMMVgates, Vgates(VMM), %s" %(VMMVgate)
        data.append(line)

        

        eChar.startThread(target = std.writeDataToFile , args=(cp.deepcopy(header), data, eChar.getFolder(), eChar.getFilename(eChar.curCycle, eChar.curCycle+1)))
        
        
        #row = eChar.dhAddRow([CurrPlotVal1,CurrPlotVal2,CurrPlotVal3,CurrPlotVal4])
        row = eChar.dhAddRow([VMM1,VMM2,VMM3,VMM4,VMM5,VMM6,VMM7,VMM8],eChar.curCycle,eChar.curCycle+NumofCycles)
        eChar.curCycle = eChar.curCycle + NumofCycles
    else:
        raise ValueError("Must have a correct number of pics for this 8x8 matrix (Max 8)")


    


    
##########################################################################################################################

def VMM_Matrix_Create(PulseChn, GateChn, GNDChn, MatVMMX, NumofRows):

    PCgate = [21,22,23,24,1,2,3,4] 
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
    # Sets the fith entry to the 2nd GND (or universal gnd where we don't calculate the current) and makes array all E's
    NormalInputTemp= [BreakMakeEnt[GNDChn+2] for n in range(24)]

    #print("DDDDDDDDDDDDDDDDDDDD:   ", NormalOutput)
    #print("DKJFHSDKJFKJSKKKKKKK:   ", NormalInputTemp)


    #$BM, BM, BM, BM, BM, BM, BM, BM
    #!12,13,14,15,16,17,18,19,20,21: Normal;
    #B, D, F, D, F, D, F, D, F, A
    #!11,13,14,15,16,17,18,19,20,22: Normal;
    #B, D, F, D, F, D, F, D, F, A
    #!10,13,14,15,16,17,18,19,20,23: Normal;
    #B, D, F, D, F, D, F, D, F, A
    #!9,13,14,15,16,17,18,19,20,24: Normal;
    #B, D, F, D, F, D, F, D, F, A


    for m in range(NumofRows):
        
        MatrixData['MakeBreak'].append(BreakMakeEnt)
        MatrixData['BreakMake'].append(MakeBreakEnt)
        MatrixData['BitInputs'].append(BitInputEnt)
        MatrixData['BitOutputs'].append(BitOutputEnt)

        NormalInput = cp.deepcopy(NormalInputTemp)
        NormalInput[PCgate[m]-1] = BreakMakeEnt[0]
        NormalInput[PCgnd[m]-1] = BreakMakeEnt[1]

        

        for k in range(len(MatVMMX)):
            #print("KK: ", k)
            #print("FDGFGFGFGFGFGFG:   ", int(MatVMMX[k]))
            if int(MatVMMX[k]) == 1:
                NormalInput[PCrram[k]-1] = BreakMakeEnt[2]
            elif int(MatVMMX[k]) == 0:
                NormalInput[PCrram[k]-1] = BreakMakeEnt[3]
            elif int(MatVMMX[k]) == 2:
                NormalInput[PCrram[k]-1] = BreakMakeEnt[4]
            elif int(MatVMMX[k]) == 3:
                NormalInput[PCrram[k]-1] = BreakMakeEnt[5]
            elif int(MatVMMX[k]) == 4:
                NormalInput[PCrram[k]-1] = BreakMakeEnt[6]
            elif int(MatVMMX[k]) == 5:
                NormalInput[PCrram[k]-1] = BreakMakeEnt[7]
            else:
                raise ValueError("Must have a correct number in your VMM matrix!")

        MatrixData['NormalInputs'].append(NormalInput)
        MatrixData['NormalOutputs'].append(NormalOutput)

    ReadMatrix = cp.deepcopy(MatrixData)
    #print("GGGGGGGGGGGGGGGGGGGGGGGGGG: ", ReadMatrix['NormalInputs'])

    return ReadMatrix
    


def ArrayStr2Int(File):
    #print("FILE: ", File)

    #with open(File) as csv_file:
        #csv_reader = csv.reader(csv_file, delimiter=',')
    results = []
    with open(File) as csvfile:
        reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC) # change contents to floats
        for row in reader: # each row is a list
            results.append(row)

    #print("RESULTS:  ", results)
    #print(type(results))


    array1 = np.asarray(results)

    #print("Array1 ", array1)

    return array1


def UTK_Forming_Circuit_2(eChar, VDD, Vreset, Vread, Cycle):

    # A-Vlow(0V), B-MR(Midrail-0.6V), C-Vhigh(1.2V) , D-Output1 (Voltage), E-Output2 (Voltage) F-Output3 (Voltage) G-OUtput4 (Current)
    # for testing (C and D are not really necessary but I have the SMUs so whatever)
    Chns = [1,2,3,4,5,6,7]
    #will the channel be aiming to set a voltage or a current? the other property will be measured. 
    # i.e. True = Set Voltage, Measure current - False = Set Current, Measure Voltage
    VorI = [True, True, True, True, True, True, True]
    # if we're setting a voltage, what will it be?
    # A-VDD=3.3V, B-GND=0V, C-Vreset(1.5V), D-0V (Seperate gnd to get current), E-Vread=-0.2V, F-Vform/Vprog, G-0V(other zero)
    Val = [VDD, 0, Vreset, 0, Vread, 3.3, 0]
    # if we're setting a current, what will it be?
    # what is the compliance current?
    #IComp = [1e-3,1e-3,1e-3,1e-3,1e-3,1e-3]
    #if Vreset < 0:
       # raise ValueError("Vreset must be positive to work in this circuit!")

    #this sets up the parameter analyzer
    #ret1 = eChar.E5274A.SpotMeasurement(Chns, VorI, Val, IComp=IComp)
    ret1 = eChar.E5274A.SpotMeasurement(Chns, VorI, Val)

    #this will control the matrix
    #Main factor is[eChar.Configuration.getMatrixConfiguration()]. This tells the program to use the matrix that is given in the selct file under configuration tab. :)
    MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), eChar.Configuration.getMatrixConfiguration(), True)

    ret = []
    n = 0
    CurCycle = 0
    print("Cycle = ", range(Cycle))
    
    for CurCycle in range(Cycle):
        #for each line in the matrix config we've generated, set the connections
        while MC.setNext():

            stop = False
            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
                tm.sleep(1)
            
            if stop:
                break
            
            #do the measurement we've defined
            #out = eChar.E5274A.SpotMeasurement(Chns, VorI, Val, IComp=IComp)
            out = eChar.E5274A.SpotMeasurement(Chns, VorI, Val)
            #resis=abs(-0.2/out[0])
            #print("Output: ", out)
            #out.append(resis)
            #print("Output Resist %s", out)
            
            #Resistance = Vread/(out['Data'][4])
            #out['Data'].append(Resistance)
            #print("Output: ", out['Data'])

            #append the measurement to our output log
            ret.append([i[0] for i in out['Data']])
            

            #update the plots  A-Gnd, B-form/gate2, C-gate1, D-set, E-rd, F-gate3, G-reset 
            Trac = ret[-1][0:7]
            eChar.IVplotData.put({"Add": True, "lineStyle": 'o', 'legend': ['IVDD(3.3V)','IGND(0V)', 'Ipin(reset)', 'Iread(Vn output)','Iread(Vpo Input)','Iform/Iprog(3.3V)','Iother(0V)'], "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': "Matrix Iteration", "Ylabel": 'Current (A)', 'Title': "input current", "ValueName": 'Current'})

            Trac = ret[-1][0]
            eChar.IVplotData.put({"Add": True, "lineStyle": 'o', "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Matrix Iteration', "Ylabel": 'current (A)', 'Title': "output current", "ValueName": 'Current'})
            n = n+1
        
        print("CurCycle = ", CurCycle)
        #print("Cycle Value = ", Cycle)
        MC = []
        #this will control the matrix
        #Main factor is[eChar.Configuration.getMatrixConfiguration()]. This tells the program to use the matrix that is given in the selct file under configuration tab. :)
        MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), eChar.Configuration.getMatrixConfiguration(), True)


    # write a header to our output file
    header = out['Header']    
    header.append('DataName, IVDD(3.3V), GND(0V), Ipin(reset), Iread(Vn output), Iread(Vpo Input), Iform/Iprog(3.3V), Iother(0V)')
    header.append('Dimension, %d, %d, %d, %d, %d, %d, %d' %(n,n,n,n,n,n,n))

    out = []
    for i in ret:
        add = 'DataValue'
        for x in i: 
            add = "%s, %s" %(add, x)

        #try:
        #    resis=abs(-0.2/i[6])
        #    print('resistance',resis,'current',i[6])
        #    add="%s,%s" %(add,str(resis))
        #except ZeroDivisionError:
        #    add="%s,%s" %(add,'error')

        out.append(add)
        
    #pass the data in RAM to a process which will write it out
    eChar.startThread(target = std.writeDataToFile , args=(cp.deepcopy(header), out, eChar.getFolder(), eChar.getFilename()))
    