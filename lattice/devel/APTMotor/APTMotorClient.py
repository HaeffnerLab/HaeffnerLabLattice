#import labrad
import sys
from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks

class DevicePanel(QtGui.QWidget):
    def __init__(self, parent, cxn, context, deviceName):
#    def __init__(self):    
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.cxn = cxn
        self.context = context
        self.deviceName = deviceName
        self.setupUI()
#        self.setupListeners()
           
    def setupUI(self):
        # Labels
#        getHardwareUnits = QtGui.QLabel('Get Available Hardware Units')
#        initHardwareDevice = QtGui.QLabel('Initialize Hardware Device')
#        getDeviceInformation = QtGui.QLabel('Get Device Information (Enter serial number)')
        device = QtGui.QLabel(self.deviceName)
        stepSize = QtGui.QLabel('Move Relative - Step Size')
        getSetVelParams = QtGui.QLabel('Get/Set Velocity Parameters')
        getVelParamLimits = QtGui.QLabel('Get Velocity Parameter Limits')
        getPosition = QtGui.QLabel('Get Current Position')
#        moveRelative = QtGui.QLabel('Move Relative')
        moveAbsolute = QtGui.QLabel('Move Absolute')
        identify = QtGui.QLabel('Identify Device')

        # Buttons
#        getHardwareUnitsButton = QtGui.QPushButton("Get", self)
#        getHardwareUnitsButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
#        getHardwareUnitsButton.clicked.connect(self.getHardwareUnitsSignal)
        
#        initHardwareDeviceButton = QtGui.QPushButton("Init", self)
#        initHardwareDeviceButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
#        initHardwareDeviceButton.clicked.connect(self.initHardwareDeviceSignal)
        
#        getDeviceInformationButton = QtGui.QPushButton("Get", self)
#        getDeviceInformationButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
#        getDeviceInformationButton.clicked.connect(self.getDeviceInformationSignal)
        
        getVelParamsButton = QtGui.QPushButton("Get", self)
        getVelParamsButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        getVelParamsButton.clicked.connect(self.getVelParamsSignal)
        getVelParamsButton.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        setVelParamsButton = QtGui.QPushButton("Set", self)
        setVelParamsButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        setVelParamsButton.clicked.connect(self.setVelParamsSignal)
        setVelParamsButton.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        getVelParamLimitsButton = QtGui.QPushButton("Get", self)
        getVelParamLimitsButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        getVelParamLimitsButton.clicked.connect(self.getVelParamLimitsSignal)
        getVelParamLimitsButton.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        getPositionButton = QtGui.QPushButton("Get", self)
        getPositionButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        getPositionButton.clicked.connect(self.getPositionSignal)
        getPositionButton.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
#        moveRelativeButton = QtGui.QPushButton("Move", self)
#        moveRelativeButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
#        moveRelativeButton.clicked.connect(self.moveRelativeSignal)
        
        stepLeftButton = QtGui.QPushButton("<", self)
        stepLeftButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        stepLeftButton.clicked.connect(self.moveRelativeLeftSignal)
        stepLeftButton.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        stepRightButton = QtGui.QPushButton(">", self)
        stepRightButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        stepRightButton.clicked.connect(self.moveRelativeRightSignal)
        stepRightButton.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        moveAbsoluteButton = QtGui.QPushButton("Move", self)
        moveAbsoluteButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        moveAbsoluteButton.clicked.connect(self.moveAbsoluteSignal)
        moveAbsoluteButton.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        identifyButton = QtGui.QPushButton("ID", self)
        identifyButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        identifyButton.clicked.connect(self.identifySignal)
        identifyButton.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

                        
        # Text Boxes
#        grid.addWidget(reviewEdit, 3, 1, 5, 1) # multiple lines!

