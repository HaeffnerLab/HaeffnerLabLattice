"""
### BEGIN NODE INFO
[info]
name = AC Server
version = 2.0
description = 
instancename = AC Server

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

from labrad.server import LabradServer, setting
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.task import LoopingCall
from RunningAverage import RunningAverage
from AlarmChecker import AlarmChecker
from Communicator import Communicator
from ResponseCalculator import ResponseCalculator
from Valves import Valves
import numpy

####testing
#get temperature array, make sure is the same

####set points for cold water should be that base temperature
####store PID, integrator in the registry
####check on physically where supply vs measurements are done
####save P,I,D, PID, valves into data vault
####delete AC stuff from lab-user
####remove excess cabling
####update wiki instructions

class AC_Server( LabradServer ):
    name = 'AC Server'
    updateRate = 1.0 #seconds
    maxDaqErrors = 10
        
    @inlineCallbacks
    def initServer( self ):
        #setting up necessary objects
        self.daq = Communicator()
        self.channels = self.daq.channels
        self.channelDict = self.daq.channelDict
        self.averager = RunningAverage(self.channels, averageNumber = 12)
        self.emailer = self.client.emailer
        yield self.emailer.set_recipients(['micramm@gmail.com']) #### set this later
        self.alarmChecker = AlarmChecker(self.emailer, self.channelDict)
        #stting up constants
        self.PIDparams =([0,0,0],..)####get from registry
        self.daqErrors = 0
        #
        self.responseCalc = ResponseCalculator()
        #begin control
        self.inControl = LoopingCall(self.control)
        self.inControl.start(self.updateRate)


    @setting(0, 'Manual Override', enable = 'b', valvePositions = '*v')
    def manualOverride(self, c, enable, valvePositions = None):
        """If enabled, allows to manual specify the positions of the valves, ignoring feedback"""
        if enable:
            if valvePositions is None: raise Exception("Please specify valve positions")
            if self.inControl.running:
                yield self.inControl.stop()
            raise NotImplementedError
            #### set valve positions through valve class (with error checking there)
            #### make sure still record and save temperatures while in manual mode
        else: #resume automated control
            self.inControl.start(self.updateRate)
            
    @setting(1, 'PID Parameters', PID = '*3v')
    def PID(self, c, PID = None):
        """Allows to view or to set the PID parameters"""
        if PID is None: return self.PID
        self.PIDparams = PID
        ####
        
    @setting(2, 'Reset Integrator')
    def resetIntegrator(self, c):
        pass
    
    @inlineCallbacks
    def control(self):
        try:
            temps = yield self.daq.getTemperatures()
        except: #put error type
            self.daqErros += 1
            yield self.checkMaxErrors()
        else:
            self.averager.add(temps)
            temps = self.averager.getAverage()
            yield self.alarmChecker.check(temps)
            PIDresponse,valveResponse =  self.responseCalc.getResponse(temps)
            toValves = self.Valves.valveSignal(valveResponse)
            yield self.daq.setValves(toValves)
            
            
    @inlineCallbacks
    def checkMaxErrors(self):
        """checks how many errors have occured in sends out a notification email"""
        if self.daqErrors >  self.maxDaqErrors:
            print "TOO MANY DAQ ERRORS"
            yield self.emailer.send('AC ALARM: TOO MANY DAQ ERRORS', '')
            self.daqErrors = 0
            yield self.inControl.stop()
    
if __name__ == "__main__":
    from labrad import util
    util.runServer(AC_Server())