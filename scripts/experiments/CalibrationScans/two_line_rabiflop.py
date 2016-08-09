from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.experiments.Experiments729.rabi_flop_scannable import rabi_flopping_scannable as rf
from lattice.scripts.scriptLibrary import scan_methods
from lattice.scripts.scriptLibrary import dvParameters
from labrad.units import WithUnit
from treedict import TreeDict
import numpy as np
import labrad

class two_line_rabi_flop(experiment):

    name = 'TwoLineRabiFlop'
    # parameters that are scanned need to be in the required_parameters 
    required_parameters = [('RabiFlopping', 'manual_scan')]
    
    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.required_parameters)
        parameters = parameters.union(set(rf.all_required_parameters()))
        parameters = list(parameters)
        #removing parameters we'll be overwriting, and they do not need to be loaded
        parameters.remove(('RabiFlopping_Sit','sit_on_excitation'))
        return parameters
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.drift_tracker = cxn.sd_tracker
        self.rabi_flop = self.make_experiment(rf)
        self.rabi_flop.initialize(cxn, context, ident)
        self.save_context = cxn.context()
        self.dv = cxn.data_vault
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        
    def run(self, cxn, context):
        
        dv_args = {'output_size':3,
                   'experiment_name': self.name,
                   'window_name': 'current',
                   'dataset_name': 'Two_Line_Rabi_Flop'
                   }
        scan_methods.setup_data_vault(cxn, self.save_context, dv_args)
        
        scan_param = self.parameters.RabiFlopping.manual_scan
        self.scan = scan_methods.simple_scan(scan_param, 'us')
        
        for i,duration in enumerate(self.scan):
            should_stop = self.pause_or_stop()
            if should_stop: break
            replace = TreeDict.fromdict({
                                     'RabiFlopping_Sit.sit_on_excitation':duration,
                                     'RabiFlopping.frequency_selection':'auto',
                                     'RabiFlopping.sideband_selection':[0,0,0,0],
                                     'RabiFlopping.line_selection':'S-1/2D-1/2'
                                    })
            self.rabi_flop.set_parameters(replace)
            excitation_delta_m0 = self.rabi_flop.run(cxn, context)
            if excitation_delta_m0 is None: break 

            replace = TreeDict.fromdict({
                                     'RabiFlopping_Sit.sit_on_excitation':duration,
                                     'RabiFlopping.frequency_selection':'auto',
                                     'RabiFlopping.sideband_selection':[0,0,0,0],
                                     'RabiFlopping.line_selection':'S-1/2D-3/2'
                                    })
            self.rabi_flop.set_parameters(replace)
            excitation_delta_m1 = self.rabi_flop.run(cxn, context)
            if excitation_delta_m1 is None: break 

            replace = TreeDict.fromdict({
                                     'RabiFlopping_Sit.sit_on_excitation':duration,
                                     'RabiFlopping.frequency_selection':'auto',
                                     'RabiFlopping.sideband_selection':[0,0,0,0],
                                     'RabiFlopping.line_selection':'S-1/2D-5/2'
                                    })
            self.rabi_flop.set_parameters(replace)
            excitation_delta_m2 = self.rabi_flop.run(cxn, context)
            if excitation_delta_m2 is None: break 

            submission = [duration['us']]
            submission.extend([excitation_delta_m0, excitation_delta_m1, excitation_delta_m2])
            
            self.dv.add(submission, context = self.save_context)
            self.update_progress(i)

    def finalize(self, cxn, context):
        self.save_parameters(self.dv, cxn, self.cxnlab, self.save_context)
        self.rabi_flop.finalize(cxn, context)

    def update_progress(self, iteration):
        progress = self.min_progress + (self.max_progress - self.min_progress) * float(iteration + 1.0) / len(self.scan)
        self.sc.script_set_progress(self.ident,  progress)

    def save_parameters(self, dv, cxn, cxnlab, context):
        measuredDict = dvParameters.measureParameters(cxn, cxnlab)
        dvParameters.saveParameters(dv, measuredDict, context)
        dvParameters.saveParameters(dv, dict(self.parameters), context)     

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = two_line_rabi_flop(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
