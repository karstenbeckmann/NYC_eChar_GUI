"""
This file contains the Tool Handle class that handles the distribution of tool resources 
Written by: Karsten Beckmann
Date: 11/6/2018
email: kbeckmann@sunypoly.edu
"""

from multiprocessing.sharedctypes import Value
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
    commandSleep = 1
    commandQueue = qu.Queue()
    commandReturnQueue = qu.Queue()
    proberChuckStatus = None
    proberScopeStatus = None
    proberStatus = None
    cmdThread = None

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

    def __init__(self, B1530ADLL="C:/Windows/System32/wgfmu.dll", offline = False, threadTimeOut=200):

        self.CurrentProberAdr = None
        self.CurrentMatrixAdr = None
        self.ChuckTemp = "--"
        self.offline = offline
        self.commandQueue = qu.Queue()
        self.commandReturnQueue = qu.Queue()
        self.threadTimeout = 200 #in milliseconds
        self.toolStatusUpdate = 500 #in milliseconds
        self.tupdateOld = tm.time_ns() #old tool update time in ns

        try:
            self.rm = vs.ResourceManager()
        except (SystemError, ValueError) as e:
            err = "Please install the NI visa software. Error: %s" %(e)
            self.Errors.put(err)
            offline = True
            #raise SystemError(err)
        
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
                                self.InitializedInst[n]["ConnectedDevices"] = []
                                self.AvailDevices.put({self.InitializedInst[n]["Type"]: True})

                                if str(self.InitializedInst[n]["Identifier"]).find("Agilent Technologies,B1500A") != -1:
                                    
                                    instrument.write("UNT? 0\n")
                                    tm.sleep(0.1)
                                    ret = instrument.read()
                                    modules = ret.strip().split(';')
                                    l=1
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
                                                addInstruments[ID]['Status'] = self.InitializedInst[n]["Status"]
                                                self.InitializedInst[n]["ConnectedDevices"].append(addInstruments[ID])
                                                
                                                self.AvailDevices.put({tool: True})
                                                Chans = DevClass.getChannelIDs()
                                                self.WGFMU_Channels = Chans['Channels']
                                            except (vs.VisaIOError, OSError) as e:
                                                self.Warnings.put("Initialization Failed for B1530")
                                        
                                        l+=1
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
                                addInstruments[ID]['Status'] = 0
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

        while not self.commandQueue.empty():
            cmd = self.commandQueue.get()
            cmd = None

        self.cmdThread = th.Thread(target=self.commandThread, args=(self.commandQueue, self.Errors, self.commandSleep, self.threadTimeout))
        self.cmdThread.start()

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

    def queueCommand(self, instr, returnQueue, command, args=None, kwargs=None):
        com = {"Instr": instr, "Command": command, "ReturnQueue": returnQueue}
        if args != None:
            com["Args"] = args
        if kwargs != None:
            com["Kwargs"] = kwargs
        
        self.commandQueue.put(com)

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

    def getProberStatus(self):
        return self.proberStatus
    
    def getProberChuckStatus(self):

        pStat = self.proberChuckStatus
        if self.proberChuckStatus == None:
            pStat = [0,0,0,0,0,0,0,0,0,0]

        ret = {}
        ret['IsInitialized'] = std.getIntegerToBinaryArray(pStat[0], 4)
        ret['Mode'] = std.getIntegerToBinaryArray(pStat[1], 8)
        ret['OnEndLimit'] = std.getIntegerToBinaryArray(pStat[2],8)
        ret['IsMoving'] = std.getIntegerToBinaryArray(pStat[3],4)
        ret['CompMode'] = pStat[4]
        ret['Vacuum'] = std.getIntegerToBinaryArray(pStat[5],1)
        ret['ZHeight'] = pStat[6]
        ret['Load Position'] = std.getIntegerToBinaryArray(pStat[7],2)
        ret['Lift'] = std.getIntegerToBinaryArray(pStat[8], 1)
        ret['ChuckCamera'] = pStat[9]

        return ret
        
    def getProberScopeStatus(self):
        
        pStat = self.proberScopeStatus
        if self.proberScopeStatus == None:
            pStat = [0,0,0,0,0,0,0,0]

        ret = {}
        ret['IsInitialized'] = std.getIntegerToBinaryArray(pStat[0], 3)
        ret['OnEndLimit'] = std.getIntegerToBinaryArray(pStat[1], 6)
        ret['IsMoving'] = std.getIntegerToBinaryArray(pStat[2], 3)
        ret['CompMode'] = pStat[3]
        ret['CompMode'] = pStat[4]
        ret['ZHeight'] = pStat[5]
        ret['ScopeLIght'] = std.getIntegerToBinaryArray(pStat[6], 1)
        ret['Mode'] = std.getIntegerToBinaryArray(pStat[7], 8)
        
        return ret
        
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
        cmd = {"Stop":True}
        self.commandQueue.put(cmd)
        try:
            self.instruments = self.rm.list_resources()
            for adr in self.instruments:
                for inst in self.InitializedInst:
                    if inst['GPIB'] == adr:
                        inst['Instrument'].turnOffline()
        except (AttributeError, vs.VisaIOError, vs.InvalidSession):
            None
        try:
            self.rm.close()
        except (AttributeError, vs.VisaIOError, vs.InvalidSession):
            None

    def getPrimaryTool(self, typ):
        for inst in self.InitializedInst:
            if inst['Type'] == typ and inst["GPIB"] != None and inst['Rank'] == 1:
                return inst
        return None

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
            self.commandQueue.put({"Pause": False})
            Prober = self.getProber()
            
            # Processing returning command over GPIB
            while not self.commandReturnQueue.empty():
                try: 
                    ret = self.commandReturnQueue.get()
                    cmd = ret["Command"]
                    retData = ret["Return"]
                    retInstr = ret['Instr']
                    errMsg = ret['ErrorMsg']
                    err = ret['Error']

                    if err:
                        msg = "ToolHandle: Error in executing command '%s' - %s" %(cmd, errMsg)
                        self.Errors.put(msg)
                    else:
                        if cmd == "ReadChuckThermoValue":
                            self.ChuckTemp = retData[0]
                        if cmd == "ReadChuckStatus":
                            self.proberChuckStatus = retData
                        if cmd == "ReadScopeStatus":
                            self.proberScopeStatus = retData
                        if cmd =="*STB?":
                            retInstr['Status'] = retData
                            try:
                                for dev in retInstr['ConnectedDevices']:
                                    dev['Status'] = retData
                            except KeyError:
                                None
                except (IndexError, ValueError) as e:
                    self.Errors.put("Instruments: %s" %(e))

            #Sent command ommand over GPIB every self.toolStatusUpdate
            tupdate = self.toolStatusUpdate * 1000 * 1000
            if self.tupdateOld + tupdate < tm.time_ns():
                self.tupdateOld = tm.time_ns()

                if Prober != None:
                    if Prober['Instrument'] != None:
                        if not Prober['Busy']:
                            cmd = {"Command": "ReadChuckThermoValue", "ReturnQueue": self.commandReturnQueue, 'Instr': Prober}
                            self.commandQueue.put(cmd)
                            cmd = {"Command": "ReadChuckStatus", "ReturnQueue": self.commandReturnQueue, 'Instr': Prober}
                            self.commandQueue.put(cmd)
                            cmd = {"Command": "ReadScopeStatus", "ReturnQueue": self.commandReturnQueue, 'Instr': Prober}
                            self.commandQueue.put(cmd)
                    else:
                        self.ChuckTemp = "--"

                for inst in self.InitializedInst:
                    if not inst["Busy"]:
                        if inst['Instrument'] != None and inst['Type'] != "B1530":
                            cmd = {"Command": "*STB?", "ReturnQueue": self.commandReturnQueue, 'Instr': inst}
                            self.commandQueue.put(cmd)

            if self.cmdThread == None:
                self.cmdThread = th.Thread(target=self.commandThread, args=(self.commandQueue, self.Errors, self.commandSleep))
                self.cmdThread.start()
            else:
                if not self.cmdThread.is_alive():
                    self.cmdThread = th.Thread(target=self.commandThread, args=(self.commandQueue, self.Errors, self.commandSleep))
                    self.cmdThread.start()
            
        else:
            self.commandQueue.put({"Pause": True})



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
                
    def commandThread(self, commandQueue, errorQueue, sleep, timeout=200):
        
        #transfer timeout from milliseconds in nanoseconds
        timeout = timeout*1000*1000
        error = False

        activeTime = tm.time_ns()
        pause = False

        while True:
            if commandQueue.empty():
                
                if activeTime + timeout < tm.time_ns():
                    break
                tm.sleep(sleep)
                continue

            else:
                cmd = commandQueue.get()
                activeTime = tm.time_ns()
                error = False

            try:
                if cmd['Stop']:
                    break
            except KeyError:
                None
            
            try:
                if cmd['Pause']:
                    pause = True
                    while not commandQueue.empty():
                        ret = commandQueue.get()
                        ret = None
                    pause = True
                    continue
                else:
                    pause = False
                    continue

            except KeyError:
                None

            if pause:
                continue
                
            
            try:
                retQu = cmd['ReturnQueue']
                command = cmd['Command']
                inst = cmd['Instr']['Instrument']
                typ = cmd['Instr']['Type']
                busy = cmd['Instr']['Busy']
                try:
                    args = cmd['Args']
                except KeyError:
                    args = tuple()

                if args == None:
                    args = tuple()
                if args == "":
                    args = tuple()

                try:
                    kwargs = cmd['Kwargs']
                except KeyError:
                    kwargs = dict()

                if kwargs == None:
                    kwargs = dict()
                if kwargs == "":
                    kwargs = dict()
                
                if inst == None:
                    continue
                    
                if busy:
                    continue

                if command == "*STB?" and typ != "B1530A":
                    try:
                        stb = inst.instQuery("*STB?")
                        
                        try:
                            stb = int(stb)
                        except ValueError:
                            stb = int(stb.split(" ")[1].strip())                            
                    except (vs.VisaIOError, TypeError, ValueError):
                        try:
                            stb = inst.read_stb()
                        except vs.VisaIOError:
                            error = True
                            break
                    if error:
                        stb = None
                    else:
                        try:
                            stb = int(stb)
                        except (TypeError,ValueError):
                            try:
                                stb = int(stb.split(" ")[1].strip())
                            except:
                                error = True
                                stb = None
                                break
                    
                    if error:
                        msg = "Error during serial polling - %s." %(typ)
                        ret = {"Command": command, "Instr": cmd['Instr'], "Return": None, "Error": True, "ErrorMsg":msg}

                    else:
                        binStb = std.getBinaryList(int(stb))
                        ret = {"Command": command, "Instr": cmd['Instr'], "Return": binStb, "Error": False, "ErrorMsg":""}
                    
                    retQu.put(ret)
                elif typ != "B1530A":
                    try:
                        func = getattr(inst,command)
                        cmdRet = func(*args, **kwargs)
                        ret = {"Command": command, "Instr": cmd['Instr'], "Return": cmdRet, "Error": False, "ErrorMsg":""}
                    except Exception as e:
                        ret = {"Command": command, "Instr": cmd['Instr'], "Return": None, "Error": True, "ErrorMsg": e}
                        errorQueue.put("Command Execution error - Instrument: %s, Command: %s, Error: %s." %(typ, command, e))
                
                retQu.put(ret)

            except KeyError:
                errorQueue.put("ToolHandle: InstrumentCommand could not be interpreted - %s." %(cmd))


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

    