'''
Created on Mar 29, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui, QtCore

from twisted.internet.defer import inlineCallbacks, returnValue

import sympy, numpy

from labradclient import signals as lrSigs, connect, getHandle, ServerHandle, getID
from serverselect import ServerSelect
from plotter import Plotter
from grapher import formatPath, formatDSName, DIR, DATASET

cacheTime = 5000

class DataVaultWidget( QtGui.QWidget ):

    def __init__( self, parent ):
        super( DataVaultWidget, self ).__init__( parent )
        self.createGui()

    def createGui( self ):
        self.setLayout( QtGui.QVBoxLayout() )

        pathRow = QtGui.QWidget( self )
        pathRow.setLayout( QtGui.QHBoxLayout() )
        pathRow.layout().addWidget( QtGui.QLabel( '<b>Current path:</b>' ) )
        path = self.path = QtGui.QLabel( 'None', self )
        path.setAlignment( QtCore.Qt.AlignLeft )
        pathRow.layout().addWidget( path )
        pathRow.layout().addStretch()

        browser = self.browser = DataVaultBrowser( self )
        browser.pathChanged.connect( path.setText )
        browser.setEnabled( False )

        filterRadio = QtGui.QCheckBox( 'Active Entries', self )
        filterRadio.toggled.connect( browser.filteringToggled )

        self.layout().addWidget( QtGui.QLabel( '<big><b>Data Vault Grapher</b></big>', self ) )
        self.layout().addWidget( pathRow )
        self.layout().addWidget( browser, 1 )
        self.layout().addWidget( filterRadio )

class DataVaultModel( QtCore.QAbstractListModel ):
    class ModelItem( object ):
        def __init__( self, name, isActive = False ):
            self.name = name
            self.isActive = isActive

    def __init__( self, parent, path ):
        super( DataVaultModel, self ).__init__( parent )
        self.datasets = []
        self.dirs = [] if path in ( [''], None ) else [self.ModelItem( '..' )]
        self.path = path

    def newDirectory( self, dir ):
        row = len( self.dirs )
        self.insertRows( row, 1, QtCore.QModelIndex(), self.ModelItem( dir, isActive = True ), DIR )

    def newDataset( self, dataset ):
        row = len( self.dirs + self.datasets )
        self.insertRows( row, 1, QtCore.QModelIndex(), self.ModelItem( dataset, isActive = True ), DATASET )

    def insertRows( self, row, count, parent, item, type ):
        self.beginInsertRows( parent, row, row + count - 1 )
        if type is DIR:
            self.dirs.append( item )
        if type is DATASET:
            self.datasets.append( item )
        self.endInsertRows()

    def rowCount( self, parent ):
        return len( self.dirs ) + len( self.datasets )

    def data( self, index, role ):
        if not index.isValid(): return QtCore.QVariant()
        row = index.row()
        if row < len( self.dirs ):
            item = self.dirs[row]
            if role == QtCore.Qt.DisplayRole:
                return item.name
            if role == QtCore.Qt.DecorationRole:
                return QtGui.QIcon( 'icons/file.svg' )
            if role == QtCore.Qt.ForegroundRole:
                color = ( 200, 0, 0 ) if item.isActive else ( 0, 0, 0 )
                return QtGui.QColor( *color )
            if role == QtCore.Qt.UserRole:
                return [ DIR, item.isActive ]
        else:
            item = self.datasets[ row - len( self.dirs ) ]
            if role == QtCore.Qt.DisplayRole:
                fullName = item.name
                return formatDSName( fullName )
            if role == QtCore.Qt.DecorationRole:
                return QtGui.QIcon( 'icons/dataset.svg' )
            if role == QtCore.Qt.ForegroundRole:
                color = ( 200, 0, 0 ) if item.isActive else ( 0, 0, 0 )
                return QtGui.QColor( *color )
            if role == QtCore.Qt.UserRole:
                return [ DATASET, item.isActive ]
        return QtCore.QVariant()

class DataVaultBrowser( QtGui.QListView ):
    models = {}
    datasets = {}
    dvName = 'Data Vault'
    isFiltering = False
    dvListener = None

    pathChanged = QtCore.pyqtSignal( str )

    def __init__( self, parent ):
        super( DataVaultBrowser, self ).__init__( parent )
        lrSigs.connected.connect( self.lrConnected )
        lrSigs.disconnected.connect( lambda: self.noConnection( 'Disconnected' ) )
        lrSigs.failed.connect( lambda: self.noConnection( 'Connection attempt failed' ) )
        self.doubleClicked.connect( self.itemSelected )
        self.emptyModel = DataVaultModel( self, None )

    def itemSelected( self, index ):
        data = str( index.data().toString() )
        type = index.data( QtCore.Qt.UserRole ).toList()[0].toInt()[0]
        path = list( self.model().sourceModel().path )
        if type is DIR:
            dir = data
            if dir == '..':
                path.pop()
            else:
                path.append( dir )
            model = self.models.get( tuple( path ) )
            if model: self.setModel( model )
        else:
            dsIndex = int( data[:data.index( ' ' )] )
            dataset, delTimer = self.datasets.get( ( tuple( path ), dsIndex ), ( None, None ) )
            if dataset:
                delTimer.stop()
                dataset.show()
                dataset.activateWindow()
            else:
                self.newDataset( path, dsIndex )

    @inlineCallbacks
    def newDataset( self, path, dsIndex ):
        dsHandle = ServerHandle( self.dvName, self, isListening = False )
        yield dsHandle( 'cd', path )
        fullPath, name = yield dsHandle( 'open', dsIndex )
        plotter = Plotter( name, fullPath, dsHandle, self )
        plotter.initDefer.addCallback( lambda _: plotter.show() )
        plotter.initDefer.addErrback(self.catchError)
        delTimer = QtCore.QTimer( self )
        delTimer.setSingleShot( True )
        delTimer.setInterval( cacheTime )
        plotter.finished.connect( lambda result: delTimer.start() )
        delTimer.timeout.connect( plotter.deleteLater )
        self.datasets[( tuple( path ), dsIndex )] = plotter, delTimer
        delTimer.timeout.connect( lambda: self.datasets.pop( ( tuple( path ), dsIndex ) ) )

    def catchError(self, err):
        print err
    def plotterInited( self, plotter ):
        print 'Plotter inited'
        plotter.show()

    def plotterInitError( self, error ):
        print 'Plotter init error'
        print error

    @inlineCallbacks
    def touchDirs( self, path, isActive = False ):
        model = yield self.createModel( path, isActive )
        dirs = [dir.name for dir in model.dirs if dir.name != '..']
        for dir in dirs:
            newPath = list( path )
            newPath.append( dir )
            yield self.touchDirs( newPath, isActive )

    @inlineCallbacks
    def initialize( self ):
        root = yield self.createModel( [''] )
        self.setModel( root )
        self.setEnabled( True )
        for dir in root.dirs:
            path = ['', dir.name]
            yield self.touchDirs( path )

    @inlineCallbacks
    def createModel( self, path, isActive = False ):
        model = DataVaultModel( self, path )
        self.models[tuple( path )] = model

        dv = ServerHandle( self.dvName, model, isListening = False )

        yield dv( 'cd', path )
        dirs, datasets = yield dv( 'dir' )

        model.dirs.extend( [DataVaultModel.ModelItem( dir, isActive ) for dir in dirs] )
        model.datasets.extend( [DataVaultModel.ModelItem( ds, isActive ) for ds in datasets] )

        newDir = getID()
        dv( 'signal: new dir', newDir )
        dv.addListener( lambda x, y: model.newDirectory( y ), newDir )
        dv.addListener( lambda x, y: self.newDirectory( path, y ), newDir )

        newDS = getID()
        dv( 'signal: new dataset', newDS )
        dv.addListener( lambda x, y: model.newDataset( y ), newDS )
        returnValue( model )

    def newDirectory( self, root, dir ):
        path = list( root )
        path.append( dir )
        self.touchDirs( path, isActive = True )

    @inlineCallbacks
    def lrConnected( self ):
        self.getListener()

        if self.dvName is None:
            self.selectDataVault()
            returnValue( None )

        tmp = getHandle()
        servers = yield tmp( 'Manager', 'Servers' )
        if self.dvName not in [server[1] for server in servers]:
            self.selectDataVault()
            returnValue( None )
        self.initialize()

    def getListener( self ):
        if self.dvListener is not None: self.dvListener.deleteLater()
        self.dvListener = dv = ServerHandle( self.dvName, self )
        dv.serverConnected.connect( self.initialize )
        dv.serverDisconnected.connect( lambda: self.noConnection( 'Data Vault disconnected' ) )

    def selectDataVault( self ):
        serverSelect = ServerSelect( self )
        serverSelect.serverSelected.connect( lambda dvName: self.dataVaultSelected( str( dvName ) ) )
        serverSelect.setModal( True )
        serverSelect.show()

    def dataVaultSelected( self, dvName ):
        self.dvName = dvName
        self.getListener()
        self.initialize()

    def noConnection( self, message ):
        self.setModel( self.emptyModel )
        for model in self.models.values(): model.deleteLater()
        self.models = {}
        for dataset in self.datasets.values():
            dataset.close()
            dataset.deleteLater()
        self.datasets = {}
        self.setEnabled( False )

        if message == 'Data Vault disconnected':
            popup = QtGui.QMessageBox( QtGui.QMessageBox.Information, message, message, QtGui.QMessageBox.Ok, self )
        else:
            popup = QtGui.QMessageBox( QtGui.QMessageBox.Question, message, message, QtGui.QMessageBox.Retry | QtGui.QMessageBox.Cancel, self )
            popup.buttonClicked.connect( lambda button: connect() if button.text() == 'Retry' else None )
        popup.show()

    def setModel( self, model ):
        dvBrowser = self
        class FilterModel( QtGui.QSortFilterProxyModel ):
            def filterAcceptsRow( self, row, parent ):
                if not dvBrowser.isFiltering: return True
                index = self.sourceModel().index( row, 0, parent )
                type, isActive = index.data( QtCore.Qt.UserRole ).toList()
                type = type.toInt()[0]
                if type is DIR: return True
                if type is DATASET: return isActive.toBool()
                return False
        proxyModel = FilterModel( dvBrowser )
        proxyModel.setSourceModel( model )
        super( DataVaultBrowser, dvBrowser ).setModel( proxyModel )
        dvBrowser.pathChanged.emit( formatPath( model.path ) )

    def filteringToggled( self, state ):
        self.isFiltering = state
        self.model().invalidateFilter()

    def keyPressEvent( self, keyEvent ):
        if keyEvent.key() == QtCore.Qt.Key_Enter or keyEvent.key() == QtCore.Qt.Key_Return:
            self.doubleClicked.emit( self.currentIndex() )
            keyEvent.accept()
        super( DataVaultBrowser, self ).keyPressEvent( keyEvent )
