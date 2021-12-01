import os
os.chdir(r"C:\Users\adrie\Miniconda3\envs\power_monitor_2\picosdk-python-wrappers-master") #change directory to the folder holding pico-python-master

import ctypes
import numpy as np
from picosdk.ps5000a import ps5000a as ps
import time
import datetime
from picosdk.functions import adc2mV, assert_pico_ok, mV2adc

#%% Determine Vin to get Desired Pressure Delivered to NHP

##USER DEPENDENT VALUE
desiredPNP = 1200 # in kPascals

# Do NOT change unless recalibrated
# If recalibrated: Update with linear relationship between x-value PNP (Pa) and y-value Vin (mVpp)
requiredVin = round((1.846E-04 * desiredPNP *1000) + 2.702e-01)
print('Input ' +str(requiredVin)+ ' mVpp to AWG for desired PNP of ' +str(desiredPNP)+ ' kPa')

#%% Set Up Experiment Dependent Inputs

# Sampling Characteristics
# Do NOT change unless using a different sampling rate or waveform
lengthOfAcq = 40 # length of acquisition in seconds
samplingRate = 1e6 # sampling rate of signal in Hz
samplingInterval = 1/samplingRate # time between each sample in seconds
totalSamples = int(samplingRate*lengthOfAcq) # total number of samples collected during acquisition
numBuffersToCapture = lengthOfAcq # number of buffers set to equal length of acq so there is one buffer per second
sizeOfOneBuffer = int(totalSamples/numBuffersToCapture) # number of samples collected in each buffer
dsf = 1000 # downsampling factor to be used in hilbert envelope


# Waveform Characteristics
# Do NOT change unless using a different waveform
amplitudeRange = requiredVin/1000 # volts peak-peak
freq = 250e3 # Hz
cyclePeriod = (1/freq) # time per cycle of sine wave in seconds
PRF = 10 # pulse repition frequency in Hz
numberOfPulses = 400 # pulse repeate 400 times
burstPeriod = (1/PRF) # time per one pulse in seconds
dutyCycle = 0.3 # ratio of ultrasound on to ultrasound not on for one pulse
timeOn = burstPeriod*dutyCycle # time that ultrasound is one for each pulse in seconds
lengthOfTotalSignal = numberOfPulses*burstPeriod # time of the total signal in seconds
cylcesPerPulse = timeOn/cyclePeriod # number of cycles of sine wave for each pulse

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

PeakVoltage_Forward = [expectedCoupleFWD] # first value in array is expected delivered peak voltage in mV
PeakVoltage_Reverse = [expectedCoupleRVS] # expected reflected peak voltage value
PeakVoltage_Net = [(expectedCoupleFWD - expectedCoupleRVS)] # net expected

#%% Run Program

n = 0
runCount = 1

