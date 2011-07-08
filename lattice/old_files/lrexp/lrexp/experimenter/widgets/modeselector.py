'''
Created on Mar 15, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui, QtCore
from ...components import Unit

class ModeSelector( QtGui.QFrame ):
    """
    Base widget that handles selection of modes.
    """
    modeSelected = QtCore.pyqtSignal( int )
    def __init__( self, parent, name = None ):
        super( ModeSelector, self ).__init__( parent )

        self.setFrameStyle( QtGui.QFrame.Plain | QtGui.QFrame.Box )

        QtGui.QHBoxLayout( self )

        if name: self.layout().addWidget( QtGui.QLabel( name + ':', self ) )

        bg = QtGui.QButtonGroup( self )
        bg.buttonClicked[int].connect( self.radioChecked )
        self.bg = bg

    def addMode( self, name, mode ):
        bg, hl = ( self.bg, self.layout() )
        radio = QtGui.QRadioButton( name )
        bg.addButton( radio )
        bg.setId( radio, mode )
        hl.addWidget( radio )

    def radioChecked( self, mode ):
        self.modeSelected.emit( mode )

    def setMode( self, mode ):
        self.bg.button( mode ).click()

class ExecModeSelector( ModeSelector ):
    """
    Mode Selector applied to the case of execution modes
    """
    def __init__( self, parent ):
        super( ExecModeSelector, self ).__init__( parent, 'Execution Mode' )

        for name, mode in zip( ( 'Probe', 'Step', 'All' ), ( Unit.PROBE, Unit.STEP, Unit.ALL ) ):
            self.addMode( name, mode )

    def radioChecked( self, mode ):
        self.parent().comp.mode = mode
        self.modeSelected.emit( mode )
