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
import queue as qu
from Exceptions import *

#8 slot SMU mainframe: 
#8 Medium Power Source Measurement Units (MPSMUs) are isntalled (model #E5281A)
class Agilent_B1500A():

    inst = None
    SMUActive = [True]*10
    SMUUsed = [False]*10
    CMUActive = [True]*10
    CMUUsed = [False]*10
    SCUUUsed = False
    execute = True
    session = None
    printOutput = True
    memoryWrite = False
    timeoutTime = 25 #in sec
    waittime = 0.1 # in sec
    label = []
    HSMOutput = []
    MainFrame = 'B1500A'
    Modules = []
    ModuleDesc = []
    ParameterOutput = []
    VoltageName = ['V1','V2','V3','V4','V5','V6','V7','V8']
    CurrentName = ['I1','I2','I3','I4','I5','I6','I7','I8']
    TimeName = ['T1','T2','T3','T4','T5','T6','T7','T8']
    SMUtype = ['MP']*4
    VR = [5, 50, 20, 200, 400, 1000, 2000, -5, -50, -20, -200, -400, -1000, -2000, 0]
    IR = [11,12,13,14,15,16,17,18,19,20,-11,-12,-13,-14,-15,-16,-17,-18,-19,-20, 0]
    RIlabel = [1e-12, 1e-11, 1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1e-12, 1e-11, 1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, "Auto"]
    RVlabel = [0.5, 5, 2, 20, 40, 100, 200, "Auto"]
    ADC_HS_Mode = 0
    ADC_HR_Mode = 0
    ADC_HS_Coef = 1
    ADC_HR_Coef = 6
    ADC_AutoZero = False
    SMUChns = []
    CMUChns = []
    SPGUChn = []
    SCUUChns = []
    curSCUU = dict()
    NumSMUs = 4
    GPIB = ''
    rm = None
    B1530 = []
    logQueue = qu.Queue()

    # initiate 
    def __init__(self, rm=None, GPIB_adr=None, Device=None, execute=True, reset=True, SCali=False, SDiag=False, SMUChns=None, CMUChns=None, printOutput=False):
        
        self.printOutput = printOutput
 
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
        if ret.strip() == "Agilent Technologies,B1500A,0,A.05.50.2013.0417\r\n".strip() or ret.strip() ==  "Agilent Technologies,B1500A,0,A.04.10.2010.0531".strip():
            self.write("You are using the %s" %(ret[:-2]))
        else:
            SystemError("You are using the wrong agilent tool!")

            #exit("You are using the wrong agilent tool!")
        #print(ret)
        # do if Agilent\sTechnologies,E5270A,0,A.01.05\r\n then correct, else the agilent tool you are using is incorrect
        
        self.instWrite("UNT? 0\n")
        tm.sleep(0.1)
        ret = self.instRead()
        modules = ret.strip().split(';')

        n=1
        self.SMUChns = []
        self.CMUChns = []
        
        for module in modules:
            module = module.split(',')[0]

            self.Modules.append(module)
            if module == "B1511A" or module == "B1511B":
                self.SMUChns.append(n)
                self.ModuleDesc.append("MPSMU")
            elif module == "B1510A":
                self.SMUChns.append(n)
                self.ModuleDesc.append("HPSMU")
            elif module == "B1514A":
                self.SMUChns.append(n)
                self.ModuleDesc.append("MCSMU")
            elif module =="B1517A":
                self.SMUChns.append(n)
                self.ModuleDesc.append("HRSMU")
            elif module =="B1517A/E5288A":
                self.SMUChns.append(n)
                self.ModuleDesc.append("HRSMU/ASU")
            elif module == "B1530A":
                self.B1530.append(n)
                self.ModuleDesc.append("WGFMU")
            elif module == "B1520A":
                self.CMUChns.append(n)
                self.ModuleDesc.append("MFCMU")
            elif module == "B1525A":
                self.SPGUChn.append(n)
                self.ModuleDesc.append("HVSPGU")
            elif module == "B1520A/N1301A":
                self.CMUChns.append(n)
                self.SCUUChns.append(n)
                self.curSCUU[n] = None
                self.ModuleDesc.append("MFCMU/SCUU")
            else:
                self.ModuleDesc.append(None)
            n+=1

        self.write("%d SMUs are available." %(len(self.SMUChns)))
        self.write("%d CMUs are available." %(len(self.CMUChns)))
        if len(self.SCUUChns) > 0:  
            self.write("SCUU is installed in Channel/s %s." %(",".join(str(x) for x in self.SCUUChns)))
        
        self.execute = execute
        self.Reset = reset # Reset
        tm.sleep(0.1) 
            
        #self.SMUActive = [True]*len(self.SMUChns)
        #self.SMUUsed = [False]*len(self.SMUChns)
        
        # Run for all 8 SMUs
        reset = False
        if reset:
            m = 0 
            for n in self.SMUChns:
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
            for n in self.CMUChns:
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
                    self.CMUActive[m] = True
                    self.write("CMU %d is available." %(m+1))
                else:
                    self.write("CMU %d is not available." %(m+1))
                m+=1

        # Self Calibration Testing
        if SCali:
            self.write("Running Self Calibration...")
            self.SelfCalibration()
            self.write("Self Calibration finished!")
        
        # Runs Diagnostic Testing
        #if SDiag:
        
        self.instWrite('FMT 1,1')
        self.inst.timeout=150000
        self.session = self.inst.session

    def finishMeasurement(self):
        None
    def resetSCUU(self):
        for key in self.curSCUU.keys():
            self.curSCUU[key] = None
    
    def setSMUSCUU(self, slot=None):
        return None
        if slot == None:
            for slot in self.SCUUChns:

                self.instWrite('SSP %d, 3' %(slot))
                self.curSCUU[slot] = 3
        else:
            if slot in self.SCUUChns:
                self.instWrite('SSP %d, 3' %(slot))
                self.curSCUU[slot] = 3

    def setCMUSCUU(self, slot=None):
        return None
        if slot == None:
            for slot in self.SCUUChns:

                self.instWrite('SSP %d, 4' %(slot))
                self.curSCUU[slot] = 4
        else:
            if slot in self.SCUUChns:
                self.instWrite('SSP %d, 4' %(slot))
                self.curSCUU[slot] = 4

    def setAutoSCUU(self, slots):
        return None
        if not isinstance(slots, list):
            slots = [slots]

        for slot in slots:

            if self.SCUUChns == []:
                continue

            if slot in self.SCUUChns:
                self.curSCUU[slot] == 4
                continue 
            
            elif slot + 1 in self.SCUUChns:

                if self.curSCUU[slot + 1] == 4:
                    raise B1500A_InputError("SMU in slot %d is not available when performing capacitive measurments.")
                elif self.curSCUU[slot + 1] == 2:
                    self.instWrite('SSP %d, 3' %(slot + 1))
                    self.curSCUU[slot + 1] = 3
                else:
                    self.instWrite('SSP %d, 1' %(slot + 1))
                    self.curSCUU[slot + 1] = 1

            elif slot + 2 in self.SCUUChns:
                if self.curSCUU[slot + 2] == 4:
                    raise B1500A_InputError("SMU in slot %d is not available when performing capacitive measurments.")
                elif self.curSCUU[slot + 2] == 1:
                    self.instWrite('SSP %d, 3' %(slot + 2))
                    self.curSCUU[slot + 2] = 3
                else:
                    self.instWrite('SSP %d, 2' %(slot + 2))
                    self.curSCUU[slot + 2] = 2

        return True
            
    def getModuleDesc(self):
        return self.ModuleDesc
    
    def getSMUDescriptions(self):
        Desc = dict()
        for smu in self.SMUChns:
            Desc[smu] = self.ModuleDesc[smu-1]
        return Desc

    def getNumberOfSMU(self):
        return sum(self.SMUActive)

    def getSMUpositions(self):
        return self.SMUChns

    def getStatus(self):
        if self.inst == None:
            return -1
        return 0

    def getB1530channels(self):
        ret = []
        for entry in self.B1530:
            ret.append(entry*100+1)
            ret.append(entry*100+2)
        return ret

    def turnOnline(self):
        try:
            self.inst = self.rm.open_resource(self.GPIB)
        except:
            self.write("The device %s does not exist." %(self.GPIB))  #maybe a problem, tranmitting None type

    def turnOffline(self):
        self.SMUChns = []
        self.CMUChns = []
        self.SPGUChn = []
        self.B1500 = None
        self.inst.clear()
        self.inst.close()

    def clear(self):
        self.inst.clear()

    def getMeasureStatus(self):

        return {'TotalTime': 0, 'Percentage': 0, 'CompletedTime': 0}

    def instWrite(self, command):
        self.inst.write(command)
        if self.printOutput:
            self.write("Write: %s" %(command))
        stb = self.inst.read_stb()
        binStb = self.getBinaryList(stb)
        err = binStb[5]
        if err == 1:
            ret = self.inst.query("ERR? 1\n")
            try:
                ret = int(ret)
                raise B1500A_InputError("Error #%s." %(ret))
            except TypeError:
                ret.strip()
                
            raise B1500AError("Error #%s." %(ret))

    def instRead(self):
        ret = self.inst.read()
        if self.printOutput:
            self.write("Read")
        return ret
    
    def instQuery(self, command):
        ret = self.inst.query(command)
        if self.printOutput:
            self.write("Query: %s" %(command))
        stb = self.inst.read_stb()
        binStb = self.getBinaryList(stb)
        err = binStb[5]
        if err == 1:
            ret = self.inst.query("ERR? 1\n")
            raise SyntaxError("B1500 encountered error #%d." %(ret.strip()))
        return ret

    def getChnsfromSMU(self, SMUs):
        if isinstance(SMUs, type([])):
            chns = []
            for SMU in SMUs:
                chns.append(self.SMUChns[SMU-1])
        elif isinstance(SMUs, int):
            chns = self.SMUChns[SMUs-1]
        else:
            raise B1500A_InputError("SMU's must be a list of integers or integers.")
        return chns
 
    def getChnsfromCMU(self, CMUs):
        if isinstance(CMUs, type([])):
            chns = []
            for CMU in CMUs:
                chns.append(self.CMUChns[CMU-1])
        elif isinstance(CMUs, int):
            chns = self.CMUChns[CMUs-1]
        else:
            raise B1500A_InputError("CMU's must be a list of integers or integers.")
        return chns
    
    def reset(self):
        self.instWrite("*CLS")
        self.instWrite("*RST")

    def resetOutput(self, SMUs):
        
        Chns = self.getChnNumFromSMUnum(SMUs)
        string = "DZ"
        for chn in Chns:
            string = "%s, %d" %(string, chn)
        string = "%s\n"
        
        self.inst.write(string)

    def setDirectExecute(self):
        self.execute = True
    
    def setRemoteExecute(self):
        self.execute = False
    
    def remoteExecute(self):
        if not self.execute:
            self.instWrite("XE\n")

    def getLogQueue(self):
        return self.logQueue

    def CloseInstrument(self):
        self.inst.close()

    def write(self, txt):
        if self.printOutput:
            msg = "B1500A - %s: %s" %(self.GPIB, txt)
            self.logQueue.put(msg)
            print(msg)
            
   
    def initialize(self):
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

        error = 0

        for n in self.SMUChns:
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

            try: 
                ret = int(ret)
            except ValueError as e:
                self.write("Error encountered in SMU%s of B1500: %s." %(n, e))
                error = error + 1
                continue

            if int(ret) == 0: 
                self.SMUActive[m] = True
                self.write("SMU %d is available." %(m+1))
            else:
                self.write("SMU %d is not available." %(m+1))
                error = error +1
            m+=1

        for n in self.CMUChns:
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
            
            try: 
                ret = int(ret)
            except ValueError as e:
                self.write("Error encountered in SMU%s of B1500: %s." %(n, e))
                error = error + 1

            if int(ret) == 0: 
                self.CMUActive[m] = True
                self.write("CMU %d is available." %(m+1))
            else:
                self.write("CMU %d is not available." %(m+1))
                error = error +1
            m+=1

        return error

    def SMUisAvailable(self, SMUNum):
        if True == self.SMUActive[SMUNum]:
            return True
        raise B1500A_InputError("SMU %d is not available." %(SMUNum))
        
    def SMUisUsed(self, SMUNum):
        if False == self.SMUUsed[SMUNum]:
            return False
        raise B1500A_InputError("CMU %d is used." %(SMUNum))

    def CMUisAvailable(self, CMUNum):
        if True == self.CMUActive[CMUNum]:
            return True
        raise B1500A_InputError("CMU %d is not available." %(CMUNum))
        
    def CMUisUsed(self, CMUNum):
        if False == self.CMUUsed[CMUNum]:
            return False
        raise B1500A_InputError("CMU %d is used." %(CMUNum))


    def performCalibration(self):
        self.SelfCalibration()

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
            if self.printOutput:
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
                    raise B1500A_InputError("Input Values for %s do not have the right dimensions" %(desc))
    
    #check if hold and delay are within allowed ranges
    def CheckDelays(self, hold, delay):
        holdMax = 655.35
        delayMax = 65535

        if hold != None:
            if not isinstance(hold, (int,float)):
                raise B1500A_InputError("Hold Time not float or int.")
            if hold < 0 or hold > holdMax: 
                raise B1500A_InputError("Hold Time must be between 0 and %f." %(holdMax))

        if delay != None:
            if not isinstance(delay, (int,float)):
                raise B1500A_InputError("Delay Time not float or int.")
            if delay < 0 or delay > holdMax: 
                raise B1500A_InputError("Delay Time must be between 0 and %f." %(delayMax))

    #check ranges for 5281A MPSMU if all values in RR are allowed ranges
    def CheckRanges(self, Chns, VorI, Range):
        n=0
        VR = [0, 5, 50, 20, 200, 400, 1000, 2000, -5, -50, -20, -200, -400, -1000, -2000]
        IR = [0,11,12,13,14,15,16,17,18,19,20,-11,-12,-13,-14,-15,-16,-17,-18,-19,-20]
        
        if VorI == "Voltage":
            for element in Range:
                if  element not in VR:
                    raise B1500A_InputError("Voltage Range for Channel %d is not valid." %(Chns[n]))
                n+=1
        elif VorI == "Current":
            for element in Range:
                if element not in IR:
                    raise B1500A_InputError("Current Range for Channel %d is not valid." %(Chns[n]))
                n+=1
        else:
            raise B1500A_InputError("CheckRanges only compares 'Voltage' or 'Current'.")

    #check ranges for 5281A MPSMU if all values in Val are allowed voltages/currents
    def CheckVolCurValues(self, Chns, VorI, Val, RV, RI):
        n=0
        
        VR = self.VR
        IR = self.IR
        
        for element in Val:
            if VorI[n]:    
                if RV[n] == VR[0]:
                    if np.absolute(int(element)) > 42:
                        raise B1500A_InputError("Voltage for Voltage range %d in Channel %d is above 42V." %(RV[n], Chns[n]))
                if RV[n] == VR[1] or RV[n] == VR[8]:
                    if np.absolute(int(element)) > 0.5:
                        raise B1500A_InputError("Voltage for Voltage range %d in Channel %d is above 0.5V." %(RV[n], Chns[n]))
                if RV[n] == VR[2] or RV[n] == VR[9]:
                    if np.absolute(int(element)) > 5:
                        raise B1500A_InputError("Voltage for Voltage range %d in Channel %d is above 5V." %(RV[n], Chns[n]))
                if RV[n] == VR[3] or RV[n] == VR[10]:
                    if np.absolute(int(element)) > 2:
                        raise B1500A_InputError("Voltage for Voltage range %d in Channel %d is above 2V." %(RV[n], Chns[n]))
                if RV[n] == VR[4] or RV[n] == VR[11]:
                    if np.absolute(int(element)) > 20:
                        raise B1500A_InputError("Voltage for Voltage range %d in Channel %d is above 20V." %(RV[n], Chns[n]))
                if RV[n] == VR[5] or RV[n] == VR[12]:
                    if np.absolute(int(element)) > 40:
                        raise B1500A_InputError("Voltage for Voltage range %d in Channel %d is above 40V." %(RV[n], Chns[n]))
                if RV[n] == VR[6] or RV[n] == VR[13]:
                    if np.absolute(int(element)) > 100:
                        raise B1500A_InputError("Voltage for Voltage range %d in Channel %d is above 42V." %(RV[n], Chns[n]))
                if RV[n] == VR[7] or RV[n] == VR[14]:
                    if np.absolute(int(element)) > 200:
                        raise B1500A_InputError("Voltage for Voltage range %d in Channel %d is above 42V." %(RV[n], Chns[n]))
            n+=1

        n=0
        for element in Val:
            if VorI[n] == False:
                if RI[n] == IR[0]:
                    if np.absolute(int(element)) > 0.2:
                        raise B1500A_InputError("Current for Current range %d in Channel %d is above 200 mA." %(RI[n], Chns[n]))
                if RI[n] == IR[1] or RI[n] == IR[11]:
                    if np.absolute(int(element)) > 1.15e-9:
                        raise B1500A_InputError("Current for Current range %d in Channel %d is above 1.15 nA." %(RI[n], Chns[n]))
                if RI[n] == IR[2] or RI[n] == IR[12]:
                    if np.absolute(int(element)) > 11.5e-9:
                        raise B1500A_InputError("Current for Current range %d in Channel %d is above 11.5 nA." %(RI[n], Chns[n]))
                if RI[n] == IR[3] or RI[n] == IR[13]:
                    if np.absolute(int(element)) > 115e-9:
                        raise B1500A_InputError("Current for Current range %d in Channel %d is above 115 nA." %(RI[n], Chns[n]))
                if RI[n] == IR[4] or RI[n] == IR[14]:
                    if np.absolute(int(element)) > 1.15e-6:
                        raise B1500A_InputError("Current for Current range %d in Channel %d is above 1.15 uA." %(RI[n], Chns[n]))
                if RI[n] == IR[5] or RI[n] == IR[15]:
                    if np.absolute(int(element)) > 11.5e-6:
                        raise B1500A_InputError("Current for Current range %d in Channel %d is above 11.5 uA." %(RI[n], Chns[n]))
                if RI[n] == IR[6] or RI[n] == IR[16]:
                    if np.absolute(int(element)) > 115e-6:
                        raise B1500A_InputError("Current for Current range %d in Channel %d is above 115 uA." %(RI[n], Chns[n]))
                if RI[n] == IR[7] or RI[n] == IR[17]:
                    if np.absolute(int(element)) > 1.15e-3:
                        raise B1500A_InputError("Current for Current range %d in Channel %d is above 1.15 mA." %(RI[n], Chns[n]))
                if RI[n] == IR[8] or RI[n] == IR[18]:
                    if np.absolute(int(element)) > 11.5e-3:
                        raise B1500A_InputError("Current for Current range %d in Channel %d is above 11.5 mA." %(RI[n], Chns[n]))
                if RI[n] == IR[9] or RI[n] == IR[19]:
                    if np.absolute(int(element)) > 115e-3:
                        raise B1500A_InputError("Current for Current range %d in Channel %d is above 115 mA." %(RI[n], Chns[n]))
                if RI[n] == IR[10] or RI[n] == IR[20]:
                    if np.absolute(int(element)) > 200e-3:
                        raise B1500A_InputError("Current for Current range %d in Channel %d is above 200 mA." %(RI[n], Chns[n]))
            n+=1
    
    def CheckCMUValues(self, freq, Vac, mode, Vdc=None):

        if not isinstance(freq, (int,float)):
            raise B1500A_InputError("Frequency for the Capacitace measurement must be float value from 1kHz to 5MHz in Hz.")
        if 1000 > freq > 5e6:
            raise B1500A_InputError("Frequency for the Capacitace measurement must be float value from 1kHz to 5MHz in Hz.")

        if not isinstance(Vac, (int,float)):
            raise B1500A_InputError("Oscillator level of the output AC voltage for the Capacitace measurement must be 0 mV to 250 mV in V.")
        if 0 > Vac > 0.25:
            raise B1500A_InputError("Oscillator level of the output AC voltage for the Capacitace measurement must be 0 mV to 250 mV in V.")
        if Vdc != None:
            if not isinstance(Vdc, (int,float)):
                raise B1500A_InputError("DC voltage for Capacitive Measurement must be between -100 to +100V in V.")
            if -100 > Vdc > 100:
                raise B1500A_InputError("DC voltage for Capacitive Measurement must be between -100 to +100V in V.")

            modes = [1,2,10,11,20,21,100,101,102,103,200,201,202,300,301,302,303,400,401,402]

        if not isinstance(mode, (int,type(None))):
            raise B1500A_InputError("CMU Measurement mode must be 1,2,10,11,20,21,100,101,102,103,200,201,202,300,301,302,303,400,401 or 402.")
        if mode != None:
            if not mode in modes:
                raise B1500A_InputError("CMU Measurement mode must be 1,2,10,11,20,21,100,101,102,103,200,201,202,300,301,302,303,400,401 or 402.")

    def CheckCompliance(self, Chns, VorI, Val, IComp, VComp, RV, RI):
        n=0
        VR = self.VR
        IR = self.IR
        
        #if np.any(IComp) == 0:
        #    raise B1500A_InputError("Current Compliance can't be 0")
        #if np.any(VComp) == 0:
        #    raise B1500A_InputError("Voltage Compliance can't be 0")

        for element in IComp:
            if VorI[n]:
                if RV[n] == VR[0]:
                    if np.absolute(Val[n]) <= 42:
                        if np.absolute(int(element)) > 100e-3:
                            raise B1500A_InputError("Current Compliance for Voltage range %d in Channel %d is not less than or equal to 100e-3 A." %(RV[n], Chns[n]))
                    else:
                        raise B1500A_InputError(">42 not supported with a Current Measurement Range of %s " %(self.RVlabel[RV[n]]))
                if RV[n] == VR[1] or RV[n] == VR[8]:
                    if np.absolute(Val[n]) <= 0.5:
                        if np.absolute(int(element)) > 100e-3:
                            raise B1500A_InputError("Current Compliance for Voltage range %d in Channel %d is not less than or equal to 100e-3 A." %(RV[n], Chns[n]))
                    else:
                        raise B1500A_InputError(">0.5 not supported with a Current Measurement Range of %s " %(self.RVlabel[RV[n]]))
                if RV[n] == VR[2] or RV[n] == VR[9]:
                    if np.absolute(Val[n]) <= 5:
                        if np.absolute(int(element)) > 100e-3:
                            raise B1500A_InputError("Current Compliance for Voltage range %d in Channel %d is not less than or equal to 100e-3 A." %(RV[n], Chns[n]))
                    else:
                        raise B1500A_InputError(">5 not supported with a Current Measurement Range of %s " %(self.RVlabel[RV[n]]))
                if RV[n] == VR[3] or RV[n] == VR[10]:
                    if np.absolute(Val[n]) <= 2:
                        if np.absolute(int(element)) > 100e-3:
                            raise B1500A_InputError("Current Compliance for Voltage range %d in Channel %d is not less than or equal to 100e-3 A." %(RV[n], Chns[n]))
                    else:
                        raise B1500A_InputError(">2 not supported with a Current Measurement Range of %s " %(self.RVlabel[RV[n]]))
                if RV[n] == VR[4] or RV[n] == VR[11]:
                    if np.absolute(Val[n]) <= 20:
                        if np.absolute(int(element)) > 100e-3:
                            raise B1500A_InputError("Current Compliance for Voltage range %d in Channel %d is not less than or equal to 100e-3 A." %(RV[n], Chns[n]))
                    else:
                        raise B1500A_InputError(">20 not supported with a Current Measurement Range of %s " %(self.RVlabel[RV[n]]))
                if RV[n] == VR[5] or RV[n] == VR[12]:
                    if np.absolute(Val[n]) <= 20:
                        if np.absolute(int(element)) > 100e-3:
                            raise B1500A_InputError("Current Compliance for Voltage range %d in Channel %d is not less than or equal to 100e-3 A." %(RV[n], Chns[n]))
                    elif np.absolute(Val[n]) <= 40:
                        if np.absolute(int(element)) > 50e-3:
                            raise B1500A_InputError("Current Compliance for Voltage range %d in Channel %d is not less than or equal to 50e-3 A." %(RV[n], Chns[n]))
                    else:
                        raise B1500A_InputError(">20 not supported with a Current Measurement Range of %s." %(self.RVlabel[RV[n]]))
                if RV[n] == VR[6] or RV[n] == VR[13]:
                    if np.absolute(Val[n]) <= 20:
                        if np.absolute(int(element)) > 100e-3:
                            raise B1500A_InputError("Current Compliance for Voltage range %d in Channel %d is not less than or equal to 100e-3 A." %(RV[n], Chns[n]))
                    elif np.absolute(Val[n]) <= 40:
                        if np.absolute(int(element)) > 50e-3:
                            raise B1500A_InputError("Current Compliance for Voltage range %d in Channel %d is not less than or equal to 50e-3 A." %(RV[n], Chns[n]))
                    elif np.absolute(Val[n]) <= 100:
                        if np.absolute(int(element)) > 20e-3:
                            raise B1500A_InputError("Current Compliance for Voltage range %d in Channel %d is not less than or equal to 20e-3 A." %(RV[n], Chns[n]))
                    else:
                        raise B1500A_InputError(">100V not supported with a Current Measurement Range of %s." %(self.RVlabel[RV[n]]))
                if RV[n] == VR[7] or RV[n] == VR[14]:
                    if np.absolute(Val[n]) < 200:
                        if np.absolute(int(element)) > 100e-3:
                            raise B1500A_InputError("Current Compliance for Voltage range %d in Channel %d is not 2e-3 A." %(RV[n], Chns[n]))
                    else:
                        raise B1500A_InputError("Incorrect Voltage Compliance Used (200V Output range won't work)!")
                    
            n+=1

        n=0

        for element in VComp:

            if not VorI[n]:
                if RI[n] == IR[0]:
                    if np.absolute(Val[n]) <= 0.2:
                        if np.absolute(int(element)) > 100:
                            raise B1500A_InputError("Voltage Compliance for Current range %d in Channel %d is not less than or equal to 100V." %(RI[n], Chns[n]))
                    else:
                        raise B1500A_InputError(">1A not supported with a Current Measurement Range of %s " %(self.RIlabel[RI[n]]))
                if RI[n] == IR[1] or RI[n] == IR[11]:
                    if np.absolute(Val[n]) <= 1.15e-9:
                        if np.absolute(int(element)) > 100:
                            raise B1500A_InputError("Voltage Compliance for Current range %d in Channel %d is not less than or equal to 100V." %(RI[n], Chns[n]))
                    else:
                        raise B1500A_InputError(">1.15e-9A not supported with a Current Measurement Range of %s " %(self.RIlabel[RI[n]]))
                if RI[n] == IR[2] or RI[n] == IR[12]:
                    if np.absolute(Val[n]) <= 11.5e-9:
                        if np.absolute(int(element)) > 100:
                            raise B1500A_InputError("Voltage Compliance for Current range %d in Channel %d is not less than or equal to 100V." %(RI[n], Chns[n]))
                    else:
                        raise B1500A_InputError(">11.5e-9A not supported with a Current Measurement Range of %s " %(self.RIlabel[RI[n]]))
                if RI[n] == IR[3] or RI[n] == IR[13]:
                    if np.absolute(Val[n]) <= 115e-9:
                        if np.absolute(int(element)) > 100:
                            raise B1500A_InputError("Voltage Compliance for Current range %d in Channel %d is not less than or equal to 100V." %(RI[n], Chns[n]))
                    else:
                        raise B1500A_InputError(">115e-9A not supported with a Current Measurement Range of %s " %(self.RIlabel[RI[n]]))
                if RI[n] == IR[4] or RI[n] == IR[14]:
                    if np.absolute(Val[n]) <= 1.15e-6:
                        if np.absolute(int(element)) > 100:
                            raise B1500A_InputError("Voltage Compliance for Current range %d in Channel %d is not less than or equal to 100V." %(RI[n], Chns[n]))
                    else:
                        raise B1500A_InputError(">1.15e-6A not supported with a Current Measurement Range of %s " %(self.RIlabel[RI[n]]))
                if RI[n] == IR[5] or RI[n] == IR[15]:
                    if np.absolute(Val[n]) <= 11.5e-6:
                        if np.absolute(int(element)) > 100:
                            raise B1500A_InputError("Voltage Compliance for Current range %d in Channel %d is not less than or equal to 100V." %(RI[n], Chns[n]))
                    else:
                        raise B1500A_InputError(">11.5e-6A not supported with a Current Measurement Range of %s " %(self.RIlabel[RI[n]]))
                if RI[n] == IR[6] or RI[n] == IR[16]:
                    if np.absolute(Val[n]) <= 115e-6:
                        if np.absolute(int(element)) > 100:
                            raise B1500A_InputError("Voltage Compliance for Current range %d in Channel %d is not less than or equal to 100V." %(RI[n], Chns[n]))
                    else:
                        raise B1500A_InputError(">115e-6A not supported with a Current Measurement Range of %s " %(self.RIlabel[RI[n]]))
                if RI[n] == IR[7] or RI[n] == IR[17]:
                    if np.absolute(Val[n]) <= 1.15e-3:
                        if np.absolute(int(element)) > 100:
                            raise B1500A_InputError("Voltage Compliance for Current range %d in Channel %d is not less than or equal to 100V." %(RI[n], Chns[n]))
                    else:
                        raise B1500A_InputError(">1.15e-3A not supported with a Current Measurement Range of %s " %(self.RIlabel[RI[n]]))
                if RI[n] == IR[8] or RI[n] == IR[18]:
                    if np.absolute(Val[n]) <= 11.5e-3:
                        if np.absolute(int(element)) > 100:
                            raise B1500A_InputError("Voltage Compliance for Current range %d in Channel %d is not less than or equal to 100V." %(RI[n], Chns[n]))
                    else:
                        raise B1500A_InputError(">11.5e-3A not supported with a Current Measurement Range of %s " %(self.RIlabel[RI[n]]))
                if RI[n] == IR[9] or RI[n] == IR[19]:
                    if np.absolute(Val[n]) <= 20e-3:
                        if np.absolute(int(element)) > 100:
                            raise B1500A_InputError("Voltage Compliance for Current range %d in Channel %d is not less than or equal to 100V." %(RI[n], Chns[n]))
                    if np.absolute(Val[n]) <= 50e-3:
                        if np.absolute(int(element)) > 40:
                            raise B1500A_InputError("Voltage Compliance for Current range %d in Channel %d is not less than or equal to 40V." %(RI[n], Chns[n]))
                    if np.absolute(Val[n]) <= 115e-3:
                        if np.absolute(int(element)) > 20:
                            raise B1500A_InputError("Voltage Compliance for Current range %d in Channel %d is not less than or equal to 20V." %(RI[n], Chns[n]))
                    else:
                        raise B1500A_InputError(">115e-3A not supported with a Current Measurement Range of %s " %(self.RIlabel[RI[n]]))
                if RI[n] == IR[10] or RI[n] == IR[20]:
                    if np.absolute(Val[n]) > 200:
                        if np.absolute(int(element)) != 100000:
                            raise B1500A_InputError("Voltage Compliance for Current range %d in Channel %d is not 100000V." %(RI[n], Chns[n]))
                    else:
                        raise B1500A_InputError("Incorrect Current Compliance Used (Above 100mA Output range won't work)!")

            n=+1


    # check the filter that can be applied to each SMU
    def CheckFilter(self, Chns, VorI, FL):
        n = 0
        if not isinstance(FL, type([])):
            raise TypeError("The Filter mode must be a list of 0 or 1.")

        for chn in Chns: 
            if not isinstance(FL[n], (int, type(None))):
                raise TypeError("The Filter mode for Channel %d must be 0, 1 or 'None'." %(Chns[n]))
            
            if not (FL[n] == 0 or FL[n] == 1 or FL[n] == None):
                raise B1500A_InputError("The Filter mode for Channel %d must be 0, 1 or 'None'." %(Chns[n]))
            n+=1

    def CheckChannelMode(self, Chns, CMM):
        n = 0
        for chn in Chns:
            if not isinstance(CMM[n], (int,type(None))):
                raise B1500A_InputError("The Channel mode for Channel %d must be 0, 1, 2, 3 or None." %(Chns[n]))
            if not CMM[n] == None: 
                if not (CMM[n] < 3 or CMM[n] > 0):
                    raise B1500A_InputError("The Channel mode for Channel %d must be 0, 1, 2, 3 or None." %(Chns[n]))
            n+=1

    def CheckSeriesResistance(self, Chns, SSR):

        for n in range(len(Chns)):
            
            if not isinstance(SSR[n], (int, type(None))):
                raise B1500A_InputError("The Series Resistor connection for Channel %d must be 0, 1 or None." %(Chns[n]))
            if not SSR[n] == None: 
                if not (SSR[n] < 3 or SSR[n] > 0):
                    raise B1500A_InputError("The Series Resistor connection for Channel %d must be 0, 1 or None." %(Chns[n]))

    def CheckADCValues(self, chns, ADCs):
        for n in range(len(chns)):
            if not isinstance(ADCs[n], int) and not ADCs[n] == None:
                raise B1500A_InputError("The ADC converter type of Channel %d must be either 0 (High-Speed) or 1 (High-resolution" %(chns[n]))
            if not (ADCs[n] == 0 or ADCs[n] == 1 or ADCs[n] == None):
                raise B1500A_InputError("The ADC converter type of Channel %d must be either 0 (High-Speed) or 1 (High-resolution" %(chns[n]))
            
    #Adjust ADC Converter setting for High-Speed and High-Resolution
    #See E5260 Manual page 206 and command 'AIT' for more details
    def SetADCConverter(self, ADC, mode, N=None):
        if not isinstance(ADC, int):
            raise B1500A_InputError("The ADC converter type must be either 0 (High-Speed) or 1 (High-resolution")
        if not (ADC == 0 or ADC == 1):
            raise B1500A_InputError("The ADC converter type must be either 0 (High-Speed) or 1 (High-resolution")
        if not isinstance(mode, int):
            raise B1500A_InputError("ADC operation mode must be 0 (auto) or 1 (manual) or 2 (PLC mode)")
        if not (mode == 0 or mode == 1 or mode == 2):
            raise B1500A_InputError("ADC operation mode must be 0 (auto) or 1 (manual) or 2 (PLC mode)")
        if not isinstance(N, int):
            raise B1500A_InputError("AV number must be 1 to 1023 or -1 to -100")
        if ADC == 0 and mode == 0:
            if (N > 1023 or N < 1):
                raise B1500A_InputError("(HighSpeed ADC/AutoMode) Number of averaging samples must be between 1 to 1023")
        if ADC == 0 and mode == 1:
            if (N > 1023 or N < 1):
                raise B1500A_InputError("(HighSpeed ADC/ManualMode) Number of averaging samples must be between 1 to 1023")
        if ADC == 0 and mode == 2:
            if (N > 100 or N < 1):
                raise B1500A_InputError("(HighSpeed ADC/PLCmode) Number of averaging samples must be between 1 to 100")
        if ADC == 1 and mode == 0:
            if (N > 127 or N < 1):
                raise B1500A_InputError("(HighResolution ADC/AutoMode) Number of averaging samples must be between 1 to 127 (default=6)")
        if ADC == 1 and mode == 1:
            if (N > 127 or N < 1):
                raise B1500A_InputError("(HighResolution ADC/ManualMode) Number of averaging samples must be between 1 to 127")
        if ADC == 1 and mode == 2:
            if (N > 100 or N < 1):
                raise B1500A_InputError("(HighResolution ADC/PLCmode) Number of averaging samples must be between 1 to 100")

        if ADC == 0: 
            self.ADC_HS_Mode = mode
            self.ADC_HS_Coef = N
        elif ADC == 1:
            self.ADC_HR_Mode = mode
            self.ADC_HR_Coef = N

        if N == None:
            self.instWrite("AIT %d, %d\n" %(ADC, mode))
            self.write("AIT %d, %d" %(ADC, mode))
        else:
            self.instWrite("AIT %d, %d, %d\n"%(ADC, mode, N))
            self.write("AIT %d, %d, %d"%(ADC, mode, N))
    
    #assign either High-Speed (0) or High-Resolution (1) ADC to a smu
    def SetADC(self, ADC, SMU):
        
        if not isinstance(ADC, int):
            raise B1500A_InputError("The ADC converter type must be either 0 (High-Speed) or 1 (High-resolution")
        if not (ADC == 0 or ADC == 1):
            raise B1500A_InputError("The ADC converter type must be either 0 (High-Speed) or 1 (High-resolution")
        
        if not isinstance(SMU, int):
            raise B1500A_InputError("The Channel number must be an integer between 1 and 10.")
        if 1 > SMU > 10:
            raise B1500A_InputError("The Channel number must be an integer between 1 and 10.")

        chn = self.getChnNumFromSMUnum(SMU)[0]
        if ADC != None:
            self.instWrite("AAD %d, %d\n" %(chn,ADC))
            self.write("AAD %d, %d" %(chn,ADC))
        
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
                raise B1500A_InputError("VM must only contain boolean values")
        for element in IM:
            if not isinstance(element, (bool)):
                raise B1500A_InputError("IM must only contain boolean values")
        for n in range(len(VM)):
            if not VM[n] and not IM[n]:
                raise B1500A_InputError("At least one VM or IM must be True")

    def CheckPulseParamSMU(self, hold, width, period, delay):
        if isinstance(hold, (float, int)):
            if hold < 0 or hold > 655.35:
                raise B1500A_InputError("Hold time must be within 0 to 655.35 sec.")
        else:
                raise B1500A_InputError("Hold time must be a float value from 0 to 655.35 sec.")

        if isinstance(width, (float, int)):
            if width < 5e-4 or width > 2:
                raise B1500A_InputError("Pulse width must be within 0 to 2 sec.")
        else:
            raise B1500A_InputError("Pulse width must be a float value from 0 to 2 sec.")
        
        if isinstance(period, (float, int, type(None))):
            if not (period == 0 or period == None or (period > 5e-3 and period < 5)):
                raise B1500A_InputError("Pulse period must be either 0 (automatic setting) or between 0.5ms to 5s.")
        else:
            raise B1500A_InputError("Pulse period must be a float value, either 0 (automatic setting) or between 0.5ms to 5s.")
        
        if width <= 0.1 and period != None:
            if period < (np.add(width,2e-3)):
               raise B1500A_InputError("Period must be larger than width+2ms (for width <= 100ms)") 
        elif width > 0.1:
            if period < (np.add(width,10e-3)):
               raise B1500A_InputError("Period must be larger than width+10ms (for width > 100ms)") 
        if not (delay == None or (delay >=0 and delay<=width)):
            raise B1500A_InputError("Delay must be larger than 0 and smaller than the pulse width")
    
    def CheckCMUSweepParam(self, hold, delay, sdelay, tdelay, mdelay, Mstart, Mstop, Mstep, Mmode):
        if isinstance(hold, (float,int)):
            if hold < 0 or hold > 655.35:
                raise B1500A_InputError("Hold time must be a within 0 to 655.35 sec.")
        else:
            raise B1500A_InputError("Hold time must be a float value from 0 to 655.35 sec.")
       
        if isinstance(delay, (float,int)):
            if delay < 0 or delay > 65.35:
                raise B1500A_InputError("Delay time must be within 0 to 65.35 sec.")
        else:
            raise B1500A_InputError("Delay time must be a float value from 0 to 65.35 sec.")

        if isinstance(sdelay, (float,int)):
            if sdelay < 0 or sdelay > 1:
                raise B1500A_InputError("Sdelay time must be within 0 to 1 sec.")
        elif sdelay == None:
            None
        else:
            raise B1500A_InputError("Sdelay time must be within a float value of 0 to 1 sec.")

        if isinstance(tdelay,(float,int)):
            if tdelay < 0 or tdelay > delay:
                raise B1500A_InputError("Tdelay time must be within 0 to delay.")
        elif tdelay == None:
            None
        else:
            raise B1500A_InputError("Tdelay time must be a float value from 0 to delay.")

        if isinstance(mdelay, (float,int)):
            if mdelay < 0 or mdelay > 65.535:
                raise B1500A_InputError("Mdelay time must be within 0 to 65.535 sec.")
        elif mdelay == None:
            None
        else:
            raise B1500A_InputError("Mdelay time must be an integer from 0 to 65.535 sec.")
        
        if Mstart > np.absolute(42) or Mstop > np.absolute(42):
            raise B1500A_InputError("Start and Stop voltages cannot exceed 42V")
        
        if isinstance(Mstep, int):
            if Mstep < 1 or Mstep > 1001:
                raise B1500A_InputError("the Step number must be an integer between 1 and 1001.")
        else: 
            raise B1500A_InputError("the Step number must be an integer between 1 and 1001.")
        
        if isinstance(Mmode, int):
            if Mmode > 4 or Mmode < 1:
                raise B1500A_InputError("The sweep mode of the staircase must be 1 (linear/single), 2 (log/single), 3 (linear/double) or 4 (log/double).")
        elif Mmode == None: 
            None
        else:
            raise B1500A_InputError("The sweep mode of the staircase must be an integer of the following values: 1 (linear/single), 2 (log/single), 3 (linear/double) or 4 (log/double).")
        
    def CheckSweepParam(self, hold, delay, sdelay, tdelay, mdelay, AA, AApost, SChn, Sstart, Sstop, MChn, Mstart, Mstop, Mstep, Mmode):
        if isinstance(hold, (float,int)):
            if hold < 0 or hold > 655.35:
                raise B1500A_InputError("Hold time must be a within 0 to 655.35 sec.")
        else:
            raise B1500A_InputError("Hold time must be a float value from 0 to 655.35 sec.")
       
        if isinstance(delay, (float,int)):
            if delay < 0 or delay > 65.35:
                raise B1500A_InputError("Delay time must be within 0 to 65.35 sec.")
        else:
            raise B1500A_InputError("Delay time must be a float value from 0 to 65.35 sec.")

        if isinstance(sdelay, (float,int)):
            if sdelay < 0 or sdelay > 1:
                raise B1500A_InputError("Sdelay time must be within 0 to 1 sec.")
        elif sdelay == None:
            None
        else:
            raise B1500A_InputError("Sdelay time must be within a float value of 0 to 1 sec.")

        if isinstance(tdelay,(float,int)):
            if tdelay < 0 or tdelay > delay:
                raise B1500A_InputError("Tdelay time must be within 0 to delay.")
        elif tdelay == None:
            None
        else:
            raise B1500A_InputError("Tdelay time must be a float value from 0 to delay.")

        if isinstance(mdelay, (float,int)):
            if mdelay < 0 or mdelay > 65.535:
                raise B1500A_InputError("Mdelay time must be within 0 to 65.535 sec.")
        elif mdelay == None:
            None
        else:
            raise B1500A_InputError("Mdelay time must be an integer from 0 to 65.535 sec.")
        
        if isinstance(AA, int):
            if not AA == 1 or not AA == 2 or not AApost==1 or AApost==2: 
                raise B1500A_InputError("AA and AApost must be 1 or 2.")
        elif AA == None:
            None
        else:
            raise B1500A_InputError("AA and AApost must be an integer of 1 or 2.")

        if not SChn == None:
            if (Sstart == None or Sstop == None):
                raise B1500A_InputError("If a synchronous sweep source is set, Sstart and Sstop must be set as well.")
        
        if isinstance(Mmode, int):
            if Mmode > 4 or Mmode < 1:
                raise B1500A_InputError("The sweep mode of the staircase must be 1 (linear/single), 2 (log/single), 3 (linear/double) or 4 (log/double).")
        elif Mmode == None: 
            None
        else:
            raise B1500A_InputError("The sweep mode of the staircase must be an integer of the following values: 1 (linear/single), 2 (log/single), 3 (linear/double) or 4 (log/double).")
        
        if Mstart > np.absolute(42) or Mstop > np.absolute(42):
            raise B1500A_InputError("Start and Stop voltages cannot exceed 42V")
        if not Sstart == None:
            if Sstart > np.absolute(42) or Sstop > np.absolute(42):
                raise B1500A_InputError("Start and Stop voltages cannot exceed 42V")
        if Mmode == 2 or Mmode == 4: 
            if Mstart > 0 and Mstop < 0:
                raise B1500A_InputError("Start and Stop voltages must be the same polarity in log sweep mode.")
        if SChn != None:
            if Sstart > 0 and Sstop < 0:
                raise B1500A_InputError("Start and Stop voltages must be the same polarity in log sweep mode.")
        
        if isinstance(Mstep, int):
            if Mstep < 1 or Mstep > 1001:
                raise B1500A_InputError("the Step number must be an integer between 1 and 1001.")
        else: 
            raise B1500A_InputError("the Step number must be an integer between 1 and 1001.")
       
    def checkComplPolarity(self, Chns,complPolarity):
        for n in range(len(Chns)): 
            if not complPolarity[n] == None: 
                if not (complPolarity[n] < 3 or complPolarity[n] > 0):
                    raise B1500A_InputError("The Compliance Polarity of connection for Channel %d must be 0, 1 or None." %(Chns[n]))
 
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
        return 
        
    def compileWT(self, hold=0, delay=0, Sdelay=None, Tdelay=None, Mdelay=None):
        ret = "WT %f, %f" %(hold, delay)
        for d in [Sdelay, Tdelay, Mdelay]:
            if d != None: 
                ret = "%s, %f" %(ret,d)
            else:
                break
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
            check= data[0][1:3]
            output.append([])
            label.append("%s%d"%(data[0][2:3],Coding[data[0][1:2]]))
            #for n in range(1,len(data)-2,1):
            for n in range(1,len(data),1):
                if data[n][1:3] == check:
                    break
                else:
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

    def getCVSweepHeader(self, CMU, freq, Vac, DCstart, DCstop, DCstep, DCmode, hold, delay, sdelay, tdelay, mdelay):
        TestPara = ['TestParameter']*12
        TestPara[0] = '%s,Channel.Type, CMU' %(TestPara[0])
        TestPara[1] = '%s,Channel.Unit, CMU%d' %(TestPara[1], CMU)
        TestPara[2] = '%s,Channel.Frequency, %f' %(TestPara[2], freq)
        TestPara[3] = '%s,Channel.Vac, %f' %(TestPara[3], Vac)
        TestPara[4] = '%s,Channel.Vstart, %f' %(TestPara[4], DCstart)
        TestPara[5] = '%s,Channel.Vstop, %f' %(TestPara[5], DCstop)
        TestPara[6] = '%s,Channel.Steps, %d' %(TestPara[6], DCstep)
        TestPara[7] = '%s,Channel.hold, %d' %(TestPara[7], DCstep)
        TestPara[8] = '%s,Channel.delay, %d' %(TestPara[8], delay)
        if sdelay == None: 
            TestPara[9] = '%s,Channel.sdelay, %d' %(TestPara[9], 0)
        else:
            TestPara[9] = '%s,Channel.sdelay, %d' %(TestPara[9], sdelay)
        if sdelay == None: 
            TestPara[9] = '%s,Channel.mdelay, %d' %(TestPara[9], 0)
        else:
            TestPara[9] = '%s,Channel.mdelay, %d' %(TestPara[9], mdelay)
        if sdelay == None: 
            TestPara[9] = '%s,Channel.tdelay, %d' %(TestPara[9], 0)
        else:
            TestPara[9] = '%s,Channel.tdelay, %d' %(TestPara[9], tdelay)

        return TestPara

    def getCVHeader(self, CMU, freq, Vac, Vdc):
        TestPara = ['TestParameter']*5
        TestPara[0] = '%s,Channel.Type, CMU' %(TestPara[0])
        TestPara[1] = '%s,Channel.Unit, CMU%d' %(TestPara[1], CMU)
        TestPara[2] = '%s,Channel.Frequency, %f' %(TestPara[2], freq)
        TestPara[3] = '%s,Channel.Vac, %f' %(TestPara[3], Vac)
        TestPara[4] = '%s,Channel.Vdc, %f' %(TestPara[4], Vdc)
        
        return TestPara

    def getHeader_1(self, Chns, Val, VorI, SSR, FL, MChn=None, SChn=None, hold=None, delay=None, SMChn=None, Index=None, Time=None):
        TestPara = ['TestParameter']*14
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

        if hold != None:
            TestPara[12] = '%s,hold,%f' %(TestPara[12],hold)
        else:
            TestPara[12] = '%s,hold,%f' %(TestPara[12],0)

        if delay != None:
            TestPara[13] = '%s,delay,%f' %(TestPara[13],delay)
        else:
            TestPara[13] = '%s,delay,%f' %(TestPara[13],0)



        return TestPara

    def CheckPulsePVPIParam(self, Chns, VPbase, VPpulse, IPbase, IPpulse, VComp, IComp, VorI, PChn):
        n=0
        for element in Chns:
            if Chns[n] == PChn:
                None
                '''
                if VorI[n]:
                    if np.absolute(VPpulse) > np.absolute(VComp[n]):
                        raise B1500A_InputError("Pbase must be lower than Compliance value")
                    if np.absolute(VPbase) > np.absolute(VPpulse):
                        raise B1500A_InputError("Pbase must be lower than Ppulse value")

                if VorI == False:
                    if np.absolute(IPpulse) > np.absolute(IComp[n]):
                        raise B1500A_InputError("Ppulse must be lower than Compliance value")
                    if np.absolute(IPbase) > np.absolute(IPpulse):
                        raise B1500A_InputError("Pbase must be lower than Ppulse value")
                '''
            n+=1

    def CheckPulseSweepParam(self, Chns, VPbase, VPpulse, VPulseStop, IPbase, IPpulse, 
                            IPulseStop, PStep, VComp, IComp, VorI, PChn):
        
        if not isinstance(PStep, (int)):
            raise B1500A_InputError("PStep must only contain integer values")
        if PStep < 1 or PStep > 1001:
            raise B1500A_InputError("PStep must be between 1 and 1001")

        n=0
        for element in Chns:
            if Chns[n] == PChn:
                if VorI[n]:
                    if np.absolute(VPpulse) > np.absolute(VComp[n]):
                        raise B1500A_InputError("Pbase must be lower than Compliance value")
                    if np.absolute(VPpulse) > np.absolute(VPulseStop):
                        raise B1500A_InputError("Ppulse must be lower than PulseStop value")    
                    if np.absolute(VPbase) > np.absolute(VPpulse):
                        raise B1500A_InputError("Pbase must be lower than Ppulse value")

                if VorI == False:
                    if np.absolute(IPpulse) > np.absolute(IComp[n]):
                        raise B1500A_InputError("Ppulse must be lower than Compliance value")
                    if np.absolute(IPpulse) > np.absolute(IPulseStop):
                        raise B1500A_InputError("Ppulse must be lower than PulseStop value")  
                    if np.absolute(IPbase) > np.absolute(IPpulse):
                        raise B1500A_InputError("Pbase must be lower than Ppulse value")

            n+=1
    
    ############################################################################################
    # can receive Values for a spot measurement if the Channels passed calibration and are installed
    # SMUs: Array with Channel Number
    # Val:  Array containing voltage values
    # Val:  Array containing current values
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
    # complPolarity: 
    # hold: Hold time (in s) that is the wait time after starting the sweep measurement and before starting the dealy time for the first step.
    # delay: Delay time (in s) that is the wait time after starting to force a step output and before starting a step measurement 
    
    def SpotMeasurement(self, SMUs, VorI, Val, VComp=None, IComp=None, RV=None, 
                        RI=None, FL=None, SSR=None, ADCs=None, CMM=None, complPolarity=None, hold=0, delay=0):

        if RV == None: RV = [0]*len(SMUs)           # auto voltage range for all active channels
        if RI == None: RI = [0]*len(SMUs)           # auto current range for all active channels
        if type(RV) == int: RV = [RV]*len(SMUs)           # use same range for all channel
        if type(RI) == int: RI = [RI]*len(SMUs)           # use same range for all channel
        if VComp == None: VComp = [None]*len(SMUs)     # auto compliance for all active Voltage channels
        if IComp == None: IComp = [None]*len(SMUs)     # auto compliance for all active Current channels
        if FL == None: FL = [None]*len(SMUs)        # don't set the filter for all active channels
        if SSR == None: SSR = [None]*len(SMUs)      # don't set the series resistance for all active channels
        if CMM == None: CMM = [None]*len(SMUs)      # don't set the channel mode for all active channels
        if complPolarity == None: complPolarity = [0]*len(SMUs)     # auto compliance polarity for all active channels
        if hold == None: hold = 0                       # set hold to standard if None
        if delay == None: delay = 0                     # set delay to standard if None

        self.checkListConsistancy([SMUs, VorI, Val, VComp, IComp, RV, RI, FL, SSR, CMM], "Spot Measurement")

        self.checkChannel(SMUs)
        Chns = self.getChnNumFromSMUnum(SMUs)
        self.setSMUSCUU()

        if ADCs == None: ADCs = [0]*len(SMUs)    

        for SMU in SMUs:
            self.SMUisAvailable(SMU)
            self.SMUisUsed(SMU)
            
        #check if all values in VorI are Boolean
        for element in VorI:
            if not isinstance(element, (bool)):
                raise B1500A_InputError("VorI must only contain boolean values")

        # Checks base variables
        self.CheckADCValues(SMUs, ADCs)
        self.CheckRanges(SMUs, "Voltage", RV)
        self.CheckRanges(SMUs, "Current", RI)
        self.CheckVolCurValues(SMUs, VorI, Val, RV, RI)
        self.CheckCompliance(SMUs, VorI, Val, IComp, VComp, RV, RI)
        self.CheckFilter(SMUs, VorI, FL)
        self.CheckSeriesResistance(SMUs, SSR)
        self.CheckChannelMode(SMUs, CMM)
        self.CheckDelays(hold, delay)

        # Clears all the channels
        for chn in self.SMUChns:
            self.instWrite("CL %d\n" %(chn))

        # Sets integration time
        n=0
        for chn in Chns:
            if ADCs[n] != None:
                self.instWrite("AAD %d, %d\n" %(chn,ADCs[n]))
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

            self.instWrite(self.compileWT(hold, delay))

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
            
            mode = "%s, %d" %(mode, Chns[n])

        self.instWrite("MM 1%s" %(mode))
        self.instWrite('FMT 1,1')
        retAr = []
        if self.execute:
            self.instWrite("TSR\n")
            self.instWrite("XE\n")
            self.instWrite("DZ\n") 

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
            #return True

        ########CreateHeader
        Header = self.getHeader_1(SMUs, Val, VorI, SSR, FL, MChn=None, SChn=None, delay=delay, hold=hold)
        ADCHeader = self.getADCHeader()
        newline = "TestParameter,Channel.Value"
        for val in Val:
            newline = "%s,%.2e" %(newline, val)
        Header.append(newline)
        Header.extend(ADCHeader)
        return {'Data': retAr, 'Header': Header}

    ############################################################################################
    # Can receive Values for a high-speed spot measurement if the Channels passed calibration and are installed
    # Chns: Array with Channel Number
    # Val:  Array containing voltages values
    # Val:  Array containing current values
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

    def HighSpeedSpotMeasurement(self, SMUs, VorI, Val, VM, IM, VComp=None, 
                                IComp=None, RV=None, RI=None, FL=None, SSR=None, 
                                ADCs=None, complPolarity=None):
        
        #if self.execute:
        #    raise SystemError("High-Speed Spot Measurement is incompatible with other measurement types, please change the excecute state.")

        if RV == None: RV = [0]*len(SMUs)           # auto voltage range for all active channels
        if RI == None: RI = [0]*len(SMUs)           # auto current range for all active channels
        if type(RV) == int: RV = [RV]*len(SMUs)           # use same range for all channel
        if type(RI) == int: RI = [RI]*len(SMUs)           # use same range for all channel
        if VComp == None: VComp = [0]*len(SMUs)     # auto compliance for all active Voltage channels
        if IComp == None: IComp = [0]*len(SMUs)     # auto compliance for all active Currentchannels
        if FL == None: FL = [None]*len(SMUs)        # don't set the filter for all active channels
        if SSR == None: SSR = [None]*len(SMUs)      # don't set the series resistance for all active channels
        if complPolarity == None: complPolarity = [0]*len(SMUs)     # auto compliance polarity for all active channels
        
        self.checkListConsistancy([SMUs, VorI, Val, VM, IM, VComp, IComp, RV, RI, FL, SSR], "High-Speed Spot Measurement")
        self.checkChannel(SMUs)
        Chns = self.getChnNumFromSMUnum(SMUs)
        self.setSMUSCUU()
        if ADCs == None: ADCs = [0]*len(SMUs)  

        for SMU in SMUs:
            self.SMUisAvailable(SMU)
            self.SMUisUsed(SMU)
        
        #check if all values in VorI are Boolean
        for element in VorI:
            if not isinstance(element, (bool)):
                raise B1500A_InputError("VorI must only contain boolean values")

        self.CheckRanges(SMUs, "Voltage", RV)
        self.CheckRanges(SMUs, "Current", RI)
        self.CheckVolCurValues(SMUs, VorI, Val, RV, RI)
        self.CheckCompliance(SMUs, VorI, Val, IComp, VComp, RV, RI)
        self.CheckFilter(SMUs, VorI, FL)
        self.CheckVMIM(VM, IM)
        self.CheckADCValues(SMUs,ADCs)

        self.instWrite("CL\n")

        # Sets integration time
        n=0
        for chn in Chns:
            if ADCs[n] != None:
                self.instWrite("AAD %d, %d\n" %(chn,ADCs[n]))
            n+=1
        n=0

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

        Header = self.getHeader_1(SMUs, Val, VorI, SSR, FL, MChn=None, SChn=None)
        ADCHeader = self.getADCHeader()
        Header.extend(ADCHeader)
        self.finishMeasurement()

        return {'Data': self.HSMOutput, 'Header': Header}
        
    ############################################################################################
    # can receive Values for a pulsed spot measurement if the Channels passed calibration and are installed
    # Chns: Array containing Channel Numbers
    # PChn: Pulse Measurement Channel must be a channel defined in Chns
    # Val:  Array containing voltage values
    # Val:  Array containing current values
    # BVal: Array containing base voltages or currents for the pulse channels (Values for constant voltage/current sources are ignored)
    # VorI: Array if I or V are forced contains Binary True for V, False for I
    # RV:   Array of ranges for voltage measurement
    # RI:   Array of ranges for current measurement
    # IComp:Array for the set Compliance Current
    # VComp:Array for the set Compliance Voltage
    # FL:   Sets the filter of the specified channels to ON or OFF.
    # SSR:  Series resistance will be applied
    # PorC: Choose if Channel shall apply a pulse or a constant voltage/current 
    # hold: Hold time for the pulse channels (in s)
    # width: Pulse width for the pulse channels (in s)
    # period: Pulse period for the pulse channels (in s)
    # delay:  Delay for the pulse channels (in s)
    # CMM:  The CMM command sets the SMU measurement operation mode.
    
    def PulsedSpotMeasurement(self, SMUs, Psmu, VPbase, VPpulse, IPbase, IPpulse, VorI, Val, hold, width, RV=None, RI=None,  
                                IComp=None, VComp=None, period=None, delay=None, BVal=None, 
                                FL=None, SSR=None, CMM=None, complPolarity=None):
        
        if RV == None: RV = [0]*len(SMUs)           # auto voltage range for all active channels
        if RI == None: RI = [0]*len(SMUs)           # auto current range for all active channels
        if type(RV) == int: RV = [RV]*len(SMUs)           # use same range for all channel
        if type(RI) == int: RI = [RI]*len(SMUs)           # use same range for all channel
        if IComp == None: IComp = [None]*len(SMUs)     # auto compliance for all active channels
        if VComp == None: VComp = [None]*len(SMUs)     # auto compliance for all active channels
        if FL == None: FL = [None]*len(SMUs)        # don't set the filter for all active channels
        if SSR == None: SSR = [None]*len(SMUs)      # don't set the series resistance for all active channels
        if CMM == None: CMM = [None]*len(SMUs)      # don't set the channel mode for all active channels
        if BVal == None: BVal = [0]*len(SMUs)       # set all BVal to 0V if not initiated
        if complPolarity == None: complPolarity = [0]*len(SMUs)     # auto compliance polarity for all active channels

        self.checkListConsistancy([SMUs, VorI, RV, RI, Val, IComp, VComp, FL, SSR, CMM], "Pulsed Spot Measurement")

        self.checkChannel(SMUs)
        self.setSMUSCUU()

        for SMU in SMUs:
            self.SMUisAvailable(SMU)
            self.SMUisUsed(SMU)
        
        #check if all values in VorI are Boolean
        for element in VorI:
            if not isinstance(element, (bool)):
                raise B1500A_InputError("VorI (Voltage or Current) must only contain boolean values")
        
        #if np.any(not PorC):
        #    raise SyntaxError("P or C (Pulse or Constant) must contain one True Value indicating a Pulse channel")

        self.CheckRanges(SMUs, "Voltage", RV)
        self.CheckRanges(SMUs, "Current", RI)
        self.CheckVolCurValues(SMUs, VorI, Val, RV, RI)
        self.CheckCompliance(SMUs, VorI, Val, IComp, VComp, RV, RI)
        self.CheckFilter(SMUs, VorI, FL)
        self.CheckSeriesResistance(SMUs, SSR)
        self.CheckChannelMode(SMUs, CMM)

        hold = np.around(hold, 2)
        width = np.around(width, 4)
        if not period == None:
            period = np.around(period, 4)
        if not delay == None:
            delay = np.around(delay, 4)

        self.CheckPulseParamSMU(hold, width, period, delay)
        self.CheckPulsePVPIParam(SMUs, VPbase, VPpulse, IPbase, IPpulse, VComp, IComp, VorI, Psmu)

        self.instWrite("CL\n")

        mode = ""

        for n in range(len(Chns)):
            self.instWrite("CN %d\n" %(Chns[n]))
            if not FL[n] == None:
                self.instWrite("FL %d, %d\n" %(FL[n], Chns[n]))

            if not SSR[n] == None:
                self.instWrite("SSR %d, %d\n" %(SSR[n], Chns[n]))
            
            if not self.is_int(PChn):
                raise B1500A_InputError("PChn must be an integer between 1 and 8 and be present in SMUs.")
            if Psmu > 8 or Psmu < 1 or Psmu not in SMUs: 
                raise B1500A_InputError("PChn must be an integer between 1 and 8 and be present in SMUs.")
            
            if VorI[n]:
                self.instWrite(self.compileDV(Chns[n], RV[n], Val[n], IComp[n], complPolarity[n], RI[n]))
            else:
                self.instWrite(self.compileDI(Chns[n], RI[n], Val[n], VComp[n], complPolarity[n], RV[n]))

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
                    if IComp[n] == None:
                        self.instWrite("PV %d, %d, %f, %f\n" %(Chns[n], RV[n], VPbase, VPpulse))
                    else:
                        self.instWrite("PV %d, %d, %f, %f, %f\n" %(Chns[n], RV[n], VPbase, VPpulse, IComp[n]))

                else:
                    if VComp[n] == None:
                        self.instWrite("PI %d, %d, %f, %f\n" %(Chns[n], RI[n], VPbase, VPpulse))
                    else:
                        self.instWrite("PI %d, %d, %f, %f, %f\n" %(Chns[n], RI[n], VPbase, VPpulse, VComp[n]))

            if VorI[n]:
                self.instWrite("RV %d, %d\n" %(Chns[n], RV[n]))
            else: 
                self.instWrite("RI %d, %d\n" %(Chns[n], RI[n]))

            if not CMM[n] == None:
                self.instWrite("CMM %d, %d\n" %(Chns[n], CMM[n]))
            
            mode = "%s, %d" %(mode, Chns[n])

        self.instWrite("MM 3, %d\n" %(PChn))
        
        self.instWrite('FMT 1,1')
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
        Header = self.getHeader_1(SMUs, Val, VorI, SSR, FL, MChn=None, SChn=None)
        ADCHeader = self.getADCHeader()
        Header.extend(ADCHeader)
        self.finishMeasurement()

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
    
    def StaircaseSweepMeasurement(self, SMUs, VorI, Msmu, Mstart, Mstop, Mstep,
                                    hold, delay, Val, VComp, IComp, Mmode=1, MeasSMUs=None, Ssmu=None, Sstart=None, 
                                    Sstop=None, AA=None, AApost=None, Pcompl=None, 
                                    sdelay=None, tdelay=None, mdelay=None, RV=None, RI=None, FL=None, 
                                    SSR=None, ADCs=None, CMM=None, complPolarity=None):
        
        if RV == None: RV = [0]*len(SMUs)                   # auto voltage range for all active channels
        if RI == None: RI = [0]*len(SMUs)                   # auto current range for all active channels
        if type(RV) == int: RV = [RV]*len(SMUs)           # use same range for all channel
        if type(RI) == int: RI = [RI]*len(SMUs)           # use same range for all channel
        if VComp == None: VComp = [0]*len(SMUs)             # auto compliance for all active channels
        if IComp == None: IComp = [0]*len(SMUs)             # auto compliance for all active channels
        if complPolarity == None: complPolarity = [0]*len(SMUs)     # auto compliance polarity for all active channels
        if FL == None: FL = [None]*len(SMUs)                # don't set the filter for all active channels
        if SSR == None: SSR = [None]*len(SMUs)              # don't set the series resistance for all active channels
        if CMM == None: CMM = [None]*len(SMUs)              # don't set the channel mode for all active channels
        if Pcompl == None: Pcompl = [None]*len(SMUs)        # don't set the Pcompl for all Channels
        if MeasSMUs == None: MeasSMUs = SMUs                # sets the standard for MeasSMU to measure all SMUs
        if ADCs == None: ADCs = [0]*len(SMUs)                 #Sets the ADC to High-Speed for all channels
        
        
        self.checkListConsistancy([SMUs, VorI, Val, VComp, IComp, RV, RI, FL, SSR, CMM], "Staircase Sweep Measurement")
        self.checkChannel(SMUs)
        Chns = self.getChnNumFromSMUnum(SMUs)
        self.setSMUSCUU() 

        for SMU in SMUs:
            self.SMUisAvailable(SMU)
            self.SMUisUsed(SMU)
            
        #check if all values in VorI are Boolean
        for element in VorI:
            if not isinstance(element, (bool)):
                raise B1500A_InputError("VorI must only contain boolean values")

        if not Ssmu == None:
            if Msmu in Ssmu:
                raise B1500A_InputError("Ssmu (Synchronized sweep Channel) must not be defined as Msmu (primary Sweep Channel).")

            for SC in Ssmu:
                if not SC in SMUs:
                    raise B1500A_InputError("Ssmu (Synchronized sweep Channel) must not be defined as an active Channel in SMUs.")
        
        self.CheckADCValues(SMUs, ADCs)
        self.CheckRanges(SMUs, "Voltage", RV)
        self.CheckRanges(SMUs, "Current", RI)
        self.CheckVolCurValues(SMUs, VorI, Val, RV, RI)
        self.CheckCompliance(SMUs, VorI, Val, IComp, VComp, RV, RI)
        self.CheckFilter(SMUs, VorI, FL)
        self.CheckSeriesResistance(SMUs, SSR)
        self.CheckChannelMode(SMUs, CMM)
        self.CheckSweepParam(hold, delay, sdelay, tdelay, mdelay, AA, AApost, Ssmu, Sstart, Sstop, Msmu, Mstart, Mstop, Mstep, Mmode)
        self.checkComplPolarity(SMUs, complPolarity)

        MChn = self.getChnNumFromSMUnum([Msmu])[0]
        if Ssmu != None:
            SChn = self.getChnNumFromSMUnum([Ssmu])[0]
        else: 
            SChn = None

        n = 0
        for SMU in SMUs:
            if SMU == Msmu:
                Mn = n
            if SMU == Ssmu:
                Sn = n

        for chn in Chns: 
            self.instWrite("CL %d\n" %(chn))

        n=0
        for chn in Chns:
            if ADCs[n] != None:
                self.instWrite("AAD %d, %d\n" %(chn,ADCs[n]))
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
            
            if MeasSMUs[n]:
                mode = "%s, %d" %(mode, Chns[n])


        if not AA == None:
            if not AApost == None:
                self.instWrite("WM %d, %d\n" %(AA, AApost))
            else:
                self.instWrite("WM %d\n" %(AA))
        
        self.instWrite("MM 2 %s\n" %(mode))
        
        self.instWrite('FMT 1,1')
        
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
        Header = self.getHeader_1(SMUs, Val, VorI, SSR, FL, MChn=Msmu, SChn=Ssmu)

        Compl = []
        for n in range(len(VComp)):
            if VorI[n]: 
                Compl.append(IComp[n])
            else:
                Compl.append(VComp[n])

        print(VComp, IComp, Compl)

        SweepMode = self.getSweepMode(Mmode)
        Header.append('TestParameter,Measurement.Primary.Locus,%s' %(SweepMode[0]))
        Header.append('TestParameter,Measurement.Primary.Scale,%s' %(SweepMode[1]))
        Header.append('TestParameter,Measurement.Primary.Start,%f' %(Mstart))
        Header.append('TestParameter,Measurement.Primary.Stop,%f' %(Mstop))
        Header.append('TestParameter,Measurement.Primary.Step,%f' %(Mstep))

        Header.append('TestParameter,Measurement.Primary.Compliance,%s' %(Compl[Mn]))

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

        if not Ssmu == None:
            Header.append('TestParameter,Measurement.Secondary.start,%f' %(Sstart))
            Header.append('TestParameter,Measurement.Secondary.stop,%f' %(Sstop))
            Header.append('TestParameter,Measurement.Secondary.Compliance,%f' %(Compl[Sn]))
            Header.append('TestParameter,Measurement.Secondary.PowerCompliance,%f' %(Pcompl[Sn]))
        
        MonitorHeader = self.getMonitorHeader(SMUs, Val, Compl, VorI, ADCs, RI, RV, CMM)
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

        ADCHeader = self.getADCHeader()
        Header.extend(ADCHeader)
        self.finishMeasurement()

        return {'Data': retAr, 'Header': Header}

    def checkChannel(self, chns):
        
        for chn in chns:
            if not isinstance(chn, int):
                raise TypeError("Channel ID must be an integer from 1 to %d." %(self.NumSMUs))
            if chn < 1 or chn > self.NumSMUs:
                raise B1500A_InputError("Channel ID must be an integer from 1 to %d." %(self.NumSMUs))
    
    def getChnNumFromSMUnum(self,chns):
        if not isinstance(chns, list):
            chns = [chns]
        newChn = []
        for chn in chns: 
            newChn.append(self.SMUChns[chn-1])
        return newChn

    def getChnNumFromCMUnum(self,chns):
        if not isinstance(chns, list):
            chns = [chns]
        newChn = []
        for chn in chns: 
            newChn.append(self.CMUChns[chn-1])
        return newChn

    def MultiChannelSweepMeasurement(self, SMU):
        self.SMUisAvailable(SMU)

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
    # MeasSMUs: specify the channels that should get measured, True/False Array, for each Chns entry in Chns; Auto is all channels
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

    def PulsedSweepMeasurement(self, SMUs, Psmu, VPbase, VPpulse, VPulseStop, IPbase, IPpulse, IPulseStop, 
                                PStep, SWMode, VorI, RV, RI, Val, IComp, VComp, hold, width, Abort, 
                                period=None, delay=None, BVal=None, FL=None, SSR=None, CMM=None, 
                                complPolarity=None, Post=None):
        if RV == None: RV = [0]*len(SMUs)           # auto voltage range for all active channels
        if RI == None: RI = [0]*len(SMUs)           # auto current range for all active channels
        if type(RV) == int: RV = [RV]*len(SMUs)           # use same range for all channel
        if type(RI) == int: RI = [RI]*len(SMUs)           # use same range for all channel
        if IComp == None: IComp = [0]*len(SMUs)     # auto compliance for all active channels
        if VComp == None: VComp = [0]*len(SMUs)     # auto compliance for all active channels
        if FL == None: FL = [None]*len(SMUs)        # don't set the filter for all active channels
        if SSR == None: SSR = [None]*len(SMUs)      # don't set the series resistance for all active channels
        if CMM == None: CMM = [None]*len(SMUs)      # don't set the channel mode for all active channels
        if BVal == None: BVal = [0]*len(SMUs)       # set all BVal to 0V if not initiated
        if complPolarity == None: complPolarity = [0]*len(SMUs)     # auto compliance polarity for all active channels
        
        self.checkListConsistancy([SMUs, VorI, RV, RI, Val, IComp, VComp, FL, SSR, CMM], "Pulsed Sweep Measurement")
        self.checkChannel(SMUs)
        Chns = self.getChnNumFromSMUnum(SMUs)
        PChn = self.getChnNumFromSMUnum([Psmu])[0]
        self.setSMUSCUU() 

        for SMU in SMUs:
            self.SMUisAvailable(SMU)
            self.SMUisUsed(SMU)
        
        #check if all values in VorI are Boolean
        for element in VorI:
            if not isinstance(element, (bool)):
                raise B1500A_InputError("VorI (Voltage or Current) must only contain boolean values")
        
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

        self.instWrite("CL\n")

        mode = ""

        for n in range(len(Chns)):
            self.instWrite("CN %d\n" %(Chns[n]))
            if not FL[n] == None:
                self.instWrite("FL %d, %d\n" %(FL[n], Chns[n]))

            if not SSR[n] == None:
                self.instWrite("SSR %d, %d\n" %(SSR[n], Chns[n]))
            
            if not self.is_int(PChn):
                raise B1500A_InputError("PChn must be an integer between 1 and 8 and be present in Chns.")
            if PChn > 8 or PChn < 1 or PChn not in Chns: 
                raise B1500A_InputError("PChn must be an integer between 1 and 8 and be present in Chns.")

            if VorI[n]:
                self.instWrite(self.compileDV(Chns[n], RV[n], Val[n], IComp[n], complPolarity[n], RI[n]))
            else:
                self.instWrite(self.compileDI(Chns[n], RI[n], Val[n], VComp[n], complPolarity[n], RV[n]))

            if Chns[n] == PChn:
                if period==None:
                    self.instWrite("PT %d, %d\n" %(hold, width))
                else:
                    if delay == None:
                        self.instWrite("PT %d, %d, %d\n" %(hold, width, period))
                    else:
                        self.instWrite("PT %d, %d, %d, %f\n" %(hold, width, period, delay))

            if Chns[n] == PChn:
                if VorI[n]:
                    self.instWrite("PWV %d, %d, %d, %d, %d, %d, %d, %d\n" %(Chns[n], SWMode, 
                                                            RV[n], VPbase, VPpulse, VPulseStop, PStep, IComp[n]))
                else:
                    self.instWrite("PWI %d, %d, %d, %d, %d, %d, %d, %d\n" %(Chns[n], SWMode, 
                                                            RI[n], IPbase, IPpulse, IPulseStop, PStep, VComp[n]))

            if VorI[n]:
                self.instWrite("RV %d, %d\n" %(Chns[n], RV[n]))
            else: 
                self.instWrite("RI %d, %d\n" %(Chns[n], RI[n]))

            if not CMM[n] == None:
                self.instWrite("CMM %d, %d\n" %(Chns[n], CMM[n]))
            
            mode = "%s, %d" %(mode, Chns[n])

        self.instWrite("MM 3 %d\n" %(PChn))
        
        self.instWrite('FMT 1,1')
        if Post == None:
            self.instWrite("WM %d\n" %(Abort))
        else:
            self.instWrite("WM %d, %d\n" %(Abort, Post))
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
        Header = self.getHeader_1(SMUs, Val, VorI, SSR, FL, MChn=None, SChn=None)
        ADCHeader = self.getADCHeader()
        Header.extend(ADCHeader)
        self.finishMeasurement()

        return {'Data': retAr, 'Header': Header}


    def StaircaseSweepWPulsedBiasMeasurement(self):
        self.SMUisAvailable(SMU)

    def QuasiPulsedSpotMeasurement(self):
        self.SMUisAvailable(SMU)

    def BinarySearchMeasurement(self):
        self.SMUisAvailable(SMU)

    def LinearSearchMeasurement(self):
        self.SMUisAvailable(SMU)

    def CheckVMon(self, VMon):

        if not isinstance(VMon, (bool, type(None))):
            raise B1500A_InputError("MFCMU data output of the AC voltage and DC voltage monitor values must be either True or False.")
    
    def CheckSSL(self, SSL):

        if not isinstance(SSL, (bool, type(None))):
            raise B1500A_InputError("MFCMU Connection status indicator (LED) of the SCUU must be either True or False")

    def CheckSCUU(self, con):
        if not isinstance(con, (int)):
            raise B1500A_InputError("SCUU connection path must be an integer between 1 and 4.")
        if 1 > con > 4:
            raise B1500A_InputError("SCUU connection path must be an integer between 1 and 4.")
    
    def CheckCMURange(self, mode, Range, freq):

        f200k = [50,100,300,1000,3000,10000,30000,100000,300000]
        f2M = [50,100,300,1000,3000,10000,30000]
        f5M = [50,100,300,1000,3000]

        if not isinstance(mode, (bool, type(None))):
            raise B1500A_InputError("CMU measurement range mode must be of type bool (True: Auto Ranging, False: Fixed range)")
        if mode != None:
            if not mode:
                if freq <= 200000:
                    if not Range in f200k:
                        raise B1500A_InputError("CMU measurement range must be 50,100,300,1000,3000,10000,30000,100000,300000 ohm for freq <= 200kHz")
                if freq <= 2000000:
                    if not Range in f2M:
                        raise B1500A_InputError("CMU measurement range must be 50,100,300,1000,3000,10000,30000 ohm for freq <= 2MHz")
                else:
                    if not Range in f5M:
                        raise B1500A_InputError("CMU measurement range must be 50,100,300,1000,3000 ohm for freq <= 5MHz")



    ############################################################################################
    # can receive Values for a Capacitive spot measurement if the Channels passed calibration and are installed
    # CMU: CMU number (1-10)
    # freq: CMU frequency
    # Vac: CMU oscilattor voltage
    # Vdc: CMU DC voltage
    # SMUs: Array with Channel Number
    # Val:  Array containing output values
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
    
    def SpotCMeasurement(self, CMU, freq, Vac, Vdc, Cmode=None, CMmode=None, CMrange=None, SMUs=None, VorI=None, Val=None, VComp=None, IComp=None, 
                                    FL=None, SSR=None, SSL=None, RV=None, RI=None, VMon=None, ADCs=None , CMM=None, complPolarity=None):
        
        if RV == None: RV = [0]*len(SMUs)           # auto voltage range for all active channels
        if RI == None: RI = [0]*len(SMUs)           # auto current range for all active channels
        if type(RV) == int: RV = [RV]*len(SMUs)           # use same range for all channel
        if type(RI) == int: RI = [RI]*len(SMUs)           # use same range for all channel
        if VComp == None: VComp = [None]*len(SMUs)     # auto compliance for all active Voltage channels
        if IComp == None: IComp = [None]*len(SMUs)     # auto compliance for all active Current channels
        if FL == None: FL = [None]*len(SMUs)        # don't set the filter for all active channels
        if SSR == None: SSR = [None]*len(SMUs)      # don't set the series resistance for all active channels
        if CMM == None: CMM = [None]*len(SMUs)      # don't set the channel mode for all active channels
        if complPolarity == None: complPolarity = [0]*len(SMUs)     # auto compliance polarity for all active channels
                
        self.checkListConsistancy([SMUs, VorI, Val, VComp, IComp, RV, RI, FL, SSR, CMM], "Spot Measurement")

        self.checkChannel(SMUs)
        self.checkChannel([CMU])
        Chns = self.getChnNumFromSMUnum(SMUs)
        CMUChn = self.getChnNumFromCMUnum(CMU)[0]
        self.setCMUSCUU(CMUChn)

        if ADCs == None: 
            ADCs = [0]*len(SMUs)    

        for SMU in SMUs:
            self.SMUisAvailable(SMU)
            self.SMUisUsed(SMU)

        self.CMUisAvailable(CMU)
        
        #check if all values in VorI are Boolean
        for element in VorI:
            if not isinstance(element, (bool)):
                raise B1500A_InputError("VorI must only contain boolean values")

        # Checks base variables
        self.CheckADCValues(SMUs, ADCs)
        self.CheckRanges(SMUs, "Voltage", RV)
        self.CheckRanges(SMUs, "Current", RI)
        self.CheckVolCurValues(SMUs, VorI, Val, RV, RI)
        self.CheckCompliance(SMUs, VorI, Val, IComp, VComp, RV, RI)
        self.CheckFilter(SMUs, VorI, FL)
        self.CheckSeriesResistance(SMUs, SSR)
        self.CheckChannelMode(SMUs, CMM)
        self.CheckCMUValues(freq, Vac, Cmode, Vdc)
        self.CheckVMon(VMon)
        self.CheckCMURange(CMmode, CMrange, freq)
        valName = self.getValName(Cmode)

        if VMon or VMon == None:
            VMon = 0
        else:
            VMon = 1

        # Clears all the channels
        self.instWrite("CL\n")
            
        self.instWrite("CN %d\n" %(CMUChn))

        # Sets integration time
        n=0
        for chn in Chns:
            if ADCs[n] != None:
                self.instWrite("AAD %d, %d\n" %(chn,ADCs[n]))
            n+=1
        n=0

        # Set mode value to blank string to be change later when calling MM
        mode = ""

        if not Cmode == None:
            self.instWrite("IMP %d\n" %(Cmode))

        if not VMon == None:
            self.instWrite("LMN %d\n" %(VMon))
        
        self.instWrite("FC %d, %f\n" %(CMUChn, freq))
        self.instWrite("ACV %d, %f\n" %(CMUChn, Vac))
        self.instWrite("DCV %d, %f\n" %(CMUChn, Vdc))

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
            
        if CMmode != None: 
            if not (CMmode == 2 and CMrange == None):
                self.instWrite(self.compileRC(CMUChn, CMmode, CMrange))
            
            
        self.instWrite("MM 17, %d" %(CMUChn))
        
        self.instWrite('FMT 1,1')

        retAr = []
        if self.execute:
            self.instWrite("TSR\n")
            self.instWrite("XE\n")
            self.instWrite("DZ\n") 

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
            #return True

        ########CreateHeader
        Header = self.getCVHeader(CMU, freq, Vac, Vdc)
        IVHeader = self.getHeader_1(SMUs, Val, VorI, SSR, FL, MChn=None, SChn=None)
        ADCHeader = self.getADCHeader()
        newline = "TestParameter,Channel.Value"
        for val in Val:
            newline = "%s,%.2e" %(newline, val)
        Header.extend(IVHeader)
        Header.append(newline)
        Header.extend(ADCHeader)
        ret = {'Data': retAr, 'Header': Header}
        ret.update(valName)
        self.finishMeasurement()
        return ret


    ############################################################################################

    # can receive Values for a Capacitive spot measurement if the Channels passed calibration and are installed
    # CMU: CMU number (1-10)
    # freq: CMU frequency
    # Vac: CMU oscilattor voltage
    # Vdc: CMU DC voltage
    # SMUs: Array with Channel Number
    # Val:  Array containing output values
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
    
    def CVSweepMeasurement(self, CMU, freq, Vac, DCstart, DCstop, DCstep, DCmode, hold, delay, sdelay=None, tdelay=None, mdelay=None, Cmode=None, 
                                    CMmode=None, CMrange=None, SMUs=None, VorI=None, Val=None, VComp=None, IComp=None, FL=None, 
                                    SSR=None, SSL=None, RV=None, RI=None, VMon=None, ADCs=None , CMM=None, complPolarity=None):

        if RV == None: RV = [0]*len(SMUs)           # auto voltage range for all active channels
        if RI == None: RI = [0]*len(SMUs)           # auto current range for all active channels
        if type(RV) == int: RV = [RV]*len(SMUs)           # use same range for all channel
        if type(RI) == int: RI = [RI]*len(SMUs)           # use same range for all channel
        if VComp == None: VComp = [None]*len(SMUs)     # auto compliance for all active Voltage channels
        if IComp == None: IComp = [None]*len(SMUs)     # auto compliance for all active Current channels
        if FL == None: FL = [None]*len(SMUs)        # don't set the filter for all active channels
        if SSR == None: SSR = [None]*len(SMUs)      # don't set the series resistance for all active channels
        if CMM == None: CMM = [None]*len(SMUs)      # don't set the channel mode for all active channels
        if complPolarity == None: complPolarity = [0]*len(SMUs)     # auto compliance polarity for all active channels

        self.checkListConsistancy([SMUs, VorI, Val, VComp, IComp, RV, RI, FL, SSR, CMM], "Spot Measurement")

        self.checkChannel(SMUs)
        self.checkChannel([CMU])
        Chns = self.getChnNumFromSMUnum(SMUs)
        CMUChn = self.getChnNumFromCMUnum(CMU)[0]
        self.setCMUSCUU(CMUChn) 

        if ADCs == None: 
            ADCs = [0]*len(SMUs)    

        for SMU in SMUs:
            self.SMUisAvailable(SMU)
            self.SMUisUsed(SMU)

        self.CMUisAvailable(CMU)
        
        #check if all values in VorI are Boolean
        for element in VorI:
            if not isinstance(element, (bool)):
                raise B1500A_InputError("VorI must only contain boolean values")

        # Checks base variables
        self.CheckADCValues(SMUs, ADCs)
        self.CheckRanges(SMUs, "Voltage", RV)
        self.CheckRanges(SMUs, "Current", RI)
        self.CheckVolCurValues(SMUs, VorI, Val, RV, RI)
        self.CheckCompliance(SMUs, VorI, Val, IComp, VComp, RV, RI)
        self.CheckFilter(SMUs, VorI, FL)
        self.CheckSeriesResistance(SMUs, SSR)
        self.CheckChannelMode(SMUs, CMM)
        self.CheckCMUValues(freq, Vac, Cmode)
        self.CheckVMon(VMon)
        self.CheckCMUSweepParam(hold, delay, sdelay, tdelay, mdelay, DCstart, DCstop, DCstep, DCmode)
        self.CheckCMURange(CMmode, CMrange, freq)
        valName = self.getValName(Cmode)

        if VMon or VMon == None:
            VMon = 0
        else:
            VMon = 1

        # Clears all the channels
        for chn in self.SMUChns:
            self.instWrite("CL %d\n" %(chn))

        self.instWrite("CL %d\n" %(CMUChn))
        self.instWrite("CN %d\n" %(CMUChn))

        # Sets integration time
        n=0
        for chn in Chns:
            if ADCs[n] != None:
                self.instWrite("AAD %d, %d\n" %(chn,ADCs[n]))
            n+=1
        n=0

        if not Cmode == None:
            self.instWrite("IMP %d\n" %(Cmode))

        if not VMon == None:
            self.instWrite("LMN %d\n" %(VMon))
        
        self.instWrite("FC %d, %f\n" %(CMUChn, freq))
        self.instWrite("ACV %d, %f\n" %(CMUChn, Vac))
        
        self.instWrite(self.compileWTDCV(hold, delay, sdelay, tdelay, mdelay))
        self.instWrite("WDCV %d, %d, %f, %f, %f\n" %(CMUChn, DCmode, DCstart, DCstop, DCstep))

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
        
        if CMmode != None: 
            if not (CMmode == 2 and CMrange == None):
                self.instWrite(self.compileRC(CMUChn, CMmode, CMrange))
            
        self.instWrite("MM 18, %d" %(CMUChn))

        self.instWrite('FMT 1,1')
        retAr = []
        if self.execute:
            self.instWrite("TSR\n")
            self.instWrite("XE\n")
            self.instWrite("DZ\n") 

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
            #return True


        ########CreateHeader
        Header = self.getCVSweepHeader(CMU, freq, Vac, DCstart, DCstop, DCstep, DCmode, hold, delay, sdelay, tdelay, mdelay)
        IVHeader = self.getHeader_1(SMUs, Val, VorI, SSR, FL, MChn=None, SChn=None)
        ADCHeader = self.getADCHeader()
        newline = "TestParameter,Channel.Value"
        for val in Val:
            newline = "%s,%.2e" %(newline, val)
        Header.extend(IVHeader)
        Header.append(newline)
        Header.extend(ADCHeader)
        ret = {'Data': retAr, 'Header': Header}
        ret.update(valName)
        self.finishMeasurement()
        return ret

    
    def getValName(self, Cmode):

        name = [None]*2
        unit = [None]*2
        name[0] = "Cp"
        name[1] = "G"
        unit[0] = "F"
        unit[1] = "S"
        if Cmode == 1:
            name[0] = "R"
            name[1] = "X"
            unit[0] = "ohm"
            unit[1] = "ohm"
        elif Cmode == 2:
            name[0] = "G"
            name[1] = "B"
            unit[0] = "s"
            unit[1] = "s"
        elif Cmode == 10:
            name[0] = "Z"
            name[1] = "phi"
            unit[0] = "ohm"
            unit[1] = "rad"
        elif Cmode == 11:
            name[0] = "Z"
            name[1] = "phi"
            unit[0] = "ohm"
            unit[1] = "deg"
        elif Cmode == 20:
            name[0] = "Y"
            name[1] = "phi"
            unit[0] = "s"
            unit[1] = "rad"
        elif Cmode == 21:
            name[0] = "Y"
            name[1] = "phi"
            unit[0] = "s"
            unit[1] = "deg"
        elif Cmode == 100:
            name[0] = "Cp"
            name[1] = "G"
            unit[0] = "F"
            unit[1] = "S"
        elif Cmode == 101:
            name[0] = "Cp"
            name[1] = "D"
            unit[0] = "F"
            unit[1] = "Dis. Fac."
        elif Cmode == 102:
            name[0] = "Cp"
            name[1] = "Q"
            unit[0] = "F"
            unit[1] = "Qual. Fac."
        elif Cmode == 103:
            name[0] = "Cp"
            name[1] = "G"
            unit[0] = "F"
            unit[1] = "ohm"
        elif Cmode == 200:
            name[0] = "Cs"
            name[1] = "Rs"
            unit[0] = "F"
            unit[1] = "ohm"
        elif Cmode == 201:
            name[0] = "Cs"
            name[1] = "Rs"
            unit[0] = "F"
            unit[1] = "Dis. Fac."
        elif Cmode == 202:
            name[0] = "Cs"
            name[1] = "Rs"
            unit[0] = "F"
            unit[1] = "ohm"
        elif Cmode == 300:
            name[0] = "Lp"
            name[1] = "G"
            unit[0] = "G"
            unit[1] = "s"
        elif Cmode == 301:
            name[0] = "Lp"
            name[1] = "D"
            unit[0] = "H"
            unit[1] = "Dis. Fac."
        elif Cmode == 302:
            name[0] = "Lp"
            name[1] = "Q"
            unit[0] = "H"
            unit[1] = "Qual. Fac."
        elif Cmode == 303:
            name[0] = "Lp"
            name[1] = "Rp"
            unit[0] = "H"
            unit[1] = "ohm"
        elif Cmode == 400:
            name[0] = "Ls"
            name[1] = "Rs"
            unit[0] = "H"
            unit[1] = "ohm"
        elif Cmode == 401:
            name[0] = "Ls"
            name[1] = "D"
            unit[0] = "H"
            unit[1] = "Dis. Fac."
        elif Cmode == 402:
            name[0] = "Ls"
            name[1] = "Q"
            unit[0] = "H"
            unit[1] = "QualFac"

        return {"Name": name, "Unit": unit}

    ############################################################################################
    def compileRC(self, CMUChn, CMmode, CMrange):

        ret = "RC %d, %d" %(CMUChn, CMmode)
        if CMmode == 2:
            ret = "%s, %d\n" %(ret, CMrange)
        return ret

    def compileWTDCV(self, hold, delay, sdelay, tdelay, mdelay):

        ret = "WTDCV %f, %f" %(hold, delay)
        if sdelay != None:
            ret = "%s, %f" %(ret, sdelay)
            if tdelay != None:
                ret = "%s, %f" %(ret, tdelay)
                if mdelay != None:
                    ret = "%s, %f" %(ret, mdelay)
        ret = "%s\n" %(ret)
        return ret

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
                MonitorHeader[n] = "%s,%s" %(MonitorHeader[n], self.getCurrentRangeMode(RI[m]))
                n+=1
                MonitorHeader[n] = "%s,%s" %(MonitorHeader[n], self.getCurrentRangeBoundary(RI[m]))
            else:
                MonitorHeader[n] = "%s,%s" %(MonitorHeader[n], self.getVoltageRangeMode(RV[m]))
                n+=1
                MonitorHeader[n] = "%s,%s" %(MonitorHeader[n], self.getCurrentRangeBoundary(RV[m]))
            
            
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
        n = abs(n)
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
            ret = 'AUTO'
        elif n > 0:
            ret = 'LIMITED'
        elif n < 0:
            ret = 'FIXED'
        return ret