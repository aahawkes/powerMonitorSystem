### Note: This repository is still in development. All the code has been made available here. A breakdown of this system will be provided later.

# powerMonitorSystem

Monitors and records power delivered to an ultrasound transducuer during focused ultrasound (FUS) neuromodulation procedures, for both 40-second pulsed burst and event-based stimulations. This system was designed to be incorporated directly into into a FUS neuromodulation setup. To run this system, only two hardware components and the associated software are required. The hardware components of this system are the (1) bi-directional coupler, ZABDC50-150HP+, Mini-Circuits, Brooklyn, and the (2) programmable USB oscilloscope, PicoScope 5424B, Pico Technology, St Neots, UK. The components should be incorporated in the FUS neuromodulation set up as shown in the following diagram: 
<p align="center">
  <img src="https://user-images.githubusercontent.com/79548629/141196488-7f4f442c-c110-4b50-a4ef-c6bc313267e7.png" height="200" height="150">
</p>

(*Note: this setup diagram is based on the 40-second and event-based stimulations for which this system was designed. Ideally, this system can be translated to any other FUS   nueromodulation experimental setup, but the steps to do so are not included here. Please contact for technical support.*)

This system is run by the software that we developed to customize the PicoScope for power monitoring functions. We developed our code by using the python wrappers, for the PicoScope C/C++ library, availalble at the GitHub repositories: https://github.com/picotech/picosdk-python-wrappers and https://github.com/colinoflynn/pico-python. For 40-second pulsed burst stimulations, the picosdk-python-wrappers repository was utilized; for event-based stimulations, the pico-python repository was utilized. For both stimulations, the physical setup of the bi-directional coupler and PicoScope 5242b and getting started with the system's software components are the same, but the steps to download and utilize the different programs are different, as they were written using different python wrappers. (*Different wrappers were used because of limitations within each wrapper that prevented us from using one or the other on both FUS stimulation sequences.*)
