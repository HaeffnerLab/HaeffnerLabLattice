from PyQt4 import QtCore, QtGui, uic
from Data import Node, ParameterNode, CollectionNode

propBase, propForm = uic.loadUiType("Views/Editors.ui")
paramBase, paramForm = uic.loadUiType("Views/ParameterEditor.ui")
lightBase, lightForm = uic.loadUiType("Views/LightEditor.ui")
cameraBase, cameraForm = uic.loadUiType("Views/CameraEditor.ui")
transformBase, transformForm = uic.loadUiType("Views/TransformEditor.ui")

class PropertiesEditor(propBase, propForm):
    
    def __init__(self, parent = None):
        super(propBase, self).__init__(parent)
        self.setupUi(self)

        self._proxyModel = None
        #create the edtiors
        self._parametersEditor = ParameterEditor(self)
        #add editors to layout
        self.layoutSpecs.addWidget(self._parametersEditor)
        #hide the edtiors
        self._parametersEditor.setVisible(False)
               
    def setSelection(self, current, old):
        current = self._proxyModel.mapToSource(current)
        node = current.internalPointer()
        if isinstance(node, ParameterNode):
            self._parametersEditor.setVisible(True)
            self._parametersEditor.setSelection(current)
        else:
            self._parametersEditor.setVisible(False)
    
    def setModel(self, proxyModel):
        '''
        sets the model for all the editors
        '''
        self._proxyModel = proxyModel
        self._parametersEditor.setModel(proxyModel)


class parameter_delegate(QtGui.QAbstractItemDelegate):
    def __init__(self, parent):
        super(parameter_delegate, self).__init__()
        self.parent = parent
        self.parent.uiValue.editingFinished.connect(self.on_new_value)
        self.parent.uiMin.editingFinished.connect(self.on_new_min)
        self.parent.uiMax.editingFinished.connect(self.on_new_max)
        
    def setEditorData(self, editor, index):
        node = index.internalPointer()
        if editor == self.parent.uiName or editor == self.parent.uiCollection:
            editor.setText(node.data(index.column()))
        elif editor == self.parent.uiValue:             
            editor.setValue(node.data(index.column()))
        elif editor == self.parent.uiMin:
            editor.setValue(node.data(index.column()))
            self.parent.uiValue.setMinimum(node.data(index.column()))
        elif editor == self.parent.uiMax:
            editor.setValue(node.data(index.column()))
            self.parent.uiValue.setMaximum(node.data(index.column()))
        elif index.column() == 6:
            suffix = node.data(index.column())
            self.parent.uiValue.setSuffix(suffix)
            self.parent.uiMin.setSuffix(suffix)
            self.parent.uiMax.setSuffix(suffix)
    
    def on_new_value(self):
        self.commitData.emit(self.parent.uiValue)
    
    def on_new_min(self):
        self.commitData.emit(self.parent.uiMin)
    
    def on_new_max(self):
        self.commitData.emit(self.parent.uiMax)
    
    def setModelData(self, editor, model, index):
        if index.column() == 6:
            return
        elif isinstance(editor, QtGui.QLineEdit):
            value = editor.text()
        else:
            value = editor.value()
        model.setData(index, QtCore.QVariant(value))

class ParameterEditor(paramBase, paramForm):
    
    def __init__(self, parent=None):
        super(ParameterEditor, self).__init__(parent)
        self.setupUi(self)
        self._dataMapper = QtGui.QDataWidgetMapper(self)
        self._dataMapper.setItemDelegate(parameter_delegate(self))
        self.connect_signals()
    
    def connect_signals(self):
        self.uiDecimals.valueChanged.connect(self.on_new_decimals)
    
    def on_new_decimals(self, decimals):
        for widget in [self.uiMin, self.uiMax, self.uiValue]:
            widget.setSingleStep(10**-decimals)
            widget.setDecimals(decimals)

    def setModel(self, proxyModel):
        self._proxyModel = proxyModel
        self._dataMapper.setModel(proxyModel.sourceModel())
        self._dataMapper.addMapping(self.uiName, 0)
        self._dataMapper.addMapping(self.uiCollection, 2)
        self._dataMapper.addMapping(self.uiMin, 3)
        self._dataMapper.addMapping(self.uiMax, 4)
        self._dataMapper.addMapping(self.uiValue, 5)
        self._dataMapper.addMapping(QtGui.QWidget(self), 6)
     
    def setSelection(self, current):
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current)