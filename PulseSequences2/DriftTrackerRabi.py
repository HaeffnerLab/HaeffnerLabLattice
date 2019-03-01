import numpy as np
from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
import time
from common.client_config import client_info as cl

detuning_1_global = U(0,'kHz')

class TrackLine1(pulse_sequence):

	scannable_params = {'DriftTrackerRabi.points' : [(-1, 1.0001, 2, ''), 'current']}

	def sequence(self):

		from StatePreparation import StatePreparation
		from subsequences.RabiExcitation import RabiExcitation
		from subsequences.StateReadout import StateReadout
		from subsequences.TurnOffAll import TurnOffAll

		self.end = U(10., 'us')
		p = self.parameters
		line1 = p.DriftTracker.line_selection_1
		channel_729= p.CalibrationScans.calibration_channel_729
		freq_729 = self.calc_freq(line1)
		
		detuning = 2.39122444/p.DriftTrackerRabi.line_1_pi_time * p.DriftTrackerRabi.points
		freq_729 += detuning

		amp = p.DriftTrackerRabi.line_1_amplitude
		duration = p.DriftTrackerRabi.line_1_pi_time

		self.addSequence(TurnOffAll)
		self.addSequence(StatePreparation)
		self.addSequence(RabiExcitation,{'Excitation_729.channel_729': channel_729,
										 'Excitation_729.rabi_excitation_frequency': freq_729,
										 'Excitation_729.rabi_excitation_amplitude': amp,
										 'Excitation_729.rabi_excitation_duration':  duration
										 })
		self.addSequence(StateReadout)

	@classmethod
	def run_initial(cls,cxn, parameters_dict):
		print "Switching the 866DP to auto mode"
		cxn.pulser.switch_auto('866DP')

	@classmethod
	def run_finally(cls, cxn, parameters_dict, all_data, det):    
		print "switching the 866 back to ON"
		cxn.pulser.switch_manual('866DP', True)

		ident = int(cxn.scriptscanner.get_running()[-1][0])
		print " sequence ident" , ident

		all_data = np.array(all_data)
		try:
			all_data = all_data.sum(1)
		except ValueError:
			return

		p = parameters_dict
		duration = p.DriftTrackerRabi.line_1_pi_time
		freq = np.pi/duration

		ind1 = np.where(det == -1)
		ind2 = np.where(det == 1)

		det1 = det[ind1][0] * 2.39122444/p.DriftTrackerRabi.line_1_pi_time
		det2 = det[ind2][0] * 2.39122444/p.DriftTrackerRabi.line_1_pi_time

		p1 = all_data[ind1][0]
		p2 = all_data[ind2][0]

		print "at ",det1, " the pop is", p1
		print "at ",det2, " the pop is", p2

		from sympy import sin, symbols, nsolve
		x = symbol('x')

		relative_det_1 = nsolve(freq**2 / (freq**2 + (x + det1)**2) * (sin((freq**2 + (x - det1)**2)**0.5 * duration / 2))**2 - p1, 0)
		relative_det_2 = nsolve(freq**2 / (freq**2 + (x + det2)**2) * (sin((freq**2 + (x - det2)**2)**0.5 * duration / 2))**2 - p2, 0)

		global detuning_1_global
		detuning_1_global = U((relative_det_1 + relative_det_2)/2, 'kHz')

		print "detuning 1", (relative_det_1 + relative_det_2)/2


