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
import pyqtgraph as pg

import inspect

def f():
    print(inspect.stack()[1][3])

def g():
    f()
 
g()
