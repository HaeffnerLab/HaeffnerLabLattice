import sys
from PyQt4 import QtGui, QtCore

class BurningWidget(QtGui.QAbstractButton):
  
    def __init__(self):      
        super(BurningWidget, self).__init__()
        self.setMinimumSize(100, 50)
        self.setCheckable(True)

    def sizeHint(self):
        return QtCore.QSize(100,50)
    
    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()
      
      
    def drawWidget(self, qp):
        size = self.size()
        w = size.width()
        h = size.height()
        if self.isChecked():
            brush = QtGui.QBrush(QtCore.Qt.gray, QtCore.Qt.SolidPattern)
            qp.setPen(QtCore.Qt.NoPen)
            qp.setBrush(brush)
            qp.drawRect(0, 0, w - 1, h - 1)
            brush = QtGui.QBrush(QtCore.Qt.green, QtCore.Qt.SolidPattern)
            qp.setBrush(brush)
            qp.drawRect(w/2.0, 3*h/8.0, (w - 1)/4.0, (h - 1)/4.0)
        else:
            brush = QtGui.QBrush(QtCore.Qt.gray, QtCore.Qt.SolidPattern)
            qp.setPen(QtCore.Qt.gray)
            qp.setBrush(brush)
            qp.drawRect(0, 0, w - 1, h - 1)
            brush = QtGui.QBrush(QtCore.Qt.darkGreen, QtCore.Qt.SolidPattern)
            qp.setBrush(brush)
            qp.drawRect(w/2.0,  3*h/8.0, (w - 1)/4.0, (h - 1)/4.0)
    


class Example(QtGui.QWidget):
    
    def __init__(self):
        super(Example, self).__init__()
        self.initUI()
        
    def initUI(self):         
        self.wid = BurningWidget()
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.wid)
        self.setLayout(hbox)
        self.setWindowTitle('Burning widget')
        self.wid.clicked.connect(self.on_click)
        self.show()
    
    def on_click(self, x):
        print x
    
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())