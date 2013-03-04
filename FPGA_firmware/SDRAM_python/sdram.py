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
#xem.WriteToBlockPipeIn(0x80, 2, buf7)
#xem.WriteToBlockPipeIn(0x80, 2, buf8)
#xem.WriteToBlockPipeIn(0x80, 2, buf9)
#xem.WriteToBlockPipeIn(0x80, 2, buf10)
#xem.WriteToBlockPipeIn(0x80, 2, buf11)
#xem.WriteToBlockPipeIn(0x80, 2, buf12)
#xem.WriteToBlockPipeIn(0x80, 2, buf13)
#xem.WriteToBlockPipeIn(0x80, 2, buf14)
#xem.WriteToBlockPipeIn(0x80, 2, buf15)
#xem.WriteToBlockPipeIn(0x80, 2, buf16)
#xem.WriteToBlockPipeIn(0x80, 2, buf17)
xem.WriteToBlockPipeIn(0x80, 2, blank)

###line trigger on###

xem.SetWireInValue(0x00,0x00,0x08)

###start one seq
xem.SetWireInValue(0x05,10) ## run 3 sequences
xem.SetWireInValue(0x00,0x06,0x06)
xem.UpdateWireIns()

print "begin reading1..."

time.sleep(5)

xem.SetWireInValue(0x07,0x0000) #stop SDRAM operation
xem.SetWireInValue(0x00,0x80,0xf0) #read number of readout count
xem.UpdateWireIns()
xem.UpdateWireOuts()

number_of_photon = ((xem.GetWireOutValue(0x23)*65536 + xem.GetWireOutValue(0x22))+8)/4

#print "Readout count is ",xem.GetWireOutValue(0x21)

if number_of_photon == 570425336:
    print "SDRAM is full"
    number_of_photon = number_of_photon - 536870912

print "Number of photon is ", number_of_photon

xem.SetWireInValue(0x07,0x0004)
xem.UpdateWireIns()
xem.SetWireInValue(0x07,0x0000)
xem.UpdateWireIns()
xem.SetWireInValue(0x07,0x0001)
xem.UpdateWireIns()


if number_of_photon > 4194302:
    number_of_photon = 4194302
    
write_size = number_of_photon

read_buf1 = write_size*4*'\x00'
print "start reading"
#xem.ReadFromBlockPipeOut(0xA0,block_size,read_buf1)
xem.ReadFromPipeOut(0xA0,read_buf1)
print "done reading"

xem.UpdateWireOuts()

print "time tag is"
for i in np.arange(write_size-16,write_size):
#for i in np.arange(0,write_size):
    print (65536*(256*ord(read_buf1[i*4+1])+ord(read_buf1[i*4]))+(256*ord(read_buf1[i*4+3])+ord(read_buf1[i*4+2])))*10E-9

#print rand[0:64]
#print read_number1[0:64]


xem.UpdateWireOuts()
readout = xem.GetWireOutValue(0x21)/2

print "Readout count is ", readout

buf = readout*4*"\x00"
xem.ReadFromBlockPipeOut(0xA2,2,buf)

for i in np.arange(0,readout):
#for i in np.arange(0,write_size):
    print (65536*(256*ord(buf[i*4+1])+ord(buf[i*4]))+(256*ord(buf[i*4+3])+ord(buf[i*4+2])))

xem.ActivateTriggerIn(0x40,6)
xem.SetWireInValue(0x04,0x00)
xem.UpdateWireIns()
 
xem.ActivateTriggerIn(0x40,4)


####phase: \x\xMSB amplitude: \x\x freq: \xLSB\xlSB\xmSB\xMSB
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x00\x00\x80\x00\x00\x00\x40")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x00\x00\x80\x00\x00\x00\x41")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x00\x00\x80\x00\x00\x00\x42")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x00\x00\x80\x00\x00\x00\x43")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x00\x00\x80\x00\x00\x00\x44")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x00\x00\x80\x00\x00\x00\x45")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x00\x00\x80\x00\x00\x00\x46")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x00\x00\x80\x00\x00\x00\x47")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x00")

time.sleep(1)
xem.ActivateTriggerIn(0x40,5)
time.sleep(1)
xem.ActivateTriggerIn(0x40,5)
time.sleep(1)
xem.ActivateTriggerIn(0x40,5)
time.sleep(1)
xem.ActivateTriggerIn(0x40,5)
time.sleep(1)
xem.ActivateTriggerIn(0x40,5)
time.sleep(1)
xem.ActivateTriggerIn(0x40,5)
time.sleep(1)
xem.ActivateTriggerIn(0x40,5)
time.sleep(1)
xem.ActivateTriggerIn(0x40,5)
time.sleep(1)
xem.ActivateTriggerIn(0x40,4)

