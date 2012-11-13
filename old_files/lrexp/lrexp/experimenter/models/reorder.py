'''
Created on Mar 16, 2011

@author: christopherreilly
'''
from PyQt4 import QtCore
class ReorderListModel( QtCore.QAbstractListModel ):
    """
    Backend to list views that support reordering
    """
    def __init__( self, sequence, parent ):
        super( ReorderListModel, self ).__init__( parent )
        self.sequence = sequence
    def rowCount( self, index ):
        return len( self.sequence )
    def data( self, index, role ):
        if role == QtCore.Qt.DisplayRole:
            return '%d: %s' % ( index.row() + 1, repr( self.sequence[index.row()] ) )
        return QtCore.QVariant()
    def flags( self, index ):
        flags = QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        if index.isValid():
            return flags
        return flags | QtCore.Qt.ItemIsDropEnabled
    def mimeTypes( self ):
        return ['text/plain']
    def mimeData( self, indexes ):
        index = indexes[0]
        mimeData = QtCore.QMimeData()
        mimeData.setData( 'text/plain', str( index.row() ) )
        return mimeData
    def dropMimeData( self, data, action, row, column, parent ):
        if action == QtCore.Qt.IgnoreAction: return True
        if not data.hasFormat( 'text/plain' ): return False
        if column is not 0: return False
        fromRow = int( data.data( 'text/plain' ) )
        toRow = row
        if fromRow < toRow and not toRow < 0: toRow -= 1
        self.sequence.insert( toRow, self.sequence.pop( fromRow ) )
        self.dataChanged.emit( parent, parent )
        return True
