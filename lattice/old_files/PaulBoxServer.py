'''
Created on Jan 24, 2011

@author: christopherreilly
'''

from labrad.server import LabradServer, setting

class PBError( Exception ):
    pass

class PaulBoxServer( LabradServer ):
    name = 'Paul\'s Box Server'

    def initServer( self ):
        self.loadConfig()
        self.connectSocket()
        self.loadDatabase()
        self.loadScripts()

    def loadConfig( self ):
        """
        Load configuration settings from registry.
        
        TODO: details
        """
        pass

    def connectSocket( self ):
        """
        Connect socket.
        
        TODO: details
        """
        pass

    def loadDatabase( self ):
        """
        Load database.
        
        TODO: details
        """
        pass

    def loadScripts( self ):
        """
        Load scrips
        
        TODO: details
        """
        pass

    def sendPB( self, toSend ):
        """
        Lower level sending
        
        TODO: details
        """
        pass

    def recPB( self, resp ):
        """
        Lower level receiving
        
        TODO: details
        """
        pass

    @setting( 0, 'Send command',
              scriptName = 's: script name',
              inputList = '*2s: input values',
              returns = 's: response from PB' )
    def sendCommand( self, scriptName, inputList ):
        """
        Send command to Paul's Box.
        
        TODO: details
        """
        if len( filter( lambda x: len( x ) == 3, inputList ) ) != len( inputList ):
            raise PBError( 'Input parameters must be in form of a list of 3 entry lists' )

        def flattenInputList( li ):
            return ';'.join( ','.join( i ) for i in list )

        toSend = 'NAME,%s;' % scriptName + flattenInputList( inputList )
        self.sendPB( toSend )
        resp = self.recPB()
        return resp







