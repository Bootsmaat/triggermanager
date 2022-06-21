import socket, sys, threading, struct
from triggers import trigger_t
from time import sleep
from threading import Thread

# opcodes
OP_START    = 0x1
OP_STOP     = 0x2
OP_EXIT     = 0x3
OP_GET      = 0x4
OP_SET      = 0x5
OP_TSET     = 0x6
OP_TSTART   = 0x7
OP_TSTOP    = 0x8
OP_FD       = 0x9
OP_TCLEAR   = 0xa
OP_REFRESH  = 0xd

# trigger activation msg code
TR_A = 0xa

CONF_PORT   = 8081
BUF_SIZE    = 32
TIMEOUT     = 1

callbacks   = {}
sock        = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
cb_i        = 0
trigger_cb  = lambda a: print("trigger callback not bound")
error_cb    = lambda a: print("error callback not bound")

class Receiver (Thread):
    def __init__ (self, sock):
        Thread.__init__(self)
        self._stop      = 0
        self.events     = []
        self.sock       = sock

        # sock.settimeout (TIMEOUT)

        self.frame = 0
        self.focus = 0
        self.iris  = 0
        self.zoom  = 0
    
    def run (self):
        print ('Receiver: Starting...')
        global trigger_cb
        while (not self.stop == 1):
            if (not self.sock._closed):
                try:
                    data = self.sock.recv (1) # read packet length
                except BaseException as e:
                    error_cb (e)
            else:
                return

            if (len (data) == 0):
                break
            _len = data[0] - 1
            data = self.sock.recv (_len) # read rest of packet

            if (data[0] == TR_A): # trigger fire message
                tr_id = (data[1] << 8) | data[2]
                trigger_cb (tr_id)
            elif (data[0] == OP_GET):
                self.frame = (data[1] << 8) | data [2]
                self.focus = (data[3] << 8) | data [4]
                self.iris  = (data[5] << 8) | data [6]
                self.zoom  = (data[7] << 8) | data [8]
            else:
                opc = data[0]
                add = data[1:]
                e = (opc, add)
                self.events.append (e)
        print ('Receiver: Exiting...')

    def pop (self):
        if (len (self.events) != 0):
            return self.events.pop (len (self.events) - 1)
        else:
            return

    def stop (self):
        self._stop = 1

    # blocks until an event is added to list
    def wait_for_event (self):
        while (len (self.events) == 0):
            sleep (.1)
    
def register_tr_cb (func = None):
    global trigger_cb
    if (func):
        trigger_cb = func

def register_error_cb (func = None):
    global error_cb
    if (func):
        error_cb = func

thr = Receiver (sock)

def construct_packet (opc, **kwargs):
    packstr = ">B B "
    plen = 2
    vals = [plen, opc]

    if 'cat_set' in kwargs:
        slen = len(kwargs['cat_set'])
        plen += slen
        packstr += (str (slen) + "s ")
        vals.append (kwargs['cat_set'].encode())

    if 'tr_id' in kwargs:
        if not 'tr_afr' in kwargs:
            print ("conman: incomplete arguments. tr_afr missing")
            return
        plen += 4       
        packstr += "H H "
        vals.append (kwargs['tr_id'])
        vals.append (kwargs['tr_afr'])

    vals[0] = plen
    packer = struct.Struct (packstr)
    data = packer.pack (*vals)
    return data

def send_opc (opc):
    global thr
    print ('sending opc: %s' % str(opc))
    data = construct_packet (opc)
    try:
        sock.send (data)
    except BrokenPipeError as e:
        error_cb (e)
        thr.stop ()
    except ConnectionAbortedError as e:
        error_cb (e)
        thr.stop ()

def connect (addr):
    global sock, thr
    if (not sock._closed):
        sock.close ()

    sock = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect ((addr, CONF_PORT))
        thr = Receiver (sock)
    except OSError as e:
        print ('OSError raised')
        raise e
    else:
        send_opc (OP_FD)
        thr.start ()

# sends all triggers
def send_trigger (triggers):
    global sock, thr
    send_opc (OP_TCLEAR)
    for t in triggers:
        data = construct_packet (OP_TSET, tr_id=t.id, tr_afr=t.activation_frame)
        try:
            sock.send (data)
        except ConnectionAbortedError as e:
            error_cb (e)
            thr.stop ()
        sleep (.1)

def send_fiz_config (fiz_string):
    global sock, thr
    data = construct_packet (OP_SET, cat_set=fiz_string)
    try:
        sock.send (data)
    except ConnectionAbortedError as e:
        error_cb (e)
        thr.stop ()

def bind_id (id, callback = None):
    global callbacks
    if callback:
        callbacks[id] = callback

def on_fire_trigger (tr_id):
    global callbacks
    if tr_id in callbacks:
        print ('on_fire_trigger: trigger %i fired' % tr_id)
        callbacks[tr_id] (tr_id)
    else:
        print ('on_fire_trigger: key %i not bound to a callback' % tr_id)