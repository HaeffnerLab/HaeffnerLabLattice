import serial #library for interfacing with the serial port
import time #library for pausing the script
import math
import sys
import os #for file operations
import pickle #for easy exporting/importing of datatypes
import types #for recognizing types of objects, functions on multiple data types
from numpy import *
import Logger
import email_notifier

directory = 'Log/'; os.chdir(directory);
ColdWaterTempBase = 7 # average ColdwaterTemp estimate 
SetPoint = [22,22,22,22,22,22,22,22,22,22,22,22,70,22,ColdWaterTempBase,22] #channels 13 and 15 (or 12,14 counting from 0) are hot/cold water
SignalDelay = 2 #how many seconds to wait before changing applied voltages and how often a response is calculated, seems to be a least 5s of minimum delay, probably an offset. 
WriteDelay = 10 #how many seconds to wait before logging the data
RunningAvgNum = 12 #how many iterations is the window for the running average of temperature measurements
DataFreq = 0.95 #how often to take data
ComDelay = 0.10 #how long to wait before sending consecutive communcations in seconds
Ch = 16; # written for 16 incoming chaneels
ControlCh = 4 #number of controlled rooms
ControlledValves = 8 # number of valves

a = 3.3540154E-03; b = 2.5627725E-04; c = 2.0829210E-06 ; d = 7.3003206E-08 # coeffs for voltage to T conversion info from thermistor datasheet
V0 = 6.95 #volts on the voltage reference
#corresponding channels
Table1=8;Table2=5;Table3=1;Table4=6;Table5=9;SupplyBigRoom=14;SupplyLaserRoom=16;SupplySmallRoom=11;ColdWaterSmallRoom=15;ColdWaterBigRoom=15;ColdWaterLaserRoom=15;HotWaterSmallRoom=13;HotWaterBigRoom=13;HotWaterLaserRoom=13;
HardwareG = [15,15,15,15,15,15,15,15,15,15,15,15,5,15,5,15] #channels 13 and 15 (or 12,14 counting from 0) have less gain for expanded range
#Control Signal
bigroomctrl = 0 #144 big room
smlroomctrl = 1 #140
laserroomctrl = 2 #144B laserroom
officectrl = 3 #144A office

#Coldoffset = [63,25,45,0] #adding an offset because the valve seems to open only at around 50 [big,sml,laser]
#Hotoffset = [70,80,75,0] #adding an offset because the valve seems to open only at around 50 [big,sml,laser]
#ValveMin = [15,62,52,65,35,60,0,0]   # making sure that the valves never close completly  [smlroom-cold,hot, big room-cold, hot, laser room-cold, hot]
Coldoffset = [65,35,45,0] #adding an offset because the valve seems to open only at around 50 [big,sml,laser]
Hotoffset = [67,70,70,0] #adding an offset because the valve seems to open only at around 50 [big,sml,laser]
ValveMin = [15,45,55,55,35,30,0,0]   # making sure that the valves never close completly  [smlroom-cold,hot, big room-cold, hot, laser room-cold, hot]
ColdWaterTempCorrection = [0,0,0,0] # should be zero, [big,sml, laser,office]
ColdWaterDiffGain = [-0,-0,-0] # should be zero 
#ColdWaterDiffGain = [-10000,-10000,-10000] # should be zero 
ColdWaterValveGain = [0.1, 0.2, 0.2, 0] # should be zero, adds some value  (ColdWaterValveGain * (ActualColdWater-ColdWaterTempBase)) to the cold valve depending on the cold water tempererature deviation from ColdWaterTempBase, [big,sml, laser]
ValveMax = 255
GuessHotWaterTemp = 70

oldvalvesignal=zeros(ControlledValves)
direction=zeros(ControlledValves)

hysteresis = [ 22, 12, 2, 7, 22, 12, 0, 0]  # smlroom (cold, hot), bigroom (cold, hot), laserroom (cold, hot) 
#hysteresis = [ 14, 12, 2, 7, 17, 12, 0, 0]  # working well
#hysteresis = [ 12, 20, 3, 13, 35, 25, 0, 0]

IntegrationMin = -500*5; #limit on how small integration response can get, modified later with I-gain and thus more than the max control signal makes not much sense, the 20 comes from the estimated cooling power rescaling (SetPoint-2)
IntegrationMax = 700*5; #limit on how big integration response can get, modified later with the I-gain, the 60 comes from the estimated heating power rescaling

DiffMax = 20000000

