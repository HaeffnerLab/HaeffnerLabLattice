from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
import numpy as np

class Parity(pulse_sequence):
    
    #name = 'Ramsey'

    scannable_params = {
                        
        'RamseyScanGap.ramsey_duration': [(0, 2.0, 0.15, 'ms') ,'parity']
     
        }

    show_params= ['RamseyScanGap.ramsey_duration',

                  
                  #need to work on this
                  'GlobalRotation.amplitude',
                  'GlobalRotation.pi_time',
                  
                  'RabiFlopping.line_selection',
                  'RabiFlopping.selection_sideband',
                  'RabiFlopping.order',
                                                      
                  'StatePreparation.channel_729',
                  'StatePreparation.optical_pumping_enable',
                  'StatePreparation.sideband_cooling_enable']
    
    #fixed_params = {'StateReadout.readout_mode':'pmt_parity'}

    
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
        
        
#         print "1234"
#         print " freq 729 " , freq_729
#         print " Wait time ", self.parameters.RamseyScanGap.ramsey_duration
#         
        # building the sequence
        self.addSequence(StatePreparation)            
        self.addSequence(GlobalRotation, { "GlobalRotation.frequency":freq_729,
                                           "GlobalRotation.angle": U(np.pi/2.0, 'rad'),
                                           "GlobalRotation.phase": U(0, 'deg')})
        
        self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : U(2, 'ms')})
        
        self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : self.parameters.RamseyScanGap.ramsey_duration})
        
        self.addSequence(GlobalRotation, {"GlobalRotation.frequency":freq_729, 
                                          "GlobalRotation.angle": U(np.pi/2.0, 'rad'), 
                                          "GlobalRotation.phase": U(0, 'deg') })
        self.addSequence(StateReadout)
        
    @classmethod
    def run_initial(cls,cxn, parameters_dict):
        print "Switching the 866DP to auto mode"
        cxn.pulser.switch_auto('866DP')
        
    @classmethod
    def run_in_loop(cls,cxn, parameters_dict, data, x):
        #print "Running in loop Rabi_floping"
        pass
    
    @classmethod
    def run_finally(cls,cxn, parameters_dict, data, x):
        print "switching the 866 back to ON"
        cxn.pulser.switch_manual('866DP', True)

#if __name__=='__main__':
#    #pv = TreeDict.fromdict({'DopplerCooling.duration':U(5, 'us')})
    #ex = Sequence(pv)
    #psw = pulse_sequence_wrapper('example.xml', pv)
#    print 'executing a scan gap'
#    Ramsey.execute_external(('Ramsey.ramsey_time', 0, 10.0, 0.1, 'ms'))
