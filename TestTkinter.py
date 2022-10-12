import pyvisa as vs
import B1530A as WGFMU
import time as tm
import ctypes as ct

rm = vs.ResourceManager()

print("1")
inst = WGFMU.Agilent_B1530A("GPIB0::18::INSTR", online=True, )
print("2")

#print(inst.turnOnline())

inst.setOperationMode(202, 2002)
inst.setOperationMode(201, 2002)

print(tm.time())
m= 0

try:
    #print(inst.doSelfTest())
    print(inst.closeSession())
    print(inst.closeSession())
    inst.getChannelIDs()
except SystemError as e:
    print('caught',e)
'''

for n in range(100000000000):
    if m == 100:
        print(tm.time())
        m = 0
    m = m+1
    for chn in inst.getChannelIDs()['Channels']:

        inst.getChannelStatus(chn)

    inst.clearLibrary()

    inst.programRectangularPulse(201, 1e-5, 1e-5, 1e-5, 1e-5, 0.5, 0, count=1, measure=True, mPoints=1, mStartTime=0, mEndTime=4e-5, AddSequence=True, Name="Read")
    inst.programGroundChn(202, 4e-5, Vg=0, count=1, measure=True, mPoints=1, mStartTime=0, mEndTime=4e-5, AddSequence=True, Name="Ground")
    
    inst.synchronize()
    inst.executeMeasurement()


    

inst.turnOffline()
'''
rm.close()