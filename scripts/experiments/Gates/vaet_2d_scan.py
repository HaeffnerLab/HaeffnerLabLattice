from common.abstractdevices.script_scanner.scan_methods import experiment
from vaet_scan_delta import vaet_scan_delta as vaet
from lattice.scripts.scriptLibrary import scan_methods
from lattice.scripts.scriptLibrary import dvParameters
#from fitters import peak_fitter
from labrad.units import WithUnit
from treedict import TreeDict
import time
import numpy as np
import labrad

class vaet_2d_scan(experiment):

    name = 'VAET2DScan'

    required_parameters = [('VAET', 'duration_scan')]

    # parameters to overwrite
    remove_parameters = [
        ('VAET','duration')
        ]

        
        

    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.required_parameters)
        parameters = parameters.union(set(vaet.all_required_parameters()))
        parameters = list(parameters)
        for p in cls.remove_parameters:
            parameters.remove(p)
        return parameters
    
    
    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.drift_tracker = cxn.sd_tracker
        self.vaet = self.make_experiment(vaet)
        
        self.vaet.initialize(cxn, context, ident)
        self.pv = cxn.parametervault
        self.dds_cw = cxn.dds_cw

        
    def run(self, cxn, context):
                       
        self.scan = []

        mint,maxt,steps = self.parameters.VAET.duration_scan
        mint = mint['us']
        maxt = maxt['us']
        self.scan = np.linspace(mint, maxt, steps)

        ## randomize the times
        #np.random.shuffle(self.scan)

        self.scan = [WithUnit(pt, 'us') for pt in self.scan]

        prog1 = 0
        prog2 = 100.0/len(self.scan)

        for i,duration in enumerate(self.scan):
            print "VAET duration: " + str(duration)

            #should_stop = self.pause_or_stop()
            if self.should_stop: break

            replace = TreeDict.fromdict({
                'VAET.duration':duration
                })

            self.vaet.set_parameters(replace)
            self.vaet.set_progress_limits(prog1, prog2)
            prog1 += 100.0/len(self.scan)
            prog2 += 100.0/len(self.scan)
        
            self.vaet.run(cxn, context)
            


    def finalize(self, cxn, context):
        self.vaet.finalize(cxn, context)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = vaet_2d_scan(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
