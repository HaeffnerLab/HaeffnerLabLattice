'''
Created on Feb 9, 2011

@author: christopherreilly
'''
from util import LRExpError
from labrad.types import Error, parseTypeTag, LRCluster, LRNone
class LabradSetting( object ):
    """
    A persistent representation of a labRAD setting. Make sure the Client class possesses a labRAD connection before attempting to use.
    
    You can optionally initialize with one of the strings from the labRAD setting's 'accept' property.  In this case the parameters property is an ordered list of labRAD type strings for that particular overloaded version of the setting.
    
    This object can be called with arguments just like a regular labRAD setting.
    """
    def __init__( self, serverName, settingName, acceptInfo = None ):
        self.serverName = serverName
        self.settingName = settingName
        self.acceptInfo = acceptInfo
        self.getInfo()

    def getInfo( self ):
        parsed = parseTypeTag( self.acceptInfo )
        if type( parsed ) is LRNone:
            pars = []
        else:
            if type( parsed ) is not LRCluster:
                parsed = ( parsed, )
            pars = [str( par ) for par in parsed]
        self.parameters = pars
        try:
            c = Client.connection
            c.refresh()
            ser = c[self.serverName]
            set = ser.settings[self.settingName]
            self.__name__ = '%s (%s)' % ( set.name, ser.name )
            docList = [ set.description ]
            docList.append( 'Accepts:' )
            docList.append( self.acceptInfo )
            self.returns = list( set.returns )
            docList.append( 'Returns:' )
            docList.append( '\n'.join( self.returns ) )
            self.__doc__ = '\n\n'.join( docList )
        except TypeError:
            self.__name__ = '%s (%s)' % ( self.settingName, self.serverName )
            self.__doc__ = 'labRAD setting: Server ID #%s, Setting ID #%s' % ( self.serverName, self.settingName )
            self.returns = 'Not available'

    def setting( self ):
        try:
            return Client.connection[self.serverName][self.settingName]
        except Error:
            raise LRExpError( 'No labRAD connection' )

    def __call__( self, *pars, **kwpars ):
        return Client.connection.servers[self.serverName].settings[self.settingName]( *pars, **kwpars )
    def __repr__( self ):
        try:
            return str( Client.connection.servers[self.serverName].settings[self.settingName] )
        except TypeError:
            return 'labRAD setting: Server ID #%d, Setting ID #%d' % ( self.serverName, self.settingName )

class Client( object ):
    """
    This packages looks to this class's connection attribute to provide a labRAD connection.
    
    Set this object with a labRAD connection before attempting to use labRAD specific features of the package.
    """
    connection = None
