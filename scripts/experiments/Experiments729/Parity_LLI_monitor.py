from common.abstractdevices.script_scanner.scan_methods import experiment
from Parity_LLI_phase_tracker import Parity_LLI_phase_tracker
import time
import labrad
import numpy as np
from treedict import TreeDict
class Parity_LLI_monitor(experiment):
    
    name = 'Parity_LLI_monitor'

    @classmethod
    def all_required_parameters(cls):
        parameters = set([])
        parameters = parameters.union(set(Parity_LLI_phase_tracker.all_required_parameters()))
        parameters = list(parameters)
        #removing parameters we'll be overwriting, and they do not need to be loade
        parameters.remove(('Parity_LLI','mirror_state'))
        return parameters
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.parity_LLI = self.make_experiment(Parity_LLI_phase_tracker)
        self.parity_LLI.initialize(cxn, context, ident)  
        self.dv = cxn.data_vault
        self.save_data = cxn.context()
        self.setup_data_vault()
        
    def run(self, cxn, context):
        replace_no_mirror = TreeDict.fromdict({
                                       'Parity_LLI.mirror_state':False,
                                       'Parity_LLI.use_short_ramsey_time':False,
                                       })
        replace_mirror = TreeDict.fromdict({
                                       'Parity_LLI.mirror_state':True,
                                       'Parity_LLI.use_short_ramsey_time':False,
                                       })
        random_number = np.random.rand()
        
        if (random_number>0.5):
            self.parity_LLI.set_parameters(replace_no_mirror)
            phase_no_mirror = self.parity_LLI.run(cxn, context)
            self.parity_LLI.set_parameters(replace_mirror)
            phase_mirror = self.parity_LLI.run(cxn, context)
        else:
            self.parity_LLI.set_parameters(replace_mirror)
            phase_mirror = self.parity_LLI.run(cxn, context)            
            self.parity_LLI.set_parameters(replace_no_mirror)
            phase_no_mirror = self.parity_LLI.run(cxn, context)  
                  
        average_phase = (phase_no_mirror+phase_mirror)/2.0
        difference_phase = (phase_no_mirror-phase_mirror)/2.0
        submission = [time.time(),phase_mirror['deg'],phase_no_mirror['deg'],average_phase['deg'],difference_phase['deg']]
        self.dv.add(submission,context=self.save_data)

    def setup_data_vault(self):
        localtime = time.localtime()
        ### save result fot long term tracking ###
        directory_LLI = ['','Drift_Tracking','LLI_tracking']
        directory_LLI.append(time.strftime("%Y%b%d",localtime))
        ### save parity###
        self.dv.cd(directory_LLI ,True, context = self.save_data)
        datasetname_parity = 'LLI_data_new'
        dataset_parity_in_folder = self.dv.dir(context= self.save_data)[1]
        names = sorted([name for name in dataset_parity_in_folder if datasetname_parity in name])
        if names:
            #dataset with that name exist
            self.dv.open_appendable(names[0],context=self.save_data)
        else:
            #dataset doesn't already exist
            self.dv.new(datasetname_parity,[('Time', 'Sec')],[('Parity','Mirror','Probability'),('Parity','No Mirror','Probability'),('Parity','Average','Probability'),('Parity','Difference','Probability')],context=self.save_data)
            window_name = [datasetname_parity]
            self.dv.add_parameter('Window', window_name,context=self.save_data)
            self.dv.add_parameter('plotLive', True,context=self.save_data) 
            
    def finalize(self, cxn, context):
        #self.save_parameters(self.dv, cxn, self.cxnlab, self.save_parity)
        self.parity_LLI.finalize(cxn, context)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = Parity_LLI_monitor(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)