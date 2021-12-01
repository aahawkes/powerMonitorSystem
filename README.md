# powerMonitorSystem

Monitors and records power delivered to an ultrasound transducuer during focused ultrasound (FUS) neuromodulation procedures, for both 40-second pulsed burst and event-based stimulations. This system was designed to be incorporated directly into into a FUS neuromodulation setup. To run this system in its raw state, minimal to no technological experience is required. The following steps are written for someone with minimal computer knowledge. Ideally, this system can be translated to other power monitoring applications, but the steps to do so are not included here. Please contact for technical support.

(Note: There are two versions of this code listed. The first version was designed for exclusively monitoring 40-second FUS stimulations; code for this system was developed in Jupyter Notebooks. Users of this original version requested the ability to run the script twice; the scripts named Run1 and Run2 meet this design parameter. Version two of this system was designed for monitoring **both** 40-second and event-based FUS stimulations. There is one script for monitoring 40-second stimlations (the code to monitor two cycles was condensed into one script) and one script for monitoring event-based stimulations (this script will run for an infinite number of FUS events, limited only by storage). Both scripts were developed in Spyder. **All the following instructions are exclusively on how to run version 2 of the program.**)

# 1. System Setup

### 1.1 Hardware Setup
To run this system, only two hardware components and the associated software are required. The hardware components of this system are the (1) bi-directional coupler, ZABDC50-150HP+, Mini-Circuits, Brooklyn, and the (2) programmable USB oscilloscope, PicoScope 5424B, Pico Technology, St Neots, UK. For both stimulations, the physical setup of the bi-directional coupler and PicoScope 5242b The components should be incorporated in the FUS neuromodulation set up as shown in the following diagram: 
<p align="center">
  <img src="https://user-images.githubusercontent.com/79548629/141196488-7f4f442c-c110-4b50-a4ef-c6bc313267e7.png" height="200">
</p>

(*Note: this setup is for the 40-second and event-based stimulations for which this system was designed*) 

