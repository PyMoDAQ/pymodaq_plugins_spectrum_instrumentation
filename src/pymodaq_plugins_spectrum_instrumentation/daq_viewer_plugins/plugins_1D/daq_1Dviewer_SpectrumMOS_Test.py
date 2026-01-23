import numpy as np
from pymodaq.utils.daq_utils import ThreadCommand, getLineInfo
from pymodaq.utils.data import DataFromPlugins, Axis, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter


import spcm
from spcm import units

from pymodaq_plugins_spectrum_instrumentation.hardware.SpectrumCard_wrapper_Single import Spectrum_Wrapper_Single


class DAQ_1DViewer_SpectrumMOS_Test(DAQ_Viewer_base):
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

        {'title': 'Clock mode:', 'name': 'clockMode', 'type': 'itemselect', 'value': dict(all_items=[ "internal PLL", "external", "external reference" ], selected=["external reference"])},

        {'title': 'Trigger parameters', 'name': 'trig_params', 'type': 'group', 'children':[
            {'title': 'Trigger:', 'name': 'triggerType', 'type': 'itemselect', 'value': dict(all_items=[ "None", "Channel trigger", "Software trigger", "External analog trigger"], selected=["External analog trigger"])},
            {'title': 'Trigger channel:', 'name': 'triggerChannel', 'type': 'itemselect', 'value': dict(all_items=[ "CH0", "CH1", "CH2", "CH3", "CH4", "CH5", "CH6", "CH7"], selected=["CH0"])},
            {'title': 'Trigger mode', 'name': 'triggerMode', 'type': 'itemselect', 'value': dict(all_items=[ "Rising edge", "Falling edge", "Both"], selected=["Rising edge"])},
            {'title': 'Trigger level (mV):', 'name': 'triggerLevel', 'type': 'slide', 'value': 100, 'default': 100, 'min': -500, 'max': 500, 'subtype': 'linear'}]},

        {'title': 'Timing', 'name': 'timing', 'type': 'group', 'children': [
            {'title': 'Laser pulses freq. (kHz):', 'name': 'PulseFreq', 'type': 'int', 'value': 1, 'default': 1, 'readonly' : True},
            {'title': 'Nbr. of laser pulses:', 'name': 'NumLPulses', 'type': 'int', 'value': 200, 'default': 200},
            {'title': 'Nbr. of samples / laser pulse:', 'name': 'NumSinPulse', 'type': 'int', 'value': 200, 'default': 200},
            {'title': 'Sample rate (MHz):', 'name': 'sampleRate', 'type': 'float', 'value': 0.2, 'default': 0.2, 'readonly' : True},
            {'title': 'Number of samples (kS):', 'name': 'NumSamples', 'type': 'int', 'value': 40, 'default': 40, 'readonly' : True},
            {'title': 'Time range (ms):', 'name': 'Range', 'type': 'float', 'value': 200, 'default': 200, 'readonly': True}]},

        {'title': 'Amplitude (mV):', 'name': 'Amp', 'type': 'float', 'value': 5000, 'default': 5000},

        {'title': 'Offset (mV):','name': 'Offset','type': 'float','value': 0, 'default': 0},

        {'title': 'Lock-in', 'name': 'lock_in', 'type': 'group', 'children': [
            {'title': 'Difference channel', 'name': 'diffChannel', 'type': 'itemselect', 'value': dict(all_items=["CH0","CH1", "CH2", "CH3", "CH4"], selected=["CH2"])},
            {'title': 'Intensity channel:', 'name': 'sumChannel', 'type': 'itemselect', 'value': dict(all_items=["CH0", "CH1", "CH2", "CH3", "CH4"], selected=["CH4"])},
            {'title': 'B pulses freq.: (Hz)', 'name': 'BPulseFreq', 'type': 'int', 'value': 500, 'default': 500},
            {'title': 'Subtract background', 'name': 'BG_sub', 'type': 'bool', 'value': True, 'default': True},
            {'title': 'Background wind. size:', 'name': 'BG_size', 'type': 'itemselect', 'value': dict(all_items=["0.125", "0.25", "0.5", "0.75"], selected=["0.125"])},
            {'title': 'PD gain:', 'name': 'Gain', 'type': 'float', 'value': 10, 'default': 10, 'readonly': True},
            {'title': 'Conversion factor:', 'name': 'Conversion', 'type': 'float', 'value': 2, 'default': 2, 'readonly': True},

            {'title': 'Plotting & Saving', 'name': 'PlotSave', 'type': 'group', 'children': [
                {'title': 'Show trace', 'name': 'showTrace', 'type': 'bool_push', 'value': False, 'default': False},
                {'title': 'Pulse train', 'name': 'PulseTrain', 'type': 'led_push', 'value': False, 'default': False},
                {'title': 'Pulse average', 'name': 'PulseAverage', 'type': 'led_push', 'value': True, 'default': True},
                {'title': 'I_Bd', 'name': 'I_Bd', 'type': 'led_push', 'value': False, 'default': False},
                {'title': 'I_Ba', 'name': 'I_Ba', 'type': 'led_push', 'value': False, 'default': False},
                {'title': 'D_Bd', 'name': 'D_Bd', 'type': 'led_push', 'value': False, 'default': False},
                {'title': 'D_Ba', 'name': 'D_Ba', 'type': 'led_push', 'value': False, 'default': False},
                {'title': 'NDa', 'name': 'NDa', 'type': 'led_push', 'value': False, 'default': False},
                {'title': 'ND_Bd', 'name': 'ND_Bd', 'type': 'led_push', 'value': False, 'default': False},
                {'title': 'ND_Ba', 'name': 'ND_Ba', 'type': 'led_push', 'value': False, 'default': False},
                {'title': 'phi_Bd', 'name': 'phi_Bd', 'type': 'led_push', 'value': False, 'default': False},
                {'title': 'phi_Ba', 'name': 'phi_Ba', 'type': 'led_push', 'value': False, 'default': False},
                {'title': 'phi_Pd', 'name': 'phi_Pd', 'type': 'led_push', 'value': False, 'default': False},
                {'title': 'phi_Pa', 'name': 'phi_Pa', 'type': 'led_push', 'value': False, 'default': False},
                {'title': 'Show & save STD', 'name': 'STD', 'type': 'bool', 'value': False, 'default': False}
                ]}]
        },

        {'title': 'External reference clock parameters', 'name': 'clock_param', 'type': 'group', 'children': [
            {'title': 'External ref. clock rate (MHz):', 'name': 'ExtClock', 'type': 'int', 'value': 80, 'default': 80},
            {'title': 'Clock threshold (V)', 'name': 'clock_th', 'type': 'float', 'value': 1.5, 'default': 1.5}] }
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
        self.activated_str = []

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
            print( self.settings.child('Timing', 'Range').value() )
            print( [ self.settings.child("channels", f"c{ii}") for ii in range(8)] )

            self.controller = Spectrum_Wrapper_Single(duration=   self.settings.child("Timing", "Range"), 
                                                      sample_rate=   self.settings.child("Timing", "sampleRate"))

            initialized = self.controller.initialise_device(clock_mode=         self.settings["clockMode"],
                                                            clock_frequency=        self.settings.child("clock_param", "ExtClock"),
                                                            channels_to_activate=       self.settings[""],
                                                            channel_amplitude=      [ self.settings.child("channels", f"c{ii}") for ii in range(8)],
                                                            channel_offset=         self.settings["Offset"],
                                                            trigger_settings=       {"trigger_type": self.settings.child("trig_params", "triggerType"),
                                                                                     "trigger_channel": self.settings.child("trig_params", "triggerChannel"),
                                                                                     "trigger_mode": self.settings.child("trig_params", "triggerMode"),
                                                                                     "trigger_level": self.settings.child("trig_params", "triggerLevel")}
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

        NumSamples = self.settings.child('timing', 'NumSamples').value()
        sampleRate = self.settings.child('timing', 'sampleRate').value()

        # --- Grab a Trace
        try:  data_tot = self.controller.grab_trace( post_trig_ms = 5 )     #TODO : Make Post trig variable

        except Exception as e:
            print("Capture Failed !")
            print(e)
            self.emit_status(ThreadCommand('Update_Status', ['Card asked while running ']))
            self.hit_except = True

        print(data_tot.shape)
        # nbrPts =NumSamples * 1000  #kS to S


        if self.settings.child('lock_in', 'diffChannel').value()['selected'] == ['CH4']:
            ii = self.activated_str.index('CH4')
            index = len(self.activated_str[:ii])    # Get the index in channel list of difference channel
            data2reshape = data_tot[index]

        if self.settings.child('lock_in', 'diffChannel').value()['selected'] == ['CH3']:
            ii = self.activated_str.index('CH3')
            index = len(self.activated_str[:ii])
            data2reshape = data_tot[index]

        if self.settings.child('lock_in', 'diffChannel').value()['selected'] == ['CH2']:
            ii = self.activated_str.index('CH2')
            index = len(self.activated_str[:ii])
            data2reshape = data_tot[index]


        if self.settings.child('lock_in', 'diffChannel').value()['selected'] == ['CH1']:
            ii = self.activated_str.index('CH1')
            index = len(self.activated_str[:ii])
            data2reshape = data_tot[index]
        if self.settings.child('lock_in', 'diffChannel').value()['selected'] == ['CH0']:
            data2reshape = data_tot[0]

            ##############

        if self.settings.child('lock_in', 'sumChannel').value()['selected'] == ['CH4']:
            ii = self.activated_str.index('CH4')
            index = len(self.activated_str[:ii])
            data_norm = data_tot[index]

        if self.settings.child('lock_in', 'sumChannel').value()['selected'] == ['CH3']:
            ii = self.activated_str.index('CH3')
            index = len(self.activated_str[:ii])
            data_norm = data_tot[index]

        if self.settings.child('lock_in', 'sumChannel').value()['selected'] == ['CH2']:
            ii = self.activated_str.index('CH2')
            index = len(self.activated_str[:ii])
            data_norm = data_tot[index]

        if self.settings.child('lock_in', 'sumChannel').value()['selected'] == ['CH1']:
            ii = self.activated_str.index('CH1')
            index = len(self.activated_str[:ii])
            data_norm = data_tot[index]

        if self.settings.child('lock_in', 'sumChannel').value()['selected'] == ['CH0']:
            data_norm = data_tot[0]



        try:

            #print('shape = ', np.shape(data2reshape))

            pulseFreq = self.settings.child('timing', 'PulseFreq').value()  #kHz
            BpulseFreq = self.settings.child('lock_in', 'BPulseFreq').value()*2

            PN = int(self.settings.child('timing', 'Range').value() * pulseFreq )  #ms / kHz = 1
            #print("PN = ", PN)
            BPN = int(self.settings.child('timing', 'Range').value() * (BpulseFreq*1e-3))

            PW = int(nbrPts/PN)

            PWb = int(PN/BPN)
        #Compute IBd, DBd and phi_Bd


            ######background subtraction





            data_chan_reshaped = data2reshape.reshape(PN, PW)
            #print('BPN = ', BPN)


            data_norm_reshaped = data_norm.reshape(PN, PW)
            #if self.settings.child('lock_in', 'operation', 'average').value() == True:
            #    data_chan_averaged = np.mean(data_chan_reshaped, axis = 1) -
            #    data_norm_averaged = np.mean(data_norm_reshaped, axis = 1)
            #    label = 'Averaged'
            #if self.settings.child('lock_in', 'operation', 'integrate').value() == True:

            if self.settings.child('lock_in', 'BG_sub').value() == True:
                data_chan_int = -np.sum(data_chan_reshaped[:,:PW//8], axis=1) + np.sum(data_chan_reshaped[:,PW//8:], axis=1)/7
                data_norm_int = -np.sum(data_norm_reshaped[:,:PW//8], axis=1) + np.sum(data_norm_reshaped[:,PW//8:], axis=1)/7
            else:
                data_chan_int = np.sum(data_chan_reshaped, axis=1)
                data_norm_int = np.sum(data_norm_reshaped, axis=1)
            #print(PW//4)
            label = 'Integrated - bg'



            ##### Computing laser pulse averaging

            D_average = np.mean(data_chan_int)
            I_average = np.mean(data_norm_int)

            ##### Computing I_Bd
            data_norm_int_reshaped = data_norm_int.reshape(BPN, PWb)
            mean_norm_over_B_pulse = np.sum(data_norm_int_reshaped, axis=1)
            if len(mean_norm_over_B_pulse)%2 !=0 :
                mean_norm_over_B_pulse = mean_norm_over_B_pulse[:-1]
            I_Bd =   mean_norm_over_B_pulse [::2] - mean_norm_over_B_pulse [1::2]
            I_Bd = np.mean(I_Bd)

            ##### Computing I_Ba
            I_Ba = np.mean(mean_norm_over_B_pulse)

            ##### Computing D_Bd
            data_diff_int_reshaped = data_chan_int.reshape(BPN, PWb)
            mean_diff_over_B_pulse = np.mean(data_diff_int_reshaped, axis=1)
            if len(mean_diff_over_B_pulse)%2 !=0 :
                mean_diff_over_B_pulse = mean_diff_over_B_pulse[:-1]
            D_Bd =   mean_diff_over_B_pulse [::2] - mean_diff_over_B_pulse [1::2]
            D_Bd = np.mean(D_Bd)

            ##### Computing D_Ba
            D_Ba = np.mean(mean_diff_over_B_pulse)

            #####normailizing

            normalized_D = np.divide(data_chan_int, data_norm_int)*1/(self.settings.child('lock_in', 'Gain').value())/2

            #####computing NDa
            NDa = np.mean(normalized_D)

            #####computing ND_Bd
            normalized_DB_reshaped = normalized_D.reshape(BPN, PWb)
            mean_normalized_DB = np.mean(normalized_DB_reshaped, axis=1)
            if len(mean_normalized_DB)%2 !=0 :
                mean_normalized_DB = mean_normalized_DB[:-1]
            normalized_D_BD = mean_normalized_DB[::2] - mean_normalized_DB[1::2]
            ND_Bd = np.mean(normalized_D_BD)

            #####computing ND_Ba
            ND_Ba = np.mean(mean_normalized_DB)


            ##### Computing phi_Ba
            phi_Ba = ND_Ba /  self.settings.child('lock_in', 'Conversion').value()
            ##### Computing phi_Bd
            # application of gain and conversion

            phi_Bd = ND_Bd / self.settings.child('lock_in', 'Conversion').value()



            ##### Computing phi_Ba

            ##### Computing phi_PdBa

            ##### Computing phi_PdBd

            ##### Computing phi_PaBd


            ##### Computing phi_PaBa

            #application of gain and conversion




            #data_chan_int *= 1/(self.settings.child('lock_in', 'Gain').value())*self.settings.child('lock_in', 'Conversion').value()

            #pump_off = data_chan_int[::2]
            #pump_on = data_chan_int[1::2]

            #diff_pump_on_off = pump_on - pump_off

            #Mean_diff = np.mean(diff_pump_on_off)


            #self.x_axis = Axis('Time', units='µs', data=data_x, index=0)

            #print('data_chan_averaged = ', data_chan_averaged)
            #print('status : ', self.card.status())
        except:
            self.emit_status(ThreadCommand('Update_Status', [
                'The nbr of laser pulses is not an integer multiple of the nbr of B pulses ! ']))
            self.hit_except = True
            #if not exit(self.manager):
            #    raise


        dwa1D1 = DataFromPlugins(name='1. Trace', data=data_tot, dim='Data1D', labels=self.activated_str, do_plot=self.settings.child('lock_in', 'PlotSave', 'showTrace').value(), do_save=self.settings.child('lock_in', 'PlotSave', 'showTrace').value())#, axes=[self.x_axis])
        #dwa1D2 = DataFromPlugins(name='2. '+label, data=data_chan_int, dim='Data1D', labels=[label+' norm. data', 'Pulse Nbr'], do_plot=False)

        dwatrain = DataFromPlugins(name='2. Pulse train', data=[data_chan_int, data_norm_int], dim='Data1D',
                                 labels=['D', 'I'], do_plot=self.settings.child('lock_in', 'PlotSave', 'PulseTrain').value(), do_save=True)

        dwa1D3 = DataFromPlugins(name='3. Pulse average', data=[np.array([D_average]), np.array([I_average])], dim='Data0D',
                                 labels=['Da', 'Ia'], do_plot=self.settings.child('lock_in', 'PlotSave', 'PulseAverage').value(), do_save=self.settings.child('lock_in', 'PlotSave', 'PulseAverage').value())
        dwaIBd = DataFromPlugins(name='I_Bd', data=I_Bd, dim='Data0D',
                                 labels=['I_Bd'], do_plot=self.settings.child('lock_in', 'PlotSave', 'I_Bd').value(), do_save=self.settings.child('lock_in', 'PlotSave', 'I_Bd').value())
        dwaIBa    = DataFromPlugins(name='I_Ba', data=I_Ba, dim='Data0D',
                                 labels=['I_Ba'], do_plot=self.settings.child('lock_in', 'PlotSave', 'I_Ba').value(), do_save=self.settings.child('lock_in', 'PlotSave', 'I_Ba').value())
        dwaNDa = DataFromPlugins(name='NDa', data=NDa, dim='Data0D',
                                 labels=['NDa'], do_plot=self.settings.child('lock_in', 'PlotSave', 'NDa').value(), do_save=self.settings.child('lock_in', 'PlotSave', 'NDa').value())
        dwaDBd = DataFromPlugins(name='D_Bd', data=D_Bd, dim='Data0D',
                                 labels=['D_Bd'], do_plot=self.settings.child('lock_in', 'PlotSave', 'D_Bd').value(), do_save=self.settings.child('lock_in', 'PlotSave', 'D_Bd').value())
        dwaDBa    = DataFromPlugins(name='D_Ba', data=D_Ba, dim='Data0D',
                                 labels=['D_Ba'], do_plot=self.settings.child('lock_in', 'PlotSave', 'D_Ba').value(), do_save=self.settings.child('lock_in', 'PlotSave', 'D_Ba').value())

        dwaNDBd = DataFromPlugins(name='ND_Bd', data=ND_Bd, dim='Data0D',
                                 labels=['ND_Bd'], do_plot=self.settings.child('lock_in', 'PlotSave', 'ND_Bd').value(), do_save=self.settings.child('lock_in', 'PlotSave', 'ND_Bd').value())
        dwaNDBa    = DataFromPlugins(name='ND_Ba', data=ND_Ba, dim='Data0D',
                                 labels=['ND_Ba'], do_plot=self.settings.child('lock_in', 'PlotSave', 'ND_Ba').value(), do_save=self.settings.child('lock_in', 'PlotSave', 'ND_Ba').value())
        dwaphi_Bd = DataFromPlugins(name='phi_Bd', data=phi_Bd, dim='Data0D',
                                 labels=['phi_Bd'], do_plot=self.settings.child('lock_in', 'PlotSave', 'phi_Bd').value(), do_save=self.settings.child('lock_in', 'PlotSave', 'phi_Bd').value())
        dwaphi_Ba    = DataFromPlugins(name='phi_Ba', data=phi_Ba, dim='Data0D',
                                 labels=['phi_Ba'], do_plot=self.settings.child('lock_in', 'PlotSave', 'phi_Ba').value(), do_save=self.settings.child('lock_in', 'PlotSave', 'phi_Ba').value())




        # New Version
        data_to_export = []
        export = {'PulseTrain':dwatrain, 'PulseAverage':dwa1D3, 'I_Bd':dwaIBd, 'I_Ba':dwaIBa, 'NDa':dwaNDa, 'D_Bd':dwaDBd, 'D_Ba':dwaDBa, 'ND_Bd':dwaNDBd, 'ND_Ba':dwaNDBa, 'phi_Bd':dwaphi_Bd, 'phi_Ba':dwaphi_Ba }
        for type_str in export.keys():
            if self.settings.child('lock_in', 'PlotSave', type_str).value():
                data_to_export.append(export[type_str])  # Only plot those we want to save


        # Old Version
        data_to_export = [dwatrain, dwa1D3, dwa1D1, dwaIBd, dwaIBa, dwaNDa, dwaDBd,dwaDBa,dwaNDBd, dwaNDBa, dwaphi_Bd, dwaphi_Ba]




        data = DataToExport('SPLockIn', data=data_to_export)
        self.dte_signal.emit(data)


        ##asynchrone version (non-blocking function with callback)
        # self.controller.your_method_to_start_a_grab_snap(self.callback)
        #########################################################


    def update_sampleRate(self):    self.settings.child('Timing', 'sampleRate') = self.settings.child("Timing", "NumSinPulse") / (1/ (self.settings.child("Timing", "pulseFreq") * 1e3) ) * 1e-6   # Points per Pulse / PulsePeriod in MHz
    def update_NumSamples(self):    self.settings.child('Timing', 'NumSamples') = self.settings.child("Timing", "NumLPulses") * self.settings.child("Timing", "NumSinPulse")    # Num of Pulses * Samples per Pulse
    def update_Range(self):    self.settings.child('Timing', 'Range') = self.settings.child("Timing", "NumLPulses") / self.settings.child('Timing', 'sampleRate')


    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        self.controller.terminate_the_communication()
        return ''







if __name__ == "__main__":
    main()