PropActionThreshold = 0.0;  # Set proportional feedback to 0 if correction would smaller than this value, units are in temperature deviation [K]; prevents some noise on control when having high P-gain.
DiffActionThreshold = 0.08;  # Set differential feedback to 0 if correction would smaller than this value, units are in temperature deviation [K]; prevents some noise on control when having high D-gain
#ControlActionThreshold = [1,1,1,1,1,1,1,1]; # idea is to reduce wear on control elements by doing adjustments only when large changes occur, SRC,SRH,BRC,BRH,LRC,LRH
ControlActionThreshold = [2,2,4,3,2,2,2,2]; # idea is to reduce wear on control elements by doing adjustments only when large changes occur, SRC,SRH,BRC,BRH,LRC,LRH



PTab=[0,0,0,1]        # contribution from table temperature to P gain 
PSup=[1,1,1,0]	# contribution from supply air (=incoming air) to P gain 
PCoolingWater=[0,0,0,0]	# contribution from cooling water (=cooling water) to P gain 

ColdValveGain=[1,1,1,0]	# correction for cold valve gain
HotValveGain=[1,1,1,0]	# correction for hot valve gain, should be 1, however, better results with higher gain?

integfile = 'lastInteg.txt'#name of the file where last integrator array is kept.
pifile = 'PIparams.txt'#where PI parameters are kept and can be modified on the fly
mancontrolfile = 'manual_valve.txt' #used for manual control of valve positions
ser = serial.Serial('/dev/ttyUSB1')  # open USB-serial port
if(not ser.isOpen()):
	print 'Error: Serial Port Not Open' 
ser.flushInput()
ser.flushOutput()
ser.baudrate = 9600;
ser.timeout = 0.1; #sets timeout of the serial port 



counter = SignalDelay+1 #so that data is outputted on the first loop
WriteCounter = SignalDelay+1 #so that data is written on the first loop
errors_count = 0 #initial number of errors
notifier = email_notifier.notifier()
notifier.set_recepients(['micramm@gmail.com','hhaeffner@berkeley.edu','haeffnerlab@gmail.com'])
officialnotifier = email_notifier.notifier()
officialnotifier.set_recepients(['micramm@gmail.com','hhaeffner@berkeley.edu','haeffnerlab@gmail.com','physics-support@lists.berkeley.edu'])

class Valves():
	def __init__(self):
		self.previousSignal = zeros(ControlledValves)
		self.newSignal = zeros(ControlledValves)

	def sign(x):
		if(x > 0.01):
			return 1
		if(x < -0.01):
			return -1
		else:
			return 0

	def ApplyValveSignal(self,incoming_signal):

		self.newSignal = self.testResponseChange(incoming_signal)

		for i in range(ControlledValves):  # taking care of the hysteresis ....
			newdirection = sign(self.newSignal[i] - oldvalvesignal[i])
			if((newdirection != direction[i]) and (newdirection)): # valve turns around
				direction[i] = newdirection
				print str(time.strftime("%H:%M:%S", time.localtime())) + ': Direction change: Valve ' + str(i) + ' ' + str(direction[i]) 
			oldvalvesignal[i] = self.newSignal[i]
			self.newSignal[i] = clip(self.newSignal[i] + direction[i] * hysteresis[i]/2,ValveMin[i],ValveMax)

		self.communicateSend()
		return self.newSignal
	#for for test in response to minimize valve motion and reduce wear and tear
	def testResponseChange(self,signal):
		for i in range(len(signal)):
			if abs(signal[i]-self.previousSignal[i]) >= ControlActionThreshold[i]:
				signal[i] = int(round(signal[i]))
				self.previousSignal[i] = signal[i]
				print str(time.strftime("%H:%M:%S", time.localtime())) + ': Changing Valve ' + str(i) + ' to ' + str(signal[i])
			else:
				signal[i] = int(round(self.previousSignal[i]))
		return signal		
	def communicateSend(self):
		signal = self.newSignal
		for i in range(ControlledValves):
			ser.write("d")
			time.sleep(ComDelay)
			ser.write(str(i))
			time.sleep(ComDelay)
			vsig = self.dec2hex(signal[i])
			ser.write(vsig)
			time.sleep(ComDelay)
			ser.flushInput()
			time.sleep(ComDelay)
	def dec2hex(self, n):#"""return the hexadecimal string representation of integer n as a two digits representation in lowercase"""
		string	= "%x" % n
		string = string.zfill(2)
		return string

