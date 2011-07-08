'''
Created on Mar 15, 2011

@author: christopherreilly
'''
import inspect
from PyQt4 import QtCore, QtGui
from ...components import Function, Input, Global, Map, Parameter, isUnit, forceUnit, Action, Scan, Sequence, Repeat
from ... import experimenter
import os

ICONSPATH = os.path.join( experimenter.__path__[0], 'icons' )

class CompItem( object ):
    """
    Creates a tree-like object from lrexp.component objects
    """
    class List( object ):
        def __init__( self, name, list, data = None ):
            self.name = name
            self.list = list
            self.data = data

    def __init__( self, comp, parent = None, row = 0 ):
        if parent is None: forceUnit( comp )
        self.comp = comp
        self.parent = parent
        self.children = []
        self.getData()
        self.row = row

    def getData( self ):
        self.children = []
        self.data = repr( self.comp )
        comp, compType = ( self.comp, type( self.comp ) )
        if issubclass( compType, Function ):
            args = [comp.parameters[key] for key in sorted( comp.parameters ) if type( key ) is int ]
            if len( args ) > 0:
                self.appendChild( self.List( 'Arguments', args ) )
            argList = comp.argList if type( comp.argList ) is list else [comp.argList]
            if comp.argListEnabled and len( argList ) > 0:
                self.appendChild( self.List( 'List Arguments', comp.argList, inspect.getargspec( comp.function )[1] ) )
            if compType is Action:
                self.appendChild( comp.result )
            return
        if compType is Parameter:
            self.appendChild( comp.input )
        if compType is Scan:
            self.appendChild( comp.scanUnit )
            self.appendChild( self.List( 'Scan Parameters', ( comp.min, comp.max, comp.steps ) ) )
        if compType is Sequence:
            for unit in comp.sequence:
                self.appendChild( unit )
            return
        if compType is Repeat:
            self.appendChild( comp.repeatUnit )
            self.appendChild( comp.repeats )
            return
        if compType is self.List:
            name, dataList, data = ( comp.name, comp.list, comp.data )
            self.data = name
            if name == 'List Arguments':
                self.data = '%s (%s)' % ( name, data )
                if isinstance( dataList, Input ):
                    self.appendChild( dataList )
                    return
            [self.appendChild( item ) for item in dataList]
            return

    def appendChild( self, child ):
        self.children.append( CompItem( child , self, len( self.children ) ) )

class UnitModel( QtCore.QAbstractItemModel ):
    """
    Back end to unit trees
    """
    def __init__( self, unit, parent = None ):
        super( UnitModel, self ).__init__( parent )
        self.root = CompItem( unit )
    def columnCount( self, parent = None ):
        return 1
    def rowCount( self, parent = QtCore.QModelIndex() ):
        if not parent.isValid():
            return 1
        return len( parent.internalPointer().children )
    def data( self, index, role ):
        if not index.isValid():
            return QtCore.QVariant()
        if role == QtCore.Qt.DisplayRole:
            return index.internalPointer().data
        if role == QtCore.Qt.DecorationRole:
            compType = type( index.internalPointer().comp )
            filename = {Action:'action', Scan:'scan', Sequence:'sequence', Repeat:'repeat'}.get( compType )
            if filename is None: return QtCore.QVariant()
            return QtGui.QIcon( os.path.join( ICONSPATH, filename + '.svg' ) )

    def index( self, row, column, parent ):
        if not self.hasIndex( row, column, parent ):
            return QtCore.QModelIndex()
        if not parent.isValid():
            return self.createIndex( 0, 0, self.root )
        try:
            return self.createIndex( row,
                                    column,
                                    parent.internalPointer().children[row] )
        except IndexError:
            return QtCore.QModelIndex()
    def parent( self, index ):
        parent = index.internalPointer().parent
        if parent is None:
            return QtCore.QModelIndex()
        return self.createIndex( parent.row, 0, parent )

    def findMatches( self, target, rootIndex = None ):
        if rootIndex is None: rootIndex = self.index( 0, 0, QtCore.QModelIndex() )
        matches = []
        if rootIndex.internalPointer().comp is target: matches.append( rootIndex )
        children = rootIndex.internalPointer().children
        for row in range( len( children ) ):
            childIndex = self.index( row, 0, rootIndex )
            matches.extend( self.findMatches( target, childIndex ) )
        return matches

