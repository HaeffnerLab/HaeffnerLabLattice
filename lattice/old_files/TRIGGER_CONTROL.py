from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks

SIGNALID = 378902

class triggerWidget(QtGui.QFrame):
    def __init__(self, reactor, parent=None):
        super(triggerWidget, self).__init__(parent)
        self.setFrameStyle(0x0001 | 0x0030)
        self.reactor = reactor
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync()
        self.server = yield self.cxn.trigger
        yield self.initializeGUI()
        yield self.setupListeners()
        
    @inlineCallbacks
    def initializeGUI(self):
        self.d = {'Switches':{},'Triggers':{}}
        #set layout
        layout = QtGui.QGridLayout()
        self.setLayout(layout)
        #get switch names and add them to the layout, and connect their function
        layout.addWidget(QtGui.QLabel('Switches'),0,0)
        switchNames = yield self.server.get_switching_channels()
        for order,name in enumerate(switchNames):
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
            self.d['Switches'][name] = {}
            self.d['Switches'][name]['ON'] = buttonOn
            self.d['Switches'][name]['OFF'] = buttonOff
            self.d['Switches'][name]['AUTO'] = buttonAuto
            buttonOn.clicked.connect(self.buttonConnectionManualOn(name))
            buttonOff.clicked.connect(self.buttonConnectionManualOff(name))
            buttonAuto.clicked.connect(self.buttonConnectionAuto(name))
            layout.addWidget(groupBox,0,1 + order)
        #do same for trigger channels
        layout.addWidget(QtGui.QLabel('Triggers'),1,0)
        triggerNames = yield self.server.get_trigger_channels()
        for order,name in enumerate(triggerNames):
            button = QtGui.QPushButton(name)
            button.clicked.connect(self.triggerConnection(name))
            self.d['Triggers'][name] = button
            layout.addWidget(button,1,1 + order)
    
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
    
    def triggerConnection(self, name):
        @inlineCallbacks
        def func(state):
            yield self.server.trigger(name)
        return func
    
    @inlineCallbacks
    def setupListeners(self):
        yield self.server.signal__switch_toggled(SIGNALID)
        yield self.server.addListener(listener = self.followSignal, source = None, ID = SIGNALID)
    
    def followSignal(self, x, (switchName, state)):
        if state == 'Auto':
            button = self.d['Switches'][switchName]['AUTO']
        elif state == 'ManualOn':
            button = self.d['Switches'][switchName]['ON']
        elif state == 'ManualOff':
            button = self.d['Switches'][switchName]['OFF']
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
    triggerWidget = triggerWidget(reactor)
    triggerWidget.show()
    reactor.run()