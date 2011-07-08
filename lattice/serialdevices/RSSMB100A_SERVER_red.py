from serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from labrad.types import Error
from twisted.internet import reactor
from twisted.internet.defer import returnValue

TIMEOUT = 1.0

class RSred(SerialDeviceServer):
    """Controls Rohde and Schwartz SMB100A Signal Generator"""
    name = "%LABRADNODE% RS Server red"
    regKey = 'RSred'
    port = None
    serNode = 'lattice-pc'
    timeout = TIMEOUT
    gpibaddr = 0
    
    @inlineCallbacks
    def initServer( self ):
        self.createDict()
        if not self.regKey or not self.serNode: raise SerialDeviceError( 'Must define regKey and serNode attributes' )
        port = yield self.getPortFromReg( self.regKey )
        self.port = port
        try:
            serStr = yield self.findSerial( self.serNode )
            self.initSerial( serStr, port )
        except SerialConnectionError, e:
            self.ser = None
            if e.code == 0:
                print 'Could not find serial server for node: %s' % self.serNode
                print 'Please start correct serial server'
            elif e.code == 1:
                print 'Error opening serial connection'
                print 'Check set up and restart serial server'
            else: raise
        
        self.ser.write(self.SetAddrStr(self.gpibaddr)) #set gpib address
        yield self.populateDict()
        print self.rsDict
        
    def createDict(self):
        d = {}
        d['state'] = None
        d['power'] = None
        d['freq'] = None
        self.rsDict = d
    
    @inlineCallbacks
    def populateDict(self):
        state = yield self.GetState(-1) #using fake context of -1
        freq = yield self.GetFreq(-1)
        power = yield self.GetPower(-1)
        self.rsDict['state'] = float(state)
        self.rsDict['power'] = float(power)
        self.rsDict['freq'] = float(freq)/10.**6 #to get to Mhz 
        
    @setting(1, "Identify", returns='s')
    def Identify(self, c):
        '''Ask instrument to identify itself'''
        self.SetControllerWait(1) #expect a reply from instrument
        command = self.IdenStr()
        self.ser.write(command)
        answer = self.ser.readline()
        return answer

    @setting(2, "GetFreq", returns='v')
    def GetFreq(self,c):
        '''Returns current frequency in Hz'''
        if self.rsDict['freq'] is not None:
            answer = self.rsDict['freq']
        else:
            self.SetControllerWait(1) #expect a reply from instrument
            command = self.FreqReqStr()
            self.ser.write(command)
            answer = self.ser.readline()
        return answer

    @setting(3, "SetFreq", freq = 'v', returns = "")
    def SetFreq(self,c,freq):
        '''Sets frequency, enter value in MHZ'''
        self.SetControllerWait(0) #expect no reply from instrument
        command = self.FreqSetStr(freq)
        self.ser.write(command)
        self.rsDict['freq'] = freq
        print self.rsDict
      
    @setting(4, "GetState", returns='w')
    def GetState(self,c):
        '''Request current on/off state of instrument'''
        if self.rsDict['state'] is not None:
            answer = int(self.rsDict['state'])
        else:
            self.SetControllerWait(1) #expect a reply from instrument
            command = self.StateReqStr()
            self.ser.write(command)
            answer = yield self.ser.readline()
            answer = int(answer)
        returnValue( answer )
    
    @setting(5, "SetState", state= 'w', returns = "")
    def SetState(self,c, state):
        '''Sets on/off (enter 1/0)'''
        self.SetControllerWait(0) #expect no reply from instrument
        command = self.StateSetStr(state)
        self.ser.write(command)
        self.rsDict['state'] = state
    
    @setting(6, "GetPower", returns = 'v')
    def GetPower(self,c):
        ''' Returns current power level in dBm'''
        if self.rsDict['power'] is not None:
            answer = self.rsDict['power']
        else:
            self.SetControllerWait(1) #expect a reply from instrument
            command = self.PowerReqStr()
            self.ser.write(command)
            answer = self.ser.readline()
        return answer
    
    @setting(7, "SetPower", level = 'v',returns = "")
    def SetPower(self,c, level):
        '''Sets power level, enter power in dBm'''
        self.SetControllerWait(0) #expect no reply from instrument
        command = self.PowerSetStr(level)
        self.ser.write(command)
        self.rsDict['power'] = level
	
    #send message to controller to indicate whether or not (status = 1 or 0)
    #a response is expected from the instrument
    def SetControllerWait(self,status):
	command = self.WaitRespStr(status) #expect response from instrument
	self.ser.write(command)
  
    def IdenStr(self):
	return '*IDN?'+'\n'
	
    # string to request current frequency
    def FreqReqStr(self):
	return 'SOURce:FREQuency?'+'\n'
	      
    # string to set freq (in MHZ)
    def FreqSetStr(self,freq):
	return 'SOURce:FREQuency '+ str(freq) +'MHZ'+'\n'
	  
    # string to request on/off?
    def StateReqStr(self):
	return 'OUTput:STATe?'+'\n'

    # string to set on/off (state is given by 0 or 1)
    def StateSetStr(self, state):
	return 'OUTput:STATe '+ str(state) +'\n'

    # string to request current power
    def PowerReqStr(self):
	return 'POWer?'+'\n'

    # string to set power (in dBm)
    def PowerSetStr(self,pwr):
	return 'POWer '+ str(pwr)+'\n'
	  
    # string for prologix to request a response from instrument, wait can be 0/1
    def WaitRespStr(self, wait):
	return '++auto '+ str(wait) + '\n'
	  
    # string to set the addressing of the prologix
    def SetAddrStr(self, addr):
	return '++addr ' + str(addr) + '\n'

if __name__ == "__main__":
    from labrad import util
    util.runServer(RSred())
