from PyQt4 import QtGui, QtCore, uic

if __name__=="__main__":
    import sys
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    from MULTIPLEXER_CONTROL_test import MULTIPLEXER_CONTROL_test
    MULTIPLEXER_CONTROL = MULTIPLEXER_CONTROL_test()
    reactor.callWhenRunning( MULTIPLEXER_CONTROL.show )
    sys.exit( reactor.run() )