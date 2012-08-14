from PyQt4 import QtGui, QtCore
from connection import connection
from readout_histogram import readout_histgram
from helper_widgets import durationWdiget, limitsWidget, optical_pumping

class control_729(QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.reactor = reactor
        self.create_layout()
        self.connection = connection()
        
    def create_layout(self):
        layout = QtGui.QGridLayout()
        dw = durationWdiget(self.reactor)
        layout.addWidget(dw, 0, 0, 1, 1)
        self.tab = tab = QtGui.QTabWidget()
        histogram_tab = self.make_histogram_tab()
        spectrum_tab =  self.make_spectrum_tab()
        optical_pump_tab = self.make_pump_tab()
        flop_tab = self.make_flop_tab()
        tab.addTab(histogram_tab, '&Histogram')
        tab.addTab(spectrum_tab, '&Spectrum')
        opt_index = tab.addTab(optical_pump_tab, '&Optical Pumping')
        tab.addTab(flop_tab, '&Rabi Flopping')
        #connect basic signals
        optical_pump_tab.enable.clicked.connect(self.change_color(opt_index))
        layout.addWidget(tab, 1, 0, 1, 4)
        self.setLayout(layout)
    
    def change_color(self, index):
        def func(selected):
            if selected:
                color = QtCore.Qt.darkGreen
            else:
                color = QtCore.Qt.black
            self.tab.tabBar().setTabTextColor(index, color)    
        return func
        
    def make_histogram_tab(self):
        tab = readout_histgram(self.reactor)
        return tab
    
    def make_spectrum_tab(self):
        spectrum = QtGui.QWidget()
        layout = QtGui.QGridLayout()
        layout.addWidget(limitsWidget(self.reactor), 0, 0, 1, 1)
        spectrum.setLayout(layout)
        return spectrum
    
    def make_flop_tab(self):
        flop = QtGui.QWidget()
        return flop
    
    def make_pump_tab(self):
        pump = optical_pumping(self.reactor)
        return pump
    
if __name__=="__main__":
    a = QtGui.QApplication( ['Control 729'] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = control_729(reactor)
    widget.show()
    reactor.run()