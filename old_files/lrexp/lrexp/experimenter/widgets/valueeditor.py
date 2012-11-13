'''
Created on Mar 15, 2011

@author: christopherreilly
'''
from PyQt4 import QtCore, QtGui
class ValueEditor( QtGui.QGroupBox ):
    """
    A Widget that shows a value and allows editing of the value
    """
    dataChanged = QtCore.pyqtSignal( str, str )
    def __init__( self, title, initValue, parent ):
        super( ValueEditor, self ).__init__( title, parent )
        self.initValue = initValue
        vl = QtGui.QVBoxLayout( self )

        titleLabel = self.titleLabel = QtGui.QLabel( self )
        vl.addWidget( titleLabel )

        hl = QtGui.QHBoxLayout( QtGui.QFrame( self ) )

        self.oldData = QtGui.QLabel( self.initValue, self )
        self.oldData.setWordWrap( True )
        hl.addWidget( self.oldData, 1 )
        edit = QtGui.QPushButton( 'Edit', self )
        edit.clicked.connect( self.clicked )
        hl.addWidget( edit )

        vl.addWidget( hl.parent() )

    def clicked( self ):
        data, result = QtGui.QInputDialog.getText( self, 'Enter new value', 'New value', mode = QtGui.QLineEdit.Normal, text = self.oldData.text() )
        data = str( data )
        if result:
            self.oldData.setText( data )
            self.dataChanged.emit( data, self.title() )

    def getText( self ):
        return self.oldData.text()
    def setText( self, text ):
        self.oldData.setText( text )

    text = property( getText, setText )


class NameEditor( ValueEditor ):
    nameChanged = QtCore.pyqtSignal( str )
    def __init__( self, parent ):
        super( NameEditor, self ).__init__( 'Name', parent.comp.name, parent )
        self.dataChanged.connect( lambda data, source: self.changeName( data ) )
    def changeName( self, data ):
        self.parent().comp.name = str( data )
        self.nameChanged.emit( data )
