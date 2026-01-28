# import numpy as np
# import spcm
# from spcm import units

# import matplotlib.pyplot as plt
# import time
# # Settings 



# def align16(x):
#     return (x // 16) * 16


# channels_to_activate = [0,0,1,0,1,0,0,0]
# activated_str = []
# Amp = 5000          # mV
# Offset = 0          # mV

# triggerType = ["External analog trigger"]
# triggerChannel = ["CH0"]
# triggerMode = ["Rising edge"]
# trigLevel = 100     # mV

# Num_Pulses = 200
# # Num_Sample_per_Pulse = 200
# Num_Sample_per_Pulse = align16(200)

# clockMode = ["external reference"]
# ExtClock = 80

# PulseFreq = 1       # kHz
# BPulseFreq = 500    # Hz







# # ---------------------------------------
# # ---- Initialize
# # ---------------------------------------

# # Setup
# # sampleRate = Num_Pulses * 1e-3              # ?
# # NumSamples = Num_Pulses * Num_Sample_per_Pulse       # ?
# # print(NumSamples)
# # Range =  NumSamples / sampleRate        # ?
# # print(Range)



# # Determine Some Properties
# Duration = Num_Pulses / (PulseFreq*1e3)     # Duration of aquisition
# Num_B_Pulse = Duration * BPulseFreq         # Number of Lock-In Periods
# Num_Samples = Num_Pulses * Num_Sample_per_Pulse # Total Number of Samples
# Sampling_Frequency = Num_Samples / Duration * 1e-6     # Sampling Frequency to give the card   (in MHz)
# print("Duration = ", Duration, "s")
# print("Number of B Periods = ", Num_B_Pulse)
# print("Number of Samples = ", Num_Samples)
# print("Sampling Frequency = ", Sampling_Frequency, "MHz")

# manager = spcm.Card('/dev/spcm0')
# enter = type(manager).__enter__
# exit = type(manager).__exit__
# value = enter(manager)
# hit_except = False


# try:
#     card = value

#     # - Choose Mode
#     card.card_mode(spcm.SPC_REC_STD_MULTI)  # single trigger standard mode
#     card.timeout(50 * units.s)  # timeout 50 s

#     # - Setup External Clock
#     clock = spcm.Clock(card)
#     if clockMode == ["internal PLL"]:
#         clock.mode(spcm.SPC_CM_INTPLL)  # clock mode internal PLL
    
#     if clockMode == ["external reference"]:
#         clock.mode(spcm.SPC_CM_EXTREFCLOCK)  # external reference clock
#         clock.reference_clock(ExtClock * units.MHz)

#     # - Check if Given Parameters Work    
#     if int(Num_B_Pulse) != Num_B_Pulse : print("Duration is not an integer amount of Lock-In Pulses !"); exit()
#     if Num_B_Pulse%2 != 0 : print("Not an even amount ou Lock-In Pulses ! Will not be able to calculate Bd"); exit()


#     # NumSamples = int(Num_Pulses *  Num_Sample_per_Pulse/ 1e3)
#     # sampleRate = Num_Sample_per_Pulse * PulseFreq*1e-3
#     # sampleRate = Num
#     Range =  Num_Pulses * 1/PulseFreq
#     clock.sample_rate(Sampling_Frequency * units.MHz, return_unit=units.MHz)



#     # Activate Channels
#     activated_channels = []

#     for ii in range(8):
#         if channels_to_activate[ii] == True:
#             activated_str.append('CH'+str(ii))
#             if ii == 0:
#                 activated_channels.append(spcm.CHANNEL0)
#             if ii == 1:
#                 activated_channels.append(spcm.CHANNEL1)
#             if ii == 2:
#                 activated_channels.append(spcm.CHANNEL2)
#             if ii == 3:
#                 activated_channels.append(spcm.CHANNEL3)
#             if ii == 4:
#                 activated_channels.append(spcm.CHANNEL4)
#             if ii == 5:
#                 activated_channels.append(spcm.CHANNEL5)
#             if ii == 6:
#                 activated_channels.append(spcm.CHANNEL6)
#             if ii == 7:
#                 activated_channels.append(spcm.CHANNEL7)

