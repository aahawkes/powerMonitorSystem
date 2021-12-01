# %% Import Libraries and Change Directory to Open PS5000a
# import os library 
import os 
# change the current directory to specified directory 
os.chdir(r"C:\Users\adrie\Miniconda3\envs\powerMonitor2\pico-python-master") #change directory to the folder holding pico-python-master

import numpy as np
from picoscope import ps5000a
import time
import datetime

#%% Open PicoScope

ps = ps5000a.PS5000a()

#%% Determine Vin to get Desired Pressure Delivered to NHP

##USER DEPENDENT VALUE
desiredPNP = 600 # in kPascals

# Do NOT change unless recalibrated
# If recalibrated: Update with linear relationship between x-value PNP (Pa) and y-value Vin (mVpp)
requiredVin = round((1.846E-04 * desiredPNP *1000) + 2.702e-01)
print('Input ' +str(requiredVin)+ ' mVpp to AWG for desired PNP of ' +str(desiredPNP)+ ' kPa')

#%% Set Up Experiment Dependent Inputs

# Sampling Characteristics
# Do NOT change unless using a different sampling rate or waveform
lengthOfAcq = 0.3 # length of acquisition in seconds
samplingRate = 5e06 # sampling rate of signal in Hz
samplingInterval = 1/samplingRate # time between each sample in seconds
totalSamples = int(samplingRate*lengthOfAcq) # total number of samples collected during acquisition

# Waveform Characteristics
# Do NOT change unless using a different waveform
amplitudeRange = requiredVin/1000 # volts peak-peak
freq = 250e3 # Hz
cyclePeriod = (1/freq) # time per cycle of sine wave in seconds
PRF = 1500 # pulse repition frequency in Hz
numberOfPulses = 450 # pulse repeated 450 times
burstPeriod = (1/PRF) # time per one pulse in seconds
dutyCycle = 0.5 # ratio of ultrasound on to ultrasound not on for one pulse
timeOn = burstPeriod*dutyCycle # time that ultrasound is one for each pulse in seconds
lengthOfTotalSignal = numberOfPulses*burstPeriod # time of the total signal in seconds
cylcesPerPulse = timeOn/cyclePeriod # number of cycles of sine wave for each pulse

(actualSamplingInterval, nSamples, maxSamples) = ps.setSamplingInterval(samplingInterval, lengthOfAcq)

#%% Set Up Calibration Dependent Inputs

# Do NOT change unless recalibrated 
# If recalibrated: Replace equation below with line of best fit between Vin (mVpp) and Vcpl_fwd, Vcpl_rvs (mV)
expectedCoupleFWD = ((0.9009*amplitudeRange*1000) +  0.1491) # millivolts
expectedCoupleRVS = ((0.2730*amplitudeRange*1000) +  0.1764) # millivolts

#%% Expected Values

timeStamp = [0]  # initialize timestamp array
timeFromPreviousTrigger = [0]
triggerNumber = [0] # initialize number of triggers recorded

rmsExpectedFWD = ((expectedCoupleFWD/np.sqrt(2))*np.sqrt(dutyCycle)) # first value in array in expexted foward RMS voltage in mV
print('Expected Forward RMS Voltage: %0.2f mV' %rmsExpectedFWD)
rmsExpectedRVS = ((expectedCoupleRVS/np.sqrt(2))*np.sqrt(dutyCycle)) # first value in array in expexted reverse RMS voltage in mV
print('Expected Reverse RMS Voltage: %0.2f mV' %rmsExpectedRVS)
RMS_Delivered = [rmsExpectedFWD]
RMS_Reflected = [rmsExpectedRVS]
RMS_Net = [(rmsExpectedFWD-rmsExpectedRVS)]

PeakVoltage_Delivered = [expectedCoupleFWD] # first value in array is expected delivered peak voltage in mV
PeakVoltage_Reflected = [expectedCoupleRVS] # expected reflected peak voltage value
PeakVoltage_Net = [(expectedCoupleFWD - expectedCoupleRVS)] # net expected

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
        rmsFWD = np.sqrt(np.mean(np.square(cplFwd)))*1000 # RMS voltage delivered to transducer in mV
        print('Forward RMS Voltage: %0.2f mV' %rmsFWD)
        rmsRVS= np.sqrt(np.mean(np.square(cplRvs)))*1000 # RMS voltage reflected at the transducer in mV
        print('Reverse RMS Voltage: %0.2f mV' %rmsRVS)
        netRMS = rmsFWD-rmsRVS # RMS voltage delivered to NHP primate in mV
        RMS_Delivered.append(rmsFWD)
        RMS_Reflected.append(rmsRVS)
        RMS_Net.append(netRMS)
        
        ## PEAK VOLTAGE VALUES
        peakVoltageDelivered = max(cplFwd[500:1000])*1000 # peak voltage delivered to transducer in mV
        peakVoltageReflected = max(cplRvs[500:1000])*1000 # peak voltage relfected at the transducer in mV
        netPeakVoltage = peakVoltageDelivered - peakVoltageReflected # peak voltage delivered to the NHP in mV
        PeakVoltage_Delivered.append(peakVoltageDelivered)
        PeakVoltage_Reflected.append(peakVoltageReflected)
        PeakVoltage_Net.append(netPeakVoltage)
        
        n = n+1
        triggerNumber.append(n)

except KeyboardInterrupt:
    print('exited')
    ps.close()
    pass


# Save the Calculated Values from Above

a = np.array(triggerNumber)
b = np.array(timeStamp)
c = np.array(timeFromPreviousTrigger)
c[1] = 0
d = np.array(RMS_Delivered)
e = np.array(RMS_Reflected)
f = np.array(RMS_Net)
g = np.array(PeakVoltage_Delivered)
h = np.array(PeakVoltage_Reflected) 
i = np.array(PeakVoltage_Net)
stacked = np.column_stack((a,b,c,d,e,f,g,h,i))

ct = datetime.datetime.now() 
timestamp = str(ct.strftime("%m%d%Y_%H%M"))

filename = "NPH_Event_Based_TUS_Data_Outputs_"+timestamp+".csv"
np.savetxt(filename, stacked, delimiter=",", fmt='%4.4f', header='Trigger Number, Time Stamp (s), Time From Last Trigger (s), Forward RMS V (mV), Reverse RMS V (mV) , Net RMS V (mV),  Forward Peak V (mV), Reverse Peak V (mV), Net Peak V (mV)', footer='Expected Values in Row 2')
