from socket import *
import time
 
HOST = 'landau.physics.berkeley.edu'
PORT = 8889
ADDR = (HOST,PORT)
BUFSIZE = 1024
 
cli = socket(AF_INET,SOCK_STREAM)
cli.connect((ADDR))
print 'connected'

buffer = chr(0x00)
buffer += chr(0x03)
buffer += 'B.0'

cli.send(buffer)
print 'buffer sent'
print buffer

time.sleep(2)
print 'receiving'
data = cli.recv(BUFSIZE)
print data
cli.close()