### 1.2 Software Setup
This system is run by our Python program that controls the PicoScope® oscilloscope for power monitoring. We developed our code by using python wrappers for the API Functions provided by the ps5000a driver in standard C format. These wrappers are available as GitHub repositories: [picosdk-python-wrappers](https://github.com/picotech/picosdk-python-wrappers) by PicoTech and [pico-python](https://github.com/colinoflynn/pico-python) by Colin O'Flynn. For 40-second pulsed burst stimulations, the picosdk-python-wrappers repository was utilized; for event-based stimulations, the pico-python repository was utilized. Although the repositories are both written for the same API driver, some of the software setup is different; these differences will be clearly noted. (*Different wrappers were used because of limitations within each library that prevented us from using one or the other on for monitoring both types of FUS stimulations.*)

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

##### For Event-based stimulation monitoring

1. Navigate to the pico-python github repository
2. Using the green "Code" button, select "Download Zip"
3. Unzip folder to C:\Users\ **username** \Miniconda3\envs\powerMonitoring (substituting **username**)
4. Open miniconda and type the following
```
cd C:\Users\username\Miniconda3\envs\powerMonitoring\pico-python-master
pip install picoscope
```

##### For 40-second pulsed burst FUS stimulation monitoring

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

##### Event-based stimulation power monitoring
The **eventBasedTUSPowerMonitor.py** script was designed to monitor short signals at a high sampling rate. When the script runs, it waits to receive a trigger from the waveform generator, samples the signal once triggered, computes a root-mean-square average and stores this value. The script then pauses and waits for another trigger. When another trigger is received, the script repeats the process, overwriting the raw signal data and compiling the newly computed averages for each trigger. This can be repeated indefintely until the user presses the red square in the console window. Once the loop is exited, the script will save all computed values (described below) and timestamps to a file in the pico-python-master folder. While it is possible to monitor a signal different from the one defined here, this monitoring mehtod is limited by the amount of available storage on the PicoScope. For ultrasound pulses that are longer or that require higher sampling rates, there will be a point at which the system will not longer be able to record data and compute the average. If there is an error with the storage , the **TUSPowerMonitor.py** script should be used.

##### Long, pulsed stimulation power monitoring
The **TUSPowerMonitor.py** script was designed to monitor longer signals at a high sampling rate, but lower than the above script. When the script runs, it waits to receive a trigger from the waveform generator, samples the signal once triggered, computes a root-mean-square average and stores this value. The script will wait for 1 more trigger, repeat the process, overwriting the raw signal data, compile and save all computed values (described below) and timestamps to a file in the picosdk-python-wrappers-master folder. As above, it is possible to monitor a signal different from the one defined here, but it will be limited by the PicoScope's storage capacity. For ultrasound pulses that are longer or require higher sampling rates, there will be a point at which the system will not longer be able to record data and compute the average. Our system has not be developed to monitor signals that exceed these boundaries.

### 2.1 How to Run & System Inputs

##### For Event-based stimulations 

1. Download the file **eventBasedTUSPowerMonitor.py**
2. Open eventBasedTUSPowerMonitor.py script
3. Update line 5 of the script to match the following path with correct username 
```
os.chdir(r"C:\Users\username\Miniconda3\envs\power_monitor_test\pico-python-master")
```
4. Update line 19 to read the desired output Peak Negative Pressure of the ultrasound transducer
5. Lines 23-24, 54-55 will need to be updated every time the ultrasound transducer is recalibrated. *Steps on this process will be provided at the end of these instructions.*
6. Lines 30-46 are the system variables that describe the ultrasound pulse sequence and match the inputs on the connected waveform generator. The variables provided in this script characterize a 300 millisecond pulse at 250 kHz with a pulse repitition frequency of 1500Hz and a duty cycle of 50%. The amplitude is determined by the calibrated values and reported to the user prior at the beginning of the script. The sampling frequency has been set to 5MHz, an appropiate sampling rate for this signal that produces a manageable amount data points for the PicoScope.**
7. Press the Green Play Button at the top of the script

*if attempting to monitor a different signal, enter the characteristics of the signal into script as they apppear on the waveform generator and the desired sampling rate that can be supported by the PicoScope.* 

##### For Event-based stimulations 

1. Download the file **eventBasedTUSPowerMonitor.py**
2. Open eventBasedTUSPowerMonitor.py script
3. Update line 5 of the script to match the following path with correct username 
```
os.chdir(r"C:\Users\username\Miniconda3\envs\power_monitor_test\pico-python-master")
```
4. Update line 19 to read the desired output Peak Negative Pressure of the ultrasound transducer
5. Lines 23-24, 54-55 will need to be updated every time the ultrasound transducer is recalibrated. *Steps on this process will be provided at the end of these instructions.*
6. Lines 30-46 are the system variables that describe the ultrasound pulse sequence and match the inputs on the connected waveform generator. The variables provided in this script characterize a 300 millisecond pulse at 250 kHz with a pulse repitition frequency of 1500Hz and a duty cycle of 50%. The amplitude is determined by the calibrated values and reported to the user prior at the beginning of the script. The sampling frequency has been set to 5MHz, an appropiate sampling rate for this signal that produces a manageable amount data points for the PicoScope.**
7. Press the Green Play Button at the top of the script

*if attempting to monitor a different signal, enter the characteristics of the signal into script as they apppear on the waveform generator and the desired sampling rate that can be supported by the PicoScope.* 

c.	In the console, three values will be printed:
i.	The correct input voltage to use on the AWG to get the desired pressure
ii.	The expected RMS voltage forward
iii.	The expected RMS voltage reverse
d.	The script will wait until it receives a trigger
e.	It will collect data for 300 ms and then pause and wait for another trigger
f.	This will repeat an infinite number of times
g.	With each trigger and recording, the script will print two values in the console:
i.	The expected RMS voltage forward
ii.	The expected RMS voltage reverse
h.	Once you have sent/received all the triggers you wish to gather, press the red stop button on the console
i.	All the expected and recorded values will be saved to a file with a timestamp in the pico-python-master folder


#### consider including "system that gives comparison values" "standard of comparison" "way to compute values and know that your system is working correctly". Consider wording the two options differently (short and long, repeated indefinitely, limited long recordings) and then specify that ours worked for these two specific types of FUS stimulations)
