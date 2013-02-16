from PyQt4 import QtCore, QtGui, QtXml, uic
import sys
import Resources

from Data import Node, TransformNode, CameraNode, LightNode, LIGHT_SHAPES
from Models import SceneGraphModel
    
    
base, form = uic.loadUiType("Views/Window.ui")

class WndTutorial06(base, form):
         
    def __init__(self, parent=None):
        super(base, self).__init__(parent)
        self.setupUi(self)

        self._rootNode   = Node("Root")
        childNode0 = TransformNode("A",    self._rootNode)
        childNode1 = LightNode("B",        self._rootNode)
        childNode2 = CameraNode("C",       self._rootNode)
        childNode3 = TransformNode("D",    self._rootNode)
        childNode4 = LightNode("E",        self._rootNode)
        childNode5 = CameraNode("F",       self._rootNode)
        childNode6 = TransformNode("G",    childNode5)
        childNode7 = LightNode("H",        childNode6)
        childNode8 = CameraNode("I",       childNode7)
       

        
        self._proxyModel = QtGui.QSortFilterProxyModel(self)
        
        """VIEW <------> PROXY MODEL <------> DATA MODEL"""

        self._model = SceneGraphModel(self._rootNode, self)
        

        self._proxyModel.setSourceModel(self._model)
        self._proxyModel.setDynamicSortFilter(True)
        self._proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        
        self._proxyModel.setSortRole(SceneGraphModel.sortRole)
        self._proxyModel.setFilterRole(SceneGraphModel.filterRole)
        self._proxyModel.setFilterKeyColumn(0)
        
        self.uiTree.setModel(self._proxyModel)
        

        QtCore.QObject.connect(self.uiFilter, QtCore.SIGNAL("textChanged(QString)"), self._proxyModel.setFilterRegExp)

        self._propEditor = PropertiesEditor(self)
        self.layoutMain.addWidget(self._propEditor)
        
        self._propEditor.setModel(self._proxyModel)
        
        

        
        QtCore.QObject.connect(self.uiTree.selectionModel(), QtCore.SIGNAL("currentChanged(QModelIndex, QModelIndex)"), self._propEditor.setSelection)


propBase, propForm = uic.loadUiType("Views/Editors.ui")
nodeBase, nodeForm = uic.loadUiType("Views/NodeEditor.ui") 
lightBase, lightForm = uic.loadUiType("Views/LightEditor.ui")
cameraBase, cameraForm = uic.loadUiType("Views/CameraEditor.ui")
transformBase, transformForm = uic.loadUiType("Views/TransformEditor.ui")



"""PROPERTIESEDITOR"""
class PropertiesEditor(propBase, propForm):
    
    def __init__(self, parent = None):
        super(propBase, self).__init__(parent)
        self.setupUi(self)

        self._proxyModel = None

        self._nodeEditor = NodeEditor(self)
        self._lightEditor = LightEditor(self)
        self._cameraEditor = CameraEditor(self)
        self._transformEditor = TransformEditor(self)

        
        self.layoutNode.addWidget(self._nodeEditor)
        self.layoutSpecs.addWidget(self._lightEditor)
        self.layoutSpecs.addWidget(self._cameraEditor)
        self.layoutSpecs.addWidget(self._transformEditor)

        self._lightEditor.setVisible(False)
        self._cameraEditor.setVisible(False)
        self._transformEditor.setVisible(False)
               
    """INPUTS: QModelIndex, QModelIndex"""
    def setSelection(self, current, old):

        current = self._proxyModel.mapToSource(current)

        node = current.internalPointer()
        
        if node is not None:
            
            typeInfo = node.typeInfo()
            
        if typeInfo == "CAMERA":
            self._cameraEditor.setVisible(True)
            self._lightEditor.setVisible(False)
            self._transformEditor.setVisible(False)
        
        elif typeInfo == "LIGHT":
            self._cameraEditor.setVisible(False)
            self._lightEditor.setVisible(True)
            self._transformEditor.setVisible(False)
             
        elif typeInfo == "TRANSFORM":
            self._cameraEditor.setVisible(False)
            self._lightEditor.setVisible(False)
            self._transformEditor.setVisible(True)
        else:
            self._cameraEditor.setVisible(False)
            self._lightEditor.setVisible(False)
            self._transformEditor.setVisible(False)

        self._nodeEditor.setSelection(current)
        self._cameraEditor.setSelection(current)
        self._lightEditor.setSelection(current)
        self._transformEditor.setSelection(current)
        

    def setModel(self, proxyModel):
        
        self._proxyModel = proxyModel
        
        self._nodeEditor.setModel(proxyModel)
        self._lightEditor.setModel(proxyModel)
        self._cameraEditor.setModel(proxyModel)
        self._transformEditor.setModel(proxyModel)


