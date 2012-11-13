'''
Created on Mar 15, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui, QtCore

from ..dialogs import input, parameter, abstractfunction, scan, sequence, repeat, execute

from ..menubar import menubar
from ..models.unit import MainUnitModel
from ..views import MainUnitTree, TreeWidget
from ..widgets.unit import UnitButtonRow
from ..widgets.globals import GlobalsWidget
from ...components import Input, Global, Map, Parameter, Action, isUnit, Scan, Sequence, Repeat
from ...lr import Client
from ...util import saveUnit

import labrad
import os

class MainDialog( QtGui.QDialog ):
    def __init__( self, parent = None ):
        super( MainDialog, self ).__init__( parent )
        self.setLayout( QtGui.QVBoxLayout() )
        self.layout().addWidget( MainWidget( self ) )

class MainWindow( QtGui.QMainWindow ):
    def __init__( self, parent = None ):
        super( MainWindow, self ).__init__( parent )
        self.setMenuBar( menubar )
        self.setCentralWidget( MainWidget( self ) )

class MainWidget( QtGui.QWidget ):
    """
    Browse through the current experiment tree. 
    Double click (or press enter) on an item to view/edit its properties.
    Details of the current component or displayed to the right.
    Execute or save any properly configured unit in the tree.
    
    Right click on a tree item and choose from available operations.
    
    Load a new root unit, or create a new root unit.
    """
    dialogDict = {Input:input.InputDialog,
                  Global:input.InputDialog,
                  Action.Result:input.ResultDialog,
                  Map:abstractfunction.MapDialog,
                  Parameter:parameter.ParameterDialog,
                  Action:abstractfunction.ActionDialog,
                  Scan:scan.ScanDialog,
                  Sequence:sequence.SequenceDialog,
                  Repeat:repeat.RepeatDialog}

    def __init__( self, parent = None ):
        super( MainWidget, self ).__init__( parent )
        self.initGui()
        self.getLRConnection()

    def keyPressEvent( self, keyEvent ):
        key = keyEvent.key()
        if key == QtCore.Qt.Key_Enter or key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Escape:
            keyEvent.accept()
        else: super( MainWidget, self ).keyPressEvent( keyEvent )

    def getLRConnection( self ):
        Client.connection = labrad.connect()

    def initGui( self ):
        vlayout = QtGui.QVBoxLayout( self )

        titleRow = QtGui.QWidget( self )
        titleRow.setLayout( QtGui.QHBoxLayout() )
        titleRow.layout().addWidget( QtGui.QLabel( '<big><b>LabRAD Experimenter</b></big>', self ) )
        showGlobs = QtGui.QCheckBox( 'Globals', self )
        showTree = QtGui.QCheckBox( 'Tree', self )
        showDetails = QtGui.QCheckBox( 'Details', self )
        titleRow.layout().addStretch()
        titleRow.layout().addWidget( showGlobs )
        titleRow.layout().addWidget( showTree )
        titleRow.layout().addWidget( showDetails )
        vlayout.addWidget( titleRow )

        globalsWidget = self.globalsWidget = GlobalsWidget( self )
        globalsWidget.setSizePolicy( QtGui.QSizePolicy( QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Maximum ) )
        globalsWidget.setMaximumSize( 500, 200 )
        vlayout.addWidget( globalsWidget )
        showGlobs.toggled.connect( lambda state: globalsWidget.setHidden( not state ) )
        showGlobs.setChecked( True )
        globalsWidget.setHidden( False )

        mainDisplay = QtGui.QHBoxLayout( QtGui.QFrame( self ) )

        tree = self.tree = MainUnitTree( self )
        tree.activated.connect( self.editItem )
        tree.pressed.connect( self.mouseEvent )
        treeWidget = TreeWidget( tree, self )
        mainDisplay.addWidget( treeWidget, 5 )
        showTree.setChecked( True )
        showTree.setHidden( False )

        globalsWidget.editRequested.connect( lambda glob: self.editItem( self.tree.model().findMatches( glob )[0] ) if glob else None )

        details = self.details = QtGui.QLabel( self )
        details.setTextFormat( QtCore.Qt.RichText )
        details.setWordWrap( True )
        details.setAlignment( QtCore.Qt.AlignTop )
        mainDisplay.addWidget( details, 2 )
        showDetails.toggled.connect( lambda state: details.setHidden( not state ) )
        showDetails.setChecked( True )
        details.setHidden( False )

        vlayout.addWidget( mainDisplay.parent(), 4 )

        def hideTree( bool ):
            mainDisplay.parent().setHidden( not bool )
            showDetails.setEnabled( bool )

        showTree.toggled.connect( hideTree )

        unitButtons = UnitButtonRow( self )
        unitButtons.unitCreated.connect( self.newRoot )
        buttons = execute, save = [ QtGui.QPushButton( name, self ) for name in ( 'Execute Root', 'Save Root' ) ]
        for button, slot in zip( buttons, ( self.executeUnit, self.saveUnit ) ):
            button.clicked.connect( slot )
            button.setAutoDefault( False )
            button.setEnabled( False )
            unitButtons.layout().addWidget( button, 0, QtCore.Qt.AlignTop )
        unitButtons.layout().addStretch()
        self.execute = execute
        self.save = save

        vlayout.addWidget( unitButtons )

    def mouseEvent( self, index ):
        if QtGui.QApplication.mouseButtons() == QtCore.Qt.RightButton:
            menu = QtGui.QMenu( self )
            if self.dialogDict.get( index.internalPointer().comp.__class__ ) is None: return
            menu.addAction( 'Edit' )
            comp = index.internalPointer().comp
            if isUnit( comp ):
                menu.addAction( 'Save' )
                if comp.configured:
                    menu.addAction( 'Execute' )
            action = menu.exec_( QtGui.QCursor.pos() )
            if action:
                { 'Edit':self.editItem, 'Save':self.saveUnit, 'Execute':self.executeUnit }[str( action.text() )]( index )

    def editItem( self, index ):
        if not index.isValid(): return
        model = index.model()
        editDialog = self.dialogDict.get( index.internalPointer().comp.__class__ )
        if editDialog is None: return
        editDialog = editDialog( index, self )
        editDialog.setMinimumWidth( 500 )
        editDialog.exec_()
        matches = model.findMatches( index.internalPointer().comp )
        matches.remove( index )
        for matchIndex in matches:
            matchIndex.internalPointer().getData()
            model.dataChanged.emit( matchIndex, matchIndex )
        index.internalPointer().getData()
        model.dataChanged.emit( index, index )
        self.updateGlobals()

    def newSelection( self, selected, deselected ):
        details = getDetails( selected.indexes()[0].internalPointer().comp )
        self.details.setText( details.replace( '\n', '<br>' ) )

    def dataChanged( self, indexL, indexR ):
        index = indexL if indexL.isValid() else self.tree.model().index( 0, 0, indexL )

        self.execute.setEnabled( self.tree.model().root.comp.configured )

        if index is self.tree.currentIndex():
            details = getDetails( index.internalPointer().comp )
            self.details.setText( details.replace( '\n', '<br>' ) )

    def executeUnit( self, index ):
        def finishExecution( result ):
            self.setEnabled( True )
            unit.initialize()
            index.internalPointer().getData()
            self.tree.model().dataChanged.emit( index, index )
        if not type( index ) is QtCore.QModelIndex: index = self.tree.model().index( 0, 0, QtCore.QModelIndex() )
        unit = index.internalPointer().comp
        execDialog = execute.ExecDialog( unit, self )
        self.setEnabled( False )
        execDialog.setEnabled( True )
        execDialog.show()
        execDialog.finished.connect( finishExecution )

    def saveUnit( self, index ):
        if not type( index ) is QtCore.QModelIndex: index = self.tree.model().index( 0, 0, QtCore.QModelIndex() )
        root = os.environ['LREXPHOME']
        filename = QtGui.QFileDialog.getSaveFileName( self, 'Save Unit', os.path.join( root, 'experiments' ), 'labRAD experiments (*.lre)' )
        if filename == '': return
        result = QtGui.QMessageBox( self )
        try:
            saveUnit( index.internalPointer().comp, filename[:-4] )
            result.setText( 'Successful!' )
        except:
            raise
            result.setText( 'Failed!' )
        result.exec_()

    def newRoot( self, unit ):
        if QtGui.QMessageBox.warning( self,
                                      'New Root Requested',
                                      'Overwriting root unit.  Ok?',
                                      QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel ) == QtGui.QMessageBox.Cancel: return
        self.tree.setModel( MainUnitModel( unit, self ) )
        self.tree.model().dataChanged.connect( self.dataChanged )
        self.tree.selectionModel().selectionChanged.connect( self.newSelection )

        self.execute.setEnabled( self.tree.model().root.comp.configured )
        self.save.setEnabled( True )
        self.updateGlobals()

    def updateGlobals( self ):
        globalsList = []
        root = self.tree.model().root
        def findGlobals( parent, globs ):
            if parent.children:
                for child in parent.children:
                    findGlobals( child, globs )
                return
            comp = parent.comp
            if isinstance( comp, Global ) and comp not in globs:
                globs.append( comp )
        findGlobals( root, globalsList )
        self.globalsWidget.setList( globalsList )


def getDetails( comp ):
    """
    Get details for a tree item
    """
    text = ''
    def appendLine( toAppend = '' ):
        return toAppend + '<br>'
    def indent( toIndent, space = 10 ):
        return '<DIV style="margin-left:%d;">' % space + toIndent + '</DIV>'
    def fmtPar( p ):
        def fmtVal( val ):
            return str( val.toString() ) if isinstance( val, QtCore.QVariant ) else val
        t = ''
        t += appendLine( repr( p.name ) )
        try:
            value = repr( p.input.value )
        except: value = 'Not configured'
        t += appendLine( indent( 'description: %s<br>value: %s' ) % ( p.description,
                                                                      fmtVal( value ) ) )
        t += appendLine()
        return t
    compType = type( comp )
    if issubclass( compType, Input ):
        text += appendLine( '<b><big>%s</big></b>' % ( 'Result' if compType is Action.Result else 'Input' ) )
        text += appendLine( '<b>ID:</b> #%d' % comp.id )
        text += appendLine( '<b>Description:</b>' )
        text += indent( appendLine( comp.description ) )
        try:
            value = repr( comp.value )
        except: value = 'Not configured'
        text += appendLine( '<b>Value:</b> %s' % repr( value ) )
    if compType is Parameter:
        text += appendLine( '<b><big>Parameter</big></b>' )
        text += appendLine()
        text += fmtPar( comp )
        return text
    if compType is Action:
        text += appendLine( '<b><big>Action</big></b>' )
        text += appendLine( '<b>Name:</b> %s' % comp.name )
        text += appendLine()
        text += appendLine( '<b>Function:</b>' )
        text += appendLine( comp.function.__name__ if comp.function else 'No function assigned' )
        doc = comp.function.__doc__ if comp.function and comp.function.__doc__ else ''
        text += indent( appendLine( doc ) )
        text += appendLine( '<b>Parameters:</b>' )
        text += appendLine()
        parameters = comp.parameters.values()
        if not parameters:
            text += appendLine( 'No parameters' )
            return text
        for parameter in parameters:
            text += appendLine( parameter.name if type( parameter.name ) is str else str( parameter.name ) )
        return text
    if compType is Scan:
        text += appendLine( '<b><big>Scan</big></b>' )
        text += appendLine( '<b>Name:</b> %s' % comp.name )
        text += appendLine()
        text += appendLine( '<b>Scan Unit:</b> %s' % repr( comp.scanUnit ) )
        text += appendLine()
        text += appendLine( '<b>Scan Range:</b>' )
        try:
            text += appendLine( '%f to %f in %d steps' % ( comp.min.input.value, comp.max.input.value, comp.steps.input.value ) )
        except:
            text += appendLine( 'Not configured' )
        return text
    if compType is Sequence:
        text += appendLine( '<b><big>Sequence</big></b>' )
        text += appendLine( '<b>Name:</b> %s' % comp.name )
        text += appendLine()
        text += appendLine( '<b>Units:</b>' )
        text += appendLine()
        for unit in comp.sequence: text += appendLine( repr( unit ) )
        return text
    if compType is Repeat:
        text += appendLine( '<b><big>Repeat</big></b>' )
        text += appendLine( '<b>Name:</b> %s' % comp.name )
        text += appendLine()
        text += appendLine( '<b>Repeat Unit</b>: %s' % repr( comp.repeatUnit ) )
        text += fmtPar( comp.repeats )
        return text
    return text
