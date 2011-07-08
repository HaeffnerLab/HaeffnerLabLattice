'''
Created on Mar 30, 2011

@author: christopherreilly
'''
from PyQt4 import QtCore, QtGui

from twisted.internet.defer import inlineCallbacks

from labradclient import signals as lrSigs, getHandle, getID, isConnected

class ServerSelect( QtGui.QDialog ):

    serverSelected = QtCore.pyqtSignal( str )

    def __init__( self, parent ):
        super( ServerSelect, self ).__init__( parent )
        lrSigs.disconnected.connect( self.reject )
        self.createGui()
        self.setMinimumSize( 250, 400 )

    @inlineCallbacks
    def createGui( self ):
        self.setLayout( QtGui.QVBoxLayout() )

        self.layout().addWidget( QtGui.QLabel( "<b>Select Data Vault</b>", self ) )

        serverListWidget = self.serverListWidget = QtGui.QListWidget( self )

        cxn = self.cxn = getHandle()

        servers = yield cxn( 'Manager', 'Servers' )

        serverListWidget.addItems( [server[1] for server in servers] )

        serverListWidget.itemDoubleClicked.connect( self._serverSelected )

        self.layout().addWidget( serverListWidget )

        serverConnect = getID()
        yield cxn( 'Manager', 'Subscribe to Named Message', 'Server Connect', serverConnect, True )
        addServer = lambda x, y: self.addServer( y[1] )
        cxn.addListener( addServer, serverConnect )

        serverDisconnect = getID()
        yield cxn( 'Manager', 'Subscribe to Named Message', 'Server Disconnect', serverDisconnect, True )
        removeServer = lambda x, y: self.removeServer( y[1] )
        cxn.addListener( removeServer, serverDisconnect )

        self.SC, self.SD = ( addServer, serverConnect ), ( removeServer, serverDisconnect )

    def addServer( self, serverName ):
        if not self.serverListWidget.findItems( serverName, QtCore.Qt.MatchExactly ):
            self.serverListWidget.addItem( serverName )

    def removeServer( self, serverName ):
        itemsToRemove = self.serverListWidget.findItems( serverName, QtCore.Qt.MatchExactly )
        itemToRemove = itemsToRemove[0]
        self.serverListWidget.takeItem( self.serverListWidget.row( itemToRemove ) )

    def _serverSelected( self, listWidgetItem ):
        self.serverSelected.emit( str( listWidgetItem.text() ) )
        self.accept()

    def done( self, result ):
        if isConnected():
            self.cxn.removeListener( *self.SC )
            self.cxn.removeListener( *self.SD )
        super( ServerSelect, self ).done( result )
