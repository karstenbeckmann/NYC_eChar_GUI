"""
Written by: Karsten Beckmann
Institution: SUNY Polytechnic Institute
Date: 6/12/2018

This class is written to support interactive plotting while running a Characterization
"""

import numpy as np
import engineering_notation as en
import pathlib as pl
import datetime as dt
import time as tm
import matplotlib
import matplotlib.pyplot as plt
import matplotlib as mpl
import math as ma 
import threading as th
from  matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches
from matplotlib.ticker import LogFormatter
import matplotlib.animation as animation
import matplotlib.markers as mks
import time as tm
import queue as qu
import sys
from matplotlib.collections import PatchCollection
import os
import StdDefinitions as std
import darkdetect

class plottingRoutine:
    
    end=False
    DieSizeX = 25
    DieSizeY = 32
    WaferSize = 300
    CenterLocationX = 0
    CenterLocationY = 0
    NumOfDies = 1
    NumOfDevices = 1
    _Close = False
    ValueName = ""
    thread = None
    data = None
    Folder = ""
    updateTime = 1
    __Figure = None
    __Axis = None
    __Graph = None
    dpi = 600
    Type = "Plot"
    
    Year = dt.datetime.today().strftime("%Y")
    Month = dt.datetime.today().strftime("%m")
    Day = dt.datetime.today().strftime("%d")
    Hour = dt.datetime.today().strftime("%H")
    Minute = dt.datetime.today().strftime("%M")
    Second = dt.datetime.today().strftime("%S")

    def __init__(self, Folder, width, height, ValueName, dpi):
        """
        updateTime in seconds
        Folder to save the final graph in
        DieSizeX: X-dimension of die in mm
        DieSizeY: Y-dimension of die in mm
        WaferSzie: wafer diameter in mm
        CenterLocation: offset in mm from the center of the [0,0] die to the center
        ValueName: Name/Abbreviation of the plotted data
        """
        
        self.ValueName = ValueName
        self.Folder = Folder
        self.width = width
        self.height = height
        self.dpi = dpi
        self.__Figure = None


    def stop(self):
        self._Close = True
        self.thread.join()
        if not self.Folder == None:
            self.SaveToFile()

    def close(self):
        if self.__Figure != None:
            plt.close(self.__Figure)
            #self.__Figure.close()

    def start(self):
        None
    
    def setDPI(self, dpi):
        if not isinstance(dpi, int):
            raise TypeError("DPI must be an integer.")
        self.dpi = dpi

    def update(self):
        None
    
    def setFolder(self, folder):
        self.Folder = folder
    
    def getFolder(self):
        return self.Folder
        
    def SaveToFile(self, filename=None, folder=None):
        
        filename = filename.replace(r"/", "-")
        filename = filename.replace(r'\\\\', "-")
        filename = filename.replace(r"\\", "-")

        filename = filename.split(".")[0]
        fig = self.getFigure()

        HomePath = pl.Path(self.Folder)

        if filename == None: 
            filename = self.Type
        if folder == None:
            Path = HomePath
        else:
            Path = pl.Path.home().joinpath(folder)
        filename = "%s_%s.png" %(filename,dt.datetime.today().strftime("%Y-%m-%d_%H-%M-%S"))

        if not os.path.exists(Path):
            os.makedirs(Path)
        
        file_to_save = Path / filename
        print(file_to_save)
        fig.savefig(file_to_save, bbox_inches='tight', dpi=self.dpi)
    
    def InputData(self, data):
        self.data = data

    def getFigure(self):
        return self.__Figure

    def getGraph(self):
        
        return self.__Graph

    def getValueName(self):
        return self.ValueName

