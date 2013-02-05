from PyQt4 import QtGui, QtCore

class fixed_width_button(QtGui.QPushButton):
    def __init__(self, text, size):
        super(fixed_width_button, self).__init__(text)
        self.size = size
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
    
    def sizeHint(self):
        return QtCore.QSize(*self.size)
        
class scheduled_widget(QtGui.QWidget):
    def __init__(self, reactor, font = None, parent = None):
        super(scheduled_widget, self).__init__(parent)
        self.reactor = reactor
        self.parent = parent
        self.font = QtGui.QFont('MS Shell Dlg 2',pointSize=12)
        if self.font is None:
            self.font = QtGui.QFont()
        self.setup_layout()
        self.connect_layout()
    
    def setup_layout(self):
        layout = QtGui.QHBoxLayout()
        self.id_label = QtGui.QLabel('001')
        self.id_label.setFont(self.font)
        self.id_label.setMinimumWidth(50)
        self.id_label.setAlignment(QtCore.Qt.AlignCenter)
        self.id_label.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.name_label = QtGui.QLabel("Name")
        self.name_label.setFont(self.font)
        self.name_label.setAlignment(QtCore.Qt.AlignLeft)
        self.name_label.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        self.name_label.setMinimumWidth(200)
        self.scheduled_duration = QtGui.QSpinBox()
        self.cancel_button = fixed_width_button("Cancel", (75,23))
        layout.addWidget(self.id_label)
        layout.addWidget(self.name_label)
        layout.addWidget(self.scheduled_duration)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)
    
    def connect_layout(self):
        pass
#        self.pause_button.pressed.connect(self.on_pause)
    
    def on_stop(self):
        if self.stop_button.text() == 'Stop':
            self.stop_button.setText('Restart') 
        
        else:
            self.stop_button.setDisabled(True)
        self.pause_button.setDisabled(True)
        
    def on_pause(self):
        if self.pause_button.text() == 'Pause':
            self.pause_button.setText('Continue')
        else:
            self.pause_button.setText('Pause')
        
    def closeEvent(self, x):
        self.reactor.stop()

class scheduled_list(QtGui.QTableWidget):
    def __init__(self, reactor, font = None, parent = None):
        super(scheduled_list, self).__init__(parent)
        self.reactor = reactor
        self.parent = parent
        self.font = font
        if self.font is None:
            self.font = QtGui.QFont('MS Shell Dlg 2',pointSize=12)
        self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.test_item()
    
    def test_item(self):
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.setColumnCount(1)
        self.setRowCount(3)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setShowGrid(False)
        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        
        for i in range(3):
            widget = scheduled_widget(self.reactor, self.parent)
            self.setCellWidget(i, 0, widget)
            self.resizeColumnsToContents()
            self.adjustSize()
#        self.removeRow(0)
    
    def sizeHint(self):
        width = 0
        for i in range(self.columnCount()):
            width += self.columnWidth(i)
        height = 0
        for i in range(self.rowCount()):
            height += self.rowHeight(i)
        return QtCore.QSize(width, height)
    
    def closeEvent(self, x):
        self.reactor.stop()
        
class scheduled_combined(QtGui.QWidget):
    def __init__(self, reactor, font = None, parent = None):
        super(scheduled_combined, self).__init__(parent)
        self.reactor = reactor
        self.parent = parent
        self.font = font
        if self.font is None:
            self.font = QtGui.QFont('MS Shell Dlg 2',pointSize=12)
        self.setupLayout()
    
    def setupLayout(self):
        layout = QtGui.QGridLayout()
        title = QtGui.QLabel("Scheduled", font = self.font)
        title.setAlignment(QtCore.Qt.AlignLeft)
        ql = scheduled_list(self.reactor, self.parent)
        cancel_all = QtGui.QPushButton("Cancel All")
        layout.addWidget(title, 0, 0, 1, 2 )
        layout.addWidget(cancel_all, 0, 2, 1, 1 )
        layout.addWidget(ql, 1, 0, 3, 3 )
        self.setLayout(layout)
    
    def closeEvent(self, x):
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    from common.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
#    widget = progress_bar(reactor).
#    widget = script_status_widget(reactor)
    widget = scheduled_widget(reactor)
#    widget = scheduled_combined(reactor)
    widget.show()
    reactor.run()