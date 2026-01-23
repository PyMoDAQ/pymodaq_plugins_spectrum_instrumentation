# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 11:46:01 2024

@author: dqml-lab
"""

import spcm
from spcm import units  # spcm uses the pint library for unit handling (units is a UnitRegistry object)
import sys



class Digitizer_Wrapper:

    ############## PMD mandatory methods

    def initialise_device(self, duration : int, sample_rate : float, clock_mode : str = "internal PLL", clock_frequency : float = 80, channels_to_activate : list[bool] = [0,0,0,1,0,1,0,0]) -> bool:
        """
        Initializes the spectrum device in Single Mode
        Input : 
            - Duration : int [ms]
            - sample_rate : float [MHz]
            - clock_mode : str ["internal PLL", "external reference"]
            - clock_frequency : float [MHz]
        """

        
        # Determine Some Properties

        Num_Samples = duration * sample_rate # Total Number of Samples
        print("--- Initializing SPCM Card ---")
        print("Duration = ", duration, "s")
        print("Number of Samples = ", Num_Samples)
        print("Sampling Frequency = ", sample_rate, "MHz")

        manager = spcm.Card('/dev/spcm0')
        enter = type(manager).__enter__
        exit = type(manager).__exit__
        value = enter(manager)
        hit_except = False


        try:
            card = value

            # - Choose Mode
            card.card_mode(spcm.SPC_REC_STD_SINGLE)  # single trigger standard mode
            card.timeout(50 * units.s)  # timeout 50 s

            # - Setup External Clock
            clock = spcm.Clock(card)
            if clock_mode == "internal PLL":
                clock.mode(spcm.SPC_CM_INTPLL)  # clock mode internal PLL
            
            if clock_mode == "external reference":
                clock.mode(spcm.SPC_CM_EXTREFCLOCK)  # external reference clock
                clock.reference_clock(clock_frequency * units.MHz)

            # - DO THIS IN DAQ VIEWER
            # # - Check if Given Parameters Work    
            # if int(Num_B_Pulse) != Num_B_Pulse : print("Duration is not an integer amount of Lock-In Pulses !"); exit()
            # if Num_B_Pulse%2 != 0 : print("Not an even amount ou Lock-In Pulses ! Will not be able to calculate Bd"); exit()

            clock.sample_rate(sample_rate * units.MHz, return_unit=units.MHz)

            # Activate Channels
            activated_channels = []

            for ii in range(8):
                if channels_to_activate[ii] == True:
                    activated_str.append('CH'+str(ii))
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




            # Can only activate certain number of channels ...
            if len(activated_channels) == 1:
                channels = spcm.Channels(card, card_enable=activated_channels[0])
            if len(activated_channels) == 2:
                channels = spcm.Channels(card, card_enable=activated_channels[0] | activated_channels[1])
            if len(activated_channels) == 3:
                channels = spcm.Channels(card, card_enable=activated_channels[0] | activated_channels[1] | activated_channels[2] | spcm.CHANNEL7)
            if len(activated_channels) == 4:
                channels = spcm.Channels(card, card_enable=activated_channels[0] | activated_channels[1] | activated_channels[2] | activated_channels[3])
            if len(activated_channels) == 5:
                channels = spcm.Channels(card, card_enable=spcm.CHANNEL0 | spcm.CHANNEL1 | spcm.CHANNEL2 | spcm.CHANNEL3 | spcm.CHANNEL4 | spcm.CHANNEL5 | spcm.CHANNEL6 | spcm.CHANNEL7)




            # Set Amplitude and Offset
            channels.amp(Amp * units.mV)
            channels[0].offset(Offset * units.mV, return_unit=units.mV)
            channels.termination(0)     # Set termination to 500MOhm ?


            # - Activate Triggering Channel Triggering
            trigger = spcm.Trigger(card)

            if triggerType == ['None']:
                trigger.or_mask(spcm.SPC_TMASK_NONE)  # trigger set to none
                trigger.ch_or_mask0(channels[0].ch_mask())
            if triggerType == ['Software trigger']:
                trigger.or_mask(spcm.SPC_TMASK_SOFTWARE)  # trigger set to software
            if triggerType == ['External analog trigger']:
                trigger.or_mask(spcm.SPC_TMASK_EXT0)  # trigger set to external analog

            if triggerType == ['Channel trigger']:
                trigger.or_mask(spcm.SPC_TMASK_NONE)
                if triggerChannel == ['CH0']:
                    trigger.ch_or_mask0(spcm.SPC_TMASK0_CH0)
                if triggerChannel == ['CH1']:
                    trigger.ch_or_mask0(spcm.SPC_TMASK0_CH1)
                if triggerChannel == ['CH2']:
                    trigger.ch_or_mask0(spcm.SPC_TMASK0_CH2)
                if triggerChannel == ['CH3']:
                    trigger.ch_or_mask0(spcm.SPC_TMASK0_CH3)
                if triggerChannel == ['CH4']:
                    trigger.ch_or_mask0(spcm.SPC_TMASK0_CH4)
                if triggerChannel == ['CH5']:
                    trigger.ch_or_mask0(spcm.SPC_TMASK0_CH5)
                if triggerChannel == ['CH6']:
                    trigger.ch_or_mask0(spcm.SPC_TMASK0_CH6)
                if triggerChannel == ['CH7']:
                    trigger.ch_or_mask0(spcm.SPC_TMASK0_CH7)



            trigger.and_mask(spcm.SPC_TMASK_NONE)  # no AND mask

            if triggerType == ['Channel trigger']:
                if triggerMode == ['Rising edge']:
                    trigger.ch_mode(channels[0], spcm.SPC_TM_POS)
                if triggerMode == ['Falling edge']:
                    trigger.ch_mode(channels[0], spcm.SPC_TM_NEG)
                if triggerMode == ['Both']:
                    trigger.ch_mode(channels[0], spcm.SPC_TM_BOTH)

                trigger.ch_level0(channels[0], trigLevel * units.mV, return_unit=units.mV)

            if triggerType == ['External analog trigger']:
                if triggerMode == ['Rising edge']:
                    trigger.ext0_mode(spcm.SPC_TM_POS)
                if triggerMode == ['Falling edge']:
                    trigger.ext0_mode(spcm.SPC_TM_NEG)
                if triggerMode == ['Both']:
                    trigger.ext0_mode(spcm.SPC_TM_BOTH)
                trigger.ext0_level0(trigLevel * units.mV, return_unit=units.mV)


        except Exception as e:
            hit_except = True
            print("EXIT WITH ERROR : ")
            print(e)



        info = "Initialized"
        initialized = True
        return info, initialized




    def get_the_x_axis(self):

        return self.data_transfer.time_data().magnitude

    def start_a_grab_snap(self, card, channel, Range, postTrigDur):

        # define the data buffer
        self.data_transfer = spcm.DataTransfer(card)
        self.data_transfer.duration(Range * units.us, post_trigger_duration=postTrigDur * units.us)
        # Start DMA transfer
        self.data_transfer.start_buffer_transfer(spcm.M2CMD_DATA_STARTDMA)

        # start card
        card.start(spcm.M2CMD_CARD_ENABLETRIGGER, spcm.M2CMD_DATA_WAITDMA)

        data_V = []
        for chan in channel:
            data_V.append(chan.convert_data(self.data_transfer.buffer[chan.index, :], units.V).magnitude)





        # def get_data_from_buffer():
        '''


        num_samples = 512 * units.KiS
        notify_samples = 128 * units.KiS
        plot_samples = 4 * units.KiS


        data_transfer = spcm.DataTransfer(card)
        data_transfer.allocate_buffer(num_samples)
        data_transfer.pre_trigger(spcm.KIBI(1))
        data_transfer.notify_samples(notify_samples)
        data_transfer.start_buffer_transfer()
        data_transfer.verbose(True)

        # start the card
        card.start(spcm.M2CMD_DATA_STARTDMA | spcm.M2CMD_CARD_ENABLETRIGGER)

        data_V = []

        time_data_s = data_transfer.time_data(total_num_samples=plot_samples)
        for chan in channel:
            data_V.append(time_data_s)

        return data_V
        '''




        return data_V

    def terminate_the_communication(self, manager, hit_except):
        try:
            print('Communication terminated')

        except:
            hit_except = True
            if not exit(manager, *sys.exc_info()):

                raise
        finally:
            if not hit_except:
                exit(manager)
                manager.close()

