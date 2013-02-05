import sys
from PyQt4 import QtCore, QtGui

class myDelegate(QtGui.QItemDelegate):
    
    def createEditor(self, parent, option, index):
        spinbox = QtGui.QSpinBox(parent)
        return spinbox
        
class myModel(QtCore.QAbstractTableModel):
    
    def rowCount(self, index):
        return 2
    
    def columnCount(self, index):
        return 3
    
    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return QtCore.QString('{0}, {1}'.format(index.row(), index.column()))
        return QtCore.QVariant()
    
    def setData(self, index, value, role):
        print 'in set data', value.toString()
#        self.dataChanged.emit()
        return True
    
    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled

if __name__ == "__main__": 
    app = QtGui.QApplication(sys.argv) 
    tableview = QtGui.QTableView()
    model = myModel()
    tableview.setModel(model)
    delegate = myDelegate()
    tableview.setItemDelegate(delegate)
    tableview.show() 
    sys.exit(app.exec_()) 