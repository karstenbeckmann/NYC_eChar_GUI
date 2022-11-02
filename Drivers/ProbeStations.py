"""
Written by: Karsten Beckmann and Maximillian Liehr
Institution: SUNY Polytechnic Institute
Date: 6/12/2018
    
For more information please use the SUSS ProbeShield remote control manual.
"""

import numpy as np 
import pyvisa as vs 
import datetime as dt 
import time as tm
import queue as qu
from Exceptions import *


class FormFactor: 

    inst = None
    ErrorQueue = qu.Queue()
    logQueue = qu.Queue()
    printOutput = False
    __GPIB = None
    __rm = None
    __online = False\

    ProbeStationName = "FormFactorDefault"

    def __init__(self,rm=None,GPIB_adr=None, Device=None):
        

        print(self.ProbeStationName)

        if (rm == None or GPIB_adr == None) and Device == None:
            self.write("%s: Either rm and GPIB_adr or a device must be given transmitted" %(self.ProbeStationName))  #maybe a problem, tranmitting None type
        elif Device == None:    

            try:
                self.inst = rm.open_resource(GPIB_adr)
                
            except:
                self.write("%s: The device %s does not exist." %(self.ProbeStationName, GPIB_adr))  #maybe a problem, tranmitting None type
        
            self.__GPIB = GPIB_adr
            self.__rm = rm
        else:
                self.inst = Device
        
        try:
            self.instWrite("*IDN?")
            tm.sleep(0.1)
            self.instRead()
            self.__online = True
        except (SystemError, vs.VisaIOError) as message:
            self.ErrorQueue.put(message)
            self.__online == False

    def Connect(self):
        try:
            self.inst = self.__rm.open_resource(self.__GPIB)
            self.instWrite("*IDN?")
            tm.sleep(0.1)
            self.instRead()
            self.__online = True
        except SystemError as message:
            self.ErrorQueue.put(message)
        

    def write(self, command):
        if self.printOutput:
            print(command)
        self.logQueue.put(command)

    def setTimeOut(self, timeout):
        if not isinstance(timeout,(float,int)):
            raise ProbeStation_InputError("Timeout must be of type float bigger than 0. The unit is milliseconds.")
        if timeout <= 0:
            raise ProbeStation_InputError("Timeout must be of type float bigger than 0. The unit is milliseconds.")
        if self.__online:
            self.inst.timeout = timeout
        else:
            self.ErrorQueue.put("The Probe Station is offline.")
    
    def deleteTimeOut(self):
        if self.__online:
            del self.inst.timeout
        else:
            self.ErrorQueue.put("The Probe Station is offline.")

    def instWrite(self, command):
        if self.__online:
            self.inst.write(command)
            if self.printOutput:
                print("Write: ", command)
        else:
            self.ErrorQueue.put("Probe Station is offline.")

    def instRead(self):
        ret = None
        if self.__online:
            ret = self.inst.read()
            if self.printOutput:
                print("Read!")
        else:
            self.ErrorQueue.put("Probe Station is offline.")
        return ret

    def instQuery(self, command):
        ret = None
        if self.__online:
            ret = self.inst.query(command)
            if self.printOutput:
                print("Query: ", command)

        else:
            self.ErrorQueue.put("Probe Station is offline.")
        return ret

    def getStatus(self):
        ret = self.instQuery("STB?")
        return ret

    def read_stb(self):
        ret = self.getStatus()
        return ret
        
    #Chuck control
    ##############################################################

    def ReadChuckHeights(self):
        ret = self.instQuery("ReadChuckHeights")
        ret = ret.split(' ')[1:]
        output = []
        for x in ret:
            output.append(float(x))
        return output
        
    def InitChuck(self):
        self.instQuery("InitChuck 7 0 0")

    def EnableMotorQuiet(self):
        self.instWrite("EnableMotorQuiet 1")
        
        
    def DisableMotorQuiet(self):
        self.instWrite("EnableMotorQuiet 0")
        

    def close(self):
        if self.__online:
            self.inst.close()
            self.__online = False

    def turnOffline(self):
        self.close()

    #Move Chuck
    #realtiveTo can be: H: Home; Z: Zero; C: Center; R: Current Position;
    #unit can be: Y: micron; I: Mils; X: Index; J: Jog;
    #velocity is from 0 to 100%
    def MoveChuck(self, X, Y, relativTo="R", unit="Y", velocity=100):
        if not (X == 0 and Y == 0):
            ret = self.instQuery("MoveChuck %s %s %s %s %s" %(-X,-Y,relativTo, unit, velocity))
            if not ret.strip() == "0:":
                raise ProbeStationError(ret)

    #Move Chuck by Index (one die)
    #realtiveTo can be: H: Home; Z: Zero; C: Center; R: Current Position;
    #X and Y are Integer 
    #velocity is from 0 to 100%
    def MoveChuckIndex(self, X, Y, relativTo="R", velocity=100):
        self.checkIndex(X, 'X')
        self.checkIndex(Y, 'Y')
        self.checkPosRef(relativTo)
        if not (X == 0 and Y == 0 and (not relativTo=="C")):
            ret = self.instQuery("MoveChuckIndex  %s %s %s %s" %(X,Y,relativTo, velocity))
            if not ret.strip() == "0:":
                raise ProbeStationError(ret)

    def MoveChuckMicron(self, X, Y, relativTo="R", velocity=100):
        self.checkXYValue(X, 'X')
        self.checkXYValue(Y, 'X')
        if not (X == 0 and Y == 0):
            self.checkPosRef(relativTo)
            ret = self.instQuery("MoveChuck %s %s %s Y %s" %(X,Y,relativTo, velocity))
            if not ret.strip() == "0:":
                raise ProbeStationError(ret)

    def MoveChuckAlign(self, velocity=100):
        self.instQuery("MoveChuckAlign %s" %(velocity))

    def MoveChuckContact(self, vel=100):
        ret = self.instQuery("MoveChuckContact %d" %(vel))
        if not ret.strip() == "0:":
            raise ProbeStationError(ret)

    #Moves the chuck to the upper (0) or lower = lifted (1) position. This initiates motion only, the actual movement may take some seconds.
    def MoveChuckLift(self, Pos):
        self.instQuery("MoveChuckLift %s" %(Pos))

    #Moves the Chuck stage in X, Y, Z and Theta to the load position.
    def MoveChuckLoad(self, Pos=1):
        self.instQuery("MoveChuckLoad %s" %(Pos))

    #Moves the chuck Z axis to the separation height. Returns error if no Contact height is set.
    def MoveChuckSeparation(self, Vel=100):
        self.instQuery("MoveChuckSeparation %s" %(Vel))

    #Moves the Chuck to Home position.
    def MoveChuckHome(self, Vel=100):
        self.instQuery("MoveChuckSubsite 0 0 Y %s" %(Vel))

    #The command gets the actual wafer size which is stored in the electronics.
    def ReadChuckIndex(self, Pos=1):
        output = None
        ret = self.instQuery("ReadChuckIndex Y" )
        if not type(None):
            ret = ret.split(' ')[1:]
            output = []
            first = True
            for x in ret:
                if first:
                    output.append(float(x))
                else:
                    output.append(float(x))
                first = False
        return output

    #Returns the actual chuck stage position in X, Y and Z. The default Compensation Mode is the currently activated compensation mode of the kernel. 
    def ReadChuckPosition(self, Unit="Y", PosRef="H"):
        output = None
        ret = self.instQuery("ReadChuckPosition %s %s" %(Unit, PosRef))
        if not ret == None:
            ret = ret.split(' ')[1:]
            output = []
            first = True
            for x in ret:
                if first:
                    output.append(-float(x))
                else:
                    output.append(-float(x))
                first = False
            return output

    def ReadChuckPositionX(self, Unit="Y", PosRef="H"):
        ret = self.instQuery("ReadChuckPosition %s %s" %(Unit, PosRef))
        ret = ret.split(' ')[1:]
        output = []
        for x in ret:
            output.append(float(x))
        return -output[0]
    
    def ReadChuckPositionY(self, Unit="Y", PosRef="H"):
        ret = self.instQuery("ReadChuckPosition %s %s" %(Unit, PosRef))
        ret = ret.split(' ')[1:]
        output = []
        for x in ret:
            output.append(float(x))
        return -output[1]
    
    def ReadChuckPositionZ(self, Unit="Y", PosRef="H"):
        ret = self.instQuery("ReadChuckPosition %s %s" %(Unit, PosRef))
        ret = ret.split(' ')[1:]
        output = []
        for x in ret:
            output.append(float(x))
        return -output[2]

    #Read the actual set or calculated temperature.
    def ReadChuckThermoValue(self):
        ret = self.instQuery("ReadChuckThermoValue C")
        ret = ret.split(' ')[1:]
        output = []
        for x in ret:
            output.append(float(x))
        return output

    #Read the actual set or calculated temperature.
    def ReadChuckStatus(self):
        ret = self.instQuery("ReadChuckStatus")
        ret = ret.split(' ')[1:]
        return ret

    #TemperatureChuck control
    ##############################################################
    
    #Read the actual set or calculated temperature.
    def EnableHeaterHoldMode(self, en):
        if en:
            ret = self.instQuery("EnableHeaterHoldMode 0")
        else:
            ret = self.instQuery("EnableHeaterHoldMode 1")
        if ret == 0:
            return True
        else:
            return False

    #This command returns the current dew point temperature, if a dew point sensor is connected. The default unit of the temperature is degrees Celsius. 
    def GetDewPointTemp(self, Unit="C"):
        ret = self.instQuery("GetDewPointTemp %s" %(Unit))
        return ret[0]

    #This command reads the current temperature of the chuck and determines the status of the thermal system. The default unit is degrees Celsius.  
    def GetHeaterTemp(self, Unit="C"):
        ret = self.instQuery("GetHeaterTemp %s" %(Unit))
        try:
            ret = float(ret)
        except TypeError as e:
            self.ErrorQueue.put("Error reading Chuck Temperature. (%s)" %(ret))
            ret = 25
        return ret
    
    #This command reads the target temperature of the chuck. The default unit is degrees Celsius.
    def GetTargetTemp(self, Unit="C"):
        ret = self.inst.query("GetTargetTemp %s" %(Unit))
        return ret[0]

    #This command sets a new target temperature and starts the heating or cooling of the chuck. An answer to the command will be returned after reaching the given temperature and waiting the soak time or an unexpected interrupt of the process. Given back is the already reached temperature. The default unit is degrees Celsius.
    def HeatChuck(self, temp, Unit="C"):
        ret = self.instQuery("HeatChuck %s %s" %(temp, Unit))
        return ret[0]
        
    #This command sets a new target temperature and starts the heating or cooling of the temperature chuck. The response is returned immediately. 
    #Given back is the new target temperature. The default unit is degrees Celsius. 
    def SetHeaterTemp(self, temp, Unit="C"):
        ret = self.instQuery("SetHeaterTemp %s %s" %(temp, Unit))
        return ret[0]

    #This command sets a new soak time value. The unit of the value is seconds. If soak time is actually running, it may be affected by the change.
    def SetHeaterSoak(self, time):
        ret = self.instQuery("SetHeaterSoak  %s" %(time))
        return ret[0]

    #This command sets a new soak time value. The unit of the value is seconds. If soak time is actually running, it may be affected by the change.
    def StopHeatChuck(self):
        self.instQuery("StopHeatChuck")

    #Read the Scope Status.
    def ReadScopeStatus(self):
        ret = self.instQuery("ReadScopeStatus")
        ret = ret.split(' ')[1:]
        return ret

    ############################################
    ############## check Values:################ 
    def checkIndex(self, n, axis): 
        if not isinstance(n, int):
            raise ProbeStation_InputError("The index for axis %s must be an int between 0 and 50." %(axis))
        if n < -50 or n > 50: 
            raise ProbeStation_InputError("The index for axis %s must be an int between 0 and 50." %(axis))

    def checkXYValue(self, n, axis): 
        if not isinstance(n, (float, int)):
            raise ProbeStation_InputError("The index for axis %s must be a double value between 0 and +-150000. (Cur. Val. %s)" %(axis, n))
        if n < -150000 or n > 150000: 
            raise ProbeStation_InputError("The index for axis %s must be a double value between 0 and +-150000. (Cur. Val. %s)" %(axis, n))

    def checkPosRef(self, pos): 
        if not isinstance(pos, str):
            raise ProbeStation_InputError("The position reference must be 'H' (Home), 'Z' (Zero), 'C' (Center) or 'R' (Current position).")
        if not (pos == 'H' or pos == 'Z' or pos == 'C' or pos == 'R'):
            raise ProbeStation_InputError("The position reference must be 'H' (Home), 'Z' (Zero), 'C' (Center) or 'R' (Current position).")

    ###########################################################################################################################################
    ###########################################################################################################################################
    ###########################################################################################################################################


