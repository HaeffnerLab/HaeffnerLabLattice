from numpy import linspace
import labrad
from labrad.units import WithUnit

class experiment_info(object):
    '''
    holds informaton about the scan or measurement
    '''
    def __init__(self, name):
        self.name = name

class experiment(experiment_info):
    
    def __init__(self, name, script_cls):
        super(experiment, self).__init__(name)
        self.script = script_cls()

    def execute(self, ident):
        '''
        Executes the scan method
        '''
        self.ident = ident
        cxn = labrad.connect()
        self.sc = cxn.servers['ScriptScanner']
        context = cxn.context()
        try:
            self.script.initialize(cxn, ident)
            self.sc.launch_confirmed(ident)
            self.execute_scan(cxn, context)
            self.script.finalize()
        except Exception as e:
            self.sc.error_finish_confirmed(self.ident, str(e))
            cxn.disconnect()
        else:
            self.sc.finish_confirmed(self.ident)
            cxn.disconnect()
            return True
    
    def pause_or_stop(self):
        should_stop = self.sc.pause_or_stop(self.ident)
        if should_stop:
            self.sc.stop_confirmed(self.ident)
            return True
    
    def execute_scan(self, cxn, context):
        '''
        implemented by the subclass
        '''

class single_run(scan_method):
    '''
    Used to perform a single measurement
    '''
    def __init__(self, script):
        super(single_run,self).__init__(script.name(), script)
    
    def execute_scan(self, cxn, context):
        self.script.run()

class repeat_measurement(scan_method):
    '''
    Used to repeat a measurement multiple times
    '''
    def __init__(self, script, repeatitions):
        self.repeatitions = repeatitions
        scan_name = self.name_format(script.name())
        super(repeat_measurement,self).__init__(scan_name, script)

    def name_format(self, name):
        return 'Repeat {0} {1} times'.format(name, self.repeatitions)
    
    def execute_scan(self, cxn, context):
        dv = cxn.data_vault
        dv.cd(['','ScriptScanner'], True, context = context)
        for i in range(self.repeatitions):
            if self.pause_or_stop(): return
            self.script.run()
            self.sc.script_set_progress(self.ident,  100 * float(i + 1) / self.repeatitions)
            
class scan_measurement_1D(scan_method):
    '''
    Used to Scan a Parameter of a measurement
    '''
    def __init__(self, script, parameter, minim, maxim, steps, units):
        scan_name = self.name_format(script.name())
        super(scan_measurement_1D,self).__init__(scan_name, script)
        self.parameter = parameter
        self.scan_points = linspace(minim, maxim, steps)
        self.scan_points = [WithUnit(pt, units) for pt in self.scan_points ]
        
    def name_format(self, name):
        return 'Scanning {0} in {1}'.format(self.parameter, name)
    
    def execute_scan(self):
        for i in range(len(self.scan_points)):
            if self.pause_or_stop(): return
            self.script.set_parameter(self.parameter, self.scan_points[i])
            self.script.run()
            self.sc.script_set_progress(self.ident,  100 * float(i + 1) / self.scan_points)
            
class excite_D(single_run):
    
    
    name = "Excite D"
    required_parameters = ['pulse_sequence_repeatitions']
    #required_parameters.extend(self.sequence.all_variables())

    def initialize(self, cxn, context, ident):
        self.cxn = cxn
        self.pulser = cxn.pulser
        self.context = context
        self.ident = ident
    
    def set_parameters(self, parameters):
        self.pulse_sequence_repeatitions = parameters.get('pulse_sequence_repeatitions', None)
    
    def check_parameters(self):
        #check self.pulse_sequence_repeatitions
        pass
    
    def run(self):
        #saving and so on
        pass

class spectrum729(single_run):
    
    name = "Spectrum 729"
    required_parameters = ['line_to_scan', 'should_save_data', 'should_fit']
    required_subexperiments = [excite_D]
    
    def initiailze(self, cxn, context, ident):
        self.cxn = cxn
        self.pulser = cxn.pulser
        self.context = context
        self.ident = ident
        self.fit = None
        
    def set_parameters(self , parameters):
        self.line_to_scan = parameters.get('line_to_scan', None)
        self.should_save_data = parameters.get('should_save_data', True)
        self.should_fit = parameters.get('should_fit', False)
        self.sequence_repeatitions = parameters.get('sequence_repeatitions', None)
        
    def get_fit(self):
        if self.fit is None:
            raise Exception("No Fit Available")
        return self.fit
    
    def get_fit_center(self):
        fit = self.get_fit()
        return fit[0]#or something
        
    def run(self):
        pass
    
    def finalize(self):
        pass
    
class cavity729_drift_track_scans(single_run):
    
    name = 'Drift Tracker 729'
    required_parameters = ['lines_to_scan']
    required_subexperiments = [spectrum729]
    
    def initialize(self, cxn, ident):
        self.cxn = cxn
        self.dv = cxn.data_vault
        self.sd_tracker = cxn.sd_tracker
        self.spectrum = spectrum729()
        self.spectrum.initiailze(cxn, cxn.context(), ident)
    
    def set_parameters(self, d):
        self.lines_to_scan = d.get('lines_to_scan', None)
        
    def check_parameters(self):
        if self.lines_to_scan is None:
            raise Exception("{0}: lines_to_scan parameter not provided".format(self.name()))
        elif not len(self.lines_to_scan) == 2:
            raise Exception("{0}: incorrect number of lines in lines_to_scan parameter".format(self.name()))
        transition_names = set(self.sd_tracker.get_transition_names())
        if not set(self.lines_to_scan).issubset(transition_names):
            raise Exception("{0}: some names in lines_to_scan are not recognized")
    
    def run(self):
        self.check_parameters()
        line_centers = []
        for line in self.lines_to_scan:
            self.spectrum.set_parameter({'line_to_scan':line})
            self.spectrum.run()
            try:
                center = self.spectrum.get_fit_center()
                line_centers.append(center)
            except Exception:
                #fit not found
                return
        submission = zip(self.lines_to_scan, line_centers)
        self.sd_tracker.submit_line_centers(submission)
        
    def finalize(self):
        self.spectrum.finalize()