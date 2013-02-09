from PyQt4 import QtGui, QtCore

class parameters_widget(QtGui.QWidget):
    def __init__(self, reactor):
        super(parameters_widget, self).__init__()
        self.reactor = reactor
        self.setupLayout()
    
    def setupLayout(self):
        layout = QtGui.QGridLayout()
        label = QtGui.QLabel("Experiment")
        dropdown = QtGui.QComboBox()
        tree = parameter_tree()
        layout.addWidget(label, 0, 0, 1, 1)
        layout.addWidget(dropdown, 0, 1, 1, 2)
        layout.addWidget(tree, 1, 0, 5, 3)
        self.setLayout(layout)
    
    def connect_layout(self):
        pass
    
    def closeEvent(self, event):
        self.reactor.stop()

class parameter_tree(QtGui.QTreeWidget):
    def __init__(self):
        super(parameter_tree, self).__init__()
        self.setColumnCount(2)
        
        simple_sub = QtGui.QTreeWidgetItem()
        box = QtGui.QDoubleSpinBox()
        box.setAutoFillBackground(True)
        self.setItemWidget(simple_sub, 0, box)
#        text = QtCore.QString("hi")
        item = QtGui.QTreeWidgetItem()
        item.setText(0, "hi")
        item.setText(1, "what")
        self.addTopLevelItem(item)
        item = QtGui.QTreeWidgetItem()
        item.setText(0, "hi")
        item.setText(1, "what")
        self.addTopLevelItem(item)

if __name__=="__main__":
    a = QtGui.QApplication( ["Script Scanner"] )
    from common.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    gui = parameter_tree()
    gui.show()
    reactor.run()