from common.abstractdevices.script_scanner.scan_methods import experiment
from excitations import excitation_rabi_2ions
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.scriptLibrary import dvParameters
from rabi_power_flopping_2ions import Rabi_power_flopping_2ions
import numpy as np
import time
import labrad
from labrad.units import WithUnit

class Parity_LLI_rabi_power_fitter(experiment):
    
    name = 'Parity_LLI_rabi_power_fitter'
    Parity_LLI_rabi_power_fitter_required_parameters = [
                           ('Parity_LLI_rabi_power_fitter','auto_fit'),
                           ('Parity_LLI_rabi_power_fitter','enable_feedback'),
                           ('Parity_LLI_rabi_power_fitter','sensitivity'),
                           ]
    
    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.Parity_LLI_rabi_power_fitter_required_parameters)
        parameters = parameters.union(set(Rabi_power_flopping_2ions.all_required_parameters()))
        return parameters
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.power_flop = self.make_experiment(Rabi_power_flopping_2ions)
    
    def run(self, cxn, context):
        ## calculate scan range ##
        span, resolution, duration, amplitude = sp['sensitivity']
        
        replace_left_ion_m12m12 = TreeDict.fromdict({
                                       'RabiPowerFlopping_2ions.block_ion1_729':False,
                                       'RabiPowerFlopping_2ions.block_ion2_729':True,
                                       'RabiPowerFlopping_2ions.ion1_line_selection':'S-1/2D-1/2',
                                       'OpticalPumping.line_selection':'S+1/2D-3/2',
                                       'OpticalPumpingAux.aux_op_line_selection':'S-1/2D+3/2',
                                       })
        
    

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = Parity_LLI_rabi_power_fitter(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)