#     # Can only activate certain number of channels ...
#     if len(activated_channels) == 1:
#         channels = spcm.Channels(card, card_enable=activated_channels[0])
#     if len(activated_channels) == 2:
#         channels = spcm.Channels(card, card_enable=activated_channels[0] | activated_channels[1])
#     if len(activated_channels) == 3:
#         channels = spcm.Channels(card, card_enable=activated_channels[0] | activated_channels[1] | activated_channels[2] | spcm.CHANNEL7)
#     if len(activated_channels) == 4:
#         channels = spcm.Channels(card, card_enable=activated_channels[0] | activated_channels[1] | activated_channels[2] | activated_channels[3])
#     if len(activated_channels) == 5:
#         channels = spcm.Channels(card, card_enable=spcm.CHANNEL0 | spcm.CHANNEL1 | spcm.CHANNEL2 | spcm.CHANNEL3 | spcm.CHANNEL4 | spcm.CHANNEL5 | spcm.CHANNEL6 | spcm.CHANNEL7)




#     # Set Amplitude and Offset
#     channels.amp(Amp * units.mV)
#     channels[0].offset(Offset * units.mV, return_unit=units.mV)
#     channels.termination(0)     # Set termination to 500MOhm ?


#     # - Activate Triggering Channel Triggering
#     trigger = spcm.Trigger(card)

#     if triggerType == ['None']:
#         trigger.or_mask(spcm.SPC_TMASK_NONE)  # trigger set to none
#         trigger.ch_or_mask0(channels[0].ch_mask())
#     if triggerType == ['Software trigger']:
#         trigger.or_mask(spcm.SPC_TMASK_SOFTWARE)  # trigger set to software
#     if triggerType == ['External analog trigger']:
#         trigger.or_mask(spcm.SPC_TMASK_EXT0)  # trigger set to external analog

#     if triggerType == ['Channel trigger']:
#         trigger.or_mask(spcm.SPC_TMASK_NONE)
#         if triggerChannel == ['CH0']:
#             trigger.ch_or_mask0(spcm.SPC_TMASK0_CH0)
#         if triggerChannel == ['CH1']:
#             trigger.ch_or_mask0(spcm.SPC_TMASK0_CH1)
#         if triggerChannel == ['CH2']:
#             trigger.ch_or_mask0(spcm.SPC_TMASK0_CH2)
#         if triggerChannel == ['CH3']:
#             trigger.ch_or_mask0(spcm.SPC_TMASK0_CH3)
#         if triggerChannel == ['CH4']:
#             trigger.ch_or_mask0(spcm.SPC_TMASK0_CH4)
#         if triggerChannel == ['CH5']:
#             trigger.ch_or_mask0(spcm.SPC_TMASK0_CH5)
#         if triggerChannel == ['CH6']:
#             trigger.ch_or_mask0(spcm.SPC_TMASK0_CH6)
#         if triggerChannel == ['CH7']:
#             trigger.ch_or_mask0(spcm.SPC_TMASK0_CH7)



#     trigger.and_mask(spcm.SPC_TMASK_NONE)  # no AND mask

#     if triggerType == ['Channel trigger']:
#         if triggerMode == ['Rising edge']:
#             trigger.ch_mode(channels[0], spcm.SPC_TM_POS)
#         if triggerMode == ['Falling edge']:
#             trigger.ch_mode(channels[0], spcm.SPC_TM_NEG)
#         if triggerMode == ['Both']:
#             trigger.ch_mode(channels[0], spcm.SPC_TM_BOTH)

#         trigger.ch_level0(channels[0], trigLevel * units.mV, return_unit=units.mV)

#     if triggerType == ['External analog trigger']:
#         if triggerMode == ['Rising edge']:
#             trigger.ext0_mode(spcm.SPC_TM_POS)
#         if triggerMode == ['Falling edge']:
#             trigger.ext0_mode(spcm.SPC_TM_NEG)
#         if triggerMode == ['Both']:
#             trigger.ext0_mode(spcm.SPC_TM_BOTH)
#         trigger.ext0_level0(trigLevel * units.mV, return_unit=units.mV)


# except Exception as e:
#     hit_except = True
#     print("EXIT WITH ERROR : ")
#     print(e)




# card.stop()   # VERY IMPORTANT
# card.reset()  # optional but strongly recommended


# card.set_i(spcm.SPC_SAMPLERATE, int(1e6))
# samples_per_segment = align16(Num_Sample_per_Pulse)
# num_segments        = Num_Pulses

# card.set_i(spcm.SPC_SEGMENTSIZE, samples_per_segment)
# card.set_i(spcm.SPC_MEMSIZE, samples_per_segment * num_segments)

# multi = spcm.Multi(card)
# multi.allocate_buffer(card.get_i(spcm.SPC_MEMSIZE))

# segsize = card.get_i(spcm.SPC_SEGMENTSIZE)
# memsize = card.get_i(spcm.SPC_MEMSIZE)
# num_segments = memsize // segsize

