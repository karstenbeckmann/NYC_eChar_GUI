
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
import queue as qu
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PyQt5 import QtWidgets, QtCore, QtGui
import Qt_stdObjects as stdObj


class ProberWindow(QtWidgets.QMainWindow):
    
    ErrorQu = qu.Queue()

    def __init__(self, MainGI, QFont=None, QMargin=None, QSpacing=None, width=300, height=200, icon=None, title="Prober"):

        self.styles = ["-", "--", ":", "-.", ".", ",", "o", "v", "^", "<", ">"]
        self.sizes = [0.5,1,1.5,2,3]
        self.colors = ['blue', 'red', 'black', 'green', "orange"]    
        
        self.QFont=QFont
        self.QMargin = QMargin
        self.QSpacing = QSpacing
        self.windowName = "ProberWindow"
        self.returnQueue = qu.Queue()
        self.actColor = "lightblue"
        self.maxMoveLength = 6
        self.maxMoveIndexLength = 2
        
        super().__init__(MainGI)
        self.MainGI = MainGI
        self.Configuration = MainGI.Configuration
        self.__width = width
        self.__height = height
        self.iconPath = self.MainGI.iconPath
        self.icon = icon
        self.Instruments = MainGI.Instruments
        self.Instr = self.Instruments.getProberInstrument()
        self.Prober = self.Instruments.getProber()
        self.chuckStatus = self.Instruments.getProberChuckStatus()
        self.scopeStatus = self.Instruments.getProberScopeStatus()
        self.chuckScope = True
        self.setTemp = 25
        self.updList = []

        if self.getConfigParameter("ChuckScope") != None:
            if self.getConfigParameter("ChuckScope"):
                self.chuckScope = True
            else:
                self.chuckScope = False

        self.columns = 9
        self.rows = 9

        self.RowHeight = int(self.__height/self.rows)
        self.ColumnWidth = int(self.__width/self.columns)

        self.setWindowTitle(title)

        try: 
            self.setWindowIcon(self.icon)
        except:
            self.MainGI.WriteError("Icon not found in window %s" %(title))
        self._main = stdObj.stdFrameGrid(self, self.MainGI, self.columns, self.rows, self.__width, self.__height)
        
        self._main.setFont(self.QFont)
        self._main.setContentsMargins(*self.QMargin)
        self.resize(int(self.__width), int(self.__height))
        self._main.resize(int(self.__width), int(self.__height))
        self.layout = self._main.layout

        rowHeight = self._main.getRowHeight()
        colWidth = self._main.getColumnWidth()
        for n in range(1,6,1):
            self.layout.setColumnMinimumWidth(n, int(rowHeight))
            
        self.Menus = []
        self.proWid = []
        self.MoveEntryWid = []

        
        defColor = self.palette().color(QtGui.QPalette.Background)
        self.defColor = [defColor.red(), defColor.green(), defColor.blue()]

        iconPath = os.path.join(self.iconPath,'Stop.png')
        wid = IconPushButton(self._main, iconPath, "Stop", self.layout, 6, 3, command=self.stop)
        self.proWid.append(wid)

        iconPath = os.path.join(self.iconPath,'DoubleArrow_Right.png')
        wid = IconPushButton(self._main, iconPath, "Right_Double", self.layout, 6, 5, command=self.moveRightIndex)
        self.proWid.append(wid)

        iconPath = os.path.join(self.iconPath,'DoubleArrow_Left.png')
        wid = IconPushButton(self._main, iconPath, "Left_Double", self.layout, 6, 1, command=self.moveLeftIndex)
        self.proWid.append(wid)

        iconPath = os.path.join(self.iconPath,'SingleArrow_Right.png')
        wid = IconPushButton(self._main, iconPath, "Right_Single", self.layout, 6, 4, command=self.moveRight)
        self.proWid.append(wid)

        iconPath = os.path.join(self.iconPath,'SingleArrow_Left.png')
        wid = IconPushButton(self._main, iconPath, "Left_Single", self.layout, 6, 2, command=self.moveLeft)
        self.proWid.append(wid)
        
        
        iconPath = os.path.join(self.iconPath,'DoubleArrow_Up.png')
        wid = IconPushButton(self._main, iconPath, "Up_Double", self.layout, 4, 3, command=self.moveUpIndex)
        self.proWid.append(wid)

        iconPath = os.path.join(self.iconPath,'DoubleArrow_Down.png')
        wid = IconPushButton(self._main, iconPath, "Down_Double", self.layout, 8, 3, command=self.moveDownIndex)
        self.proWid.append(wid)

        iconPath = os.path.join(self.iconPath,'SingleArrow_Up.png')
        wid = IconPushButton(self._main, iconPath, "Up_Single", self.layout, 5, 3, command=self.moveUp)
        self.proWid.append(wid)

        iconPath = os.path.join(self.iconPath,'SingleArrow_Down.png')
        wid = IconPushButton(self._main, iconPath, "Down_Single", self.layout, 7, 3, command=self.moveDown)
        self.proWid.append(wid)

        height = rowHeight
        width = rowHeight * 5
        self.chuckScopeFrame = ChuckScope(self._main, self.MainGI, width, height)
        self.layout.addWidget(self.chuckScopeFrame, 1, 1, 1, 5)

        self.contactModesFrame = Contact(self._main, self.MainGI, self.iconPath, self.Prober, width, height)
        self.layout.addWidget(self.contactModesFrame, 2, 1, 1, 5)

        height = rowHeight*6
        width = colWidth*2
        align = QtCore.Qt.AlignRight
        self.statusFrame = StatusWidgets(self._main, self.MainGI, self.iconPath, self.Prober, width, height)
        self.layout.addWidget(self.statusFrame, 4, 8, 6, 2, align)

        alignRight = QtCore.Qt.AlignRight
        alignLeft = QtCore.Qt.AlignLeft

        chuckTemp = self.Instruments.getChuckTemperature()

        self.TempTxt = Label(self._main, "Chuck Temperature: ", self.layout, 1, 6, rowspan=1, columnspan=4, alignment=alignRight)
        self.CurChuckTempTx = Label(self._main, "Current (℃): ", self.layout, 2, 6, rowspan=1, columnspan=3, alignment=alignRight)
        self.ProberCurTemp = Label(self._main, " %s" %(chuckTemp), self.layout, 2, 9, rowspan=1, columnspan=1, alignment=alignLeft)

        self.SetChuckTempTx = Label(self._main, "Set (℃): ", self.layout, 3, 6, rowspan=1, columnspan=3, alignment=alignRight)
        self.TempEnt = LineEdit(self._main, str(chuckTemp), self.layout, 3, 9, 1, 1, validateNumbers="^[1-9]$|^[1-9][0-9]$|^[1-2][0-9][0-9]$|^(300)$", command=self.ChangeTempReturn)
        
        label = Label(self._main, "Move (\u03BCm)", self.layout, 4, 6, rowspan=1, columnspan=2, alignment=alignRight)
        label = Label(self._main, "X:", self.layout, 5, 6, rowspan=1, columnspan=1, alignment=alignRight)
        self.MoveXWid = ChuckScopeEntry(self._main, self.MainGI, "MoveX", maxLength=self.maxMoveLength,  default=100, command=self.writeMoveX)
        self.MoveEntryWid.append(self.MoveXWid)
        self.layout.addWidget(self.MoveXWid, 5, 7, 1, 1)
        label = Label(self._main, "Y:", self.layout, 6, 6, rowspan=1, columnspan=1, alignment=alignRight)
        self.MoveYWid = ChuckScopeEntry(self._main, self.MainGI, "MoveY", maxLength=self.maxMoveLength,  default=100, command=self.writeMoveY)
        self.MoveEntryWid.append(self.MoveYWid)
        self.layout.addWidget(self.MoveYWid, 6, 7, 1, 1)
        
        label = Label(self._main, "Move (die)", self.layout, 7, 6, rowspan=1, columnspan=2, alignment=alignRight)
        label = Label(self._main, "X:", self.layout, 8, 6, rowspan=1, columnspan=1, alignment=alignRight)
        self.MoveXIndexWid = ChuckScopeEntry(self._main, self.MainGI, "MoveXIndex", maxLength=self.maxMoveIndexLength, default=1, command=self.writeMoveIndexX)
        self.MoveEntryWid.append(self.MoveXIndexWid)
        self.layout.addWidget(self.MoveXIndexWid, 8, 7, 1, 1)
        label = Label(self._main, "Y:", self.layout, 9, 6, rowspan=1, columnspan=1, alignment=alignRight)
        self.MoveYIndexWid = ChuckScopeEntry(self._main, self.MainGI, "MoveYIndex", maxLength=self.maxMoveIndexLength, default=1, command=self.writeMoveIndexY)
        self.MoveEntryWid.append(self.MoveYIndexWid)
        self.layout.addWidget(self.MoveYIndexWid, 9, 7, 1, 1)
        
        label = Label(self._main, "Velocity:", self.layout, 9, 1, rowspan=1, columnspan=2, alignment=alignRight)
        self.VelocityEntryWid = ChuckScopeEntry(self._main, self.MainGI, "Velocity", "^[1-9]$|^[1-9][0-9]$|^(100)$", 3, default=100, command=self.writeVelocity)
        self.MoveEntryWid.append(self.VelocityEntryWid)
        self.layout.addWidget(self.VelocityEntryWid, 9, 3, 1, 1)
        

        self.setFixedSize(self.size())
        self.getMoves()

    def updateList(self, widget):
        self.updList.append(widget)

    def hide(self):
        self.savePosition()
        super().hide()

    def ChangeTempReturn(self):
        try:
            self.setTemp = int(self.TempEnt.text())
            self.Instruments.getProberInstrument().SetHeaterTemp(self.setTemp)
            self.MainGI.WriteLog("Chuck Temperature set to %d." %(self.setTemp))
            self.TempEntryLocked = True
        except:
            self.MainGI.WriteError("Not able to set Chuck Temperature to %d." %(self.setTemp))

    def getMoves(self):
        self.moveX = self.MoveXWid.getVariable()
        self.moveY = self.MoveYWid.getVariable()
        self.moveIndexX = self.MoveXIndexWid.getVariable()
        self.moveIndexY = self.MoveYIndexWid.getVariable()
        self.moveVel = self.VelocityEntryWid.getVariable()

    def writeMoveX(self):
        self.moveX = self.MoveXWid.getVariable()

    def writeMoveY(self):
        self.moveY = self.MoveYWid.getVariable()

    def writeMoveIndexX(self):
        self.moveIndexX = self.MoveXIndexWid.getVariable()

    def writeMoveIndexY(self):
        self.moveIndexY = self.MoveYIndexWid.getVariable()

    def writeVelocity(self):
        self.moveVel = self.VelocityEntryWid.getVariable()

    def moveUp(self):
        x = 0
        y = self.moveY
        v = self.moveVel

        if self.chuckScope:
            cmd = "MoveChuck"
        else:
            cmd = "MoveChuck"

        args = (x,y)
        kwargs = {"velocity":v}

        self.Instruments.queueCommand(self.Prober, self.returnQueue, cmd, args, kwargs)

    def moveDown(self):
        
        x = 0
        y = -1*self.moveY
        v = self.moveVel

        if self.chuckScope:
            cmd = "MoveChuck"
        else:
            cmd = "MoveChuck"

        args = (x,y)
        kwargs = {"velocity":v}

        self.Instruments.queueCommand(self.Prober, self.returnQueue, cmd, args, kwargs)

    
    def moveRight(self):
        x = self.moveX
        y = 0
        v = self.moveVel

        if self.chuckScope:
            cmd = "MoveChuck"
        else:
            cmd = "MoveChuck"

        args = (x,y)
        kwargs = {"velocity":v}

        self.Instruments.queueCommand(self.Prober, self.returnQueue, cmd, args, kwargs)

    def moveLeft(self):
        
        x = -1*self.moveX
        y = 0
        v = self.moveVel

        if self.chuckScope:
            cmd = "MoveChuck"
        else:
            cmd = "MoveChuck"

        args = (x,y)
        kwargs = {"velocity":v}

        self.Instruments.queueCommand(self.Prober, self.returnQueue, cmd, args, kwargs)

    def moveUpIndex(self):
        x = 0
        y = self.moveIndexY
        v = self.moveVel

        if self.chuckScope:
            cmd = "MoveChuckIndex"
        else:
            cmd = "MoveScopeIndex"

        args = (x,y)
        kwargs = {"velocity":v}

        self.Instruments.queueCommand(self.Prober, self.returnQueue, cmd, args, kwargs)


    def moveDownIndex(self):
        x = 0
        y = -1*self.moveIndexY
        v = self.moveVel

        if self.chuckScope:
            cmd = "MoveChuckIndex"
        else:
            cmd = "MoveScopeIndex"

        args = (x,y)
        kwargs = {"velocity":v}

        self.Instruments.queueCommand(self.Prober, self.returnQueue, cmd, args, kwargs)

    
    def moveRightIndex(self):
        x = self.moveIndexX
        y = 0
        v = self.moveVel

        if self.chuckScope:
            cmd = "MoveChuckIndex"
        else:
            cmd = "MoveScopeIndex"

        args = (x,y)
        kwargs = {"velocity":v}

        self.Instruments.queueCommand(self.Prober, self.returnQueue, cmd, args, kwargs)

    def moveLeftIndex(self):
        
        x = -1*self.moveIndexX
        y = 0
        v = self.moveVel

        if self.chuckScope:
            cmd = "MoveChuckIndex"
        else:
            cmd = "MoveScopeIndex"

        args = (x,y)
        kwargs = {"velocity":v}

        self.Instruments.queueCommand(self.Prober, self.returnQueue, cmd, args, kwargs)


    def scopeClicked(self):
        self.chuckScope = False
        self.contactModesFrame.scopeClicked()
        for wid in self.MoveEntryWid:
            wid.scopeClicked()
        
        self.getMoves()

    def chuckClicked(self):
        self.chuckScope = True
        self.contactModesFrame.chuckClicked()
        for wid in self.MoveEntryWid:
            wid.chuckClicked()
        
        self.getMoves()

    def stop(self):
        None

    def savePosition(self):
        self.Configuration.setValue("%sX" %(self.windowName), self.pos().x())
        self.Configuration.setValue("%sY" %(self.windowName), self.pos().y())
        self.Configuration.setValue("%sMon" %(self.windowName), QtWidgets.QDesktopWidget().screenNumber(self))

    def closeEvent(self, event):
        self.hide()

    def update(self):

        if self.Prober != None:
            
            if self.MainGI.isRunning():
                self.setEnabled(False)
            else:
                self.setEnabled(True)
                self.chuckScopeFrame.update()
                self.contactModesFrame.update()
                self.statusFrame.update()
                self.chuckStatus = self.Instruments.getProberChuckStatus()
                self.scopeStatus = self.Instruments.getProberScopeStatus()
                for entry in self.updList:
                    entry.update()
        else:
            self.setEnabled(False)


        if self.Instruments.getProberInstrument() != None:
            self.ProberCurTemp.setText(" %s" %(self.Instruments.getChuckTemperature()))
       
    def getConfigParameter(self, name):
        name = "$$ProberWindow$$_%s" %(name)
        ret =  self.Configuration.getValue(name)
        return ret
        
    def setConfigParameter(self, name, parameter):
        name = "$$ProberWindow$$_%s" %(name)
        self.Configuration.setValue(name, parameter)

    def on_closing(self):
        self.destroy()