#        getHardwareUnitsEdit = QtGui.QLineEdit(readOnly=True)
#        initHardwareDeviceEdit = QtGui.QLineEdit()
#        getDeviceInformationSNEdit = QtGui.QLineEdit()
#        getDeviceInformation1Edit = QtGui.QLineEdit(readOnly=True)
#        getDeviceInformation2Edit = QtGui.QLineEdit(readOnly=True)
#        getDeviceInformation3Edit = QtGui.QLineEdit(readOnly=True)
        self.getSetVelParams1Edit = QtGui.QLineEdit()
        self.getSetVelParams1Edit.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.getSetVelParams2Edit = QtGui.QLineEdit()
        self.getSetVelParams2Edit.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.getSetVelParams3Edit = QtGui.QLineEdit()
        self.getSetVelParams3Edit.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.getVelParamLimits1Edit = QtGui.QLineEdit(readOnly=True)
        self.getVelParamLimits1Edit.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.getVelParamLimits2Edit = QtGui.QLineEdit(readOnly=True)
        self.getVelParamLimits2Edit.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.getPositionEdit = QtGui.QLineEdit(readOnly=True)
        self.getPositionEdit.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.stepSizeEdit = QtGui.QLineEdit()
        self.stepSizeEdit.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.moveRelativeEdit = QtGui.QLineEdit()
        self.moveRelativeEdit.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.moveAbsoluteEdit = QtGui.QLineEdit()        
        self.moveAbsoluteEdit.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

        # Layout        
        grid = QtGui.QGridLayout()
        grid.setSpacing(5)

#        grid.addWidget(getHardwareUnits, 1, 0)
#        grid.addWidget(getHardwareUnitsButton, 1, 1)
#        grid.addWidget(getHardwareUnitsEdit, 1, 2)
#
#        grid.addWidget(initHardwareDevice, 2, 0)
#        grid.addWidget(initHardwareDeviceButton, 2, 1)
#        grid.addWidget(initHardwareDeviceEdit, 2, 2)
#
#        grid.addWidget(getDeviceInformation, 3, 0)
#        grid.addWidget(getDeviceInformationButton, 3, 1)
#        grid.addWidget(getDeviceInformationSNEdit, 3, 2)
#        grid.addWidget(getDeviceInformation1Edit, 3, 3)
#        grid.addWidget(getDeviceInformation2Edit, 3, 4)
#        grid.addWidget(getDeviceInformation3Edit, 3, 5)

        grid.addWidget(device, 3, 0)
        
        grid.addWidget(getSetVelParams, 4, 0)
        grid.addWidget(getVelParamsButton, 4, 1, QtCore.Qt.AlignRight)
        grid.addWidget(setVelParamsButton, 4, 2)
        grid.addWidget(self.getSetVelParams1Edit, 4, 3)
        grid.addWidget(self.getSetVelParams2Edit, 4, 4)
        grid.addWidget(self.getSetVelParams3Edit, 4, 5)

        grid.addWidget(getVelParamLimits, 5, 0)
        grid.addWidget(getVelParamLimitsButton, 5, 1, QtCore.Qt.AlignRight)
        grid.addWidget(self.getVelParamLimits1Edit, 5, 2)
        grid.addWidget(self.getVelParamLimits2Edit, 5, 3)

        grid.addWidget(getPosition, 6, 0)
        grid.addWidget(getPositionButton, 6, 1, QtCore.Qt.AlignRight)
        grid.addWidget(self.getPositionEdit, 6, 2)
        grid.addWidget(stepSize, 8, 1)

#        grid.addWidget(moveRelative, 7, 0)
#        grid.addWidget(moveRelativeButton, 7, 1)
#        grid.addWidget(self.moveRelativeEdit, 7, 2)
        grid.addWidget(stepLeftButton, 7, 0, QtCore.Qt.AlignRight)
        grid.addWidget(self.stepSizeEdit, 7, 1)
        grid.addWidget(stepRightButton, 7, 2)

        grid.addWidget(moveAbsolute, 6, 3, QtCore.Qt.AlignRight)
        grid.addWidget(moveAbsoluteButton, 6, 4, QtCore.Qt.AlignRight)
        grid.addWidget(self.moveAbsoluteEdit, 6, 5)

        grid.addWidget(identify, 7, 3, QtCore.Qt.AlignRight)
        grid.addWidget(identifyButton, 7, 4, QtCore.Qt.AlignRight) 

        self.setLayout(grid)        
        self.show()        
        
    # Button Functions