class ResponseCalculator():
	def __init__(self):
		self.lastErrSigArr = zeros(Ch) #initial vale of lastErrorSignal, used to disable Diff gain for the first time
		self.loadExternalParams()	
	def loadExternalParams(self):
		if(os.path.isfile(integfile)):#if integ file exists (with information about last integration), open it in read/write mode and read in last integrator setting
			self.INTEGFILE =  open(integfile,"r+");
			self.integralerrorSigArr = array(pickle.load(self.INTEGFILE))
		else: #if file does not exist, create it and specify initial integrator parameters.
			self.INTEGFILE =  open(integfile,"w");
			self.integralerrorSigArr = zeros(Ch)
		if(os.path.isfile(pifile)): #if file exists, load the PI parameters
			self.PIFILE = open(pifile,"r+")
			self.P = array(pickle.load(self.PIFILE))
			self.I = array(pickle.load(self.PIFILE))
			self.D = array(pickle.load(self.PIFILE))
			self.PIFILE.close()
		else:
			self.PIFILE = open(pifile,"w") #if file doesn't not exist, create it
			#proportionality constant for PID in the format [#144 big room / #140 small room / #144B Laser Room / #144A office]
			self.P = array([-15,-15,-15,-0])
			self.I = array([-.1,-.1,-.1,-0])
			self.D = array([-40,-40,-40,0])
			pickle.dump(self.P.tolist(),self.PIFILE)
			pickle.dump(self.I.tolist(),self.PIFILE)
			pickle.dump(self.D.tolist(),self.PIFILE)
			self.PIFILE.close()
		self.PImodtime = os.path.getmtime(pifile) #time when pifile is last modified
	def updateExternalPIDParams(self):
		if(os.path.getmtime(pifile) != self.PImodtime): #if PI parmeters have been modified externally, update them
			self.PIFILE = open(pifile, 'r')
			self.P = array(pickle.load(self.PIFILE))
			self.I = array(pickle.load(self.PIFILE))
			self.D = array(pickle.load(self.PIFILE))
			self.PIFILE.close()
			self.PImodtime = os.path.getmtime(pifile)
			print("new P,I,D parameters are")
			print self.P
			print self.I
			print self.D
			
	def getResponse(self):
		return [self.PIDresponseArr,self.valvesignalArr]
	
	def calculateResponse(self, curTempArr):
		self.errorSigArr = self.finderrorSig(curTempArr)
		self.integralerrorSigArr = self.calcintegrator(self.integralerrorSigArr, self.errorSigArr)
		self.saveIntegralError(self.integralerrorSigArr)
		self.PIDresponseArr = self.findPIDresponse(self.errorSigArr, self.integralerrorSigArr,self.lastErrSigArr) 
		self.lastErrSigArr= self.errorSigArr
		self.valvesignalArr = self.CalcValveSignal(self.PIDresponseArr, curTempArr)
		
	def saveIntegralError(self,integError):
		#print integError
		self.INTEGFILE.seek(0) #moves position to the beginning of the file
		pickle.dump(integError, self.INTEGFILE)
		self.INTEGFILE.truncate() 

		
	def finderrorSig(self, CurTemp): #takes array with current temperatures and finds the error signal array
		error = CurTemp - SetPoint
		return error
		
	def calcintegrator(self,oldArr, newArr):
		TotalArr = oldArr + newArr
		# Normalize maximum by the mean of the integration constants
		minim = IntegrationMin/(-sum(self.I)/len(self.I))
		maxim = IntegrationMax/(-sum(self.I)/len(self.I))
		TotalArr=clip(TotalArr,minim,maxim)
		return TotalArr
			
	def findPIDresponse(self,curErrArr, IntErrArr, lastErrArr):	#produces array containg signal to be sent to valves in format [Control1, Control2..] where each one is measured from -255 to 255 positive to hotter, negative for colder
		P = self.P
		I = self.I
		D = self.D
		propArr = zeros(ControlCh)
		propArr[bigroomctrl] = PSup[bigroomctrl]*curErrArr[SupplyBigRoom-1]#0 + PTab[bigroomctrl]*curErrArr[Table1-1]#0 + PCoolingWater[bigroomctrl]*curErrArr[ColdWaterBigRoom]
		propArr[smlroomctrl] = PSup[smlroomctrl]*curErrArr[SupplySmallRoom-1]#0 + PTab[smlroomctrl]*curErrArr[Table3-1]#0 + PCoolingWater[smlroomctrl]*curErrArr[ColdWaterSmallRoom]
		propArr[laserroomctrl] = PSup[laserroomctrl]*curErrArr[SupplyLaserRoom-1]#0 + PTab[laserroomctrl]*curErrArr[Table4-1]#0 + PCoolingWater[laserroomctrl]*curErrArr[ColdWaterLaserRoom]
		propArr[officectrl] = 0 #no control in office
		propArr = propArr - clip(propArr, -PropActionThreshold,PropActionThreshold)
	
		proprespArr = (P * propArr) # when used with arrays, * is component by component multiplcation or dot product for 1D arrays
	
		integArr =  zeros(ControlCh)
		integArr[bigroomctrl] = IntErrArr[Table1-1]
		integArr[smlroomctrl] = IntErrArr[Table3-1]
		integArr[laserroomctrl] = IntErrArr[Table4-1]
		integArr[officectrl] = 0 #no control in office
		integrespArr = (I * integArr) # when used with arrays, * is component by component multiplcation or dot product for 1D arrays
		#print integArr
		
		if((lastErrArr == zeros(Ch)).any()): #when the lastErrArr is the zero array, then don't do any diff because it's the first run
			diffrespArr = zeros(ControlCh)
		else:
			diffArr =  zeros(ControlCh)
			DiffErrArr = curErrArr - lastErrArr
			diffArr[bigroomctrl] = DiffErrArr[SupplyBigRoom-1] + ColdWaterDiffGain[bigroomctrl] * DiffErrArr[ColdWaterBigRoom-1] / D[bigroomctrl]
			diffArr[smlroomctrl] = DiffErrArr[SupplySmallRoom-1] + ColdWaterDiffGain[smlroomctrl] * DiffErrArr[ColdWaterSmallRoom-1] / D[smlroomctrl]
			diffArr[laserroomctrl] = DiffErrArr[SupplyLaserRoom-1] + ColdWaterDiffGain[laserroomctrl] * DiffErrArr[ColdWaterLaserRoom-1] / D[laserroomctrl]
			diffArr[officectrl] = 0 # no control in office
			diffArr = diffArr - clip(diffArr, -DiffActionThreshold,DiffActionThreshold)

			diffrespArr = (D * diffArr)
			diffrespArr = clip(diffrespArr, -DiffMax, DiffMax)
		print 'P', proprespArr
		print 'I', integrespArr
		print 'D', diffrespArr
		responseArr = proprespArr + integrespArr + diffrespArr	
		return responseArr
			
	def CalcValveSignal(self,responseArr,curTempArr):#hard codes which control channel correspond to which output number
		valvesignalArr = zeros(ControlledValves)
	
		#ColdWater = array([curTempArr[ColdWaterBigRoom-1], curTempArr[ColdWaterSmallRoom-1], curTempArr[ColdWaterLaserRoom-1],0 ])
		#ColdWater = clip(ColdWater,0,20)
		ColdWater = array([13.0,13.0,13.0,0.0]);   # set cold water temp to 13 degrees because the sensor is not working atm

		HotWater = array([curTempArr[HotWaterBigRoom-1], curTempArr[HotWaterSmallRoom-1], curTempArr[HotWaterLaserRoom-1], 0])
		SetPointAux = array([SetPoint[Table1-1], SetPoint[Table3-1], SetPoint[Table4-1], 0])  

		CoolingPower = clip(SetPointAux - ColdWater - ColdWaterTempCorrection,1.0,100.0) # estimate cooling power for valve settings, always assume some cooling power
		HeatingPower =  clip(HotWater - SetPointAux,20.0,200.0) # minum heating power corresponds to 20 degrees temp-difference

		ColdValveSignal = - responseArr/CoolingPower*ColdValveGain + Coldoffset# + ColdWaterValveGain * (ColdWater-ColdWaterTempBase)
		HotValveSignal = Hotoffset + responseArr/HeatingPower*HotValveGain
		
                valvesignalArr[0] = ColdValveSignal[smlroomctrl]
                valvesignalArr[1] = HotValveSignal[smlroomctrl]
                valvesignalArr[2] = ColdValveSignal[bigroomctrl]
                valvesignalArr[3] = HotValveSignal[bigroomctrl]
                valvesignalArr[4] = ColdValveSignal[laserroomctrl]
                valvesignalArr[5] = HotValveSignal[laserroomctrl]
                valvesignalArr[6] = 0
                valvesignalArr[7] = 0

