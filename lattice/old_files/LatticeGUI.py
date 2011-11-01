import sys
import os
from PyQt4 import QtGui
from PyQt4 import QtCore,uic
import labrad

import COMPENSATION_CONTROL
import ENDCAP_CONTROL
import CAVITY_CONTROL
#import SHUTTER_CONTROL
import PAULBOX_CONTROL
import TRAPDRIVE_CONTROL
import AOMRED_CONTROL
#import TRAPDRIVE_MODULATION_CONTROL
import multiplexer.MULTIPLEXER_CONTROL as MULTIPLEXER_CONTROL
import PMT_CONTROL
import TIME_RESOLVED_CONTROL
zz
import DCONRF_CONTROL
import COMPENSATION_LINESCAN

class LATTICE_GUI(QtGui.QMainWindow):
    def __init__(self, LabRADcxn,cxn2, parent=None):
        QtGui.QWidget.__init__(self, parent)
        basepath = os.environ.get('LABRADPATH',None)
        if not basepath:
            raise Exception('Please set your LABRADPATH environment variable')
        path = os.path.join(basepath,'lattice/clients/qtui/latticeGUI.ui')
        uic.loadUi(path,self)
        self.LabRADcxn = LabRADcxn
        self.cxn2 = cxn2
        startServers = ['dc_box','compensation_box','lattice_pc_hp_server','laserdac','paul_box',
                        'lattice_pc_rs_server_blue','lattice_pc_rs_server_red','lattice_pc_agilent_33220a_server',
                        'multiplexer_server', 'pmt_server','time_resolved_server']
        for server in startServers:
            if server in runningServers:
                self.loadGui(server)
            else:
                print 'Please start ', server
        
        startClients = ['experimenter']
        for client in startClients:
            self.loadGui(client)
            self.setupShorcuts()
      
    def loadGui(self,name):
        if name == 'dc_box':
            self.verticalLayoutDC.addWidget(ENDCAP_CONTROL.ENDCAP_CONTROL(self.LabRADcxn.dc_box))
            #self.verticalLayoutFreq_2.addWidget(SHUTTER_CONTROL.SHUTTER_CONTROL(self.LabRADcxn.dc_box))
            self.verticalLayoutFreq_2.addWidget(INTENSITY_CONTROL.INTENSITY_CONTROL(self.LabRADcxn))
        elif name == 'compensation_box':
            self.verticalLayoutDC.addWidget(COMPENSATION_CONTROL.COMPENSATION_CONTROL(self.LabRADcxn.compensation_box))
            self.verticalLayoutDC.addWidget(COMPENSATION_LINESCAN.COMPENSATION_LINESCAN_CONTROL(self.cxn2))
            self.verticalLayoutDC.addWidget(DCONRF_CONTROL.DCONRF_CONTROL(self.LabRADcxn.dc_box))#assumes it's running
        elif name =='lattice_pc_hp_server':
            pass
            #self.verticalLayoutDC.addWidget(TRAPDRIVE_CONTROL.TRAPDRIVE_CONTROL(self.LabRADcxn.lattice_pc_hp_server))
        elif name == 'laserdac':
            pass
            #self.verticalLayoutFreq.addWidget(CAVITY_CONTROL.CAVITY_CONTROL(self.LabRADcxn))
        elif name == 'paul_box':
            self.verticalLayoutPB.addWidget(PAULBOX_CONTROL.PAULBOX_CONTROL(self.LabRADcxn.paul_box))
        elif name =='lattice_pc_rs_server_red':
            self.verticalLayoutFreq_2.addWidget(AOMRED_CONTROL.AOMRED_CONTROL(self.LabRADcxn.lattice_pc_rs_server_red))
        elif name == 'lattice_pc_agilent_33220a_server':
            self.verticalLayoutDC.addWidget(TRAPDRIVE_MODULATION_CONTROL.TRAPDRIVE_MODULATION_CONTROL(self.LabRADcxn.lattice_pc_agilent_33220a_server))
        elif name == 'experimenter':
            self.tab_4.layout().addWidget(LREXP(self, QtCore.Qt.Widget))
        elif name == 'multiplexer_server':
            pass
            #self.verticalLayoutFreq_3.addWidget(MULTIPLEXER_CONTROL.MULTIPLEXER_CONTROL(self.LabRADcxn.multiplexer_server))
        elif name == 'pmt_server':
            self.verticalLayoutFreq_2.addWidget(PMT_CONTROL.PMT_CONTROL(self.LabRADcxn.pmt_server))
        elif name == 'time_resolved_server':
            self.verticalLayoutFreq_2.addWidget(TIME_RESOLVED_CONTROL.TIME_RESOLVED_CONTROL(self.LabRADcxn.time_resolved_server))
     
    def setupShorcuts(self):
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+1"), self, lambda : self.tabWidget.setCurrentIndex(0) )
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+2"), self, lambda : self.tabWidget.setCurrentIndex(1) )
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+3"), self, lambda : self.tabWidget.setCurrentIndex(2) )
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+4"), self, lambda : self.tabWidget.setCurrentIndex(3) )
        
cxn = labrad.connect()
cxn2 = labrad.connect() #### make better later
runningServers = [x for x in cxn.servers]
app = QtGui.QApplication(sys.argv)
from lrexp.experimenter.mainwindow import MainWindow as LREXP
icon = LATTICE_GUI(cxn, cxn2)
icon.show()
app.exec_()