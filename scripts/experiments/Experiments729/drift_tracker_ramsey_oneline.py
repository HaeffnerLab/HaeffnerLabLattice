from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from excitations import excitation_ramsey
from treedict import TreeDict
from labrad.units import WithUnit
from numpy import arcsin, pi
import time

class drift_tracker_ramsey_oneline(experiment):
    
    name = 'DriftTrackerRamseyOneLine'
    dt_required_parameters = [
                           ('DriftTrackerRamsey','line_selection'),
                           ('DriftTrackerRamsey','gap_time'),
                           ('DriftTrackerRamsey','pi_time'),
                           ('DriftTrackerRamsey','amplitude'),
                           ('DriftTrackerRamsey','detuning'),
                           ('DriftTrackerRamsey','readouts'),
                           ('DriftTrackerRamsey','optical_pumping_enable_DT'),
                           
                           ('StateReadout','camera_primary_ion'),
                           ('StateReadout','use_camera_for_readout'),                 
                           ]

    
    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.dt_required_parameters)
        parameters = parameters.union(set(excitation_ramsey.all_required_parameters()))
        parameters = list(parameters)
        #removing parameters we'll be overwriting, and they do not need to be loaded
        parameters.remove(('Ramsey','ramsey_time'))
        parameters.remove(('Ramsey','second_pulse_phase'))
        parameters.remove(('Excitation_729','rabi_excitation_amplitude'))
        parameters.remove(('Excitation_729','rabi_excitation_frequency'))
        parameters.remove(('Tomography','iteration'))
        parameters.remove(('Tomography','rabi_pi_time'))
        parameters.remove(('Tomography','tomography_excitation_amplitude'))
        parameters.remove(('Tomography','tomography_excitation_frequency'))
        parameters.remove(('TrapFrequencies','axial_frequency'))
        parameters.remove(('TrapFrequencies','radial_frequency_1')),
        parameters.remove(('TrapFrequencies','radial_frequency_2')),
        parameters.remove(('TrapFrequencies','rf_drive_frequency')),
        #will be disabling sideband cooling automatically
        parameters.remove(('SidebandCooling','sideband_cooling_enable')),
        parameters.remove(('SidebandCooling','frequency_selection')),
        parameters.remove(('SidebandCooling','manual_frequency_729')),
        parameters.remove(('SidebandCooling','line_selection')),
        parameters.remove(('SidebandCooling','sideband_selection')),
        parameters.remove(('SidebandCooling','sideband_cooling_type')),
        parameters.remove(('SidebandCooling','sideband_cooling_cycles')),
        parameters.remove(('SidebandCooling','sideband_cooling_duration_729_increment_per_cycle')),
        parameters.remove(('SidebandCooling','sideband_cooling_frequency_854')),
        parameters.remove(('SidebandCooling','sideband_cooling_amplitude_854')),
        parameters.remove(('SidebandCooling','sideband_cooling_frequency_866')),
        parameters.remove(('SidebandCooling','sideband_cooling_amplitude_866')),
        parameters.remove(('SidebandCooling','sideband_cooling_amplitude_729')),
        parameters.remove(('SidebandCooling','sideband_cooling_optical_pumping_duration')),
        parameters.remove(('SidebandCoolingContinuous','sideband_cooling_continuous_duration')),             
        parameters.remove(('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_729')),
        parameters.remove(('SidebandCoolingPulsed','sideband_cooling_pulsed_cycles')),
        parameters.remove(('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_repumps')),
        parameters.remove(('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_additional_866')),
        parameters.remove(('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_between_pulses')),                          
        #will be enable optical pumping automatically
        parameters.remove(('OpticalPumping', 'optical_pumping_enable'))
        return parameters
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.drift_tracker = cxn.sd_tracker
        self.excitation = self.make_experiment(excitation_ramsey)
        self.excitation.initialize(cxn, context, ident)
        self.phases = [WithUnit(90.0, 'deg'), WithUnit(-90.0, 'deg')]
        self.dv = cxn.data_vault
        
    def setup_data_vault(self):
        line_name = self.parameters.DriftTrackerRamsey.line_selection
        #navigate to the directory
        localtime = time.localtime()
        dirappend = [ time.strftime("%Y%b%d",localtime)]
        directory = ['','Experiments']
        directory.extend([self.name])
        directory.extend(dirappend)
        self.dv.cd(directory ,True)
        #try opening the existing dataset
        datasetname = 'RameyDriftTrack {}'.format(line_name)
        datasets_in_folder = self.dv.dir()[1]
        names = sorted([name for name in datasets_in_folder if datasetname in name])
        if names:
            #dataset with that name exist
            self.dv.open_appendable(names[0])
        else:
            #dataset doesn't already exist
            self.dv.new(datasetname,[('Time', 'Sec')],[('Excitation','Average','percent'),('Excitation','Deviation','percent')])
            window_name = ['Ramey Drift Track {0}'.format(self.parameters.DriftTrackerRamsey.line_selection)]
            self.dv.add_parameter('Window', window_name)
            self.dv.add_parameter('plotLive', True)

    def run(self, cxn, context):
        self.setup_data_vault()
        dt = self.parameters.DriftTrackerRamsey
        excitations = []
        frequency = cm.frequency_from_line_selection('auto', None , dt.line_selection, self.drift_tracker)
        frequency = frequency + dt.detuning
        for iter,phase in enumerate(self.phases):
            replace = TreeDict.fromdict({
                                           'Ramsey.first_pulse_duration':dt.pi_time / 2.0,
                                           'Ramsey.second_pulse_duration':dt.pi_time / 2.0,
                                           'Ramsey.ramsey_time':dt.gap_time,
                                           'Ramsey.second_pulse_phase':phase,
                                           'Excitation_729.rabi_excitation_amplitude':dt.amplitude,
                                           'Excitation_729.rabi_excitation_frequency':frequency,
                                           'Tomography.iteration':0.0,
                                           'StateReadout.repeat_each_measurement':dt.readouts,
                                           'SidebandCooling.sideband_cooling_enable':False,
                                           'OpticalPumping.optical_pumping_enable':dt.optical_pumping_enable_DT,
                                           })
            self.excitation.set_parameters(replace)
            self.update_progress(iter)
            if not self.parameters.StateReadout.use_camera_for_readout:
                #using PMT
                excitation_array, readout = self.excitation.run(cxn, context)
                excitation = excitation_array[0]
            else:
                primary_ion = int(self.parameters.StateReadout.camera_primary_ion)
                excitation_array, readout = self.excitation.run(cxn, context)
                excitation = excitation_array[primary_ion]
            excitations.append(excitation)
        print excitations
        detuning, average_excitation = self.calculate_detuning(excitations)
        corrected_frequency = frequency + detuning
#        print corrected_frequency, average_excitation
        return corrected_frequency,average_excitation
    
    def calculate_detuning(self, excitations):
        dt = self.parameters.DriftTrackerRamsey
        if not dt.optical_pumping_enable_DT:
            #if we are not doing optical pumping during drift tracking, then need to double the measured excitations
            excitations[0] = excitations[0]*2.0
            excitations[1] = excitations[1]*2.0
        average = (excitations[0] + excitations[1]) / 2.0
        deviation = (excitations[0] - excitations[1])
        detuning = arcsin(deviation) / (2.0 * pi * dt.gap_time['s'])
        detuning = WithUnit(detuning, 'Hz')
        self.dv.add([time.time(), average, deviation])
        return detuning, average
    
    def update_progress(self, iteration):
        progress = self.min_progress + (self.max_progress - self.min_progress) * float(iteration + 1.0) / len(self.phases)
        self.sc.script_set_progress(self.ident,  progress)
     
    def finalize(self, cxn, context):
        self.excitation.finalize(cxn, context)

if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = drift_tracker_ramsey_oneline(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)