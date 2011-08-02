if __name__=="__main__":
    import sys
    from PyQt4 import QtGui
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    from trapdriveWidget import TRAPDRIVE_CONTROL
    trapdriveWidget = TRAPDRIVE_CONTROL()
    reactor.callWhenRunning( trapdriveWidget.show )
    sys.exit( reactor.run() )