class ProberWindowSubFrame(stdObj.stdFrame):

    def __init__(self, parent, MainGI, width, height, **kwargs):

        super().__init__(parent, MainGI, width, height, **kwargs)

        self.width = width
        self.height = height

        self.Configuration = parent.Configuration
        self.defColor = parent.defColor
        self.Instruments = MainGI.Instruments
        self.returnQueue = qu.Queue()
        self.MainGI = MainGI
        self.actColor = parent.actColor

        self.chuckScope = parent.chuckScope

        self.defPal = self.MainGI.getColorPalette("default", "base")
        self.actPal = self.MainGI.getColorPalette("orange", "base")

    def __getattr__(self, item):
        if item == "changeWidgetColor":
            return getattr(self.MainGI, item)

        return getattr(self.parent(), item)

    def getChuckScope(self):
        return self.parent().chuckScope

    def getChuckStatus(self):
        return self.parent().chuckStatus

    def getScopeStatus(self):
        return self.parent().scopeStatus

    def getLayout(self):
        return self.layout
        
    def getConfigParameter(self, name):
        name = "$$ProberWindow$$_%s" %(name)
        self.Configuration.getValue(name)
        
    def setConfigParameter(self, name, paramter):
        name = "$$ProberWindow$$_%s" %(name)
        self.Configuration.setValue(name, paramter)

