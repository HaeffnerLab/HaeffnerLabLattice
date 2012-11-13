class AlarmChecker():
    '''Class for checking the temperatures and sending out a notification email if they exceed a tolerable deviation from the set point'''

    timeToReset = 12*3600  #seconds
    messageMax = 1 #maximum number of allowed emails per the number of callstoReset
    #dictionary in the format channelToCheck: (setpoint, max deviation)
    params = {
            'Table1':(22.0 , 2.0),
            'Table3':(22.0 , 2.0),
            'Table4':(22.0,  2.0),
            #'ColdWater'
            'HotWater':(45.0,35.0)
            }
    
    def __init__(self, emailer, channelDict):
        self.emailer = emailer
        self.messageSent = 0
        self.alarmReset = LoopingCall(self.reset)
        self.alarmReset.start(self.timeToReset, now = False)
        self.channelDict = channelDict
        
    def reset(self):
        self.messageSent = 0
    
    @inlineCallbacks
    def check(self, temp):
        message = None
        for channelName in self.params.keys():
            ch = self.channelDict[channelName]
            setpoint,deviation = self.params[channelName]
            if(abs(temp[ch] - setpoint) > deviation):
                message = ('AC ALARM','The differential between {} temperature and setpoint exceeds norm'.format(channelName))
        if message and (self.messageSent < self.messageMax): 
            yield self.emailer.send(*message)
            self.messageSent +=1