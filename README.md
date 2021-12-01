# powerMonitorSystem

Monitors and records power delivered to an ultrasound transducuer during focused ultrasound (FUS) neuromodulation procedures, for both short and long pulsed burst stimulations. Computes and compares expected power output values to recorded power output in real-time for simple visual tracking. This system was designed to be incorporated directly into into a FUS neuromodulation setup. To run this system in its raw state, minimal to no technological experience is required. The following steps are written for someone with minimal computer knowledge. This system was specifically designed to monitoring Event-based stimulations of 300 millisecond, and manually triggered 40-second pulsed stimulations. Ideally, this system can be translated to other power monitoring applications. We have not provided the exact steps to do so, but have described the methods and limitiation of this system to inform further applications.

(Note: There are also two versions of this code listed. The first version was designed for exclusively monitoring 40-second FUS stimulations; code for this system was developed in Jupyter Notebooks. Users of this original version requested the ability to monitor two consecutive stimulations; the scripts named Run1 and Run2 meet this design parameter. Version two of this system was designed for monitoring **both** of event-based based 300ms and manually-triggered 40s stimulations, with one script for each method. These scripts can be used for monitoring shorter and longer FUS stimulations relatively. Both scripts were developed in Spyder. **All the following instructions are exclusively on how to run version 2 of the program.**)

# 1. System Setup

### 1.1 Hardware Setup
To run this system, only two hardware components and the associated software are required. The hardware components of this system are the (1) bi-directional coupler, ZABDC50-150HP+, Mini-Circuits, Brooklyn, and the (2) programmable USB oscilloscope, PicoScope 5424B, Pico Technology, St Neots, UK. For both stimulations, the physical setup of the bi-directional coupler and PicoScope 5242b The components should be incorporated in the FUS neuromodulation set up as shown in the following diagram: 
<p align="center">
  <img src="https://user-images.githubusercontent.com/79548629/141196488-7f4f442c-c110-4b50-a4ef-c6bc313267e7.png" height="200">
</p>

(*Note: this setup is for the FUS experiments for which this system was designed and will most likely need to be adapted for other systems*) 

