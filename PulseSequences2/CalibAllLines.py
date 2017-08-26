from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict


class CalibLine1(pulse_sequence):

	scannable_params = {}


    def guess(self, f, p, force_guess = False):
        '''
        just take the point at the peak value
        '''
        max_index = np.where(p == p.max())[0][0]
        fmax = f[max_index]
        if (p.max() <= 0.2 and not force_guess):
            raise Exception("Peak not found")
        else:
            # center, amplitude, width guesses
            return np.array([ fmax,  p.max(), 6e-3 ])
    
    def fit(self, f, p, return_all_params = False, init_guess = None):
        model = lambda x, c0, a, w: a*np.exp(-(x - c0)**2/w**2)
        force_guess = False
        if return_all_params: force_guess = True
        if init_guess is None:
            guess = self.guess(f, p, force_guess)        
        else:
            guess = init_guess
        popt, copt = curve_fit(model, f, p, p0=guess)
        if return_all_params:
            return popt[0], popt[1], popt[2] # center value, amplitude, width
        else:
            return popt[0] # return only the center value


	def sequence(self):

    	from StatePreparation import StatePreparation
    	from subsequences.RabiExcitation import RabiExcitation
    	from subsequences.StateReadout import StateReadout
    	from subsequences.TurnOffAll import TurnOffAll

    	self.end = U(10., 'us')



class CalibLine2(CalibLine1):

	scannable_params = {}


	def sequence(self):

		from StatePreparation import StatePreparation
        from subsequences.RabiExcitation import RabiExcitation
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll

        self.end = U(10., 'us')


class CalibAllLines(pulse_sequence):
    is_composite = True
    
    sequences = [CalibLine1, CalibLine2]

    show_params= ['DriftTracker.line_selection_1',
    			  'DriftTracker.line_selection_2',
    			  'CalibrationScans.calibration_channel_729',
    			  'Spectrum.car1_sensitivity',
    			  'Spectrum.car2_sensitivity'
                  ]