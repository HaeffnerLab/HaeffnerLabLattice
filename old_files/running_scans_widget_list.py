from PyQt4 import QtGui, QtCore
 
class progress_bar(QtGui.QProgressBar):
    def __init__(self, reactor, parent=None):
        super(progress_bar, self).__init__(parent)
        self.reactor = reactor
        self.setStatus('Running', 50.0)
    
    def setStatus(self, status_name, percentage):
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
    def __init__(self, reactor, font = None, parent = None):
        super(script_status_widget, self).__init__(parent)
        self.reactor = reactor
        self.parent = parent
        self.font = QtGui.QFont('MS Shell Dlg 2',pointSize=12)
        if self.font is None:
            self.font = QtGui.QFont()
        self.setup_layout()
        self.connect_layout()
    
    def setup_layout(self):
        layout = QtGui.QHBoxLayout()
        self.name_label = QtGui.QLabel("Name")
        self.name_label.setFont(self.font)
        self.name_label.setAlignment(QtCore.Qt.AlignLeft)
        self.name_label.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        self.name_label.setMinimumWidth(200)
        self.progress_bar = progress_bar(self.reactor, self.parent)
        self.pause_button = fixed_width_button("Pause", (75,23))
        self.stop_button = fixed_width_button("Stop", (75,23))
        layout.addWidget(self.name_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.stop_button)
        self.setLayout(layout)
    
    def connect_layout(self):
        self.stop_button.pressed.connect(self.on_stop)
        self.pause_button.pressed.connect(self.on_pause)
    
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

class running_scans_list(QtGui.QListWidget):
    def __init__(self, reactor, font = None, parent = None):
        super(running_scans_list, self).__init__(parent)
        self.reactor = reactor
        self.parent = parent
        self.font = font
        if self.font is None:
            self.font = QtGui.QFont('MS Shell Dlg 2',pointSize=12)
        self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.test_item()
        self.itemDoubleClicked.connect(self.on_double_click)
    
    def on_double_click(self, widgetitem):
        widgetitem.setBackgroundColor(QtCore.Qt.lightGray)
    
    def test_item(self):
        new_scan = script_status_widget(self.reactor, self.parent)

        widgetitem = QtGui.QListWidgetItem()
        widgetitem.setSizeHint(new_scan.sizeHint())
        self.setMinimumWidth(new_scan.sizeHint().width() + 20)
        self.addItem(widgetitem)
        self.setItemWidget(widgetitem, new_scan)
        
        new_scan = script_status_widget(self.reactor, self.parent)
        widgetitem = QtGui.QListWidgetItem()
        widgetitem.setSizeHint(new_scan.sizeHint())

        self.addItem(widgetitem)
        self.setItemWidget(widgetitem, new_scan)
        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)

    def closeEvent(self, x):
        self.reactor.stop()
        
class running_scans(QtGui.QWidget):
    def __init__(self, reactor, font = None, parent = None):
        super(running_scans, self).__init__(parent)
        self.reactor = reactor
        self.parent = parent
        self.font = font
        if self.font is None:
            self.font = QtGui.QFont('MS Shell Dlg 2',pointSize=12)
        self.setupLayout()
    
    def setupLayout(self):
        layout = QtGui.QGridLayout()
        title = QtGui.QLabel("Running Experiments", font = self.font)
        scans_list = running_scans_list(self.reactor, self.parent)
        clear_finished = QtGui.QPushButton("Clear Finished")
        layout.addWidget(title, 0, 0, 1, 2 )
        layout.addWidget(clear_finished, 0, 2, 1, 1 )
        layout.addWidget(scans_list, 1, 0, 3, 3 )
        self.setLayout(layout)
    
    def closeEvent(self, event):
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    from common.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
#    widget = progress_bar(reactor).
#    widget = script_status_widget(reactor)
#    widget = running_scans_list(reactor)
    widget = running_scans(reactor)
    widget.show()
    reactor.run()