### 1.2 Software Setup
This system is run by our Python program that controls the PicoScope® oscilloscope for power monitoring. We developed our code by using python wrappers for the API Functions provided by the ps5000a driver in standard C format. These wrappers are available as GitHub repositories: [picosdk-python-wrappers](https://github.com/picotech/picosdk-python-wrappers) by PicoTech and [pico-python](https://github.com/colinoflynn/pico-python) by Colin O'Flynn. For monitoring longer stimulations, the picosdk-python-wrappers repository was utilized; for monitoring shorter stimulations, the pico-python repository was utilized. Although the repositories were both written for the same API driver, some of the software setup is different; these differences in setup are noted below. (*Different wrappers were used because of limitations within each library that prevented us from using one or the other on for monitoring both types of FUS stimulations.*)

#### Step One: PicoScope Setup

Navigate to the [PicoScope Software](https://www.picotech.com/downloads) download page. Select “Discontinued Products”. Select “5242B”. Download and install the appropriate PicoScope 6 software for your operating system; this software will not be directly used in the power monitor system, however, it will be used to calibrate the system and determine system inputs (described in Section 2.1.2). Download the appropiate PicoSDK for your operating system's bit version. The image below indicates an example of where to locate the two downloads required in this step. 
<p align="center">
  <img src="https://user-images.githubusercontent.com/79548629/141529704-23a285b3-ca74-4a08-8b76-b10d46f1c376.png" width="500">
</p>

#### Step Two: Miniconda Setup

Miniconda will be used to download the packages that are crucial for running the power monitor system software. Miniconda is a distribution of the Python programming language that allows for simpler package and environment management. Install the appropriate version of [Miniconda](https://docs.conda.io/en/latest/miniconda.html) for your operating system. Once installed, open Miniconda. Walk through each line of the following code blocks in Miniconda. 

Setup the virtual environment in which the packages needed for the power monitoring scripts will be downloaded. Activate the environment.
```
conda create --name powerMonitoring
conda activate powerMonitoring
```

From within the activated environment, download each of the necessary packages: Spyder, Numpy, Scipy. 
```
conda install -c anaconda spyderconda 
conda install numpy
conda install scipy
```
Spyder is the development tool that will be used to run the power monitoring code.

#### Step Three: Download PicoScope Python Wrappers

##### Monitoring shorter stimulations

1. Navigate to the pico-python github repository
2. Using the green "Code" button, select "Download Zip"
3. Unzip folder to C:\Users\ **username** \Miniconda3\envs\powerMonitoring (substituting **username**)
4. Open miniconda and type the following
```
cd C:\Users\username\Miniconda3\envs\powerMonitoring\pico-python-master
pip install picoscope
```

##### Monitoring longer stimulations

1. Navigate to the picosdk-python-wrappers github repository
2. Using the green "Code" button, select "Download Zip"
3. Unzip folder to C:\Users\ **username** \Miniconda3\envs\powerMonitoring (substituting **username**)
4. Navigate to the folder C:\Users\username\Miniconda3\envs\powerMonitor\picosdk-python-wrappers-master
5. Open the file *setup.py*. Comment out lines 17 through 22. Change line 16 to read:
```
    name = 'ps5000'
```
7. Open miniconda and type the following
```
cd C:\Users\username\Miniconda3\envs\powerMonitor\picosdk-python-wrappers-master
python setup.py install
```
#### Step Four: Make sure PATH variables are set up correctly

Sometimes when installing the Python wrappers from the above GitHub repositories, the PATH environment variables need to be re-ordered. This simply means the path the correct directory needs to be clarified in the system. This will allow the power monitoring software to run. Follow the steps below to edit the PATH environment variable (these instructions are for a Microsoft Windows operating system, if there is an error in running the code that reads " ***insert Error message*** ", similarily edit the PATH envinronment variable for the operating system being used.
1. Open the Control Panel
2. Select: System and Security > System > Advanced system settings > Environment Variables
3. Under "System Variables" select the line that reads "Path" and contains a value relating to the Pico Technology SDK lib > Edit
4. Select the path variable to the SDK library and move it to the top of the list > Save

# 2. Running the System

### 2.1 How it Works

##### Monitoring shorter stimulations
The **shortPowerMonitor.py** script was designed to monitor short signals at a high sampling rate. When the script runs, it waits to receive a trigger from the waveform generator, samples the signal once triggered, computes a root-mean-square average and stores this value. The script then pauses and waits for another trigger. When another trigger is received, the script repeats the process, overwriting the raw signal data and compiling the newly computed averages for each trigger. This can be repeated indefintely until the user presses the red square in the console window. Once the loop is exited, the script will save all computed values (described in Section 2.3) and timestamps to a file in the pico-python-master folder. While it is possible to monitor a signal different from the one defined here, this monitoring mehtod is limited by the amount of available storage on the PicoScope. For ultrasound pulses that are longer or that require higher sampling rates, there will be a point at which the system will not longer be able to record data and compute the average. If there is an error with the storage , the **longPowerMonitor.py** script should be used.

##### Monitoring longer stimulations
The **longPowerMonitor.py** script was designed to monitor longer signals at a high sampling rate, but lower than the above script. When the script runs, it waits to receive a trigger from the waveform generator, samples the signal once triggered, computes a root-mean-square average and stores this value. The script will wait for 1 more trigger, repeat the process, overwriting the raw signal data, compile and save all computed values (described in Section 2.3) and timestamps to a file in the picosdk-python-wrappers-master folder. As above, it is possible to monitor a signal different from the one defined here, but it will be limited by the PicoScope's storage capacity. For ultrasound pulses that are longer or require higher sampling rates, there will be a point at which the system will not longer be able to record data and compute the average. Our system has not be developed to monitor signals that exceed these boundaries.

### 2.2 How to Run & System Inputs

##### Monitoring shorter stimulations
1. Download the file **shortPowerMonitor.py**
2. Open eventBasedTUSPowerMonitor.py script
3. Update line 5 of the script to match the following path with correct username 
```
os.chdir(r"C:\Users\username\Miniconda3\envs\power_monitor_test\pico-python-master")
```
4. Update line 19 to read the desired output peak-negative-pressure (PNP) of the ultrasound transducer.
5. Lines 23, 54-55 will need to be updated every time the ultrasound transducer is recalibrated (steps on this process listed in Section 3).
6. Lines 30-46 are the system variables that describe the ultrasound pulse sequence and match the inputs on the connected waveform generator. The variables provided in this script characterize a 300 millisecond pulse at 250 kHz with a pulse repitition frequency of 1500Hz and a duty cycle of 50%. The sampling frequency has been set to 5MHz, an appropiate sampling rate for this signal that produces a manageable amount data points for the PicoScope.**
7. Press the Green Play Button at the top of the script

##### Monitoring longer stimulations
1. Download the file **longPowerMonitor.py**
2. Open the python script in Spyder
3. Update line 5 of the script to match the following path with correct username 
```
os.chdir(r"C:\Users\username\Miniconda3\envs\power_monitor_test\pico-python-master")
```
4. Update line 14 to read the desired output PNP of the ultrasound transducer.
5. Lines 18, 51-52 will need to be updated every time the ultrasound transducer is recalibrated (steps on this process listed in Section 3).
6. Lines 25-45 are the system variables that describe the ultrasound pulse sequence and match the inputs on the connected waveform generator. The variables provided in this script characterize a 40 second signal of 250 kHz with a pulse repitition frequency of 10Hz and a duty cycle of 30%. The sampling frequency has been set to 1.5MHz.**
7. Press the Green Play Button at the top of the script

** *if attempting to monitor a different signal than either of the above signals, choose the appropriate script based on previously described system boundaries, and enter the characteristics of the signal into script as they apppear on the waveform generator and the desired sampling rate that can be supported by the PicoScope.* 

### 2.3 System Outputs

##### For monitoring both shorter and longer stimulations

For both scripts, there are be 3 types of outputs generated in the console window. These outputs will inform the user on amplitude input, expected power output averages for the characterized ultrasound pulse sequence, and averages of the power actually delivered to the ultrasound transducer.
1. **Input voltage:** the script will tell the user what amplitude should be input to the waveform generator in order to obtain the desired output pressure for the transducer being used. This value is computed from the user-input for desired PNP. To obtain the correct equation for input voltage for this system, follow the steps listed in Section 3. 
2. **Expected forward and reverse root-mean-square (RMS) voltage:** the way that this system reports power delivered to the transducer is through a computed average. These are the target values for power delivery, and are computed using two equations obtained in the calibration steps (Section 3). The system reports the power delivered in two values - forward and reverse voltages. These values are correspond to the two channels on the coupler that are connected to the PicoScope. The forward coupled channel reads the signal sent to the transducer, the reverse coupled channels reads the signal reflected by the transducer.
3. **Foward and reverse RMS voltage:** these are the power delivery averages for the signal that is actually delivered to the transducer. The system reads the signal from the coupler (the forward and reverse channels) and computes and reports the RMS voltage. For shorter pulses, the RMS voltage is computed from the entire burst. These two output voltage averages will be reported for every trigger received by the script. For longer pulses, the RMS voltage is computed from every 1 second of data acquired. These two output voltage averages will be reported every second. As described above, power monitoring for longer pulses has been set to run twice, as set in line 77. 

At the end of both scripts, an Excel file is saved containing the expected forward and reverse RMS voltages, expected peak voltage, computed forward and reverse RMS voltages, computed peak voltages, and the corresponding timestamps. There should be as many forward and reverse RMS voltages and peak voltages as there are events/triggers when using **shortPowerMonitor.py**. There should be (40 * # of runs) of forward and reverse RMS voltages and peak voltages when using **longPowerMonitor.py**. 

## 3. Calibrating to Update System Inputs

There are 4 inputs that will change if the transducer used in the experiment is recalibrated prior to the experiment. To determine these inputs, the calibration first has to be completed. The following steps will walk through the calibration process. To establish this calibration process, we used the **blank** hydrophone and in a water bath with our single-element focused ultrasound transducer.

1. Download the **FUS_Calibration.xlsx** file.
2. Leave the PicoScope and bi-directional coupler set up as they were.
3. Set up the hydrophone with the transducer in a waterbath.
4. Detach the reverse port of the coupler from Channel B on the PicoScope.
5. Attach the output of the hydrophone to Channel B. The forward port of the coupler should still be attached to Channel A.
6. Open the PicoScope 6 software previously downloaded & find the focal point of the transducer.
7. Open the Excel file and navigate to the tab "Run with Coupler".
8. Update the value in **J1** to the correct volts to pressure conversion factor for the hydrophone and frequency being used.
9. Update the value in **J4** to the correct frequency being used.
10. Set the waveform generator to 10 mVpp and record the peak voltage outputs on Channal A and Channel B on the Excel sheet under "Vcpl_fwd (mV)" and "Vout (mV)" respectively.
11. Measure forward coupled voltage and hydrophone output voltage for all input voltages listed under "Vin (mVpp)". Note that while the input voltage is in mV peak-peak, all other voltage measurements are in mV.
12. Detach the forward port of the coupler from Channel A on the PicoScope and attach the reverse port of the coupler to Channel A.
13. Repeat steps 8-9, but this time only record the peak voltage output on Channel A on the Excel sheet under "Vcpl_rvs (mV)".
14. Once these output voltages have been recorded, the 3 plots should update automatically. Each plot should have a line of best fit that also updates.
15. Use the equation from the *Vin vs PNP* plot to update line 23 in **shortPowerMonitor.py** and line 18 in **longPowerMonitor.py**. This will make sure the user is given the correct input voltage necessary to reach the target PNP from the transducer.
16. Use the equation from the *Vcpl_fwd vs Vin* plot to update line 54 in **shortPowerMonitor.py** and line 51 in **longPowerMonitor.py**. This will make make sure the user is provided an accurate expected foward coupled RMS voltage for comparison.
17. Use the equation from the *Vcpl_rvs vs Vin* plot to update line 55 in **shortPowerMonitor.py** and line 52 in **longPowerMonitor.py**. This will make make sure the user is provided an accurate expected reverse coupled RMS voltage for comparison.
18. Close PicoScope 6 (the power monitoring system cannot run if the PicoScope is open in another program).
19. Re-attach the bi-directional coupler with the forward port to Channel A and the reverse port to Channel B on the PicoScope.

