if __name__=="__main__":
    import sys
    from PyQt4 import QtGui
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    from pmt_widget import pmtWidget
    pmtWidget = pmtWidget()
    reactor.callWhenRunning( pmtWidget.show )
    sys.exit( reactor.run() )