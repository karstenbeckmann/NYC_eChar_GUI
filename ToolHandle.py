"""
This file contains the Tool Handle class that handles the distribution of tool resources 
Written by: Karsten Beckmann
Date: 11/6/2018
email: kbeckmann@sunypoly.edu
"""

import sys
sys.path.append('Drivers')

from ctypes import *
import os as os
import pathlib as path
import csv as getModuleInformations
import time as tm
import numpy as np
import pyvisa as vs
import math as ma
import sys
import statistics as stat
import threading as th
import DataHandling as dh
import queue as qu
import StdDefinitions as std
import Drivers.Instruments as Inst
import copy as cp


class ToolHandle:

    InitializedInst = []
    instruments = None
    Warnings = qu.Queue()
    Errors = qu.Queue()
    AvailDevices = qu.Queue()
    readyQu = qu.Queue()
    threads = []
    ready = False

    supportedDevices = []
    #supportedDevices.append(['SUSS_PA300', 'Prober', "Suss MicroTec Test Systems GmbH,ProberBench PC"])
    supportedDevices.append(['SUSS_PA300', 'Prober', "Cascade MicroTech Dresden GmbH, ProberBench PC"])
    supportedDevices.append(['Cascade_CM300', 'Prober', "Cascade Microtech,Velox"])
    supportedDevices.append(['Cascade_S300', 'Prober', "Cascade Microtech, S300 Theta"])
    supportedDevices.append(['Agilent_B1500A', 'B1500A', 'Agilent Technologies,B1500A'])
    supportedDevices.append(['Keithley_707A', 'Matrix', "707A03"])
    supportedDevices.append(['Agilent_81110A', 'PG81110A', "HEWLETT-PACKARD,HP81110A"])
    supportedDevices.append(['BNC_Model765', 'PGBNC765', "ACTIVE TECHNOLOGIES,AT-PULSE-RIDER-PG1074"])
    supportedDevices.append(['LeCroy_WP740Zi', 'LeCroyOsc', 'LECROY,WP740ZI'])
    supportedDevices.append(['LeCroy_WR640Zi', 'LeCroyOsc', 'LECROY,WR640ZI'])
    supportedDevices.append(['Agilent_E5274A', 'E5274A', "Agilent Technologies,E5270A"])

    toolTypes = ['Prober', "Matrix", "B1500A", 'PG81110A', "PGBNC765", "B1530A", 'E5274A', 'LeCroyOsc']

    WGFMU_Channels = []
    SMUs = []

    def __init__(self, B1530ADLL="C:/Windows/System32/wgfmu.dll", offline = False):

        self.CurrentProberAdr = None
        self.CurrentMatrixAdr = None
        self.ChuckTemp = "--"
        self.offline = offline

        try:
            self.rm = vs.ResourceManager()
        except (SystemError) as e:
            err = "Please install the NI visa software. Error: %s" %(e)
            self.Errors.put(err)
            raise SystemError(err)
        
        self.addSupportedDevices()

        self.B1530ADLL = B1530ADLL
        if not offline:
            self.Initialize()
        self.ready = True
    
    def addSupportedDevices(self):
        self.init = {"Instrument": None, "GPIB": None, "Model": "", "Company": "", "Busy": False, "Status": None, "Rank": None}
        n = 0
        for dev in self.supportedDevices:
            self.AvailDevices.put({dev[1]: False})
            self.InitializedInst.append(cp.deepcopy(self.init))
            self.InitializedInst[n]['Identifier'] = dev[2]
            self.InitializedInst[n]['Class'] = dev[0]
            self.InitializedInst[n]['Type'] = dev[1]
            n = n + 1
    
    def getToolTypes(self):
        return self.toolTypes

    def ReInitialize(self):
        self.readyQu.put(False)
        tm.sleep(0.1)
        self.WGFMU_Channels = []
        self.SMU_Positions = []
            
        self.close()
        self.InitializedInst = []
        self.addSupportedDevices()

        try:
            self.rm = vs.ResourceManager()
        except:
            raise SystemError("Please install the NI visa software.")
        if not self.offline:
            try:
                self.Initialize()
                self.readyQu.put(True)
            except (ValueError, SystemError, vs.VisaIOError) as e:
                war = "Initialization of Devices Failed! Error: %s" %(e)
                self.Warnings.put(war)

    def Initialize(self):
        self.instruments = self.rm.list_resources()
        ##### check for valid GPIB address - error on SEM01 showing too many GPIB addresses

        tempInst = []
        for inst in self.instruments:

            if inst.split("::")[0].lower().find("gpib") != -1:
                if inst.split("::")[2].lower() != "instr":
                    continue

            tempInst.append(inst)
        
        self.instruments = tuple(tempInst)
        for GPIB in self.instruments:
            try:
                instrument = self.rm.open_resource(GPIB)
            except vs.VisaIOError as e:
                continue
            if GPIB.find("GPIB") != -1 or GPIB.find("TCPIP") != -1:

                try:
                    stb = instrument.write("*RST")
                    tm.sleep(0.05)
                except:
                    None

                tryTime = 1
                curTime = 0
                TimeStep = 0.1
                contin = False
                while tryTime > curTime:
                    
                        
                    try:
                        stb = instrument.query("*STB?")
                        
                        try:
                            stb = int(stb)
                        except ValueError:
                            stb = int(stb.split(" ")[1].strip())
                            
                    except (vs.VisaIOError, TypeError, ValueError):
                        try:
                            stb = instrument.read_stb()
                        except vs.VisaIOError:
                            contin = True
                            break
                    try:
                        stb = int(stb)
                    except ValueError:
                        try:
                            stb = int(stb.split(" ")[1].strip())
                        except:
                            contin = True
                            break
                    
                    binStb = std.getBinaryList(int(stb))
                    err = binStb[5]
                    mes = None
                    if err == 1:
                        instrument.write("*esr?")
                        tm.sleep(0.1)
                        try:
                            mes = instrument.read()
                            war = "Initialization Failed with %s. (code: %s)" %(GPIB, mes.strip())
                            self.Warnings.put(war)
                        except vs.VisaIOError as e:
                            self.Warnings.put("Initialization Failed with %s. (code: %s)" %(GPIB, e))
                    else:
                        break
                
                    tm.sleep(0.01)
                    curTime = curTime + TimeStep
                if contin:
                    continue
                try:
                    instrument.write("*IDN?")
                except vs.VisaIOError as e:
                    self.Warnings.put("Initialization Failed with %s. (code: %s)" %(GPIB, e))
                    continue
                
                tm.sleep(0.01)
                try:
                    ret = instrument.read()
                    n = 0
                    addInstruments = []
                    for initInst in self.InitializedInst:
                        #print(initInst["Identifier"], " and ", ret, " and ", GPIB)
                        if ret.find(str(initInst["Identifier"])) != -1:
                            #print("found")
                            if initInst["Identifier"] != None:
                                try:
                                    Class = getattr(Inst, self.InitializedInst[n]['Class'])
                                except (SystemError, ValueError) as e:
                                    self.Errors.put("ToolHandle:", e)
                                    continue
                                try:
                                    DevClass = Class(Device=instrument)
                                except (SystemError) as e:
                                    self.Errors.put("ToolHandle:", e)
                                    continue
                                self.InitializedInst[n]['Instrument'] = DevClass 
                                self.InitializedInst[n]['GPIB'] = GPIB
                                self.InitializedInst[n]['Model'] = ret
                                self.InitializedInst[n]['Rank'] = self.getNextAvailableRank(initInst["Type"])
                                self.InitializedInst[n]["Busy"] = False
                                self.AvailDevices.put({self.InitializedInst[n]["Type"]: True})

                                if str(self.InitializedInst[n]["Identifier"]).find("Agilent Technologies,B1500A") != -1:
                                    
                                    instrument.write("UNT? 0\n")
                                    tm.sleep(0.1)
                                    ret = instrument.read()
                                    modules = ret.strip().split(';')
                                    n=1
                                    self.SMUChns = []
                                    for module in modules:
                                        module = module.split(',')[0]
                                        #if module == "B1511A" or module == "B1510A" or module =="B1517A":
                                        #    self.SMUChns.append(n)
                                        if module == "B1530A": 
                                            try:
                                                tool = "B1530A"
                                                B1530A = WinDLL(self.B1530ADLL)
                                                DevClass = Inst.Agilent_B1530A(GPIB, B1530A, online=True, calibration=False, selfTest=False, B1500=self.InitializedInst[n]['Instrument'])
                                                addInstruments.append(dict())
                                                ID = len(addInstruments)-1
                                                addInstruments[ID]['Instrument'] = DevClass 
                                                addInstruments[ID]['GPIB'] = GPIB
                                                addInstruments[ID]['Model'] = ret
                                                addInstruments[ID]["Busy"] = False
                                                addInstruments[ID]['Rank'] = self.getNextAvailableRank("B1530A")
                                                addInstruments[ID]["Identifier"] = 'Agilent Technologies,B1500A'
                                                addInstruments[ID]["Type"] = "B1530A"
                                                addInstruments[ID]['Class'] = "Agilent_B1530A"
                                                addInstruments[ID]['Status'] = None
                                                self.AvailDevices.put({tool: True})
                                                Chans = DevClass.getChannelIDs()
                                                self.WGFMU_Channels = Chans['Channels']
                                            except (vs.VisaIOError, OSError) as e:
                                                self.Warnings.put("Initialization Failed for B1530")
                                        
                                        n+=1
                            else:
                                addInstruments.append(dict())
                                ID = len(addInstruments)-1
                                Class = getattr(Inst, self.InitializedInst[n]['Class'])
                                DevClass = Class(Device=instrument)
                                ID = len(self.InitializedInst)-1
                                addInstruments[ID]['Instrument'] = DevClass 
                                addInstruments[ID]['GPIB'] = GPIB
                                addInstruments[ID]['Model'] = ret
                                addInstruments[ID]["Busy"] = False
                                addInstruments[ID]["Identifier"] = initInst["Identifier"]
                                addInstruments[ID]["Type"] = initInst["Type"]
                                addInstruments[ID]["Class"] = initInst["Class"]
                                addInstruments[ID]['Status'] = None
                                addInstruments[ID]['Rank'] = self.getNextAvailableRank(initInst["Type"])
                        
                        n = n+1
                    self.InitializedInst.extend(addInstruments)    

                except (vs.VisaIOError, ValueError) as e:
                    self.Warnings.put("Initialization Failed with %s. (code: %s)" %(GPIB, e))

        Instr = self.__getInstrumentsByType('Prober')
        if len(Instr) > 0: 
            n= 0
            for inst in Instr:
                if Instr[n]['GPIB'] != None and Instr[n]['Rank']:
                    self.setCurrentProber(Instr[n]['GPIB'])
                    break
                n = n+1
        
        Instr = self.__getInstrumentsByType('Matrix')
        if len(Instr) > 0: 
            n= 0
            for inst in Instr:
                if Instr[n]['GPIB'] != None and  Instr[n]['Rank']:
                    self.setCurrentMatrix(Instr[0]['GPIB'])
                    break
                n = n+1

    def isTypePresent(self, tool, gpib=None):
        
        for inst in self.InitializedInst:
            if inst['Instrument'] == None:
                continue
            if inst['Type'] == tool:
                return True
        return False
    
    def getNextAvailableRank(self, typ):

        ranks = []
        for inst in self.InitializedInst:
            if inst['Instrument'] != None and inst['Type'] == typ and inst['Rank'] != None:
                ranks.append(inst['Rank'])
        ranks.sort()

        n = 1
        for r in ranks:
            if r != n:
                return n
            n = n+1
        return n

    def getSupportedDeviceTypes(self):
        return [x[1] for x in self.supportedDevices]

    def getInstrument(self, address):
        if not self.ready:
            return None

        n = 0
        for inst in self.InitializedInst:
            if self.InitializedInst[n]['GPIB'] == address:
                return self.InitializedInst[n]
            n = n+1
        
        raise ValueError("ToolHandle: Instrument Address - %s - doesnt exist." %(address))
    
    def getProber(self):
        if not self.ready:
            return None
        Instr = self.getInstrumentsByType('Prober')
        for inst in Instr:
            if inst['GPIB'] == self.CurrentProberAdr:
                return inst
        return None
