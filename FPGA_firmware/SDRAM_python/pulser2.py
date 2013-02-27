import ok
import numpy as np
import array
import time
from struct import Struct

xem = ok.FrontPanel()
xem.OpenBySerial("")
xem.GetDeviceID()
# print xem.ConfigureFPGA('C:\Users\lattice\Desktop\LabRAD\lattice\FPGA_firmware\SDRAM_python\ramtest.bit')
# print xem.ConfigureFPGA('C:\Program Files (x86)\Opal Kelly\FrontPanelUSB\API\ramtest.bit')
xem.ConfigureFPGA('pulser.bit')

#### set normal pmt count period ###
xem.SetWireInValue(0x01,0x0064)
xem.UpdateWireIns()

#### get normal pmt count ####
buf = "\x00"*2*2*32
xem.ReadFromBlockPipeOut(0xa1,2,buf)
a = Struct("H"*(len(buf)/2))
print Struct.unpack(a,buf)


xem.ActivateTriggerIn(0x40,0)

### reset pulser ram ###
xem.ActivateTriggerIn(0x40,1)

buf1 = "\x00\x00\x00\x00\x01\x00\x01\x00"
buf2 = "\x10\x00\x00\x00\x02\x00\x02\x00"
buf3 = "\x20\x00\x00\x00\x04\x00\x04\x00"
buf4 = "\x30\x00\x00\x00\x08\x00\x08\x00"
buf5 = "\x40\x00\x00\x00\x10\x00\x10\x00"
buf6 = "\x50\x00\x00\x00\x20\x00\x20\x00"
buf7 = "\x60\x00\x00\x00\x40\x00\x40\x00"
buf8 = "\x70\x00\x00\x00\x80\x00\x80\x00"
buf9 = "\x80\x00\x00\x00\x00\x01\x00\x01"
buf10 = "\x90\x00\x00\x00\x00\x02\x00\x02"
buf11 = "\xa0\x00\x00\x00\x00\x04\x00\x04"
buf12 = "\xb0\x00\x00\x00\x00\x08\x00\x08"
buf13 = "\xc0\x00\x00\x00\x00\x10\x00\x10"
buf14 = "\xd0\x00\x00\x00\x00\x20\x00\x20"
buf15 = "\xe0\x00\x00\x00\x00\x40\x00\x40"
buf16 = "\xf0\x00\x00\x00\x00\x80\x00\x80"
buf17 = "\x00\x01\x00\x00\x00\x00\x00\x00"
blank = "\x00\x00\x00\x00\x00\x00\x00\x00"

xem.WriteToBlockPipeIn(0x80, 2, buf1)
xem.WriteToBlockPipeIn(0x80, 2, buf2)
xem.WriteToBlockPipeIn(0x80, 2, buf3)
xem.WriteToBlockPipeIn(0x80, 2, buf4)
xem.WriteToBlockPipeIn(0x80, 2, buf5)
xem.WriteToBlockPipeIn(0x80, 2, buf6)
xem.WriteToBlockPipeIn(0x80, 2, buf7)
xem.WriteToBlockPipeIn(0x80, 2, buf8)
xem.WriteToBlockPipeIn(0x80, 2, buf9)
xem.WriteToBlockPipeIn(0x80, 2, buf10)
xem.WriteToBlockPipeIn(0x80, 2, buf11)
xem.WriteToBlockPipeIn(0x80, 2, buf12)
xem.WriteToBlockPipeIn(0x80, 2, buf13)
xem.WriteToBlockPipeIn(0x80, 2, buf14)
xem.WriteToBlockPipeIn(0x80, 2, buf15)
xem.WriteToBlockPipeIn(0x80, 2, buf16)
xem.WriteToBlockPipeIn(0x80, 2, buf17)
xem.WriteToBlockPipeIn(0x80, 2, blank)

### start looped seq
xem.SetWireInValue(0x00,0x06,0x06)
xem.UpdateWireIns()