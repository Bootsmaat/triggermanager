from time import sleep
from threading import Thread
from conman import TR_A, OP_GET
from fizprotocol import OP_STATUS

# thread to receive 
class Receiver (Thread):
    def __init__ (
        self, 
        trigger_cb = None, 
        error_cb = None, 
        generic_cb = None,
        status_update_cb = None
        ):
        Thread.__init__(self)
        self._stop      = 0
        self.events     = []

        self.frame = 0
        self.focus = 0
        self.iris  = 0
        self.zoom  = 0
        self.old_data = None

        self.trigger_cb  = trigger_cb
        self.error_cb    = error_cb
        self.generic_event_cb = generic_cb
        self.status_update_cb = status_update_cb

    def setSocket(self, socket):
        self.sock = socket
    
    def run (self):
        print ('Receiver: Starting...')

        # read initial message
        initial_state = self.sock.recv(3)

        while (not self._stop):
            if (not self.sock._closed):
                try:
                    data = self.sock.recv (1) # read packet length
                except BaseException as e:
                    self.error_cb(e)
                    self.stop()
                    print ("Error on connection: {}".format(e))
                    break
                    #raise e
            else:
                return

            if (len (data) == 0):
                return

            _len = data[0] - 1
            data = self.sock.recv(_len) # read rest of packet

            if (data[0] == TR_A): # trigger fire message
                tr_id = (data[1] << 8) | data[2]
                self.trigger_cb(tr_id)

            elif (data[0] == OP_GET):
                self.frame = (data[1] << 8) | data [2]
                self.focus = (data[3] << 8) | data [4]
                self.iris  = (data[5] << 8) | data [6]
                self.zoom  = (data[7] << 8) | data [8]

            elif(data[0] == OP_STATUS):
                if (data == self.old_data):
                    break
                self.old_data = data[1:]
                self.status_update_cb(data[1:])

            else:
                opc = data[0]
                add = data[1:]
                e = (opc, add)
                try:
                    self.generic_event_cb(e)

                except BaseException as p:
                    print('no generic callback set')
                    print(p)
                    raise

                self.events.append(e)

        print ('Receiver: Exiting...')

    def pop(self):
        if (len (self.events) != 0):
            return self.events.pop (len (self.events) - 1)
        else:
            return

    def stop(self):
        self._stop = 1

    # blocks until an event is added to list
    def wait_for_event (self):
        while (len (self.events) == 0):
            sleep (.1)