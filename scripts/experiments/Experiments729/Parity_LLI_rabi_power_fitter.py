from common.abstractdevices.script_scanner.scan_methods import experiment
from rabi_power_flopping_2ions import Rabi_power_flopping_2ions
import numpy as np
import labrad
from treedict import TreeDict
from labrad.units import WithUnit

class Parity_LLI_rabi_power_fitter(experiment):
    
    name = 'Parity_LLI_rabi_power_fitter'
    required_parameters = [
                           ('Parity_LLI_rabi_power_fitter','enable_feedback'),
                           ('Parity_LLI_rabi_power_fitter','resolution'),
                           ('Parity_LLI_rabi_power_fitter','power_scan_span'),
                           ('Parity_transitions','left_ionSm12Dm12_power'),
                           ('Parity_transitions','left_ionSm12Dm52_power'),
                           ('Parity_transitions','left_ionSp12Dp12_power'),
                           ('Parity_transitions','left_ionSp12Dp52_power'),
                           ('Parity_transitions','right_ionSm12Dm12_power'),
                           ('Parity_transitions','right_ionSm12Dm52_power'),
                           ('Parity_transitions','right_ionSp12Dp12_power'),
                           ('Parity_transitions','right_ionSp12Dp52_power'),
                           ('DriftTrackerRamsey','line_1_amplitude'),
                           ('DriftTrackerRamsey','line_2_amplitude'),
                           ]
    
    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.required_parameters)
        parameters = parameters.union(set(Rabi_power_flopping_2ions.all_required_parameters()))
        parameters = list(parameters)
        parameters.remove(('RabiPowerFlopping_2ions','block_ion1_729'))
        parameters.remove(('RabiPowerFlopping_2ions','block_ion2_729'))
        parameters.remove(('RabiPowerFlopping_2ions','ion1_line_selection'))
        parameters.remove(('RabiPowerFlopping_2ions','ion2_line_selection'))
        parameters.remove(('OpticalPumping','line_selection'))
        parameters.remove(('OpticalPumpingAux','aux_op_line_selection'))
        parameters.remove(('RabiPowerFlopping_2ions','manual_power_scan'))
        parameters.remove(('Rabi_excitation_729_2ions','use_primary_dds'))
        return parameters
    
    def initialize(self, cxn, context, ident):
        
        self.ident = ident
        #self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.power_flop = self.make_experiment(Rabi_power_flopping_2ions)
        self.power_flop.initialize(cxn, context, ident)
        self.enable_feedback = self.parameters['Parity_LLI_rabi_power_fitter.enable_feedback']
        self.pv = cxn.parametervault
        self.span = self.parameters['Parity_LLI_rabi_power_fitter.power_scan_span']
        self.resolution = self.parameters['Parity_LLI_rabi_power_fitter.resolution']
        self.steps = int(self.span / self.resolution)
        
    
    def run(self, cxn, context):
        self.run_left_ion_m12m12(cxn, context)
        self.run_left_ion_m12m52(cxn, context)
        self.run_left_ion_p12p12(cxn, context)
        self.run_left_ion_p12p52(cxn, context)
        self.run_right_ion_m12m12(cxn, context)
        self.run_right_ion_m12m52(cxn, context)
        self.run_right_ion_p12p12(cxn, context)
        self.run_right_ion_p12p52(cxn, context)
        self.run_left_ion_m12m52_drift_track(cxn, context)
        self.run_left_ion_p12m32_drift_track(cxn, context)

    def run_left_ion_m12m52_drift_track(self,cxn, context): 
        center_power = self.parameters['DriftTrackerRamsey.line_1_amplitude']
        minim = center_power - self.span/2.0
        maxim = center_power + self.span/2.0
        scan = [minim,maxim,self.steps]
        replace = TreeDict.fromdict({
                                       'Rabi_excitation_729_2ions.use_primary_dds':True,
                                       'RabiPowerFlopping_2ions.block_ion1_729':False,
                                       'RabiPowerFlopping_2ions.block_ion2_729':True,
                                       'RabiPowerFlopping_2ions.ion1_line_selection':'S-1/2D-5/2',
                                       'RabiPowerFlopping_2ions.ion2_line_selection':'S-1/2D-1/2',
                                       'RabiPowerFlopping_2ions.ion1_excitation_duration':WithUnit(20.0,'us'),
                                       'OpticalPumping.line_selection':'S+1/2D-3/2',
                                       'OpticalPumpingAux.aux_op_line_selection':'S-1/2D+3/2',
                                       'RabiPowerFlopping_2ions.manual_power_scan':scan,
                                       })
        self.power_flop.set_parameters(replace)
        self.power_flop.setup_sequence_parameters()
        target_power, accepted = self.power_flop.run(cxn, context)
        if self.enable_feedback:
            if accepted:
                self.pv.set_parameter('DriftTrackerRamsey','line_1_amplitude',target_power)

        
    def run_left_ion_p12m32_drift_track(self,cxn, context): 
        center_power = self.parameters['DriftTrackerRamsey.line_2_amplitude']
        minim = center_power - self.span/2.0
        maxim = center_power + self.span/2.0
        scan = [minim,maxim,self.steps]
        replace = TreeDict.fromdict({
                                       'Rabi_excitation_729_2ions.use_primary_dds':True,
                                       'RabiPowerFlopping_2ions.block_ion1_729':False,
                                       'RabiPowerFlopping_2ions.block_ion2_729':True,
                                       'RabiPowerFlopping_2ions.ion1_line_selection':'S-1/2D+3/2',
                                       'RabiPowerFlopping_2ions.ion2_line_selection':'S-1/2D-1/2',
                                       'RabiPowerFlopping_2ions.ion1_excitation_duration':WithUnit(20.0,'us'),
                                       'OpticalPumping.line_selection':'S+1/2D-3/2',
                                       'OpticalPumpingAux.aux_op_line_selection':'S-1/2D+3/2',
                                       'RabiPowerFlopping_2ions.manual_power_scan':scan,
                                       })
        self.power_flop.set_parameters(replace)
        self.power_flop.setup_sequence_parameters()
        target_power, accepted = self.power_flop.run(cxn, context)
        if self.enable_feedback:
            if accepted:
                self.pv.set_parameter('DriftTrackerRamsey','line_2_amplitude',target_power)
                
    def run_left_ion_m12m12(self,cxn, context): 
        center_power = self.parameters['Parity_transitions.left_ionSm12Dm12_power']
        minim = center_power - self.span/2.0
        maxim = center_power + self.span/2.0
        scan = [minim,maxim,self.steps]
        replace = TreeDict.fromdict({
                                       'Rabi_excitation_729_2ions.use_primary_dds':True,
                                       'RabiPowerFlopping_2ions.block_ion1_729':False,
                                       'RabiPowerFlopping_2ions.block_ion2_729':True,
                                       'RabiPowerFlopping_2ions.ion1_line_selection':'S-1/2D-1/2',
                                       'RabiPowerFlopping_2ions.ion2_line_selection':'S+1/2D+1/2',
                                       'OpticalPumping.line_selection':'S+1/2D-3/2',
                                       'OpticalPumpingAux.aux_op_line_selection':'S-1/2D+3/2',
                                       'RabiPowerFlopping_2ions.manual_power_scan':scan,
                                       })
        self.power_flop.set_parameters(replace)
        self.power_flop.setup_sequence_parameters()
        target_power, accepted = self.power_flop.run(cxn, context)
        if self.enable_feedback:
            if accepted:
                self.pv.set_parameter('Parity_transitions','left_ionSm12Dm12_power',target_power)
        
    def run_left_ion_m12m52(self,cxn, context): 
        center_power = self.parameters['Parity_transitions.left_ionSm12Dm52_power']
        minim = center_power - self.span/2.0
        maxim = center_power + self.span/2.0
        scan = [minim,maxim,self.steps]
        replace = TreeDict.fromdict({
                                       'Rabi_excitation_729_2ions.use_primary_dds':False,
                                       'RabiPowerFlopping_2ions.block_ion1_729':False,
                                       'RabiPowerFlopping_2ions.block_ion2_729':True,
                                       'RabiPowerFlopping_2ions.ion1_line_selection':'S-1/2D-5/2',
                                       'RabiPowerFlopping_2ions.ion2_line_selection':'S-1/2D-1/2',
                                       'OpticalPumping.line_selection':'S+1/2D-3/2',
                                       'OpticalPumpingAux.aux_op_line_selection':'S-1/2D+3/2',
                                       'RabiPowerFlopping_2ions.manual_power_scan':scan,
                                       })
        self.power_flop.set_parameters(replace)
        self.power_flop.setup_sequence_parameters()
        target_power, accepted = self.power_flop.run(cxn, context)
        if self.enable_feedback:
            if accepted:
                self.pv.set_parameter('Parity_transitions','left_ionSm12Dm52_power',target_power)

    def run_left_ion_p12p12(self,cxn, context): 
        center_power = self.parameters['Parity_transitions.left_ionSp12Dp12_power']
        minim = center_power - self.span/2.0
        maxim = center_power + self.span/2.0
        scan = [minim,maxim,self.steps]
        replace = TreeDict.fromdict({
                                       'Rabi_excitation_729_2ions.use_primary_dds':True,
                                       'RabiPowerFlopping_2ions.block_ion1_729':False,
                                       'RabiPowerFlopping_2ions.block_ion2_729':True,
                                       'RabiPowerFlopping_2ions.ion1_line_selection':'S+1/2D+1/2',
                                       'RabiPowerFlopping_2ions.ion2_line_selection':'S-1/2D-1/2',
                                       'OpticalPumping.line_selection':'S-1/2D+3/2',
                                       'OpticalPumpingAux.aux_op_line_selection':'S+1/2D-3/2',
                                       'RabiPowerFlopping_2ions.manual_power_scan':scan,
                                       })
        self.power_flop.set_parameters(replace)
        self.power_flop.setup_sequence_parameters()
        target_power, accepted = self.power_flop.run(cxn, context)
        if self.enable_feedback:
            if accepted:
                self.pv.set_parameter('Parity_transitions','left_ionSp12Dp12_power',target_power)

    def run_left_ion_p12p52(self,cxn, context): 
        center_power = self.parameters['Parity_transitions.left_ionSp12Dp52_power']
        minim = center_power - self.span/2.0
        maxim = center_power + self.span/2.0
        scan = [minim,maxim,self.steps]
        replace = TreeDict.fromdict({
                                       'Rabi_excitation_729_2ions.use_primary_dds':False,
                                       'RabiPowerFlopping_2ions.block_ion1_729':False,
                                       'RabiPowerFlopping_2ions.block_ion2_729':True,
                                       'RabiPowerFlopping_2ions.ion1_line_selection':'S+1/2D+5/2',
                                       'RabiPowerFlopping_2ions.ion2_line_selection':'S-1/2D-1/2',
                                       'OpticalPumping.line_selection':'S-1/2D+3/2',
                                       'OpticalPumpingAux.aux_op_line_selection':'S+1/2D-3/2',
                                       'RabiPowerFlopping_2ions.manual_power_scan':scan,
                                       })
        self.power_flop.set_parameters(replace)
        self.power_flop.setup_sequence_parameters()
        target_power, accepted = self.power_flop.run(cxn, context)
        if self.enable_feedback:
            if accepted:
                self.pv.set_parameter('Parity_transitions','left_ionSp12Dp52_power',target_power)
            
    def run_right_ion_m12m12(self,cxn, context): 
        center_power = self.parameters['Parity_transitions.right_ionSm12Dm12_power']
        minim = center_power - self.span/2.0
        maxim = center_power + self.span/2.0
        scan = [minim,maxim,self.steps]
        replace = TreeDict.fromdict({
                                       'Rabi_excitation_729_2ions.use_primary_dds':True,
                                       'RabiPowerFlopping_2ions.block_ion1_729':True,
                                       'RabiPowerFlopping_2ions.block_ion2_729':False,
                                       'RabiPowerFlopping_2ions.ion1_line_selection':'S-1/2D-1/2',
                                       'RabiPowerFlopping_2ions.ion2_line_selection':'S-1/2D-1/2',
                                       'OpticalPumping.line_selection':'S-1/2D+3/2',
                                       'OpticalPumpingAux.aux_op_line_selection':'S+1/2D-3/2',
                                       'RabiPowerFlopping_2ions.manual_power_scan':scan,
                                       })
        self.power_flop.set_parameters(replace)
        self.power_flop.setup_sequence_parameters()
        target_power, accepted = self.power_flop.run(cxn, context)
        if self.enable_feedback:
            if accepted:
                self.pv.set_parameter('Parity_transitions','right_ionSm12Dm12_power',target_power)
        
    def run_right_ion_m12m52(self,cxn, context): 
        center_power = self.parameters['Parity_transitions.right_ionSm12Dm52_power']
        minim = center_power - self.span/2.0
        maxim = center_power + self.span/2.0
        scan = [minim,maxim,self.steps]
        replace = TreeDict.fromdict({
                                       'Rabi_excitation_729_2ions.use_primary_dds':False,
                                       'RabiPowerFlopping_2ions.block_ion1_729':True,
                                       'RabiPowerFlopping_2ions.block_ion2_729':False,
                                       'RabiPowerFlopping_2ions.ion1_line_selection':'S+1/2D+5/2',
                                       'RabiPowerFlopping_2ions.ion2_line_selection':'S-1/2D-5/2',
                                       'OpticalPumping.line_selection':'S-1/2D+3/2',
                                       'OpticalPumpingAux.aux_op_line_selection':'S+1/2D-3/2',
                                       'RabiPowerFlopping_2ions.manual_power_scan':scan,
                                       })
        self.power_flop.set_parameters(replace)
        self.power_flop.setup_sequence_parameters()
        target_power, accepted = self.power_flop.run(cxn, context)
        if self.enable_feedback:
            if accepted:
                self.pv.set_parameter('Parity_transitions','right_ionSm12Dm52_power',target_power)

    def run_right_ion_p12p12(self,cxn, context): 
        center_power = self.parameters['Parity_transitions.right_ionSp12Dp12_power']
        minim = center_power - self.span/2.0
        maxim = center_power + self.span/2.0
        scan = [minim,maxim,self.steps]
        replace = TreeDict.fromdict({
                                       'Rabi_excitation_729_2ions.use_primary_dds':True,
                                       'RabiPowerFlopping_2ions.block_ion1_729':True,
                                       'RabiPowerFlopping_2ions.block_ion2_729':False,
                                       'RabiPowerFlopping_2ions.ion1_line_selection':'S-1/2D-1/2',
                                       'RabiPowerFlopping_2ions.ion2_line_selection':'S+1/2D+1/2',
                                       'OpticalPumping.line_selection':'S+1/2D-3/2',
                                       'OpticalPumpingAux.aux_op_line_selection':'S-1/2D+3/2',
                                       'RabiPowerFlopping_2ions.manual_power_scan':scan,
                                       })
        self.power_flop.set_parameters(replace)
        self.power_flop.setup_sequence_parameters()
        target_power, accepted = self.power_flop.run(cxn, context)
        if self.enable_feedback:
            if accepted:
                self.pv.set_parameter('Parity_transitions','right_ionSp12Dp12_power',target_power)

    def run_right_ion_p12p52(self,cxn, context): 
        center_power = self.parameters['Parity_transitions.right_ionSp12Dp52_power']
        minim = center_power - self.span/2.0
        maxim = center_power + self.span/2.0
        scan = [minim,maxim,self.steps]
        replace = TreeDict.fromdict({
                                       'Rabi_excitation_729_2ions.use_primary_dds':False,
                                       'RabiPowerFlopping_2ions.block_ion1_729':True,
                                       'RabiPowerFlopping_2ions.block_ion2_729':False,
                                       'RabiPowerFlopping_2ions.ion1_line_selection':'S-1/2D-5/2',
                                       'RabiPowerFlopping_2ions.ion2_line_selection':'S+1/2D+5/2',
                                       'OpticalPumping.line_selection':'S+1/2D-3/2',
                                       'OpticalPumpingAux.aux_op_line_selection':'S-1/2D+3/2',
                                       'RabiPowerFlopping_2ions.manual_power_scan':scan,
                                       })
        self.power_flop.set_parameters(replace)
        self.power_flop.setup_sequence_parameters()
        target_power, accepted = self.power_flop.run(cxn, context)
        if self.enable_feedback:
            if accepted:
                self.pv.set_parameter('Parity_transitions','right_ionSp12Dp52_power',target_power)
                    
    def finalize(self, cxn, context):
        self.power_flop.finalize(cxn, context)
    
if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = Parity_LLI_rabi_power_fitter(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)