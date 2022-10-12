
"""
This is the standard Frame that introduces the distribution of necessary variables and subclasses for the all Frames
Written by: Karsten Beckmann
Date: 01/01/2019
email: kbeckmann@sunypoly.edu
"""

import sys
from ctypes import *
import win32api
import win32con
import PlottingRoutines as PR
import threading as th
import queue as qu 
import time as tm
import StdDefinitions as std
import copy as dp
import os as os
import functools
from PyQt5 import QtWidgets, QtCore, QtGui
import Qt_stdObjects as stdObj

#parent, MainGI, columns, rows, horHeader=None, vertHeader=None, content=None

class SpecTable(stdObj.Table):

    def __init__(self, parent, MainGI, **kwargs):
        
        self.rows = 2
        self.columns = 7
        self.MainGI = MainGI
        self.Configuration = self.MainGI.getConfiguration()
        self.specs = self.Configuration.getSpecs()
        horHeader = ["Name", "SpecCode", "Target", "Spec High", "Spec Low", "Yield High", "Yield Low"]
        super().__init__(parent, MainGI, self.columns, self.rows, **kwargs, horHeader=horHeader)
        self.MainGI = MainGI
        self.width = self.MainGI.getWindowWidth()

    def update(self, specs):
        
        rows = len(specs)
        self.setRowCount(rows)

        self.clearContents()  
        n = 0  
        for spec in specs:
            self.writeRow(n, [spec['Name'],spec['Code'],spec['Target'],spec['SpecLow'],spec['SpecHigh'],spec['YieldLow'], spec['YieldHigh']])
            n = n+1

        self.resizeColumnsToContents()
        self.resizeRowsToContents()

        
class MatrixTable(stdObj.Table):

    def __init__(self, parent, MainGI, **kwargs):
        
        self.rows = 2
        self.columns = 6
        self.MainGI = MainGI
        self.Configuration = self.MainGI.getConfiguration()
        self.specs = self.Configuration.getSpecs()
        horHeader = ["BreakMake", "MakeBreak", "Normal Inputs", "Normal Outputs", "Bit Inputs", "Bit Outputs"]
        super().__init__(parent, MainGI, self.columns, self.rows, **kwargs, horHeader=horHeader)
        self.MainGI = MainGI
        self.width = self.MainGI.getWindowWidth()
    
    def update(self, data):
        data = dp.deepcopy(data)
        self.clearContents()
        for key, value in data.items():
            for n in range(len(value)):
                if value[n] == None or value[n] == []:
                    data[key][n] = ["-"]
        rows = len(data['BreakMake'])
        self.setRowCount(rows)

        for n in range(rows):
            BM = ",".join([str(i) for i in data['BreakMake'][n]])
            MB = ",".join([str(i) for i in data['MakeBreak'][n]])
            NI = ",".join([str(i) for i in data['NormalInputs'][n]])
            NO = ",".join([str(i) for i in data['NormalOutputs'][n]])
            BI = ",".join([str(i) for i in data['BitInputs'][n]])
            BO = ",".join([str(i) for i in data['BitOutputs'][n]])

            self.writeRow(n,[BM, MB, NI, NO, BI, BO])

        self.resizeColumnsToContents()
        self.resizeRowsToContents()