'''
Created on Feb 22, 2011

@author: christopherreilly

The BaseTree is how a unit heirarchical structure is visualized in Qt.
'''
from PyQt4 import QtGui, QtCore

class TreeWidget( QtGui.QFrame ):
    """
    Equips a tree with expand-all and collapse-all capability
    """
    def __init__( self, tree, parent, name = None ):
        super( TreeWidget, self ).__init__( parent )

        layout = QtGui.QVBoxLayout( self )

        if name: layout.addWidget( QtGui.QLabel( name, self ) )

        layout.addWidget( tree )

        hlButtons = QtGui.QWidget( self )
        QtGui.QHBoxLayout( hlButtons )

        for name, slot in ( ( 'Expand All', tree.expandAll ), ( 'Collapse All', tree.collapseAll ) ):
            button = QtGui.QPushButton( name, self )
            button.clicked.connect( slot )
            hlButtons.layout().addWidget( button )

        hlButtons.layout().addStretch()

        layout.addWidget( hlButtons )

        self.setFrameStyle( QtGui.QFrame.StyledPanel )


class BaseTree( QtGui.QTreeView ):
    """
    Formats a standard QtGui.QTreeView and links the Return key to the activate signal
    """
    activated = QtCore.pyqtSignal( QtCore.QModelIndex )
    def __init__( self, parent = None ):
        super( BaseTree, self ).__init__( parent )
        self.doubleClicked.connect( self.activated.emit )
        self.setAlternatingRowColors( True )
        self.setHeaderHidden( True )
        self.setExpandsOnDoubleClick( False )

    def keyPressEvent( self, keyEvent ):
        if keyEvent.key() == QtCore.Qt.Key_Enter or keyEvent.key() == QtCore.Qt.Key_Return:
            self.activated.emit( self.currentIndex() )
            keyEvent.accept()
        super( BaseTree, self ).keyPressEvent( keyEvent )

class MainUnitTree( BaseTree ):
    """
    Expands to the previously edited item after an edit event
    """
    def dataChanged( self, indexL, indexR ):
        self.collapseAll()
        self.update()
        def getparents( child, parents = None ):
            if parents is None: parents = []
            if child.parent().isValid():
                parents.insert( 0, child.parent() )
                return getparents( child.parent(), parents )
            return parents
        for parent in getparents( indexL ):
            self.expand( parent )
        super( MainUnitTree, self ).dataChanged( indexL, indexR )

class InputTree( BaseTree ):
    """
    Expands out to all the 'hot' inputs
    """
    def expandTo( self, target ):
        def getTargetMatches( parent, matches ):
            if parent.internalPointer().comp is target:
                matches.append( parent )
            children = [parent.child( row, 0 ) for row in range( parent.model().rowCount( parent ) )]
            for child in children:
                getTargetMatches( child, matches )
        def getChain( child, chain ):
            chain.append( child )
            parent = child.parent()
            if parent in chain or not parent.isValid(): return
            getChain( parent, chain )
        if self.model() is None: return
        matches = []
        getTargetMatches( self.model().index( 0, 0, QtCore.QModelIndex() ), matches )
        chain = []
        for match in matches: getChain( match, chain )
        for index in chain:
            self.expand( index )

class ReorderListView( QtGui.QListView ):
    """
    A reorderable list view
    """
    def __init__( self, list, modelClass, parent ):
        super( ReorderListView, self ).__init__( parent )
        self.setMovement( QtGui.QListView.Snap )
        self.setDragDropOverwriteMode( False )
        self.setDropIndicatorShown( True )
        self.modelClass = modelClass
        self.setModel( list )
        self.model().setSupportedDragActions( QtCore.Qt.CopyAction )

    def setModel( self, list ):
        super( ReorderListView, self ).setModel( self.modelClass( list, self ) )
