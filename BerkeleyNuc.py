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
import queue as qu

import numpy as np
import pyvisa as vs


#Agilen Pulse Generator 81110A: 
class BNC_Model765:

    printOutput = False
    NumOfChannels = 4
    ErrorQueue = qu.Queue()

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
        self.instWrite("*CLS")
        ret = self.instQuery("*IDN?")
        
        if not ret.find("ACTIVE TECHNOLOGIES,AT-PULSE-RIDER-PG1074") == -1:
            self.write("You are using the %s" %(ret[:-2]))
        else:
            #print("You are using the wrong Berkeley Nucleonics!")
            self.inst.close()
            self.ErrorQueue.put("You are using the wrong Berkeley Nucleonics tool! (%s)" %(ret))
            raise SystemError("You are using the wrong Berkeley Nucleonics tool! (%s)" %(ret))
        #print(ret)
        # do if ACTIVE TECHNOLOGIES, AT-PULSE-RIDER PG107 then correct, else the agilent tool you are using is incorrect
        if calibration: 
            self.calibration()
        
        if selfTest:
            self.selfTest()
        
        if Reset:
            self.reset()


    def instWrite(self, command):
        ret = self.inst.write("%s\n" %(command))
        if self.printOutput:
            self.write("Write: %s\n" %(command))
        n = 0
        jobDone = False
        while not jobDone and n < 10:
            try:
                stb = self.inst.query("*STB?")
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
            ret = self.inst.query("SYST:ERR?")
            raise SyntaxError("Model765: %s. Command: %s" %(ret, command))
        return ret


    def instRead(self):
        ret = self.inst.read()
        if self.printOutput:
            self.write("Read")
        return ret
    
    def instQuery(self, command):
        if self.printOutput:
            self.write("Query: %s\n" %(command))
        ret = self.inst.query("%s\n" %(command))
        n = 0
        jobDone = False
        while not jobDone and n < 10:
            try:
                stb = self.inst.query("*STB?")
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
            ret = self.inst.query("SYST:ERR?")
            raise SyntaxError("Model765 encountered error #%s." %(ret))
        return ret

    def reset(self):
        self.instWrite("*CLS")
        self.instWrite("*RST")

    def getModel(self):
        model = "Berkeley Nucleonics - Model 765"
        return model

    def identificatioN(self):
        self.instWrite("*IDN?")

    def performCalibration(self):
        self.calibration()

    def calibration(self):
        self.inst.timeout(240000)
        ret = self.instQuery("*CAL?")
        self.inst.timeout(10000)
        return ret

    def selfTest(self):
        ret = self.instQuery("*TST?")
        return ret

    def turnDisplayOff(self):
            None
    
    def turnDisplayOn(self):
            None

    def write(self, com):
        if self.printOutput:
            print(com)

    '''
    def setExtInputImpedance(self, imp):

        if not isinstance(imp, int):
            raise ValueError("Impedance must be either 50 or 10000 ohm.")
        if not (imp == 50 or imp == 10000): 
            raise ValueError("Impedance must be either 50 or 10000 ohm.")
        if imp == 50:
            self.instWrite(":ARM:IMP 50OHM")
        else:
            self.instWrite(":ARM:IMP 10KOHM")
    '''

    # generates a Trigger event
    def trigger(self):
        self.instWrite("*TRG")

    # clear Trigger
    def clearTrigger(self):
        self.instWrite("TRIG:SEQ:CLEA")

    #Return Trigger status
    def getTriggerStatus(self):
        ret = self.instQuery("TRIG:SEQ:STAT?")
        return ret

    #Query if trigger was missed
    def triggerMissed(self):
        ret = self.instQuery("TRIG:SEQ:MISS?")
        return ret

    #Query Trigger Mode
    def getTriggerMode(self):
        ret = self.instQuery("TRIG:SEQ:MODE")
        return ret 

    #Set Trigger Mode Burst
    def setTriggerModeBurst(self):
        self.instWrite("TRIG:MODE BURS")

    #Set Trigger Mode Single
    def setTriggerModeSingle(self):
        self.instWrite("TRIG:MODE SIN")
        
    #Set Trigger Mode Gated
    def setTriggerModeGated(self):
        self.instWrite("TRIG:MODE GAT")

    #Set Trigger Mode Continuous 
    def setTriggerModeContinuous(self):
        self.instWrite("TRIG:MODE CONT")
        
    #Set Trigger chn
    def setTriggerSourceManual(self):
        self.instWrite("TRIG:SEQ:SOUR MAN")
    def setTriggerSourceTimer(self):
        self.instWrite("TRIG:SEQ:SOUR TIM")
    def setTriggerSourceExternal(self):
        self.instWrite("TRIG:SEQ:SOUR EXT")

    #Query Trigger chn
    def getTriggerSource(self):
        ret = self.instQuery("TRIG:SEQ:SOUR?")
        return ret

    #Set Trigger Slope
    def setTriggerSlopeRising(self):
        self.instWrite("TRIG:SEQ:SLOP RISING")
    def setTriggerSlopeFalling(self):
        self.instWrite("TRIG:SEQ:SLOP FALLING")

    #Query Trigger Slope
    def getTtriggerSlope(self):
        ret = self.instQuery("TRIG:SEQ:SLOP?")
        return ret

    #Set Trigger Threshold
    def setTriggerThreshold(self, threshold):
        
        maxTr = self.getMaxTriggerThreshold()
        minTr = self.getMinTriggerThreshold()

        if not isinstance(threshold, (float,int)):
            raise TypeError("Threshold voltage must a float value from %e to %e V." %(minTr, maxTr))

        if minTr > threshold > maxTr:
            raise TypeError("Threshold voltage must a float value from %e to %e V." %(minTr, maxTr))

        self.instWrite("TRIG:SEQ:THRE %e" %(threshold))

    #Query Trigger Threshold
    def getTriggerThreshold(self):
        ret = self.instQuery("TRIG:SEQ:THRE?")
        ret = float(ret)
        return ret

    #Query Maximum Threshold Voltage
    def getMaxTriggerThreshold(self):
        ret = self.instQuery("TRIG:SEQ:THRE? MAX")
        ret = float(ret)
        return ret
    
    #Query Minimum Threshold Voltage
    def getMinTriggerThreshold(self):
        ret = self.instQuery("TRIG:SEQ:THRE? MIN")
        ret = float(ret)
        return ret

    #Set Trigger AutoSense
    def triggerAutosense(self):
        self.instWrite("TRIG:SEQ:AUTOSENS")

    #Set Trigger Impedance to 50ohm
    def setTriggerImpedanceTo50ohm(self):
        self.instWrite("TRIG:SEQ:IMP 50Ohm")
    #Set Trigger Impedance to 50ohm
    def setTriggerImpedanceTo1Kohm(self):
        self.instWrite("TRIG:SEQ:IMP 1KOhm")

    #Get Trigger Impedance
    def getTriggerImpedance(self):
        ret = self.instQuery("TRIG:SEQ:IMP?")
        return ret

    
    #Set Trigger Timer
    def setTriggerTimer(self, time):

        maxTrigTim = self.getMaxTriggerTimer()
        minTrigTim = self.getMinTriggerTimer()
        if not isinstance(time, (float,int)):
            raise TypeError("Threshold voltage must a float value from 20ns to 50s.")

        if minTrigTim > time or time > maxTrigTim:
            raise TypeError("Threshold voltage must a float value from 20ns to 50s.")

        self.instWrite("TRIG:SEQ:TIM %e" %(time))

    #Query Trigger Timer
    def getTriggerTimer(self):
        ret = self.instQuery("TRIG:SEQ:TIM?")
        ret = float(ret)
        return ret

    #Query Maximum Trigger Timer
    def getMaxTriggerTimer(self):
        ret = self.instQuery("TRIG:SEQ:TIM? MAX")
        ret = float(ret)
        return ret
    
    #Query Minimum Trigger Timer
    def getMinTriggerTimer(self):
        ret = self.instQuery("TRIG:SEQ:TIM? MIN")
        ret = float(ret)
        return ret
    
    #Query Trigger Frequency
    def getTriggerFrequency(self):
        ret = self.instQuery("TRIG:SEQ:FREQ?")
        ret = bool(ret)
        return ret

    #Query Trigger Output Amplitude
    def getTriggerOutputAmplitude(self):
        ret = self.instQuery("TRIG:OUTP:AMPL?")
        ret = float(ret)
        return ret
    
    
    #Query Trigger Output State On/Off
    def getTriggerOutputState(self):
        ret = self.instQuery("TRIG:OUTP:ENABL?")
        ret = int(ret)
        ret = bool(ret)
        return ret

    def enableTriggerOutput(self):
        self.instWrite("TRIG:OUTP:ENABL 1")

    def disableTriggerOutput(self):
        self.instWrite("TRIG:OUTP:ENABL 0")

    #Set Trigger Output Amplitude
    def setTriggerOutputAmplitude(self, amplitude):

        maxAmp = self.getMaxTriggerOutputAmplitude()
        minAmp = self.getMinTriggerOutputAmplitude()

        if not isinstance(amplitude, (float,int)):
            raise TypeError("Threshold Output Amplitude must a float value from %e to %e." %(minAmp, maxAmp))

        if minAmp > amplitude or amplitude > maxAmp:
            raise TypeError("Threshold Output Amplitude must a float value from %e to %e." %(minAmp, maxAmp))


        self.instWrite("TRIG:OUTP:AMPL %e" %(amplitude))
        

    #Query Maximum Trigger Amplitude
    def getMaxTriggerOutputAmplitude(self):
        ret = self.instQuery("TRIG:OUTP:AMPL? MAX")
        ret = float(ret)
        return ret
    
    #Query Minimum Trigger Amplitude
    def getMinTriggerOutputAmplitude(self):
        ret = self.instQuery("TRIG:OUTP:AMPL? MIN")
        ret = float(ret)
        return ret



    #Set Trigger Output Delay
    def setTriggerOutputDelay(self, delay):

        maxDel = self.getMaxTriggerOutputDelay()
        minDel = self.getMinTriggerOutputDelay()

        if not isinstance(delay, (float,int)):
            raise TypeError("Threshold Output Delay must a float value from %e to %e." %(minDel, maxDel))

        if minDel > delay or delay > maxDel:
            raise TypeError("Threshold Output Delay must a float value from %e to %e." %(minDel, maxDel))


        self.instWrite("TRIG:OUTP:DEL %e" %(delay))
        

    #Query Maximum Trigger Delay
    def getMaxTriggerOutputDelay(self):
        ret = self.instQuery("TRIG:OUTP:DEL? MAX")
        ret = float(ret)
        return ret
    
    #Query Minimum Trigger Delay
    def getMinTriggerOutputDelay(self):
        ret = self.instQuery("TRIG:OUTP:DEL? MIN")
        ret = float(ret)
        return ret
    
    def setTriggerOutputSource(self, chn=1):
        
        if not isinstance(chn, int):
            raise TypeError("Trigger chn must be an integer from 1 to 4.")
        if 1 > chn or chn > self.NumOfChannels: 
            raise ValueError("Trigger chn must be an integer from 1 to 4.")

        self.instWrite("TRIG:OUTP:SOUR OUT%d" %(chn))

    def setTriggerOutputPolarityPositive(self):
        self.instWrite("TRIG:OUTP:POL POS")
        
    def setTriggerOutputPolarityNegative(self):
        self.instWrite("TRIG:OUTP:POL NEG")

    def setDisplayChannel(self, channel):
        
        if not isinstance(channel, int):
            raise TypeError("Display Channel must be an integer from 1 to 4.")
        if 1 > channel > 4: 
            raise ValueError("Display Channel must be an integer from 1 to 4.")

        self.instWrite("DISP:CHAN OUT%d" %(channel))
    

    def wait(self):
        self.instWrite("*WAI")

    def getSystemTemperature(self):
        ret = self.instQuery("SYST:TEMP?")
        ret = float(ret)
        return ret
    
    def beep(self):
        self.instWrite("SYST:BEEP:IMM")

    def getSystemBeepState(self):
        ret = self.instQuery("SYST:BEEP:STAT?")
        return ret

    def turnOnSystemBeepState(self):
        self.instQuery("SYST:BEEP:STAT ON")
    
    def turnOffSystemBeepState(self):
        self.instQuery("SYST:BEEP:STAT OFF")

    def getSystemError(self):
        ret = self.instQuery("SYST:ERR:NEXT?")
        return ret

    def turnOnClickSound(self):
        self.instWrite("SYST:KCL:STAT ON")

    def turnOffClickSound(self):
        self.instWrite("SYST:KCL:STAT OFF")

    def getClickSoundState(self):
        ret = self.instQuery("SYST:KCL:STAT?")

        # do some analysis  
        return ret

    def lockInterface(self):
        self.instWrite("SYST:TLOC:STAT ON")

    def unlockInterface(self):
        self.instWrite("SYST:TLOC:STAT OFF")

    def getInterfaceLockState(self):
        ret = self.instQuery("SYST:TLOC:STAT?")

        # do some analysis  
        return ret

    def getSystemLanguage(self):
        ret = self.instQuery("SYST:ULAN?")

        # do some analysis  
        return ret

    def getSystemVersion(self):
        ret = self.instQuery("SYST:VERS?")
        ret = ret.strip()
        return ret

    def getOperationEventRegister(self):
        ret = self.instQuery("SYST:OPER:EVEN?")
        ret = ret.strip()
        return ret

    def getOperationConditionRegister(self):
        ret = self.instQuery("SYST:OPER:COND?")
        ret = ret.strip()
        return ret


    def getOperationEnableRegister(self):
        ret = self.instQuery("SYST:OPER:ENAB?")
        ret = ret.strip()
        return ret
    def setOperationEnableRegister(self, bit):
        if not isinstance(bit, int):
            raise TypeError("bit must be an integer")
        self.instWrite("SYST:OPER:ENAB %d" %(bit))
        
    def getQuestionableEventRegister(self):
        ret = self.instQuery("STAT:QUES:EVEN?")
        ret = ret.strip()
        return ret

    def getQuestionableConditionRegister(self):
        ret = self.instQuery("STAT:QUES:COND?")
        ret = ret.strip()
        return ret
    
    def getQuestionableEnableRegister(self):
        ret = self.instQuery("STAT:QUES:ENAB?")
        ret = ret.strip()
        return ret
    def setQuestionableEnableRegister(self, bit):
        if not isinstance(bit, int):
            raise TypeError("bit must be an integer")
        self.instWrite("STAT:QUES:ENAB %d" %(bit))

    def presetStatusRegister(self):
        self.instWrite("STAT:PRES")

    def clearEventRegister(self):
        self.instWrite("*CLS")

    def getEventStatusRegister(self):
        ret = self.instQuery("*ESE?")
        return ret

    def setEventStatusRegister(self, bit):
        if not isinstance(bit, int):
            raise TypeError("bit must be an integer from 0 to 255")
        if 0 > bit > 255: 
            raise ValueError("bit must be an integer from 0 to 255")
        self.instWrite("*ESE %d" %(bit))

    def getStandardEventStatusRegister(self):
        ret = self.instQuery("*ESR?")
        return ret

    def getServiceRequestEnableRegister(self):
        ret = self.instQuery("*SRE?")
        ret = ret.strip()
        return ret
    def setServiceRequestEnableRegister(self, bit):
        if not isinstance(bit, int):
            raise TypeError("bit must be an integer")
        if 0 > bit > 255: 
            raise ValueError("bit must be an integer from 0 to 255")
        self.instWrite("*SRE %d" %(bit))

    def getStatusByteRegister(self):
        ret = self.instQuery("*STB?")
        ret = ret.strip()
        return ret

    def getDeviceEventStatusEnableRegister(self):
        ret = self.instQuery("DESE?")
        ret = ret.strip()
        return ret
    def setDeviceEventStatusEnableRegister(self,bit):
        if not isinstance(bit, int):
            raise TypeError("bit must be an integer")
        if 0 > bit > 255: 
            raise ValueError("bit must be an integer from 0 to 255")
        self.instWrite("DESE %d" %(bit))

    def getOperationComplete(self):
        ret = self.instQuery("*OPC?")
        ret = ret.strip()
        return ret
    def setOperationComplete(self):
        self.instWrite("*OPC" )

    def arm(self):
        self.instWrite("PULSEGENC:START")

    def dearm(self):
        self.instWrite("PULSEGENC:STOP")

    def start(self):
        self.instWrite("PULSEGENC:START")

    def stop(self):
        self.instWrite("PULSEGENC:STOP")

    def getInstrumentStatus(self):
        ret = self.instQuery("PULSEGENC:STAT?")
        return ret

    def setPulsePeriod(self, period, chn=1):
        
        perMin = self.getMinPeriod(chn)
        perMax = self.getMaxPeriod(chn)
        
        if not isinstance(period, (float,int)):
            raise TypeError("period must be float")
        if perMin > period or period > perMax: 
            raise ValueError("period must be float from %e to %e." %(perMin, perMax))
        if not isinstance(chn, int):
            raise TypeError("channel must be an integer")
        if 1 > chn or chn > self.NumOfChannels: 
            raise ValueError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
        
        self.instWrite("SOUR%d:PER %e" %(chn,period))

    def getMaxPeriod(self, chn=None):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("PER? MAX")
        else:
            ret = self.instQuery("SOUR%d:PER? MAX" %(chn))


        return float(ret)

    def getMinPeriod(self, chn=None):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("PER? MIN")
        else:
            ret = self.instQuery("SOUR%d:PER? MIN" %(chn))
        return float(ret)

    def getMaxWidth(self, chn=None):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("PER? MAX")
        else:
            ret = self.instQuery("SOUR%d:PER? MAX" %(chn))
        return ret

    def getMinWidth(self, chn=None):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("PER? MIN")
        else:
            ret = self.instQuery("SOUR%d:PER? MIN" %(chn))
        return ret

    def setFrequency(self, frequency, chn=1):  
        
        frqMin = self.getMinFrequency(chn)
        frqMax = self.getMaxFrequency(chn)
        
        if not isinstance(frequency, (float,int)):
            raise TypeError("frequency must be float")
        if frqMin > frequency or frequency > frqMax: 
            raise ValueError("frequency must be float from %e to %e." %(frqMin, frqMax))
        if not isinstance(chn, int):
            raise TypeError("channel must be an integer")
        if 1 > chn or chn > self.NumOfChannels: 
            raise ValueError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
        
        self.instWrite("SOUR%d:FREQ %e" %(chn,frequency))

    def getMaxFrequency(self, chn=None):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("FREQ? MAX")
        else:
            ret = self.instQuery("SOUR%d:FREQ? MAX" %(chn))
        return ret

    def getMinFrequency(self, chn=None):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("FREQ? MIN")
        else:
            ret = self.instQuery("SOUR%d:FREQ? MIN" %(chn))
        return ret

    def setCycles(self, cycles, chn=1):  
        
        cycMin = self.getMinNumOfCycles(chn)
        cycMax = self.getMaxNumOfCycles(chn)
        
        if not isinstance(cycles, (int,float)):
            raise TypeError("frequency must be float")
        if cycMin > cycles or cycles > cycMax: 
            raise ValueError("frequency must be float from %e to %e." %(cycMin, cycMax))
        if not isinstance(chn, int):
            raise TypeError("channel must be an integer")
        if 1 > chn or chn > self.NumOfChannels: 
            raise ValueError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
        
        self.instWrite("SOUR%d:BURS:NCYC %e" %(chn,cycles))

    def getMaxNumOfCycles(self, chn=None):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("BURS:NCYC? MAX")
            ret = float(ret)
        else:
            ret = self.instQuery("SOUR%d:BURS:NCYC? MAX" %(chn))
            ret = float(ret)
        return ret

    def getMinNumOfCycles(self, chn=None):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("BURS:NCYC? MIN")
            ret = float(ret)
        else:
            ret = self.instQuery("SOUR%d:BURS:NCYC? MIN" %(chn))
            ret = float(ret)
        return ret

    def setInitDelay(self, delay, chn=1):  
        
        delMin = self.getMinInitDelay(chn)
        delMax = self.getMaxInitDelay(chn)
        
        if not isinstance(delay, (int)):
            raise TypeError("frequency must be float")
        if delMin > delay or delay > delMax: 
            raise ValueError("frequency must be float from %e to %e." %(delMin, delMax))
        if not isinstance(chn, int):
            raise TypeError("channel must be an integer")
        if 1 > chn or chn > self.NumOfChannels: 
            raise ValueError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
        
        self.instWrite("SOUR%d:INITDEL %e" %(chn,delay))

    def getInitDelay(self, chn=None):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("INITDEL?")
        else:
            ret = self.instQuery("SOUR%d:INITDEL?" %(chn))
        return ret

    def getMaxInitDelay(self, chn=None):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("INITDEL? MAX")
        else:
            ret = self.instQuery("SOUR%d:INITDEL? MAX" %(chn))
        return ret

    def getMinInitDelay(self, chn=None):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("INITDEL? MIN")
        else:
            ret = self.instQuery("SOUR%d:INITDEL? MIN" %(chn))
        return ret

    def setLoadImpedance(self, impedance, chn=1):  
        
        impMin = self.getMinLoadImpedance(chn)
        impMax = self.getMaxLoadImpedance(chn)
        
        if not isinstance(impedance, (int)):
            raise TypeError("frequency must be float")
        if impMin > impedance or impedance > impMax: 
            raise ValueError("frequency must be float from %e to %e." %(impMin, impMax))
        if not isinstance(chn, int):
            raise TypeError("channel must be an integer")
        if 1 > chn or chn > self.NumOfChannels: 
            raise ValueError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
        
        self.instWrite("SOUR%d:LOAD:IMP %e" %(chn,impedance))

    def getLoadImpedance(self, chn=None):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("LOAD:IMP?")
        else:
            ret = self.instQuery("SOUR%d:LOAD:IMP?" %(chn))
        return ret

    def getMaxLoadImpedance(self, chn=None):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("LOAD:IMP? MAX")
        else:
            ret = self.instQuery("SOUR%d:LOAD:IMP? MAX" %(chn))
        return ret

    def getMinLoadImpedance(self, chn=None):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("LOAD:IMP? MIN")
        else:
            ret = self.instQuery("SOUR%d:LOAD:IMP? MIN" %(chn))
        return ret

    def turnOnLoadCompensation(self, chn):  
        if not isinstance(chn, int):
            raise TypeError("channel must be an integer")
        if 1 > chn or chn > self.NumOfChannels: 
            raise ValueError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
        
        self.instWrite("SOUR%d:LOAD:COMP ON" %(chn))
    
    def turnOffLoadCompensation(self, chn):  
        if not isinstance(chn, int):
            raise TypeError("channel must be an integer")
        if 1 > chn or chn > self.NumOfChannels: 
            raise ValueError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
        
        self.instWrite("SOUR%d:LOAD:COMP OFF" %(chn))

    def getLoadCompensation(self, chn=None):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("LOAD:COMP?")
        else:
            ret = self.instQuery("SOUR%d:LOAD:IMP?" %(chn))
        return ret

    def invertedOutputPolarity(self, chn=1):  
        if not isinstance(chn, int):
            raise TypeError("channel must be an integer")
        if 1 > chn or chn > self.NumOfChannels: 
            raise ValueError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
        
        self.instWrite("SOUR%d:INV ON" %(chn))
    
    def normalOutputPolarity(self, chn=1):  
        if not isinstance(chn, int):
            raise TypeError("channel must be an integer")
        if 1 > chn or chn > self.NumOfChannels: 
            raise ValueError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
        
        self.instWrite("SOUR%d:INV OFF" %(chn))

    def getOutputPolarity(self, chn=None):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("INV?")
        else:
            ret = self.instQuery("SOUR%d:INV?" %(chn))
        return ret

    def setVoltageAmplitude(self, voltage, chn=1):  
        
        volMin = self.getMinVoltageAmplitude(chn)
        volMax = self.getMaxVoltageAmplitude(chn)
        
        if not isinstance(voltage, (int)):
            raise TypeError("voltage must be float")
        if volMin > voltage or voltage > volMax: 
            raise ValueError("voltage must be float from %e to %e." %(volMin, volMax))
        if not isinstance(chn, int):
            raise TypeError("channel must be an integer")
        if 1 > chn or chn > self.NumOfChannels: 
            raise ValueError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
        
        self.instWrite("SOUR%d:VOLT:LEV:IMM:AMP %e" %(chn,voltage))

    def getVoltageAmplitude(self, chn):
        if not isinstance(chn, int):
            raise TypeError("channel must be an integer")
        if 1 > chn or chn > self.NumOfChannels: 
            raise ValueError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
        ret = self.instQuery("SOUR%d:VOLT:LEV:IMM:AMPL?" %(chn))
        ret = float(ret)
        return ret

    def getMaxVoltageAmplitude(self, chn=None):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("VOLT:LEV:IMM:AMP? MAX")
        else:
            ret = self.instQuery("SOUR%d:VOLT:LEV:IMM:AMP? MAX" %(chn))
        return ret

    def getMinVoltageAmplitude(self, chn=None):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("VOLT:LEV:IMM:AMP? MIN")
        else:
            ret = self.instQuery("SOUR%d:VOLT:LEV:IMM:AMP? MIN" %(chn))
        return ret

    def setVoltageOffset(self, voltage, chn=1):  
        
        volMin = self.getMinVoltageOffset(chn)
        volMax = self.getMaxVoltageOffset(chn)
        
        if not isinstance(voltage, (int)):
            raise TypeError("voltage must be float")
        if volMin > voltage or voltage > volMax: 
            raise ValueError("voltage must be float from %e to %e." %(volMin, volMax))
        if not isinstance(chn, int):
            raise TypeError("channel must be an integer")
        if 1 > chn or chn > self.NumOfChannels: 
            raise ValueError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
        
        self.instWrite("SOUR%d:VOLT:LEV:IMM:OFFS %e" %(chn,voltage))

    def getVoltageOffset(self, chn):
        if not isinstance(chn, int):
            raise TypeError("channel must be an integer")
        if 1 > chn or chn > self.NumOfChannels: 
            raise ValueError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
        ret = self.instQuery("SOUR%d:VOLT:LEV:IMM:OFFS?" %(chn))
        ret = float(ret)
        return ret

    def getMaxVoltageOffset(self, chn=None):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("VOLT:LEV:IMM:OFFS? MAX")
        else:
            ret = self.instQuery("SOUR%d:VOLT:LEV:IMM:OFFS? MAX" %(chn))
        return ret

    def getMinVoltageOffset(self, chn=None):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("VOLT:LEV:IMM:OFFS? MIN")
        else:
            ret = self.instQuery("SOUR%d:VOLT:LEV:IMM:OFFS? MIN" %(chn))
        return ret

    def setVoltageHigh(self, voltage, chn=1):  
        
        volMin = self.getMinVoltageHigh(chn)
        volMax = self.getMaxVoltageHigh(chn)
        
        if not isinstance(voltage, (int, float)):
            raise TypeError("voltage must be float")
        if volMin > voltage or voltage > volMax: 
            raise ValueError("voltage must be float from %e to %e." %(volMin, volMax))
        if not isinstance(chn, int):
            raise TypeError("channel must be an integer")
        if 1 > chn or chn > self.NumOfChannels: 
            raise ValueError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
        
        self.instWrite("SOUR%d:VOLT:LEV:IMM:HIGH %e" %(chn,voltage))

    def getVoltageHigh(self, chn):
        if not isinstance(chn, int):
            raise TypeError("channel must be an integer")
        if 1 > chn or chn > self.NumOfChannels: 
            raise ValueError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
        ret = self.instQuery("SOUR%d:VOLT:LEV:IMM:HIGH?" %(chn))
        ret = float(ret)
        return ret

    def getMaxVoltageHigh(self, chn=None):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("VOLT:LEV:IMM:HIGH? MAX")
        else:
            ret = self.instQuery("SOUR%d:VOLT:LEV:IMM:HIGH? MAX" %(chn))
        try:
            ret = float(ret)
        except TypeError as e: 
            raise TypeError("BNC765 - return error - getMaxVoltageHigh - %s" %(e))
        return float(ret)

    def getMinVoltageHigh(self, chn=None):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("VOLT:LEV:IMM:HIGH? MIN")
        else:
            ret = self.instQuery("SOUR%d:VOLT:LEV:IMM:HIGH? MIN" %(chn))
        try:
            ret = float(ret)
        except TypeError as e: 
            raise TypeError("BNC765 - return error - getMinVoltageHigh - %s" %(e))
        return float(ret)

    def setVoltageLow(self, voltage, chn=1): 

        volMin = self.getMinVoltageLow(chn)
        volMax = self.getMaxVoltageLow(chn)
        
        if not isinstance(voltage, (int, float)):
            raise TypeError("voltage must be float")
        if volMin > voltage or voltage > volMax: 
            raise ValueError("voltage must be float from %e to %e." %(volMin, volMax))
        if not isinstance(chn, int):
            raise TypeError("channel must be an integer")
        if 1 > chn or chn > self.NumOfChannels: 
            raise ValueError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
        
        self.instWrite("SOUR%d:VOLT:LEV:IMM:LOW %e" %(chn,voltage))

    def getVoltageLow(self, chn=1):
        if not isinstance(chn, int):
            raise TypeError("channel must be an integer")
        if 1 > chn or chn > self.NumOfChannels: 
            raise ValueError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
        ret = self.instQuery("SOUR%d:VOLT:LEV:IMM:LOW?" %(chn))
        ret = float(ret)
        return ret

    def getMaxVoltageLow(self, chn=1):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("VOLT:LEV:IMM:LOW? MAX")
        else:
            ret = self.instQuery("SOUR%d:VOLT:LEV:IMM:LOW? MAX" %(chn))
        try:
            ret = float(ret)
        except TypeError as e: 
            raise TypeError("BNC765 - return error - getMaxVoltageLow - %s" %(e))
        return ret

    def getMinVoltageLow(self, chn=1):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("VOLT:LEV:IMM:LOW? MIN")
        else:
            ret = self.instQuery("SOUR%d:VOLT:LEV:IMM:LOW? MIN" %(chn))
        try:
            ret = float(ret)
        except TypeError as e: 
            raise TypeError("BNC765 - return error - getMinVoltageLow - %s" %(e))
        return ret

    def setPulseWidth(self, width, chn=1, pulse=1):  
        
        widthMin = self.getMinPulseWidth(chn)
        widthMax = self.getMaxPulseWidth(chn)

        if pulse != None:
            if not isinstance(chn, int):
                raise TypeError("pulse must be an integer from 1 to 4")
            if 1 > pulse > 4: 
                raise ValueError("pulse must be an integer from 1 to 4")
        if not isinstance(width, (int, float)):
            raise TypeError("width must be float")
        if widthMin > width or width > widthMax: 
            raise ValueError("width must be float from %e to %e." %(widthMin, widthMax))
        if not isinstance(chn, int):
            raise TypeError("channel must be an integer")
        if 1 > chn or chn > self.NumOfChannels: 
            raise ValueError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
        
        self.instWrite("SOUR%d:PULS%d:WIDTH %e" %(chn,pulse,width))


    def getPulseWidth(self, chn=1, pulse=1):
        
        if pulse != None:
            if not isinstance(chn, int):
                raise TypeError("pulse must be an integer from 1 to 4")
            if 1 > pulse > 4: 
                raise ValueError("pulse must be an integer from 1 to 4")
        if not isinstance(chn, int):
            raise TypeError("channel must be an integer")
        if 1 > chn or chn > self.NumOfChannels: 
            raise ValueError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
        ret = self.instQuery("SOUR%d:PULS%d:WIDTH?" %(chn,pulse))
        ret = float(ret)
        return ret

    def getMaxPulseWidth(self, chn=None, pulse=1):
        
        if pulse != None:
            if not isinstance(chn, int):
                raise TypeError("pulse must be an integer from 1 to 4")
            if 1 > pulse > 4: 
                raise ValueError("pulse must be an integer from 1 to 4")
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("PULS%d:WIDTH? MAX" %(pulse))
        else:
            ret = self.instQuery("SOUR%d:PULS%d:WIDTH? MAX" %(chn, pulse))
        try:
            ret = float(ret)
        except TypeError as e: 
            raise TypeError("BNC765 - return error - getMaxPulseWidth - %s" %(e))
        return ret

    def getMinPulseWidth(self, chn=None, pulse=1):
        
        if pulse != None:
            if not isinstance(chn, int):
                raise TypeError("pulse must be an integer from 1 to 4")
            if 1 > pulse > 4: 
                raise ValueError("pulse must be an integer from 1 to 4")
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("PULS%d:WIDT? MIN" %(pulse))
        else:
            ret = self.instQuery("SOUR%d:PULS%d:WIDTH? MIN" %(chn, pulse))
        try:
            ret = float(ret)
        except TypeError as e: 
            raise TypeError("BNC765 - return error - getMinPulseWidth - %s" %(e))
        return ret

    
    def setDelay(self, delay, chn=1, pulse=1):  
        delMin = self.getMinDelay(chn)
        delMax = self.getMaxDelay(chn)
        if pulse != None:
            if not isinstance(chn, int):
                raise TypeError("pulse must be an integer from 1 to 4")
            if 1 > pulse or pulse > 4: 
                raise ValueError("pulse must be an integer from 1 to 4")
        if not isinstance(delay, (int,float)):
            raise TypeError("frequency must be float")
        if delMin > delay or delay > delMax: 
            raise ValueError("frequency must be float from %e to %e." %(delMin, delMax))
        if not isinstance(chn, int):
            raise TypeError("channel must be an integer")
        if 1 > chn or chn > self.NumOfChannels: 
            raise ValueError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
        
        self.instWrite("SOUR%d:PULS%d:DEL %e" %(chn,pulse,delay))

    def getDelay(self, chn=None, pulse=1):
        
        if pulse != None:
            if not isinstance(chn, int):
                raise TypeError("pulse must be an integer from 1 to 4")
            if 1 > pulse > 4: 
                raise ValueError("pulse must be an integer from 1 to 4")
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("PULS%d:DEL?" %(pulse))
        else:
            ret = self.instQuery("SOUR%d:PULS%d:DEL?" %(chn,pulse))
        return ret

    def getMaxDelay(self, chn=None, pulse=1):
        
        if pulse != None:
            if not isinstance(chn, int):
                raise TypeError("pulse must be an integer from 1 to 4")
            if 1 > pulse > 4: 
                raise ValueError("pulse must be an integer from 1 to 4")
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("PULS%d:DEL? MAX" %(pulse))
            ret = float(ret)
        else:
            ret = self.instQuery("SOUR%d:PULS%d:DEL? MAX" %(chn,pulse))
            ret = float(ret)
        return ret

    def getMinDelay(self, chn=None, pulse=1):
        
        if pulse != None:
            if not isinstance(chn, int):
                raise TypeError("pulse must be an integer from 1 to 4")
            if 1 > pulse > 4: 
                raise ValueError("pulse must be an integer from 1 to 4")
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("PULS%d:DEL? MIN" %(pulse))
            ret = float(ret)
        else:
            ret = self.instQuery("SOUR%d:PULS%d:DEL? MIN" %(chn,pulse))
            ret = float(ret)
        return ret

    def setDutyCycle(self, dutyCycle, chn=1, pulse=1):  
        
        cycMin = self.getMinDutyCycle(chn)
        cycMax = self.getMaxDutyCycle(chn)
        
        if pulse != None:
            if not isinstance(chn, int):
                raise TypeError("pulse must be an integer from 1 to 4")
            if 1 > pulse > 4: 
                raise ValueError("pulse must be an integer from 1 to 4")
        if not isinstance(dutyCycle, (int)):
            raise TypeError("frequency must be float")
        if cycMin > dutyCycle or dutyCycle > cycMax: 
            raise ValueError("frequency must be float from %e to %e." %(cycMin, cycMax))
        if not isinstance(chn, int):
            raise TypeError("channel must be an integer")
        if 1 > chn or chn > self.NumOfChannels: 
            raise ValueError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
        
        self.instWrite("SOUR%d:PULS%d:DEL %e" %(chn, pulse, dutyCycle))

    def getDutyCycle(self, chn=None, pulse=1):
        if pulse != None:
            if not isinstance(chn, int):
                raise TypeError("pulse must be an integer from 1 to 4")
            if 1 > pulse > 4: 
                raise ValueError("pulse must be an integer from 1 to 4")
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("PULS%d:DEL?" %(pulse))
        else:
            ret = self.instQuery("SOUR%d:PULS%d:DEL?" %(chn,pulse))
        return ret

    def getMaxDutyCycle(self, chn=None, pulse=1):
        if pulse != None:
            if not isinstance(chn, int):
                raise TypeError("pulse must be an integer from 1 to 4")
            if 1 > pulse > 4: 
                raise ValueError("pulse must be an integer from 1 to 4")
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("PULS%d:DCYC? MAX" %(pulse))
        else:
            ret = self.instQuery("SOUR%d:PULS%d:DCYC? MAX" %(chn,pulse))
        return ret

    def getMinDutyCycle(self, chn=None, pulse=1):
        if pulse != None:
            if not isinstance(chn, int):
                raise TypeError("pulse must be an integer from 1 to 4")
            if 1 > pulse > 4: 
                raise ValueError("pulse must be an integer from 1 to 4")
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("PULS%d:DCYC? MIN" %(pulse))
        else:
            ret = self.instQuery("SOUR%d:PULS%d:DCYC? MIN" %(chn,pulse))
        return ret

    def setPulsePhase(self, phase, chn=1, pulse=1):  
        
        phaMin = self.getMinDutyCycle(chn)
        phaMax = self.getMaxDutyCycle(chn)
        
        if pulse != None:
            if not isinstance(chn, int):
                raise TypeError("pulse must be an integer from 1 to 4")
            if 1 > pulse > 4: 
                raise ValueError("pulse must be an integer from 1 to 4")
        if not isinstance(phase, (int)):
            raise TypeError("Pulse phase must be float")
        if phaMin > phase or phase > phaMax: 
            raise ValueError("Pulse phase must be float from %e to %e." %(phaMin, phaMax))
        if not isinstance(chn, int):
            raise TypeError("channel must be an integer")
        if 1 > chn or chn > self.NumOfChannels: 
            raise ValueError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
        
        self.instWrite("SOUR%d:PULS%d:PHAS %e" %(chn, pulse, phase))

    def getDutyPulsePhase(self, chn=None, pulse=1):
        if pulse != None:
            if not isinstance(chn, int):
                raise TypeError("pulse must be an integer from 1 to 4")
            if 1 > pulse > 4: 
                raise ValueError("pulse must be an integer from 1 to 4")
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
        if chn == None:
            ret = self.instQuery("PULS%d:PHAS?" %(pulse))
        else:
            ret = self.instQuery("SOUR%d:PULS%d:PHAS?" %(chn,pulse))
        return ret

    def getMaxPulsePhase(self, chn=None, pulse=1):
        if pulse != None:
            if not isinstance(chn, int):
                raise TypeError("pulse must be an integer from 1 to 4")
            if 1 > pulse > 4: 
                raise ValueError("pulse must be an integer from 1 to 4")
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to %d" %(self.NumOfChannels))
        if chn == None:
            ret = self.instQuery("PULS%d:PHAS? MAX" %(pulse))
        else:
            ret = self.instQuery("SOUR%d:PULS%d:PHAS? MAX" %(chn,pulse))
        return ret

    def getMinPulsePhase(self, chn=None, pulse=1):
        if pulse != None:
            if not isinstance(chn, int):
                raise TypeError("pulse must be an integer from 1 to 4")
            if 1 > pulse > 4: 
                raise ValueError("pulse must be an integer from 1 to 4")
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer from 1 to 4")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        if chn == None:
            ret = self.instQuery("PULS%d:PHAS? MIN" %(pulse))
        else:
            ret = self.instQuery("SOUR%d:PULS%d:PHAS? MIN" %(chn,pulse))
        return ret

    def setPulseModeSingle(self, chn=1):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        self.instWrite("OUTP%d:PULS:MODE SIN" %(chn))

    def setPulseModeDouble(self, chn=1):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        self.instWrite("OUTP%d:PULS:MODE DOU" %(chn))
    
    def setPulseModeTriple(self, chn=1):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        self.instWrite("OUTP%d:PULS:MODE TRI" %(chn))
    
    def setPulseModeQuad(self, chn=1):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        self.instWrite("OUTP%d:PULS:MODE QUAD" %(chn))

    def setPulseModeExternalWidth(self, chn):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        self.instWrite("OUTP%d:PULS:MODE EXTWID" %(chn))

    def getPulseMode(self, chn=1):        
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        ret = self.instQuery("OUTP%d:PULS:MODE?" %(chn))
        return ret
    #### same as enableOutput
    def turnOnOutput(self, chn=1):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        self.instWrite("OUTP%d:STAT ON" %(chn))
    
    #### same as disableOutput
    def turnOffOutput(self, chn=1):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        self.instWrite("OUTP%d:STAT OFF" %(chn))

    def enableOutput(self, chn=1):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        self.instWrite("OUTP%d:STAT ON" %(chn))

    def disableOutput(self, chn=1):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        self.instWrite("OUTP%d:STAT OFF" %(chn))

    def getOutputState(self, chn=1):
        if chn != None:
            if not isinstance(chn, int):
                raise TypeError("channel must be an integer")
            if 1 > chn or chn > self.NumOfChannels: 
                raise ValueError("channel must be an integer from 1 to 4")
        ret = self.instQuery("OUTP%d:STAT?" %(chn))
        return ret

    def turnOffline(self):

        self.inst.close()


    ########################## additional functions ####################################
    def setPulseVoltage(self, V, chn):

        curVhigh = self.getVoltageHigh(chn)
        curVLow = self.getVoltageLow(chn)


        if V < 0:
            self.setVoltageLow(V, chn)
            self.setVoltageHigh(0, chn)
            self.invertedOutputPolarity(chn)

        if V > 0: 
            self.setVoltageHigh(V, chn)
            self.setVoltageLow(0, chn)
            self.normalOutputPolarity(chn) 