from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.experiments.Experiments729.rabi_flop_scannable import rabi_flopping_scannable as rf
from lattice.scripts.scriptLibrary import scan_methods
from lattice.scripts.scriptLibrary import dvParameters
from labrad.units import WithUnit
from treedict import TreeDict
import numpy as np
import labrad
import time

class rabi_excitation_continuous(experiment):

    name = 'RabiExcContinuous'    
    required_parameters = [                                            
                           ]
    
    
    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.required_parameters)
        parameters = parameters.union(set(rf.all_required_parameters()))
        parameters = list(parameters)
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
        
        dv_args = {'output_size':self.rabi_flop.excite.output_size,
                   'experiment_name': self.name,
                   'window_name': 'RabiExcitationContinuous',
                   'dataset_name': 'rabi_excitation'
                   }
        scan_methods.setup_data_vault(cxn, self.save_context, dv_args)
        
        while True:
            should_stop = self.pause_or_stop()
            if should_stop: break
            excitation = self.rabi_flop.run(cxn, context)
            if excitation is None: break
            t = time.time()
            submission = [t]
            submission.extend([excitation])
            self.dv.add(submission, context = self.save_context)

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
    exprt = rabi_excitation_continuous(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)