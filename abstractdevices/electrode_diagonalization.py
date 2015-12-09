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
from numpy import cos, sin, sqrt

SIGNALID = 66060

class Electrode_Diagonalization( LabradServer ):

    name = 'Electrode Diagonalization'
    on_new_value = Signal(SIGNALID, 'signal: new value', '(sv)')
    
    def initServer( self ):
        self.parameters = {}.fromkeys(['endcap_angle','xz_angle','m0','m2'])
        self.voltages = {}.fromkeys(['C1','C2','D1','D2'])
        self.fields = {}.fromkeys(['Ex','Ey','Ez','w_z_sq'])
        self.voltage_range_comp = None,None
        self.voltage_range_dac = None,None
        self.voltage_priority = True
        self.listeners = set()
        self.load_params_from_registry()
        self.intialize_connections()
    
    @inlineCallbacks
    def load_params_from_registry(self):
        '''
        load the matrix parameters from registry
        '''
        reg = self.client.registry
        yield reg.cd(['','Servers','Electrode Diagonalization'])
        for param in self.parameters:
            self.parameters[param] = yield reg.get(param)
        print self.parameters
    
    @inlineCallbacks
    def save_params_to_registry(self):
        '''
        save the matrix parameters to registry
        '''
        reg = self.client.registry
        yield reg.cd(['','Servers','Electrode Diagonalization'])
        for param, value in self.parameters.iteritems():
            if param in ['comp_angle','endcap_angle']:
                yield reg.set(param, value.inUnitsOf('deg'))
            else:
                yield reg.set(param, value)
    
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
            yield self.get_dac_range()
        try:
            self.comp = self.client.shq_222m_server
        except AttributeError:
            self.comp = None
        else:
            yield self.get_comp_voltages()
            yield self.get_comp_range()
        if self.comp is not None and self.dac is not None:
            new_fields = self.calculate_fields()
            self.fields.update(new_fields)
    
    @inlineCallbacks
    def get_comp_voltages(self):
        for electrode in ['C1','C2']:
            self.voltages[electrode] = yield self.do_get_voltage(electrode)
    
    @inlineCallbacks
    def get_dac_voltages(self):
        for electrode in ['D1','D2']:
            self.voltages[electrode] = yield self.do_get_voltage(electrode)
    
    @inlineCallbacks
    def get_comp_range(self):
        self.voltage_range_comp = yield self.comp.voltage_range()
    
    @inlineCallbacks
    def get_dac_range(self):
        self.voltage_range_dac = yield self.dac.get_range('comp1')
    
    @setting(0, "XZ Angle", angle = 'v[rad]', returns='v[rad]')
    def xz_angle(self, c, angle = None):
        '''
        Set or get the compensation angle
        '''
        if angle is not None:
            self.parameters['xz_angle'] = angle
            if self.voltage_priority:
                new_fields = self.calculate_fields()
                self.fields.update(new_fields)
                self.on_new_fields()
            else:
                new_voltages = self.calculate_voltages()
                #check range first, if this raises error we stop
                for electrode, voltage in new_voltages.iteritems():
                    self.check_range(electrode, voltage)
                self.voltages.update(new_voltages)
                for electrode, voltage in self.voltages.iteritems():
                    yield self.do_set_voltage(electrode, voltage)
                self.on_new_voltages()
            self.notifyOtherListeners(c, ('xz_angle',angle['deg']), self.on_new_value)
        returnValue(self.parameters['xz_angle'])

    @setting(1, "Endcap Angle", angle = 'v[rad]', returns='v[rad]')
    def endcap_angle(self, c, angle = None):
        '''
        Set or get the endcap angle
        '''
        if angle is not None:
            self.parameters['endcap_angle'] = angle
            if self.voltage_priority:
                new_fields = self.calculate_fields()
                self.fields.update(new_fields)
                self.on_new_fields()
            else:
                new_voltages = self.calculate_voltages()
                #check range first, if this raises error we stop
                for electrode, voltage in new_voltages.iteritems():
                    self.check_range(electrode, voltage)
                self.voltages.update(new_voltages)
                for electrode, voltage in self.voltages.iteritems():
                    yield self.do_set_voltage(electrode, voltage)
                self.on_new_voltages()
            self.notifyOtherListeners(c, ('endcap_angle',angle['deg']), self.on_new_value)
        returnValue(self.parameters['endcap_angle'])
    
    @setting(11, "slope m0", value = 'v', returns='v')
    def m0(self, c, value = None):
        if value is not None:
            self.parameters['m0'] = value
            if self.voltage_priority:
                new_fields = self.calculate_fields()
                self.fields.update(new_fields)
                self.on_new_fields()
            else:
                new_voltages = self.calculate_voltages()
                #check range first, if this raises error we stop
                for electrode, voltage in new_voltages.iteritems():
                    self.check_range(electrode, voltage)
                self.voltages.update(new_voltages)
                for electrode, voltage in self.voltages.iteritems():
                    yield self.do_set_voltage(electrode, voltage)
                self.on_new_voltages()
            self.notifyOtherListeners(c, ('m0', value), self.on_new_value)
        returnValue(self.parameters['m0'])
    
    @setting(12, "slope m2", value = 'v', returns='v')
    def m1(self, c, value = None):
        if value is not None:
            self.parameters['m2'] = value
            if self.voltage_priority:
                new_fields = self.calculate_fields()
                self.fields.update(new_fields)
                self.on_new_fields()
            else:
                new_voltages = self.calculate_voltages()
                #check range first, if this raises error we stop
                for electrode, voltage in new_voltages.iteritems():
                    self.check_range(electrode, voltage)
                self.voltages.update(new_voltages)
                for electrode, voltage in self.voltages.iteritems():
                    yield self.do_set_voltage(electrode, voltage)
                self.on_new_voltages()
            self.notifyOtherListeners(c, ('m2', value), self.on_new_value)
        returnValue(self.parameters['m2'])
    
    @setting(2, "Voltage priority", voltage_priority='b')
    def voltage_priority(self, c, voltage_priority = None):
        '''
        True for voltage priority: when angles are changes voltages will be fixed and field recalculated
        False for field priority: when angles are changes fields are fixed and voltages recalculated
        '''
        if voltage_priority is not None:
            self.voltage_priority = voltage_priority
            self.notifyOtherListeners(c, ('priority',voltage_priority), self.on_new_value)
        return self.voltage_priority
    
    @setting(3, "Voltage", electrode = 's', voltage = 'v[V]')
    def voltage(self, c, electrode, voltage = None):
        if electrode not in self.voltages:
            raise Exception('Wrong electrode name')
        if voltage is not None:
            yield self.do_set_voltage(electrode, voltage)
            self.voltages[electrode] = voltage 
            new_fields = self.calculate_fields()
            self.fields.update(new_fields)
            self.on_new_fields()
            self.notifyOtherListeners(c, (electrode,voltage['V']), self.on_new_value)
        else:
            voltage = yield self.do_get_voltage(electrode)
        returnValue(voltage)  
    
    @setting(4, "Field", fieldname = 's', field = 'v', returns = 'v')
    def field(self, c, fieldname, field = None):
        if fieldname not in self.fields:
            raise Exception('Wrong field name')
        if field is not None:
            self.fields[fieldname] = field
            new_voltages = self.calculate_voltages()
            #check range first, if this raises error we stop
            for electrode, voltage in new_voltages.iteritems():
                self.check_range(electrode, voltage)
            self.voltages.update(new_voltages)
            for electrode, voltage in self.voltages.iteritems():
                yield self.do_set_voltage(electrode, voltage)
            self.on_new_voltages()
            self.notifyOtherListeners(c, (fieldname,field), self.on_new_value)
        returnValue(self.fields[fieldname])
    
    @inlineCallbacks
    def do_get_voltage(self, electrode):
        if electrode == 'C1':
            voltage = yield self.comp.voltage(1)
            voltage = -voltage
        elif electrode == 'C2':
            voltage = yield self.comp.voltage(2)
            voltage = -voltage
        elif electrode == 'D1':
            voltage = yield self.dac.get_voltage('comp1') # ??? this is actually the endcap1
        elif electrode == 'D2':
            voltage = yield self.dac.get_voltage('comp2') # ??? this is actually the endcap2
        else:
            raise Exception("Wrong electrode")
        returnValue(voltage)
    
    @inlineCallbacks
    def do_set_voltage(self,electrode, voltage):
        self.check_range(electrode, voltage)
        if electrode == 'C1':
            voltage = -voltage
            yield self.comp.voltage(1, voltage)
        elif electrode == 'C2':
            voltage = -voltage
            yield self.comp.voltage(2, voltage)
        elif electrode == 'D1':
            yield self.dac.set_voltage('comp1', voltage) # ??? this is actually the endcap1
        elif electrode == 'D2':
            yield self.dac.set_voltage('comp2', voltage) # ??? this is actually the endcap2
        else:
            raise Exception("Wrong electrode")
        returnValue(voltage)
    
    def check_range(self, electrode, voltage):
        if electrode in ['C1','C2']:
            voltage = -voltage
            print 'checkig range', electrode, voltage
            minim,maxim = self.voltage_range_comp
        elif electrode in ['D1','D2']:
            minim,maxim = self.voltage_range_dac
        if not minim <= voltage and voltage <= maxim:
            raise Exception( "Voltage out of Range {}".format(electrode)) 
        
    def rotation_matrx(self):
        '''
        returns the rotation matrix M such that
        Voltages = M * fields
        '''
        theta_d = self.parameters['endcap_angle']['rad']
        th = self.parameters['xz_angle']['rad']
        m0 = self.parameters['m0']
        m2 = self.parameters['m2']
        norm = sqrt(m0 **2 + m2 **1 + 1**2)
        R1 = np.array([
                     [1,     0,      0,      0],
                     [0,     1,      0,      0],
                     [0,     0,     cos(theta_d),      sin(theta_d)],
                     [0,     0,     -sin(theta_d),     cos(theta_d)],
                      ])
        v0 = m0 / norm
        v1 = 1. / norm
        v2 = m2 / norm
        
        R2 = np.array([
                       [-v1*cos(th)-v0*v2*sin(th),  v0,     -v0*v2*cos(th)+v1*sin(th),  0.],
                       [ v0*cos(th)-v1*v2*sin(th),  v1,     -v1*v2*cos(th)-v0*sin(th),  0.],
                       [(v0**2 + v1**2)  *sin(th),  v2,     (v0**2 + v1**2)  *cos(th),  0.],
                       [0.,                         0.,     0.,                         1.],
                       ])
        M = R1.dot(R2)
        return M
    
    def calculate_fields(self):
        M = self.rotation_matrx()
        M_inv = LA.inv(M)
        voltages = [self.voltages[key]['V'] for key in ['C1','C2','D1','D2']]
        new_fields = M_inv.dot(voltages)
        field_dict = {}
        for i,field in enumerate(['Ex','Ey','Ez','w_z_sq']):
            field_dict[field] = new_fields[i]
        return field_dict
    
    def calculate_voltages(self):
        M  = self.rotation_matrx()
        fields = [self.fields[key] for key in ['Ex','Ey','Ez','w_z_sq']]
        new_voltages = M.dot(fields)
        voltage_dict = {}
        for i,voltage in enumerate(['C1','C2','D1','D2']):
            voltage_dict[voltage] = WithUnit(new_voltages[i], 'V')
        return voltage_dict
    
    def on_new_voltages(self):
        for electrode, voltage in self.voltages.iteritems():
            self.notifyAllListeners((electrode,voltage['V']), self.on_new_value)
    
    def on_new_fields(self):
        '''
        send out signal that new fields available
        '''
        for fieldname, value in self.fields.iteritems():
            self.notifyAllListeners((fieldname,value), self.on_new_value)
        
    @inlineCallbacks
    def serverConnected( self, ID, name ):
        """Connect to the server"""
        if name == 'SHQ_222M_SERVER':
            self.comp = self.client.shq_222m_server
            yield self.get_comp_voltages()
            yield self.get_comp_range()
        if name == 'DAC':
            self.dac = self.client.dac
            yield self.get_dac_voltages()
            yield self.get_dac_range()

    def serverDisconnected( self, ID, name ):
        """Close connection"""
        if name == 'SHQ_222M_SERVER':
            self.comp = None
        if name == 'DAC':
            self.dac = None

    @inlineCallbacks
    def stopServer(self):
        try:
            yield self.save_params_to_registry()
        except:
            pass
        
    def initContext(self, c):
        self.listeners.add(c.ID)
    
    def expireContext(self, c):
        self.listeners.remove(c.ID)
    
    def notifyOtherListeners(self, context, message, f):
        """
        Notifies all listeners except the one in the given context, executing function f
        """
        notified = self.listeners.copy()
        notified.remove(context.ID)
        f(message,notified)
    
    def notifyAllListeners(self, message, f):
        """
        Notifies all listeners except the one in the given context, executing function f
        """
        notified = self.listeners.copy()
        f(message,notified)

if __name__ == "__main__":
    from labrad import util
    util.runServer(Electrode_Diagonalization())