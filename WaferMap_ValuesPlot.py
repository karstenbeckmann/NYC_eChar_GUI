import PlottingRoutines as PR 
import numpy as np 
import matplotlib.pyplot as plt
import pathlib as pl

Folder = r'C:\Users\KB511298\Desktop\ILT_M1_1816BRSN001.011'
Filename = 'nRVT0p6x0p06_Ioff.csv'

file_to_open = pl.Path(Folder, Filename)
f = open(file_to_open)

SpecLow = float(0)
SpecHigh = float(12e-7)

#SpecLow = -0.0003
#SpecHigh = -0.0002


lines = f.readlines()
Graph = PR.WaferMapValues(Filename[:-4], SpecLow, SpecHigh, Folder, DieSizeX=12, DieSizeY=15, ValueName="", width=300, height=200, dpi=600)

Xcenter = 11
Ycenter = 13

X = []
Y = []
Value = []

start = False
for line in lines:

    entry = line.split(",")

    if start:
        X.append(int(entry[0].strip())-Xcenter)
        Y.append(int(entry[1].strip())-Ycenter)
        Value.append(float(entry[2].strip()))

    if entry[0].strip() == "X":
        start = True

f.close()

for n in range(len(X)):
    
    Graph.writeToData(X[n], Y[n], value=Value[n])

Graph.update()
Graph.SaveToFile(Filename)



