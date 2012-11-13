'''
Created on Apr 15, 2011

@author: SAM FENDELL
'''

from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks
from sympy import sympify, lambdify, Symbol

from grapher import getSympyFunc, XPLOT, YPLOT, XAXIS, YAXIS

class ConfigDialog( QtGui.QDialog ):
    axesChanged = QtCore.pyqtSignal()
    xSelection = None
    ySelection = None
    def __init__( self, parent, xVars, yVars, dsHandle ):
        super( ConfigDialog, self ).__init__( parent )

        self.dsHandle = dsHandle

        self.setLayout( QtGui.QVBoxLayout() )
        self.layout().addWidget( QtGui.QLabel( "<b><big>Edit Data Sets</big></b>", self ), 0, QtCore.Qt.AlignCenter )

        functions = QtGui.QWidget()
        functions.setLayout( QtGui.QHBoxLayout() )

        xList = self.xList = XAxesList( self, xVars )
        functions.layout().addWidget( xList )

        yList = self.yList = YAxesList( self, yVars )
        functions.layout().addWidget( yList )

        self.layout().addWidget( functions )
        buttonRow = QtGui.QWidget( self )
        QtGui.QHBoxLayout( buttonRow )
        setDefaults = QtGui.QPushButton( 'Set as default', self )
        setDefaults.clicked.connect( self.setDefaults )
        buttonRow.layout().addWidget( setDefaults )
        buttonRow.layout().addStretch()
        cancelButton = QtGui.QPushButton( 'Cancel', self )
        cancelButton.clicked.connect( self.reject )
        buttonRow.layout().addWidget( cancelButton )
        applyButton = QtGui.QPushButton( 'Apply', self )
        applyButton.clicked.connect( self.accept )
        buttonRow.layout().addWidget( applyButton )
        self.layout().addWidget( buttonRow )

    def setDefaults( self ):
        self.xList.listView.update( QtCore.QModelIndex() )
#        def getData( item ):
#            i = item.data( AXIS )
#            if i.isValid():
#                return i.toInt()[0]
#            f = item.data( FORMULA )
#            if f.isValid():
#                return str( item.text() ) , str( f.toString() )
#            raise Exception( 'Could not get data' )
#        xDef = getData( self.xList.listView.selectedItems()[0] )
#        self.dsHandle( 'add parameter', XPLOT, xDef )
#        yDefs = tuple( [getData( item ) for item in self.yList.listView.selectedItems()] )
#        self.dsHandle( 'add parameter', YPLOT, yDefs )

    def show( self ):
        super( ConfigDialog, self ).show()
        self.xList.show()
        self.yList.show()

    def reject( self ):
        super( ConfigDialog, self ).reject()
        if self.xList.reject() or self.yList.reject(): self.axesChanged.emit()

    def accept( self ):
        super( ConfigDialog, self ).accept()
        if self.xList.accept() or self.yList.accept(): self.axesChanged.emit()

class AxesList( QtGui.QWidget ):

    sympyVars = None

    def __init__( self, parent ):
        super( AxesList, self ).__init__( parent )
        self.setLayout( QtGui.QVBoxLayout() )
        self.layout().addWidget( QtGui.QLabel( "<b>%s</b>" % self.title, self ) )

        self.listView = listView = QtGui.QListView( self )
        listView.setModel( AxesListModel( self ) )
        self.layout().addWidget( listView, 1 )

        buttonRow = QtGui.QWidget()
        QtGui.QHBoxLayout( buttonRow )

        newButton = QtGui.QPushButton( "New", self )
        newButton.clicked.connect( self.newItem )
        buttonRow.layout().addWidget( newButton )

        removeButton = QtGui.QPushButton( "Remove", self )
        removeButton.clicked.connect( lambda: self.removeAxes( listView.selectedIndexes() ) )
        buttonRow.layout().addWidget( removeButton )

        self.layout().addWidget( buttonRow )

    def newItem( self ):
        name, result = QtGui.QInputDialog.getText( self, "New Function", "Enter Name:" )
        if not result or name.isEmpty():
            return
        name = str( name )
        error = False
        while( True ):
            formula, result = QtGui.QInputDialog.getText( self, "New Function" , "Bad Input, try again:" if error else "Enter Formula:" )
            if not result:
                return
            formula = str( formula )
            function = getSympyFunc( formula, self.sympyVars )
            if function: break
            error = True

        self.listView.model().addAxis( Map( name, function, formula ) )

    def addColumns( self, names ):
        for column, name in enumerate( names ):
            self.listView.model().addAxis( Column( name, column, "Column %d" % ( column + 1 ) ) )

    def removeAxes( self, indexes ):
        for index in indexes:
            axis = self.listView.model().axes[index.row()]
            if type( axis ) is Map:
                self.listView.model().removeAxis( index )
                if index in self.selectedIndexes:
                    self.selectedIndexes.remove( index )
                    self.result = True

    def show( self ):
        self.selectedIndexes = self.listView.selectedIndexes()
        self.result = False

    def accept( self ):
        self.selectedIndexes = self.listView.selectedIndexes()
        self.result = True
        return self.result

    def reject( self ):
        tmp = self.listView.selectionMode()
        self.listView.setSelectionMode( self.listView.MultiSelection )
        self.listView.selectionModel().clearSelection()
        if len( self.selectedIndexes ):
            for index in self.selectedIndexes:
                self.listView.setCurrentIndex( index )
        else:
            self.listView.setCurrentRow( 0 )
        self.listView.setSelectionMode( tmp )
        return self.result

class AxesListModel( QtCore.QAbstractListModel ):
    def __init__( self, parent ):
        super( AxesListModel, self ).__init__( parent )
        self.axes = []
    def rowCount( self, parent = QtCore.QModelIndex() ):
        return len( self.axes )
    def data( self, index, role ):
        if not index.isValid():
            return QtCore.QVariant()
        axis = self.axes[index.row()]
        if role == QtCore.Qt.DisplayRole:
            return axis.name
        if role == QtCore.Qt.ToolTipRole:
            return axis.description
        if role == QtCore.Qt.FontRole:
            if type( axis ) is Column:
                bold = QtGui.QFont()
                bold.setBold( True )
                return bold
        return QtCore.QVariant()
    def addAxis( self, axis ):
        self.beginInsertRows( QtCore.QModelIndex(), len( self.axes ), len( self.axes ) )
        self.axes.append( axis )
        self.endInsertRows()
    def removeAxis( self, index ):
        axis = self.axes[index.row()]
        self.beginRemoveRows( QtCore.QModelIndex(), index.row(), index.row() )
        self.axes.remove( axis )
        self.endRemoveRows()

class Axis( object ):
    def __init__( self, name, data, description ):
        self.name = name
        self.data = data
        self.description = description
class Column( Axis ): pass
class Map( Axis ): pass

class XAxesList( AxesList ):
    title = XAXIS
    def __init__( self, parent, xVars ):
        super( XAxesList, self ).__init__( parent )
        self.sympyVars = [Symbol( 'x_%d' % ( i + 1 ) ) for i in range( len( xVars ) ) ]
        self.addColumns( xVars )
        self.listView.setSelectionMode( self.listView.SingleSelection )

class YAxesList( AxesList ):
    title = YAXIS
    def __init__( self, parent, yVars ):
        super( YAxesList, self ).__init__( parent )
        self.sympyVars = [Symbol( 'y_%d' % ( i + 1 ) ) for i in range( len( yVars ) )]
        self.addColumns( yVars )
        self.listView.setSelectionMode( self.listView.ExtendedSelection )
