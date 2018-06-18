from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from subsequences.StateReadout import StateReadout

class tester(pulse_sequence):

	scannable_params = {   'MolmerSorensen.duration': [(0,200.0, 1.0, 'us'),'ms_time']}

	show_params= ['MolmerSorensen.duration']
         
	def sequence(self):


		ampl_off = U(-63.0, 'dBm')
		frequency = U(200, "MHz")
		start = U(1, "us")
		frequency_advance_duration = U(6, "us")
		slope_duration = U(4, "us")
		duration = U(8, "us")

		self.addDDS('729global', start, frequency_advance_duration, 
					frequency, ampl_off)
		self.addDDS('729global', start + frequency_advance_duration, slope_duration, 
					frequency, U(-5, "dBm"), profile=2)
		self.addDDS('729global', start + frequency_advance_duration + slope_duration, duration, 
		 			frequency, U(-5, "dBm"), profile=4)
		self.addDDS('729global', start + frequency_advance_duration + slope_duration + duration, frequency_advance_duration, 
		 			frequency, ampl_off, profile=0)
		


		self.end = U(100, "us")

		self.addSequence(StateReadout)