import serial

serA = serial.Serial('COM12',timeout=1)
serB = serial.Serial('COM13',timeout=1)

def VoltageToFormat( volt ):
    if not  0 < volt < 4000: 
    	raise DCVSError( 'voltage not in range' )
    else:
    	num = round( ( volt / 4000.0 ) * 1023 )
    return int( num )

def MakeComString( num ):
    """
    takes a a number of converts it to a string understood by microcontroller, i.e 23 -> C0023!
    """
    comstring = 'C' + str( num ).zfill( 4 ) + '!'
    return comstring

def sV(red, blue):
	serA.write(MakeComString(VoltageToFormat(red)))
	serB.write(MakeComString(VoltageToFormat(blue)))