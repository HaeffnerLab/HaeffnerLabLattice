import labrad
import sys
from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks

class ControlPanel(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
       
        #self.connect()
        self.setupUI()
        
    def setupUI(self):
        self.setWindowTitle("APT Motor Control Panel")
        getHardwareUnits = QtGui.QLabel('Get Available Hardware Units')
        initHardwareDevice = QtGui.QLabel('Initialize Hardware Device')
        getDeviceInformation = QtGui.QLabel('Get Device Information (Enter serial number)')
        getSetVelParams = QtGui.QLabel('Get/Set Velocity Parameters')
        getVelParamLimits = QtGui.QLabel('Get Velocity Parameter Limits')
        getPosition = QtGui.QLabel('Get Current Position')
        moveRelative = QtGui.QLabel('Move Relative')
        moveAbsolute = QtGui.QLabel('Move Absolute')
        identify = QtGui.QLabel('Identify Device')

        getHardwareUnitsButton = QtGui.QPushButton("Get", self)
        getHardwareUnitsButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        initHardwareDeviceButton = QtGui.QPushButton("Init", self)
        initHardwareDeviceButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        getDeviceInformationButton = QtGui.QPushButton("Get", self)
        getDeviceInformationButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        getVelParamsButton = QtGui.QPushButton("Get", self)
        getVelParamsButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        setVelParamsButton = QtGui.QPushButton("Set", self)
        setVelParamsButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        getVelParamLimitsButton = QtGui.QPushButton("Get", self)
        getVelParamLimitsButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        getPositionButton = QtGui.QPushButton("Get", self)
        getPositionButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        moveRelativeButton = QtGui.QPushButton("Move", self)
        moveRelativeButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        moveAbsoluteButton = QtGui.QPushButton("Move", self)
        moveAbsoluteButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        identifyButton = QtGui.QPushButton("ID", self)
        identifyButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
                        
        
        getHardwareUnitsEdit = QtGui.QLineEdit(readOnly=True)
        initHardwareDeviceEdit = QtGui.QLineEdit()
        getDeviceInformationSNEdit = QtGui.QLineEdit()
        getDeviceInformation1Edit = QtGui.QLineEdit(readOnly=True)
        getDeviceInformation2Edit = QtGui.QLineEdit(readOnly=True)
        getDeviceInformation3Edit = QtGui.QLineEdit(readOnly=True)
        getSetVelParams1Edit = QtGui.QLineEdit()
        getSetVelParams2Edit = QtGui.QLineEdit()
        getSetVelParams3Edit = QtGui.QLineEdit()
        getVelParamLimits1Edit = QtGui.QLineEdit(readOnly=True)
        getVelParamLimits2Edit = QtGui.QLineEdit(readOnly=True)
        getPositionEdit = QtGui.QLineEdit(readOnly=True)
        moveRelativeEdit = QtGui.QLineEdit()
        moveAbsoluteEdit = QtGui.QLineEdit()        
        
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(getHardwareUnits, 1, 0)
        grid.addWidget(getHardwareUnitsButton, 1, 1)
        grid.addWidget(getHardwareUnitsEdit, 1, 2)

        grid.addWidget(initHardwareDevice, 2, 0)
        grid.addWidget(initHardwareDeviceButton, 2, 1)
        grid.addWidget(initHardwareDeviceEdit, 2, 2)

        grid.addWidget(getDeviceInformation, 3, 0)
        grid.addWidget(getDeviceInformationButton, 3, 1)
        grid.addWidget(getDeviceInformationSNEdit, 3, 2)
        grid.addWidget(getDeviceInformation1Edit, 3, 3)
        grid.addWidget(getDeviceInformation2Edit, 3, 4)
        grid.addWidget(getDeviceInformation3Edit, 3, 5)

        grid.addWidget(getSetVelParams, 4, 0)
        grid.addWidget(getVelParamsButton, 4, 1)
        grid.addWidget(setVelParamsButton, 4, 2)
        grid.addWidget(getSetVelParams1Edit, 4, 3)
        grid.addWidget(getSetVelParams2Edit, 4, 4)
        grid.addWidget(getSetVelParams3Edit, 4, 5)

        grid.addWidget(getVelParamLimits, 5, 0)
        grid.addWidget(getVelParamLimitsButton, 5, 1)
        grid.addWidget(getVelParamLimits1Edit, 5, 2)
        grid.addWidget(getVelParamLimits2Edit, 5, 3)

        grid.addWidget(getPosition, 6, 0)
        grid.addWidget(getPositionButton, 6, 1)
        grid.addWidget(getPositionEdit, 6, 2)

        grid.addWidget(moveRelative, 7, 0)
        grid.addWidget(moveRelativeButton, 7, 1)
        grid.addWidget(moveRelativeEdit, 7, 2)

        grid.addWidget(moveAbsolute, 8, 0)
        grid.addWidget(moveAbsoluteButton, 8, 1)
        grid.addWidget(moveAbsoluteEdit, 8, 2)

        grid.addWidget(identify, 9, 0)
        grid.addWidget(identifyButton, 9, 1)

    

#        grid.addWidget(reviewEdit, 3, 1, 5, 1) # multiple lines!
        
        self.setLayout(grid) 
        
        #self.setGeometry(300, 300, 350, 300)
        self.show()        
        
        

#        getNumberUnitsButton = QtGui.QPushButton("Available HW Units", self)
#        getNumberUnitsButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        
        
        
    @inlineCallbacks
    def connect(self):
        print 'trying to connect?'
#        from labrad.wrappers import connectAsync
#        from labrad.types import Error
        self.cxn = labrad.connect()
        self.server = yield self.cxn.apt_motor_server
        print 'connected?'
        hwunits = yield self.server.get_available_hardware_units()
        print hwunits      
        #self.cxn.apt_motor_server.clean_up_apt()

if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    controlPanel = ControlPanel()
    sys.exit(a.exec_())


