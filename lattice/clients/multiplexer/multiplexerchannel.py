import sys
from PyQt4 import QtGui
from PyQt4 import QtCore,uic
import os
import RGBconverter as RGB

class Multiplexer_Channel(QtGui.QWidget):
    def __init__(self, server, wavelength, parent=None):
        QtGui.QWidget.__init__(self, parent)
        basepath = os.environ.get('LABRADPATH',None)
        if not basepath:
            raise Exception('Please set your LABRADPATH environment variable')
        path = os.path.join(basepath,'lattice/clients/qtui/MultiplexerChannel.ui')
        uic.loadUi(path,self)
        self.server= server
        self.channel = self.server.get_channel_from_wavelength(wavelength)
        self.RGBconverter = RGB.RGBconverter()
        #set initial values
        [r,g,b] = self.RGBconverter.wav2RGB(int(wavelength))
        self.label.setStyleSheet('color:rgb(%d,%d,%d)' %(r,g,b))
        self.label.setText(wavelength + 'nm')
        isSelected = self.channel in server.get_selected_channels()
        self.checkBox.setChecked(isSelected)
        exposure = self.server.get_exposures()[self.channel]
        self.spinBox.setValue(exposure)
        #connect functions
        self.connect(self.checkBox, QtCore.SIGNAL('stateChanged(int)'), self.measureChannel)
        self.connect(self.spinBox, QtCore.SIGNAL('valueChanged(int)'), self.setExposure)
        
    def measureChannel(self, state):
        self.server.toggle_channel(self.channel, self.checkBox.isChecked())

    def setExposure(self, exp):
        self.server.set_exposure(self.channel,exp)
    
    def setText(self, text):
        self.expectedfreq.setText(text)
        
    def setFreq(self,freqlist):
        if self.checkBox.isChecked():
            freq = freqlist[self.channel]
            if freq is not None:
                if float(freq) == -3.0:
                    text = 'UnderExposed'
                elif float(freq) == -4.0:
                    text = 'OverExposed'
                elif float(freq) == -5.0:
                    text = 'NeedStartWM'
                else:
                    text =  '%.5f'%freq
            else:
                text = 'NotMeasured'
        else:
            text = 'NotMeasured'
        self.freq.setText(text)

if __name__=="__main__":
    import labrad
    cxn = labrad.connect()
    server = cxn.multiplexer_server
    app = QtGui.QApplication(sys.argv)
    icon = Multiplexer_Channel(server, wavelength = '866')
    icon.show()
    app.exec_()