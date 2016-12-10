# scan picomotor
from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.experiments.Experiments729.rabi_flop_scannable import rabi_flopping_scannable as rf
from lattice.scripts.scriptLibrary import scan_methods
from lattice.scripts.scriptLibrary import dvParameters
from labrad.units import WithUnit
from treedict import TreeDict
import numpy as np
import labrad
import time

class scan_beam_position(experiment):

    name = 'ScanBeamPosition'

    required_parameters = [
        ('CalibrationScans', 'position_scan_axis'),
        ('CalibrationScans', 'position_scan_num_steps'),
        ('CalibrationScans', 'position_scan_steps_per_move')
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
        self.rabi_flop.initialize(cxn, context, ident, report_all_ions=True)
        self.save_context = cxn.context()
        self.dv = cxn.data_vault
        self.cxnlab = labrad.connect('192.168.169.49', password='lab', tls_mode='off') #connection to labwide network

    def generate_scan(self):
        steps_per_move = int(self.parameters.CalibrationScans.position_scan_steps_per_move)
        n_steps = int(self.parameters.CalibrationScans.position_scan_num_steps)
        
        scan = np.arange(-n_steps, n_steps+1, steps_per_move)
        return scan, steps_per_move, n_steps

    def Moving_home(self,picomotor,i,steps_per_move,n_steps,axis):
        
        delta=int(i*steps_per_move)
        
        if delta < n_steps: steps_Home = n_steps-delta
        else: steps_Home = -(delta-n_steps)
                           
        picomotor.relative_move(axis,int(steps_Home)-209)
        print 'Moving home', steps_Home, 'number of steps'
        time.sleep(2)
        print picomotor.get_position(axis)
       

    def run(self, cxn, context):
        
        dv_args = {'output_size':self.rabi_flop.excite.output_size,
                   'experiment_name': self.name,
                   'window_name': 'current',
                   'dataset_name': 'beam_position_scan'
                   }
        scan_methods.setup_data_vault(cxn, self.save_context, dv_args)

        picomotor= self.cxn.picomotorserver
        #picomotor.mark_current_setpoint() # return point after the scan

       
        axis = int(self.parameters.CalibrationScans.position_scan_axis)
        self.scan, steps_per_move, n_steps = self.generate_scan()
                
        print 'Engine zero pos',picomotor.get_position(axis)


        # move all the way to the left side of the scan
        picomotor.relative_move(axis, -n_steps)
        time.sleep(20)
    
        print 'Engine is moving to the scan begin',picomotor.get_position(axis)
    
        for i,x in enumerate(self.scan):
            
            print 'iter' ,i,'Motor in pos: ', picomotor.get_position(axis)
                      
            excitation = self.rabi_flop.run(cxn, context)
            print excitation
            #if excitation is None:break 

            submission = [WithUnit(x*1.0, '')]
            if isinstance(excitation, np.ndarray):
                submission.extend(excitation)
            else:
                #submission.extend([excitation])
                submission.extend(excitation)
            print submission
            self.dv.add(submission, context = self.save_context)
            self.update_progress(i)

            picomotor.relative_move(axis, steps_per_move)
            time.sleep(2) # needed to allow time for communication with picomotor

            should_stop = self.pause_or_stop()
            if should_stop: break  
         

               
        print "Going back home"
        self.Moving_home(picomotor,i+1,steps_per_move,n_steps,axis)
        
        #picomotor.return_to_setpoint() # go back to where we were before scan
        #picomotor.relative_move(axis, +n_steps)
            
        time.sleep(2) # needed to allow time for communication with picomotor
        print 'Motor in pos: '
        print picomotor.get_position(axis)

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
    exprt = scan_beam_position(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
