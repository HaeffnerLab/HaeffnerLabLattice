import ok
import numpy as np
import array
import time

def _intToBuf(num):
    '''
    takes the integer representing the setting and returns the buffer string for dds programming
    '''
    #converts value to buffer string, i.e 128 -> \x00\x00\x00\x80
    a, b = num // 256**2, num % 256**2
    arr = array.array('B', [a % 256 ,a // 256, b % 256, b // 256])
    ans = arr.tostring()
    return ans

#    ans = 65536*(256*ord(buf[1])+ord(buf[0]))+(256*ord(buf[3])+ord(buf[2]))


xem = ok.FrontPanel()
xem.OpenBySerial("")
xem.GetDeviceID()
# print xem.ConfigureFPGA('C:\Users\lattice\Desktop\LabRAD\lattice\FPGA_firmware\SDRAM_python\ramtest.bit')
# print xem.ConfigureFPGA('C:\Program Files (x86)\Opal Kelly\FrontPanelUSB\API\ramtest.bit')
xem.ConfigureFPGA('ramtest.bit')

write_size = 65535

rand = np.random.random_integers(0,256**2-1,write_size) #each one is 16 bit
buf = ''.join([_intToBuf(num) for num in rand])

#reset FIFO on fpga
xem.SetWireInValue(0x00,0x0004)
xem.UpdateWireIns()
xem.SetWireInValue(0x00,0x0000)
xem.UpdateWireIns()

#begin write to memory
xem.SetWireInValue(0x00,0x0002)
xem.UpdateWireIns()
print "writing to mem..."
xem.WriteToPipeIn(0x80, buf)

xem.UpdateWireOuts()

print "done writing..."
print "begin reading1..."

xem.SetWireInValue(0x00,0x0004)
xem.UpdateWireIns()
xem.SetWireInValue(0x00,0x0000)
xem.UpdateWireIns()
xem.SetWireInValue(0x00,0x0001)
xem.UpdateWireIns()

read_buf1 = write_size*4*'\x00'

xem.ReadFromPipeOut(0xA0, read_buf1)
print "done reading1"


read_number1 = rand.copy()
for i in np.arange(0,len(rand)):
    read_number1[i] = 65536*(256*ord(read_buf1[i*4+1])+ord(read_buf1[i*4]))+(256*ord(read_buf1[i*4+3])+ord(read_buf1[i*4+2]))

time.sleep(1)
    
print "begin reading2..."

xem.SetWireInValue(0x00,0x0004)
xem.UpdateWireIns()
xem.SetWireInValue(0x00,0x0000)
xem.UpdateWireIns()
xem.SetWireInValue(0x00,0x0001)
xem.UpdateWireIns()

read_buf2 = write_size*4*'\x00'

xem.ReadFromPipeOut(0xA0, read_buf2)
print "done reading2"


read_number2 = rand.copy()
for i in np.arange(0,len(rand)):
    read_number2[i] = 65536*(256*ord(read_buf2[i*4+1])+ord(read_buf2[i*4]))+(256*ord(read_buf2[i*4+3])+ord(read_buf2[i*4+2]))

print rand[0:255]
print read_number1[0:255]
print read_number2[0:255]