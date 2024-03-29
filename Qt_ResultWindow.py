
import sys
from ctypes import *
import win32api
import win32con
import PlottingRoutines as PR
import threading as th
import queue as qu 
import time as tm
import traceback
import StdDefinitions as std
import copy as dp
import os as os
import functools
import queue as qu
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PyQt5 import QtWidgets, QtCore, QtGui
import Qt_stdObjects as stdObj


class ResultWindow(QtWidgets.QMainWindow):
    
    ErrorQu = qu.Queue()

    def __init__(self, MainGI, QFont=None, QMargin=None, QSpacing=None, width=600, height=400, icon=None, title="Results"):


        self.styles = ["-", "--", ":", "-.", ".", ",", "o", "v", "^", "<", ">"]
        self.sizes = [0.5,1,1.5,2,3]
        self.colors = ['blue', 'red', 'black', 'green', "orange"]    
        
        self.QFont=QFont
        self.QMargin = QMargin
        self.QSpacing = QSpacing

        super().__init__(MainGI)
        self.filename = ""
        self.folder = ""
        self.UpdateRequestsQu = qu.Queue()
        self.Updates = qu.Queue()
        self.MainGI = MainGI
        self.Configuration = MainGI.Configuration
        self.__width = width
        self.__height = height
        self.icon = icon
        self.FigCancas = None
        self.Fig = None
        
        self.columns = 9
        self.rows = 20

        self.RowHeight = int(self.__height/self.rows)
        self.ColumnWidth = int(self.__width/self.columns)
        self.figData = []

        self.GraphProp = dict()

        self.GraphProp['lineStyle'] = "o"
        self.GraphProp['lineSize'] = 1
        self.GraphProp['lineColor'] = 'blue'
        self.GraphProp['xLabel'] = "Voltage (V)"
        self.GraphProp['yLabel'] = "Current (A)"
        self.GraphProp['cLabel'] = "Resistance ($\Omega$)"
        self.GraphProp['legend'] = None
        self.GraphProp['title'] = ""
        self.GraphProp['x'] = True
        self.GraphProp['map'] = False
        self.GraphProp['xScale'] = 'lin'
        self.GraphProp['yScale'] = 'lin'
        self.GraphProp['valueName'] = 'IV-Curve'

        self.setWindowTitle(title)

        try: 
            self.setWindowIcon(self.icon)
        except:
            self.MainGI.writeError("Icon not found in window %s" %(title))
        
        self._main = stdObj.stdFrameGrid(self, self.MainGI, self.columns, self.rows, self.__width, self.__height)
        self._main.setFont(self.QFont)
        self._main.setContentsMargins(*self.QMargin)
        self.resize(int(self.__width), int(self.__height))
        self.layout = self._main.layout
        self.Menus = []
        self.IntWid = []

        self.IntWid.append(ComboBox(self._main, self.layout, "DieX", row=2, column=1, columnspan=1))
        
        self.IntWid.append(ComboBox(self._main, self.layout, "DieY", row=2, column=2, columnspan=1))
        
        self.IntWid.append(ComboBox(self._main, self.layout, "DevX", row=2, column=3, columnspan=1))
        
        self.IntWid.append(ComboBox(self._main, self.layout, "DevY", row=2, column=4, columnspan=1))
        
        self.IntWid.append(ComboBox(self._main, self.layout, "Meas", row=2, column=5, columnspan=2))
        
        self.IntWid.append(ComboBox(self._main, self.layout, "Val", row=2, column=7, columnspan=2))
        
        self.IntWid.append(ComboBox(self._main, self.layout, "Num", default='Live', items=['Live'], row=2, column=9, columnspan=1))
        
        self.TxTab7DieX=Label(self._main, "Die X",self.layout, row=1, column=1, columnspan=1)
        
        self.TxTab7DieY=Label(self._main, "Die Y",self.layout, row=1, column=2, columnspan=1)
        
        self.TxTab7DevX=Label(self._main, "Device X",self.layout, row=1, column=3, columnspan=1)

        self.TxTab7DevY=Label(self._main, "Device Y",self.layout, row=1, column=4, columnspan=1)
        
        self.TxTab7Meas=Label(self._main, "Measurement",self.layout, row=1, column=5, columnspan=2)
        
        self.TxTab7Val=Label(self._main, "Value", self.layout, row=1, column=7, columnspan=2)

        self.TxTab7Num=Label(self._main, "Number", self.layout, row=1, column=9, columnspan=1)

        self.SaveBut = QtWidgets.QPushButton("Save Plot", self._main)
        self.SaveBut.clicked.connect(self.SaveFigure)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.layout.addWidget(self.SaveBut, 20, 8, 1, 2)

        self.TxLineStyle=Label(self._main, "Style", self.layout, row=20, column=2, columnspan=1)
        self.LineStyle = ComboBox(self._main, self.layout, "lineStyle", row=20, column=3, default=self.GraphProp['lineStyle'], items=self.styles, columnspan=1, command=self.updateLineStyle)
        
        self.TxLineSize=Label(self._main, "Size",self.layout, row=20, column=4, columnspan=1)
        self.LineSize = ComboBox(self._main, self.layout, "lineSize", row=20, column=4, default=self.GraphProp['lineSize'], items=(self.sizes), columnspan=1, command=self.updateLineSize)
        
        self.TxColorStart=Label(self._main, "Color", self.layout, row=20, column=6, columnspan=1)
        self.ColorStart = ComboBox(self._main, self.layout, "lineColor", row=20, column=5, default=self.GraphProp['lineColor'], items=(self.colors), columnspan=2, command=self.updateLineColor)
        
        self.ClearBut = PushButton(self._main, "Clear Results", "clear", self.layout, row=20, column=1, columnspan=2, command=self.clearResults)

        self.CreateCanvas()
        self.setFixedSize(self.size())


    def savePosition(self):
        self.Configuration.setValue("ResultWindowX", self.pos().x())
        self.Configuration.setValue("ResultWindowY", self.pos().y())
        self.Configuration.setValue("ResultWindowMon", QtWidgets.QDesktopWidget().screenNumber(self))

    def SaveFigure(self):

        Folder = self.MainGI.eChar.getFolder()
        Folder = "%s/Plots" %(Folder)

        if Folder.strip() == "" or Folder == None:
            self.ErrorQu.put("ResultWindow - Save Figure: No Folder is defined!")
            return None
        
        if self.filename != "":
            self.XYGraph.SaveToFile(self.filename, Folder)

    def closeEvent(self, event):
        self.hide()

    def clearResults(self):
        self.figData = [1]
        self.updateCanvas()


    def update(self):
        
        graphUpdate = False

        while not self.Updates.empty():

            entry = self.Updates.get()
            #tm.sleep(1)
            for key, item in entry.items():

                for widget in self.IntWid:

                    name = widget.getName()
                    if key == name:
                        widget.update(item)

                    if key == "%sChn" %(name):
                        widget.change(item)
                
                if key == "Figure":
                    
                    for gkey, gitem in item.items():

                        self.GraphProp[gkey] = gitem

                    graphUpdate = True

                if key =="fileName":
                    self.filename = item
                
                if key =="folder":
                    self.folder = item

                if key == "Data":
                    self.figData = item
                    graphUpdate = True

                if key == "Show":
                    self.show()
        
        if graphUpdate:
            self.updateCanvas()

    def checkIfinList(self, item, lis):
        if item in lis:
            return item
        else:
            return ""

    def getKeyFromVal(self, value, dictinary):
        for key, val in dictinary.items():
            if value == val:
                return key

    def CreateCanvas(self, row=3, column=1, rowspan=17, columnspan=10):

        height = int(rowspan*self.RowHeight)
        width = int(columnspan*self.ColumnWidth)
        
        self.figData = [1,1,1,1,1,1,1,1,1,1]
    
        self.XYGraph = PR.XY(self.MainGI.getConfiguration().getMainFolder(), self.figData, self.GraphProp, height=height, width=width)

        figure = self.XYGraph.getFigure()
        
        self.__Canvas_1 = FigureCanvasQTAgg(figure)
        self.__Canvas_1.setParent(self._main)
        self.__Canvas_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.__Canvas_1.updateGeometry()
        self.__Canvas_1.draw() 

        self.layout.addWidget(self.__Canvas_1, row, column, rowspan, columnspan)

    def updateLineSize(self, value):
        self.GraphProp['lineSize'] = value
        self.updateCanvas()

    def updateLineStyle(self, value):
        self.GraphProp['lineStyle'] = value
        self.updateCanvas()
        
    def updateLineColor(self, value):
        self.GraphProp['lineColor'] = value
        self.updateCanvas()

    def updateCanvas(self):
        try: 
            self.XYGraph.updateWithResult(self.figData, self.GraphProp)
            self.__Canvas_1.draw()
        except ValueError as e:
            self.ErrorQu.put("Error while updating Graph: %s" %(e))

    def updateOptionMenu(self, menu, variable, newChoices):
        if len(newChoices) == 0:
            newChoices.append("")
        menu.deleteOptions()
        for choice in newChoices:
            menu.addOption(choice, variable)
    
    def on_closing(self):
        self.destroy()
        self.ResultHandling.clear()
        self.ResultHandling.CloseWindow()


