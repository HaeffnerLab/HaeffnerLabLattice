'''
Created on Dec 22, 2010

@author: christopherreilly
'''
# General class representing device server
# that communicates with serial ports.

# Handles writing, reading operations from
# serial port, as well as connecting.

# Subclass this if you are writing a device
# server that communicates using serial port

# Only connects to one port right now.
# Might be cleaner to keep it this way.

# TODO: Node launching of the serial server.
#       Port selection by client.

# We use a default naming convention of
# naming our servers the same name as the
# key to the port string in the registry.

from twisted.internet.defer import returnValue, inlineCallbacks

from labrad.server import LabradServer, setting
from labrad.types import Error
from string import replace

class SerialDeviceError( Exception ):
    def __init__( self, value ):
        self.value = value
    def __str__( self ):
        return repr( self.value )

class SerialConnectionError( Exception ):
    errorDict = { 0:'Could not find serial server in list', 1:'Serial server not connected' }
    def __init__( self, code ):
        self.code = code
    def __str__( self ):
        return self.errorDict[self.code]

class PortRegError( SerialConnectionError ):
    errorDict = { 0:'Registry not properly configured' , 1:'Key not found in registry' , 2:'No keys in registry' }

NAME = 'SerialDevice'

class SerialDeviceServer( LabradServer ):
    """Base class for serial device servers."""
    name = NAME
    ser = None
    port = None

    class SerialConnection():
        """
        Wrapper for our server's client connection to the serial server.      
        """
        def __init__( self, ser, port ):
            ser.open( port )
            self.write = lambda s: ser.write_line( s )
            self.read = lambda: ser.read_line()
            self.close = lambda: ser.close()

    @inlineCallbacks
    def findSerial( self ):
        cli = self.client
        # look for servers with 'serial' in the name, take first result
        servers = yield cli.manager.servers()
        serStr = filter( lambda x: 'serial' in x[1].lower() , servers )
        if serStr: returnValue( serStr[0][1] )
        else: raise SerialConnectionError( 0 )

    # given a port string, open a serial connection
    @inlineCallbacks
    def initSerial( self, serStr, port ):
        """
        Attempts to initialize a serial connection using
        given key for serial serial and port string.
        Throws SerialConnectError #1 otherwise.
        """
        cli = self.client
        try:
            # get server wrapper for serial server
            ser = yield cli.servers[ serStr ]
            print ser.__doc__
            # instantiate SerialConnection convenience class
            self.ser = yield self.SerialConnection( ser = ser, port = port )
        except Error:
            self.ser = None
            raise SerialConnectionError( 1 )

    @inlineCallbacks
    def getPortFromReg( self, regKey = None ):
        """
        Find port string in registry given key.
        If you do not input a parameter, it will look for the first four letters of your name attribute in the registry port keys
        """
        reg = self.client.registry
        #There must be a 'Ports' directory at the root of the registry folder
        try:
            reg.cd( ['', 'Ports'] )
            y = yield reg.dir()
            if not regKey:
                if self.name: regKey = self.name[:4].lower()
                else: raise SerialDeviceError( 'name attribute is None' )
            else: regKey = regKey.lower()
            portStrKey = filter( lambda x: regKey in x.lower() , y[1] )
            if portStrKey: portStrKey = portStrKey[0]
            else: raise SerialDeviceError( 'key not found in registry' )
            portStrVal = yield reg.get( portStrKey )
            returnValue( portStrVal )
        except Error, e:
            if e.code == 17: raise PortRegError( 0 )
            else: raise
        except IndexError:
            raise PortRegError( 1 )
	  
    #allows user to manually specify which port to use by looking up available ports from the regsitry
    @inlineCallbacks
    def selectPortFromReg( self ):
        """
        Select port string from list of keys in registry
        """
        reg = self.client.registry
        try:
            #change this back to 'Ports'
            yield reg.cd( ['', 'Ports'] )
            portDir = yield reg.dir()
            portKeys = portDir[1]
            if not portKeys: raise PortRegError( 2 )
            keyDict = {}
            map( lambda x , y: keyDict.update( { x:y } ) ,
                 [str( i ) for i in range( len( portKeys ) )] ,
                 portKeys )
            for key in keyDict:
                print key, ':', keyDict[key]
            selection = None
            while True:
                print 'Select the number corresponding to the device you are using:'
                selection = raw_input( '' )
                if selection in keyDict:
                    portStr = yield reg.get( keyDict[selection] )
                    returnValue( portStr )
        except Error, e:
            if e.code == 13: raise PortRegError( 0 )
            else: raise

    def serverConnected( self, ID, name ):
        """Check to see if we can connect to serial server now"""
        if not self.ser and self.port and 'serial' in name.lower():
            print 'Serial server connected after we connected'
            self.initSerial( name, self.port )

    def serverDisconnected( self, ID, name ):
        """Close connection (if we are connected)"""
        if self.ser and 'serial' in name.lower():
            self.ser = None

    def stopServer( self ):
        """
        Close serial connection before exiting.
        """
        if self.ser:
            self.ser.close()

if __name__ == "__main__":
    from labrad import util
    util.runServer( SerialDeviceServer() )