#                valvesignalArr[0] = clip(ColdValveSignal[smlroomctrl],ValveMin[0],ValveMax)
#                valvesignalArr[1] = clip(HotValveSignal[smlroomctrl],ValveMin[1],ValveMax)
#                valvesignalArr[2] = clip(ColdValveSignal[bigroomctrl],ValveMin[2],ValveMax)
#                valvesignalArr[3] = clip(HotValveSignal[bigroomctrl],ValveMin[3],ValveMax)
#                valvesignalArr[4] = clip(ColdValveSignal[laserroomctrl],ValveMin[4],ValveMax)
#                valvesignalArr[5] = clip(HotValveSignal[laserroomctrl],ValveMin[5],ValveMax)
#                valvesignalArr[6] = 0
#                valvesignalArr[7] = 0
	
		valvesignal = valvesignalArr.tolist()

		return valvesignalArr
	def __del__(self):
		self.INTEGFILE.close()
		
class DataAcquisition():
	def binarytoTempC(self,bin, ch): #converts binary output to a physical temperature in C
		Vin = 2.56*(float(bin)+1)/1024 #voltage that is read in 1023 is 2.56 0 is 0
		
		dV = (15/HardwareG[ch])*(Vin/1.2 - 1) #when G = 15 (most channels) dV of 2.4 corresponds to bridge voltage of 1 and dV of 0 is bridge voltage of -1 	
					#G = 5 for low res channels for cold water, hot water supply
					#G is determines by INA114 gain resistor
		R = (dV/V0 +.5) / (- dV/V0 + .5) * 10 #convert bridge voltage to R in kohms
		T = 1/(a + b*math.log(R/10.) + c * pow(math.log(R/10.),2) + d * pow(math.log(R/10.),3)) #consult datasheet for this
		TempC = round(T - 273.15,2) #Kelvin to C
		return TempC

	def readTemp(self,ser):#processing the input in the format 03:1023<space>... where 03 is the number of the detector, 1023 is the voltage representation 
			#returns array with data
		global errors_count
		curTempArr = zeros(Ch)
		ser.write('t') # command to output readings
		curLine = ser.read(Ch*8)          # reads 128 bytes, 16 channels 7 bytes each and 16 spaces
		if(len(curLine)==128): # read everything correctly
			for i in range(Ch):
				# left and right ranges for number of voltages
				lnum = 8*i + 0
				rnum = 8*i + 2
				lvol = 8*i + 3
				rvol = 8*i + 7
				num = curLine[lnum:rnum] #number of the detector is the first
				vol = int(curLine[lvol:rvol]) #voltage readout
				TempC = self.binarytoTempC(vol, i)
				curTempArr[i] = TempC
				
		else:
			if(errors_count > 20):
				notifier.set_content('AC ALARM','The program quit because there were too many errors with data acquisition')
				notifier.send()
				sys.exit()
			errors_count = errors_count + 1
			print "Error: Data not collected"
			print curLine
			time.sleep(DataFreq)
			curTempArr = self.readTemp(ser)
		return curTempArr
	
