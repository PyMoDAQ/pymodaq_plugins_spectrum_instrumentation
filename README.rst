pymodaq_plugins_spectrum_instrumentation
########################################

.. image:: https://img.shields.io/pypi/v/pymodaq_plugins_template.svg
   :target: https://pypi.org/project/pymodaq_plugins_spectrum_instrumentation/
   :alt: Latest Version

.. image:: icon2.ico

Authors
=======

* Martin Luttmann  (martin.luttmann@epfl.ch)
* Malo Hervé (malo.herve@epfl.ch)

Instruments
===========

This package is related to the `Spectrum Instrumentation <https://spectrum-instrumentation.com/>`__ company.

This plugin was created with a model M2p.5933-x4 .
Also implemented for M2p.5936-x4 .

Viewer1D
++++++++

* **Spectrum**: Simple 1D acquisition defined by a number of laser pulses to observe and a sample rate. Tested with
  model M2p.5936-x4
* **Spectrum Lock In**: An advanced version of the Spectrum viewer, where the obtained trace is treated to
  extract data at certain frequencies (Lock In)


Installation instructions
=========================

* pip isntall pymodaq_plugins_spectrum_instrumentation
* Tested on Windows 11



Classic Usage
=============

While the plugin is made to be used for data acquisition, small changes can be made to the plugin for convenience.
The viewer currently works for 2 modes of acquisition : Single and Multi.
In both cases, the the duration and the sampling rate of the acquisition is determined by two values : a number of pulses (at a given frequency), and a number of samples per pulse.
The plugin supports channel triggering and external signal triggering, with variable post trigger.
Clock synchronisation is also supported.

Lock In Usage
=============

Lock In measurement allows to extract signals at a certain frequency.
This is done by giving a lock-in frequency.
This Lock In viewer is made for Balanced measurement, so giving a "Sum" (I) and "Difference" (D) channel is also required to calculate the normalized difference (ND).
Each trace is seperated into isolated pulses and integrated.
Finally, background removal (Pulse - signal after pulse) is supported and toggleable.

The user can then choose to represent a few parameters : 

* (I/D/ND)_Ba : corresponds the average signal in the (I/D/ND) channel
* (I/D/ND)_Bd : corresponds to the average locked-in difference, containing the signal at the lock-in frequency.