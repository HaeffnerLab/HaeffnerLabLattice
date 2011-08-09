## import Opal Kelly library ##
import ok

xem = ok.FrontPanel()
xem.OpenBySerial("")
xem.GetDeviceID()

#This line load a configuration file into the FPGA#

xem.ConfigureFPGA("/Users/thanedp/Dropbox/WORK/VHDL/Spartan/BTstream/led.bit")

#This one is to set the phase-locked loop chip on board

pll = ok.PLL22150()
xem.GetEepromPLL22150Configuration(pll)

#The last number is basically the frequency of the counting.
#Sampling rate is 800/n in MHz where n is the last argument

pll.SetDiv1(pll.DivSrc_VCO,4)

#Update PLL
xem.SetPLL22150Configuration(pll)


from struct import Struct

#16776192 is the max number. Each block of \x00 gives you 40 ns.
#So max data chunk is equivalent to 671.1 ms.

buf = "\x00"*16776192


a = Struct("L"*(len(buf)/8))
#This line reset the memory on board to wait for the next pulse
xem.ActivateTriggerIn(0x40,0)
#This line execute the calling of the data from the FPGA. Timeout is 10 s.
xem.ReadFromBlockPipeOut(0xa0,1024,buf)

count = 0
photon=0
while (count<len(buf)):
	if (buf[count] != "\x00"):
		photon = photon+1
	count=count+1

photon