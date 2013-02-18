from PyQt4 import QtCore, QtGui
from Data import CollectionNode

class ParametersTreeModel(QtCore.QAbstractItemModel):
    
    filterRole  = QtCore.Qt.UserRole
    
    def __init__(self, root, parent=None):
        super(ParametersTreeModel, self).__init__(parent)
        self._rootNode = root
        
    def rowCount(self, parent):
        '''
        returns the count
        '''
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()
        return parentNode.childCount()

    def columnCount(self, parent):
        return 2
        
    def data(self, index, role):
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return node.data(index.column())
        
        if role == ParametersTreeModel.filterRole:
            return node.filter_text()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():
            node = index.internalPointer()
            if role == QtCore.Qt.EditRole:
                node.setData(index.column(), value)
                self.dataChanged.emit(index, index)
                return True
        return False

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return "Collection"
            else:
                return "Value"

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def parent(self, index):      
        '''
        returns the index of the parent of the node at the given index
        '''
        node = self.getNode(index)
        parentNode = node.parent()
        if parentNode == self._rootNode:
            return QtCore.QModelIndex()
        return self.createIndex(parentNode.row(), 0, parentNode)
        
    def index(self, row, column, parent): 
        '''
        returns the index for the given parent, row and column
        '''
        parentNode = self.getNode(parent)
        childItem = parentNode.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def getNode(self, index):
        '''
        returns node of the given index
        '''
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node            
        return self._rootNode

'''
commenting out insertion, removal. not needed at this point.
'''
#    """INPUTS: int, int, QModelIndex"""
#    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
#        parentNode = self.getNode(parent)
#        self.beginInsertRows(parent, position, position + rows - 1)
#        for row in range(rows):
#            
#            childCount = parentNode.childCount()
#            childNode = Node("untitled" + str(childCount))
#            success = parentNode.insertChild(position, childNode)
#        
#        self.endInsertRows()
#
#        return success
#    
#    def insertLights(self, position, rows, parent=QtCore.QModelIndex()):
#        
#        parentNode = self.getNode(parent)
#        
#        self.beginInsertRows(parent, position, position + rows - 1)
#        
#        for row in range(rows):
#            
#            childCount = parentNode.childCount()
#            childNode = LightNode("light" + str(childCount))
#            success = parentNode.insertChild(position, childNode)
#        
#        self.endInsertRows()
#
#        return success
#
#    """INPUTS: int, int, QModelIndex"""
#    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
#        
#        parentNode = self.getNode(parent)
#        self.beginRemoveRows(parent, position, position + rows - 1)
#        
#        for row in range(rows):
#            success = parentNode.removeChild(position)
#            
#        self.endRemoveRows()
#        return success