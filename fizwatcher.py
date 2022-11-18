import socket, struct
from threading import Thread
from pisync_protocol import OP_GET
from tkinter import StringVar
from conman import construct_packet, send_opc, CONF_PORT
from time import sleep

class fiz_watcher (Thread):
    def __init__ (self, address, string_f, string_i, string_z, string_frame):
        Thread.__init__ (self)
        self.string_f = string_f
        self.string_i = string_i
        self.string_z = string_z
        self.string_frame = string_frame
        self.stop = False

        self.socket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.connect ((address, CONF_PORT))
        except OSError as e:
            print ('fiz_watcher: failed to connect to socket')
            raise e
        
        self.socket.recv (3) # read first 3 status bytes
        data = construct_packet (OP_GET)
        self.socket.send (data)
    
    def run (self):
        print ('fiz_watcher: Starting...')
        while (not self.stop):
            data = None
            try:
                data = self.socket.recv (1)
            except BaseException as e:
                print ('fiz_watcher: error on recv. e = %s' % e)
                stop = True
            
            data_length = data[0] - 1
            data = self.socket.recv (data_length)

            if (data[0] != OP_GET):
                print ('fiz_watcher: received different opcode %s' % data[0])
            
            if (len (data) > 2):
                frame = (data[1] << 8) | data [2]
                focus = (data[3] << 8) | data [4]
                iris  = (data[5] << 8) | data [6]
                zoom  = (data[7] << 8) | data [8]

                print ('FIZ: %i | %i | %i' % (focus, iris, zoom))

                self.string_frame.set(frame)
                self.string_f.set(("%i (%.02f)" % (focus, self.mapValue(focus))))
                self.string_i.set(("%i (%.02f)" % (iris, self.mapValue(iris))))
                self.string_z.set(("%i (%.02f)" % (zoom, self.mapValue(zoom))))

        print ('fiz_watcher: Exiting...')

    def mapValue(self, val):
        return (1.0 / 65535.0 * val)

    def stop (self):
        stop = True

