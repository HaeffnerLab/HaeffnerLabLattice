from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.experiments.Experiments729.rabi_flopping import rabi_flopping
from lattice.scripts.scriptLibrary import scan_methods
from lattice.scripts.scriptLibrary import dvParameters
from fitters import peak_fitter
from labrad.units import WithUnit
from treedict import TreeDict
import time
import numpy as np
import labrad

from lattice.scripts.sciptLibrary import singlepass

class calibrate_sigmaz(experiment):

    name = 'CalibSigmaz'

    required_parameters = [('DriftTracker', 'line_selection_1'),
                           ('DriftTracker', 'line_selection_2'),
                           ('CalibrationScans', 'sigmaz_time_scan'),
                           ('CalibrationScans', 'sigmaz_excitation_power')
                           ('CalibrationScans', 'sigmaz_sideband_selection')
                           ('CalibrationScans', 'sigmaz_on_radial2')
                           ]

    # parameters to overwrite
    remove_parameters = [
        ('RabiFlopping', 'line_selection'),
        ('RabiFlopping', 'sideband_selection'),
        ('RabiFlopping', 'rabi_amplitude_729'),
        ('RabiFlopping', 'manual_scan'),

        ('StateReadout', 'repeat_each_measurement'),
        ('StateReadout', 'use_camera_for_readout'),
        
        ('Excitation_729', 'bichro'),
        ('Excitation_729', 'channel_729')]

        
        

    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.required_parameters)
        parameters = parameters.union(set(rabi_flopping.all_required_parameters()))
        parameters = list(parameters)
        for p in cls.remove_parameters:
            parameters.remove(p)
        return parameters
    
    
    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.drift_tracker = cxn.sd_tracker
        self.rabi_flopping = self.make_experiment(rabi_flopping)
        
        #self.rabi_flopping.initialize(cxn, context, ident, use_camera_override = False)
        self.rabi_flopping.initialize(cxn, context, ident)

        self.pv = cxn.parametervault
        self.dds_cw = cxn.dds_cw

        
    def run(self, cxn, context):
        
        dt = self.parameters.DriftTracker
        
        # general parameters
        replace = TreeDict.fromdict({
               'Display.relative_frequencies':False,
               'StateReadout.repeat_each_measurement':100,
               'StateReadout.use_camera_for_readout':False,
               'Excitation_729.bichro':False,
               'Excitation_729.channel_729':'729local'})

        ### SET THE AXIAL FREQUENCY TO HALF THE RADIAL TRAP FREQUENCY
        ### AND RUN A RABIFLOP

        radial1_freq = self.pv.get_parameter('TrapFrequencies', 'radial_frequency_1').value
        radial2_freq = self.pv.get_parameter('TrapFrequencies', 'radial_frequency_2').value

        if self.parameters.CalibrationScans.sigmaz_on_radial2:
            self.pv.set_parameter('TrapFrequencies', 'axial_frequency', WithUnit(radial2_freq/2.0,'MHz'))

            my_dict = {
                    'bichro_shift' : WithUnit(radial2_freq/2.0, 'MHz'), 
                    'ac_stark_shift' : WithUnit(0.0, 'MHz'),
                    'detuning' : WithUnit(0.0, 'MHz'),
                    'amp_red' : self.parameter.SZX.amp_red,
                    'amp_blue' : self.parameter.SZX.amp_blue
                    }
        else
            self.pv.set_parameter('TrapFrequencies', 'axial_frequency', WithUnit(radial1_freq/2.0,'MHz'))

            my_dict = {
                    'bichro_shift' : WithUnit(radial1_freq/2.0, 'MHz'), 
                    'ac_stark_shift' : WithUnit(0.0, 'MHz'),
                    'detuning' : WithUnit(0.0, 'MHz'),
                    'amp_red' : self.parameter.SZX.amp_red,
                    'amp_blue' : self.parameter.SZX.amp_blue
                    }

        # setting single pass AOMs
        single_pass.setup_sp_local(self.dds_cw, my_dict)

        # Switch bichros on
        bichro_setting = self.pv.get_parameter('Excitation_729', 'bichro')
        self.pv.set_parameter('Excitation_729', 'bichro', True)
        
        carr_dict = TreeDict.fromdict({
            'RabiFlopping.rabi_amplitude_729':self.parameters.CalibrationScans.sigmaz_excitation_power,
            'RabiFlopping.manual_scan':self.parameters.CalibrationScans.sigmaz_time_scan,
            'RabiFlopping.sideband_selection':self.parameters.CalibrationScans.sigmaz_sideband_selection,
            })
      
        carr_dict.update(replace)
      
        self.rabi_flopping.set_parameters(carr_dict)
        self.rabi_flopping.set_progress_limits(0, 100.0)
        
        fr, ex = self.rabi_flopping.run(cxn, context)

        # Switch bichros to original state
        self.pv.set_parameter('Excitation_729', 'bichro', bichro_setting)

   
    def finalize(self, cxn, context):
        self.rabi_flopping.finalize(cxn, context)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = calibrate_temperature(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
