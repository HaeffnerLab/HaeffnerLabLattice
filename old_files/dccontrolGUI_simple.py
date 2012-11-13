import sys
from PyQt4 import QtGui
from dcfrontend import Ui_DC_control

app = QtGui.QApplication(sys.argv)
window = QtGui.QDialog()
ui = Ui_DC_control()
ui.setupUi(window)

window.show()
sys.exit(app.exec_())