#import labrad
#import numpy
#import time
#from msvcrt import getch, kbhit
#
#cxn = labrad.connect()
#cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
#rf = cxn.trap_drive
#dc = cxn.dc_box
#ld = cxnlab.laserdac
#pulser = cxn.pulser
#
#def kbfunc():
#    x = kbhit()
#    if x:
#        ret = getch()
#    else:
#        ret = 0
#    return ret
#
#ch = '397'
#initcavity = ld.getvoltage(ch) 
#initpower = rf.amplitude()
#min = initcavity - 20
#
#print 're-crystallization script running..'
#print initcavity, min, initpower
#
#while 1:
#	key = kbfunc()
#	#initpower = rf.amplitude()
#	if key == "\r": #\x1b
#    		print 'Resetting rf & Switching on far-red beam..'		
#		time.sleep(0.1)
#    		rf.amplitude(-7.0)
#		pulser.switch_manual('crystallization',  True) # crystallization shutter open
#		pulser.switch_manual('110DP',  False) # 110DP off 
#		#dc.setendcap(1,0.695)
#		#dc.setendcap(2,5.305)
#		time.sleep(2)	
#		pulser.switch_manual('110DP',  True)
#		#pulser.switch_manual('crystallization',  False)
#		rf.amplitude(initpower)
#		#dc.setendcap(1,3.695)
#		#dc.setendcap(2,8.305)
#   		#for voltage in numpy.arange(initcavity, min, -1):
#   		 #   print voltage
#   		 #   time.sleep(0.05)
#   		 #   ld.setvoltage(ch,voltage)
# 
import time
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
from PyQt4 import QtGui, QtCore

class ShortCutter(QtGui.QWidget):
    def __init__(self,reactor, parent=None):
        QtGui.QWidget.__init__(self)
        self.reactor = reactor
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync()
        self.rf = self.cxn.trap_drive
        self.pulser = self.cxn.pulser
        self.setupWidget()
        
    def setupWidget(self):
        self.setGeometry(300, 300, 250, 150)
        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(5)
        
        singleButton = QtGui.QPushButton("Recrystalize!", self)
        singleButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        singleButton.clicked.connect(self.recrystallize)
        
        self.shortcut = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_X), self)
        self.shortcut.activated.connect(self.recrystallize)
        
        shortcutLabel = QtGui.QLabel()
        shortcutLabel.setText('Ctrl-X')
 
        self.grid.addWidget(singleButton, 0, 0, QtCore.Qt.AlignCenter)
        self.grid.addWidget(shortcutLabel, 0, 1, QtCore.Qt.AlignCenter)
        self.setLayout(self.grid)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        self.show()

    @inlineCallbacks    
    def recrystallize(self, evt = None):
        print 'Resetting rf & Switching on far-red beam..'  
        initpower = yield self.rf.amplitude()      
        yield deferToThread(time.sleep, 0.1)
        yield self.rf.amplitude(-7.0)
        yield self.pulser.switch_manual('crystallization',  True) # crystallization shutter open
        yield self.pulser.switch_manual('110DP',  False) # 110DP off 
        #dc.setendcap(1,0.695)
        #dc.setendcap(2,5.305)
        yield deferToThread(time.sleep, 2.0)  
        yield self.pulser.switch_manual('110DP',  True)
        yield self.pulser.switch_manual('crystallization',  False)
        yield self.rf.amplitude(initpower)
        #dc.setendcap(1,3.695)
        #dc.setendcap(2,8.305)
           #for voltage in numpy.arange(initcavity, min, -1):
            #   print voltage
            #   time.sleep(0.05)
            #   ld.setvoltage(ch,voltage)

    
    def closeEvent(self, x):
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    ShortCutter = ShortCutter(reactor)
    #ShortCutter.show()
    reactor.run()
