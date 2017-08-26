from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict

#class RabiFloppingMulti(pulse_sequence):
#    is_multi = True
#    sequences = [RabiFlopping, Spectrum]

class RabiFlopping(pulse_sequence):
    scannable_params = {
        'RabiFlopping.duration':  [(0., 50., 3, 'us'), 'rabi']
        #'Excitation_729.rabi_excitation_duration' : [(-150, 150, 10, 'kHz'),'spectrum'],
              }

    show_params= ['Excitation_729.channel_729',
                  'Excitation_729.bichro',
                  'RabiFlopping.line_selection',
                  'RabiFlopping.rabi_amplitude_729',
                  'RabiFlopping.duration',
                  'RabiFlopping.sideband_selection',
                  'RabiFlopping.sideband_order'
                  ]
    
    #fixed_params = {'StateReadout.ReadoutMode':'camera'}



    def sequence(self):
        from StatePreparation import StatePreparation
        from subsequences.RabiExcitation import RabiExcitation
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll
        
        ## calculate the scan params
        rf = self.parameters.RabiFlopping 
        
        freq_729=self.calc_freq(rf.line_selection)
        print "Rabi flopping 729 freq is {}".format(freq_729)
        print "Rabi flopping duration is {}".format(rf.duration)
        # building the sequence
        self.end = U(10., 'us')
        #self.addSequence(TurnOffAll)
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)
        #self.addSequence(RabiExcitation)     
        self.addSequence(RabiExcitation,{'Excitation_729.rabi_excitation_frequency': freq_729,
                                         'Excitation_729.rabi_excitation_amplitude': rf.rabi_amplitude_729,
                                         'Excitation_729.rabi_excitation_duration':  rf.duration })
        self.addSequence(StateReadout)
        
    #@classmethod
    #def run_initial(cls):
    #    print "Running initial _Rabi_floping"
    #@classmethod
    #def run_in_loop(cls):
    #    print "Running in loop Rabi_floping"
        #pass
    #@classmethod
    #def run_finally(cls):
    #    print "Running finally Rabi_floping"
        #pass
        
