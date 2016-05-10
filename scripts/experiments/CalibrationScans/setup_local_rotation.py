from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.experiments.Experiments729.rabi_flopping import rabi_flopping as rf
from lattice.scripts.scriptLibrary import scan_methods
from lattice.scripts.scriptLibrary import dvParameters
from fitters import pi_time_fitter
from labrad.units import WithUnit
from treedict import TreeDict
import numpy as np
import labrad

class setup_local_rotation(experiment):
    
    name = 'SetupLocalRotation'

    required_parameters = [('LocalRotation', 'amplitude'),
                           ('MolmerSorensen', 'line_selection'),
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
        parameters.remove(('Excitation_729', 'channel_729'))
        return parameters

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.drift_tracker = cxn.sd_tracker
        self.rabi_flop = self.make_experiment(rf)
        self.rabi_flop.initialize(cxn, context, ident)
        self.fitter = pi_time_fitter()
        self.pv = cxn.parametervault
    
    def run(self, cxn, context):
        time_scan = [WithUnit(0, 'us'), WithUnit(50, 'us'), 60]
        
        ms = self.parameters.MolmerSorensen
        lr = self.parameters.LocalRotation
        replace = TreeDict.fromdict({
            'RabiFlopping.manual_scan':time_scan,
            'RabiFlopping.line_selection':ms.line_selection,
            'RabiFlopping.rabi_amplitude_729':lr.amplitude,
            'RabiFlopping.frequency_selection':'auto',
            'RabiFlopping.sideband_selection':[0,0,0,0],
            'Excitation_729.channel_729':'729local',
            })

        self.rabi_flop.set_parameters(replace)
        t, ex = self.rabi_flop.run(cxn, context)

        ex = ex.flatten()

        #print ex

        t_pi = self.fitter.fit(t, ex)
        t_pi = WithUnit(t_pi, 'us')
        
        self.pv.set_parameter('LocalRotation', 'pi_time', t_pi)
        print t_pi

    def finalize(self, cxn, context):
        #self.rabi_flop.finalize(cxn, context)
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = setup_local_rotation(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)

