'''
Created on Mar 15, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui

from . import CompEditDialog

from ..views import MainUnitTree, TreeWidget
from ..models.unit import MainUnitModel
from ..widgets.valueeditor import NameEditor
from ..widgets.unit import UnitButtonRow

class RepeatDialog( CompEditDialog ):
    """
    Edits the repeatUnit of Repeats
    """
    def createGui( self ):
        vl = QtGui.QVBoxLayout( self )
        vl.addWidget( QtGui.QLabel( '<big><b>Edit Repeat</b></big>', self ) )
        vl.addWidget( NameEditor( self ) )
        unitRow = UnitButtonRow( self )
        unitRow.unitCreated.connect( self.newRepeatUnit )
        vl.addWidget( unitRow )
        tree = self.tree = MainUnitTree( self )
        vl.addWidget( TreeWidget( tree, self ) )
        self.updateTree()
    def newRepeatUnit( self, repeatUnit ):
        self.comp.repeatUnit = repeatUnit
        self.updateTree()
    def updateTree( self ):
        if self.comp.repeatUnit:
            self.tree.setModel( MainUnitModel( self.comp.repeatUnit, self ) )
            self.tree.expandAll()
