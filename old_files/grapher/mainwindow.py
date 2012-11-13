'''
Created on Mar 29, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui

menuBar = QtGui.QMenuBar()

from datavault import DataVaultWidget

from labradclient import connect, signals as lrSigs

class MainWindow( QtGui.QMainWindow ):

    def __init__( self, reactor ):
        self.reactor = reactor
        super( MainWindow, self ).__init__()
        self.initGui()
        connect()

    def initGui( self ):

        dvWidget = self.dvWidget = DataVaultWidget( self )
        self.setCentralWidget( dvWidget )
        
        #### menu bar doesn't seem to work
        connectMenu = menuBar.addMenu( '&Grapher' )
        connectAction = self.connectAction = connectMenu.addAction( '&Connect' )
        connectAction.triggered.connect( lambda _: connect() )

        lrSigs.connecting.connect( lambda: connectAction.setEnabled( False ) )
        lrSigs.failed.connect( lambda: connectAction.setEnabled( True ) )
        lrSigs.disconnected.connect( lambda: connectAction.setEnabled( True ) )

        selectDVAction = self.selectDVAction = connectMenu.addAction( 'Select &Data Vault' )
        selectDVAction.triggered.connect( dvWidget.browser.selectDataVault )
        selectDVAction.setEnabled( False )

        lrSigs.connected.connect( lambda: selectDVAction.setEnabled( True ) )
        lrSigs.failed.connect( lambda: selectDVAction.setEnabled( False ) )
        lrSigs.disconnected.connect( lambda: selectDVAction.setEnabled( False ) )
    
    def closeEvent(self, x):
        self.reactor.stop()
