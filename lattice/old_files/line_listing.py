from PyQt4 import QtGui, QtCore

class line_listing(QtGui.QTableWidget):
    
    on_new_info = QtCore.pyqtSignal(str)
    
    def __init__(self, reactor, font = None, names = [], column_titles = [], column_suffix = [], column_sig_figs = [], parent = None):
        super(line_listing, self).__init__(parent)
        self.reactor = reactor
        self.font = font
        self.column_suffix = column_suffix
        self.column_sig_figs = column_sig_figs
        self.column_titles = column_titles
        self.names = names
        self.titles_to_columns = dict([(title,enum) for (enum,title) in enumerate(column_titles)])
        self.names_to_rows = dict([(name,enum) for (enum,name) in enumerate(names)])
        self.info_dict = {}.fromkeys(names, {})
        self.initializeGUI()
    
    def initializeGUI(self):
        self.setRowCount(len(self.names))
        self.setColumnCount(len(self.column_titles))
        self.setHorizontalHeaderLabels(self.column_titles)
        for i,name in enumerate(self.names):
            label = QtGui.QTableWidgetItem(name)
            if self.font is not None:
                label.setFont(self.font)
            self.setItem(i, 0, label)
    
    def set_names(self, names):
        self.clear()
        #update the known names, copying common information over from the previous dictionary
        new_dict = {}.fromkeys(names, {})
        self.update_common(new_dict, self.info_dict)
        self.info_dict = new_dict
        self.initializeGUI()
        for title,info in self.info_dict.iteritems():
            self.set_info(title, info)
           
    def update_common(self, to_update, other):
        '''update the first dictionary with values from second for all common keys'''
        common = to_update.viewkeys() & other.viewkeys()
        for key,val in other.iterkeys():
            if key in common and to_update[key] != other[key]: 
                to_update[key] = val
    
    def set_info(self, title, info):
        self.info_dict[title] = info
        for name,val in info:
            try:
                row = self.names_to_rows[name]
                col = self.titles_to_columns[title]
            except KeyError:
                pass
            else:
                self.set_item_info(row, col, val, title)
    
    def set_item_info(self,row,col, val, title):
        try:
            widget = self.cellWidget(row, col)
            widget.blockSignals(True)
            widget.setValue(val)
            widget.blockSignals(False)
        except AttributeError:
            widget = QtGui.QDoubleSpinBox()
            #widget.setRange()
            widget.setValue(val)
            widget.valueChanged.connect(lambda x: self.on_new_info.emit(title))
            self.setCellWidget(row, col, widget)
            
    def get_info(self, title):
        try:
            col = self.titles_to_columns[title]
        except KeyError:
            raise Exception('{} Not Found'.format(title))
        info = []
        for row in range(self.rowCount()):
            try:
                name = self.cellWidget(row, 0).currentText()
                value = self.cellWidget(row, col).value()
                info.append((name,value))
            except AttributeError:
                pass
        return info
            
    def closeEvent(self, x):
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = line_listing(reactor, names = ['hi', 'bye'], column_titles = ['Line Name','Center Frequency', 'Scan Span', 'Scan Points', 'Scan 729 Amplitude', 'Scan 729 Duration'])
    widget.set_info('Center Frequency', [('hi',2)])
    widget.show()
    reactor.run()