class WaferMap(plottingRoutine):

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

    im = None
    l = None
    cmap = None

    MeasurementStatus = None

    ticks = 15

    def __init__(self, Folder=None, DieSizeX=25, DieSizeY=32, WaferSize=300, CenterLocaiton=[0,0], NumOfDies=1, NumOfDev=1, width=300, height=200, ValueName="", dpi=600, title=None, initValue=None, backgroundColor=None):
           
        
        super().__init__(Folder, width, height, ValueName, dpi)
        
        self.DieSizeX = float(DieSizeX)
        self.DieSizeY = float(DieSizeY)
        self.WaferSize = float(WaferSize)
        self.CenterLocationX = float(CenterLocaiton[0])
        self.CenterLocationY = float(CenterLocaiton[1])
        self.NumOfDies = int(NumOfDies)
        self.NumOfDevices = int(NumOfDev)
        self.initValue = initValue
        self.title = title
        if self.title == None:
            self.WindowTitle = "Wafer map - progress"
        else:
            self.WindowTitle = self.title

        self.xInch = 5
        ratio = height/width
        self.yInch = self.xInch*ratio*.9
        self.dpi = width/self.xInch

        if darkdetect.isDark():
            plt.style.use('dark_background')
        else:
            plt.style.use('ggplot')

        self.__Figure = plt.figure(figsize=(self.xInch, self.yInch), dpi=self.dpi)
        #self.__Figure.suptitle(self.WindowTitle)
        #self.__Figure.style.use('ggplot')
        
        if backgroundColor != None:
            if darkdetect.isDark():
                self.__Figure.patch.set_facecolor(backgroundColor)
            else:
                self.__Figure.patch.set_facecolor(backgroundColor)


        self.start()
        self.__Figure.tight_layout()

    def getFigure(self):
        return self.__Figure
    
    def getGraph(self):
        return self.__Graph

    def getTicks(self, axis):
        radius = float(self.WaferSize)/2
        if axis == 'X':
            self.xhigh = int(ma.floor((radius-self.DieSizeX/2-self.CenterLocationX)/self.DieSizeX))
            self.xlow = -int(ma.floor((radius-self.DieSizeX/2+self.CenterLocationX)/self.DieSizeX))
            Rng = list(range(self.xlow,self.xhigh+1,1))
        elif axis == 'Y':
            self.yhigh = int(ma.floor((radius-self.DieSizeY/2-self.CenterLocationY)/self.DieSizeY))
            self.ylow = -int(ma.floor((radius-self.DieSizeY/2+self.CenterLocationY)/self.DieSizeY))
            Rng = list(range(self.ylow,self.yhigh+1,1))
        return Rng
    
    def calcProp(self):
        self.vmin=0
        self.vmax=self.NumOfDevices
        self.xticks = self.getTicks('X')
        self.yticks = self.getTicks('Y')
        self.xlow = self.xticks[0]
        self.ylow = self.yticks[0]


    def start(self):
            
        c = ["darkred","red", "tomato","orange","green","darkgreen"]
        v = [0,0.2,.4,0.6,0.8,1.]

        self.l = list(zip(v,c))
        self.cmap=LinearSegmentedColormap.from_list('rgr',self.l, N=256)

        self.vmin=0
        self.vmax=self.NumOfDevices

        self.xticks = self.getTicks('X')
        self.yticks = self.getTicks('Y')
        self.xlow = self.xticks[0]
        self.ylow = self.yticks[0]
        
        self.data = np.empty((len(self.yticks), len(self.xticks)), np.longdouble)
        self.data[:] = np.nan

        if not self.initValue == None:
            for x in range(abs(self.xlow)*2+1):
                for y in range(abs(self.ylow)*2+1):
                    if std.isDieInWafer(self.WaferSize, x+self.xlow, y+self.ylow, 12, 15):
                        self.data[y][x] = self.initValue
        
        self.__Graph = self.__Figure.add_subplot(111)
        self.im = self.__Graph.imshow(self.data, cmap=self.cmap, vmin=self.vmin, vmax=self.vmax)

        self.axisPrep()
       
    def axisPrep(self):

        if self.ValueName == "":
            self.ValueName = "Measured Dies"

        # We want to show all ticks...
        xlen = len(self.xticks)
        ylen = len(self.yticks)

        n = 0
        for x in self.xticks:
            if x == 0:
                self.CenterLocationX
            n+=0

        n = 0
        for x in self.yticks:
            if x == 0:
                self.CenterLocationY
            n+=0

        xSep = int(ma.ceil(xlen/self.ticks))
        ySep = int(ma.ceil(ylen/self.ticks))

        PrXticks = []
        PrYticks = []

        for x in self.xticks:
            if x % xSep:
                PrXticks.append('')
            else:
                PrXticks.append(x)
        
        for y in self.yticks:
            if y % ySep:
                PrYticks.append('')
            else:
                PrYticks.append(-y)

        self.__Graph.set_xticks(np.arange(len(PrXticks)))
        self.__Graph.set_yticks(np.arange(len(PrYticks)))

        self.__Graph.set_xticklabels(PrXticks)
        self.__Graph.set_yticklabels(PrYticks)

        self.__Graph.set_xlabel("X Die Number")
        self.__Graph.set_ylabel("Y Die Number")

        self.__Graph.set_title(self.WindowTitle)

    def update(self, **kwargs):
        
        calcUpdate = False
        for key, item in kwargs.items():

            if key == "Folder":
                self.Folder = item
            if key == "DieSizeX":
                self.DieSizeX = item
                calcUpdate = True
            if key == "DieSizeY":
                self.DieSizeY = item
                calcUpdate = True
            if key == "WaferSize":
                self.WaferSize = item
                calcUpdate = True
            if key == "CenterLocation":
                self.CenterLocationX = item[0]
                self.CenterLocationY = item[1]
                calcUpdate = True
            if key == "NumOfDies":
                self.NumOfDies = item
                calcUpdate = True
            if key == "NumOfDevices":
                self.NumOfDevices = item
                calcUpdate = True
            if key == "BackgroundColor":
                calcUpdate = True

        if calcUpdate:
            self.calcProp()
            
            self.data = np.empty((len(self.yticks), len(self.xticks)), np.longdouble)
            self.data[:] = np.nan
                
            if darkdetect.isDark():
                plt.style.use('dark_background')
            else:
                plt.style.use('ggplot')
            
            self.__Figure = plt.figure(figsize=(self.xInch, self.yInch), dpi=self.dpi)
            self.__Graph = self.__Figure.add_subplot(111)
            
            if darkdetect.isDark():
                plt.style.use('dark_background')
            else:
                plt.style.use('ggplot')

            if "BackgroundColor" in kwargs:
                if darkdetect.isDark():
                    self.__Figure.patch.set_facecolor(kwargs["BackgroundColor"])
                else:
                    self.__Figure.patch.set_facecolor(kwargs["BackgroundColor"])

        if "locations" in kwargs:
            
            if "value" in kwargs:
                vals = kwargs['value']
            else:
                vals = [0]*len(kwargs['locations'])
            for loc, val in zip(kwargs["locations"], vals):
                self.writeToData(loc[0], loc[1], value=val)

        #if isinstance(self.im)
        #    self.im.remove()
        self.im = self.__Graph.imshow(self.data, cmap=self.cmap, vmin=self.vmin, vmax=self.vmax)
        self.axisPrep()
        self.__Figure.tight_layout()
            

    def writeToData(self, xDie, yDie, add=0, value=None):
        if value==None:
            newData = self.data[-yDie-self.ylow,xDie-self.xlow] + float(add)
            self.data[-yDie-self.ylow,xDie-self.xlow] = float(newData)
        else:
            newData = value
            self.data[-yDie-self.ylow,xDie-self.xlow] = float(value)