class ComboBox(QtWidgets.QComboBox):

    def __init__(self, parent, layout, name, row, column, rowspan=1, columnspan=1, alignment=None, default="", items=[""], **kwargs):

        super().__init__(parent)
        self.addItems([str(i) for i in items])

        index = self.findText(str(default))

        self.setCurrentIndex(index)
        self.name = name
        self.prevText = self.currentText()
        self.update(items)
        self.layout = layout
        self.row = row
        self.column = column
        self.rowspan = rowspan
        self.columnspan = columnspan
        self.MainGI = parent.MainGI
        if alignment == None:
            self.layout.addWidget(self, row, column, rowspan, columnspan)
        else:
            self.layout.addWidget(self, row, column, rowspan, columnspan, alignment)
        self.queue = parent.parentWidget().UpdateRequestsQu

        self.Blocked = False
        self.command = None
        if "command" in kwargs:
            self.command = kwargs['command']
        
        self.activated.connect(self.callFunc)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    def getName(self):
        return self.name

    def update(self, items):

        self.prevText = self.currentText()
        self.clear()
        if items != None:
            self.addItems([str(i) for i in items])
            index = self.findText(str(self.prevText))
            if index == -1: 
                index = 0
            self.setCurrentIndex(index)

    def change(self, item):
        index = self.findText(str(item))
        if index != -1:
            self.setCurrentIndex(index)
                
    def callFunc(self):
    
        self.queue.put({self.name: self.currentText()})

        if self.command != None:
            self.command(self.currentText())

