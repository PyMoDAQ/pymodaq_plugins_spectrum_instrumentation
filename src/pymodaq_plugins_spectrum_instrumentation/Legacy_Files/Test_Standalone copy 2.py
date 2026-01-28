# import spcm
# manager = spcm.Card('/dev/spcm0')
# enter = type(manager).__enter__
# exit = type(manager).__exit__
# value = enter(manager)
# hit_except = False
# card = value





# def align16(x):
#     return (x // 16) * 16


# # -------------------------
# # 1) FULL RESET
# # -------------------------
# card.stop()   # VERY IMPORTANT
# card.reset()  # optional but strongly recommended


# # -------------------------
# # 2) CARD MODE
# # -------------------------
# card.set_i(spcm.SPC_CARDMODE, spcm.SPC_REC_STD_MULTI)


# # -------------------------
# # 3) BASIC SETTINGS
# # -------------------------
# card.set_i(spcm.SPC_SAMPLERATE, int(1e6))
# card.set_i(spcm.SPC_CHENABLE, spcm.CHANNEL0 | spcm.CHANNEL1)


# # -------------------------
# # 4) SEGMENT GEOMETRY
# # -------------------------
# samples_per_segment = align16(192)
# num_segments = 200

# card.set_i(spcm.SPC_SEGMENTSIZE, samples_per_segment)
# card.set_i(spcm.SPC_MEMSIZE, samples_per_segment * num_segments)


# # -------------------------
# # 5) MULTI OBJECT + DMA
# # -------------------------
# multi = spcm.Multi(card)
# multi.allocate_buffer(card.get_i(spcm.SPC_MEMSIZE))


# # -------------------------
# # 6) READ BACK (IMPORTANT)
# # -------------------------
# segsize = card.get_i(spcm.SPC_SEGMENTSIZE)


# # -------------------------
# # 7) PRE / POST TRIGGER
# # -------------------------
# pre  = min(align16(4096), segsize - 16)
# post = segsize - pre

# multi.pre_trigger(pre)
# multi.post_trigger(post)


# # -------------------------
# # 8) TRIGGER SOURCE
# # -------------------------
# card.set_i(spcm.SPC_TRIG_ORMASK, spcm.SPC_TMASK_EXT0)
# card.set_i(spcm.SPC_TRIG_EXT0_MODE, spcm.SPC_TM_POS)
# card.set_i(spcm.SPC_TRIG_EXT0_LEVEL0, 2000)


# # -------------------------
# # 9) START (ONE COMMAND)
# # -------------------------
# print("Starting")
# multi.start_buffer_transfer(spcm.M2CMD_DATA_STARTDMA)
# # Arm card + enable trigger
# card.start(
#     spcm.M2CMD_CARD_START,
#     # spcm.M2CMD_CARD_ENABLETRIGGER
#     spcm.M2CMD_CARD_WAITTRIGGER
# )


# print("Will Wait now")
# # Wait for DMA to finish
# card.start(spcm.M2CMD_CARD_WAITTRIGGER)


# data = multi.buffer

# print(data.shape)
# # card.start(
# #     spcm.M2CMD_CARD_START |
# #     spcm.M2CMD_CARD_ENABLETRIGGER |
# #     spcm.M2CMD_DATA_STARTDMA |
# #     spcm.M2CMD_DATA_WAITDMA
# # )
