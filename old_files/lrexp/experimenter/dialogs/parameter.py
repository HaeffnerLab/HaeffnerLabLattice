'''
Created on Mar 15, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui

from . import CompEditDialog
from input import OldInputDialog
from ..widgets.input import InputButtonRow
from ..widgets.valueeditor import ValueEditor
from ...components import Input, Map

class ParameterDialog( CompEditDialog ):
    """
    Dialog that allows user to edit the properties of a parameter.
    You can edit the parameter's description and you can assign a new or existing input to the parameter's input.
    """
    def createGui( self ):
        vl = QtGui.QVBoxLayout( self )

        for text in ( '<big><b>Edit Parameter</b></big>',
                      '<b>Name:</b> %s' % self.comp.name ):
            vl.addWidget( QtGui.QLabel( text, self ) )

        descriptionEdit = ValueEditor( 'description', self.comp.description, self )
        descriptionEdit.dataChanged.connect( self.writeDescription )

        vl.addWidget( descriptionEdit, 1 )

        inputButtons = InputButtonRow( self, self.index.model().root.comp, self.comp.input )
        inputButtons.inputCreated.connect( self.newInput )
        vl.addWidget( inputButtons )

        done = QtGui.QPushButton( 'Done', self )
        done.clicked.connect( self.accept )
        vl.addWidget( done )

    def writeDescription( self, description, _ ):
        description = str( description )
        self.comp.description = description

    def newInput( self, input ):
        self.comp.input = input
