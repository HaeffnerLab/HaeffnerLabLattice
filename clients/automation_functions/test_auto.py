from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qtui.SliderSpin import SliderSpin
from twisted.internet.defer import inlineCallbacks, returnValue

UpdateTime = 100 #in ms, how often data is checked for communication with the server
SIGNALID = 197566

class auto_gadget(QWidget):
    def __init__(self, reactor, parent=None):
        super(auto_gadget, self).__init__(parent)
        self.reactor = reactor
        self.connect()
           
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.types import Error
        self.cxn = yield connectAsync('192.168.169.49')
        self.server = yield self.cxn.laserdac
        self.registry = yield self.cxn.registry

        #yield self.loadDict()
        #yield self.setupListeners()
        yield self.initializeGUI()
    
    @inlineCallbacks
    def setupListeners(self):
        yield self.server.signal__channel_has_been_updated(SIGNALID)
        yield self.server.addListener(listener = self.followSignal, source = None, ID = SIGNALID)
    
    def followSignal(self, x, (chanName,voltage)):
        widget = self.d[chanName].widget
        widget.setValueNoSignal(voltage)
    
    def sizeHint(self):
        return QSize(800,500)
    
    @inlineCallbacks
    def initializeGUI(self):
        self.load_ion = QPushButton('Load Ion')
        self.load_ion_threshold = QLineEdit('3')

        #self.load_ion.clicked.connect(self.load_ion_func)

        self.setup_experiment = QPushButton('Setup Experiment')
        #self.setup_experiment.clicked.connect(self.setup_experiment_func)

        
        # set layout
        self.layout = QGridLayout()

        self.layout.addWidget(self.load_ion, 0, 0)
        self.layout.addWidget(self.load_ion_threshold, 0, 1)
        self.layout.addWidget(self.setup_experiment, 1, 0)

        self.setLayout(self.layout)

        #start timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.sendToServer)
        self.timer.start(UpdateTime)
    
    @inlineCallbacks
    def getRangefromReg(self, rangeName):
        yield self.registry.cd(['','Clients','Cavity Control'],True)
        try:
            range = yield self.registry.get(rangeName)
            range = list(range)
        except:
            print 'problem with acquiring range from registry'
            range = [0,2500]
        returnValue( range )
    
    #if inputs are updated by user, send the values to server
    @inlineCallbacks
    def sendToServer(self):
        pass

    def closeEvent(self, x):
        self.reactor.stop()  

if __name__=="__main__":
    a = QApplication( [] )
    #import qt4reactor
    import common.clients.qt4reactor as qt4reactor    
    qt4reactor.install()
    from twisted.internet import reactor
    cavityWidget = auto_gadget(reactor)
    cavityWidget.show()
    reactor.run()
