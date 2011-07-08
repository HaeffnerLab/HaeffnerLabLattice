import os
import shelve
import socket
#class for storing information about each script
class script:
    scriptname = ''
    filemodtime = ''
    varlist = [];

class PaulBoxServer():
    def __init__( self ):
        self.dbfile = 'scriptinfo.db'
        self.directory = '/home/micramm/Desktop/sequencer2/PulseSequences/protected/'
        port_of_server = 8880
        #connect socket to sequencer2 server
        self.sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        local_ip = '192.168.169.69'
        #local_ip = socket.gethostbyname(socket.gethostname())# find ip of localhost if running on same machine as python server
        self.sock.connect( ( local_ip, port_of_server ) )
        #opens a new database TODO open existing one, then replace keys if file modified
        self.db = shelve.open( self.dbfile, 'c' )
        self.loadscripts( self.directory, self.db )

    #returns list of available scripts
    def availableScripts( self ):
        return self.db.keys()

    def variableList( self, scriptname ):
        return self.db[scriptname].varlist

    #send scriptname with input parameters given up inputlist
    #inputlist is in the format [[var_name,var_type,var_value],..[]]
    def sendcommand( self, scriptname, inputlist ):
        print 'Sending command to sequencer2 server:'
        command = 'NAME,' + scriptname
        for var in inputlist:
            command += ';' + var[1] + ',' + var[0] + ',' + var[2]
        print command
        self.sock.sendall( command )
        data = self.sock.recv( 4 * 8192 )
        print data
        data = self.sock.recv( 4 * 8192 )
        print data

    def loadscripts( self, directory, db ):
        #print len(self.db.keys())
        for filename in os.listdir( directory ):
            path = directory + filename
            try:
                fobj = open( path )
                sequence_string = fobj.read()
                fobj.close()
                modtime = os.stat( path ).st_mtime
            except:
                raise RuntimeError( "Error while loading sequence:" + str( filename ) )
            newscript = script()
            newscript.scriptname = filename
            newscript.filemodtime = modtime
            newscript.varlist = self.parse_sequence( sequence_string )
            db[filename] = newscript;
    #parses through the file and returrns array of available variables in the form
    #[[var1_name,var1_type,default_val,min(opt),max(opt)],[..],...]
    def parse_sequence( self, sequence_string ):
        varlist = []
        for line in sequence_string.splitlines():
            setvarindex = line.find( "self.set_variable(" )
            if setvarindex > -1: #if line contains 'self.set_variable'
                poundindex = line.find( "#" )
                if poundindex == -1 or poundindex > setvarindex: #if the line is not commented out ('#' after 'self.setvariable')
                    end = line.find( ")" )
                    relevantline = line[setvarindex + len( "self.set_variable(" ):end]
                    values = relevantline.split( ',' )
                    var_type = str( values[0].replace( '"', '' ) ) #gets rid of quotes by replacing them with nothing
                    var_name = str( values[1].replace( '"', '' ) )
                    default_val = str( values[2] )
                    if len( values ) == 5:
                        min_val = str( values[3] )
                        max_val = str( values[4] )
                    else:
                        min_val = ''
                        max_val = ''
                    varlist.append( [var_name, var_type, default_val, min_val, max_val] )
        return varlist

    def __del__( self ):
        self.db.close()
        self.sock.close()
