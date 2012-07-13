import ok

class api_dac():
    '''class containing all commands for interfacing with the fpga'''
    def __init__(self):
        self.xem = None
        self.okDeviceID = 'DAC'
        
    def checkConnection(self):
        if self.xem is None: raise Exception("FPGA not connected")
    
    def connectOKBoard(self):
        fp = ok.FrontPanel()
        module_count = fp.GetDeviceCount()
        print "Found {} unused modules".format(module_count)
        for i in range(module_count):
            serial = fp.GetDeviceListSerial(i)
            tmp = ok.FrontPanel()
            tmp.OpenBySerial(serial)
            id = tmp.GetDeviceID()
            if id == self.okDeviceID:
                self.xem = tmp
                print 'Connected to {}'.format(id)
                self.programOKBoard()
                return True
        return False
    
    def programOKBoard(self):
        prog = self.xem.ConfigureFPGA("dac.bit")
        if prog: raise("Not able to program FPGA")
        pll = ok.PLL22150()
        self.xem.GetEepromPLL22150Configuration(pll)
        pll.SetDiv1(pll.DivSrc_VCO,4)
        self.xem.SetPLL22150Configuration(pll)
        
    def setVoltage(self, channel, value):
        ## 32621 is mid-way ##
        self.xem.SetWireInValue(channel,value)
        self.xem.UpdateWireIns()
  
    def getVoltage(self, channel):
        self.xem.UpdateWireOuts()
        return self.xem.GetWireOutValue(32+channel)
