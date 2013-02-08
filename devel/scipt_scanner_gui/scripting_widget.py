from PyQt4 import QtGui, QtCore
from scheduled_widget import scheduled_combined
from running_scans_widget import running_combined
from queued_widget import queued_combined
from experiment_selector_widget import experiment_selector_widget

class scripting_widget(QtGui.QWidget):
    
    on_run = QtCore.pyqtSignal(str)
    on_repeat = QtCore.pyqtSignal((str, int))
    on_cancel_queued = QtCore.pyqtSignal(int)
    on_cancel_scheduled = QtCore.pyqtSignal(int)
    on_schedule = QtCore.pyqtSignal((str,float))
    on_schedule_duration = QtCore.pyqtSignal((int, float))
        
    def __init__(self, reactor):
        super(scripting_widget, self).__init__()
        self.reactor = reactor
        self.setupLayout()
    
    def setupLayout(self):
        layout = QtGui.QVBoxLayout()
        self.selector = experiment_selector_widget(self.reactor)
        self.running = running_combined(self.reactor)
        self.scheduled = scheduled_combined(self.reactor)
        self.queued = queued_combined(self.reactor)
        layout.addWidget(self.selector)
        layout.addWidget(self.scheduled)
        layout.addWidget(self.queued)
        layout.addWidget(self.running)
        self.setLayout(layout)
    
    def addExperiment(self, experiment):
        self.selector.addExperiment(experiment)
    
    def addQueued(self, ident, name):
        self.queued.add(ident, name)
    
    def removeQueued(self, ident):
        self.queued.remove(ident)

    def addRunning(self, experiment):
        pass
    
    def addScheduled(self, ident, name, duration):
        self.scheduled.add(ident, name, duration)
    
    def removeScheduled(self, ident):
        self.scheduled.remove(ident)
    
    def newScheduledDuration(self, info):
        ident, duration = info
        self.scheduled.change(ident, duration)
     
    def connect_layout(self):
        self.selector.on_run.connect(self.on_run.emit)
        self.selector.on_repeat.connect(self.on_repeat)
        self.selector.on_schedule.connect(self.on_schedule)
        self.queued.ql.on_cancel.connect(self.on_cancel_queued.emit)
        self.scheduled.sl.on_cancel.connect(self.on_cancel_scheduled.emit)
        self.scheduled.sl.on_new_duration.connect(self.on_schedule_duration)
           
    def closeEvent(self, event):
        self.reactor.stop()