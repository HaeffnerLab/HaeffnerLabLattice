from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks, returnValue

class LATTICE_GUI(QtGui.QMainWindow):
    def __init__(self, reactor, parent=None):
        super(LATTICE_GUI, self).__init__(parent)
        self.reactor = reactor
        self.connect_labrad()

    @inlineCallbacks
    def connect_labrad(self):
        from common.clients.connection import connection
        cxn = connection()
        yield cxn.connect()
        self.create_layout(cxn)
    
    def create_layout(self, cxn):
        lightControlTab = self.makeLightWidget(reactor)
        voltageControlTab = self.makeVoltageWidget(reactor, cxn)
        tableOpticsWidget = self.makeTableOpticsWidget(reactor, cxn)
        histogram = self.make_histogram_widget(reactor, cxn)
        drift_tracker = self.make_drift_tracker_widget(reactor, cxn)
        centralWidget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()
        from common.clients.script_scanner_gui.script_scanner_gui import script_scanner_gui
        script_scanner = script_scanner_gui(reactor, cxn)
        script_scanner.show()
        self.tabWidget = QtGui.QTabWidget()
        self.tabWidget.addTab(voltageControlTab,'&Trap Voltages')
        self.tabWidget.addTab(lightControlTab,'&LaserRoom')
        self.tabWidget.addTab(tableOpticsWidget,'&Optics')
#        self.tabWidget.addTab(translationStageWidget,'&Translation Stages')
        self.tabWidget.addTab(histogram, '&Readout Histogram')
        self.tabWidget.addTab(drift_tracker, '&Drift Tracker')
        self.createGrapherTab()
        layout.addWidget(self.tabWidget)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
    
    def make_drift_tracker_widget(self, reactor, cxn):
        from common.clients.drift_tracker.drift_tracker import drift_tracker
        widget = drift_tracker(reactor, cxn)
        return widget
    
    @inlineCallbacks
    def createGrapherTab(self):
        grapher = yield self.makeGrapherWidget(reactor)
        self.tabWidget.addTab(grapher, '&Grapher')
    
    @inlineCallbacks
    def makeGrapherWidget(self, reactor):
        widget = QtGui.QWidget()
        from common.clients.pygrapherlive.connections import CONNECTIONS
        vboxlayout = QtGui.QVBoxLayout()
        Connections = CONNECTIONS(reactor)
        @inlineCallbacks
        def widgetReady():
            window = yield Connections.introWindow
            vboxlayout.addWidget(window)
            widget.setLayout(vboxlayout)
        yield Connections.communicate.connectionReady.connect(widgetReady)
        returnValue(widget)

    def createExperimentParametersTab(self):
        self.tabWidget.addTab(self.experimentParametersWidget, '&Experiment Parameters')
    
    def make_histogram_widget(self, reactor, cxn):
        from common.clients.readout_histogram import readout_histogram
        widget = readout_histogram(reactor, cxn)
        return widget
    
    def makeTranslationStageWidget(self, reactor):
        widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()
        widget.setLayout(gridLayout)
        return widget
    
    def makeLightWidget(self, reactor):
        widget = QtGui.QWidget()
        from common.clients.CAVITY_CONTROL import cavityWidget
        from common.clients.multiplexer.MULTIPLEXER_CONTROL import multiplexerWidget
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(cavityWidget(reactor),0,0)
        gridLayout.addWidget(multiplexerWidget(reactor),0,1)
        widget.setLayout(gridLayout)
        return widget
    
    def makeVoltageWidget(self, reactor, cxn):
        widget = QtGui.QWidget()
        from ENDCAP_CONTROL import ENDCAP_CONTROL as endcapWidget 
        from COMPENSATION_CONTROL import COMPENSATION_CONTROL as compensationWidget
        from HV_CONTROL import hvWidget
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(endcapWidget(reactor, cxn),0,0,1,1)
        gridLayout.addWidget(compensationWidget(reactor, cxn),1,0,1,1)
        gridLayout.addWidget(hvWidget(reactor), 2,0, 1, 1)
        widget.setLayout(gridLayout)
        return widget
    
    def makeTableOpticsWidget(self, reactor, cxn):
        widget = QtGui.QWidget()
        from common.clients.PMT_CONTROL import pmtWidget
        from common.clients.SWITCH_CONTROL import switchWidget
        from common.clients.DDS_CONTROL import DDS_CONTROL
        from common.clients.LINETRIGGER_CONTROL import linetriggerWidget
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(pmtWidget(reactor),0, 1, 1, 1, alignment = QtCore.Qt.AlignRight)
        gridLayout.addWidget(switchWidget(reactor, cxn),1,0, 1, 2)
        gridLayout.addWidget(linetriggerWidget(reactor, cxn), 0, 0, 1, 1)
        gridLayout.addWidget(DDS_CONTROL(reactor, cxn), 2, 0, 1, 2)
        widget.setLayout(gridLayout)
        return widget

    def closeEvent(self, x):
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import common.clients.qt4reactor as qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    latticeGUI = LATTICE_GUI(reactor)
    latticeGUI.setWindowTitle('Lattice GUI')
    latticeGUI.show()
    reactor.run()