"""
Written by: Karsten Beckmann and Maximillian Liehr
Institution: SUNY Polytechnic Institute
Date: 6/12/2018

For more information please use the Keithley A707 matix manual.
"""
import numpy as np 
import pyvisa as vs 
import datetime as dt 
import types as tp
import StdDefinitions as std
import time as tm


#LeCroy WavePro 740Zi Oscilloscope: 
class LeCroy_WP740Zi():

    printOutput = False

    def __init__(self, rm=None, adr=None, Device=None, reset=False, calibration=False, printOutput=False, timeout=5, maxIdleInteration=10):
        
        self.timeout = timeout
        self.maxIdleInteration = maxIdleInteration
        self.printOutput = printOutput
        self.inst=None
        if (rm == None or adr == None) and Device == None:
            self.write("Either rm and GPIB_adr or a device must be given transmitted")  #maybe a problem, tranmitting None type
        elif Device == None:    

            try:
                self.inst = rm.open_resource(adr)
                
            except:
                self.write("The device %s does not exist." %(adr))  #maybe a problem, tranmitting None type
        
        else:
            self.inst = Device
            
        self.inst.write("*SRE 1")
        ret = self.instQuery("InstrumentID")
        if not ret.lower().find("lecroy,wp740zi,") == -1:
            self.write("You are using the %s" %(ret[:-2]))
        else:
            #print("You are using the wrong agilent tool!")
            exit("You are using the wrong agilent tool!")

        self.inst.write("COMM_HEADER OFF")
        self.inst.write(r"""vbs 'app.settodefaultsetup' """)
        
        if calibration: 
            self.calibration()
        
        if reset:
            self.initialize()

    def turnOffline(self):
        self.inst.close()

    def write(self, com):
        if self.printOutput:
            print("WavePro 740Zi: ", com)

    def initialize(self):
        self.instWrite("app.settodefaultsetup")
        self.instWrite("app.measure.clearall")
        self.instWrite("app.measure.clearsweeps")
        self.instWrite('app.acquisition.triggermode = "stopped"')

    def getModel(self):
        ret = self.instQuery("InstrumentID")
        return ret

    def instWrite(self, command, value = None):
        if value != None: 
            if isinstance(value, str):
                command = '%s = "%s"' %(command, value)
            elif isinstance(value, float):
                command = '%s = %s' %(command, value)
            else:
                command = '%s = %s' %(command, value)
        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        self.inst.write(r"""vbs '%s' """ %(command))
        if self.printOutput:
            self.write("Write: %s" %(command))
        
    def instRead(self):
        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        ret = self.inst.read()
        if self.printOutput:
            self.write("Read")
        return ret

    def instQuery(self, command):
        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        ret = self.inst.query(r"""vbs? 'return=app.%s' """ %(command))
        if self.printOutput:
            self.write("Query: %s" %(command))
        return ret

    def writeAcquisition(self, command, value=None):
        if value != None: 
            if isinstance(value, str):
                command = '%s = "%s"' %(command, value)
            elif isinstance(value, float):
                command = '%s = %s' %(command, value)
            else:
                command = '%s = %s' %(command, value)
        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        self.inst.write(r"""vbs 'app.Acquisition.%s' """ %(command))
        if self.printOutput:
            self.write("Write: app.Acquisition.%s" %(command))
        return True

    def queryAcquisition(self, command, *args):
        arguments = ""
        n = 0 
        for arg in args:
            if n == 0 : 
                arguments = "(%s" %(arg)
            else:
                arguments = "%s,%s" %(arguments, arg)
            n = n+1
        if n > 0: 
            arguments = "%s)" %(arguments)

        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        ret = self.inst.query(r"""vbs? 'return=app.Acquisition.%s%s' """ %(command, arguments))
        if self.printOutput:
            self.write("Query: app.Acquisition.%s%s" %(command, arguments))
        return ret
    
    def checkIdleState(self, timeout=5, maxInteration=10):
        retry = True
        Idle = True
        n = 0
        while retry and n < maxInteration: 
            try:
                ret = self.inst.query(r"""vbs? 'return=app.WaitUntilIdle(%d)'""" %(timeout))
                if ret.find("VBS") != -1:
                    ret = ret.split(" ")[1].strip()
                if int(ret) == 1:
                    return Idle
            except vs.VisaIOError:
                Idle = False
            tm.sleep(0.1)
            n = n+1
        return Idle 

    def writeAcquisitionChn(self, channel, command, value=None):
        if not isinstance(channel, int):
            raise TypeError("Osc: Channel number must be an integer between 1 and 4. ")
        if 1 > channel > 4:
            raise TypeError("Osc: Channel number must be an integer between 1 and 4. ")
        if value != None: 
            if isinstance(value, str):
                command = '%s = "%s"' %(command, value)
            elif isinstance(value, float):
                command = '%s = %s' %(command, value)
            else:
                command = '%s = %s' %(command, value)

        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        ret = self.inst.write(r"""vbs 'app.Acquisition.C%d.%s' """ %(channel, command))
        if self.printOutput:
            self.write("Write: app.Acquisition.C%d.%s" %(channel, command))
        return ret

    def queryAcquisitionChn(self, channel, command, *args):
        arguments = ""
        n = 0 
        for arg in args:
            if n == 0 : 
                arguments = "(%s" %(arg)
            else:
                arguments = "%s,%s" %(arguments, arg)
            n = n+1
        if n > 0: 
            arguments = "%s)" %(arguments)

        if not isinstance(channel, int):
            raise TypeError("Osc: Channel number must be an integer between 1 and 4. ")
        if 1 > channel > 4:
            raise TypeError("Osc: Channel number must be an integer between 1 and 4. ")

        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        ret = self.inst.query(r"""vbs? 'return=app.Acquisition.C%d.%s%s' """ %(channel, command, arguments))
        if self.printOutput:
            self.write("Query: return=app.Acquisition.C%d.%s%s' """ %(channel, command, arguments))
        return ret

    def writeAcquisitionHoriz(self, command, value=None):

        if value != None: 
            if isinstance(value, str):
                command = '%s = "%s"' %(command, value)
            elif isinstance(value, float):
                command = '%s = %s' %(command, value)
            else:
                command = '%s = %s' %(command, value)
        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        ret = self.inst.write(r"""vbs 'app.Acquisition.Horizontal.%s' """ %(command))
        if self.printOutput:
            self.write("Write: app.Acquisition.Horizontal.%s" %(command))
        return ret

    def queryAcquisitionHoriz(self, command, *args):
        arguments = ""
        n = 0 
        for arg in args:
            if n == 0 : 
                arguments = " (%s" %(arg)
            else:
                arguments = "%s,%s" %(arguments, arg)
            n = n+1
        if n > 0: 
            arguments = "%s)" %(arguments)

        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        ret = self.inst.query(r"""vbs? 'return=app.Acquisition.Horizontal.%s%s' """ %(command, arguments))
        if self.printOutput:
            self.write("Query: app.Acquisition.Horizontal.%s" %(command))
        return ret

    def writeAcquisitionAuxOut(self, command, value=None):

        if value != None: 
            if isinstance(value, str):
                command = '%s = "%s"' %(command, value)
            elif isinstance(value, float):
                command = '%s = %s' %(command, value)
            else:
                command = '%s = %s' %(command, value)
        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        ret = self.inst.write(r"""vbs 'app.Acquisition.AuxOutput.%s' """ %(command))
        if self.printOutput:
            self.write("Write: app.Acquisition.AuxOutput.%s" %(command))
        return ret

    def queryAcquisitionAuxOut(self, command, *args):
        arguments = ""
        n = 0 
        for arg in args:
            if n == 0 : 
                arguments = " (%s" %(arg)
            else:
                arguments = "%s,%s" %(arguments, arg)
            n = n+1
        if n > 0: 
            arguments = "%s)" %(arguments)

        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        ret = self.inst.query(r"""vbs? 'return=app.Acquisition.AuxOutput.%s%s' """ %(command, arguments))
        if self.printOutput:
            self.write("Query: app.Acquisition.AuxOutput.%s" %(command))
        return ret

    def writeAcquisitionAuxIn(self, command, value=None):

        if value != None: 
            if isinstance(value, str):
                command = '%s = "%s"' %(command, value)
            elif isinstance(value, float):
                command = '%s = %s' %(command, value)
            else:
                command = '%s = %s' %(command, value)
        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        ret = self.inst.write(r"""vbs 'app.Acquisition.AuxIn.%s' """ %(command))
        if self.printOutput:
            self.write("Write: app.Acquisition.AuxIn.%s" %(command))
        return ret

    def queryAcquisitionAuxIn(self, command, *args):
        arguments = ""
        n = 0 
        for arg in args:
            if n == 0 : 
                arguments = " (%s" %(arg)
            else:
                arguments = "%s,%s" %(arguments, arg)
            n = n+1
        if n > 0: 
            arguments = "%s)" %(arguments)

        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        ret = self.inst.query(r"""vbs? 'return=app.Acquisition.AuxIn.%s%s' """ %(command, arguments))
        if self.printOutput:
            self.write("Query: app.Acquisition.AuxIn.%s" %(command))
        return ret

    def writeAcquisitionTrigger(self, command, value=None):

        if value != None: 
            if isinstance(value, str):
                command = '%s = "%s"' %(command, value)
            elif isinstance(value, float):
                command = '%s = %s' %(command, value)
            else:
                command = '%s = %s' %(command, value)
        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        ret = self.inst.write(r"""vbs 'app.Acquisition.Trigger.%s' """ %(command))
        if self.printOutput:
            self.write("Write: app.Acquisition.Trigger.%s" %(command))
        return ret

    def clearAllMeasurements(self):
        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        self.inst.write(r"""vbs 'app.measure.clearall ' """)

    def clearAllMeasurementSweeps(self):
        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        self.inst.write(r"""vbs 'app.measure.clearsweeps ' """)

    def setMeasurement(self, parameter, value, channel1, channel2=None):
        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        self.inst.write(r"""vbs 'app.measure.showmeasure = true ' """)
        self.inst.write(r"""vbs 'app.measure.statson = true ' """)
        self.inst.write(r"""vbs 'app.measure.p%d.view = true ' """ %(parameter))
        self.inst.write(r"""vbs 'app.measure.p%d.paramengine = "%s" ' """%(parameter, value))
        self.inst.write(r"""vbs 'app.measure.p%d.source1 = "C%d" ' """ %(parameter, channel1))
        if channel2 != None:
            self.inst.write(r"""vbs 'app.measure.p%d.source2 = "C%d" ' """ %(parameter, channel2))

    '''

        def setMeasurement(self, command, value, parameter=None):

            quRet = self.inst.query(r"""vbs? 'return=app.WaitUntilIdle(5)' """)
            if parameter == None:
                ret = self.inst.write(r"""vbs 'app.measure.%s = %s' """ %(command, value))
                if self.printOutput:
                    self.write("Write: app.measure.%s = %s" %(command, value))
                return ret
            else:
                ret = self.inst.write(r"""vbs 'app.measure.pP%d.%s = %s' """ %(parameter, command, value))
                if self.printOutput:
                    self.write("Write: app.measure.p%d.%s = %s" %(parameter, command, value))
                return ret
    '''

    def getMeasurementResults(self, parameter):
        self.inst.query(r"""vbs? 'return=app.WaitUntilIdle(5)' """)
        'return=app.measure.p1.out.result.value'

        ret = self.inst.query(r"""vbs? 'return=app.measure.p%d.out.result.value' """ %(parameter))
        return ret

    def instWrite_GPIB(self, command):
        self.inst.write(command)
        if self.printOutput:
            self.write("Write: %s" %(command))
        stb = self.inst.query("*STB?")
        binStb = std.getBinaryList(int(stb))
        err = binStb[5]
        if err == 1:
            ret = self.inst.query("ERR? 1\n")
            raise SyntaxError("Osciolloscope 740Zi encountered error #%d." %(ret))

    def instRead_GPIB(self):
        ret = self.inst.read()
        if self.printOutput:
            self.write("Read")
        return ret
    
    def instQuery_GPIB(self, command):
        ret = self.inst.query(command)
        if self.printOutput:
            self.write("Query: %s" %(command))
        stb = self.inst.query("*STB?")
        #stb = self.inst.read_stb()
        binStb = std.getBinaryList(int(stb))
        err = binStb[5]
        if err == 1:
            ret = self.inst.query("ERR? 1\n")
            raise SyntaxError("Osciolloscope 740Zi encountered error #%d." %(ret))
        return ret

    def performCalibration(self):
        self.calibration()

    def calibration(self):
        self.writeAcquisition("Calibrate")

    def clearSweeps(self):
        self.writeAcquisition("ClearSweeps")

    def queryDataArray(self, channel):
        self.inst.query(r"""vbs? 'return=app.WaitUntilIdle(5)' """)
        ret = self.inst.query(r"""vbs? 'return=join(app.Acquisition.C%d.Out.Result.DataArray, chr(44))'""" %(channel))
        ret = ret.split(",")
        newRet = []
        #print("array length:", len(ret))
        for r in ret:
            newRet.append(float(r))
        ret = newRet
        if self.printOutput:
            self.write("Query: return=join(app.Acquisition.C%d.Out.Result.DataArray(0), chr(44))" %(channel))
        return ret

    def queryDataTimePerPoint(self):
        self.inst.query(r"""vbs? 'return=app.WaitUntilIdle(5)' """)
        ret = self.inst.query(r"""vbs? 'return=app.Acquisition.Horizontal.TimePerPoint'""")
        #ret = ret.split(",")
        newRet = []
        #print("Time Per Point:", ret)
        if self.printOutput:
            self.write("Query: return=app.Acquisition.Horizontal.TimePerPoint")
        return ret

    def checkChannel(self, channel):

        if not isinstance(channel, int):
            self.ValError("Oscillocope Channel must be an Integer from 1 to 4. (%s)" %(channel))

        if 1 > channel > 4:
            self.ValError("Oscillocope Channel must be an Integer from 1 to 4. (%s)" %(channel))
    
    def SysError(self, error):
        raise SystemError("WGFMU System Error: %s" %(error))

    def ValError(self, error):
        raise ValueError("WGFMU Value Error: %s" %(error))
    
    def TypError(self, error):
        raise TypeError("WGFMU Type Error: %s" %(error))







