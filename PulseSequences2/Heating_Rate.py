import numpy as np
from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
from Spectrum import Spectrum

class rsb(Spectrum):

	@classmethod
	def run_finally(cls, cxn, parameter_dict, data, data_x):
		print "switching the 866 back to ON"
		cxn.pulser.switch_manual('866DP', True)
		data = data.sum(1)
		# peak_guess =  cls.peak_guess(data_x, data)[0]
		# print "@@@@@@@@@@@@@@", peak_guess
		print data_x
		print data
		fit_params = cls.gaussian_fit(data_x, data, return_all_params = True)
		print "red sideband"
		print "############## fit params: ", fit_params
		print "Amplitude: ", fit_params[1]
		return fit_params[1]

class bsb(Spectrum):

	@classmethod
	def run_finally(cls, cxn, parameter_dict, data, data_x):
		print "switching the 866 back to ON"
		cxn.pulser.switch_manual('866DP', True)
		data = data.sum(1)
		# peak_guess =  cls.peak_guess(data_x, data)[0]
		# print "@@@@@@@@@@@@@@", peak_guess
		print data_x
		print data
		fit_params = cls.gaussian_fit(data_x, data, return_all_params = True)
		print "blue sideband"
		print "############## fit params: ", fit_params
		print "Amplitude: ", fit_params[1]
		return fit_params[1]

class nbar(pulse_sequence):

	sequence = [(rsb, {'Spectrum.order':-1.0}), (bsb, {'Spectrum.order': 1.0})]

	@classmethod
	def run_finally(cls, cxn, parameter_dict, amp, seq_name):
		try:
			R = 1.0 * amp[0] / amp[1]
			return 1.0*R/(1.0-1.0*R)
		except:
			pass

class Heating_Rate(pulse_sequence):

	scannable_params = {'Heating.background_heating_time': [(0., 5000., 500., 'us'), 'HeatingRate']}

	sequence = nbar