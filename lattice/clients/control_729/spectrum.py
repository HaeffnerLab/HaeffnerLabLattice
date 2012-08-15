from PyQt4 import QtGui
from helper_widgets import durationWdiget, limitsWidget, saved_frequencies_dropdown

class spectrum(QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(spectrum, self).__init__(parent)
        self.reactor = reactor
        self.initializeGUI()
        self.connect_widgets()
        
    def initializeGUI(self):
        layout = QtGui.QGridLayout()
        self.dropdown = saved_frequencies_dropdown(self.reactor)
        self.duration = durationWdiget(self.reactor)
        self.limits = limitsWidget(self.reactor)
        layout.addWidget(self.duration, 0, 0, 1, 1)
        layout.addWidget(self.dropdown, 0, 1, 1, 1)
        layout.addWidget(self.limits, 1, 0, 1, 2)
        self.setLayout(layout)
    
    def connect_widgets(self):
        self.dropdown.selected_signal.connect(self.limits.center.setValue)
        
    def closeEvent(self, x):
        self.reactor.stop()
        
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = spectrum(reactor)
    widget.show()
    reactor.run()