from PyQt4 import QtGui, QtCore

class LATTICE_GUI(QtGui.QMainWindow):
    def __init__(self, reactor, parent=None):
        super(LATTICE_GUI, self).__init__(parent)
        self.reactor = reactor
        
        lightControlTab = self.makeLightWidget(reactor)
        voltageControlTab = self.makeVoltageWidget(reactor)
        tableOpticsWidget = self.makeTableOpticsWidget(reactor)
        tabWidget = QtGui.QTabWidget()
        tabWidget.addTab(voltageControlTab,'&Trap Voltages')
        tabWidget.addTab(lightControlTab,'&LaserRoom')
        tabWidget.addTab(tableOpticsWidget,'&Optics')
        self.setCentralWidget(tabWidget)
    
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
        from TRAPDRIVE_MODULATION_CONTROL import TRAPDRIVE_MODULATION_CONTROL as trapModWidget
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(endcapWidget(reactor),0,0,1,2)
        gridLayout.addWidget(compensationWidget(reactor),1,0,1,2)
        gridLayout.addWidget(trapDriveWidget(reactor),2,0)
        gridLayout.addWidget(dconrfWidget(reactor),2,1)
        gridLayout.addWidget(trapModWidget(reactor),3,0)
        widget.setLayout(gridLayout)
        return widget
    
    def makeTableOpticsWidget(self, reactor):
        widget = QtGui.QWidget()
        from PMT_CONTROL import pmtWidget
        from TRIGGER_CONTROL import triggerWidget
        from INTENSITY_CONTROL import INTENSITY_CONTROL as intensityWidget
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(triggerWidget(reactor),0,0)
        gridLayout.addWidget(pmtWidget(reactor),0,1)
        gridLayout.addWidget(intensityWidget(reactor),1,0,1,2)
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
    latticeGUI.show()
    reactor.run()