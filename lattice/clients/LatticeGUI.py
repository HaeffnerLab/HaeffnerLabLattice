from PyQt4 import QtGui, QtCore
import time
from twisted.internet.threads import deferToThread
from twisted.internet.defer import Deferred, inlineCallbacks, returnValue

class LATTICE_GUI(QtGui.QMainWindow):
    def __init__(self, reactor, parent=None):
        super(LATTICE_GUI, self).__init__(parent)
        self.reactor = reactor
        lightControlTab = self.makeLightWidget(reactor)
        voltageControlTab = self.makeVoltageWidget(reactor)
        tableOpticsWidget = self.makeTableOpticsWidget(reactor)
        translationStageWidget = self.makeTranslationStageWidget(reactor)
        self.tabWidget = QtGui.QTabWidget()
        self.tabWidget.addTab(voltageControlTab,'&Trap Voltages')
        self.tabWidget.addTab(lightControlTab,'&LaserRoom')
        self.tabWidget.addTab(tableOpticsWidget,'&Optics')
        self.tabWidget.addTab(translationStageWidget,'&Translation Stages')
        self.createGrapherTab()
        self.setCentralWidget(self.tabWidget)
    
    @inlineCallbacks
    def createGrapherTab(self):
        grapher = yield self.makeGrapherWidget(reactor)
        self.tabWidget.addTab(grapher, '&Grapher')
    
    @inlineCallbacks
    def makeGrapherWidget(self, reactor):
        widget = QtGui.QWidget()
        from pygrapherlive.connections import CONNECTIONS
        from pygrapherlive.connections import COMMUNICATE
        vboxlayout = QtGui.QVBoxLayout()
        Connections = CONNECTIONS(reactor)
        @inlineCallbacks
        def widgetReady():
            window = yield Connections.introWindow
            vboxlayout.addWidget(window)
            widget.setLayout(vboxlayout)
        #yield deferToThread(time.sleep, 3)
        yield Connections.communicate.connectionReady.connect(widgetReady)
        returnValue(widget)

    def makeTranslationStageWidget(self, reactor):
        widget = QtGui.QWidget()
        from APTMotorClient import APTMotorClient
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(APTMotorClient(reactor), 0, 0)
        widget.setLayout(gridLayout)
        return widget
    
    def makeLightWidget(self, reactor):
        widget = QtGui.QWidget()
        from CAVITY_CONTROL import cavityWidget
        from multiplexer.MULTIPLEXER_CONTROL import multiplexerWidget
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(cavityWidget(reactor),0,0)
        gridLayout.addWidget(multiplexerWidget(reactor),0,1)
        widget.setLayout(gridLayout)
        return widget
    
    def makeVoltageWidget(self, reactor):
        widget = QtGui.QWidget()
        from TRAPDRIVE_CONTROL import TRAPDRIVE_CONTROL as trapDriveWidget
        from ENDCAP_CONTROL import ENDCAP_CONTROL as endcapWidget 
        from COMPENSATION_CONTROL import COMPENSATION_CONTROL as compensationWidget
        from DCONRF_CONTROL import DCONRF_CONTROL as dconrfWidget
        #from TRAPDRIVE_MODULATION_CONTROL import TRAPDRIVE_MODULATION_CONTROL as trapModWidget
        from COMPENSATION_LINESCAN import COMPENSATION_LINESCAN_CONTROL as compLineWidget
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(endcapWidget(reactor),0,0,1,2)
        gridLayout.addWidget(compensationWidget(reactor),1,0,1,2)
        gridLayout.addWidget(compLineWidget(reactor),2,1)
        gridLayout.addWidget(trapDriveWidget(reactor),3,0)
        gridLayout.addWidget(dconrfWidget(reactor),3,1)
        #gridLayout.addWidget(trapModWidget(reactor),4,0)
        widget.setLayout(gridLayout)
        return widget
    
    def makeTableOpticsWidget(self, reactor):
        widget = QtGui.QWidget()
        from PMT_CONTROL import pmtWidget
        from SWITCH_CONTROL import switchWidget
        from INTENSITY_CONTROL import INTENSITY_CONTROL as intensityWidget
        #from doublePassWidget import doublePassWidget
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(switchWidget(reactor),0,0)
        gridLayout.addWidget(pmtWidget(reactor),0,1)
        gridLayout.addWidget(intensityWidget(reactor),1,0,1,2)
        #gridLayout.addWidget(doublePassWidget(reactor),2,0,1,2)
        widget.setLayout(gridLayout)
        return widget

    def closeEvent(self, x):
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    latticeGUI = LATTICE_GUI(reactor)
    latticeGUI.setWindowTitle('Lattice GUI')
    latticeGUI.show()
    reactor.run()