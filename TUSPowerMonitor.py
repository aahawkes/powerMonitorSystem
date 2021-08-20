# %% Import Libraries and Change Directory to Open PS3000a
# import os library 
import os 
# change the current directory to specified directory 
os.chdir(r"C:\Users\adrie\Miniconda3\envs\power_monitor_test\pico-python-master") #change directory to the folder holding pico-python-master

import numpy as np
from picoscope import ps5000a
import time
import datetime

#%% Open PicoScope

ps = ps5000a.PS5000a()


#%% Experiment Dependent Inputs

# Constants
lengthOfAcq = 40 # length of acquisition in seconds
samplingRate = 15e5 # sampling rate of signal in Hz
samplingInterval = 1/samplingRate # time between each sample in seconds
totalSamples = int(samplingRate*lengthOfAcq) # total number of samples collected during acquisition

# Waveform Characteristics: dont change unless using different waveform 
amplitudeRange = 0.233 # volts peak-peak
freq = 250e3 # Hz
cyclePeriod = (1/freq) # time per cycle of sine wave in seconds
PRF = 10 # pulse repition frequency in Hz
numberOfPulses = 400 # pulse repeate 450 times
burstPeriod = (1/PRF) # time per one pulse in seconds
dutyCycle = 0.3 # ratio of ultrasound on to ultrasound not on for one pulse
timeOn = burstPeriod*dutyCycle # time that ultrasound is one for each pulse in seconds
lengthOfTotalSignal = numberOfPulses*burstPeriod # time of the total signal in seconds
cylcesPerPulse = timeOn/cyclePeriod # number of cycles of sine wave for each pulse

(actualSamplingInterval, nSamples, maxSamples) = ps.setSamplingInterval(samplingInterval, lengthOfAcq)

#%% Calibration Dependent Inputs

# If reclibrated - replace value below with new Average Amp value in excel sheet
totalAmplification = 4.78 # dB
amplifiedVoltageOut = (amplitudeRange/2)* ( 10**(totalAmplification/20))

# If recalibrated - replace equation below with line of best fit between Vin and peak Vcouple 
expectedPeakVolts = ((0.8628*amplitudeRange) +  0.1018) # millivolts

# If recalibrated - replace equation below with line of best fit between Vin and PNP in Pa
expectedPNP =  int((5151.5*amplitudeRange*1000) - 1353.3) # Pascals

# If recalibrated - replace values below with values from line of best fit between Vcouple and PNP in Pa
acquiredPNPslope = 5969 # slope for line of best of fit between Vcouple and pressure in pascals
acquiredPNPintercept = 797.39 # y-int for line of best of fit between Vcouple and pressure in pascals

#%% Set Channel 

ps.setChannel(channel="A", coupling="DC", VRange=1)
ps.setChannel(channel="B", coupling="DC", VRange=1)

#%% Set Simple Trigger 

trigSrc = 'External' # uses external trigger as the source of trigger, comes from square wave
threshold = 1.0 # max voltage range on external +-1V
direction = 'Rising' # triggers on the rising edge
delay = 0 # delay between trigger and rising edge
timeout_ms = 0 # makes picoscope wait indefinitely for a rising edge
enabled = True

ps.setSimpleTrigger(trigSrc, threshold, direction, delay, timeout_ms, enabled)

#%% Expected Values

timeStamp = [0]  # initialize timestamp array
timeFromPreviousTrigger = [0]
triggerNumber = [0] # initialize number of triggers recorded

# influence by 
rmsExpected = ((amplifiedVoltageOut/np.sqrt(2))*np.sqrt(dutyCycle)*1000) # first value in array in expexted delivered RMS voltage in mV
print('Expected RMS Voltage: %0.2f mV' %rmsExpected)
RMS_Delivered = [rmsExpected]
RMS_Reflected = [0] # no expected reflect RMS voltage value
RMS_Net = [0] # no net expected RMS voltage because no expected reflect RMS voltage value

