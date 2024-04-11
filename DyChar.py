"""
Code for adjusting the parameters automatically after Set/Reset (Dynamic Charaterization - DyChar)
Maximilian Liehr and Jubin Hazra
"""

import numpy as np 
import pyvisa as vs 
import datetime as dt 
import types as tp
import time as tm


def DyChar(eChar, SMUs, Vdc, DCcompl, PulseChn, GroundChn, Vset, Vreset, delay, trise, tfall, twidth, tbase, MeasPoints, 
                    Specs, read=True, tread=10e-6, Vread=-0.2, initalRead=True):

    # PulseChn, GroundChn, Vform, delay, trise, tfall, twidth, tbase, MeasPoints,
    # Take 
    # Original format:
        #eChar.setDCVoltages(SMUs=[3], Vdc=[-0.5], DCcompl=[1e-3]) --- (Will stay the same)
        #eChar.PulseForming(201,202,4,1000e3,100e-3,100e-3,0,1000e-3,100, Vread=0.2) --- (Will stay the same)
            # May need to add variable to save output data to be used for inputs to new code ***
        #eChar.setDCVoltages(SMUs=[3], Vdc=[-0.1], DCcompl=[1e-3]) --- (First DC voltage set for 1st reset)
        #eChar.PulseReset(201,202,-1.7, 100e-3, 1000e-3, 1000e-3,0,100e-3,10000) --- (First reset, Initial param from testing)
            # May need to add variable to save output data to be used for inputs to new code ***
        # ********* Where the new code will start ********
        #eChar.PulseSet(201,202, 2.5, 1e-5, 100e-6, 100e-6, 0, 10e-6, 100)
        #eChar.PulseReset(201,202,-1.5, 100e-3, 10e-3, 10e-3,0,100e-3,100)
        #eChar.PulseSet(201,202, 2.5, 1e-5, 100e-6, 100e-6, 0, 10e-6, 100) etc.
    # 
    # Inputs for code:
        # Use setDCVoltages(SMUs=[3], Vdc=[-0.1], DCcompl=[1e-3]) as input (Vdc Will be adjusted throughout code)
        # Set original value for Vresetmax (-1.7V in this case) as variable that can be used for input to this def
            # Example eChar.PulseReset(201,202, Vresetmax, 100e-3, 1000e-3, 1000e-3,0,100e-3,10000)
        # StatOutValues used for HRS, LRS, ImaxReset, Vreset (for Set and Reset)
            # These are the outputs from froming and reset.
        # Initial times should be given the same as for Endurance and will adjust other parameters first before time.
    # Code:
        # Have 2 for loops running:
            # 1. Apply initial Vreset and adjust if 2nd for loop doesn't work.
            # 2. Run Reset/Set iteration for n times checking variables compared to Specs.
            # If nothing works return statement "failed" and do not run endurance. Move to next device.

        # For possible future work:
            # Run 3 Reset/Set iterations with initial cond. Taking the avg. of HRS, LRS, ImaxReset, V (Set/Reset)
            # Compare results with given Specs.
            # If results outside of specs:
                # 1. Adjust Vdc.
                    # Repeat until within specs or hit max/min Vdc allowed.
                    # If works return parameters and run Endurance. ***
                    # If not move to next adjustment parameter.
                # 2. Adjust Vresetmax/Vsetmax and repeat 1.
                    # Repeat until hit max/min of Vresetmax.
                # 3. Adjust time variables to large rise/fall specs and repeat 1 and 2.
                # 4. If nothing works return statement "failed" and do not run endurance. Move to next device.
    n = 0
    s = 10
    DontWork = 0
    Setret = []
    Resret = []
    change = 0
    setnum = 0
    for Vreset in range(-1, -2.1, -0.1):
        for n in range(0,s):

            # Reset Measurement
            eChar.updateTime()
            tfallread = tread * 0.1
            triseread = tread * 0.1

            tmstart = tbase/2 + tfallread
            tmend = tbase/2 + tfallread + tread
            duration = sum([tbase,tfallread,triseread,tread])
            
            eChar.wgfmu.clearLibrary()

            if read and initalRead:
                eChar.wgfmu.programRectangularPulse(PulseChn, tread, tfallread, triseread, tbase, Vread, 0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Read", WriteHeader=False)
                eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Ground", WriteHeader=False)
                paReadID = 1

            durationF = sum([trise,twidth,tfall,tbase])
            endTime = tbase/2+trise+tfall+twidth
            if twidth == 0: 
                eChar.wgfmu.programTriangularPulse(PulseChn, trise, tfall, tbase, Vreset, 0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Form")
                eChar.wgfmu.programGroundChn(GroundChn, durationF, Vg=0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Ground")
            else: 
                eChar.wgfmu.programRectangularPulse(PulseChn, twidth, trise, tfall, tbase, Vreset, 0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Form")
                eChar.wgfmu.programGroundChn(GroundChn, durationF, Vg=0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Ground")

            paItstart = 1

            if read and not initalRead:
                eChar.wgfmu.programRectangularPulse(PulseChn, tread, tfallread, triseread, tbase, Vread, 0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Read", WriteHeader=False)
                eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Ground", WriteHeader=False)
                paItstart = 1
                paReadID = 3

            if read and initalRead:
                eChar.wgfmu.addSequence(PulseChn, "Read_%d_%d" %(paReadID,PulseChn), 1)
                eChar.wgfmu.addSequence(GroundChn, "Ground_%d_%d" %(paReadID+1,GroundChn), 1)
                paItstart = 3

            eChar.wgfmu.addSequence(PulseChn, "Form_%d_%d" %(paItstart,PulseChn), 1)
            eChar.wgfmu.addSequence(GroundChn, "Ground_%d_%d" %(paItstart+1,GroundChn), 1)

            if read:
                eChar.wgfmu.addSequence(PulseChn, "Read_%d_%d" %(paReadID,PulseChn), 1)
                eChar.wgfmu.addSequence(GroundChn, "Ground_%d_%d" %(paReadID+1,GroundChn), 1)
            
            eChar.wgfmu.synchronize()
            
            Resret = eChar.wgfmu.executeMeasurement()

            # Compare Specs with output data.
            eChar.CompareSpecs(Setret, Resret, Specs)


            if change == 0:
                #eChar.Vreset = Vreset  # Change endurance and pulse IV Vreset to this variable
                #break   # saves Vreset and breaks out of def and then we will run Pulse IV and then Endurance

                 # Set Measurement
                eChar.localtime = tm.localtime()
                tfallread = tread * 0.1
                triseread = tread * 0.1

                tmstart = tbase/2 + tfallread
                tmend = tbase/2 + tfallread + tread
                duration = sum([tbase,tfallread,triseread,tread])
                
                eChar.wgfmu.clearLibrary()

                if read:
                    eChar.wgfmu.programRectangularPulse(PulseChn, tread, tfallread, triseread, tbase, Vread, 0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Read", WriteHeader=False)
                    eChar.wgfmu.programGroundChn(GroundChn, duration, Vg=0, measure=True, mPoints=1, mStartTime=tmstart, mEndTime=tmend, AddSequence=False, Name="Ground", WriteHeader=False)

                durationF = sum([trise,twidth,tfall,tbase])
                endTime = tbase/2+trise+tfall+twidth
                if twidth == 0: 
                    eChar.wgfmu.programTriangularPulse(PulseChn, trise, tfall, tbase, Vset, 0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Form")
                    eChar.wgfmu.programGroundChn(GroundChn, durationF, Vg=0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Ground")
                else: 
                    eChar.wgfmu.programRectangularPulse(PulseChn, twidth, trise, tfall, tbase, Vset, 0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Form")
                    eChar.wgfmu.programGroundChn(GroundChn, durationF, Vg=0, measure=True, mPoints=MeasPoints, mStartTime=tbase/2, mEndTime=endTime, AddSequence=False, Name="Ground")

                paItstart = 1

                if read and initalRead:
                    eChar.wgfmu.addSequence(PulseChn, "Read_1_%d" %(PulseChn), 1)
                    eChar.wgfmu.addSequence(GroundChn, "Ground_2_%d" %(GroundChn), 1)
                    paItstart = 3

                eChar.wgfmu.addSequence(PulseChn, "Form_%d_%d" %(paItstart,PulseChn), 1)
                eChar.wgfmu.addSequence(GroundChn, "Ground_%d_%d" %(paItstart+1,GroundChn), 1)

                if read:
                    eChar.wgfmu.addSequence(PulseChn, "Read_1_%d" %(PulseChn), 1)
                    eChar.wgfmu.addSequence(GroundChn, "Ground_2_%d" %(GroundChn), 1)
                
                eChar.wgfmu.synchronize()
                
                Setret = eChar.wgfmu.executeMeasurement()

                n = 0
                setnum = setnum + 1

                if setnum == 20:
                    eChar.Vreset = Vreset  # Change endurance and pulse IV Vreset to this variable
                    DontWork = 0
                    break   # saves Vreset and breaks out of def and then we will run Pulse IV and then Endurance
          
    DontWork = 1
    return DontWork 

# Needs to know which ret data represents LRS and HRS.***************************
def CompareSpecs(eChar, Setret, Resret, Specs):
    change = 0
    if Setret == []:
        if Resret['HRS'] > Specs[2] or Resret['HRS'] < Specs[3]:
            change = 1
    else:
        if Setret['LRS'] > Specs[0] or Setret['LRS'] < Specs[1]:
            change = 1

        if Resret['HRS'] > Specs[2] or Resret['HRS'] < Specs[3]:
            change = 1

    return change

    
