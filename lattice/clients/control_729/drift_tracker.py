from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
from helper_widgets import saved_frequencies, saved_frequencies_dropdown
import numpy
from configuration import config_729_tracker as c


class readout_histgram(QtGui.QWidget):
    def __init__(self, reactor, cxn = None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.reactor = reactor
        self.cxn = cxn
        self.subscribed = False
        self.create_layout()
        self.connect_labrad()
    
    def create_layout(self):
        layout = QtGui.QGridLayout()
        plot_layout = self.create_drift_layout()
        widget_layout = self.create_widget_layout()
        spectrum_layout = self.create_spectrum_layout()
        layout.addLayout(plot_layout, 0, 0, 1, 2)
        layout.addLayout(widget_layout, 1, 0, 1, 1)
        layout.addLayout(spectrum_layout, 1, 1, 1, 1)
        self.setLayout(layout)
   
    def create_drift_layout(self):
        layout = QtGui.QVBoxLayout()
        self.fig = Figure()
        self.drift_canvas = FigureCanvas(self.fig)
        self.drift_canvas.setParent(self)  
        gs = gridspec.GridSpec(1, 2, wspace=0.15, left = 0.05, right = 0.95)
        line_drift = self.fig.add_subplot(gs[0, 0])
        line_drift.set_xlabel('Time (min)')
        line_drift.set_ylabel('KHz')
        line_drift.set_title("Line Center Drift")
        self.line_drift = line_drift
        self.line_drift_lines = []
        self.line_drift_fit_line = []
        b_drift = self.fig.add_subplot(gs[0, 1], sharex=line_drift)
        b_drift.set_xlabel('Time (min)')
        b_drift.set_ylabel('mgauss')
        b_drift.set_title("B Field Drift")
        self.b_drift_lines = []
        self.b_drift_fit_line = []
        self.b_drift = b_drift
        self.mpl_toolbar = NavigationToolbar(self.drift_canvas, self)
        layout.addWidget(self.mpl_toolbar)
        layout.addWidget(self.drift_canvas)
        return layout
    
    def create_spectrum_layout(self):
        layout = QtGui.QVBoxLayout()
        self.fig = Figure()
        self.spec_canvas = FigureCanvas(self.fig)
        self.spec_canvas.setParent(self)  
        gs = gridspec.GridSpec(1, 1, wspace=0.15, left = 0.05, right = 0.95)
        spec = self.fig.add_subplot(gs[0, 0])
        spec.set_xlim(left = c.frequency_limit[0], right = c.frequency_limit[1])
        spec.set_ylim(bottom = 0, top = 1)
        spec.set_xlabel('MHz')
        spec.set_ylabel('Arb')
        spec.set_title("Predicted Spectrum")
        self.spec = spec
        self.mpl_toolbar = NavigationToolbar(self.spec_canvas, self)
        self.spectral_lines = []
        layout.addWidget(self.mpl_toolbar)
        layout.addWidget(self.spec_canvas)
        return layout
    
    def create_widget_layout(self):
        layout = QtGui.QGridLayout()
        self.frequency_table = saved_frequencies(self.reactor, limits = c.frequency_limit, suffix = ' MHz', sig_figs = 4)
        self.entry_table = saved_frequencies_dropdown(self.reactor, limits = c.frequency_limit, suffix = ' MHz', sig_figs = 4)
        self.entry_button = QtGui.QPushButton("Submit")
        self.remove_button = QtGui.QPushButton("Remove")
        self.remove_count = QtGui.QSpinBox()
        self.remove_count.setRange(-20,20)
        self.tosemaphore = QtGui.QCheckBox()
        self.tosemaphore_rate = QtGui.QDoubleSpinBox()
        self.track_duration = QtGui.QDoubleSpinBox()
        self.keep = QtGui.QDoubleSpinBox()
        layout.addWidget(self.frequency_table, 0, 0, 2, 1)
        layout.addWidget(self.entry_table, 0, 1 , 1 , 1)
        layout.addWidget(self.entry_button, 1, 1, 1, 1)
        remove_layout = QtGui.QHBoxLayout() 
        remove_layout.addWidget(self.remove_count)
        remove_layout.addWidget(self.remove_button)    
        update_layout = QtGui.QHBoxLayout()
        update_layout.addWidget(QtGui.QLabel("Update Semaphore"))
        update_layout.addWidget(self.tosemaphore)
        update_layout.addWidget(QtGui.QLabel("Rate (sec)"))
        update_layout.addWidget(self.tosemaphore_rate)
        keep_layout = QtGui.QHBoxLayout()
        keep_layout.addWidget(QtGui.QLabel("Tracking Duration"))
        keep_layout.addWidget(self.keep)
        layout.addLayout(update_layout, 2, 1, 1, 1)
        layout.addLayout(remove_layout, 2, 0, 1, 1)
        layout.addLayout(keep_layout, 3, 1, 1, 1)
        return layout
        
    def connect_layout(self):
        self.remove_button.clicked.connect(self.on_remove)
        self.entry_button.clicked.connect(self.on_entry)
        #connect remove button
        #connect submit
        #connect update semahore
        #connect tracking duration
    
    @inlineCallbacks
    def initialize_layout(self):
        server = self.cxn.servers['SD Tracker']
        transitions = yield server.get_transition_names()
        self.entry_table.fill_out(transitions)
    
    @inlineCallbacks
    def on_remove(self, clicked):
        to_remove = self.remove_count.value()
        server = self.cxn.servers['SD Tracker']
        yield server.remove_measurement(to_remove)
    
    @inlineCallbacks
    def on_entry(self, clicked):
        server = self.cxn.servers['SD Tracker']
        info = self.entry_table.get_info()
        with_units = [(name, self.WithUnit(val, 'MHz')) for name,val in info]
        yield server.set_measurements(with_units)
    
    @inlineCallbacks
    def connect_labrad(self):
        from labrad.units import WithUnit
        self.WithUnit = WithUnit
        if self.cxn is None:
            from connection import connection
            self.cxn = connection()
            yield self.cxn.connect()
        self.context = yield self.cxn.context()
        try:
            yield self.subscribe_tracker()
        except Exception as e:
            print e
            self.setDisabled(True)
        self.cxn.on_connect['SD Tracker'].append( self.reinitialize_tracker)
        self.cxn.on_disconnect['SD Tracker'].append( self.disable)
        yield self.initialize_layout()
        self.connect_layout()
        
    @inlineCallbacks
    def subscribe_tracker(self):
        yield self.cxn.servers['SD Tracker'].signal__new_fit(c.ID, context = self.context)
        yield self.cxn.servers['SD Tracker'].addListener(listener = self.on_new_fit, source = None, ID = c.ID, context = self.context)
        self.subscribed = True
    
    @inlineCallbacks
    def reinitialize_tracker(self):
        self.setDisabled(False)
        yield self.cxn.servers['SD Tracker'].signal__new_fit(c.ID, context = self.context)
        if not self.subscribed:
            yield self.cxn.servers['SD Tracker'].addListener(listener = self.on_new_fit, source = None, ID = c.ID, context = self.context)
            self.subscribed = True
    
    @inlineCallbacks
    def on_new_fit(self, x, y):
        server = self.cxn.servers['SD Tracker']
        lines = yield server.get_current_lines()
        self.update_spectrum(lines)
        self.update_listing(lines)
        #update measurements and fit
        history = yield server.get_fit_history()
        inunits_b = [(t['min'], b['mgauss']) for (t,b,freq) in history]
        inunits_f = [(t['min'], freq['kHz']) for (t,b,freq) in history]
        self.update_track(inunits_b, self.b_drift, self.b_drift_lines)
        self.update_track(inunits_f, self.line_drift, self.line_drift_lines)
        fit_b = yield server.get_fit_parameters('bfield')
        fit_f = yield server.get_fit_parameters('linecenter')
        self.plot_fit(fit_b, self.b_drift, self.b_drift_fit_line, 1000)
        self.plot_fit(fit_f, self.line_drift, self.line_drift_fit_line, 1000)       
    
    def update_track(self, meas, axes, lines):
        #clear
        for i in range(len(lines)):
            line = lines.pop()
            line.remove()
        x = numpy.array([m[0] for m in meas])
        y = [m[1] for m in meas]
        line = axes.plot(x,y, 'b*')[0]
        lines.append(line)
        self.drift_canvas.draw()
    
    def plot_fit(self, p, axes, line, m = 1):
        for i in range(len(line)):
            l = line.pop()
            l.remove()
        xmin,xmax = axes.get_xlim()
        xmin-= 10
        xmax+= 10
        points = 1000
        x = numpy.linspace(xmin, xmax, points) 
        y = m * numpy.polyval(p, 60*x)
        l = axes.plot(x, y, '-r')[0]
        line.append(l)
        self.drift_canvas.draw()
        
    def update_spectrum(self, lines):
        #clear
        for i in range(len(self.spectral_lines)):
            line = self.spectral_lines.pop()
            line.remove()
        srt = sorted(lines, key = lambda x: x[1])
        num = len(srt)
        for i, (name, freq) in enumerate(srt):
            line = self.spec.axvline(freq['MHz'], linewidth=1.0, ymin = 0, ymax = 1)
            self.spectral_lines.append(line)
            label = self.spec.annotate(name, xy = (freq['MHz'], 0.9 - i * 0.7 / num), xycoords = 'data', fontsize = 13.0)
            self.spectral_lines.append(label)
        self.spec.set_xlim(xmin = srt[0][1]['MHz'] - 1.0)
        self.spec.set_xlim(xmax = srt[num - 1][1]['MHz'] + 1.0)
        self.spec_canvas.draw()

    def update_listing(self, lines):
        self.frequency_table.fill_out_widget(lines)
        
    @inlineCallbacks
    def disable(self):
        self.setDisabled(True)
        yield None
    
    def closeEvent(self, x):
        self.reactor.stop()  
    
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = readout_histgram(reactor)
    widget.show()
    reactor.run()