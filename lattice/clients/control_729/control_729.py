from PyQt4 import QtGui, QtCore
from readout_histogram import readout_histgram
from spectrum import spectrum_connection
from rabi_flops import rabi_flop_connection
from state_preparation import state_preparation_connection
from twisted.internet.defer import inlineCallbacks

class control_729(QtGui.QWidget):
    def __init__(self, reactor, cxn = None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.reactor = reactor
        self.cxn = cxn
        self.connect_labrad()

    @inlineCallbacks
    def connect_labrad(self):
        if self.cxn is None:
            from connection import connection
            self.cxn = connection()
            yield self.cxn.connect()
        self.create_layout()
        self.connect_tab_signals()
        
    def create_layout(self):
        layout = QtGui.QGridLayout()
        self.tab = tab = QtGui.QTabWidget()
        histogram_tab = readout_histgram(self.reactor, self.cxn)
        self.state_preparation_tab = state_preparation_connection(self.reactor, self.cxn)
        spectrum_tab =  spectrum_connection(self.reactor, self.cxn)
        flop_tab = rabi_flop_connection(self.reactor, self.cxn)
        tab.addTab(histogram_tab, 'State Readout')
        self.state_prep_index = tab.addTab(self.state_preparation_tab, 'State Preparation')
        tab.addTab(spectrum_tab, 'Spectrum')
        tab.addTab(flop_tab, 'Rabi Flopping')
        layout.addWidget(tab, 1, 0, 1, 4)
        self.setLayout(layout)
    
    def connect_tab_signals(self):
        pumping_enable = self.state_preparation_tab.optical_pumping_frame.enable
        pumping_enable.stateChanged.connect(self.change_color(self.state_prep_index))
        self.change_color(self.state_prep_index)(pumping_enable.isChecked())
            
    
    def change_color(self, index):
        def func(selected):
            if selected:
                color = QtCore.Qt.darkGreen
            else:
                color = QtCore.Qt.black
            self.tab.tabBar().setTabTextColor(index, color)    
        return func

    def closeEvent(self, x):
        self.reactor.stop()
    
if __name__=="__main__":
    a = QtGui.QApplication( ['Control 729'] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = control_729(reactor)
    widget.show()
    reactor.run()