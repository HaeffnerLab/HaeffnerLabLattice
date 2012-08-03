import time
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
from PyQt4 import QtGui, QtCore
from script import Script
from script2 import Script2

class Parent(QtGui.QWidget):
    def __init__(self,reactor, parent=None):
        QtGui.QWidget.__init__(self)
        self.reactor = reactor
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync()
        self.setupWidget()
        
    def setupWidget(self):
        self.setGeometry(300, 300, 250, 150)
        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(5)
        
        singleButton = QtGui.QPushButton("Run Script", self)
        singleButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        singleButton.clicked.connect(self.runScript)

        singleButton2 = QtGui.QPushButton("Run Script2", self)
        singleButton2.setGeometry(QtCore.QRect(0, 0, 30, 30))
        singleButton2.clicked.connect(self.runScript2)
        
        backgroundButton = QtGui.QPushButton("Start Background Process", self)
        backgroundButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        backgroundButton.clicked.connect(self.startBackgroundProcess)
        
        self.spinBox = QtGui.QSpinBox()
        self.spinBox.setRange(0, 100000)
        self.spinBox.setSingleStep(1)
        
        self.grid.addWidget(singleButton, 0, 0, QtCore.Qt.AlignCenter)
        self.grid.addWidget(singleButton2, 1, 0, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.spinBox, 0, 1, QtCore.Qt.AlignCenter)
        self.grid.addWidget(backgroundButton, 0, 2, QtCore.Qt.AlignCenter)
        self.setLayout(self.grid)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        self.show()
    
    def runScript(self):
        script = Script()
        script.start()        

    def runScript2(self):
        self.cxn.semaphore.set_flag(True)      
        # here you should subscribe to a signal that gets fired when semaphore starts blocking!
        script2 = Script2()
        script2.start()        
    
    @inlineCallbacks
    def startBackgroundProcess(self, evt):
        server = self.cxn.external_server
        semaphore = self.cxn.semaphore
        for i in range(100000):
            yield deferToThread(time.sleep, 2)
            number = yield server.get_number()
            self.spinBox.setValue(number)
            if (number % 10 == 0):
                semaphore.set_flag(True)
            else:
                semaphore.set_flag(False)
   
    def closeEvent(self, x):
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    parent = Parent(reactor)
    reactor.run()
