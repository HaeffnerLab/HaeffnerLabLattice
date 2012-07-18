## import Opal Kelly library ##
import ok
import time
from struct import Struct
import array

xem = ok.FrontPanel()

xem.OpenBySerial("")

xem.GetDeviceID()

#This line load a configuration file into the FPGA#

xem.ConfigureFPGA("/Users/thanedp/LabRAD/lattice/okfpgaservers/pulser/photon.bit")


#### write to dds #####
#### first 2 is the frequency, last 2 is the amplitude ####
####  \xff\x00 in freq means (7 downto 0) is ff and (15 downto 8) is 00 ##
#### Each unit in freq is to increase by about 3 kHz #####


xem.ActivateTriggerIn(0x40,6)
xem.ActivateTriggerIn(0x40,4)

xem.SetWireInValue(0x04,0x00)
xem.UpdateWireIns()

data1 = "\x00\x00\xff\xff"
freq = 220.0  ### in MHz
freq_round = int(freq*(2**32)/800.00)
a, b = freq_round // 256**2, freq_round % 256**2
arr = array.array('B', [b % 256 ,b // 256, a % 256, a // 256])
data2 = arr.tostring()
data = data1 + data2

####phase: \xLSB\xMSB amplitude: \x\xMSB freq: \xLSB\xlSB\xmSB\xMSB

xem.WriteToBlockPipeIn(0x81, 2, data)

xem.WriteToBlockPipeIn(0x81, 2, "\x00\x00")

