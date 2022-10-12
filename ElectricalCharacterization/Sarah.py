'''
This file contains definitons from Sarah Rafiq
'''

import time as tm
import StdDefinitions as std
import DataHandling as dh
import threading as th
import math as ma
import numpy as np
import queue as qu


def Meas_8x81T1RComp(eChar, test1):

    # A-Gnd, B-form/gate2(low), C-gate1(high), D-set, E-rd, F-reset, G-Gnd for testing
    Chns = [1,2,3,4,5,6,7]
    #will the channel be aiming to set a voltage or a current? the other property will be measured. 
    # i.e. True = Set Voltage, Measure current - False = Set Current, Measure Voltage
    VorI = [True, True, True, True, True,True,True]
    # if we're setting a voltage, what will it be?
    Val = [0, 1.2, 1.8, 2.5,-0.2, -1.5, 0]
    # if we're setting a current, what will it be?
    # what is the compliance current?
    IComp = [1e-3,1e-3,1e-3, 1e-3, 1e-3,1e-3,1e-3]
    # what's the measurement type?
    Typ = 'SpotMeas'
    
    #what's the name of this program?
    MeasType = '8x81T1RComputing'

    #this sets up the parameter analyzer
    ret1 = eChar.E5274A.SpotMeasurement(Chns, VorI, Val, IComp=IComp)

    #this will control the matrix
    MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), eChar.Configuration.getMatrixConfiguration(), True)

    ret = []
    n = 0
    #for each line in the matrix config we've generated, set the connections
    while MC.setNext():

        if eChar.checkStop():
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
        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', 'legend': ['Ignd','Ivg(1.2V)', 'Ivg(1.8V)', 'Iset','Iread','Ireset','Ignd2, Resistance'], "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': "Matrix Iteration", "Ylabel": 'Current (A)', 'Title': "input current", "MeasurementType": Typ, "ValueName": 'Current'})

        Trac = ret[-1][0]
        eChar.IVplotData.put({"Add": True, "lineStyle": 'o', "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Matrix Iteration', "Ylabel": 'current (A)', 'Title': "output current", "MeasurementType": Typ, "ValueName": 'Current'})
        n = n+1

    # write a header to our output file
    header = out['Header']
    
    header.insert(0,"TestParameter,Measurement.Type,%s" %(MeasType))
    header.append("Measurement,Device,%s" %(eChar.device))
    header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.localtime)))
    
    header.append('DataName, Ignd, Ivg(1.2V), Ivg(1.8V), Iset, Iread, Ireset, Ignd2, Resistance')
    header.append('Dimension, %d, %d, %d, %d, %d, %d, %d, %d' %(n,n,n,n,n,n,n,n))

    out = []
    for i in ret:
        add = 'DataValue'
        for x in i: 
            add = "%s, %s" %(add, x)

        try:
            resis=abs(-0.2/i[0])
            print('resistance',resis,'current',i[0])
            add="%s,%s" %(add,str(resis))
        except ZeroDivisionError:
            add="%s,%s" %(add,'error')

        out.append(add)
        
    #pass the data in RAM to a process which will write it out
    eChar.writeDataToFile(header, out, Typ=Typ)
