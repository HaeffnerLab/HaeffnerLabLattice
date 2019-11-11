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

class calibrate_temperature(experiment):

    name = 'CalibTemperature'

    required_parameters = [('DriftTracker', 'line_selection_1'),
                           ('DriftTracker', 'line_selection_2'),
                           ('CalibrationScans', 'do_rabi_flop_carrier'),
                           ('CalibrationScans', 'do_rabi_flop_radial1'),
                           ('CalibrationScans', 'do_rabi_flop_radial2'),
                           ('CalibrationScans', 'carrier_time_scan'),
                           ('CalibrationScans', 'radial1_time_scan'),
                           ('CalibrationScans', 'radial2_time_scan'),
                           ('CalibrationScans', 'carrier_excitation_power'),
                           ('CalibrationScans', 'radial1_excitation_power'),
                           ('CalibrationScans', 'radial2_excitation_power')
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
        self.rabi_flopping.initialize(cxn, context, ident)

        self.pv = cxn.parametervault
        self.dds_cw = cxn.dds_cw

        
        
    def run(self, cxn, context):

        dt = self.parameters.DriftTracker
        
        # save original state of DDS 5
        dds5_state = self.dds_cw.output('5')

        self.dds_cw.output('5', True)
        time.sleep(1)

        # general parameters
        replace = TreeDict.fromdict({
               'Display.relative_frequencies':False,
               'StateReadout.repeat_each_measurement':100,
               'StateReadout.use_camera_for_readout':False,
               'Excitation_729.bichro':False,
               'Excitation_729.channel_729':'729local',               
               'Documentation.sequence':'calibrate_temperature',
               'Heating.background_heating_time': self.parameters.Heating.background_heating_time
               })

        ### RUN THE CARRIER        
        if self.parameters.CalibrationScans.do_rabi_flop_carrier:
 
           print "Doing carrier flop ..."

           carr_dict = TreeDict.fromdict({
               'RabiFlopping.rabi_amplitude_729':self.parameters.CalibrationScans.carrier_excitation_power,
               'RabiFlopping.manual_scan':self.parameters.CalibrationScans.carrier_time_scan,
               'RabiFlopping.sideband_selection':[0,0,0,0],
               'Documentation.scan_type':'carrier_flop'
               })

           carr_dict.update(replace)

           self.rabi_flopping.set_parameters(carr_dict)
           self.rabi_flopping.set_progress_limits(0, 33.0)
              
           fr, ex = self.rabi_flopping.run(cxn, context)

           self.rabi_flopping.finalize(cxn, context)


        #### RUN THE RADIAL1 BLUE SIDEBAND
        if self.parameters.CalibrationScans.do_rabi_flop_radial1:   
           
           print "Doing radial1 flop ..."

           carr_dict = TreeDict.fromdict({
               'RabiFlopping.rabi_amplitude_729':self.parameters.CalibrationScans.radial1_excitation_power,
               'RabiFlopping.manual_scan':self.parameters.CalibrationScans.radial1_time_scan,
               'RabiFlopping.sideband_selection':[+1,0,0,0],
               'Documentation.scan_type':'radial1_flop'
               })

           carr_dict.update(replace)

           self.rabi_flopping.set_parameters(carr_dict)
           self.rabi_flopping.set_progress_limits(33.0, 66.0)
   
           fr, ex = self.rabi_flopping.run(cxn, context)
           
           self.rabi_flopping.finalize(cxn, context)
 
        #### RUN THE RADIAL2 BLUE SIDEBAND
        if self.parameters.CalibrationScans.do_rabi_flop_radial2:   

           print "Doing radial2 flop ..."

           carr_dict = TreeDict.fromdict({
               'RabiFlopping.rabi_amplitude_729':self.parameters.CalibrationScans.radial2_excitation_power,
               'RabiFlopping.manual_scan':self.parameters.CalibrationScans.radial2_time_scan,
               'RabiFlopping.sideband_selection':[0,+1,0,0],
               'Documentation.scan_type':'radial2_flop'
               })

           carr_dict.update(replace)

           self.rabi_flopping.set_parameters(carr_dict)
           self.rabi_flopping.set_progress_limits(66.0, 100.0)
   
           fr, ex = self.rabi_flopping.run(cxn, context)

           self.rabi_flopping.finalize(cxn, context)
      
        # resetting DDS5 state
        time.sleep(1)
        #self.dds_cw.output('5', False)
        self.dds_cw.output('5', dds5_state)
        time.sleep(1)

    def finalize(self, cxn, context):
        #self.rabi_flopping.finalize(cxn, context)
        pass

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = calibrate_temperature(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
