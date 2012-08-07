import time
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
from PyQt4 import QtGui, QtCore


class ScriptControl(QtGui.QWidget):
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

        blockButton = QtGui.QPushButton("Block Script 1", self)
        blockButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        blockButton.clicked.connect(self.blockScript1)

        singleButton2 = QtGui.QPushButton("Run Script2", self)
        singleButton2.setGeometry(QtCore.QRect(0, 0, 30, 30))
        singleButton2.clicked.connect(self.runScript2)

        singleButton3 = QtGui.QPushButton("Run Script3", self)
        singleButton3.setGeometry(QtCore.QRect(0, 0, 30, 30))
        singleButton3.clicked.connect(self.runScript3)

        singleButton4 = QtGui.QPushButton("Run Script4", self)
        singleButton4.setGeometry(QtCore.QRect(0, 0, 30, 30))
        singleButton4.clicked.connect(self.runScript4)
        
        backgroundButton = QtGui.QPushButton("Start Background Process", self)
        backgroundButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        backgroundButton.clicked.connect(self.startBackgroundProcess)
        
        self.spinBox = QtGui.QSpinBox()
        self.spinBox.setRange(0, 100000)
        self.spinBox.setSingleStep(1)
        
        self.grid.addWidget(singleButton, 0, 0, QtCore.Qt.AlignCenter)
        self.grid.addWidget(singleButton2, 1, 0, QtCore.Qt.AlignCenter)
        self.grid.addWidget(blockButton, 1, 1, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.spinBox, 0, 1, QtCore.Qt.AlignCenter)
        self.grid.addWidget(backgroundButton, 0, 2, QtCore.Qt.AlignCenter)
        self.grid.addWidget(singleButton3, 2, 0, QtCore.Qt.AlignCenter)
        self.grid.addWidget(singleButton4, 2, 1, QtCore.Qt.AlignCenter)
        self.setLayout(self.grid)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        self.show()

    def closeEvent(self, x):
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    scriptControl = ScriptControl(reactor)
    reactor.run()