class RunningAverage():
	def __init__(self):
		self.RunningAvgNum = RunningAvgNum
		self.historyArr = zeros([self.RunningAvgNum,Ch])
		self.binfull = 0
		self.historyCounter = 0
		self.printintro()
	def printintro(self):
		print '\n' + 'Filling up history for ' + str(self.RunningAvgNum) +' seconds \n'
	def printbinfull(self):
		print 'Running Average Operational'
	def addNumber(self,newnumber):
		self.historyArr[self.historyCounter,:] = newnumber #updates history by cycling through rows of historyArr and replacing old data with readTemp
		self.historyCounter = (self.historyCounter + 1) % self.RunningAvgNum
		if(self.historyCounter == 0):
			if(self.binfull == 0):
				self.printbinfull()
			self.binfull = 1
	def getAverage(self):
		if(self.binfull): #if bin is full, take the mean
			average = mean(self.historyArr,axis=0) #current temperature is the average of the columns of the history array	
		else: #if bin is not filled, return mean of existing elements
			average =  sum(self.historyArr[0:(self.historyCounter+1),:],axis=0)/(self.historyCounter)
		return average
		
class ManualController():
	def __init__(self):
		if(os.path.isfile(mancontrolfile)):#if file exists open it in read mode
			pass
		else: #if file doesn't exist, create it
			self.FILE =  open(mancontrolfile,"w");
			pickle.dump(0,self.FILE) #indicates automatic control, 1 is manual
			pickle.dump(zeros(ControlledValves).tolist(),self.FILE)
			self.FILE.close()
		self.modtime = os.path.getmtime(mancontrolfile)
		self.valves = zeros(ControlledValves)
	def isControlManual(self):
		self.FILE =  open(mancontrolfile,"r");
		self.mancontrol = pickle.load(self.FILE)
		self.valves = array(pickle.load(self.FILE))
		self.FILE.close()
		return self.mancontrol
	def ManualValvePos(self):
		return self.valves
	
