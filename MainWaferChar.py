"""
This is the main program that governs the Electrical wafer level Characterization integrated devices
Written by: Karsten Beckmann
Date: 7/25/2018
email: kbeckmann@sunypoly.edu
"""

### START DO NOT CHANGE ###
import numpy as np
import math as ma
import threading as th
import ECharacterization as EC
import ProbeStations as PS
import Keithley as KL
import matplotlib as mp 
import matplotlib.pyplot as plt
import time as tm 
import datetime as dt
import Configuration as cf
import pyvisa as vs
import StdDefinitions as std
import sys
import DataHandling as dh
import GraphicalInterface as GI
import GraphicalInterface as GI 
import queue as qu
import ToolHandle as tool

### END DO NOT CHANGE

#adjust these values according to your setup: 

GPIBB1500 = "GPIB0::18::INSTR"
GPIBProbeStation = "GPIB0::22::INSTR"
GPIBMatrix = "GPIB0::14::INSTR"

Mainfolder = 'C:/Users/KB511298/Documents/E-Test_Python'
Subfolder = 'TestReRAM'
DeviceName = 'skynet1R'
WaferID = '1820BRSN001.001'
SpecFile = 'C:/Users/KB511298/Documents/PythonScripts/AutomatedProbingFailingConditions.txt'
#Die and Wafer Size in mm
DieSizeX = 12
DieSizeY = 15
WaferSize = 300
WaferMapVariable = 'resistance'

#locaiton of the center die with respect to the wafer in fraction of the die
CenterLocation = [0,0]
#The die file must have two integer numbers seperated by a comma, 
#Each entry must be in a new row or seperated by ';'
#I.E.
#0,0
#1,1
#or
#0,0;1,1
#DieFile = "C:/Users/KB511298/Documents/PythonScripts/AutomatedProbing/StdDieFile.csv"
DieFile = None

#In addition you can choose between several DieMaps by using the following digits
#The diefile gets preferred
#0. Current Die
#1. Full 
#2. chess
#3. Tier 3 chess field
#4. Tier 4 chess field
DieMap = 4

#Device Seperation to measure multiple devices on a Die use Die seperation and the array size 
#Values in um
Xseperation = -200
Yseperation = 200

NumXdevices = 2
NumYdevices = 1


