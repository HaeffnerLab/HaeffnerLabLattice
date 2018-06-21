from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from MotionAnalysisSpectrum import MotionAnalysisSpectrum as MASpectrum
from lattice.scripts.scriptLibrary.devices import agilent
from treedict import TreeDict
import time
import numpy as np

class MotionAnalysisRamsey(pulse_sequence):

    scannable_params = {
        'Motion_Analysis.ramsey_duration': [(0, 10.0, 0.5, 'ms') ,'ramsey']
        #'Ramsey.second_pulse_phase': [(0, 360., 15, 'deg') ,'ramsey']
        }

    show_params= [#'RamseyScanGap.ramsey_duration',
                  #'RamseyScanPhase.scanphase',
                  #'RamseyScanGap.detuning',

                  'Motion_Analysis.pulse_width_397',
                  'Motion_Analysis.amplitude_397',
                  'Motion_Analysis.sideband_selection',
                  'Motion_Analysis.ramsey_detuning',

                  'RabiFlopping.duration',
                  'RabiFlopping.rabi_amplitude_729',
                  'RabiFlopping.line_selection',
                  'RabiFlopping.selection_sideband',
                  'RabiFlopping.order',

                  'StatePreparation.channel_729',
                  'StatePreparation.optical_pumping_enable',
                  'StatePreparation.sideband_cooling_enable']

    @classmethod
    def run_initial(cls, cxn, parameters_dict):
        #         print "Switching the 866DP to auto mode"
        cxn.pulser.switch_auto('866DP')
        cxn.pulser.switch_auto('397mod')


        ######### motion analysis
        # creating an agilent instance
        agi = agilent(cxn)
        # getting the params
        ma = parameters_dict.Motion_Analysis

        detuning = ma.ramsey_detuning
        # calc frequcy shift
        mode = ma.sideband_selection

        trap_frequency = parameters_dict['TrapFrequencies.' + mode]
                
        # run with detuning
        f = parameters_dict['TrapFrequencies.' + mode]
        f = f + detuning
        # changing the frequency of the Agilent
        agi.set_frequency(f)
        print "run initial " , agi.get_frequency()
        
        time.sleep(0.5) # just make sure everything is programmed before starting the sequence


    @classmethod
    def run_in_loop(cls, cxn, parameters_dict, data_so_far, data_x):
        pass

    @classmethod
    def run_finally(cls, cxn, parameters_dict, data, x):
        #         print "switching the 866 back to ON"
        cxn.pulser.switch_manual('866DP', True)
        cxn.pulser.switch_manual('397mod', False)

    def sequence(self):

        from StatePreparation import StatePreparation
        from subsequences.EmptySequence import EmptySequence
        from subsequences.OpticalPumping import OpticalPumping
        from subsequences.MotionAnalysis import MotionAnalysis
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll
        from subsequences.RabiExcitation import RabiExcitation

        # additional optical pumping duration
        duration_op = self.parameters.SidebandCooling.sideband_cooling_optical_pumping_duration

        # calculate the final diagnosis params
        rf = self.parameters.RabiFlopping
        freq_729 = self.calc_freq(rf.line_selection, rf.selection_sideband, rf.order)

        # print out some diagnostics
        print "Using freq 729: ", freq_729
        print "Using detuning: ", self.parameters.Motion_Analysis.detuning
        print "Ramsey wait time: ", self.parameters.RamseyScanGap.ramsey_duration

        # state preparation
        self.end = U(10., 'us')
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)

        # 397 excitation and small optical pumping after the motion excitation
        self.addSequence(MotionAnalysis)
        self.addSequence(OpticalPumping, { 'OpticalPumpingContinuous.optical_pumping_continuous_duration': duration_op })

        # wait for desired time
        self.addSequence(EmptySequence,  { 'EmptySequence.empty_sequence_duration' : self.parameters.Motion_Analysis.ramsey_duration})

        # 397 excitation and small optical pumping after the motion excitation
        self.addSequence(MotionAnalysis)
        self.addSequence(OpticalPumping, { 'OpticalPumpingContinuous.optical_pumping_continuous_duration': duration_op })

        # 729 excitation to transfer the motional DOF to the electronic DOF
        # running the excitation from the Rabi flopping
        self.addSequence(RabiExcitation, {'Excitation_729.rabi_excitation_frequency': freq_729,
                                          'Excitation_729.rabi_excitation_amplitude': rf.rabi_amplitude_729,
                                          'Excitation_729.rabi_excitation_duration':  rf.duration })
        self.addSequence(StateReadout)
