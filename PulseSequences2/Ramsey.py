from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
import numpy as np

class Ramsey(pulse_sequence):
    
    #name = 'Ramsey'

    scannable_params = {
                        
        'RamseyScanGap.ramsey_duration': [(0, 1.0, 0.5, 'ms') ,'ramsey'],
        'Ramsey.second_pulse_phase': [(0, 360., 15, 'deg') ,'ramsey']
        }

    show_params= ['RamseyScanGap.ramsey_duration',
                  'RamseyScanPhase.scanphase',
                  'RamseyScanGap.detuning',
                  
                  #need to work on this
                  'GlobalRotation.amplitude',
                  'GlobalRotation.pi_time',
                  
                  'RabiFlopping.line_selection',
                  'RabiFlopping.selection_sideband',
                  'RabiFlopping.order',
                                                      
                  'StatePreparation.channel_729',
                  'StatePreparation.optical_pumping_enable',
                  'StatePreparation.sideband_cooling_enable']

    
    def sequence(self):
        
        from StatePreparation import StatePreparation
        from subsequences.GlobalRotation import GlobalRotation
        from subsequences.StateReadout import StateReadout
        from subsequences.EmptySequence import EmptySequence
        from subsequences.StateReadout import StateReadout
        
        
        
        ## calculate the 729 params
        rf = self.parameters.RabiFlopping   
        # calculating the 729 freq form the Rabi flop params
        freq_729=self.calc_freq(rf.line_selection , rf.selection_sideband , rf.order)
        # adding the Ramsey detuning
        freq_729 = freq_729+ self.parameters.RamseyScanGap.detuning
        
        print "1234"
        print " freq 729 " , freq_729
        print " Wait time ", self.parameters.RamseyScanGap.ramsey_duration
        
        # building the sequence
        self.addSequence(StatePreparation)            
        self.addSequence(GlobalRotation, { "GlobalRotation.frequency":freq_729,
                                           "GlobalRotation.angle": U(np.pi/2.0, 'rad'),
                                           "GlobalRotation.phase": U(0, 'deg')})
        
        self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : self.parameters.RamseyScanGap.ramsey_duration})
        
        self.addSequence(GlobalRotation, {"GlobalRotation.frequency":freq_729, 
                                          "GlobalRotation.angle": U(np.pi/2.0, 'rad'), 
                                          "GlobalRotation.phase": self.parameters.Ramsey.second_pulse_phase })
        self.addSequence(StateReadout)
        

#if __name__=='__main__':
#    #pv = TreeDict.fromdict({'DopplerCooling.duration':U(5, 'us')})
    #ex = Sequence(pv)
    #psw = pulse_sequence_wrapper('example.xml', pv)
#    print 'executing a scan gap'
#    Ramsey.execute_external(('Ramsey.ramsey_time', 0, 10.0, 0.1, 'ms'))
