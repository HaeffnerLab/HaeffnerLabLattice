from PyQt4 import QtCore, QtGui, uic
import sys

from Data import Node, ParameterNode, CollectionNode, ScanNode
from Models import ParametersTreeModel
from PropertiesEditor import PropertiesEditor
    
base, form = uic.loadUiType("Views/ParametersEditor.ui")

class ParametersEditor(base, form):
    def __init__(self, parent=None):
        super(base, self).__init__(parent)
        self.setupUi(self)
        self.setup_sample_nodes()
        self.setup_model()
        self.connect_layout()
    
    def setup_sample_nodes(self):
        self._rootNode   = Node("Root")
        collectionDoppler = CollectionNode("Doppler Cooling", self._rootNode)
        childNode0 = ParameterNode("frequency", collectionDoppler)
        childNode1 = ParameterNode("amplitude", collectionDoppler)
        sidebandCooling = CollectionNode("Sideband Cooling", self._rootNode)
        childNode2 = ParameterNode("frequency", sidebandCooling)
        childNode3 = ParameterNode("amplitude", sidebandCooling)
        spectrum = CollectionNode("Spectrum", self._rootNode)
        childNode4 = ScanNode("frequency scan", spectrum)
    
    def setup_model(self): 
        self.uiTree.setSortingEnabled(False)
        self._proxyModel = QtGui.QSortFilterProxyModel(self)
        self._model = ParametersTreeModel(self._rootNode, self)
        self._proxyModel.setSourceModel(self._model)
        self._proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._proxyModel.setFilterRole(ParametersTreeModel.filterRole)
        self._proxyModel.setFilterKeyColumn(-1) #look at all columns while filtering
        self.uiTree.setModel(self._proxyModel)
        
        self._propEditor = PropertiesEditor(self)
        self.layoutMain.addWidget(self._propEditor)
        self._propEditor.setModel(self._proxyModel)
    
    def connect_layout(self):
        self.uiFilter.textChanged.connect(self._proxyModel.setFilterRegExp)
        self.uiTree.selectionModel().currentChanged.connect(self._propEditor.setSelection)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    wnd = ParametersEditor()
    wnd.show()
    sys.exit(app.exec_())