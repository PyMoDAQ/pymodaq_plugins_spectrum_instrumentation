import numpy as np
from pymodaq.utils.daq_utils import ThreadCommand, getLineInfo
from pymodaq.utils.data import DataFromPlugins, Axis, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter

# import spcm
# from spcm import units # spcm uses the pint library for unit handling (units is a UnitRegistry object)
import PyQt5.QtCore as Qtc
import PyQt5.QtWidgets as Qtw
import sys
import spcm
from spcm import units
# from pymodaq_plugins_template2.hardware.SpectrumCard_wrapper import Digitizer_Wrapper
from ...hardware.SpectrumCard_wrapper2 import Digitizer_Wrapper


# class PythonWrapperOfYourInstrument:
#  TODO Replace this fake class with the import of the real python wrapper of your instrument
#   pass


# TODO:
# (1) change the name of the following class to DAQ_1DViewer_TheNameOfYourChoice
# (2) change the name of this file to daq_1Dviewer_TheNameOfYourChoice ("TheNameOfYourChoice" should be the SAME
#     for the class name and the file name.)
# (3) this file should then be put into the right folder, namely IN THE FOLDER OF THE PLUGIN YOU ARE DEVELOPING:
#     pymodaq_plugins_my_plugin/daq_viewer_plugins/plugins_1D
class DAQ_1DViewer_SpectrumLockIn(DAQ_Viewer_base):
    """ Instrument plugin class for a 1D viewer.

    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Viewer module through inheritance via
    DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and the Python wrapper of a particular instrument.

    TODO Complete the docstring of your plugin with:
        * The set of instruments that should be compatible with this instrument plugin.
        * With which instrument it has actually been tested.
        * The version of PyMoDAQ during the test.
        * The version of the operating system.
        * Installation instructions: what manufacturer’s drivers should be installed to make it run?

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.

    # TODO add your particular attributes here if any

        """
    #led_push
    params = comon_parameters + [

        {'title': 'Channels:',
         'name': 'channels',
         'type': 'group', 'children':
            [{'title': 'CH0', 'name': 'c0', 'type': 'led_push', 'value': True, 'default': True},
             {'title': 'CH1', 'name': 'c1', 'type': 'led_push', 'value': False, 'default': False},
             {'title': 'CH2', 'name': 'c2', 'type': 'led_push', 'value': True, 'default': True},
             {'title': 'CH3', 'name': 'c3', 'type': 'led_push', 'value': False, 'default': False},
             {'title': 'CH4', 'name': 'c4', 'type': 'led_push', 'value': True, 'default': True},
             {'title': 'CH5', 'name': 'c5', 'type': 'led_push', 'value': False, 'default': False},
             {'title': 'CH6', 'name': 'c6', 'type': 'led_push', 'value': False, 'default': False},
             {'title': 'CH7', 'name': 'c7', 'type': 'led_push', 'value': False, 'default': False}
             ]},

        {'title': 'Clock mode:',
         'name': 'clockMode',
         'type': 'itemselect',
         'value': dict(all_items=[
             "internal PLL", "external", "external reference"], selected=["external reference"])},

        {'title': 'Trigger parameters', 'name': 'trig_params', 'type': 'group', 'children':
            [{'title': 'Trigger:',
         'name': 'triggerType',
         'type': 'itemselect',
         'value': dict(all_items=[
             "None", "Channel trigger", "Software trigger", "External analog trigger"], selected=["Channel trigger"])},

             {'title': 'Trigger channel:',
              'name': 'triggerChannel',
              'type': 'itemselect',
              'value': dict(all_items=[
                  "CH0", "CH1", "CH2", "CH3", "CH4", "CH5", "CH6", "CH7"], selected=["CH0"])},

             {'title': 'Trigger mode',
              'name': 'triggerMode',
              'type': 'itemselect',
              'value': dict(all_items=[
                  "Rising edge", "Falling edge", "Both"], selected=["Rising edge"])},

             {'title': 'Trigger level (mV):', 'name': 'trigLevel', 'type': 'slide', 'value': 100, 'default': 100,
              'min': -500,
              'max': 500, 'subtype': 'linear'}]},

        {'title': 'Timing', 'name': 'timing', 'type': 'group', 'children':
            [{'title': 'Sample rate (MHz):',
         'name': 'sampleRate',
         'type': 'float',
         'value': 0.2, 'default': 0.2},
             {'title': 'Number of samples (kS):',
              'name': 'NumSamples',
              'type': 'int',
              'value': 10, 'default': 10},
             {'title': 'Segment size (kS):',
              'name': 'SamplesPerSegment',
              'type': 'int',
              'value':10, 'default': 10},
             {'title': 'Time range (ms):',
              'name': 'Range',
              'type': 'float',
              'value': 50, 'default': 50, 'readonly': True}
             ]},







        {'title': 'Amplitude (mV):',
         'name': 'Amp',
         'type': 'float',
         'value': 1000, 'default': 1000},

        {'title': 'Offset (mV):',
         'name': 'Offset',
         'type': 'float',
         'value': 0, 'default': 0},



        {'title': 'Lock-in parameters', 'name': 'lock_in', 'type': 'group', 'children':
            [{'title': 'Channel of interest:',
         'name': 'interestChannel',
         'type': 'itemselect',
         'value': dict(all_items=[
             "CH0",  "CH2", "CH3", "CH4"], selected=["CH2"])},
             {'title': 'Normalization channel:',
              'name': 'normChannel',
              'type': 'itemselect',
              'value': dict(all_items=[
                  "CH0", "CH2", "CH3", "CH4"], selected=["CH4"])},
                {'title': 'Nbr of pulses:', 'name': 'PulseNbr', 'type': 'int', 'value': 20,
              'default': 50},
             {'title': 'Hide trace', 'name': 'showTrace', 'type': 'bool_push', 'value': True, 'default': True},
             {'title': 'Hide pre-averaged data', 'name': 'showRest', 'type': 'bool_push', 'value': True, 'default': True},
             {'title': 'Operation', 'name': 'operation', 'type': 'group', 'children':
                 [ {'title': 'Average', 'name': 'average', 'type': 'bool', 'value': False},
                   {'title': 'Integrate', 'name': 'integrate', 'type': 'bool', 'value': True}]},
             {'title': 'PD gain:',
              'name': 'Gain',
              'type': 'float',
              'value': 100, 'default': 100, 'readonly': False},
             {'title': 'Conversion factor:',
              'name': 'Conversion',
              'type': 'float',
              'value': 2, 'default': 2, 'readonly': False}

             ]

         },

        {'title': 'External reference clock parameters', 'name': 'clock_param', 'type': 'group', 'children':
            [{'title': 'External ref. clock rate (MHz):', 'name': 'ExtClock', 'type': 'int', 'value': 80, 'default': 80},
             {'title': 'Clock threshold (V)', 'name': 'clock_th', 'type': 'float', 'value': 1.5, 'default': 1.5}]

         }
    ]


    def ini_attributes(self):
        #  TODO declare the type of the wrapper (and assign it to self.controller) you're going to use for easy
        #  autocompletion

        self.controller: Digitizer_Wrapper = None
        # self.controller = Digitizer_Wrapper()
        # TODO declare here attributes you want/need to init with a default value

        self.x_axis = None

        self.card = None

        self.manager = None

        self.hit_except = None

        self.trigger = None

        self.clock = None

        self.activated_str = []

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        ## TODO for your custom plugin
        if param.name() == "channels":
            channel = param.value()

            channel_nbr = int(channel[1])

            self.controller.setChannel(channel_nbr, self.settings.child('Amp').value(),
                                       self.settings.child('Offset').value())

        if param.name() == "sampleRate":
            #clock = spcm.Clock(self.card)
            #clock.mode(spcm.SPC_CM_INTPLL)  # clock mode internal PLL
            self.clock.sample_rate(self.settings.child('timing', 'sampleRate').value() * units.MHz, return_unit=units.MHz)
            self.settings.child('timing', 'Range').setValue(self.settings.child('timing','NumSamples').value() / self.settings.child('timing', 'sampleRate').value())

        if param.name() == "NumSamples":
            self.settings.child('timing', 'Range').setValue(self.settings.child('timing','NumSamples').value() / self.settings.child('timing', 'sampleRate').value())

        if param.name() == "Offset":
            self.channels[0].offset(self.settings.child('Offset').value() * units.mV, return_unit=units.mV)

        if param.name() == "Amp":
            self.channels.amp(self.settings.child('Amp').value() * units.mV)

        if param.name() == "trigLevel":
            self.trigger.ch_level0(self.channels[0], param.value() * units.mV, return_unit=units.mV)

        if param.name() == "Range":
            wait_time = self.settings.child('timing', 'Range').value()
            self.emit_status(ThreadCommand('update_main_settings', [['wait_time'], wait_time*1e-3*2, 'value']))
            self.settings.child('timing', 'Range').setValue(self.settings.child('timing','NumSamples').value() / self.settings.child('timing', 'sampleRate').value())
        #        elif ...

        if param.name() == "average":
            self.settings.child('lock_in', 'operation', 'integrate').setValue(not param.value())

        if param.name() == "integrate":
            self.settings.child('lock_in', 'operation', 'average').setValue(not param.value())


        ##

    def ini_detector(self, controller=None):

        """Detector communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator/detector by controller
            (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """
        #print('value = ', self.settings.child('NumSamples').value()*1e3/(self.settings.child('sampleRate').value()*1e6)*1e3*2)
        self.emit_status(ThreadCommand('update_main_settings', [['wait_time'], self.settings.child('timing', 'NumSamples').value()*1e3/(self.settings.child('timing', 'sampleRate').value()*1e6)*1e3*2, 'value']))
        #self.emit_status(ThreadCommand('update_main_settings', [['wait_time'], 40, 'value']))
        self.emit_status(ThreadCommand('update_main_settings', [['refresh_time'], self.settings.child('timing', 'NumSamples').value()*1e3/(self.settings.child('timing', 'sampleRate').value()*1e6)*1e3, 'value']))

        self.settings.child('timing', 'Range').setValue(
            self.settings.child('timing', 'NumSamples').value() / self.settings.child('timing', 'sampleRate').value())

        self.manager = (spcm.Card('/dev/spcm0'))
        enter = type(self.manager).__enter__
        exit = type(self.manager).__exit__
        value = enter(self.manager)
        self.hit_except = False

        try:
            self.card = value
        #except:
            #hit_except = True
            #if not exit(self.manager, *sys.exc_info()):
                #raise

                ###### try standard setup

        #try:

            # card : spcm.Card
            # with spcm.Card('/dev/spcm0') as card:                       # if you want to open a specific card
            # with spcm.Card('TCPIP::192.168.1.10::inst0::INSTR') as card:  # if you want to open a remote card
            # with spcm.Card(serial_number=12345) as card:                  # if you want to open a card by its serial number
            # card = spcm.Card(card_type=spcm.SPCM_TYPE_AI)         # if you want to open the first card of a specific type

            # do a simple standard setup
            self.card.card_mode(spcm.SPC_REC_STD_MULTI)  # single trigger standard mode
            self.card.timeout(1 * units.s)  # timeout 50 s


            self.trigger = spcm.Trigger(self.card)



            self.clock = spcm.Clock(self.card)
            if self.settings.child('clockMode').value()['selected'] == ["internal PLL"]:
                self.clock.mode(spcm.SPC_CM_INTPLL)  # clock mode internal PLL
            if self.settings.child('clockMode').value()['selected'] == ["external reference"]:

                self.clock.mode(spcm.SPC_CM_EXTREFCLOCK)  # external reference clock
                #self.clock.mode(spcm.SPC_REFERENCECLOCK, self.settings.child('clock_param', 'ExtClock').value()* units.MHz) #80MHz
                self.clock.reference_clock(self.settings.child('clock_param', 'ExtClock').value()* units.MHz)

                #self.clock.mode(spcm.SPC_CLOCK_THRESHOLD, self.settings.child('clock_param', 'clock_th').value()* units.V)
                #self.clock.threshold(self.settings.child('clock_param', 'clock_th').value()* units.V)



            #self.emit_status(ThreadCommand('Update_Status', ['Using external reference clock']))


            self.clock.sample_rate(self.settings.child('timing', 'sampleRate').value() * units.MHz, return_unit=units.MHz)

            # setup the channels

            activated_channels = []

            for ii in range(8):
                if self.settings.child('channels', 'c'+str(ii)).value() == True:
                    self.activated_str.append('CH'+str(ii))
                    if ii == 0:
                        activated_channels.append(spcm.CHANNEL0)
                    if ii == 1:
                        activated_channels.append(spcm.CHANNEL1)
                    if ii == 2:
                        activated_channels.append(spcm.CHANNEL2)
                    if ii == 3:
                        activated_channels.append(spcm.CHANNEL3)
                    if ii == 4:
                        activated_channels.append(spcm.CHANNEL4)
                    if ii == 5:
                        activated_channels.append(spcm.CHANNEL5)
                    if ii == 6:
                        activated_channels.append(spcm.CHANNEL6)
                    if ii == 7:
                        activated_channels.append(spcm.CHANNEL7)

            if len(activated_channels) == 1:
                self.channels = spcm.Channels(self.card, card_enable=activated_channels[0])
            if len(activated_channels) == 2:
                self.channels = spcm.Channels(self.card, card_enable=activated_channels[0] | activated_channels[1])
            if len(activated_channels) == 3:
                self.channels = spcm.Channels(self.card, card_enable=activated_channels[0] | activated_channels[1] | activated_channels[2] | spcm.CHANNEL7)
            if len(activated_channels) == 4:
                self.channels = spcm.Channels(self.card, card_enable=activated_channels[0] | activated_channels[1] | activated_channels[2] | activated_channels[3])
            if len(activated_channels) == 5:
                self.channels = spcm.Channels(self.card, card_enable=spcm.CHANNEL0 | spcm.CHANNEL1 | spcm.CHANNEL2 | spcm.CHANNEL3 | spcm.CHANNEL4 | spcm.CHANNEL5 | spcm.CHANNEL6 | spcm.CHANNEL7)



            # self.channels = spcm.Channels(self.card, card_enable=spcm.CHANNEL0 | spcm.CHANNEL1| spcm.CHANNEL2| spcm.CHANNEL3)#|spcm.CHANNEL1) # enable channel 0
            self.channels.amp(self.settings.child('Amp').value() * units.mV)
            self.channels[0].offset(self.settings.child('Offset').value() * units.mV, return_unit=units.mV)

            self.channels.termination(1)




            if self.settings.child('trig_params', 'triggerType').value()['selected'] == ['None']:
                self.trigger.or_mask(spcm.SPC_TMASK_NONE)  # trigger set to none
                self.trigger.ch_or_mask0(self.channels[0].ch_mask())
            if self.settings.child('trig_params', 'triggerType').value()['selected'] == ['Software trigger']:
                self.trigger.or_mask(spcm.SPC_TMASK_SOFTWARE)  # trigger set to software
            if self.settings.child('trig_params', 'triggerType').value()['selected'] == ['External analog trigger']:
                self.trigger.or_mask(spcm.SPC_TMASK_EXT0)  # trigger set to external analog

            if self.settings.child('trig_params', 'triggerType').value()['selected'] == ['Channel trigger']:
                self.trigger.or_mask(spcm.SPC_TMASK_NONE)
                if self.settings.child('trig_params', 'triggerChannel').value()['selected'] == ['CH0']:
                    self.trigger.ch_or_mask0(spcm.SPC_TMASK0_CH0)
                if self.settings.child('trig_params', 'triggerChannel').value()['selected'] == ['CH1']:
                    self.trigger.ch_or_mask0(spcm.SPC_TMASK0_CH1)
                if self.settings.child('trig_params', 'triggerChannel').value()['selected'] == ['CH2']:
                    self.trigger.ch_or_mask0(spcm.SPC_TMASK0_CH2)
                if self.settings.child('trig_params', 'triggerChannel').value()['selected'] == ['CH3']:
                    self.trigger.ch_or_mask0(spcm.SPC_TMASK0_CH3)
                if self.settings.child('trig_params', 'triggerChannel').value()['selected'] == ['CH4']:
                    self.trigger.ch_or_mask0(spcm.SPC_TMASK0_CH4)
                if self.settings.child('trig_params', 'triggerChannel').value()['selected'] == ['CH5']:
                    self.trigger.ch_or_mask0(spcm.SPC_TMASK0_CH5)
                if self.settings.child('trig_params', 'triggerChannel').value()['selected'] == ['CH6']:
                    self.trigger.ch_or_mask0(spcm.SPC_TMASK0_CH6)
                if self.settings.child('trig_params', 'triggerChannel').value()['selected'] == ['CH7']:
                    self.trigger.ch_or_mask0(spcm.SPC_TMASK0_CH7)




            self.trigger.and_mask(spcm.SPC_TMASK_NONE)  # no AND mask


            # channels.coupling(spcm.COUPLING_DC)

            # Channel triggering
            #self.trigger.ch_or_mask0(self.channels[0].ch_mask())

            if self.settings.child('trig_params', 'triggerMode').value()['selected'] == ['Rising edge']:
                self.trigger.ch_mode(self.channels[0], spcm.SPC_TM_POS)
            if self.settings.child('trig_params', 'triggerMode').value()['selected'] == ['Falling edge']:
                self.trigger.ch_mode(self.channels[0], spcm.SPC_TM_NEG)
            if self.settings.child('trig_params', 'triggerMode').value()['selected'] == ['Both']:
                self.trigger.ch_mode(self.channels[0], spcm.SPC_TM_BOTH)

            self.trigger.ch_level0(self.channels[0], self.settings.child('trig_params', 'trigLevel').value() * units.mV,
                                   return_unit=units.mV)

            # define the data buffer
            # data_transfer = spcm.DataTransfer(self.card)
            # data_transfer.duration(self.settings.child('Range').value()*units.us, post_trigger_duration=self.settings.child('postTrigDur').value()*units.us)
            # self.card.start(spcm.M2CMD_CARD_ENABLETRIGGER, spcm.M2CMD_DATA_WAITDMA)

        except:
            self.hit_except = True
            if not exit(self.manager, *sys.exc_info()):
                raise

        # self.emit_status(ThreadCommand('show_splash', 'Starting initialization ...'))
        # Qtc.QThread.msleep(500)
        self.ini_detector_init(old_controller=controller,
                               new_controller=Digitizer_Wrapper())
        #self.emit_status(ThreadCommand('show_splash', 'Connecting to card ...'))
        #Qtc.QThread.msleep(500)

        #self.emit_status(ThreadCommand('show_splash', 'Enjoy taking data :)'))
        #Qtc.QThread.msleep(1000)
        # QtCore.QThread.msleep(500)
        # initialize viewers with the future type of data
        self.dte_signal_temp.emit(DataToExport('Card', data=[DataFromPlugins(name='Trace1', data=[np.zeros((100))],
                                                                             dim='Data1D',
                                                                             labels=[])]))




        NumSamples = self.settings.child('timing', 'NumSamples').value()

        SamplesPerSegment = self.settings.child('timing', 'SamplesPerSegment').value()
        num_samples = int(NumSamples * 1e3 /1024 *units.KiS )
        samples_per_segment = int(SamplesPerSegment * 1e3 /1024 *units.KiS )
        self.multiple_recording = spcm.Multi(self.card)

        self.multiple_recording.memory_size(num_samples)
        self.multiple_recording.allocate_buffer(samples_per_segment)
        post  = self.multiple_recording.post_trigger(samples_per_segment//2)
        #print('post trig = ', post)









        self.emit_status(ThreadCommand('close_splash'))

        info = "Initialized"
        initialized = True
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        ## TODO for your custom plugin
        # raise NotImplemented  # when writing your own plugin remove this line
        self.controller.terminate_the_communication(self.manager,
                                                    self.hit_except)  # when writing your own plugin replace this line

    def grab_data(self, Naverage=1, **kwargs):


        # self.emit_status(ThreadCommand('show_splash', 'Bla ...'))
        # Qtc.QThread.msleep(1000)
        """Start a grab from the detector

        Parameters
        ----------
        Naverage: int
            Number of hardware averaging (if hardware averaging is possible, self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        kwargs: dict
            others optionals arguments
        """
        ## TODO for your custom plugin: you should choose EITHER the synchrone or the asynchrone version following

        ##synchrone version (blocking function)
        NumSamples = self.settings.child('timing', 'NumSamples').value()

        SamplesPerSegment = self.settings.child('timing', 'SamplesPerSegment').value()

        data_tot = self.controller.start_a_grab_snap(self.card, self.channels, NumSamples, SamplesPerSegment, self.multiple_recording)
        #data_tot = np.array(data_tot)
        #print('data = ', data_tot)
        # self.emit_status(ThreadCommand('show_splash', 'Bla 2 ...'))

        #data_x = self.controller.get_the_x_axis()

        sampleRate = self.settings.child('timing', 'sampleRate').value()
        #nbrPts = int(sampleRate * Range )
        nbrPts =SamplesPerSegment * 1000  #kS to S
        #data_x = np.linspace( -Range + postTrigDur, postTrigDur, nbrPts)
        #print(nbrPts)
        #Lock in

        if self.settings.child('lock_in', 'interestChannel').value()['selected'] == ['CH4']:
            data2reshape = data_tot[3]

        if self.settings.child('lock_in', 'interestChannel').value()['selected'] == ['CH3']:
            data2reshape = data_tot[2]

        if self.settings.child('lock_in', 'interestChannel').value()['selected'] == ['CH2']:
            data2reshape = data_tot[1]

        if self.settings.child('lock_in', 'interestChannel').value()['selected'] == ['CH0']:
            data2reshape = data_tot[0]

        ########################
        if self.settings.child('lock_in', 'normChannel').value()['selected'] == ['CH4']:
            data_norm = data_tot[3]

        if self.settings.child('lock_in', 'normChannel').value()['selected'] == ['CH3']:
            data_norm = data_tot[2]

        if self.settings.child('lock_in', 'normChannel').value()['selected'] == ['CH2']:
            data_norm = data_tot[1]

        if self.settings.child('lock_in', 'normChannel').value()['selected'] == ['CH0']:
            data_norm = data_tot[0]

        #print('shape = ', np.shape(data2reshape))

        PN = self.settings.child('lock_in', 'PulseNbr').value()
        PW = int(nbrPts/PN)



        data_chan_reshaped = data2reshape.reshape(PN, PW)
        data_norm_reshaped = data_norm.reshape(PN, PW)
        if self.settings.child('lock_in', 'operation', 'average').value() == True:
            data_chan_averaged = np.mean(data_chan_reshaped, axis = 1)
            data_norm_averaged = np.mean(data_norm_reshaped, axis = 1)
            label = 'Averaged'
        if self.settings.child('lock_in', 'operation', 'integrate').value() == True:
            data_chan_averaged = np.sum(data_chan_reshaped, axis=1)
            data_norm_averaged = np.sum(data_norm_reshaped, axis=1)
            label = 'Integrated'

        data_chan_averaged = np.divide(data_chan_averaged , data_norm_averaged)
        #application of gain and conversion
        data_chan_averaged *= 1/(self.settings.child('lock_in', 'Gain').value()*self.settings.child('lock_in', 'Conversion').value())

        pump_off = data_chan_averaged[::2]
        pump_on = data_chan_averaged[1::2]

        diff_pump_on_off = pump_on - pump_off

        Mean_diff = np.mean(diff_pump_on_off)


        #self.x_axis = Axis('Time', units='µs', data=data_x, index=0)

        #print('data_chan_averaged = ', data_chan_averaged)
        #print('status : ', self.card.status())


        dwa1D1 = DataFromPlugins(name='1. Trace', data=data_tot, dim='Data1D', labels=self.activated_str, do_plot=self.settings.child('lock_in', 'showTrace').value())#, axes=[self.x_axis])
        dwa1D2 = DataFromPlugins(name='2. '+label, data=data_chan_averaged, dim='Data1D', labels=[label+' norm. data', 'Pulse Nbr'], do_plot=True)
        dwa1D3 = DataFromPlugins(name='3. Difference', data=diff_pump_on_off, dim='Data1D',
                                 labels=['Pump on - Pump off', 'Pulses pair Nbr'], do_plot=True)

        dwa0D = DataFromPlugins(name='4. Time-averaged difference', data=Mean_diff, dim='Data0D',
                                 labels=['Pump-probe signal'], units='rad')




        data = DataToExport('SPLockIn', data=[ dwa0D, dwa1D3, dwa1D2, dwa1D1 ])




        self.dte_signal.emit(data)

        ##asynchrone version (non-blocking function with callback)
        # self.controller.your_method_to_start_a_grab_snap(self.callback)
        #########################################################

    def callback(self):
        """optional asynchrone method called when the detector has finished its acquisition of data"""
        data_tot = self.controller.your_method_to_get_data_from_buffer()
        self.dte_signal.emit(DataToExport('myplugin',
                                          data=[DataFromPlugins(name='Mock1', data=data_tot,
                                                                dim='Data1D', labels=['dat0', 'data1'])]))

    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        ## TODO for your custom plugin
        raise NotImplemented  # when writing your own plugin remove this line
        self.controller.your_method_to_stop_acquisition()  # when writing your own plugin replace this line
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))
        ##############################
        return ''