# motional ramsey experiment on one radial mode

from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.experiments.Experiments729.rabi_flop_scannable import rabi_flopping_scannable as rf
from lattice.scripts.scriptLibrary.devices import agilent
from lattice.scripts.scriptLibrary import scan_methods
from lattice.scripts.scriptLibrary import dvParameters
from labrad.units import WithUnit
from treedict import TreeDict
import numpy as np
import time
import labrad

class motional_ramsey_oneline(experiment):

    name = 'MotionalRamseyOneLine'

    required_parameters = [                           
                           ('Motion_Analysis','sideband_selection'),
                           ('Motion_Analysis','excitation_enable'),
                           ]

    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.required_parameters)
        parameters = parameters.union(set(rf.all_required_parameters()))
        parameters = list(parameters)
        return parameters

    def initialize(self, cxn, context, ident):
        self.ident = ident

        self.rabi_flop = self.make_experiment(rf)
        self.rabi_flop.initialize(cxn, context, ident)
        self.save_context = cxn.context()
        self.dv = cxn.data_vault
        self.pv = cxn.parametervault

        self.agi = agilent(cxn)

    def run(self, cxn, context):

        mode = self.parameters.Motion_Analysis.sideband_selection

        detuning = self.parameters.Motion_Analysis.detuning

        d0 = 2*np.pi*detuning['Hz']
        t = np.pi/d0
        t = WithUnit(t, 's')

        readout_duration = self.parameters.Motion_Analysis.readout_duration

        if mode == 'radial_frequency_1':
            readout_mode = [-1, 0, 0, 0]
            window = 'radial1'
        if mode = 'radial_frequency_2':
            readout_mode = [0, -1, 0, 0]
            window = 'radial2'

        dv_args = {
            'name':self.name,
            'dataset_name': 'motional_ramsey_' + window,
            'independents': ['time [s]'],
            'dependents': ['frequency (frequency) [MHz]' ]
            }

        scan_methods.setup_data_vault_appendable(cxn, self.save_context, dv_args)


        if mode == 'radial_frequency_2': readout_mode = [0, -1, 0, 0]

        replace = TreeDict.fromdict({
                'Motion_Analysis.excitation_enable':True,
                'Motion_Analysis.ramsey_time':t,
                'RabiFlopping.sideband_selection': readout_mode,
                'RabiFlopping_Sit.sit_on_excitation': readout_duration,
                'StateReadout.use_camera_for_readout':False,
                })

        self.rabi_flop.set_parameters(replace)

        # run on resonance
        f = self.parameters['TrapFrequencies.' + mode]
        self.agi.set_frequency(f)
        p1 = self.rabi_flop.run(cxn, context)

        # run with detuning
        f = self.parameters['TrapFrequencies.' + mode]
        f = f + detuning
        self.agi.set_frequency(f)
        p2 = self.rabi_flop.run(cxn, context)
        error = self.compute_error(p1, p2, t)

        f = self.parameters['TrapFrequencies.' + mode] + error
        self.pv.set_parameter('TrapFrequencies', mode, f)

        self.dv.add([time.time(), error['kHz'] ])
        return error

    def compute_error(self, p1, p2, t):
        error = np.arcsin( (p1 - p2)/(p1 + p2) ) / (2 * np.pi * t)
        # this is error in Hz
        error = error/1e3 # now  in kHz
        error = WithUnit(error, 'kHz')
        return error

    def finalize(self, cxn, context):
        self.rabi_flop.finalize(cxn, context)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = motional_ramsey_oneline(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
