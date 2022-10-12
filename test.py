import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import os as os
from win32com.shell import shell, shellcon
import BerkeleyNuc as BC
import pyvisa as vs 
import StdDefinitions as std
import time as tm
import numpy as np
from ctypes import *


arr = [-1.5e-13, 2.5e-13, 0.0, -3.5e-13, -2e-13, -4.5e-13, -3.5e-13, -3.5e-13, -2.5e-13, 6e-13]

a = np.array(arr)
b = 1

calcRes = np.absolute(np.divide(b,a, out=np.full(len(a), 2e20, dtype=float), where=a!=0))


print(calcRes)
#print(np.divide(a,b, out=np.zeros_like(b, dtype=float), where=a!=0))
cSize = c_int()
size = 5
cSize.value = size
print(size)
ret = c_int()*(size)

#cl = BC.BNC_Model765(rm, "TCPIP0::AT::inst0::INSTR")
