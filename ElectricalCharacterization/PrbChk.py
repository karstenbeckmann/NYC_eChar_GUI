'''
This file contains definitons from Maximilian Liehr
'''

import time as tm
import StdDefinitions as std
import DataHandling as dh
import threading as th
import math as ma
import numpy as np
import queue as qu


###########################################################################################################################

def ProbeCardCheck2x12(eChar, test):

    Chns = [1,2,3,4,5,6,7]
    VorI = [True, True, True, True, True, True, True]
    Val = [0.0, 1.2, 3.3, 1.2, 0.3, 0.0, 0.0]
    IComp = [1e-3, 1e-3, 1e-3, 1e-3, 1e-3, 1e-3, 1e-3]
    Typ = 'SpotMeas'

    MeasType = 'ProbeCardCheck2x12'

    MC = std.MatrixChange(eChar.Instruments.getMatrixInstrument(), eChar.Configuration.getMatrixConfiguration(), True)

    ret = []
    n = 0
    while MC.setNext():

        if eChar.checkStop():
            break

        out = eChar.E5274A.SpotMeasurement(Chns, VorI, Val, IComp=IComp)

        ret.append([i[0] for i in out['Data']])

        Trac = ret[-1][0:3]
        eChar.plotIVData({"Add": True, "lineStyle": 'o', 'legend': ['GND', 'Vlow', 'Vhigh'], "lineWidth":0.5, 'Yscale': 'log',  "Traces":Trac, 'Xaxis': False, 'Xlabel': "Matrix Iteration", "Ylabel": 'current (A)', 'Title': "input current", "MeasurementType": Typ, "ValueName": 'Current'})

        Trac = ret[-1][3]
        eChar.plotIVData({"Add": True, "lineStyle": 'o', "lineWidth":0.5, 'Yscale': 'lin',  "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Matrix Iteration', "Ylabel": 'voltage (V)', 'Title': "output voltage", "MeasurementType": Typ, "ValueName": 'voltage'})
        n = n+1

    header = out['Header']

    header.insert(0,"TestParameter,Measurement.Type,%s" %(MeasType))
    header.append("Measurement,Device,%s" %(eChar.device))
    header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.localtime)))

    header.append('DataName, Ignd, Ivlow, Ivhigh, Irvt, Isrc, Idrn, Vsense')
    header.append('Dimension, %d, %d, %d, %d, %d, %d, %d' %(n,n,n,n,n,n,n))

    out = []
    for i in ret:
        add = 'DataValue'
        for x in i:
            add = "%s, %s" %(add, x)
        out.append(add)

    

    eChar.writeDataToFile(header, out, Typ=Typ)
