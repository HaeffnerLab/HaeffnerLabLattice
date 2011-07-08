'''
Created on Apr 25, 2011

@author: christopherreilly
'''
from PyQt4 import QtGui, QtCore

menubar = QtGui.QMenuBar()
fileMenu = menubar.addMenu( 'File' )
recentFiles = fileMenu.addMenu( 'Load recent file' )
