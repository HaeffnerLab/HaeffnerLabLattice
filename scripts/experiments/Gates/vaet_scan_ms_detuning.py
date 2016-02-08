from common.abstractdevices.script_scanner.scan_methods import experiment
from vaet import vaet_base
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.scriptLibrary import scan_methods
from lattice.scripts.experiments.Crystallization.crystallization import crystallization
import time
import labrad
from labrad.units import WithUnit
from numpy import linspace
from treedict import TreeDict

class vaet_scan_ms_detuning(experiment):

    name = 'VAETScanMSDet'
    
    required_parameters = [
        ('MolmerSorensen', 'detuning_scan')
        ]

    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.required_parameters)
        parameters = parameters.union(set(vaet_base.all_required_parameters()))
        parameters = list(parameters)
        parameters.remove(('MolmerSorensen', 'detuning'))
        return parameters

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.excite = self.make_experiment(vaet_base)
        self.excite.initialize(cxn, context, ident)
        if self.parameters.Crystallization.auto_crystallization:
            self.crystallizer = self.make_experiment(crystallization)
            self.crystallizer.initialize(cxn, context, ident)
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.dv = cxn.data_vault
        self.dds_cw = cxn.dds_cw
        self.save_context = cxn.context()
        try:
            self.grapher = cxn.grapher
        except: self.grapher = None

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
        ds = self.dv.new('VAET Scan Time {}'.format(datasetNameAppend),[('Excitation', 'us')], dependents , context = self.save_context)
        self.dv.add_parameter('Window', ['VAET-MS-DET'], context = self.save_context)
        self.dv.add_parameter('plotLive', True, context = self.save_context)

        if self.grapher is not None:
            self.grapher.plot_with_axis(directory, datasetNameAppend, 'vaet_ms_det', self.scan, ds[1])
    
    def run(self, cxn, context):

        scan = scan_methods.simple_scan(self.parameters.MolmerSorensen.detuning_scan, 'kHz')
        self.scan = scan

        self.setup_data_vault()
        for i, freq in enumerate(scan):
            should_stop = self.pause_or_stop()
            if should_stop: break
            replace = TreeDict.fromdict({
                'MolmerSorensen.detuning':freq
                })
            self.excite.set_parameters(replace)
            states = self.excite.run(cxn, context)
            if states is None: break
            submission = [freq['kHz']]
            submission.extend(states)
            self.dv.add(submission, context = self.save_context)
            self.update_progress(i)

    def finalize(self, cxn, context):
        self.save_parameters(self.dv, cxn, self.cxnlab, self.save_context)
        self.dds_cw.output('5', True)
        self.excite.finalize(cxn, context)

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
    exprt = vaet_scan_ms_detuning(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)

