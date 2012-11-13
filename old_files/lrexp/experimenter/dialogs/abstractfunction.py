'''
Created on Mar 15, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui, QtCore

from . import CompEditDialog
from .input import OldInputDialog
from .function import NewFunctionDialog, NewLRSettingDialog
from ..models.reorder import ReorderListModel
from ..models.unit import ReadOnlyInputModel
from ..views import ReorderListView, InputTree, TreeWidget
from ..widgets.input import InputButtonRow
from ..widgets.modeselector import ModeSelector
from ..widgets.valueeditor import NameEditor
from ...components import Action, Input
from ...functions import standard
from ..widgets.valueeditor import ValueEditor

try:
    from ...functions import custom
    useCustom = True
except ImportError:
    useCustom = False

class AbstractFunctionDialog( CompEditDialog ):
    """
    Base class for dialogs whose component inherits from the lrexp.components.Function base class.
    Handles configuration of the component's function, arguments, and list arguments
    """
    class ArgListTab( QtGui.QWidget ):
        """
        Handles configuration of the function's list argument (if the function has one)
        """
        MONO = 111
        POLY = 222

        def __init__( self, parent ):
            super( ActionDialog.ArgListTab, self ).__init__( parent )

            self.comp = parent.comp
            vl = QtGui.QVBoxLayout( self )

            listMode = ModeSelector( self, 'Mode' )
            MONO, POLY = ( self.MONO, self.POLY )
            for name, mode in ( ( 'Mono', MONO ), ( 'Poly', POLY ) ): listMode.addMode( name, mode )

            listMode.modeSelected.connect( self.modeSelected )

            vl.addWidget( listMode )

            argListView = ReorderListView( [], ReorderListModel, self )
            vl.addWidget( argListView )
            self.argListView = argListView

            self.parent().tabs.currentChanged.connect( lambda x: self.argListView.setModel( self.comp.argList if type( self.comp.argList ) is list else [self.comp.argList] ) if x is 1 else None )

            inputButtons = InputButtonRow( self, self.parent().index.model().root.comp )
            inputButtons.inputCreated.connect( self.addInput )

            remove = self.removeButton = QtGui.QPushButton( 'Remove Input', self )
            remove.clicked.connect( self.remove )

            inputButtons.layout().addWidget( remove )

            vl.addWidget( inputButtons )

            if type( self.comp.argList ) is Input:
                listMode.setMode( MONO )
            else:
                listMode.setMode( POLY )

        def modeSelected( self, mode ):
            self.mode = mode
            if mode is self.MONO:
                self.removeButton.setEnabled( False )
                self.argListView.setEnabled( False )
                argList = self.comp.argList
                self.comp.argList = Input( [] ) if type( argList ) is list else argList
                self.argListView.setModel( [self.comp.argList] )
            if mode is self.POLY:
                self.removeButton.setEnabled( True )
                self.argListView.setEnabled( True )
                argList = self.comp.argList
                self.comp.argList = argList if type( argList ) is list else []
                self.argListView.setModel( self.comp.argList )

        def addInput( self, input ):
            if self.mode is ActionDialog.ArgListTab.MONO:
                self.comp.argList = input
                self.argListView.setModel( [self.comp.argList] )
                return
            self.comp.argList.append( input )
            self.argListView.setModel( self.comp.argList )

        def remove( self ):
            self.comp.argList.pop( self.argListView.currentIndex().row() )
            self.argListView.setModel( self.comp.argList )

    class FunctionTab( QtGui.QWidget ):
        """
        Handles assignment of a new function to the Function subclass.
        Can choose from functions in the lrexp.functions.standard and lrexp.functions.custom modules, as well as any LabRAD setting.
        """
        newFunctionSet = QtCore.pyqtSignal()
        def __init__( self, parent ):
            super( ActionDialog.FunctionTab, self ).__init__( parent )
            self.comp = parent.comp
            layout = QtGui.QVBoxLayout( self )

            #=======================================================================
            # Info Widget
            #=======================================================================
            info = QtGui.QLabel( self )
            info.setTextFormat( QtCore.Qt.RichText )
            info.setFrameStyle( QtGui.QFrame.Plain | QtGui.QFrame.Box )
            info.setWordWrap( True )
            info.setText( self.getFunctionInfo( self.comp.function ) )
            layout.addWidget( info )
            self.info = info

            #=======================================================================
            # New Function Buttons
            #=======================================================================
            hlButtons = QtGui.QHBoxLayout( QtGui.QFrame( self ) )

            func = QtGui.QPushButton( 'New Function', self )
            func.clicked.connect( self.newFunction )

            custfunc = QtGui.QPushButton( 'New Custom Function', self )
            custfunc.clicked.connect( self.newCustomFunction )
            custfunc.setEnabled( useCustom )

            lrSetting = QtGui.QPushButton( 'New labRAD setting', self )
            lrSetting.clicked.connect( self.newLRSetting )

            for button in ( func, custfunc, lrSetting ):
                button.setSizePolicy( QtGui.QSizePolicy() )
                hlButtons.addWidget( button )

            hlButtons.addStretch()

            layout.addWidget( hlButtons.parent() )

        def newFunction( self ):
            nfDial = NewFunctionDialog( self, standard, 'New Function' )
            if nfDial.exec_():
                self.setNewFunction( nfDial.tree.currentIndex().internalPointer().item )

        def newCustomFunction( self ):
            ncfDial = NewFunctionDialog( self, custom, 'New Custom Function' )
            if ncfDial.exec_():
                self.setNewFunction( ncfDial.tree.currentIndex().internalPointer().item )

        def newLRSetting( self ):
            newLRSetting = NewLRSettingDialog( self )
            if newLRSetting.exec_():
                self.setNewFunction( newLRSetting.lrSetting )

        def setNewFunction( self, function ):
            self.comp.function = function
            self.info.setText( self.getFunctionInfo( self.comp.function ) )
            self.newFunctionSet.emit()

        @staticmethod
        def getFunctionInfo( function ):
            text = ''
            if function:
                text += '<big><b>%s</b></big><br>' % function.__name__
                text += '<b>Doc:</b><br><i>%s</i><br>' % function.__doc__
            else: text += '<big><i>No function assigned</i></big><br>'
            return text.replace( '\n', '<br>' )

    def addTabWidget( self ):
        tabs = self.tabs = QtGui.QTabWidget( self )

        functionTab = self.FunctionTab( self )
        functionTab.newFunctionSet.connect( self.newFunctionSet )
        tabs.addTab( functionTab, 'Function' )
        tabs.addTab( self.ArgListTab( self ), 'Argument List' )
        tabs.setTabEnabled( 1, self.comp.argListEnabled )

        self.layout().addWidget( tabs, 1 )

    def newFunctionSet( self ):
        self.tabs.setTabEnabled( 1, self.comp.argListEnabled )

class ActionDialog( AbstractFunctionDialog ):
    """
    Dialog for Actions.
    Adds a name edit box.
    """
    def createGui( self ):
        vl = QtGui.QVBoxLayout( self )
        vl.addWidget( QtGui.QLabel( '<big><b>Edit Action</b></big>' ) )

        vl.addWidget( NameEditor( self ) )
        self.addTabWidget()

class MapDialog( AbstractFunctionDialog ):
    """
    Dialog for Maps.
    Adds a description editor and a tab for browsing its global tree position.
    """
    def createGui( self ):
        vl = QtGui.QVBoxLayout( self )
        vl.addWidget( QtGui.QLabel( '<big><b>Edit Map</b></big>' ), 0 )

        desc = ValueEditor( 'Description', self.comp.description, self )
        desc.dataChanged.connect( self.setDescription )
        vl.addWidget( desc, 0 )

        self.addTabWidget()

        tree = InputTree( self )
        tree.setModel( ReadOnlyInputModel( self.comp, self.index.model().root.comp, self ) )
        tree.expandTo( self.comp )

        self.tabs.addTab( TreeWidget( tree, self ), 'Tree View' )

    def setDescription( self, description ):
        self.comp.description = description

