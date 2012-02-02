#Written by Michael Ramm, 2/3/10, Haeffner Lab
#to use, modify the FileName() and MakePrintLine for appropriate names/formats\
#the file name is set to be today's date, is changed when date switches
import time
import datetime

class Logger():
	def __init__(self):
		self.outputfile = self.FileName()
		self.FILE = open(self.outputfile,'a')
	def FileName(self):
		return str(datetime.date.today()) #opens log named after today's date
	def MakeLog(self, curTempArr,responseArr,valvesignalArr):
		self.UpdateFileName()
		self.line = self.MakePrintLine(curTempArr,responseArr,valvesignalArr)
		self.FILE.writelines(self.line)
		self.FILE.flush()
	def UpdateFileName(self):
		if(self.outputfile != self.FileName()): #if date swtiches, switch log file
			self.FILE.close()
			self.outputfile = self.FileName()
			self.FILE = open(self.outputfile,"w")
	def MakePrintLine(self, curTempArr,responseArr,valvesignalArr):
		lineout = []
		lineout.append(str(time.strftime("%H:%M:%S", time.localtime())) + ',')
		for i in range(len(curTempArr)):
			lineout.append(str("%5.2f" % curTempArr[i]) + ',');
		for j in range(len(responseArr)):
			lineout.append(str("%.0f" % responseArr[j]) + ',')
		for j in range(len(valvesignalArr)-1):
			lineout.append(str("%.0f" % valvesignalArr[j]) + ',')
		lineout.append(str("%.0f" % valvesignalArr[-1]))
		lineout.append("\n")
		return lineout
	def __del__(self):
		self.FILE.close()