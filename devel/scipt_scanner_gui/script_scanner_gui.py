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
        from labrad.types import Error
        self.WithUnit = WithUnit
        self.Error = Error
        if self.cxn is None:
            self.cxn = connection()
            yield self.cxn.connect()
        self.context = yield self.cxn.context()
        try:
            yield self.populateInformation()
            yield self.setupListeners()
            self.connect_layouts()
        except Exception, e:
            print 'script_scanner_gui: script scanner not available'
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
        for ident,name in running:
            self.scripting_widget.addRunning(ident,name)
    
    @inlineCallbacks
    def setupListeners(self):
        sc = self.cxn.servers['scriptscanner']
        #queued
        yield sc.signal_on_queued_new_script(self.SIGNALID, context = self.context)
        yield sc.addListener(listener = self.on_new_queued_script, source = None, ID = self.SIGNALID, context = self.context)   
        yield sc.signal_on_queued_removed(self.SIGNALID + 1, context = self.context)
        yield sc.addListener(listener = self.on_removed_queued_sciprt, source = None, ID = self.SIGNALID + 1, context = self.context)     
        #scheduled
        yield sc.signal_on_scheduled_new_duration(self.SIGNALID + 2, context = self.context)
        yield sc.addListener(listener = self.on_scheduled_new_duration, source = None, ID = self.SIGNALID + 2, context = self.context)     
        yield sc.signal_on_scheduled_new_script(self.SIGNALID + 3, context = self.context)
        yield sc.addListener(listener = self.on_scheduled_new_script, source = None, ID = self.SIGNALID + 3, context = self.context)     
        yield sc.signal_on_scheduled_removed(self.SIGNALID + 4, context = self.context)
        yield sc.addListener(listener = self.on_scheduled_removed, source = None, ID = self.SIGNALID + 4, context = self.context)     
        #running
        yield sc.signal_on_running_new_script(self.SIGNALID + 5, context = self.context)
        yield sc.addListener(listener = self.on_running_new_script, source = None, ID = self.SIGNALID + 5, context = self.context)     
        yield sc.signal_on_running_new_status(self.SIGNALID + 6, context = self.context)
        yield sc.addListener(listener = self.on_running_new_status, source = None, ID = self.SIGNALID + 6, context = self.context)
        yield sc.signal_on_running_script_finished(self.SIGNALID + 7, context = self.context)
        yield sc.addListener(listener = self.on_running_script_finished, source = None, ID = self.SIGNALID + 7, context = self.context)       
        yield sc.signal_on_running_script_finished_error(self.SIGNALID + 8, context = self.context)
        yield sc.addListener(listener = self.on_running_script_finished_error, source = None, ID = self.SIGNALID + 8, context = self.context)        
        yield sc.signal_on_running_script_paused(self.SIGNALID + 9, context = self.context)
        yield sc.addListener(listener = self.on_running_script_paused, source = None, ID = self.SIGNALID + 9, context = self.context) 
    
    def on_running_script_finished_error(self, signal, info):
        ident, message = info
        self.scripting_widget.runningScriptFinished(ident)
        self.displayError("Experiment {0} ended with an error {1}".format(ident, message) )
        
    def on_running_script_paused(self, signal, info):
        self.scripting_widget.runningScriptPaused(*info)
         
    def on_running_script_finished(self, signal, ident):
        self.scripting_widget.runningScriptFinished(ident)

    def on_running_new_script(self, signal, info):
        self.scripting_widget.addRunning(*info)
    
    def on_running_new_status(self, signal, info):
        self.scripting_widget.runningNewStatus(*info)
        
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
        self.scripting_widget.on_running_stop.connect(self.running_stop)
        self.scripting_widget.on_running_restart.connect(self.running_restart)
        self.scripting_widget.on_running_pause.connect(self.running_pause)

    def get_widgets(self):
        return self.scripting_widget
    
    def show(self):
        self.scripting_widget.show()
        self.parameters_widget.show()
    
    @inlineCallbacks
    def running_stop(self, ident):
        sc = self.cxn.servers['scriptscanner']
        ident = int(ident)
        try:
            yield sc.stop_script(ident)
        except self.Error as e:
            self.displayError(e.msg)
    
    @inlineCallbacks
    def running_restart(self, ident):
        sc = self.cxn.servers['scriptscanner']
        ident = int(ident)
        try:
            yield sc.restart_script(ident)
        except self.Error as e:
            self.displayError(e.msg)
    
    @inlineCallbacks
    def running_pause(self, ident, should_pause):
        sc = self.cxn.servers['scriptscanner']
        ident = int(ident)
        try:
            yield sc.pause_script(ident, should_pause)
        except self.Error as e:
            self.displayError(e.msg)
    
    @inlineCallbacks
    def scheduled_duration(self, ident, duration):
        sc = self.cxn.servers['scriptscanner']
        ident = int(ident)
        duration = self.WithUnit(float(duration), 's')
        try:
            yield sc.change_scheduled_duration(ident, duration)
        except self.Error as e:
            self.displayError(e.msg)
    
    @inlineCallbacks
    def scheduled_cancel(self, ident):
        ident = int(ident)
        sc = self.cxn.servers['scriptscanner']
        try:
            yield sc.cancel_scheduled_script(ident)
        except self.Error as e:
            self.displayError(e.msg)
        
    @inlineCallbacks
    def schedule_script(self, name, duration):
        sc = self.cxn.servers['scriptscanner']
        name = str(name)
        duration = self.WithUnit(duration, 's')
        try:
            yield sc.new_script_schedule(name, duration)
        except self.Error as e:
            self.displayError(e.msg)
        
    @inlineCallbacks
    def repeat_script(self, name, repeatitions):
        sc = self.cxn.servers['scriptscanner']
        name = str(name)
        try:
            yield sc.new_script_repeat(name, repeatitions)
        except self.Error as e:
            self.displayError(e.msg)
    
    @inlineCallbacks
    def on_cancel_queued(self, ident):
        sc = self.cxn.servers['scriptscanner']
        ident = int(ident)
        try:
            yield sc.remove_queued_script(ident, context = self.context)
        except self.Error as e:
            self.displayError(e.msg)
        
    @inlineCallbacks
    def run_script(self, script):
        sc = self.cxn.servers['scriptscanner']
        script = str(script)
        try:
            yield sc.new_experiment(script, context = self.context)
        except self.Error as e:
            self.displayError(e.msg)
    
    def setupWidgets(self):
        self.scripting_widget = scripting_widget(self.reactor)
        self.parameters_widget = parameters_widget(self.reactor)
    
    def displayError(self, text):
        message = QtGui.QMessageBox()
        message.setText(text)
        message.exec_()

if __name__=="__main__":
    a = QtGui.QApplication( ["Script Scanner"] )
    from common.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    gui = script_scanner_gui(reactor)
    gui.show()
    reactor.run()