'''
This file contains ReRAM characterization definitions from Karsten Beckmann
kbeckmann@sunypoly.edu
'''

import time as tm
import StdDefinitions as std
import DataHandling as dh
import threading as th
import math as ma
import numpy as np
import queue as qu
import copy as cp



###########################################################################################################################

def AnalogRet_PG81110(eChar, PGPulseChn, OscPulseChn, OscGNDChn, ExpReadCurrent, Vset, Vreset, twidthSet, twidthReset, Vread, tread, duration, tseperation, Rgoal, MaxPulses, Repetition, RetentionFailure, PowerSplitter, WriteHeader=True):
    
    """
    Applies voltage pulses via the Agilent 81110A pulse generator and measures the pulse response via a LeCroy oscilloscope
    Both Devices must be available. RF setup is recommended for rise times below 50ns. 
    PGPulseChn:     Pulse Channel of 81110A, (1 or 2)
    OscPulseChn:    Oscilloscope Pulse Channel
    OscGNDChn:      Oscilloscope GND Channel
    Vset:           Set Voltage (V)
    Vreset:         Reset Voltage (V)
    twidthSet:      Set pulse width (s)
    twidthReset:    Reset pulse width (s)
    Vread:          Read Voltage (V)
    tread:          Read pulse width(V)
    duration:       retention duration (s)
    tseperation:    Retention seperation time (s)
    Rgoal:          Aimed resistance step per Set
    MaxPulses:      Maximum number of pulses per step until pulsing is stopped
    Repetition:     Number of Retention repetitions
    RetentionFailure: Failure in percentage from Rgoal
    PowerSplitter:  Is a power splitter in use? 
    WriteHeader: Enable/Disable writing the header into overlaying summary output files
    """

    #if a power splitter is used the input voltage gets divided by two to measure the voltage as well. 
    PS = PowerSplitter
    if PS:
        Vset = 2*Vset
        Vreset = 2*Vreset
        Vread = 2*Vread

    settrise = 0.8e-9
    #settrise = 2e-9
    NumOfPul = int(duration/tseperation)
    VertScale = max([Vset,Vreset,Vread])*3
    VertScale2 = 50*ExpReadCurrent/2
    HorScale = tread/2
    TriggerLevel = 0.25*Vread
    ArmLevel = 0.7
    ExtInpImpedance = 10000
    OscInpImpedance = 50
    OscPulChn = OscPulseChn
    timeout = 2
    refresh = 1e-1
    period = 100*tread
    CycStart = eChar.curCycle
    
    
    Oscilloscope = eChar.getPrimaryLeCroyOscilloscope()
    PulseGen = eChar.PG81110A

    OscName = Oscilloscope.getModel()
    PGName = PulseGen.getModel()

    OscPulAcInput = OscPulChn.strip()[1]
    OscGNDAcInput = OscGNDChn.strip()[1]
    OscPulChn = int(OscPulChn.strip()[0])
    OscGNDChn = int(OscGNDChn.strip()[0])

    Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "View", 1)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale2)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "Coupling", "DC50")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "EnhanceResType", "3bits")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "ActiveInput", "Input%s" %(OscGNDAcInput))

    Oscilloscope.writeAcquisitionChn(OscPulChn, "ClearSweeps")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "View", 1)
    Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)
    Oscilloscope.writeAcquisitionChn(OscPulChn, "Coupling", "DC50")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "EnhanceResType", "3bits")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "ActiveInput", "Input%s" %(OscPulAcInput))

    Oscilloscope.writeAcquisitionHoriz("HorScale", HorScale)
    Oscilloscope.writeAcquisitionHoriz("MaxSamples", 250000)

    Oscilloscope.writeAcquisitionAuxOut("Amplitude", 2)
    Oscilloscope.writeAcquisitionAuxOut("AuxMode", "TriggerEnabled")

    TrigChn = OscPulChn
    Oscilloscope.writeAcquisitionTrigger("Edge.Source", "C%d" %(TrigChn))
    if Vread > 0: 
        Oscilloscope.writeAcquisitionTrigger("Edge.Slope", "Positive")
    else:
        Oscilloscope.writeAcquisitionTrigger("Edge.Slope", "Negative")   

    Oscilloscope.writeAcquisitionTrigger("C%dLevel" %(TrigChn), TriggerLevel)

    # set measurements 
    Oscilloscope.clearAllMeasurements()
    Oscilloscope.clearAllMeasurementSweeps()
    Oscilloscope.setMeasurement(1, "Amplitude", OscPulChn)
    Oscilloscope.setMeasurement(2, "Amplitude", OscGNDChn)

    PulseGen.reset()
    PulseGen.disableDigitalPatternMode()
    PulseGen.setTriggeredPulses(arming="external")
    PulseGen.setLevelArm()
    PulseGen.setArmLevel(ArmLevel)
    PulseGen.setTriggerCount(1)
    PulseGen.setPulsePeriod(period, PGPulseChn)
    PulseGen.setExtInputImpedance(ExtInpImpedance)
    PulseGen.setTransistionTimeOfLeadingEdge(settrise, PGPulseChn)
    PulseGen.setPulseDelay(0, PGPulseChn)
    PulseGen.turnDisplayOn()

    Rret = []
    Cret = []
    tret = []
    Rretdev = []
    Pretdev = []
    Rretgoal = []

    Rreset = []
    nReset = []
    Creset = []
    Rresgoal = []
    Rresetdev = []
    Presetdev = []

    Rcompl = []
    Ccompl = []
    RgoalCompl = []
    RdeltaCompl = []
    PercDelCompl = []

    stop = False
    RunRep = 0


    for n in range(Repetition):

        Rreset.append([])
        Creset.append([])
        nReset.append([])
        Rresgoal.append([])
        Rresetdev.append([])
        Presetdev.append([])

        Rcompl.append([])
        Ccompl.append([])
        RgoalCompl.append([])
        RdeltaCompl.append([])
        PercDelCompl.append([])

        if Vread < 0:
            PulseGen.invertedOutputPolarity(PGPulseChn)
            posV = 0
            negV = Vread
        else:
            PulseGen.normalOutputPolarity(PGPulseChn)
            posV = Vread
            negV = 0

        PulseGen.setVoltageHigh(posV, PGPulseChn) 
        PulseGen.setVoltageLow(negV, PGPulseChn)
        Vprev = Vread
        PulseGen.setPulseWidth(tread)
        Oscilloscope.writeAcquisitionTrigger("C%dLevel" %(TrigChn), TriggerLevel)
        VertScale = abs(Vread/4)
        Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)

        Oscilloscope.writeAcquisition("TriggerMode", "Stop")
        PulseGen.turnOnOutput(PGPulseChn)
        if not PS:
            PulseGen.turnDifferentialOutputOn(PGPulseChn)

        Oscilloscope.writeAcquisition("TriggerMode", "Single")

        tstart = tm.time()
        while True:
            tm.sleep(refresh)
            try: 
                TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
            except:
                TrigMode = "" 
            if TrigMode.strip() == "Stopped" or tm.time()>tstart+timeout:
                break
        PulseGen.turnOffOutput(PGPulseChn)
        if not PS:
            PulseGen.turnDifferentialOutputOff(PGPulseChn)
        
        #V = Oscilloscope.queryDataArray(OscPulChn)
        #I = np.divide(Oscilloscope.queryDataArray(OscGNDChn),OscInpImpedance)

        if PS:
            V = float(Oscilloscope.getMeasurementResults(1))
        else:
            V = Vread
        I = float(Oscilloscope.getMeasurementResults(2))/50

        R = abs(V/I)
        Trac = [[1/R]]  
        eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change", "ValueName": 'C'})
        Trac = [[R]]
        eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change", "ValueName": 'R'})
        
        C = 1/R
        Pdev = (abs(R-Rgoal)/Rgoal)
        Rdev = (abs(R-Rgoal))
        print("rR", R, " goal ", Rgoal)
        '''
        Rreset[-1].append(R)
        nReset[-1].append(0)
        Creset[-1].append(C)
        Rgoal[-1].append(Rgoal)
        Rresetdev[-1].append(Rdev)
        Presetdev[-1].append(Pdev)
        '''

        Rcompl[-1].append(R)
        Ccompl[-1].append(1/R)
        RgoalCompl[-1].append(Rgoal)
        RdeltaCompl[-1].append(Rdev)
        PercDelCompl[-1].append(Pdev)

        # set operation
        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
        if stop:    
            eChar.finished.put(True)
            break

        k = 0

        if Vset > 0 and Vprev > 0:
            PulseGen.setVoltageHigh(Vset, chn=PGPulseChn) 
        elif Vset < 0 and Vprev < 0:
            PulseGen.setVoltageLow(Vset, chn=PGPulseChn)
        elif Vset > 0:
            PulseGen.normalOutputPolarity(chn=PGPulseChn)
            PulseGen.setVoltageHigh(Vset, chn=PGPulseChn) 
            PulseGen.setVoltageLow(0, chn=PGPulseChn)
            PulseGen.setVoltageHigh(Vset, chn=PGPulseChn) 
            PulseGen.setVoltageLow(0, chn=PGPulseChn)
        else:
            PulseGen.invertedOutputPolarity(chn=PGPulseChn)
            PulseGen.setVoltageLow(Vset, chn=PGPulseChn)
            PulseGen.setVoltageHigh(0, chn=PGPulseChn) 
            PulseGen.setVoltageLow(Vset, chn=PGPulseChn)
            PulseGen.setVoltageHigh(0, chn=PGPulseChn)

        Vprev = Vset
        PulseGen.setPulseWidth(twidthSet)

        PulseGen.turnOnOutput(chn=PGPulseChn)
        if not PS:
            PulseGen.turnDifferentialOutputOn(PGPulseChn)
        Oscilloscope.writeAcquisition("TriggerMode", "Single") 

        tstart = tm.time()
        while True:
            try: 
                TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
            except AttributeError:
                TrigMode = "" 
            if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                break

        PulseGen.turnOffOutput(chn=PGPulseChn)
        if not PS:
            PulseGen.turnDifferentialOutputOff(PGPulseChn)
        Oscilloscope.writeAcquisition("TriggerMode", "Stop")
        
        if Vread > 0 and Vprev > 0:
            PulseGen.setVoltageHigh(Vread, chn=PGPulseChn) 
        elif Vread < 0 and Vprev < 0:
            PulseGen.setVoltageLow(Vread, chn=PGPulseChn)
        elif Vread > 0:
            PulseGen.normalOutputPolarity(chn=PGPulseChn)
            PulseGen.setVoltageHigh(Vread, chn=PGPulseChn) 
            PulseGen.setVoltageLow(0, chn=PGPulseChn)
            PulseGen.setVoltageHigh(Vread, chn=PGPulseChn) 
            PulseGen.setVoltageLow(0, chn=PGPulseChn)
        else:
            PulseGen.invertedOutputPolarity(chn=PGPulseChn)
            PulseGen.setVoltageLow(Vread, chn=PGPulseChn)
            PulseGen.setVoltageHigh(0, chn=PGPulseChn) 
            PulseGen.setVoltageLow(Vread, chn=PGPulseChn)
            PulseGen.setVoltageHigh(0, chn=PGPulseChn) 
        
        Vprev = Vread
        PulseGen.setPulseWidth(tread)
        
        Oscilloscope.writeAcquisitionTrigger("C%dLevel" %(TrigChn), TriggerLevel)
        Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)

        PulseGen.turnOnOutput(chn=PGPulseChn)
        if not PS:
            PulseGen.turnDifferentialOutputOn(PGPulseChn)
        Oscilloscope.writeAcquisition("TriggerMode", "Single")

        tstart = tm.time()
        while True:
            try: 
                TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
            except AttributeError:
                TrigMode = "" 
            if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                break

        PulseGen.turnOffOutput(chn=PGPulseChn)
        if not PS:
            PulseGen.turnDifferentialOutputOff(PGPulseChn)
        
        if PS:
            V = float(Oscilloscope.getMeasurementResults(1))
        else:
            V = Vread
        I = float(Oscilloscope.getMeasurementResults(2))/50

        R = abs(V/I)
        
        C = 1/R
        Pdev = (abs(R-Rgoal)/Rgoal)
        Rdev = (abs(R-Rgoal))
        print("rR", R, " goal ", Rgoal)

        Rreset[-1].append(R)
        Creset[-1].append(C)
        nReset[-1].append(0)
        Rresgoal[-1].append(Rgoal)
        Rresetdev[-1].append(Rdev)
        Presetdev[-1].append(Pdev)

        Rcompl[-1].append(R)
        Ccompl[-1].append(1/R)
        RgoalCompl[-1].append(Rgoal)
        RdeltaCompl[-1].append(Rdev)
        PercDelCompl[-1].append(Pdev)
        
        Trac = [[1/R]]  
        eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change", "ValueName": 'C'})
        Trac = [[R]]
        eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change", "ValueName": 'R'})
        

        r = 1
        while r <= MaxPulses:
            
            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
            if stop:    
                eChar.finished.put(True)
                break

            if R > Rgoal: 
                break

            print("r", r)

            ####### Reset
            if Vreset > 0 and Vprev > 0:
                PulseGen.setVoltageHigh(Vreset, chn=PGPulseChn) 
            elif Vreset < 0 and Vprev < 0:
                PulseGen.setVoltageLow(Vreset, chn=PGPulseChn)
            elif Vreset > 0:
                PulseGen.normalOutputPolarity(chn=PGPulseChn)
                PulseGen.setVoltageHigh(Vreset, chn=PGPulseChn) 
                PulseGen.setVoltageLow(0, chn=PGPulseChn)
                PulseGen.setVoltageHigh(Vreset, chn=PGPulseChn)
                PulseGen.setVoltageLow(0, chn=PGPulseChn)
            else:
                PulseGen.invertedOutputPolarity(chn=PGPulseChn)
                PulseGen.setVoltageLow(Vreset, chn=PGPulseChn)
                PulseGen.setVoltageHigh(0, chn=PGPulseChn) 
                PulseGen.setVoltageLow(Vreset, chn=PGPulseChn)
                PulseGen.setVoltageHigh(0, chn=PGPulseChn)
            
            #posV = 0
            #negV = Vreset
            
            Vprev = Vreset
            PulseGen.setPulseWidth(twidthReset)
            #tm.sleep(0.1)
            PulseGen.turnOnOutput(chn=PGPulseChn)
            if not PS:
                PulseGen.turnDifferentialOutputOn(PGPulseChn)
            #tm.sleep(1e-2)
            Oscilloscope.writeAcquisition("TriggerMode", "Single") 
            tstart = tm.time()
            while True:
                try: 
                    TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                except AttributeError:
                    TrigMode = "" 
                if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                    break
                tm.sleep(refresh)
            PulseGen.turnOffOutput(chn=PGPulseChn)
            if not PS:
                PulseGen.turnDifferentialOutputOff(PGPulseChn)

            Oscilloscope.writeAcquisition("TriggerMode", "Stop")
            
            if Vread > 0 and Vprev > 0:
                PulseGen.setVoltageHigh(Vread, chn=PGPulseChn) 
            elif Vread < 0 and Vprev < 0:
                PulseGen.setVoltageLow(Vread, chn=PGPulseChn)
            elif Vread > 0:
                PulseGen.setVoltageHigh(Vread, chn=PGPulseChn) 
                PulseGen.setVoltageLow(0, chn=PGPulseChn)
                PulseGen.setVoltageHigh(Vread, chn=PGPulseChn) 
                PulseGen.setVoltageLow(0, chn=PGPulseChn)
                PulseGen.normalOutputPolarity(chn=PGPulseChn)
            else:
                PulseGen.setVoltageLow(Vread, chn=PGPulseChn)
                PulseGen.setVoltageHigh(0, chn=PGPulseChn) 
                PulseGen.setVoltageLow(Vread, chn=PGPulseChn)
                PulseGen.setVoltageHigh(0, chn=PGPulseChn) 
                PulseGen.invertedOutputPolarity(chn=PGPulseChn)

            Vprev = Vread
            PulseGen.setPulseWidth(tread)
            
            Oscilloscope.writeAcquisitionTrigger("C%dLevel" %(TrigChn), TriggerLevel)
            Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)

            PulseGen.turnOnOutput(chn=PGPulseChn)
            if not PS:
                PulseGen.turnDifferentialOutputOn(PGPulseChn)
                
            Oscilloscope.writeAcquisition("TriggerMode", "Single")

            tstart = tm.time()
            while True:
                try: 
                    TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                except AttributeError:
                    TrigMode = "" 
                if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                    break
            PulseGen.turnOffOutput(chn=PGPulseChn)
            if not PS:
                PulseGen.turnDifferentialOutputOff(PGPulseChn)
            
            if PS:
                V = float(Oscilloscope.getMeasurementResults(1))
            else:
                V = Vread
            I = float(Oscilloscope.getMeasurementResults(2))/50

            R = abs(V/I)
            C = 1/R
            Pdev = (abs(R-Rgoal)/Rgoal)
            Rdev = (abs(R-Rgoal))
            print("rR", R, " goal ", Rgoal)

            Rreset[-1].append(R)
            Creset[-1].append(C)
            nReset[-1].append(r)
            Rresgoal[-1].append(Rgoal)
            Rresetdev[-1].append(Rdev)
            Presetdev[-1].append(Pdev)

            Rcompl[-1].append(R)
            Ccompl[-1].append(1/R)
            RgoalCompl[-1].append(Rgoal)
            RdeltaCompl[-1].append(Rdev)
            PercDelCompl[-1].append(Pdev)

            Trac = [[1/R]]  
            eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change", "ValueName": 'C'})
            Trac = [[R]]
            eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change", "ValueName": 'R'})
            r = r+1
        

        Rret.append([])
        Cret.append([])
        tret.append([])
        Rretgoal.append([])
        Rretdev.append([])
        Pretdev.append([])

        tmstart = tm.time()
        for ret in range(NumOfPul):
            
            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
            if stop:    
                eChar.finished.put(True)
                break

            tloop = tm.time()

            PulseGen.turnOnOutput(chn=PGPulseChn)
            if not PS:
                PulseGen.turnDifferentialOutputOn(PGPulseChn)
                
            Oscilloscope.writeAcquisition("TriggerMode", "Single")

            tstart = tm.time()
            while True:
                try: 
                    TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                except AttributeError:
                    TrigMode = "" 
                if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                    break
            PulseGen.turnOffOutput(chn=PGPulseChn)
            if not PS:
                PulseGen.turnDifferentialOutputOff(PGPulseChn)
            
            if PS:
                V = float(Oscilloscope.getMeasurementResults(1))
            else:
                V = Vread
            I = float(Oscilloscope.getMeasurementResults(2))/50

            R = abs(V/I)
            C = 1/R
            t = tm.time()-tmstart
            Pdev = (abs(R-Rgoal)/Rgoal)
            Rdev = (abs(R-Rgoal))
            print("retR", R, " goal ", Rgoal)

            Rret[-1].append(R)
            Cret[-1].append(C)
            tret[-1].append(t)
            Rretgoal[-1].append(Rreset[-1][-1])
            Rretdev[-1].append(Rdev)
            Pretdev[-1].append(Pdev)

            Rcompl[-1].append(R)
            Ccompl[-1].append(1/R)
            RgoalCompl[-1].append(Rgoal)
            RdeltaCompl[-1].append(Rdev)
            PercDelCompl[-1].append(Pdev)

            Trac = [[1/R]]  
            eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})
            Trac = [[R]]
            eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
            r = r+1
            while True:

                if tloop+tseperation < tm.time():
                    break
                
                tm.sleep(0.01)
        
        eChar.curCycle = eChar.curCycle + 1

        RunRep = RunRep + 1
            
    PulseGen.turnOffOutput(chn=PGPulseChn)
    if not PS:
        PulseGen.turnDifferentialOutputOff(PGPulseChn)

    ################################################################

    if not WriteHeader:
        header = eChar.getHeader("Combined")
    else:
        header = []    
    header.append("Instrument,Oscilloscope,%s" %(OscName.strip()))
    header.append("Instrument,PulseGenerator,%s" %(PGName.strip()))
    header.append("Measurement,PGPulseChannel, %s" %(PGPulseChn))
    header.append("Measurement,OscPulseChn, %s" %(OscPulseChn))
    header.append("Measurement,OscGNDChn, %s" %(OscGNDChn))
    header.append("Measurement,Vset, %.2e" %(Vset))
    header.append("Measurement,Set Pulse Width, %.2e" %(twidthSet))
    header.append("measurement,Set Resistance Step, %.2f" %( twidthReset))
    header.append("Measurement,Vreset, %.2e" %(Vreset))
    header.append("Measurement,Reset Pulse Width, %.2e" %(twidthReset))
    header.append("Measurement,Vread, %.2e" %(Vread))
    header.append("Measurement,Read Pulse Width, %.2e" %(tread))
    header.append("Measurement,Read Time Seperation, %.2e" %(tseperation))
    header.append("Measurement,Rgoal, %s" %(Rgoal))
    header.append("Measurement,MaxPulses, %s" %(MaxPulses))
    header.append("Measurement,Repetition, %s" %(Repetition))
    header.append("Measurement,PowerSplitter, %s" %(PS))

    if WriteHeader:
        header.writeHeader("Combined",header)

    newline = [None]*3
    newline[0] = 'DataName'
    newline[1] = 'Dimension'
    newline[2] = 'Repetition'
    OutputData = []
    
    nMax = 0
    
    for n in range(RunRep):
        try:
            newline[0] = '%s, Entry #, Reset Goal (ohm), Reset Resistance (ohm), Reset Dev. (value), Reset Dev. (perc), Reset Conductance (s)' %(newline[0])
            newline[1] = '%s, %d, %d, %d, %d, %d, %d' %(newline[1],len(nReset[n]),len(Rresgoal[n]), len(Rreset[n]), len(Rresetdev[n]), len(Presetdev[n]), len(Creset))
            newline[2] = '%s, %d, %d, %d, %d, %d, %d' %(newline[2],n+1,n+1,n+1,n+1,n+1,n+1)
            
            newline[0] = '%s, time , Retention Goal (ohm), Ret. Resistance (ohm), Ret. Dev. (value), Ret. Dev. (perc), Ret. Conductance (s)' %(newline[0])
            newline[1] = '%s, %d, %d, %d, %d, %d, %d' %(newline[1],len(tret[n]),len(Rretgoal[n]), len(Rret[n]), len(Rretdev[n]), len(Pretdev[n]), len(Cret))
            newline[2] = '%s, %d, %d, %d, %d, %d, %d' %(newline[2],n+1,n+1,n+1,n+1,n+1,n+1)

        except IndexError:
            None
            
        CurMax = max([len(Rreset[n]),len(Rret[n])])

        if CurMax > nMax:
            nMax = CurMax

    OutputData = []
    for n in range(nMax):
        data = 'DataValue'
        for k in range(RunRep):
            try:
                data = "%s, %f, %f, %f, %f, %f, %f" %(data, nReset[k][n], Rresgoal[k][n], Rreset[k][n], Rresetdev[k][n], Presetdev[k][n], Creset[k][n])
            except IndexError:
                data = "%s, , , , , , " %(data)
            try:
                data = "%s, %f, %f, %f, %f, %f, %f" %(data, tret[k][n], Rretgoal[k][n], Rret[k][n], Rretdev[k][n], Pretdev[k][n], Cret[k][n])
            except IndexError:
                data = "%s, , , , , , " %(data)

        OutputData.append(data)


    header1 = cp.deepcopy(header)
    header1.extend(newline)

    eChar.writeDataToFile(header, OutputData, startCyc=CycStart, endCyc=eChar.curCycle-1)
            
    nMax = 0
    for n in range(RunRep):
        
        try:
            newline[0] = '%s, Res. Goal (ohm), Resistance (ohm), Res. Dev. (value), Res. Dev. (perc), Res. Conductance (s)' %(newline[0])
            newline[1] = '%s, %d, %d, %d, %d, %d' %(newline[1],len(RgoalCompl[n]), len(Rcompl[n]), len(RdeltaCompl[n]), len(PercDelCompl[n]), len(Ccompl[n]))
            newline[2] = '%s, %d, %d, %d, %d, %d' %(newline[2],n+1,n+1,n+1,n+1,n+1)
        except IndexError:
            None
        CurMax = len(Rreset)

        if CurMax > nMax:
            nMax = CurMax

    OutputData = []
    for n in range(nMax):
        data = 'DataValue'
        for k in range(RunRep):
            try:
                data = "%s, %f, %f, %f, %f, %f" %(data, RgoalCompl[k][n], Rcompl[k][n], RdeltaCompl[k][n], PercDelCompl[k][n], Ccompl[k][n])
            except IndexError:
                data = "%s, , , , , " %(data)

        OutputData.append(data)
    
    header.extend(newline)
    Typ2 = "Compl_%s" %(eChar.getMeasurementType())
    eChar.writeDataToFile(header, OutputData, startCyc=CycStart, endCyc=eChar.curCycle-1, Typ=Typ2)

    AvgLRS =  eChar.dhValue([], 'FirstHRS', DoYield=False, Unit='ohm')
    AvgHRS =  eChar.dhValue([], 'FirstLRS', DoYield=False, Unit='ohm')
    AvgRret =  eChar.dhValue([], 'Rret', DoYield=False, Unit='ohm')
    Avgtfail =  eChar.dhValue([], 'tfail', DoYield=False, Unit='ohm')
    
    for n in range(RunRep-1):
        if len(Rreset) > n: 
            if len(Rreset[n]) > 0: 
                AvgLRS.extend(Rreset[n][0])
                AvgHRS.extend(Rreset[n][-1])
        try:
            tfail = tret[n][-1]
            for k in range(len(Rret[n])):
                if (1-RetentionFailure/100)*Rreset[n][-1] < Rret[n][k] > (1+RetentionFailure/100)*Rreset[n][-1]:
                    tfail = tret[n][k]
                    break
            Avgtfail.extend(tfail)
        except IndexError:
            None
        AvgRret.extend(Rret[n])

    row = eChar.dhAddRow([AvgLRS,AvgHRS,AvgRret, Avgtfail])


###########################################################################################################################

