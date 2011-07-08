'''
Created on Feb 14, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui
from lrexp.experimenter.dialogs.main import MainDialog

if __name__ == "__main__":

    app = QtGui.QApplication( [] )

    mainDialog = MainDialog()

    mainDialog.show()

    app.exec_()

    app.closeAllWindows()
