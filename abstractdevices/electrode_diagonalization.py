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
from twisted.internet.defer import inlineCallbacks
from numpy import linalg as LA
import numpy as np
from numpy import cos, sin

SIGNALID = 66060

class electrode_diagonalization( LabradServer ):

    name = 'Electrode diagonalization'
    onNewRange = Signal(SIGNALID, 'signal: new range', '(vv)')
    
    def initServer( self ):
        self.load_params_from_registry()
        self.intialize_connections()
        self.listeners = set()
        self.parameters = {}.fromkeys(['comp_angle','endcap_angle'])
        self.voltages = {}.fromkeys(['C1','C2','D1','D2'])
        self.fields = {}.fromkeys['Ex','Ey','Ez','w_z_sq']
        self.voltage_priority = True
    
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
            if self.voltage_priority:
                self.calculate_fields()
            else:
                self.calculate_voltages()
        return WithUnit(self.parameters['comp_angle'], 'rad')
        
    @setting(1, "Endcap Angle", angle = 'v[rad]', returns='v[rad')
    def endcap_angle(self, c, angle = None):
        '''
        Set or get the endcap angle
        '''
        if angle is not None:
            self.parameters['endcap_angle'] = angle['rad']
            if self.voltage_priority:
                self.calculate_fields()
            else:
                self.calculate_voltages()
        return WithUnit(self.parameters['endcap_angle'], 'rad')
    
    @setting(2, "Voltage priority", voltage_priority='b')
    def voltage_priority(self, c, voltage_priority = None):
        '''
        True for voltage priority: when angles are changes voltages will be fixed and field recalculated
        False for field priority: when angles are changes fields are fixed and voltages recalculated
        '''
        if voltage_priority is not None:
            self.voltage_priority = voltage_priority
        return self.voltage_priority
    
    @setting(3, "Voltage", electrode = 's', voltage = 'v[V]')
    def voltage(self, c, electride, voltage = None):
        pass
    
    @setting(4, "Field", fieldname = 's', value = 'v')
    def field(self, c, fieldname, value = None):
        pass
    
    def rotation_matrx(self):
        theta_c = self.parameters['comp_angle']
        theta_d = self.parameters['endcap_angle']
        m = np.array([
                     [cos(theta_c),     -sin(theta_c),      0,      0],
                     [sin(theta_c),      cos(theta_c),      0,      0],
                     [0,                    0,              cos(theta_d),      -sin(theta_d)],
                     [0,                    0,              sin(theta_d),       cos(theta_d)],
                      ])
        return m
    
    def calculate_fields(self):
        m = self.rotation_matrx()
        voltages = [self.voltages[key] for key in ['C1','C2','D1','D2']]
        fields = m * voltages
        self.new_fields()
    
    def new_fields(self):
        pass
    
    def calculate_voltages(self):
        m = self.rotation_matrx()
        m_inv = LA.inv(m)
        fields = [self.fields[key] for key in ['Ex','Ey','Ez','w_z_sq']]
        voltages = m_inv * fields
        self.set_voltages(voltages)
        self.new_voltages(voltages)
    
    def new_voltages(self):
        pass
        
    @inlineCallbacks
    def stopServer(self):
        yield None
        
    def initContext(self, c):
        self.listeners.add(c.ID)
    
    def expireContext(self, c):
        self.listeners.remove(c.ID)

if __name__ == "__main__":
    from labrad import util
    util.runServer(electrode_diagonalization())