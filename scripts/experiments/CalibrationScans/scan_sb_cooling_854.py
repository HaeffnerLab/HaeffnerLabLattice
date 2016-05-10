from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.experiments.Experiments729.rabi_flop_scannable import rabi_flopping_scannable as rf
from lattice.scripts.scriptLibrary import scan_methods
from lattice.scripts.scriptLibrary import dvParameters
from labrad.units import WithUnit
from treedict import TreeDict
import numpy as np
import labrad

class scan_sb_cooling_854(experiment):

    name = 'ScanSBC_854'
    required_parameters = [('CalibrationScans', 'sbc_854_scan')]
    
    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.required_parameters)
        parameters = parameters.union(set(rf.all_required_parameters()))
        parameters = list(parameters)
        #removing parameters we'll be overwriting, and they do not need to be loaded
        parameters.remove(('SidebandCooling','sideband_cooling_amplitude_854'))
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
                   'window_name': 'current',
                   'dataset_name': '854_scan'
                   }
        scan_methods.setup_data_vault(cxn, self.save_context, dv_args)
        
        scan_param = self.parameters.CalibrationScans.sbc_854_scan
        self.scan = scan_methods.simple_scan(scan_param, 'dBm')
        
        for i,ampl in enumerate(self.scan):
            should_stop = self.pause_or_stop()
            if should_stop: break
            replace = TreeDict.fromdict({
                                     'SidebandCooling.sideband_cooling_amplitude_854':ampl
                                    })
            self.rabi_flop.set_parameters(replace)
            excitation = self.rabi_flop.run(cxn, context)
            if excitation is None: break 
            submission = [ampl['dBm']]
            submission.extend([excitation])
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
    exprt = scan_sb_cooling_854(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