def AnalogRet_PGBNC765(eChar, PGPulseChn, OscPulseChn, OscGNDChn, ExpReadCurrent, Vset, Vreset, twidthSet, twidthReset, Vread, tread, duration, tseperation, Rgoal, MaxPulses, Repetition, RetentionFailure, PowerSplitter, WriteHeader=True):
    
    """
    Applies voltage pulses via the Agilent 81110A pulse generator and measures the pulse response via a LeCroy oscilloscope
    Both Devices must be available. RF setup is recommended for rise times below 50ns. 
    PGPulseChn:     Pulse Channel of BNC Model 765, (1 to 4)
    OscPulseChn:    Oscilloscope Pulse Channel
    OscGNDChn:      Oscilloscope GND Channel
    Vset:           Set Voltage (V)
    Vreset:         Reset Voltage (V)
    twidthSet:      Set pulse width (s)
    twidthReset:    Reset pulse width (s)
    Vread:          Read Voltage (V)
    tread:          Read pulse width(V)
    duration:       retention duration (s)
    tseperation:    Retention seperation time (s)
    Rgoal:          Aimed resistance step per Set
    MaxPulses:      Maximum number of pulses per step until pulsing is stopped
    Repetition:     Number of Retention repetitions
    RetentionFailure: Failure in percentage from Rgoal
    PowerSplitter:  Is a power splitter in use? 
    WriteHeader: Enable/Disable writing the header into overlaying summary output files
    """

    #if a power splitter is used the input voltage gets divided by two to measure the voltage as well. 
    PS = PowerSplitter
    if PS:
        Vset = 2*Vset
        Vreset = 2*Vreset
        Vread = 2*Vread

    NumOfPul = int(duration/tseperation)
    VertScale = max([Vset,Vreset,Vread])*3
    VertScale2 = 50*ExpReadCurrent/2
    HorScale = tread/2
    TriggerOutputLevel = 1.5
    TriggerLevel = TriggerOutputLevel/3
    OscInpImpedance = 50
    OscPulChn = OscPulseChn
    timeout = 2
    refresh = 1e-1
    period = 5*max(tread, twidthSet, twidthReset)
    CycStart = eChar.curCycle
        
    Oscilloscope = eChar.getPrimaryLeCroyOscilloscope()
    PulseGen = eChar.PGBNC765

    OscName = Oscilloscope.getModel()
    PGName = PulseGen.getModel()

    PulseGen.setTriggerOutputSource(PGPulseChn)
    PulseGen.setTriggerOutputDelay(0)
    PulseGen.setTriggerOutputPolarityPositive()
    PulseGen.setTriggerOutputAmplitude(TriggerOutputLevel)
    PulseGen.setTriggerModeSingle()
    PulseGen.setTriggerSourceExternal()

    OscPulAcInput = OscPulseChn.strip()[1]
    OscGNDAcInput = OscGNDChn.strip()[1]
    OscPulChn = int(OscPulseChn.strip()[0])
    OscGNDChn = int(OscGNDChn.strip()[0])

    Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "View", 1)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale2)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "Coupling", "DC50")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "EnhanceResType", "3bits")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "ActiveInput", "Input%s" %(OscGNDAcInput))

    Oscilloscope.writeAcquisitionChn(OscPulChn, "ClearSweeps")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "View", 1)
    Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)
    Oscilloscope.writeAcquisitionChn(OscPulChn, "Coupling", "DC50")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "EnhanceResType", "3bits")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "ActiveInput", "Input%s" %(OscPulAcInput))

    Oscilloscope.writeAcquisitionHoriz("HorScale", HorScale)
    Oscilloscope.writeAcquisitionHoriz("MaxSamples", 250000)

    Oscilloscope.writeAcquisitionAuxOut("Amplitude", 2)
    Oscilloscope.writeAcquisitionAuxOut("AuxMode", "TriggerEnabled")

    Oscilloscope.writeAcquisitionTrigger("Edge.Source", "EXT")
    Oscilloscope.writeAcquisitionTrigger("Edge.Slope", "Positive")

    Oscilloscope.writeAcquisitionTrigger("ExtLevel", TriggerLevel)

    # set measurements 
    Oscilloscope.clearAllMeasurements()
    Oscilloscope.clearAllMeasurementSweeps()
    Oscilloscope.setMeasurement(1, "Amplitude", OscPulChn)
    Oscilloscope.setMeasurement(2, "Amplitude", OscGNDChn)

    PulseGen.reset()
    PulseGen.clearTrigger()
    PulseGen.setTriggerSourceExternal()
    PulseGen.setTriggerThreshold(TriggerLevel)
    PulseGen.setPulseModeSingle(PGPulseChn)
    PulseGen.setPulsePeriod(period, PGPulseChn)
    PulseGen.setTriggerModeSingle()
    PulseGen.setTriggerImpedanceTo50ohm()
    PulseGen.enableOutput(PGPulseChn)
    PulseGen.arm()
    PulseGen.disableOutput(PGPulseChn)

    Rret = []
    Cret = []
    tret = []
    Rretdev = []
    Pretdev = []
    Rretgoal = []

    Rreset = []
    nReset = []
    Creset = []
    Rresgoal = []
    Rresetdev = []
    Presetdev = []

    Rcompl = []
    Ccompl = []
    RgoalCompl = []
    RdeltaCompl = []
    PercDelCompl = []

    stop = False
    RunRep = 0


    for n in range(Repetition):

        Rreset.append([])
        Creset.append([])
        nReset.append([])
        Rresgoal.append([])
        Rresetdev.append([])
        Presetdev.append([])

        Rcompl.append([])
        Ccompl.append([])
        RgoalCompl.append([])
        RdeltaCompl.append([])
        PercDelCompl.append([])

        PG_BNC_setPulseVoltage(PulseGen, PGPulseChn, Vread)
        PulseGen.setPulseWidth(tread)
        
        Oscilloscope.writeAcquisitionTrigger("ExtLevel", TriggerLevel)
        VertScale = abs(Vread/4)
        Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)

        Oscilloscope.writeAcquisition("TriggerMode", "Stop")
        PulseGen.enableOutput(PGPulseChn)

        Oscilloscope.writeAcquisition("TriggerMode", "Single")

        tstart = tm.time()
        while True:
            tm.sleep(refresh)
            try: 
                TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                print(TrigMode)
            except ValueError as e:
                print(e)
                TrigMode = "" 
            if TrigMode.strip() == "Stopped" or tm.time() > tstart+timeout:
                break
            
        PulseGen.disableOutput(PGPulseChn)
        
        #V = Oscilloscope.queryDataArray(OscPulChn)
        #I = np.divide(Oscilloscope.queryDataArray(OscGNDChn),OscInpImpedance)

        if PS:
            V = float(Oscilloscope.getMeasurementResults(1))
        else:
            V = Vread
        I = float(Oscilloscope.getMeasurementResults(2))/50

        R = abs(V/I)
        Trac = [[1/R]]  
        eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})
        Trac = [[R]]
        eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
        
        C = 1/R
        Pdev = (abs(R-Rgoal)/Rgoal)
        Rdev = (abs(R-Rgoal))
        print("rR", R, " goal ", Rgoal)
        '''
        Rreset[-1].append(R)
        nReset[-1].append(0)
        Creset[-1].append(C)
        Rgoal[-1].append(Rgoal)
        Rresetdev[-1].append(Rdev)
        Presetdev[-1].append(Pdev)
        '''

        Rcompl[-1].append(R)
        Ccompl[-1].append(1/R)
        RgoalCompl[-1].append(Rgoal)
        RdeltaCompl[-1].append(Rdev)
        PercDelCompl[-1].append(Pdev)

        # set operation
        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
        if stop:    
            eChar.finished.put(True)
            break

        k = 0

        PG_BNC_setPulseVoltage(PulseGen, PGPulseChn, Vset)
        PulseGen.setPulseWidth(twidthSet)
        PulseGen.disableTriggerOutput()

        PulseGen.enableOutput(PGPulseChn)

        Oscilloscope.writeAcquisition("TriggerMode", "Single") 

        tstart = tm.time()
        while True:
            try: 
                TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
            except AttributeError:
                TrigMode = "" 
            if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                break

        PulseGen.disableOutput(PGPulseChn)

        Oscilloscope.writeAcquisition("TriggerMode", "Stop")
        
        
        PulseGen.setPulseVoltage(Vread, PGPulseChn)
        PulseGen.setPulseWidth(tread, PGPulseChn)
        PulseGen.enableTriggerOutput()
        
        Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)

        PulseGen.enableOutput(PGPulseChn)
        Oscilloscope.writeAcquisition("TriggerMode", "Single")

        tstart = tm.time()
        while True:
            try: 
                TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
            except AttributeError:
                TrigMode = "" 
            if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                break

        PulseGen.disableOutput(PGPulseChn)
        
        if PS:
            V = float(Oscilloscope.getMeasurementResults(1))
        else:
            V = Vread
        I = float(Oscilloscope.getMeasurementResults(2))/50

        R = abs(V/I)
        
        C = 1/R
        Pdev = (abs(R-Rgoal)/Rgoal)
        Rdev = (abs(R-Rgoal))
        print("rR", R, " goal ", Rgoal)

        Rreset[-1].append(R)
        Creset[-1].append(C)
        nReset[-1].append(0)
        Rresgoal[-1].append(Rgoal)
        Rresetdev[-1].append(Rdev)
        Presetdev[-1].append(Pdev)

        Rcompl[-1].append(R)
        Ccompl[-1].append(1/R)
        RgoalCompl[-1].append(Rgoal)
        RdeltaCompl[-1].append(Rdev)
        PercDelCompl[-1].append(Pdev)
        
        Trac = [[1/R]]  
        eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})
        Trac = [[R]]
        eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
        

        r = 1
        while r <= MaxPulses:
            
            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
            if stop:    
                eChar.finished.put(True)
                break

            if R > Rgoal: 
                break

            print("r", r)

            ####### Reset
            

            PulseGen.setPulseVoltage(Vreset, PGPulseChn)
            PulseGen.setPulseWidth(twidthReset)
            PulseGen.disableTriggerOutput()
            #tm.sleep(0.1)
            
            PulseGen.enableOutput(PGPulseChn)
            #tm.sleep(1e-2)
            Oscilloscope.writeAcquisition("TriggerMode", "Single") 
            tstart = tm.time()
            while True:
                try: 
                    TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                except AttributeError:
                    TrigMode = "" 
                if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                    break
                tm.sleep(refresh)

            PulseGen.disableOutput(PGPulseChn)
            
            Oscilloscope.writeAcquisition("TriggerMode", "Stop")
            
            PulseGen.setPulseVoltage(Vread, PGPulseChn)
            PulseGen.setPulseWidth(tread, PGPulseChn)
            PulseGen.enableTriggerOutput()
            
            Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)

            PulseGen.enableOutput(PGPulseChn)
                
            Oscilloscope.writeAcquisition("TriggerMode", "Single")

            tstart = tm.time()
            while True:
                try: 
                    TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                except AttributeError:
                    TrigMode = "" 
                if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                    break
                
            PulseGen.disableOutput(PGPulseChn)
            
            if PS:
                V = float(Oscilloscope.getMeasurementResults(1))
            else:
                V = Vread
            I = float(Oscilloscope.getMeasurementResults(2))/50

            R = abs(V/I)
            C = 1/R
            Pdev = (abs(R-Rgoal)/Rgoal)
            Rdev = (abs(R-Rgoal))
            print("rR", R, " goal ", Rgoal)

            Rreset[-1].append(R)
            Creset[-1].append(C)
            nReset[-1].append(r)
            Rresgoal[-1].append(Rgoal)
            Rresetdev[-1].append(Rdev)
            Presetdev[-1].append(Pdev)

            Rcompl[-1].append(R)
            Ccompl[-1].append(1/R)
            RgoalCompl[-1].append(Rgoal)
            RdeltaCompl[-1].append(Rdev)
            PercDelCompl[-1].append(Pdev)

            Trac = [[1/R]]  
            eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})
            Trac = [[R]]
            eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
            r = r+1
        

        Rret.append([])
        Cret.append([])
        tret.append([])
        Rretgoal.append([])
        Rretdev.append([])
        Pretdev.append([])

        tmstart = tm.time()
        for ret in range(NumOfPul):
            
            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
            if stop:    
                eChar.finished.put(True)
                break

            tloop = tm.time()

            PulseGen.enableOutput(PGPulseChn)
            Oscilloscope.writeAcquisition("TriggerMode", "Single")

            tstart = tm.time()
            while True:
                try: 
                    TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                except AttributeError:
                    TrigMode = "" 
                if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                    break
            PulseGen.disableOutput(PGPulseChn)
            
            if PS:
                V = float(Oscilloscope.getMeasurementResults(1))
            else:
                V = Vread
            I = float(Oscilloscope.getMeasurementResults(2))/50

            R = abs(V/I)
            C = 1/R
            t = tm.time()-tmstart
            Pdev = (abs(R-Rgoal)/Rgoal)
            Rdev = (abs(R-Rgoal))
            print("retR", R, " goal ", Rgoal)

            Rret[-1].append(R)
            Cret[-1].append(C)
            tret[-1].append(t)
            Rretgoal[-1].append(Rreset[-1][-1])
            Rretdev[-1].append(Rdev)
            Pretdev[-1].append(Pdev)

            Rcompl[-1].append(R)
            Ccompl[-1].append(1/R)
            RgoalCompl[-1].append(Rgoal)
            RdeltaCompl[-1].append(Rdev)
            PercDelCompl[-1].append(Pdev)

            Trac = [[1/R]]  
            eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})
            Trac = [[R]]
            eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': '# of Pulses', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
            r = r+1
            while True:

                if tloop+tseperation < tm.time():
                    break
                
                tm.sleep(0.01)
        
        eChar.curCycle = eChar.curCycle + 1

        RunRep = RunRep + 1

        PulseGen.disableOutput(PGPulseChn)

        PulseGen.dearm()

    ################################################################################

    if not WriteHeader:
        header = eChar.getHeader("Combined")
    else:
        header = []

    header.append("Instrument,Oscilloscope,%s" %(OscName.strip()))
    header.append("Instrument,PulseGenerator,%s" %(PGName.strip()))
    header.append("Measurement,Device,%s" %(eChar.getDevice()))
    header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.getLocalTime())))
    header.append("Measurement,PGPulseChannel, %s" %(PGPulseChn))
    header.append("Measurement,OscPulseChn, %s" %(OscPulseChn))
    header.append("Measurement,OscGNDChn, %s" %(OscGNDChn))
    header.append("Measurement,Vset, %.2e" %(Vset))
    header.append("Measurement,Set Pulse Width, %.2e" %(twidthSet))
    header.append("measurement,Set Resistance Step, %.2f" %( twidthReset))
    header.append("Measurement,Vreset, %.2e" %(Vreset))
    header.append("Measurement,Reset Pulse Width, %.2e" %(twidthReset))
    header.append("Measurement,Vread, %.2e" %(Vread))
    header.append("Measurement,Read Pulse Width, %.2e" %(tread))
    header.append("Measurement,Read Time Seperation, %.2e" %(tseperation))
    header.append("Measurement,Rgoal, %s" %(Rgoal))
    header.append("Measurement,MaxPulses, %s" %(MaxPulses))
    header.append("Measurement,Repetition, %s" %(Repetition))
    header.append("Measurement,PowerSplitter, %s" %(PS))

    if WriteHeader:
        eChar.extendHeader("Combined", header)

    newline = [None]*3
    newline[0] = 'DataName'
    newline[1] = 'Dimension'
    newline[2] = 'Repetition'
    OutputData = []
    
    nMax = 0
    
    for n in range(RunRep):
        try:
            newline[0] = '%s, Entry #, Reset Goal (ohm), Reset Resistance (ohm), Reset Dev. (value), Reset Dev. (perc), Reset Conductance (s)' %(newline[0])
            newline[1] = '%s, %d, %d, %d, %d, %d, %d' %(newline[1],len(nReset[n]),len(Rresgoal[n]), len(Rreset[n]), len(Rresetdev[n]), len(Presetdev[n]), len(Creset))
            newline[2] = '%s, %d, %d, %d, %d, %d, %d' %(newline[2],n+1,n+1,n+1,n+1,n+1,n+1)
            
            newline[0] = '%s, time , Retention Goal (ohm), Ret. Resistance (ohm), Ret. Dev. (value), Ret. Dev. (perc), Ret. Conductance (s)' %(newline[0])
            newline[1] = '%s, %d, %d, %d, %d, %d, %d' %(newline[1],len(tret[n]),len(Rretgoal[n]), len(Rret[n]), len(Rretdev[n]), len(Pretdev[n]), len(Cret))
            newline[2] = '%s, %d, %d, %d, %d, %d, %d' %(newline[2],n+1,n+1,n+1,n+1,n+1,n+1)

        except IndexError:
            None
            
        CurMax = max([len(Rreset[n]),len(Rret[n])])

        if CurMax > nMax:
            nMax = CurMax

    OutputData = []
    for n in range(nMax):
        data = 'DataValue'
        for k in range(RunRep):
            try:
                data = "%s, %f, %f, %f, %f, %f, %f" %(data, nReset[k][n], Rresgoal[k][n], Rreset[k][n], Rresetdev[k][n], Presetdev[k][n], Creset[k][n])
            except IndexError:
                data = "%s, , , , , , " %(data)
            try:
                data = "%s, %f, %f, %f, %f, %f, %f" %(data, tret[k][n], Rretgoal[k][n], Rret[k][n], Rretdev[k][n], Pretdev[k][n], Cret[k][n])
            except IndexError:
                data = "%s, , , , , , " %(data)

        OutputData.append(data)


    header1 = cp.deepcopy(header)
    header1.extend(newline)

    eChar.writeDataToFile(header, OutputData, startCyc=CycStart, endCyc=eChar.curCycle-1)
            
    nMax = 0
    for n in range(RunRep):
        
        try:
            newline[0] = '%s, Res. Goal (ohm), Resistance (ohm), Res. Dev. (value), Res. Dev. (perc), Res. Conductance (s)' %(newline[0])
            newline[1] = '%s, %d, %d, %d, %d, %d' %(newline[1],len(RgoalCompl[n]), len(Rcompl[n]), len(RdeltaCompl[n]), len(PercDelCompl[n]), len(Ccompl[n]))
            newline[2] = '%s, %d, %d, %d, %d, %d' %(newline[2],n+1,n+1,n+1,n+1,n+1)
        except IndexError:
            None
        CurMax = len(Rreset)

        if CurMax > nMax:
            nMax = CurMax

    OutputData = []
    for n in range(nMax):
        data = 'DataValue'
        for k in range(RunRep):
            try:
                data = "%s, %f, %f, %f, %f, %f" %(data, RgoalCompl[k][n], Rcompl[k][n], RdeltaCompl[k][n], PercDelCompl[k][n], Ccompl[k][n])
            except IndexError:
                data = "%s, , , , , " %(data)

        OutputData.append(data)
    
    header.extend(newline)
    Typ2 = "Compl_%s" %(Typ)
    
    eChar.writeDataToFile(header, OutputData, Typ=Typ2, startCyc=CycStart, endCyc=eChar.curCycle-1)

    AvgLRS =  eChar.dhValue([], 'FirstHRS', DoYield=False, Unit='ohm')
    AvgHRS =  eChar.dhValue([], 'FirstLRS', DoYield=False, Unit='ohm')
    AvgRret =  eChar.dhValue([], 'Rret', DoYield=False, Unit='ohm')
    Avgtfail =  eChar.dhValue([], 'tfail', DoYield=False, Unit='ohm')
    
    for n in range(RunRep-1):
        if len(Rreset) > n: 
            if len(Rreset[n]) > 0: 
                AvgLRS.extend(Rreset[n][0])
                AvgHRS.extend(Rreset[n][-1])
        try:
            tfail = tret[n][-1]
            for k in range(len(Rret[n])):
                if (1-RetentionFailure/100)*Rreset[n][-1] < Rret[n][k] > (1+RetentionFailure/100)*Rreset[n][-1]:
                    tfail = tret[n][k]
                    break
            Avgtfail.extend(tfail)
        except IndexError:
            None
        AvgRret.extend(Rret[n])

    row = eChar.dhAddRow([AvgLRS,AvgHRS,AvgRret, Avgtfail])

    




###########################################################################################################################
def AnalogSwi_PG81110A(eChar, PGPulseChn, OscPulseChn, OscGNDChn, ExpReadCurrent, Vset, Vreset, twidthSet, twidthReset, Vread, tread, RstepSet, RstepReset, MaxResistance, MaxPulsesPerStepSet, MaxPulsesPerStepReset, Round, Repetition, PowerSplitter, WriteHeader=True):
        
    """
    Applies voltage pulses via the Agilent 81110A pulse generator and measures the pulse response via a LeCroy oscilloscope
    Both Devices must be available. RF setup is recommended for rise times below 50ns. 
    PGPulseChn:     Pulse Channel of 81110A, (1 or 2)
    OscPulseChn:    Oscilloscope Pulse Channel
    OscGNDChn:      Oscilloscope GND Channel
    Vset:           Set Voltage (V)
    Vreset:         Reset Voltage (V)
    settwidth:      Set pulse width (s)
    resettwidth:    Reset pulse width (s)
    Vread:          Read Voltage (V)
    tread:          Read pulse width(V)
    RstepSet:       Aimed resistance step per Set
    RstepReset:     Aimed resistance step per Reset
    MaxPulsesPerStepSet:    Maximum number of pulses per step until pulsing is stopped
    MaxPulsesPerStepReset:  Maximum number of pulses per step until pulsing is stopped
    Round           Round to next RstepSize
    Repetition:     Number of set/rest cycles
    PowerSplitter:  Is a power splitter in use? 
    WriteHeader: Enable/Disable writing the header into overlaying summary output files
    """

    #if a power splitter is used the input voltage gets divided by two to measure the voltage as well. 
    PS = PowerSplitter
    if PS:
        Vset = 2*Vset
        Vreset = 2*Vreset
        Vread = 2*Vread

    #settrise = 0.8e-9
    settrise = 2e-9
    VertScale = max([Vset,Vreset,Vread])*3
    VertScale2 = 50*ExpReadCurrent/2
    HorScale = tread/2
    TriggerLevel = 0.25*Vread
    ArmLevel = 0.7
    ExtInpImpedance = 10000
    OscInpImpedance = 50
    OscPulChn = OscPulseChn
    timeout = 2
    refresh = 1e-1
    period = 10*tread
    CycStart = eChar.curCycle

        
    PulseGenModel = eChar.PG81110A
    

    ################ PulseGen #######################################

    Oscilloscope = eChar.Oscilloscope
    PulseGen = eChar.PulseGen

    OscPulAcInput = OscPulChn.strip()[1]
    OscGNDAcInput = OscGNDChn.strip()[1]
    OscPulChn = int(OscPulChn.strip()[0])
    OscGNDChn = int(OscGNDChn.strip()[0])

    Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "View", 1)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale2)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "Coupling", "DC50")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "EnhanceResType", "3bits")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "ActiveInput", "Input%s" %(OscGNDAcInput))

    Oscilloscope.writeAcquisitionChn(OscPulChn, "ClearSweeps")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "View", 1)
    Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)
    Oscilloscope.writeAcquisitionChn(OscPulChn, "Coupling", "DC50")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "EnhanceResType", "3bits")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "ActiveInput", "Input%s" %(OscPulAcInput))

    Oscilloscope.writeAcquisitionHoriz("HorScale", HorScale)
    Oscilloscope.writeAcquisitionHoriz("MaxSamples", 250000)

    Oscilloscope.writeAcquisitionAuxOut("Amplitude", 2)
    Oscilloscope.writeAcquisitionAuxOut("AuxMode", "TriggerEnabled")

    TrigChn = OscPulChn
    Oscilloscope.writeAcquisitionTrigger("Edge.Source", "C%d" %(TrigChn))
    if Vread > 0: 
        Oscilloscope.writeAcquisitionTrigger("Edge.Slope", "Positive")
    else:
        Oscilloscope.writeAcquisitionTrigger("Edge.Slope", "Negative")   

    Oscilloscope.writeAcquisitionTrigger("C%dLevel" %(TrigChn), TriggerLevel)

    # set measurements 
    Oscilloscope.clearAllMeasurements()
    Oscilloscope.clearAllMeasurementSweeps()
    Oscilloscope.setMeasurement(1, "Amplitude", OscPulChn)
    Oscilloscope.setMeasurement(2, "Amplitude", OscGNDChn)

    PulseGen.reset()
    PulseGen.disableDigitalPatternMode()
    PulseGen.setTriggeredPulses(arming="external")
    PulseGen.setLevelArm()
    PulseGen.setArmLevel(ArmLevel)
    PulseGen.setTriggerCount(1)
    PulseGen.setPulsePeriod(period, PGPulseChn)
    PulseGen.setExtInputImpedance(ExtInpImpedance)
    PulseGen.setTransistionTimeOfLeadingEdge(settrise, PGPulseChn)
    PulseGen.setPulseDelay(0, PGPulseChn)
    PulseGen.turnDisplayOn()

    nReset = []
    Rreset = []
    RresGoal = []

    nSet = []
    Rset = []
    RsetGoal = []
    Rep = []
    RdelReset = []
    PercDelReset = []
    RdelSet = []
    PercDelSet = []

    Rcompl = []
    ncompl = []
    RgoalCompl = []
    Ccompl = []
    RdeltaCompl = []
    PercDelCompl = []

    stop = False
    RunRep = 1


    if Vread < 0:
        PulseGen.invertedOutputPolarity(chn=PGPulseChn)
        posV = 0
        negV = Vread
    else:
        PulseGen.normalOutputPolarity(chn=PGPulseChn)
        posV = Vread
        negV = 0

    PulseGen.setVoltageHigh(posV, chn=PGPulseChn) 
    PulseGen.setVoltageLow(negV, chn=PGPulseChn)
    Vprev = Vread
    PulseGen.setPulseWidth(tread)
    Oscilloscope.writeAcquisitionTrigger("C%dLevel" %(TrigChn), TriggerLevel)
    VertScale = abs(Vread/4)
    Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)

    Oscilloscope.writeAcquisition("TriggerMode", "Stop")
    PulseGen.turnOnOutput(PGPulseChn)
    if not PS:
        PulseGen.turnDifferentialOutputOn(PGPulseChn)

    Oscilloscope.writeAcquisition("TriggerMode", "Single")

    tstart = tm.time()
    while True:
        tm.sleep(refresh)
        try: 
            TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
        except:
            TrigMode = "" 
        if TrigMode.strip() == "Stopped" or tm.time()>tstart+timeout:
            break
    PulseGen.turnOffOutput(PGPulseChn)
    if not PS:
        PulseGen.turnDifferentialOutputOff(PGPulseChn)
    
    #V = Oscilloscope.queryDataArray(OscPulChn)
    #I = np.divide(Oscilloscope.queryDataArray(OscGNDChn),OscInpImpedance)

    if PS:
        V = float(Oscilloscope.getMeasurementResults(1))
    else:
        V = Vread
    I = float(Oscilloscope.getMeasurementResults(2))/50

    R0 = abs(V/I)
    R = R0
    Trac = [[R]]
    eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
    Trac = [[1/R]]  
    eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})

    Rcompl.append(R)
    Ccompl.append(1/R)
    ncompl.append(0)
    RgoalCompl.append(R)
    RdeltaCompl.append(0)
    PercDelCompl.append(0)   

    for n in range(Repetition):
        print("n", n)

        nReset.append([])
        Rreset.append([])
        RresGoal.append([])
        nSet.append([])
        Rset.append([])
        RsetGoal.append([])
        RdelReset.append([])
        PercDelReset.append([])
        RdelSet.append([])
        PercDelSet.append([])

        Rplot = []
        nplot = []
        
        # Set the first goal resistance to be hit 
        if Round:
            Rgoal = ma.ceil(R/RstepReset)*RstepReset
        else: 
            Rgoal = R + RstepReset

        r = 1
        Rwrote = False

        #write first value from Previous Read
        Rreset[n].append(R)
        nReset[n].append(0)
        RresGoal[n].append(R)
        RdelReset[n].append(0)
        PercDelReset[n].append(0)

        r = 1
        
        while r <= MaxPulsesPerStepReset and float(R) <= MaxResistance:
            print("r", r)

            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
            if stop:    
                eChar.finished.put(True)
                break

            ####### Reset
            if Vreset > 0 and Vprev > 0:
                PulseGen.setVoltageHigh(Vreset, chn=PGPulseChn) 
            elif Vreset < 0 and Vprev < 0:
                PulseGen.setVoltageLow(Vreset, chn=PGPulseChn)
            elif Vreset > 0:
                PulseGen.normalOutputPolarity(chn=PGPulseChn)
                PulseGen.setVoltageHigh(Vreset, chn=PGPulseChn) 
                PulseGen.setVoltageLow(0, chn=PGPulseChn)
                PulseGen.setVoltageHigh(Vreset, chn=PGPulseChn)
                PulseGen.setVoltageLow(0, chn=PGPulseChn)
            else:
                PulseGen.invertedOutputPolarity(chn=PGPulseChn)
                PulseGen.setVoltageLow(Vreset, chn=PGPulseChn)
                PulseGen.setVoltageHigh(0, chn=PGPulseChn) 
                PulseGen.setVoltageLow(Vreset, chn=PGPulseChn)
                PulseGen.setVoltageHigh(0, chn=PGPulseChn)
            
            #posV = 0
            #negV = Vreset
            
            Vprev = Vreset
            PulseGen.setPulseWidth(twidthReset)
            #tm.sleep(0.1)
            PulseGen.turnOnOutput(chn=PGPulseChn)
            if not PS:
                PulseGen.turnDifferentialOutputOn(PGPulseChn)
            #tm.sleep(1e-2)
            Oscilloscope.writeAcquisition("TriggerMode", "Single") 
            tstart = tm.time()
            while True:
                try: 
                    TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                except AttributeError:
                    TrigMode = "" 
                if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                    break
                    tm.sleep(refresh)
                PulseGen.turnOffOutput(chn=PGPulseChn)
                if not PS:
                    PulseGen.turnDifferentialOutputOff(PGPulseChn)

                Oscilloscope.writeAcquisition("TriggerMode", "Stop")
                
                if Vread > 0 and Vprev > 0:
                    PulseGen.setVoltageHigh(Vread, chn=PGPulseChn) 
                elif Vread < 0 and Vprev < 0:
                    PulseGen.setVoltageLow(Vread, chn=PGPulseChn)
                elif Vread > 0:
                    PulseGen.setVoltageHigh(Vread, chn=PGPulseChn) 
                    PulseGen.setVoltageLow(0, chn=PGPulseChn)
                    PulseGen.setVoltageHigh(Vread, chn=PGPulseChn) 
                    PulseGen.setVoltageLow(0, chn=PGPulseChn)
                    PulseGen.normalOutputPolarity(chn=PGPulseChn)
                else:
                    PulseGen.setVoltageLow(Vread, chn=PGPulseChn)
                    PulseGen.setVoltageHigh(0, chn=PGPulseChn) 
                    PulseGen.setVoltageLow(Vread, chn=PGPulseChn)
                    PulseGen.setVoltageHigh(0, chn=PGPulseChn) 
                    PulseGen.invertedOutputPolarity(chn=PGPulseChn)

                Vprev = Vread
                PulseGen.setPulseWidth(tread)
                
                Oscilloscope.writeAcquisitionTrigger("C%dLevel" %(TrigChn), TriggerLevel)
                VertScale = abs(Vread/4)
                Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)

                PulseGen.turnOnOutput(chn=PGPulseChn)
                if not PS:
                    PulseGen.turnDifferentialOutputOn(PGPulseChn)
                #tm.sleep(1e-2)
                Oscilloscope.writeAcquisition("TriggerMode", "Single")

                tstart = tm.time()
                while True:
                    try: 
                        TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                    except AttributeError:
                        TrigMode = "" 
                    if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                        break
                PulseGen.turnOffOutput(chn=PGPulseChn)
                if not PS:
                    PulseGen.turnDifferentialOutputOff(PGPulseChn)
                
                if PS:
                    V = float(Oscilloscope.getMeasurementResults(1))
                else:
                    V = Vread
                I = float(Oscilloscope.getMeasurementResults(2))/50

                R = abs(V/I)
                print("rR", R, " goal ", Rgoal)

                Rcompl.append(R)
                Ccompl.append(1/R)
                ncompl.append(r)
                RgoalCompl.append(Rgoal)
                RdeltaCompl.append(abs(R-Rgoal))
                PercDelCompl.append(abs((R-Rgoal)/R))

                if R > Rgoal:
                    Rreset[n].append(R)
                    nReset[n].append(r)
                    RresGoal[n].append(Rgoal)
                    RdelReset[n].append(abs(R-Rgoal))
                    PercDelReset[n].append(abs((R-Rgoal)/R))
                    
                    r = 1
                    Rgoal = Rgoal + RstepReset
                    Trac = [[R]]
                    eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
                    Trac = [[1/R]]  
                    eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})
                    Rwrote = True
                else:
                    r = r+1
            
            if not Rwrote:
                Rreset[n].append(R)
                nReset[n].append(r-1)
                RresGoal[n].append(Rgoal)
                RdelReset[n].append(abs(R-Rgoal))
                PercDelReset[n].append(abs((R-Rgoal)/R))

                Trac = [[R]]
                eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
                Trac = [[1/R]]  
                eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})
                    
            s = 1
            
            if Round:
                Rgoal = ma.floor(R/RstepSet)*RstepSet
            else: 
                Rgoal = R - RstepSet


            #write first value from Previous Read
            Rset[n].append(R)
            nSet[n].append(0)
            RsetGoal[n].append(R)
            RdelSet[n].append(0)
            PercDelSet[n].append(0)
            
            Swrote = False
            while s <= MaxPulsesPerStepSet:

                while not eChar.Stop.empty():
                    stop = eChar.Stop.get()
                if stop:    
                    eChar.finished.put(True)
                    break

                ####### Set
                if Vset > 0 and Vprev > 0:
                    PulseGen.setVoltageHigh(Vset, chn=PGPulseChn) 
                elif Vset < 0 and Vprev < 0:
                    PulseGen.setVoltageLow(Vset, chn=PGPulseChn)
                elif Vset > 0:
                    PulseGen.normalOutputPolarity(chn=PGPulseChn)
                    PulseGen.setVoltageHigh(Vset, chn=PGPulseChn) 
                    PulseGen.setVoltageLow(0, chn=PGPulseChn)
                    PulseGen.setVoltageHigh(Vset, chn=PGPulseChn) 
                    PulseGen.setVoltageLow(0, chn=PGPulseChn)
                else:
                    PulseGen.invertedOutputPolarity(chn=PGPulseChn)
                    PulseGen.setVoltageLow(Vset, chn=PGPulseChn)
                    PulseGen.setVoltageHigh(0, chn=PGPulseChn) 
                    PulseGen.setVoltageLow(Vset, chn=PGPulseChn)
                    PulseGen.setVoltageHigh(0, chn=PGPulseChn) 
                Vprev = Vset
                PulseGen.setPulseWidth(twidthSet)

                PulseGen.turnOnOutput(chn=PGPulseChn)
                if not PS:
                    PulseGen.turnDifferentialOutputOn(PGPulseChn)
                Oscilloscope.writeAcquisition("TriggerMode", "Single") 

                tstart = tm.time()
                while True:
                    try: 
                        TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                    except AttributeError:
                        TrigMode = "" 
                    if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                        break
                PulseGen.turnOffOutput(chn=PGPulseChn)
                if not PS:
                    PulseGen.turnDifferentialOutputOff(PGPulseChn)
                Oscilloscope.writeAcquisition("TriggerMode", "Stop")
                
                if Vread > 0 and Vprev > 0:
                    PulseGen.setVoltageHigh(Vread, chn=PGPulseChn) 
                elif Vread < 0 and Vprev < 0:
                    PulseGen.setVoltageLow(Vread, chn=PGPulseChn)
                elif Vread > 0:
                    PulseGen.normalOutputPolarity(chn=PGPulseChn)
                    PulseGen.setVoltageHigh(Vread, chn=PGPulseChn) 
                    PulseGen.setVoltageLow(0, chn=PGPulseChn)
                    PulseGen.setVoltageHigh(Vread, chn=PGPulseChn) 
                    PulseGen.setVoltageLow(0, chn=PGPulseChn)
                else:
                    PulseGen.invertedOutputPolarity(chn=PGPulseChn)
                    PulseGen.setVoltageLow(Vread, chn=PGPulseChn)
                    PulseGen.setVoltageHigh(0, chn=PGPulseChn) 
                    PulseGen.setVoltageLow(Vread, chn=PGPulseChn)
                    PulseGen.setVoltageHigh(0, chn=PGPulseChn) 
                
                Vprev = Vread
                PulseGen.setPulseWidth(tread)
                
                Oscilloscope.writeAcquisitionTrigger("C%dLevel" %(TrigChn), TriggerLevel)
                VertScale = abs(Vread/4)
                Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)

                PulseGen.turnOnOutput(chn=PGPulseChn)
                if not PS:
                    PulseGen.turnDifferentialOutputOn(PGPulseChn)
                Oscilloscope.writeAcquisition("TriggerMode", "Single")

                tstart = tm.time()
                while True:
                    try: 
                        TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                    except AttributeError:
                        TrigMode = "" 
                    if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                        break

                PulseGen.turnOffOutput(chn=PGPulseChn)
                if not PS:
                    PulseGen.turnDifferentialOutputOff(PGPulseChn)
                
                if PS:
                    V = float(Oscilloscope.getMeasurementResults(1))
                else:
                    V = Vread
                I = float(Oscilloscope.getMeasurementResults(2))/50

                R = abs(V/I)
                print("sR", R, " goal ", Rgoal)
            

                Rcompl.append(R)
                Ccompl.append(1/R)
                ncompl.append(r)
                RgoalCompl.append(Rgoal)
                RdeltaCompl.append(abs(R-Rgoal))
                PercDelCompl.append(abs((R-Rgoal)/R))

                if R < Rgoal:
                    Rset[n].append(R)
                    nSet[n].append(s)
                    RsetGoal[n].append(Rgoal)
                    RdelSet[n].append(abs(R-Rgoal))
                    PercDelSet[n].append(abs((R-Rgoal)/R))
                    
                    Trac = [[R]]
                    eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
                    Trac = [[1/R]]  
                    eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})
                    s = 1
                    Rgoal = Rgoal - RstepSet
                    Swrote = True
                else:
                    s = s+1
            
            if not Swrote:
                Rset[n].append(R)
                nSet[n].append(s-1)
                RsetGoal[n].append(Rgoal)
                RdelSet[n].append(abs(R-Rgoal))
                PercDelSet[n].append(abs((R-Rgoal)/R))
                                
                Trac = [[R]]
                eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
                Trac = [[1/R]]  
                eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})

            eChar.curCycle = eChar.curCycle + 1

            RunRep = RunRep + 1
            if stop:    
                eChar.finished.put(True)
                break
        
        PulseGen.turnOffOutput(chn=PGPulseChn)
        if not PS:
            PulseGen.turnDifferentialOutputOff(PGPulseChn)


    if not WriteHeader:
        header = eChar.getHeader("Combined")
    else:
        header = []
    
    header.append("Instrument,Oscilloscope,%s" %(OscName.strip()))
    header.append("Instrument,PulseGenerator,%s" %(PGName.strip()))
    header.append("Measurement,Vset, %.2e" %(Vset))
    header.append("Measurement,Set Pulse Width, %.2e" %(twidthSet))
    header.append("Measurement,Set Max Pulses Per Step,  %d" %(MaxPulsesPerStepSet))
    header.append("measurement,Set Resistance Step, %.2f" %( RstepSet))
    header.append("Measurement,Vreset, %.2e" %(Vreset))
    header.append("Measurement,Reset Pulse Width, %.2e" %(twidthReset))
    header.append("Measurement,Reset Max Pulses Per Step,  %d" %(MaxPulsesPerStepReset))
    header.append("measurement,Reset Resistance Step, %.2e" %( RstepReset))
    header.append("Measurement,Vread, %.2e" %(Vread))
    header.append("Measurement,Read Pulse Width, %.2e" %(tread))
    header.append("Measurement,Round, %s" %(Round))
    header.append("Measurement,Repetition, %s" %(Repetition))
    header.append("Measurement,PowerSplitter, %s" %(PS))

    if WriteHeader:
        eChar.extendHeader("Combined", header)


    newline = [None]*3
    newline[0] = 'DataName'
    newline[1] = 'Dimension'
    newline[2] = 'Repetition'
    EntryNumReset = []
    EntryNumSet = []
    OutputData = []
    
    nMax = 0
    for n in range(len(Rset)):
        CondReset = list(np.reciprocal(Rreset[n]))
        CondSet = list(np.reciprocal(Rset[n]))
        
        newline[0] = '%s,Entry #, Res. Goal, Res., # of Pulses, Res. Dev. (value), Res. Dev. (perc), Res. Conductance (s)' %(newline[0])
        newline[1] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[1],len(RresGoal[n]),len(RresGoal[n]), len(Rreset[n]), len(nReset[n]), len(RdelReset[n]), len(PercDelReset[n]), len(CondReset))
        newline[2] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[2],n+1,n+1,n+1,n+1,n+1,n+1,n+1)
        if EntryNumReset == []:
            EntryNumReset.append(list(range(1,1+len(RresGoal[n]),1)))
        else:
            EntryNumReset.append(list(range(EntryNumSet[-1][-1]+1,EntryNumSet[-1][-1]+1+len(RresGoal[n]),1)))

        newline[0] = '%s,Entry #, Set. Goal, Set., # of Pulses, Set. Dev. (value), Set. Dev. (perc), Set. Conductance (s)' %(newline[0])
        newline[1] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[1],len(RsetGoal[n]),len(RsetGoal[n]), len(Rset[n]), len(nSet[n]), len(RdelSet[n]), len(PercDelSet[n]), len(CondSet))
        newline[2] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[2],n+1,n+1,n+1,n+1,n+1,n+1,n+1)

        EntryNumSet.append(list(range(EntryNumReset[-1][-1]+1,EntryNumReset[-1][-1]+1+len(RresGoal[n]),1)))

        CurMax = max(len(RresGoal[n]), len(Rreset[n]), len(nReset[n]), len(RdelReset[n]), len(PercDelReset[n]), len(CondReset),len(RsetGoal[n]), len(Rset[n]), len(nSet[n]), len(RdelSet[n]), len(PercDelSet[n]), len(CondSet))

        if CurMax > nMax:
            nMax = CurMax

        

    OutputData = []
    for n in range(nMax):
        data = 'DataValue'
        for k in range(len(Rset)):
            try:
                CondReset = float(1/Rreset[k][n])
                data = "%s, %f, %f, %f, %f, %f, %f, %f" %(data, EntryNumReset[k][n], RresGoal[k][n], Rreset[k][n], nReset[k][n], RdelReset[k][n], PercDelReset[k][n], CondReset)
            except IndexError:
                data = "%s, , , , , , , " %(data)
            try:
                CondSet = float(1/Rset[k][n])
                data = "%s, %f, %f, %f, %f, %f, %f, %f" %(data,  EntryNumSet[k][n], RsetGoal[k][n], Rset[k][n], nSet[k][n], RdelSet[k][n], PercDelSet[k][n], CondSet)
            except IndexError:
                data = "%s, , , , , , , " %(data)
        OutputData.append(data)
        
    header1 = cp.deepcopy(header)
    header1.extend(newline)
    
    eChar.writeDataToFile(header, OutputData, startCyc=CycStart, endCyc=eChar.curCycle-1)
            
    newline = [None]*2
    newline[0] = 'DataName, R Goal, R, # of Pulses, Deviation (value), Deviation (perc), Conductance (s)'
    newline[1] = 'Dimension, %d, %d, %d, %d, %d, %d' %(len(RgoalCompl), len(Rcompl), len(ncompl), len(RdeltaCompl), len(PercDelCompl), len(Ccompl))
    
    OutputData2 = []
    for n in range(len(Rcompl)):
        data = 'DataValue, %f, %f, %d, %f, %f, %f' %(RgoalCompl[n], Rcompl[n], ncompl[n], RdeltaCompl[n], PercDelCompl[n], Ccompl[n])
        OutputData2.append(data)
    
    header.extend(newline)
    Typ2 = "Compl_%s" %(Typ)
    
    eChar.writeDataToFile(header, OutputData2, Typ=Typ2, startCyc=CycStart, endCyc=eChar.curCycle-1)
         
    r0 = R0
    Rdelta = []
    Rdelta.append(Rreset[0][-1] - R0)
    for r, s in zip(Rreset, Rset):
        Rdelta.append(r[-1]-s[-1])


    AvgSetPul =  eChar.dhValue([], 'FirstHRS', DoYield=False, Unit='ohm')
    AvgResetPul =  eChar.dhValue([], 'FirstLRS', DoYield=False, Unit='ohm')

    for n in nSet:
        AvgSetPul.extend(n)

    for n in nReset:
        AvgResetPul.extend(n)

    AvgRratio =  eChar.dhValue(Rdelta, 'ImaxForm', DoYield=eChar.DoYield, Unit='A')
    row = eChar.dhAddRow([AvgSetPul,AvgResetPul,AvgRratio], eChar.curCycle,eChar.curCycle)

    



    
