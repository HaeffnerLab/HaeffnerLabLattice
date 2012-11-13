'''
Created on Mar 15, 2011

@author: christopherreilly
'''
import os, sys

from PyQt4 import QtGui, QtCore

class FunctionItem( object ):
    """
    Creates a tree-like dictionary from package->module->function structure of python library
    """
    def __init__( self, item, parent = None ):
        self.parent = parent
        self.item = item
        self.getData()
    def getData( self ):
        item = self.item
        self.children = []
        self.data = self.item.__name__.split( '.' )[-1]
        if type( item ) is type( os ):
            self.enabled = False
            file = item.__file__
            self.type = 'Module'
            if '__init__.py' in os.path.basename( file ):
                self.type = 'Package'
                modName = self.item.__name__
                path = os.path.dirname( file )
                childFiles = os.listdir( path )
                childFileTups = [childFile.split( '.' ) for childFile in childFiles]
                childMods = [childTup[0] for childTup in childFileTups if len( childTup ) is 2 and childTup[1] == 'py']
                childMods.remove( '__init__' )
                for childMod in childMods:
                    try:
                        fullChildModName = '.'.join( ( modName, childMod ) )
                        __import__( fullChildModName )
                        importedModule = sys.modules[fullChildModName]
                    except ImportError:
                        continue
                    self.children.append( FunctionItem( importedModule, self ) )
                childDirs = [childFile for childFile in childFiles if os.path.isdir( os.path.join( path, childFile ) )]
                for dir in childDirs:
                    try:
                        fullChildPackageName = '.'.join( ( modName, dir ) )
                        __import__( fullChildPackageName )
                        package = sys.modules[fullChildPackageName]
                    except ImportError: continue
                    self.children.append( FunctionItem( package, self ) )
            functions = [self.item.__dict__[key] for key in sorted( self.item.__dict__ ) if callable( self.item.__dict__[key] )]
            for function in functions: self.children.append( FunctionItem( function, self ) )
            return
        self.type = 'Function'
        self.enabled = True

class FunctionModel( QtCore.QAbstractItemModel ):
    """
    Back end to function trees
    """
    def __init__( self, module, parent ):
        super( FunctionModel, self ).__init__( parent )
        self.root = FunctionItem( module )

    def rowCount( self, parent ):
        if not parent.isValid(): return len( self.root.children )
        return len( parent.internalPointer().children )

    def columnCount( self, parent ):
        return 1

    def index( self, row, column, parent ):
        if not self.hasIndex( row, column, parent ):
            return QtCore.QModelIndex()
        if not parent.isValid():
            return self.createIndex( row, 0, self.root.children[row] )
        return self.createIndex( row, 0, parent.internalPointer().children[row] )

    def parent( self, index ):
        if not index.isValid(): return QtCore.QModelIndex()
        parent = index.internalPointer().parent
        if parent is self.root:
            return QtCore.QModelIndex()
        if parent.parent is self.root:
            return self.createIndex( self.root.children.index( parent ), 0, parent )
        return self.createIndex( parent.parent.children.index( parent ), 0, parent )

    def data( self, index, role ):
        if not index.isValid():
            return QtCore.QVariant()
        modelItem = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return modelItem.data
        if role == QtCore.Qt.FontRole:
            if modelItem.enabled:
                font = QtGui.QFont()
                font.setWeight( QtGui.QFont.Bold )
                return font

