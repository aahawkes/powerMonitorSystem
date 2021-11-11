### Note: This repository is still in development. All the code has been made available here. A breakdown of this system will be provided later.

# powerMonitorSystem

Monitors and records power delivered to an ultrasound transducuer during focused ultrasound (FUS) neuromodulation procedures, for both 40-second pulsed burst and event-based stimulations. This system was designed to be incorporated directly into into a FUS neuromodulation setup. To run this system, only two hardware components and the associated software are required. The hardware components of this system are the (1) bi-directional coupler, ZABDC50-150HP+, Mini-Circuits, Brooklyn, and the (2) programmable USB oscilloscope, PicoScope 5424B, Pico Technology, St Neots, UK. The components should be incorporated in the FUS neuromodulation set up as shown in the following diagram: 
<p align="center">
  <img src="https://user-images.githubusercontent.com/79548629/141196488-7f4f442c-c110-4b50-a4ef-c6bc313267e7.png" height="200" height="150">
</p>

(*Note: this setup diagram is based on the 40-second and event-based stimulations for which this system was designed. Ideally, this system can be translated to any other FUS   nueromodulation experimental setup, but the steps to do so are not included here. Please contact for technical support.*)



A system that enables the user to monitor and record power output to an ultrasound transducer during focused ultrasound (FUS) nueromodulation experiements. There are both hardware and software components to this power monitor system. The two main hardware components are the PicoScope 5242b and a bi-directional coupler.  This system provides an accessible and affordable method to monitor power in real-time and log this data for retroactive analysis for both event-based and 40-second pulsed FUS stimulations. to an ultrasonic neuromodulation system using PicoScope® 5000 Series. This system has been designed to work in parallel with the neuromodulation of non-human primates experiment. As the RF signal is applied to the subject, the power monitor system acquires, records, and calculates characteristics of the signal output by a high-power, bi-directional coupler that is in series with the transducer. All instructions below only apply to the power monitoring component of the experimental setup. There are also other system components for the neuromodulation of non-human primates experiment that will need to be incorporated but are not explained in this manual. 
knowledge of electrical current delivered to a transducer is important to ensure delivery of intended FUS exposures. There are limited options for monitoring current: built-in meters are often imprecise, and it can be difficult to successfully monitor sessions with an oscilloscope.
We present an open-source method to monitor current delivery using a programmable USB oscilloscope. 