class StatusWidgets(stdObj.stdFrameGrid):

    def __init__(self, parent, MainGI, iconPath, prober, width, height, **kwargs):


        self.width = width/2
        self.height = self.width * 2 / 3 

        super().__init__( parent, MainGI, 2, 7, self.width, self.height, cell=True, **kwargs)

        self.returnQueue = qu.Queue()

        self.proWid = []

        marg = QtCore.QMargins(1,1,1,1)
        self.layout.setContentsMargins(marg)
        self.layout.setSpacing(1)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        wid = StatusPushButton(self, self.iconPath, "Motor_QuiteMode", "Mode", [6,6], 2, self.layout, self.RowHeight, self.ColumnWidth, 7,1, command=self.toggleQuiteMode)
        self.proWid.append(wid)
        
        #wid = StatusPushButton(self, self.iconPath, "ChuckVacuum", "Vacuum", 0, 0, self.layout, self.RowHeight, self.ColumnWidth, 1, 3, command=self.toggleQuiteMode)
        #self.proWid.append(wid)

        size = QtCore.QSize(int(self.width), int(self.height))

        self.defPal = self.MainGI.getColorPalette("default", "base")
        self.actPal = self.MainGI.getColorPalette("orange", "base")


    def toggleQuiteMode(self):
        chuckScope = self.getChuckScope()
        chuckStatus = self.getChuckStatus()
        scopeStatus = self.getScopeStatus()

        try:
            try:
                mode = chuckStatus["Mode"][6]
            except IndexError as e:
                return False

            if mode:
                cmd = "DisableMotorQuiet"
            else:
                cmd = "EnableMotorQuiet"
            
                    
            self.Instruments.queueCommand(self.Prober, self.returnQueue, cmd)

        except (ValueError, KeyError) as e:
            self.ErrorQu.put("ProberControl: ToggleQuiteMode - %s" %(e))

    def update(self):
        self.chuckScope = self.parent().chuckScope
        for entry in self.proWid:
            entry.update()

    def __getattr__(self, item):
        if item == "changeWidgetColor":
            return getattr(self.MainGI, item)

        return getattr(self.parent(), item)

    def getChuckScope(self):
        return self.parent().chuckScope

    def getChuckStatus(self):
        return self.parent().chuckStatus

    def getScopeStatus(self):
        return self.parent().scopeStatus

    def getLayout(self):
        return self.layout
        
    def getConfigParameter(self, name):
        name = "$$ProberWindow$$_%s" %(name)
        self.Configuration.getValue(name)
        
    def setConfigParameter(self, name, paramter):
        name = "$$ProberWindow$$_%s" %(name)
        self.Configuration.setValue(name, paramter)

