from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict

class StatePreparation(pulse_sequence):
    
    #name = 'State preparation'

    scannable_params = {
                        }

    show_params= ['DopplerCooling.duration',
                  'Spectrum.line_selection',
                  'sideband_selection']

    def sequence(self):
        print "STARTING STATE PREP"
        print self.start
        
        from subsequences.TurnOffAll import TurnOffAll
        from subsequences.RepumpD import RepumpD
        from subsequences.DopplerCooling import DopplerCooling
        from subsequences.OpticalPumping import OpticalPumping
        from subsequences.SidebandCooling import SidebandCooling
        from subsequences.EmptySequence import EmptySequence
        
        self.end = U(10., 'us')
        self.addSequence(TurnOffAll)
        self.addSequence(RepumpD) # initializing the state of the ion
        self.addSequence(DopplerCooling) 
        
        if self.parameters.StatePreparation.optical_pumping_enable:
            self.addSequence(OpticalPumping)
            
  
        # side band cooling             
        if self.parameters.StatePreparation.sideband_cooling_enable:       
            duration_op= self.parameters.SidebandCooling.sideband_cooling_optical_pumping_duration
            for i in range(int(self.parameters.SidebandCooling.sideband_cooling_cycles)):
                self.addSequence(SidebandCooling)
                self.addSequence(OpticalPumping, {'OpticalPumpingContinuous.optical_pumping_continuous_duration':duration_op }) # apply an additional full optical pumping aftereach cycle
                
                if self.parameters.SequentialSBCooling.enable:
                    print "sequential side band cooling"
                    sbc=self.parameters.SequentialSBCooling
                    # replacing the channel, sideband and order 
                    self.addSequence(SidebandCooling,{"StatePreparation.channel_729" : sbc.channel_729,
                                                      "SidebandCooling.selection_sideband" : sbc.selection_sideband,
                                                      "SidebandCooling.order" : sbc.order
                                                      })
                    self.addSequence(OpticalPumping, {'OpticalPumpingContinuous.optical_pumping_continuous_duration':duration_op })
                #print "Running sideband cooling cycle #"
                #print(i) 
                # aux_optical_pumping
        
        if self.parameters.StatePreparation.aux_optical_pumping_enable:
            op_aux=self.parameters.OpticalPumpingAux
#             print "12345 adding aux optical pumping"
#             print  op_aux.channel_729, op_aux.aux_op_line_selection,op_aux.duration
#             print "Aux Optical Pumping"
            self.addSequence(OpticalPumping, {'StatePreparation.channel_729': op_aux.channel_729,
                                              'OpticalPumping.line_selection': op_aux.aux_op_line_selection,
                                              'OpticalPumping.optical_pumping_amplitude_729': op_aux.aux_optical_pumping_amplitude_729,
                                              'OpticalPumpingContinuous.optical_pumping_continuous_duration':op_aux.duration })
                  
        self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : self.parameters.Heating.background_heating_time})
        
        