# MAX_PRE = 4096  # safe value on most cards

# pre  = min(align16(4096), segsize - 16)
# post = segsize - pre

# print(pre)

# multi.pre_trigger(pre)
# multi.post_trigger(post)

# card.set_i(spcm.SPC_TRIG_ORMASK, spcm.SPC_TMASK_EXT0)
# card.set_i(spcm.SPC_TRIG_EXT0_MODE, spcm.SPC_TM_POS)
# card.set_i(spcm.SPC_TRIG_EXT0_LEVEL0, 100)  # mV

# # Start acquisition + DMA
# card.start(
#     spcm.M2CMD_CARD_START |
#     spcm.M2CMD_CARD_ENABLETRIGGER |
#     spcm.M2CMD_DATA_STARTDMA
# )

# # Wait until all segments are done
# card.start(spcm.M2CMD_DATA_WAITDMA)


# data = multi.buffer
# print(data.shape)

# # # # # In multi-mode, the aquisition is divided into segments. Here I define the segment size
# # # num_segments = Num_Pulses                                                          # One segment per pulse 
# # # samples_per_segment = Num_Sample_per_Pulse                                          # Each segment has the right amount
# # # total_samples = num_segments * samples_per_segment

# # # print("---")
# # # print("Wanted Num Segments : ", num_segments)
# # # print("Wanted Segment size : ", Num_Sample_per_Pulse)
# # # print("Total Samples : ", total_samples)




# # # multiple_recording = spcm.Multi(card)
# # # tot_samp = multiple_recording.allocate_buffer(total_samples)

# # # card.set_i(spcm.SPC_SEGMENTSIZE, samples_per_segment)
# # # card.set_i(spcm.SPC_MEMSIZE, total_samples)
# # # segments = card.get_i(spcm.SPC_MEMSIZE) // card.get_i(spcm.SPC_SEGMENTSIZE)


# # # print("---")
# # # print("Number of segments:", segments)
# # # print("Set Segment size:", card.get_i(spcm.SPC_SEGMENTSIZE))
# # # print("Set Total mem:", card.get_i(spcm.SPC_MEMSIZE))


# # # card.set_i(spcm.SPC_SAMPLERATE, 200000 )
# # # print("Samplerate:", card.get_i(spcm.SPC_SAMPLERATE))

# # # pre  = align16(20)
# # # post = samples_per_segment - pre


# # # multiple_recording.pre_trigger(pre)
# # # multiple_recording.post_trigger(post)

# # info = "Initialized"
# # initialized = True


# # # ---------------------------------------
# # # ---- Grab Data
# # # ---------------------------------------
# # def grab():

# #     try:

# #         multiple_recording.start_buffer_transfer(spcm.M2CMD_DATA_STARTDMA)

# #         card.start(
# #             spcm.M2CMD_CARD_START |
# #             spcm.M2CMD_CARD_ENABLETRIGGER |
# #             spcm.M2CMD_DATA_WAITDMA
# #         )

# #         data = multiple_recording.buffer
# #         print(data.shape)
# #         # data_V = []

# #         # for segment in range(data.shape[0]):
# #         #     for chan in channels:
# #         #         chan_data = chan.convert_data(data[segment, :, chan], units.V).magnitude # index definition: [segment, sample, channel]
# #         #         data_V.append(chan_data)

# #         # return np.array(data_V)




# #         # # data_tot = controller.start_a_grab_snap(self.card, self.channels, NumSamples, SamplesPerSegment, self.multiple_recording)
# #         # multiple_recording.start_buffer_transfer(spcm.M2CMD_DATA_STARTDMA)
        
# #         # try:
# #         #     card.start(spcm.M2CMD_CARD_ENABLETRIGGER, spcm.M2CMD_DATA_WAITDMA)
# #         #     data = multiple_recording.buffer
# #         #     data_V = []

# #         #     for segment in range(data.shape[0]):
# #         #         for chan in channels:
# #         #             chan_data = chan.convert_data(data[segment, :, chan], units.V).magnitude # index definition: [segment, sample, channel]
# #         #             data_V.append(chan_data)

# #         #     return np.array(data_V)

# #         # except spcm.SpcmTimeout as timeout:
# #         #     print("Timeout...")

# #     except Exception as e:
# #         print(e)
# #         quit()




# # data = grab()
# # print("Data Shape :", data.shape)


# # # print(np.argmax(data[:200]))
# # # plt.plot(data[:200])
# # # plt.show()