import GraphicalInterface as GI 
import matplotlib as mpl
import numpy as np
import sys
import matplotlib.backends.tkagg as tkagg
from matplotlib.backends.backend_agg import FigureCanvasAgg


Mainfolder = 'C:/Users/KB511298/Documents/E-Test_Python'

WaferCharacteristics = {'NumOfXDevices':5,'NumOfYDevices':10, 'NumOfDies': 5, 'DieSizeX': 12, 'DieSizeY': 15, 'WaferSize':300, 'WaferID': 'WaferID'}
Int = GI.GraphicalInterface(400,300,"test",WaferCharacteristics,updateTime=1)

tk.mainloop()

threads = Int.getThreats()

for th in threads:
    th.join()

Int.close()