class ChuckScope(ProberWindowSubFrame):

    def __init__(self, parent, MainGI, width, height, **kwargs):
        
        super().__init__(parent, MainGI, width, height, **kwargs)
        
        self.layout = QtWidgets.QHBoxLayout(self)
        
        self.ChuckWid = QtWidgets.QPushButton("Chuck", self)
        self.ChuckWid.clicked.connect(self.chuckClicked)
        self.layout.addWidget(self.ChuckWid)
        self.ChuckWid.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.ChuckWid.setAutoFillBackground(True)
                
        self.ScopeWid = QtWidgets.QPushButton("Scope", self)
        self.ScopeWid.clicked.connect(self.scopeClicked)
        self.layout.addWidget(self.ScopeWid)
        self.ScopeWid.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.ScopeWid.setAutoFillBackground(True)
        
        self.font = self.ChuckWid.font()
        pointSize = self.font.pointSize()+4
        self.font.setPixelSize(pointSize)
        
        self.ChuckWid.setAutoFillBackground(True)
        self.ScopeWid.setAutoFillBackground(True)

        if self.chuckScope:
            self.changeWidgetColor(self.ChuckWid, self.actColor, "background")
            self.changeWidgetColor(self.ScopeWid, "default", "background")
            self.ScopeWid.setFont(self.font)
            self.ChuckWid.setFont(self.font)
        else:
            self.changeWidgetColor(self.ScopeWid, self.actColor, "background")
            self.changeWidgetColor(self.ChuckWid, "default", "background")
            self.ScopeWid.setFont(self.font)
            self.ChuckWid.setFont(self.font)

        self.layout.setContentsMargins(1,1,1,1)
        self.layout.setSpacing(1)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

    def chuckClicked(self):
        if not self.chuckScope:
            self.chuckScope = True
            self.parent().chuckClicked()
            self.setConfigParameter("ChuckScope", self.chuckScope)
            self.changeWidgetColor(self.ChuckWid, self.actColor, "background")
            self.changeWidgetColor(self.ScopeWid, "default", "background")
            self.ScopeWid.setFont(self.font)
            self.ChuckWid.setFont(self.font)
        
    def scopeClicked(self):
        if self.chuckScope:
            self.chuckScope = False
            self.parent().scopeClicked()
            self.setConfigParameter("ChuckScope", self.chuckScope)
            self.changeWidgetColor(self.ScopeWid, self.actColor, "background")
            self.changeWidgetColor(self.ChuckWid, "default", "background")
            self.ScopeWid.setFont(self.font)
            self.ChuckWid.setFont(self.font)

    def update(self):
        None
    
