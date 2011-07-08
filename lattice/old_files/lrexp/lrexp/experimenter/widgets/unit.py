'''
Created on Mar 15, 2011

@author: christopherreilly
'''
import os

from PyQt4 import QtCore, QtGui
from ...components import Unit, Action, Scan, Sequence, Repeat
from ...util import loadUnit
from ..menubar import recentFiles

class RecentFile( QtGui.QAction ):
    def __init__( self, filename, parent ):
        super( RecentFile, self ).__init__( filename.split( '/' )[-1][:-4], parent )
        self.triggered.connect( lambda: parent.newUnit.emit( loadUnit( filename[:-4] ) ) )

class UnitButtonRow( QtGui.QWidget ):
    """
    A widget that allows creation of new Units and loading of saved Units
    """
    unitCreated = QtCore.pyqtSignal( Unit )
    def __init__( self, parent ):
        super( UnitButtonRow, self ).__init__( parent )
        hl = QtGui.QHBoxLayout( self )

        new = NewUnitSelector( self )
        load = UnitLoader( self )

        for button in ( new, load ):
            button.newUnit.connect( self.unitCreated.emit )
            hl.addWidget( button, 0, QtCore.Qt.AlignTop )

        hl.addStretch()

class NewUnitSelector( QtGui.QWidget ):
    """
    A QButton/QComboBox combination that emits a signal containing a new instance of a lrexp unit when clicked.
    """
    newUnit = QtCore.pyqtSignal( Unit )
    def __init__( self, parent ):
        super( NewUnitSelector, self ).__init__( parent )
        self.createGui()

    def createGui( self ):
        vl = QtGui.QVBoxLayout( self )

        new = QtGui.QPushButton( 'New Unit', self )
        new.setSizePolicy( QtGui.QSizePolicy() )
        new.clicked.connect( self.clicked )
        new.setAutoDefault( False )
        vl.addWidget( new, 0, QtCore.Qt.AlignTop )

        types = QtGui.QComboBox( self )
        for unit in ( 'Action', 'Scan', 'Sequence', 'Repeat' ):
            types.insertItem( 4, unit )
        types.setSizePolicy( QtGui.QSizePolicy() )
        vl.addWidget( types )
        self.types = types
        self.layout().setContentsMargins( 12, 0, 12, 12 )

    def clicked( self ):
        unitName = str( self.types.currentText() )
        name, result = QtGui.QInputDialog.getText( self, 'Give new unit a name', 'Enter name', mode = QtGui.QLineEdit.Normal, text = '' )
        if result:
            name = str( name )
            name = None if name == '' else name
            self.newUnit.emit( { 'Action':Action, 'Scan':Scan, 'Sequence':Sequence, 'Repeat':Repeat }[unitName]( name ) )

class UnitLoader( QtGui.QPushButton ):
    """
    Loads an experiment (*.lre) file from a hardcoded directory (TODO: fix filesystem set up for saving/loading units).
    Returns the loaded unit.
    """
    newUnit = NewUnitSelector.newUnit
    def __init__( self, parent ):
        super( UnitLoader, self ).__init__( 'Load Unit', parent )
        self.clicked.connect( self.getUnit )
        self.setAutoDefault( False )
    def getUnit( self ):
        root = os.environ['LREXPHOME']
        filename = QtGui.QFileDialog.getOpenFileName( self, 'Load Unit', os.path.join( root, 'experiments' ), 'labRAD experiments (*.lre)' )
        recentFiles.addAction( RecentFile( filename, recentFiles ) )
        if filename != '':
            unit = loadUnit( filename[:-4] )
            self.newUnit.emit( unit )
        return
