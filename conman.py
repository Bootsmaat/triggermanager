import socket, sys, threading, struct
from triggers import trigger_t

#define opcodes here
OP_START    = 0x1
OP_STOP     = 0x2
OP_EXIT     = 0x3
OP_GET      = 0x4
OP_SET      = 0x5
OP_TSET     = 0x6
OP_TSTART   = 0x7
OP_TSTOP    = 0x8

callbacks   = []
conf_sock   = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
tr_sock     = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
conf_sock.settimeout    (100)
tr_sock.settimeout      (100)

def trigger_loop ():
    global callbacks
    global conf_sock

    # sort list based on activation frame
    callbacks.sort (key=lambda t: t[1])
    print (callbacks)

    i = 0
    while (i < len (callbacks)):
        id, a_fr, func = callbacks[i]

        if thr_looping:
            data = conf_sock.recv (BUF_SIZE)
            print ('executing t:%i on %i' % (id, a_fr))
            func    ()
            print   (data)
            i = i+1
        

# globals
CONF_PORT   = 8081
TR_PORT     = 8082
BUF_SIZE    = 32
thr_loop    = threading.Thread (name='thr_loop', target=trigger_loop)
thr_looping = 0

def construct_packet (opc, **kwargs):
    packstr = "B B "
    plen = 2
    vals = (plen, opc)

    if 'cat_set' in kwargs:
        slen = len(kwargs['cat_set'])
        plen += slen
        packstr += slen + "s "
        vals = (*vals, kwargs['cat_set'])

    if 'tr_id' in kwargs:
        if not 'tr_afr' in kwargs:
            print ("conman: incomplete arguments. tr_afr missing")
            return
        plen += 4       
        packstr += "H H "
        vals = (*vals, kwargs['tr_id'], kwargs['tr_afr'])

    vals[0] = plen
    packer = struct.Struct (packstr)
    return packer.pack (*vals)

#function definitions
def connect (addr):
    global conf_sock
    conf_sock.connect   ((addr, CONF_PORT))
    thr_loop.start ()

def send_trigger (triggers):
    global conf_sock
    status = -1
    for t in triggers:
        cmd = "TRSET:%02i:%i" % (t.id, t.activation_frame)
        conf_sock.send (cmd.encode ())

        data    = conf_sock.recv (BUF_SIZE)
        status  = str (data)
    return status

def bind_id (id, activation_frame, callback = None):
    global callbacks
    if callback:
        callbacks.append ((id, activation_frame, callback))

def thr_start ():
    global thr_looping, thr_loop
    thr_looping = 1

def thr_stop ():
    global thr_looping, thr_loop
    thr_looping = 0

        
