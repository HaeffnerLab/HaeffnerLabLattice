from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks

SIGNALID = 378902

class switchWidget(QtGui.QFrame):
    def __init__(self, reactor, parent=None):
        super(switchWidget, self).__init__(parent)
        #which channels to show and in what order, if None, then shows all
        self.channels = ['axial','866DP','110DP','crystallization','bluePI','729DP','pump']
        self.reactor = reactor
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync()
        self.server = yield self.cxn.pulser
        yield self.initializeGUI()
        yield self.setupListeners()
        
    @inlineCallbacks
    def initializeGUI(self):
        self.d = {}
        #set layout
        layout = QtGui.QGridLayout()
        self.setLayout(layout)
        self.setFrameStyle(0x0001 | 0x0030)
        #get switch names and add them to the layout, and connect their function
        layout.addWidget(QtGui.QLabel('Switches'),0,0)
        switchNames = yield self.server.get_channels()
        switchNames = [el[0] for el in switchNames] #picking first of the tuple
        if self.channels is not None:
            channels = [name for name in self.channels if name in switchNames]
        else:
            channels = switchNames
        for order,name in enumerate(channels):
            #setting up physical container
            groupBox = QtGui.QGroupBox(name) 
            groupBoxLayout = QtGui.QVBoxLayout()
            buttonOn = QtGui.QPushButton('ON')
            buttonOn.setAutoExclusive(True)
            buttonOn.setCheckable(True)
            buttonOff = QtGui.QPushButton('OFF')
            buttonOff.setCheckable(True)
            buttonOff.setAutoExclusive(True)
            buttonAuto = QtGui.QPushButton('Auto')
            buttonAuto.setCheckable(True)
            buttonAuto.setAutoExclusive(True)
            groupBoxLayout.addWidget(buttonOn)
            groupBoxLayout.addWidget(buttonOff)
            groupBoxLayout.addWidget(buttonAuto)
            groupBox.setLayout(groupBoxLayout)
            #setting initial state
            initstate = yield self.server.get_state(name)
            ismanual = initstate[0]
            manstate = initstate[1]
            if not ismanual:
                buttonAuto.setChecked(True)
            else:
                if manstate:
                    buttonOn.setChecked(True)
                else:
                    buttonOff.setChecked(True)
            #adding to dictionary for signal following
            self.d[name] = {}
            self.d[name]['ON'] = buttonOn
            self.d[name]['OFF'] = buttonOff
            self.d[name]['AUTO'] = buttonAuto
            buttonOn.clicked.connect(self.buttonConnectionManualOn(name))
            buttonOff.clicked.connect(self.buttonConnectionManualOff(name))
            buttonAuto.clicked.connect(self.buttonConnectionAuto(name))
            layout.addWidget(groupBox,0,1 + order)
    
    def buttonConnectionManualOn(self, name):
        @inlineCallbacks
        def func(state):
            yield self.server.switch_manual(name, True)
        return func
    
    def buttonConnectionManualOff(self, name):
        @inlineCallbacks
        def func(state):
            yield self.server.switch_manual(name, False)
        return func
    
    def buttonConnectionAuto(self, name):
        @inlineCallbacks
        def func(state):
            yield self.server.switch_auto(name)
        return func
    
    @inlineCallbacks
    def setupListeners(self):
        yield self.server.signal__switch_toggled(SIGNALID)
        yield self.server.addListener(listener = self.followSignal, source = None, ID = SIGNALID)
    
    def followSignal(self, x, (switchName, state)):
        if switchName not in self.d.keys(): return None
        if state == 'Auto':
            button = self.d[switchName]['AUTO']
        elif state == 'ManualOn':
            button = self.d[switchName]['ON']
        elif state == 'ManualOff':
            button = self.d[switchName]['OFF']
        button.setChecked(True)

    def closeEvent(self, x):
        self.reactor.stop()
    
    def sizeHint(self):
        return QtCore.QSize(100,100)
            
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    triggerWidget = switchWidget(reactor)
    triggerWidget.show()
    reactor.run()