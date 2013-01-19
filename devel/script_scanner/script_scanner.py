#Created on Feb 22, 2012
#@author: Hong, Mike Haeffner Lab
'''
### BEGIN NODE INFO
[info]
name = ScriptScanner
version = 0.1
description =
instancename = ScriptScanner

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
'''
from labrad.server import LabradServer, setting, Signal
#from labrad.units import WithUnit
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock
from twisted.internet.task import LoopingCall
#from twisted.internet.threads import deferToThread
from labrad.units import WithUnit
from numpy import linspace
#configuration file
from configuration import config
import scan_methods
from scheduler import scheduler

class script_class_parameters(object):
    '''
    storage class for information about the launchable script
    '''
    def  __init__(self, name, cls, parameters):
        self.name = name
        self.cls = cls
        self.parameters = parameters
        
class ScriptScanner(LabradServer):
    
    name = 'ScriptScanner'
#    onNewVoltage = Signal(123556, 'signal: new voltage', '(sv)')
    
#    @inlineCallbacks
    def initServer(self):
        self.script_parameters = {}
        self.scheduler = scheduler()
        self.load_scripts()
        self.listeners = set()
    
    def load_scripts(self):
        '''
        loads script information from th configuration file
        '''
        for name, (import_path, class_name) in config.scripts.iteritems():
            try:
                module = __import__(import_path)
                cls = getattr(module, class_name)
            except ImportError as e:
                print 'Script Control Error importing: ', e
            except AttributeError:
                print 'There is no class {0} in module {1}'.format(class_name, module) 
            else:
                parameters = cls.required_parameters()
                self.script_parameters[name] = script_class_parameters(name, cls, parameters)
            
    @setting(0, "Get Available Scripts", returns = '*s')
    def get_available_scripts(self, c):
        return self.script_parameters.keys()
    
    @setting(1, "Get Script Parameters", script = 's', returns = '*s')
    def get_script_parameters(self, c, script):
        if script not in self.script_parameters.keys():
            raise Exception ("Script {} Not Found".format(script))
        return self.script_parameters[script].parameters
    
    @setting(2, "Get Parameter Limits", script = 's', parameter = 's', returns = 'vv')
    def get_parameter_limits(self, c, script, parameter):
        #this somehow involves semaphore lookup and a lookup table.
        yield None
        returnValue ( ( WithUnit(1.0,'s'), WithUnit(2.0, 's') ) )
    
    @setting(10, 'New Script', script = 's', returns = 'w')
    def new_script(self, c, script):
        '''
        Launch the script. Returns ID of the queued scan.
        '''
        if script not in self.script_parameters.keys():
            raise Exception ("Script {} Not Found".format(script))
        single_launch = scan_methods.repeat_script(script, repeatitions = 1)
        scan_id = self.scheduler.add_scan_to_queue(single_launch)
        return scan_id
    
    @setting(11, "New Script Repeat", script = 's', repeat = 'w')
    def new_script_repeat(self, c, script, repeat):
        #error checking that it's a valid script and parameter
        #same as scan but with no setting of parameter
        yield None
    
    @setting(12, "New Script Scan", script = 's', parameter = 's', minim = 'v', maxim = 'v', units = 's', steps = 'w')
    def new_scan(self, c, script, parameter, minim, maxim, units, steps):
        from test_experiment import test1
        #error checking that it's a valid script and parameter
        scan_points = linspace(minim, maxim, steps)
        inst = test1()
        inst.initialize()
        for pt in scan_points:
            #if should continue
            inst.set_parameter(WithUnit(pt, units))
            inst.run()
        inst.stop()
    
    @setting(13, "New Scheduled Script", script = 's', duration = 'v[s]')
    def new_scheduled_script(self, c, script, duration):
        #error checking that valid script and valid duration
        duration = duration['s']
    
    @setting(14, "Pause Script", script_ID = 'w', should_pause = 'b')
    def pause_script(self, c, script_ID, should_pause):
        pass
        #check that script running
        
    @setting(15, "Stop Script", script_ID = 'w')
    def stop_script(self, c, script_ID):
        #check that it's running or paused
        pass
    
    def notifyOtherListeners(self, context, message, f):
        """
        Notifies all listeners except the one in the given context, executing function f
        """
        notified = self.listeners.copy()
        notified.remove(context.ID)
        f(message,notified)
    
    def initContext(self, c):
        """Initialize a new context object."""
        self.listeners.add(c.ID)
    
    def expireContext(self, c):
        self.listeners.remove(c.ID)
    
#    @inlineCallbacks
#    def stopServer(self):
#        '''save the latest voltage information into registry'''
#        try:
#            yield self.client.registry.cd(['','Servers', 'DAC'], True)
#            for name,channel in self.d.iteritems():
#                yield self.client.registry.set(name, channel.voltage)
#        except AttributeError:
#            #if dictionary doesn't exist yet (i.e bad identification error), do nothing
#            pass

if __name__ == "__main__":
    from labrad import util
    util.runServer( ScriptScanner() )