###########################################################################################################################
def AnalogSwi_PGBNC765(eChar, PGPulseChn, OscPulseChn, OscGNDChn, ExpReadCurrent, Vset, Vreset, twidthSet, twidthReset, Vread, tread, RstepSet, RstepReset, MaxResistance, MaxPulsesPerStepSet, MaxPulsesPerStepReset, Round, Repetition, PowerSplitter, WriteHeader=True):
        
    """
    Applies voltage pulses via the Agilent 81110A pulse generator and measures the pulse response via a LeCroy oscilloscope
    Both Devices must be available. RF setup is recommended for rise times below 50ns. 
    PGPulseChn:     Pulse Channel of BNC Model 765, (1 to 4)
    OscPulseChn:    Oscilloscope Pulse Channel
    OscGNDChn:      Oscilloscope GND Channel
    Vset:           Set Voltage (V)
    Vreset:         Reset Voltage (V)
    settwidth:      Set pulse width (s)
    resettwidth:    Reset pulse width (s)
    Vread:          Read Voltage (V)
    tread:          Read pulse width(V)
    RstepSet:       Aimed resistance step per Set
    RstepReset:     Aimed resistance step per Reset
    MaxPulsesPerStepSet:    Maximum number of pulses per step until pulsing is stopped
    MaxPulsesPerStepReset:  Maximum number of pulses per step until pulsing is stopped
    Round           Round to next RstepSize
    Repetition:     Number of set/rest cycles
    PowerSplitter:  Is a power splitter in use? 
    WriteHeader: Enable/Disable writing the header into overlaying summary output files
    """

    #if a power splitter is used the input voltage gets divided by two to measure the voltage as well. 
    PS = PowerSplitter
    if PS:
        Vset = 2*Vset
        Vreset = 2*Vreset
        Vread = 2*Vread

    VertScale = max([Vset,Vreset,Vread])*3
    VertScale2 = 50*ExpReadCurrent/2
    #VertScale2 = ExpReadCurrent
    HorScale = tread/2
    TriggerLevel = 0.25*Vread
    ArmLevel = 0.7
    TriggerOutputLevel = 1.5
    ExtInpImpedance = 10000
    OscInpImpedance = 50
    OscPulChn = OscPulseChn
    timeout = 2
    refresh = 1e-1
    period = 5*max(tread, twidthSet, twidthReset)
    CycStart = eChar.curCycle


    ################ PulseGen #######################################

    Oscilloscope = eChar.Oscilloscope
    PulseGen = eChar.PGBNC765


    OscName = Oscilloscope.getModel()
    PGName = PulseGen.getModel()

    PulseGen.setTriggerOutputSource(PGPulseChn)
    PulseGen.setTriggerOutputDelay(0)
    PulseGen.setTriggerOutputPolarityPositive()
    PulseGen.setTriggerOutputAmplitude(TriggerOutputLevel)
    PulseGen.setTriggerModeSingle()
    PulseGen.setTriggerSourceExternal()

    OscPulAcInput = OscPulChn.strip()[1]
    OscGNDAcInput = OscGNDChn.strip()[1]
    OscPulChn = int(OscPulChn.strip()[0])
    OscGNDChn = int(OscGNDChn.strip()[0])

    #print("VertScale2", VertScale2)
    #print(OscGNDChn, OscPulChn)
    #print(OscGNDAcInput, OscPulAcInput)

    Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "View", 1)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale2)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "Coupling", "DC50")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "EnhanceResType", "3bits")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "ActiveInput", "Input%s" %(OscGNDAcInput))
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "BandwidthLimit", "20MHz")

    Oscilloscope.writeAcquisitionChn(OscPulChn, "ClearSweeps")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "View", 1)
    Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)
    Oscilloscope.writeAcquisitionChn(OscPulChn, "Coupling", "DC50")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "EnhanceResType", "3bits")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "ActiveInput", "Input%s" %(OscPulAcInput))

    Oscilloscope.writeAcquisitionHoriz("HorScale", HorScale)
    Oscilloscope.writeAcquisitionHoriz("MaxSamples", 250000)

    Oscilloscope.writeAcquisitionAuxOut("Amplitude", 2)
    Oscilloscope.writeAcquisitionAuxOut("AuxMode", "TriggerEnabled")

    TrigChn = OscPulChn
    Oscilloscope.writeAcquisitionTrigger("Edge.Source", "EXT")
    Oscilloscope.writeAcquisitionTrigger("Edge.Slope", "Negative")   

    Oscilloscope.writeAcquisitionTrigger("ExtLevel", TriggerLevel)

    # set measurements 
    Oscilloscope.clearAllMeasurements()
    Oscilloscope.clearAllMeasurementSweeps()
    Oscilloscope.setMeasurement(1, "Amplitude", OscPulChn)
    Oscilloscope.setMeasurement(2, "Amplitude", OscGNDChn)

    PulseGen.reset()
    PulseGen.clearTrigger()
    PulseGen.setTriggerSourceExternal()
    PulseGen.setTriggerThreshold(ArmLevel)
    PulseGen.setPulseModeSingle(PGPulseChn)
    PulseGen.setPulsePeriod(period, PGPulseChn)
    PulseGen.setTriggerModeSingle()
    PulseGen.setTriggerImpedanceTo50ohm()
    PulseGen.enableOutput(PGPulseChn)
    PulseGen.arm()
    PulseGen.disableOutput(PGPulseChn)

    nReset = []
    Rreset = []
    RresGoal = []

    nSet = []
    Rset = []
    RsetGoal = []
    Rep = []
    RdelReset = []
    PercDelReset = []
    RdelSet = []
    PercDelSet = []

    Rcompl = []
    ncompl = []
    RgoalCompl = []
    Ccompl = []
    RdeltaCompl = []
    PercDelCompl = []

    stop = False
    RunRep = 1
  
    PG_BNC_setPulseVoltage(PulseGen, PGPulseChn, Vread)
    PulseGen.setPulseWidth(tread)

    Oscilloscope.writeAcquisitionTrigger("ExtLevel", TriggerLevel)
    VertScale = abs(Vread/4)
    Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)

    Oscilloscope.writeAcquisition("TriggerMode", "Stop")
    PulseGen.enableOutput(PGPulseChn)
    PulseGen.setTriggerOutputAmplitude(1.5)

    Oscilloscope.writeAcquisition("TriggerMode", "Single")

    tstart = tm.time()
    while True:
        tm.sleep(refresh)
        try: 
            TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
        except:
            TrigMode = "" 
        if TrigMode.strip() == "Stopped" or tm.time()>tstart+timeout:
            break
    PulseGen.disableOutput(PGPulseChn)
    PulseGen.setTriggerOutputPolarityNegative()
    
    #V = Oscilloscope.queryDataArray(OscPulChn)
    #I = np.divide(Oscilloscope.queryDataArray(OscGNDChn),OscInpImpedance)

    if PS:
        V = float(Oscilloscope.getMeasurementResults(1))
    else:
        V = Vread
    I = float(Oscilloscope.getMeasurementResults(2))/50

    R0 = abs(V/I)
    R = R0
    Trac = [[R]]
    eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
    Trac = [[1/R]]  
    eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})

    Rcompl.append(R)
    Ccompl.append(1/R)
    ncompl.append(0)
    RgoalCompl.append(R)
    RdeltaCompl.append(0)
    PercDelCompl.append(0)   

    for n in range(Repetition):
        print("n", n)

        nReset.append([])
        Rreset.append([])
        RresGoal.append([])
        nSet.append([])
        Rset.append([])
        RsetGoal.append([])
        RdelReset.append([])
        PercDelReset.append([])
        RdelSet.append([])
        PercDelSet.append([])

        Rplot = []
        nplot = []
        
        # Set the first goal resistance to be hit 
        if Round:
            Rgoal = ma.ceil(R/RstepReset)*RstepReset
        else: 
            Rgoal = R + RstepReset

        r = 1
        Rwrote = False

        #write first value from Previous Read
        Rreset[n].append(R)
        nReset[n].append(0)
        RresGoal[n].append(R)
        RdelReset[n].append(0)
        PercDelReset[n].append(0)

        r = 1
        
        while r <= MaxPulsesPerStepReset and float(R) <= MaxResistance:
            print("r", r)

            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
            if stop:    
                eChar.finished.put(True)
                break

            ####### Reset
            
            PG_BNC_setPulseVoltage(PulseGen, PGPulseChn, Vreset)
            PulseGen.setPulseWidth(twidthReset)

            PulseGen.enableOutput(PGPulseChn)
            PulseGen.setTriggerOutputAmplitude(1.5)
            
            Oscilloscope.writeAcquisition("TriggerMode", "Single") 
            tstart = tm.time()
            while True:
                try: 
                    TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                except AttributeError:
                    TrigMode = "" 
                if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                    break
                tm.sleep(refresh)
            PulseGen.disableOutput(PGPulseChn)
            PulseGen.setTriggerOutputPolarityNegative()

            Oscilloscope.writeAcquisition("TriggerMode", "Stop")
            
            PG_BNC_setPulseVoltage(PulseGen, PGPulseChn, Vread)
            PulseGen.setPulseWidth(tread)
            
            Oscilloscope.writeAcquisitionTrigger("C%dLevel" %(TrigChn), TriggerLevel)
            VertScale = abs(Vread/4)
            Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)

            PulseGen.enableOutput(PGPulseChn)
            PulseGen.setTriggerOutputAmplitude(1.5)
            #tm.sleep(1e-2)
            Oscilloscope.writeAcquisition("TriggerMode", "Single")

            tstart = tm.time()
            while True:
                try: 
                    TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                except AttributeError:
                    TrigMode = "" 
                if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                    break

            PulseGen.disableOutput(PGPulseChn)
            PulseGen.setTriggerOutputPolarityNegative()
            
            ##############################################################################################################################
            ############## Update this section for Burst pulsing!!!!! ####################################################################
            if PS:
                V = float(Oscilloscope.getMeasurementResults(1))
            else:
                V = Vread
            I = float(Oscilloscope.getMeasurementResults(2))/50

            R = abs(V/I)
            print("rR", R, " goal ", Rgoal)

            Rcompl.append(R)
            Ccompl.append(1/R)
            ncompl.append(r)
            RgoalCompl.append(Rgoal)
            RdeltaCompl.append(abs(R-Rgoal))
            PercDelCompl.append(abs((R-Rgoal)/R))

            if R > Rgoal:
                Rreset[n].append(R)
                nReset[n].append(r)
                RresGoal[n].append(Rgoal)
                RdelReset[n].append(abs(R-Rgoal))
                PercDelReset[n].append(abs((R-Rgoal)/R))
                
                r = 1
                Rgoal = Rgoal + RstepReset
                Trac = [[R]]
                eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
                Trac = [[1/R]]  
                eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})
                Rwrote = True
            else:
                r = r+1
        
        if not Rwrote:
            Rreset[n].append(R)
            nReset[n].append(r-1)
            RresGoal[n].append(Rgoal)
            RdelReset[n].append(abs(R-Rgoal))
            PercDelReset[n].append(abs((R-Rgoal)/R))

            Trac = [[R]]
            eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
            Trac = [[1/R]]  
            eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})
                
        s = 1
        
        if Round:
            Rgoal = ma.floor(R/RstepSet)*RstepSet
        else: 
            Rgoal = R - RstepSet


        #write first value from Previous Read
        Rset[n].append(R)
        nSet[n].append(0)
        RsetGoal[n].append(R)
        RdelSet[n].append(0)
        PercDelSet[n].append(0)
        
        Swrote = False
        while s <= MaxPulsesPerStepSet:

            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
            if stop:    
                eChar.finished.put(True)
                break

            ####### Set
            PG_BNC_setPulseVoltage(PulseGen, PGPulseChn, Vset)
            Vprev = Vset
            PulseGen.setPulseWidth(twidthSet)

            PulseGen.enableOutput(PGPulseChn)
            PulseGen.setTriggerOutputAmplitude(1.5)
            Oscilloscope.writeAcquisition("TriggerMode", "Single") 

            tstart = tm.time()
            while True:
                try: 
                    TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                except AttributeError:
                    TrigMode = "" 
                if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                    break
                
            PulseGen.disableOutput(PGPulseChn)
            PulseGen.setTriggerOutputPolarityNegative()
            Oscilloscope.writeAcquisition("TriggerMode", "Stop")

            PG_BNC_setPulseVoltage(PulseGen, PGPulseChn, Vread)
            PulseGen.setPulseWidth(tread)
            
            Oscilloscope.writeAcquisitionTrigger("C%dLevel" %(TrigChn), TriggerLevel)
            VertScale = abs(Vread/4)
            Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)

            PulseGen.enableOutput(PGPulseChn)
            PulseGen.setTriggerOutputAmplitude(1.5)
            Oscilloscope.writeAcquisition("TriggerMode", "Single")

            tstart = tm.time()
            while True:
                try: 
                    TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                except AttributeError:
                    TrigMode = "" 
                if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                    break

            PulseGen.disableOutput(PGPulseChn)
            PulseGen.setTriggerOutputPolarityNegative()
            
            if PS:
                V = float(Oscilloscope.getMeasurementResults(1))
            else:
                V = Vread
            I = float(Oscilloscope.getMeasurementResults(2))/50

            R = abs(V/I)
            print("sR", R, " goal ", Rgoal)
        

            Rcompl.append(R)
            Ccompl.append(1/R)
            ncompl.append(r)
            RgoalCompl.append(Rgoal)
            RdeltaCompl.append(abs(R-Rgoal))
            PercDelCompl.append(abs((R-Rgoal)/R))

            if R < Rgoal:
                Rset[n].append(R)
                nSet[n].append(s)
                RsetGoal[n].append(Rgoal)
                RdelSet[n].append(abs(R-Rgoal))
                PercDelSet[n].append(abs((R-Rgoal)/R))
                
                Trac = [[R]]
                eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
                Trac = [[1/R]]  
                eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})
                s = 1
                Rgoal = Rgoal - RstepSet
                Swrote = True
            else:
                s = s+1
        

        ####### Set Pulse at the end to make sure it really sets ##########
        PulseGen.setPulseVoltage(2.5, PGPulseChn)
        PulseGen.setPulseWidth(5e-5)
        PulseGen.disableTriggerOutput()

        #PulseGen.turnOnOutput(PGPulseChn)
        PulseGen.arm()
        Oscilloscope.writeAcquisition("TriggerMode", "Single") 

        tstart = tm.time()
        while True:
            try: 
                TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
            except AttributeError:
                TrigMode = "" 
            if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                break

        #PulseGen.turnOffOutput(chn=PGPulseChn)
        PulseGen.dearm()
        Oscilloscope.writeAcquisition("TriggerMode", "Stop")



        if not Swrote:
            Rset[n].append(R)
            nSet[n].append(s-1)
            RsetGoal[n].append(Rgoal)
            RdelSet[n].append(abs(R-Rgoal))
            PercDelSet[n].append(abs((R-Rgoal)/R))
                            
            Trac = [[R]]
            eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
            Trac = [[1/R]]  
            eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})

        eChar.curCycle = eChar.curCycle + 1


        RunRep = RunRep + 1
        if stop:    
            eChar.finished.put(True)
            break
    
    PulseGen.disableOutput(PGPulseChn)
    PulseGen.setTriggerOutputPolarityNegative()
    PulseGen.dearm()

    ########## Data Analysis

    if not WriteHeader:
        header = eChar.getHeader("Combined")
    else:
        header = []
    
    header.append("Instrument,Oscilloscope,%s" %(OscName.strip()))
    header.append("Instrument,PulseGenerator,%s" %(PGName.strip()))
    header.append("Measurement,Vset, %.2e" %(Vset))
    header.append("Measurement,Set Pulse Width, %.2e" %(twidthSet))
    header.append("Measurement,Set Max Pulses Per Step,  %d" %(MaxPulsesPerStepSet))
    header.append("measurement,Set Resistance Step, %.2f" %( RstepSet))
    header.append("Measurement,Vreset, %.2e" %(Vreset))
    header.append("Measurement,Reset Pulse Width, %.2e" %(twidthReset))
    header.append("Measurement,Reset Max Pulses Per Step,  %d" %(MaxPulsesPerStepReset))
    header.append("measurement,Reset Resistance Step, %.2e" %( RstepReset))
    header.append("Measurement,Vread, %.2e" %(Vread))
    header.append("Measurement,Read Pulse Width, %.2e" %(tread))
    header.append("Measurement,Round, %s" %(Round))
    header.append("Measurement,Repetition, %s" %(Repetition))
    header.append("Measurement,PowerSplitter, %s" %(PS))

    if WriteHeader:
        header.extendHeader("Combined",header)

    newline = [None]*3
    newline[0] = 'DataName'
    newline[1] = 'Dimension'
    newline[2] = 'Repetition'
    EntryNumReset = []
    EntryNumSet = []
    OutputData = []
    
    nMax = 0
    for n in range(len(Rset)):
        CondReset = list(np.reciprocal(Rreset[n]))
        CondSet = list(np.reciprocal(Rset[n]))
        
        newline[0] = '%s,Entry #, Res. Goal, Res., # of Pulses, Res. Dev. (value), Res. Dev. (perc), Res. Conductance (s)' %(newline[0])
        newline[1] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[1],len(RresGoal[n]),len(RresGoal[n]), len(Rreset[n]), len(nReset[n]), len(RdelReset[n]), len(PercDelReset[n]), len(CondReset))
        newline[2] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[2],n+1,n+1,n+1,n+1,n+1,n+1,n+1)
        if EntryNumReset == []:
            EntryNumReset.append(list(range(1,1+len(RresGoal[n]),1)))
        else:
            EntryNumReset.append(list(range(EntryNumSet[-1][-1]+1,EntryNumSet[-1][-1]+1+len(RresGoal[n]),1)))

        newline[0] = '%s,Entry #, Set. Goal, Set., # of Pulses, Set. Dev. (value), Set. Dev. (perc), Set. Conductance (s)' %(newline[0])
        newline[1] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[1],len(RsetGoal[n]),len(RsetGoal[n]), len(Rset[n]), len(nSet[n]), len(RdelSet[n]), len(PercDelSet[n]), len(CondSet))
        newline[2] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[2],n+1,n+1,n+1,n+1,n+1,n+1,n+1)

        EntryNumSet.append(list(range(EntryNumReset[-1][-1]+1,EntryNumReset[-1][-1]+1+len(RresGoal[n]),1)))

        CurMax = max(len(RresGoal[n]), len(Rreset[n]), len(nReset[n]), len(RdelReset[n]), len(PercDelReset[n]), len(CondReset),len(RsetGoal[n]), len(Rset[n]), len(nSet[n]), len(RdelSet[n]), len(PercDelSet[n]), len(CondSet))

        if CurMax > nMax:
            nMax = CurMax

        

    OutputData = []
    for n in range(nMax):
        data = 'DataValue'
        for k in range(len(Rset)):
            try:
                CondReset = float(1/Rreset[k][n])
                data = "%s, %f, %f, %f, %f, %f, %f, %f" %(data, EntryNumReset[k][n], RresGoal[k][n], Rreset[k][n], nReset[k][n], RdelReset[k][n], PercDelReset[k][n], CondReset)
            except IndexError:
                data = "%s, , , , , , , " %(data)
            try:
                CondSet = float(1/Rset[k][n])
                data = "%s, %f, %f, %f, %f, %f, %f, %f" %(data,  EntryNumSet[k][n], RsetGoal[k][n], Rset[k][n], nSet[k][n], RdelSet[k][n], PercDelSet[k][n], CondSet)
            except IndexError:
                data = "%s, , , , , , , " %(data)
        OutputData.append(data)
        
    header1 = cp.deepcopy(header)
    header1.extend(newline)
    
    eChar.writeDataToFile(header1, OutputData, startCyc=CycStart, endCyc=eChar.curCycle-1)
            
    newline = [None]*2
    newline[0] = 'DataName, R Goal, R, # of Pulses, Deviation (value), Deviation (perc), Conductance (s)'
    newline[1] = 'Dimension, %d, %d, %d, %d, %d, %d' %(len(RgoalCompl), len(Rcompl), len(ncompl), len(RdeltaCompl), len(PercDelCompl), len(Ccompl))
    
    OutputData2 = []
    for n in range(len(Rcompl)):
        data = 'DataValue, %f, %f, %d, %f, %f, %f' %(RgoalCompl[n], Rcompl[n], ncompl[n], RdeltaCompl[n], PercDelCompl[n], Ccompl[n])
        OutputData2.append(data)
    
    header.extend(newline)
    Typ2 = "Compl_%s" %(self.eChar.getMeasurementType())
    eChar.writeDataToFile(header, OutputData2, Typ=Typ2, startCyc=CycStart, endCyc=eChar.curCycle-1)
            
    r0 = R0
    Rdelta = []
    Rdelta.append(Rreset[0][-1] - R0)
    for r, s in zip(Rreset, Rset):
        Rdelta.append(r[-1]-s[-1])


    AvgSetPul =  eChar.dhValue([], 'FirstHRS', DoYield=False, Unit='ohm')
    AvgResetPul =  eChar.dhValue([], 'FirstLRS', DoYield=False, Unit='ohm')

    for n in nSet:
        AvgSetPul.extend(n)

    for n in nReset:
        AvgResetPul.extend(n)

    AvgRratio =  eChar.dhValue(Rdelta, 'ImaxForm', DoYield=eChar.DoYield, Unit='A')
    row = eChar.dhAddRow([AvgSetPul,AvgResetPul,AvgRratio],eChar.curCycle,eChar.curCycle)

    


