from common.abstractdevices.script_scanner.scan_methods import experiment
from Sideband_tracker import Sideband_tracker as sb
from labrad.units import WithUnit
from treedict import TreeDict
import numpy as np
import labrad

class sb_track_dual(experiment):
    name = 'SBTrackDual'
    
    required_parameters = []
    
    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.required_parameters)
        parameters = parameters.union(set(sb.all_required_parameters()))
        parameters = list(parameters)
        #removing parameters we'll be overwriting, and they do not need to be loaded
        parameters.remove(('Sideband_tracker','sideband_selection'))
        return parameters
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.drift_tracker = cxn.sd_tracker
        self.sb_tracker = self.make_experiment(sb)
        self.sb_tracker.initialize(cxn, context, ident)
        
    def run(self, cxn, context):
        replace = TreeDict.fromdict({
                                     'Sideband_tracker.sideband_selection':[1,0,0,0]
                                    })
        
        self.sb_tracker.set_parameters(replace)
        self.sb_tracker.set_progress_limits(0, 50.0)
        self.sb_tracker.run(cxn, context)

        replace = TreeDict.fromdict({
                                     'Sideband_tracker.sideband_selection':[0,1,0,0]
                                    })
        
        self.sb_tracker.set_parameters(replace)
        self.sb_tracker.set_progress_limits(50.0, 100.0)
        self.sb_tracker.run(cxn, context)
        
    def finalize(self, cxn, context):
        self.sb_tracker.finalize(cxn, context)
        
if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = sb_track_dual(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)