class TrackLine2(pulse_sequence):

	scannable_params = {'DriftTrackerRabi.points' : [(-1, 1.0001, 2, ''), 'current']}

	def sequence(self):

		from StatePreparation import StatePreparation
		from subsequences.RabiExcitation import RabiExcitation
		from subsequences.StateReadout import StateReadout
		from subsequences.TurnOffAll import TurnOffAll

		self.end = U(10., 'us')
		p = self.parameters
		line2 = p.DriftTracker.line_selection_2
		channel_729= p.CalibrationScans.calibration_channel_729
		freq_729 = self.calc_freq(line2)
		
		detuning = 2.39122444/p.DriftTrackerRabi.line_1_pi_time * p.DriftTrackerRabi.points
		freq_729 += detuning

		amp = p.DriftTrackerRabi.line_2_amplitude
		duration = p.DriftTrackerRabi.line_2_pi_time

		self.addSequence(TurnOffAll)
		self.addSequence(StatePreparation)
		self.addSequence(RabiExcitation,{'Excitation_729.channel_729': channel_729,
										 'Excitation_729.rabi_excitation_frequency': freq_729,
										 'Excitation_729.rabi_excitation_amplitude': amp,
										 'Excitation_729.rabi_excitation_duration':  duration
										})
		self.addSequence(StateReadout)

	@classmethod
	def run_initial(cls,cxn, parameters_dict):
		print "Switching the 866DP to auto mode"
		cxn.pulser.switch_auto('866DP')

	@classmethod
	def run_finally(cls, cxn, parameters_dict, all_data, det):    
		print "switching the 866 back to ON"
		cxn.pulser.switch_manual('866DP', True)

		ident = int(cxn.scriptscanner.get_running()[-1][0])
		print " sequence ident" , ident

		all_data = np.array(all_data)
		try:
			all_data = all_data.sum(1)
		except ValueError:
			return

		p = parameters_dict
		duration = p.DriftTrackerRabi.line_2_pi_time
		freq = np.pi/duration

		ind1 = np.where(det == -1)
		ind2 = np.where(det == 1)

		det1 = det[ind1][0] * 2.39122444/p.DriftTrackerRabi.line_1_pi_time
		det2 = det[ind2][0] * 2.39122444/p.DriftTrackerRabi.line_1_pi_time

		p1 = all_data[ind1][0]
		p2 = all_data[ind2][0]

		print "at ",det1, " the pop is", p1
		print "at ",det2, " the pop is", p2

		from sympy import sin, symbols, nsolve
		x = symbol('x')

		relative_det_1 = nsolve(freq**2 / (freq**2 + (x + det1)**2) * (sin((freq**2 + (x - det1)**2)**0.5 * duration / 2))**2 - p1, 0)
		relative_det_2 = nsolve(freq**2 / (freq**2 + (x + det2)**2) * (sin((freq**2 + (x - det2)**2)**0.5 * duration / 2))**2 - p2, 0)

		detuning_2 = U((relative_det_1 + relative_det_2)/2, 'kHz')

		print "detuning 2", (relative_det_1 + relative_det_2)/2

		line_1 = p.DriftTracker.line_selection_1
		line_2 = p.DriftTracker.line_selection_2

		carr_1 = detuning_1_global+p.Carriers[carrier_translation[line_1]]
		carr_2 = detuning_2+p.Carriers[carrier_translation[line_2]]

		submission = [(line_1, carr_1), (line_2, carr_2)]
		print  "3243", submission

		print carr_1
		print carr_2

		if p.DriftTrackerRabi.submit:
			cxn.sd_tracker.set_measurements(submission)
			import labrad
			global_sd_cxn = labrad.connect(cl.global_address , password = cl.global_password, tls_mode='off')
			print cl.client_name , "is sub lines to global SD"
			print submission 
			global_sd_cxn.sd_tracker_global.set_measurements(submission, cl.client_name) 
			global_sd_cxn.disconnect()

class DriftTrackerRabi(pulse_sequence):
	is_composite = True

	fixed_params = {'StatePreparation.aux_optical_pumping_enable': False,
					# 'StatePreparation.sideband_cooling_enable': False,
					# 'StateReadout.readout_mode':'pmt',
					# 'Excitation_729.channel_729': "729local",
					}

	sequence = [TrackLine1, TrackLine2]

	show_params= ['CalibrationScans.calibration_channel_729',
				  'DriftTrackerRabi.line_1_amplitude',
				  'DriftTrackerRabi.line_1_pi_time',
				  'DriftTrackerRabi.line_2_amplitude',
				  'DriftTrackerRabi.line_2_pi_time',
				  'DriftTracker.line_selection_1',
				  'DriftTracker.line_selection_2',
				  'DriftTrackerRabi.submit',
				  ]