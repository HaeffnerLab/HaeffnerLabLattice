from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
import num as np

#class RabiFloppingMulti(pulse_sequence):
#    is_multi = True
#    sequences = [RabiFlopping, Spectrum]

def pi_time_guess(t,p,threshold=0.9):
    # looking for the first 0.8 probability
    temp=p/p.max()
    first_peak=np.where(temp>threshold)[0][0]
    pi_time=t[first_peak]
    print "pi time", pi_time
    f= 1.0/(2*pi_time)/2
    
    return p.max(), f

class SetupGlobalRotation(pulse_sequence):
    scannable_params = {
        'RabiFlopping.duration':  [(0., 50., 3, 'us'), 'rabi']
        #'Excitation_729.rabi_excitation_duration' : [(-150, 150, 10, 'kHz'),'spectrum'],
              }

    show_params= [
                  'GlobalRotation.pi_time',
                  'RabiFlopping.line_selection',
                  'RabiFlopping.rabi_amplitude_729',
                  'RabiFlopping.duration',
                  'RabiFlopping.rabi_amplitude_729',
                  'RabiFlopping.duration',
                  'RabiFlopping.line_selection',
                  'RabiFlopping.selection_sideband',
                  'RabiFlopping.order',

                  ]
    
    #fixed_params = {'StateReadout.ReadoutMode':'camera'}



    def sequence(self):
        from StatePreparation import StatePreparation
        from subsequences.RabiExcitation import RabiExcitation
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll
        
        ## calculate the scan params
        rf = self.parameters.RabiFlopping 
        
        #freq_729=self.calc_freq(rf.line_selection)
        freq_729=self.calc_freq(rf.line_selection , rf.selection_sideband , rf.order)
        channel_729 = '729_global'#self.parameters.Excitation_729.channel_729
        
        print "Rabi flopping 729 freq is {}".format(freq_729)
        print "Rabi flopping duration is {}".format(rf.duration)
        # building the sequence
        self.end = U(10., 'us')
        #self.addSequence(TurnOffAll)
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)
        #self.addSequence(RabiExcitation)     
        self.addSequence(RabiExcitation,{'Excitation_729.channel_729':channel_729,
                                         'Excitation_729.rabi_excitation_frequency': freq_729,
                                         'Excitation_729.rabi_excitation_amplitude': rf.rabi_amplitude_729,
                                         'Excitation_729.rabi_excitation_duration':  rf.duration })
        self.addSequence(StateReadout)
        
   
    
    @classmethod
    def run_finally(cls, cxn, parameters_dict, all_data, t):
        from scipy.optimize import curve_fit
        
        # for the multiple case we summ the probabilities, this also
        # reduces the dimension to 1 for single ion case 
        try:
            all_data = all_data.sum(1)
        except ValueError:
            return
        
        #print "139490834", freq_data, all_data
        
        model = lambda  x, a, f: a * np.sin(( 2*np.pi*f*x ))**2
        
        po=pi_time_guess(t,all_data)
        print po
        popt, copt = curve_fit(model, t, all_data, p0)
        print "best fit params" , popt
        print "pi time is: ", 1.0/f/4
        
        # add the setting of the value for the pi time
        
        
   # @classmethod
   # def run_initial(cls,cxn, parameters_dict):
   #     print "Running initial _Rabi_floping"
   # @classmethod
   # def run_in_loop(cls):
   #     print "Running in loop Rabi_floping"
        #pass
   # @classmethod
   # def run_finally(cls):
   #     print "Running finally Rabi_floping"
        #pass
        