PeakVoltage_Delivered = [expectedPeakVolts*1000] # first value in array is expected delivered peak voltage in mV
PeakVoltage_Reflected = [0] # no expected reflected peak voltage value
PeakVoltage_Net = [0] # no net expected because no expected reflected peak voltage value

PNP_Delivered = [expectedPNP/1000] # first value in array is expected delivered peak negative pressure in kPa
PNP_Reflected = [0] # no expected relfected PNP value
PNP_Net = [0] # no net expected PNP because no expected relfected PNP value

#%% Run PicoScope, Collect Data, Print RMS Voltage, Append Data to an array

n = 0

try:
    while True:
        
        ps.runBlock()
        ps.waitReady()

        ## RAW DATA
        cplFwd = ps.getDataV("A",totalSamples)
        cplRvs = ps.getDataV("B",totalSamples)
        
        ## RECORD TIMESTAMP
        t = time.time()
        timeFromPreviousTrigger.append(t-timeStamp[-1])
        timeStamp.append(t)
        
        
        ## RMS VOLTAGE VALUES
        rmsDelivered = np.sqrt(np.mean(np.square(cplFwd)))*1000 # RMS voltage delivered to transducer in mV
        print('RMS Voltage Delivered to Transducer: %0.2f mV' %rmsDelivered)
        rmsReflected = np.sqrt(np.mean(np.square(cplRvs)))*1000 # RMS voltage reflected at the transducer in mV
        netRMS = rmsDelivered-rmsReflected # RMS voltage delivered to NHP primate in mV
        RMS_Delivered.append(rmsDelivered)
        RMS_Reflected.append(rmsReflected)
        RMS_Net.append(netRMS)
        
        ## PEAK VOLTAGE VALUES
        peakVoltageDelivered = max(cplFwd)*1000 # peak voltage delivered to transducer in mV
        peakVoltageReflected = max(cplRvs)*1000 # peak voltage relfected at the transducer in mV
        netPeakVoltage = peakVoltageDelivered - peakVoltageReflected # peak voltage delivered to the NHP in mV
        PeakVoltage_Delivered.append(peakVoltageDelivered)
        PeakVoltage_Reflected.append(peakVoltageReflected)
        PeakVoltage_Net.append(netPeakVoltage)
        
        ## PRESSURE VALUES 
        pnpDelivered = (int((acquiredPNPslope*peakVoltageDelivered) + acquiredPNPintercept))/1000 # PNP in kPa delivered to transducer
        pnpReflected = (int((acquiredPNPslope*peakVoltageReflected) + acquiredPNPintercept))/1000 # PNP in kPa reflected at transducer
        netPNP = (int((acquiredPNPslope*netPeakVoltage) + acquiredPNPintercept))/1000 # in pascals # PNP in kPa deliver to NHP
        PNP_Delivered.append(pnpDelivered)
        PNP_Reflected.append(pnpReflected)
        PNP_Net.append(netPNP)

        n = n+1
        triggerNumber.append(n)

except KeyboardInterrupt:
    print('exited')
    ps.close()
    pass


#%% Save the Calculated Values from Above

a = np.array(triggerNumber)
b = np.array(timeStamp)
c = np.array(timeFromPreviousTrigger)
d = np.array(RMS_Delivered)
e = np.array(RMS_Reflected)
f = np.array(RMS_Net)
g = np.array(PeakVoltage_Delivered)
h = np.array(PeakVoltage_Reflected) 
i = np.array(PeakVoltage_Net)
j = np.array(PNP_Delivered)
k = np.array(PNP_Reflected)
l = np.array(PNP_Net)
stacked = np.column_stack((a,b,c,d,g,j))

ct = datetime.datetime.now() 
timestamp = str(ct.strftime("%m%d%Y"))

filename = "NPH_TUS_Data_Outputs_"+timestamp+".csv"
np.savetxt(filename, stacked, delimiter=",", fmt='%4.4f', header='Trigger Number, Time Stamp (s), Time From Last Trigger (s), RMS V (mV) at Transducer, Peak V (mV) at Transducer, PNP (kPa) at Transducer', footer='Expected Values in Row 2')