class Contact(ProberWindowSubFrame):

    def __init__(self, parent, MainGI, iconPath, Prober, width, height, **kwargs):
        
        super().__init__(parent, MainGI, width, height,  **kwargs)
        
        self.layout = QtWidgets.QHBoxLayout(self)
        self.Prober = Prober
        
        self.iconPath = iconPath
        
        self.ChuckContactIcon = QtGui.QIcon(os.path.join(self.iconPath,'Contact.png'))
        self.ChuckAlignIcon = QtGui.QIcon(os.path.join(self.iconPath,'Align.png'))
        self.ChuckSeparateIcon = QtGui.QIcon(os.path.join(self.iconPath,'Separation.png'))

        self.ScopeContactIcon = QtGui.QIcon(os.path.join(self.iconPath,'Contact_Scope.png'))
        self.ScopeAlignIcon = QtGui.QIcon(os.path.join(self.iconPath,'Align_Scope.png'))
        self.ScopeSeparateIcon = QtGui.QIcon(os.path.join(self.iconPath,'Separation_Scope.png'))
        
        if self.chuckScope:
            self.ContactIcon = self.ChuckContactIcon
            self.AlignIcon = self.ChuckAlignIcon
            self.SeparateIcon = self.ChuckSeparateIcon
        else:
            self.ContactIcon = self.ScopeContactIcon
            self.AlignIcon = self.ScopeAlignIcon
            self.SeparateIcon = self.ScopeSeparateIcon

        self.SeparationWid = QtWidgets.QPushButton(self)
        self.SeparationWid.setIcon(self.SeparateIcon)
        self.layout.addWidget(self.SeparationWid)
        self.SeparationWid.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.SeparationWid.clicked.connect(self.SeparateClicked)

        self.AlignWid = QtWidgets.QPushButton(self)
        self.AlignWid.setIcon(self.AlignIcon)
        self.layout.addWidget(self.AlignWid)
        self.AlignWid.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.AlignWid.clicked.connect(self.AlignClicked)

        self.ContactWid = QtWidgets.QPushButton(self)
        self.ContactWid.setIcon(self.ContactIcon)
        self.layout.addWidget(self.ContactWid)
        self.ContactWid.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.ContactWid.clicked.connect(self.ContactClicked)
        
        iconWidth = 77.5
        iconHeight = 45
        iconRatio = iconWidth/iconHeight

        widWidth = self.ContactWid.size().width()
        widHeight = float(widWidth)/iconRatio
        
        width = self.AlignWid.size().width()
        height = self.AlignWid.size().height()

        size = QtCore.QSize(int(width), int(height))

        self.SeparationWid.setIconSize(size)
        self.ContactWid.setIconSize(size)
        self.AlignWid.setIconSize(size)


        self.layout.setContentsMargins(1,1,1,1)
        self.layout.setSpacing(1)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        self.update()

    def ContactClicked(self):
        if self.ContactStatus != "C":
            if self.chuckScope:
                cmd = "MoveChuckContact"
            else:
                cmd = "MoveScopeContact"
            self.Instruments.queueCommand(self.Prober, self.returnQueue, cmd)

    def AlignClicked(self):
        if self.ContactStatus != "A":
            if self.chuckScope:
                cmd = "MoveChuckAlign"
            else:
                cmd = "MoveScopeAlign"
            self.Instruments.queueCommand(self.Prober, self.returnQueue, cmd)
    
    def SeparateClicked(self):
        if self.ContactStatus != "S":
            if self.chuckScope:
                cmd = "MoveChuckSeparation"
            else:
                cmd = "MoveScopeSeparation"
            self.Instruments.queueCommand(self.Prober, self.returnQueue, cmd)
        
    def setContactIconDefault(self):
        self.changeWidgetColor(self.ContactWid, "Default", "background")
    
    def setContactIconActive(self):
        self.changeWidgetColor(self.ContactWid, self.actColor, "background")
    
    def setAlignIconDefault(self):
        self.changeWidgetColor(self.AlignWid, "Default", "background")
    
    def setAlignIconActive(self):
        self.changeWidgetColor(self.AlignWid,  self.actColor, "background")
    
    def setSeparateIconDefault(self):
        self.changeWidgetColor(self.SeparationWid,  "Default", "background")
    
    def setSeparateIconActive(self):
        self.changeWidgetColor(self.SeparationWid,  self.actColor, "background")
    

    def chuckClicked(self):
        self.ChuckScope = True
        self.ContactIcon = self.ChuckContactIcon
        self.AlignIcon = self.ChuckAlignIcon
        self.SeparateIcon = self.ChuckSeparateIcon
        self.updateIcons()

    def updateIcons(self):
        self.ContactWid.setIcon(self.ContactIcon)
        self.SeparationWid.setIcon(self.SeparateIcon)
        self.AlignWid.setIcon(self.AlignIcon)
    
    def scopeClicked(self):
        self.ChuckScope = False
        self.ContactIcon = self.ScopeContactIcon
        self.AlignIcon = self.ScopeAlignIcon
        self.SeparateIcon = self.ScopeSeparateIcon
        self.updateIcons()

    def getChuckScope(self):
        return self.ChuckScope

    def getLayout(self):
        return self.layout
    
    def setScope(self):
        self.chuckScope = False
    
    def setChuck(self):
        self.chuckScope = True

    def update(self):

        try:
            if self.chuckScope:
                self.ContactStatus = self.parent().chuckStatus["ZHeight"]
            else:
                self.ContactStatus = self.parent().scopeStatus["ZHeight"]
        except (TypeError, KeyError):
            self.ContactStatus = 0

        if self.ContactStatus == "C":
            self.setSeparateIconDefault()
            self.setAlignIconDefault()
            self.setContactIconActive()

        elif self.ContactStatus == "S":
            self.setSeparateIconActive()
            self.setContactIconDefault()
            self.setAlignIconDefault()

        elif self.ContactStatus == "A":
            self.setSeparateIconDefault()
            self.setAlignIconActive()
            self.setContactIconDefault()
        else:
            self.setSeparateIconDefault()
            self.setAlignIconDefault()
            self.setContactIconDefault()

        while not self.returnQueue.empty():
            self.returnQueue.get()


