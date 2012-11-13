'''
Created on Jan 31, 2011

@author: christopherreilly
'''

#===============================================================================
# 2011 - 01 - 31
# 
# Variation on the DC Box server.
# 
# Configured to wait for reponse from DC Box before
# proceeding to further writes.
#===============================================================================

from dcbox import DCBoxServer, DCBoxError, SerialDeviceError, inlineCallbacks, reactor
import time
#time to wait for response from dc box
TIMEOUT = 1.0
#expected response from dc box after write
RESP_STRING = 'r'
#time to wait if correct response not received
ERROR_TIME = 1.0

errDict = DCBoxError.errorDict
RESP_ERROR = max( errDict.keys() ) + 1
errDict[RESP_ERROR] = 'Correct reponse from DC box not received, sleeping for short period'

class DCBoxRespServer( DCBoxServer ):
    """
    DC Box Response Server
    
    Serial device controlling setting and getting of three separate voltage sources:
        
        End caps
        Compensation Electrodes
        Shutters
        
    Subclass of DC Box Server.
    Adjusted to check for response after writing. 
    """
    timeout = TIMEOUT

    @inlineCallbacks
    def writeToSerial( self, channel, value ):
        """
        Write value to specified channel through serial connection.
        
        Convert message to microcontroller's syntax.
        Check for correct response.
        Handle possible error, or
        save written value to memory and check queue.
        
        @param channel: Channel to write to
        @param value: Value to write
        
        @raise SerialConnectionError: Error code 2.  No open serial connection.
        """
        self.checkConnection()
        toSend = self.mapMessage( channel, value )
        self.ser.write( toSend )
        resp = yield self.ser.read( len( RESP_STRING ) )
        if RESP_STRING != resp:
#            Since we didn't get the the correct reponse,
#            place the value back in the front of the queue
#            and wait for a specified ERROR_TIME before
#            checking the queue again.
            self.queue.insert( 0, ( channel, value ) )
            reactor.callLater( ERROR_TIME, self.checkQueue )
        else:
#            Since we got the correct reponse,
#            update the value entry for this channel
#            and check the queue.
            dev, devChannel = self.getChannelInfo( channel )
            self.dcDict[dev]['devChannels'][devChannel]['value'] = value
            self.checkQueue()


if __name__ == "__main__":
    from labrad import util
    util.runServer( DCBoxRespServer() )