#Please put your algorithms form ECharacterization in here. 
def deviceCharacterization(eChar, Var1=False, Var=False):

    #for the B1530, please set the appropriate channel parameters
    eChar.setChannelParameter(201, eChar.WGFMU_OPERATION_MODE_PG, measureMode=eChar.WGFMU_MEASURE_MODE_VOLTAGE, 
                                forceVoltageRange=eChar.WGFMU_FORCE_VOLTAGE_RANGE_5V, measureCurrentRange=eChar.WGFMU_MEASURE_CURRENT_RANGE_10MA)
    eChar.setChannelParameter(202, eChar.WGFMU_OPERATION_MODE_FASTIV, measureMode=eChar.WGFMU_MEASURE_MODE_CURRENT, 
                                forceVoltageRange=eChar.WGFMU_FORCE_VOLTAGE_RANGE_3V, measureCurrentRange=eChar.WGFMU_MEASURE_CURRENT_RANGE_10MA)
    
    eChar.setDCVoltages(SMUs=[3], Vdc=[-0.7], DCcompl=[1e-3])
    eChar.PulseForming(201,202,5,1e3,10e-6, 10e-6, 0,1e-3,100, Vread=0.2)
    #tm.sleep(1)
    eChar.setDCVoltages(SMUs=[3], Vdc=[-0.3], DCcompl=[1e-3])
    eChar.PulseReset(201,202,-1.8, 1e-3, 100e-3 ,100e-3, 0, 1e-3, 1000)

    eChar.PulseSet(201,202, 2.5, 1e-5, 100e-6, 100e-6, 0, 10e-6, 100)
    #Dontwork = 0
    #eChar.DyChar(3, -0.1, 1e-3, 201, 202, 2.5, -1.5, 10e-6, 1e-6, 1e-6, 0, 10e-6, 100, 
    #                   Specs=[800, 6000, 6000, 1e6], read=True, tread=10e-6, Vread=-0.2, initalRead=True)

    #eChar.DyChar(SMUs, Vdc, DCcompl, PulseChn, GroundChn, Vset, Vreset, delay, trise, tfall, twidth, tbase, MeasPoints, 
    #                   Specs, read=True, tread=10e-6, Vread=-0.2, initalRead=True)


    #eChar.PulseSet(201,202, 2.5, 1e-5, 100e-6, 100e-6, 0, 10e-6, 100)
    #eChar.PulseReset(201,202,-1.5, 100e-3, 10e-3, 10e-3,0,100e-3,100)
    #eChar.PulseSet(201,202, 2.5, 1e-5, 100e-6, 100e-6, 0, 10e-6, 100)
     
    #eChar.setChannelParameter(202, eChar.WGFMU_OPERATION_MODE_FASTIV, measureMode=eChar.WGFMU_MEASURE_MODE_CURRENT, 
    #                            forceVoltageRange=eChar.WGFMU_FORCE_VOLTAGE_RANGE_3V, measureCurrentRange=eChar.WGFMU_MEASURE_CURRENT_RANGE_1MA)
    #if Dontwork == 1:
    #    Dontwork = 0

    eChar.PulseIV(201, 202, 2.5, -1.5, 10e-6, 10e-6, 10e-6, 0, 100e-6, 100e-6, 0, 100e-6, 100, 10, tread=100e-6, initialRead=False)
    eChar.performEndurance(201, 202, 2.5, -1.5, 10e-6, 1e-6, 1e-6, 0, 1e-6, 1e-6, 0, 10e-6, 100000, MeasPoints=100, tread=1e-6, Vread=-0.2, IVIteration=100000, IVcount=10, ReadEndurance=True, DoYield=False)

    #eChar.PulseRead(201,202,1,1e-4,1e-4,1e-5)

#### START DO NOT CHANGE ###

#window = thtk.Tk()
window = thtk.ThemedTk()
#window.withdraw()

#window.deiconify()
try:
    Devices = tool.ToolHandle(offline=False)
except SystemError as e:
    sys.exit()

Configuration = cf.Configuration('config.csv')

eChar = EC.ECharacterization(Devices, WaferChar=True, Configuration=Configuration)
#eChar.setWaferID(WaferID)
#eChar.Subfolder=Subfolder


ProStat = Devices.getProberInstrument()
if ProStat != None:
    ProStat.setTimeOut(60000)
    initPos = ProStat.ReadChuckPosition("X","C")
    initPosMic = ProStat.ReadChuckPosition("Y","C")

updateTime = 0.1


if DieFile == None:
    dies = std.CreateDiePattern(DieMap,WaferSize,DieSizeX,DieSizeY, CenterLocation)
else:
    dies = std.LoadDieFile(DieFile,WaferSize,DieSizeX,DieSizeY)


dies = std.sortDies(dies)

dieLen = len(dies)

threads = qu.Queue()

std.CreateExternalHeader(eChar,WaferSize,Xseperation,Yseperation,NumXdevices,NumYdevices,dieLen,DieFile, DieMap)
GraInterface = GI.GraphicalInterface(window, 'large',"Wafer Map",Configuration, eChar, Devices, threads)
#GraIntThread = th.Thread(target=GraInterface.start, args=(updateTime,))
#GraIntThread.start()


#ExecThread = th.Thread(target=std.MesurementExecution, args=(deviceCharacterization, eChar, WaferProperties, dies, threads, GraInterface, ProStat))
#ExecThread.start()

tk.mainloop()

while not threads.empty:
    thread = threads.get()
    if thread.is_alive():
        thread.join()

#while GraIntThread.isAlive():
#    tm.sleep(updateTime*5)

Devices.close()
exit()
#### END DO NOT CHANGE ###
