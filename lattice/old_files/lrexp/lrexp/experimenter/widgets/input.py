'''
Created on Mar 16, 2011

@author: christopherreilly
'''
from PyQt4 import QtCore, QtGui

from ..dialogs.input import OldInputDialog

from ...components import Input, Map, Global

class InputButtonRow( QtGui.QWidget ):
    """
    A widget that allows creation of new Inputs and Maps, as well as linking to existing inputs
    """
    inputCreated = QtCore.pyqtSignal( Input )
    def __init__( self, parent, root, input = None ):
        self.root = root
        self.input = input
        super( InputButtonRow, self ).__init__( parent )
        QtGui.QHBoxLayout( self )
        for name, slot in zip( ( 'New Input', 'Old Input', 'New Map', 'New Global' ), ( self.new, self.old, self.newMap, self.newGlobal ) ):
            button = QtGui.QPushButton( name, self )
            button.clicked.connect( slot )
            self.layout().addWidget( button )
        self.layout().addStretch()

    def new( self ):
        self.inputCreated.emit( Input( None ) )

    def old( self ):
        old = OldInputDialog( self.input, self.root, self )
        if old.exec_(): self.inputCreated.emit( old.input )

    def newMap( self ):
        self.inputCreated.emit( Map( None ) )

    def newGlobal( self ):
        name, result = QtGui.QInputDialog.getText( self, 'New global input', 'Name the new global input', mode = QtGui.QLineEdit.Normal, text = '' )
        if result:
            self.inputCreated.emit( Global( name, None ) )