##########################################################################################

###########################################################################################################################
def AnalogForm_PGBNC765(eChar, PGPulseChn, OscPulseChn, OscGNDChn, ExpReadCurrent, Vform, twidthForm, Vread, tread, Rform, MaxPulses, PowerSplitter, WriteHeader=True):
        
    """
    Applies voltage pulses via the Agilent 81110A pulse generator and measures the pulse response via a LeCroy oscilloscope
    Both Devices must be available. RF setup is recommended for rise times below 50ns. 
    PGPulseChn:     Pulse Channel of 81110A, (1 or 2)
    OscPulseChn:    Oscilloscope Pulse Channel
    OscGNDChn:      Oscilloscope GND Channel
    Vset:           Set Voltage (V)
    Vreset:         Reset Voltage (V)
    settwidth:      Set pulse width (s)
    resettwidth:    Reset pulse width (s)
    Vread:          Read Voltage (V)
    tread:          Read pulse width(V)
    RstepSet:       Aimed resistance step per Set
    RstepReset:     Aimed resistance step per Reset
    MaxPulsesPerStepSet:    Maximum number of pulses per step until pulsing is stopped
    MaxPulsesPerStepReset:  Maximum number of pulses per step until pulsing is stopped
    Round           Round to next RstepSize
    Repetition:     Number of set/rest cycles
    PowerSplitter:  Is a power splitter in use? 
    WriteHeader: Enable/Disable writing the header into overlaying summary output files
    """

    #if a power splitter is used the input voltage gets divided by two to measure the voltage as well. 
    PS = PowerSplitter
    if PS:
        Vform = 2*Vform
        Vread = 2*Vread


    Typ = 'RFForming'
    VertScale = max([Vform,Vread])*3
    VertScale2 = 50*ExpReadCurrent/2
    HorScale = tread/2
    TriggerOutputLevel = 1.5
    TriggerLevel = TriggerOutputLevel/3
    ExtInpImpedance = 10000
    OscInpImpedance = 50
    OscPulChn = OscPulseChn
    timeout = 2
    refresh = 1e-1
    period = 100*tread
    CycStart = eChar.curCycle

    Oscilloscope = eChar.getPrimaryLeCroyOscilloscope()
    PulseGen = eChar.PGBNC765

    OscName = Oscilloscope.getModel()
    PGName = PulseGen.getModel()
    
    OscPulAcInput = OscPulChn.strip()[1]
    OscGNDAcInput = OscGNDChn.strip()[1]
    OscPulChn = int(OscPulChn.strip()[0])
    OscGNDChn = int(OscGNDChn.strip()[0])

    Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "View", 1)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale2)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "Coupling", "DC50")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "EnhanceResType", "3bits")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "ActiveInput", "Input%s" %(OscGNDAcInput))
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "BandwidthLimit", "20MHz")

    Oscilloscope.writeAcquisitionChn(OscPulChn, "ClearSweeps")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "View", 1)
    Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)
    Oscilloscope.writeAcquisitionChn(OscPulChn, "Coupling", "DC50")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "EnhanceResType", "3bits")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "ActiveInput", "Input%s" %(OscPulAcInput))

    Oscilloscope.writeAcquisitionHoriz("HorScale", HorScale)
    Oscilloscope.writeAcquisitionHoriz("MaxSamples", 250000)

    Oscilloscope.writeAcquisitionAuxOut("Amplitude", 2)
    Oscilloscope.writeAcquisitionAuxOut("AuxMode", "TriggerEnabled")

    Oscilloscope.writeAcquisitionTrigger("Edge.Source", "EXT")
    Oscilloscope.writeAcquisitionTrigger("Edge.Slope", "Either")

    Oscilloscope.writeAcquisitionTrigger("ExtLevel", TriggerLevel/2)

    # set measurements 
    Oscilloscope.clearAllMeasurements()
    Oscilloscope.clearAllMeasurementSweeps()
    Oscilloscope.setMeasurement(1, "Amplitude", OscPulChn)
    Oscilloscope.setMeasurement(2, "Amplitude", OscGNDChn)

    PulseGen.reset()
    PulseGen.clearTrigger()
    PulseGen.setTriggerSourceExternal()
    PulseGen.setTriggerThreshold(TriggerLevel)
    PulseGen.setTriggerOutputAmplitude(TriggerOutputLevel)
    PulseGen.setPulseModeSingle(PGPulseChn)
    PulseGen.setPulsePeriod(period, PGPulseChn)
    PulseGen.setTriggerModeSingle()
    PulseGen.setTriggerImpedanceTo50ohm()
    #PulseGen.setTriggerOutputPolarityPositive()
    PulseGen.setTriggerOutputPolarityNegative()
    #PulseGen.enableOutput(PGPulseChn)
    #PulseGen.arm()
    #PulseGen.disableOutput(PGPulseChn)

    Rcompl = []
    Ccompl = []

    stop = False

    PulseGen.setPulseVoltage(Vread, PGPulseChn)
    PulseGen.setPulseWidth(tread, PGPulseChn)
    PulseGen.enableTriggerOutput()

    Oscilloscope.writeAcquisitionTrigger("ExtLevel", TriggerLevel)

    VertScale = abs(Vread/4)
    Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)

    Oscilloscope.writeAcquisition("TriggerMode", "Stop")
    PulseGen.turnOnOutput(PGPulseChn)
    PulseGen.arm()

    Oscilloscope.writeAcquisition("TriggerMode", "Single")

    tstart = tm.time()
    while True:
        tm.sleep(refresh)
        try: 
            TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
        except:
            TrigMode = "" 
        if TrigMode.strip() == "Stopped" or tm.time()>tstart+timeout:
            break

    #PulseGen.turnOffOutput(PGPulseChn)
    PulseGen.dearm()
    #V = Oscilloscope.queryDataArray(OscPulChn)
    #I = np.divide(Oscilloscope.queryDataArray(OscGNDChn),OscInpImpedance)

    if PS:
        V = float(Oscilloscope.getMeasurementResults(1))
    else:
        V = Vread

    I = float(Oscilloscope.getMeasurementResults(2))/50

    R0 = abs(V/I)
    R = R0
    print("Resistance: ", R)
    Trac = [[R]]
    eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance",   "ValueName": 'R'})
    Trac = [[1/R]]  
    eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance",   "ValueName": 'C'})

    Rcompl.append(R)
    Ccompl.append(1/R)
    
    r = 1
    
    while r <= MaxPulses and float(R) >= Rform:
        print("Forming try", r)

        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
        if stop:    
            eChar.finished.put(True)
            break

        ####### Form
        PulseGen.setPulseVoltage(Vform, PGPulseChn)
        PulseGen.setPulseWidth(twidthForm)
        PulseGen.disableTriggerOutput()
        if Vform > 0:
            PulseGen.setTriggerOutputPolarityPositive()
        else:
            PulseGen.setTriggerOutputPolarityNegative()

        #tm.sleep(0.1)
        #PulseGen.turnOnOutput(chn=PGPulseChn)
        PulseGen.arm()
        #tm.sleep(1e-2)
        Oscilloscope.writeAcquisition("TriggerMode", "Single") 
        tstart = tm.time()
        while True:
            try: 
                TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
            except AttributeError:
                TrigMode = "" 
            if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                break
            tm.sleep(refresh)

        #PulseGen.turnOffOutput(chn=PGPulseChn)
        PulseGen.dearm()

        Oscilloscope.writeAcquisition("TriggerMode", "Stop")
        if Vread < 0:
            PulseGen.setTriggerOutputPolarityNegative()
        else:
            PulseGen.setTriggerOutputPolarityPositive()
        
        PulseGen.setPulseVoltage(Vread, PGPulseChn)
        PulseGen.setPulseWidth(tread, PGPulseChn)
        PulseGen.enableTriggerOutput()
        
        Oscilloscope.writeAcquisitionTrigger("ExtLevel", TriggerLevel)
        VertScale = abs(Vread/4)
        Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)

        #PulseGen.turnOnOutput(chn=PGPulseChn)
        PulseGen.arm()

        #tm.sleep(1e-2)
        Oscilloscope.writeAcquisition("TriggerMode", "Single")

        tstart = tm.time()
        while True:
            try: 
                TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
            except AttributeError:
                TrigMode = "" 
            if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                break

        PulseGen.setTriggerOutputPolarityNegative()
        #PulseGen.turnOffOutput(chn=PGPulseChn)
        PulseGen.dearm()
        
        if PS:
            V = float(Oscilloscope.getMeasurementResults(1))
        else:
            V = Vread
        I = float(Oscilloscope.getMeasurementResults(2))/50
        
        try:
            R = abs(V/I)
        except ZeroDivisionError:
            R = 1e12
        print("Resistance: ", R)

        Rcompl.append(R)
        Ccompl.append(1/R)

        Trac = [[R]]
        eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
        Trac = [[1/R]]  
        eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})

        r = r+1
        if stop:    
            eChar.finished.put(True)
            break
    

    PulseGen.turnOffOutput(chn=PGPulseChn)
    PulseGen.enableTriggerOutput()


    if not WriteHeader:
        header = eChar.getHeader("Combined")
    else:
        header = []

    header.insert(0,"TestParameter,Measurement.Type,RFFormingBNC765")
    
    header.append("Instrument,Oscilloscope,%s" %(OscName.strip()))
    header.append("Instrument,PulseGenerator,%s" %(PGName.strip()))
    header.append("Measurement,Vform, %.2e" %(Vform))
    header.append("Measurement,Forming Pulse Width, %.2e" %(twidthForm))
    header.append("Measurement,Forming Max Pulses,  %d" %(MaxPulses))
    header.append("Measurement,Forming Resistance,  %d" %(Rform))
    header.append("Measurement,Vread, %.2e" %(Vread))
    header.append("Measurement,Read Pulse Width, %.2e" %(tread))
    header.append("Measurement,PowerSplitter, %s" %(PS))

    if WriteHeader:
        header.extendHeader("Combined",header)


    newline = [None]*2
    newline[0] = 'DataName'
    newline[1] = 'Dimension'
    EntryNumReset = []
    EntryNumSet = []
    OutputData = []
    
    nMax = 0
    newline[0] = '%s, Entry #, FormingRGoal, FormRes, FormCond' %(newline[0])
    newline[1] = '%s, %d, %d, %d, %d' %(newline[1],len(Rcompl),len(Rcompl),len(Rcompl), len(Ccompl))

    OutputData = []
    data = 'DataValue'

    n = 0
    
    for k in range(len(Rcompl)):
        try:
            data = "DataValue, %d, %f, %f, %f" %(n+1, Rform, Rcompl[n], Ccompl[n])
        except IndexError:
            data = "%s, , , , " %(data)
        n = n+1
        OutputData.append(data)
        
    header1 = cp.deepcopy(header)
    header1.extend(newline)
    OutDa = cp.deepcopy(OutputData)
    
    eChar.writeDataToFile(header1, OutDa, Typ=Typ, startCyc=CycStart, endCyc=eChar.curCycle-1) 

    HRS =  eChar.dhValue(Rcompl[0], 'FirstHRS', DoYield=eChar.DoYield, Unit='ohm')
    LRS =  eChar.dhValue(Rcompl[-1], 'FirstLRS', DoYield=eChar.DoYield, Unit='ohm')
    row = eChar.dhAddRow([HRS,LRS],eChar.curCycle,eChar.curCycle)

    



