'''
Created on Mar 15, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui, QtCore

from ..models.unit import ExecModel
from ..views import BaseTree
from ...components import Action, Scan, Sequence, Repeat, forceUnit
from ...util import LRExpSignal

class ExecDialog( QtGui.QDialog ):
    """
    Dialog which performs execution of a unit.
    Step through each increment of the experiment or run continuously with pausing capability.
    The step sizes are determined by the execution mode (PROBE, STEP, or ALL).
    Dialog exits and initializes the unit when the unit completes execution.
    """
    running = None
    def __init__( self, unit, parent ):
        super( ExecDialog, self ).__init__( parent )
        forceUnit( unit )
        self.unit = unit
        self.createGui()

    def createGui( self ):
        vl = QtGui.QVBoxLayout( self )
        tree = BaseTree( self )
        tree.setModel( ExecModel( self.unit, self ) )
        tree.expandAll()
        vl.addWidget( tree )
        self.tree = tree

        hlButtons = QtGui.QHBoxLayout( QtGui.QFrame( self ) )

        nextButton = QtGui.QPushButton( 'Next Step', self )
        nextButton.clicked.connect( self.nextStep )
        hlButtons.addWidget( nextButton )
        self.next = nextButton

        runButton = QtGui.QPushButton( 'Run', self )
        runButton.clicked.connect( self.startRun )
        hlButtons.addWidget( runButton )
        self.startRun = runButton

        pauseButton = QtGui.QPushButton( 'Paused', self )
        pauseButton.clicked.connect( self.pauseRun )
        pauseButton.setEnabled( False )
        hlButtons.addWidget( pauseButton )
        self.pause = pauseButton

        hlButtons.addStretch()

        vl.addWidget( hlButtons.parent() )

    def startRun( self ):
        self.startRun.setEnabled( False )
        self.next.setEnabled( False )
        self.pause.setEnabled( True )
        self.startRun.setText( 'Running...' )
        self.run()

    def run( self ):
        self.nextStep()
        running = QtCore.QTimer( self )
        running.setSingleShot( True )
        running.timeout.connect( self.run )
        running.start( 1 )
        self.running = running

    def pauseRun( self ):
        self.running.stop()
        self.running = None
        self.startRun.setEnabled( True )
        self.startRun.setText( 'Run' )
        self.next.setEnabled( True )
        self.pause.setEnabled( False )
        self.pause.setText( 'Paused' )

    def nextStep( self ):
        try:
            chain = self.unit.next()
        except LRExpSignal, signal:
            chain = signal.chain
            if self.running:
                self.running.stop()
                self.running = None
            QtGui.QMessageBox.information( self, 'Experiment Complete.', 'Experiment done.' )
            self.done( 1 )
            return
        self.updateProgress( chain )

    def updateProgress( self, chain ):
        root = self.tree.model().index( 0, 0, QtCore.QModelIndex() )
        index = root
        compItem = index.internalPointer()
        while chain:
            compType, state = chain.pop()
            if compType in ( Sequence, Scan, Repeat ):
                if state is None:
                    if hasattr( compItem, 'progress' ): del compItem.progress
                    self.tree.model().dataChanged.emit( index, index )
                    continue
                comp = compItem.comp
                if compType is Scan:
                    total = comp.steps.input.value
                if compType is Sequence:
                    total = len( comp.sequence )
                if compType is Repeat:
                    total = comp.repeats.input.value
                compItem.progress = '%d of %d' % ( state + 1, total )
                self.tree.model().dataChanged.emit( index, index )
                index = index.child( state if compType is Sequence else 0, 0 )
                compItem = index.internalPointer()
            if compType is Action:
                compItem.progress = repr( state )
                self.tree.model().dataChanged.emit( index, index )
                break
        self.tree.setCurrentIndex( index )

    def done( self, result ):
        if self.running:
            print 'quitting and stopping timer'
            self.running.stop()
            self.running = None
        super( ExecDialog, self ).done( result )
