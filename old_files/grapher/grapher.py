DIR = 0
DATASET = 1
XPLOT = 'x plot'
YPLOT = 'y plot'
XAXIS = 'X Axis'
YAXIS = 'Y Axis'
COLUMN = 66666
MAP = 55555

from PyQt4 import QtGui

def formatPath( pathList ):
    return ' -> '.join( dir if dir else 'Root' for dir in pathList ) if pathList else 'None'

def formatDSName( dsName ):
    return str( int( dsName[:5] ) ) + ' - ' + dsName[8:]

def getSympyFunc( exp, sympyVars ):
    from sympy import sympify, lambdify
    import numpy
    try:
        foo = lambdify( sympyVars, sympify( exp ), numpy )
        foo( *[1.0 for i in range( len( sympyVars ) )] )
        return foo
    except:
        return False

if __name__ == '__main__':
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    from mainwindow import MainWindow
    MainWindow = MainWindow(reactor)
    MainWindow.show()
    reactor.run()
