from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.experiments.Experiments729.rabi_flop_scannable import rabi_flopping_scannable as rf
from lattice.scripts.scriptLibrary import scan_methods
from lattice.scripts.scriptLibrary import dvParameters
from labrad.units import WithUnit
from treedict import TreeDict
import numpy as np
import labrad

class align_729local(experiment):
    
    name = 'Align_729local'
    
    required_parameters = []

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
        self.rabi_flop.initialize(cxn, context, ident, report_all_ions=False)
        self.save_context = cxn.context()
        self.dv = cxn.data_vault
        self.cxnlab = labrad.connect('192.168.169.49') # connection to labwide network
        self.server = cxn.picomotorserver
    
    def run(self, cxn, context):
        
        axes = [1, 2]

        # mark the current location as the setpoint in case something goes horribly wrong
        self.server.mark_setpoint()

        scan_box = [-300, 300, 30]

        # initial starting points
        center_x = self.server.get_position(2)
        center_y = self.server.get_position(1)

        for k in range(0, n_passes):
            center_x = self.scan_axis(2, scan_box, center_x)
            center_y = self.scan_axis(1, scan_box, center_y)

    
    
