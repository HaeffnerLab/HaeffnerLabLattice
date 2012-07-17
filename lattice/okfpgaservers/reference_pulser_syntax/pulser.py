## import Opal Kelly library ##
import ok
import time
from struct import Struct

xem = ok.FrontPanel()

xem.OpenBySerial("")

xem.GetDeviceID()

#This line load a configuration file into the FPGA#

xem.ConfigureFPGA("/Users/thanedp/LabRAD/lattice/okfpgaservers/pulser/photon.bit")
#xem.OpenBySerial('12020002LF')
#xem.ConfigureFPGA('C:\Users\lattice\Hong_DB\Dropbox\WORK\VHDL\XEM6010\Photon_sd_ram_2012_05_10\photon\photon.bit')

# Each buf is 8 bit long. Each line in the pulser is 64 bit long. 8 bit is 1 bytes

#max number of pulses is 1024

#LSB/MSB

buf1 = "\x00\x00\x00\x00\x04\x00\x01\x00"
buf2 = "\x40\x00\x00\x00\x00\x00\x10\x00"
buf3 = "\x80\x00\x00\x00\x04\x00\x01\x00"
buf4 = "\xc0\x00\x00\x00\x00\x00\x10\x00"
buf5 = "\x40\x01\x00\x00\x04\x00\x01\x00"
buf6 = "\x80\x01\x00\x00\x08\x00\x00\x01"
buf7 = "\xc0\x04\x00\x00\x00\x00\x00\x00"
blank = "\x00\x00\x00\x00\x00\x00\x00\x00"

#### write to dds #####
#### first 2 is the frequency, last 2 is the amplitude ####
####  \xff\x00 in freq means (7 downto 0) is ff and (15 downto 8) is 00 ##
#### Each unit in freq is to increase by about 3 kHz #####

### Example of setting the first frequency of channel 0 ###

#xem.ActivateTriggerIn(0x40,4);time.sleep(0.1);xem.WriteToBlockPipeIn(0x81, 2, "\x00\x80\xff\xff");xem.WriteToBlockPipeIn(0x81, 2, "\x00\x90\xff\xff");xem.WriteToBlockPipeIn(0x81, 2, "\x00\xA0\xff\xff");xem.WriteToBlockPipeIn(0x81, 2, "\x00\xb0\xff\xff");xem.WriteToBlockPipeIn(0x81, 2, "\x00\xc0\xff\xff");xem.WriteToBlockPipeIn(0x81, 2, "\x00\x00");time.sleep(0.25);xem.ActivateTriggerIn(0x40,5);time.sleep(0.25);xem.ActivateTriggerIn(0x40,5);time.sleep(0.25);xem.ActivateTriggerIn(0x40,5);time.sleep(0.25);xem.ActivateTriggerIn(0x40,5);time.sleep(0.25);xem.ActivateTriggerIn(0x40,5);time.sleep(0.25);xem.ActivateTriggerIn(0x40,5)

xem.ActivateTriggerIn(0x40,4)

xem.SetWireInValue(0x04,0x00)
xem.UpdateWireIns()

time.sleep(0.25)

xem.WriteToBlockPipeIn(0x81, 2, "\x77\x77\x77\x77")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x00")


xem.WriteToBlockPipeIn(0x81, 2, "\x00\x20\xff\x80")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x30\xff\x40")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x00\x00\x00")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x50\xff\xff")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x60\xff\xff")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x70\xff\xff")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x80\xff\xff")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x00\x00\x00")

time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)




xem.ActivateTriggerIn(0x40,4)
xem.SetWireInValue(0x04,0x01)
xem.UpdateWireIns()
time.sleep(0.25)
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x10\x00\x1f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x20\x00\x1f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x30\x00\x1f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x40\x00\x1f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x50\x00\x1f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x60\x00\x1f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x70\x00\x1f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x80\x00\x1f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x00\x00\x00")

time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)




xem.ActivateTriggerIn(0x40,4)
xem.SetWireInValue(0x04,0x02)
xem.UpdateWireIns()
time.sleep(0.25)

xem.WriteToBlockPipeIn(0x81, 2, "\x00\x00\xff\xff")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x00")


xem.WriteToBlockPipeIn(0x81, 2, "\x00\x20\x00\x80")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x30\x00\x2f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x40\x00\x2f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x50\x00\x2f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x60\x00\x2f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x70\x00\x2f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x80\x00\x2f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x90\x00\x2f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x00\x00\x00")

time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)


xem.ActivateTriggerIn(0x40,4)
xem.SetWireInValue(0x04,0x03)
xem.UpdateWireIns()
time.sleep(0.25)
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x30\x00\x3f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x40\x00\x3f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x50\x00\x3f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x60\x00\x3f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x70\x00\x3f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x80\x00\x3f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x90\x00\x3f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\xa0\x00\x3f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x00\x00\x00")

time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)



xem.ActivateTriggerIn(0x40,4)
xem.SetWireInValue(0x04,0x04)
xem.UpdateWireIns()
time.sleep(0.25)
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x40\x00\x4f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x50\x00\x4f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x60\x00\x4f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x70\x00\x4f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x80\x00\x4f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x90\x00\x4f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\xa0\x00\x4f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\xb0\x00\x4f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x00\x00\x00")

