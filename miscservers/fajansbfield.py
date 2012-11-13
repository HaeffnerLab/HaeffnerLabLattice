from socket import *
import time
from labrad.server import LabradServer, setting
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread


HOST = 'landau.physics.berkeley.edu'
PORT = 8889
ADDR = (HOST,PORT)
BUFSIZE = 1024


class BFieldMonitorServer(LabradServer):
    """Server to monitor magnetic field from the lab across the hall """
    name = "B Field Monitor Server"

    def initServer(self):

        self.listeners = set()  
        self.currentMeasurement = None
        self._setupBuffer()
        
    def _connect(self):
        try:
            self.cli = socket(AF_INET,SOCK_STREAM)
            self.cli.connect((ADDR))        
        except:
            raise Exception('Could not connect.')
    
    def _disconnect(self):
        self.cli.close()
        
    def _setupBuffer(self):
        self.buffer = chr(0x00)
        self.buffer += chr(0x03)
        self.buffer += 'B.0'
    
    @inlineCallbacks
    def _startMeasurement(self):
        #time.strftime("%Y%b%d_%H%M_%S",time.localtime())
#        dv = self.client.data_vault
#        yield dv.cd(['', 'QuickMeasurements', 'FajansBFieldMeasurements'], True)
#        yield dv.new('B-Field', [('Time', '')], [('B Field','','Gauss')])
        while(1):
            self._connect()
            self.cli.send(self.buffer)
            yield deferToThread(time.sleep, 2)
            data = self.cli.recv(BUFSIZE)
            print data
            self.currentMeasurement = data
            self._disconnect()
            #process and add it to datavault
            yield dv.add([])        

    @setting(1, "Get Current Measurement", returns="v")
    def getCurrentMeasurement(self, c, ):
        """Returns the current reading"""
        return self.currentMeasurement

    @setting(2, "Start Measurement", returns="")
    def startMeasurement(self, c, ):
        """Starts the Measurement"""
        yield deferToThread(self._startMeasurement)


if __name__ == "__main__":
    from labrad import util
    util.runServer(BFieldMonitorServer())
