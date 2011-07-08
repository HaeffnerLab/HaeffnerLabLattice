'''
Created on Mar 15, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui, QtCore
from . import CompEditDialog

from ..models.reorder import ReorderListModel
from ..views import ReorderListView
from ..widgets.modeselector import ExecModeSelector
from ..widgets.valueeditor import NameEditor
from ..widgets.unit import UnitButtonRow
class SequenceDialog( CompEditDialog ):
    """
    Edit a Sequence instance.
    Add a new unit or load a unit or remove a unit or rearrange the order of existing units in the sequence.
    """
    def createGui( self ):
        vl = QtGui.QVBoxLayout( self )

        vl.addWidget( QtGui.QLabel( '<big><b>Edit Sequence</b></big>' ) )

        vl.addWidget( NameEditor( self ) )

        mode = ExecModeSelector( self )
        mode.setMode( self.comp.mode )
        vl.addWidget( mode )

        sequenceList = ReorderListView( self.comp.sequence, ReorderListModel, self )
        self.sequenceList = sequenceList

        vl.addWidget( sequenceList )

        unitRow = UnitButtonRow( self )
        unitRow.unitCreated.connect( self.newUnit )

        remove = QtGui.QPushButton( 'Remove Unit' )
        remove.clicked.connect( self.removeUnit )
        unitRow.layout().addWidget( remove, 0, QtCore.Qt.AlignTop )

        vl.addWidget( unitRow )

    def newUnit( self, unit ):
        self.comp.addUnit( unit )
        self.sequenceList.setModel( self.comp.sequence )

    def removeUnit( self ):
        self.comp.sequence.pop( self.sequenceList.currentIndex().row() )
        self.sequenceList.setModel( self.comp.sequence )