while n<1:
    
    count = 0
    
    # Create chandle and status ready for use
    chandle = ctypes.c_int16()
    status = {}
    
    # Open PicoScope 5000 Series device
    resolution =ps.PS5000A_DEVICE_RESOLUTION["PS5000A_DR_12BIT"] # Resolution set to 12 Bit
    status["openunit"] = ps.ps5000aOpenUnit(ctypes.byref(chandle), None, resolution) # handle to chandle for use in API functions
    try:
        assert_pico_ok(status["openunit"])
    except: # PicoNotOkError:
    
        powerStatus = status["openunit"]
    
        if powerStatus == 286:
            status["changePowerSource"] = ps.ps5000aChangePowerSource(chandle, powerStatus)
        elif powerStatus == 282:
            status["changePowerSource"] = ps.ps5000aChangePowerSource(chandle, powerStatus)
        else:
            raise
    
        assert_pico_ok(status["changePowerSource"])
        
    ## Set Channels
    enabled = 1
    disabled = 0
    analogue_offset = 0.0
    channel_range = ps.PS5000A_RANGE['PS5000A_500MV']
    status["setChA"] = ps.ps5000aSetChannel(chandle, ps.PS5000A_CHANNEL['PS5000A_CHANNEL_A'],enabled,ps.PS5000A_COUPLING['PS5000A_DC'],channel_range,analogue_offset)
    assert_pico_ok(status["setChA"])
    status["setChB"] = ps.ps5000aSetChannel(chandle, ps.PS5000A_CHANNEL['PS5000A_CHANNEL_B'],enabled,ps.PS5000A_COUPLING['PS5000A_DC'],channel_range,analogue_offset)
    assert_pico_ok(status["setChB"])
    
    ## Set Buffers
    bufferAMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16) # Create buffer array for data collection
    memory_segment = 0
    status["setDataBuffersA"] = ps.ps5000aSetDataBuffers(chandle,ps.PS5000A_CHANNEL['PS5000A_CHANNEL_A'],bufferAMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),None,totalSamples,memory_segment,ps.PS5000A_RATIO_MODE['PS5000A_RATIO_MODE_NONE'])
    assert_pico_ok(status["setDataBuffersA"])
    bufferBMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16) # Create buffer array for data collection
    status["setDataBuffersB"] = ps.ps5000aSetDataBuffers(chandle,ps.PS5000A_CHANNEL['PS5000A_CHANNEL_B'],bufferBMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),None,totalSamples,memory_segment,ps.PS5000A_RATIO_MODE['PS5000A_RATIO_MODE_NONE'])
    assert_pico_ok(status["setDataBuffersB"])
    
    ## Setup ADC
    maxADC = ctypes.c_int16()
    status["maximumValue"] = ps.ps5000aMaximumValue(chandle, ctypes.byref(maxADC))
    assert_pico_ok(status["maximumValue"])
    
    ## Set up single trigger
    enabled = 1
    source = ps.PS5000A_CHANNEL["PS5000A_EXTERNAL"] # trigger on the external channel on the picoscope
    threshold = int(mV2adc(20,channel_range, maxADC)) # threshold set to 20 mV
    direction = 2 # PS5000A_RISING, trigger on the rising edge
    delay = 0 # no delay between trigger and rising edge
    autoTrigger = 0 # set to 0, makes picoscope wait indefinitely for a rising edge
    status["trigger"] = ps.ps5000aSetSimpleTrigger(chandle,enabled,source,threshold,direction,delay,autoTrigger)
    assert_pico_ok(status["trigger"])
    
    ## Setup Streaming Mode
    sampleInterval = ctypes.c_int16(int((1/samplingRate)*1e09)) # sampling interval in nanoseconds
    sampleUnits = ps.PS5000A_TIME_UNITS['PS5000A_NS']
    maxPreTriggerSamples = 0 # no samples collected before the trigger
    autoStopOn = 1
    downsampleRatio = 1 # no downsampling
    status["runStreaming"] = ps.ps5000aRunStreaming(chandle,ctypes.byref(sampleInterval),sampleUnits,maxPreTriggerSamples,totalSamples,autoStopOn,downsampleRatio,ps.PS5000A_RATIO_MODE['PS5000A_RATIO_MODE_NONE'],sizeOfOneBuffer)
    assert_pico_ok(status["runStreaming"])
    
    
    ## Define Callback Function for Streaming Mode Loop
    bufferCompleteA = np.zeros(shape=totalSamples, dtype=np.int16) # buffer not registered with driver to hold all of buffers collected
    bufferCompleteB = np.zeros(shape=totalSamples, dtype=np.int16) # buffer not registered with driver to hold all of buffers collected
    nextSample = 0
    autoStopOuter = False
    wasCalledBack = False
    bufferEnd = [0]
    count = 0
    
    def streaming_callback(handle, noOfSamples, startIndex, overflow, triggerAt, triggered, autoStop, param):
        global nextSample, autoStopOuter, wasCalledBack, count, trigIdx, rmsExpected
        
        # Prevent loop from continuing until a trigger is detected
        if triggered!=0:
            trigIdx = triggerAt
            count=1
        
        # Once trigger is detected, move forward collecting data
        if count==1:
            wasCalledBack = True
            sourceEnd = startIndex + noOfSamples
            noOfSamplesPostTrigger = noOfSamples-triggerAt
            destEnd = nextSample + noOfSamplesPostTrigger
            bufferCompleteA[nextSample:destEnd] = bufferAMax[(startIndex+triggerAt):sourceEnd]
            bufferCompleteB[nextSample:destEnd] = bufferBMax[(startIndex+triggerAt):sourceEnd]

            
            # Compute and store RMS and Peak Voltages for Vcouple_forward and Vcouple_reverse
            if sourceEnd==sizeOfOneBuffer:
                    
                ## RECORD TIMESTAMP AND TRIGGER
                t = time.time()
                timeFromPreviousTrigger.append(t-timeStamp[-1])
                timeStamp.append(t)
                triggerNumber.append(runCount)
                
                bufferEnd.append(destEnd)
                cplFWD = bufferCompleteA[bufferEnd[-2]:bufferEnd[-1]] # select values from each complete buffer on Channel A as acquired
                cplRVS = bufferCompleteB[bufferEnd[-2]:bufferEnd[-1]] # select values from each complete buffer on Channel B as acquired
                
                ## RMS VOLTAGE VALUES
                rmsA = [np.sqrt(np.mean(np.array(cplFWD, dtype='int64')**2))] # RMS voltage delivered to transducer in mV
                rmsFWD = np.array(adc2mV(rmsA, channel_range, maxADC))
                print('Forward RMS Voltage: %0.2f mV' %rmsFWD)
                rmsB = [np.sqrt(np.mean(np.array(cplRVS, dtype='int64')**2))] # RMS voltage delivered to transducer in mV
                rmsRVS = np.array(adc2mV(rmsB, channel_range, maxADC))
                print('Reverse RMS Voltage: %0.2f mV' %rmsRVS)
                netRMS = rmsFWD-rmsRVS # RMS voltage delivered to NHP primate in mV
                RMS_Delivered.append(rmsFWD)
                RMS_Reflected.append(rmsRVS)
                RMS_Net.append(netRMS)
                
                ## PEAK VOLTAGE VALUES
                peakVoltageFWD = [max(cplFWD)]
                peakVoltageFWD = np.array(adc2mV(peakVoltageFWD,channel_range, maxADC))
                peakVoltageRVS = [max(cplRVS)]
                peakVoltageRVS = np.array(adc2mV(peakVoltageRVS,channel_range, maxADC))
                peakVoltageNet = peakVoltageFWD - peakVoltageRVS
                PeakVoltage_Forward.append(peakVoltageFWD)
                PeakVoltage_Reverse.append(peakVoltageRVS)
                PeakVoltage_Net.append(peakVoltageNet)
                
            nextSample += noOfSamplesPostTrigger
            if autoStop:
                autoStopOuter = True
                
    cFuncPtr = ps.StreamingReadyType(streaming_callback) # Convert the python function into a C function pointer.
    
    # While loop to collect data and perform desired calculations and plots
    while nextSample < totalSamples and not autoStopOuter:
        wasCalledBack = False
        status["getStreamingLastestValues"] = ps.ps5000aGetStreamingLatestValues(chandle, cFuncPtr, None)
    
    # Stop the scope
    status["stop"] = ps.ps5000aStop(chandle)
    assert_pico_ok(status["stop"])
    
    # Disconnect the scope
    status["close"] = ps.ps5000aCloseUnit(chandle)
    assert_pico_ok(status["close"])

    runCount = runCount+1 
    n = n+1

#%% Save the Calculated Values from Above

a = np.array(triggerNumber, dtype=object)
b = np.array(timeStamp, dtype=object)
c = np.array(timeFromPreviousTrigger, dtype=object)
c[1] = 0
d = np.array(RMS_Delivered, dtype=object)
e = np.array(RMS_Reflected, dtype=object)
f = np.array(RMS_Net, dtype=object)
g = np.array(PeakVoltage_Forward, dtype=object)
h = np.array(PeakVoltage_Reverse, dtype=object) 
i = np.array(PeakVoltage_Net, dtype=object)
stacked2 = np.column_stack((a,b,c,d,e,f,g,h,i))

ct = datetime.datetime.now() 
timestamp2 = str(ct.strftime("%m%d%Y_%H%M"))

filename2 = "LooseFWD_TUS_Data_Outputs_"+timestamp2+".csv"
np.savetxt(filename2, stacked2, delimiter=",", fmt='%4.4f', header='Trigger Number, Time Stamp (s), Time From Last Trigger (s), Forward RMS V (mV), Reverse RMS V (mV) , Net RMS V (mV),  Forward Peak V (mV), Reverse Peak V (mV), Net Peak V (mV)', footer='Expected Values in Row 2')
