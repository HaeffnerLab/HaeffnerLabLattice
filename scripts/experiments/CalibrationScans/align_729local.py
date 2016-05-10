from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.experiments.Experiments729.rabi_flop_scannable import rabi_flopping_scannable as rf
from lattice.scripts.scriptLibrary import scan_methods
from lattice.scripts.scriptLibrary import dvParameters
from labrad.units import WithUnit
from treedict import TreeDict
import numpy as np
import labrad
import time

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

    def walk_axis(self, axis, step_size):
        '''
        First compute the excitation at the current point.
        Then walk in some direction (say positive) and see if the excitation
        gets higher or lower.
        If higher, keep walking until the change smaller than some threshold
        '''

        ts = 1 # delay time to allow stage to move
        threshold = 0.1 # relative change in excitation to trigger a 
                        # termination of the walk
        p0 = self.rabi_flop.run(cxn, context)
        
        p = p0
        below_threshold = lambda p, p1: (p - p1)/p1 < -threshold
        above_threshold = lambda p, p1: (p - p1)/p1 >= threshold

        terminate = False
        while not ( below_threshold(p, p0) )
            '''
            Keep going as long as the excitation doesn't fall below
            the initial one by more than some threshold
            '''
            should_stop = self.pause_or_stop
            if should_stop: break
            self.server.move_relative(axis, step_size)
            time.sleep(ts)
            p = self.rabi_flop.run(cxn, context)

            if ( above_threshold(p, p0) ):
                # keep running, but don't reverse course once we fall out of the loop
                terminate = True

        p0 = p # reset to the last point
        while (not terminate) and (not below_threshold(p, p0)):
            '''
            We've fallen out of the above while loop without ever making the signal better,
            so now we try the other direction
            '''
            should_stop = self.pause_or_stop:
            if should_stop: break
            self.server.move_relative(axis, step_size)
            time.sleep(ts)
            p = self.rabi_flop.run(cxn, context)
    
    def run(self, cxn, context):
        
        axes = [1, 2]

        # mark the current location as the setpoint in case something goes horribly wrong
        self.server.mark_setpoint()

        step_size = 50

        # initial starting points
        center_x = self.server.get_position(2)
        center_y = self.server.get_position(1)

        for k in range(0, n_passes):
            center_x = self.scan_axis(2, scan_box, center_x)
            center_y = self.scan_axis(1, scan_box, center_y)

    
    
