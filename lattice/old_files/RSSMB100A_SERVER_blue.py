from labrad.server import LabradServer, setting
import serial 

class DCServer(LabradServer):
    """Controls Rohde and Schwartz SMB100A Signal Generator"""
    name = "%LABRADNODE% RS Server blue"
    
    def initServer( self ):
        #communication configuration
        self._port = 'COM16'
        self._addr = 0 #instruments GPIB address
        self._wait = 1 #instrument response requested
        #initialize communication
        self._ser = serial.Serial(self._port)
        self._ser.timeout = 1
        self._ser.write(self.SetAddrStr(self._addr))
        
    @setting(1, "Identify", returns='s')
    def Identify(self, c):
	'''Ask instrument to identify itself'''
	self.SetControllerWait(1) #expect a reply from instrument
	command = self.IdenStr()
	self._ser.write(command)
	#time.sleep(self._waitTime) ## apperently not needed, communication fast
	answer = self._ser.readline()
	return answer

    @setting(2, "GetFreq", returns='v')
    def GetFreq(self,c):
	'''Returns current frequency'''
	self.SetControllerWait(1) #expect a reply from instrument
	command = self.FreqReqStr()
	self._ser.write(command)
	answer = self._ser.readline()
	return answer

    @setting(3, "SetFreq", freq = 'v', returns = "")
    def SetFreq(self,c,freq):
	'''Sets frequency, enter value in MHZ'''
	self.SetControllerWait(0) #expect no reply from instrument
	command = self.FreqSetStr(freq)
	self._ser.write(command)
      
    @setting(4, "GetState", returns='w')
    def GetState(self,c):
	'''Request current on/off state of instrument'''
	self.SetControllerWait(1) #expect a reply from instrument
	command = self.StateReqStr()
	self._ser.write(command)
	answer = int(self._ser.readline())
	return answer
    
    @setting(5, "SetState", state= 'w', returns = "")
    def SetState(self,c, state):
	'''Sets on/off (enter 1/0)'''
	self.SetControllerWait(0) #expect no reply from instrument
	command = self.StateSetStr(state)
	self._ser.write(command)
    
    @setting(6, "GetPower", returns = 'v')
    def GetPower(self,c):
	''' Returns current power level in dBm'''
	self.SetControllerWait(1) #expect a reply from instrument
	command = self.PowerReqStr()
	self._ser.write(command)
	answer = self._ser.readline()
	return answer
    
    @setting(7, "SetPower", level = 'v',returns = "")
    def SetPower(self,c, level):
	'''Sets power level, enter power in dBm'''
	self.SetControllerWait(0) #expect no reply from instrument
	command = self.PowerSetStr(level)
	self._ser.write(command)
	
    #send message to controller to indicate whether or not (status = 1 or 0)
    #a response is expected from the instrument
    def SetControllerWait(self,status):
	command = self.WaitRespStr(status) #expect response from instrument
	self._ser.write(command)
  
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
    util.runServer(DCServer())
