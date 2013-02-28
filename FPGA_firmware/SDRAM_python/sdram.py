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

xem.ConfigureFPGA('pulser.bit')

write_size = 64

#rand = np.random.random_integers(0,256**2-1,write_size) #each one is 16 bit
#buf = ''.join([_intToBuf(num) for num in rand])

#reset FIFO on fpga
xem.SetWireInValue(0x07,0x0004)
xem.UpdateWireIns()
xem.SetWireInValue(0x07,0x0000)
xem.UpdateWireIns()

#begin write to memory
xem.SetWireInValue(0x07,0x0002)
xem.UpdateWireIns()

#print "writing to mem..."
#xem.WriteToPipeIn(0x82, buf)

#xem.UpdateWireOuts()

#print "done writing..."


print "begin pulse sequence"

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

###start one seq
xem.SetWireInValue(0x00,0x06,0x06)
xem.UpdateWireIns()

print "begin reading1..."

time.sleep(1)

xem.SetWireInValue(0x07,0x0004)
xem.UpdateWireIns()
xem.SetWireInValue(0x07,0x0000)
xem.UpdateWireIns()
xem.SetWireInValue(0x07,0x0001)
xem.UpdateWireIns()

#time.sleep(5)

read_buf1 = write_size*4*'\x00'

xem.ReadFromPipeOut(0xA0, read_buf1)
print "done reading1"

xem.UpdateWireOuts()


#read_number1 = rand.copy()
for i in np.arange(0,write_size):
    print (65536*(256*ord(read_buf1[i*4+1])+ord(read_buf1[i*4]))+(256*ord(read_buf1[i*4+3])+ord(read_buf1[i*4+2])))*10E-9

#print rand[0:64]
#print read_number1[0:64]