##############################################################################################################
#################### 
#LeCroy WaveRunner 640Zi Oscilloscope: 
class LeCroy_WR640Zi():

    printOutput = False

    def __init__(self, rm=None, adr=None, Device=None, reset=False, calibration=False, printOutput=False, timeout=5, maxIdleInteration=10):
        
        self.timeout = timeout
        self.maxIdleInteration = maxIdleInteration
        self.printOutput = printOutput
        self.inst=None
        if (rm == None or adr == None) and Device == None:
            self.write("Either rm and GPIB_adr or a device must be given transmitted")  #maybe a problem, tranmitting None type
        elif Device == None:    

            try:
                self.inst = rm.open_resource(adr)
                
            except:
                self.write("The device %s does not exist." %(adr))  #maybe a problem, tranmitting None type
        
        else:
            self.inst = Device
            

        self.inst.write("*SRE 1")
        ret = self.instQuery("InstrumentID")
        print(ret)
        if not ret.find("LECROY,WR640Zi,") == -1:
            self.write("You are using the %s" %(ret[:-2]))
        else:
            #print("You are using the wrong agilent tool!")
            exit("You are using the wrong lecroy tool!")

        self.inst.write("COMM_HEADER OFF")
        self.inst.write(r"""vbs 'app.settodefaultsetup' """)
        
        if calibration: 
            self.calibration()
        
        if reset:
            self.initialize()

    def turnOffline(self):
        self.inst.close()

    def write(self, com):
        if self.printOutput:
            print("WavePro 640Zi: ", com)

    def initialize(self):
        self.instWrite("app.settodefaultsetup")
        self.instWrite("app.measure.clearall")
        self.instWrite("app.measure.clearsweeps")
        self.instWrite('app.acquisition.triggermode = "stopped"')

    def getModel(self):
        ret = self.instQuery("InstrumentID")
        return ret

    def instWrite(self, command, value = None):
        if value != None: 
            if isinstance(value, str):
                command = '%s = "%s"' %(command, value)
            elif isinstance(value, float):
                command = '%s = %s' %(command, value)
            else:
                command = '%s = %s' %(command, value)
        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        self.inst.write(r"""vbs '%s' """ %(command))
        if self.printOutput:
            self.write("Write: %s" %(command))
        
    def instRead(self):
        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        ret = self.inst.read()
        if self.printOutput:
            self.write("Read")
        return ret

    def instQuery(self, command):
        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        ret = self.inst.query(r"""vbs? 'return=app.%s' """ %(command))
        if self.printOutput:
            self.write("Query: %s" %(command))
        return ret

    def writeAcquisition(self, command, value=None):
        if value != None: 
            if isinstance(value, str):
                command = '%s = "%s"' %(command, value)
            elif isinstance(value, float):
                command = '%s = %s' %(command, value)
            else:
                command = '%s = %s' %(command, value)
        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        self.inst.write(r"""vbs 'app.Acquisition.%s' """ %(command))
        if self.printOutput:
            self.write("Write: app.Acquisition.%s" %(command))
        return True

    def queryAcquisition(self, command, *args):
        arguments = ""
        n = 0 
        for arg in args:
            if n == 0 : 
                arguments = "(%s" %(arg)
            else:
                arguments = "%s,%s" %(arguments, arg)
            n = n+1
        if n > 0: 
            arguments = "%s)" %(arguments)

        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        ret = self.inst.query(r"""vbs? 'return=app.Acquisition.%s%s' """ %(command, arguments))
        if self.printOutput:
            self.write("Query: app.Acquisition.%s%s" %(command, arguments))
        return ret
    
    def checkIdleState(self, timeout=5, maxInteration=10):
        retry = True
        Idle = True
        n = 0
        while retry and n < maxInteration: 
            try:
                ret = self.inst.query(r"""vbs? 'return=app.WaitUntilIdle(%d)'""" %(timeout))
                if ret.find("VBS") != -1:
                    ret = ret.split(" ")[1].strip()
                if int(ret) == 1:
                    return Idle
            except vs.VisaIOError:
                Idle = False
            tm.sleep(0.1)
            n = n+1
        return Idle 

    def writeAcquisitionChn(self, channel, command, value=None):
        if not isinstance(channel, int):
            raise TypeError("Osc: Channel number must be an integer between 1 and 4. ")
        if 1 > channel > 4:
            raise TypeError("Osc: Channel number must be an integer between 1 and 4. ")
        if value != None: 
            if isinstance(value, str):
                command = '%s = "%s"' %(command, value)
            elif isinstance(value, float):
                command = '%s = %s' %(command, value)
            else:
                command = '%s = %s' %(command, value)

        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        ret = self.inst.write(r"""vbs 'app.Acquisition.C%d.%s' """ %(channel, command))
        if self.printOutput:
            self.write("Write: app.Acquisition.C%d.%s" %(channel, command))
        return ret

    def queryAcquisitionChn(self, channel, command, *args):
        arguments = ""
        n = 0 
        for arg in args:
            if n == 0 : 
                arguments = "(%s" %(arg)
            else:
                arguments = "%s,%s" %(arguments, arg)
            n = n+1
        if n > 0: 
            arguments = "%s)" %(arguments)

        if not isinstance(channel, int):
            raise TypeError("Osc: Channel number must be an integer between 1 and 4. ")
        if 1 > channel > 4:
            raise TypeError("Osc: Channel number must be an integer between 1 and 4. ")

        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        ret = self.inst.query(r"""vbs? 'return=app.Acquisition.C%d.%s%s' """ %(channel, command, arguments))
        if self.printOutput:
            self.write("Query: return=app.Acquisition.C%d.%s%s' """ %(channel, command, arguments))
        return ret

    def writeAcquisitionHoriz(self, command, value=None):

        if value != None: 
            if isinstance(value, str):
                command = '%s = "%s"' %(command, value)
            elif isinstance(value, float):
                command = '%s = %s' %(command, value)
            else:
                command = '%s = %s' %(command, value)
        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        ret = self.inst.write(r"""vbs 'app.Acquisition.Horizontal.%s' """ %(command))
        if self.printOutput:
            self.write("Write: app.Acquisition.Horizontal.%s" %(command))
        return ret

    def queryAcquisitionHoriz(self, command, *args):
        arguments = ""
        n = 0 
        for arg in args:
            if n == 0 : 
                arguments = " (%s" %(arg)
            else:
                arguments = "%s,%s" %(arguments, arg)
            n = n+1
        if n > 0: 
            arguments = "%s)" %(arguments)

        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        ret = self.inst.query(r"""vbs? 'return=app.Acquisition.Horizontal.%s%s' """ %(command, arguments))
        if self.printOutput:
            self.write("Query: app.Acquisition.Horizontal.%s" %(command))
        return ret

    def writeAcquisitionAuxOut(self, command, value=None):

        if value != None: 
            if isinstance(value, str):
                command = '%s = "%s"' %(command, value)
            elif isinstance(value, float):
                command = '%s = %s' %(command, value)
            else:
                command = '%s = %s' %(command, value)
        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        ret = self.inst.write(r"""vbs 'app.Acquisition.AuxOutput.%s' """ %(command))
        if self.printOutput:
            self.write("Write: app.Acquisition.AuxOutput.%s" %(command))
        return ret

    def queryAcquisitionAuxOut(self, command, *args):
        arguments = ""
        n = 0 
        for arg in args:
            if n == 0 : 
                arguments = " (%s" %(arg)
            else:
                arguments = "%s,%s" %(arguments, arg)
            n = n+1
        if n > 0: 
            arguments = "%s)" %(arguments)

        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        ret = self.inst.query(r"""vbs? 'return=app.Acquisition.AuxOutput.%s%s' """ %(command, arguments))
        if self.printOutput:
            self.write("Query: app.Acquisition.AuxOutput.%s" %(command))
        return ret

    def writeAcquisitionAuxIn(self, command, value=None):

        if value != None: 
            if isinstance(value, str):
                command = '%s = "%s"' %(command, value)
            elif isinstance(value, float):
                command = '%s = %s' %(command, value)
            else:
                command = '%s = %s' %(command, value)
        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        ret = self.inst.write(r"""vbs 'app.Acquisition.AuxIn.%s' """ %(command))
        if self.printOutput:
            self.write("Write: app.Acquisition.AuxIn.%s" %(command))
        return ret

    def queryAcquisitionAuxIn(self, command, *args):
        arguments = ""
        n = 0 
        for arg in args:
            if n == 0 : 
                arguments = " (%s" %(arg)
            else:
                arguments = "%s,%s" %(arguments, arg)
            n = n+1
        if n > 0: 
            arguments = "%s)" %(arguments)

        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        ret = self.inst.query(r"""vbs? 'return=app.Acquisition.AuxIn.%s%s' """ %(command, arguments))
        if self.printOutput:
            self.write("Query: app.Acquisition.AuxIn.%s" %(command))
        return ret

    def writeAcquisitionTrigger(self, command, value=None):

        if value != None: 
            if isinstance(value, str):
                command = '%s = "%s"' %(command, value)
            elif isinstance(value, float):
                command = '%s = %s' %(command, value)
            else:
                command = '%s = %s' %(command, value)
        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        ret = self.inst.write(r"""vbs 'app.Acquisition.Trigger.%s' """ %(command))
        if self.printOutput:
            self.write("Write: app.Acquisition.Trigger.%s" %(command))
        return ret

    def clearAllMeasurements(self):
        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        self.inst.write(r"""vbs 'app.measure.clearall ' """)

    def clearAllMeasurementSweeps(self):
        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        self.inst.write(r"""vbs 'app.measure.clearsweeps ' """)

    def setMeasurement(self, parameter, value, channel1, channel2=None):
        Idle = self.checkIdleState(self.timeout, self.maxIdleInteration)
        if not Idle:
            return False
        self.inst.write(r"""vbs 'app.measure.showmeasure = true ' """)
        self.inst.write(r"""vbs 'app.measure.statson = true ' """)
        self.inst.write(r"""vbs 'app.measure.p%d.view = true ' """ %(parameter))
        self.inst.write(r"""vbs 'app.measure.p%d.paramengine = "%s" ' """%(parameter, value))
        self.inst.write(r"""vbs 'app.measure.p%d.source1 = "C%d" ' """ %(parameter, channel1))
        if channel2 != None:
            self.inst.write(r"""vbs 'app.measure.p%d.source2 = "C%d" ' """ %(parameter, channel2))

    '''

        def setMeasurement(self, command, value, parameter=None):

            quRet = self.inst.query(r"""vbs? 'return=app.WaitUntilIdle(5)' """)
            if parameter == None:
                ret = self.inst.write(r"""vbs 'app.measure.%s = %s' """ %(command, value))
                if self.printOutput:
                    self.write("Write: app.measure.%s = %s" %(command, value))
                return ret
            else:
                ret = self.inst.write(r"""vbs 'app.measure.pP%d.%s = %s' """ %(parameter, command, value))
                if self.printOutput:
                    self.write("Write: app.measure.p%d.%s = %s" %(parameter, command, value))
                return ret
    '''

    def getMeasurementResults(self, parameter):
        self.inst.query(r"""vbs? 'return=app.WaitUntilIdle(5)' """)
        'return=app.measure.p1.out.result.value'

        ret = self.inst.query(r"""vbs? 'return=app.measure.p%d.out.result.value' """ %(parameter))
        return ret

    def instWrite_GPIB(self, command):
        self.inst.write(command)
        if self.printOutput:
            self.write("Write: %s" %(command))
        stb = self.inst.query("*STB?")
        binStb = std.getBinaryList(int(stb))
        err = binStb[5]
        if err == 1:
            ret = self.inst.query("ERR? 1\n")
            raise SyntaxError("Osciolloscope 740Zi encountered error #%d." %(ret))

    def instRead_GPIB(self):
        ret = self.inst.read()
        if self.printOutput:
            self.write("Read")
        return ret
    
    def instQuery_GPIB(self, command):
        ret = self.inst.query(command)
        if self.printOutput:
            self.write("Query: %s" %(command))
        stb = self.inst.query("*STB?")
        #stb = self.inst.read_stb()
        binStb = std.getBinaryList(int(stb))
        err = binStb[5]
        if err == 1:
            ret = self.inst.query("ERR? 1\n")
            raise SyntaxError("Osciolloscope 740Zi encountered error #%d." %(ret))
        return ret

    def performCalibration(self):
        self.calibration()

    def calibration(self):
        self.writeAcquisition("Calibrate")

    def clearSweeps(self):
        self.writeAcquisition("ClearSweeps")

    def queryDataArray(self, channel):
        self.inst.query(r"""vbs? 'return=app.WaitUntilIdle(5)' """)
        ret = self.inst.query(r"""vbs? 'return=join(app.Acquisition.C%d.Out.Result.DataArray, chr(44))'""" %(channel))
        ret = ret.split(",")
        newRet = []
        for r in ret:
            newRet.append(float(r))
        ret = newRet
        if self.printOutput:
            self.write("Query: return=join(app.Acquisition.C%d.Out.Result.DataArray(0), chr(44))" %(channel))
        return ret

    def checkChannel(self, channel):

        if not isinstance(channel, int):
            self.ValError("Oscillocope Channel must be an Integer from 1 to 4. (%s)" %(channel))

        if 1 > channel > 4:
            self.ValError("Oscillocope Channel must be an Integer from 1 to 4. (%s)" %(channel))
    
    def SysError(self, error):
        raise SystemError("WGFMU System Error: %s" %(error))

    def ValError(self, error):
        raise ValueError("WGFMU Value Error: %s" %(error))
    
    def TypError(self, error):
        raise TypeError("WGFMU Type Error: %s" %(error))



