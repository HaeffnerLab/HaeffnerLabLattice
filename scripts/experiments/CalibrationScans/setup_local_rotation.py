from common.abstractdevices.script_scanner.scan_methods import experiment
#from lattice.scripts.experiments.Experiments729.rabi_flopping import rabi_flopping as rf
from lattice.scripts.experiments.Gates.ms import ms
from lattice.scripts.scriptLibrary import scan_methods
from lattice.scripts.scriptLibrary import dvParameters
from fitters import pi_time_fitter
from labrad.units import WithUnit
from treedict import TreeDict
import time
import numpy as np
import labrad

class setup_local_rotation(experiment):
    """ Run a MS interaction turning off the
        actual gate. Vary only the local rotation
        time.
        Automatically enable the SDDS_enable to rotate the qubit
        and disable the SDDS_rotate_out to not do a second pulse
    """
    
    name = 'SetupLocalRotation'

    required_parameters = [('LocalRotation', 'amplitude'),
                           ('MolmerSorensen', 'line_selection'),
                           ]
    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.required_parameters)
        parameters = parameters.union(set(ms.all_required_parameters()))
        parameters = list(parameters)

        parameters.remove(('LocalRotation','pi_time'))
        parameters.remove(('MolmerSorensen','amplitude'))
        parameters.remove(('MolmerSorensen','analysis_pulse_enable'))
        parameters.remove(('LocalStarkShift', 'enable'))
        parameters.remove(('MolmerSorensen', 'SDDS_enable'))
        parameters.remove(('MolmerSorensen', 'SDDS_rotate_out'))
        return parameters

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.drift_tracker = cxn.sd_tracker
        self.ms = self.make_experiment(ms)
        self.ms.initialize(cxn, context, ident)
        self.fitter = pi_time_fitter()
        self.pv = cxn.parametervault
        self.save_context = cxn.context()
        
    def setup_data_vault(self):
        localtime = time.localtime()
        datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        dirappend = [ time.strftime("%Y%b%d",localtime) ,time.strftime("%H%M_%S", localtime)]
        directory = ['','Experiments']
        directory.extend([self.name])
        directory.extend(dirappend)
        self.dv.cd(directory ,True, context = self.save_context)
        if not self.parameters.StateReadout.use_camera_for_readout:
            dependents = [('NumberExcited',st,'Probability') for st in ['0', '1', '2'] ]
        else:
            dependents = [('State', st, 'Probability') for st in ['SS', 'SD', 'DS', 'DD']]
        ds = self.dv.new('MS Gate {}'.format(datasetNameAppend),[('Excitation', 'us')], dependents , context = self.save_context)
        if self.grapher is not None:
            self.grapher.plot_with_axis(ds, 'rabi', self.scan)
    
    def run(self, cxn, context):
        self.scan = [WithUnit(0, 'us'), WithUnit(50, 'us'), 60]
        
        use_cam = self.parameters.StateReadout.use_camera_for_readout
        
        t_list = []
        ex_list = []
        
        for t in self.scan:
            
            replace = TreeDict.fromdict({'LocalRotation.pi_time':t,
                                         'MolmerSorensen.amplitude':WithUnit(-63, 'dBm'),
                                         'MolmerSorensen.analysis_pulse_enable':False,
                                         'MolmerSorensen.SDDS_enable':True,
                                         'MolmerSorensen.SDDS_rotate_out':False,
                                         'LocalStarkShift.enable':False
                                         })
            self.ms.set_parameters(replace)
            ex = self.ms.run(cxn, context)
            submission = [t['us']]
            submission.extend(ex)
            self.dv.add(submission, context = self.save_context)
            
            t_list.append(t['us'])
            if use_cam: # DS state
                ex_list.append(ex[2])
            else: # 1 ion dark state
                ex_list.append(ex[1])

        t_list = np.array(t_list)
        ex_list = np.array(ex_list)

        #print ex

        t_pi = self.fitter.fit(t_list, ex_list)
        t_pi = WithUnit(t_pi, 'us')
        
        self.pv.set_parameter('LocalRotation', 'pi_time', t_pi)
        print t_pi

    def finalize(self, cxn, context):
        self.ms.finalize(cxn, context)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = setup_local_rotation(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)

