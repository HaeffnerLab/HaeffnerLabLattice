\from PyQt4.QtGui import *
from twisted.internet.defer import inlineCallbacks, returnValue
from common.clients.connection import connection


import sys
import time
#import labrad
import os

class auto_gadget(QWidget):
    def __init__(self, reactor, clipboard = None, cxn = None, parent = None):
        super(auto_gadget, self).__init__()
        
        self.reactor = reactor
        #self.cxn = cxn
        self.cxn = connection()
        self.cxn.connect()
        print self.cxn


        self.setup_labrad()

        self.load_ion = QPushButton('Load Ion')
        self.load_ion_threshold = QLineEdit('3')

        self.load_ion.clicked.connect(self.load_ion_func)

        self.setup_experiment = QPushButton('Setup Experiment')
        self.setup_experiment.clicked.connect(self.setup_experiment_func)

        
        # set layout
        self.layout = QGridLayout()

        self.layout.addWidget(self.load_ion, 0, 0)
        self.layout.addWidget(self.load_ion_threshold, 0, 1)
        self.layout.addWidget(self.setup_experiment, 1, 0)

        self.setLayout(self.layout)

    def setup_labrad(self):
        print "Loading server"
        print self.cxn._servers        
        #self.server = self.cxn.get_server('DDS_CW')        
        #print self.server
        print "done"
        #self.cxn = labrad.connect()
        #self.multiplexer = labrad.connect('192.168.169.49')

    def load_ion_func(self):
	threshold = float(self.load_ion_threshold.text())

        print "Loading Ion with threshold " +  str(threshold)
        self.cxn.pulser.switch_manual('bluePI', True)
        time.sleep(1.0)

        ampl_397 = self.cxn.pulser.amplitude('global397')

        self.cxn.pulser.amplitude('global397', labrad.units.Value(-12, 'dBm'))
        counts = 0.0
        while counts < threshold: 

            # get PMT counts
            counts = self.cxn.normalpmtflow.get_next_counts('ON', 1, True)
            # switch off blue PI, if above threshold
            if counts > threshold:
                self.cxn.pulser.switch_manual('bluePI', False)
                print "Loaded an ion ..."

                time.sleep(0.5)
        self.cxn.pulser.amplitude('global397', labrad.units.Value(ampl_397.value, 'dBm'))

    def setup_experiment_func(self):

        os.system('ipython /home/lattice/LabRAD/lattice/scripts/experiments/Experiments729/setup_experiment.py')
        




#if __name__ == '__main__':
#	app = QApplication(sys.argv)
#	myWindow = auto_gadget()
#	myWindow.show()
#	app.exec_()

 
if __name__=="__main__":
    a = QApplication( [] )
    import common.clients.qt4reactor as qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    #cxn = connection()
    #cxn.connect()
    trapdriveWidget = auto_gadget(reactor)
    trapdriveWidget.show()
    reactor.run()
