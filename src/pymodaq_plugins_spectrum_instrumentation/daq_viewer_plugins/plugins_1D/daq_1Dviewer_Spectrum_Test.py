import numpy as np
from pymodaq.utils.daq_utils import ThreadCommand, getLineInfo
from pymodaq.utils.data import DataFromPlugins, Axis, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter


import spcm
from spcm import units

from pymodaq_plugins_spectrum_instrumentation.hardware.SpectrumCard_wrapper_Single import Spectrum_Wrapper_Single

#TODO : Make Post trig variable
#TODO : Make it possible to change params without rebooting card

class DAQ_1DViewer_Spectrum_Test(DAQ_Viewer_base):
    """ Instrument plugin class for a 1D viewer.

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.

        """

    params = comon_parameters + [

        {'title': 'Channels:', 'name': 'channels', 'type': 'group', 'children':[
            {'title': 'CH0', 'name': 'c0', 'type': 'led_push', 'value': False, 'default': False},
            {'title': 'CH1', 'name': 'c1', 'type': 'led_push', 'value': False, 'default': False},
            {'title': 'CH2', 'name': 'c2', 'type': 'led_push', 'value': True, 'default': True},
            {'title': 'CH3', 'name': 'c3', 'type': 'led_push', 'value': False, 'default': False},
            {'title': 'CH4', 'name': 'c4', 'type': 'led_push', 'value': True, 'default': True},
            {'title': 'CH5', 'name': 'c5', 'type': 'led_push', 'value': False, 'default': False},
            {'title': 'CH6', 'name': 'c6', 'type': 'led_push', 'value': False, 'default': False},
            {'title': 'CH7', 'name': 'c7', 'type': 'led_push', 'value': False, 'default': False} ]},


        {'title': 'Trigger parameters', 'name': 'trig_params', 'type': 'group', 'children':[
            {'title': 'Trigger:', 'name': 'triggerType', 'type': 'itemselect', 'value': dict(all_items=[ "None", "Channel trigger", "Software trigger", "External analog trigger"], selected=["External analog trigger"])},
            {'title': 'Trigger channel:', 'name': 'triggerChannel', 'type': 'itemselect', 'value': dict(all_items=[ "CH0", "CH1", "CH2", "CH3", "CH4", "CH5", "CH6", "CH7"], selected=["CH0"])},
            {'title': 'Trigger mode', 'name': 'triggerMode', 'type': 'itemselect', 'value': dict(all_items=[ "Rising edge", "Falling edge", "Both"], selected=["Rising edge"])},
            {'title': 'Trigger level (mV):', 'name': 'triggerLevel', 'type': 'slide', 'value': 100, 'default': 100, 'min': -500, 'max': 500, 'subtype': 'linear'}]},

        {'title': 'timing', 'name': 'timing', 'type': 'group', 'children': [
            {'title': 'Laser pulses freq. (kHz):', 'name': 'PulseFreq', 'type': 'int', 'value': 1, 'default': 1, 'readonly' : True},
            {'title': 'Nbr. of laser pulses:', 'name': 'NumLPulses', 'type': 'int', 'value': 200, 'default': 200},
            {'title': 'Nbr. of samples / laser pulse:', 'name': 'NumSinPulse', 'type': 'int', 'value': 200, 'default': 200},
            {'title': 'Sample rate (MHz):', 'name': 'sampleRate', 'type': 'float', 'value': 0.2, 'default': 0.2, 'readonly' : True},
            {'title': 'Number of samples (kS):', 'name': 'NumSamples', 'type': 'int', 'value': 40, 'default': 40, 'readonly' : True},
            {'title': 'Time range (ms):', 'name': 'Range', 'type': 'float', 'value': 200, 'default': 200, 'readonly': True}]},

        {'title': 'Amplitude (mV):', 'name': 'Amp', 'type': 'float', 'value': 5000, 'default': 5000},

        {'title': 'Offset (mV):','name': 'Offset','type': 'float','value': 0, 'default': 0},

        {'title': 'External reference clock parameters', 'name': 'clock_param', 'type': 'group', 'children': [
            {'title': 'Clock mode:', 'name': 'clockMode', 'type': 'itemselect', 'value': dict(all_items=[ "internal PLL", "external", "external reference" ], selected=["external reference"])} ,
            {'title': 'External ref. clock rate (MHz):', 'name': 'ExtClock', 'type': 'int', 'value': 80, 'default': 80},
            {'title': 'Clock threshold (V)', 'name': 'clock_th', 'type': 'float', 'value': 1.5, 'default': 1.5},
            ]}
    ]


    def ini_attributes(self):
        """ 
        Called at initialisation of the Daq View
        """
        self.controller: Spectrum_Wrapper_Single = None
        self.x_axis = None
        self.card = None
        self.manager = None
        self.hit_except = None
        self.trigger = None
        self.clock = None

        # --- Init all readonly values
        self.update_sampleRate()
        self.update_NumSamples()
        self.update_Range()


    def commit_settings(self, param: Parameter):
        """
        Called when param of ParameterTree is changed
        """

        if param.name() == "channels":
            channel = param.value()
            channel_nbr = int(channel[1])
            self.controller.setChannel(channel_nbr, self.settings.child('Amp').value(), self.settings.child('Offset').value())
        
        elif param.name() == "average":
            self.settings.child('lock_in', 'operation', 'integrate').setValue(not param.value())

        elif param.name() == "integrate":
            self.settings.child('lock_in', 'operation', 'average').setValue(not param.value())

        elif param.name() == "NumLPulses" or param.name() == "NumSinPulse":
            self.update_NumSamples()
            self.update_Range()
            self.update_sampleRate()

            # self.controller.update()  # TODO


    def ini_detector(self, controller=None):
        """
        Detector communication initialization
        """

        if self.is_master:
            self.controller = Spectrum_Wrapper_Single(duration=   self.settings.child("timing", "Range").value(), 
                                                      sample_rate=   self.settings.child("timing", "sampleRate").value())

            initialized = self.controller.initialise_device(clock_mode=             self.settings.child("clock_param", "clockMode").value(),
                                                            clock_frequency=        self.settings.child("clock_param", "ExtClock").value(),
                                                            channels_to_activate=   [ self.settings.child("channels", f"c{ii}").value() for ii in range(8)],
                                                            channel_amplitude=      self.settings["Amp"],
                                                            channel_offset=         self.settings["Offset"],
                                                            trigger_settings=       {"trigger_type":    self.settings.child("trig_params", "triggerType").value(),
                                                                                     "trigger_channel": self.settings.child("trig_params", "triggerChannel").value(),
                                                                                     "trigger_mode":    self.settings.child("trig_params", "triggerMode").value(),
                                                                                     "trigger_level":   self.settings.child("trig_params", "triggerLevel").value()}
                                                            )
            

        else:
            self.controller = controller
            initialized = True

        
        info = "Initialized"
        return info, initialized


    def close(self):
        """Terminate the communication protocol"""
        self.controller.terminate_the_communication(self.manager, self.hit_except) 


    def grab_data(self, Naverage=1, **kwargs):
        """ Start a grab from the detector
        """

        # --- Grab a Trace
        try:  data_tot = self.controller.grab_trace( post_trig_ms = 5 )     
        except Exception as e:
            print("Capture Failed !")
            print(e)
            self.emit_status(ThreadCommand('Update_Status', ['Card asked while running ']))
            self.hit_except = True

        dwa = DataFromPlugins(name='Trace', data=data_tot, dim='Data1D')

        data_to_export = [dwa]

        data = DataToExport('Spectrum', data=data_to_export)
        self.dte_signal.emit(data)


    def update_sampleRate(self):    self.settings.child('timing', 'sampleRate').setValue(       self.settings.child("timing", "NumSinPulse").value() / (1/ (self.settings.child("timing", "PulseFreq").value() * 1e3) ) * 1e-6      )  # Points per Pulse / PulsePeriod, in MHz
    def update_NumSamples(self):    self.settings.child('timing', 'NumSamples').setValue(       self.settings.child("timing", "NumLPulses").value() * self.settings.child("timing", "NumSinPulse").value()                          )    # Num of Pulses * Samples per Pulse
    def update_Range(self):         self.settings.child('timing', 'Range').setValue(        self.settings.child('timing', 'NumSamples').value() / (self.settings.child('timing', 'sampleRate').value()*1e6) * 1e3     )  # NumPulse / sampleRate[MHz], in ms


    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        self.controller.terminate_the_communication()
        return ''






def main(plugin_file=None, init=True, title='Testing'):
    """
    this method start a DAQ_Viewer object with this defined plugin as detector
    Returns
    -------
    """
    import sys
    from qtpy import QtWidgets
    from pymodaq.utils.gui_utils import DockArea
    from pymodaq.control_modules.daq_viewer import DAQ_Viewer
    from pathlib import Path
    from pymodaq_gui.utils.utils import mkQApp

    app = mkQApp("PyMoDAQ Viewer")

    win = QtWidgets.QMainWindow()
    area = DockArea()
    win.setCentralWidget(area)
    win.resize(1000, 500)
    win.setWindowTitle('PyMoDAQ Viewer')
    if plugin_file is None:
        detector = 'Spectrum_Test'
        det_type = f'DAQ1D'
    else:
        detector = Path(plugin_file).stem[13:]
        det_type = f'DAQ{Path(plugin_file).stem[4:6].upper()}'
    prog = DAQ_Viewer(area, title=title)
    win.show()
    prog.daq_type = det_type
    prog.detector = detector
    if init:
        prog.init_hardware_ui()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    