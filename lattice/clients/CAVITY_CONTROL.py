if __name__=="__main__":
    import sys
    from PyQt4 import QtGui
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    from cavity_widget import cavityWidget
    cavityWidget = cavityWidget()
    reactor.callWhenRunning( cavityWidget.show )
    sys.exit( reactor.run() )