class Label(QtWidgets.QLabel):

    def __init__(self, parent, text, layout, row, column, rowspan=1, columnspan=1, alignment=None, **kwargs):

        super().__init__(text, parent)

        self.row = row
        self.column = column
        self.rowspan = rowspan
        self.columnspan = columnspan
        self.layout = layout
        if alignment == None:
            self.layout.addWidget(self, row, column, rowspan, columnspan)
        else:
            self.layout.addWidget(self, row, column, rowspan, columnspan, alignment)

class PushButton(QtWidgets.QPushButton):

    def __init__(self, parent, text, name, layout, row, column, rowspan=1, columnspan=1, alignment=None, **kwargs):
         
        super().__init__(text, parent)

        self.name = name
        self.layout = layout
        self.row = row
        self.column = column
        self.rowspan = rowspan
        self.columnspan = columnspan
        self.MainGI = parent.MainGI
        if alignment == None:
            self.layout.addWidget(self, row, column, rowspan, columnspan)
        else:
            self.layout.addWidget(self, row, column, rowspan, columnspan, alignment)
        self.queue = parent.parentWidget().UpdateRequestsQu

        self.command = None
        if "command" in kwargs:
            self.command = kwargs['command']
        
        self.clicked.connect(self.callFunc)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    
    def getName(self):
        return self.name

    def callFunc(self):
        
        self.queue.put({self.name: True})

        if self.command != None:
            self.command()