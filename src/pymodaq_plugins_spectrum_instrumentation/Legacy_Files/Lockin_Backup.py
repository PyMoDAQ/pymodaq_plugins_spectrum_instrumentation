# self.LI_pulseFreq = self.settings.child('lock_in', 'LI_PulseFreq').value()*2 *1e-3   # kHz
# self.num_pulses = self.settings.child('timing', 'Num_Pulses').value()
# self.num_LI_period = int( self.settings.child('timing', 'Range').value() * self.LI_pulseFreq)          # LI = Lock In, LI_Period = Up or Down
# self.points_per_pulse = self.settings.child('timing', 'Sample_per_Pulse').value() # Points per pulse
# self.pulse_per_LI_Period = self.num_pulses/self.num_LI_period # Pulses per Period



# def lock_in_backup(self, diff_data, sum_data):
#     """
#     From 2 traces, calculate all relevant values
#     """

#     # --- Reshape to correct size (TODO: way of avoiding ? Or just expected that num sample != actual num samples )
#     diff_data = diff_data[: int(self.num_pulses*self.points_per_pulse) ]
#     sum_data = sum_data[: int(self.num_pulses*self.points_per_pulse) ]

#     # --- Integrate Pulses and remove Background
#     diff_chan_reshaped = diff_data.reshape(self.num_pulses, self.points_per_pulse)
#     sum_chan_reshaped = sum_data.reshape(self.num_pulses, self.points_per_pulse)

#     if self.settings.child('lock_in', 'BG_sub').value() == True:
#         cutoff = int(self.points_per_pulse * self.settings.child("lock_in", "BG_prop").value()/100)
#         diff_data_int = np.sum( diff_chan_reshaped[:,:cutoff], axis=1 ) * (1-self.settings.child('lock_in', 'BG_sub').value()/100) - np.sum(diff_chan_reshaped[:,cutoff:], axis=1) * self.settings.child('lock_in', 'BG_sub').value()/100
#         sum_data_int = np.sum( sum_chan_reshaped[:,:cutoff], axis=1 ) * (1-self.settings.child('lock_in', 'BG_sub').value()/100) - np.sum(sum_chan_reshaped[:,cutoff:], axis=1) * self.settings.child('lock_in', 'BG_sub').value()/100
#     else:
#         diff_data_int = np.sum(diff_chan_reshaped, axis=1)
#         sum_data_int = np.sum(sum_chan_reshaped, axis=1)

#     # - Compute I_a and D_a
#     D_a = np.mean(diff_data_int)
#     I_a = np.mean(sum_data_int)


#     # --- Reshape into a correct number of pulse that works with LockIn



#     # - Compute I_Ba and I_Bd
#     sum_data_int_reshaped = sum_data_int.reshape(self.num_LI_period, self.pulse_per_LI_Period)
#     mean_sum_over_B_pulse = np.mean(sum_data_int_reshaped, axis=1)           # TODO : Don't really get what is happening here
#     # Reduce if you cannot divide by 2
#     if len(mean_sum_over_B_pulse)%2 !=0 : mean_sum_over_B_pulse = mean_sum_over_B_pulse[:-1]
#     I_Bd =   mean_sum_over_B_pulse [::2] - mean_sum_over_B_pulse [1::2]
#     I_Bd = np.mean(I_Bd)
#     I_Ba = np.mean(mean_sum_over_B_pulse)


#     # - Compute D_Ba and D_Bd
#     diff_data_int_reshaped = diff_data_int.reshape(self.num_LI_period, self.pulse_per_LI_Period)
#     mean_diff_over_B_pulse = np.mean(diff_data_int_reshaped, axis=1)
#     # Reduce if you cannot divide by 2
#     if len(mean_diff_over_B_pulse)%2 !=0 : mean_diff_over_B_pulse = mean_diff_over_B_pulse[:-1]
#     D_Bd =   mean_diff_over_B_pulse [::2] - mean_diff_over_B_pulse [1::2]
#     D_Bd = np.mean(D_Bd)
#     D_Ba = np.mean(mean_diff_over_B_pulse)


#     # - Compute ND_Ba and ND_Bd
#     ND_int = np.divide(diff_data_int, sum_data_int) / self.settings.child('lock_in', 'Gain').value() / 2
#     ND_a = np.mean(ND_int)

#     ND_reshaped = ND_int.reshape(self.num_LI_period, self.pulse_per_LI_Period)
#     mean_ND_over_B_pulse = np.mean(ND_reshaped, axis=1)
#     # Reduce if you cannot divide by 2
#     if len(mean_ND_over_B_pulse)%2 !=0 : mean_ND_over_B_pulse = mean_ND_over_B_pulse[:-1]
#     ND_Bd = mean_ND_over_B_pulse[::2] - mean_ND_over_B_pulse[1::2]
#     ND_Bd = np.mean(ND_Bd)
#     ND_Ba = np.mean(mean_ND_over_B_pulse)

#     # - Computing phi_Ba and phi_Bd
#     phi_a = ND_a / self.settings.child('lock_in', 'Conversion').value()
#     phi_Ba = ND_Ba / self.settings.child('lock_in', 'Conversion').value()
#     phi_Bd = ND_Bd / self.settings.child('lock_in', 'Conversion').value()

#     return sum_data_int, I_a, I_Ba, I_Bd, diff_data_int, D_a, D_Ba, D_Bd, ND_a, ND_Ba, ND_Bd, phi_a, phi_Ba, phi_Bd
