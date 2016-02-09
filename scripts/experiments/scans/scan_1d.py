from common.abstractdevices.script_scanner.scan_methods import experiment
import sys
import labrad
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm

class scan_1d(experiment):

    '''
    General wrapper function for writing 1d scans. Holds most of the
    boilerplate code for the scans. What needs to be defined by
    the child class:

    1. Name
    2. Required parameters
    3. Base experiment class
    4. Parameter to scan
    5. Additional parameters to replace -- function to implement in subclass
    '''

    name = ''
    base_experiment_class = ('', '')
    frequency_lookup_required = False
    scanned_parameter = ('', '')
    scan_setting = ('', '')


    # frequency_looks up has the form
    # {'parameter_to_replace': ('line_selection_parameter', 'sideband_selection_parameter')}
    frequency_lookups = {}

    

    def initialize(self, cxn, context, ident):
        import_path, class_name = self.base_experiment_class
        
        try:
            __import__(import_path)
            module = sys.modules[import_path]
            exc = getattr(module, class_name)
            self.excite = self.make_experiment(exc)
            self.excite.initialize(cxn, context, ident)
        except ImportError as e:
            print 'Import error: ', e
        self.ident = ident
        
        self.scan = []
        try:
            self.cxnlab = labrad.connect('192.168.169.49')
        except Error as e:
            print "No connection to the labwide network!"
        try:
            self.drift_trcker = cxn.sd_tracker
        except Error as e:
            print "Can't connect to drift tracker"
        try:
            self.dv = cxn.data_vault
        except Error as e:
            print "No connection to data vault."

        self.data_save_context = cxn.context()

    # implement in the subclass
    def additional_replace_parameters(self):
        pass

    def lookup_frequency(self, line_selection, sideband_selection):
        frequency = cm.frequency_from_line_selection('auto', None, line_selection, self.drift_tracker)
        frequency = cm.add_sidebands(frequency, sideband_selection, self.parameters.TrapFrequencies)
        return frequency

    def setup_sequence_parameters(self):

        scan = self.scan_setting[0] + '.' + self.scan_setting[1]
        
        minim, maxim, steps = self.parameters[scan]
    
        