class WaferMapValues(plottingRoutine):
    
    DieSizeX = 25
    DieSizeY = 36
    WaferSize = 300
    CenterLocationX = 0
    CenterLocationY = 0

    xticks = []
    yticks = []

    title = "Value Map"

    xlow = 0
    ylow = 0

    xhigh = 0
    yhigh = 0

    xcenter = 0
    ycenter = 0

    SpecLow = 0
    SpecHigh = 1

    data = np.array([[]])

    im = None
    l = None
    cmap = None

    MeasurementStatus = None

    ticks = 15

    def __init__(self, title, SpecLow=0, SpecHigh=1, Folder=None, DieSizeX=25, DieSizeY=32, WaferSize=300, CenterLocaiton=[0,0], NumOfDies=1, NumOfDev=1, width=300, height=200, ValueName="", dpi=600):
        
    
        self.DieSizeX = float(DieSizeX)
        self.DieSizeY = float(DieSizeY)
        self.WaferSize = float(WaferSize)
        self.CenterLocationX = float(CenterLocaiton[0])
        self.CenterLocationY = float(CenterLocaiton[1])
        self.NumOfDies = int(NumOfDies)
        self.NumOfDevices = int(NumOfDev)

        self.title = title
        self.SpecLow = SpecLow
        self.SpecHigh = SpecHigh


        super().__init__(Folder, width, height, ValueName, dpi)

    def animate(self):
        None


    def getFigure(self):
        return self.__Figure
    
    def getGraph(self):
        return self.__Graph

    def getTicks(self, axis):
        radius = self.WaferSize/2
        if axis == 'X':
            self.xhigh = int(ma.floor((radius-self.DieSizeX/2-self.CenterLocationX)/self.DieSizeX))
            self.xlow = -int(ma.floor((radius-self.DieSizeX/2+self.CenterLocationX)/self.DieSizeX))
            Rng = list(range(self.xlow,self.xhigh+1,1))
        elif axis == 'Y':
            self.yhigh = int(ma.floor((radius-self.DieSizeY/2-self.CenterLocationY)/self.DieSizeY))
            self.ylow = -int(ma.floor((radius-self.DieSizeY/2+self.CenterLocationY)/self.DieSizeY))
            Rng = list(range(self.ylow,self.yhigh+1,1))

        return Rng
    
    def start(self):

        c = ["darkred","red", "tomato","orange","green","darkgreen","green","orange","tomato", "red","darkred"]
        v = [0,0.1,0.2,.3,.4,.5,0.6,.7,0.8,0.9,1.]
        WindowTitle =  "Wafer Map - %s" %(self.title)
            
        self.l = list(zip(v,c))
        self.cmap=LinearSegmentedColormap.from_list('rgr',self.l, N=256)

        self.xticks = self.getTicks('X')
        self.yticks = self.getTicks('Y')
        self.xlow = self.xticks[0]
        self.ylow = self.yticks[0]

        self.data = np.empty((len(self.yticks), len(self.xticks)), np.longdouble)
        #self.data[:] = 1
        self.data[:] = np.nan

        X = np.linspace(0, 2 * np.pi, 50)
        Y = np.sin(X)
        
        self.xInch = 5
        self.ratio = self.height/self.width
        self.yInch = self.xInch*self.ratio
        self.dpi = self.width/self.xInch

        self.patches = []

        if darkdetect.isDark():
            plt.style.use('dark_background')
        else:
            plt.style.use('ggplot')
            
        self.__Figure = plt.figure(figsize=(self.xInch,self.yInch), dpi=self.dpi)
        self.__Figure.tight_layout()
        self.__Figure.suptitle(WindowTitle)
        self.__Graph = self.__Figure.add_subplot(111)
        self.im = self.__Graph.imshow(self.data, cmap=self.cmap, vmin=self.SpecLow, vmax=self.SpecHigh)

        width = self.WaferSize/self.DieSizeX
        height = self.WaferSize/self.DieSizeY
        
        self.Ellipse = mpatches.Ellipse((-self.xlow, -self.ylow), width=width, height=height, edgecolor='darkblue', fill=False)
        self.__Graph.add_patch(self.Ellipse)


        #self.__Graph.grid(True)

        # Create colorbar

        #cmap=plt.get_cmap("PiYG", 7), norm=norm, cbar_kw=dict(ticks=np.arange(-3, 4), format=fmt),
        #cbarlabel = "cbarlabel"
        #cbar = self.__Figure.colorbar(self.im, ax=self.__Graph)
        #cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

        if self.ValueName == "":
            self.ValueName = "Measured Dies"
        # We want to show all ticks...
        xlen = len(self.xticks)
        ylen = len(self.yticks)

        n = 0
        for x in self.xticks:
            if x == 0:
                self.CenterLocationX
            n+=0

        n = 0
        for x in self.yticks:
            if x == 0:
                self.CenterLocationY
            n+=0

        xSep = int(ma.ceil(xlen/self.ticks))
        ySep = int(ma.ceil(ylen/self.ticks))

        PrXticks = []
        PrYticks = []

        for x in self.xticks:
            if x % xSep:
                PrXticks.append('')
            else:
                PrXticks.append(x)
        
        for y in self.yticks:
            if y % ySep:
                PrYticks.append('')
            else:
                PrYticks.append(-y)

        self.__Graph.set_xticks(np.arange(len(PrXticks)))
        self.__Graph.set_yticks(np.arange(len(PrYticks)))

        self.__Graph.set_xticklabels(PrXticks)
        self.__Graph.set_yticklabels(PrYticks)

        self.__Graph.set_xlabel("X Die Number")
        self.__Graph.set_ylabel("Y Die Number")


    def update(self):
        
        self.__Graph.imshow(self.data, cmap=self.cmap, vmin=self.SpecLow, vmax=self.SpecHigh)
        #self.__Graph.set_aspect(aspect=self.ratio)

    def writeToData(self, xDie, yDie, add=0, value=None, Unit=None):

        if value==None:
            newData = self.data[yDie-self.ylow,xDie-self.xlow] + add
            self.data[yDie-self.ylow,xDie-self.xlow] = newData
        else:
            newData = value
            self.data[yDie-self.ylow,xDie-self.xlow] = value

        EngValue = en.EngNumber(newData, 1)
        if isinstance(Unit, str):
            EngValue = "%s%s" %(EngValue, Unit)

        self.__Graph.text(xDie-self.xlow-1.35, yDie-self.ylow-0.6, str(EngValue), fontdict={'size': 9})

