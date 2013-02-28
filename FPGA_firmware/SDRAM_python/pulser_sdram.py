import ok
import numpy as np
import array
import time

def _intToBuf(num):
    '''
    takes the integer representing the setting and returns the buffer string for dds programming
    '''
    #converts value to buffer string, i.e 128 -> \x00\x00\x00\x80
    b = num % 256**2
    arr = array.array('B', [b % 256, b // 256])
    ans = arr.tostring()
    return ans

#    ans = 65536*(256*ord(buf[1])+ord(buf[0]))+(256*ord(buf[3])+ord(buf[2]))


xem = ok.FrontPanel()
xem.OpenBySerial("")
xem.GetDeviceID()
pll = ok.PLL22393()
xem.GetPLL22393Configuration(pll) ### load configuration
pll.SetPLLParameters(0,25,3,True) ### PLL VCO setting: f = 48*25/3 = 400 MHz
pll.SetOutputDivider(0,4) ### Output1: 400/4 = 100 MHz
pll.SetOutputDivider(1,4) ### Output2: 400/4 = 100 MHz
pll.SetOutputEnable(0, True) ### Enable output1
pll.SetOutputEnable(1, True) ### Enable output2
print pll.GetOutputFrequency(0)
print pll.GetOutputFrequency(1)
xem.SetPLL22393Configuration(pll) ### set PLL configuration

# print xem.ConfigureFPGA('C:\Users\lattice\Desktop\LabRAD\lattice\FPGA_firmware\SDRAM_python\ramtest.bit')
# print xem.ConfigureFPGA('C:\Program Files (x86)\Opal Kelly\FrontPanelUSB\API\ramtest.bit')
xem.ConfigureFPGA('pulser.bit')


xem.SetWireInValue(0x07,0x0004)
xem.UpdateWireIns()
xem.SetWireInValue(0x07,0x0000)
xem.UpdateWireIns()
xem.SetWireInValue(0x07,0x0002)
xem.UpdateWireIns()

time.sleep(5)


write_size = 128

rand = np.random.random_integers(0,256**2-1,write_size) #each one is 16 bit


xem.SetWireInValue(0x07,0x0004)
xem.UpdateWireIns()
xem.SetWireInValue(0x07,0x0000)
xem.UpdateWireIns()
xem.SetWireInValue(0x07,0x0001)
xem.UpdateWireIns()


read_buf1 = write_size*2*'\x00'

xem.ReadFromPipeOut(0xA0, read_buf1)


read_number1 = rand.copy()
for i in np.arange(0,len(rand)):
    read_number1[i] = (256*ord(read_buf1[i*2+1])+ord(read_buf1[i*2]))

#print rand[0:64]
print read_number1[0:256]