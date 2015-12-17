from common.abstractdevices.script_scanner.scan_methods import experiment
from szx import szx
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.scriptLibrary import scan_methods
from lattice.scripts.experiments.Crystallization.crystallization import crystallization
import time
import labrad
from labrad.units import WithUnit
from numpy import linspace
from treedict import TreeDict

class szx_scan_time_phase(experiment):
    
    name = 'SZXScanTimePhase'
    
    required_parameters = [
        ('SZX_analysis', 'duration_scan')
        ]
    
    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.required_parameters)
        parameters = parameters.union(set(szx.all_required_parameters()))
        parameters = list(parameters)
        parameters.remove(('SZX', 'duration'))
        parameters.remove(('SZX', 'second_pulse_phase'))
        return parameters
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.excite = self.make_experiment(szx)
        self.excite.initialize(cxn, context, ident)
        if self.parameters.Crystallization.auto_crystallization:
            self.crystallizer = self.make_experiment(crystallization)
            self.crystallizer.initialize(cxn, context, ident)
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.dv = cxn.data_vault
        self.save_context = cxn.context()
        self.contrast_save_context = cxn.context()
        
    def setup_data_vault(self):
        localtime = time.localtime()
        datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        dirappend = [ time.strftime("%Y%b%d",localtime) ,time.strftime("%H%M_%S", localtime)]
        directory = ['','Experiments']
        directory.extend([self.name])
        directory.extend(dirappend)
        
        dependents = [('Excitation','Phase {}'.format(phase),'Probability') for phase in self.scan_phi]
        self.dv.new('{0} {1}'.format(self.name, datasetNameAppend),[('Excitation', 'us')], dependents , context = self.save_context)
        window_name = ['Dephasing, Scan Duration Phase']
        self.dv.add_parameter('Window', window_name, context = self.save_context)
        self.dv.add_parameter('plotLive', True, context = self.save_context)
        
        # context for saving the contrast
        dependents = [('Contrast','Contrast','Arb')]
        self.dv.new('{0} {1}'.format(self.name, contrastDatasetNameAppend),[('Excitation', 'us')], dependents , context = self.contrast_save_context)
        window_name = ['Dephasing, Contrast']
        self.dv.add_parameter('Window', window_name, context = self.contrast_save_context)
        self.dv.add_parameter('plotLive', True, context = self.contrast_save_context)
               
    
    
    