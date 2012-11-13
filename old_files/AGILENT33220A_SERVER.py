from labrad.server import LabradServer, setting
import serial 

class AgilentServer(LabradServer):
    """Controls Agilent 33220A Signal Generator"""
    name = "%LABRADNODE% AGILENT 33220A SERVER"
    
    def initServer( self ):
        #communication configuration
        self._port = 'COM11'
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
	answer = self._ser.readline()[:-1]
	return answer

    @setting(2, "GetFreq", returns='v')
    def GetFreq(self,c):
	'''Returns current frequency'''
	command = self.FreqReqStr()
	self._ser.write(command)
	self.ForceRead() #expect a reply from instrument
	answer = self._ser.readline()
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
	answer = str(int(self._ser.readline()))
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
    
    @setting(8, "GetVoltage", returns = 'v')
    def GetVoltage(self,c):
        '''Returns current voltage level in Volts'''
        command = self.VoltageReqStr()
        self._ser.write(command)
        self.ForceRead() #expect a reply from instrument
        answer = self._ser.readline()
        return answer
    
    @setting(9, "SetVoltage", level = 'v',returns = "")
    def SetVoltage(self,c, level):
        '''Sets voltage level, enter power in volts'''
        command = self.VoltageSetStr(level)
        self._ser.write(command)
    
    @setting(10, "Get Function", returns = 's')
    def GetFunc(self,c):
        ''' Returns the current function output of the instrument'''
        command = self.FunctionReqStr()
        self._ser.write(command)
        self.ForceRead() #expect a reply from instrument
        answer = self._ser.readline()[:-1]
        return answer
    
    @setting(11, "Set Function", func = 's',returns = "")
    def setFunc(self,c, func):
        '''Sets type of function to output: SINE, SQUARE, RAMP, PULSE, NOISE, or DC'''
        command = self.FunctionSetStr(func)
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
	return '*IDN?'+'\r\n'
	
    # string to request current frequency
    def FreqReqStr(self):
	return 'FREQuency?' + '\r\n'
	
    # string to set freq in Hz
    def FreqSetStr(self,freq):
	return 'FREQuency '+ str(freq) +'\r\n'
	  
    # string to request on/off?
    def StateReqStr(self):
	return 'OUTPut?' + '\r\n'

    # string to set on/off (state is given by 0 or 1)
    def StateSetStr(self, state):
	if state == 1:
	    comstr = 'OUTPut ON' + '\r\n'
	else:
	    comstr = 'OUTPut OFF' + '\r\n'
	return comstr

    # string to request current power
    def PowerReqStr(self):
	return 'Voltage:UNIT DBM\r\n'+'Voltage?' + '\r\n'
    
    # string to request voltage
    def VoltageReqStr(self):
        return 'Voltage:UNIT VPP\r\n'+'Voltage?' + '\r\n'

    # string to set power (in dBm)
    def PowerSetStr(self,pwr):
	return 'Voltage:UNIT DBM\r\n' + 'Voltage ' +str(pwr) + '\r\n'
    
    # string to set voltage
    def VoltageSetStr(self,volt):
        return 'Voltage:UNIT VPP\r\n'+'Voltage ' +str(volt) + '\r\n'

    # string to get current function
    def FunctionReqStr(self):
        return 'FUNCtion?\r\n'
    
    # string to set function
    def FunctionSetStr(self,func):
        if func == 'SINE':
            comstr = 'FUNCtion ' + 'SIN' + '\r\n'
        elif func == 'SQUARE':
            comstr = 'FUNCtion ' + 'SQU' + '\r\n'
        elif func == 'RAMP':
            comstr = 'FUNCtion ' + 'RAMP' + '\r\n'
        elif func == 'PULSE':
            comstr = 'FUNCtion ' + 'PULSe' + '\r\n'
        elif func == 'NOISE':
            comstr = 'FUNCtion ' + 'NOISe' + '\r\n'
        elif func == 'DC':
            comstr = 'FUNCtion ' + 'DC' + '\r\n'
        return comstr

    # string to force read
    def ForceReadStr(self):
        return '++read eoi' + '\r\n'
	
    # string for prologix to request a response from instrument, wait can be 0 for listen / for talk
    def WaitRespStr(self, wait):
	return '++auto '+ str(wait) + '\r\n'
	  
    # string to set the addressing of the prologix
    def SetAddrStr(self, addr):
	return '++addr ' + str(addr) + '\r\n'

if __name__ == "__main__":
    from labrad import util
    util.runServer(AgilentServer())
