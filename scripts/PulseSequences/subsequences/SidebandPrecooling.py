from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from treedict import TreeDict
from labrad.units import WithUnit

class sideband_precooling(pulse_sequence):

    required_parameters = [
        ('SidebandPrecooling', 'cycles'),
        ('SidebandPrecooling', 'mode_1'),
        ('SidebandPrecooling', 'mode_2'),
        ('SidebandPrecooling', 'frequency_1'),
        ('SidebandPrecooling', 'frequency_2'),

        ('SidebandCoolingContinuous','sideband_cooling_continuous_duration'),
        ('SidebandCoolingContinuous', 'sideband_cooling_continuous_amplitude_729'),
        ('SidebandCoolingContinuous', 'sideband_cooling_continuous_amplitude_854'),
        ('SidebandCoolingContinuous', 'sideband_cooling_continuous_amplitude_866')
        ]

    required_subsequences = [optical_pumping]

    replaced_parameters = {
        optical_pumping:[ ('OpticalPumping','optical_pumping_continuous'),
                          ('OpticalPumpingContinuous','optical_pumping_continuous_duration') ]


    def sequence(self):

        sc = self.parameters.SidebandCooling
        scc = self.parameters.SidebandCoolingContinuous
        spc = self.paramters.SidebandPrecooling

        repump_dir = WithUnit(100, 'us')
        f_repump = WithUnit(80, 'MHz')

        if mode_1 == 'aux_radial': channel1 = '729local'
        if mode_1 == 'aux_axial': channel1 == '729global'
        if mode_2 == 'aux_radial': channel2 == '729local'
        if mode_2 == 'aux_axial': channel2 = '729global'

        cooling_duration = scc.sideband_cooling_continuous_duration
        cooling_amplitude = scc.sideband_cooling_continuous_amplitude_729
        amp_854 = scc.sideband_cooling_continuous_amplitude_854
        amp_866 = scc.sideband_cooling_continuous_amplitude_866
        
        op_replace = {'OpticalPumping.optical_pumping_continuous':True,
                      'OpticalPumpingContinuous.optical_pumping_continuous_duration':sc.sideband_cooling_optical_pumping_duration}

        self.end = self.start

        for n in range(spc.cycles):
            self.cycle_start_time = self.end
        
            if mode_1 != 'off':
                self.addDDS(channel1, self.cycle_start_time, cooling_duration,  spc.frequency_1, cooling_amplitude)
                self.addDDS('854', self.cycle_start_time, cooling_duration + repump_dur, f_repump, amp_854)
                self.addDDS('866', self.cycle_start_time, cooling_duration + repump_dur, f_repump, amp_866)
                self.end = self.cycle_start_time + cooling_duration + repump_dur
                self.cycle_start_time = self.end

            if mode_2 != 'off':
                self.addDDS(channel2, self.cycle_start_time, cooling_duration, spc.frequency_2)
                self.addDDS('854', self.cycle_start_time, cooling_duration + repump_dur, f_repump, amp_854)
                self.addDDS('866', self.cycle_start_time, cooling_duration + repump_dur, f_repump, amp_866)
                self.end = self.cycle_start_time + cooling_duration + repump_dur
                self.cycle_start_time = self.end

            ## optical pumping
            if ((mode_1 != 'off') and (mode_2 != 'off')):
                self.addSequence(optical_pumping, TreeDict.fromdict(op_replace))

class sideband_precooling_with_splocal(pulse_sequence):

    required_parameters = [
        ('SidebandPrecooling', 'cycles'),
        ('SidebandPrecooling', 'mode_1'),
        ('SidebandPrecooling', 'mode_2'),
        ('SidebandPrecooling', 'frequency_1'),
        ('SidebandPrecooling', 'frequency_2'),

        ('SidebandCoolingContinuous','sideband_cooling_continuous_duration'),
        ('SidebandCoolingContinuous', 'sideband_cooling_continuous_amplitude_729'),
        ('SidebandCoolingContinuous', 'sideband_cooling_continuous_amplitude_854'),
        ('SidebandCoolingContinuous', 'sideband_cooling_continuous_amplitude_866')
        ]

    required_subsequences = [optical_pumping]

    replaced_parameters = {
        optical_pumping:[ ('OpticalPumping','optical_pumping_continuous'),
                          ('OpticalPumpingContinuous','optical_pumping_continuous_duration') ]


    def sequence(self):

        sc = self.parameters.SidebandCooling
        scc = self.parameters.SidebandCoolingContinuous
        spc = self.paramters.SidebandPrecooling

        repump_dir = WithUnit(100, 'us')
        f_repump = WithUnit(80, 'MHz')

        if mode_1 == 'aux_radial': channel1 = '729local'
        if mode_1 == 'aux_axial': channel1 == '729global'
        if mode_2 == 'aux_radial': channel2 == '729local'
        if mode_2 == 'aux_axial': channel2 = '729global'

        cooling_duration = scc.sideband_cooling_continuous_duration
        cooling_amplitude = scc.sideband_cooling_continuous_amplitude_729
        amp_854 = scc.sideband_cooling_continuous_amplitude_854
        amp_866 = scc.sideband_cooling_continuous_amplitude_866
        
        op_replace = {'OpticalPumping.optical_pumping_continuous':True,
                      'OpticalPumpingContinuous.optical_pumping_continuous_duration':sc.sideband_cooling_optical_pumping_duration}

        self.end = self.start

        self.start_initial = self.start

        for n in range(spc.cycles):
            self.cycle_start_time = self.end
        
            if mode_1 != 'off':
                self.addDDS(channel1, self.cycle_start_time, cooling_duration,  spc.frequency_1, cooling_amplitude)
                self.addDDS('854', self.cycle_start_time, cooling_duration + repump_dur, f_repump, amp_854)
                self.addDDS('866', self.cycle_start_time, cooling_duration + repump_dur, f_repump, amp_866)
                self.end = self.cycle_start_time + cooling_duration + repump_dur
                self.cycle_start_time = self.end

            if mode_2 != 'off':
                self.addDDS(channel2, self.cycle_start_time, cooling_duration, spc.frequency_2)
                self.addDDS('854', self.cycle_start_time, cooling_duration + repump_dur, f_repump, amp_854)
                self.addDDS('866', self.cycle_start_time, cooling_duration + repump_dur, f_repump, amp_866)
                self.end = self.cycle_start_time + cooling_duration + repump_dur
                self.cycle_start_time = self.end

            ## optical pumping
            if ((mode_1 != 'off') and (mode_2 != 'off')):
                self.addSequence(optical_pumping, TreeDict.fromdict(op_replace))

        
        f = WithUnit(80. - 0.2, 'MHz')
        duration = self.end - self.start
        self.addDDS('SP_local', self.start_initial, self.end - self.start_initial, f, WithUnit(-14., 'dBm'))
