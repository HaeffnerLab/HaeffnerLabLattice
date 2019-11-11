from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from subsequences.RepumpDwithDoppler import doppler_cooling_after_repump_d
from subsequences.SidebandCooling import sideband_cooling
from subsequences.OpticalPumping import optical_pumping
from subsequences.Tomography import tomography_readout
from subsequences.TurnOffAll import turn_off_all

from subsequences.RabiExcitation import rabi_excitation, rabi_excitation_no_offset
from subsequences.BlueHeating import blue_heating
from subsequences.EmptySequence import empty_sequence

from treedict import TreeDict
from labrad.units import WithUnit
           
class ramsey_with_heating(pulse_sequence):
    
    required_parameters = [
                           ('OpticalPumping','optical_pumping_enable'), 
                           ('SidebandCooling','sideband_cooling_enable'),
                           ('Dephasing_Pulses', 'preparation_pulse_frequency'),
                           ('Dephasing_Pulses', 'preparation_pulse_duration'),
                           ('Dephasing_Pulses', 'preparation_pulse_amplitude'),
                           
                           ('Dephasing_Pulses', 'evolution_pulses_frequency'),
                           ('Dephasing_Pulses', 'evolution_pulses_duration'),
                           ('Dephasing_Pulses', 'evolution_pulses_amplitude'),
                           ('Dephasing_Pulses', 'evolution_ramsey_time'),
                           ('Dephasing_Pulses', 'evolution_pulses_phase'),
                           
                           #('RamseyDephase','first_pulse_duration'),
                           ('RamseyDephase','pulse_gap'),
                           #('RamseyDephase','dephasing_frequency'),
                           #('RamseyDephase','dephasing_amplitude'),
                           #('RamseyDephase','dephasing_duration'),
                           #('RamseyDephase','second_pulse_duration'),
                           ('Heating','local_blue_heating_frequency_397'),
                           ('Heating','local_blue_heating_amplitude_397'),
                           ('Heating','blue_heating_frequency_866'),
                           ('Heating','blue_heating_amplitude_866'),
                           ('Heating','blue_heating_duration'),
                           ('Heating','blue_heating_repump_additional'),
                           ('Heating','blue_heating_delay_before'),
                           ('Heating','enable_heating_pulse'),                           
                           ]

    required_subsequences = [doppler_cooling_after_repump_d, optical_pumping, 
                             tomography_readout, turn_off_all, sideband_cooling, blue_heating, empty_sequence, rabi_excitation, rabi_excitation_no_offset]
 
    
    replaced_parameters = {empty_sequence:[('EmptySequence','empty_sequence_duration')],
                           rabi_excitation:[('Excitation_729','rabi_excitation_frequency'),
                                            ('Excitation_729','rabi_excitation_phase'),
                                            ('Excitation_729','rabi_excitation_amplitude'),
                                            ('Excitation_729','rabi_excitation_duration'),
                                            ],
                           rabi_excitation_no_offset:[('Excitation_729','rabi_excitation_frequency'),
                                            ('Excitation_729','rabi_excitation_phase'),
                                            ('Excitation_729','rabi_excitation_amplitude'),
                                            ('Excitation_729','rabi_excitation_duration'),
                                            ],
                           blue_heating:[ ('Excitation_729','rabi_excitation_frequency'),
                                            ('Excitation_729','rabi_excitation_phase'),
                                            ('Excitation_729','rabi_excitation_amplitude'),
                                            ('Excitation_729','rabi_excitation_duration'),
                                            ('Heating','local_blue_heating_frequency_397'),
                                            ('Heating','local_blue_heating_amplitude_397'),
                                            ('Heating','blue_heating_frequency_866'),
                                            ('Heating','blue_heating_amplitude_866'),
                                            ('Heating','blue_heating_duration'),
                                            ('Heating','blue_heating_repump_additional')]
                           }


    def sequence(self):
        p = self.parameters


        rp = self.parameters.Dephasing_Pulses
        replace_preparation = TreeDict.fromdict({
        'Excitation_729.rabi_excitation_frequency':rp.preparation_pulse_frequency,
        'Excitation_729.rabi_excitation_duration':rp.preparation_pulse_duration,
        'Excitation_729.rabi_excitation_amplitude':rp.preparation_pulse_amplitude,
        'Excitation_729.rabi_excitation_phase':WithUnit(0,'deg')
        })
        evolution_pulse = TreeDict.fromdict({
        'Excitation_729.rabi_excitation_frequency':rp.evolution_pulses_frequency,
        'Excitation_729.rabi_excitation_duration':rp.evolution_pulses_duration,
        'Excitation_729.rabi_excitation_amplitude':rp.evolution_pulses_amplitude,
        'Excitation_729.rabi_excitation_phase':rp.evolution_pulses_phase                                               
        })
        rd = p.RamseyDephase
        heating_replace = TreeDict.fromdict({'Heating.local_blue_heating_frequency_397':rd.dephasing_frequency,
                                             'Heating.local_blue_heating_amplitude_397':rd.dephasing_amplitude,
                                             'Heating.blue_heating_frequency_866':rp.StateReadout.state_readout_frequency_866,
                                             'Heating.blue_heating_amplitude_866':rp.StateReadout.state_readout_amplitude_866,
                                             'Heating.blue_heating_duration':rd.dephasing_duration,
                                             'Heating.blue_heating_repump_additional':WithUnit(5, 'us')
                                             })



        self.end = WithUnit(10, 'us')
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling_after_repump_d)
        if p.OpticalPumping.optical_pumping_enable:
            self.addSequence(optical_pumping)
        if p.SidebandCooling.sideband_cooling_enable:
            self.addSequence(sideband_cooling)

        
        #import subsequences.boerge_tools as boerge_tools
        #boerge_tools.dump_keys(rp)

        #import IPython
        #IPython.embed()        
            

        frequency_advance_duration = WithUnit(6, 'us')
        total_heating_time = frequency_advance_duration + p.Heating.blue_heating_duration + p.Heating.blue_heating_repump_additional        

        remaining_ramsey_time = rp.evolution_ramsey_time-total_heating_time-p.Heating.blue_heating_delay_before
        
        self.addSequence(rabi_excitation, replacement_dict = replace_preparation)
        
        # took out the next empty sequence since the blue heating takes care of that
        # self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':p.Heating.blue_heating_delay_before}))        
        
        if p.Heating.enable_heating_pulse==True:
            self.addSequence(blue_heating, replace_preparation)
        else:
            # if there is no heating pulse, then we just do a ramsey gap scan
            remaining_ramsey_time = rp.evolution_ramsey_time
            
        self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':remaining_ramsey_time}))        

        if rp.preparation_pulse_frequency == rp.evolution_pulses_frequency:
            self.addSequence(rabi_excitation_no_offset, replacement_dict = evolution_pulse)
        else:
            self.addSequence(rabi_excitation, replacement_dict = evolution_pulse)

        self.addSequence(tomography_readout)

        print "Ramsey gap time", rp.evolution_ramsey_time
        print "Blue start time", p.Heating.blue_heating_delay_before
        print "Total heating time", total_heating_time
        print "Remaining Ramsey time ", remaining_ramsey_time, " with phase ", rp.evolution_pulses_phase
        
        ##import IPython
        ##IPython.embed()
        #import boerge_tools
        #print "Boerges Sequence"
        #print "First pulse:"
        #boerge_tools.dump_keys(replace_preparation)
        #print "Empty seq:"
        #print p.evolution_ramsey_time
        #print "Second Pulse:"
        #boerge_tools.dump_keys(evolution_pulse)        
        



