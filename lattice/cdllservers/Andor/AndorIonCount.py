from ctypes import *
import time
from PIL import Image
import sys
import numpy as np
import time
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread
from labrad.server import LabradServer, setting, Signal
from AndorServer import Andor, AndorServer

class AndorIonCount(LabradServer, AndorServer):
    """ Contains methods that count ions in pictures taken by the Andor Luca"""
    
    name = "Andor Ion Count"

    def initServer(self):

        self.listeners = set()  
        self.prepareCamera()

    def initContext(self, c):
        """Initialize a new context object."""
        self.listeners.add(c.ID)
    
    def expireContext(self, c):
        self.listeners.remove(c.ID)
        
    def getOtherListeners(self,c):
        notified = self.listeners.copy()
        notified.remove(c.ID)
        return notified


    @setting(40, "Count Ions", threshold = 'i', iterations = 'i', returns = 'i')
    def countIons(self, c, threshold, iterations):
        """Given the iterations, will return the average number of ions"""
        self.camera.GetStatus()
        status = self.camera.status
        if (status == 'DRV_IDLE'):
            numKin = 2*iterations
            self.camera.SetAcquisitionMode(3)
            self.camera.SetNumberKinetics(numKin)
            self.camera.SetKineticCycleTime(0.02)
            print 'Starting Acqusition (Ion Count)'
            yield deferToThread(self.camera.StartAcquisitionKinetic, numKin)
            yield self.camera.GetAcquiredDataKinetic(numKin)
            data = np.array(self.camera.imageArray)
            returnValue(int(data[2]))
            
        else:
            raise Exception(status)
    
if __name__ == "__main__":
    from labrad import util
    util.runServer(AndorIonCount())