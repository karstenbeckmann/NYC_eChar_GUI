"""
Written by: Karsten Beckmann and Maximilian Liehr
Institution: SUNY Polytechnic Institute
Date: 11/18/2018

This program is a wrapper for the use of the Keysight B1110A. 
"""

import datetime as dt
import time as tm
import types as tp
from ctypes import *
import StdDefinitions as std
import engineering_notation as eng
import math as ma
from Exceptions import *

import numpy as np
import pyvisa as vs


#Agilen Pulse Generator 81110A: 
class Agilent_81110A:

    printOutput = False

    def __init__(self, rm=None, GPIB_adr=None, ErrorCheck=True, calibration=False, selfTest=False, Device=None, Reset=True, PrintOutput=False, DisplayOn=False, Execute=False):
        self.inst=None
        if (rm == None or GPIB_adr == None) and Device == None:
            self.write("Either rm and GPIB_adr or a device must be given transmitted")  #maybe a problem, tranmitting None type
        elif Device == None:    

            try:
                self.inst = rm.open_resource(GPIB_adr)
                
            except:
                self.write("The device %s does not exist." %(GPIB_adr))  #maybe a problem, tranmitting None type
        
        else:
            self.inst = Device
        self.DisplayOn = DisplayOn

        self.printOutput = PrintOutput

        ret = self.instQuery("*IDN?")
        if not ret.find("HEWLETT-PACKARD,HP81110A") == -1:
            self.write("You are using the %s" %(ret[:-2]))
        else:
            #print("You are using the wrong agilent tool!")
            exit("You are using the wrong agilent tool!")
        #print(ret)
        # do if Agilent\sTechnologies,E5270A,0,A.01.05\r\n then correct, else the agilent tool you are using is incorrect
        if calibration: 
            self.calibration()
        
        if Reset:
            self.reset()
        if DisplayOn:
            self.turnDisplayOn()
        else:
           self.turnDisplayOff()
        if ErrorCheck == False:
            self.SwitchOffErrorChecking()
    
    def instWrite(self, command):
        ret = self.inst.write(command)
        if self.printOutput:
            self.write("Write: %s" %(command))
        n = 0
        jobDone = False
        while not jobDone and n < 10:
            try:
                stb = self.inst.read_stb()
                jobDone = True
            except vs.VisaIOError:
                None
            n = n+1
        if jobDone:
            binStb = std.getBinaryList(stb)
            err = binStb[5]
        else: 
            err = 1

        if err == 1:
            ret = self.inst.query("SYST:ERR? 1\n")
            raise B1110A_Error("PG81110 encountered error #%d." %(ret))
        return ret


    def instRead(self):
        ret = self.inst.read()
        if self.printOutput:
            self.write("Read")
        return ret
    
    def instQuery(self, command):
        ret = self.inst.query(command)
        if self.printOutput:
            self.write("Query: %s" %(command))
        n = 0
        jobDone = False
        while not jobDone and n < 10:
            try:
                stb = self.inst.read_stb()
                jobDone = True
            except vs.VisaIOError:
                None
            n = n+1
        if jobDone:
            binStb = std.getBinaryList(stb)
            err = binStb[5]
        else: 
            err = 1

        if err == 1:
            ret = self.inst.query("ERR? 1\n")
            raise B1110A_Error("PG81110 encountered error #%d." %(ret))
        return ret

    def reset(self):
        if self.DisplayOn:
            self.instWrite("*RST")
        else:
            self.instWrite(":SYST:PRES")

    def turnDisplayOff(self):
            self.instWrite(":DISP OFF")
    
    def turnDisplayOn(self):
            self.instWrite(":DISP ON")


    def write(self, com):
        if self.printOutput:
            print(com)

    def setExtInputImpedance(self, imp):

        if not isinstance(imp, int):
            raise B1110A_InputError("Impedance must be either 50 or 10000 ohm.")
        if not (imp == 50 or imp == 10000): 
            raise B1110A_InputError("Impedance must be either 50 or 10000 ohm.")
        if imp == 50:
            self.instWrite(":ARM:IMP 50OHM")
        else:
            self.instWrite(":ARM:IMP 10KOHM")

    def setArmFrequency(self, freq):

        if not isinstance(freq, (int,float)):
            raise B1110A_InputError("Trigger Frequency must be between 1mHz and 150MHz.")
        if 1e-3 <= freq <=150e6:
            raise B1110A_InputError("Trigger Frequency must be between 1mHz and 150MHz.")
        
        self.instWrite(":ARM:FREQ %sHZ" %(eng.EngNumber(freq)))

    def enableArmExtWidth(self):
        self.instWrite(":ARM:EWID ON")

    def disableArmExtWidth(self):
        self.instWrite(":ARM:EWID OFF")

    def setArmLevel(self, voltage):

        if not isinstance(voltage, (int,float)):
            raise B1110A_InputError("Trigger Level must be between -10V and 10V.")
        if -10 > voltage > 10:
            raise B1110A_InputError("Trigger Level must be between -10V and 10V.")
        
        self.instWrite(":ARM:LEV %.2fV"%(voltage))
    
    def setArmPeriod(self, period):

        if not isinstance(period, (int,float)):
            raise B1110A_InputError("Arm Period must be between 3.03ns and 999.5s.")
        if 3.03e-9 > period > 999.5:
            raise B1110A_InputError("Arm Period must be between 3.03ns and 999.5s.")
        
        self.instWrite(":ARM:PER %sS" %(str(eng.EngNumber(period, precision=0)).upper()))

    def setEdgeArm(self):
        self.instWrite(":ARM:SENS EDGE")

    def setLevelArm(self):
        self.instWrite(":ARM:SENS LEV")

    def setArmSlopePositive(self):
        self.instWrite(":ARM:SLOP POS")

    def setArmSlopeNegative(self):
        self.instWrite(":ARM:SLOP NEG")

    def setArmSlopeEither(self):
        self.instWrite(":ARM:SLOP EITH")

    def setArmSourceInternal1(self):        
        self.instWrite(":ARM:SOUR IMM")

    def setArmSourceInternal2(self):        
        self.instWrite(":ARM:SOUR INT2")

    def setArmSourceExternal(self):        
        self.instWrite(":ARM:SOUR EXT")

    def setArmSourceManual(self):        
        self.instWrite(":ARM:SOUR MAN")

    def enableChannelAddition(self):      
        self.instWrite(":CHAN:MATH PLUS")

    def disableChannelAddition(self):      
        self.instWrite(":CHAN:MATH OFF")

    def calibration(self):
        ret = self.instQuery(":CAL:ALL")
        return ret
    
    def getPatternData(self, data, chn=None):

        if not isinstance(data, int):
            raise B1110A_InputError("The Pattern data must be an integer (check manual for more information).")
        if not (chn==1 or chn==2 or (str(chn).lower() == 'both') or chn == None):
            raise B1110A_InputError("The Channel to get the Pattern must be 1,2 or 'Both'")
        ret = None
        if chn == 1:
            ret = self.instQuery(":DIG:PATT:DATA1 %d" %(data))
        elif chn == 2:
            ret = self.instQuery(":DIG:PATT:DATA2 %d" %(data))
        elif str(chn).lower() == 'both':
            ret = self.instQuery(":DIG:PATT:DATA3 %d" %(data))
        else:
            ret = self.instQuery(":DIG:PATT:DATA %d" %(data))
        return ret

    def setPseudoRandomBitSequence(self, n=7, length=2, chn=None):
        
        if not isinstance(n, int):
            raise B1110A_InputError("The basis of the PRBS must be between 7 and 14.")
        if 7 > n > 14:
            raise B1110A_InputError("The basis of the PRBS must be between 7 and 14.")
        if not isinstance(length, int):
            raise B1110A_InputError("The length of the PRBS must be between 2 and 16384.")
        if 2 > length > 16384:
            raise B1110A_InputError("The length of the PRBS must be between 2 and 16384.")

        if not (chn==1 or chn==2 or (str(chn).lower() == 'both') or chn == None):
            raise B1110A_InputError("The Channel to get the Pattern must be 1,2 or 'Both'")
        
        if not isinstance(n, int):
            raise B1110A_InputError("The Pattern data must be an integer (check manual for more information).")
        
        if chn == 1:
            ret = self.instQuery(":DIG:PATT:PRBS1 %d, %d" %(n, length))
        elif chn == 2:
            ret = self.instQuery(":DIG:PATT:PRBS2 %d, %d" %(n, length))
        elif str(chn).lower() == 'both':
            ret = self.instQuery(":DIG:PATT:PRBS3 %d, %d" %(n, length))
        else:
            ret = self.instQuery(":DIG:PATT:PRBS %d, %d" %(n, length))
        return ret

    def setClockData(self, n, length, chn=None):

        if not isinstance(n, int):
            raise B1110A_InputError("The divider of the Clock data stream must be between 2 and 16384.")
        if 2 > n > 16384:
            raise B1110A_InputError("The divider of the Clock data stream must be between 2 and 16384.")
        if not isinstance(length, int):
            raise B1110A_InputError("The length of the Clock data stream must be between 2 and 16384.")
        if 2 > length > 16384:
            raise B1110A_InputError("The length of the Clock data stream must be between 2 and 16384.")

        if not (chn==1 or chn==2 or (str(chn).lower() == 'both') or chn == None):
            raise B1110A_InputError("The Channel to get the Pattern must be 1,2 or 'Both'")
        
        if not isinstance(n, int):
            raise B1110A_InputError("The Pattern data must be an integer (check manual for more information).")
        
        if chn == 1:
            ret = self.instQuery(":DIG:PATT:PRES1 %d, %d" %(n, length))
        elif chn == 2:
            ret = self.instQuery(":DIG:PATT:PRES2 %d, %d" %(n, length))
        elif str(chn).lower() == 'both':
            ret = self.instQuery(":DIG:PATT:PRES3 %d, %d" %(n, length))
        else:
            ret = self.instQuery(":DIG:PATT:PRES %d, %d" %(n, length))
        return ret

    def getModel(self):
        ret = self.instQuery("*IDN?")
        return ret

    def enableDigitalPatternMode(self):
        self.instWrite(":DIG:PATT ON")

    def disableDigitalPatternMode(self):
        self.instWrite(":DIG:PATT OFF")
    
    def enableAutomaticPatternUpdate(self):
        self.instWrite(":DIG:PATT:UPD ON")
    
    def disableAutomaticPatternUpdate(self):
        self.instWrite(":DIG:PATT:UPD OFF")
        
    def UpdatePatternData(self):
        self.instWrite(":DIG:PATT:UPD ONCE")

    def setReturnToZeroDataFormat(self, chn=None):
        
        if not (chn==1 or chn==2 or chn == None):
            raise B1110A_InputError("The Channel to get the Pattern must be 1,2")
        if chn == None:
            self.instWrite(":DIG:SIGN:FORM RZ")
        else:
            self.instWrite(":DIG:SIGN:FORM%d RZ" %(chn))


    def setNonReturnToZeroDataFormat(self, chn=None):
        if not (chn==1 or chn==2 or chn == None):
            raise B1110A_InputError("The Channel to get the Pattern must be 1,2")
        if chn == None:
            self.instWrite(":DIG:SIGN:FORM NRZ")
        else:
            self.instWrite(":DIG:SIGN:FORM%d NRZ" %(chn))

    def getMemoryCardListing(self):
        return self.instQuery(":MMEM:CAT?")

    def setMemoryCardDirectory(self, direc=None):
        if not isinstance(direc, (str, type(None))):
            raise B1110A_InputError("The new directory must be a string or None (root)")
        
        if direc != None:
            self.instWrite(":MMEM:CDIR direc")
        else:
            self.instWrite(":MMEM:CDIR")

    def copyFile(self, filename, copy):
        if not isinstance(filename, (str,)):
            raise B1110A_InputError("The filename must be a string.")
        if not isinstance(copy, (str,)):
            raise B1110A_InputError("The copy name must be a string.")
        
        self.instWrite(":MMEM:COPY %s, %s" %(filename, copy))
        
    def deleteFile(self, filename):
        if not isinstance(filename, (str,)):
            raise B1110A_InputError("The filename must be a string.")

        self.instWrite(":MMEM:DEL %s" %(filename))

    def InitializeMemoryCard(self):
        self.instWrite(":MMEM:INIT")

    def LoadSettingIntoInternalMemory(self, n, filename):
        if not isinstance(filename, (str,)):
            raise B1110A_InputError("The filename must be a string.")
        if not isinstance(n, int):
            raise B1110A_InputError("n must be an integer from 0 to 9")
        if 0 > n < 9:
            raise B1110A_InputError("n must be an integer from 0 to 9")
        
        self.instWrite(":MMEM:LOAD:STAT %d, %s" %(n, filename))


    def StoreSettingOntoMemoryCard(self, n, filename):
        if not isinstance(filename, (str,)):
            raise B1110A_InputError("The filename must be a string.")
        if not isinstance(n, int):
            raise B1110A_InputError("n must be an integer from 0 to 9")
        if 0 > n < 9:
            raise B1110A_InputError("n must be an integer from 0 to 9")
        
        self.instWrite(":MMEM:STOR:STAT %d, %s" %(n, filename))

    def turnOnOutput(self, chn=1):

        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        jobDone = False
        n = 0
        while n < 10 and not jobDone: 
            self.instWrite(":OUTP%d ON" %(chn))
            ret = self.instQuery(":OUTP%d?" %(chn))
            try:
                ret = int(ret.strip())
            except:
                ret = 0
            if int(ret) == 1:
                jobDone = True
            n = n+1

    

    def turnOffOutput(self, chn=1):

        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        jobDone = False
        n = 0
        while n < 10 and not jobDone: 
            self.instWrite(":OUTP%d OFF" %(chn))
            ret = self.instQuery(":OUTP%d?" %(chn))
            try:
                ret = int(ret.strip())
            except:
                ret = 1
            if int(ret) == 0:
                jobDone = True
            n = n+1

    def turnDifferentialOutputOn(self, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        jobDone = False
        n = 0
        while n < 10 and not jobDone: 
            self.instWrite(":OUTP%d:COMP ON" %(chn))
            ret = self.instQuery(":OUTP%d:COMP?" %(chn))
            try:
                ret = int(ret.strip())
            except:
                ret = 1
            if int(ret) == 0:
                jobDone = True
            n = n+1
    
    def turnDifferentialOutputOff(self, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.") 
        
        jobDone = False
        n = 0
        while n < 10 and not jobDone: 
            self.instWrite(":OUTP%d:COMP OFF" %(chn))
            ret = self.instQuery(":OUTP%d:COMP?" %(chn))
            try:
                ret = int(ret.strip())
            except:
                ret = 1
            if int(ret) == 0:
                jobDone = True
            n = n+1

    def setOutputImpedance(self, impedance, chn=1):

        if not isinstance(impedance, int):
            raise B1110A_InputError("The impedance must be either 50 or 1000")
        if not (impedance == 50 or impedance==1000):
            raise B1110A_InputError("The impedance must be either 50 or 1000")
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")

        self.instWrite(":OUTP%d:IMP %dOHM" %(chn, impedance))
    
    def setExpectedLoadImpedance(self, impedance, chn=1):

        if not isinstance(impedance, int):
            raise B1110A_InputError("The impedance must be either 50 or 1e6")
        if not (impedance == 50 or impedance==1e6):
            raise B1110A_InputError("The impedance must be either 50 or 1e6")
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")

        self.instWrite(":OUTP%d:IMP %sOHM" %(chn, eng.EngNumber(impedance, precision=2)))

    def invertedOutputPolarity(self, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instWrite(":OUTP%d:POL INV"%(chn))
        
    def normalOutputPolarity(self, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instWrite(":OUTP%d:POL NORM"%(chn))
    
    def setCurrentOutput(self, current, chn=1):
        if not isinstance(current, (int,float)):
            raise B1110A_InputError("The current amplitude must be between 0 and 400mA (0 - 400e-3")
        if 0 > current > 400e-3:
            raise B1110A_InputError("The current amplitude must be between 0 and 400mA (0 - 400e-3")
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instWrite(":CURR%d %sA"%(chn,str(eng.EngNumber(current)).upper()))

    def setCurrentOffset(self, offset, chn=1):
        if not isinstance(offset, (int,float)):
            raise B1110A_InputError("The current offset must be an integer.")
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instWrite(":CURR%d:OFF %sA"%(chn,str(eng.EngNumber(offset)).upper()))

    def setCurrentLowLevel(self, current, chn=1):
        if not isinstance(current, (int,float)):
            raise B1110A_InputError("The current low level must be between -400mA and 396mA (-400e-3 - 396-3")
        if -400e-3 > current > 396e-3:
            raise B1110A_InputError("The current low level must be between -400mA and 396mA (-400e-3 - 396-3")
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instWrite(":CURR%d:LOW %sA"%(chn,str(eng.EngNumber(current)).upper()))

    def setCurrentLimit(self, current, chn=1):
        if not isinstance(current, (int,float)):
            raise B1110A_InputError("The current limit must be a float/integer")
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        return self.instQuery(":CURR%d:LIM %sA"%(chn,str(eng.EngNumber(current)).upper()))
    
    def setCurrentLimitLow(self, current, chn=1):
        if not isinstance(current, (int,float)):
            raise B1110A_InputError("The current limit low must be a float/integer")
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        return self.instQuery(":CURR%d:LIM:LOW %sA"%(chn,str(eng.EngNumber(current)).upper()))
    
    def turnCurrentLimitsOn(self, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instWrite(":CURR%d:LIM:STAT ON"%(chn))
        
    def turnCurrentLimitsOff(self, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instWrite(":CURR%d:LIM:STAT OFF"%(chn))

    def setPulseFrequency(self, frequency=None):
        if not isinstance(frequency, (int,float, type(None))):
            raise B1110A_InputError("The frequency must be between 1e6 and 330e6 Hz.")
        if frequency != None:
            if 1e6 > frequency > 330e6:
                raise B1110A_InputError("The frequency must be between 1e6 and 330e6 Hz.")
            return self.instWrite(":FREQ %sHz" %(eng.EngNumber("frequency")))
        else:
            return self.instWrite(":FREQ?")
    
    def measureClockInFrequency(self):
        self.instWrite(":TRIG:SOUR EXT2")
        self.instWrite(":FREQ:AUTO ONCE")
        return self.instQuery(":FREQ?")
    
    def enableVoltageSource(self):
        self.instWrite(":HOLD VOLT")
    
    def enableCurrentSource(self):
        self.instWrite(":HOLD CURR")
    
    def setRelativePhaseDelay(self, phase, chn=1):
        if not isinstance(phase, int):
            raise B1110A_InputError("The phase delay must be 0 to 360 degrees")
        if 0 > phase > 360:
            raise B1110A_InputError("The phase delay must be 0 to 360 degrees")
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instWrite(":PHAS%d %d DEG"%(chn, phase))

    def setDutyCycle(self, dutycycle, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not isinstance(dutycycle, (float,int)):
            raise B1110A_InputError("The dutycycle must be between 0.001 and 99.9%")
        if 0.001 > dutycycle > 99.9:
            raise B1110A_InputError("The dutycycle must be between 0.001 and 99.9%")
        
        self.instWrite(":PULS:DCYC%d %dPCT" %(chn, dutycycle))

    def setPulseDelay(self, delay, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not isinstance(delay, (float,int)):
            raise B1110A_InputError("The pulse delay must be between 0 and 999s")
        if 0 > delay > 999:
            raise B1110A_InputError("The pulse delay must be between 0 and 999s")
        
        self.instWrite(":PULS:DEL%d %sS" %(chn, str(eng.EngNumber(delay, precision=0)).upper()))
    
    def getPulseDelay(self, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instQuery(":PULS:DEL%d?" %(chn))

    def setConstantDelay(self, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instQuery(":PULS:DEL%d:HOLD TIME" %(chn))

    def setConstantPhase(self, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instQuery(":PULS:DEL%d:HOLD PRAT" %(chn))

    def setDelayUnit(self, unit, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (unit=="S" or unit=="PCT" or unit=="DEG" or unit == "RAD"):
            raise B1110A_InputError("The unit must be either S (seconds), PCT (percentage), DEG (degree), RAD (radiant).")

        self.instQuery(":PULS:DEL%d:UNIT %s" %(chn, unit))
    
    def turnDoublePulseModeOn(self, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        
        self.instWrite(":PULS:DOUB%d ON"%(chn))
        
    def turnDoublePulseModeOff(self, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        
        self.instWrite(":PULS:DOUB%d OFF"%(chn))

    def setDoublePulseModeDelay(self, delay, chn=1):

        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not isinstance(delay, (float,int)):
            raise B1110A_InputError("The pulse delay must be between 0 and 999s")
        if 3.03e-9 > delay > 999.5:
            raise B1110A_InputError("The pulse delay must be between 0 and 999s")
        
        self.instWrite("PULS:DOUB%d:DEL %s" %(chn, str(eng.EngNumber(delay, precision=0)).upper()))
        

    def setDoubleModeConstantDelay(self, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instWrite(":PULS:DOUB%d:DEL:HOLD TIME" %(chn))

    def setDoubleModeConstantPhase(self, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instWrite(":PULS:DOUB%d:DEL:HOLD PRAT" %(chn))

    def setDoubleModeUnit(self, unit, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (unit=="S" or unit=="PCT"):
            raise B1110A_InputError("The unit must be either S (seconds), PCT (percentage).")

        self.instWrite(":PULS:DOUB%d:DEL:UNIT %s" %(chn, unit))
    
    def setPulseWidthConstant(self, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        
        self.instWrite(":PULS:HOLD%d WIDT"%(chn))

    def setPulseDutyCycleConstant(self, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        
        self.instWrite(":PULS:HOLD%d DCYC"%(chn))
    
    def doSelfTest(self):
        self.instWrite("*TST?")
        tmstart = tm.time()
        timeout = 30

        while True:
            tm.sleep(0.5)
            try:
                stb = self.inst.read_stb()
                jobDone = True
            except vs.VisaIOError:
                continue
            binStb = std.getBinaryList(stb)
            stat = binStb[4]
            
            if stat == 1: 
                ret = self.instRead()
                return int(ret.strip())

            if tmstart+timeout < tm.time():
                raise B1110A_SelfTestError("PG81110: timeout during self-test.")

            tm.sleep(0.5)


    def setPulseTrailingEdgeConstant(self, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        
        self.instWrite(":PULS:HOLD%d TDEL"%(chn))

    def setPulsePeriod(self, period):
        if not isinstance(period, (int,float)):
            raise B1110A_InputError("the pulse period must be float/integer from 3.03ns to 999.5s.")
        if 3.03e-9 > period > 999.5:
            raise B1110A_InputError("the pulse period must be float/integer from 3.03ns to 999.5s.")
        self.instWrite(":PULS:PER %sS" %(str(eng.EngNumber(period)).upper()))

    def getPulsePeriod(self):
        self.instWrite(":TRIG:SOUR EXT2")
        self.instWrite(":PULS:PER:AUTO ONCE")
        return self.instQuery(":PULS:PER?")

    def setTrailingDelay(self, delay, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not isinstance(delay, (float,int)):
            raise B1110A_InputError("The pulse delay must be between 1.5ns and 999s")
        if 1.5e-9 > delay > 999.5:
            raise B1110A_InputError("The pulse delay must be between 1.5ns and 999s")
        self.instWrite(":PULS:TDEL%d %sS" %(chn, str(eng.EngNumber(delay)).upper()))
    
    def setConstantTransistionTime(self, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instWrite(":PULS:TRAN%d:HOLD TIME" %(chn))

    def setConstantTransistionPulseWidthRatio(self, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instWrite(":PULS:TRAN%d:HOLD WRAT" %(chn))

    def setTransistionTimeUnit(self, unit, chn):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (unit=="S" or unit=="PCT"):
            raise B1110A_InputError("The unit must be either S (seconds), PCT (percentage).")
        self.instWrite(":PULS:TRAN%d:UNIT %s"%(chn, unit))

    def setTransistionTimeOfLeadingEdge(self, transTime, chn):
        if not isinstance(transTime, (int,float)):
            raise B1110A_InputError("The Transistion Time must be 0.8ns or 1.6ns")
        #if not (transTime == 8e-10 or transTime == 16e-10):
        #    raise B1110A_InputError("The Transistion Time must be 0.8ns or 1.6ns")
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instWrite(":PULS:TRAN%d %sS" %(chn, str(eng.EngNumber(transTime)).upper()))

    def setTransistionTimeOfTrailingEdge(self, transTime, chn):
        if not isinstance(transTime, (int,float)):
            raise B1110A_InputError("The Transistion Time must be between 0.8ns or 1.6ns")
        if not (transTime == 8e-10 or transTime == 16e-10):
            raise B1110A_InputError("The Transistion Time must be between 0.8ns or 1.6ns")
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instWrite(":PULS:TRAN%d:TRA %s" %(chn, str(eng.EngNumber(transTime)).upper()))

    def turnAutomaticPulseCouplingOn(self, chn):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instWrite(":PULS:TRAN%d:TRA:AUTO ON" %(chn))
        
    def turnAutomaticPulseCouplingOff(self, chn):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instWrite(":PULS:TRAN%d:TRA:AUTO OFF" %(chn))
    
    def CoupleTrailingAndLeadingEdge(self, chn):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instWrite(":PULS:TRAN%d:TRA:AUTO ONCE" %(chn))
    
    def setTriggerOutputToTTL(self, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instWrite(":PULS:TRIG%d:VOLT TTL" %(chn))

    def setTriggerOutputToECL(self, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instWrite(":PULS:TRIG%d:VOLT ECL" %(chn))
       
    def setPulseWidth(self, width, chn=1):
        if not isinstance(width, (float, int)):
            raise B1110A_InputError("The pulse width must be between, 1.5ns and 999.5s.")
        if 1.5e-9 > width > 999.5:
            raise B1110A_InputError("The pulse width must be between, 1.5ns and 999.5s.")
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instWrite(":PULS:WIDT%d %sS" %(chn, str(eng.EngNumber(width)).upper()))

    def setPLLreference(self, source, frequency):
        if not (str(source.lower()) == "internal" or str(source.lower()) == "external"):
            raise B1110A_InputError("The reference source must be either 'internal' or 'external'.")
        if not (frequency == 5e6  or frequency==10e6):
            raise B1110A_InputError("The reference frequency must be 5 or 10 MHz (5e6 or 10e6")

        if str(source.lower())=="internal":
            s = "INT"
        else:
            s = "EXT"
        self.instWrite(":rOSC:SOUR %s" %(s))
        self.instWrite(":ROSC:EXT:FREQ %sHZ" %(eng.EngNumber(frequency)))


    def setVoltageAmplitude(self, voltage, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not isinstance(voltage, (float,int)):
            raise B1110A_InputError("Voltage must be a float/integer from 100mV to 3.8V")
        if 1e-1 > voltage > 3.8:
            raise B1110A_InputError("Voltage must be a float/integer from 100mV to 3.8V")
        self.instWrite(":VOLT%d %sV" %(chn, str(eng.EngNumber(voltage)).upper()))
    
    def setVoltageOffset(self, offset, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not isinstance(offset, (float,int)):
            raise B1110A_InputError("Voltage offset must be a float/integer from -2 to 3.8V")
        if -2 > offset > 3.8:
            raise B1110A_InputError("Voltage offset must be a float/integer from -2 to 3.8V")
        #self.instWrite(":VOLT%d:OFF %sV" %(chn, str(eng.EngNumber(offset)).upper()))
        self.instWrite(":VOLT%d:OFF %sMV" %(chn, offset*1000))
        
    def setVoltageHigh(self, voltage, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not isinstance(voltage, (float,int)):
            raise B1110A_InputError("Voltage high level must be a float/integer from -1.9 to 3.8V")
        if -1.9 > voltage > 3.8:
            raise B1110A_InputError("Voltage high level must be a float/integer from -1.9 to 3.8V")
        self.instWrite(":VOLT%d:HIGH %sV" %(chn, str(eng.EngNumber(voltage)).upper()))

    def setVoltageLow(self, voltage, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not isinstance(voltage, (float,int)):
            raise B1110A_InputError("Voltage low level must be a float/integer from -2 to 3.8V")
        if -2 > voltage > 3.8:
            raise B1110A_InputError("Voltage low level must be a float/integer from -2 to 3.8V")
        self.instWrite(":VOLT%d:LOW %sV" %(chn, str(eng.EngNumber(voltage)).upper()))

    def setVoltageLimitLow(self, voltage, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not isinstance(voltage, (float,int)):
            raise B1110A_InputError("Voltage low limit must be a float/integer from -2 to 3.8V")
        if -2 > voltage > 3.8:
            raise B1110A_InputError("Voltage low limit must be a float/integer from -2 to 3.8V")
        self.instWrite(":VOLT%d:LIM:LOW %sV" %(chn, str(eng.EngNumber(voltage)).upper()))

    def turnVoltageLimitOn(self, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instWrite(":VOLT%d:LIM:STAT ON" %(chn))
        
    def turnVoltageLimitOff(self, chn=1):
        if not isinstance(chn, int):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        if not (chn == 1 or chn ==2):
            raise B1110A_InputError("The channel ID must be eithe 1 or 2.")
        self.instWrite(":VOLT%d:LIM:STAT OFF" %(chn))

    def getStatusEvent(self):
        return self.instQuery(":STAT:QUES:EVEN?")
        
    def getStatusCondition(self):
        return self.instQuery(":STAT:QUES:COND?")

    def setStatusEnableRegister(self, n):
        if not isinstance(n, int):
            raise B1110A_InputError("Enable register number must be between 0 and 32767.")
        if 0 > n > 32767: 
            raise B1110A_InputError("Enable register number must be between 0 and 32767.")
        return self.instWrite(":STAT:QUES:ENAB %d" %(n))

    def setStatusNegTransistionRegister(self, n):
        if not isinstance(n, int):
            raise B1110A_InputError("Negative transition register number must be between 0 and 32767.")
        if 0 > n > 32767: 
            raise B1110A_InputError("Negative transition register number must be between 0 and 32767.")
        return self.instWrite(":STAT:QUES:NTR %d" %(n))

    def setStatusPosTransistionRegister(self, n):
        if not isinstance(n, int):
            raise B1110A_InputError("Positive transition register number must be between 0 and 32767.")
        if 0 > n > 32767: 
            raise B1110A_InputError("Positive transition register number must be between 0 and 32767.")
        return self.instWrite(":STAT:QUES:PTR %d" %(n))

    def SwitchOffErrorChecking(self):
        self.instWrite(":SYST:CHEC OFF")
    
    def ReadError(self):
        return self.instQuery(":SYST:ERR?")

    def getLastPressedKey(self):
        return self.instQuery(":SYST:KEY?")
    
    def PressKey(self, key):
        if not isinstance(key, int):
            raise  ValueError("the key must be an integer form -1 to 30.")
        if -1 > key > 30: 
            raise  ValueError("the key must be an integer form -1 to 30.")
        self.instWrite("SYST:KEY %d" %(key))
    
    def switchSystemSecurityOff(self):
        self.instWrite(":SYST:SEC OFF")

    def switchSystemSecurityOn(self):
        self.instWrite(":SYST:SEC ON")
    
    def getSystemSettings(self):
        return self.instQuery(":SYST:SET?")
    
    def getSystemVersion(self):
        return self.instQuery(":SYST:VERS?")

    def getSystemWarnings(self):
        return self.instQuery(":SYST:WARN:STR?")
    
    def getSystemWarningBuffer(self):
        return self.instQuery(":SYST:WARN:BUFF?")

    def setTriggerCount(self, n):
        if not isinstance(n, int):
            raise B1110A_InputError("the trigger count must be between 1 and 65536")
        if 1 > n > 65536:
            raise B1110A_InputError("the trigger count must be between 1 and 65536")
        self.instWrite(":TRIG:COUN %d" %(n))

    def setTriggerImpedance(self, impedance):
        if not isinstance(impedance, int):
            raise B1110A_InputError("Impedance must be either 50 or 10000 ohm.")
        if not (impedance == 50 or impedance == 1000): 
            raise B1110A_InputError("Impedance must be either 50 or 10000 ohm.")
        if impedance == 50:
            self.instWrite(":TRIG:IMP 50OHM")
        else:
            self.instWrite(":TRIG:IMP 10KOHM")

    def setTriggerLevel(self, voltage):

        if not isinstance(voltage, (int,float)):
            raise B1110A_InputError("Trigger Level must be between -10V and 10V.")
        if -10 <= voltage <= 10:
            raise B1110A_InputError("Trigger Level must be between -10V and 10V.")
        
        self.instWrite(":TRIG:LEV %.2fV"%(voltage))

    def setPositiveTriggerSlope(self):
        self.instWrite(":TRIG:SLOP POS")
        
    def setNegativeTriggerSlope(self):
        self.instWrite(":TRIG:SLOP NEG")

    def setTriggerSourceInternal1(self):        
        self.instWrite(":TRIG:SOUR IMM")

    def setTriggerSourceInternal2(self):        
        self.instWrite(":TRIG:SOUR INT2")

    def setTriggerSourceExternal(self):        
        self.instWrite(":TRIG:SOUR EXT")

    def setTriggerSourceExternal2(self):        
        self.instWrite(":TRIG:SOUR EXT2")

    def setContinousPulse(self, double=False, trigger="internal", doubleChn=2):
        '''
        period: set burst/pulse/pattern repetition time
        SignalFormat: RZ (return to Zero), NRZ (non return to zero)
        trigger: internal, internal2 (PLL), external2
        double: second/other channel generates double
        doubleChn: channel which outputs the double pulse
        '''
        
        self.disableDigitalPatternMode()
        self.setArmSourceInternal1()
        if trigger.lower() == "external2":
            self.setTriggerSourceInternal2()
        elif  trigger.lower() == "internal2" or  trigger.lower() == "pll":
            self.setTriggerSourceInternal2()   
        else:
            self.setTriggerSourceInternal1()
        if double:
            self.turnDoublePulseModeOn(doubleChn)

    def setContinousBurst(self, count, period=1e-7, trigger="", double=False, doubleChn=2):
        '''
        period: set burst/pulse/pattern repetition time
        count: number of pulses/pattern in a burst
        trigger: internal, internal2 (PLL), external2
        double: second/other channel generates double
        doubleChn: channel which outputs the double pulse
        '''

        self.disableDigitalPatternMode()
        self.setTriggerCount(count)
        self.setArmSourceInternal1()
        self.setArmPeriod(period)
        if trigger.lower() == "external2":
            self.setTriggerSourceInternal2()
        elif  trigger.lower() == "internal2" or  trigger.lower() == "pll":
            self.setTriggerSourceInternal2()   
        else:
            self.setTriggerSourceInternal1()
        if double:
            self.turnDoublePulseModeOn(doubleChn)

    def setContinousPattern(self, period=1e-5, count=1, SignalFormat='RZ', trigger="", double=False, doubleChn=2):
        '''
        period: set burst/pulse/pattern repetition time
        count: number of pulses/pattern in a burst
        SignalFormat: RZ (return to Zero), NRZ (non return to zero)
        trigger: internal, internal2 (PLL), external
        double: second/other channel generates double
        doubleChn: channel which outputs the double pulse
        '''
        
        self.enableDigitalPatternMode()
        self.setTriggerCount(count)
        self.setArmSourceInternal1()
        if SignalFormat == "NRZ":
            self.setNonReturnToZeroDataFormat()
        else:
            self.setReturnToZeroDataFormat()
        self.setArmPeriod(period)
        if trigger.lower() == "external2":
            self.setTriggerSourceInternal2()
        elif  trigger.lower() == "internal2" or  trigger.lower() == "pll":
            self.setTriggerSourceInternal2()   
        else:
            self.setTriggerSourceInternal1()  
        self.setArmPeriod(period)
        if double:
            self.turnDoublePulseModeOn(doubleChn)
    
    def setTriggeredBurst(self, period=5e-6, count=2, trigger="internal", arming="manual", double=False, doubleChn=2):
        '''
        period: set burst/pulse/pattern repetition time
        count: number of pulses/pattern in a burst
        trigger: internal, internal2 (PLL), external2 (Clock-In)
        arming: manual, internal2 (PLL), external
        double: second/other channel generates double
        doubleChn: channel which outputs the double pulse
        '''
        
        self.disableDigitalPatternMode()
        self.setEdgeArm()
        self.setTriggerCount(count)
        self.setArmPeriod(period)
        if trigger.lower() == "external2" or trigger.lower() == "clock-in":
            self.setTriggerSourceExternal2()
        elif  trigger.lower() == "internal2" or  trigger.lower() == "pll":
            self.setTriggerSourceInternal2()   
        else:
            self.setTriggerSourceInternal1()

        if arming.lower() == "manual":
            self.setArmSourceManual()
        elif  arming.lower() == "internal2" or  arming.lower() == "pll":
            self.setArmSourceInternal2()
        else:
            self.setArmSourceExternal()
        if double:
            self.turnDoublePulseModeOn(doubleChn)
    
    def setTriggeredPulses(self, arming="", double=False, doubleChn=2):
        '''
        arming: manual, external
        double: second/other channel generates double
        doubleChn: channel which outputs the double pulse
        '''
        
        self.disableDigitalPatternMode()
        self.setEdgeArm()
        if arming.lower() == "manual":
            self.setArmSourceManual()
        else:
            self.setArmSourceExternal()
        if double:
            self.turnDoublePulseModeOn(doubleChn)

    
    def setTriggeredPattern(self, count=2, trigger="internal", arming="manual", SignalFormat="RZ", double=False, doubleChn=2):
        '''
        count: number of pulses/pattern in a burst
        SignalFormat: RZ (return to Zero), NRZ (non return to zero)
        trigger: internal, internal2 (PLL), external
        double: second/other channel generates double
        doubleChn: channel which outputs the double pulse
        '''
        
        self.enableDigitalPatternMode()
        self.setTriggerCount(count)
        self.setEdgeArm()
        if SignalFormat == "NRZ":
            self.setNonReturnToZeroDataFormat()
        else:
            self.setReturnToZeroDataFormat()
        if trigger.lower() == "external2" or trigger.lower() == "clock-in":
            self.setTriggerSourceExternal2()
        elif  trigger.lower() == "internal2" or  trigger.lower() == "pll":
            self.setTriggerSourceInternal2()   
        else:
            self.setTriggerSourceInternal1()

        if arming.lower() == "manual":
            self.setArmSourceManual()
        elif  arming.lower() == "internal2" or  arming.lower() == "pll":
            self.setArmSourceInternal2()
        else:
            self.setArmSourceExternal()
    
    def setGatedBurst(self, period=5e-6, count=2, trigger="internal", arming="manual", double=False, doubleChn=2):
        '''
        period: set burst/pulse/pattern repetition time
        count: number of pulses/pattern in a burst
        trigger: internal, internal2 (PLL), external2 (Clock-In)
        arming: manual, external
        double: second/other channel generates double
        doubleChn: channel which outputs the double pulse
        '''
        
        self.disableDigitalPatternMode()
        self.setLevelArm()
        self.setTriggerCount(count)
        self.setArmPeriod(period)
        if trigger.lower() == "external2" or trigger.lower() == "clock-in":
            self.setTriggerSourceExternal2() 
        elif  trigger.lower() == "internal2" or  trigger.lower() == "pll":
            self.setTriggerSourceInternal2()   
        else:
            self.setTriggerSourceInternal1()

        if arming.lower() == "manual":
            self.setArmSourceManual()
        else:
            self.setArmSourceExternal()
        if double:
            self.turnDoublePulseModeOn(doubleChn)
    
    def setGatedPulses(self, arming="manual", trigger="internal", double=False, doubleChn=2):
        '''
        trigger: internal, internal2 (PLL), external2 (Clock-In)
        arming: manual, external
        double: second/other channel generates double
        doubleChn: channel which outputs the double pulse
        '''
        
        self.disableDigitalPatternMode()
        self.setLevelArm()
        if trigger.lower() == "external2" or trigger.lower() == "clock-in":
            self.setTriggerSourceExternal2() 
        elif  trigger.lower() == "internal2" or  trigger.lower() == "pll":
            self.setTriggerSourceInternal2()   
        else:
            self.setTriggerSourceInternal1()

        if arming.lower() == "manual":
            self.setArmSourceManual()
        else:
            self.setArmSourceExternal()
        if double:
            self.turnDoublePulseModeOn(doubleChn)

    
    def setGatedPattern(self, count=2, trigger="internal", arming="manual", SignalFormat="RZ", double=False, doubleChn=2):
        '''
        count: number of pulses/pattern in a burst
        SignalFormat: RZ (return to Zero), NRZ (non return to zero)
        trigger: internal, external
        double: second/other channel generates double
        doubleChn: channel which outputs the double pulse
        '''
        
        self.enableDigitalPatternMode()
        self.setTriggerCount(count)
        self.setLevelArm()
        if SignalFormat == "NRZ":
            self.setNonReturnToZeroDataFormat()
        else:
            self.setReturnToZeroDataFormat()
        if trigger.lower() == "external2" or trigger.lower() == "clock-in":
            self.setTriggerSourceExternal2()
        elif  trigger.lower() == "internal2" or  trigger.lower() == "pll":
            self.setTriggerSourceInternal2()   
        else:
            self.setTriggerSourceInternal1()

        if arming.lower() == "manual":
            self.setArmSourceManual()
        else:
            self.setArmSourceExternal()
    
    def turnOffline(self):

        self.inst.close()
        
    def getBinaryList(self, IntIn, binSize=8):
        binIn = bin(IntIn)[2:]
        binOut = [0]*binSize
        inSize = len(binIn)

        for n in range(inSize):
            binOut[n] = int(binIn[inSize-1-n])

        return binOut