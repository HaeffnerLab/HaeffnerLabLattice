from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.experiments.Experiments729.rabi_flopping import rabi_flopping as rf
from lattice.scripts.scriptLibrary import scan_methods
from lattice.scripts.scriptLibrary import dvParameters
from fitters import pi_time_fitter
from labrad.units import WithUnit
from treedict import TreeDict
import numpy as np
import labrad

class setup_dt(experiment):

    name = 'SetupDT'
    
    required_parameters = [('DriftTracker', 'line_selection_1'),
                           ('DriftTracker', 'line_selection_2'),
                           ('DriftTrackerRamsey', 'line_1_amplitude'),
                           ('DriftTrackerRamsey', 'line_2_amplitude'),
                          ]

    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.required_parameters)
        parameters = parameters.union(set(rf.all_required_parameters()))
        parameters = list(parameters)

        parameters.remove(('RabiFlopping','manual_scan'))
        parameters.remove(('RabiFlopping', 'line_selection'))
        parameters.remove(('RabiFlopping', 'rabi_amplitude_729'))
        parameters.remove(('RabiFlopping', 'frequency_selection'))
        parameters.remove(('RabiFlopping', 'sideband_selection'))

        parameters.remove(('Tomography','iteration'))
        parameters.remove(('Tomography','rabi_pi_time'))
        parameters.remove(('Tomography','tomography_excitation_amplitude'))
        parameters.remove(('Tomography','tomography_excitation_frequency'))
        parameters.remove(('TrapFrequencies','axial_frequency'))
        parameters.remove(('TrapFrequencies','radial_frequency_1')),
        parameters.remove(('TrapFrequencies','radial_frequency_2')),
        parameters.remove(('TrapFrequencies','rf_drive_frequency')),
        #will be disabling sideband cooling automatically
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
        parameters.remove(('StatePreparation', 'optical_pumping_enable'))
        parameters.remove(('StatePreparation', 'sideband_cooling_enable'))
        return parameters

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.drift_tracker = cxn.sd_tracker
        self.rabi_flop = self.make_experiment(rf)
        self.rabi_flop.initialize(cxn, context, ident)
        self.fitter = pi_time_fitter()
        self.pv = cxn.parametervault
    
    def run(self, cxn, context):

        time_scan = [WithUnit(0, 'us'), WithUnit(40, 'us'), 40]
        #time_scan = [WithUnit(0, 'us'), WithUnit(25, 'us'), 10]
        
        dtr = self.parameters.DriftTrackerRamsey
        dt = self.parameters.DriftTracker

        replace = TreeDict.fromdict({
            'RabiFlopping.manual_scan':time_scan,
            'RabiFlopping.line_selection':dt.line_selection_1,
            'RabiFlopping.rabi_amplitude_729':dtr.line_1_amplitude,
            'RabiFlopping.frequency_selection':'auto',
            'RabiFlopping.sideband_selection':[0,0,0,0],
            'StatePreparation.sideband_cooling_enable':False,
            'StatePreparation.optical_pumping_enable':True
            })
        self.rabi_flop.set_parameters(replace)
        self.rabi_flop.set_progress_limits(0, 50.0)
        t, ex = self.rabi_flop.run(cxn, context)

        ex = ex.flatten()
        
        pi_time_1 = self.fitter.fit(t, ex)
        pi_time_1 = WithUnit(pi_time_1, 'us')

        self.pv.set_parameter('DriftTrackerRamsey', 'line_1_pi_time', pi_time_1)

        replace = TreeDict.fromdict({
            'RabiFlopping.manual_scan':time_scan,
            'RabiFlopping.line_selection':dt.line_selection_2,
            'RabiFlopping.rabi_amplitude_729':dtr.line_2_amplitude,
            'RabiFlopping.frequency_selection':'auto',
            'RabiFlopping.sideband_selection':[0,0,0,0],
            'StatePreparation.sideband_cooling_enable':False,
            'StatePreparation.optical_pumping_enable':True
            })
        self.rabi_flop.set_parameters(replace)
        self.rabi_flop.set_progress_limits(50.0, 100.0)
        t, ex = self.rabi_flop.run(cxn, context)

        ex = ex.flatten()

        pi_time_2 = self.fitter.fit(t, ex)
        pi_time_2 = WithUnit(pi_time_2, 'us')

        self.pv.set_parameter('DriftTrackerRamsey', 'line_2_pi_time', pi_time_2)

       
    def finalize(self, cxn, context):
        # this line raises an error
        #self.rabi_flop.finalize(cxn, context)
        pass
        
if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = setup_dt(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
