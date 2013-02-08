from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks
from parameters_widget import parameters_widget
from scripting_widget import scripting_widget
from common.clients.connection import connection

class script_scanner_gui(object):
    
    SIGNALID = 319245
    
    def __init__(self, reactor, cxn = None):
        self.cxn = cxn
        self.reactor = reactor
        self.setupWidgets()
        self.connect()
    
    @inlineCallbacks
    def connect(self):
        from labrad.units import WithUnit
        self.WithUnit = WithUnit
        if self.cxn is None:
            self.cxn = connection()
            yield self.cxn.connect()
        self.context = yield self.cxn.context()
        try:
            yield self.populateInformation()
            yield self.setupListeners()
            self.connect_layouts()
        except Exception, e:
            print e
            print 'script_scanner_gui: DAC not available'
            self.disable(True)
#        self.cxn.on_connect['DAC'].append( self.reinitialize)
#        self.cxn.on_disconnect['DAC'].append( self.disable)
    
    def disable(self, should_disable):
        if should_disable:
            self.scripting_widget.setDisabled(should_disable)
            self.parameters_widget.setDisabled(should_disable)
        else:
            self.scripting_widget.setEnabled()
            self.parameters_widget.setEnabled()
    
    @inlineCallbacks
    def populateInformation(self):
        sc = self.cxn.servers['scriptscanner']
        available = yield sc.get_available_scripts(context = self.context)
        queued = yield sc.get_queue(context = self.context)
        running = yield sc.get_running(context = self.context)
        scheduled = yield sc.get_scheduled(context = self.context)
        for experiment in available:
            self.scripting_widget.addExperiment(experiment)
        for ident,name in queued:
            self.scripting_widget.addQueued(ident, name)
        for ident,name,duration in scheduled:
            self.scripting_widget.addScheduled(ident,name,duration)
#                self.scripting_widget.addRunning(running)
    
    @inlineCallbacks
    def setupListeners(self):
        sc = self.cxn.servers['scriptscanner']
        yield sc.signal_on_queued_new_script(self.SIGNALID, context = self.context)
        yield sc.addListener(listener = self.on_new_queued_script, source = None, ID = self.SIGNALID, context = self.context)   
        yield sc.signal_on_queued_removed(self.SIGNALID + 1, context = self.context)
        yield sc.addListener(listener = self.on_removed_queued_sciprt, source = None, ID = self.SIGNALID + 1, context = self.context)     
        yield sc.signal_on_scheduled_new_duration(self.SIGNALID + 2, context = self.context)
        yield sc.addListener(listener = self.on_scheduled_new_duration, source = None, ID = self.SIGNALID + 2, context = self.context)     
        yield sc.signal_on_scheduled_new_script(self.SIGNALID + 3, context = self.context)
        yield sc.addListener(listener = self.on_scheduled_new_script, source = None, ID = self.SIGNALID + 3, context = self.context)     
        yield sc.signal_on_scheduled_removed(self.SIGNALID + 4, context = self.context)
        yield sc.addListener(listener = self.on_scheduled_removed, source = None, ID = self.SIGNALID + 4, context = self.context)     
            
    
    def on_scheduled_new_duration(self, signal, info):
        self.scripting_widget.newScheduledDuration(info)
        
    def on_scheduled_new_script(self, signal, info):
        self.scripting_widget.addScheduled(*info)
    
    def on_scheduled_removed(self, signal, info):
        self.scripting_widget.removeScheduled(info)
         
    def on_new_queued_script(self, signal, info):
        self.scripting_widget.addQueued(*info)
    
    def on_removed_queued_sciprt(self, signal, ident):
        self.scripting_widget.removeQueued(ident) 
    
    def connect_layouts(self):
        self.scripting_widget.connect_layout()
        self.parameters_widget.connect_layout()
        self.scripting_widget.on_run.connect(self.run_script)
        self.scripting_widget.on_cancel_queued.connect(self.on_cancel_queued)
        self.scripting_widget.on_repeat.connect(self.repeat_script)
        self.scripting_widget.on_schedule.connect(self.schedule_script)
        self.scripting_widget.on_cancel_scheduled.connect(self.scheduled_cancel)
        self.scripting_widget.on_schedule_duration.connect(self.scheduled_duration)
    
    def get_widgets(self):
        return self.scripting_widget
    
    def show(self):
        self.scripting_widget.show()
        self.parameters_widget.show()
    
    @inlineCallbacks
    def scheduled_duration(self, ident, duration):
        sc = self.cxn.servers['scriptscanner']
        ident = int(ident)
        duration = self.WithUnit(float(duration), 's')
        yield sc.change_scheduled_duration(ident, duration)
    
    @inlineCallbacks
    def scheduled_cancel(self, ident):
        ident = int(ident)
        sc = self.cxn.servers['scriptscanner']
        yield sc.cancel_scheduled_script(ident)
        
    @inlineCallbacks
    def schedule_script(self, name, duration):
        sc = self.cxn.servers['scriptscanner']
        name = str(name)
        duration = self.WithUnit(duration, 's')
        yield sc.new_script_schedule(name, duration)
        
    @inlineCallbacks
    def repeat_script(self, name, repeatitions):
        sc = self.cxn.servers['scriptscanner']
        name = str(name)
        yield sc.new_script_repeat(name, repeatitions)
    
    @inlineCallbacks
    def on_cancel_queued(self, ident):
        sc = self.cxn.servers['scriptscanner']
        ident = int(ident)
        yield sc.remove_queued_script(ident, context = self.context)
        
    @inlineCallbacks
    def run_script(self, script):
        sc = self.cxn.servers['scriptscanner']
        script = str(script)
        yield sc.new_experiment(script, context = self.context)
    
    def setupWidgets(self):
        self.scripting_widget = scripting_widget(self.reactor)
        self.parameters_widget = parameters_widget(self.reactor)

if __name__=="__main__":
    a = QtGui.QApplication( ["Script Scanner"] )
    from common.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    gui = script_scanner_gui(reactor)
    gui.show()
    reactor.run()