time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)


xem.ActivateTriggerIn(0x40,4)
xem.SetWireInValue(0x04,0x05)
xem.UpdateWireIns()
time.sleep(0.25)
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x50\x00\x5f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x60\x00\x5f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x70\x00\x5f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x80\x00\x5f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x90\x00\x5f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\xa0\x00\x5f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\xb0\x00\x5f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\xc0\x00\x5f")
xem.WriteToBlockPipeIn(0x81, 2, "\x00\x00\x00\x00")

time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)
time.sleep(0.25)
xem.ActivateTriggerIn(0x40,5)



#### set dds channel ####

xem.SetWireInValue(0x04,0x00)
xem.UpdateWireIns()

### reset all dds ####
xem.ActivateTriggerIn(0x40,4)

### step dds to next ####
xem.ActivateTriggerIn(0x40,5)

### reset dds chips ###
xem.ActivateTriggerIn(0x40,6)

#### write to pulser ####

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
xem.WriteToBlockPipeIn(0x80, 2, blank)

### reset counter for the pulse sequence ###
xem.ActivateTriggerIn(0x40,0)

### reset pulser ram ###
xem.ActivateTriggerIn(0x40,1)

### reset normal pmt fifo ###
xem.ActivateTriggerIn(0x40,2)

### reset time_resolved pmt fifo ###
xem.ActivateTriggerIn(0x40,3)

###start one seq
xem.SetWireInValue(0x00,0x04,0x06)
xem.UpdateWireIns()

###stop one seq
xem.SetWireInValue(0x00,0x00,0x06)
xem.UpdateWireIns()

### start looped seq
xem.SetWireInValue(0x00,0x06,0x06)
xem.UpdateWireIns()

### stop looped seq
xem.SetWireInValue(0x00,0x02,0x06)
xem.UpdateWireIns()

### normal pmt mode ###
xem.SetWireInValue(0x00,0x00,0x01)
xem.UpdateWireIns()

### diff pmt mode ###
xem.SetWireInValue(0x00,0x01,0x01)
xem.UpdateWireIns()

### Request if seq is done ###
xem.SetWireInValue(0x00,0x00,0xf0)
xem.UpdateWireIns()
xem.UpdateWireOuts()
xem.GetWireOutValue(0x21)

### request number of photon counted ###

xem.UpdateWireOuts()
xem.GetWireOutValue(0x22)

#### request time resolved photon data ####

buf = "\x00"*2*2*320
xem.ReadFromBlockPipeOut(0xa0,2,buf)
a = Struct("H"*(len(buf)/2))
Struct.unpack(a,buf)

#### request how many sequnce done ####
xem.SetWireInValue(0x00,0x20,0xf0)
xem.UpdateWireIns()
xem.UpdateWireOuts()
xem.GetWireOutValue(0x21)

#### get normal pmt count ####
buf = "\x00"*2*2*32
xem.ReadFromBlockPipeOut(0xa1,2,buf)
a = Struct("H"*(len(buf)/2))
Struct.unpack(a,buf)

#### set normal pmt count period ###
xem.SetWireInValue(0x01,0x0064)
xem.UpdateWireIns()

#### request how many data in normal pmt ####
xem.SetWireInValue(0x00,0x40,0xf0)
xem.UpdateWireIns()
xem.UpdateWireOuts()
xem.GetWireOutValue(0x21)

### set how many loops to do ###
### 0 is infinite ####
xem.SetWireInValue(0x05,0x0a)
xem.UpdateWireIns()

#### logic out overwrite ####
### channel 0 ####
### Pulser by pass ###
xem.SetWireInValue(0x02,0x00,0x01)
xem.SetWireInValue(0x03,0x00,0x01)
xem.UpdateWireIns()

### Pulser by pass inverted ###
xem.SetWireInValue(0x02,0x00,0x01)
xem.SetWireInValue(0x03,0x01,0x01)
xem.UpdateWireIns()

### Manual on ###
xem.SetWireInValue(0x02,0x01,0x01)
xem.SetWireInValue(0x03,0x01,0x01)
xem.UpdateWireIns()

### Manual off ###
xem.SetWireInValue(0x02,0x01,0x01)
xem.SetWireInValue(0x03,0x00,0x01)
xem.UpdateWireIns()

### channel 1 ####
### Pulser by pass ###
xem.SetWireInValue(0x02,0x00,0x02)
xem.SetWireInValue(0x03,0x00,0x02)
xem.UpdateWireIns()

### Pulser by pass inverted ###
xem.SetWireInValue(0x02,0x00,0x02)
xem.SetWireInValue(0x03,0x02,0x02)
xem.UpdateWireIns()

### Manual on ###
xem.SetWireInValue(0x02,0x02,0x02)
xem.SetWireInValue(0x03,0x02,0x02)
xem.UpdateWireIns()

### Manual off ###
xem.SetWireInValue(0x02,0x02,0x02)
xem.SetWireInValue(0x03,0x00,0x02)
xem.UpdateWireIns()