class ChuckScopeEntry(stdObj.Entry):

    def __init__(self, parent, MainGI, valueName, validateNumbers=None, maxLength=None, *args, **kwargs): 
        
        self.name = valueName
        self.validateNumbers = "^[0-9]+$"
        if validateNumbers != None:
            self.validateNumbers = validateNumbers
        
        self.chuckScope = parent.chuckScope
        
        if self.chuckScope:
            cs = "Chuck"
        else:
            cs = "Scope"

        self.valueName = "$$ProberWindow$$_%s_%s" %(cs, self.name)

        kwargs['type'] = int
        kwargs['default'] = 0

        super().__init__(parent, MainGI, self.valueName, validateNumbers=self.validateNumbers, maxLength=maxLength, *args, **kwargs)

    def getVariable(self):
        return int(self.text())

    def chuckClicked(self):
        cs = "Chuck"
        self.chuckScope = True
        self.valueName = "$$ProberWindow$$_%s_%s" %(cs, self.name)
        val = self.getConfigParameter()
        if val == None:
            val = self.default
        self.setVariable(val)

    def scopeClicked(self):
        cs = "Scope"
        self.chuckScope = False
        self.valueName = "$$ProberWindow$$_%s_%s" %(cs, self.name)
        val = self.getConfigParameter()
        if val == None:
            val = self.default
        self.setVariable(val)

    def getConfigParameter(self):
        if self.chuckScope:
            cs = "Chuck"
        else:
            cs = "Scope"
    
        name = "$$ProberWindow$$_%s_%s" %(cs, self.name)
        return self.Configuration.getValue(name)
        
    def setConfigParameter(self, paramter):
        if self.chuckScope:
            cs = "Chuck"
        else:
            cs = "Scope"

        name = "$$ProberWindow$$_%s_%s" %(cs, self.name)
        self.Configuration.setValue(name, paramter)


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

        self.Blocked = False
        self.command = None
        if "command" in kwargs:
            self.command = kwargs['command']
        if alignment == None:
            self.layout.addWidget(self, row, column, rowspan, columnspan)
        else:
            self.layout.addWidget(self, row, column, rowspan, columnspan, alignment)
        
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

        self.command = None
        if "command" in kwargs:
            self.command = kwargs['command']
        if alignment == None:
            self.layout.addWidget(self, row, column, rowspan, columnspan)
        else:
            self.layout.addWidget(self, row, column, rowspan, columnspan, alignment)
        
        self.clicked.connect(self.callFunc)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    
    def getName(self):
        return self.name

    def callFunc(self):
        
        self.queue.put({self.name: True})

        if self.command != None:
            self.command()

