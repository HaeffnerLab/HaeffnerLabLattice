from PyQt4 import QtGui, QtCore
 
class progress_bar(QtGui.QProgressBar):
    def __init__(self, reactor, parent=None):
        super(progress_bar, self).__init__(parent)
        self.reactor = reactor
        self.set_status('', 0.0)
    
    def set_status(self, status_name, percentage):
        self.setValue(percentage)
        self.setFormat('{0} %p%'.format(status_name))

    def closeEvent(self, x):
        self.reactor.stop()

class fixed_width_button(QtGui.QPushButton):
    def __init__(self, text, size):
        super(fixed_width_button, self).__init__(text)
        self.size = size
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
    
    def sizeHint(self):
        return QtCore.QSize(*self.size)
        
class script_status_widget(QtGui.QWidget):
    def __init__(self, reactor, ident, name , font = None, parent = None):
        super(script_status_widget, self).__init__(parent)
        self.reactor = reactor
        self.ident = ident
        self.name = name
        self.parent = parent
        self.font = QtGui.QFont('MS Shell Dlg 2',pointSize=12)
        if self.font is None:
            self.font = QtGui.QFont()
        self.setup_layout()
        self.connect_layout()
        self.finished = False
    
    def setup_layout(self):
        layout = QtGui.QHBoxLayout()
        self.id_label = QtGui.QLabel('{0}'.format(self.ident))
        self.id_label.setFont(self.font)
        self.id_label.setMinimumWidth(50)
        self.id_label.setAlignment(QtCore.Qt.AlignCenter)
        self.id_label.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.name_label = QtGui.QLabel(self.name)
        self.name_label.setFont(self.font)
        self.name_label.setAlignment(QtCore.Qt.AlignLeft)
        self.name_label.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        self.name_label.setMinimumWidth(200)
        self.progress_bar = progress_bar(self.reactor, self.parent)
        self.pause_button = fixed_width_button("Pause", (75,23))
        self.stop_button = fixed_width_button("Stop", (75,23))
        layout.addWidget(self.id_label)
        layout.addWidget(self.name_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.stop_button)
        self.setLayout(layout)
    
    def connect_layout(self):
        pass
#        self.stop_button.pressed.connect(self.on_stop)
#        self.pause_button.pressed.connect(self.on_pause)
        
    def on_pause(self):
        if self.pause_button.text() == 'Pause':
            self.pause_button.setText('Continue')
        else:
            self.pause_button.setText('Pause')
    
    def setFinished(self):
        self.stop_button.setText('Restart') 
        self.id_label.setDisabled(True)
        self.name_label.setDisabled(True)
        self.pause_button.setDisabled(True)
        self.progress_bar.setDisabled(True)
        self.finished = True
    
    def set_status(self, status, percentage):
        self.progress_bar.set_status(status, percentage)
        
    def closeEvent(self, x):
        self.reactor.stop()

class running_scans_list(QtGui.QTableWidget):
    
    on_cancel = QtCore.pyqtSignal(int)
    on_pause = QtCore.pyqtSignal(int, bool)
    on_stop = QtCore.pyqtSignal(int)
    
    def __init__(self, reactor, font = None, parent = None):
        super(running_scans_list, self).__init__(parent)
        self.reactor = reactor
        self.parent = parent
        self.font = font
        if self.font is None:
            self.font = QtGui.QFont('MS Shell Dlg 2',pointSize=12)
        self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.setupLayout()
        self.d = {}
        self.cellDoubleClicked.connect(self.on_double_click)
    
    def on_double_click(self, row, column):
        widget = self.cellWidget(row, column)
        item = self.item(row, column)
        self.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.selectRow(row)
        self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
    
    def setupLayout(self):
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.setColumnCount(1)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setShowGrid(False)
        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)

    def cancel_all(self):
        pass
#        for ident in self.d.keys():
#            self.on_cancel.emit(ident)
    
    def add(self, ident, name):
        ident = int(ident)
        row_count = self.rowCount()
        self.setRowCount(row_count + 1)
        widget = script_status_widget(self.reactor, parent = self.parent, ident = ident, name = name)
#        self.mapper_cancel.setMapping(widget.cancel_button, ident)
#        widget.cancel_button.pressed.connect(self.mapper_cancel.map)
#        self.mapper_duration.setMapping(widget.scheduled_duration, ident)
#        widget.scheduled_duration.valueChanged.connect(self.mapper_duration.map)
        self.setCellWidget(row_count, 0, widget)
        self.resizeColumnsToContents()
        self.d[ident] = widget
    
    def set_status(self, ident, status, percentage):
        try:
            widget = self.d[ident]
        except KeyError:
            print "trying set status of experiment that's not there"
        else:
            widget.set_status(status, percentage)
            
    def remove(self, ident):
        selected = [model.row() for model in self.selectionModel().selectedRows()]
        widget = self.d[ident]
        for row in range(self.rowCount()):
            if self.cellWidget(row, 0) == widget and not row in selected:
                del self.d[ident]
                self.removeRow(row)
    
    def sizeHint(self):
        width = 0
        for i in range(self.columnCount()):
            width += self.columnWidth(i)
        height = 0
        for i in range(self.rowCount()):
            height += self.rowHeight(i)
        return QtCore.QSize(width, height)

    def finish(self, ident):
        try:
            widget = self.d[ident]
            widget.setFinished()
        except KeyError:
            print "trying disable experiment that's not there"
    
    def clear_finished(self):
        [self.remove(ident) for (ident, widget) in self.d.items() if widget.finished]
                  
    def closeEvent(self, x):
        self.reactor.stop()
        
class running_combined(QtGui.QWidget):
    def __init__(self, reactor, font = None, parent = None):
        super(running_combined, self).__init__(parent)
        self.reactor = reactor
        self.parent = parent
        self.font = font
        if self.font is None:
            self.font = QtGui.QFont('MS Shell Dlg 2',pointSize=12)
        self.setupLayout()
        self.connect_layout()
    
    def setupLayout(self):
        layout = QtGui.QGridLayout()
        title = QtGui.QLabel("Running", font = self.font)
        title.setAlignment(QtCore.Qt.AlignLeft)
        self.scans_list = running_scans_list(self.reactor, self.parent)
        self.clear_finished = QtGui.QPushButton("Clear Finished")
        layout.addWidget(title, 0, 0, 1, 2 )
        layout.addWidget(self.clear_finished, 0, 2, 1, 1 )
        layout.addWidget(self.scans_list, 1, 0, 3, 3 )
        self.setLayout(layout)
    
    def add(self, ident, name):
        self.scans_list.add(ident, name)
    
    def set_status(self, ident, status, percentage):
        self.scans_list.set_status(ident, status, percentage)
    
    def finish(self, ident):
        self.scans_list.finish(ident)
    
    def connect_layout(self):
        self.clear_finished.pressed.connect(self.scans_list.clear_finished)
    
    def closeEvent(self, x):
        self.reactor.stop()