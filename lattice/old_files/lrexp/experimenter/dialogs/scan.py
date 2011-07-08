'''
Created on Mar 15, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui
from . import CompEditDialog

from ..models.unit import ScanInputModel
from ..widgets.modeselector import ExecModeSelector
from ..widgets.unit import UnitButtonRow
from ..widgets.valueeditor import NameEditor
from ..views import InputTree, TreeWidget
from ...components import Input

class ScanDialog( CompEditDialog ):
    """
    Edits a Scan instance.
    Can load a new scan unit or create a new one.
    Select a scan input from the scan unit tree.
    """
    def createGui( self ):
        vl = QtGui.QVBoxLayout( self )
        vl.addWidget( QtGui.QLabel( '<big><b>Edit Scan</b></big>' ) )

        vl.addWidget( NameEditor( self ) )

        mode = ExecModeSelector( self )
        mode.setMode( self.comp.mode )
        vl.addWidget( mode )

        unitRow = UnitButtonRow( self )
        unitRow.unitCreated.connect( self.newScanUnit )
        vl.addWidget( unitRow )

        vlInput = QtGui.QVBoxLayout( QtGui.QFrame( self ) )
        vlInput.parent().setFrameStyle( QtGui.QFrame.Plain | QtGui.QFrame.Box )
        vlInput.addWidget( QtGui.QLabel( '<b>Scan Input</b>', self ) )

        tree = InputTree( self )
        tree.activated.connect( self.changeInput )
        vlInput.addWidget( TreeWidget( tree, self ) )
        self.tree = tree
        self.updateTree()

        vl.addWidget( vlInput.parent() )

    def updateTree( self ):
        if self.comp.scanUnit:
            self.tree.setModel( ScanInputModel( self.comp.scanInput, self.comp.scanUnit, self ) )
            self.tree.expandTo( self.comp.scanInput ) if self.comp.scanInput else self.tree.expandAll()

    def changeInput( self, index ):
        comp = index.internalPointer().comp
        if type( comp ) is Input:
            self.comp.scanInput = index.internalPointer().comp
            self.updateTree()
            return

    def newScanUnit( self, unit ):
        self.comp.scanUnit = unit
        self.updateTree()
