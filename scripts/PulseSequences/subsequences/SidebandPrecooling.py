from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from treedict import TreeDict
from OpticalPumping import optical_pumping
from labrad.units import WithUnit

class sideband_precooling(pulse_sequence):

    required_parameters = [
        ('SidebandPrecooling', 'cycles'),
        ('SidebandPrecooling', 'mode_1'),
        ('SidebandPrecooling', 'mode_2'),
        ('SidebandPrecooling', 'frequency_1'),
        ('SidebandPrecooling', 'frequency_2'),

        ('SidebandCoolingContinuous','sideband_cooling_continuous_duration'),
        ('SidebandCooling', 'sideband_cooling_amplitude_729'),
        ('SidebandCooling', 'sideband_cooling_amplitude_854'),
        ('SidebandCooling', 'sideband_cooling_amplitude_866'),
        ('SidebandCooling', 'sideband_cooling_optical_pumping_duration')
        ]

    required_subsequences = [optical_pumping]

    replaced_parameters = {
        optical_pumping:[ ('OpticalPumping','optical_pumping_continuous'),
                          ('OpticalPumpingContinuous','optical_pumping_continuous_duration') ] }


    def sequence(self):

        sc = self.parameters.SidebandCooling
        scc = self.parameters.SidebandCoolingContinuous
        spc = self.parameters.SidebandPrecooling

        repump_dur = WithUnit(100, 'us')
        f_repump = WithUnit(80, 'MHz')

        if spc.mode_1 == 'aux_radial': channel1 = '729local'
        if spc.mode_1 == 'aux_axial': channel1 = '729global'
        if spc.mode_2 == 'aux_radial': channel2 = '729local'
        if spc.mode_2 == 'aux_axial': channel2 = '729global'

        cooling_duration = scc.sideband_cooling_continuous_duration
        cooling_amplitude = sc.sideband_cooling_amplitude_729
        amp_854 = sc.sideband_cooling_amplitude_854
        amp_866 = sc.sideband_cooling_amplitude_866
        
        op_replace = {'OpticalPumping.optical_pumping_continuous':True,
                      'OpticalPumpingContinuous.optical_pumping_continuous_duration':sc.sideband_cooling_optical_pumping_duration}

        self.end = self.start
        do_optical_pumping = False

        for n in range(int(spc.cycles)):
            self.cycle_start_time = self.end
        
            if spc.mode_1 != 'off':
                self.addDDS(channel1, self.cycle_start_time, cooling_duration,  spc.frequency_1, cooling_amplitude)
                self.addDDS('854', self.cycle_start_time, cooling_duration + repump_dur, f_repump, amp_854)
                self.addDDS('866', self.cycle_start_time, cooling_duration + repump_dur, f_repump, amp_866)
                self.end = self.cycle_start_time + cooling_duration + repump_dur
                do_optical_pumping = True
                self.cycle_start_time = self.end

            if spc.mode_2 != 'off':
                self.addDDS(channel2, self.cycle_start_time, cooling_duration, spc.frequency_2, cooling_amplitude)
                self.addDDS('854', self.cycle_start_time, cooling_duration + repump_dur, f_repump, amp_854)
                self.addDDS('866', self.cycle_start_time, cooling_duration + repump_dur, f_repump, amp_866)
                self.end = self.cycle_start_time + cooling_duration + repump_dur
                do_optical_pumping = True
                self.cycle_start_time = self.end

            ## optical pumping
            if do_optical_pumping:
                self.addSequence(optical_pumping, TreeDict.fromdict(op_replace))

class sideband_precooling_with_splocal(pulse_sequence):

    required_parameters = [
        ('SidebandPrecooling', 'cycles'),
        ('SidebandPrecooling', 'mode_1'),
        ('SidebandPrecooling', 'mode_2'),
        ('SidebandPrecooling', 'frequency_1'),
        ('SidebandPrecooling', 'frequency_2'),

        ('SidebandCoolingContinuous','sideband_cooling_continuous_duration'),
        ('SidebandCooling', 'sideband_cooling_amplitude_729'),
        ('SidebandCooling', 'sideband_cooling_amplitude_854'),
        ('SidebandCooling', 'sideband_cooling_amplitude_866'),
        ('SidebandCooling', 'sideband_cooling_optical_pumping_duration')
        ]

    required_subsequences = [optical_pumping]

    replaced_parameters = {
        optical_pumping:[ ('OpticalPumping','optical_pumping_continuous'),
                          ('OpticalPumpingContinuous','optical_pumping_continuous_duration') ] }


    def sequence(self):

        sc = self.parameters.SidebandCooling
        scc = self.parameters.SidebandCoolingContinuous
        spc = self.parameters.SidebandPrecooling

        repump_dur = WithUnit(100, 'us')
        f_repump = WithUnit(80, 'MHz')

        if spc.mode_1 == 'aux_radial': channel1 = '729local'
        if spc.mode_1 == 'aux_axial': channel1 = '729global'
        if spc.mode_2 == 'aux_radial': channel2 = '729local'
        if spc.mode_2 == 'aux_axial': channel2 = '729global'

        cooling_duration = scc.sideband_cooling_continuous_duration
        cooling_amplitude = sc.sideband_cooling_amplitude_729
        amp_854 = sc.sideband_cooling_amplitude_854
        amp_866 = sc.sideband_cooling_amplitude_866
        
        op_replace = {'OpticalPumping.optical_pumping_continuous':True,
                      'OpticalPumpingContinuous.optical_pumping_continuous_duration':sc.sideband_cooling_optical_pumping_duration}

        self.end = self.start

        self.start_initial = self.start
        do_optical_pumping = False

        for n in range(int(spc.cycles)):
            self.cycle_start_time = self.end
        
            if spc.mode_1 != 'off':
                self.addDDS(channel1, self.cycle_start_time, cooling_duration,  spc.frequency_1, cooling_amplitude)
                self.addDDS('854', self.cycle_start_time, cooling_duration + repump_dur, f_repump, amp_854)
                self.addDDS('866', self.cycle_start_time, cooling_duration + repump_dur, f_repump, amp_866)
                self.end = self.cycle_start_time + cooling_duration + repump_dur
                do_optical_pumping = True
                self.cycle_start_time = self.end

            if spc.mode_2 != 'off':
                self.addDDS(channel2, self.cycle_start_time, cooling_duration, spc.frequency_2, cooling_amplitude)
                self.addDDS('854', self.cycle_start_time, cooling_duration + repump_dur, f_repump, amp_854)
                self.addDDS('866', self.cycle_start_time, cooling_duration + repump_dur, f_repump, amp_866)
                self.end = self.cycle_start_time + cooling_duration + repump_dur
                do_optical_pumping  = True
                self.cycle_start_time = self.end

            ## optical pumping
            if do_optical_pumping:
                self.addSequence(optical_pumping, TreeDict.fromdict(op_replace))

        
        f = WithUnit(80. - 0.2, 'MHz')
        duration = self.end - self.start
        self.addDDS('SP_local', self.start_initial, self.end - self.start_initial, f, WithUnit(-14., 'dBm'))
