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
import time as tm

#2 Slot Keithley 707A Switching Matric: 
#This programm is configured for a 2 Slot using 7174  setup with 24 output connections and 8 input connections
class Keithley_707A:

    inst = None
    printOutput = False
    RelayDelayTime = 0.015 #Relay delay time in sec
    RowStatus = [0]*8 # RowStatus; 0 for Dont care; 1 for Make/Break; 2 for Break/Make
    SRQParameter = int(8) # 8 sets SRQByte when matrix is ready
    row = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    rowDic = {'A':1, 'B':2, 'C':3, 'D':4, 'E':5, 'F':6, 'G':7, 'H':8}

    def __init__(self, rm=None, GPIB_adr=None, Device=None):

        if (rm == None or GPIB_adr == None) and Device == None:
            self.write("Matrix707A: Either rm and GPIB_adr or a device must be given transmitted")  #maybe a problem, tranmitting None type
        elif Device == None:    

            try:
                self.inst = rm.open_resource(GPIB_adr)
                
            except:
                self.write("Matrix707A: The device %s does not exist." %(GPIB_adr))  #maybe a problem, tranmitting None type
        
        else:
                self.inst = Device

        self.instWrite("*IDN?\n")
        tm.sleep(0.1)
        ret = self.instRead()
        if ret.strip() == "707A03": ###Update
            self.write("You are using %s!" %(ret[:-4]))
        else:
            #print("You are using the wrong agilent tool!")
            exit("You are using the wrong tool!")
        #print(ret)

        # do if Agilent\sTechnologies,E5270A,0,A.01.05\r\n then correct, else the agilent tool you are using is incorrect

        self.instWrite("J0") # Self-test 
        self.instWrite("P0X") # Reset
        self.SRQByte(self.SRQParameter) # set SRQByte to specified value
        self.editMemorySetup(0)     #Sets the relays as the standard memory setup

    def turnOffline(self):
        self.inst.clear()
        self.inst.close()

    def instWrite(self, command):
        self.inst.write(command)
        if self.printOutput:
            print("Write: ", command)

    def initialize(self):
        self.RestoreDefault()

    def instQuery(self, command):
        ret = self.inst.query(command)
        if self.printOutput:
            print("Query: ", command)
        return ret
    
    def instRead(self):
        ret = self.inst.read()
        if self.printOutput:
            print("Read!")
        return ret

    def write(self, command):
        if self.printOutput:
            print(command)

    def StoreConnection(self, ConList):
        None
    
    def SetStoredConnection(self, location):
        None
    

    def CheckConList(self, ConList):
        
        row = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        if not ConList == None:
            if not type(ConList) == list:
                raise ValueError("The Connection List must be of type List.")
            if len(ConList) < 1:
                raise ValueError("The Connection List must be of type List and have at least 1 entry.")
            for con in ConList: 
                if not type(con) == list:
                    raise ValueError("The Connections in Connection List must be of type List (2 entries.")
                if not len(con) == 2:
                    raise ValueError("The Connection entries can only contain the row and column list (size 2)")
                if not con[0] in row:
                    raise ValueError("The row entry of con must only contain the letters A to H.")
                if con[1] < 1 or con[1] > 24:
                    raise ValueError("The column entry of the conection must be between 1 and 24.")
                
             
    def CheckMatrix(self, Matrix):
        if not Matrix == None:
            if not type(Matrix) == list:
                raise ValueError("The Connection Matrix must be of type List.")
            if len(Matrix) > 8 or len(Matrix) < 1:
                raise ValueError("The maximum row size of the connection Matrix is 8 but must have at least one entry.")
            for cons in Matrix: 
                if not type(cons) == list:
                    raise ValueError("The Connection Matrix must be a 2D List.")
                if len(cons) > 24 or len(cons) < 1:
                    raise ValueError("The number of columns is 24 for this installation but at least one column must befined.")
                for con in cons: 
                    if not isinstance(con, bool):
                        raise ValueError("The connection matrix entries can only contain boolean values.")

    def CheckMakeBreak(self, MakeBreak, BreakMake):
        row = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        if not isinstance(MakeBreak, list) or not isinstance(BreakMake, list): 
            raise ValueError("MakeBreak and BreakMake must be of the type list.")
        if len(MakeBreak)+len(MakeBreak) > 8:
            raise ValueError("MakeBreak and BreakMake cannot contain more than 8 entries.")
        for entry in MakeBreak:
            if not entry in row:
                raise ValueError("MakeBreak must only contain a list of rows from 'A' to 'H'.")
            if entry in MakeBreak:
                raise ValueError("MakeBreak and BreakMake must contain mutually exlusive rows.")
        for entry in BreakMake:
            if not entry in row:
                raise ValueError("BreakMake must only contain a list of rows from 'A' to 'H'.")

    def setMakeBreak(self, MakeBreak):
        row = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        Wri = "V"
        for n in range(8):
            if row[n] in MakeBreak:
                Wri = "%s1"%(Wri)
            else:
                Wri = "%s0"%(Wri)
        Wri = "%sX"%(Wri)
        self.instWrite(Wri)
        
    def setBreakMake(self, BreakMake):
        row = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        Wri = "W"
        for n in range(8):
            if row[n] in BreakMake:
                Wri = "%s1"%(Wri)
            else:
                Wri = "%s0"%(Wri)
        Wri = "%sX"%(Wri)
        self.instWrite(Wri)
    
    #Copy the from relay/memory setup to relay/memory setup; 
    #0 represents the relay setup
    #1 to 100 the memory location
    def CopySetup(self, IN, OUT):
        if not isinstance(IN,int):
            raise ValueError("Input must be an integer!")
        if not isinstance(OUT,int):
            raise ValueError("Input must be an integer!")
        wri = "Z%d,%dX" %(IN,OUT)
        self.instWrite(wri)

    def EnableTrigger(self):
        self.instWrite("F0X")

    def DisableTrigger(self):
        self.instWrite("F1X")
    
    #enables to edit the relay
    def editRelay(self):
        self.instWrite("E0X")

    #enables the memory setup 'n' to be edited
    #n may be 0 for the relay 
    #n may be a memory position between 1 and 100
    def editMemorySetup(self,n):
        if not isinstance(n, int):
            raise ValueError("the parameter must be an integer from 0 to 100.")
        if n > 100 or n < 0: 
            raise ValueError("the parameter must be an integer from 0 to 100.")
        self.instWrite("E%dX" %(n))

    #Set the output format (standard is 0, full detail)
    #see the 707A manual for more detail on 4-24
    def SetOutputFormat(self, n):
        if not isinstance(n, int):
            raise ValueError("The parameter must be an integer from 0 to 7.")
        if n > 9 or n < 0: 
            raise ValueError("The settling time must be an integer from 0 to 7.")
        self.instWrite("G%dX" %(n))

    #Sets the Matrix Ready output
    #True: Positive True 
    #False: Posistive False
    def MatrixReady(self, param):
        if not isinstance(param, bool):
            raise ValueError("The parameter must be a boolean value.")
        if param: 
            self.instWrite("B1X")
        else:
            self.instWrite("B0X")
    
    #Sets the External Trigger Flank
    #0 for Falling edge flank
    #1 for Rising edge flank
    def SetExternalTriggerFlank(self, n):
        if not isinstance(n, int):
            raise ValueError("n must be an integer of 0 or 1.")
        if n > 1 or n < 0: 
            raise ValueError("n must be an integer of 0 or 1.")
        self.instWrite("A%dX" %(n))


    #Write the text on the display, will cut of after 14 letters
    def editDisplay(self, text):
        dis = str(text)
        dis = dis[:14]
        self.instWrite("D%sX" %(dis))

    #Program the settling time
    #setTime can be between 0 and 65000ms (65s)
    def setSettlingTime(self, setTime):
        if not isinstance(setTime, int):
            raise ValueError("The settling time must be an integer from 0 to 65000 (in ms).")
        if setTime > 9 or setTime < 0: 
            raise ValueError("The settling time must be an integer from 0 to 65000 (in ms).")
        self.instWrite("S%dX" %(setTime))
    
    #Restore to factory settings, delete all memory setups and relay setup
    def RestoreDefault(self):
        self.instWrite("R0X")
    
    #Deletes one Setup from the memory
    def deleteSetup(self, setup):
        if not isinstance(setup, int):
            raise ValueError("The setup number must be an integer 1 to 100.")
        if setup > 100 or setup < 1: 
            raise ValueError("The setup number must be an integer 1 to 100.")
        self.instWrite("Q%dX" %(setup))

    #Clears Crosspoints
    #n = 0, deletes current relay setup
    #n = 1-100, deletes the stored relay setup
    def ClearCrosspoint(self, n):
        if not isinstance(n, int):
            raise ValueError("The setup number must be an integer 0 to 100.")
        if n > 100 or n < 0: 
            raise ValueError("The setup number must be an integer 0 to 100.")
        self.instWrite("P%dX" %(n))

    #Sets the Digital Output:
    #n represents the number for the digital bits
    #this sets the digital output pins 17 to 24,
    #the integer n represents the bit weight starting at 17 with 1 and ending at 24 with 128
    def SetDigitalOutput(self, n):
        if not isinstance(n, int):
            raise ValueError("The number for the digital outputs must be an integer 0 to 255.")
        if n > 255 or n < 0: 
            raise ValueError("The number for the digital outputs must be an integer 0 to 255.")
        self.instWrite("O%dX" %(n))

    #set the trigger type: 
    #Trigger 0 or 1: Trigger on Talk
    #Trigger 2 or 3: Trigger on Get
    #Trigger 4 or 5: Trigger on "X" (execute command)
    #Trigger 6 or 7: Trigger on External Trigger pulse (+5V)
    #Trigger 8 or 9: Trigger on Front MANUAL key
    def setTrigger(self, trigger):
        if not isinstance(trigger, int):
            raise ValueError("the trigger type must be an integer from 0 to 9.")
        if trigger > 9 or trigger < 0: 
            raise ValueError("the trigger type must be an integer from 0 to 9.")
        
        self.instWrite("F0T%dX" %(trigger))
        self.instWrite("F1X")
    
    #Insert Blank Setup at n 
    #n must be a setup position between 1 and 100
    def InsertBlankSetup(self,n):
        if not isinstance(n, int):
            raise ValueError("the parameter must be an integer from 1 to 100.")
        if n > 100 or n < 0: 
            raise ValueError("the parameter must be an integer from 1 to 100.")
        self.instWrite("I%dX" %(n))

    #Set EOI and Hold-off
    #0: Send EOI with last byte, hold off on X until Ready
    #1: No EOI, hold-off on X until Ready
    #2: Send EOI with last byte, do not hold-off
    #3: No EOI, do not hold-off on X
    #4: Send EOI with last byte, hold-off on X until Ready
    #5: No EOI, hold-off on X until Matrix Ready
    def SetEOI_HoldOff(self, n):
        if not isinstance(n, int):
            raise ValueError("the parameter must be an integer from 0 to 5.")
        if n > 5 or n < 0: 
            raise ValueError("the parameter must be an integer from 0 to 5.")
        self.instWrite("K%dX"%(n))

    def execute(self):
        self.instWrite("X")

    #Retrieve tha status of the Switching matrix
    #Parameter 0: Send machine status work
    #Parameter 1: Send error status word
    #Parameter 2: output setup, needs subparameter 0 (relay) or 1-100 (memory)
    #Parameter 3: send vlaue of RELAY STEP pointer.
    #Parameter 4: send number of slaves
    #Parameter 5: Send ID of each card in unit "0-1" (specify in subparameter)
    #Parameter 6: Send longest relay settling time
    #Parameter 7: Send digital input unit
    #Parameter 8: Send RELAY TEST input
    def getStatus(self,parameter, subparameter=None):
        if not isinstance(parameter,int) or (not isinstance(subparameter,int) and not subparameter == None):
            raise ValueError("Input parameters must be an integer!")
        if parameter > 0 or parameter < 8:
            wri = "U%dX" %(parameter)
            if parameter == 2:
                if subparameter == None:
                    raise ValueError("Please specify the relay (0) or stored setups (1-100).")
                if subparameter > 100 or subparameter < 0:
                    raise ValueError("Please specify the relay (0) or stored setups (1-100).")
                wri = "U2,%dX" %(subparameter)
            if parameter == 5:
                if subparameter == None:
                    raise ValueError("Please specify the card unit 0 or 1.")
                if subparameter > 1 or subparameter < 0:
                    raise ValueError("Please specify the card unit 0 or 1.")

                wri = "U5,%dX" %(subparameter)
        else:
            raise ValueError("Input parameter must be an integer between 0 and 8.")

        ret = self.instQuery(wri)
        return ret

    #Set SRQ and Serial Poll Byte:
    #0 SRQ disabled
    #2 Front panel key press
    #4 Digital I/O interrupt
    #8 Matrix Ready
    #16 Ready for trigger
    #32 Error
    def SRQByte(self, n):
        if not isinstance(n, int):
            raise ValueError("n must be an integer.")
        if not n in [0,2,4,8,16,32]:
            raise ValueError("n must be 0, 1, 2, 4, 8, 16, 32.")
    
    #Opens a Crosspoint (either relay or memory in dependence on what the endpointer defined)
    #row: A to H
    #Column: 1 - 24
    def OpenCrosspoint(self, row, column, execute=True):
        if not isinstance(row, str) or not isinstance(column, int):
            raise ValueError("Row must be a string from A to H and Column must an integer form 1 to 24. (Row: %s, Column:%s)" %(row, column))
        if column > 24 and column < 1: 
            raise ValueError("Row must be a string from A to H and Column must an integer form 1 to 24. (Row: %s, Column:%s)" %(row, column))
        if len(row) > 1 or not row in self.row:
            raise ValueError("Row must be a string from A to H and Column must an integer form 1 to 24. (Row: %s, Column:%s)" %(row, column))
        if execute:
            self.instWrite("N%s%dX" %(row, column))
        else:
            self.instWrite("N%s%d" %(row, column))
    
    def CloseCrosspoint(self, row, column, execute=True):
        if not isinstance(row, str) or not isinstance(column, int):
            raise ValueError("Row must be a string from A to H and Column must an integer form 1 to 24. (Row: %s, Column:%s)" %(row, column))
        if column > 24 and column < 1: 
            raise ValueError("Row must be a string from A to H and Column must an integer form 1 to 24. (Row: %s, Column:%s)" %(row, column))
        if len(row) > 1 or not row in self.row:
            raise ValueError("Row must be a string from A to H and Column must an integer form 1 to 24. (Row: %s, Column:%s)" %(row, column))
        if execute:
            self.instWrite("C%s%dX" %(row, column))
        else:
            self.instWrite("C%s%d" %(row, column))
    
        
    #Set a new Connections
    #ConList contains a 2D lists with Row and Column (row: A-H; col: 1-24)
    #Matrix contains a boolean matrix with a max. size of 8x24 which correspond to the rows (8) and columns (24)
    #MakeBreak contains the rows that will Make the new connection first and then break it. 
    #BreakMake contains the rows that will Break the old connections first and then Make the new ones.
    #Make/Break and BreakMake are complimentary, the cannot contain the same row, if the row is not in MakeBreak, it is dont care. 
    def SetConnections(self, ConList=None, Matrix=None, 
                        MakeBreak=[], BreakMake=[], 
                        SetupPosition=0):
        if ConList == None and Matrix==None: 
            raise ValueError("Either 'ConList' or 'Matrix' must be defined")
        self.CheckConList(ConList)
        self.CheckMatrix(Matrix)

        self.CheckMakeBreak(MakeBreak, BreakMake)
        
        self.editMemorySetup(SetupPosition)
        self.ClearCrosspoint(SetupPosition)

        self.setMakeBreak(MakeBreak)
        self.setBreakMake(BreakMake)

        if ConList == None:
            ConList = []
            n = 0
            m = 1
            for rows in Matrix:
                for col in rows:
                    ConList.append([self.row[n], m])
                    m+=1
                n+=1
        
        l = 0
        CCstr = "C"
        for con in ConList:
            l+=1
            CCstr = "%s,%s%d" %(CCstr,con[0],con[1])
            if l == 25:
                self.instWrite("%sX" %CCstr)
                CCstr = "C"
                l = 0

    def rowIntToStr(self, n):  
        if isinstance(n, list):
            ret = []
            for m in n: 
                ret.append(self.row[m-1])
        else:
            ret = self.row[n-1]
        return ret

    def ClearMakeBreak(self):
        self.setMakeBreak([])
        self.setBreakMake([])
    
    def MakeBreak(self, MakeBreak):
        self.CheckMakeBreak(MakeBreak, [])
        self.setMakeBreak(MakeBreak)

    def BreakMake(self, BreakMake):
        self.CheckMakeBreak([], BreakMake)
        self.setBreakMake(BreakMake)
