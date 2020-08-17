import socket 
import struct

s = socket.socket (socket.AF_INET, socket.SOCK_STREAM)

s.connect (("PiTwo.local", 8081))

ip = input ('send\n>')

while not (ip == 'q'):
    vals = (2, int(ip))
    packer = struct.Struct ('B B')
    packed_data = packer.pack (*vals)
    print ('sending %s', packed_data)
    s.send(packed_data)
    ip = input ('send\n>')
