'''
Created on Mar 15, 2011

@author: christopherreilly
'''

from PyQt4 import QtCore, QtGui

from ..views import BaseTree
from ..models.function import FunctionModel
from ...lr import Client, LabradSetting

class NewFunctionDialog( QtGui.QDialog ):
    """
    Selects a new function from the lrexp package's function module.
    Add new functions here to improve the usefulness of this application.
    Browse through a package->module->function tree.
    """
    def __init__( self, parent, module, title ):
        super( NewFunctionDialog, self ).__init__( parent )
        self.module = module
        self.title = title
        self.createGui()

    def createGui( self ):
        vl = QtGui.QVBoxLayout( self )

        vl.addWidget( QtGui.QLabel( '<big><b>%s</b></big>' % self.title ) )

        hl = QtGui.QHBoxLayout( QtGui.QFrame( self ) )

        tree = BaseTree( self )
        tree.setModel( FunctionModel( self.module, self ) )
        tree.selectionModel().selectionChanged.connect( self.updateInfo )
        tree.activated.connect( self.functionSelected )
        hl.addWidget( tree, 4 )
        self.tree = tree

        info = QtGui.QLabel( '<i>Function info</i>', self )
        info.setTextFormat( QtCore.Qt.RichText )
        info.setFrameStyle( QtGui.QFrame.Plain | QtGui.QFrame.Box )
        info.setWordWrap( True )
        info.setAlignment( QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft )
        hl.addWidget( info, 3 )
        self.info = info

        vl.addWidget( hl.parent() )

    def updateInfo( self, index, old ):
        index = index.indexes()[0]
        modelItem = index.internalPointer()
        info = '<big>%s:<br><b>%s</b></big><br><br>' % ( modelItem.type, modelItem.data )
        info += '<i>%s</i>' % ( 'No documentation' if modelItem.item.__doc__ is None else modelItem.item.__doc__.strip() )
        self.info.setText( info )

    def functionSelected( self, index ):
        modelItem = index.internalPointer()
        if modelItem.enabled:
            self.accept()

class NewLRSettingDialog( QtGui.QDialog ):
    """
    Selects a new labRAD setting from a dynamically generated dictionary obtained from the labRAD manager.
    Browse through settings organized by server.  User must select which overloaded version of the function to use.
    See the labRAD documentation to learn the syntax.
    """
    class LRSettingModel( QtCore.QAbstractItemModel ):
        def __init__( self, lrList, parent ):
            super( NewLRSettingDialog.LRSettingModel, self ).__init__( parent )
            self.lrList = lrList
        def columnCount( self, parent = None ):
            return 1
        def rowCount( self, parent = None ):
            if not parent.isValid():
                return len( self.lrList )
            depth = parent.internalPointer()['Type']
            if depth == 'Server':
                return len( parent.internalPointer()['Settings'] )
            if depth == 'Setting':
                return len( parent.internalPointer()['Accepts'] )
            if depth == 'Accept':
                return 0
            return 0
        def index( self, row, column, parent ):
            if not self.hasIndex( row, column, parent ):
                return QtCore.QModelIndex()
            if not parent.isValid():
                return self.createIndex( row, 0, self.lrList[row] )
            depth = parent.internalPointer()['Type']
            if depth == 'Server':
                return self.createIndex( row, 0, parent.internalPointer()['Settings'][row] )
            if depth == 'Setting':
                return self.createIndex( row, 0, parent.internalPointer()['Accepts'][row] )
            return QtCore.QModelIndex()
        def data( self, index, role ):
            if not index.isValid():
                return QtCore.QVariant()
            depth = index.internalPointer()['Type']
            if role == QtCore.Qt.DisplayRole:
                if depth in ( 'Server', 'Setting' ):
                    return index.internalPointer()['Name']
                if depth == 'Accept':
                    info = index.internalPointer()['Info']
                    return info if info else 'No Input'
            if role == QtCore.Qt.FontRole:
                if depth == 'Accept':
                    font = QtGui.QFont()
                    font.setWeight( QtGui.QFont.Bold )
                    return font
            return QtCore.QVariant()

        def parent( self, index ):
            if not index.isValid(): return QtCore.QModelIndex()
            item = index.internalPointer()
            depth = item['Type']
            if depth == 'Server':
                return QtCore.QModelIndex()
            if depth == 'Setting':
                parent = item['Server']
                return self.createIndex( parent['Row'], 0, parent )
            if depth == 'Accept':
                parent = item['Setting']
                return self.createIndex( parent['Row'], 0, parent )

    def __init__( self, parent ):
        super( NewLRSettingDialog, self ).__init__( parent )
        self.createLRList()
        self.createGui()

    def createLRList( self ):
        def append( p, c ):
            c['Row'] = len( p )
            p.append( c )
        l = []
        servers = Client.connection.servers
        for serverName in servers.keys():
            server = servers[serverName]
            serverD = {}
            serverD['Type'] = 'Server'
            serverD['Name'] = server.name
            serverD['Description'] = server.__doc__
            serverD['Settings'] = settingsList = []
            settings = server.settings
            for settingName in settings.keys():
                setting = settings[settingName]
                settingConfig = {}
                settingConfig['Type'] = 'Setting'
                settingConfig['Name'] = setting.name
                settingConfig['Description'] = setting.description
                settingConfig['Server'] = serverD
                settingConfig['Accepts'] = acceptsList = []
                accepts = setting.accepts
                for acceptInfo in accepts:
                    accept = {}
                    accept['Type'] = 'Accept'
                    accept['Info'] = acceptInfo
                    accept['Setting'] = settingConfig
                    append( acceptsList, accept )
                append( settingsList, settingConfig )
            append( l, serverD )
        self.lrList = l

    def createGui( self ):
        hl = QtGui.QHBoxLayout( self )

        tree = BaseTree( self )
        tree.setModel( self.LRSettingModel( self.lrList, self ) )
        tree.activated.connect( self.settingSelected )
        tree.selectionModel().selectionChanged.connect( self.selectionChanged )

        hl.addWidget( tree, 1 )

        details = QtGui.QLabel( '<big><b>Setting details</b></big>' )
        details.setTextFormat( QtCore.Qt.RichText )
        details.setWordWrap( True )
        details.setAlignment( QtCore.Qt.AlignTop )

        hl.addWidget( details, 1 )
        self.details = details

    def selectionChanged( self, selected, deselected ):
        index = selected.indexes()[0]
        self.details.setText( self.formatItem( index.internalPointer() ) )

    @staticmethod
    def formatItem( d ):
        text = ''
        info = None
        if d.has_key( 'Setting' ):
            d, info = d['Setting'], d['Info']
        text += '<big><b>%s</b></big><br>' % d['Name']
        if info: text += 'Parameters: <b>%s</b><br>' % info
        if d.has_key( 'Server' ):
            text += 'Server: <b>%s</b><br>' % d['Server']['Name']
        text += 'Description:<br>'
        text += '<i>%s</i>' % d['Description']
        return text

    def settingSelected( self, index ):
        if index.isValid():
            result = index.internalPointer()
            if result['Type'] == 'Accept':
                accept, setting, server = ( result['Info'], result['Setting']['Name'], result['Setting']['Server']['Name'] )
                lrSetting = LabradSetting( server, setting, accept )
                self.lrSetting = lrSetting
                self.accept()