class AlarmChecker():
	def __init__(self):
		self.messagesent = 0
		self.callstoReset = 900*12  # set time for next alarm to 12h
		self.callsCount = 0
		self.messageMax = 1 #maximum number of allowed emails per the number of callstoReset
	def updateCallsCount(self):
		if(self.callsCount >= self.callstoReset):  
			self.messagesent = 0
			self.callsCount = 0
			print 'alarm armed again'
		else:
			self.callsCount = self.callsCount + 1;
	def checkForAlarm(self,curTempArr):
		self.updateCallsCount()
		if(abs(curTempArr[Table1 - 1] - SetPoint[Table1 -1]) > 2):
			notifier.set_content('AC ALARM','The differential between Table1 temperature and setpoint exceeds norm')
			if(self.messagesent < self.messageMax):
				notifier.send()
				self.messagesent = self.messagesent + 1
		if(abs(curTempArr[Table3 - 1] - SetPoint[Table3 - 1]) > 2):
			notifier.set_content('AC ALARM','The differential between Table3 temperature and setpoint exceeds norm')
			if(self.messagesent < self.messageMax):
				notifier.send()
				self.messagesent = self.messagesent + 1
		if(abs(curTempArr[Table4 - 1] - SetPoint[Table4 - 1]) > 2):
			notifier.set_content('AC ALARM','The differential between Table4 temperature and setpoint exceeds norm')
			if(self.messagesent < self.messageMax):
				notifier.send()
				self.messagesent = self.messagesent + 1
		#if(abs(curTempArr[ColdWaterBigRoom - 1] - 7) > 8):
			#notifier.set_content('AC ALARM','The ColdWaterBigRoom temperature is too far from norm')
			#officialnotifier.set_content('Haeffner Lab: Possible Chiller Issue','The cold water supply temperature is currently ' + str(curTempArr[ColdWaterBigRoom - 1])+ ', too far from norm of 7 degrees \n This is an automatically generated email.')
			#if(self.messagesent < self.messageMax):
				#notifier.send()
				#officialnotifier.send()
				#self.messagesent = self.messagesent + 1
		if(abs(curTempArr[HotWaterBigRoom - 1] - 50) > 40):  # Hot water varies really a lot
			notifier.set_content('AC ALARM','The HotWaterBigRoom temperature is too far from norm')
			if(self.messagesent < self.messageMax):
				notifier.send()
				self.messagesent = self.messagesent + 1
	
alarmchecker = AlarmChecker()		
runaverage = RunningAverage()
acquire = DataAcquisition()
log = Logger.Logger()
valves = Valves()
responsecalculator = ResponseCalculator()
manualcontrol = ManualController()

try:
	while('true'):
		counter = counter + DataFreq
		WriteCounter = WriteCounter + DataFreq
		time.sleep(DataFreq)
		runaverage.addNumber(acquire.readTemp(ser))
		curTempArr = runaverage.getAverage()
		alarmchecker.checkForAlarm(curTempArr)
		responsecalculator.calculateResponse(curTempArr)
		if counter > SignalDelay: #apply the output singal every SignalDelay seconds
			counter = 0	
			if(manualcontrol.isControlManual()):
				valvesignalArr = manualcontrol.ManualValvePos()
				PIDresponseArr = zeros(ControlCh) #neded for logging 0s
				print 'manual control' + str(valvesignalArr)
			else:
				[PIDresponseArr,valvesignalArr] = responsecalculator.getResponse()
			sentValveSignalArr = valves.ApplyValveSignal(valvesignalArr)
			#print sentValveSignalArr
		if WriteCounter > WriteDelay: #write data to log file
			WriteCounter = 0
			log.MakeLog(curTempArr, PIDresponseArr,sentValveSignalArr)					
		responsecalculator.updateExternalPIDParams()
except KeyboardInterrupt:
	time.sleep(DataFreq)
	ser.flushInput()
	ser.flushOutput()
	ser.close() # closes the serial port
	print 'Graceful exit'
