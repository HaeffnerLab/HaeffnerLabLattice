from numpy import linspace
import labrad
from labrad.units import WithUnit

class scan_info(object):
    '''
    holds informaton about the scan or measurement
    '''
    def __init__(self, name):
        self.name = name

class scan_method(scan_info):
    
    def __init__(self, name, script_cls):
        super(scan_method, self).__init__(name)
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