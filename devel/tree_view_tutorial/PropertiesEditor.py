from PyQt4 import QtCore, QtGui, uic
from Data import Node, ParameterNode, CollectionNode

propBase, propForm = uic.loadUiType("Views/Editors.ui")
paramBase, paramForm = uic.loadUiType("Views/ParameterEditor.ui")
nodeBase, nodeForm = uic.loadUiType("Views/NodeEditor.ui") 
lightBase, lightForm = uic.loadUiType("Views/LightEditor.ui")
cameraBase, cameraForm = uic.loadUiType("Views/CameraEditor.ui")
transformBase, transformForm = uic.loadUiType("Views/TransformEditor.ui")

class PropertiesEditor(propBase, propForm):
    
    def __init__(self, parent = None):
        super(propBase, self).__init__(parent)
        self.setupUi(self)

        self._proxyModel = None
        #create the edtiors
        self._nodeEditor = NodeEditor(self)
        self._lightEditor = LightEditor(self)
        self._parametersEditor = ParameterEditor(self)
        self._transformEditor = TransformEditor(self)
        #add editors to layout
        self.layoutNode.addWidget(self._nodeEditor)
        self.layoutSpecs.addWidget(self._parametersEditor)
        self.layoutSpecs.addWidget(self._lightEditor)
        self.layoutSpecs.addWidget(self._transformEditor)
        #hide the edtiors
        self._lightEditor.setVisible(False)
        self._parametersEditor.setVisible(False)
        self._transformEditor.setVisible(False)
               
    """INPUTS: QModelIndex, QModelIndex"""
    def setSelection(self, current, old):

        current = self._proxyModel.mapToSource(current)

        node = current.internalPointer()
        if isinstance(node, ParameterNode):
            self._parametersEditor.setVisible(True)
            self._lightEditor.setVisible(False)
            self._transformEditor.setVisible(False)
        else:
            self._parametersEditor.setVisible(False)
            self._lightEditor.setVisible(False)
            self._transformEditor.setVisible(False)

        self._nodeEditor.setSelection(current)
        self._parametersEditor.setSelection(current)
        self._lightEditor.setSelection(current)
        self._transformEditor.setSelection(current)
    
    def setModel(self, proxyModel):
        '''
        sets the model for all the editors
        '''
        self._proxyModel = proxyModel
        self._nodeEditor.setModel(proxyModel)
        self._lightEditor.setModel(proxyModel)
        self._parametersEditor.setModel(proxyModel)
        self._transformEditor.setModel(proxyModel)

class NodeEditor(nodeBase, nodeForm):
    
    def __init__(self, parent=None):
        super(nodeBase, self).__init__(parent)
        self.setupUi(self)
        
        self._dataMapper = QtGui.QDataWidgetMapper(self)
        
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
        

class LightEditor(lightBase, lightForm):
    
    def __init__(self, parent=None):
        super(lightBase, self).__init__(parent)
        self.setupUi(self)
        
        self._dataMapper = QtGui.QDataWidgetMapper(self)
   
        for i in ['hi, bye']:
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
        
    
class ParameterEditor(paramBase, paramForm):
    
    def __init__(self, parent=None):
        super(ParameterEditor, self).__init__(parent)
        self.setupUi(self)
        
        self._dataMapper = QtGui.QDataWidgetMapper(self)
#        self.uiName.setText('name')
#        self.uiValue.setValue(1.0)
        
        
    def setModel(self, proxyModel):
        self._proxyModel = proxyModel
        self._dataMapper.setModel(proxyModel.sourceModel())
        
        self._dataMapper.addMapping(self.uiName, 0)
#        self._dataMapper.addMapping(self.uiShakeIntensity, 3)
#        
    """INPUTS: QModelIndex"""
    def setSelection(self, current):
        
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)
        
        self._dataMapper.setCurrentModelIndex(current)

class TransformEditor(transformBase, transformForm):
    
    def __init__(self, parent=None):
        super(transformBase, self).__init__(parent)
        self.setupUi(self)

        self._dataMapper = QtGui.QDataWidgetMapper(self)
        
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