###########################################################################################################################
def AnalogSwi_PGBNC765_Burst(eChar, PGPulseChnSetReset, PGPulseChnRead, OscPulseChn, OscGNDChn, BurstPulseNumSet, BurstPulseNumReset, ExpReadCurrent, Vset, Vreset, tperiod, twidthSet, twidthReset, Vread, tread, treaddelay, Round, Repetition, PowerSplitter, WriteHeader=True):
        
    """
    Applies voltage pulses via the Agilent 81110A pulse generator and measures the pulse response via a LeCroy oscilloscope
    Both Devices must be available. RF setup is recommended for rise times below 50ns. 
    PGPulseChnSetReset:     Pulse Channel of 765, (1, 2, 3, or 4)
    PGPulseChnRead: Pulse Channel of 765, (1, 2, 3, or 4) Cannot be the same as PGPulseChnSetReset
    OscPulseChn:    Oscilloscope Pulse Channel
    OscGNDChn:      Oscilloscope GND Channel
    Vset:           Set Voltage (V)
    Vreset:         Reset Voltage (V)
    settwidth:      Set pulse width (s)
    resettwidth:    Reset pulse width (s)
    Vread:          Read Voltage (V)
    tread:          Read pulse width(V)
    RstepSet:       Aimed resistance step per Set
    RstepReset:     Aimed resistance step per Reset
    MaxPulsesPerStepSet:    Maximum number of pulses per step until pulsing is stopped
    MaxPulsesPerStepReset:  Maximum number of pulses per step until pulsing is stopped
    Round           Round to next RstepSize
    Repetition:     Number of set/rest cycles
    PowerSplitter:  Is a power splitter in use? 
    WriteHeader: Enable/Disable writing the header into overlaying summary output files
    """

    #If PGPulseChnSetReset and PGPulseChnRead are the same then throw error
    if PGPulseChnSetReset == PGPulseChnRead:
        raise ValueError("PGPulseChnSetReset and PGPulseChnRead Cannot be the same channel")

    #If treaddelay is smaller than  twidthSet or twidthReset then throw error
    if treaddelay < (twidthSet or twidthReset):
        raise ValueError("Pulse Delay Read must be larger than both Set and Reset Pulse Width!")

    #if a power splitter is used the input voltage gets divided by two to measure the voltage as well. 
    PS = PowerSplitter
    if PS:
        Vset = 2*Vset
        Vreset = 2*Vreset
        Vread = 2*Vread

    Typ = 'IncrementalSwitching'
    
    VertScale = max([Vset,Vreset,Vread])*3
    VertScale2 = 50*ExpReadCurrent/2
    #HorScale = tread/2
    HorScaleSet = (BurstPulseNumSet*tperiod)/4
    HorScaleReset = (BurstPulseNumReset*tperiod)/4
    TriggerOutputLevel = 1.5
    TriggerLevel = TriggerOutputLevel/3
    ExtInpImpedance = 10000
    OscInpImpedance = 50
    OscPulChn = OscPulseChn
    timeout = 2
    refresh = 1e-1
    CycStart = eChar.curCycle

    Oscilloscope = eChar.getPrimaryLeCroyOscilloscope()
    PulseGen = eChar.PGBNC765

    OscName = Oscilloscope.getModel()
    PGName = PulseGen.getModel()

    OscPulAcInput = OscPulChn.strip()[1]
    OscGNDAcInput = OscGNDChn.strip()[1]
    OscPulChn = int(OscPulChn.strip()[0])
    OscGNDChn = int(OscGNDChn.strip()[0])

    Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "View", 1)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale2)
    #Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "Coupling", "DC50")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "EnhanceResType", "3bits")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "ActiveInput", "Input%s" %(OscGNDAcInput))

    Oscilloscope.writeAcquisitionChn(OscPulChn, "ClearSweeps")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "View", 1)
    #Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale2)
    Oscilloscope.writeAcquisitionChn(OscPulChn, "Coupling", "DC50")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "EnhanceResType", "3bits")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "ActiveInput", "Input%s" %(OscPulAcInput))

    Oscilloscope.writeAcquisitionHoriz("HorScale", HorScaleReset)
    Oscilloscope.writeAcquisitionHoriz("MaxSamples", 250000)
    #Oscilloscope.writeAcquisitionHoriz("MaxSamples", 4000000)
    #Oscilloscope.writeAcquisitionHoriz("MaxSamples", 2500)

    Oscilloscope.writeAcquisitionAuxOut("Amplitude", 2)
    Oscilloscope.writeAcquisitionAuxOut("AuxMode", "TriggerEnabled")

    Oscilloscope.writeAcquisitionTrigger("Edge.Source", "EXT")
    Oscilloscope.writeAcquisitionTrigger("Edge.Slope", "Either")

    Oscilloscope.writeAcquisitionTrigger("ExtLevel", TriggerLevel)

    # set measurements 
    Oscilloscope.clearAllMeasurements()
    Oscilloscope.clearAllMeasurementSweeps()
    Oscilloscope.setMeasurement(1, "Amplitude", OscPulChn)
    Oscilloscope.setMeasurement(2, "Amplitude", OscGNDChn)

    PulseGen.reset()
    PulseGen.clearTrigger()
    PulseGen.setTriggerSourceExternal()
    PulseGen.setTriggerThreshold(TriggerLevel)
    PulseGen.setTriggerOutputPolarityPositive()
    PulseGen.setPulseModeSingle(PGPulseChnSetReset)
    PulseGen.setPulseModeSingle(PGPulseChnRead)
    PulseGen.setTriggerModeSingle()
    #PulseGen.setTriggerModeBurst()
    PulseGen.setTriggerImpedanceTo50ohm()
    #PulseGen.enableOutput(PGPulseChn)
    #PulseGen.arm()
    #PulseGen.disableOutput(PGPulseChn)


    nReset = []
    Rreset = []
    RresGoal = []

    nSet = []
    Rset = []
    RsetGoal = []
    Rep = []
    RdelReset = []
    PercDelReset = []
    RdelSet = []
    PercDelSet = []

    Rcompl = []
    ncompl = []
    RgoalCompl = []
    Ccompl = []
    RdeltaCompl = []
    PercDelCompl = []

    stop = False
    RunRep = 1
    

    #PulseGen.setCycles(10,PGPulseChnSetReset)
    PulseGen.setPulseVoltage(Vread, PGPulseChnRead)
    PulseGen.setPulseWidth(tread, PGPulseChnRead)
    #PulseGen.setPulseDelay(ReadDelay, PGPulseChnSetReset, 1)
    PulseGen.enableTriggerOutput()

    VertScale = abs(Vread/4)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale)

    Oscilloscope.writeAcquisitionTrigger("ExtLevel", TriggerLevel)

    Oscilloscope.writeAcquisition("TriggerMode", "Stop")
    PulseGen.turnOnOutput(PGPulseChnRead)
    PulseGen.arm()

    Oscilloscope.writeAcquisition("TriggerMode", "Single")

    tstart = tm.time()
    while True:
        tm.sleep(refresh)
        try: 
            TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
        except:
            TrigMode = "" 
        if TrigMode.strip() == "Stopped" or tm.time()>tstart+timeout:
            break

    #PulseGen.turnOffOutput(PGPulseChn)
    PulseGen.turnOffOutput(PGPulseChnSetReset)
    PulseGen.turnOffOutput(PGPulseChnRead)
    PulseGen.dearm()
    
    #V = Oscilloscope.queryDataArray(OscPulChn)
    #I = np.divide(Oscilloscope.queryDataArray(OscGNDChn),OscInpImpedance)

    ###############################################################000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000###############################################################
    ############## Update this section for Burst pulsing!!!!! ####################################################################
            

    if PS:
        V = float(Oscilloscope.getMeasurementResults(OscGNDChn))
    else:
        V = Vread
    I = float(Oscilloscope.getMeasurementResults(2))/50

    R0 = abs(V/I)
    R = R0
    print("First R", R)
    Trac = [[R]]
    #eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
    Trac = [[1/R]]  
    #eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})
    '''
    Rcompl.append(R)
    Ccompl.append(1/R)
    ncompl.append(0)
    RgoalCompl.append(R)
    RdeltaCompl.append(0)
    PercDelCompl.append(0)   
    '''
    #write first value from Previous Read
    #Rreset.append(R)
    #nReset.append(0)
    #RresGoal[n].append(R)
    #RdelReset[n].append(0)
    #PercDelReset[n].append(0)

    #nReset.append([])
    #Rreset.append([])
    #RresGoal.append([])
    #nSet.append([])
    #Rset.append([])
    #RsetGoal.append([])
    #RdelReset.append([])
    #PercDelReset.append([])
    #RdelSet.append([])
    #PercDelSet.append([])
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale2)

    Rplot = []
    nplot = []
    RepititionNumArr = []

    for n in range(Repetition):
        print("n", n)

        
        '''
        # Set the first goal resistance to be hit 
        if Round:
            Rgoal = ma.ceil(R/RstepReset)*RstepReset
        else: 
            Rgoal = R + RstepReset
        '''
        r = 1
        Rwrote = False
        '''
        #write first value from Previous Read
        Rreset[n].append(R)
        nReset[n].append(0)
        #RresGoal[n].append(R)
        #RdelReset[n].append(0)
        #PercDelReset[n].append(0)
        '''
        #r = 1
        #print(MaxResistance, float(R), r, MaxPulsesPerStepReset, float(R) <= MaxResistance, r <= MaxPulsesPerStepReset)
       
        #print("r", r)

        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
        if stop:    
            eChar.finished.put(True)
            print("stop1")
            break
        
        Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
        Oscilloscope.writeAcquisitionHoriz("HorScale", HorScaleReset)

        ####### Reset ##############################################
        # Reset the Pulse Generator to default conditions to be replaced in following code
        PulseGen.reset()
        PulseGen.clearTrigger()
        PulseGen.setTriggerSourceExternal()
        PulseGen.setTriggerThreshold(TriggerLevel)
        PulseGen.setTriggerOutputPolarityPositive()
        PulseGen.setPulseModeSingle(PGPulseChnSetReset)
        PulseGen.setPulseModeSingle(PGPulseChnRead)
        PulseGen.setTriggerModeSingle()
        #PulseGen.setTriggerModeBurst()
        PulseGen.setTriggerImpedanceTo50ohm()

        if Vreset > 0:
            PulseGen.setTriggerOutputPolarityPositive()
        else:
            PulseGen.setTriggerOutputPolarityNegative()

        # Set paparmeters for burst pulse operation!
        PulseGen.setTriggerModeBurst()

        # Set the period of both channels
        #PulseGen.setPulsePeriod(15e-6, PGPulseChnSetReset)
        #PulseGen.setPulsePeriod(15e-6, PGPulseChnRead)
        #print("tperiod: ", tperiod)
        PulseGen.setPulsePeriod(tperiod, PGPulseChnSetReset)
        PulseGen.setPulsePeriod(tperiod, PGPulseChnRead)

        #print("Vreset: ", Vreset)
        #print("Vread: ", Vread)
        # Set voltage for reset/set and read
        PulseGen.setPulseVoltage(Vreset, PGPulseChnSetReset)
        PulseGen.setPulseVoltage(Vread, PGPulseChnRead)

        #print("twidthReset: ", twidthReset)
        #print("tread: ", tread)
        # Set pulse width for reset/set and read
        PulseGen.setPulseWidth(twidthReset, PGPulseChnSetReset)
        PulseGen.setPulseWidth(tread, PGPulseChnRead)

        # Delay for read pulse
        #PulseGen.setDelay(treaddelay, PGPulseChnRead)
        PulseGen.setDelay(treaddelay, PGPulseChnRead)

        # Set number of burst pulses
        PulseGen.setCycles(BurstPulseNumReset, PGPulseChnSetReset)
        PulseGen.setCycles(BurstPulseNumReset, PGPulseChnRead)

        # 
        #PulseGen.s
        #PulseGen.setCycles(10,PGPulseChnSetReset)
        #PulseGen.setPulseVoltage(Vread, PGPulseChnSetReset)
        #PulseGen.setPulseWidth(tread, PGPulseChnSetReset)
        #PulseGen.setPulseDelay(ReadDelay, PGPulseChnSetReset, 1)
        PulseGen.enableTriggerOutput()

        #PulseGen.disableTriggerOutput()
        #tm.sleep(0.1)

        # Turn on both Channels used in Program
        PulseGen.turnOnOutput(PGPulseChnSetReset)
        PulseGen.turnOnOutput(PGPulseChnRead)
        #PulseGen.turnOnOutput(chn=PGPulseChn)
        PulseGen.arm()
        

        DataReads = []

        Oscilloscope.writeAcquisition("TriggerMode", "Single") 
        #Oscilloscope.writeAcquisition("TriggerMode", "Normal")
        #tm.sleep(1) 
        tstart = tm.time()
        while True:
            try: 
                TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                DataReads = Oscilloscope.queryDataArray(OscGNDChn)
                deltat = Oscilloscope.queryDataTimePerPoint()
                #print("ReRAMLength:", len(DataReads))
                #print("deltat", deltat)
                #DataReads.append(DataReadsOut)
                #print("DataReads: ", DataReads)
                #print("DataReads!!!!")
            except AttributeError:
                TrigMode = "" 
            if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                break
            tm.sleep(refresh)
        
        PulseGen.dearm()

        Oscilloscope.writeAcquisition("TriggerMode", "Stop")
        Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
        
        ##############################################################################################################################
        ############## Update this section for Burst pulsing!!!!! ####################################################################
        if PS:
            #DataReads = Oscilloscope.queryDataArray(1)
            #eChar.plotIVData({"Add": True, "Traces":DataReads, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Voltage (V)', 'Title': "Resistance Change",   "ValueName": 'V'})
            er = 1
            #V = float(Oscilloscope.getMeasurementResults(1))


        else:
            V = Vread

        V = Vread
        ####### Data Splitting ###############
        DataPoints = []
        VoltageOutputArray = []
        A = np.array(DataReads)
        #print("Length of Array A: ", len(A))
        B = A[len(A)//2:]
        #print("Length of Array B: ", len(B))
        C = A[:len(A)//2]
        Cavg = np.mean(C)
        print("Cavg: ", Cavg)
        
        #DataReads
        DataPoints1 = (tperiod/2)/float(deltat)
        DataPoints1 = int(DataPoints1)
        DataPointsPeriodLength = int(tperiod/float(deltat))
        #print("Value of first pulse: ", B[DataPoints1])
        
        for f in range(BurstPulseNumReset):
            DataPointsChange = int(DataPoints1 + f*DataPointsPeriodLength)
            
            DataPoints.append(DataPointsChange)
            BvalueReset = B[DataPoints[f]]
            BvalueResetAdjusted = BvalueReset - Cavg
            #VoltageOutputArray.append(B[DataPoints[f]])
            VoltageOutputArray.append(BvalueResetAdjusted)

        #print("DataPoints: ", DataPoints)
        #print("VoltageOutputArray: ", VoltageOutputArray)

        #I = float(Oscilloscope.getMeasurementResults(2))/50

        #I = DataPoints/50
        #I = np.divide(DataPoints, 50) 
        I = np.divide(VoltageOutputArray, 50) 

        #print("Current: ", I)

        Varray = np.tile(V, len(I))
        R = abs(Varray/I)
        

        #R = np.divide(I, 1/V) 
        #print("rReset: ", R)
        #print("Rreset[n]: ", Rreset[n])

        
        #R = abs(V/I)
        #print("rR", R, " goal ", Rgoal)

        #Rcompl.append(R)
        #Ccompl.append(1/R)
        #ncompl.append(r)
        #RgoalCompl.append(Rgoal)
        #RdeltaCompl.append(abs(R-Rgoal))
        #PercDelCompl.append(abs((R-Rgoal)/R))


        arr1 = np.arange(1, (BurstPulseNumReset+1))
        #print("arr: ", arr)
        ### Convert to List ####
        #Rlist1 = R.tolist()
        #print("Rlist1: ", Rlist1)
        #arrlist1 = arr.tolist()

        #if R > Rgoal:
        if True:

            for e in range(len(R)):
                #Rreset.append(R[e])
                
                Rcompl.append(R[e])
                #print("Rreset[n]: ", Rreset[n])
                #nReset.append(arr[e])
                
                ncompl.append(arr1[e])
                #print("nReset[n]: ", nReset[n])
                #RresGoal[n].append(Rgoal)
                #RdelReset[n].append(abs(R-Rgoal))
                #PercDelReset[n].append(abs((R-Rgoal)/R))
                if e == range(len(R)):
                    Rreset[n].append(R[e])
                    nReset[n].append(arr1[e])
                #r = 1
                #Rgoal = Rgoal + RstepReset
                Trac = [[R[e]]]
                eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Pulse Number', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
                #Trac = [[1/R]]  
                #eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})
            Rwrote = True
            #print(DataReads)
            #Rreads = B
            #print(Rreads)
            #Trac = Rreads
            #eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Pulse Number', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
                
        else:
            r = r+1
        
        PulseGen.turnOffOutput(PGPulseChnSetReset)
        PulseGen.turnOffOutput(PGPulseChnRead)
        #print("Rreset[n]: ", Rreset[n])
        ############################ Set ########################
        #########################################################
        r = 1
        Rwrote = False

        #write first value from Previous Read ## Don't need this with burst pulsing for between set and reset
        #Rset[n].append(R)
        #nSet[n].append(0)
        #RresGoal[n].append(R)
        #RdelReset[n].append(0)
        #PercDelReset[n].append(0)

        #r = 1
        #print(MaxResistance, float(R), r, MaxPulsesPerStepReset, float(R) <= MaxResistance, r <= MaxPulsesPerStepReset)
       
        #print("r", r)

        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
        if stop:    
            eChar.finished.put(True)
            break
        
        Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
        Oscilloscope.writeAcquisitionHoriz("HorScale", HorScaleSet)

        ####### Set ##############################################

        # Reset the Pulse Generator to default conditions to be replaced in following code
        PulseGen.reset()
        PulseGen.clearTrigger()
        PulseGen.setTriggerSourceExternal()
        PulseGen.setTriggerThreshold(TriggerLevel)
        PulseGen.setTriggerOutputPolarityPositive()
        PulseGen.setPulseModeSingle(PGPulseChnSetReset)
        PulseGen.setPulseModeSingle(PGPulseChnRead)
        PulseGen.setTriggerModeSingle()
        #PulseGen.setTriggerModeBurst()
        PulseGen.setTriggerImpedanceTo50ohm()

        if Vset > 0:
            PulseGen.setTriggerOutputPolarityPositive()
        else:
            PulseGen.setTriggerOutputPolarityNegative()

        # Set paparmeters for burst pulse operation!
        PulseGen.setTriggerModeBurst()

        # Set the period of both channels
        #PulseGen.setPulsePeriod(15e-6, PGPulseChnSetReset)
        #PulseGen.setPulsePeriod(15e-6, PGPulseChnRead)
        #print("tperiod: ", tperiod)
        PulseGen.setPulsePeriod(tperiod, PGPulseChnSetReset)
        PulseGen.setPulsePeriod(tperiod, PGPulseChnRead)

        print("Vreset: ", Vreset)
        print("Vset: ", Vset)
        print("Vread: ", Vread)
        # Set voltage for reset/set and read
        PulseGen.setPulseVoltage(Vset, PGPulseChnSetReset)
        PulseGen.setPulseVoltage(Vread, PGPulseChnRead)

        #print("twidthReset: ", twidthReset)
        #print("tread: ", tread)
        # Set pulse width for reset/set and read
        PulseGen.setPulseWidth(twidthSet, PGPulseChnSetReset)
        PulseGen.setPulseWidth(tread, PGPulseChnRead)

        # Delay for read pulse
        #PulseGen.setDelay(treaddelay, PGPulseChnRead)
        PulseGen.setDelay(treaddelay, PGPulseChnRead)

        # Set number of burst pulses
        PulseGen.setCycles(BurstPulseNumSet, PGPulseChnSetReset)
        PulseGen.setCycles(BurstPulseNumSet, PGPulseChnRead)

        # 
        #PulseGen.s
        #PulseGen.setCycles(10,PGPulseChnSetReset)
        #PulseGen.setPulseVoltage(Vread, PGPulseChnSetReset)
        #PulseGen.setPulseWidth(tread, PGPulseChnSetReset)
        #PulseGen.setPulseDelay(ReadDelay, PGPulseChnSetReset, 1)
        PulseGen.enableTriggerOutput()

        #PulseGen.disableTriggerOutput()
        #tm.sleep(0.1)

        # Turn on both Channels used in Program
        PulseGen.turnOnOutput(PGPulseChnSetReset)
        PulseGen.turnOnOutput(PGPulseChnRead)
        #PulseGen.turnOnOutput(chn=PGPulseChn)
        PulseGen.arm()
       

        DataReads = []

        Oscilloscope.writeAcquisition("TriggerMode", "Single") 
        #Oscilloscope.writeAcquisition("TriggerMode", "Normal") 
        #tm.sleep(1)
        tstart = tm.time()
        while True:
            try: 
                TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                DataReads = Oscilloscope.queryDataArray(OscGNDChn)
                deltat = Oscilloscope.queryDataTimePerPoint()
                #print("ReRAMLength:", len(DataReads))
                #print("deltat", deltat)
                #DataReads.append(DataReadsOut)
                #print("DataReads: ", DataReads)
                #print("DataReads!!!!")
            except AttributeError:
                TrigMode = "" 
            if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                break
            tm.sleep(refresh)
        #PulseGen.turnOffOutput(chn=PGPulseChn)
        PulseGen.dearm()

        Oscilloscope.writeAcquisition("TriggerMode", "Stop")
        Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
        
        ##############################################################################################################################
        ############## Update this section for Burst pulsing!!!!! ####################################################################
        if PS:
            #DataReads = Oscilloscope.queryDataArray(1)
            #eChar.plotIVData({"Add": True, "Traces":DataReads, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Voltage (V)', 'Title': "Resistance Change",   "ValueName": 'V'})
            er = 1
            #V = float(Oscilloscope.getMeasurementResults(1))


        else:
            V = Vread

        #print("SET!!!!!")

        V = Vread
        ####### Data Splitting ###############
        DataPoints = []
        VoltageOutputArray = []
        A = np.array(DataReads)
        B = A[len(A)//2:]
        #C = A[:len(A)//2]
        #print("Length of Array: ", len(B))
        C = A[:len(A)//2]
        Cavg = np.mean(C)
        print("Cavg: ", Cavg)
        
        #print("Min voltage Array B: ", min(B))
        #print("Min voltage Array C: ", min(C))
        #print("Max voltage Array B: ", max(B))
        #print("Max voltage Array C: ", max(C))
        #DataReads
        DataPoints1 = (tperiod/2)/float(deltat)
        DataPoints1 = int(DataPoints1)
        DataPointsPeriodLength = int(tperiod/float(deltat))
        #print("Value of first pulse: ", B[DataPoints1])
        
        for f in range(BurstPulseNumSet):
            DataPointsChange = int(DataPoints1 + f*DataPointsPeriodLength)
            
            DataPoints.append(DataPointsChange)
            #VoltageOutputArray.append(B[DataPoints[f]])
            
            BvalueSet = B[DataPoints[f]]
            BvalueSetAdjusted = BvalueSet - Cavg
            #VoltageOutputArray.append(B[DataPoints[f]])
            VoltageOutputArray.append(BvalueSetAdjusted)

        #print("DataPoints: ", DataPoints)
        #print("VoltageOutputArray: ", VoltageOutputArray)

        #I = float(Oscilloscope.getMeasurementResults(2))/50

        #I = DataPoints/50
        #I = np.divide(DataPoints, 50) 
        I = np.divide(VoltageOutputArray, 50) 

        #print("Current: ", I)

        Varray = np.tile(V, len(I))
        R = abs(Varray/I)
        

        #R = np.divide(I, 1/V) 
        #print("rSet: ", R)
        #print("Rset: ", Rset)
        
        #R = abs(V/I)
        #print("rR", R, " goal ", Rgoal)

        #Rcompl.append(R)
        #Ccompl.append(1/R)
        #ncompl.append(r)
        #RgoalCompl.append(Rgoal)
        #RdeltaCompl.append(abs(R-Rgoal))
        #PercDelCompl.append(abs((R-Rgoal)/R))


        arr2 = np.arange(1, (BurstPulseNumSet+1))
        #print("arr: ", arr)
        ### Convert to List ####
        #Rlist1 = R.tolist()
        #print("Rlist1: ", Rlist1)
        #arrlist1 = arr.tolist()

        #if R > Rgoal:
        if True:

            for e in range(len(R)):
                #Rset.append(R[e])
                #Rset[n].extend(R[e])
                Rcompl.append(R[e])
                #print("Rset[n]: ", Rset[n])
                #nSet.append(arr[e])
                ncompl.append(arr2[e])
                #print("nSet[n]: ", nSet[n])
                #RresGoal[n].append(Rgoal)
                #RdelReset[n].append(abs(R-Rgoal))
                #PercDelReset[n].append(abs((R-Rgoal)/R))

                if e == range(len(R)):
                    Rset[n].append(R[e])
                    nSet[n].append(arr2[e])

                #r = 1
                #Rgoal = Rgoal + RstepReset
                Trac = [[R[e]]]
                eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Pulse Number', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
                #Trac = [[1/R]]  
                #eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})
            Rwrote = True
        else:
            r = r+1
        
        RepititionNumArrLen = len(arr1) + len(arr2)
        #RepititionNumArr1 = []
        #RepititionNumArr1 = np.repeat(n+1, (RepititionNumArrLen))
        for q in range(RepititionNumArrLen):
            RepititionNumArr.append(int(n+1))
        #print("RepititionNumArr: ", RepititionNumArr)


    
    PulseGen.dearm()
    PulseGen.turnOffOutput(PGPulseChnSetReset)
    PulseGen.turnOffOutput(PGPulseChnRead)
    #PGPulseChnSetReset == PGPulseChnRead

    ############################################# Header ######################################################
    if not WriteHeader:
        header = eChar.getHeader("Combined")
    else:
        header = []

    header.insert(0,"TestParameter,Measurement.Type,HFincrementalPulsing81110A")
    
    header.append("Instrument,Oscilloscope,%s" %(OscName.strip()))
    header.append("Instrument,PulseGenerator,%s" %(PGName.strip()))
    header.append("Measurement,Vset, %.2e" %(Vset))
    header.append("Measurement,Set Pulse Width, %.2e" %(twidthSet))
    header.append("Measurement,Set Burst Pulse Number, %.2e" %(BurstPulseNumSet))
    #header.append("Measurement,Set Max Pulses Per Step,  %d" %(MaxPulsesPerStepSet))
    #header.append("measurement,Set Resistance Step, %.2f" %( RstepSet))
    header.append("Measurement,Vreset, %.2e" %(Vreset))
    header.append("Measurement,Reset Pulse Width, %.2e" %(twidthReset))
    header.append("Measurement,Reset Burst Pulse Number, %.2e" %(BurstPulseNumReset))
    #header.append("Measurement,Reset Max Pulses Per Step,  %d" %(MaxPulsesPerStepReset))
    #header.append("measurement,Reset Resistance Step, %.2e" %( RstepReset))
    header.append("Measurement,Vread, %.2e" %(Vread))
    header.append("Measurement,Read Pulse Width, %.2e" %(tread))
    header.append("Measurement,Pulse Period Width, %.2e" %(tperiod))
    header.append("Measurement,Read Pulse Delay, %.2e" %(treaddelay))
    header.append("Measurement,Round, %s" %(Round))
    header.append("Measurement,Repetition, %s" %(Repetition))
    header.append("Measurement,PowerSplitter, %s" %(PS))

    if WriteHeader:
        header.extendHeader("Combined",header)

    newline = [None]*3
    newline[0] = 'DataName'
    newline[1] = 'Dimension'
    newline[2] = 'Repetition'
    EntryNumReset = []
    EntryNumSet = []
    OutputData = []
    
    nMax = 0
    #print("Length Rset: ", len(Rset))
    #print("Rreset: ", Rreset)
    #print("nReset: ", nReset)
    #print("Rset: ", Rset)
    #print("nSet: ", nSet)
    '''
    for n in range(len(Rset)):
        #CondReset = list(np.reciprocal(Rreset[n]))
        #CondSet = list(np.reciprocal(Rset[n]))
        
        #newline[0] = '%s,Entry #, Res. Goal, Res., # of Pulses, Res. Dev. (value), Res. Dev. (perc), Res. Conductance (s)' %(newline[0])
        newline[0] = '%s,Entry #, # of Pulses, Reset Res.' %(newline[0])
        #newline[1] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[1],len(RresGoal[n]),len(RresGoal[n]), len(Rreset[n]), len(nReset[n]), len(RdelReset[n]), len(PercDelReset[n]), len(CondReset))
        newline[1] = '%s, %d, %d' %(newline[1], len(nReset), len(Rreset))
        #newline[2] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[2],n+1,n+1,n+1,n+1,n+1,n+1,n+1)
        newline[2] = '%s, %d, %d' %(newline[2],n+1,n+1)

        if EntryNumReset == []:
            EntryNumReset.append(list(range(1,1+len(RresGoal[n]),1)))
        else:
            EntryNumReset.append(list(range(EntryNumSet[-1][-1]+1,EntryNumSet[-1][-1]+1+len(RresGoal[n]),1)))

        #newline[0] = '%s,Entry #, Set. Goal, Set., # of Pulses, Set. Dev. (value), Set. Dev. (perc), Set. Conductance (s)' %(newline[0])
        newline[0] = '%s,Entry #,  # of Pulses, Set Res.' %(newline[0])
        #newline[1] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[1],len(RsetGoal[n]),len(RsetGoal[n]), len(Rset[n]), len(nSet[n]), len(RdelSet[n]), len(PercDelSet[n]), len(CondSet))
        newline[1] = '%s, %d, %d' %(newline[1], len(nSet), len(Rset))
        #newline[2] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[2],n+1,n+1,n+1,n+1,n+1,n+1,n+1)
        newline[2] = '%s, %d, %d' %(newline[2],n+1,n+1)

        #EntryNumSet.append(list(range(EntryNumReset[-1][-1]+1,EntryNumReset[-1][-1]+1+len(RresGoal[n]),1)))
    
    CurMax = max(len(Rreset[n]), len(nReset[n]), len(Rset[n]), len(nSet[n]))

    if CurMax > nMax:
        nMax = CurMax
    
        

    OutputData = []
    for n in range(nMax):
        data = 'DataValue'
        for k in range(len(Rset)):
            try:
                #CondReset = float(1/Rreset[k][n])
                data = "%s, %f, %f, %f" %(data, EntryNumReset[k][n],nReset[k][n], Rreset[k][n])
            except IndexError:
                data = "%s, , , " %(data)
            try:
                #CondSet = float(1/Rset[k][n])
                data = "%s, %f, %f, %f" %(data, EntryNumSet[k][n], nSet[k][n], Rset[k][n])
            except IndexError:
                data = "%s, , , " %(data)
        OutputData.append(data)
        
    header1 = cp.deepcopy(header)
    header1.extend(newline)
    
    eChar.writeDataToFile(header1, OutputData, Typ=Typ, startCyc=CycStart, endCyc=eChar.curCycle-1)
    '''

    newline = [None]*2
    #newline[0] = 'DataName, R Goal, R, # of Pulses, Deviation (value), Deviation (perc), Conductance (s)'
    newline[0] = 'DataName, Repition #, # of Pulses, R'
    newline[1] = 'Dimension, %d, %d, %d' %(len(RepititionNumArr), len(ncompl), len(Rcompl))
    '''
    print("len(RepititionNumArr): ", len(RepititionNumArr))
    print("len(ncompl): ", len(ncompl))
    print("len(Rcompl): ", len(Rcompl))
    print("RepititionNumArr: ", RepititionNumArr)
    print("ncompl: ", ncompl)
    print("Rcompl: ", Rcompl)
    '''
    OutputData2 = []
    for n in range(len(Rcompl)):
        data = 'DataValue, %d, %d, %f' %(RepititionNumArr[n], ncompl[n], Rcompl[n])
        OutputData2.append(data)
    
    header.extend(newline)
    Typ2 = "Compl_%s" %(Typ)
    
    eChar.writeDataToFile(header, OutputData2, Typ=Typ2, startCyc=CycStart, endCyc=eChar.curCycle-1)
    '''
    r0 = R0
    Rdelta = []
    Rdelta.append(Rreset[0][-1] - R0)
    for r, s in zip(Rreset, Rset):
        Rdelta.append(r[-1]-s[-1])
    

    AvgSetPul =  eChar.dhValue([], 'FirstHRS', DoYield=False, Unit='ohm')
    AvgResetPul =  eChar.dhValue([], 'FirstLRS', DoYield=False, Unit='ohm')

    for n in nSet:
        AvgSetPul.extend(n)

    for n in nReset:
        AvgResetPul.extend(n)

    #AvgRratio =  eChar.dhValue(Rdelta, 'ImaxForm', DoYield=eChar.DoYield, Unit='A')
    r#ow = eChar.dhAddRow([AvgSetPul,AvgResetPul,AvgRratio],eChar.curCycle,eChar.curCycle)

    #
    '''



###########################################################################################################################
def AnalogSwi_PGBNC765_BurstRead(eChar, PGPulseChnSetReset, PGPulseChnRead, OscPulseChn, OscGNDChn, BurstPulseNumSet, BurstPulseNumReset, BurstPulseNumSetRead, BurstPulseNumResetRead, ExpReadCurrent, Vset, Vreset, tperiodset, tperiodreset, tperiodsetread, tperiodresetread, twidthSet, twidthReset, Vread, tread, treaddelayreset, treaddelayset, Round, Repetition, SetReps, ResetReps, PowerSplitter, WriteHeader=True):
        
    """
    Applies voltage pulses via the Agilent 81110A pulse generator and measures the pulse response via a LeCroy oscilloscope
    Both Devices must be available. RF setup is recommended for rise times below 50ns. 
    PGPulseChnSetReset:     Pulse Channel of 765, (1, 2, 3, or 4)
    PGPulseChnRead: Pulse Channel of 765, (1, 2, 3, or 4) Cannot be the same as PGPulseChnSetReset
    OscPulseChn:    Oscilloscope Pulse Channel
    OscGNDChn:      Oscilloscope GND Channel
    Vset:           Set Voltage (V)
    Vreset:         Reset Voltage (V)
    settwidth:      Set pulse width (s)
    resettwidth:    Reset pulse width (s)
    Vread:          Read Voltage (V)
    tread:          Read pulse width(V)
    RstepSet:       Aimed resistance step per Set
    RstepReset:     Aimed resistance step per Reset
    MaxPulsesPerStepSet:    Maximum number of pulses per step until pulsing is stopped
    MaxPulsesPerStepReset:  Maximum number of pulses per step until pulsing is stopped
    Round           Round to next RstepSize
    Repetition:     Number of set/rest cycles
    PowerSplitter:  Is a power splitter in use? 
    WriteHeader: Enable/Disable writing the header into overlaying summary output files
    """

    #If PGPulseChnSetReset and PGPulseChnRead are the same then throw error
    if PGPulseChnSetReset == PGPulseChnRead:
        raise ValueError("PGPulseChnSetReset and PGPulseChnRead Cannot be the same channel")

    #If treaddelayreset is smaller than tperiodreset*BurstPulseNumReset then throw error
    if treaddelayreset < (tperiodreset*BurstPulseNumReset):
        raise ValueError("Pulse Delay Read must be larger than Total Number of Reset Pulses multiplied by reset period!")

    #If treaddelayset is smaller than tperiodset*BurstPulseNumSet then throw error
    if treaddelayset < (tperiodset*BurstPulseNumSet):
        raise ValueError("Pulse Delay Read must be larger than Total Number of Set Pulses multiplied by set period!")

    #If treaddelayreset is larger than tperiodresetread then throw error
    if treaddelayreset > (tperiodresetread):
        raise ValueError("Pulse Delay Read must be less than total reset read period!")

    #If treaddelayset is larger than tperiodsetread then throw error
    if treaddelayset > (tperiodsetread):
        raise ValueError("Pulse Delay Read must be less than total set read period!")

    #If treaddelayset is larger than tperiodsetread then throw error
    if 3*(tperiodset*BurstPulseNumSet) > (tperiodsetread):
        raise ValueError("Pulse Set Read Period must be at least 3 times longer than total set pulse train length to avoid overlap and for data collection!")

    #If treaddelayset is larger than tperiodsetread then throw error
    if 3*(tperiodreset*BurstPulseNumReset) > (tperiodresetread):
        raise ValueError("Pulse Reset Read Period must be at least 3 times longer than total reset pulse train length to avoid overlap and for data collection!")

    #if a power splitter is used the input voltage gets divided by two to measure the voltage as well. 
    PS = PowerSplitter
    if PS:
        Vset = 2*Vset
        Vreset = 2*Vreset
        Vread = 2*Vread

    Typ = 'IncrementalSwitching'
    
    VertScale = max([Vset,Vreset,Vread])*3
    VertScale2 = 50*ExpReadCurrent/2
    #HorScale = tread/2
    HorScaleSet = (BurstPulseNumSet*tperiodset)/4
    HorScaleReset = (BurstPulseNumReset*tperiodreset)/4
    HorScaleResetRead = (BurstPulseNumResetRead*tperiodresetread)/4
    HorScaleSetRead = (BurstPulseNumSetRead*tperiodsetread)/4
    TriggerOutputLevel = 1.5
    TriggerLevel = TriggerOutputLevel/3
    ExtInpImpedance = 10000
    OscInpImpedance = 50
    OscPulChn = OscPulseChn
    timeout = 2
    refresh = 1e-1
    CycStart = eChar.curCycle

    Oscilloscope = eChar.getPrimaryLeCroyOscilloscope()
    PulseGen = eChar.PGBNC765

    OscName = Oscilloscope.getModel()
    PGName = PulseGen.getModel()

    OscPulAcInput = OscPulChn.strip()[1]
    OscGNDAcInput = OscGNDChn.strip()[1]
    OscPulChn = int(OscPulChn.strip()[0])
    OscGNDChn = int(OscGNDChn.strip()[0])

    Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "View", 1)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale2)
    #Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "Coupling", "DC50")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "EnhanceResType", "3bits")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "ActiveInput", "Input%s" %(OscGNDAcInput))

    Oscilloscope.writeAcquisitionChn(OscPulChn, "ClearSweeps")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "View", 1)
    Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)
    Oscilloscope.writeAcquisitionChn(OscPulChn, "Coupling", "DC50")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "EnhanceResType", "3bits")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "ActiveInput", "Input%s" %(OscPulAcInput))

    Oscilloscope.writeAcquisitionHoriz("HorScale", HorScaleResetRead)
    Oscilloscope.writeAcquisitionHoriz("MaxSamples", 250000)
    #Oscilloscope.writeAcquisitionHoriz("MaxSamples", 4000000)

    Oscilloscope.writeAcquisitionAuxOut("Amplitude", 2)
    Oscilloscope.writeAcquisitionAuxOut("AuxMode", "TriggerEnabled")

    Oscilloscope.writeAcquisitionTrigger("Edge.Source", "EXT")
    Oscilloscope.writeAcquisitionTrigger("Edge.Slope", "Either")

    Oscilloscope.writeAcquisitionTrigger("ExtLevel", TriggerLevel)

    # set measurements 
    Oscilloscope.clearAllMeasurements()
    Oscilloscope.clearAllMeasurementSweeps()
    Oscilloscope.setMeasurement(1, "Amplitude", OscPulChn)
    Oscilloscope.setMeasurement(2, "Amplitude", OscGNDChn)

    PulseGen.reset()
    PulseGen.clearTrigger()
    PulseGen.setTriggerSourceExternal()
    PulseGen.setTriggerThreshold(TriggerLevel)
    PulseGen.setTriggerOutputPolarityPositive()
    PulseGen.setPulseModeSingle(PGPulseChnSetReset)
    PulseGen.setPulseModeSingle(PGPulseChnRead)
    PulseGen.setTriggerModeSingle()
    #PulseGen.setTriggerModeBurst()
    PulseGen.setTriggerImpedanceTo50ohm()
    #PulseGen.enableOutput(PGPulseChn)
    #PulseGen.arm()
    #PulseGen.disableOutput(PGPulseChn)


    nReset = []
    Rreset = []
    RresGoal = []

    nSet = []
    Rset = []
    RsetGoal = []
    Rep = []
    RdelReset = []
    PercDelReset = []
    RdelSet = []
    PercDelSet = []

    Rcompl = []
    ncompl = []
    RgoalCompl = []
    Ccompl = []
    RdeltaCompl = []
    PercDelCompl = []

    stop = False
    RunRep = 1
    

    #PulseGen.setCycles(10,PGPulseChnSetReset)
    PulseGen.setPulseVoltage(Vread, PGPulseChnRead)
    PulseGen.setPulseWidth(tread, PGPulseChnRead)
    #PulseGen.setPulseDelay(ReadDelay, PGPulseChnSetReset, 1)
    PulseGen.enableTriggerOutput()

    VertScale = abs(Vread/4)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale)

    Oscilloscope.writeAcquisitionTrigger("ExtLevel", TriggerLevel)

    Oscilloscope.writeAcquisition("TriggerMode", "Stop")
    PulseGen.turnOnOutput(PGPulseChnRead)
    PulseGen.arm()

    Oscilloscope.writeAcquisition("TriggerMode", "Single")

    tstart = tm.time()
    while True:
        tm.sleep(refresh)
        try: 
            TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
        except:
            TrigMode = "" 
        if TrigMode.strip() == "Stopped" or tm.time()>tstart+timeout:
            break

    #PulseGen.turnOffOutput(PGPulseChn)
    PulseGen.turnOffOutput(PGPulseChnSetReset)
    PulseGen.turnOffOutput(PGPulseChnRead)
    PulseGen.dearm()
    
    #V = Oscilloscope.queryDataArray(OscPulChn)
    #I = np.divide(Oscilloscope.queryDataArray(OscGNDChn),OscInpImpedance)

    ###############################################################000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000###############################################################
    ############## Update this section for Burst pulsing!!!!! ####################################################################
            

    if PS:
        V = float(Oscilloscope.getMeasurementResults(OscGNDChn))
    else:
        V = Vread
    I = float(Oscilloscope.getMeasurementResults(2))/50

    R0 = abs(V/I)
    R = R0
    print("First R", R)
    Trac = [[R]]
    #eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
    Trac = [[1/R]]  
    #eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})
    '''
    Rcompl.append(R)
    Ccompl.append(1/R)
    ncompl.append(0)
    RgoalCompl.append(R)
    RdeltaCompl.append(0)
    PercDelCompl.append(0)   
    '''
    #write first value from Previous Read
    #Rreset.append(R)
    #nReset.append(0)
    #RresGoal[n].append(R)
    #RdelReset[n].append(0)
    #PercDelReset[n].append(0)

    #nReset.append([])
    #Rreset.append([])
    #RresGoal.append([])
    #nSet.append([])
    #Rset.append([])
    #RsetGoal.append([])
    #RdelReset.append([])
    #PercDelReset.append([])
    #RdelSet.append([])
    #PercDelSet.append([])
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale2)
    #Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale)

    Rplot = []
    nplot = []
    RepititionNumArr = []

    for n in range(Repetition):
        print("n", n)
        #for j in range(TotalPulses):
        
        '''
        # Set the first goal resistance to be hit 
        if Round:
            Rgoal = ma.ceil(R/RstepReset)*RstepReset
        else: 
            Rgoal = R + RstepReset
        '''
        r = 1
        Rwrote = False
        '''
        #write first value from Previous Read
        Rreset[n].append(R)
        nReset[n].append(0)
        #RresGoal[n].append(R)
        #RdelReset[n].append(0)
        #PercDelReset[n].append(0)
        '''
        #r = 1
        #print(MaxResistance, float(R), r, MaxPulsesPerStepReset, float(R) <= MaxResistance, r <= MaxPulsesPerStepReset)
       
        #print("r", r)

        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
        if stop:    
            eChar.finished.put(True)
            break
        
        for h in range(ResetReps):


            Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
            Oscilloscope.writeAcquisitionHoriz("HorScale", HorScaleResetRead)

            ####### Reset ##############################################
            # Reset the Pulse Generator to default conditions to be replaced in following code
            PulseGen.reset()
            PulseGen.clearTrigger()
            PulseGen.setTriggerSourceExternal()
            PulseGen.setTriggerThreshold(TriggerLevel)
            PulseGen.setTriggerOutputPolarityPositive()
            PulseGen.setPulseModeSingle(PGPulseChnSetReset)
            PulseGen.setPulseModeSingle(PGPulseChnRead)
            PulseGen.setTriggerModeSingle()
            #PulseGen.setTriggerModeBurst()
            PulseGen.setTriggerImpedanceTo50ohm()


            # Set paparmeters for burst pulse operation!
            PulseGen.setTriggerModeBurst()

            # Set the period of both channels
            #PulseGen.setPulsePeriod(15e-6, PGPulseChnSetReset)
            #PulseGen.setPulsePeriod(15e-6, PGPulseChnRead)
            #print("tperiod: ", tperiod)
            PulseGen.setPulsePeriod(tperiodreset, PGPulseChnSetReset)
            PulseGen.setPulsePeriod(tperiodresetread, PGPulseChnRead)

            #print("Vreset: ", Vreset)
            #print("Vread: ", Vread)
            # Set voltage for reset/set and read
            PulseGen.setPulseVoltage(Vreset, PGPulseChnSetReset)
            PulseGen.setPulseVoltage(Vread, PGPulseChnRead)

            #print("twidthReset: ", twidthReset)
            #print("tread: ", tread)
            # Set pulse width for reset/set and read
            PulseGen.setPulseWidth(twidthReset, PGPulseChnSetReset)
            PulseGen.setPulseWidth(tread, PGPulseChnRead)

            # Delay for read pulse
            #PulseGen.setDelay(treaddelay, PGPulseChnRead)
            PulseGen.setDelay(treaddelayreset, PGPulseChnRead)

            # Set number of burst pulses
            PulseGen.setCycles(BurstPulseNumReset, PGPulseChnSetReset)
            PulseGen.setCycles(BurstPulseNumResetRead, PGPulseChnRead)

            # 
            #PulseGen.s
            #PulseGen.setCycles(10,PGPulseChnSetReset)
            #PulseGen.setPulseVoltage(Vread, PGPulseChnSetReset)
            #PulseGen.setPulseWidth(tread, PGPulseChnSetReset)
            #PulseGen.setPulseDelay(ReadDelay, PGPulseChnSetReset, 1)
            PulseGen.enableTriggerOutput()

            #PulseGen.disableTriggerOutput()
            #tm.sleep(0.1)

            # Turn on both Channels used in Program
            PulseGen.turnOnOutput(PGPulseChnSetReset)
            PulseGen.turnOnOutput(PGPulseChnRead)
            #PulseGen.turnOnOutput(chn=PGPulseChn)
            PulseGen.arm()
            #tm.sleep(1e-2)

            DataReads = []

            Oscilloscope.writeAcquisition("TriggerMode", "Single") 
            #Oscilloscope.writeAcquisition("TriggerMode", "Normal") 
            tstart = tm.time()
            while True:
                try: 
                    TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                    DataReads = Oscilloscope.queryDataArray(OscGNDChn)
                    deltat = Oscilloscope.queryDataTimePerPoint()
                    #print("ReRAMLength:", len(DataReads))
                    #print("deltat", deltat)
                    #DataReads.append(DataReadsOut)
                    #print("DataReads: ", DataReads)
                    #print("DataReads!!!!")
                except AttributeError:
                    TrigMode = "" 
                if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                    break
                tm.sleep(refresh)
            
            PulseGen.dearm()

            Oscilloscope.writeAcquisition("TriggerMode", "Stop")
            Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
            
            ##############################################################################################################################
            ############## Update this section for Burst pulsing!!!!! ####################################################################
            if PS:
                #DataReads = Oscilloscope.queryDataArray(1)
                #eChar.plotIVData({"Add": True, "Traces":DataReads, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Voltage (V)', 'Title': "Resistance Change",   "ValueName": 'V'})
                er = 1
                #V = float(Oscilloscope.getMeasurementResults(1))


            else:
                V = Vread

            V = Vread
            ####### Data Splitting ###############
            DataPoints = []
            VoltageOutputArray = []
            A = np.array(DataReads)
            B = A[len(A)//2:]
            #print("Length of Array: ", len(B))
            
            #DataReads
            DataPoints1 = (tperiodresetread/2)/float(deltat)
            DataPoints1 = int(DataPoints1)
            DataPointsPeriodLength = int(tperiodresetread/float(deltat))
            #print("Value of first pulse: ", B[DataPoints1])
            
            for f in range(BurstPulseNumResetRead):
                DataPointsChange = int(DataPoints1 + f*DataPointsPeriodLength)
                
                DataPoints.append(DataPointsChange)
                VoltageOutputArray.append(B[DataPoints[f]])

            print("DataPoints: ", DataPoints)
            print("VoltageOutputArray: ", VoltageOutputArray)

            #I = float(Oscilloscope.getMeasurementResults(2))/50

            #I = DataPoints/50
            #I = np.divide(DataPoints, 50) 
            I = np.divide(VoltageOutputArray, 50) 

            print("Current: ", I)

            Varray = np.tile(V, len(I))
            R = abs(Varray/I)
            

            #R = np.divide(I, 1/V) 
            print("rReset: ", R)
            #print("Rreset[n]: ", Rreset[n])

            
            #R = abs(V/I)
            #print("rR", R, " goal ", Rgoal)

            #Rcompl.append(R)
            #Ccompl.append(1/R)
            #ncompl.append(r)
            #RgoalCompl.append(Rgoal)
            #RdeltaCompl.append(abs(R-Rgoal))
            #PercDelCompl.append(abs((R-Rgoal)/R))


            arr1 = np.arange(1, (BurstPulseNumResetRead+1))
            #print("arr: ", arr)
            ### Convert to List ####
            #Rlist1 = R.tolist()
            #print("Rlist1: ", Rlist1)
            #arrlist1 = arr.tolist()

            #if R > Rgoal:
            if True:

                for e in range(len(R)):
                    #Rreset.append(R[e])
                    
                    Rcompl.append(R[e])
                    #print("Rreset[n]: ", Rreset[n])
                    #nReset.append(arr[e])
                    
                    ncompl.append(arr1[e])
                    #print("nReset[n]: ", nReset[n])
                    #RresGoal[n].append(Rgoal)
                    #RdelReset[n].append(abs(R-Rgoal))
                    #PercDelReset[n].append(abs((R-Rgoal)/R))
                    if e == range(len(R)):
                        Rreset[n].append(R[e])
                        nReset[n].append(arr1[e])
                    #r = 1
                    #Rgoal = Rgoal + RstepReset
                    Trac = [[R[e]]]
                    eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Pulse Number', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
                    #Trac = [[1/R]]  
                    #eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})
                Rwrote = True
            else:
                r = r+1
            
            PulseGen.turnOffOutput(PGPulseChnSetReset)
            PulseGen.turnOffOutput(PGPulseChnRead)
            #print("Rreset[n]: ", Rreset[n])

            RepititionNumArr1Len = len(arr1)
            #RepititionNumArr1 = []
            #RepititionNumArr1 = np.repeat(n+1, (RepititionNumArrLen))
            for q in range(RepititionNumArr1Len):
                RepititionNumArr.append(int(n+1))
            #print("RepititionNumArr: ", RepititionNumArr)

        #print("RepititionNumArr: ", RepititionNumArr)
        #print("Len of RepititionNumArr: ", len(RepititionNumArr))
        #for q in range(len(RepititionNumArr)/ResetReps):
        #    RepititionNumArrSetReset.append(int(n+1))

        ############################ Set ########################
        #########################################################

        for p in range(SetReps):

            r = 1
            Rwrote = False

            #write first value from Previous Read ## Don't need this with burst pulsing for between set and reset
            #Rset[n].append(R)
            #nSet[n].append(0)
            #RresGoal[n].append(R)
            #RdelReset[n].append(0)
            #PercDelReset[n].append(0)

            #r = 1
            #print(MaxResistance, float(R), r, MaxPulsesPerStepReset, float(R) <= MaxResistance, r <= MaxPulsesPerStepReset)
        
            #print("r", r)

            while not eChar.Stop.empty():
                stop = eChar.Stop.get()
            if stop:    
                eChar.finished.put(True)
                break
            
            Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
            Oscilloscope.writeAcquisitionHoriz("HorScale", HorScaleSetRead)

            ####### Set ##############################################

            # Reset the Pulse Generator to default conditions to be replaced in following code
            PulseGen.reset()
            PulseGen.clearTrigger()
            PulseGen.setTriggerSourceExternal()
            PulseGen.setTriggerThreshold(TriggerLevel)
            PulseGen.setTriggerOutputPolarityPositive()
            PulseGen.setPulseModeSingle(PGPulseChnSetReset)
            PulseGen.setPulseModeSingle(PGPulseChnRead)
            PulseGen.setTriggerModeSingle()
            #PulseGen.setTriggerModeBurst()
            PulseGen.setTriggerImpedanceTo50ohm()

            # Set paparmeters for burst pulse operation!
            PulseGen.setTriggerModeBurst()

            # Set the period of both channels
            #PulseGen.setPulsePeriod(15e-6, PGPulseChnSetReset)
            #PulseGen.setPulsePeriod(15e-6, PGPulseChnRead)
            #print("tperiod: ", tperiod)
            PulseGen.setPulsePeriod(tperiodset, PGPulseChnSetReset)
            PulseGen.setPulsePeriod(tperiodsetread, PGPulseChnRead)

            print("Vreset: ", Vreset)
            print("Vset: ", Vset)
            print("Vread: ", Vread)
            # Set voltage for reset/set and read
            PulseGen.setPulseVoltage(Vset, PGPulseChnSetReset)
            PulseGen.setPulseVoltage(Vread, PGPulseChnRead)

            #print("twidthReset: ", twidthReset)
            #print("tread: ", tread)
            # Set pulse width for reset/set and read
            PulseGen.setPulseWidth(twidthSet, PGPulseChnSetReset)
            PulseGen.setPulseWidth(tread, PGPulseChnRead)

            # Delay for read pulse
            #PulseGen.setDelay(treaddelay, PGPulseChnRead)
            PulseGen.setDelay(treaddelayset, PGPulseChnRead)

            # Set number of burst pulses
            PulseGen.setCycles(BurstPulseNumSet, PGPulseChnSetReset)
            PulseGen.setCycles(BurstPulseNumSetRead, PGPulseChnRead)

            # 
            #PulseGen.s
            #PulseGen.setCycles(10,PGPulseChnSetReset)
            #PulseGen.setPulseVoltage(Vread, PGPulseChnSetReset)
            #PulseGen.setPulseWidth(tread, PGPulseChnSetReset)
            #PulseGen.setPulseDelay(ReadDelay, PGPulseChnSetReset, 1)
            PulseGen.enableTriggerOutput()

            #PulseGen.disableTriggerOutput()
            #tm.sleep(0.1)

            # Turn on both Channels used in Program
            PulseGen.turnOnOutput(PGPulseChnSetReset)
            PulseGen.turnOnOutput(PGPulseChnRead)

            #PulseGen.turnOnOutput(chn=PGPulseChn)
            PulseGen.arm()
            #tm.sleep(1e-2)

            DataReads = []

            Oscilloscope.writeAcquisition("TriggerMode", "Single") 
            #Oscilloscope.writeAcquisition("TriggerMode", "Normal") 
            tstart = tm.time()
            while True:
                try: 
                    TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                    DataReads = Oscilloscope.queryDataArray(OscGNDChn)
                    deltat = Oscilloscope.queryDataTimePerPoint()
                    #print("ReRAMLength:", len(DataReads))
                    #print("deltat", deltat)
                    #DataReads.append(DataReadsOut)
                    #print("DataReads: ", DataReads)
                    #print("DataReads!!!!")
                except AttributeError:
                    TrigMode = "" 
                if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                    break
                tm.sleep(refresh)
            #PulseGen.turnOffOutput(chn=PGPulseChn)
            PulseGen.dearm()

            Oscilloscope.writeAcquisition("TriggerMode", "Stop")
            Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
            
            ##############################################################################################################################
            ############## Update this section for Burst pulsing!!!!! ####################################################################
            if PS:
                #DataReads = Oscilloscope.queryDataArray(1)
                #eChar.plotIVData({"Add": True, "Traces":DataReads, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Voltage (V)', 'Title': "Resistance Change",   "ValueName": 'V'})
                er = 1
                #V = float(Oscilloscope.getMeasurementResults(1))


            else:
                V = Vread

            #print("SET!!!!!")

            V = Vread
            ####### Data Splitting ###############
            DataPoints = []
            VoltageOutputArray = []
            A = np.array(DataReads)
            B = A[len(A)//2:]
            C = A[:len(A)//2]
            #print("Length of Array: ", len(B))
            
            #print("Min voltage Array B: ", min(B))
            #print("Min voltage Array C: ", min(C))
            #print("Max voltage Array B: ", max(B))
            #print("Max voltage Array C: ", max(C))
            #DataReads
            DataPoints1 = (tperiodsetread/2)/float(deltat)
            DataPoints1 = int(DataPoints1)
            DataPointsPeriodLength = int(tperiodsetread/float(deltat))
            #print("Value of first pulse: ", B[DataPoints1])
            
            for f in range(BurstPulseNumSetRead):
                DataPointsChange = int(DataPoints1 + f*DataPointsPeriodLength)
                
                DataPoints.append(DataPointsChange)
                VoltageOutputArray.append(B[DataPoints[f]])

            print("DataPoints: ", DataPoints)
            print("VoltageOutputArray: ", VoltageOutputArray)

            #I = float(Oscilloscope.getMeasurementResults(2))/50

            #I = DataPoints/50
            #I = np.divide(DataPoints, 50) 
            I = np.divide(VoltageOutputArray, 50) 

            print("Current: ", I)

            Varray = np.tile(V, len(I))
            R = abs(Varray/I)
            

            #R = np.divide(I, 1/V) 
            print("rSet: ", R)
            #print("Rset: ", Rset)
            
            #R = abs(V/I)
            #print("rR", R, " goal ", Rgoal)

            #Rcompl.append(R)
            #Ccompl.append(1/R)
            #ncompl.append(r)
            #RgoalCompl.append(Rgoal)
            #RdeltaCompl.append(abs(R-Rgoal))
            #PercDelCompl.append(abs((R-Rgoal)/R))


            arr2 = np.arange(1, (BurstPulseNumSetRead+1))
            #print("arr: ", arr)
            ### Convert to List ####
            #Rlist1 = R.tolist()
            #print("Rlist1: ", Rlist1)
            #arrlist1 = arr.tolist()

            #if R > Rgoal:
            if True:

                for e in range(len(R)):
                    #Rset.append(R[e])
                    #Rset[n].extend(R[e])
                    Rcompl.append(R[e])
                    #print("Rset[n]: ", Rset[n])
                    #nSet.append(arr[e])
                    ncompl.append(arr2[e])
                    #print("nSet[n]: ", nSet[n])
                    #RresGoal[n].append(Rgoal)
                    #RdelReset[n].append(abs(R-Rgoal))
                    #PercDelReset[n].append(abs((R-Rgoal)/R))

                    if e == range(len(R)):
                        Rset[n].append(R[e])
                        nSet[n].append(arr2[e])

                    #r = 1
                    #Rgoal = Rgoal + RstepReset
                    Trac = [[R[e]]]
                    eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Pulse Number', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
                    #Trac = [[1/R]]  
                    #eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})
                Rwrote = True
            else:
                r = r+1
            
            RepititionNumArr2Len = len(arr2)
            #RepititionNumArr1 = []
            #RepititionNumArr1 = np.repeat(n+1, (RepititionNumArrLen))
            for q in range(RepititionNumArr2Len):
                RepititionNumArr.append(int(n+1))
            #print("RepititionNumArr: ", RepititionNumArr)
            


        #TotalRepititionNumArrLen = len(arr2)
        #RepititionNumArr1 = []
        #RepititionNumArr1 = np.repeat(n+1, (RepititionNumArrLen))
        #for q in range(len(RepititionNumArr)/SetReps):
        #    RepititionNumArrSetReset.append(int(n+1))
        #print("RepititionNumArr: ", RepititionNumArr)



###########################################################################################################################################################################################################################################################################################################################
###########################################################################################################################################################################################################################################################################################################################
###########################################################################################################################################################################################################################################################################################################################
###########################################################################################################################################################################################################################################################################################################################
###########################################################################################################################################################################################################################################################################################################################
###########################################################################################################################################################################################################################################################################################################################
###########################################################################################################################################################################################################################################################################################################################
###########################################################################################################################################################################################################################################################################################################################
   
    PulseGen.dearm()
    PulseGen.turnOffOutput(PGPulseChnSetReset)
    PulseGen.turnOffOutput(PGPulseChnRead)
    #PGPulseChnSetReset == PGPulseChnRead

    
    

    ############################################# Header ######################################################
    if not WriteHeader:
        header = eChar.getHeader("Combined")
    else:
        header = []

    header.insert(0,"TestParameter,Measurement.Type,HFincrementalPulsing81110A")
    
    header.append("Instrument,Oscilloscope,%s" %(OscName.strip()))
    header.append("Instrument,PulseGenerator,%s" %(PGName.strip()))
    header.append("Measurement,Device,%s" %(eChar.getDevice()))
    header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.getLocalTime())))
    header.append("Measurement,Vset, %.2e" %(Vset))
    header.append("Measurement,Set Pulse Width, %.2e" %(twidthSet))
    header.append("Measurement,Set Burst Pulse Number, %.2e" %(BurstPulseNumSet))
    #header.append("Measurement,Set Max Pulses Per Step,  %d" %(MaxPulsesPerStepSet))
    #header.append("measurement,Set Resistance Step, %.2f" %( RstepSet))
    header.append("Measurement,Vreset, %.2e" %(Vreset))
    header.append("Measurement,Reset Pulse Width, %.2e" %(twidthReset))
    header.append("Measurement,Reset Burst Pulse Number, %.2e" %(BurstPulseNumReset))
    #header.append("Measurement,Reset Max Pulses Per Step,  %d" %(MaxPulsesPerStepReset))
    #header.append("measurement,Reset Resistance Step, %.2e" %( RstepReset))
    header.append("Measurement,Vread, %.2e" %(Vread))
    header.append("Measurement,Read Pulse Width, %.2e" %(tread))
    header.append("Measurement,Reset Burst Read Pulse Number, %.2e" %(BurstPulseNumResetRead))
    header.append("Measurement,Set Burst Read Pulse Number, %.2e" %(BurstPulseNumSetRead))
    header.append("Measurement,Set Pulse Period Width, %.2e" %(tperiodset))
    header.append("Measurement,Reset Pulse Period Width, %.2e" %(tperiodreset))
    header.append("Measurement,Set Read Pulse Period Width, %.2e" %(tperiodsetread))
    header.append("Measurement,Reset Read Pulse Period Width, %.2e" %(tperiodresetread))
    header.append("Measurement,Set Read Pulse Delay, %.2e" %(treaddelayset))
    header.append("Measurement,Reset Read Pulse Delay, %.2e" %(treaddelayreset))
    header.append("Measurement,Round, %s" %(Round))
    header.append("Measurement,Repetition, %s" %(Repetition))
    header.append("Measurement,Set Repetitions, %s" %(SetReps))
    header.append("Measurement,Reset Repetition, %s" %(ResetReps))
    header.append("Measurement,PowerSplitter, %s" %(PS))

    if WriteHeader:
        eChar.extendHeader("Combined",header)

    newline = [None]*3
    newline[0] = 'DataName'
    newline[1] = 'Dimension'
    newline[2] = 'Repetition'
    EntryNumReset = []
    EntryNumSet = []
    OutputData = []
    
    nMax = 0
    #print("Length Rset: ", len(Rset))
    #print("Rreset: ", Rreset)
    #print("nReset: ", nReset)
    #print("Rset: ", Rset)
    #print("nSet: ", nSet)
    '''
    for n in range(len(Rset)):
        #CondReset = list(np.reciprocal(Rreset[n]))
        #CondSet = list(np.reciprocal(Rset[n]))
        
        #newline[0] = '%s,Entry #, Res. Goal, Res., # of Pulses, Res. Dev. (value), Res. Dev. (perc), Res. Conductance (s)' %(newline[0])
        newline[0] = '%s,Entry #, # of Pulses, Reset Res.' %(newline[0])
        #newline[1] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[1],len(RresGoal[n]),len(RresGoal[n]), len(Rreset[n]), len(nReset[n]), len(RdelReset[n]), len(PercDelReset[n]), len(CondReset))
        newline[1] = '%s, %d, %d' %(newline[1], len(nReset), len(Rreset))
        #newline[2] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[2],n+1,n+1,n+1,n+1,n+1,n+1,n+1)
        newline[2] = '%s, %d, %d' %(newline[2],n+1,n+1)

        if EntryNumReset == []:
            EntryNumReset.append(list(range(1,1+len(RresGoal[n]),1)))
        else:
            EntryNumReset.append(list(range(EntryNumSet[-1][-1]+1,EntryNumSet[-1][-1]+1+len(RresGoal[n]),1)))

        #newline[0] = '%s,Entry #, Set. Goal, Set., # of Pulses, Set. Dev. (value), Set. Dev. (perc), Set. Conductance (s)' %(newline[0])
        newline[0] = '%s,Entry #,  # of Pulses, Set Res.' %(newline[0])
        #newline[1] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[1],len(RsetGoal[n]),len(RsetGoal[n]), len(Rset[n]), len(nSet[n]), len(RdelSet[n]), len(PercDelSet[n]), len(CondSet))
        newline[1] = '%s, %d, %d' %(newline[1], len(nSet), len(Rset))
        #newline[2] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[2],n+1,n+1,n+1,n+1,n+1,n+1,n+1)
        newline[2] = '%s, %d, %d' %(newline[2],n+1,n+1)

        #EntryNumSet.append(list(range(EntryNumReset[-1][-1]+1,EntryNumReset[-1][-1]+1+len(RresGoal[n]),1)))
    
    CurMax = max(len(Rreset[n]), len(nReset[n]), len(Rset[n]), len(nSet[n]))

    if CurMax > nMax:
        nMax = CurMax
    
        

    OutputData = []
    for n in range(nMax):
        data = 'DataValue'
        for k in range(len(Rset)):
            try:
                #CondReset = float(1/Rreset[k][n])
                data = "%s, %f, %f, %f" %(data, EntryNumReset[k][n],nReset[k][n], Rreset[k][n])
            except IndexError:
                data = "%s, , , " %(data)
            try:
                #CondSet = float(1/Rset[k][n])
                data = "%s, %f, %f, %f" %(data, EntryNumSet[k][n], nSet[k][n], Rset[k][n])
            except IndexError:
                data = "%s, , , " %(data)
        OutputData.append(data)
        
    header1 = cp.deepcopy(header)
    header1.extend(newline)
    eChar.writeDataToFile(header1, OutputData, Typ=Typ, startCyc=CycStart, endCyc=eChar.curCycle-1)
    '''

    newline = [None]*2
    #newline[0] = 'DataName, R Goal, R, # of Pulses, Deviation (value), Deviation (perc), Conductance (s)'
    newline[0] = 'DataName, Repition # Read, Repition # Operation, # of Pulses, R'
    #newline[1] = 'Dimension, %d, %d, %d, %d' %(len(RepititionNumArr), len(RepititionNumArrSetReset), len(ncompl), len(Rcompl))
    newline[1] = 'Dimension, %d, %d, %d' %(len(RepititionNumArr), len(ncompl), len(Rcompl))
    '''
    print("len(RepititionNumArr): ", len(RepititionNumArr))
    print("len(ncompl): ", len(ncompl))
    print("len(Rcompl): ", len(Rcompl))
    print("RepititionNumArr: ", RepititionNumArr)
    print("ncompl: ", ncompl)
    print("Rcompl: ", Rcompl)
    '''
    OutputData2 = []
    for n in range(len(Rcompl)):
        #data = 'DataValue, %d, %d, %d, %f' %(RepititionNumArr[n], RepititionNumArrSetReset[n],ncompl[n], Rcompl[n])
        data = 'DataValue, %d, %d, %f' %(RepititionNumArr[n],ncompl[n], Rcompl[n])
        OutputData2.append(data)
    
    header.extend(newline)
    Typ2 = "Compl_%s" %(Typ)
    eChar.writeDataToFile(header, OutputData2, Typ=Typ2, startCyc=CycStart, endCyc=eChar.curCycle-1)
    '''
    r0 = R0
    Rdelta = []
    Rdelta.append(Rreset[0][-1] - R0)
    for r, s in zip(Rreset, Rset):
        Rdelta.append(r[-1]-s[-1])
    

    AvgSetPul =  eChar.dhValue([], 'FirstHRS', DoYield=False, Unit='ohm')
    AvgResetPul =  eChar.dhValue([], 'FirstLRS', DoYield=False, Unit='ohm')

    for n in nSet:
        AvgSetPul.extend(n)

    for n in nReset:
        AvgResetPul.extend(n)

    #AvgRratio =  eChar.dhValue(Rdelta, 'ImaxForm', DoYield=eChar.DoYield, Unit='A')
    r#ow = eChar.dhAddRow([AvgSetPul,AvgResetPul,AvgRratio],eChar.curCycle,eChar.curCycle)

    #
    '''

