#import labrad
import sys
from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks

class DevicePanel(QtGui.QWidget):
    def __init__(self, parent, cxn, context, serialNumber):
#    def __init__(self):    
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.cxn = cxn
        self.context = context
        self.serialNumber = serialNumber
        self.setupUI()
#        self.setupListeners()
           
    def setupUI(self):
        # Labels
#        getHardwareUnits = QtGui.QLabel('Get Available Hardware Units')
#        initHardwareDevice = QtGui.QLabel('Initialize Hardware Device')
#        getDeviceInformation = QtGui.QLabel('Get Device Information (Enter serial number)')
        getSetVelParams = QtGui.QLabel('Get/Set Velocity Parameters')
        getVelParamLimits = QtGui.QLabel('Get Velocity Parameter Limits')
        getPosition = QtGui.QLabel('Get Current Position')
        moveRelative = QtGui.QLabel('Move Relative')
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
        
        setVelParamsButton = QtGui.QPushButton("Set", self)
        setVelParamsButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        setVelParamsButton.clicked.connect(self.setVelParamsSignal)
        
        getVelParamLimitsButton = QtGui.QPushButton("Get", self)
        getVelParamLimitsButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        getVelParamLimitsButton.clicked.connect(self.getVelParamLimitsSignal)
        
        getPositionButton = QtGui.QPushButton("Get", self)
        getPositionButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        getPositionButton.clicked.connect(self.getPositionSignal)
        
        moveRelativeButton = QtGui.QPushButton("Move", self)
        moveRelativeButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        moveRelativeButton.clicked.connect(self.moveRelativeSignal)
        
        moveAbsoluteButton = QtGui.QPushButton("Move", self)
        moveAbsoluteButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        moveAbsoluteButton.clicked.connect(self.moveAbsoluteSignal)
        
        identifyButton = QtGui.QPushButton("ID", self)
        identifyButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
#       identifyButton.clicked.connect(self.identifySignal)
                        
        # Text Boxes
#        grid.addWidget(reviewEdit, 3, 1, 5, 1) # multiple lines!

#        getHardwareUnitsEdit = QtGui.QLineEdit(readOnly=True)
#        initHardwareDeviceEdit = QtGui.QLineEdit()
#        getDeviceInformationSNEdit = QtGui.QLineEdit()
#        getDeviceInformation1Edit = QtGui.QLineEdit(readOnly=True)
#        getDeviceInformation2Edit = QtGui.QLineEdit(readOnly=True)
#        getDeviceInformation3Edit = QtGui.QLineEdit(readOnly=True)
        self.getSetVelParams1Edit = QtGui.QLineEdit()
        self.getSetVelParams2Edit = QtGui.QLineEdit()
        self.getSetVelParams3Edit = QtGui.QLineEdit()
        self.getVelParamLimits1Edit = QtGui.QLineEdit(readOnly=True)
        self.getVelParamLimits2Edit = QtGui.QLineEdit(readOnly=True)
        self.getPositionEdit = QtGui.QLineEdit(readOnly=True)
        self.moveRelativeEdit = QtGui.QLineEdit()
        self.moveAbsoluteEdit = QtGui.QLineEdit()        

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

        grid.addWidget(getSetVelParams, 4, 0)
        grid.addWidget(getVelParamsButton, 4, 1)
        grid.addWidget(setVelParamsButton, 4, 2)
        grid.addWidget(self.getSetVelParams1Edit, 4, 3)
        grid.addWidget(self.getSetVelParams2Edit, 4, 4)
        grid.addWidget(self.getSetVelParams3Edit, 4, 5)

        grid.addWidget(getVelParamLimits, 5, 0)
        grid.addWidget(getVelParamLimitsButton, 5, 1)
        grid.addWidget(self.getVelParamLimits1Edit, 5, 2)
        grid.addWidget(self.getVelParamLimits2Edit, 5, 3)

        grid.addWidget(getPosition, 6, 0)
        grid.addWidget(getPositionButton, 6, 1)
        grid.addWidget(self.getPositionEdit, 6, 2)

        grid.addWidget(moveRelative, 7, 0)
        grid.addWidget(moveRelativeButton, 7, 1)
        grid.addWidget(self.moveRelativeEdit, 7, 2)

        grid.addWidget(moveAbsolute, 8, 0)
        grid.addWidget(moveAbsoluteButton, 8, 1)
        grid.addWidget(self.moveAbsoluteEdit, 8, 2)

        grid.addWidget(identify, 9, 0)
        grid.addWidget(identifyButton, 9, 1) 

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
        ok = yield self.parent.server.set_velocity_parameters(self.serialNumber, float(self.getSetVelParams1Edit.text()), float(self.getSetVelParams2Edit.text()), float(self.getSetVelParams3Edit.text()), context = self.context)

    @inlineCallbacks
    def getVelParamLimitsSignal(self, evt):
        velParamLimits = yield self.parent.server.get_velocity_parameter_limits(self.serialNumber, context = self.context)
        self.getVelParamLimits1Edit.setText(str(velParamLimits[0]))
        self.getVelParamLimits2Edit.setText(str(velParamLimits[1]))

#    @inlineCallbacks
#    def getPositionSignal(self):
#        position = yield self.parent.server.get_position(self.serialNumber, context = self.context)
#        self.getPositionEdit.setText(position[0])
#        
    @inlineCallbacks
    def moveRelativeSignal(self, evt):
        ok = yield self.parent.server.move_relative(self.serialNumber, float(self.moveRelativeEdit.text()), context = self.context)
        if (ok == True):
            self.getPositionSignal(1)
        
    @inlineCallbacks
    def moveAbsoluteSignal(self, evt):
        ok = yield self.parent.server.move_absolute(self.serialNumber, float(self.moveAbsoluteEdit.text()), context = self.context)
        if (ok == True):
            self.getPositionSignal(1)

    @inlineCallbacks
    def identifySignal(self, evt):
        ok = yield self.parent.server.identify(self.serialNumber, context = self.context)


    @inlineCallbacks
    def getVelParamsSignal(self, evt):
        velParams = yield self.parent.server.get_velocity_parameters(self.serialNumber, context = self.context)
        self.getSetVelParams1Edit.setText(str(velParams[0]))
        self.getSetVelParams2Edit.setText(str(velParams[1]))
        self.getSetVelParams3Edit.setText(str(velParams[2]))

    @inlineCallbacks
    def getPositionSignal(self, evt):
        position = yield self.parent.server.get_position(self.serialNumber, context = self.context)
        self.getPositionEdit.setText(str(position))

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
        hwunits = yield self.server.get_available_hardware_units()
        print hwunits
        self.setupUI(hwunits)


    @inlineCallbacks
    def setupUI(self, hwunits):
        self.setWindowTitle("APT Motor Control Panel")
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        self.setLayout(grid) 

        numDevices = len(hwunits)/2
        
        for i in range(numDevices):
            context = yield self.cxn.context()
            ok = yield self.server.initialize_hardware_device(hwunits[2*i + 1], context = context)
#            ok = True
            if (ok == True):
                devPanel = DevicePanel(self, self.cxn, context, hwunits[2*i + 1])
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