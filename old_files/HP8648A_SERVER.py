from labrad.server import LabradServer, setting
import serial 

class HPServer(LabradServer):
    """Controls HP8648A Signal Generator"""
    name = "%LABRADNODE% HP Server"
    
    def initServer( self ):
        #communication configuration
        self._port = 'COM14'
        self._addr = 0 #instruments GPIB address
        #initialize communication
        self._ser = serial.Serial(self._port)
        self._ser.timeout = 1
        self._ser.write(self.SetAddrStr(self._addr)) #set address
        self.SetControllerWait(0) #turns off automatic listen after talk, necessary to stop line unterminated errors
    @setting(1, "Identify", returns='s')
    def Identify(self, c):
	'''Ask instrument to identify itself'''
	command = self.IdenStr()
	self._ser.write(command)
	self.ForceRead() #expect a reply from instrument
	#time.sleep(self._waitTime) ## apperently not needed, communication fast
	answer = self._ser.readline()
	return answer

    @setting(2, "GetFreq", returns='v')
    def GetFreq(self,c):
	'''Returns current frequency'''
	command = self.FreqReqStr()
	self._ser.write(command)
	self.ForceRead() #expect a reply from instrument
	answer = self._ser.readline()
	print answer
	return answer

    @setting(3, "SetFreq", freq = 'v', returns = "")
    def SetFreq(self,c,freq):
	'''Sets frequency, enter value in MHZ'''
	command = self.FreqSetStr(freq)
	self._ser.write(command)
      
    @setting(4, "GetState", returns='w')
    def GetState(self,c):
	'''Request current on/off state of instrument'''
	command = self.StateReqStr()
	self._ser.write(command)
	self.ForceRead() #expect a reply from instrument
	answer = int(self._ser.readline())
	return answer
    
    @setting(5, "SetState", state= 'w', returns = "")
    def SetState(self,c, state):
	'''Sets on/off (enter 1/0)'''
	command = self.StateSetStr(state)
	self._ser.write(command)
    
    @setting(6, "GetPower", returns = 'v')
    def GetPower(self,c):
	''' Returns current power level in dBm'''
	command = self.PowerReqStr()
	self._ser.write(command)
	self.ForceRead() #expect a reply from instrument
	answer = self._ser.readline()
	return answer
    
    @setting(7, "SetPower", level = 'v',returns = "")
    def SetPower(self,c, level):
	'''Sets power level, enter power in dBm'''
	command = self.PowerSetStr(level)
	self._ser.write(command)

    #send message to controller to indicate whether or not (status = 1 or 0)
    #a response is expected from the instrument
    def SetControllerWait(self,status):
	command = self.WaitRespStr(status) #expect response from instrument
	self._ser.write(command)

    def ForceRead(self):
        command = self.ForceReadStr()
        self._ser.write(command)
  
    def IdenStr(self):
	return '*IDN?'+'\n'
	
    # string to request current frequency
    def FreqReqStr(self):
	return 'FREQ:CW?' + '\n'
	
    # string to set freq (in MHZ)
    def FreqSetStr(self,freq):
	return 'FREQ:CW '+ str(freq) +'MHZ'+'\n'
	  
    # string to request on/off?
    def StateReqStr(self):
	return 'OUTP:STAT?' + '\n'

    # string to set on/off (state is given by 0 or 1)
    def StateSetStr(self, state):
	if state == 1:
	    comstr = 'OUTP:STAT ON' + '\n'
	else:
	    comstr = 'OUTP:STAT OFF' + '\n'
	return comstr

    # string to request current power
    def PowerReqStr(self):
	return 'POW:AMPL?' + '\n'

    # string to set power (in dBm)
    def PowerSetStr(self,pwr):
	return 'POW:AMPL ' +str(pwr) + 'DBM' + '\n'

    # string to force read
    def ForceReadStr(self):
        return '++read eoi' + '\n'
	
    # string for prologix to request a response from instrument, wait can be 0 for listen / for talk
    def WaitRespStr(self, wait):
	return '++auto '+ str(wait) + '\n'
	  
    # string to set the addressing of the prologix
    def SetAddrStr(self, addr):
	return '++addr ' + str(addr) + '\n'

if __name__ == "__main__":
    from labrad import util
    util.runServer(HPServer())