#    @inlineCallbacks
#    def getVelParamsSignal(self, evt):
#        velParams = yield self.parent.server.get_velocity_parameters(self.serialNumber, context = self.context)
#        self.getSetVelParams1Edit.setText(velParams[0])
#        self.getSetVelParams2Edit.setText(velParams[1])
#        self.getSetVelParams3Edit.setText(velParams[2])

    @inlineCallbacks
    def setVelParamsSignal(self, evt):
        ok = yield self.parent.server.set_velocity_parameters(float(self.getSetVelParams1Edit.text()), float(self.getSetVelParams2Edit.text()), float(self.getSetVelParams3Edit.text()), context = self.context)

    @inlineCallbacks
    def getVelParamLimitsSignal(self, evt):
        velParamLimits = yield self.parent.server.get_velocity_parameter_limits(context = self.context)
        self.getVelParamLimits1Edit.setText(str(round(velParamLimits[0], 4)))
        self.getVelParamLimits2Edit.setText(str(round(velParamLimits[1], 4)))

#    @inlineCallbacks
#    def getPositionSignal(self):
#        position = yield self.parent.server.get_position(self.serialNumber, context = self.context)
#        self.getPositionEdit.setText(position[0])
#        
#    @inlineCallbacks
#    def moveRelativeSignal(self, evt):
#        ok = yield self.parent.server.move_relative(float(self.moveRelativeEdit.text()), context = self.context)
#        if (ok == True):
#            self.getPositionSignal(1)
#        
    @inlineCallbacks
    def moveRelativeLeftSignal(self, evt):
        ok = yield self.parent.server.move_relative(-float(self.stepSizeEdit.text()), context = self.context)
        if (ok == True):
            self.getPositionSignal(1)

    @inlineCallbacks
    def moveRelativeRightSignal(self, evt):
        ok = yield self.parent.server.move_relative(float(self.stepSizeEdit.text()), context = self.context)
        if (ok == True):
            self.getPositionSignal(1)

    
    @inlineCallbacks
    def moveAbsoluteSignal(self, evt):
        ok = yield self.parent.server.move_absolute(float(self.moveAbsoluteEdit.text()), context = self.context)
        if (ok == True):
            self.getPositionSignal(1)

    @inlineCallbacks
    def identifySignal(self, evt):
        ok = yield self.parent.server.identify(context = self.context)


    @inlineCallbacks
    def getVelParamsSignal(self, evt):
        velParams = yield self.parent.server.get_velocity_parameters(context = self.context)
        self.getSetVelParams1Edit.setText(str(round(velParams[0], 4)))
        self.getSetVelParams2Edit.setText(str(round(velParams[1], 4)))
        self.getSetVelParams3Edit.setText(str(round(velParams[2], 4)))

    @inlineCallbacks
    def getPositionSignal(self, evt):
        position = yield self.parent.server.get_position(context = self.context)
        self.getPositionEdit.setText(str(round(position, 4)))

#    @inlineCallbacks
#    def setupListeners(self):               
#        yield self.parent.server.signal__position_change(88888, context = self.context)
#        yield self.parent.server.addListener(listener = self.signalTest, source = None, ID = 88888)    
#        yield self.parent.server.signal__velocity_parameter_change(99999, context = self.context)
#        yield self.parent.server.addListener(listener = self.signalTest2, source = None, ID = 99999)    
#        print 'listeners set up'
#        
#    def signalTest(self, sig):
#        print sig
#        print 'signal?'
#    
#    def signalTest2(self, sig):
#        print sig
#        print 'signal2?'


class MainPanel(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.devDict = {}
        #self.setupUI(4)     
        self.connect()              
        
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.types import Error
        self.cxn = yield connectAsync()
        self.server = yield self.cxn.apt_motor_server
        availableDevices = yield self.server.get_available_devices()
        print availableDevices
        self.setupUI(availableDevices)

    @inlineCallbacks
    def setupUI(self, availableDevices):
        self.setWindowTitle("APT Motor Control Panel")
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        self.setLayout(grid) 

        numDevices = len(availableDevices)

        for i in range(numDevices):
            context = yield self.cxn.context()
            self.server.select_device(availableDevices[i], context = context)
            devPanel = DevicePanel(self, self.cxn, context, availableDevices[i])
#            devPanel = DevicePanel()
            self.devDict[i] = devPanel
            if (i % 2 == 0): #even
                grid.addWidget(devPanel, (i / 2) , 0)
            else:
                grid.addWidget(devPanel, ((i - 1) / 2) , 1)
        #self.setGeometry(300, 300, 350, 300)
        self.show()        
    
if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    mainPanel = MainPanel()
    reactor.run()