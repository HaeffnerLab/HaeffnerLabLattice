if __name__=="__main__":
    import sys
    from PyQt4 import QtGui
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    from multiplexer_widgets import multiplexerWidget
    multiplexerWidget = multiplexerWidget()
    reactor.callWhenRunning( multiplexerWidget.show )
    sys.exit( reactor.run() )