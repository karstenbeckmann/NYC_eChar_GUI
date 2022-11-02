

class ToolError(Exception):

    def __init__(self, message, eChar=None, *args):
        self.message = "Tool Error: %s" %(message) 

        self.eChar = eChar
        if self.eChar != None: 
            self.eChar.writeError(self.message)

            
class ToolInputError(ToolError):

    def __init__(self, message, eChar=None, *args):
        self.message = "Input Error: %s" %(message) 

        self.eChar = eChar
        if self.eChar != None: 
            self.eChar.writeError(self.message)

            
class OperationError(ToolError):

    def __init__(self, message, eChar=None, *args):
        self.message = "Operation Error: %s" %(message) 

        self.eChar = eChar
        if self.eChar != None: 
            self.eChar.writeError(self.message)

class CommunicationError(ToolInputError):
    
    def __init__(self, message, eChar=None, *args):
        self.message = "Communication Error: %s" %(message) 

        self.eChar = eChar
        if self.eChar != None: 
            self.eChar.writeError(self.message)

class B1500AError(ToolError):
    def __init__(self, message, eChar=None, *args):
        self.message = "B1500: %s" %(message) 

        super().__init__(message, eChar, *args)

class B1500A_InputError(ToolInputError):
    def __init__(self, message, eChar=None, *args):
        self.message = "B1500A Wrong Input: %s" %(message) 

        super().__init__(message, eChar, *args)
        
class B1500A_TestError(B1500AError):
    def __init__(self, message, eChar=None, *args):
        self.message = "Self-Test: %s" %(message) 

        super().__init__(message, eChar, *args)

class B1500A_CalibrationError(B1500AError):
    def __init__(self, message, eChar=None, *args):
        self.message = "Calibration: %s" %(message) 

        super().__init__(message, eChar, *args)
        
class B1530AError(ToolError):
    def __init__(self, message, eChar=None, *args):
        self.message = "B1530: %s" %(message) 

        super().__init__(message, eChar, *args)

class B1530A_InputError(ToolInputError):
    def __init__(self, message, eChar=None, *args):
        self.message = "B1530A Wrong Input: %s" %(message) 

        super().__init__(message, eChar, *args)
        
class B1530A_SessionExistsError(ToolError):
    def __init__(self, message="", eChar=None, *args):
        self.message = "B1530A A session has already been opened. %s" %(message)

        super().__init__(message, eChar, *args)
        
class ProbeStationError(B1530AError):
    def __init__(self, message, eChar=None, *args):
        self.message = "ProbeStation: %s" %(message) 

        super().__init__(message, eChar, *args)

        
class BNC_Model765Error(ToolError):
    def __init__(self, message, eChar=None, *args):
        self.message = "BNC_Model765: %s" %(message) 

        super().__init__(message, eChar, *args)

class BNC_Model765_InputError(ToolInputError):
    def __init__(self, message, eChar=None, *args):
        self.message = "BNC Model 765 Wrong Input: %s" %(message) 

        super().__init__(message, eChar, *args)
        
class ProbeStationError(ToolError):
    def __init__(self, message, eChar=None, *args):
        self.message = "ProbeStation: %s" %(message) 

        super().__init__(message, eChar, *args)

class ProbeStation_InputError(ToolInputError):
    def __init__(self, message, eChar=None, *args):
        self.message = "Probe Station Wrong Input: %s" %(message) 

        super().__init__(message, eChar, *args)

class E5274AError(ToolError):
    def __init__(self, message, eChar=None, *args):
        self.message = "E5274A: %s" %(message) 

        super().__init__(message, eChar, *args)

class E5274A_InputError(ToolInputError):
    def __init__(self, message, eChar=None, *args):
        self.message = "E5274A Wrong Input: %s" %(message) 

        super().__init__(message, eChar, *args)
        
class E5274A_TestError(E5274AError):
    def __init__(self, message, eChar=None, *args):
        self.message = "Self-Test: %s" %(message) 

        super().__init__(message, eChar, *args)

class E5274A_CalibrationError(E5274AError):
    def __init__(self, message, eChar=None, *args):
        self.message = "Calibration: %s" %(message) 

        super().__init__(message, eChar, *args)
        
class LeCroy_Osc_Error(ToolError):
    def __init__(self, message, eChar=None, *args):
        self.message = "LeCroy WP740Zi: %s" %(message) 

        super().__init__(message, eChar, *args)

class LeCroy_Osc_InputError(ToolInputError):
    def __init__(self, message, eChar=None, *args):
        self.message = "LeCroy WP740Zi Wrong Input: %s" %(message) 

        super().__init__(message, eChar, *args)

        
class Keithley_707A_Error(ToolError):
    def __init__(self, message, eChar=None, *args):
        self.message = "Keithley_707A: %s" %(message) 

        super().__init__(message, eChar, *args)

class Keithley_707A_InputError(ToolInputError):
    def __init__(self, message, eChar=None, *args):
        self.message = "Keithley_707A Wrong Input: %s" %(message) 

        super().__init__(message, eChar, *args)
        
class B1110A_Error(ToolError):
    def __init__(self, message, eChar=None, *args):
        self.message = "B1110A: %s" %(message) 

        super().__init__(message, eChar, *args)

class B1110A_InputError(ToolInputError):
    def __init__(self, message, eChar=None, *args):
        self.message = "B1110A Wrong Input: %s" %(message) 

        super().__init__(message, eChar, *args)

        
class B1110A_SelfTestError(B1110A_Error):
    def __init__(self, message, eChar=None, *args):
        self.message = "Self-Test: %s" %(message) 

        super().__init__(message, eChar, *args)