#       self.Warnings.put("Tool Handle: No prober available!")

    def getProberInstrument(self):
        if not self.ready:
            return None
        Instr = self.getInstrumentsByType('Prober')
        for inst in Instr:
            if inst['GPIB'] == self.CurrentProberAdr:
                return inst["Instrument"]
        try:
            return Instr[0]["Instrument"]
        except:
            return None
            #self.Warnings.put("Tool Handle: No prober available!")

    def getChuckTemperature(self):
        if not self.ready:
            return None
        return self.ChuckTemp

    def getMatrix(self):
        if not self.ready:
            return None
        Instr = self.getInstrumentsByType('Matrix')
        for inst in Instr:
            if inst['Rank']:
                return inst
        try:
            return Instr[0]
        except:
            self.Warnings.put("Tool Handle: No Matrix available! Err 1")

    def getMatrixInstrument(self):
        if not self.ready:
            return None
        Instr = self.getInstrumentsByType('Matrix')
        for inst in Instr:
            if inst['Rank']:
                return inst["Instrument"]
        try:
            return Instr[0]["Instrument"]
        except:
            self.Warnings.put("Tool Handle: No Matrix available! Err 0")

    def getInstrumentsByName(self, Name):
        if not self.ready:
            return []
        retInst = []
        n = 0
        for inst in self.InitializedInst:
            if self.InitializedInst[n]['Class'] == Name:
                retInst.append(self.InitializedInst[n])
            n = n+1
        
        return retInst

    def getInstrumentsByType(self, typ):
        if not self.ready:
            return []
        retInst = []
        n = 0
        for inst in self.InitializedInst:
            if self.InitializedInst[n]['Type'] == typ:
                retInst.append(self.InitializedInst[n])
            n = n+1
        
        return retInst

    def getRanksForTools(self, typ):
        ranks = []
        for inst in self.InitializedInst:
            if inst['Type'] == typ and inst['GPIB'] != None:
                ranks.append(inst['Rank'])
        
        ranks.sort()
        return ranks


    def getToolRank(self, GPIB):

        for inst in self.InitializedInst:
            if inst["GPIB"] == GPIB:
                return inst['Rank']

        return 0

    def setToolRank(self, GPIB, rank):
        if not isinstance(rank, int):
            return False
        typ = 0
        oldRank = 0
        instChange = None
        for inst in self.InitializedInst:
            if inst["GPIB"] == GPIB:
                typ = inst['Type']
                oldRank = inst['Rank']
                instChange = inst
                break
        if instChange == None:
            return False
        if oldRank == rank:
            return True
        for inst in self.InitializedInst:
            if inst['Type'] == typ and inst['GPIB'] != None and inst['GPIB'] != GPIB:
                if inst['Rank'] >= rank and inst['Rank'] < oldRank:
                    inst['Rank'] = inst['Rank'] + 1
                if inst['Rank'] <= rank and inst['Rank'] > oldRank:
                    inst['Rank'] = inst['Rank'] - 1
        return True
        

    def __getInstrumentsByType(self, typ):
        retInst = []
        n = 0
        for inst in self.InitializedInst:
            if self.InitializedInst[n]['Type'] == typ:
                retInst.append(self.InitializedInst[n])
            n = n+1
        
        return retInst

    def __getInstrumentsByName(self, Name):
        retInst = []
        n = 0
        for inst in self.InitializedInst:
            if self.InitializedInst[n]['Class'] == Name:
                retInst.append(self.InitializedInst[n])
            n = n+1
        
        return retInst

    def getAvailableTools(self):
        if not self.ready:
            return []
        devices = []
        for inst in self.InitializedInst:
            if inst["Instrument"] != None:
                devices.append(inst['Class'])
        return devices
    
    def getAvailableInstruments(self):
        if not self.ready:
            return []
        '''
        same as getAvailableTools()
        '''
        devices = []
        for inst in self.InitializedInst:
            if inst["Instrument"] != None:
                devices.append(inst['Class'])
        return devices

    def getAvailableToolsComplete(self):
        if not self.ready:
            return []
        devices = []
        for inst in self.InitializedInst:
            if inst["Instrument"] != None:
                devices.append(inst)
        return devices

    def getAvailableInstrumentsComplete(self):
        if not self.ready:
            return []
        devices = []
        for inst in self.InitializedInst:
            if inst["Instrument"] != None:
                devices.append(inst)
        return devices

    def InstrumentCalibration(self, address=None, ID=None):        
        instrument = None

        tm.sleep(0.1)
        
        if address != None:
            n = 0
            for inst in self.InitializedInst:
                if inst["GPIB"] == address:
                    instrument = self.InitializedInst[n]
                    break
                n = n+1
        elif ID != None:
            try: 
                instrument = self.InitializedInst[ID]
                address = self.InitializedInst[ID]['GPIB']
            except:
                raise ValueError("ToolHandle: Calibration - either GPIB or ID must be defined and valid!")
        
        if instrument == None:
            raise ValueError("ToolHandle: Calibration - either GPIB or ID must be defined and valid!")

        thread = None
        
        if instrument['Instrument'] != None:
            if not instrument["Busy"]:
                self.readyQu.put([address, True])
                thread = th.Thread(target=self.CalibrationThread, args=(instrument['Instrument'].performCalibration,address))
                self.threads.append(thread)
                thread.start()
            else:
                self.Warnings.put("%s is currently busy." %(instrument['Class']))

        return thread

    def setCurrentProber(self, GPIB):

        self.setToolRank(GPIB, 1)
        self.CurrentProberAdr = GPIB
    
    def setCurrentMatrix(self, GPIB):
        self.setToolRank(GPIB, 1)
        self.CurrentMatrixAdr = GPIB

    def InstrumentReset(self, address=None, ID=None):
        
        if not self.ready:
            return None
       
        instrument = None

        if address != None:
            n = 0
            for inst in self.InitializedInst:
                if inst["GPIB"] == address:
                    instrument = self.InitializedInst[n]
                n = n+1
        elif ID != None:
            try: 
                instrument = self.InitializedInst[ID]
                address = self.InitializedInst[ID]['GPIB']
            except:
                raise ValueError("ToolHandle: Calibration - either GPIB or ID must be defined and valid!")
        if instrument == None:
            raise ValueError("ToolHandle: Calibration - either GPIB or ID must be defined and valid!")
        
        thread = None
        if instrument['Instrument'] != None:
            if not instrument["Busy"]:
                self.readyQu.put([address, False])
                thread = th.Thread(target=self.CalibrationThread, args=(instrument['Instrument'].initialize,address))
                self.threads.append(thread)
                thread.start()
            else:
                self.Warnings.put("%s is currently busy." %(instrument['Class']))
        
        return thread
        
    def CalibrationThread(self, func, tool):
        try: 
            tm.sleep(0.1)
            ret = func()
            self.Warnings.put(ret)
        except: 
            self.Warnings.put("Calibration is not available for: %s" %(tool))

        self.readyQu.put([tool, True])

    def ResetThread(self, func, tool):
        try: 
            ret = func()
            self.Warnings.put(ret)
        except: 
            self.Warnings.put("Reset/Initialization is not available for: %s" %(tool))

        self.readyQu.put([tool, False])

    def close(self):
        try:
            self.instruments = self.rm.list_resources()
            for adr in self.instruments:
                for inst in self.InitializedInst:
                    if inst['GPIB'] == adr:
                        inst['Instrument'].turnOffline()
        except (vs.VisaIOError, vs.InvalidSession):
            None
        try:
            self.rm.close()
        except (vs.VisaIOError, vs.InvalidSession):
            None

    def getPrimaryTool(self, typ):
        for inst in self.InitializedInst:
            if inst['Type'] == typ and inst["GPIB"] != None and inst['Rank'] == 1:
                return inst
        return None

    def updateThread(self, MainGI):
        None

    def update(self, MainGI):
        
        for inst in self.InitializedInst:

            try:
                logQueue = inst['Instrument'].getLogQueue()
                while not logQueue.empty():
                    self.Warnings.put(logQueue.get())
            except AttributeError:
                None

        while not self.readyQu.empty():
            get = self.readyQu.get()
            try: 
                get = bool(get)
                if get == False:
                    self.ready = False
                elif get:
                    self.ready = True
            except TypeError:
                n = 0
                for inst in self.InitializedInst:
                    if inst["GPIB"] == get[0]:
                        self.InitializedInst[n]["Busy"] = (not bool(get[1]))
                        break
                    n = n+1

        if not MainGI.isRunning():
            Prober = self.getProber()
            if Prober != None:
                if Prober['Instrument'] != None:
                    if not Prober['Busy']:
                        try:
                            self.ChuckTemp = Prober['Instrument'].ReadChuckThermoValue()[0]
                        except:
                            SystemError("ToolHandle: Prober is offline.")
                else:
                    self.ChuckTemp = "--"

        for initInst in self.InitializedInst:
            if initInst['Type'] == 'B1530A':
                initInst['Status'] = None
                while not initInst['Instrument'].StatusQueue.empty():
                    status =  initInst['Instrument'].StatusQueue.get()
                    if status != initInst['Status']:
                        self.Warnings.put("ToolHandle: %s" %(status))
                while not initInst['Instrument'].ErrQueue.empty():
                    err = initInst['Instrument'].ErrQueue.get()
                    self.Errors.put("ToolHandle: %s" %(err))
                

    def checkInstrumentation(self, Instruments=None):
        
        if isinstance(Instruments, type([])):
            for instr in Instruments:
                if instr != None:
                    self.getInstrumentsByName(instr)['Instrument'].clearLibrary()
                    self.getInstrumentsByName(instr)['Instrument'].turnOnline()
                    self.getInstrumentsByName(instr)['Instrument'].initialize()
                    self.getInstrumentsByName(instr)['Instrument'].turnOffline()
                    
                    for n in range(3):
                        try: 
                            ret = self.getInstrumentsByName(instr)['Instrument'].doSelfTest()
                            try: 
                                errInt = int(ret)
                            except (SystemError, ValueError, AttributeError) as e:
                                errInt = int(ret.split(":")[0])
                                self.Errors.put("ToolHandle: %s" %(e))

                            if errInt == 0:
                                err = 0
                                break
                            else:
                                err = errInt 
                        except (SystemError, ValueError, AttributeError) as e:
                            err = 1 
                            self.Errors.put("ToolHandle: %s" %(e))
                    if err != 0:
                        raise SystemError(ret)
        elif Instruments == None:
            for inst in self.InitializedInst:
                if inst['Instrument'] != None:
                    if inst['Type'] == "B1530A":
                        inst['Instrument'].clearLibrary()
                        inst['Instrument'].turnOnline()
                        err = 0
                        for n in range(3):
                            try: 
                                try:
                                    ret = inst['Instrument'].getError()
                                    self.Errors.put("ToolHandle: %s" %(ret))
                                except OSError:
                                    self.Errors.put("ToolHandle: No error on the tool.")

                                inst['Instrument'].reset()

                                #ret = inst['Instrument'].doSelfTest()
                                #self.Errors.put("ToolHandle B1530A selfTest: %s" %(ret))
                                ret = inst['Instrument'].initialize()
                                self.Errors.put("ToolHandle B1530A initialize: %s" %(ret))
                                inst['Instrument'].turnOffline()
                                try: 
                                    errInt = int(ret)
                                except (SystemError, ValueError, AttributeError) as e:
                                    errInt = int(ret.split(":")[0])
                                    self.Errors.put("ToolHandle: %s" %(e))

                                if errInt == 0:
                                    err = 0
                                    break
                                else:
                                    err = errInt 

                            except (SystemError, ValueError, AttributeError) as e:
                                err = 1 
                                self.Errors.put("ToolHandle: %s" %(e))
                            
                            twait = 20
                            for n in range(twait):
                                print("wait for Tool %d/%ds" %(n,twait))
                                tm.sleep(1)
                        
                        if err != 0:
                            msg = "ToolHandle: checkInstrumentation after 3 recoverings: %s" %(err)
                            self.Errors.put(msg)
                            raise SystemError(msg)

                    if inst['Type'] == "B1500A":
                        inst['Instrument'].clear()
                        err = 0
                        for n in range(3):
                            try:
                                ret = inst['Instrument'].SelfTest()
                                self.Errors.put("ToolHandle B1500A selfTest: %s" %(ret))
                                if int(ret) == 0:
                                    err = 0
                                    break
                                else:
                                    err = 1
                            except (SystemError, ValueError) as e:
                                err = 1
                        if err != 0:
                            msg = "ToolHandle: checkInstrumentation after 3 recoverings: %s" %(err)
                            self.Errors.put(msg)
                            raise SystemError(msg)
                    if inst['Type'] == "PG":
                        inst['Instrument'].reset()
                        err = 0
                        for n in range(3):
                            try:
                                ret = inst['Instrument'].doSelfTest()
                                self.Errors.put("ToolHandle %s selfTest: %s" %(inst['Class'], ret))
                                if int(ret) == 0:
                                    break
                                else:
                                    err = int(ret.split(":")[0]) 
                            except (SystemError, ValueError) as e:
                                None
                        if err != 0:
                            msg = "ToolHandle: checkInstrumentation after 3 recoverings: %s" %(err)
                            self.Errors.put(msg)
                            raise SystemError(msg)


    def changeADC(self, MainGI, gpib, typ, mod, n):

        if not MainGI.isRunning():
            tool = self.getInstrument(gpib)['Instrument']
            try:
                n = int(n)
                tool.SetADCConverter(typ, mod, N=n)
                return True
            except (ValueError, SystemError) as e:
                self.Errors.put("Changing ADC error - GPIB: %s - Type: %s - mod: %s - n: %s - Error: %s" %(gpib, typ, mod, n, e))
                return False
        else:
            self.Errors.put("Changing ADC error - Measurement is currently running.")
            return False

    def setADC(self, MainGI, gpib, typ, smu):

        if not MainGI.isRunning():
            tool = self.getInstrument(gpib)['Instrument']
            try:
                tool.SetADC(typ, smu)
                return True
            except (ValueError, SystemError) as e:
                self.Errors.put("Changing ADC error - GPIB: %s - SMU: %s, Type: %s - Error: %s" %(gpib, smu, typ, e))
                return False
        else:
            self.Errors.put("Changing ADC error - Measurement is currently running.")
            return False

    def getModuleInformations(self, gpib):
        
        tool = self.getInstrument(gpib)['Instrument']
        try:
            desc = tool.getSMUDescriptions()
        except AttributeError:
            desc = None    
            self.Errors.put("%s is not a Keysight Mainframe (i.e. B1500A)" %(gpib))
        return desc

    def getModuleInformation(self, gpib, smu):
        
        tool = self.getInstrument(gpib)['Instrument']
        try:
            desc = tool.getSMUDescriptions()
        except AttributeError:
            desc = None    
            self.Errors.put("%s is not a Keysight Mainframe (i.e. B1500A)" %(gpib))

        n = 1
        out = ""
        for key, val in desc.items():
            if n == smu:
                out = val
                break
            n = n+1
        return {key:out}

    