from PyQt4 import QtGui, QtCore
from scheduled_widget import scheduled_combined
from running_scans_widget import running_combined
from queued_widget import queued_combined

class script_scanner_gui(QtGui.QWidget):
    def __init__(self, reactor):
        super(script_scanner_gui, self).__init__()
        self.reactor = reactor
        self.setupLayout()
        
    def setupLayout(self):
        layout = QtGui.QVBoxLayout()
        running = running_combined(self.reactor)
        scheduled = scheduled_combined(self.reactor)
        queued = queued_combined(self.reactor)
        layout.addWidget(scheduled)
        layout.addWidget(queued)
        layout.addWidget(running)
        self.setLayout(layout)
        
    def closeEvent(self, event):
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication( ["Script Scanner"] )
    from common.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = script_scanner_gui(reactor)
    widget.show()
    reactor.run()