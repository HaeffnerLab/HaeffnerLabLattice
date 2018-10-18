from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
import numpy as np

class RamseyGlobalEchoPowerSpectralDensity(pulse_sequence):
    
    #name = 'Ramsey'

    scannable_params = {
        'RamseyScanGap.ramsey_duration': [(0, 1.0, 0.01, 'ms') ,'ramsey'],
        'Ramsey.second_pulse_phase': [(0, 360., 15, 'deg') ,'ramsey'],
        'GlobalRotation.pi_time': [(0, 50., 0.5, 'us') ,'rabi']
        }

    show_params= ['RamseyScanGap.ramsey_duration',
                  'RamseyScanGap.dynamical_decoupling_num_pulses',
                  'RamseyScanGap.dynamical_decoupling_scheme',
                  'Ramsey.second_pulse_phase',
                  
                  'GlobalRotation.amplitude',
                  'GlobalRotation.pi_time',
                  
                  'RabiFlopping.line_selection',
                  'RabiFlopping.selection_sideband',
                  'RabiFlopping.order',
                  'RamseyScanGap.pi_half_scaling_factor',
                  'RamseyScanGap.pi_half'
                                                      
                  ]

    
    def sequence(self):
        
        from StatePreparation import StatePreparation
        from subsequences.GlobalRotation import GlobalRotation
        from subsequences.StateReadout import StateReadout
        from subsequences.EmptySequence import EmptySequence
        
        ## calculate the 729 params
        rf = self.parameters.RabiFlopping   
                # calculating the 729 freq form the Rabi flop params
        freq_729=self.calc_freq(rf.line_selection , rf.selection_sideband , rf.order)
        
        # adding the Ramsey detuning
        freq_729 = freq_729 + self.parameters.RamseyScanGap.detuning

        s = self.parameters.RamseyScanGap.pi_half_scaling_factor
        pi_half = self.parameters.RamseyScanGap.pi_half
        ramsey_duration = self.parameters.RamseyScanGap.ramsey_duration
        dd_scheme = self.parameters.RamseyScanGap.dynamical_decoupling_scheme
        n = int(self.parameters.RamseyScanGap.dynamical_decoupling_num_pulses)
        
        print "1212"
        print "freq 729:" , freq_729
        print "total wait time:", ramsey_duration

         # construct wait_times list of (n+1) elements
        wait_times = []
        if dd_scheme == 'CPMG':
          wait_times.append(ramsey_duration / (2.0 * n))
          wait_times.extend([ramsey_duration / float(n)] * (n-1))
          wait_times.append(ramsey_duration / (2.0 * n))
        elif dd_scheme == 'UDD':
          normalized_start_times = []
          for j in range(1,n+2):
            delta_j = np.sin(np.pi*j/(2.0*n+2.0))**2 # from UDD paper
            normalized_start_times.append(delta_j)
          
          print "normalized start times list:", normalized_start_times
          prev_t = 0
          for t in normalized_start_times:
            wait_times.append((t - prev_t) * ramsey_duration)
            prev_t = t

        print "wait times list:", wait_times

        
        # building the sequence
        self.addSequence(StatePreparation)

        # # initial pi/2 rotation at 0 degrees
        if pi_half: 
          self.addSequence(GlobalRotation, { "GlobalRotation.frequency":freq_729,
                                             "GlobalRotation.angle": U(s*np.pi, 'rad'),
                                             # "GlobalRotation.phase": U(0, 'deg')
                                             })

       

        # n pi-pulses, one after each of the first n wait_times
        for i in range(n):
          if pi_half:
            self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : wait_times[i] })
            
          self.addSequence(GlobalRotation, { "GlobalRotation.frequency":freq_729,
                                              "GlobalRotation.angle": U(np.pi, 'rad'), 
                                              "GlobalRotation.phase": U(89.99, 'deg')
                                            })
          
        # wait for final wait_time
        if pi_half:
          self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : wait_times[n] })        

          # final pi/2 rotation at 270 degrees plus scan phase
          self.addSequence(GlobalRotation, {"GlobalRotation.frequency":freq_729, 
                                           "GlobalRotation.angle": U(s*np.pi, 'rad'), 
                                           "GlobalRotation.phase": U(2*np.pi/2.0, 'rad')
                                               + self.parameters.Ramsey.second_pulse_phase 
                                               })

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
