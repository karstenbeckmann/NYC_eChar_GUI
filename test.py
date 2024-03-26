import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import os as os
from win32com.shell import shell, shellcon
import pyvisa as vs 
import StdDefinitions as std
import time as tm
import numpy as np
from ctypes import *
from Exceptions import *



dataOrg = np.array([2,3,4,10,20,20,30,50], dtype=float)
dataNew1 = np.array([0,1,4,10,20,30,50], dtype=float)
dataNew2 = np.array([0,4,510,30,50], dtype=float)

orgShape = np.shape(dataOrg)
newShape = np.shape(dataNew1)

if len(orgShape) == 3:
    dataOrg = np.append(dataOrg, dataNew1, axis=0)

elif len(orgShape) == 2:
    newShape = (orgShape[0], orgShape[1] + newShape[1])
    tempData = np.empty(newShape, dtype=float)
    for m in range(orgShape[0]):
        tempData[m][0:orgShape[1]] = dataOrg[m]
        tempData[m][orgShape[1]:] = dataNew1[m]
    dataOrg = tempData
else:
    newShape = orgShape[0] + newShape[0]
    tempData = np.empty(newShape, dtype=float)
    tempData[0:orgShape[0]] = dataOrg
    tempData[orgShape[0]:] = dataNew1
    dataOrg = tempData


print(np.shape(dataOrg), dataOrg,np.shape(dataOrg)[0]-5)

dataOrg = np.delete(dataOrg, np.s_[:np.shape(dataOrg)[0]-5])
print(np.shape(dataOrg), dataOrg)