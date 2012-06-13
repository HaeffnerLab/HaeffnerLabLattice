'''
Created on Mar 30, 2011

@author: christopherreilly
'''
from PyQt4 import QtCore

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.error import ConnectError

from labrad.wrappers import connectAsync

class Client( object ):
    _cxn = None

class Counter( object ):
    _ID = 111111

class Signals( QtCore.QObject ):
    connecting = QtCore.pyqtSignal()
    connected = QtCore.pyqtSignal()
    failed = QtCore.pyqtSignal()
    disconnected = QtCore.pyqtSignal()

signals = Signals()

@inlineCallbacks
def connect():
    if isConnected(): signals.disconnected.emit()
    signals.connecting.emit()
    try:
        cxn = yield connectAsync( name = 'Grapher client' )
        cxn._cxn.onDisconnect().addBoth( lambda x: connectionLost() )
        Client._cxn = cxn
        signals.connected.emit()
    except ConnectError:
        Client._cxn = None
        signals.failed.emit()

def connectionLost():
    Client._cxn = None
    Counter._ID = 111111
    signals.disconnected.emit()

class ContextHandle( object ):
    def __init__( self ):
        self.context = Client._cxn.context()

    @inlineCallbacks
    def __call__( self, server, setting, *args, **kwargs ):
        kwargs['context'] = self.context
        result = yield Client._cxn.servers[server].settings[setting]( *args, **kwargs )
        returnValue( result )

    def addListener( self, listener, ID ):
        Client._cxn._addListener( listener = listener, source = None, ID = ID, context = self.context )

    def removeListener( self, listener, ID ):
        Client._cxn._removeListener( listener = listener, source = None, ID = ID, context = self.context )

class ServerHandle( ContextHandle, QtCore.QObject ):

    serverConnected = QtCore.pyqtSignal()
    serverDisconnected = QtCore.pyqtSignal()

    def __init__( self, serverName, parent, isListening = True ):
        super( ServerHandle, self ).__init__()
        super( ContextHandle, self ).__init__( parent )
        self.serverName = serverName
        if isListening: self.startListening()

    @inlineCallbacks
    def startListening( self ):
        serverConnected = getID()
        yield super( ServerHandle, self ).__call__( 'Manager', 'Subscribe to Named Message', 'Server Connect', serverConnected, True )
        self.addListener( lambda x, y: self.serverConnected.emit() if y[1] == self.serverName else None, serverConnected )
        serverDisconnected = getID()
        yield super( ServerHandle, self ).__call__( 'Manager', 'Subscribe to Named Message', 'Server Disconnect', serverDisconnected, True )
        self.addListener( lambda x, y: self.serverDisconnected.emit() if y[1] == self.serverName else None, serverDisconnected )

    @inlineCallbacks
    def __call__( self, setting, *args, **kwargs ):
        result = yield super( ServerHandle, self ).__call__( self.serverName, setting, *args, **kwargs )
        returnValue( result )

def getHandle():
    return ContextHandle()
def isConnected():
    return Client._cxn is not None

def getID():
    id = Counter._ID
    Counter._ID += 1
    return id