"""NODE"""
class NodeEditor(nodeBase, nodeForm):
    
    def __init__(self, parent=None):
        super(nodeBase, self).__init__(parent)
        self.setupUi(self)
        
        self._dataMapper = QtGui.QDataWidgetMapper()
        
    def setModel(self, proxyModel):
        self._proxyModel = proxyModel
        self._dataMapper.setModel(proxyModel.sourceModel())
        
        self._dataMapper.addMapping(self.uiName, 0)
        self._dataMapper.addMapping(self.uiType, 1)
        
    """INPUTS: QModelIndex"""
    def setSelection(self, current):
        
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)
        
        self._dataMapper.setCurrentModelIndex(current)
        


"""LIGHT"""
class LightEditor(lightBase, lightForm):
    
    def __init__(self, parent=None):
        super(lightBase, self).__init__(parent)
        self.setupUi(self)
        
        self._dataMapper = QtGui.QDataWidgetMapper()
   
        for i in LIGHT_SHAPES.names:
            if i != "End":
                self.uiShape.addItem(i)
   

    def setModel(self, proxyModel):
        self._proxyModel = proxyModel
        self._dataMapper.setModel(proxyModel.sourceModel())
        
        self._dataMapper.addMapping(self.uiLightIntensity, 2)
        self._dataMapper.addMapping(self.uiNear, 3)
        self._dataMapper.addMapping(self.uiFar, 4)
        self._dataMapper.addMapping(self.uiShadows, 5)
        self._dataMapper.addMapping(self.uiShape, 6, "currentIndex")
        
    """INPUTS: QModelIndex"""
    def setSelection(self, current):
        
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)
        
        self._dataMapper.setCurrentModelIndex(current)
        
        
"""CAMERA"""
class CameraEditor(cameraBase, cameraForm):
    
    def __init__(self, parent=None):
        super(cameraBase, self).__init__(parent)
        self.setupUi(self)
        
        self._dataMapper = QtGui.QDataWidgetMapper()
        
        
    def setModel(self, proxyModel):
        self._proxyModel = proxyModel
        self._dataMapper.setModel(proxyModel.sourceModel())
        
        self._dataMapper.addMapping(self.uiMotionBlur, 2)
        self._dataMapper.addMapping(self.uiShakeIntensity, 3)
        
    """INPUTS: QModelIndex"""
    def setSelection(self, current):
        
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)
        
        self._dataMapper.setCurrentModelIndex(current)
        
"""TRANSFORM"""
class TransformEditor(transformBase, transformForm):
    
    def __init__(self, parent=None):
        super(transformBase, self).__init__(parent)
        self.setupUi(self)

        self._dataMapper = QtGui.QDataWidgetMapper()
        
    def setModel(self, proxyModel):
        self._proxyModel = proxyModel
        self._dataMapper.setModel(proxyModel.sourceModel())
        
        self._dataMapper.addMapping(self.uiX, 2)
        self._dataMapper.addMapping(self.uiY, 3)
        self._dataMapper.addMapping(self.uiZ, 4)
        
    """INPUTS: QModelIndex"""
    def setSelection(self, current):
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current)
        
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setStyle("plastique")
    wnd = WndTutorial06()
    wnd.show()
    sys.exit(app.exec_())