class Cascade_S300: 

    inst = None
    ErrorQueue = qu.Queue()
    logQueue = qu.Queue()
    printOutput = False
    __GPIB = None
    __rm = None
    __online = False
    deviceID = 2

    def __init__(self,rm=None,GPIB_adr=None, Device=None):
        

        if (rm == None or GPIB_adr == None) and Device == None:
            self.write("Cascade Microtech S300: Either rm and GPIB_adr or a device must be given transmitted")  #maybe a problem, tranmitting None type
        elif Device == None:    

            try:
                self.inst = rm.open_resource(GPIB_adr)
                
            except:
                self.write("Cascade Microtech S300: The device %s does not exist." %(GPIB_adr))  #maybe a problem, tranmitting None type
        
            self.__GPIB = GPIB_adr
            self.__rm = rm
        else:
                self.inst = Device
        
        try:
            self.instWrite("*IDN?")
            tm.sleep(0.1)
            self.instRead()
            self.__online = True
            self.instWrite(":set:unit 2 metric")
        except (SystemError, vs.VisaIOError) as message:
            self.ErrorQueue.put(message)
            self.__online == False

    def Connect(self):
        try:
            self.inst = self.__rm.open_resource(self.__GPIB)
            self.instWrite("*IDN?")
            tm.sleep(0.1)
            self.instRead()
            self.__online = True
        except SystemError as message:
            self.ErrorQueue.put(message)
        

    def write(self, command):
        if self.printOutput:
            print(command)
        self.logQueue.put(command)

    def setTimeOut(self, timeout):
        if not isinstance(timeout,(float,int)):
            raise ProbeStation_InputError("Timeout must be of type float bigger than 0. The unit is milliseconds.")
        if timeout <= 0:
            raise ProbeStation_InputError("Timeout must be of type float bigger than 0. The unit is milliseconds.")
        if self.__online:
            self.inst.timeout = timeout
        else:
            self.ErrorQueue.put("The Probe Station is offline.")
    
    def deleteTimeOut(self):
        if self.__online:
            del self.inst.timeout
        else:
            self.ErrorQueue.put("The Probe Station is offline.")

    def instWrite(self, command):
        if self.__online:
            self.inst.write(command)
            if self.printOutput:
                print("Write: ", command)
        else:
            self.ErrorQueue.put("Probe Station is offline.")

    def instRead(self):
        ret = None
        if self.__online:
            ret = self.inst.read()
            if self.printOutput:
                print("Read!")
        else:
            self.ErrorQueue.put("Probe Station is offline.")
        return ret

    def instQuery(self, command):
        ret = None
        if self.__online:
            ret = self.inst.query(command)
            if self.printOutput:
                print("Query: ", command)
        else:
            self.ErrorQueue.put("Probe Station is offline.")
        return ret

    def getStatus(self):
        ret = self.instQuery("STB?")
        return ret

    def read_stb(self):
        ret = self.getStatus()
        return ret

    def GetUnit(self):
        out = self.instQuery(":set:unit? %d" %(self.deviceID))
        return out

    def SetUnit(self, unit="Y"):
        if unit == "I":
            self.instWrite(":set:unit %d English" %(self.deviceID))
        else:
            self.instWrite(":set:unit %d metric" %(self.deviceID))

    #Chuck control
    ##############################################################

    def ReadChuckHeights(self):
        """
        Contact height: Value of current contact height or -1 if contact height is not set.
        Overtravel gap: Value of overtravel gap added to contact height defines overtravel height.
        Alignment gap: Value of alignment gap subtracted from contact height defines alignment height.
        Separation gap: Value of separation gap subtracted from contact height defines separation height.
        Search gap: Value of search gap added to the contact height defines as search height. It is the maximum move destination for auto contact search
        """
        
        ret = []

        out = self.instQuery(":set:contact? %d" %(self.deviceID))
        ret.append(float(out))
        
        out = self.instQuery(":set:edg:over? %d" %(self.deviceID))
        ret.append(float(out))

        out = self.instQuery(":set:separate? %d" %(self.deviceID))
        ret.append(float(out))
        ret.append(float(out))

        out = self.instQuery("set:cont:ban?")
        ret.append(float(out))

        return ret
        
    def InitChuck(self):
        self.MoveChuckHome()

    def EnableMotorQuiet(self):
        try:
            self.instWrite("EnableMotorQuiet 1")
        except: 
            pass
        
    def DisableMotorQuiet(self):
        try:
            self.instWrite("EnableMotorQuiet 0")
        except: 
            pass

    def close(self):
        if self.__online:
            self.inst.close()
            self.__online = False

    def turnOffline(self):
        self.close()

    #Move Chuck
    #realtiveTo can be: H: Home; Z: Zero; C: Center; R: Current Position;
    #unit can be: Y: micron; I: Mils; X: Index; J: Jog;
    #velocity is from 0 to 100%
    def MoveChuck(self, X, Y, relativTo="R", unit="Y", velocity=100):
        
        self.SetUnit(unit)

        self.checkPosRef(relativTo)

        if relativTo == "R":
            if not (X == 0 and Y == 0):
                self.instWrite(":move:relative %d %s %s none" %(self.deviceID,X,Y))
        elif relativTo == "H":
                self.instWrite(":move:absolute %d %s %s none" %(self.deviceID,X,Y))

    #Move Chuck by Index (one die)
    #realtiveTo can be: H: Home; Z: Zero; C: Center; R: Current Position;
    #X and Y are Integer 
    #velocity is from 0 to 100%
    def MoveChuckIndex(self, X, Y, relativTo="R", velocity=100):
        self.SetVelocity(velocity)

        self.checkIndex(X, 'X')
        self.checkIndex(Y, 'Y')
        self.checkPosRef(relativTo)
        
        if relativTo =="R":
            if not (X == 0 and Y == 0 and (not relativTo=="C")):
                self.instWrite(":move:probeplan:relative:index %d %s %s none" %(self.deviceID, X,Y))
        elif relativTo == "C":
            if not (X == 0 and Y == 0 and (not relativTo=="C")):
                self.instWrite(":move:probeplan:absolute:index %d %s %s none" %(self.deviceID, X,Y))
        

    def MoveChuckMicron(self, X, Y, relativTo="R", velocity=100):
        self.SetVelocity(velocity)

        self.checkXYValue(X, 'X')
        self.checkXYValue(Y, 'X')

        self.checkPosRef(relativTo)

        if relativTo == "R":
            if not (X == 0 and Y == 0):
                self.instWrite(":move:relative %d %s %s none" %(self.deviceID,X,Y))
        elif relativTo == "H":
                self.instWrite(":move:absolute %d %s %s none" %(self.deviceID,X,Y))



    def MoveChuckAlignPosition(self, velocity=100):
        self.SetContactSpeed(velocity)
        self.instQuery(":mov:align %d" %(self.deviceID))

    def MoveChuckAlign(self, velocity=100):
        self.MoveChuckSeparation(velocity)

    def MoveChuckContact(self):
        self.instWrite(":move:contact %d" %(self.deviceID))
        ret = self.instQuery(":move:contact? %d" %(self.deviceID))
        if not ret.strip() == "TRUE":
            raise ProbeStationError(ret)

    #Moves the chuck to the upper (0) or lower = lifted (1) position. This initiates motion only, the actual movement may take some seconds.
    def MoveChuckLift(self, Pos):
        if Pos == 0:
            self.instWrite(":move:up %d" %(self.deviceID))
            ret = self.instQuery(":move:up? %d" %(self.deviceID))
        else:
            self.instWrite(":move:down %d" %(self.deviceID))
            ret = self.instQuery(":move:down? %d" %(self.deviceID))

        if not ret.strip() == "TRUE":
            raise ProbeStationError(ret)

    #Moves the Chuck stage in X, Y, Z and Theta to the load position.
    def MoveChuckLoad(self, Pos=1):
        self.instWrite(":mov:load %d" %(self.deviceID))

    def SetContactSpeed(self, Vel):
        speed = int(500 * Vel/100)

        self.instWrite(":set:cont:spee %d " %(speed))
        out = self.instQuery(":set:cont:spee?")

        if int(out) != speed: 
            raise ProbeStationError("Setting contact Speed unsuccessful!")

    def SetVelocity(self, Vel, direction="xyz"):
       
        if Vel < 20:
            speed = "uslow"
        elif Vel < 35:
            speed = "vslow"
        elif Vel < 45:
            speed = "slow"
        elif Vel < 55:
            speed = "medium"
        elif Vel < 65: 
            speed = "fast"
        elif Vel < 80:
            speed = "vfast"
        else:
            speed = "ufast"

        self.instWrite(":set:vel %d %s %s" %(self.deviceID, direction, speed))


    
    #Moves the chuck Z axis to the separation height. Returns error if no Contact height is set.
    def MoveChuckSeparation(self, Vel=100):

        self.SetContactSpeed(Vel)

        self.instWrite(":mov:sep  %d" %(self.deviceID))
        ret = self.instQuery(":mov:sep ? %d" %(self.deviceID))
        if not ret.strip() == "TRUE":
            raise ProbeStationError(ret)

    #Moves the Chuck to Home position.
    def MoveChuckHome(self, Vel=100):
        self.SetVelocity(Vel)
        self.instWrite(":mov:home %d" %(self.deviceID))

    #The command gets the actual wafer size which is stored in the electronics.
    def ReadChuckIndex(self, Pos=1):
        output = None
        ret = self.instQuery(":move:probeplan:absolute:die? %d" %(self.deviceID))
        if not type(None):
            ret = ret.split(' ')
            output = []
            first = True
            for x in ret:
                if first:
                    output.append(float(x))
                else:
                    output.append(float(x))
                first = False
        return output

    #Returns the actual chuck stage position in X, Y and Z. The default Compensation Mode is the currently activated compensation mode of the kernel. 
    def ReadChuckPosition(self, Unit="Y", PosRef="H"):
        output = None
        ret = self.instQuery(":move:absolute? %d %s %s" %(self.deviceID))
        if not ret == None:
            ret = ret.split(' ')
            output = []
            first = True
            for x in ret:
                if first:
                    output.append(-float(x))
                else:
                    output.append(-float(x))
                first = False
            return output

    def ReadChuckPositionX(self):
        ret = self.instQuery(":move:absolute? %d %s %s" %(self.deviceID))
        ret = ret.split(' ')
        output = []
        for x in ret:
            output.append(float(x))
        return -output[0]
    
    def ReadChuckPositionY(self):
        ret = self.instQuery(":move:absolute? %d %s %s" %(self.deviceID))
        ret = ret.split(' ')
        output = []
        for x in ret:
            output.append(float(x))
        return -output[1]
    
    def ReadChuckPositionZ(self):
        ret = self.instQuery(":move:absolute? %d %s %s" %(self.deviceID))
        ret = ret.split(' ')
        output = []
        for x in ret:
            output.append(float(x))
        return -output[2]

    #Read the actual set or calculated temperature.
    def ReadChuckThermoValue(self):
        ret = self.instQuery(":ther:temp:curr?")
        ret = ret.split(' ')[1:]
        output = []
        for x in ret:
            output.append(float(x))
        return output

    # System identification
    def SystemIndentificaiton(self):
        ret = self.instQuery(":syst:iden?")
        return ret

    #Read the actual set or calculated temperature.
    def ReadChuckStatus(self):
        ret = self.instQuery(":system:error?")
        return ret

    #TemperatureChuck control
    ##############################################################
    
    #Read the actual set or calculated temperature.
    def EnableHeaterHoldMode(self, en):
        if en:
            ret = self.instQuery(":ther:acti")
        else:
            ret = self.instQuery(":ther:deac")
        if ret == 0:
            return True
        else:
            return False

    #This command returns the current dew point temperature, if a dew point sensor is connected. The default unit of the temperature is degrees Celsius. 
    def GetDewPointTemp(self):
        None

    #This command reads the current temperature of the chuck and determines the status of the thermal system. The default unit is degrees Celsius.  
    def GetHeaterTemp(self):
        ret = self.instQuery(":ther:temp:curr?")
        return float(ret)
    
    #This command reads the target temperature of the chuck. The default unit is degrees Celsius.
    def GetTargetTemp(self):
        ret = self.inst.query(":ther:temp:targ?")
        return float(ret)

    #This command sets a new target temperature and starts the heating or cooling of the chuck. An answer to the command will be returned after reaching the given temperature and waiting the soak time or an unexpected interrupt of the process. Given back is the already reached temperature. The default unit is degrees Celsius.
    def HeatChuck(self, temp):
        self.instWrite(" :ther:temp:sett %s" %(temp))
        
    #This command sets a new target temperature and starts the heating or cooling of the temperature chuck. The response is returned immediately. 
    #Given back is the new target temperature. The default unit is degrees Celsius. 
    def SetHeaterTemp(self, temp):
        self.instWrite(":ther:temp:sett %s %s" %(temp))

    #This command sets a new soak time value. The unit of the value is seconds. If soak time is actually running, it may be affected by the change.
    def SetHeaterSoak(self, time):
        None

    #This command sets a new soak time value. The unit of the value is seconds. If soak time is actually running, it may be affected by the change.
    def StopHeatChuck(self):
        self.instWrite("StopHeatChuck")

    def SetTemperatureWindow(self, temp):
        self.checkTempWindow(temp)
        self.instWrite(":ther:temp:wind %s" %(temp))
        
    def GetTemperatureWindow(self):
        ret = self.instQuery(":ther:temp:wind?")
        return float(ret)
    

    ############################################
    ############## check Values:################ 
    def checkIndex(self, n, axis): 
        if not isinstance(n, int):
            raise ProbeStation_InputError("The index for axis %s must be an int between 0 and 50." %(axis))
        if n < -50 or n > 50: 
            raise ProbeStation_InputError("The index for axis %s must be an int between 0 and 50." %(axis))

    def checkXYValue(self, n, axis): 
        if not isinstance(n, (float, int)):
            raise ProbeStation_InputError("The index for axis %s must be a double value between 0 and +-150000. (Cur. Val. %s)" %(axis, n))
        if n < -150000 or n > 150000: 
            raise ProbeStation_InputError("The index for axis %s must be a double value between 0 and +-150000. (Cur. Val. %s)" %(axis, n))

    def checkPosRef(self, pos): 
        if not isinstance(pos, str):
            raise ProbeStation_InputError("The position reference must be 'H' (Home), 'Z' (Zero), 'C' (Center) or 'R' (Current position).")
        if not (pos == 'H' or pos == 'R'):
            raise ProbeStation_InputError("The position reference must be 'H' (Home), 'R' (Current position).")
    
    def checkTempWindow(self, temp):
        if not isinstance(temp, (float,int)):
            raise ProbeStation_InputError("The temperature window must be a float value between 0.1 and 9.9C.")
        if 0.1 < temp > 9.9:
            raise ProbeStation_InputError("The temperature window must be a float value between 0.1 and 9.9C.")
        
    #Read the Scope Status.
    def ReadScopeStatus(self):
        ret = self.instQuery("ReadScopeStatus")
        ret = ret.split(' ')[1:]
        return ret
        
class SUSS_PA300(FormFactor): 

    ProbeStationName = "SUSS PA300"
    
class Cascade_CM300(FormFactor): 

    ProbeStationName = "Cascade CM300"
    