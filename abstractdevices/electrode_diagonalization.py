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

class Electrode_Diagonalization( LabradServer ):
    name = 'Electrode Diagonalization'
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
        reg = self.client.registry
        yield reg.cd(['Servers','Electrode Diagonalization'])
        for param in self.parameters:
            self.parameters[param] = yield reg.get(param)
    
    @inlineCallbacks
    def save_params_to_registry(self):
        '''
        save the matrix parameters to registry
        '''
        reg = self.client.registry
        yield reg.cd(['Servers','Electrode Diagonalization'])
        for param, value in self.parameters.iteritems():
            yield reg.set(param, value.inUnitsOf('deg'))
    
    @inlineCallbacks
    def intialize_connections(self):
        '''
        connect to DAC and COMPENSATION
        '''
        try:
            self.dac = self.client.dac
        except AttributeError:
            self.dac = None
        else:
            yield self.get_dac_voltages()
        try:
            self.comp = self.client.shq.shq_222m_server
        except AttributeError:
            self.comp = None
        else:
            yield self.get_comp_voltages()
    
    @inlineCallbacks
    def get_comp_voltages(self):
        try:
            self.vol
        
    @setting(0, "Compensation Angle", angle = 'v[rad]', returns='v[rad]')
    def compensation_angle(self, c, angle = None):
        '''
        Set or get the compensation angle
        '''
        if angle is not None:
            self.parameters['comp_angle'] = angle['rad']
        return WithUnit(self.parameters['comp_angle'], 'rad')
    
    @setting(1, "Endcap Angle", angle = 'v[rad]', returns='v[rad]')
    def endcap_angle(self, c, angle = None):
        '''
        Set or get the compensation angle
        '''
        if angle is not None:
            self.parameters['endcap_angle'] = angle['rad']
        return WithUnit(self.parameters['endcap_angle'], 'rad')
    
    @inlineCallbacks
    def serverConnected( self, ID, name ):
        """Connect to the server"""
        if name == 'SHQ_222M_SERVER':
            self.comp = self.client.shq_222m_server
            yield self.get_comp_voltages()
        if name == 'DAC':
            self.dac = None
            yield self.get_dac_voltages()

    def serverDisconnected( self, ID, name ):
        """Close connection"""
        if name == 'SHQ_222M_SERVER':
            self.comp = None
        if name == 'DAC':
            self.dac = None

    @inlineCallbacks
    def stopServer(self):
        yield self.save_params_to_registry()
        
    def initContext(self, c):
        self.listeners.add(c.ID)
    
    def expireContext(self, c):
        self.listeners.remove(c.ID)

if __name__ == "__main__":
    from labrad import util
    util.runServer(Electrode_Diagonalization())