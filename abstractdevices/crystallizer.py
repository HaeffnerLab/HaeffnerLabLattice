"""
### BEGIN NODE INFO
[info]
name = Crystallizer
version = 1.0
description = 
instancename = Crystallizer

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""
from labrad.server import LabradServer, setting
from twisted.internet import reactor
from labrad.units import WithUnit
from twisted.internet.defer import inlineCallbacks, Deferred

class Crystallizer( LabradServer ):

    name = 'Crystallizer'
    
    def initServer( self ):
        self.intialize_connections()
    
    def intialize_connections(self):
        '''
        connect to the pulser
        '''
        try:
            self.pulser = self.client.pulser
        except AttributeError:
            self.pulser = None
    
    @setting(0, "Crystallize Once", crystallization_time = 'v[s]')
    def crystalizer(self, c, crystallization_time = None):
        '''
        Run the crystallization procedure
        '''
        if crystallization_time is None:
            crystallization_time = WithUnit(0.5,'s')
        crystallization_time = crystallization_time['s']
        yield self.do_crystallize(crystallization_time)
    
    @inlineCallbacks
    def do_crystallize(self, crystallization_time):
        init_110DP = yield self.pulser.output('global397')
        yield self.pulser.switch_manual('crystallization',  True)
        yield self.pulser.output('global397',  False) 
        yield self.wait(crystallization_time, None)
        yield self.pulser.output('global397',  init_110DP) 
        yield self.pulser.switch_manual('crystallization',  False)
    
    def wait(self, seconds, result=None):
        """Returns a deferred that will be fired later"""
        d = Deferred()
        reactor.callLater(seconds, d.callback, result)
        return d

    def serverConnected( self, ID, name ):
        """Connect to the server"""
        if name == 'Pulser':
            self.pulser = self.client.pulser

    def serverDisconnected( self, ID, name ):
        """Close connection"""
        if name == 'Pulser':
            self.Pulser = None

if __name__ == "__main__":
    from labrad import util
    util.runServer(Crystallizer())