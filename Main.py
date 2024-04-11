
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QFileInfo
from ctypes import *
import win32api
import win32con
import time
import threading as th
import ECharacterization as EC
import datetime as dt
import Configuration as cf
import pyvisa as vs
import DataHandling as dh
import time as tm
import copy as cp
import numpy as np
import StdDefinitions as std
import queue as qu
import ToolHandle as tool
import Qt_MainButtons as Qt_MB
import screeninfo as scrInfo
import glob, imp
import os as os

import ResultHandling as RH

import Qt_WaferMap as Qt_WM
import Qt_stdObjects as stdObj
import Qt_MeasTab as Qt_MT
import Qt_Config as Qt_CF
import Qt_ResultWindow as Qt_RW
import Qt_Tables as Qt_TB
import Qt_B1500A as Qt_B1500A
import Qt_E5274A as Qt_E5274A
import Qt_MainWindow as Qt_Main
import qdarktheme as qtdt
import darkdetect
import ctypes
myappid = 'mycompany.myproduct.subproduct.version' 
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
time.sleep(0.1)

def hideConsole():
    """
    Hides the console window in GUI mode. Necessary for frozen application, because
    this application support both, command line processing AND GUI mode and theirfor
    cannot be run via pythonw.exe.
    """
    whnd = windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        windll.user32.ShowWindow(whnd, 0)
        # if you wanted to close the handles...
        #ctypes.windll.kernel32.CloseHandle(whnd)

 

def showConsole():
    """
    Shows the console window in GUI mode. Necessary for frozen application, because
    this application support both, command line processing AND GUI mode and theirfor
    cannot be run via pythonw.exe.
    """
    whnd = windll.kernel32.GetConsoleWindow()
    if whnd == 0:
        windll.user32.ShowWindow(whnd, 1)
        # if you wanted to close the handles...
        #ctypes.windll.kernel32.CloseHandle(whnd)
    
try:
    Instruments = tool.ToolHandle(offline=False)
except SystemError as e:
    print(e)
    sys.exit()

qtdt.enable_hi_dpi()
app = QtWidgets.QApplication(sys.argv + ['-platform', 'windows:darkmode=2'])

# Force the style to be the same on all OSs:
app.setStyle("Fusion")

#set Icon
iconPath = "etc/icon.ico"
iconPath =  os.path.join(os.getcwd(),iconPath)
app.setWindowIcon(QtGui.QIcon(iconPath))

#set Dark Mode based on System
qtdt.setup_theme("auto")


app.setQuitOnLastWindowClosed(False)
desk = QtWidgets.QDesktopWidget()


try:
    hideConsole()
except Exception as e:
    print(e)

monHeight = desk.availableGeometry(0).size().height()

if monHeight > 1080: 
    size = 'extralarge'
elif monHeight > 768:
    size = 'large'
elif monHeight > 600:
    size = 'medium'
else:
    size = 'small'

Configuration = cf.Configuration('config.csv')

eChar = EC.ECharacterization(Instruments, WaferChar=True, Configuration=Configuration)
#eChar.setWaferID(WaferID)
#eChar.Subfolder=Subfolder


ProStat = Instruments.getProberInstrument()
if ProStat != None:
    ProStat.setTimeOut(60000)
    initPos = ProStat.ReadChuckPosition("X","C")
    initPosMic = ProStat.ReadChuckPosition("Y","C")

updateTime = 0.2

threads = qu.Queue()


ui = Qt_Main.MainUI(app, size,"Wafer Map",Configuration, eChar, Instruments, threads,icon=iconPath)
ui.show()

sys.exit(app.exec_())

