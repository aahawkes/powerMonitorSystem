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

##### For Event-based stimulations (or for monitoring short burst of signal)

1. Navigate to the pico-python github repository
2. Using the green "Code" button, select "Download Zip"
3. Unzip folder to C:\Users\ **username** \Miniconda3\envs\powerMonitoring (substituting **username**)
4. Open miniconda and type the following
```
cd C:\Users\username\Miniconda3\envs\powerMonitoring\pico-python-master
pip install picoscope
```

##### For 40-second pulsed burst FUS stimulations (or for signals that are too long to be monitored by the Event-based script)

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

## 2.1 How to Run

##### For Event-based stimulations 

Download the code for 