class MainUnitModel( UnitModel ):
    """
    Adds component-specific coloring
    
    Red indicates an unconfigured Unit
    Blue indicates that input is a Result
    Green indicates that input is a Map
    Purple indicates that input is a Global
    """
    def data( self, index, role ):
        data = super( MainUnitModel, self ).data( index, role )
        if data is not None: return data
        if role == QtCore.Qt.FontRole:
            if isUnit( index.internalPointer().comp ):
                font = QtGui.QFont()
                font.setWeight( QtGui.QFont.Bold )
                return font
        if role == QtCore.Qt.ForegroundRole:
            comp = index.internalPointer().comp
            if isUnit( comp ) and not comp.configured:
                return QtGui.QBrush( QtGui.QColor( 255, 0, 0 ) )
            if type( comp ) is Action.Result:
                return QtGui.QBrush( QtGui.QColor( 0, 0, 255 ) )
            if type( comp ) is Map:
                return QtGui.QBrush( QtGui.QColor( 0, 255, 0 ) )
            if type( comp ) is Global:
                return QtGui.QBrush( QtGui.QColor( 148, 0, 211 ) )
        return QtCore.QVariant()

class ExecModel( UnitModel ):
    """
    Updates component name to indicate execution progress
    """
    def rowCount( self, parent = QtCore.QModelIndex() ):
        if not parent.isValid(): return 1
        if isinstance( parent.internalPointer().comp, Sequence ):
            return len( parent.internalPointer().children )
        if isinstance( parent.internalPointer().comp, Action ):
            return 0
        return 1
    def data( self, index, role ):
        if not index.isValid():
            return QtCore.QVariant()
        if role == QtCore.Qt.DisplayRole:
            compItem = index.internalPointer()
            data = compItem.data
            if hasattr( compItem, 'progress' ) and not compItem.progress is None:
                data += ' - ' + compItem.progress
            return data
        if role == QtCore.Qt.ForegroundRole:
            return QtCore.QVariant()
        if role == QtCore.Qt.DecorationRole:
            return super( ExecModel, self ).data( index, role )
        return QtCore.QVariant()

class InputModel( UnitModel ):
    """
    Enables tracking of a specific input.
    
    Red indicates that 'hot' input is an Input or Global
    Purple indicates that 'hot' input is a Result
    Brown indicates that 'hot' input is a Map
    Blue indicates that input is a Result and not 'hot'
    Green indicates that input is a Map and not 'hot'
    """
    def __init__( self, input, unit, parent ):
        super( InputModel, self ).__init__( unit, parent )
        self.input = input

    def data( self, index, role ):
        data = super( InputModel, self ).data( index, role )
        if data is not None: return data
        comp = index.internalPointer().comp
        if role == QtCore.Qt.FontRole:
            if isinstance( comp, Input ):
                font = QtGui.QFont()
                font.setWeight( QtGui.QFont.Bold )
                return font
        if role == QtCore.Qt.ForegroundRole:
            if comp is self.input and not self.input is None:
                compType = type( comp )
                if compType is Action.Result:
                    return QtGui.QBrush( QtGui.QColor( 170, 0, 255 ) )
                if compType is Map:
                    return QtGui.QBrush( QtGui.QColor( 255, 255, 0 ) )
                return QtGui.QBrush( QtGui.QColor( 255, 0, 0 ) )
            if type( comp ) is Action.Result:
                return QtGui.QBrush( QtGui.QColor( 0, 0, 255 ) )
            if type( comp ) is Map:
                return QtGui.QBrush( QtGui.QColor( 0, 255, 0 ) )
        return QtCore.QVariant()

    def flags( self, index ):
        if issubclass( index.internalPointer().comp.__class__, Input ):
            return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.NoItemFlags

class ReadOnlyInputModel( InputModel ):
    """
    Activating disabled
    """
    def flags( self, index ):
        return QtCore.Qt.NoItemFlags

class ScanInputModel( InputModel ):
    """
    Only inputs can be activated
    """
    def flags( self, index ):
        compType = type( index.internalPointer().comp )
        if compType is Input:
            return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.NoItemFlags

