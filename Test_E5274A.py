import pyvisa as vs 
import Agilent as ag 
import matplotlib.pyplot as plt

rm = vs.ResourceManager()

print(rm.list_resources())
mf = ag.E5274A(rm, "GPIB0::16::INSTR", reset = False)

""" #Staircase sweep test
Chns = [1,2]
VorI = [True, True]
MChn = 1
MVstart = 0.1
MVstop = 1.1
MVstep = 21
MIstart = 1e-3
MIstop = 10e-3
MIstep = 21
hold = 0
delay = 0
VVal = [1,0]
IVal = [0,0]
IComp = [100e-3,100e-3]
VComp = [100,100]

res = mf.StaircaseSweepMeasurement(Chns, VorI, MChn, MVstart, MVstop, MVstep, MIstart, MIstop, MIstep,
                                    hold, delay, VVal, IVal, IComp, VComp)
#print(res['Data'][1])
#plt.plot(res['Data'][2], res['Data'][0])
#plt.show()
"""

 #Spot measurement test
Chns = [1,2]
VorI = [True,True]
VVal = [1,0]
IVal = [0,0]
VComp = [100,100]
IComp = [100e-3,100e-3]
RV = [0,0]
RI = [0,0]

spotres = mf.SpotMeasurement(Chns, VorI, VVal, IVal, VComp, IComp, RV, RI)

print(spotres)


""" High Speed Spot Measurement Test
Chns = [1,2]
VorI = [True,True]
Val = [0,0]
VM = [True,True]
IM = [False,False]
Compl = [1e-3,1e-3]

Hspotres = mf.HighSpeedSpotMeasurement(Chns, VorI, Val, VM, IM, Compl)

print(Hspotres)
"""

""" Pulsed Spot Measurement Test

Chns = [1,2]
#Chns = [1]
PChn = 1
VPbase = 0.2
VPpulse = 1.0
IPbase = 1e-3
IPpulse = 10e-3
IComp = [100e-3,100e-3]
#IComp = [100e-3]
VComp = [100,100]
#VComp = [100]
VorI = [True,True]
#VorI = [True]
VVal = [0.6,0.0]
#VVal = [0.5]
IVal = [0,0]
#IVal = [0]
hold = 0.5
width = 0.5
period = 1.0
delay = 0.2
RV = [0,0]
#RV = [0]
RI = [0,0]
#RI = [0]



PSMres = mf.PulsedSpotMeasurement(Chns, PChn, VPbase, VPpulse, IPbase, IPpulse, VorI, RV, RI, VVal, IVal, IComp, VComp, hold, width, period, delay)

"""

"""

Chns = [1,2]
PChn = 1
VPbase = 0.1
VPpulse = 0.2
VPulseStop = 1.1
IPbase = 1e-3
IPpulse = 10e-3
IPulseStop = 100e-3
PStep = 10
IComp = [100e-3,100e-3]
VComp = [100,100]
VorI = [True,True]
VVal = [1,0]
IVal = [0,0]
hold = 0.025
width = 0.05
period = 0.1
delay = 0.025
RV = [0,0]
RI = [0,0]
SWMode = 1

PSWMres = mf.PulsedSweepMeasurement(Chns, PChn, VPbase, VPpulse, VPulseStop, IPbase, IPpulse, IPulseStop, 
                                PStep, SWMode, VorI, RV, RI, VVal, IVal, IComp, VComp, hold, width, 
                                period, delay, AA=None, BVal=None, FL=None, SSR=None, CMM=None, PCompl=None,
                                complPolarity=None, AApost=None,SChn=None, Sstart=None, Sstop=None)

"""

""" Multi Channel Sweep Measurement (Fix WNX setup...)

Chns = [1,2]
MChn = 1
MVstart = 0.1
MVstop = 1.1
MVstep = 21
MIstart = 1e-3
MIstop = 10e-3
MIstep = 21
IComp = [100e-3,100e-3]
VComp = [100.0,100.0]
VorI = [True,True]
VVal = [0.2,0.1]
IVal = [0,0]
hold = 0.025
width = 0.05
period = 0.1
delay = 0.025
RV = [0,0]
RI = [0,0]
SWMode = 1
Mmode = 1

MCSMres = mf.MultiChannelSweepMeasurement(Chns, VorI, MChn, MVstart, MVstop, MVstep, MIstart, MIstop, MIstep,
                                    hold, delay, VVal, IVal, VComp, IComp, Mmode, RV, RI, MeasChns=None, 
                                    SChn=None, Sstart=None, Sstop=None, AA=None, AApost=None, Pcompl=None, 
                                    sdelay=None, tdelay=None, mdelay=None,  FL=None, 
                                    SSR=None, ADC=None, CMM=None, complPolarity=None)

"""

""" Staircase Sweep With Pulsed Bias Measurement

Chns = [1,2]
VorI = [True,True]
PBChn = 2
SSChn = 1
SynSChn = None
MVstart = 0.1
MVstop = 1.1
MVstep = 21
MIstart = 1e-3
MIstop = 10e-3
MIstep = 21
hold = 0.5
width = 0.2
period = 0.5
delay = 0.1
VVal = [0.2,0.0]
IVal = [0.0,0.0]
IComp = [100e-3,100e-3]
VComp = [100.0,100.0]
Mmode = 1
VPbase = 0.1
VPpulse = 0.2
IPbase = 1e-3
IPpulse = 10e-3
RV = [0,0]
RI = [0,0]
AA = 1
AApost = None


SSPBres = mf.StaircaseSweepWPulsedBiasMeasurement(Chns, VorI, PBChn, SSChn, SynSChn, MVstart, MVstop, MVstep, 
                                    MIstart, MIstop, MIstep, hold, width, period, delay, VVal, IVal, 
                                    VComp, IComp, Mmode, VPbase, VPpulse, IPbase, IPpulse, RV, RI, AA, AApost,
                                    MeasChns=None, SChn=None, Sstart=None, Sstop=None, Pcompl=None, 
                                    sdelay=None, tdelay=None, mdelay=None, FL=None, SSR=None, 
                                    ADC=None, CMM=None, complPolarity=None)

"""

""" Quasi Pulsed Spot Measurement

Chns = [1,2]
VorI = [True,True]
SourceChn = 1
MeasChn = 2
hold = 0.5
delay = 0.1
VVal = [0.2,0.0]
IVal = [0.0,0.0]
IComp = [100e-3,100e-3]
VComp = [100.0,100.0]
RV = [0,0]
RI = [0,0]
AA = 1
AApost = None
BDMmode = 0
BDMInterval = 0
BDVstart = 0.0
BDVstop = 100.0
BDIstart = 0.0
BDIstop = 1.0



QPSMres = mf.QuasiPulsedSpotMeasurement(Chns, VorI, SourceChn, MeasChn, hold, delay, VVal, IVal, 
                                    VComp, IComp, RV, RI, AA, AApost, 
                                    BDMmode, BDMInterval, BDVstart, BDVstop, BDIstart, BDIstop,
                                    MeasChns=None, SChn=None, Sstart=None, Sstop=None, Pcompl=None, 
                                    sdelay=None, tdelay=None, mdelay=None, FL=None, SSR=None, 
                                    ADC=None, CMM=None, complPolarity=None, SynSChn=None)

"""