##########################################################################################

###########################################################################################################################
def AnalogFormPS_PGBNC765(eChar, PGPulseChnForm, PGPulseChnRead, OscPulseChn, OscGNDChn, ExpReadCurrent, Vform, tperiod, twidthForm, Vread, tread, Round, ResistanceGoal, Repetition, PowerSplitter=True, WriteHeader=True):
        
    """
    Applies voltage pulses via the Agilent 81110A pulse generator and measures the pulse response via a LeCroy oscilloscope
    Both Devices must be available. RF setup is recommended for rise times below 50ns. 
    PGPulseChnSetReset:     Pulse Channel of 765, (1, 2, 3, or 4)
    PGPulseChnRead: Pulse Channel of 765, (1, 2, 3, or 4) Cannot be the same as PGPulseChnSetReset
    OscPulseChn:    Oscilloscope Pulse Channel
    OscGNDChn:      Oscilloscope GND Channel
    Vset:           Set Voltage (V)
    Vreset:         Reset Voltage (V)
    settwidth:      Set pulse width (s)
    resettwidth:    Reset pulse width (s)
    Vread:          Read Voltage (V)
    tread:          Read pulse width(V)
    RstepSet:       Aimed resistance step per Set
    RstepReset:     Aimed resistance step per Reset
    MaxPulsesPerStepSet:    Maximum number of pulses per step until pulsing is stopped
    MaxPulsesPerStepReset:  Maximum number of pulses per step until pulsing is stopped
    Round           Round to next RstepSize
    Repetition:     Number of set/rest cycles
    PowerSplitter:  Is a power splitter in use? 
    WriteHeader: Enable/Disable writing the header into overlaying summary output files
    """

    #If PGPulseChnSetReset and PGPulseChnRead are the same then throw error
    if PGPulseChnForm == PGPulseChnRead:
        raise ValueError("PGPulseChnSetReset and PGPulseChnRead Cannot be the same channel")

    #If treaddelay is smaller than  twidthSet or twidthReset then throw error
    #if treaddelay < (twidthSet or twidthReset):
    #    raise ValueError("Pulse Delay Read must be larger than both Set and Reset Pulse Width!")

    #if a power splitter is used the input voltage gets divided by two to measure the voltage as well. 
    PS = PowerSplitter
    if PS:
        #Vform = 2*Vform
        Vread = 2*Vread
    else:
        raise ValueError("Power Splitter must be true for this format to work!")


    Typ = 'IncrementalSwitching'
    
    VertScale = max([Vform,Vread])*3
    VertScale2 = 50*ExpReadCurrent/2
    HorScaleRead = tread/2
    #HorScaleSet = (BurstPulseNumSet*tperiod)/4
    #HorScaleReset = (BurstPulseNumReset*tperiod)/4
    HorScaleForm = (tperiod)/2
    TriggerOutputLevel = 1.5
    TriggerLevel = TriggerOutputLevel/3
    ExtInpImpedance = 10000
    OscInpImpedance = 50
    OscPulChn = OscPulseChn
    timeout = 2
    refresh = 1e-1
    CycStart = eChar.curCycle

    Oscilloscope = eChar.getPrimaryLeCroyOscilloscope()
    PulseGen = eChar.PGBNC765

    OscName = Oscilloscope.getModel()
    PGName = PulseGen.getModel()

    OscPulAcInput = OscPulChn.strip()[1]
    OscGNDAcInput = OscGNDChn.strip()[1]
    OscPulChn = int(OscPulChn.strip()[0])
    OscGNDChn = int(OscGNDChn.strip()[0])

    Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "View", 1)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale2)
    #Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "Coupling", "DC50")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "EnhanceResType", "3bits")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "ActiveInput", "Input%s" %(OscGNDAcInput))

    Oscilloscope.writeAcquisitionChn(OscPulChn, "ClearSweeps")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "View", 1)
    #Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale2)
    Oscilloscope.writeAcquisitionChn(OscPulChn, "Coupling", "DC50")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "EnhanceResType", "3bits")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "ActiveInput", "Input%s" %(OscPulAcInput))

    Oscilloscope.writeAcquisitionHoriz("HorScale", HorScaleForm)
    Oscilloscope.writeAcquisitionHoriz("MaxSamples", 250000)
    #Oscilloscope.writeAcquisitionHoriz("MaxSamples", 4000000)
    #Oscilloscope.writeAcquisitionHoriz("MaxSamples", 2500)

    Oscilloscope.writeAcquisitionAuxOut("Amplitude", 2)
    Oscilloscope.writeAcquisitionAuxOut("AuxMode", "TriggerEnabled")

    Oscilloscope.writeAcquisitionTrigger("Edge.Source", "EXT")
    Oscilloscope.writeAcquisitionTrigger("Edge.Slope", "Either")

    Oscilloscope.writeAcquisitionTrigger("ExtLevel", TriggerLevel)

    # set measurements 
    Oscilloscope.clearAllMeasurements()
    Oscilloscope.clearAllMeasurementSweeps()
    Oscilloscope.setMeasurement(1, "Amplitude", OscPulChn)
    Oscilloscope.setMeasurement(2, "Amplitude", OscGNDChn)

    PulseGen.reset()
    PulseGen.clearTrigger()
    PulseGen.setTriggerSourceExternal()
    PulseGen.setTriggerThreshold(TriggerLevel)
    PulseGen.setTriggerOutputPolarityPositive()
    PulseGen.setPulseModeSingle(PGPulseChnForm)
    PulseGen.setPulseModeSingle(PGPulseChnRead)
    PulseGen.setTriggerModeSingle()
    #PulseGen.setTriggerModeBurst()
    PulseGen.setTriggerImpedanceTo50ohm()
    #PulseGen.enableOutput(PGPulseChn)
    #PulseGen.arm()
    #PulseGen.disableOutput(PGPulseChn)


    nReset = []
    Rreset = []
    RresGoal = []
    Rform = []
    nform = []

    nSet = []
    Rset = []
    RsetGoal = []
    Rep = []
    RdelReset = []
    PercDelReset = []
    RdelSet = []
    PercDelSet = []

    Rcompl = []
    ncompl = []
    RgoalCompl = []
    Ccompl = []
    RdeltaCompl = []
    PercDelCompl = []

    NumberRun = []

    stop = False
    RunRep = 1
    

    #PulseGen.setCycles(10,PGPulseChnSetReset)
    PulseGen.setPulseVoltage(Vread, PGPulseChnRead)
    PulseGen.setPulseWidth(tread, PGPulseChnRead)
    #PulseGen.setPulseDelay(ReadDelay, PGPulseChnSetReset, 1)
    PulseGen.enableTriggerOutput()

    VertScale = abs(Vread/4)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale)

    Oscilloscope.writeAcquisitionTrigger("ExtLevel", TriggerLevel)

    Oscilloscope.writeAcquisition("TriggerMode", "Stop")
    PulseGen.turnOnOutput(PGPulseChnRead)
    PulseGen.arm()

    Oscilloscope.writeAcquisition("TriggerMode", "Single")

    tstart = tm.time()
    while True:
        tm.sleep(refresh)
        try: 
            TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
        except:
            TrigMode = "" 
        if TrigMode.strip() == "Stopped" or tm.time()>tstart+timeout:
            break

    #PulseGen.turnOffOutput(PGPulseChn)
    PulseGen.turnOffOutput(PGPulseChnForm)
    PulseGen.turnOffOutput(PGPulseChnRead)
    PulseGen.dearm()
    
    #V = Oscilloscope.queryDataArray(OscPulChn)
    #I = np.divide(Oscilloscope.queryDataArray(OscGNDChn),OscInpImpedance)

    ###############################################################000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000###############################################################
    ############## Update this section for Burst pulsing!!!!! ####################################################################
            

    if PS:
        V = float(Oscilloscope.getMeasurementResults(OscGNDChn))
    else:
        V = Vread
    I = float(Oscilloscope.getMeasurementResults(2))/50

    R0 = abs(V/I)
    R = R0
    print("First R", R)

    Trac = [[R]]
    #eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
    Trac = [[1/R]]  
    #eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})
    '''
    Rcompl.append(R)
    Ccompl.append(1/R)
    ncompl.append(0)
    RgoalCompl.append(R)
    RdeltaCompl.append(0)
    PercDelCompl.append(0)   
    '''
    #write first value from Previous Read
    #Rreset.append(R)
    #nReset.append(0)
    #RresGoal[n].append(R)
    #RdelReset[n].append(0)
    #PercDelReset[n].append(0)

    #nReset.append([])
    #Rreset.append([])
    #RresGoal.append([])
    #nSet.append([])
    #Rset.append([])
    #RsetGoal.append([])
    #RdelReset.append([])
    #PercDelReset.append([])
    #RdelSet.append([])
    #PercDelSet.append([])
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale2)

    Rplot = []
    nplot = []
    RepititionNumArr = []

    for n in range(Repetition):
        print("n", n)

        
        '''
        # Set the first goal resistance to be hit 
        if Round:
            Rgoal = ma.ceil(R/RstepReset)*RstepReset
        else: 
            Rgoal = R + RstepReset
        '''
        r = 1
        Rwrote = False
        '''
        #write first value from Previous Read
        Rreset[n].append(R)
        nReset[n].append(0)
        #RresGoal[n].append(R)
        #RdelReset[n].append(0)
        #PercDelReset[n].append(0)
        '''
        #r = 1
        #print(MaxResistance, float(R), r, MaxPulsesPerStepReset, float(R) <= MaxResistance, r <= MaxPulsesPerStepReset)
       
        #print("r", r)

        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
        if stop:    
            eChar.finished.put(True)
            break
        
        Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
        Oscilloscope.writeAcquisitionHoriz("HorScale", HorScaleForm)

        ####### Form ##############################################
        # Form the Pulse Generator to default conditions to be replaced in following code 
        PulseGen.reset()
        PulseGen.clearTrigger()
        PulseGen.setTriggerSourceExternal()
        PulseGen.setTriggerThreshold(TriggerLevel)
        PulseGen.setTriggerOutputPolarityPositive()
        PulseGen.setPulseModeSingle(PGPulseChnForm)
        PulseGen.setPulseModeSingle(PGPulseChnRead)
        PulseGen.setTriggerModeSingle()
        #PulseGen.setTriggerModeBurst()
        PulseGen.setTriggerImpedanceTo50ohm()


        # Set paparmeters for burst pulse operation!
        #PulseGen.setTriggerModeBurst()

        # Set the period of both channels
        #PulseGen.setPulsePeriod(15e-6, PGPulseChnSetReset)
        #PulseGen.setPulsePeriod(15e-6, PGPulseChnRead)
        #print("tperiod: ", tperiod)
        PulseGen.setPulsePeriod(tperiod, PGPulseChnForm)
        PulseGen.setPulsePeriod(tperiod, PGPulseChnRead)

        #print("Vreset: ", Vreset)
        #print("Vread: ", Vread)
        # Set voltage for Double Form Pulse due to PS
        PulseGen.setPulseVoltage(Vform, PGPulseChnForm)
        PulseGen.setPulseVoltage(Vform, PGPulseChnRead)

        #print("twidthReset: ", twidthReset)
        #print("tread: ", tread)
        # Set pulse width for reset/set and read
        PulseGen.setPulseWidth(twidthForm, PGPulseChnForm)
        PulseGen.setPulseWidth(twidthForm, PGPulseChnRead)

        # Delay for read pulse
        #PulseGen.setDelay(treaddelay, PGPulseChnRead)
        #PulseGen.setDelay(treaddelay, PGPulseChnRead)

        # Set number of burst pulses
        #PulseGen.setCycles(BurstPulseNumReset, PGPulseChnSetReset)
        #PulseGen.setCycles(BurstPulseNumReset, PGPulseChnRead)

        # 
        #PulseGen.s
        #PulseGen.setCycles(10,PGPulseChnSetReset)
        #PulseGen.setPulseVoltage(Vread, PGPulseChnSetReset)
        #PulseGen.setPulseWidth(tread, PGPulseChnSetReset)
        #PulseGen.setPulseDelay(ReadDelay, PGPulseChnSetReset, 1)
        PulseGen.enableTriggerOutput()

        #PulseGen.disableTriggerOutput()
        #tm.sleep(0.1)

        # Turn on both Channels used in Program
        PulseGen.turnOnOutput(PGPulseChnForm)
        PulseGen.turnOnOutput(PGPulseChnRead)
        #PulseGen.turnOnOutput(chn=PGPulseChn)
        PulseGen.arm()
        #tm.sleep(1e-2)

        DataReads = []

        Oscilloscope.writeAcquisition("TriggerMode", "Single") 
        #Oscilloscope.writeAcquisition("TriggerMode", "Normal") 
        tstart = tm.time()
        while True:
            try: 
                TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                #DataReads = Oscilloscope.queryDataArray(OscGNDChn)
                #deltat = Oscilloscope.queryDataTimePerPoint()
                #print("ReRAMLength:", len(DataReads))
                #print("deltat", deltat)
                #DataReads.append(DataReadsOut)
                #print("DataReads: ", DataReads)
                #print("DataReads!!!!")
            except AttributeError:
                TrigMode = "" 
            if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                break
            tm.sleep(refresh)
        
        PulseGen.dearm()

        Oscilloscope.writeAcquisition("TriggerMode", "Stop")
        Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")

        Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
        Oscilloscope.writeAcquisitionHoriz("HorScale", HorScaleRead)


        ####### Reading The Form!!!!!!!! ##############################################
        # Form the Pulse Generator to default conditions to be replaced in following code 
        PulseGen.reset()
        PulseGen.clearTrigger()
        PulseGen.setTriggerSourceExternal()
        PulseGen.setTriggerThreshold(TriggerLevel)
        PulseGen.setTriggerOutputPolarityPositive()
        PulseGen.setPulseModeSingle(PGPulseChnForm)
        PulseGen.setPulseModeSingle(PGPulseChnRead)
        PulseGen.setTriggerModeSingle()
        #PulseGen.setTriggerModeBurst()
        PulseGen.setTriggerImpedanceTo50ohm()


        # Set paparmeters for burst pulse operation!
        #PulseGen.setTriggerModeBurst()

        # Set the period of both channels
        #PulseGen.setPulsePeriod(15e-6, PGPulseChnSetReset)
        #PulseGen.setPulsePeriod(15e-6, PGPulseChnRead)
        #print("tperiod: ", tperiod)
        PulseGen.setPulsePeriod(tread*2, PGPulseChnForm)
        PulseGen.setPulsePeriod(tread*2, PGPulseChnRead)

        #print("Vreset: ", Vreset)
        #print("Vread: ", Vread)
        # Set voltage for Double Form Pulse due to PS
        PulseGen.setPulseVoltage(0, PGPulseChnForm)
        PulseGen.setPulseVoltage(Vread, PGPulseChnRead)

        #print("twidthReset: ", twidthReset)
        #print("tread: ", tread)
        # Set pulse width for reset/set and read
        PulseGen.setPulseWidth(tread, PGPulseChnForm)
        PulseGen.setPulseWidth(tread, PGPulseChnRead)

        # Delay for read pulse
        PulseGen.setDelay(tread/2, PGPulseChnRead)
        PulseGen.setDelay(tread/2, PGPulseChnRead)

        # Set number of burst pulses
        PulseGen.setCycles(1, PGPulseChnForm)
        PulseGen.setCycles(1, PGPulseChnRead)

        # 
        #PulseGen.s
        #PulseGen.setCycles(10,PGPulseChnSetReset)
        #PulseGen.setPulseVoltage(Vread, PGPulseChnSetReset)
        #PulseGen.setPulseWidth(tread, PGPulseChnSetReset)
        #PulseGen.setPulseDelay(ReadDelay, PGPulseChnSetReset, 1)
        PulseGen.enableTriggerOutput()

        #PulseGen.disableTriggerOutput()
        #tm.sleep(0.1)

        # Turn on both Channels used in Program
        PulseGen.turnOnOutput(PGPulseChnForm)
        PulseGen.turnOnOutput(PGPulseChnRead)
        #PulseGen.turnOnOutput(chn=PGPulseChn)
        PulseGen.arm()
        #tm.sleep(1e-2)

        DataReads = []

        Oscilloscope.writeAcquisition("TriggerMode", "Single") 
        #Oscilloscope.writeAcquisition("TriggerMode", "Normal") 
        tstart = tm.time()
        while True:
            try: 
                TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                DataReads = Oscilloscope.queryDataArray(OscGNDChn)
                deltat = Oscilloscope.queryDataTimePerPoint()
                #print("ReRAMLength:", len(DataReads))
                #print("deltat", deltat)
                #DataReads.append(DataReadsOut)
                #print("DataReads: ", DataReads)
                #print("DataReads!!!!")
            except AttributeError:
                TrigMode = "" 
            if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                break
            tm.sleep(refresh)
        
        PulseGen.dearm()

        Oscilloscope.writeAcquisition("TriggerMode", "Stop")
        Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
        
        ##############################################################################################################################
        ############## Update this section for Burst pulsing!!!!! ####################################################################
        if PS:
            #DataReads = Oscilloscope.queryDataArray(1)
            #eChar.plotIVData({"Add": True, "Traces":DataReads, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Voltage (V)', 'Title': "Resistance Change",   "ValueName": 'V'})
            er = 1
            #V = float(Oscilloscope.getMeasurementResults(1))


        else:
            V = Vread

        V = Vread
        ####### Data Splitting ###############
        DataPoints = []
        VoltageOutputArray = []
        A = np.array(DataReads)
        #print("Length of Array A: ", len(A))
        B = A[len(A)//2:]
        #print("Length of Array B: ", len(B))
        C = A[:len(A)//2]
        Cavg = np.mean(C)
        print("Cavg: ", Cavg)
        
        #DataReads
        DataPoints1 = (tread)/float(deltat)
        DataPoints1 = int(DataPoints1)
        DataPointsPeriodLength = int(tperiod/float(deltat))
        #print("Value of first pulse: ", B[DataPoints1])
        '''
        for f in range(BurstPulseNumReset):
            DataPointsChange = int(DataPoints1 + f*DataPointsPeriodLength)
            
            DataPoints.append(DataPointsChange)
            BvalueReset = B[DataPoints[f]]
            BvalueResetAdjusted = BvalueReset - Cavg
            #VoltageOutputArray.append(B[DataPoints[f]])
            VoltageOutputArray.append(BvalueResetAdjusted)
        '''

        DataPoints.append(DataPoints1)
        BvalueRead = B[DataPoints]
        BvalueReadAdjusted = BvalueRead - Cavg
        #VoltageOutputArray.append(B[DataPoints[f]])
        VoltageOutputArray.append(BvalueReadAdjusted)


        print("DataPoints: ", DataPoints)
        print("VoltageOutputArray: ", VoltageOutputArray)

        #I = float(Oscilloscope.getMeasurementResults(2))/50

        #I = DataPoints/50
        #I = np.divide(DataPoints, 50) 
        I = np.divide(VoltageOutputArray, 50) 

        print("Current: ", I)

        Varray = np.tile(V, len(I))
        R = abs(Varray/I)
        

        #R = np.divide(I, 1/V) 
        print("rForm: ", R)
        #print("Rreset[n]: ", Rreset[n])

        
        #R = abs(V/I)
        #print("rR", R, " goal ", Rgoal)

        #Rcompl.append(R)
        #Ccompl.append(1/R)
        #ncompl.append(r)
        #RgoalCompl.append(Rgoal)
        #RdeltaCompl.append(abs(R-Rgoal))
        #PercDelCompl.append(abs((R-Rgoal)/R))


        #arr1 = np.arange(1, (n))
        #print("arr: ", arr)
        ### Convert to List ####
        #Rlist1 = R.tolist()
        #print("Rlist1: ", Rlist1)
        #arrlist1 = arr.tolist()

        #if R > Rgoal:
        if True:

            for e in range(len(R)):
                #Rreset.append(R[e])
                
                Rcompl.append(R[e])
                #print("Rreset[n]: ", Rreset[n])
                #nReset.append(arr[e])
                
                ncompl.append(n)
                #print("nReset[n]: ", nReset[n])
                #RresGoal[n].append(Rgoal)
                #RdelReset[n].append(abs(R-Rgoal))
                #PercDelReset[n].append(abs((R-Rgoal)/R))
                if e == range(len(R)):
                    Rform[n].append(R[e])
                    nform[n].append(n)
                #r = 1
                #Rgoal = Rgoal + RstepReset
                Trac = [[R[e]]]
                eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Pulse Number', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
                #Trac = [[1/R]]  
                #eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})
            Rwrote = True
            #print(DataReads)
            #Rreads = B
            #print(Rreads)
            #Trac = Rreads
            #eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Pulse Number', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
                
        else:
            r = r+1
        
        NumberRun.append(n+1)
        
        PulseGen.turnOffOutput(PGPulseChnForm)
        PulseGen.turnOffOutput(PGPulseChnRead)
        
        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
        if stop:    
            eChar.finished.put(True)
            break
        
        Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
        Oscilloscope.writeAcquisitionHoriz("HorScale", HorScaleRead)

        if R < ResistanceGoal:
            break


    PulseGen.dearm()
    PulseGen.turnOffOutput(PGPulseChnForm)
    PulseGen.turnOffOutput(PGPulseChnRead)
    #PGPulseChnSetReset == PGPulseChnRead

    ############################################# Header ######################################################
    if not WriteHeader:
        header = eChar.getHeader("Combined")
    else:
        header = []

    header.insert(0,"TestParameter,Measurement.Type,HFincrementalPulsing81110A")
    
    header.append("Instrument,Oscilloscope,%s" %(OscName.strip()))
    header.append("Instrument,PulseGenerator,%s" %(PGName.strip()))
    header.append("Measurement,Device,%s" %(eChar.getDevice()))
    header.append("Measurement,Time,%s" %(tm.strftime("%Y-%m-%d_%H-%M-%S",eChar.getLocalTime())))
    header.append("Measurement,Vform, %.2e" %(Vform))
    header.append("Measurement,Set Pulse Width, %.2e" %(twidthForm))
    #header.append("Measurement,Set Burst Pulse Number, %.2e" %(BurstPulseNumSet))
    #header.append("Measurement,Set Max Pulses Per Step,  %d" %(MaxPulsesPerStepSet))
    #header.append("measurement,Set Resistance Step, %.2f" %( RstepSet))
    #header.append("Measurement,Vreset, %.2e" %(Vreset))
    #header.append("Measurement,Reset Pulse Width, %.2e" %(twidthReset))
    #header.append("Measurement,Reset Burst Pulse Number, %.2e" %(BurstPulseNumReset))
    #header.append("Measurement,Reset Max Pulses Per Step,  %d" %(MaxPulsesPerStepReset))
    #header.append("measurement,Reset Resistance Step, %.2e" %( RstepReset))
    header.append("Measurement,Vread, %.2e" %(Vread))
    header.append("Measurement,Read Pulse Width, %.2e" %(tread))
    header.append("Measurement,Pulse Period Width, %.2e" %(tperiod))
    #header.append("Measurement,Read Pulse Delay, %.2e" %(treaddelay))
    header.append("Measurement,Round, %s" %(Round))
    header.append("Measurement,Repetition, %s" %(Repetition))
    header.append("Measurement,PowerSplitter, %s" %(PS))

    if WriteHeader:
        eChar.extendHeader("Combined", header)

    newline = [None]*3
    newline[0] = 'DataName'
    newline[1] = 'Dimension'
    newline[2] = 'Repetition'
    EntryNumReset = []
    EntryNumSet = []
    OutputData = []
    
    nMax = 0
    #print("Length Rset: ", len(Rset))
    #print("Rreset: ", Rreset)
    #print("nReset: ", nReset)
    #print("Rset: ", Rset)
    #print("nSet: ", nSet)
    '''
    for n in range(len(Rset)):
        #CondReset = list(np.reciprocal(Rreset[n]))
        #CondSet = list(np.reciprocal(Rset[n]))
        
        #newline[0] = '%s,Entry #, Res. Goal, Res., # of Pulses, Res. Dev. (value), Res. Dev. (perc), Res. Conductance (s)' %(newline[0])
        newline[0] = '%s,Entry #, # of Pulses, Reset Res.' %(newline[0])
        #newline[1] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[1],len(RresGoal[n]),len(RresGoal[n]), len(Rreset[n]), len(nReset[n]), len(RdelReset[n]), len(PercDelReset[n]), len(CondReset))
        newline[1] = '%s, %d, %d' %(newline[1], len(nReset), len(Rreset))
        #newline[2] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[2],n+1,n+1,n+1,n+1,n+1,n+1,n+1)
        newline[2] = '%s, %d, %d' %(newline[2],n+1,n+1)

        if EntryNumReset == []:
            EntryNumReset.append(list(range(1,1+len(RresGoal[n]),1)))
        else:
            EntryNumReset.append(list(range(EntryNumSet[-1][-1]+1,EntryNumSet[-1][-1]+1+len(RresGoal[n]),1)))

        #newline[0] = '%s,Entry #, Set. Goal, Set., # of Pulses, Set. Dev. (value), Set. Dev. (perc), Set. Conductance (s)' %(newline[0])
        newline[0] = '%s,Entry #,  # of Pulses, Set Res.' %(newline[0])
        #newline[1] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[1],len(RsetGoal[n]),len(RsetGoal[n]), len(Rset[n]), len(nSet[n]), len(RdelSet[n]), len(PercDelSet[n]), len(CondSet))
        newline[1] = '%s, %d, %d' %(newline[1], len(nSet), len(Rset))
        #newline[2] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[2],n+1,n+1,n+1,n+1,n+1,n+1,n+1)
        newline[2] = '%s, %d, %d' %(newline[2],n+1,n+1)

        #EntryNumSet.append(list(range(EntryNumReset[-1][-1]+1,EntryNumReset[-1][-1]+1+len(RresGoal[n]),1)))
    
    CurMax = max(len(Rreset[n]), len(nReset[n]), len(Rset[n]), len(nSet[n]))

    if CurMax > nMax:
        nMax = CurMax
    
        

    OutputData = []
    for n in range(nMax):
        data = 'DataValue'
        for k in range(len(Rset)):
            try:
                #CondReset = float(1/Rreset[k][n])
                data = "%s, %f, %f, %f" %(data, EntryNumReset[k][n],nReset[k][n], Rreset[k][n])
            except IndexError:
                data = "%s, , , " %(data)
            try:
                #CondSet = float(1/Rset[k][n])
                data = "%s, %f, %f, %f" %(data, EntryNumSet[k][n], nSet[k][n], Rset[k][n])
            except IndexError:
                data = "%s, , , " %(data)
        OutputData.append(data)
        
    header1 = cp.deepcopy(header)
    header1.extend(newline)
    
    eChar.writeDataToFile(header1, OutputData, Typ=Typ, startCyc=CycStart, endCyc=eChar.curCycle-1)
    '''

    newline = [None]*2
    #newline[0] = 'DataName, R Goal, R, # of Pulses, Deviation (value), Deviation (perc), Conductance (s)'
    newline[0] = 'DataName, Repition #, # of Pulses, R'
    newline[1] = 'Dimension, %d, %d, %d' %(len(NumberRun), len(ncompl), len(Rcompl))
    '''
    print("len(RepititionNumArr): ", len(RepititionNumArr))
    print("len(ncompl): ", len(ncompl))
    print("len(Rcompl): ", len(Rcompl))
    print("RepititionNumArr: ", RepititionNumArr)
    print("ncompl: ", ncompl)
    print("Rcompl: ", Rcompl)
    '''
    OutputData2 = []
    for n in range(len(Rcompl)):
        data = 'DataValue, %d, %d, %f' %(NumberRun[n], ncompl[n], Rcompl[n])
        OutputData2.append(data)
    
    header.extend(newline)
    Typ2 = "Compl_%s" %(Typ)
    
    eChar.writeDataToFile(header, OutputData2, Typ=Typ2, startCyc=CycStart, endCyc=eChar.curCycle-1)
    '''
    r0 = R0
    Rdelta = []
    Rdelta.append(Rreset[0][-1] - R0)
    for r, s in zip(Rreset, Rset):
        Rdelta.append(r[-1]-s[-1])
    

    AvgSetPul =  eChar.dhValue([], 'FirstHRS', DoYield=False, Unit='ohm')
    AvgResetPul =  eChar.dhValue([], 'FirstLRS', DoYield=False, Unit='ohm')

    for n in nSet:
        AvgSetPul.extend(n)

    for n in nReset:
        AvgResetPul.extend(n)

    #AvgRratio =  eChar.dhValue(Rdelta, 'ImaxForm', DoYield=eChar.DoYield, Unit='A')
    r#ow = eChar.dhAddRow([AvgSetPul,AvgResetPul,AvgRratio],eChar.curCycle,eChar.curCycle)

    #
    '''

###########################################################################################################################
def AnalogSwiVariableReset_PGBNC765_Burst(eChar, PGPulseChnSetReset, PGPulseChnRead, OscPulseChn, OscGNDChn, BurstPulseNumReset, ExpReadCurrent, Vreset, Vresetstep, NumLevels, tperiod, twidthSet, twidthReset, Vread, tread, treaddelay, Round, ResistanceGoal, PowerSplitter, WriteHeader=True):
        
    """
    Applies voltage pulses via the Agilent 81110A pulse generator and measures the pulse response via a LeCroy oscilloscope
    Both Devices must be available. RF setup is recommended for rise times below 50ns. 
    PGPulseChnSetReset:     Pulse Channel of 765, (1, 2, 3, or 4)
    PGPulseChnRead: Pulse Channel of 765, (1, 2, 3, or 4) Cannot be the same as PGPulseChnSetReset
    OscPulseChn:    Oscilloscope Pulse Channel
    OscGNDChn:      Oscilloscope GND Channel
    Vset:           Set Voltage (V)
    Vreset:         Reset Voltage (V)
    settwidth:      Set pulse width (s)
    resettwidth:    Reset pulse width (s)
    Vread:          Read Voltage (V)
    tread:          Read pulse width(V)
    RstepSet:       Aimed resistance step per Set
    RstepReset:     Aimed resistance step per Reset
    MaxPulsesPerStepSet:    Maximum number of pulses per step until pulsing is stopped
    MaxPulsesPerStepReset:  Maximum number of pulses per step until pulsing is stopped
    Round           Round to next RstepSize
    Repetition:     Number of set/rest cycles
    PowerSplitter:  Is a power splitter in use? 
    WriteHeader: Enable/Disable writing the header into overlaying summary output files
    """

    #If PGPulseChnSetReset and PGPulseChnRead are the same then throw error
    if PGPulseChnSetReset == PGPulseChnRead:
        raise ValueError("PGPulseChnSetReset and PGPulseChnRead Cannot be the same channel")

    #If treaddelay is smaller than  twidthSet or twidthReset then throw error
    if treaddelay < (twidthSet or twidthReset):
        raise ValueError("Pulse Delay Read must be larger than both Set and Reset Pulse Width!")

    #if a power splitter is used the input voltage gets divided by two to measure the voltage as well. 
    PS = PowerSplitter
    if PS:
        Vset = 2*Vset
        Vreset = 2*Vreset
        Vread = 2*Vread

    
    #TotCount = Count*NumLevels

    VresetLevels = []
    #print(Vg)
    #print(Vgfloat)
    for i in range(NumLevels):
        j = Vreset + i*Vresetstep
        VresetLevels.append(j)
    print("Vreset all: ", VresetLevels)

    Typ = 'IncrementalSwitching'
    
    VertScale = max([Vset,Vreset,Vread])*3
    VertScale2 = 50*ExpReadCurrent/2
    #HorScale = tread/2
    HorScaleSet = (BurstPulseNumSet*tperiod)/4
    HorScaleReset = (BurstPulseNumReset*tperiod)/4
    TriggerOutputLevel = 1.5
    TriggerLevel = TriggerOutputLevel/3
    ExtInpImpedance = 10000
    OscInpImpedance = 50
    OscPulChn = OscPulseChn
    timeout = 2
    refresh = 1e-1
    CycStart = eChar.curCycle

    Oscilloscope = eChar.getPrimaryLeCroyOscilloscope()
    PulseGen = eChar.PGBNC765

    OscName = Oscilloscope.getModel()
    PGName = PulseGen.getModel()

    OscPulAcInput = OscPulChn.strip()[1]
    OscGNDAcInput = OscGNDChn.strip()[1]
    OscPulChn = int(OscPulChn.strip()[0])
    OscGNDChn = int(OscGNDChn.strip()[0])

    Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "View", 1)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale2)
    #Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "Coupling", "DC50")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "EnhanceResType", "3bits")
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "ActiveInput", "Input%s" %(OscGNDAcInput))

    Oscilloscope.writeAcquisitionChn(OscPulChn, "ClearSweeps")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "View", 1)
    #Oscilloscope.writeAcquisitionChn(OscPulChn, "VerScale", VertScale)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale2)
    Oscilloscope.writeAcquisitionChn(OscPulChn, "Coupling", "DC50")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "EnhanceResType", "3bits")
    Oscilloscope.writeAcquisitionChn(OscPulChn, "ActiveInput", "Input%s" %(OscPulAcInput))

    Oscilloscope.writeAcquisitionHoriz("HorScale", HorScaleReset)
    Oscilloscope.writeAcquisitionHoriz("MaxSamples", 250000)
    #Oscilloscope.writeAcquisitionHoriz("MaxSamples", 4000000)
    #Oscilloscope.writeAcquisitionHoriz("MaxSamples", 2500)

    Oscilloscope.writeAcquisitionAuxOut("Amplitude", 2)
    Oscilloscope.writeAcquisitionAuxOut("AuxMode", "TriggerEnabled")

    Oscilloscope.writeAcquisitionTrigger("Edge.Source", "EXT")
    Oscilloscope.writeAcquisitionTrigger("Edge.Slope", "Either")

    Oscilloscope.writeAcquisitionTrigger("ExtLevel", TriggerLevel)

    # set measurements 
    Oscilloscope.clearAllMeasurements()
    Oscilloscope.clearAllMeasurementSweeps()
    Oscilloscope.setMeasurement(1, "Amplitude", OscPulChn)
    Oscilloscope.setMeasurement(2, "Amplitude", OscGNDChn)

    PulseGen.reset()
    PulseGen.clearTrigger()
    PulseGen.setTriggerSourceExternal()
    PulseGen.setTriggerThreshold(TriggerLevel)
    PulseGen.setTriggerOutputPolarityPositive()
    PulseGen.setPulseModeSingle(PGPulseChnSetReset)
    PulseGen.setPulseModeSingle(PGPulseChnRead)
    PulseGen.setTriggerModeSingle()
    #PulseGen.setTriggerModeBurst()
    PulseGen.setTriggerImpedanceTo50ohm()
    #PulseGen.enableOutput(PGPulseChn)
    #PulseGen.arm()
    #PulseGen.disableOutput(PGPulseChn)


    nReset = []
    Rreset = []
    RresGoal = []

    nSet = []
    Rset = []
    RsetGoal = []
    Rep = []
    RdelReset = []
    PercDelReset = []
    RdelSet = []
    PercDelSet = []

    Vresetarray = []
    Vresetavg = []
    Ravgarray = []

    Rcompl = []
    ncompl = []
    RgoalCompl = []
    Ccompl = []
    RdeltaCompl = []
    PercDelCompl = []

    stop = False
    RunRep = 1
    

    #PulseGen.setCycles(10,PGPulseChnSetReset)
    PulseGen.setPulseVoltage(Vread, PGPulseChnRead)
    PulseGen.setPulseWidth(tread, PGPulseChnRead)
    #PulseGen.setPulseDelay(ReadDelay, PGPulseChnSetReset, 1)
    PulseGen.enableTriggerOutput()

    VertScale = abs(Vread/4)
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale)

    Oscilloscope.writeAcquisitionTrigger("ExtLevel", TriggerLevel)

    Oscilloscope.writeAcquisition("TriggerMode", "Stop")
    PulseGen.turnOnOutput(PGPulseChnRead)
    PulseGen.arm()

    Oscilloscope.writeAcquisition("TriggerMode", "Single")

    tstart = tm.time()
    while True:
        tm.sleep(refresh)
        try: 
            TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
        except:
            TrigMode = "" 
        if TrigMode.strip() == "Stopped" or tm.time()>tstart+timeout:
            break

    #PulseGen.turnOffOutput(PGPulseChn)
    PulseGen.turnOffOutput(PGPulseChnSetReset)
    PulseGen.turnOffOutput(PGPulseChnRead)
    PulseGen.dearm()
    
    #V = Oscilloscope.queryDataArray(OscPulChn)
    #I = np.divide(Oscilloscope.queryDataArray(OscGNDChn),OscInpImpedance)

    ###############################################################000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000###############################################################
    ############## Update this section for Burst pulsing!!!!! ####################################################################
            

    if PS:
        V = float(Oscilloscope.getMeasurementResults(OscGNDChn))
    else:
        V = Vread
    I = float(Oscilloscope.getMeasurementResults(2))/50

    R0 = abs(V/I)
    R = R0
    print("First R", R)
    Trac = [[R]]
    #eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
    Trac = [[1/R]]  
    #eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})
    '''
    Rcompl.append(R)
    Ccompl.append(1/R)
    ncompl.append(0)
    RgoalCompl.append(R)
    RdeltaCompl.append(0)
    PercDelCompl.append(0)   
    '''
    #write first value from Previous Read
    #Rreset.append(R)
    #nReset.append(0)
    #RresGoal[n].append(R)
    #RdelReset[n].append(0)
    #PercDelReset[n].append(0)

    #nReset.append([])
    #Rreset.append([])
    #RresGoal.append([])
    #nSet.append([])
    #Rset.append([])
    #RsetGoal.append([])
    #RdelReset.append([])
    #PercDelReset.append([])
    #RdelSet.append([])
    #PercDelSet.append([])
    Oscilloscope.writeAcquisitionChn(OscGNDChn, "VerScale", VertScale2)

    Rplot = []
    nplot = []
    RepititionNumArr = []

    for n in range(Vresetstep):
        print("n", n)

        
        '''
        # Set the first goal resistance to be hit 
        if Round:
            Rgoal = ma.ceil(R/RstepReset)*RstepReset
        else: 
            Rgoal = R + RstepReset
        '''
        r = 1
        Rwrote = False
        '''
        #write first value from Previous Read
        Rreset[n].append(R)
        nReset[n].append(0)
        #RresGoal[n].append(R)
        #RdelReset[n].append(0)
        #PercDelReset[n].append(0)
        '''
        #r = 1
        #print(MaxResistance, float(R), r, MaxPulsesPerStepReset, float(R) <= MaxResistance, r <= MaxPulsesPerStepReset)
       
        #print("r", r)

        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
        if stop:    
            eChar.finished.put(True)
            break
        
        Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
        Oscilloscope.writeAcquisitionHoriz("HorScale", HorScaleReset)

        ####### Reset ##############################################
        # Reset the Pulse Generator to default conditions to be replaced in following code
        PulseGen.reset()
        PulseGen.clearTrigger()
        PulseGen.setTriggerSourceExternal()
        PulseGen.setTriggerThreshold(TriggerLevel)
        PulseGen.setTriggerOutputPolarityPositive()
        PulseGen.setPulseModeSingle(PGPulseChnSetReset)
        PulseGen.setPulseModeSingle(PGPulseChnRead)
        PulseGen.setTriggerModeSingle()
        #PulseGen.setTriggerModeBurst()
        PulseGen.setTriggerImpedanceTo50ohm()


        # Set paparmeters for burst pulse operation!
        PulseGen.setTriggerModeBurst()

        # Set the period of both channels
        #PulseGen.setPulsePeriod(15e-6, PGPulseChnSetReset)
        #PulseGen.setPulsePeriod(15e-6, PGPulseChnRead)
        #print("tperiod: ", tperiod)
        PulseGen.setPulsePeriod(tperiod, PGPulseChnSetReset)
        PulseGen.setPulsePeriod(tperiod, PGPulseChnRead)

        #print("Vreset: ", Vreset)
        #print("Vread: ", Vread)
        # Set voltage for reset/set and read
        PulseGen.setPulseVoltage(VresetLevels[n], PGPulseChnSetReset)
        PulseGen.setPulseVoltage(Vread, PGPulseChnRead)

        #print("twidthReset: ", twidthReset)
        #print("tread: ", tread)
        # Set pulse width for reset/set and read
        PulseGen.setPulseWidth(twidthReset, PGPulseChnSetReset)
        PulseGen.setPulseWidth(tread, PGPulseChnRead)

        # Delay for read pulse
        #PulseGen.setDelay(treaddelay, PGPulseChnRead)
        PulseGen.setDelay(treaddelay, PGPulseChnRead)

        # Set number of burst pulses
        PulseGen.setCycles(BurstPulseNumReset, PGPulseChnSetReset)
        PulseGen.setCycles(BurstPulseNumReset, PGPulseChnRead)

        # 
        #PulseGen.s
        #PulseGen.setCycles(10,PGPulseChnSetReset)
        #PulseGen.setPulseVoltage(Vread, PGPulseChnSetReset)
        #PulseGen.setPulseWidth(tread, PGPulseChnSetReset)
        #PulseGen.setPulseDelay(ReadDelay, PGPulseChnSetReset, 1)
        PulseGen.enableTriggerOutput()

        #PulseGen.disableTriggerOutput()
        #tm.sleep(0.1)

        # Turn on both Channels used in Program
        PulseGen.turnOnOutput(PGPulseChnSetReset)
        PulseGen.turnOnOutput(PGPulseChnRead)
        #PulseGen.turnOnOutput(chn=PGPulseChn)
        PulseGen.arm()
        #tm.sleep(1e-2)

        DataReads = []

        Oscilloscope.writeAcquisition("TriggerMode", "Single") 
        #Oscilloscope.writeAcquisition("TriggerMode", "Normal") 
        tstart = tm.time()
        while True:
            try: 
                TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                DataReads = Oscilloscope.queryDataArray(OscGNDChn)
                deltat = Oscilloscope.queryDataTimePerPoint()
                #print("ReRAMLength:", len(DataReads))
                #print("deltat", deltat)
                #DataReads.append(DataReadsOut)
                #print("DataReads: ", DataReads)
                #print("DataReads!!!!")
            except AttributeError:
                TrigMode = "" 
            if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                break
            tm.sleep(refresh)
        
        PulseGen.dearm()

        Oscilloscope.writeAcquisition("TriggerMode", "Stop")
        Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
        
        ##############################################################################################################################
        ############## Update this section for Burst pulsing!!!!! ####################################################################
        if PS:
            #DataReads = Oscilloscope.queryDataArray(1)
            #eChar.plotIVData({"Add": True, "Traces":DataReads, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Voltage (V)', 'Title': "Resistance Change",   "ValueName": 'V'})
            er = 1
            #V = float(Oscilloscope.getMeasurementResults(1))


        else:
            V = Vread

        V = Vread
        ####### Data Splitting ###############
        DataPoints = []
        VoltageOutputArray = []
        A = np.array(DataReads)
        #print("Length of Array A: ", len(A))
        B = A[len(A)//2:]
        #print("Length of Array B: ", len(B))
        C = A[:len(A)//2]
        Cavg = np.mean(C)
        print("Cavg: ", Cavg)
        
        #DataReads
        DataPoints1 = (tperiod/2)/float(deltat)
        DataPoints1 = int(DataPoints1)
        DataPointsPeriodLength = int(tperiod/float(deltat))
        #print("Value of first pulse: ", B[DataPoints1])
        
        for f in range(BurstPulseNumReset):
            DataPointsChange = int(DataPoints1 + f*DataPointsPeriodLength)
            
            DataPoints.append(DataPointsChange)
            BvalueReset = B[DataPoints[f]]
            BvalueResetAdjusted = BvalueReset - Cavg
            #VoltageOutputArray.append(B[DataPoints[f]])
            VoltageOutputArray.append(BvalueResetAdjusted)

        print("DataPoints: ", DataPoints)
        print("VoltageOutputArray: ", VoltageOutputArray)

        #I = float(Oscilloscope.getMeasurementResults(2))/50

        #I = DataPoints/50
        #I = np.divide(DataPoints, 50) 
        I = np.divide(VoltageOutputArray, 50) 

        print("Current: ", I)

        Varray = np.tile(V, len(I))
        R = abs(Varray/I)

        Ravg = np.mean(R)
        Ravgarray.append(Ravg)
        

        #R = np.divide(I, 1/V) 
        print("rReset: ", R)
        #print("Rreset[n]: ", Rreset[n])

        
        #R = abs(V/I)
        #print("rR", R, " goal ", Rgoal)

        #Rcompl.append(R)
        #Ccompl.append(1/R)
        #ncompl.append(r)
        #RgoalCompl.append(Rgoal)
        #RdeltaCompl.append(abs(R-Rgoal))
        #PercDelCompl.append(abs((R-Rgoal)/R))


        arr1 = np.arange(1, (BurstPulseNumReset+1))
        #print("arr: ", arr)
        ### Convert to List ####
        #Rlist1 = R.tolist()
        #print("Rlist1: ", Rlist1)
        #arrlist1 = arr.tolist()

        #if R > Rgoal:
        if True:

            for e in range(len(R)):
                #Rreset.append(R[e])
                
                Rcompl.append(R[e])
                #print("Rreset[n]: ", Rreset[n])
                #nReset.append(arr[e])
                
                ncompl.append(arr1[e])
                Vresetarray.append(VresetLevels[n])
                #print("nReset[n]: ", nReset[n])
                #RresGoal[n].append(Rgoal)
                #RdelReset[n].append(abs(R-Rgoal))
                #PercDelReset[n].append(abs((R-Rgoal)/R))
                if e == range(len(R)):
                    Rreset[n].append(R[e])
                    nReset[n].append(arr1[e])
                    #Vresetarray[n].append(VresetLevels[n])
                #r = 1
                #Rgoal = Rgoal + RstepReset
                Trac = [[R[e]]]
                eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Pulse Number', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
                #Trac = [[1/R]]  
                #eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})
            Rwrote = True
            #print(DataReads)
            #Rreads = B
            #print(Rreads)
            #Trac = Rreads
            #eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Pulse Number', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
                
        else:
            r = r+1
        
        PulseGen.turnOffOutput(PGPulseChnSetReset)
        PulseGen.turnOffOutput(PGPulseChnRead)
        #print("Rreset[n]: ", Rreset[n])
        ############################ Set ########################
        #########################################################
        r = 1
        Rwrote = False

        #write first value from Previous Read ## Don't need this with burst pulsing for between set and reset
        #Rset[n].append(R)
        #nSet[n].append(0)
        #RresGoal[n].append(R)
        #RdelReset[n].append(0)
        #PercDelReset[n].append(0)

        #r = 1
        #print(MaxResistance, float(R), r, MaxPulsesPerStepReset, float(R) <= MaxResistance, r <= MaxPulsesPerStepReset)
       
        #print("r", r)

        while not eChar.Stop.empty():
            stop = eChar.Stop.get()
        if stop:    
            eChar.finished.put(True)
            break
        
        Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
        Oscilloscope.writeAcquisitionHoriz("HorScale", HorScaleSet)

        if Ravg > ResistanceGoal:
            break
        '''
        ####### Set ##############################################

        # Reset the Pulse Generator to default conditions to be replaced in following code
        PulseGen.reset()
        PulseGen.clearTrigger()
        PulseGen.setTriggerSourceExternal()
        PulseGen.setTriggerThreshold(TriggerLevel)
        PulseGen.setTriggerOutputPolarityPositive()
        PulseGen.setPulseModeSingle(PGPulseChnSetReset)
        PulseGen.setPulseModeSingle(PGPulseChnRead)
        PulseGen.setTriggerModeSingle()
        #PulseGen.setTriggerModeBurst()
        PulseGen.setTriggerImpedanceTo50ohm()

        # Set paparmeters for burst pulse operation!
        PulseGen.setTriggerModeBurst()

        # Set the period of both channels
        #PulseGen.setPulsePeriod(15e-6, PGPulseChnSetReset)
        #PulseGen.setPulsePeriod(15e-6, PGPulseChnRead)
        #print("tperiod: ", tperiod)
        PulseGen.setPulsePeriod(tperiod, PGPulseChnSetReset)
        PulseGen.setPulsePeriod(tperiod, PGPulseChnRead)

        print("Vreset: ", Vreset)
        print("Vset: ", Vset)
        print("Vread: ", Vread)
        # Set voltage for reset/set and read
        PulseGen.setPulseVoltage(Vset, PGPulseChnSetReset)
        PulseGen.setPulseVoltage(Vread, PGPulseChnRead)

        #print("twidthReset: ", twidthReset)
        #print("tread: ", tread)
        # Set pulse width for reset/set and read
        PulseGen.setPulseWidth(twidthSet, PGPulseChnSetReset)
        PulseGen.setPulseWidth(tread, PGPulseChnRead)

        # Delay for read pulse
        #PulseGen.setDelay(treaddelay, PGPulseChnRead)
        PulseGen.setDelay(treaddelay, PGPulseChnRead)

        # Set number of burst pulses
        PulseGen.setCycles(BurstPulseNumSet, PGPulseChnSetReset)
        PulseGen.setCycles(BurstPulseNumSet, PGPulseChnRead)

        # 
        #PulseGen.s
        #PulseGen.setCycles(10,PGPulseChnSetReset)
        #PulseGen.setPulseVoltage(Vread, PGPulseChnSetReset)
        #PulseGen.setPulseWidth(tread, PGPulseChnSetReset)
        #PulseGen.setPulseDelay(ReadDelay, PGPulseChnSetReset, 1)
        PulseGen.enableTriggerOutput()

        #PulseGen.disableTriggerOutput()
        #tm.sleep(0.1)

        # Turn on both Channels used in Program
        PulseGen.turnOnOutput(PGPulseChnSetReset)
        PulseGen.turnOnOutput(PGPulseChnRead)
        #PulseGen.turnOnOutput(chn=PGPulseChn)
        PulseGen.arm()
        #tm.sleep(1e-2)

        DataReads = []

        Oscilloscope.writeAcquisition("TriggerMode", "Single") 
        #Oscilloscope.writeAcquisition("TriggerMode", "Normal") 
        tstart = tm.time()
        while True:
            try: 
                TrigMode = Oscilloscope.queryAcquisition("TriggerMode").strip()
                DataReads = Oscilloscope.queryDataArray(OscGNDChn)
                deltat = Oscilloscope.queryDataTimePerPoint()
                #print("ReRAMLength:", len(DataReads))
                #print("deltat", deltat)
                #DataReads.append(DataReadsOut)
                #print("DataReads: ", DataReads)
                #print("DataReads!!!!")
            except AttributeError:
                TrigMode = "" 
            if TrigMode == "Stopped" or tm.time()>tstart+timeout:
                break
            tm.sleep(refresh)
        #PulseGen.turnOffOutput(chn=PGPulseChn)
        PulseGen.dearm()

        Oscilloscope.writeAcquisition("TriggerMode", "Stop")
        Oscilloscope.writeAcquisitionChn(OscGNDChn, "ClearSweeps")
        
        ##############################################################################################################################
        ############## Update this section for Burst pulsing!!!!! ####################################################################
        if PS:
            #DataReads = Oscilloscope.queryDataArray(1)
            #eChar.plotIVData({"Add": True, "Traces":DataReads, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Voltage (V)', 'Title': "Resistance Change",   "ValueName": 'V'})
            er = 1
            #V = float(Oscilloscope.getMeasurementResults(1))


        else:
            V = Vread

        #print("SET!!!!!")

        V = Vread
        ####### Data Splitting ###############
        DataPoints = []
        VoltageOutputArray = []
        A = np.array(DataReads)
        B = A[len(A)//2:]
        #C = A[:len(A)//2]
        #print("Length of Array: ", len(B))
        C = A[:len(A)//2]
        Cavg = np.mean(C)
        print("Cavg: ", Cavg)
        
        #print("Min voltage Array B: ", min(B))
        #print("Min voltage Array C: ", min(C))
        #print("Max voltage Array B: ", max(B))
        #print("Max voltage Array C: ", max(C))
        #DataReads
        DataPoints1 = (tperiod/2)/float(deltat)
        DataPoints1 = int(DataPoints1)
        DataPointsPeriodLength = int(tperiod/float(deltat))
        #print("Value of first pulse: ", B[DataPoints1])
        
        for f in range(BurstPulseNumSet):
            DataPointsChange = int(DataPoints1 + f*DataPointsPeriodLength)
            
            DataPoints.append(DataPointsChange)
            #VoltageOutputArray.append(B[DataPoints[f]])
            
            BvalueSet = B[DataPoints[f]]
            BvalueSetAdjusted = BvalueSet - Cavg
            #VoltageOutputArray.append(B[DataPoints[f]])
            VoltageOutputArray.append(BvalueSetAdjusted)

        print("DataPoints: ", DataPoints)
        print("VoltageOutputArray: ", VoltageOutputArray)

        #I = float(Oscilloscope.getMeasurementResults(2))/50

        #I = DataPoints/50
        #I = np.divide(DataPoints, 50) 
        I = np.divide(VoltageOutputArray, 50) 

        print("Current: ", I)

        Varray = np.tile(V, len(I))
        R = abs(Varray/I)
        

        #R = np.divide(I, 1/V) 
        print("rSet: ", R)
        #print("Rset: ", Rset)
        
        #R = abs(V/I)
        #print("rR", R, " goal ", Rgoal)

        #Rcompl.append(R)
        #Ccompl.append(1/R)
        #ncompl.append(r)
        #RgoalCompl.append(Rgoal)
        #RdeltaCompl.append(abs(R-Rgoal))
        #PercDelCompl.append(abs((R-Rgoal)/R))


        arr2 = np.arange(1, (BurstPulseNumSet+1))
        #print("arr: ", arr)
        ### Convert to List ####
        #Rlist1 = R.tolist()
        #print("Rlist1: ", Rlist1)
        #arrlist1 = arr.tolist()

        #if R > Rgoal:
        if True:

            for e in range(len(R)):
                #Rset.append(R[e])
                #Rset[n].extend(R[e])
                Rcompl.append(R[e])
                #print("Rset[n]: ", Rset[n])
                #nSet.append(arr[e])
                ncompl.append(arr2[e])
                #print("nSet[n]: ", nSet[n])
                #RresGoal[n].append(Rgoal)
                #RdelReset[n].append(abs(R-Rgoal))
                #PercDelReset[n].append(abs((R-Rgoal)/R))

                if e == range(len(R)):
                    Rset[n].append(R[e])
                    nSet[n].append(arr2[e])

                #r = 1
                #Rgoal = Rgoal + RstepReset
                Trac = [[R[e]]]
                eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Pulse Number', "Ylabel": 'Resistance (R)', 'Title': "Resistance Change",   "ValueName": 'R'})
                #Trac = [[1/R]]  
                #eChar.plotIVData({"Add": True, "Traces":Trac, 'Xaxis': False, 'Xlabel': 'Iteration', "Ylabel": 'Conductance (s)', 'Title': "Conductance Change",   "ValueName": 'C'})
            Rwrote = True
        else:
            r = r+1
        '''
        RepititionNumArrLen = len(arr1)
        #RepititionNumArr1 = []
        #RepititionNumArr1 = np.repeat(n+1, (RepititionNumArrLen))
        for q in range(RepititionNumArrLen):
            RepititionNumArr.append(int(n+1))
        #print("RepititionNumArr: ", RepititionNumArr)


    
    PulseGen.dearm()
    PulseGen.turnOffOutput(PGPulseChnSetReset)
    PulseGen.turnOffOutput(PGPulseChnRead)
    #PGPulseChnSetReset == PGPulseChnRead

    ############################################# Header ######################################################
    if not WriteHeader:
        header = eChar.getHeader("Combined")
    else:
        header = []

    header.insert(0,"TestParameter,Measurement.Type,HFincrementalPulsing81110A")
    
    header.append("Instrument,Oscilloscope,%s" %(OscName.strip()))
    header.append("Instrument,PulseGenerator,%s" %(PGName.strip()))
    #header.append("Measurement,Vset, %.2e" %(Vset))
    #header.append("Measurement,Set Pulse Width, %.2e" %(twidthSet))
    #header.append("Measurement,Set Burst Pulse Number, %.2e" %(BurstPulseNumSet))
    #header.append("Measurement,Set Max Pulses Per Step,  %d" %(MaxPulsesPerStepSet))
    #header.append("measurement,Set Resistance Step, %.2f" %( RstepSet))
    header.append("Measurement,Vreset start, %.2e" %(Vreset))
    header.append("Measurement,Vresetstep, %.2e" %(Vresetstep))
    header.append("Measurement,Reset Pulse Width, %.2e" %(twidthReset))
    header.append("Measurement,Reset Burst Pulse Number, %.2e" %(BurstPulseNumReset))
    header.append("Measurement,ResistanceGoal, %.2e" %(ResistanceGoal))

    #header.append("Measurement,Reset Max Pulses Per Step,  %d" %(MaxPulsesPerStepReset))
    #header.append("measurement,Reset Resistance Step, %.2e" %( RstepReset))
    header.append("Measurement,Vread, %.2e" %(Vread))
    header.append("Measurement,Read Pulse Width, %.2e" %(tread))
    header.append("Measurement,Pulse Period Width, %.2e" %(tperiod))
    header.append("Measurement,Read Pulse Delay, %.2e" %(treaddelay))
    header.append("Measurement,Round, %s" %(Round))
    #header.append("Measurement,Repetition, %s" %(Repetition))
    header.append("Measurement,NumLevels, %s" %(NumLevels))
    header.append("Measurement,PowerSplitter, %s" %(PS))

    if WriteHeader:
        eChar.extendHeader("Combined", header)    

    newline = [None]*3
    newline[0] = 'DataName'
    newline[1] = 'Dimension'
    newline[2] = 'NumLevels'
    EntryNumReset = []
    EntryNumSet = []
    OutputData = []
    
    nMax = 0
    #print("Length Rset: ", len(Rset))
    #print("Rreset: ", Rreset)
    #print("nReset: ", nReset)
    #print("Rset: ", Rset)
    #print("nSet: ", nSet)
    '''
    for n in range(len(Rset)):
        #CondReset = list(np.reciprocal(Rreset[n]))
        #CondSet = list(np.reciprocal(Rset[n]))
        
        #newline[0] = '%s,Entry #, Res. Goal, Res., # of Pulses, Res. Dev. (value), Res. Dev. (perc), Res. Conductance (s)' %(newline[0])
        newline[0] = '%s,Entry #, # of Pulses, Reset Res.' %(newline[0])
        #newline[1] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[1],len(RresGoal[n]),len(RresGoal[n]), len(Rreset[n]), len(nReset[n]), len(RdelReset[n]), len(PercDelReset[n]), len(CondReset))
        newline[1] = '%s, %d, %d' %(newline[1], len(nReset), len(Rreset))
        #newline[2] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[2],n+1,n+1,n+1,n+1,n+1,n+1,n+1)
        newline[2] = '%s, %d, %d' %(newline[2],n+1,n+1)

        if EntryNumReset == []:
            EntryNumReset.append(list(range(1,1+len(RresGoal[n]),1)))
        else:
            EntryNumReset.append(list(range(EntryNumSet[-1][-1]+1,EntryNumSet[-1][-1]+1+len(RresGoal[n]),1)))

        #newline[0] = '%s,Entry #, Set. Goal, Set., # of Pulses, Set. Dev. (value), Set. Dev. (perc), Set. Conductance (s)' %(newline[0])
        newline[0] = '%s,Entry #,  # of Pulses, Set Res.' %(newline[0])
        #newline[1] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[1],len(RsetGoal[n]),len(RsetGoal[n]), len(Rset[n]), len(nSet[n]), len(RdelSet[n]), len(PercDelSet[n]), len(CondSet))
        newline[1] = '%s, %d, %d' %(newline[1], len(nSet), len(Rset))
        #newline[2] = '%s, %d, %d, %d, %d, %d, %d, %d' %(newline[2],n+1,n+1,n+1,n+1,n+1,n+1,n+1)
        newline[2] = '%s, %d, %d' %(newline[2],n+1,n+1)

        #EntryNumSet.append(list(range(EntryNumReset[-1][-1]+1,EntryNumReset[-1][-1]+1+len(RresGoal[n]),1)))
    
    CurMax = max(len(Rreset[n]), len(nReset[n]), len(Rset[n]), len(nSet[n]))

    if CurMax > nMax:
        nMax = CurMax
    
        

    OutputData = []
    for n in range(nMax):
        data = 'DataValue'
        for k in range(len(Rset)):
            try:
                #CondReset = float(1/Rreset[k][n])
                data = "%s, %f, %f, %f" %(data, EntryNumReset[k][n],nReset[k][n], Rreset[k][n])
            except IndexError:
                data = "%s, , , " %(data)
            try:
                #CondSet = float(1/Rset[k][n])
                data = "%s, %f, %f, %f" %(data, EntryNumSet[k][n], nSet[k][n], Rset[k][n])
            except IndexError:
                data = "%s, , , " %(data)
        OutputData.append(data)
        
    header1 = cp.deepcopy(header)
    header1.extend(newline)
    
    eChar.writeDataToFile(header1, OutputData, Typ=Typ, startCyc=CycStart, endCyc=eChar.curCycle-1)
    '''

    # Making VresetLevels and Ravg same length as other values
    arrones = []
    arrones = np.ones(1)
    while len(VresetLevels) < len(Rcompl):
        VresetLevels.append(arrones)
        Ravgarray.append(arrones)
    
    newline = [None]*2
    #newline[0] = 'DataName, R Goal, R, # of Pulses, Deviation (value), Deviation (perc), Conductance (s)'
    newline[0] = 'DataName, Repition #, Vreset, # of Pulses, R, VresetSingle, Average R'
    newline[1] = 'Dimension, %d, %d, %d, %d, %d' %(len(RepititionNumArr), len(Vresetarray), len(ncompl), len(Rcompl), len(VresetLevels), len(Ravgarray))
    '''
    print("len(RepititionNumArr): ", len(RepititionNumArr))
    print("len(ncompl): ", len(ncompl))
    print("len(Rcompl): ", len(Rcompl))
    print("RepititionNumArr: ", RepititionNumArr)
    print("ncompl: ", ncompl)
    print("Rcompl: ", Rcompl)
    '''
    OutputData2 = []
    for n in range(len(Rcompl)):
        data = 'DataValue, %d, %f, %d, %f, %f, %f' %(RepititionNumArr[n], Vresetarray[n], ncompl[n], Rcompl[n], VresetLevels[n], Ravgarray[n])
        OutputData2.append(data)
    
    header.extend(newline)
    Typ2 = "Compl_%s" %(Typ)
    
    eChar.writeDataToFile(header, OutputData2, Typ=Typ2, startCyc=CycStart, endCyc=eChar.curCycle-1)
    '''
    r0 = R0
    Rdelta = []
    Rdelta.append(Rreset[0][-1] - R0)
    for r, s in zip(Rreset, Rset):
        Rdelta.append(r[-1]-s[-1])
    

    AvgSetPul =  eChar.dhValue([], 'FirstHRS', DoYield=False, Unit='ohm')
    AvgResetPul =  eChar.dhValue([], 'FirstLRS', DoYield=False, Unit='ohm')

    for n in nSet:
        AvgSetPul.extend(n)

    for n in nReset:
        AvgResetPul.extend(n)

    #AvgRratio =  eChar.dhValue(Rdelta, 'ImaxForm', DoYield=eChar.DoYield, Unit='A')
    r#ow = eChar.dhAddRow([AvgSetPul,AvgResetPul,AvgRratio],eChar.curCycle,eChar.curCycle)

    #
    '''

    
