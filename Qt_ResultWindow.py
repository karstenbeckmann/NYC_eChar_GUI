
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
from PyQt5 import QtWidgets, QtCore, QtGui
import Qt_stdObjects as stdObj
import darkdetect
import numpy as np
import pyqtgraph as pg
import datetime as dt
import pyqtgraph.exporters
from matplotlib import cm
import matplotlib as mpl
import copy as cp

class ResultWindow(QtWidgets.QMainWindow):
    
    ErrorQu = qu.Queue()

    def __init__(self, MainGI, QFont=None, QMargin=None, QSpacing=None, width=600, height=400, icon=None, title="Results"):
        
        self.QFont= QFont
        self.QMargin = QMargin
        self.QSpacing = QSpacing
        self.darkMode = darkdetect.isDark()

        super().__init__(MainGI)
        self.filename = ""
        self.folder = ""
        self.UpdateRequestsQu = qu.Queue()
        self.updates = qu.Queue()
        self.MainGI = MainGI
        self.Configuration = MainGI.Configuration
        self.__width = width
        self.__height = height
        self.icon = icon

        self.rows = 19
        self.columns = 8

        self.frameHeight = int(self.__height)-self.QMargin.top()-self.QMargin.bottom()-15
        self.frameWidth = int(self.__width)-self.QMargin.left()-self.QMargin.right()

        self.RowHeight = int(self.frameHeight/self.rows)
        self.ColumnWidth = int(self.frameWidth/self.columns)
        self.figData = []

        self.setWindowTitle(title)

        try: 
            self.setWindowIcon(self.icon)
        except:
            self.MainGI.writeError("Icon not found in window %s" %(title))
        
        self._main = stdObj.stdFrameGrid(self, self.MainGI, self.columns, self.rows, self.frameWidth, self.frameHeight,fixSize=False)
        self._main.layout.setRowMinimumHeight(0, int(self.RowHeight))
        self._main.layout.setRowStretch(0, 0)
        self._main.layout.setRowMinimumHeight(2, int(self.RowHeight))
        self._main.layout.setRowStretch(1, 0)
        self._main.layout.setRowMinimumHeight(18, int(self.RowHeight))
        self._main.layout.setRowStretch(18, 0)
        self._main.layout.setRowMinimumHeight(19, int(self.RowHeight))
        self._main.layout.setRowStretch(19, 0)
        for n in range(self.rows-4):
            self._main.layout.setRowStretch(n+2, 1)
        for n in range(self.columns-1):
            self._main.layout.setColumnMinimumWidth(n, int(self.ColumnWidth))
            self._main.layout.setColumnStretch(n, 1)

        #self._main.setFont(self.QFont)
        self.resize(int(self.__width), int(self.__height))
        #self._main.setContentsMargins(self.QMargin)
        #self._main.resize(int(self.__width), int(self.__height))
        self._main.resize(self.frameWidth, self.frameWidth)
        self._main.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.layout = self._main.layout

        cols = 8
        rows = 2
        frWidth = int(self.ColumnWidth*(4.5))
        frHeight = self.RowHeight*2
        self.comboBoxFrame = stdObj.stdFrameGrid(self._main, self.MainGI, cols, rows, frWidth, frHeight, cell=False, fixSize=False)
        self.comboBoxFrame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.comboBoxFrame.setLineWidth(2)
        self.comboBoxFrame.setMidLineWidth(2)
        self.comboBoxFrame.setFrameStyle(2)
        self.comboBoxFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.layout.addWidget(self.comboBoxFrame, 0, 0, 2, 5)
        self.layoutComboBox = self.comboBoxFrame.layout
        

        self.Menus = []
        self.IntWid = []

        self.IntWid.append(ComboBox(self._main, self.layoutComboBox, "DieX", row=1, column=0, columnspan=1))
        
        self.IntWid.append(ComboBox(self._main, self.layoutComboBox, "DieY", row=1, column=1, columnspan=1))
        
        self.IntWid.append(ComboBox(self._main, self.layoutComboBox, "DevX", row=1, column=2, columnspan=1))
        
        self.IntWid.append(ComboBox(self._main, self.layoutComboBox, "DevY", row=1, column=3, columnspan=1))
        
        self.IntWid.append(ComboBox(self._main, self.layoutComboBox, "Meas", row=1, column=4, columnspan=2))
        self.IntWid[-1].view().setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        self.IntWid.append(ComboBox(self._main, self.layoutComboBox, "Val", row=1, column=6, columnspan=2))
        self.IntWid[-1].view().setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        
        self.TxTab7DieX=Label(self._main, "Die X",self.layoutComboBox, row=0, column=0, columnspan=1)
        
        self.TxTab7DieY=Label(self._main, "Die Y",self.layoutComboBox, row=0, column=1, columnspan=1)
        
        self.TxTab7DevX=Label(self._main, "Device X",self.layoutComboBox, row=0, column=2, columnspan=1)

        self.TxTab7DevY=Label(self._main, "Device Y",self.layoutComboBox, row=0, column=3, columnspan=1)
        
        self.TxTab7Meas=Label(self._main, "Measurement",self.layoutComboBox, row=0, column=4, columnspan=2)
        
        self.TxTab7Val=Label(self._main, "Value", self.layoutComboBox, row=0, column=6, columnspan=2)

        cols = 3
        rows = 2
        frWidth = self.ColumnWidth*3-3
        frHeight = self.RowHeight*2
        self.comboBoxFrame2 = stdObj.stdFrameGrid(self._main, self.MainGI, cols, rows, frWidth, frHeight, cell=False, fixSize=False)
        self.comboBoxFrame2.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.comboBoxFrame2.setLineWidth(2)
        self.comboBoxFrame2.setMidLineWidth(2)
        self.comboBoxFrame2.setFrameStyle(2)
        self.comboBoxFrame2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.layout.addWidget(self.comboBoxFrame2, 0, 5, 2, 4)
        self.layoutComboBox2 = self.comboBoxFrame2.layout
        
        self.IntWid.append(ComboBox(self._main, self.layoutComboBox2, "Num", default='Live', items=['', 'Live'], row=1, column=0, columnspan=3))
        self.IntWid[-1].view().setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.TxTab7Num=Label(self.comboBoxFrame2, "Predefined Graphs", self.layoutComboBox2, row=0, column=0, columnspan=3)

        self.SaveBut = QtWidgets.QPushButton("Save\nPlot", self._main)
        self.SaveBut.clicked.connect(self.SaveFigure)
        self.SaveBut.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.layout.addWidget(self.SaveBut, 18, 8, 2, 1)


        self.ResultPlot = PlotWidget(self._main, self.MainGI, name="ResultPlotWidget", background=self.MainGI.getBackgroundColor(True), labelColor=self.MainGI.getLabelColor(True), title="Result Plotting")
        self.ResultPlot.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        row=2
        column=0
        rowspan=16
        columnspan=9
        self.layout.addWidget(self.ResultPlot, row, column, rowspan,  columnspan)
        graphProp=self.ResultPlot.getStdGraphProperties()
        
        self.TxRow=Label(self._main, "Row", self.layout, row=18, column=2, columnspan=1, alignment=QtCore.Qt.AlignRight)
        self.Row = stdObj.Entry(self, MainGI, "ResultRow", validate='all', validateNumbers="-1|[0-9]+", type=int, default=-1, command=self.updateGraph, sizePolicy=(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.SaveBut.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.layout.addWidget(self.Row, 18, 3, 1, 1)
        
        self.TxColumn=Label(self._main, "Column", self.layout, row=18, column=4, columnspan=1, alignment=QtCore.Qt.AlignRight)
        self.Column = stdObj.Entry(self, MainGI, "ResultColumn", validate='all', validateNumbers="-1|[0-9]+", type=int, default=-1, command=self.updateGraph, sizePolicy=(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.layout.addWidget(self.Column, 18, 5, 1, 1)
        
        self.TxStyle=Label(self._main, "Style", self.layout, row=19, column=2, columnspan=1, alignment=QtCore.Qt.AlignRight)
        self.Style = ComboBox(self._main, self.layout, "Style", row=19, column=3, default=graphProp['Style'], items=self.ResultPlot.getStyleOptions(), columnspan=1, command=self.updateStyle)
        
        self.TxLineStyle=Label(self._main, "Line", self.layout, row=19, column=4, columnspan=1, alignment=QtCore.Qt.AlignRight)
        self.LineStyle = ComboBox(self._main, self.layout, "lineStyle", row=19, column=5, default=graphProp['LineStyle'], items=self.ResultPlot.getLineStyleOptions(), columnspan=1, command=self.updateLineStyle)
        
        self.TxScatterStyle=Label(self._main, "Symbol", self.layout, row=19, column=4, columnspan=1, alignment=QtCore.Qt.AlignRight)
        self.ScatterStyle = ComboBox(self._main, self.layout, "scatterStyle", row=19, column=5, default=graphProp['ScatterStyle'], items=self.ResultPlot.getScatterStyleOptions(), columnspan=1, command=self.updateScatterStyle)
        
        self.TxLineWidth=Label(self._main, "Width",self.layout, row=19, column=6, columnspan=1, alignment=QtCore.Qt.AlignRight)
        self.LineWidth = ComboBox(self._main, self.layout, "lineWidth", row=19, column=7, default=graphProp['LineWidth'], items=self.ResultPlot.getLineWidthOptions(), columnspan=1, command=self.updateLineWidth)
        
        self.TxScatterSize=Label(self._main, "Size",self.layout, row=19, column=6, columnspan=1, alignment=QtCore.Qt.AlignRight)
        self.ScatterSize = ComboBox(self._main, self.layout, "scatterSize", row=19, column=7, default=graphProp['ScatterSize'], items=self.ResultPlot.getScatterSizeOptions(), columnspan=1, command=self.updateScatterSize)

        self.TxLabelSize=Label(self._main, "Label Size", self.layout, row=19, column=0, columnspan=1, alignment=QtCore.Qt.AlignRight)
        self.LabelSize = ComboBox(self._main, self.layout, "labelSize", row=19, column=1, default=self.ResultPlot.getLabelSizeOptions()[0], items=self.ResultPlot.getLabelSizeOptions(), columnspan=1, command=self.updateLabelSize)

        #self.TxAppendGraph=Label(self._main, "Append Pl.", self.layout, row=18, column=6, columnspan=1, alignment=QtCore.Qt.AlignRight)
        #self.AppendGraph = CheckBox(self._main, self.layout, "appendGraph", row=18, column=7, columnspan=1, command=self.appendGraph)
        
        #self.AppendGraph = PushButton(self._main, "Append Graph", "appendGraph", row=18, column=6, columnspan=1, command=self.appendGraph)
        self.AddGraph = PushButton(self._main, "Add Graph", "addGraph", self.layout,  row=18, column=6, columnspan=1)

        self.ClearBut = PushButton(self._main, "Clear Results", "clear", self.layout, row=18, column=0, columnspan=2, command=self.clearResults)
        self.updateStyle(graphProp['Style'])

        self.setMinimumSize(self.size())
        self.updateGraph()

    def eventFilter(self, event):
        if (event.type() == QtCore.QEvent.Resize):
            self.ResizeSignal.emit(1)
        return True

    def resizeEvent(self, event):

        self.__width = self.frameGeometry().width()
        self.__height = self.frameGeometry().height()

        self.RowHeight = int(self.__height/self.rows)
        self.ColumnWidth = int(self.__width/self.columns)

        for n in range(self.columns-1):
            self._main.layout.setColumnMinimumWidth(n, int(self.ColumnWidth))

        self.frameHeight = int(self.__height)-self.QMargin.top()-self.QMargin.bottom()-15
        self.frameWidth = int(self.__width)-self.QMargin.left()-self.QMargin.right()

        self._main.resize(self.frameWidth, self.frameHeight)

        return super().resizeEvent(event)

    def updateGraph(self):
        row = self.getCurrentRow()
        col = self.getCurrentCol()

        gp = self.ResultPlot.getGraphProperties(row, col)

        if gp != None:
            style = gp['Style']
            self.Style.change(style)
            self.__updateStyle(style)
            if style.lower() == "line":
                self.LineWidth.change(gp['LineWidth'])
                self.LineStyle.change(gp['LineStyle'])
            else:
                self.ScatterSize.change(gp['ScatterSize'])
                self.ScatterStyle.change(gp['ScatterStyle'])
        
    def getCurrentRow(self):
        return self.Row.getVariable()
    
    def getCurrentCol(self):
        return self.Column.getVariable()

    def updateLabelSize(self, value):
        row = self.getCurrentRow()
        col = self.getCurrentCol()
        self.ResultPlot.updateLabelSize(value, row, col)

    def updateLineWidth(self, value):
        row = self.getCurrentRow()
        col = self.getCurrentCol()
        self.ResultPlot.updateLineWidth(value, row, col)

    def updateScatterSize(self, value):
        row = self.getCurrentRow()
        col = self.getCurrentCol()
        self.ResultPlot.updateScatterSize(value, row, col)

    def updateLineStyle(self, value):
        row = self.getCurrentRow()
        col = self.getCurrentCol()
        self.ResultPlot.updateLineStyle(value, row, col)

    def updateScatterStyle(self, value):
        row = self.getCurrentRow()
        col = self.getCurrentCol()
        self.ResultPlot.updateScatterStyle(value, row, col)

    def __updateStyle(self, value):
        if value.lower() == "scatter":
            self.TxLineStyle.hide()
            self.LineStyle.hide()
            self.TxLineWidth.hide()
            self.LineWidth.hide()
            self.TxScatterStyle.show()
            self.ScatterStyle.show()
            self.TxScatterSize.show()
            self.ScatterSize.show()
        else: 
            self.TxLineStyle.show()
            self.LineStyle.show()
            self.TxLineWidth.show()
            self.LineWidth.show()
            self.TxScatterStyle.hide()
            self.ScatterStyle.hide()
            self.TxScatterSize.hide()
            self.ScatterSize.hide()


    def updateStyle(self, value):
        self.__updateStyle(value)
        row = self.getCurrentRow()
        col = self.getCurrentCol()
        self.ResultPlot.updateStyle(value, row, col)
        gp = self.ResultPlot.getGraphProperties(row, col)
        if gp != None:
            if value.lower() == ["line"]:
                self.LineWidth.change(gp['LineWidth'])
                self.LineStyle.change(gp['LineStyle'])
            else:
                self.ScatterSize.change(gp['ScatterSize'])
                self.ScatterStyle.change(gp['ScatterStyle'])
       

    def savePosition(self):
        self.Configuration.setValue("ResultWindowX", self.pos().x())
        self.Configuration.setValue("ResultWindowY", self.pos().y())
        self.Configuration.setValue("ResultWindowMon", QtWidgets.QDesktopWidget().screenNumber(self))

    def SaveFigure(self):
        folder = self.MainGI.eChar.getFolder()
        folder = os.path.join(folder, "Plots")

        if folder.strip() == "" or folder == None:
            self.ErrorQu.put("ResultWindow - Save Figure: No Folder is defined!")
            return None
        

        self.ResultPlot.SaveToFile(folder)
    
    
    def closeEvent(self, event):
        self.hide()

    def clearResults(self):
        self.ResultPlot.clear()

    def update(self, **kwargs):
        
        graphUpdate = False
        dataUpdate = False
        appendGraph = False
        addFigData = []
        addGraph = False
        graphProp = []
        data = []
        
        if "BackgroundColor" in kwargs:
            self.ResultPlot.updateBackground(kwargs["BackgroundColor"])
            
        if "LabelColor" in kwargs:
            self.ResultPlot.updateLabelColor(kwargs["LabelColor"])

        row = -1
        column = -1

        graphUpdate = False
        dataUpdate = False
        appendGraph = False
        addFigData = []
        addGraph = False
        graphProp = []
        data = []
        
        while not self.updates.empty():

            entry = self.updates.get()
            for key, value in entry.items():
                for widget in self.IntWid:
                    name = widget.getName()
                    if key == name:
                        widget.update(value)
                    if key == "%sChn" %(name):
                        widget.change(value)
                
                if key == "Default":
                    for defKey, defValue in value.items():
                        for widget in self.IntWid:
                            name = widget.getName()
                            if defKey == name:
                                widget.change(defValue)
                                break

                if key == "AppendGraph":
                    appendGraph = True
                    appendFigData = value
                    
                if key == "AddGraph":
                    addGraph = True
                    addFigData = value

                if key == "GraphData":
                    for gkey, gvalue in value.items():
                        if gkey =="GraphProp":
                            graphProp = gvalue
                            
                        if gkey =="Data":
                            data = gvalue

                        if gkey =="Filename":
                            self.filename = gvalue
                        
                        if gkey =="Folder":
                            self.folder = gvalue
                        
                    graphUpdate = True

                if key == "Data":
                    data = value
                    dataUpdate = True

                if key == "Show":
                    self.show()

        if self.darkMode != darkdetect.isDark():
            self.darkMode = darkdetect.isDark()
            graphUpdate = True
        
        if appendGraph:
            self.ResultPlot.appendGraph(appendFigData)

        if addGraph:
            self.ResultPlot.addGraph(addFigData, self.Row.getVariable(), self.Column.getVariable())
            
            cbox = self.getComboBox("Num")
            if cbox != None:
                cbox.change("")

        if graphUpdate:
            self.ResultPlot.updateGraphs(data, graphProp)

    def checkIfinList(self, item, lis):
        if item in lis:
            return item
        else:
            return ""

    def getKeyFromVal(self, value, dictinary):
        for key, val in dictinary.items():
            if value == val:
                return key

    def getComboBox(self, name):
        for w in self.IntWid:
            if w.name == name:
                return w

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


class CheckBox(QtWidgets.QCheckBox):

    def __init__(self, parent, layout, name, row, column, rowspan=1, columnspan=1, alignment=None, default=False, **kwargs):

        super().__init__(parent)

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

        self.Blocked = False
        self.command = None
        if "command" in kwargs:
            self.command = kwargs['command']
        
        self.stateChanged.connect(self.callFunc)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    def getName(self):
        return self.name

    def change(self, item):
        if isinstance(item, str):
            if item.lower() == "true":
                item == True
            else:
                item == False
        elif isinstance(item, (int, float)):
            if item >=1:
                item = True
        elif not isinstance(item, bool):
            return False

        self.setCheckState(item)
                
    def callFunc(self):
        self.queue.put({self.name: self.checkState()})

        if self.command != None:
            self.command(self.checkState())
            
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
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        

        self.Blocked = False
        self.command = None
        if "command" in kwargs:
            self.command = kwargs['command']
        
        self.activated.connect(self.callFunc)
            

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
            
class PlotWidget(pg.GraphicsLayoutWidget):

    xticks = []
    yticks = []

    xlow = 0
    ylow = 0

    xhigh = 0
    yhigh = 0

    xcenter = 0
    ycenter = 0

    Type = 'WafProgress'
    initValue = None
    title = None
    
    data = np.array([[]])
    
    ticks = 15

    def __init__(self, parent=None, mainGI=None, background='default', labelColor="k", name=None, labels=None, title="", initValue=0, ValueName="", **kwargs):

        super().__init__(parent, *kwargs)

        self.setWindowTitle(title)
        
        self.MainGI = mainGI
        self.config = self.MainGI.getConfiguration()
        self.mainFolder = self.config.getMainFolder()
        self.backgroundColor = background
        self.labelColor = labelColor
        self.title = title
        self.appendGraph = False

        self.setBackground(self.backgroundColor)
        
        pg.setConfigOption('background', self.backgroundColor)
        pg.setConfigOption('foreground', self.labelColor)

        self.graphDefinitions()

        # first dimension is row, second dimension is column
        self.figData = []  
        standardGraphProp = cp.deepcopy(self.standardGraphProp)
        standardGraphProp["X"] = False
        standardGraphProp["Map"] = False
        standardGraphProp["Yscale"] = "lin"
        standardGraphProp["Xscale"] = "lin"
        standardGraphProp["LabelSize"] = 10
        #self.updatePlotItems([[0,1,2,3,4,5,6,7,8,9],[1,10,100,1000,10000,100000,1000000,10000000,100000000,1000000000]], Row=0, Column=0, graphProp=standardGraphProp)
        #self.updatePlotItems([[0,1,2,3,4,5,6,7,8,9],[1,10,100,1000,10000,100000,1000000,10000000,100000000,1000000000]], Row=1, Column=1, graphProp=standardGraphProp)
        #self.updatePlotItems([[0,1,2,3,4,5,6,7,8,9],[1,10,100,1000,10000,100000,1000000,10000000,100000000,1000000000]], Row=2, Column=2, graphProp=standardGraphProp)
        #self.updatePlotItems([[0,1,2,3,4,5,6,7,8,9],[1,10,100,1000,10000,100000,1000000,10000000,100000000,1000000000]], Row=3, Column=3, graphProp=standardGraphProp)
        
        #self.updatePlotItems([[0,1,2],[1,2,3],[1000,3,250]], graphProp=graphProp)
        

    def axisPrep(self, plotItem, figIndex):
        graphProp = self.figData[figIndex]['GraphProp']
        labelStyle = {'font-weight': 'bold', 'color': self.labelColor}


        if 'LabelSize' in graphProp.keys():
            labelStyle['font-size'] = "%spt" %(graphProp["LabelSize"])

        if 'Title' in graphProp.keys():
            plotItem.setTitle(title=graphProp['Title']['PlotTitle'], **labelStyle)

        if 'Ylabel' in graphProp.keys():
            ylabel = graphProp['Ylabel']
            yunit = []
            yLabelStyle = cp.deepcopy(labelStyle)
            if 'Yunit' in graphProp.keys():
                yunit.append(graphProp['Yunit'])
            else:
                if ylabel.find("(") != -1: 
                    yunit.append(ylabel.split("(")[1].split(")")[0])
                    ylabel = ylabel.split("(")[0].strip()
                elif ylabel.find("[") != -1:
                    yunit.append(ylabel.split("[")[1].split("]")[0])
                    ylabel = ylabel.split("(")[0].strip()
            plotItem.setLabel('left', ylabel, *yunit, **yLabelStyle) 
        if 'Xlabel' in graphProp.keys():
            xlabel = graphProp['Xlabel']
            xLabelStyle = cp.deepcopy(labelStyle)
            xunit = []
            if 'Xunit' in graphProp.keys():
                xunit.append(graphProp['Xunit'])
            else:
                if xlabel.find("(") != -1: 
                    xunit.append(xlabel.split("(")[1].split(")")[0])
                    xlabel = xlabel.split("(")[0].strip()
                elif xlabel.find("[") != -1:
                    xunit.append(xlabel.split("[")[1].split("]")[0])
                    xlabel = xlabel.split("(")[0].strip()
            plotItem.setLabel('bottom', xlabel, *xunit, **xLabelStyle)

        plotItem.showAxis("top", False)
        plotItem.showAxis("left")
        plotItem.showAxis("bottom")
        plotItem.showAxis("right", False)

        leftAxis = plotItem.getAxis("left")
        leftAxis.setTextPen(self.labelColor)
        botAxis = plotItem.getAxis("bottom")
        botAxis.setTextPen(self.labelColor)

    def updatePlotProperties(self, GraphProp={}, row=0, column=0, **kwargs):

        plotItem = self.getItem(row,column)
        
        if plotItem == None:
            return False
        
        self.removeItem(plotItem)

        for n,d in enumerate(self.figData):
            if d["GraphProp"]['Row'] == row and d["GraphProp"]['Column'] == column:
                break

        for key, value in GraphProp.items():
            self.figData[n]["GraphProp"][key] = value

        self.updatePlotItems(figIndex=n)

    
    def updatePlotPropertiesbyIndex(self, GraphProp={}, figIndex=0, **kwargs):

        try:
            figData = self.figData[figIndex]
        except ValueError:
            return False
        
        curGraphProp = figData['GraphProp']

        plotItem = self.getItem(curGraphProp['Row'],curGraphProp['Column'])
        self.removeItem(plotItem)

        for key, value in curGraphProp.items():
            figData["GraphProp"][key] = value

        self.updatePlotItems(figIndex=figIndex)

    
    def appendGraph(self, figData, graphData):
        pass

    def updatePlotItems(self, figIndex=0, **kwargs):
        
        try:
            figData = self.figData[figIndex]
            data = figData["Data"]
            graphProp = figData["GraphProp"]
        except ValueError:
            return False
                

        if not isinstance(graphProp['Map'], pg.ImageItem) and not graphProp['PlotType'] == 'Map':
            self.checkInputDimensions(graphProp, "LineStyle")
            self.checkInputDimensions(graphProp, "LineWidth")
            self.checkInputDimensions(graphProp, "ScatterStyle")
            self.checkInputDimensions(graphProp, "ScatterSize")
            self.checkInputDimensions(graphProp, "ColorTable")

        if graphProp['PlotType'] == "Map":
            graphProp['Map'] = pg.ImageItem()
        
        ## if no row/column are defined (automatically asign None) the plots will we appended if specified in the GUI
        clear = False
        if graphProp['Row'] == None and graphProp['Column'] == None:
            clear = True
                
        if graphProp['Row'] == -2 or graphProp['Column'] == -2:
            clear = True
        
        if graphProp['Row'] == None or graphProp['Row'] == -2:
            graphProp['Row'] = -1
        if graphProp['Column'] == None or graphProp['Column'] == -2:
            graphProp['Column'] = -1


        if graphProp['Row'] == -1 and graphProp['Column'] == -1:
            if clear:
                self.clear()
            plotItem = self.addPlot(rowspan=graphProp['Rowspan'], colspan=graphProp['Colspan'])
            graphProp['Row'], graphProp['Column'] = self.getRowColumn(plotItem)
        elif graphProp['Row'] == None:
            plotItem = self.addPlot(row=0, col=graphProp['Column'], rowspan=graphProp['Rowspan'], colspan=graphProp['Colspan'])
            graphProp['Row'] = 0
        elif graphProp['Column'] == None:
            plotItem = self.addPlot(row=graphProp['Row'], col=0, rowspan=graphProp['Rowspan'], colspan=graphProp['Colspan'])
            graphProp['Column'] = 0
        else:
            plotItem = self.addPlot(row=graphProp['Row'], col=graphProp['Column'], rowspan=graphProp['Rowspan'], colspan=graphProp['Colspan'])
        
        self.axisPrep(plotItem, figIndex)
        self.updatePlot(plotItem, figIndex)
    
    def addGraph(self, figData, row=None, column=None):
        for d in figData:
            graphProp = d['GraphProp']
            data = d['Data']
            
            graphProp['Row'] = -1
            graphProp['Column'] = -1
            if row != None:
                graphProp['Row'] = row
            if column != None:
                graphProp['Column'] = row

            self.figData.append({"Data": data, "GraphProp":graphProp})
            self.updatePlotItems(-1)

    def updateGraphs(self, data, graphProp):
        self.clear()
        self.figData = []
        
        if 'Title' in graphProp[0].keys():
            self.setWindowTitle(graphProp[0]['Title']['GraphTitle'])

        n = 0
        for d, i in zip(data, graphProp):
            self.figData.append({"Data": d, "GraphProp":i})
            self.updatePlotItems(n)
            n = n+1

    def getRowColumn(self, plotItem):
        for n in range(100):
            for m in range(100):
                if plotItem == self.getItem(n,m):
                    return (n, m)
        return (0,0)

    def clear(self):
        super().clear()
        self.figData = []

    def adjustInput(self, input, data, plotType):
        if not isinstance(input, list):
            if isinstance(data, (list, np.ndarray)):
                if plotType == "Y":
                    return [input]
                elif plotType == "XY":
                    if len(np.shape(data)) == 3:
                        return [input]*(len(data))
                    elif len(np.shape(data)) == 2:
                        return [input]*(len(data)-1)
                    else:
                        return [input]
                elif plotType == "YY":
                    return [input]*(len(data))
            else:
                return [input]
        else:
            return input
        
    def getRequiredLength(self, data, plotType):
        if not isinstance(input, list):
            if isinstance(data, (list, np.ndarray)):
                if plotType == "Y":
                    return 1
                elif plotType == "XY":
                    if len(np.shape(data)) == 3:
                        return len(data)
                    elif len(np.shape(data)) == 2:
                        return len(data)-1
                    else:
                        return 1
                elif plotType == "YY":
                    return len(data)
            else:
                return 1
        else:
            return 0

    def checkData(self, figData):
        data = figData['Data']
        figData['GraphProp']['PlotType']='Y'
        if not isinstance(data, (list, np.ndarray)):
            raise ValueError("Data must be a one or more dimensional list of int/float.")
        if not isinstance(data[0], (list, np.ndarray)):
            figData['GraphProp']['PlotType']='Y'
        else:
            if figData['GraphProp']["Map"]:
                figData['GraphProp']['PlotType'] = 'Map'
            else:
                if figData['GraphProp']['X']:
                    figData['GraphProp']['PlotType'] ='XY'
                else:
                    figData['GraphProp']['PlotType'] ='YY'
        return figData['GraphProp']['PlotType']

    def checkInputDimensions(self, graphProp, description):
        plotType = graphProp['PlotType']
        n = graphProp[description]
                
        if not isinstance(n, (int,float,str,type(None))):
            if isinstance(n, list):
                if plotType=='Y' and len(n) < 1:
                    raise TypeError("%s must be the same dimension as the data input")
                #if not len(list) == len(n):
                #    raise TypeError("%s must be the same dimension as the data input")
                for x in range(len(n)):
                    if not isinstance(x, (int,float,str)):
                        raise TypeError("%s inputs must be int,float or str.")
        
    def updatePlot(self, plotItem, figIndex):
        #plotItem.clear()
        lines = []
        graphProp = self.figData[figIndex]['GraphProp']
        data = self.figData[figIndex]['Data']
        plotType = graphProp["PlotType"]
        style = graphProp["Style"]
        linestyle = []
        for x in graphProp["LineStyle"]:
            try:
                linestyle.append(self.lineLookup[x])
            except KeyError:
                linestyle.append(list(self.lineLookup.values())[0])

        linewidth = graphProp["LineWidth"]
        scatterstyle = graphProp["ScatterStyle"]
        scattersize = graphProp["ScatterSize"]
        colorTable = graphProp["ColorTable"]

        
        if 'Legend' in graphProp.keys():
            pass

        xState = False
        if graphProp['Xscale'] == 'log':
            xState=True
            
        yState = False
        if graphProp['Yscale'] == 'log':
            yState=True

        mkPens = []
        mkBrush = []
        symbol = []

        scatter = False
        if plotType != "Map":
            if style.lower() == "line":
                for n in range(len(linestyle)):
                    pen = {}
                    if linestyle[n] != None:
                        pen['style'] =  linestyle[n]
                    if linewidth[n] != None:
                        pen['width'] = float(linewidth[n])
                    if colorTable[n] != None:
                        pen['color'] = colorTable[n]
                    mkPens.append(pg.mkPen(**pen))
            else:
                for n in range(len(scatterstyle)):
                    pen = {}
                    brush = ()
                    symbol.append({})
                    if scatterstyle[n] != None:
                        symbol[-1]['symbol'] = scatterstyle[n]
                    if scattersize[n] != None:
                        symbol[-1]['size'] = scattersize[n]
                    if colorTable[n] != None:
                        symbol[-1]['brush'] = pg.mkBrush(*colorTable[n])
                        pen['color'] = colorTable[n]
                    mkPens.append(pg.mkPen(**pen))
                scatter = True

            plotItem.setLogMode(xState, yState)
        
        lines.append([])
        if plotType == 'Y':
            lines.append(None)
            if yState:
                data1 = np.arange(1,len(data)+1,1)
                data2 = np.absolute(data)
                if scatter:
                    lines[0] = plotItem.addItem(pg.ScatterPlotItem(x=data1, y=data2, **symbol[0], pen=mkPens[0]))
                else:
                    lines[0] = plotItem.plot(x=data1, y=data2, pen=mkPens[0])

        elif plotType == 'XY':
            # data in 3D array 
            if len(np.shape(data)) == 3:
                for n in range(np.shape(data)[0]):
                    lines.append(None)
                    data1 = data[n][0]
                    if yState:
                        data1 = np.absolute(data[n][0])
                    data2 = data[n][1]
                    if xState:
                        data2 = np.absolute(data[n][1])
                    if scatter:
                        lines[n] = plotItem.addItem(pg.ScatterPlotItem(x=data1, y=data2, **symbol[n], pen=mkPens[n]))
                    else:
                        lines[n] = plotItem.plot(x=data1, y=data2, pen=mkPens[n])

                #if data[0][0][-1] < 0.1 and self.xscale=='lin':
                #    plotItem.ticklabel_format(style='sci', axis='x', scilimits=(-1,1))
           
            # data in 2D array
            else: 
                plotNum = np.shape(data)[0]-1 
                data1 = data[0]
                if xState:
                    data1 = np.absolute(data[0])
                for n in range(plotNum):
                    lines.append(None)
                    data2 = data[n+1]
                    if yState:
                        data2 = np.absolute(data[n+1])
                    if scatter:
                        lines[n] = plotItem.addItem(pg.ScatterPlotItem(x=data1, y=data2, **symbol[n], pen=mkPens[n]))
                    else:
                        lines[n] = plotItem.plot(x=data1, y=data2, pen=mkPens[n]) 

                #if data[0][-1] < 0.1 and self.xscale=='lin':
                #    plotItem.ticklabel_format(style='sci', axis='x', scilimits=(-1,1))

        elif plotType == 'YY':
            for n in range(len(data)):
                lines.append(None)
                data1 = np.arange(1,len(data[n])+1,1)
                data2 = np.absolute(data[n])
                if yState:
                    data1 = np.absolute(data[n])
                if scatter:
                    lines[n] = plotItem.addItem(pg.ScatterPlotItem(x=data1, y=data2, **symbol[n], pen=mkPens[n]))
                else:
                    lines[n] = plotItem.plot(x=data1, y=data2, pen=mkPens[n])
            
            try:
                size = len(data1)
            except:
                size = data1.size

            #if size > 99 and not xState:
            #    plotItem.ticklabel_format(style='sci', axis='x', scilimits=(-1,1))

        elif plotType == 'Map':

            kwargs = {}
            if "Clabel" in graphProp:
                kwargs["label"] = graphProp["Clabel"]

            data1 = std.equalizeArray(data)
            data1 = np.array(data1, np.longdouble)
                    
            maxValue = 0
            minValue = sys.float_info.max
            for ent in data: 
                if max(ent)>maxValue:
                    maxValue = max(ent)
                if max(ent)<minValue:
                    minValue = max(ent)
                    
            # Get the colormap
            maxValue = 255
            colormap = pg.colormap.getFromMatplotlib("viridis")  # cm.get_cmap("CMRmap")
            graphProp['Map'].setImage(data1)
            graphProp['Map'].setColorMap(colormap)
            tr = QtGui.QTransform()
            graphProp['Map'].setTransform(tr)
            graphProp['Map'].setBorder(1)
            plotItem.addColorBar( graphProp['Map'], colorMap=colormap, values=(minValue, maxValue), *kwargs)   
            plotItem.addItem(graphProp['Map'])

    def getFilename(self):
        if len(self.figData) == 0:
            return ""
        
        grProp = self.figData[0]["GraphProp"]
        
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H-%M-%S-%f")
        filename = "ResultWindow_%s_%s" %(filename, timestamp)
        filename = "%s_DieX%dY%d_DevX%dY%d_%s" %(filename, grProp['DieX'], grProp['DieY'], grProp['DevX'], grProp['DevY'], grProp['Measurement'])
        return filename

    def SaveToFile(self, folder):
        
        if len(self.figData) == 0:
            return None
        
        currentRowMax = 0
        currentColMax = 0
        
        filename = self.getFilename()
        

        while self.getItem(currentRowMax, 0) is not None:
            currentRowMax += 1
        
        while self.getItem(0, currentColMax) is not None:
            currentColMax += 1

        if not os.path.exists(folder):
            os.makedirs(folder)
        
        for n, m in zip(range(currentRowMax), range(currentColMax)):
            for f in self.figData:
                if f["GraphProp"]['Row'] == n and f["GraphProp"]['Column'] == m:
                    filename = "%s_%s" %(filename, f["GraphProp"]['ValueName'])
            item = self.getItem(n,m)
            exporter = pg.exporters.ImageExporter(item)
            filename = "%s_Row%d_Col%d.png" %(filename, n,m)
            path = os.path.join(folder, filename)
            exporter.export(path)

    def updateBackground(self, backgroundColor):
        self.backgroundColor = backgroundColor

        self.setBackground(self.backgroundColor)
        pg.setConfigOption('background', self.backgroundColor)

    def updateLabelColor(self, labelColor):
        self.labelColor = labelColor
        pg.setConfigOption('foreground', self.labelColor)

        currentRowMax = 0
        currentColMax = 0
        
        while self.getItem(currentRowMax, 0) is not None:
            currentRowMax += 1
        
        while self.getItem(0, currentColMax) is not None:
            currentColMax += 1


        for n, m in zip(range(currentRowMax), range(currentColMax)):
            item = self.getItem(n,m)

            axisNames = [ 'left', 'bottom', 'top', 'right']
            for a in axisNames:
                axis = item.getAxis(a)
                axis.setTextPen(self.labelColor)

    def getStdGraphProperties(self):
        return cp.deepcopy(self.standardGraphProp)
    
    def getGraphProperties(self, row, col):
        for d in self.figData:
            gp = d['GraphProp']
            if gp['Row'] == row and col == gp['Column']:
                return gp
        return None

    def updateScatterSize(self, value, row, col):
        try:
            value = int(value)
        except ValueError:
            return None
        
        if self.scatterSizeMin <= value and self.scatterSizeMax >= value:
            graphProp = {}
            graphProp['ScatterSize'] = value
            self.updatePlotProperties(graphProp, row, col)

    def updateLabelSize(self, value, row, col):
        value = float(value)
        if self.labelSizeMin <= value and self.labelSizeMax >= value:
            graphProp = {}
            graphProp['LabelSize'] = value
            self.updatePlotProperties(graphProp, row, col)

    def updateLineWidth(self, value, row, col):
        value = float(value)
        if self.lineWidthMin <= value and self.lineWidthMax >= value:
            graphProp = {}
            graphProp['LineWidth'] = value
            self.updatePlotProperties(graphProp, row, col)

    def updateScatterStyle(self, value, row, col):
        if value in self.scatterLookup:
            graphProp = {}
            graphProp['ScatterStyle'] = value
            self.updatePlotProperties(graphProp, row, col)

    def updateLineStyle(self, value, row, col):
        if value in list(self.lineLookup.keys()):
            graphProp = {}
            graphProp['LineStyle'] = value
            self.updatePlotProperties(graphProp, row, col)
            
    def updateStyle(self, value, row, col):
        if value in list(self.styleLookup):
            graphProp = {}
            graphProp['Style'] = value
            self.updatePlotProperties(graphProp, row, col)
            
    
    def _updateColorTable(self, name):
        cmapTemp = mpl.colormaps[name]
        cmap = []
        mult=255
        for c in cmapTemp.colors:
            cmap.append((int(mult*c[0]),int(mult*c[1]),int(mult*c[2])))
        return cmap

    def updateColorTable(self, name):
        cmap = self._updateColorTable(name)
        
        graphProp = {}
        graphProp['ColorTable'] = cmap
        self.updatePlotProperties(graphProp)


    def graphDefinitions(self):
        self.lineLookup = {}
        self.lineLookup["-"] = QtCore.Qt.SolidLine
        self.lineLookup["--"] = QtCore.Qt.DashLine
        self.lineLookup["."] = QtCore.Qt.DotLine
        self.lineLookup["-."] = QtCore.Qt.DashDotLine
        self.lineLookup["-.."] = QtCore.Qt.DashDotDotLine

        self.scatterLookup = ["o", "s", "t", "d", "+", "t1", "t2", "t3", "p", "h", "star", "x", "arrow_up", "arrow_right", "arrow_down", "arrow_left", "crosshair"]
        
        self.styleLookup = ['Line', "Scatter"]

        self.labelSizeMin = 5
        self.labelSizeStep = 1
        self.labelSizeMax = 25

        self.labelSizeLookup = list(np.arange(self.labelSizeMin,self.labelSizeMax+self.labelSizeMin, self.labelSizeStep))
        self.labelSizeLookup = [x for x in self.labelSizeLookup]

        self.lineWidthMin = 0.5
        self.lineWidthStep = 0.5
        self.lineWidthMax = 5
        self.lineWidthLookup = list(np.arange(self.lineWidthMin,self.lineWidthMax+self.lineWidthMin, self.lineWidthStep))
        self.lineWidthLookup = [x for x in self.lineWidthLookup]
        
        self.scatterSizeMin = 1
        self.scatterSizeStep = 1
        self.scatterSizeMax = 12
        self.scatterSizeLookup = list(np.arange(self.scatterSizeMin,self.scatterSizeMax+self.scatterSizeMin, self.scatterSizeStep))
        self.scatterSizeLookup = [x for x in self.scatterSizeLookup]

        colorMapName = "tab10"
        
        self.standardGraphProp = {}
        self.standardGraphProp['ColorTable'] = self._updateColorTable(colorMapName)
        self.standardGraphProp['Xlabel'] = "A.U."
        self.standardGraphProp['Ylabel'] = "A.U."
        #self.standardGraphProp['Clabel'] = "Resistance ($\Omega$)"
        self.standardGraphProp['Legend'] = None
        self.standardGraphProp['Title'] = ""
        self.standardGraphProp['X'] = True
        self.standardGraphProp['Map'] = False
        self.standardGraphProp['Xscale'] = 'lin'
        self.standardGraphProp['Yscale'] = 'lin'
        self.standardGraphProp['ValueName'] = ''
        self.standardGraphProp['Filename'] = 'test'
        self.standardGraphProp['Row'] = None
        self.standardGraphProp['Column'] = None
        self.standardGraphProp['Rowspan'] = 1
        self.standardGraphProp['Colspan'] = 1
        self.standardGraphProp['Append'] = False

        self.standardGraphProp['Style'] = "Scatter"
        self.standardGraphProp['LineStyle'] = list(self.lineLookup.keys())[0]
        self.standardGraphProp['ScatterStyle'] = self.scatterLookup[0]
        self.standardGraphProp['LineWidth'] = 5
        self.standardGraphProp['ScatterSize'] = 8
        
        
    def getColorTable(self):
        return self.colorTable
    
    def getLineStyleOptions(self):
        return list(self.lineLookup.keys())
    
    def getScatterStyleOptions(self):
        return list(self.scatterLookup)
    
    def getStyleOptions(self):
        return list(self.styleLookup)
    
    def getLabelSizeOptions(self):
        return list(self.labelSizeLookup)
    
    def getLineWidthOptions(self):
        return list(self.lineWidthLookup)
        
    def getScatterSizeOptions(self):
        return list(self.scatterSizeLookup)
    
    def updateAppendGraph(self, state):
        self.appendGraph = state
