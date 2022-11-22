"""
Written by: Karsten Beckmann and Maximilian Liehr
Institution: SUNY Polytechnic Institute
Date: 6/12/2018

For more information please use the Keysight E5260 remote control manual.
"""
import numpy as np 
import pyvisa as vs 
import datetime as dt 
import types as tp
import time as tm
from Exceptions import *

#8 slot SMU mainframe: 
#8 Medium Power Source Measurement Units (MPSMUs) are isntalled (model #E5281A)
class Agilent_E5274A:

    inst = None
    SMUActive = [True]*8
    SMUUsed = [False]*8
    execute = True
    session = None
    printOutput = False
    memoryWrite = False
    timeoutTime = 25 #in sec
    waittime = 0.01 # in sec
    label = []
    HSMOutput = []
    MainFrame = 'E5274A'
    Modules = []
    ModuleDesc = []
    ParameterOutput = []
    VoltageName = ['V1','V2','V3','V4','V5','V6','V7','V8']
    CurrentName = ['I1','I2','I3','I4','I5','I6','I7','I8']
    TimeName = ['T1','T2','T3','T4','T5','T6','T7','T8']
    SMUtype = ['MP']*8
    ADC_HS_Mode = 0
    ADC_HR_Mode = 0
    ADC_HS_Coef = 1
    ADC_HR_Coef = 6
    ADC_AutoZero = False
    VR = [0, 5, 50, 20, 200, 400, 1000, 2000, -5, -50, -20, -200, -400, -1000, -2000]
    IR = [0,11,12,13,14,15,16,17,18,19,20,-11,-12,-13,-14,-15,-16,-17,-18,-19,-20]
    VCompDefault = 25
    ICompDefault = 100e-3

    # initiate 
    def __init__(self, rm=None, GPIB_adr=None, Device=None, execute=True, reset=False, SCali=False, SDiag=False):
        
        self.curHeader = []
        if (rm == None or GPIB_adr == None) and Device == None:
            self.write("Either rm and GPIB_adr or a device must be given transmitted")  #maybe a problem, tranmitting None type
        elif Device == None:    

            try:
                self.inst = rm.open_resource(GPIB_adr)
                
            except:
                self.write("The device %s does not exist." %(GPIB_adr))  #maybe a problem, tranmitting None type
        
        else:
                self.inst = Device

        #self.instWrite("LOCAL 7\n")
        #self.instWrite("RL1 *RST\n")
        #self.instWrite("*RST\n")
        #self.instWrite("CL\n")
        self.instWrite("*IDN?\n")
        tm.sleep(0.1)
        ret = self.instRead()
        if ret == "Agilent Technologies,E5270A,0,A.01.05\r\n":
            self.write("You are using the %s" %(ret[:-2]))
        else:
            #print("You are using the wrong agilent tool!")
            exit("You are using the wrong agilent tool!")
        #print(ret)

        # do if Agilent\sTechnologies,E5270A,0,A.01.05\r\n then correct, else the agilent tool you are using is incorrect

        self.execute = execute
        #self.instWrite("*CLS\n") # Clear 
        self.reset # Reset
        tm.sleep(0.1) 
        
        # Run for all 8 SMUs
        if reset:
            for n in range(8):
                self.instWrite("*TST? %d\n" %(n+1))
                stTime = tm.time()
                # While loop reads from the inst until the tool finishes current write function. If the binary response has a 
                # 1 in [4] then the program finished correctly.
                while True:
                    stb = self.inst.read_stb()
                    binStb = self.getBinaryList(stb)
                    if (binStb[4] == 1) or ((tm.time() - stTime) > self.timeoutTime):
                        break
                    tm.sleep(0.5)

                ret = self.instRead()
                
                if int(ret) == 0: 
                    self.SMUActive[n] = True
                    self.write("SMU %d is available." %(n+1))
                else:
                    self.write("SMU %d is not available." %(n+1))
        
        self.instWrite("UNT? \n")
        tm.sleep(0.5)
        ret = self.instRead()
        n = 0

        for ent in ret.split(';'):
            mod = ent.split(',')[0]
            self.Modules.append(mod)
            if mod == "E5281A":
                desc = "MPSMU"
            elif mod == "E5280A":
                desc = "HPSMU"
            self.ModuleDesc.append(desc)
            if not reset:
                self.SMUActive[n] = True
            n = n+1

        # Self Calibration Testing
        if SCali:
            self.write("Running Self Calibration...")
            self.SelfCalibration()
            self.write("Self Calibration finished!")
        
        # Runs Diagnostic Testing
        #if SDiag:
        
        self.instWrite("FMT 1,1\n")
        self.inst.timeout=150000
        self.session = self.inst.session

    def initialize(self):
        self.reset()
    
    def performCalibration(self):
        self.SelfCalibration()

    def calibration(self):
        self.SelfCalibration()

    def getModuleDesc(self):
        return self.ModuleDesc
    
    def getSMUDescriptions(self):
        Desc = dict()
        for smu in range(8):
            Desc[smu] = self.ModuleDesc[smu]
        return Desc

    def getNumberOfSMU(self):
        return sum(self.SMUActive)

    def read_stb(self):
        stb = self.inst.read_stb()
        binStb = self.getBinaryList(stb)
        return binStb

    def instWrite(self, command):

        if self.printOutput:
            self.write("Write: %s" %(command))
        err = self.inst.query("ERR?\n")
        if not err == '0,0,0,0\r\n':
            #self.inst.write("DZ\n")
            self.inst.write("CL\n")
            raise E5274AError("Error code %s" %(err))

        self.inst.write(command)

    def getHeader(self):
        return self.curHeader

    def instRead(self):
        ret = self.inst.read()
        if self.printOutput:
            self.write("Read")
        return ret
    
    def turnOffline(self):
        self.reset()
    
    def instQuery(self, command):
        ret = self.inst.query(command)
        if self.printOutput:
            self.write("Query: %s" %(command))
        stb = self.inst.read_stb()
        binStb = self.getBinaryList(stb)
        err = binStb[5]
        if err == 1:
            ret = self.inst.query("ERR? 1\n")
            raise E5274AError("E5274A encountered error #%d." %(ret))
        return ret

    def setDirectExecute(self):
        self.execute = True
    
    def setRemoteExecute(self):
        self.execute = False
    
    def remoteExecute(self):
        if not self.execute:
            self.instWrite("XE\n")

    def ChangeExecuteState(self, execute):
        self.execute = execute

    def CloseInstrument(self):
        self.inst.close()

    def write(self, txt):
        if self.printOutput:
            print(txt)

    def reset(self):
        self.instWrite("*CLS\n")
        self.instWrite("*RST\n")
        self.ADC_AutoZero = False

    def query(self,txt):
        ret = self.instQuery(txt)
        return ret

    def read(self):
        ret = self.instRead()
        return ret

    def SelfTest(self):
        m = 0 
        for n in range(8):
            self.instWrite("*TST? %d\n" %(n))
            stTime = tm.time()
            # While loop reads from the inst until the tool finishes current write function. If the binary response has a 
            # 1 in [4] then the program finished correctly.
            while True:
                stb = self.inst.read_stb()
                binStb = self.getBinaryList(stb)
                if (binStb[4] == 1) or ((tm.time() - stTime) > self.timeoutTime):
                    break
                tm.sleep(0.5)

            ret = self.instRead()
            
            if int(ret) == 0: 
                self.SMUActive[m] = True
                self.write("SMU %d is available." %(m+1))
            else:
                self.write("SMU %d is not available." %(m+1))
            m+=1

    def SMUisAvailable(self, SMUNum):
        if True == self.SMUActive[SMUNum]:
            return True
        raise E5274A_InputError("SMU %d is not available." %(SMUNum))
        
    def SMUisUsed(self, SMUNum):
        if False == self.SMUUsed[SMUNum]:
            return False
        raise E5274A_InputError("SMU %d is used." %(SMUNum))

    def getBinaryList(self, IntIn, binSize=8):
        
        binIn = bin(IntIn)[2:]
        binOut = [0]*binSize
        inSize = len(binIn)

        for n in range(inSize):
            binOut[n] = int(binIn[inSize-1-n])

        return binOut

    def SelfCalibration(self):
        self.instWrite("*CAL?\n")
        stTime = tm.time()

        # While loop reads from the inst until the tool finishes current write function. If the binary response has a 
        # 1 in [4] then the program finished correctly.
        while True:
            stb = self.inst.read_stb()
            binStb = self.getBinaryList(stb)
                    
            if (binStb[4] == 1) or ((tm.time() - stTime) > self.timeoutTime):
                break

            tm.sleep(0.5)

        ret = self.instRead()
        
        if int(ret) == 0:
            print("Passed, no failure detected.")
            return "Passed, no failure detected."
        stat = []
        self.checkCalibration(ret,8,stat)
        textAr = ["Passed. No failure detected.",
                    "Slot 1 module failed.",
                    "Slot 2 module failed.",
                    "Slot 3 module failed.",
                    "Slot 4 module failed.",
                    "Slot 5 module failed.",
                    "Slot 6 module failed.",
                    "Slot 7 module failed.",
                    "Slot 8 module failed.",
                    "Mainframe failed."]
        output=[]
        for st in stat:
            output.append(textAr[st])
        
        return output

    def checkCalibration(self, ret,n,stat):
        newret = ret-2**n
        if n != 0:
            if newret < 0:
                return self.checkCalibration(ret,n-1,stat)
            else:
                stat.append(n)
                return self.checkCalibration(newret,n-1,stat)

    #check if all entries have the same dimension and through a valueError if not with the description
    def checkListConsistancy(self, List2D, desc):
        for l in List2D[1:]:
            if not l == None:
                if not len(l) == len(List2D[0]):
                    raise E5274A_InputError("Input Values for %s do not have the right dimensions" %(desc))


    #check ranges for 5281A MPSMU if all values in RR are allowed ranges
    def CheckRanges(self, Chns, VorI, Range):
        n=0
        VR = self.VR 
        IR = self.IR
        
        if VorI == "Voltage":
            for element in Range:
                if  element not in VR:
                    raise E5274A_InputError("Voltage Range for Channel %d is not valid." %(Chns[n]))
                n+=1
        elif VorI == "Current":
            for element in Range:
                if element not in IR:
                    raise E5274A_InputError("Current Range for Channel %d is not valid." %(Chns[n]))
                n+=1
        else:
            raise E5274A_InputError("CheckRanges only compares 'Voltage' or 'Current'.")


    #check ranges for 5281A MPSMU if all values in Val are allowed voltages/currents
    def CheckVolCurValues(self, Chns, VorI, Val, RV, RI):
        n=0
        VR = self.VR
        IR = self.IR

        for element in Val:
            if VorI[n]:    
                if RV[n] == VR[0]:
                    if np.absolute(int(element)) > 42:
                        raise E5274A_InputError("Voltage for Voltage range %d in Channel %d is above 42V." %(RV[n], Chns[n]))
                if RV[n] == VR[1] or RV[n] == VR[8]:
                    if np.absolute(int(element)) > 0.5:
                        raise E5274A_InputError("Voltage for Voltage range %d in Channel %d is above 0.5V." %(RV[n], Chns[n]))
                if RV[n] == VR[2] or RV[n] == VR[9]:
                    if np.absolute(int(element)) > 5:
                        raise E5274A_InputError("Voltage for Voltage range %d in Channel %d is above 5V." %(RV[n], Chns[n]))
                if RV[n] == VR[3] or RV[n] == VR[10]:
                    if np.absolute(int(element)) > 2:
                        raise E5274A_InputError("Voltage for Voltage range %d in Channel %d is above 2V." %(RV[n], Chns[n]))
                if RV[n] == VR[4] or RV[n] == VR[11]:
                    if np.absolute(int(element)) > 20:
                        raise E5274A_InputError("Voltage for Voltage range %d in Channel %d is above 20V." %(RV[n], Chns[n]))
                if RV[n] == VR[5] or RV[n] == VR[12]:
                    if np.absolute(int(element)) > 40:
                        raise E5274A_InputError("Voltage for Voltage range %d in Channel %d is above 40V." %(RV[n], Chns[n]))
                if RV[n] == VR[6] or RV[n] == VR[13]:
                    if np.absolute(int(element)) > 100:
                        raise E5274A_InputError("Voltage for Voltage range %d in Channel %d is above 42V." %(RV[n], Chns[n]))
                if RV[n] == VR[7] or RV[n] == VR[14]:
                    if np.absolute(int(element)) > 200:
                        raise E5274A_InputError("Voltage for Voltage range %d in Channel %d is above 42V." %(RV[n], Chns[n]))
            n+=1

        n=0
        for element in Val:
            if VorI[n] == False:
                if RI[n] == IR[0]:
                    if np.absolute(int(element)) > 0.2:
                        raise E5274A_InputError("Current for Current range %d in Channel %d is above 200 mA." %(RI[n], Chns[n]))
                if RI[n] == IR[1] or RI[n] == IR[11]:
                    if np.absolute(int(element)) > 1.15e-9:
                        raise E5274A_InputError("Current for Current range %d in Channel %d is above 1.15 nA." %(RI[n], Chns[n]))
                if RI[n] == IR[2] or RI[n] == IR[12]:
                    if np.absolute(int(element)) > 11.5e-9:
                        raise E5274A_InputError("Current for Current range %d in Channel %d is above 11.5 nA." %(RI[n], Chns[n]))
                if RI[n] == IR[3] or RI[n] == IR[13]:
                    if np.absolute(int(element)) > 115e-9:
                        raise E5274A_InputError("Current for Current range %d in Channel %d is above 115 nA." %(RI[n], Chns[n]))
                if RI[n] == IR[4] or RI[n] == IR[14]:
                    if np.absolute(int(element)) > 1.15e-6:
                        raise E5274A_InputError("Current for Current range %d in Channel %d is above 1.15 uA." %(RI[n], Chns[n]))
                if RI[n] == IR[5] or RI[n] == IR[15]:
                    if np.absolute(int(element)) > 11.5e-6:
                        raise E5274A_InputError("Current for Current range %d in Channel %d is above 11.5 uA." %(RI[n], Chns[n]))
                if RI[n] == IR[6] or RI[n] == IR[16]:
                    if np.absolute(int(element)) > 115e-6:
                        raise E5274A_InputError("Current for Current range %d in Channel %d is above 115 uA." %(RI[n], Chns[n]))
                if RI[n] == IR[7] or RI[n] == IR[17]:
                    if np.absolute(int(element)) > 1.15e-3:
                        raise E5274A_InputError("Current for Current range %d in Channel %d is above 1.15 mA." %(RI[n], Chns[n]))
                if RI[n] == IR[8] or RI[n] == IR[18]:
                    if np.absolute(int(element)) > 11.5e-3:
                        raise E5274A_InputError("Current for Current range %d in Channel %d is above 11.5 mA." %(RI[n], Chns[n]))
                if RI[n] == IR[9] or RI[n] == IR[19]:
                    if np.absolute(int(element)) > 115e-3:
                        raise E5274A_InputError("Current for Current range %d in Channel %d is above 115 mA." %(RI[n], Chns[n]))
                if RI[n] == IR[10] or RI[n] == IR[20]:
                    if np.absolute(int(element)) > 200e-3:
                        raise E5274A_InputError("Current for Current range %d in Channel %d is above 200 mA." %(RI[n], Chns[n]))
            n+=1
        
                
    def CheckCompliance(self, Chns, VorI, Val, IComp, VComp, RV, RI):
        n=0
        VR = self.VR
        IR = self.IR

        #for i in IComp:
        #    if i == 0:
        #        raise E5274A_InputError("Current Compliance can't be 0")
        #for V in VComp:
        #    if V == 0:
        #        raise E5274A_InputError("Voltage Compliance can't be 0")
        
        for element in IComp:
            if element != None:
                if VorI[n] == True:    
                    if RV[n] == VR[0]:
                        if np.absolute(Val[n]) <= 42:
                            if np.absolute(int(element)) > 100e-3:
                                raise E5274A_InputError("Current Compliance for Voltage range %d in Channel %d is not less than or equal to 100e-3 A." %(RV[n], Chns[n]))
                        else:
                            raise E5274A_InputError("Incorrect Current Compliance Used!")
                    if RV[n] == VR[1] or RV[n] == VR[8]:
                        if np.absolute(Val[n]) <= 0.5:
                            if np.absolute(int(element)) > 100e-3:
                                raise E5274A_InputError("Current Compliance for Voltage range %d in Channel %d is not less than or equal to 100e-3 A." %(RV[n], Chns[n]))
                        else:
                            raise E5274A_InputError("Incorrect Current Compliance Used!")
                    if RV[n] == VR[2] or RV[n] == VR[9]:
                        if np.absolute(Val[n]) <= 5:
                            if np.absolute(int(element)) > 100e-3:
                                raise E5274A_InputError("Current Compliance for Voltage range %d in Channel %d is not less than or equal to 100e-3 A." %(RV[n], Chns[n]))
                        else:
                            raise E5274A_InputError("Incorrect Current Compliance Used!")
                    if RV[n] == VR[3] or RV[n] == VR[10]:
                        if np.absolute(Val[n]) <= 2:
                            if np.absolute(int(element)) > 100e-3:
                                raise E5274A_InputError("Current Compliance for Voltage range %d in Channel %d is not less than or equal to 100e-3 A." %(RV[n], Chns[n]))
                        else:
                            raise E5274A_InputError("Incorrect Current Compliance Used!")
                    if RV[n] == VR[4] or RV[n] == VR[11]:
                        if np.absolute(Val[n]) <= 20:
                            if np.absolute(int(element)) > 100e-3:
                                raise E5274A_InputError("Current Compliance for Voltage range %d in Channel %d is not less than or equal to 100e-3 A." %(RV[n], Chns[n]))
                        else:
                            raise E5274A_InputError("Incorrect Current Compliance Used!")
                    if RV[n] == VR[5] or RV[n] == VR[12]:
                        if np.absolute(Val[n]) <= 20:
                            if np.absolute(int(element)) > 100e-3:
                                raise E5274A_InputError("Current Compliance for Voltage range %d in Channel %d is not less than or equal to 100e-3 A." %(RV[n], Chns[n]))
                        if np.absolute(Val[n]) > 20 and np.absolute(Val[n]) <= 40:
                            if np.absolute(int(element)) > 50e-3:
                                raise E5274A_InputError("Current Compliance for Voltage range %d in Channel %d is not less than or equal to 50e-3 A." %(RV[n], Chns[n]))
                        else:
                            raise E5274A_InputError("Incorrect Current Compliance Used!")
                    if RV[n] == VR[6] or RV[n] == VR[13]:
                        if np.absolute(Val[n]) <= 20:
                            if np.absolute(int(element)) > 100e-3:
                                raise E5274A_InputError("Current Compliance for Voltage range %d in Channel %d is not less than or equal to 100e-3 A." %(RV[n], Chns[n]))
                        if np.absolute(Val[n]) > 20 and np.absolute(Val[n]) <= 40:
                            if np.absolute(int(element)) > 50e-3:
                                raise E5274A_InputError("Current Compliance for Voltage range %d in Channel %d is not less than or equal to 50e-3 A." %(RV[n], Chns[n]))
                        if np.absolute(Val[n]) > 40 and np.absolute(Val[n]) <= 100:
                            if np.absolute(int(element)) > 20e-3:
                                raise E5274A_InputError("Current Compliance for Voltage range %d in Channel %d is not less than or equal to 20e-3 A." %(RV[n], Chns[n]))
                        else:
                            raise E5274A_InputError("Incorrect Voltage Compliance Used!")
                    if RV[n] == VR[7] or RV[n] == VR[14]:
                        if np.absolute(Val[n]) < 200:
                            if np.absolute(int(element)) > 100e-3:
                                raise E5274A_InputError("Current Compliance for Voltage range %d in Channel %d is not 2e-3 A." %(RV[n], Chns[n]))
                        else:
                            raise E5274A_InputError("Incorrect Voltage Compliance Used (200V Output range won't work)!")
            n+=1

        n=0

        for element in VComp:
            if element != None:
                if VorI[n] == False:
                    if RI[0] == IR[0]:
                        if np.absolute(Val[n]) <= 0.2:
                            if np.absolute(int(element)) > 100:
                                raise E5274A_InputError("Voltage Compliance for Current range %d in Channel %d is not less than or equal to 100V." %(RI[n], Chns[n]))
                        else:
                            raise E5274A_InputError("Incorrect Current Compliance Used!")
                    if RI == IR[1] or RI == IR[11]:
                        if np.absolute(Val[n]) <= 1.15e-9:
                            if np.absolute(int(element)) > 100:
                                raise E5274A_InputError("Voltage Compliance for Current range %d in Channel %d is not less than or equal to 100V." %(RI[n], Chns[n]))
                        else:
                            raise E5274A_InputError("Incorrect Current Compliance Used!")
                    if RI == IR[2] or RI == IR[12]:
                        if np.absolute(Val[n]) <= 11.5e-9:
                            if np.absolute(int(element)) > 100:
                                raise E5274A_InputError("Voltage Compliance for Current range %d in Channel %d is not less than or equal to 100V." %(RI[n], Chns[n]))
                        else:
                            raise E5274A_InputError("Incorrect Current Compliance Used!")
                    if RI == IR[3] or RI == IR[13]:
                        if np.absolute(Val[n]) <= 115e-9:
                            if np.absolute(int(element)) > 100:
                                raise E5274A_InputError("Voltage Compliance for Current range %d in Channel %d is not less than or equal to 100V." %(RI[n], Chns[n]))
                        else:
                            raise E5274A_InputError("Incorrect Current Compliance Used!")
                    if RI == IR[4] or RI == IR[14]:
                        if np.absolute(Val[n]) <= 1.15e-6:
                            if np.absolute(int(element)) > 100:
                                raise E5274A_InputError("Voltage Compliance for Current range %d in Channel %d is not less than or equal to 100V." %(RI[n], Chns[n]))
                        else:
                            raise E5274A_InputError("Incorrect Current Compliance Used!")
                    if RI == IR[5] or RI == IR[15]:
                        if np.absolute(Val[n]) <= 11.5e-6:
                            if np.absolute(int(element)) > 100:
                                raise E5274A_InputError("Voltage Compliance for Current range %d in Channel %d is not less than or equal to 100V." %(RI[n], Chns[n]))
                        else:
                            raise E5274A_InputError("Incorrect Current Compliance Used!")
                    if RI == IR[6] or RI == IR[16]:
                        if np.absolute(Val[n]) <= 115e-6:
                            if np.absolute(int(element)) > 100:
                                raise E5274A_InputError("Voltage Compliance for Current range %d in Channel %d is not less than or equal to 100V." %(RI[n], Chns[n]))
                        else:
                            raise E5274A_InputError("Incorrect Current Compliance Used!")
                    if RI == IR[7] or RI == IR[17]:
                        if np.absolute(Val[n]) <= 1.15e-3:
                            if np.absolute(int(element)) > 100:
                                raise E5274A_InputError("Voltage Compliance for Current range %d in Channel %d is not less than or equal to 100V." %(RI[n], Chns[n]))
                        else:
                            raise E5274A_InputError("Incorrect Current Compliance Used!")
                    if RI == IR[8] or RI == IR[18]:
                        if np.absolute(Val[n]) <= 11.5e-3:
                            if np.absolute(int(element)) > 100:
                                raise E5274A_InputError("Voltage Compliance for Current range %d in Channel %d is not less than or equal to 100V." %(RI[n], Chns[n]))
                        else:
                            raise E5274A_InputError("Incorrect Current Compliance Used!")
                    if RI == IR[9] or RI == IR[19]:
                        if np.absolute(Val[n]) <= 20e-3:
                            if np.absolute(int(element)) > 100:
                                raise E5274A_InputError("Voltage Compliance for Current range %d in Channel %d is not less than or equal to 100V." %(RI[n], Chns[n]))
                        if np.absolute(Val[n]) <= 50e-3:
                            if np.absolute(int(element)) > 40:
                                raise E5274A_InputError("Voltage Compliance for Current range %d in Channel %d is not less than or equal to 40V." %(RI[n], Chns[n]))
                        if np.absolute(Val[n]) <= 115e-3:
                            if np.absolute(int(element)) > 20:
                                raise E5274A_InputError("Voltage Compliance for Current range %d in Channel %d is not less than or equal to 20V." %(RI[n], Chns[n]))
                        else:
                            raise E5274A_InputError("Incorrect Current Compliance Used!")
                    if RI == IR[10] or RI == IR[20]:
                        if np.absolute(Val[n]) <= 200e-3:
                            if np.absolute(int(element)) != 100000:
                                raise E5274A_InputError("Voltage Compliance for Current range %d in Channel %d is not 100000V." %(RI[n], Chns[n]))
                        else:
                            raise E5274A_InputError("Incorrect Current Compliance Used (Above 100mA Output range won't work)!")

            n=+1


    # check the filter that can be applied to each SMU
    def CheckFilter(self, Chns, VorI, FL):
        n = 0
        if not isinstance(FL, type([])):
            raise E5274A_InputError("The Filter mode must be a list of 0 or 1.")

        for chn in Chns: 
            if not isinstance(FL[n], (int, type(None))):
                raise E5274A_InputError("The Filter mode for Channel %d must be 0, 1 or 'None'." %(Chns[n]))
            
            if not (FL[n] == 0 or FL[n] == 1 or FL[n] == None):
                raise E5274A_InputError("The Filter mode for Channel %d must be 0, 1 or 'None'." %(Chns[n]))
            n+=1

    def CheckChannelMode(self, Chns, CMM):
        n = 0
        for chn in Chns:
            if not isinstance(CMM[n], (int,type(None))):
                raise E5274A_InputError("The Channel mode for Channel %d must be 0, 1, 2, 3 or None." %(Chns[n]))
            if not CMM[n] == None: 
                if not (CMM[n] < 3 or CMM[n] > 0):
                    raise E5274A_InputError("The Channel mode for Channel %d must be 0, 1, 2, 3 or None." %(Chns[n]))
            n+=1

    def CheckSeriesResistance(self, Chns, SSR):

        for n in range(len(Chns)):
            
            if not isinstance(SSR[n], (int, type(None))):
                raise E5274A_InputError("The Series Resistor connection for Channel %d must be 0, 1 or None." %(Chns[n]))
            if not SSR[n] == None: 
                if not (SSR[n] < 3 or SSR[n] > 0):
                    raise E5274A_InputError("The Series Resistor connection for Channel %d must be 0, 1 or None." %(Chns[n]))

    def CheckADCValues(self, chns, ADCs):
        for n in range(len(chns)):
            if not isinstance(ADCs[n], int) and not ADCs[n] == None:
                raise E5274A_InputError("The ADC converter type of Channel %d must be either 0 (High-Speed) or 1 (High-resolution" %(chns[n]))
            if not (ADCs[n] == 0 or ADCs[n] == 1 or ADCs[n] == None):
                raise E5274A_InputError("The ADC converter type of Channel %d must be either 0 (High-Speed) or 1 (High-resolution" %(chns[n]))
            
    #Adjust ADC Converter setting for High-Speed and High-Resolution
    #See E5260 Manual page 206 and command 'AIT' for more details
    def SetADCConverter(self, ADC, mode, N=None):
        if not isinstance(ADC, int):
            raise E5274A_InputError("The ADC converter type must be either 0 (High-Speed) or 1 (High-resolution")
        if not (ADC == 0 or ADC == 1):
            raise E5274A_InputError("The ADC converter type must be either 0 (High-Speed) or 1 (High-resolution")
        if not isinstance(mode, int):
            raise E5274A_InputError("ADC operation mode must be 0 (auto) or 1 (manual) or 2 (PLC mode)")
        if not (mode == 0 or mode == 1 or mode == 2):
            raise E5274A_InputError("ADC operation mode must be 0 (auto) or 1 (manual) or 2 (PLC mode)")
        if not isinstance(N, int):
            raise E5274A_InputError("AV number must be 1 to 1023 or -1 to -100")
        if ADC == 0 and mode == 0:
            if (N > 1023 or N < 1):
                raise E5274A_InputError("(HighSpeed ADC/AutoMode) Number of averaging samples must be between 1 to 1023")
        if ADC == 0 and mode == 1:
            if (N > 1023 or N < 1):
                raise E5274A_InputError("(HighSpeed ADC/ManualMode) Number of averaging samples must be between 1 to 1023")
        if ADC == 0 and mode == 2:
            if (N > 100 or N < 1):
                raise E5274A_InputError("(HighSpeed ADC/PLCmode) Number of averaging samples must be between 1 to 100")
        if ADC == 1 and mode == 0:
            if (N > 127 or N < 1):
                raise E5274A_InputError("(HighResolution ADC/AutoMode) Number of averaging samples must be between 1 to 127 (default=6)")
        if ADC == 1 and mode == 1:
            if (N > 127 or N < 1):
                raise E5274A_InputError("(HighResolution ADC/ManualMode) Number of averaging samples must be between 1 to 127")
        if ADC == 1 and mode == 2:
            if (N > 100 or N < 1):
                raise E5274A_InputError("(HighResolution ADC/PLCmode) Number of averaging samples must be between 1 to 100")

        if ADC == 0: 
            self.ADC_HS_Mode = mode
            self.ADC_HS_Coef = N
        elif ADC == 1:
            self.ADC_HR_Mode = mode
            self.ADC_HR_Coef = N

        if N == None:
            self.instWrite("AIT %d, %d\n" %(ADC, mode))
        else:
            self.instWrite("AIT %d, %d, %d\n"%(ADC, mode, N))
    
    #assign either High-Speed (0) or High-Resolution (1) ADC to a smu
    def SetADC(self, ADC, Chn):
        
        if not isinstance(ADC, int):
            raise E5274A_InputError("The ADC converter type must be either 0 (High-Speed) or 1 (High-resolution")
        if not (ADC == 0 or ADC == 1):
            raise E5274A_InputError("The ADC converter type must be either 0 (High-Speed) or 1 (High-resolution")
        
        if not isinstance(Chn, int):
            raise E5274A_InputError("The Channel number must be an integer between 1 and 8.")
        if 1 > Chn > 8:
            raise E5274A_InputError("The Channel number must be an integer between 1 and 8.")
        
        if ADC != None:
            self.instWrite("AAD %d, %d\n" %(Chn,ADC))
        
    #enable the ADC zero function that is the function to cancel offset of the high-resolution A/D converter
    def EnalbeAutoZero(self):
        self.instWrite("AZ 1\n")
        self.ADC_AutoZero = True

    #disable the ADC zero function that is the function to cancel offset of the high-resolution A/D converter
    def DisableAutoZero(self):
        self.instWrite("AZ 0\n")
        self.ADC_AutoZero = False

    def CheckVMIM(self, VM, IM):
        #check if all values in VM and IM are Boolean
        for element in VM:
            if not isinstance(element, (bool)):
                raise E5274A_InputError("VM must only contain boolean values")
        for element in IM:
            if not isinstance(element, (bool)):
                raise E5274A_InputError("IM must only contain boolean values")
        for n in range(len(VM)):
            if not VM[n] and not IM[n]:
                raise E5274A_InputError("At least one VM or IM must be True")

    def CheckPulseParamSMU(self, hold, width, period, delay):
        if isinstance(hold, (float, int)):
            if hold < 0 or hold > 655.35:
                raise E5274A_InputError("Hold time must be within 0 to 655.35 sec.")
        else:
                raise E5274A_InputError("Hold time must be a float value from 0 to 655.35 sec.")

        if isinstance(width, (float, int)):
            if width < 5e-4 or width >2:
                raise E5274A_InputError("Pulse width must be within 0 to 2 sec.")
        else:
            raise E5274A_InputError("Pulse width must be a float value from 0 to 2 sec.")
        
        if period != None:
            if isinstance(period, (float, int)):
                if not (period == 0 or period == None or (period > 5e-3 and period < 5)):
                    raise E5274A_InputError("Pulse period must be either 0 (automatic setting) or between 0.5ms to 5s.")
            else:
                raise E5274A_InputError("Pulse period must be a float value, either 0 (automatic setting) or between 0.5ms to 5s.")
        
            if width <= 0.1:
                if period < (np.add(width,2e-3)):
                    raise E5274A_InputError("Period must be larger than width+2ms (for width <= 100ms)") 
            elif width > 0.1:
                if period < (np.add(width,10e-3)):
                    raise E5274A_InputError("Period must be larger than width+10ms (for width > 100ms)") 
        
        if period != None and delay != None:
            if isinstance(delay, (float, int)):
                if not (delay == None or (delay >=0 and delay<=width)):
                    raise E5274A_InputError("Delay must be larger than 0 and smaller than the pulse width")
    
    def CheckSweepParamV(self, hold, delay, sdelay, tdelay, mdelay, AA, AApost, SChn, Sstart, Sstop, MChn, MVstart, MVstop, MVstep, Mmode):
        if isinstance(hold, (float,int)):
            if hold < 0 or hold > 655.35:
                raise E5274A_InputError("Hold time must be a within 0 to 655.35 sec.")
        else:
            raise E5274A_InputError("Hold time must be a float value from 0 to 655.35 sec.")
       
        if isinstance(delay, (float,int)):
            if delay < 0 or delay > 65.35:
                raise E5274A_InputError("Delay time must be within 0 to 65.35 sec.")
        else:
            raise E5274A_InputError("Delay time must be a float value from 0 to 65.35 sec.")

        if isinstance(sdelay, (float,int)):
            if sdelay < 0 or sdelay > 1:
                raise E5274A_InputError("Sdelay time must be within 0 to 1 sec.")
        elif sdelay == None:
            None
        else:
            raise E5274A_InputError("Sdelay time must be within a float value of 0 to 1 sec.")

        if isinstance(tdelay,(float,int)):
            if tdelay < 0 or tdelay > delay:
                raise E5274A_InputError("Tdelay time must be within 0 to delay.")
        elif tdelay == None:
            None
        else:
            raise E5274A_InputError("Tdelay time must be a float value from 0 to delay.")

        if isinstance(mdelay, (float,int)):
            if mdelay < 0 or mdelay > 65.535:
                raise E5274A_InputError("Mdelay time must be within 0 to 65.535 sec.")
        elif mdelay == None:
            None
        else:
            raise E5274A_InputError("Mdelay time must be an integer from 0 to 65.535 sec.")
        
        if isinstance(AA, int):
            if not AA == 1 and not AA == 2 and not AA == None: 
                raise E5274A_InputError("AA must be 1, 2, or None.")
            if not AApost == 1 and not AApost == 2 and not AApost == None:
                raise E5274A_InputError("AApost must be 1, 2, or None.")
        elif AA == None:
            None
        else:
            raise E5274A_InputError("AA and AApost must be an integer of 1 or 2.")

        if not SChn == None:
            if (Sstart == None or Sstop == None):
                raise E5274A_InputError("If a synchronous sweep source is set, Sstart and Sstop must be set as well.")
        if isinstance(Mmode, int):
            if Mmode > 4 or Mmode < 1:
                raise E5274A_InputError("The sweep mode of the staircase must be 1 (linear/single), 2 (log/single), 3 (linear/double) or 4 (log/double).")
        elif Mmode == None: 
            None
        else:
            raise E5274A_InputError("The sweep mode of the staircase must be an integer of the following values: 1 (linear/single), 2 (log/single), 3 (linear/double) or 4 (log/double).")
        
        if MVstart > np.absolute(42) or MVstop > np.absolute(42):
            raise E5274A_InputError("Start and Stop voltages cannot exceed 42V")
        if not Sstart == None:
            if Sstart > np.absolute(42) or Sstop > np.absolute(42):
                raise E5274A_InputError("Start and Stop voltages cannot exceed 42V")
        if Mmode == 2 or Mmode == 4: 
            if MVstart > 0 and MVstop < 0:
                raise E5274A_InputError("Start and Stop voltages must be the same polarity in log sweep mode.")
            if Sstart > 0 and Sstop < 0:
                raise E5274A_InputError("Start and Stop voltages must be the same polarity in log sweep mode.")
        
        if isinstance(MVstep, int):
            if MVstep < 1 or MVstep > 1001:
                raise E5274A_InputError("the Step number must be an integer between 1 and 1001.")
        else: 
            raise E5274A_InputError("the Step number must be an integer between 1 and 1001.")

    def CheckSweepParamI(self, hold, delay, sdelay, tdelay, mdelay, AA, AApost, SChn, Sstart, Sstop, MChn, MIstart, MIstop, MIstep, Mmode):
        if isinstance(hold, (float,int)):
            if hold < 0 or hold > 655.35:
                raise E5274A_InputError("Hold time must be a within 0 to 655.35 sec.")
        else:
            raise E5274A_InputError("Hold time must be a float value from 0 to 655.35 sec.")
       
        if isinstance(delay, (float,int)):
            if delay < 0 or delay > 65.35:
                raise E5274A_InputError("Delay time must be within 0 to 65.35 sec.")
        else:
            raise E5274A_InputError("Delay time must be a float value from 0 to 65.35 sec.")

        if isinstance(sdelay, (float,int)):
            if sdelay < 0 or sdelay > 1:
                raise E5274A_InputError("Sdelay time must be within 0 to 1 sec.")
        elif sdelay == None:
            None
        else:
            raise E5274A_InputError("Sdelay time must be within a float value of 0 to 1 sec.")

        if isinstance(tdelay,(float,int)):
            if tdelay < 0 or tdelay > delay:
                raise E5274A_InputError("Tdelay time must be within 0 to delay.")
        elif tdelay == None:
            None
        else:
            raise E5274A_InputError("Tdelay time must be a float value from 0 to delay.")

        if isinstance(mdelay, (float,int)):
            if mdelay < 0 or mdelay > 65.535:
                raise E5274A_InputError("Mdelay time must be within 0 to 65.535 sec.")
        elif mdelay == None:
            None
        else:
            raise E5274A_InputError("Mdelay time must be an integer from 0 to 65.535 sec.")
        
        if isinstance(AA, int):
            if not AA == 1 and not AA == 2 and not AA == None: 
                raise E5274A_InputError("AA must be 1, 2, or None.")
            if not AApost == 1 and not AApost == 2 and not AApost == None:
                raise E5274A_InputError("AApost must be 1, 2, or None.")
        elif AA == None:
            None
        else:
            raise E5274A_InputError("AA and AApost must be an integer of 1 or 2.")

        if not SChn == None:
            if (Sstart == None or Sstop == None):
                raise E5274A_InputError("If a synchronous sweep source is set, Sstart and Sstop must be set as well.")
        if isinstance(Mmode, int):
            if Mmode > 4 or Mmode < 1:
                raise E5274A_InputError("The sweep mode of the staircase must be 1 (linear/single), 2 (log/single), 3 (linear/double) or 4 (log/double).")
        elif Mmode == None: 
            None
        else:
            raise E5274A_InputError("The sweep mode of the staircase must be an integer of the following values: 1 (linear/single), 2 (log/single), 3 (linear/double) or 4 (log/double).")
        
        if MIstart > np.absolute(42) or MIstop > np.absolute(42):
            raise E5274A_InputError("Start and Stop voltages cannot exceed 42V")
        if not Sstart == None:
            if Sstart > np.absolute(42) or Sstop > np.absolute(42):
                raise E5274A_InputError("Start and Stop voltages cannot exceed 42V")
        if Mmode == 2 or Mmode == 4: 
            if MIstart > 0 and MIstop < 0:
                raise E5274A_InputError("Start and Stop voltages must be the same polarity in log sweep mode.")
            if Sstart > 0 and Sstop < 0:
                raise E5274A_InputError("Start and Stop voltages must be the same polarity in log sweep mode.")
        
        if isinstance(MIstep, int):
            if MIstep < 1 or MIstep > 1001:
                raise E5274A_InputError("the Step number must be an integer between 1 and 1001.")
        else: 
            raise E5274A_InputError("the Step number must be an integer between 1 and 1001.")
       
    def checkComplPolarity(self, Chns,complPolarity):
        for n in range(len(Chns)): 
            if not complPolarity[n] == None: 
                if not (complPolarity[n] < 3 or complPolarity[n] > 0):
                    raise E5274A_InputError("The Compliance Polarity of connection for Channel %d must be 0, 1 or None." %(Chns[n]))
 

    #creates the DV command string
    def compileDV(self, chnum, vrange, voltage ,Icomp=None,comp_polarity=None, irange=None):
        ret = "DV %d, %d, %f" %(chnum, vrange, voltage)
        if not Icomp == None: 
            ret = "%s, %f" %(ret,Icomp)
            if not comp_polarity == None: 
                ret = "%s, %d" %(ret,comp_polarity)
                if not irange == None: 
                    ret = "%s, %d" %(ret,irange)
        return ret

    #creates the DI command string
    def compileDI(self, chnum, irange, current ,Vcomp=None,comp_polarity=None, vrange=None):
        ret = "DI %d, %d, %f" %(chnum, irange, current)
        if not Vcomp == None: 
            ret = "%s, %f" %(ret,Vcomp)
            if not comp_polarity == None: 
                ret = "%s, %d" %(ret,comp_polarity)
                if not vrange == None: 
                    ret = "%s, %d" %(ret, vrange)
        return ret

    #creates the PT command string
    def compilePT(self, hold, width, period=None, Tdelay=None):
        ret = "PT %f, %f" %(hold, width)
        if not period == None: 
            ret = "%s, %f" %(ret,period)
            if not Tdelay == None: 
                ret = "%s, %f" %(ret,Tdelay)
        ret = "%s\n" %(ret)
        return ret
        
    #creates the WV command string
    def compileWV(self, chnum,mode,Range,start,stop,step,Icomp=None,Pcomp=None):
        ret = "WV %d, %d, %d, %f, %f, %d" %(chnum, mode, Range, start, stop, step)
        if not Icomp == None: 
            ret = "%s, %f" %(ret,Icomp)
            if not Pcomp == None: 
                ret = "%s, %f" %(ret,Pcomp)
        ret = "%s\n" %(ret)
        return ret

    #creates the WI command string
    def compileWI(self, chnum,mode,Range,start,stop,step,Vcomp=None,Pcomp=None):
        ret = "WI %d, %d, %d, %f, %f, %d" %(chnum, mode, Range, start, stop, step)
        if not Vcomp == None: 
            ret = "%s, %f" %(ret,Vcomp)
            if not Pcomp == None: 
                ret = "%s, %f" %(ret,Pcomp)
        ret = "%s\n" %(ret)
        return ret

    # Creates the WNX command string
    def compileWNX(self, L, chnum, mode, Range, start, stop, step, Comp=None, Pcompl=None):
        ret = "WNX %d, %d, %d, %d, %f, %f, %d" %(L, chnum, mode, Range, start, stop, step)
        if not Comp == None: 
            ret = "%s, %f" %(ret,Comp)
            if not Pcompl == None: 
                ret = "%s, %f" %(ret,Pcompl)
        ret = "%s\n" %(ret)
        return ret

    #creates the AV command string
    def compileAV(self, number,mode=None):
        ret = "AV %d" %(number)
        if not mode == None: 
            ret = "%s, %d" %(ret,mode)
        ret = "%s\n" %(ret)
        return ret

    #creates the AV command string
    def compile(self, number,mode=None):
        ret = "AV %d" %(number)
        if not mode == None: 
            ret = "%s, %d" %(ret,mode)
        ret = "%s\n" %(ret)
        return ret

    #creates the WSI command string
    def compileWSI(self, chnum,Range,start,stop,Vcomp,Pcomp=None):
        ret = "WSI %d, %d, %f, %f" %(chnum, Range, start, stop)
        if not Vcomp == None: 
            ret = "%s, %f" %(ret,Vcomp)
            if not Pcomp == None: 
                ret = "%s, %f" %(ret,Pcomp)
        ret = "%s\n" %(ret)
        return ret

    #creates the WSV command string
    def compileWSV(self, chnum, Range,start,stop,Icomp,Pcomp=None):
        ret = "WSV %d, %d, %f, %f" %(chnum, Range, start, stop)
        if not Icomp == None: 
            ret = "%s, %f" %(ret,Icomp)
            if not Pcomp == None: 
                ret = "%s, %f" %(ret,Pcomp)
        ret = "%s\n" %(ret)
        return ret

    #the output data from the tool can be various formats depending on the FMT command
    def getOutputData(self, chns, data, format, output):
        Coding = {'A':1,'B':2,'C':3,'D':4,'E':5,'F':6,'G':7,'H':8}
        data = data[:-2].split(',')
        label = []
        if format == "FMT1" or format == "FMT5":      #data format ABCDDDDDDDDDDDD
            check = []
            check.append(data[0][1:3])
            output.append([])
            label.append("%s%d"%(data[0][2:3],Coding[data[0][1:2]]))
            #for n in range(1,len(data)-2,1):
            for n in range(1,len(data),1):
                if data[n][1:3] in check:
                    break
                else:
                    check.append(data[n][1:3])
                    output.append([])
                    label.append("%s%d"%(data[n][2:3],Coding[data[n][1:2]]))
            l = len(output)
            m=0
            for n in range(len(data)):
                output[m].append(float(data[n][3:]))
                m+=1
                if m == l:
                    m = 0
            
            #return label
            return {'Label': label, 'Output': output}

    def getHeader_1(self, Chns, Val, VorI, SSR, FL, MChn=None, SChn=None, SMChn=None, Index=None, Time=None):
        TestPara = ['TestParameter']*12
        TestPara[0] = '%s,MainFrame' %(TestPara[0])
        TestPara[1] = '%s,Channel.Type' %(TestPara[1])
        TestPara[2] = '%s,Channel.Unit' %(TestPara[2])
        TestPara[3] = '%s,Channel.IName' %(TestPara[3])
        TestPara[4] = '%s,Channel.VName' %(TestPara[4])
        TestPara[5] = '%s,Channel.Mode' %(TestPara[5])
        TestPara[6] = '%s,Channel.Func' %(TestPara[6])
        TestPara[7] = '%s,Channel.Value' %(TestPara[7])
        TestPara[8] = '%s,Channel.Index' %(TestPara[8])
        TestPara[9] = '%s,Channel.Time' %(TestPara[9])
        TestPara[10] = '%s,Measurement.Port.SeriesResistance' %(TestPara[10])
        TestPara[11] = '%s,Measurement.Port.Filter' %(TestPara[11])

        for n in range(len(Chns)):
            TestPara[1] = '%s,SMU' %(TestPara[1])
            TestPara[2] = '%s,SMU%d:%s' %(TestPara[2],Chns[n],self.SMUtype[Chns[n]-1])
            TestPara[3] = '%s,%s' %(TestPara[3],self.CurrentName[n])
            TestPara[4] = '%s,%s' %(TestPara[4],self.VoltageName[n])
            if VorI:
                TestPara[5] = '%s,V' %(TestPara[5])
            else:
                TestPara[5] = '%s,I' %(TestPara[5])
            if MChn == Chns[n]:
                TestPara[6] = '%s,VAR1' %(TestPara[6])
            elif SChn == Chns[n]:
                TestPara[6] = '%s,VAR1\'' %(TestPara[6])
            elif SMChn == Chns[n]:
                TestPara[6] = '%s,VAR2' %(TestPara[6])
            else:
                TestPara[6] = '%s,CONST' %(TestPara[6])
            
            if MChn == Chns[n] or SChn == Chns[n] or SMChn == Chns[n]:
                TestPara[7] = '%s,-' %(TestPara[7])
            else:
                TestPara[7] = '%s, %f' %(TestPara[7], Val[n])

            if Index == None:
                TestPara[8] = '%s,' %(TestPara[8])
            else:
                TestPara[8] = '%s,%d' %(TestPara[8],Index[n])
            if Time == None:    
                TestPara[9] = '%s,' %(TestPara[9])
            else:
                TestPara[9] = '%s,%f' %(TestPara[9],Time[n])
            if FL == 1:
                TestPara[10] = '%s,OFF' %(TestPara[10])
            else:
                TestPara[10] = '%s,ON' %(TestPara[10])
            TestPara[11] = '%s,0' %(TestPara[11])

        return TestPara

    def CheckPulsePVPIParam(self, Chns, Pbase, Ppulse, VComp, IComp, VorI, PChn):
        n=0
        for element in Chns:
            if Chns[n] == PChn:
                if VorI[n]:
                    if np.absolute(Ppulse) > np.absolute(VComp[n]):
                        raise E5274A_InputError("Pbase must be lower than Compliance value (Voltage)")
                    if np.absolute(Pbase) > np.absolute(Ppulse):
                        raise E5274A_InputError("Pbase must be lower than Ppulse value (Current)")

                if VorI == False:
                    if np.absolute(Ppulse) > np.absolute(IComp[n]):
                        raise E5274A_InputError("Ppulse must be lower than Compliance value (Voltage)")
                    if np.absolute(Pbase) > np.absolute(Ppulse):
                        raise E5274A_InputError("Pbase must be lower than Ppulse value (Current)")

            n+=1

    def CheckPulseSweepParam(self, Chns, VPbase, VPpulse, VPulseStop, IPbase, IPpulse, 
                            IPulseStop, PStep, VComp, IComp, VorI, PChn):
        
        if not isinstance(PStep, (int)):
            raise E5274A_InputError("PStep must only contain integer values")
        if PStep < 1 or PStep > 1001:
            raise E5274A_InputError("PStep must be between 1 and 1001")

        n=0
        for element in Chns:
            if Chns[n] == PChn:
                if VorI[n]:
                    if np.absolute(VPpulse) > np.absolute(VComp[n]):
                        raise E5274A_InputError("Pbase must be lower than Compliance value")
                    if np.absolute(VPpulse) > np.absolute(VPulseStop):
                        raise E5274A_InputError("Ppulse must be lower than PulseStop value")    
                    if np.absolute(VPbase) > np.absolute(VPpulse):
                        raise E5274A_InputError("Pbase must be lower than Ppulse value")

                if VorI == False:
                    if np.absolute(IPpulse) > np.absolute(IComp[n]):
                        raise E5274A_InputError("Ppulse must be lower than Compliance value")
                    if np.absolute(IPpulse) > np.absolute(IPulseStop):
                        raise E5274A_InputError("Ppulse must be lower than PulseStop value")  
                    if np.absolute(IPbase) > np.absolute(IPpulse):
                        raise E5274A_InputError("Pbase must be lower than Ppulse value")

            n+=1

    def checkBDMValues(self, BDMInterval, BDMmode):
        n = 0
        if not ( BDMInterval == 0 or BDMInterval == 1 ):
             raise E5274A_InputError("BDMInterval must be either 0 or 1")
        if not ( BDMmode == 0 or BDMmode == 1 or BDMInterval == None):
             raise E5274A_InputError("BDMmode must be either 0 or 1")

    def CheckBDTValues(self, hold, delay):
        if isinstance(hold, float):
            if hold < 0 or hold > 655.35:
                raise E5274A_InputError("Hold time must be within 0 to 655.35 sec.")
        else:
                raise E5274A_InputError("Hold time must be a float value from 0 to 655.35 sec.")

        if isinstance(delay, float):
            if hold < 0 or hold > 6.5535:
                raise E5274A_InputError("Delay time must be within 0 to 6.5535 sec.")
        else:
                raise E5274A_InputError("Delay time must be a float value from 0 to 6.5535 sec.")

    def CheckBDVValues(self, BDVstart, BDVstop):
        if not abs(BDVstart - BDVstop) > 10:
            raise E5274A_InputError("Absolute value of BDVstart - BDVstop must be greater than 10V.")

            

    
    ############################################################################################
    # can receive Values for a spot measurement if the Channels passed calibration and are installed
    # Chns: Array with Channel Number
    # Val:  Array containing voltage/current values
    # VorI: Array if I or V are forced contains Binary True for V, False for I
    # RV:   Array of ranges for voltage measurement
    # RI:   Array of ranges for current measurement
    # IComp: Array for the set Compliance Current
    # VComp: Array for the set Compliance Voltage
    # FL:   Sets the filter of the specified channels to ON or OFF.
    # SSR:  Series resistance will be applied
    # AVnum:    This command sets the number of averaging samples of the ADC (A/D converter).
    # AVmode:   This command sets the mode of averaging samples of the ADC (A/D converter).
    # CMM:  The CMM command sets the SMU measurement operation mode.
    
    def SpotMeasurement(self, Chns, VorI, Val, VComp=None, IComp=None, RV=None, 
                        RI=None, FL=None, SSR=None, ADC=None , CMM=None, complPolarity=None):
                        
        if RV == None: RV = [0]*len(Chns)           # auto voltage range for all active channels
        if RI == None: RI = [0]*len(Chns)           # auto current range for all active channels
        if VComp == None: VComp = [self.VCompDefault]*len(Chns)     # auto compliance for all active Voltage channels
        if IComp == None: IComp = [self.ICompDefault]*len(Chns)     # auto compliance for all active Current channels
        if FL == None: FL = [None]*len(Chns)        # don't set the filter for all active channels
        if SSR == None: SSR = [None]*len(Chns)      # don't set the series resistance for all active channels
        if CMM == None: CMM = [None]*len(Chns)      # don't set the channel mode for all active channels
        if complPolarity == None: complPolarity = [0]*len(Chns)     # auto compliance polarity for all active channels
        
        self.checkListConsistancy([Chns, VorI, Val, VComp, IComp, RV, RI, FL, SSR, CMM], "Spot Measurement")

        if ADC == None: ADC = [0]*len(Chns)    

        for chn in Chns:
            self.SMUisAvailable(chn)
            self.SMUisUsed(chn)
        
        #check if all values in VorI are Boolean
        for element in VorI:
            if not isinstance(element, (bool)):
                raise E5274A_InputError("VorI must only contain boolean values")

        # Checks base variables
        self.CheckADCValues(Chns, ADC)
        self.CheckRanges(Chns, "Voltage", RV)
        self.CheckRanges(Chns, "Current", RI)
        self.CheckVolCurValues(Chns, VorI, Val, RV, RI)
        self.CheckCompliance(Chns, VorI, Val, IComp, VComp, RV, RI)
        self.CheckFilter(Chns, VorI, FL)
        self.CheckSeriesResistance(Chns, SSR)
        self.CheckChannelMode(Chns, CMM)
        
        # Reset all channels to 0V
        # 
        # self.instWrite("DZ\n")
        # Clears all the channels
        self.instWrite("CL\n")

        # Sets integration time
        n=0
        for chn in Chns:
            if ADC[n] != None:
                self.instWrite("AAD %d, %d\n" %(chn,ADC[n]))
            n+=1
        n=0

        # Set mode value to blank string to be change later when calling MM
        mode = ""

        for n in range(len(Chns)):
            self.instWrite("CN %d\n" %(Chns[n]))
            if not FL[n] == None:
                self.instWrite("FL %d, %d\n" %(FL[n], Chns[n]))

            if not SSR[n] == None:
                self.instWrite("SSR %d, %d\n" %(SSR[n], Chns[n]))

            if VorI[n]:  
                self.instWrite(self.compileDV(Chns[n], RV[n], Val[n], IComp[n], complPolarity[n], RI[n]))
            else:
                self.instWrite(self.compileDI(Chns[n], RI[n], Val[n], VComp[n], complPolarity[n], RV[n]))

            if VorI[n]:
                if RI[n] != None:
                    self.instWrite("RI %d, %d\n" %(Chns[n], RI[n]))
            else: 
                if RV[n] != None:
                    self.instWrite("RV %d, %d\n" %(Chns[n], RV[n]))

            if not CMM[n] == None:
                self.instWrite("CMM %d, %d\n" %(Chns[n], CMM[n]))
            
            mode = "%s, %d" %(mode, Chns[n])

        self.instWrite("MM 1%s" %(mode))
        self.instWrite("FMT 1, 1 \n")
        #self.instWrite("TSR\n")
        retAr = []
        if self.execute:
            self.instWrite("XE\n")

            stTime = tm.time()
            while True:
                stb = self.inst.read_stb()
                binStb = self.getBinaryList(stb)
                if ((tm.time() - stTime) > self.timeoutTime):
                    timeOut = True
                    break
                if(binStb[0] ==1):
                    ret = self.instRead()
                    self.label = self.getOutputData(Chns,ret,'FMT1',retAr)
                    break

                tm.sleep(self.waittime)

            #self.instWrite("TSQ\n")
            #self.inst.wait_for_srq()
            #print(self.inst.query_ascii_values("trace:data?"))
            #self.instWrite("DZ\n") 
            #return True

        ########CreateHeader
        Header = self.getHeader_1(Chns,Val, VorI, SSR, FL, MChn=None, SChn=None)
        ADCHeader = self.getADCHeader()
        Header.extend(ADCHeader)

        #self.instWrite("DZ\n")
        self.instWrite("CL\n")
        self.curHeader = Header
        return {'Data': retAr, 'Header': Header}

    ############################################################################################
    # Can receive Values for a high-speed spot measurement if the Channels passed calibration and are installed
    # Chns: Array with Channel Number
    # Val:  Array containing voltage/current values
    # VorI: Array if I or V are forced contains Binary True for V, False for I
    # RV:   Array of ranges for voltage measurement
    # RI:   Array of ranges for current measurement
    # VComp: Array for the set Compliance Voltage
    # IComp: Array for the set Compliance Current
    # FL:   Sets the filter of the specified channels to ON or OFF.
    # SSR:  Series resistance will be applied
    # AVnum:    This command sets the number of averaging samples of the ADC (A/D converter).
    # AVmode:   This command sets the mode of averaging samples of the ADC (A/D converter).
    # VM: Boolean Array of direct Voltage Measurement
    # IM: Boolean Array of direct Current Measurement

    def HighSpeedSpotMeasurement(self, Chns, VorI, Val, VComp=None, 
                                IComp=None, RV=None, RI=None, FL=None, SSR=None, 
                                AVnum=1, AVmode=0, complPolarity=None):
        
        #if self.execute:
        #    raise SystemError("High-Speed Spot Measurement is incompatible with other measurement types, please change the excecute state.")

        self.checkListConsistancy([Chns, VorI, Val, VM, IM, VComp, IComp, RV, RI, FL, SSR], "High-Speed Spot Measurement")
        if RV == None: RV = [0]*len(Chns)           # auto voltage range for all active channels
        if RI == None: RI = [0]*len(Chns)           # auto current range for all active channels
        if VComp == None: VComp = [self.VCompDefault]*len(Chns)     # auto compliance for all active Voltage channels
        if IComp == None: IComp = [self.ICompDefault]*len(Chns)     # auto compliance for all active Current channels
        if FL == None: FL = [None]*len(Chns)        # don't set the filter for all active channels
        if SSR == None: SSR = [None]*len(Chns)      # don't set the series resistance for all active channels
        if complPolarity == None: complPolarity = [0]*len(Chns)     # auto compliance polarity for all active channels
        
        for chn in Chns:
            self.SMUisAvailable(chn)
            self.SMUisUsed(chn)
        
        #check if all values in VorI are Boolean
        for element in VorI:
            if not isinstance(element, (bool)):
                raise E5274A_InputError("VorI must only contain boolean values")

        self.CheckRanges(Chns, "Voltage", RV)
        self.CheckRanges(Chns, "Current", RI)
        self.CheckVolCurValues(Chns, VorI, Val, RV, RI)
        self.CheckCompliance(Chns, VorI, Val, IComp, VComp, RV, RI)
        self.CheckFilter(Chns, VorI, FL)
        self.CheckVMIM(VM, IM)

        #self.instWrite("DZ\n")
        self.instWrite("CL\n")
        self.instWrite("AV %d, %d\n")

        for n in range(len(Chns)):
            self.instWrite("CN %d\n" %(Chns[n]))
            if not FL[n] == None:
                self.instWrite("FL %d, %d\n" %(FL[n], Chns[n]))

            if not SSR[n] == None:
                self.instWrite("SSR %d, %d\n" %(SSR[n], Chns[n]))

            if VorI[n]:
                self.instWrite(self.compileDV(Chns[n], RV[n], Val[n], IComp[n], complPolarity[n], RI[n]))
            else:
                self.instWrite(self.compileDI(Chns[n], RI[n], Val[n], VComp[n], complPolarity[n], RV[n]))

            if VorI[n]:
                self.instWrite("RI %d, %d\n" %(Chns[n], RI[n]))
            else: 
                self.instWrite("RV %d, %d\n" %(Chns[n], RV[n]))
            
            self.instWrite("TSR\n")

            if VM[n]:
                self.instWrite("TTV %d, %d\n" %(Chns[n], RV[n]))
                stTime = tm.time()
                retAr = []
                while True:
                    stb = self.inst.read_stb()
                    binStb = self.getBinaryList(stb)
                    if ((tm.time() - stTime) > self.timeoutTime):
                        timeOut = True
                        break
                    if(binStb[0] ==1):
                        ret = self.instRead()
                        self.label = self.getOutputData(Chns,ret,'FMT1',retAr)
                        self.HSMOutput.append({'Label': self.label['Label'], 'Output': self.label['Output']})
                        break

                tm.sleep(self.waittime)

            
            if IM[n]:
                self.instWrite("TTI %d, %d\n" %(Chns[n], RI[n]))
                stTime = tm.time()
                retAr = []
                while True:
                    stb = self.inst.read_stb()
                    binStb = self.getBinaryList(stb)
                    if ((tm.time() - stTime) > self.timeoutTime):
                        timeOut = True
                        break
                    if(binStb[0] ==1):
                        ret = self.instRead()
                        self.label = self.getOutputData(Chns,ret,'FMT1',retAr)
                        self.HSMOutput.append({'Label': self.label['Label'], 'Output': self.label['Output']})
                        break

                tm.sleep(self.waittime)

        Header = self.getHeader_1(Chns,Val, VorI, SSR, FL, MChn=None, SChn=None)
        ADCHeader = self.getADCHeader()
        Header.extend(ADCHeader)

        #self.instWrite("DZ\n")
        self.instWrite("CL\n")
        self.curHeader = Header

        return {'Data': self.HSMOutput, 'Header': Header}
        
    ############################################################################################
    # can receive Values for a pulsed spot measurement if the Channels passed calibration and are installed
    # Chns: Array containing Channel Numbers
    # PChn: Pulse Measurement Channel must be a channel defined in Chns
    # Val:  Array containing voltage/current values
    # BVal: Array containing base voltages or currents for the pulse channels (Values for constant voltage/current sources are ignored)
    # VorI: Array if I or V are forced contains Binary True for V, False for I
    # hold: Hold time (in s) 0 to 655.35 sec. 10 ms resolution. Initial setting = 0.
    # width: Pulse width for the pulse channels (in s) 0.5 ms to 2.0 s. 0.1 ms resolution. Initial setting = 1 ms.
    # period: Pulse period for the pulse channels (in s) 0, or 5 ms to 5.0 s. 0.1 ms resolution. Initial or default setting = 10 ms.
    # Tdelay: Trigger output dealy time 0 to width sec. 0.1 ms resolution. Default setting = 0.
    # IComp: Array for the set Compliance Current
    # VComp: Array for the set Compliance Voltage
    # RV:   Array of ranges for voltage measurement
    # RI:   Array of ranges for current measurement
    # FL:   Sets the filter of the specified channels to ON or OFF.
    # SSR:  Series resistance will be applied
    # PorC: Choose if Channel shall apply a pulse or a constant voltage/current 
    # hold: Hold time for the pulse channels (in s)
    # delay:  Delay for the pulse channels (in s)
    # CMM:  The CMM command sets the SMU measurement operation mode.
    
    def PulsedSpotMeasurement(self, Chns, PChn, MChn, Val, Pbase, VorI, hold, width, IComp=None, VComp=None, 
                                RV=None, RI=None, period=None, delay=None, tdelay=None, BVal=None, 
                                FL=None, SSR=None, CMM=None, complPolarity=None):
        
        self.checkListConsistancy([Chns, VorI, RV, RI, Val, IComp, VComp, FL, SSR, CMM], "Pulsed Spot Measurement")
        if RV == None: RV = [0]*len(Chns)           # auto voltage range for all active channels
        if RI == None: RI = [0]*len(Chns)           # auto current range for all active channels
        if VComp == None: VComp = [self.VCompDefault]*len(Chns)     # auto compliance for all active Voltage channels
        if IComp == None: IComp = [self.ICompDefault]*len(Chns)     # auto compliance for all active Current channels
        if FL == None: FL = [None]*len(Chns)        # don't set the filter for all active channels
        if SSR == None: SSR = [None]*len(Chns)      # don't set the series resistance for all active channels
        if CMM == None: CMM = [None]*len(Chns)      # don't set the channel mode for all active channels
        if BVal == None: BVal = [0]*len(Chns)       # set all BVal to 0V if not initiated
        if complPolarity == None: complPolarity = [0]*len(Chns)     # auto compliance polarity for all active channels

        for chn in Chns:
            self.SMUisAvailable(chn)
            self.SMUisUsed(chn)
        
        #check if all values in VorI are Boolean
        for element in VorI:
            if not isinstance(element, (bool)):
                raise E5274A_InputError("VorI (Voltage or Current) must only contain boolean values")
        
        #if np.any(not PorC):
        #    raise SyntaxError("P or C (Pulse or Constant) must contain one True Value indicating a Pulse channel")

        self.CheckRanges(Chns, "Voltage", RV)
        self.CheckRanges(Chns, "Current", RI)
        self.CheckVolCurValues(Chns, VorI, Val, RV, RI)
        self.CheckCompliance(Chns, VorI, Val, IComp, VComp, RV, RI)
        self.CheckFilter(Chns, VorI, FL)
        self.CheckSeriesResistance(Chns, SSR)
        self.CheckChannelMode(Chns, CMM)

        hold = float(np.around(hold, 2))
        width = float(np.around(width, 4))
        if not period == None:
            period = float(np.around(period, 4))
        if not delay == None:
            delay = float(np.around(delay, 4))

        self.CheckPulseParamSMU(hold, width, period, delay)

        n= 0
        for Chn in Chns:
            if Chn == PChn:
                self.CheckPulsePVPIParam(Chns, Pbase, Val[n], VComp, IComp, VorI, PChn)
                Ppulse = Val[n]
                break
            
            n = n+1   
        if not MChn in Chns:
            raise E5274A_InputError("MChn is not in Chn list!")

        if MChn == PChn:
            raise E5274A_InputError("PChn must Not be MChn!")

        
        #self.instWrite("DZ\n")
        self.instWrite("CL\n")

        mode = ""

        for n in range(len(Chns)):
            self.instWrite("CN %d\n" %(Chns[n]))
            if not FL[n] == None:
                self.instWrite("FL %d, %d\n" %(FL[n], Chns[n]))

            if not SSR[n] == None:
                self.instWrite("SSR %d, %d\n" %(SSR[n], Chns[n]))
            
            if not self.is_int(PChn):
                raise E5274A_InputError("PChn must be an integer between 1 and 8 and be present in Chns.")
            if PChn > 8 or PChn < 1 or PChn not in Chns: 
                raise E5274A_InputError("PChn must be an integer between 1 and 8 and be present in Chns.")

            
            if Chns[n] == PChn:
                if period==None:
                    self.instWrite("PT %f, %f\n" %(hold, width))
                else:
                    if delay == None:
                        self.instWrite("PT %f, %f, %f\n" %(hold, width, period))
                    else:
                        self.instWrite("PT %f, %f, %f, %f\n" %(hold, width, period, delay))

            if Chns[n] == PChn:
                if VorI[n]:
                    self.instWrite("PV %d, %d, %f, %f, %f\n" %(Chns[n], RV[n], Pbase, Ppulse, IComp[n]))
                else:
                    self.instWrite("PI %d, %d, %f, %f, %f\n" %(Chns[n], RI[n], Pbase, Ppulse, VComp[n]))
            else:
                if VorI[n]:
                    self.instWrite(self.compileDV(Chns[n], RV[n], Val[n], IComp[n], complPolarity[n], RI[n]))
                else:
                    self.instWrite(self.compileDI(Chns[n], RI[n], Val[n], VComp[n], complPolarity[n], RV[n]))


            if VorI[n]:
                self.instWrite("RV %d, %d\n" %(Chns[n], RV[n]))
            else: 
                self.instWrite("RI %d, %d\n" %(Chns[n], RI[n]))

            if not CMM[n] == None:
                self.instWrite("CMM %d, %d\n" %(Chns[n], CMM[n]))
            
            mode = "%s, %d" %(mode, Chns[n])

        self.instWrite("MM 3, %d\n" %(MChn))
        self.instWrite("FMT 1, 1 \n")
        #self.instWrite("MM 3 %d\n" %(PChn))
       # self.instWrite("TSR\n")
        if self.execute:
            #self.instWrite("TM 2\n")
            self.instWrite("XE\n")
            stTime = tm.time()
            retAr = []
            while True:
                stb = self.inst.read_stb()
                binStb = self.getBinaryList(stb)
                if ((tm.time() - stTime) > self.timeoutTime):
                    timeOut = True
                    break
                if(binStb[0] ==1):
                    ret = self.instRead()
                    self.label = self.getOutputData(Chns,ret,'FMT1',retAr)
                    break

                tm.sleep(self.waittime)

        ########CreateHeader
        Header = self.getHeader_1(Chns,Val, VorI, SSR, FL, MChn=None, SChn=None)
        ADCHeader = self.getADCHeader()
        Header.extend(ADCHeader)

        #self.instWrite("DZ\n")
        self.instWrite("CL\n")
        self.curHeader = Header

        return {'Data': retAr, 'Header': Header}

    ############################################################################################
    # can receive Values for a staircase sweep measurement if the Channels passed calibration and are installed
    # Chns: Array with Channel Number
    # VorI: Array if I or V are forced contains Binary True for V, False for I
    # MChn:    Master sweep channel, must be defined within Chns!
    # MVstart:  Master sweep channel start voltage in V
    # MVstop:  Master sweep channel stop voltage in V
    # MVstep:  Master sweep channel steps for V
    # MIstart:  Master sweep channel start voltage in I
    # MIstop:  Master sweep channel stop voltage in I
    # MIstep:  Master sweep channel steps for I
    # hold:  hold time in sec
    # delay:  delay time in sec
    # Val:  Array containing voltages or current values
    # Compl: Array for the set Compliance Current/Voltage
    # Mmode: Sweep mode(1: linear/Single, 2: log/single, 3: linear/double, 4: log/double)
    # MeasChns: specify the channels that should get measured, True/False Array, for each Chns entry in Chns; Auto is all channels
    # SChn:    Secondary sweep channel, must be defined within Chns!
    # Sstart:  Secondary sweep channel start voltage in V
    # Sstop:  Secondary sweep channels stop voltage in V
    # AA: Automatic abort function, 1: Disables the function (initial setting), 2: Enables the function
    # AApost: Source output value after the measurement is normally completed. 1: Start Value (initial setting), 2: Stop Value
    # PCompl: Array for the Power Compliance
    # sdelay:  Step delay time (in seconds)
    # tdelay:  Step source trigger delay time (in seconds)
    # mdelay:  Step measurement trigger delay time (in seconds)
    # RV:   Array of ranges for voltage measurement (standard is auto)
    # RI:   Array of ranges for current measurement (standard is auto)
    # FL:   Sets the filter of the specified channels to ON or OFF.
    # SSR:  Series resistance will be applied
    # ADC:    Sets either the High resolution or High speed A/D converter.
    # CMM:  sets the measurement side, 0: compliance side (initial setting), 1: always Voltage side, 2: always Current side, 3: Force side measurement
    # complPolarity: Polarity of voltage comliance, 0: aAuto mode (default), 1: Manual mode, uses compl polarity
    
    def StaircaseSweepMeasurement(self, Chns, VorI, MChn, Mstart, Mstop, Mstep,
                                    hold, delay, Val, VComp, IComp, Mmode, MeasChns=None, SChn=None, Sstart=None, 
                                    Sstop=None, AA=None, AApost=None, Pcompl=None, 
                                    sdelay=None, tdelay=None, mdelay=None, RV=None, RI=None, FL=None, 
                                    SSR=None, ADC=None, CMM=None, complPolarity=None):
        
        self.checkListConsistancy([Chns, VorI, Val, VComp, IComp, RV, RI, FL, SSR, CMM], "Staircase Sweep Measurement")
        if RV == None: RV = [0]*len(Chns)                   # auto voltage range for all active channels
        if RI == None: RI = [0]*len(Chns)                   # auto current range for all active channels
        if VComp == None: VComp = [0]*len(Chns)             # auto compliance for all active channels
        if IComp == None: IComp = [0]*len(Chns)             # auto compliance for all active channels
        if complPolarity == None: complPolarity = [0]*len(Chns)     # auto compliance polarity for all active channels
        if FL == None: FL = [None]*len(Chns)                # don't set the filter for all active channels
        if SSR == None: SSR = [None]*len(Chns)              # don't set the series resistance for all active channels
        if CMM == None: CMM = [None]*len(Chns)              # don't set the channel mode for all active channels
        if Pcompl == None: Pcompl = [None]*len(Chns)        # don't set the Pcompl for all Channels
        if MeasChns == None: MeasChns = Chns                # sets the standard for MeasChn to measure all Chns
        if ADC == None: ADC = [0]*len(Chns)                 #Sets the ADC to High-Speed for all channels
        for chn in Chns:
            self.SMUisAvailable(chn)
            self.SMUisUsed(chn)
        
        #check if all values in VorI are Boolean
        for element in VorI:
            if not isinstance(element, (bool)):
                raise E5274A_InputError("VorI must only contain boolean values")
        if not SChn == None:
            if MChn in SChn:
                raise E5274A_InputError("SChn (Synchronized sweep Channel) must not be defined as MChn (primary Sweep Channel).")

            for SC in SChn:
                if not SC in Chns:
                    raise E5274A_InputError("SChn (Synchronized sweep Channel) must not be defined as an active Channel in Chns.")
        
        self.CheckADCValues(Chns, ADC)
        self.CheckRanges(Chns, "Voltage", RV)
        self.CheckRanges(Chns, "Current", RI)
        self.CheckVolCurValues(Chns, VorI, Val, RV, RI)
        self.CheckCompliance(Chns, VorI, Val, IComp, VComp, RV, RI)
        self.CheckFilter(Chns, VorI, FL)
        self.CheckSeriesResistance(Chns, SSR)
        self.CheckChannelMode(Chns, CMM)
        n=0
        for chn in Chns: 
            if MChn == chn: 
                if VorI[n]:
                    self.CheckSweepParamV(hold, delay, sdelay, tdelay, mdelay, AA, AApost, SChn, Sstart, Sstop, MChn, Mstart, Mstop, Mstep, Mmode)
                else:
                    self.CheckSweepParamI(hold, delay, sdelay, tdelay, mdelay, AA, AApost, SChn, Sstart, Sstop, MChn, Mstart, Mstop, Mstep, Mmode)
                break
            n= n+1

        self.checkComplPolarity(Chns, complPolarity)

        n = 0
        for Chn in Chns:
            if Chn == MChn:
                Mn = n
            if Chn == SChn:
                Sn = n

        self.instWrite("CL\n")

        n=0
        for chn in Chns:
            if ADC[n] != None:
                self.instWrite("AAD %d, %d\n" %(chn,ADC[n]))
            n+=1
        n=0

        mode = ''

        for n in range(len(Chns)):            
            self.instWrite("CN %d\n" %(Chns[n]))
            
            if not FL[n] == None:
                self.instWrite("FL %d, %d\n" %(FL[n], Chns[n]))

            if not SSR[n] == None:
                self.instWrite("SSR %d, %d\n" %(SSR[n], Chns[n]))
            
            if Chns[n] == MChn:
                if VorI[n]:
                    self.instWrite(self.compileWV(Chns[n], Mmode, RV[n], Mstart, Mstop, Mstep, IComp[n]))
                else:
                    self.instWrite(self.compileWI(Chns[n], Mmode, RV[n], Mstart, Mstop, Mstep, VComp[n]))
                #Val[n] = 0
            elif not SChn == None:
                if Chns[n] in SChn:
                    if VorI[n]:
                        self.instWrite(self.compileWSV(Chns[n], RV[n], Sstart, Sstop, IComp[n], Pcompl[n]))
                    else:
                        self.instWrite(self.compileWSI(Chns[n], RI[n], Sstart, Sstop, VComp[n], Pcompl[n]))
                    #Val[n] = 0
                else:
                    if VorI[n]:  
                        self.instWrite(self.compileDV(Chns[n], RV[n], Val[n], IComp[n], complPolarity[n], RI[n]))
                    else:
                        self.instWrite(self.compileDI(Chns[n], RV[n], Val[n], VComp[n], complPolarity[n], RV[n]))
            else:
                if VorI[n]:  
                    self.instWrite(self.compileDV(Chns[n], RV[n], Val[n], IComp[n], complPolarity[n], RI[n]))
                else:
                    self.instWrite(self.compileDI(Chns[n], RV[n], Val[n], VComp[n], complPolarity[n], RV[n]))
            
            if VorI[n]:
                self.instWrite("RI %d, %d\n" %(Chns[n], RI[n]))
            else: 
                self.instWrite("RV %d, %d\n" %(Chns[n], RV[n]))

            if not CMM[n] == None:
                self.instWrite("CMM %d, %d\n" %(Chns[n], CMM[n]))
            
            if MeasChns[n]:
                mode = "%s, %d" %(mode, Chns[n])


        if not AA == None:
            if not AApost == None:
                self.instWrite("WM %d, %d\n" %(AA, AApost))
            else:
                self.instWrite("WM %d\n" %(AA))
        
        self.instWrite("MM 2 %s\n" %(mode))
        
        self.instWrite("FMT 1, 1 \n")

        if self.execute:
            self.instWrite("XE\n")
            
            stTime = tm.time()
            retAr = []
            while True:
                stb = self.inst.read_stb()
                binStb = self.getBinaryList(stb)
                if ((tm.time() - stTime) > self.timeoutTime):
                    timeOut = True
                    break
                if(binStb[0] ==1):
                    ret = self.instRead()
                    self.label = self.getOutputData(Chns,ret,'FMT1',retAr)
                    break
                
                tm.sleep(self.waittime)

        ########CreateHeader
        Header = self.getHeader_1(Chns,Val, VorI, SSR, FL, MChn=MChn, SChn=SChn)

        """
        SweepMode = self.getSweepMode(Mmode)
        Header.append('TestParameter,Measurement.Primary.Locus,%s' %(SweepMode[0]))
        Header.append('TestParameter,Measurement.Primary.Scale,%s' %(SweepMode[1]))
        Header.append('TestParameter,Measurement.Primary.Start,%f' %(Mstart))
        Header.append('TestParameter,Measurement.Primary.Stop,%f' %(Mstop))
        Header.append('TestParameter,Measurement.Primary.Step,%f' %(Mstep))
        Header.append('TestParameter,Measurement.Primary.Compliance,%f,%f' %(VComp[Mn], IComp[Mn]))
        if Pcompl[Mn] == None:
            Header.append('TestParameter,Measurement.Primary.PowerCompliance,0')
        else:
            Header.append('TestParameter,Measurement.Primary.PowerCompliance,%f' %(Pcompl[Mn]))
        if AA == 1:
            Header.append('TestParameter,Measurement.Aborting.Condition,CONTINUE AT ANY')
            if AApost == None or AApost == 1:
                Header.append('TestParameter,Measurement.PostOutput.Value, START')
            else:
                Header.append('TestParameter,Measurement.PostOutput.Value, STOP')
        elif AA == 2:
            Header.append('TestParameter,Measurement.Aborting.Condition, ENABLED')
            if AApost == None or AApost == 1:
                Header.append('TestParameter,Measurement.PostOutput.Value, START')
            else:
                Header.append('TestParameter,Measurement.PostOutput.Value, STOP')
        else:
            Header.append('TestParameter,Measurement.Aborting.Condition,CONTINUE AT ANY')
            Header.append('TestParameter,Measurement.PostOutput.Value, START')

        if not SChn == None:
            Header.append('TestParameter,Measurement.Secondary.start,%f' %(Sstart))
            Header.append('TestParameter,Measurement.Secondary.stop,%f' %(Sstop))
            Header.append('TestParameter,Measurement.Secondary.Compliance,%f' %(Compl[Sn]))
            Header.append('TestParameter,Measurement.Secondary.PowerCompliance,%f' %(Pcompl[Sn]))
        
        MonitorHeader = self.getMonitorHeader(Chns, Val, Compl, VorI, ADC, RI, RV, CMM)
        Header.extend(MonitorHeader)

        Header.append('TestParameter,Timing.Hold, %f' %(hold))
        Header.append('TestParameter,Timing.Delay, %f' %(delay))
        if not sdelay == None:
            Header.append('TestParameter,Timing.StepDelay, %f' %(sdelay))
        else:
            Header.append('TestParameter,Timing.StepDelay,')
        if not tdelay == None:
            Header.append('TestParameter,Timing.StepSourceTriggerDelay, %f' %(tdelay))
        else:
            Header.append('TestParameter,Timing.StepSourceTriggerDelay,')
        if not mdelay == None:
            Header.append('TestParameter,Timing.StepMeasurementTriggerDelay, %f' %(mdelay))
        else:
            Header.append('TestParameter,Timing.StepMeasurementTriggerDelay,')
        """
        ADCHeader = self.getADCHeader()
        Header.extend(ADCHeader)

        #self.instWrite("DZ\n")
        self.instWrite("CL\n")
        self.curHeader = Header

        return {'Data': retAr, 'Header': Header}

    ############################################################################################
    # can receive Values for a staircase sweep measurement if the Channels passed calibration and are installed
    # Chns: Array with Channel Number
    # VorI: Array if I or V are forced contains Binary True for V, False for I
    # MChn:    Master sweep channel, must be defined within Chns!
    # Mstart:  Master sweep channel start voltage in V
    # Mstop:  Master sweep channel stop voltage in V
    # Mstep:  Master sweep channel steps
    # hold:  hold time in sec
    # delay:  delay time in sec
    # Val:  Array containing voltages or current values
    # Compl: Array for the set Compliance Current/Voltage
    # Mmode: Sweep mode(1: linear/Single, 2: log/single, 3: linear/double, 4: log/double)
    # MeasChns: specify the channels that should get measured, True/False Array, for each Chns entry in Chns; Auto is all channels
    # SChn:    Secondary sweep channel, must be defined within Chns!
    # Sstart:  Secondary sweep channel start voltage in V
    # Sstop:  Secondary sweep channels stop voltage in V
    # AA: Automatic abort function, 1: Disables the function (initial setting), 2: Enables the function
    # AApost: Source output value after the measurement is normally completed. 1: Start Value (initial setting), 2: Stop Value
    # PCompl: Array for the Power Compliance
    # sdelay:  Step delay time (in seconds)
    # tdelay:  Step source trigger delay time (in seconds)
    # mdelay:  Step measurement trigger delay time (in seconds)
    # RV:   Array of ranges for voltage measurement (standard is auto)
    # RI:   Array of ranges for current measurement (standard is auto)
    # FL:   Sets the filter of the specified channels to ON or OFF.
    # SSR:  Series resistance will be applied
    # ADC:    Sets either the High resolution or High speed A/D converter.
    # CMM:  sets the measurement side, 0: compliance side (initial setting), 1: always Voltage side, 2: always Current side, 3: Force side measurement
    # complPolarity: Polarity of voltage comliance, 0: aAuto mode (default), 1: Manual mode, uses compl polarity

    def MultiChannelSweepMeasurement(self, Chns, VorI, MChn, MVstart, MVstop, MVstep, MIstart, MIstop, MIstep,
                                    hold, delay, Val, VComp, IComp, Mmode, RV, RI, MeasChns=None, 
                                    SChn=None, Sstart=None, Sstop=None, AA=None, AApost=None, Pcompl=None, 
                                    sdelay=None, tdelay=None, mdelay=None, FL=None, 
                                    SSR=None, ADC=None, CMM=None, complPolarity=None):

        self.checkListConsistancy([Chns, VorI, Val, VComp, IComp, RV, RI, FL, SSR, CMM], "Multi Channel Sweep Measurement")
        if RV == None: RV = [0]*len(Chns)                   # auto voltage range for all active channels
        if RI == None: RI = [0]*len(Chns)                   # auto current range for all active channels
        if VComp == None: VComp = [0]*len(Chns)             # auto compliance for all active channels
        if IComp == None: IComp = [0]*len(Chns)             # auto compliance for all active channels
        if complPolarity == None: complPolarity = [0]*len(Chns)     # auto compliance polarity for all active channels
        if FL == None: FL = [None]*len(Chns)                # don't set the filter for all active channels
        if SSR == None: SSR = [None]*len(Chns)              # don't set the series resistance for all active channels
        if CMM == None: CMM = [None]*len(Chns)              # don't set the channel mode for all active channels
        if Pcompl == None: Pcompl = [None]*len(Chns)        # don't set the Pcompl for all Channels
        if MeasChns == None: MeasChns = Chns                # sets the standard for MeasChn to measure all Chns
        if ADC == None: ADC = [0]*len(Chns)                 #Sets the ADC to High-Speed for all channels
        for chn in Chns:
            self.SMUisAvailable(chn)
            self.SMUisUsed(chn)
        
        #check if all values in VorI are Boolean
        for element in VorI:
            if not isinstance(element, (bool)):
                raise E5274A_InputError("VorI must only contain boolean values")
        if not SChn == None:
            if MChn in SChn:
                raise E5274A_InputError("SChn (Synchronized sweep Channel) must not be defined as MChn (primary Sweep Channel).")

            for SC in SChn:
                if not SC in Chns:
                    raise E5274A_InputError("SChn (Synchronized sweep Channel) must not be defined as an active Channel in Chns.")
        
        self.CheckADCValues(Chns, ADC)
        self.CheckRanges(Chns, "Voltage", RV)
        self.CheckRanges(Chns, "Current", RI)
        self.CheckVolCurValues(Chns, VorI, Val, RV, RI)
        self.CheckCompliance(Chns, VorI, Val, IComp, VComp, RV, RI)
        self.CheckFilter(Chns, VorI, FL)
        self.CheckSeriesResistance(Chns, SSR)
        self.CheckChannelMode(Chns, CMM)
        self.CheckSweepParamV(hold, delay, sdelay, tdelay, mdelay, AA, AApost, SChn, Sstart, Sstop, MChn, MVstart, MVstop, MVstep, Mmode)
        self.CheckSweepParamI(hold, delay, sdelay, tdelay, mdelay, AA, AApost, SChn, Sstart, Sstop, MChn, MIstart, MIstop, MIstep, Mmode)
        self.checkComplPolarity(Chns, complPolarity)

        n = 0
        for Chn in Chns:
            if Chn == MChn:
                Mn = n
            if Chn == SChn:
                Sn = n

        #self.instWrite("DZ\n")
        self.instWrite("CL\n")

        n=0
        for chn in Chns:
            if ADC[n] != None:
                self.instWrite("AAD %d, %d\n" %(chn,ADC[n]))
            n+=1
        n=0



        mode = ''

        L = 1

        for n in range(len(Chns)):            
            self.instWrite("CN %d\n" %(Chns[n]))
            
            if not FL[n] == None:
                self.instWrite("FL %d, %d\n" %(FL[n], Chns[n]))

            if not SSR[n] == None:
                self.instWrite("SSR %d, %d\n" %(SSR[n], Chns[n]))
            
            if Chns[n] == MChn:
                if VorI[n]:
                    self.instWrite(self.compileWV(Chns[n], Mmode, RV[n], MVstart, MVstop, MVstep, IComp[n]))
                else:
                    self.instWrite(self.compileWI(Chns[n], Mmode, RV[n], MIstart, MIstop, MIstep, VComp[n]))
                #Val[n] = 0
            else:
                L+=1
                if VorI[n]:
                    WMXmode = 1
                    self.instWrite(self.compileWNX(L, Chns[n], WMXmode, RV[n], MVstart, MVstop, MVstep, IComp[n], Pcompl[n]))
                else:
                    WMXmode = 2
                    self.instWrite(self.compileWNX(L, Chns[n], WMXmode, RI[n], MIstart, MIstop, MIstep, VComp[n], Pcompl[n]))
            
            if VorI[n]:
                self.instWrite("RI %d, %d\n" %(Chns[n], RV[n]))
            else: 
                self.instWrite("RV %d, %d\n" %(Chns[n], RI[n]))

            if not CMM[n] == None:
                self.instWrite("CMM %d, %d\n" %(Chns[n], CMM[n]))
            
            if MeasChns[n]:
                mode = "%s, %d" %(mode, Chns[n])


        if not AA == None:
            if not AApost == None:
                self.instWrite("WM %d, %d\n" %(AA, AApost))
            else:
                self.instWrite("WM %d\n" %(AA))
        
        self.instWrite("WM 1\n")
        self.instWrite("MM 16%s\n" %(mode))
        self.instWrite("FMT 1, 1 \n")
        
        if self.execute:
            self.instWrite("XE\n")
            
            stTime = tm.time()
            retAr = []
            while True:
                stb = self.inst.read_stb()
                binStb = self.getBinaryList(stb)
                if ((tm.time() - stTime) > self.timeoutTime):
                    timeOut = True
                    break
                if(binStb[0] ==1):
                    ret = self.instRead()
                    self.label = self.getOutputData(Chns,ret,'FMT1',retAr)
                    break
                
                tm.sleep(self.waittime)

        ########CreateHeader
        Header = self.getHeader_1(Chns,Val, VorI, SSR, FL, MChn=MChn, SChn=SChn)

        """
        SweepMode = self.getSweepMode(Mmode)
        Header.append('TestParameter,Measurement.Primary.Locus,%s' %(SweepMode[0]))
        Header.append('TestParameter,Measurement.Primary.Scale,%s' %(SweepMode[1]))
        Header.append('TestParameter,Measurement.Primary.Start,%f' %(Mstart))
        Header.append('TestParameter,Measurement.Primary.Stop,%f' %(Mstop))
        Header.append('TestParameter,Measurement.Primary.Step,%f' %(Mstep))
        Header.append('TestParameter,Measurement.Primary.Compliance,%f,%f' %(VComp[Mn], IComp[Mn]))
        if Pcompl[Mn] == None:
            Header.append('TestParameter,Measurement.Primary.PowerCompliance,0')
        else:
            Header.append('TestParameter,Measurement.Primary.PowerCompliance,%f' %(Pcompl[Mn]))
        if AA == 1:
            Header.append('TestParameter,Measurement.Aborting.Condition,CONTINUE AT ANY')
            if AApost == None or AApost == 1:
                Header.append('TestParameter,Measurement.PostOutput.Value, START')
            else:
                Header.append('TestParameter,Measurement.PostOutput.Value, STOP')
        elif AA == 2:
            Header.append('TestParameter,Measurement.Aborting.Condition, ENABLED')
            if AApost == None or AApost == 1:
                Header.append('TestParameter,Measurement.PostOutput.Value, START')
            else:
                Header.append('TestParameter,Measurement.PostOutput.Value, STOP')
        else:
            Header.append('TestParameter,Measurement.Aborting.Condition,CONTINUE AT ANY')
            Header.append('TestParameter,Measurement.PostOutput.Value, START')

        if not SChn == None:
            Header.append('TestParameter,Measurement.Secondary.start,%f' %(Sstart))
            Header.append('TestParameter,Measurement.Secondary.stop,%f' %(Sstop))
            Header.append('TestParameter,Measurement.Secondary.Compliance,%f' %(Compl[Sn]))
            Header.append('TestParameter,Measurement.Secondary.PowerCompliance,%f' %(Pcompl[Sn]))
        
        MonitorHeader = self.getMonitorHeader(Chns, Val, Compl, VorI, ADC, RI, RV, CMM)
        Header.extend(MonitorHeader)

        Header.append('TestParameter,Timing.Hold, %f' %(hold))
        Header.append('TestParameter,Timing.Delay, %f' %(delay))
        if not sdelay == None:
            Header.append('TestParameter,Timing.StepDelay, %f' %(sdelay))
        else:
            Header.append('TestParameter,Timing.StepDelay,')
        if not tdelay == None:
            Header.append('TestParameter,Timing.StepSourceTriggerDelay, %f' %(tdelay))
        else:
            Header.append('TestParameter,Timing.StepSourceTriggerDelay,')
        if not mdelay == None:
            Header.append('TestParameter,Timing.StepMeasurementTriggerDelay, %f' %(mdelay))
        else:
            Header.append('TestParameter,Timing.StepMeasurementTriggerDelay,')
        """
        ADCHeader = self.getADCHeader()
        Header.extend(ADCHeader)

        #self.instWrite("DZ\n")
        self.instWrite("CL\n")
        self.curHeader = Header

        return {'Data': retAr, 'Header': Header}

    ############################################################################################
    # can receive Values for a staircase sweep measurement if the Channels passed calibration and are installed
    # Chns: Array with Channel Number
    # VorI: Array if I or V are forced contains Binary True for V, False for I
    # MChn:    Master sweep channel, must be defined within Chns!
    # Mstart:  Master sweep channel start voltage in V
    # Mstop:  Master sweep channel stop voltage in V
    # Mstep:  Master sweep channel steps
    # hold:  hold time in sec
    # delay:  delay time in sec
    # Val:  Array containing voltages or current values
    # Compl: Array for the set Compliance Current/Voltage
    # Mmode: Sweep mode(1: linear/Single, 2: log/single, 3: linear/double, 4: log/double)
    # MeasChns: specify the channels that should get measured, True/False Array, for each Chns entry in Chns; Auto is all channels
    # SChn:    Secondary sweep channel, must be defined within Chns!
    # Sstart:  Secondary sweep channel start voltage in V
    # Sstop:  Secondary sweep channels stop voltage in V
    # AA: Automatic abort function, 1: Disables the function (initial setting), 2: Enables the function
    # AApost: Source output value after the measurement is normally completed. 1: Start Value (initial setting), 2: Stop Value
    # PCompl: Array for the Power Compliance
    # sdelay:  Step delay time (in seconds)
    # tdelay:  Step source trigger delay time (in seconds)
    # mdelay:  Step measurement trigger delay time (in seconds)
    # RV:   Array of ranges for voltage measurement (standard is auto)
    # RI:   Array of ranges for current measurement (standard is auto)
    # FL:   Sets the filter of the specified channels to ON or OFF.
    # SSR:  Series resistance will be applied
    # ADC:    Sets either the High resolution or High speed A/D converter.
    # CMM:  sets the measurement side, 0: compliance side (initial setting), 1: always Voltage side, 2: always Current side, 3: Force side measurement
    # complPolarity: Polarity of voltage comliance, 0: aAuto mode (default), 1: Manual mode, uses compl polarity
    # SWMode: Sweep Mode for Pulsed sweep voltage/current, 1: Linear sweep (single stair, start to stop.), 3: Linear sweep (double stair, start to stop to start.)

    def PulsedSweepMeasurement(self, Chns, PChn, VPbase, VPpulse, VPulseStop, IPbase, IPpulse, IPulseStop, 
                                PStep, SWMode, VorI, RV, RI, Val, IComp, VComp, hold, width, period=None, 
                                delay=None, AA=None, BVal=None, FL=None, SSR=None, CMM=None, PCompl=None,
                                complPolarity=None, AApost=None,SChn=None, Sstart=None, Sstop=None):
        self.checkListConsistancy([Chns, VorI, RV, RI, Val, IComp, VComp, FL, SSR, CMM], "Pulsed Sweep Measurement")
        if RV == None: RV = [0]*len(Chns)           # auto voltage range for all active channels
        if RI == None: RI = [0]*len(Chns)           # auto current range for all active channels
        if IComp == None: IComp = [0]*len(Chns)     # auto compliance for all active channels
        if VComp == None: VComp = [0]*len(Chns)     # auto compliance for all active channels
        if FL == None: FL = [None]*len(Chns)        # don't set the filter for all active channels
        if SSR == None: SSR = [None]*len(Chns)      # don't set the series resistance for all active channels
        if CMM == None: CMM = [None]*len(Chns)      # don't set the channel mode for all active channels
        if BVal == None: BVal = [0]*len(Chns)       # set all BVal to 0V if not initiated
        if complPolarity == None: complPolarity = [0]*len(Chns)     # auto compliance polarity for all active channels
        if period == None: period = [0]*len(Chns)     # set period for all active channels
        if delay == None: delay = [0]*len(Chns)     # set delay for all active channels
        if PCompl == None: PCompl = [None]*len(Chns)     # sets None Compliance for Power Output for all active channels


        for chn in Chns:
            self.SMUisAvailable(chn)
            self.SMUisUsed(chn)
        
        #check if all values in VorI are Boolean
        for element in VorI:
            if not isinstance(element, (bool)):
                raise E5274A_InputError("VorI (Voltage or Current) must only contain boolean values")
        
        #if np.any(not PorC):
        #    raise SyntaxError("P or C (Pulse or Constant) must contain one True Value indicating a Pulse channel")

        self.CheckRanges(Chns, "Voltage", RV)
        self.CheckRanges(Chns, "Current", RI)
        self.CheckVolCurValues(Chns, VorI, Val, RV, RI)
        self.CheckCompliance(Chns, VorI, Val, IComp, VComp, RV, RI)
        self.CheckFilter(Chns, VorI, FL)
        self.CheckSeriesResistance(Chns, SSR)
        self.CheckChannelMode(Chns, CMM)

        hold = np.around(hold, 2)
        width = np.around(width, 4)
        if not period == None:
            period = np.around(period, 4)
        if not delay == None:
            delay = np.around(delay, 4)

        self.CheckPulseParamSMU(hold, width, period, delay)
        self.CheckPulseSweepParam(Chns, VPbase, VPpulse, VPulseStop, IPbase, IPpulse, IPulseStop, PStep, VComp, IComp, VorI, PChn)

        #self.instWrite("DZ\n")
        self.instWrite("CL\n")

        mode = ""

        for n in range(len(Chns)):
            self.instWrite("CN %d\n" %(Chns[n]))
            if not FL[n] == None:
                self.instWrite("FL %d, %d\n" %(FL[n], Chns[n]))

            if not SSR[n] == None:
                self.instWrite("SSR %d, %d\n" %(SSR[n], Chns[n]))
            
            if not self.is_int(PChn):
                raise E5274A_InputError("PChn must be an integer between 1 and 8 and be present in Chns.")
            if PChn > 8 or PChn < 1 or PChn not in Chns: 
                raise E5274A_InputError("PChn must be an integer between 1 and 8 and be present in Chns.")

            if Chns[n] == PChn:
                if period==None:
                    self.instWrite("PT %f, %f\n" %(hold, width))
                else:
                    if delay == None:
                        self.instWrite("PT %f, %f, %f\n" %(hold, width, period))
                    else:
                        self.instWrite("PT %f, %f, %f, %f\n" %(hold, width, period, delay))

            if Chns[n] == PChn:
                if VorI[n]:
                    self.instWrite("PWV %d, %d, %d, %f, %f, %f, %d, %f\n" %(Chns[n], SWMode, 
                                                            RV[n], VPbase, VPpulse, VPulseStop, PStep, IComp[n]))
                else:
                    self.instWrite("PWI %d, %d, %d, %f, %f, %f, %d, %f\n" %(Chns[n], SWMode, 
                                                            RI[n], IPbase, IPpulse, IPulseStop, PStep, VComp[n]))
            elif not SChn == None:
                if Chns[n] in SChn:
                    if VorI[n]:
                        self.instWrite(self.compileWSV(Chns[n], RV[n], Sstart, Sstop, IComp[n], PCompl[n]))
                    else:
                        self.instWrite(self.compileWSI(Chns[n], RI[n], Sstart, Sstop, VComp[n], PCompl[n]))
                    #Val[n] = 0
                else:
                    if not Chns[n] == PChn:
                        if VorI[n]:  
                            self.instWrite(self.compileDV(Chns[n], RV[n], Val[n], IComp[n], complPolarity[n], RI[n]))
                        else:
                            self.instWrite(self.compileDI(Chns[n], RV[n], Val[n], VComp[n], complPolarity[n], RV[n]))
            else:
                if VorI[n]:
                    self.instWrite(self.compileDV(Chns[n], RV[n], Val[n], IComp[n], complPolarity[n], RI[n]))
                else:
                    self.instWrite(self.compileDI(Chns[n], RI[n], Val[n], VComp[n], complPolarity[n], RV[n]))

            if VorI[n]:
                self.instWrite("RV %d, %d\n" %(Chns[n], RV[n]))
            else: 
                self.instWrite("RI %d, %d\n" %(Chns[n], RI[n]))

            if not CMM[n] == None:
                self.instWrite("CMM %d, %d\n" %(Chns[n], CMM[n]))
            
            mode = "%s, %d" %(mode, Chns[n])

        if not AA == None:
            if not AApost == None:
                self.instWrite("WM %d, %d\n" %(AA, AApost))
            else:
                self.instWrite("WM %d\n" %(AA))
        
        self.instWrite("MM 4, %d\n" %(PChn))
        self.instWrite("FMT 1, 1 \n")
        #self.instWrite("MM 4, 2\n")
       # self.instWrite("TSR\n")
        if self.execute:
            self.instWrite("XE\n")
            stTime = tm.time()
            retAr = []
            while True:
                stb = self.inst.read_stb()
                binStb = self.getBinaryList(stb)
                if ((tm.time() - stTime) > self.timeoutTime):
                    timeOut = True
                    break
                if(binStb[0] ==1):
                    ret = self.instRead()
                    self.label = self.getOutputData(Chns,ret,'FMT1',retAr)
                    break

                tm.sleep(self.waittime)

        ########CreateHeader
        Header = self.getHeader_1(Chns,Val, VorI, SSR, FL, MChn=None, SChn=None)
        ADCHeader = self.getADCHeader()
        Header.extend(ADCHeader)
        self.curHeader = Header

        return {'Data': retAr, 'Header': Header}


    ############################################################################################
    # can receive Values for a Staircase Sweep Pulsed Bias Measurement if the Channels passed calibration and are installed
    # Chns: Array with Channel Number
    # VorI: Array if I or V are forced contains Binary True for V, False for I
    # MChn:    Master sweep channel, must be defined within Chns!
    # MVstart:  Master sweep channel start voltage in V
    # MVstop:  Master sweep channel stop voltage in V
    # MVstep:  Master sweep channel steps for V
    # MIstart:  Master sweep channel start voltage in I
    # MIstop:  Master sweep channel stop voltage in I
    # MIstep:  Master sweep channel steps for I
    # hold:  hold time in sec
    # delay:  delay time in sec
    # Val:  Array containing voltages or current values
    # Compl: Array for the set Compliance Current/Voltage
    # Mmode: Sweep mode(1: linear/Single, 2: log/single, 3: linear/double, 4: log/double)
    # MeasChns: specify the channels that should get measured, True/False Array, for each Chns entry in Chns; Auto is all channels
    # SChn:    Secondary sweep channel, must be defined within Chns!
    # Sstart:  Secondary sweep channel start voltage in V
    # Sstop:  Secondary sweep channels stop voltage in V
    # AA: Automatic abort function, 1: Disables the function (initial setting), 2: Enables the function
    # AApost: Source output value after the measurement is normally completed. 1: Start Value (initial setting), 2: Stop Value
    # PCompl: Array for the Power Compliance
    # sdelay:  Step delay time (in seconds)
    # tdelay:  Step source trigger delay time (in seconds)
    # mdelay:  Step measurement trigger delay time (in seconds)
    # RV:   Array of ranges for voltage measurement (standard is auto)
    # RI:   Array of ranges for current measurement (standard is auto)
    # FL:   Sets the filter of the specified channels to ON or OFF.
    # SSR:  Series resistance will be applied
    # ADC:    Sets either the High resolution or High speed A/D converter.
    # CMM:  sets the measurement side, 0: compliance side (initial setting), 1: always Voltage side, 2: always Current side, 3: Force side measurement
    # complPolarity: Polarity of voltage comliance, 0: aAuto mode (default), 1: Manual mode, uses compl polarity

    def StaircaseSweepWPulsedBiasMeasurement(self, Chns, VorI, PBChn, SSChn, SynSChn, MVstart, MVstop, MVstep, 
                                    MIstart, MIstop, MIstep, hold, width, period, delay, Val, 
                                    VComp, IComp, Mmode, VPbase, VPpulse, IPbase, IPpulse, RV, RI, AA, AApost,
                                    MeasChns=None, SChn=None, Sstart=None, Sstop=None, Pcompl=None, 
                                    sdelay=None, tdelay=None, mdelay=None, FL=None, SSR=None, 
                                    ADC=None, CMM=None, complPolarity=None):
        
        self.checkListConsistancy([Chns, VorI, Val, VComp, IComp, RV, RI, FL, SSR, CMM], "Staircase Sweep Pulsed Bias Measurement")
        if RV == None: RV = [0]*len(Chns)                   # auto voltage range for all active channels
        if RI == None: RI = [0]*len(Chns)                   # auto current range for all active channels
        if VComp == None: VComp = [0]*len(Chns)             # auto compliance for all active channels
        if IComp == None: IComp = [0]*len(Chns)             # auto compliance for all active channels
        if complPolarity == None: complPolarity = [0]*len(Chns)     # auto compliance polarity for all active channels
        if FL == None: FL = [None]*len(Chns)                # don't set the filter for all active channels
        if SSR == None: SSR = [None]*len(Chns)              # don't set the series resistance for all active channels
        if CMM == None: CMM = [None]*len(Chns)              # don't set the channel mode for all active channels
        if Pcompl == None: Pcompl = [None]*len(Chns)        # don't set the Pcompl for all Channels
        if MeasChns == None: MeasChns = Chns                # sets the standard for MeasChn to measure all Chns
        if ADC == None: ADC = [0]*len(Chns)                 #Sets the ADC to High-Speed for all channels
        for chn in Chns:
            self.SMUisAvailable(chn)
            self.SMUisUsed(chn)
        
        #check if all values in VorI are Boolean
        for element in VorI:
            if not isinstance(element, (bool)):
                raise E5274A_InputError("VorI must only contain boolean values")
        if not SynSChn == None:
            if PBChn in SynSChn:
                raise E5274A_InputError("SynSChn (Synchronized sweep Channel) must not be defined as PBChn (Pulsed Bias Channel).")
            if SynSChn in SChn:
                raise E5274A_InputError("SynSChn (Synchronized sweep Channel) must not be defined as MChn (primary Sweep Channel).")

            for SC in SynSChn:
                if not SC in Chns:
                    raise E5274A_InputError("SynSChn (Synchronized sweep Channel) must not be defined as an active Channel in Chns.")
        
        self.CheckADCValues(Chns, ADC)
        self.CheckRanges(Chns, "Voltage", RV)
        self.CheckRanges(Chns, "Current", RI)
        self.CheckVolCurValues(Chns, VorI, Val, RV, RI)
        self.CheckCompliance(Chns, VorI, Val, IComp, VComp, RV, RI)
        self.CheckFilter(Chns, VorI, FL)
        self.CheckSeriesResistance(Chns, SSR)
        self.CheckChannelMode(Chns, CMM)
        self.CheckSweepParamV(hold, delay, sdelay, tdelay, delay, AA, AApost, SChn, Sstart, Sstop, SSChn, MVstart, MVstop, MVstep, Mmode)
        self.CheckSweepParamI(hold, delay, sdelay, tdelay, delay, AA, AApost, SChn, Sstart, Sstop, SSChn, MIstart, MIstop, MIstep, Mmode)
        self.checkComplPolarity(Chns, complPolarity)

        n = 0
        """
        for Chn in Chns:
            if Chn == MChn:
                Mn = n
            if Chn == SChn:
                Sn = n
        """
        #self.instWrite("DZ\n")
        self.instWrite("CL\n")

        n=0

        mode = ''

        for n in range(len(Chns)):            
            self.instWrite("CN %d\n" %(Chns[n]))
            
            if not FL[n] == None:
                self.instWrite("FL %d, %d\n" %(FL[n], Chns[n]))

            if not SSR[n] == None:
                self.instWrite("SSR %d, %d\n" %(SSR[n], Chns[n]))


            if not self.is_int(SSChn):
                raise E5274A_InputError("SSChn must be an integer between 1 and 8 and be present in Chns.")
            if SSChn > 8 or SSChn < 1 or SSChn not in Chns: 
                raise E5274A_InputError("SSChn must be an integer between 1 and 8 and be present in Chns.")

            if not self.is_int(PBChn):
                raise E5274A_InputError("PBChn must be an integer between 1 and 8 and be present in Chns.")
            if PBChn > 8 or PBChn < 1 or PBChn not in Chns: 
                raise E5274A_InputError("PBChn must be an integer between 1 and 8 and be present in Chns.")

            
            if Chns[n] == SSChn:
                if VorI[n]:
                    self.instWrite(self.compileWV(Chns[n], Mmode, RV[n], MVstart, MVstop, MVstep, IComp[n]))
                else:
                    self.instWrite(self.compileWI(Chns[n], Mmode, RV[n], MIstart, MIstop, MIstep, VComp[n]))
                #Val[n] = 0

            if Chns[n] == PBChn:
                if period==None:
                    self.instWrite("PT %f, %f\n" %(hold, width))
                else:
                    if delay == None:
                        self.instWrite("PT %f, %f, %f\n" %(hold, width, period))
                    else:
                        self.instWrite("PT %f, %f, %f, %f\n" %(hold, width, period, delay))

            if Chns[n] == PBChn:
                if VorI[n]:
                    self.instWrite("PV %d, %d, %f, %f, %f\n" %(Chns[n], RV[n], VPbase, VPpulse, IComp[n]))
                else:
                    self.instWrite("PI %d, %d, %f, %f, %f\n" %(Chns[n], RI[n], IPbase, IPpulse, VComp[n]))
            
            if Chns[n] == SynSChn:
                if VorI[n]:
                    self.instWrite(self.compileWSV(Chns[n], RV[n], Sstart, Sstop, IComp[n], Pcompl[n]))
                else:
                    self.instWrite(self.compileWSI(Chns[n], RI[n], Sstart, Sstop, VComp[n], Pcompl[n]))
            
            
            if VorI[n]:
                self.instWrite("RI %d, %d\n" %(Chns[n], RI[n]))
            else: 
                self.instWrite("RV %d, %d\n" %(Chns[n], RV[n]))

            if not CMM[n] == None:
                self.instWrite("CMM %d, %d\n" %(Chns[n], CMM[n]))
            
            if MeasChns[n]:
                mode = "%s, %d" %(mode, Chns[n])


        if not AA == None:
            if not AApost == None:
                self.instWrite("WM %d, %d\n" %(AA, AApost))
            else:
                self.instWrite("WM %d\n" %(AA))
        
        self.instWrite("MM 5, %s\n" %(PBChn))
        self.instWrite("FMT 1, 1 \n")
        
        if self.execute:
            self.instWrite("XE\n")
            
            stTime = tm.time()
            retAr = []
            while True:
                stb = self.inst.read_stb()
                binStb = self.getBinaryList(stb)
                if ((tm.time() - stTime) > self.timeoutTime):
                    timeOut = True
                    break
                if(binStb[0] ==1):
                    ret = self.instRead()
                    self.label = self.getOutputData(Chns,ret,'FMT1',retAr)
                    break
                
                tm.sleep(self.waittime)

        ########CreateHeader
        Header = self.getHeader_1(Chns,Val, VorI, SSR, FL, MChn=SSChn, SChn=PBChn)

        """
        SweepMode = self.getSweepMode(Mmode)
        Header.append('TestParameter,Measurement.Primary.Locus,%s' %(SweepMode[0]))
        Header.append('TestParameter,Measurement.Primary.Scale,%s' %(SweepMode[1]))
        Header.append('TestParameter,Measurement.Primary.Start,%f' %(Mstart))
        Header.append('TestParameter,Measurement.Primary.Stop,%f' %(Mstop))
        Header.append('TestParameter,Measurement.Primary.Step,%f' %(Mstep))
        Header.append('TestParameter,Measurement.Primary.Compliance,%f,%f' %(VComp[Mn], IComp[Mn]))
        if Pcompl[Mn] == None:
            Header.append('TestParameter,Measurement.Primary.PowerCompliance,0')
        else:
            Header.append('TestParameter,Measurement.Primary.PowerCompliance,%f' %(Pcompl[Mn]))
        if AA == 1:
            Header.append('TestParameter,Measurement.Aborting.Condition,CONTINUE AT ANY')
            if AApost == None or AApost == 1:
                Header.append('TestParameter,Measurement.PostOutput.Value, START')
            else:
                Header.append('TestParameter,Measurement.PostOutput.Value, STOP')
        elif AA == 2:
            Header.append('TestParameter,Measurement.Aborting.Condition, ENABLED')
            if AApost == None or AApost == 1:
                Header.append('TestParameter,Measurement.PostOutput.Value, START')
            else:
                Header.append('TestParameter,Measurement.PostOutput.Value, STOP')
        else:
            Header.append('TestParameter,Measurement.Aborting.Condition,CONTINUE AT ANY')
            Header.append('TestParameter,Measurement.PostOutput.Value, START')

        if not SChn == None:
            Header.append('TestParameter,Measurement.Secondary.start,%f' %(Sstart))
            Header.append('TestParameter,Measurement.Secondary.stop,%f' %(Sstop))
            Header.append('TestParameter,Measurement.Secondary.Compliance,%f' %(Compl[Sn]))
            Header.append('TestParameter,Measurement.Secondary.PowerCompliance,%f' %(Pcompl[Sn]))
        
        MonitorHeader = self.getMonitorHeader(Chns, Val, Compl, VorI, ADC, RI, RV, CMM)
        Header.extend(MonitorHeader)

        Header.append('TestParameter,Timing.Hold, %f' %(hold))
        Header.append('TestParameter,Timing.Delay, %f' %(delay))
        if not sdelay == None:
            Header.append('TestParameter,Timing.StepDelay, %f' %(sdelay))
        else:
            Header.append('TestParameter,Timing.StepDelay,')
        if not tdelay == None:
            Header.append('TestParameter,Timing.StepSourceTriggerDelay, %f' %(tdelay))
        else:
            Header.append('TestParameter,Timing.StepSourceTriggerDelay,')
        if not mdelay == None:
            Header.append('TestParameter,Timing.StepMeasurementTriggerDelay, %f' %(mdelay))
        else:
            Header.append('TestParameter,Timing.StepMeasurementTriggerDelay,')
        """
        ADCHeader = self.getADCHeader()
        Header.extend(ADCHeader)

        #self.instWrite("DZ\n")
        self.instWrite("CL\n")
        self.curHeader = Header

        return {'Data': retAr, 'Header': Header}


    ############################################################################################
    # can receive Values for a Quasi Pulsed Spot Measurement if the Channels passed calibration and are installed
    # Chns: Array with Channel Number
    # VorI: Array if I or V are forced contains Binary True for V, False for I
    # SourceChn:    Pulse channel, must be defined within Chns!
    # Val:  Voltage/Current Values
    # PBase: Pulse base current/voltage
    # RV:   Array of ranges for voltage measurement (standard is auto)
    # RI:   Array of ranges for current measurement (standard is auto)
    # Vcomp: Voltage compliance
    # Icomp: Current compliance
    # BDMmode: Measurement mode 
    # BDMinterval: settling detection interval (0: Short, 1: Long)
    # hold:  hold time in sec
    # delay:  delay time in sec
    # FL:   Sets the filter of the specified channels to ON or OFF.
    # SSR:  Series resistance will be applied
    # CMM:  sets the measurement side, 0: compliance side (initial setting), 1: always Voltage side, 2: always Current side, 3: Force side measurement
    # complPolarity: Polarity of voltage comliance, 0: aAuto mode (default), 1: Manual mode, uses compl polarity


    def QuasiPulsedSpotMeasurement(self, Chns, VorI, SourceChn, Val, PBase, RV=None, RI=None, VComp=None, IComp=None, 
                                    BDMmode=None, BDMInterval=None, hold=None, delay=None, 
                                    FL=None, SSR=None, CMM=None, complPolarity=None):

        self.checkListConsistancy([Chns, VorI, Val, VComp, IComp, RV, RI, FL, SSR, CMM], "Quasi Pulsed Spot Measurement")
        if RV == None: RV = [0]*len(Chns)                   # auto voltage range for all active channels
        if RI == None: RI = [0]*len(Chns)                   # auto current range for all active channels
        if VComp == None: VComp = [0]*len(Chns)             # auto compliance for all active channels
        if IComp == None: IComp = [0]*len(Chns)             # auto compliance for all active channels
        if complPolarity == None: complPolarity = [0]*len(Chns)     # auto compliance polarity for all active channels
        if FL == None: FL = [None]*len(Chns)                # don't set the filter for all active channels
        if SSR == None: SSR = [None]*len(Chns)              # don't set the series resistance for all active channels
        if CMM == None: CMM = [None]*len(Chns)              # don't set the channel mode for all active channels
        if Pcompl == None: Pcompl = [None]*len(Chns)        # don't set the Pcompl for all Channels
        if MeasChns == None: MeasChns = Chns                # sets the standard for MeasChn to measure all Chns
        if ADC == None: ADC = [0]*len(Chns)                 #Sets the ADC to High-Speed for all channels
        for chn in Chns:
            self.SMUisAvailable(chn)
            self.SMUisUsed(chn)
        
        #check if all values in VorI are Boolean
        for element in VorI:
            if not isinstance(element, (bool)):
                raise E5274A_InputError("VorI must only contain boolean values")
       
        self.CheckADCValues(Chns, ADC)
        self.CheckRanges(Chns, "Voltage", RV)
        self.CheckRanges(Chns, "Current", RI)
        self.CheckVolCurValues(Chns, VorI, Val, RV, RI)
        self.CheckCompliance(Chns, VorI, Val, IComp, VComp, RV, RI)
        self.CheckFilter(Chns, VorI, FL)
        self.CheckSeriesResistance(Chns, SSR)
        self.CheckChannelMode(Chns, CMM)
        self.checkComplPolarity(Chns, complPolarity)
    
        if BDMInterval != None and BDMmode != None:
            self.checkBDMValues(BDMInterval, BDMmode)
        if hold != None and delay != None:
            self.CheckBDTValues(hold, delay)

        n= 0
        for Chn in Chns: 
            if Chn == SourceChn:
                if VorI[n] == False:
                    raise E5274A_InputError("Quasi Pulsed Spot Measurement - SourceChn must be a Voltage Source.")
                self.CheckBDVValues(PBase, Val[n])
            n = n+1
        n = 0
        """
        for Chn in Chns:
            if Chn == MChn:
                Mn = n
            if Chn == SChn:
                Sn = n
        """

        #self.instWrite("DZ\n")
        self.instWrite("CL\n")

        n=0

        mode = ''

        for n in range(len(Chns)):            
            self.instWrite("CN %d\n" %(Chns[n]))
            
            if not FL[n] == None:
                self.instWrite("FL %d, %d\n" %(FL[n], Chns[n]))

            if not SSR[n] == None:
                self.instWrite("SSR %d, %d\n" %(SSR[n], Chns[n]))


            if not self.is_int(SourceChn): #SourceChn is Source Channel
                raise E5274A_InputError("SourceChn must be an integer between 1 and 8 and be present in Chns.")
            if SourceChn > 8 or SourceChn < 1 or SourceChn not in Chns: 
                raise E5274A_InputError("SourceChn must be an integer between 1 and 8 and be present in Chns.")

            
            if Chns[n] == SourceChn:
                self.instWrite("BDM %d, %d\n" %(BDMInterval, BDMmode))
                if hold != None and delay != None: 
                    self.instWrite("BDT %f, %f\n" %(hold, delay))

                if VorI[n]:
                     self.instWrite("BDV %d, %d, %f, %f, %f\n" %(Chns[n], RV[n], PBase, Val[n], IComp[n]))
                else:
                     self.instWrite("BDI %d, %d, %f, %f, %f\n" %(Chns[n], RI[n], PBase, Val[n], VComp[n]))
                #Val[n] = 0

            if Chns[n] != SourceChn:
                if VorI[n]:  
                    self.instWrite(self.compileDV(Chns[n], RV[n], Val[n], IComp[n], complPolarity[n], RI[n]))
                else:
                    self.instWrite(self.compileDI(Chns[n], RI[n], Val[n], VComp[n], complPolarity[n], RV[n]))
            

            if VorI[n]:
                self.instWrite("RI %d, %d\n" %(Chns[n], RI[n]))
            else: 
                self.instWrite("RV %d, %d\n" %(Chns[n], RV[n]))

            if not CMM[n] == None:
                self.instWrite("CMM %d, %d\n" %(Chns[n], CMM[n]))
            
            if MeasChns[n]:
                mode = "%s, %d" %(mode, Chns[n])
        
        self.instWrite("MM 9, %s\n" %(SourceChn))
        self.instWrite("FMT 1, 1 \n")
        
        if self.execute:
            self.instWrite("XE\n")
            
            stTime = tm.time()
            retAr = []
            while True:
                stb = self.inst.read_stb()
                binStb = self.getBinaryList(stb)
                if ((tm.time() - stTime) > self.timeoutTime):
                    timeOut = True
                    break
                if(binStb[0] ==1):
                    ret = self.instRead()
                    self.label = self.getOutputData(Chns,ret,'FMT1',retAr)
                    break
                
                tm.sleep(self.waittime)

        ########CreateHeader
        Header = self.getHeader_1(Chns, Val, VorI, SSR, FL, MChn=SourceChn)
        Header.insert(0, 'TestParameter,Measurement, Quasi Pulsed Spot Measurement' )

        ADCHeader = self.getADCHeader()
        Header.extend(ADCHeader)

        #self.instWrite("DZ\n")
        self.instWrite("CL\n")

        return {'Data': retAr, 'Header': Header}

    def BinarySearchMeasurement(self):
        self.SMUisAvailable(SMU)

    def LinearSearchMeasurement(self):
        self.SMUisAvailable(SMU)

    def is_int(self, val):
        if type(val) == int:
            return True
        else:
            if val.is_integer():
                return True
            else:
                return False

    def getADCHeader(self):
        ADCHeader = []
        if self.ADC_HS_Mode == 0:
            ADCHeader.append('TestParameter,Measurement.Adc.HighSpeed.Mode,AUTO')
        elif self.ADC_HS_Mode == 0:
            ADCHeader.append('TestParameter,Measurement.Adc.HighSpeed.Mode,MANUAL')
        else:
            ADCHeader.append('TestParameter,Measurement.Adc.HighSpeed.Mode,PLC')
        ADCHeader.append('TestParameter,Measurement.Adc.HighSpeed.Coeff, %d' %(self.ADC_HS_Coef))

        if self.ADC_AutoZero:
            ADCHeader.append('TestParameter,Measurement.Adc.HighResolution.AutoZero, OFF')
        else:
            ADCHeader.append('TestParameter,Measurement.Adc.HighResolution.AutoZero, ON')

        if self.ADC_HR_Mode == 0:
            ADCHeader.append('TestParameter,Measurement.Adc.HighResolution.Mode,AUTO')
        elif self.ADC_HR_Mode == 0:
            ADCHeader.append('TestParameter,Measurement.Adc.HighResolution.Mode,MANUAL')
        else:
            ADCHeader.append('TestParameter,Measurement.Adc.HighResolution.Mode,PLC')

        ADCHeader.append('TestParameter,Measurement.Adc.HighResolution.Coeff, %d' %(self.ADC_HR_Coef))

        return ADCHeader



    def getMonitorHeader(self, Chns, Val, Compl, VorI, ADC, RI, RV, CMM):
        MonitorHeader = []
        MonitorHeader.append('TestParameter,Measurement.Bias.Source')
        MonitorHeader.append('TestParameter,Measurement.Bias.Compliance')
        MonitorHeader.append('TestParameter,Measurement.Unit')
        MonitorHeader.append('TestParameter,Measurement.Adc')
        MonitorHeader.append('TestParameter,Measurement.Measurement')
        MonitorHeader.append('TestParameter,Measurement.RangingMode')
        MonitorHeader.append('TestParameter,Measurement.RangeBoundary')

        m = 0
        for chn in Chns:
            n=0
            MonitorHeader[n] = "%s,%f" %(MonitorHeader[n], Val[m])
            n+=1
            MonitorHeader[n] = "%s,%f" %(MonitorHeader[n], Compl[m])
            n+=1
            MonitorHeader[n] = "%s,SMU%d:%s" %(MonitorHeader[n],chn,self.SMUtype[chn])
            n+=1
            MonitorHeader[n] = "%s,%s" %(MonitorHeader[n], self.getADCtype(ADC[m]))
            n+=1
            MonitorHeader[n] = "%s,%s" %(MonitorHeader[n], self.getMeasurementOperationMode(CMM))
            n+=1
            if VorI[m]:
                MonitorHeader[n] = "%s,%s" %(MonitorHeader[n], self.getCurrentRangeMode())
                n+=1
                MonitorHeader[n] = "%s,%s" %(MonitorHeader[n], self.getCurrentRangeBoundary())
            else:
                MonitorHeader[n] = "%s,%s" %(MonitorHeader[n], self.getVoltageRangeMode())
                n+=1
                MonitorHeader[n] = "%s,%s" %(MonitorHeader[n], self.getCurrentRangeBoundary())
            m+=1

        return MonitorHeader


    def getADCtype(self, ADC):
        ret = 'ERROR: NOT FOUND'
        if ADC == 0 or ADC == None:
            ret = 'HS ADC'
        elif ADC == 1:
            ret = 'HR ADC'
        return ret 
    
    def getMeasurementOperationMode(self, mode):
        ret = 'ERROR: NOT FOUND'
        if mode == 0 or mode == None:
            ret = 'Compliance Side'
        elif mode == 1:
            ret = 'Current'
        elif mode == 2:
            ret = 'Voltage'
        elif mode == 3:
            ret = 'Force Side'
        return ret


    def getSweepMode(self, SweepMode):
        ret = [None]*3
        if SweepMode == 1: 
            ret[0] = 'Single'
            ret[1] = 'LINEAR'
            ret[2] = 'Linear sweep (single stair, start to stop.)'
        elif SweepMode == 2:
            ret[0] = 'Single'
            ret[1] = 'LOG'
            ret[2] = 'Log sweep (single stair, start to stop.)'
        elif SweepMode == 3:
            ret[0] = 'Double'
            ret[1] = 'Linear'
            ret[2] = 'Log sweep (single stair, start to stop.)'
        elif SweepMode == 4:
            ret[0] = 'Double'
            ret[1] = 'Linear'
            ret[2] = 'Log sweep (double stair, start to stop to start.)'
        
        return ret
    
    def getVoltageRangeBoundary(self, n):
        ret = 'ERROR: NOT FOUND'
        n = abs(n)
        if n == 0:
            ret = 'AUTO'
        elif n == 5:
            ret = '0.5V'
        elif n == 50:
            ret = '5V'
        elif n == 20 or n == 11:
            ret = '2V'
        elif n == 200 or n == 12:
            ret = '20V'
        elif n == 400 or n == 13:
            ret = '40V'
        elif n == 1000 or n == 14:
            ret = '100V'
        elif n == 2000 or n == 15:
            ret = '200V'
        return ret
    
    def getVoltageRangeMode(self, n):
        ret = 'ERROR: NOT FOUND'
        if n == 0:
            ret = 'AUTO'
        elif n > 0:
            ret = 'LIMITED'
        elif n < 0:
            ret = 'FIXED'
        return ret
    
    def getCurrentRangeBoundary(self, n):
        ret = 'ERROR: NOT FOUND'
        n = abs(0)
        if n == 0:
            ret = 'AUTO'
        elif n == 8:
            ret = '1pA'
        elif n == 9:
            ret = '10pA'
        elif n == 10:
            ret = '100pA'
        elif n == 11:
            ret = '1nA'
        elif n == 12:
            ret = '10nA'
        elif n == 13:
            ret = '100nA'
        elif n == 14:
            ret = '1uA'
        elif n == 15:
            ret = '10uA'
        elif n == 16:
            ret = '100uA'
        elif n == 17:
            ret = '1mA'
        elif n == 18:
            ret = '10mA'
        elif n == 19:
            ret = '100mA'
        elif n == 20:
            ret = '200mA'
        return ret

    def getCurrentRangeMode(self, n):
        ret = 'ERROR: NOT FOUND'
        if n == 0:
            ret = 'NOT LIMITED'
        elif n > 0:
            ret = 'LIMITED'
        elif n < 0:
            ret = 'FIXED'
        return ret