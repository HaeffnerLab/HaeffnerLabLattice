from common.abstractdevices.script_scanner.scan_methods import experiment
from ramsey_dephase_scan_second_pulse import ramsey_dephase_scan_second_pulse
from rabi_flopping import rabi_flopping
from labrad.units import WithUnit
import numpy as np
from treedict import TreeDict

class ramsey_dephase_complete_abridged(experiment):
    
    name = 'RamseyDephaseCompleteAbridged'
    required_parameters = [
                           ('RamseyDephase', 'scan_dephase_duration'),
                           ('RamseyDephase', 'scan_second_pulse'),
                           ('RamseyDephase', 'first_pulse_duration'),
                           ]

    required_parameters.extend(ramsey_dephase_scan_second_pulse.required_parameters)
    required_parameters.extend(rabi_flopping.required_parameters)
    required_parameters = list(set(required_parameters))
    #removing parameters we'll be overwriting, and they do not need to be loaded
    required_parameters.remove(('RamseyDephase','dephasing_duration'))
    required_parameters.remove(('RabiFlopping','manual_scan'))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.rabi = self.make_experiment(rabi_flopping)
        self.dephase = self.make_experiment(ramsey_dephase_scan_second_pulse)
        self.rabi.initialize(cxn, context, ident)
        self.dephase.initialize(cxn, context, ident)
        self.rabi_scan = None
        self.dephasing_scan = None
    
    def setup_sequence_parameters(self):
        #define the dephasing scan
        minim,maxim,steps = self.parameters.RamseyDephase.scan_dephase_duration
        minim = minim['us']; maxim = maxim['us']
        self.dephasing_scan = np.linspace(minim,maxim, steps)
        self.dephasing_scan = [WithUnit(pt, 'us') for pt in self.dephasing_scan]
        #define the rabi flop scan
        minim,maxim,steps = self.parameters.RamseyDephase.scan_second_pulse
        minim = minim['us']; maxim = maxim['us']
        rabi_minim = self.parameters.RamseyDephase.first_pulse_duration['us']
        rabi_maxim = maxim + self.parameters.RamseyDephase.first_pulse_duration['us']
        self.rabi.set_parameters(
                                 TreeDict.fromdict({'RabiFlopping.manual_scan':(WithUnit(rabi_minim, 'us'), WithUnit(rabi_maxim, 'us'), steps)})
                                 )
    
    def run(self, cxn, context):
        self.setup_sequence_parameters()
        total = len(self.dephasing_scan)
        for i,duration in enumerate(self.dephasing_scan):
            #rabi flop
            self.rabi.set_progress_limits(100.0 * i / total, 100.0 * (i + 0.5) / total)
            self.rabi.run(cxn, context)
            if self.rabi.should_stop: return
            #dephase
            self.dephase.set_parameters(TreeDict.fromdict({'RamseyDephase.dephasing_duration':duration}))
            self.dephase.set_progress_limits(100.0 * (i+ 0.5) / total, 100.0 * (i + 1.0) / total)
            self.dephase.run(cxn, context)
            if self.dephase.should_stop: return

if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = ramsey_dephase_complete_abridged(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)