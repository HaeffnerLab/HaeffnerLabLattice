'''
Created on Mar 15, 2011

@author: christopherreilly
'''
import yaml

from PyQt4 import QtGui
from . import CompEditDialog
from ..widgets.valueeditor import ValueEditor
from ..views import InputTree, TreeWidget
from ..models.unit import InputModel, ReadOnlyInputModel

class InputDialog( CompEditDialog ):
    """
    Allows editing of an input's description, value, and default members.
    Values and defaults are interpreted as YAML strings.
    A tree is provided which displays which parameters share this input.
    """
    def createGui( self ):
        vl = QtGui.QVBoxLayout( self )

        for text in ( '<big><b>Edit Input</b></big>', '<b>ID:</b> #%d' % self.comp.id ):
            vl.addWidget( QtGui.QLabel( text, self ) )

        hlMain = QtGui.QHBoxLayout( QtGui.QFrame( self ) )

        vlEdit = QtGui.QVBoxLayout( QtGui.QFrame( self ) )

        descriptionEdit = ValueEditor( 'description', self.comp.description, self )
        descriptionEdit.dataChanged.connect( self.writeData )
        vlEdit.addWidget( descriptionEdit )

        valueEdit = ValueEditor( 'value', yaml.dump( self.comp.value ), self )
        valueEdit.dataChanged.connect( self.writeData )
        vlEdit.addWidget( valueEdit )
        self.valueEdit = valueEdit

        done = QtGui.QPushButton( 'Done', self )
        done.clicked.connect( self.accept )
        done.setSizePolicy( QtGui.QSizePolicy() )
        vlEdit.addWidget( done )

        vlEdit.addStretch()

        hlMain.addWidget( vlEdit.parent() )

        tree = InputTree( self )
        tree.setModel( ReadOnlyInputModel( self.comp, self.index.model().root.comp, self ) )
        tree.expandTo( self.comp )
        hlMain.addWidget( TreeWidget( tree, self ) )

        vl.addWidget( hlMain.parent() )

    def writeData( self, data, name ):
        data, name = ( str( data ), str( name ) )
        input = self.comp
        if name == 'description':
            input.description = data
            return
        if name == 'value':
            input.value = yaml.load( data )
            return

class ResultDialog( InputDialog ):
    """
    The value property of Results are gettable, not settable, so we remove the valueEdit attribute.
    """
    def createGui( self ):
        super( ResultDialog, self ).createGui()
        self.valueEdit.hide()

class OldInputDialog( QtGui.QDialog ):
    """
    Allows user to select an input from a tree.
    """
    def __init__( self, input, comp, parent ):
        super( OldInputDialog, self ).__init__( parent )
        self.model = InputModel( input, comp, self )
        self.input = input
        self.createGui()

    def createGui( self ):
        QtGui.QVBoxLayout( self )

        tree = InputTree( self )
        tree.setModel( self.model )
        tree.activated.connect( self.inputSelected )
        tree.expandTo( self.input ) if self.input else tree.expandAll()

        self.layout().addWidget( TreeWidget( tree, self ) )

    def inputSelected( self, index ):
        self.input = index.internalPointer().comp
        self.accept()
