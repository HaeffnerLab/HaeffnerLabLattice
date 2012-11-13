from qtui.QCustomFreqPower import QCustomFreqPower
from twisted.internet.defer import inlineCallbacks
from PyQt4 import QtGui, QtCore

class ShortCutter(QtGui.QWidget):
    def __init__(self,reactor, parent=None):
        super(ShortCutter, self).__init__(parent)
        self.reactor = reactor
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync()
        self.server = self.cxn.lattice_pc_hp_server
        self.setupWidget()
        
    def setupWidget(self):
        self.shortcut = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_0), self)
        self.shortcut.activated.connect(self.follow)
    
    def follow(self):
        print 'got it!'
    
    def closeEvent(self, x):
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    ShortCutter = ShortCutter(reactor)
    ShortCutter.show()
    reactor.run()