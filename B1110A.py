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
import math as ma

import numpy as np
import pyvisa as vs


#Keysight B1530A WGFMU: 
#The WGFMU (B1530A) instrument Library muss be installed prior to executing this programan
class B1530A:

    printOutput = False

    def __init__(self, rm=None, GPIB_adr=None, Device=None, Reset=True, DisplayOn = False)
    
        if (rm == None or GPIB_adr == None) and Device == None:
            self.write("Either rm and GPIB_adr or a device must be given transmitted")  #maybe a problem, tranmitting None type
        elif Device == None:    

            try:
                self.inst = rm.open_resource(GPIB_adr)
                
                
            except:
                self.write("The device %s does not exist." %(GPIB_adr))  #maybe a problem, tranmitting None type
        
        else:
                self.inst = Device

        self.instWrite("*IDN?\n")
        tm.sleep(0.1)
        ret = self.instRead()
        if ret == "Agilent Technologies,B1500A,0,A.05.04.2013.0328\r\n":
            self.write("You are using the %s" %(ret[:-2]))
        else:
            #print("You are using the wrong agilent tool!")
            exit("You are using the wrong agilent tool!")
        #print(ret)
        # do if Agilent\sTechnologies,E5270A,0,A.01.05\r\n then correct, else the agilent tool you are using is incorrect
        if Reset:
            self.instWrite("*RST")
        if DisplayOn:
            self.instWrite(":DISPlay OFF")

    def performCalibration(self):
        None

    def instWrite(self, command):
        self.inst.write(command)
        if self.printOutput:
            self.write("Write: %s" %(command))
        stb = self.inst.read_stb()
        binStb = self.getBinaryList(stb)
        err = binStb[5]
        if err == 1:
            ret = self.inst.query("ERR? 1\n")
            raise SyntaxError("B1500 encountered error #%d." %(ret))

    def instRead(self):
        ret = self.inst.read()
        if self.printOutput:
            self.write("Read")
        return ret
    
    def instQuery(self, command):
        self.inst.query(command)
        if self.printOutput:
            self.write("Query: %s" %(command))
        stb = self.inst.read_stb()
        binStb = self.getBinaryList(stb)
        err = binStb[5]
        if err == 1:
            ret = self.inst.query("ERR? 1\n")
            raise SyntaxError("B1500 encountered error #%d." %(ret.strip()))
        return ret

    def reset(self):
        self.instWrite("*CLS")
        self.instWrite("*RST")