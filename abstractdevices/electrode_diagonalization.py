"""
### BEGIN NODE INFO
[info]
name = Electrode Diagonalization
version = 1.0
description = 
instancename = Electrode Diagonalization

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""


from labrad.server import LabradServer, setting, Signal
from labrad.units import WithUnit
from twisted.internet.defer import inlineCallbacks, returnValue
from numpy import linalg as LA
import numpy as np

SIGNALID = 66060

class compLineScan( LabradServer ):
    """Allows for simple parameterized scanning of the compensation
    The scans are in the form 
    c1 = c1 + r*cos(theta)
    c2 = c2 + r*sin(theta)
    """
    name = 'Compensation LineScan'
    onNewRange = Signal(SIGNALID, 'signal: new range', '(vv)')
    
    def initServer( self ):
        self.load_params_from_registry()
        self.intialize_connections()
        self.listeners = set()
        self.parameters = {}.fromkeys(['comp_angle','endcap_angle'])
    
    @inlineCallbacks
    def load_params_from_registry(self):
        '''
        load the matrix parameters from registry
        '''
        yield None
        pass
        
    @inlineCallbacks
    def intialize_connections(self):
        '''
        connect to DAC and COMPENSATION
        '''
        self.server = self.client.compensation_box
        self.rangec1 = yield self.server.getrange(1)
        self.rangec2 = yield self.server.getrange(2)
        yield self.setAmplitudeRange()


    @setting(0, "Compensation Angle", angle = 'v[rad]', returns='v[rad')
    def compensation_angle(self, c, angle = None):
        '''
        Set or get the compensation angle
        '''
        if angle is not None:
            self.parameters['comp_angle'] = angle['rad']
        return WithUnit(self.parameters['comp_angle'], 'rad')
    
    @setting(1, "Endcap Angle", angle = 'v[rad]', returns='v[rad')
    def endcap_angle(self, c, angle = None):
        '''
        Set or get the compensation angle
        '''
        if angle is not None:
            self.parameters['endcap_angle'] = angle['rad']
        return WithUnit(self.parameters['endcap_angle'], 'rad')
    
    @inlineCallbacks
    def stopServer(self):
        yield None
        
    def initContext(self, c):
        self.listeners.add(c.ID)
    
    def expireContext(self, c):
        self.listeners.remove(c.ID)

if __name__ == "__main__":
#     from labrad import util
#     util.runServer(compLineScan())
    arr = np.array([[1,-1],[1,1]])
    print arr
    print LA.inv(arr)