#class ResistiveStates(plottingRoutine):

class XY(plottingRoutine):

    def __init__(self, Folder, data, GraphProperties, width=5, height=4, dpi=600, backgroundColor=None):

        super().__init__(Folder, width, height, GraphProperties['valueName'], dpi)

        self.width = width
        self.height = height
        self.X = GraphProperties['x']
        self.Map = GraphProperties['map']

        if data == []:
            data = [0]
        self.data = data
        
        self.checkData(self.data)

        self.xscale = GraphProperties['xScale']
        self.yscale = GraphProperties['yScale']
        self.legend = GraphProperties['legend']

        self.linestyle = self.adjustInput(GraphProperties['lineStyle'])
        self.linewidth = self.adjustInput(GraphProperties['lineSize'])
        self.color = self.adjustInput(GraphProperties['lineColor'])
        
        if not self.Map:
            self.checkInputDimensions(self.linestyle, "Linestyle")
            self.checkInputDimensions(self.linewidth, "Linewidth")
            self.checkInputDimensions(self.color, "Color")

        xInch = 5
        ratio = self.height/self.width
        yInch = xInch*ratio
        dpi = self.width/xInch

        self.__Figure = plt.figure(figsize=(xInch,yInch), dpi=dpi)
        self.__Figure.tight_layout()
        self.__Graph = self.__Figure.add_subplot(111)
        
        if backgroundColor != None:
            if darkdetect.isDark():
                self.__Figure.patch.set_facecolor(backgroundColor)
            else:
                self.__Figure.patch.set_facecolor(backgroundColor)
        
        self.updateWithResult(self.data, GraphProperties)

    def adjustInput(self, Input):
        if not isinstance(Input, list):
            if isinstance(self.data, (list, np.ndarray)):
                if self.PlotType == "Y":
                    return [Input]
                elif self.PlotType == "XY":
                    if len(np.shape(self.data)) == 3:
                        return [Input]*(len(self.data))
                    elif len(np.shape(self.data)) == 2:
                        return [Input]*(len(self.data)-1)
                    else:
                        return [Input]
                elif self.PlotType == "YY":
                    return [Input]*(len(self.data))
            else:
                return [Input]
        else:
            return Input

    def checkData(self, data):
        if not isinstance(data, (list, np.ndarray)):
            raise ValueError("Data must be a one or more dimensional list of int/float.")
        if not isinstance(data[0], (list, np.ndarray)):
            self.PlotType='Y'
        else:
            if self.Map:
                self.PlotType = 'Map'
            else:
                if self.X:
                    self.PlotType='XY'
                else:
                    self.PlotType='YY'

        

    def checkInputDimensions(self, n, description):
        if not isinstance(n, (int,float,str)):
            if isinstance(n, list):
                if self.PlotType=='Y' and len(n) < 1:
                    raise TypeError("%s must be the same dimension as the data input")
                #if not len(list) == len(n):
                #    raise TypeError("%s must be the same dimension as the data input")
                for x in range(len(n)):
                    if not isinstance(x, (int,float,str)):
                        raise TypeError("%s inputs must be int,float or str.")

    def updateWithResult(self, data, GraphProperties):

        self.X = GraphProperties['x']
        self.Map = GraphProperties['map']
        self.data = data

        self.checkData(self.data)
        self.xscale = GraphProperties['xScale']
        self.yscale = GraphProperties['yScale']
        self.cbarlabel = GraphProperties['cLabel']
        self.legend = GraphProperties['legend']
        if not isinstance(self.legend, list) and self.legend != None:
            self.legend = [self.legend]

        self.linestyle = GraphProperties['lineStyle']
        self.linewidth = GraphProperties['lineSize']
        self.color = GraphProperties['lineColor']
        
        self.linestyle = self.adjustInput(self.linestyle)
        self.linewidth = self.adjustInput(self.linewidth)
        self.color = self.adjustInput(self.color)

        if not self.Map:
            self.checkInputDimensions(self.linestyle, "Linestyle")
            self.checkInputDimensions(self.linewidth, "Linewidth")
            self.checkInputDimensions(self.color, "Color")
        self.__Graph.cla()
        
        self.update(self.data, self.X, self.Map)
        
        if self.yscale == 'lin':
            self.__Graph.ticklabel_format(style='sci', axis='y', scilimits=(-1,1))

        if self.xscale == 'lin':
            self.__Graph.ticklabel_format(style='sci', axis='x', scilimits=(-1,1))
        
        if self.legend != None:
            for line, label in zip(self.lines,self.legend):
                line.set_label(label)
            self.__Graph.legend(loc="upper right", prop={"size":8})
            #self.__Graph.legend(handles=self.lines, self.legend, loc="upper right")

        if self.Map:
            if len(self.__Graph.figure.axes) < 2:
                #formatter = LogFormatter(10, labelOnlyBase=False)
                cbarkwargs = {}
                #cbarkwargs = {'format': formatter}
                self.cbar = self.__Graph.figure.colorbar(self.lines[0], ax=self.__Graph, **cbarkwargs)
            else:
                try:
                    self.cbar.update_bruteforce(self.lines[-1])
                except ArithmeticError:
                    pass            
            self.cbar.ax.set_ylabel(ylabel=self.cbarlabel, rotation=-90, va='bottom')
            self.cbar.formatter.set_powerlimits((0, 0))

            self.cbar.update_ticks()
            
            #self.cbar.update_normal(self.lines[-1])
            #self.cbar.draw_all() 
        
        self.__Graph.set_xlabel(GraphProperties['xLabel'])
        self.__Graph.set_ylabel(GraphProperties['yLabel'])
            
        if not GraphProperties['title'].strip() == "":
            self.__Graph.set_title(GraphProperties['title'], fontweight='bold')
        self.__Figure.tight_layout()


    def update(self, data, X=False, Map=False):
        
        self.X = X
        self.Map = Map
        
        self.checkData(data)
        self.data = data
        self.__update()

    def getAbsolute(self, data):
        temp = np.absolute(data)
        return temp



    def __update(self):
        self.lines = []
        if self.PlotType == 'Y':
            self.lines.append(None)
            data = self.getAbsolute(self.data)
            if self.yscale == 'log' and self.xscale == 'log':
                self.lines[0], = self.__Graph.loglog(data)
            elif self.yscale == 'log':
                self.lines[0], = self.__Graph.semilogy(data)
            elif self.xscale == 'log':
                self.lines[0], = self.__Graph.semilogx(data)
            else:
                self.lines[0], = self.__Graph.plot(data)

        elif self.PlotType == 'XY':
            
            # data in 3D array 
            if len(np.shape(self.data)) == 3:
                for n in range(np.shape(self.data)[0]):
                    #print("data", self.data[n][0], self.data[n][1])
                    self.lines.append(None)
                    if self.yscale == 'log' and self.xscale == 'log':
                        data1 = self.getAbsolute(self.data[n][0])
                        data2 = self.getAbsolute(self.data[n][1])
                        self.lines[n], = self.__Graph.loglog(data1, data2)
                    elif self.yscale == 'log':
                        data = self.getAbsolute(self.data[n][0])
                        self.lines[n], = self.__Graph.semilogy(self.data[n][2], data)
                    elif self.xscale == 'log':
                        data = self.getAbsolute(self.data[n][0])
                        self.lines[n], = self.__Graph.semilogx(data, self.data[n][1])
                    else:
                        self.lines[n], = self.__Graph.plot(self.data[n][0], self.data[n][1])

                if self.data[0][0][-1] < 0.1 and self.xscale=='lin':
                    self.__Graph.ticklabel_format(style='sci', axis='x', scilimits=(-1,1))
           
            # data in 2D array
            else: 
                plotNum = np.shape(self.data)[0]-1 
                for n in range(plotNum):
                    self.lines.append(None)
                    if self.yscale == 'log' and self.xscale == 'log':
                        data1 = self.getAbsolute(self.data[0])
                        data2 = self.getAbsolute(self.data[n+1])
                        self.lines[n], = self.__Graph.loglog(data1, data2)
                    elif self.yscale == 'log':
                        data = self.getAbsolute(self.data[n+1])
                        self.lines[n], = self.__Graph.semilogy(self.data[0], data)
                    elif self.xscale == 'log':
                        data = self.getAbsolute(self.data[0])
                        self.lines[n], = self.__Graph.semilogx(data, self.data[n+1])
                    else:
                        self.lines[n], = self.__Graph.plot(self.data[0], self.data[n+1])
                if self.data[0][-1] < 0.1 and self.xscale=='lin':
                    self.__Graph.ticklabel_format(style='sci', axis='x', scilimits=(-1,1))

        elif self.PlotType == 'YY':
            for n in range(len(self.data)):
                self.lines.append(None)
                if self.yscale == 'log' and self.xscale == 'log':
                    data = self.getAbsolute(self.data[n])
                    self.lines[n], = self.__Graph.loglog(data)
                elif self.yscale == 'log':
                    data = self.getAbsolute(self.data[n])
                    self.lines[n], = self.__Graph.semilogy(data)
                elif self.xscale == 'log':
                    self.lines[n], = self.__Graph.semilogx(self.data[n])
                else:
                    self.lines[n], = self.__Graph.plot(self.data[n])
            try:
                size = len(self.data[0])
            except:
                size = self.data[0].size

            if size > 99 and self.xscale=='lin':
                self.__Graph.ticklabel_format(style='sci', axis='x', scilimits=(-1,1))

        elif self.PlotType == 'Map':
            data = std.equalizeArray(self.data)
            data = np.array(data, np.longdouble)
            self.lines.append(None)
            self.lines[-1] = self.__Graph.imshow(data, aspect='auto')


        if self.PlotType != 'Map':
            for n in range(len(self.lines)):
                if self.color[n] != None:
                    self.lines[n].set_color(self.color[n])
                if self.linestyle[n] in mks.MarkerStyle.markers.keys():
                    if self.linewidth[n] != None:
                        self.lines[n].set_markersize(self.linewidth[n])
                    if self.linestyle[n] != None:
                        self.lines[n].set_marker(self.linestyle[n])
                else:
                    if self.linewidth[n] != None:
                        self.lines[n].set_linewidth(self.linewidth[n])
                    if self.linestyle != None:
                        self.lines[n].set_linestyle(self.linestyle[n])

    def extend(self, newData):

        if not isinstance(newData, list):
            raise ValueError("Added data must be a one or more dimensional list of int/float.")
        if isinstance(self.data[0], list):
            for x in range(len(newData)):
                if not isinstance(x, list):
                    raise ValueError("Added data must have the same dimension as data.")
            if not len(newData) == len(self.data):
                raise ValueError("Added data must have the same dimension as data.")

        if isinstance(self.data[0], list):
            for n in range(len(self.data)):
                self.data[n].extend(newData[n])
        else:
            self.data.extend(newData)
        
        self.__update()

    def getFigure(self):
        return self.__Figure