class IconPushButton(QtWidgets.QPushButton):

    def __init__(self, parent, icon, name, layout, row, column, rowspan=1, columnspan=1, alignment=None, **kwargs):
         
        if type(icon) == QtGui.QIcon:
            self.icon = icon
        else:
            self.icon = QtGui.QIcon(icon)

        self.iconSize = QtCore.QSize(20,20)

        super().__init__(parent)
        self.setIcon(self.icon)
        self.setIconSize(self.iconSize)

        self.name = name
        self.layout = layout
        self.row = row
        self.column = column
        self.rowspan = rowspan
        self.columnspan = columnspan
        self.MainGI = parent.MainGI

        self.setIcon(self.icon)

        if alignment == None:
            self.layout.addWidget(self, row, column, rowspan, columnspan)
        else:
            self.layout.addWidget(self, row, column, rowspan, columnspan, alignment)

        self.command = None
        if "command" in kwargs:
            self.command = kwargs['command']
        
        self.clicked.connect(self.callFunc)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    
    def getName(self):
        return self.name

    def callFunc(self):
        
        if self.command != None:
            self.command()


class StatusPushButton(QtWidgets.QPushButton):

    def __init__(self, parent, iconPath, name, category, bits, chuckScope, layout, rowheight, colwidth, row, column, rowspan=1, columnspan=1, alignment=None, **kwargs):
        
        #chuckScope - 0 for chuck only, 1 for scope only, 2 for both

        super().__init__(parent)

        self.MainGI = parent.MainGI
        self.iconPath = iconPath
        self.iconPathOn = os.path.join(iconPath,'%s_On.png' %(name))
        self.iconPathOff = os.path.join(iconPath,'%s_Off.png' %(name))
        self.chuckScope = chuckScope
        self.category = category
        if not isinstance(bits, list):
            self.bits = [bits]
        else:
            self.bits = bits
        self.rowheight = rowheight
        self.colwidth = colwidth

        self.iconOff = QtGui.QIcon(self.iconPathOff)
        self.iconOn = QtGui.QIcon(self.iconPathOn)
        self.setIcon(self.iconOff)

        self.name = name
        self.layout = layout
        self.row = row
        self.column = column
        self.rowspan = rowspan
        self.columnspan = columnspan

        if alignment == None:
            self.layout.addWidget(self, row, column, rowspan, columnspan)
        else:
            self.layout.addWidget(self, row, column, rowspan, columnspan, alignment)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        self.command = None
        if "command" in kwargs:
            self.command = kwargs['command']

        self.iconSize = QtCore.QSize(int(self.colwidth), int(self.rowheight))

        self.iconSize = QtCore.QSize(int(self.colwidth*0.75), int(self.rowheight*0.75))
        self.setIconSize(self.iconSize)

        self.clicked.connect(self.callFunc)

        self.parent().updateList(self)

    def getName(self):
        return self.name

    def callFunc(self):
        if self.command != None:
            self.command()

    def update(self):
        
        if self.chuckScope == 0:
            try:
                status = self.parent().getChuckStatus()[self.category][self.bits[0]]
            except (IndexError, TypeError):
                status = None
        elif self.chuckScope == 1:
            try:
                status = self.parent().getScopeStatus()[self.category][self.bits[0]]
            except (IndexError, TypeError):
                status = None
        else:
            if self.parent().getChuckScope():
                try:
                    status = self.parent().getChuckStatus()[self.category][self.bits[0]]
                except (IndexError, TypeError):
                    status = None
            else:
                try:
                    status = self.parent().getScopeStatus()[self.category][self.bits[1]]
                except (IndexError, TypeError):
                    status = None

        if isinstance(status, bool) and status == True:
            self.setIcon(self.iconOn)
            #self.setChecked(True)
        else:
            self.setIcon(self.iconOff)
            #self.setChecked(False)

        
            
class LineEdit(QtWidgets.QLineEdit):

    def __init__(self, parent, text, layout, row, column, columnspan=1, rowspan=1, **kwargs):
            
        super().__init__(parent)
        self.setText(str(text))

        self.layout = layout
        self.layout.addWidget(self, row, column, rowspan, columnspan)

        if 'width' in kwargs:
            self.setMinimumWidth(int(kwargs['width']))

        self.addCommand = None
        if 'command' in kwargs:
            self.addCommand = kwargs['command']

        if 'validateNumbers' in kwargs:
            regEx = QtCore.QRegularExpression(kwargs['validateNumbers'])
            validator = QtGui.QRegularExpressionValidator(regEx, self)
            self.setValidator(validator)
        
        if 'state' in kwargs:
            if kwargs['state'] == 'disabled':
                self.setDisabled(True)
            else:
                self.setDisabled(False)
        
        if self.addCommand != None:
            self.returnPressed.connect(self.addCommand)
        
    def focusOutEvent(self, event):
        
        if self.addCommand != None:
            self.addCommand()
        
        super().focusOutEvent(event)

