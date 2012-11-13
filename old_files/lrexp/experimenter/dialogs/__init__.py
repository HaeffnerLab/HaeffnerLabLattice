from PyQt4 import QtGui, QtCore

class CompEditDialog( QtGui.QDialog ):
    """
    Base class of comp-editing dialogs.
    Assigns the comp and model index as a member and handles ok/cancel key events.
    """
    def __init__( self, index, parent = None ):
        super( CompEditDialog, self ).__init__( parent )
        self.index = index
        self.comp = index.internalPointer().comp
        self.createGui()

    def keyPressEvent( self, keyEvent ):
        super( CompEditDialog, self ).keyPressEvent( keyEvent )
        if keyEvent.key() == QtCore.Qt.Key_Enter or keyEvent.key() == QtCore.Qt.Key_Return or keyEvent.key() == QtCore.Qt.Key_Escape:
            self.done( 1 )
            keyEvent.accept()
