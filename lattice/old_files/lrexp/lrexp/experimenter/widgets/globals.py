'''
Created on Apr 11, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui, QtCore

from ...components import Global

class GlobalsWidget( QtGui.QGroupBox ):
    editRequested = QtCore.pyqtSignal( Global )
    class ListView( QtGui.QListView ):
        def keyPressEvent( self, event ):
            key = event.key()
            if any( x == key for x in ( QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return ) ):
                self.doubleClicked.emit( self.currentIndex() )
                return
            super( GlobalsWidget.ListView, self ).keyPressEvent( event )
    class ListModel( QtCore.QAbstractListModel ):
        def __init__( self, items, parent ):
            super( GlobalsWidget.ListModel, self ).__init__( parent )
            self.items = items

        def rowCount( self, parent ):
            if not parent.isValid():
                return len( self.items )
            return 0

        def data( self, index, role ):
            if role == QtCore.Qt.DisplayRole:
                item = self.items[index.row()]
                return item.name + ' -> ' + repr( item.value )
            return QtCore.QVariant()

    def __init__( self, parent ):
        super( GlobalsWidget, self ).__init__( parent )

        self.setTitle( 'Global Inputs' )
        self.setLayout( QtGui.QHBoxLayout() )

        globalList = self.gl = self.ListView( self )
        globalList.setSelectionMode( globalList.SingleSelection )
        globalList.itemFromIndex = lambda index: globalList.model().items[index.row()] if index.isValid() else None

        globalList.doubleClicked.connect( lambda currentIndex: self.editRequested.emit( globalList.itemFromIndex( currentIndex ) ) )

        globalInfo = QtGui.QGroupBox( 'Global Info', self )
        globalInfo.setLayout( QtGui.QVBoxLayout() )
        self.textLabel = QtGui.QLabel( '<i>Select a global to edit</i>', self )
        self.textLabel.setWordWrap( True )
        globalInfo.layout().addWidget( self.textLabel )

        self.layout().addWidget( globalList )
        self.layout().addWidget( globalInfo )
        self.layout().addStretch()

    def getText( self ):
        return self.textLabel.text()
    def setText( self, text ):
        self.textLabel.setText( text )
    text = property( getText, setText )

    def updateInfo( self, glob ):
        self.text = '<b>%s</b><br>Value: %s<br>Description: <i>%s</i>' % ( glob.name, repr( glob.value ), glob.description )

    def setList( self, globals ):
        self.gl.setModel( self.ListModel( globals, self ) )
        self.gl.selectionModel().currentChanged.connect( lambda indexNew, indexOld: self.updateInfo( self.gl.itemFromIndex( indexNew ) ) )
