import numpy as np
from pymodaq.utils.daq_utils import ThreadCommand, getLineInfo
from pymodaq.utils.data import DataFromPlugins, Axis, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter
import os
import sys

import spcm
from spcm import units

from pymodaq_plugins_spectrum_instrumentation.daq_viewer_plugins.plugins_1D.daq_1Dviewer_Spectrum_Test import DAQ_1DViewer_Spectrum_Test
from pymodaq_plugins_spectrum_instrumentation.hardware.SpectrumCard_wrapper_Single import Spectrum_Wrapper_Single


class DAQ_1DViewer_Spectrum_Test_Lockin(DAQ_1DViewer_Spectrum_Test):
    """ Instrument plugin class for a 1D viewer.

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.

        """

    params = DAQ_1DViewer_Spectrum_Test.params + [

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
    ]


    def __init__(self, parent=None, params_state=None):
        super().__init__(parent, params_state)

        # --- Calculate some Lock In Parameters
        self.BpulseFreq = self.settings.child('lock_in', 'BPulseFreq').value()*2 *1e-3   # kHz
        self.num_pulses = self.settings.child('timing', 'NumLPulses').value()
        self.num_LI_period = int( self.settings.child('timing', 'Range').value() * self.BpulseFreq)          # LI = Lock In, LI_Period = Up or Down
        self.points_per_pulse = self.settings.child('timing', 'NumSinPulse').value() # Points per pulse
        self.pulse_per_LI_Period = int(self.num_pulses/self.num_LI_period) # Pulses per Period


        print("--- Lock In Info")
        print(f"Number of Pulses = {self.num_pulses}")
        print(f"Number of LI periods = {self.num_LI_period}") 
        print(f"Points per pulse = {self.points_per_pulse}")
        print(f"Pulse Per LI Period = {self.pulse_per_LI_Period}")


    


    def grab_data(self, Naverage=1, **kwargs):
        """ Start a grab from the detector
        """

        # --- Grab a Trace
        try:  data_tot = self.controller.grab_trace( post_trig_ms = 5 )     #TODO : Make Post trig variable

        except Exception as e:
            print("Capture Failed !")
            print(e)
            self.emit_status(ThreadCommand('Update_Status', ['Card asked while running ']))
            self.hit_except = True

        ii = self.controller.activated_str.index( self.settings.child('lock_in', 'diffChannel').value()['selected'][0] )
        index = len(self.controller.activated_str[:ii])
        diff_data = data_tot[index]

        ii = self.controller.activated_str.index( self.settings.child('lock_in', 'sumChannel').value()['selected'][0] )
        index = len(self.controller.activated_str[:ii])
        sum_data = data_tot[index]

        # --- Lock In Process
        try: sum_data_int, I_a, I_Ba, I_Bd, diff_data_int, D_a, D_Ba, D_Bd, ND_a, ND_Ba, ND_Bd, phi_a, phi_Ba, phi_Bd = self.lock_in(diff_data, sum_data)
        except Exception as e:
            print(" - Problem during lockin Process")
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

            self.emit_status(ThreadCommand('Update_Status', [ 'Problem During the LockIn Process ! ! ']))
            self.hit_except = True
            

        # - Create Pymodaq objects for all

        dwa1D1 = DataFromPlugins(name='Trace', data=data_tot, dim='Data1D', labels=self.controller.activated_str, do_plot=self.settings.child('lock_in', 'PlotSave', 'showTrace').value(), do_save=self.settings.child('lock_in', 'PlotSave', 'showTrace').value())

        dwatrain = DataFromPlugins(name='Pulse train', data=[diff_data_int, sum_data_int], dim='Data1D', labels=['D', 'I'], do_plot=self.settings.child('lock_in', 'PlotSave', 'PulseTrain').value(), do_save=True)

        dwa1D3 = DataFromPlugins(name='Pulse average', data=[np.array([D_a]), np.array([I_a])], dim='Data0D',
                                 labels=['Da', 'Ia'], do_plot=self.settings.child('lock_in', 'PlotSave', 'PulseAverage').value(), do_save=self.settings.child('lock_in', 'PlotSave', 'PulseAverage').value())
        
        dwaIBd = DataFromPlugins(name='I_Bd', data=I_Bd, dim='Data0D',
                                 labels=['I_Bd'], do_plot=self.settings.child('lock_in', 'PlotSave', 'I_Bd').value(), do_save=self.settings.child('lock_in', 'PlotSave', 'I_Bd').value())
        
        dwaIBa    = DataFromPlugins(name='I_Ba', data=I_Ba, dim='Data0D',
                                 labels=['I_Ba'], do_plot=self.settings.child('lock_in', 'PlotSave', 'I_Ba').value(), do_save=self.settings.child('lock_in', 'PlotSave', 'I_Ba').value())
        
        dwaNDa = DataFromPlugins(name='NDa', data=ND_a, dim='Data0D',
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
        data_to_export = [dwa1D1]
        export = {'PulseTrain':dwatrain, 'PulseAverage':dwa1D3, 'I_Bd':dwaIBd, 'I_Ba':dwaIBa, 'NDa':dwaNDa, 'D_Bd':dwaDBd, 'D_Ba':dwaDBa, 'ND_Bd':dwaNDBd, 'ND_Ba':dwaNDBa, 'phi_Bd':dwaphi_Bd, 'phi_Ba':dwaphi_Ba }
        for type_str in export.keys():
            if self.settings.child('lock_in', 'PlotSave', type_str).value():
                data_to_export.append(export[type_str])  # Only plot those we want to save


        # # Old Version
        # data_to_export = [dwatrain, dwa1D3, dwa1D1, dwaIBd, dwaIBa, dwaNDa, dwaDBd,dwaDBa,dwaNDBd, dwaNDBa, dwaphi_Bd, dwaphi_Ba]


        data = DataToExport('SPLockIn', data=data_to_export)
        self.dte_signal.emit(data)



    def lock_in(self, diff_data, sum_data):
        """
        From 2 traces, calculate all relevant values
        """

        
        # --- Reshape to correct size (TODO: way of avoiding ? Or just expected that num sample != actual num samples )
        diff_data = diff_data[: int(self.num_pulses*self.points_per_pulse) ]
        sum_data = sum_data[: int(self.num_pulses*self.points_per_pulse) ]

        # --- Integrate Pulses and remove Background
        diff_chan_reshaped = diff_data.reshape(self.num_pulses, self.points_per_pulse)
        data_norm_reshaped = sum_data.reshape(self.num_pulses, self.points_per_pulse)

        if self.settings.child('lock_in', 'BG_sub').value() == True:    # TODO : Make background subtraction more smart (especially if trigger not stable, maybe get more background)
            diff_data_int = -np.sum(diff_chan_reshaped[:,:self.points_per_pulse//8], axis=1) + np.sum(diff_chan_reshaped[:,self.points_per_pulse//8:], axis=1)/7
            sum_data_int = -np.sum(data_norm_reshaped[:,:self.points_per_pulse//8], axis=1) + np.sum(data_norm_reshaped[:,self.points_per_pulse//8:], axis=1)/7
        else:
            diff_data_int = np.sum(diff_chan_reshaped, axis=1)
            sum_data_int = np.sum(data_norm_reshaped, axis=1)

        # - Compute I_a and D_a

        D_a = np.mean(diff_data_int)
        I_a = np.mean(sum_data_int)


        # - Compute I_Ba and I_Bd
        sum_data_int_reshaped = sum_data_int.reshape(self.num_LI_period, self.pulse_per_LI_Period)
        mean_sum_over_B_pulse = np.mean(sum_data_int_reshaped, axis=1)           # TODO : Don't really get what is happening here
        # Reduce if you cannot divide by 2
        if len(mean_sum_over_B_pulse)%2 !=0 : mean_sum_over_B_pulse = mean_sum_over_B_pulse[:-1]
        I_Bd =   mean_sum_over_B_pulse [::2] - mean_sum_over_B_pulse [1::2]
        I_Bd = np.mean(I_Bd)
        I_Ba = np.mean(mean_sum_over_B_pulse)


        # - Compute D_Ba and D_Bd
        diff_data_int_reshaped = diff_data_int.reshape(self.num_LI_period, self.pulse_per_LI_Period)
        mean_diff_over_B_pulse = np.mean(diff_data_int_reshaped, axis=1)
        # Reduce if you cannot divide by 2
        if len(mean_diff_over_B_pulse)%2 !=0 : mean_diff_over_B_pulse = mean_diff_over_B_pulse[:-1]
        D_Bd =   mean_diff_over_B_pulse [::2] - mean_diff_over_B_pulse [1::2]
        D_Bd = np.mean(D_Bd)
        D_Ba = np.mean(mean_diff_over_B_pulse)


        # - Compute ND_Ba and ND_Bd
        ND_int = np.divide(diff_data_int, sum_data_int) / self.settings.child('lock_in', 'Gain').value() / 2
        ND_a = np.mean(ND_int)

        ND_reshaped = ND_int.reshape(self.num_LI_period, self.pulse_per_LI_Period)
        mean_ND_over_B_pulse = np.mean(ND_reshaped, axis=1)
        # Reduce if you cannot divide by 2
        if len(mean_ND_over_B_pulse)%2 !=0 : mean_ND_over_B_pulse = mean_ND_over_B_pulse[:-1]
        ND_Bd = mean_ND_over_B_pulse[::2] - mean_ND_over_B_pulse[1::2]
        ND_Bd = np.mean(ND_Bd)
        ND_Ba = np.mean(mean_ND_over_B_pulse)

        # - Computing phi_Ba and phi_Bd
        phi_a = ND_a / self.settings.child('lock_in', 'Conversion').value()
        phi_Ba = ND_Ba / self.settings.child('lock_in', 'Conversion').value()
        phi_Bd = ND_Bd / self.settings.child('lock_in', 'Conversion').value()

        return sum_data_int, I_a, I_Ba, I_Bd, diff_data_int, D_a, D_Ba, D_Bd, ND_a, ND_Ba, ND_Bd, phi_a, phi_Ba, phi_Bd






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
        detector = 'Spectrum_Test_Lockin'
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