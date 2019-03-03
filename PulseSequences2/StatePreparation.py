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
        from subsequences.PreDopplerCooling import PreDopplerCooling
        from subsequences.OpticalPumping import OpticalPumping
        from subsequences.OpticalPumpingPulsed import OpticalPumpingPulsed
        from subsequences.SidebandCooling import SidebandCooling
        from subsequences.EmptySequence import EmptySequence
        
        self.end = U(10., 'us')
        self.addSequence(TurnOffAll)
        self.addSequence(RepumpD) # initializing the state of the ion
        self.addSequence(PreDopplerCooling) 
        self.addSequence(DopplerCooling) 
        
        if self.parameters.StatePreparation.optical_pumping_enable:
            self.addSequence(OpticalPumping)
            
        
        # precolling side band cooling             
        if self.parameters.StatePreparation.precooling_sideband_enable:       

            duration_op= self.parameters.SidebandCooling.sideband_cooling_optical_pumping_duration

            if self.parameters.SequentialSBCooling1.enable:
              for i in range(int(self.parameters.SequentialSBCooling1.cycles)):
                print "sequential side band cooling mode 1"
                print "cycle number ", i
                sbc=self.parameters.SequentialSBCooling1
                # replacing the channel, sideband and order 
                self.addSequence(SidebandCooling,{"StatePreparation.channel_729" : sbc.channel_729,
                                                      "SidebandCooling.selection_sideband" : sbc.selection_sideband,
                                                      "SidebandCooling.order" : sbc.order
                                                      })
                self.addSequence(OpticalPumping, {'OpticalPumpingContinuous.optical_pumping_continuous_duration':duration_op })

            if self.parameters.SequentialSBCooling2.enable:
              for i in range(int(self.parameters.SequentialSBCooling2.cycles)):
                print "sequential side band cooling mode 2"
                print "cycle number ", i
                sbc=self.parameters.SequentialSBCooling2
                # replacing the channel, sideband and order 
                self.addSequence(SidebandCooling,{"StatePreparation.channel_729" : sbc.channel_729,
                                                      "SidebandCooling.selection_sideband" : sbc.selection_sideband,
                                                      "SidebandCooling.order" : sbc.order
                                                      })
                self.addSequence(OpticalPumping, {'OpticalPumpingContinuous.optical_pumping_continuous_duration':duration_op })


          
        


        # side band cooling             
        if self.parameters.StatePreparation.sideband_cooling_enable:       
            duration_op= self.parameters.SidebandCooling.sideband_cooling_optical_pumping_duration
            for i in range(int(self.parameters.SidebandCooling.sideband_cooling_cycles)):
                
                
                if self.parameters.SequentialSBCooling.enable:
                    print "sequential side band cooling"
                    sbc=self.parameters.SequentialSBCooling
                    # replacing the channel, sideband and order 
                    self.addSequence(SidebandCooling,{"StatePreparation.channel_729" : sbc.channel_729,
                                                      "SidebandCooling.selection_sideband" : sbc.selection_sideband,
                                                      "SidebandCooling.order" : sbc.order,
                                                      "SidebandCooling.line_selection" : sbc.line_selection
                                                      })
                    self.addSequence(OpticalPumping, {'OpticalPumpingContinuous.optical_pumping_continuous_duration':duration_op })

                #  This is the important mode to cool
                self.addSequence(SidebandCooling)
                self.addSequence(OpticalPumping, {'OpticalPumpingContinuous.optical_pumping_continuous_duration':duration_op }) # apply an additional full optical pumping aftereach cycle
                
                if self.parameters.SequentialSBCooling1.enable:
                    print "sequential side band cooling"
                    sbc=self.parameters.SequentialSBCooling1
                    # replacing the channel, sideband and order 
                    self.addSequence(SidebandCooling,{"StatePreparation.channel_729" : sbc.channel_729,
                                                      "SidebandCooling.selection_sideband" : sbc.selection_sideband,
                                                      "SidebandCooling.order" : sbc.order
                                                      })
                    self.addSequence(OpticalPumping, {'OpticalPumpingContinuous.optical_pumping_continuous_duration':duration_op })
                
                if self.parameters.SequentialSBCooling2.enable:
                    print "sequential side band cooling"
                    sbc=self.parameters.SequentialSBCooling2
                    # replacing the channel, sideband and order 
                    self.addSequence(SidebandCooling,{"StatePreparation.channel_729" : sbc.channel_729,
                                                      "SidebandCooling.selection_sideband" : sbc.selection_sideband,
                                                      "SidebandCooling.order" : sbc.order
                                                      })
                    self.addSequence(OpticalPumping, {'OpticalPumpingContinuous.optical_pumping_continuous_duration':duration_op })
                
        
        if self.parameters.StatePreparation.aux_optical_pumping_enable and not self.parameters.StatePreparation.aux_optical_pumping_pulsed_enable:
            op_aux = self.parameters.OpticalPumpingAux
#             print "12345 adding aux optical pumping"
#             print  op_aux.channel_729, op_aux.aux_op_line_selection,op_aux.duration
#             print "Aux Optical Pumping"
            self.addSequence(OpticalPumping, {'StatePreparation.channel_729': op_aux.channel_729,
                                              'OpticalPumping.line_selection': op_aux.aux_op_line_selection,
                                              'OpticalPumping.optical_pumping_amplitude_729': op_aux.aux_optical_pumping_amplitude_729,
                                              'OpticalPumpingContinuous.optical_pumping_continuous_duration':op_aux.duration,
                                              "OpticalPumping.optical_pumping_amplitude_854": op_aux.amp_854 })
                  
        
        if self.parameters.StatePreparation.aux_optical_pumping_enable and self.parameters.StatePreparation.aux_optical_pumping_pulsed_enable:
            op_aux = self.parameters.OpticalPumpingAux
            for _ in range(int(self.parameters.StatePreparation.number_of_cycles)):
                self.addSequence(OpticalPumpingPulsed, {'StatePreparation.channel_729': op_aux.channel_729,
                                                        'OpticalPumping.line_selection': op_aux.aux_op_line_selection
                                                       })

        self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : self.parameters.Heating.background_heating_time})
        
