import PlottingRoutines as PR 
import numpy as np 
import matplotlib.pyplot as plt
import pathlib as pl

Folder = r'C:\Users\KB511298\Desktop\1833BRSN001_000'
Filename = '1833BRSN001_000_DieTested_20181001.csv'





Graph = PR.WaferMap(Folder, DieSizeX=12, DieSizeY=15, ValueName="", title="Measured Dies", width=300, height=200, dpi=600, initValue=None)

Xcenter = 11
Ycenter = 13

X = [-9,-7,-5,-3,-1,1,3,5,7,9,-1,0,1]
Y = [0,0,0,0,0,0,0,0,0,0,1,1,1]
Value = [1]*13

for n in range(len(X)):
    
    Graph.writeToData(X[n], Y[n], value=Value[n])

Graph.update()
Graph.SaveToFile(Filename)



