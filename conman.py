import socket, sys
from triggers import trigger_t

# globals
CONF_PORT   = 8081
TR_PORT     = 8082
BUF_SIZE    = 32
conf_sock   = None
tr_sock     = None
callbacks   = []

#function definitions
def connect (addr):
    global conf_sock
    conf_sock = socket.socket    (socket.AF_INET, socket.SOCK_STREAM)
    conf_sock.connect            ((addr, TR_PORT))

    tr_sock = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
    tr_sock.connect         ((addr, TR_PORT))

def send_trigger (triggers):
    global conf_sock
    status = -1
    for t in triggers:
        cmd = "TRSET:%02i:%i" % (t.id, t.activation_frame)
        conf_sock.sendall (cmd.encode ())

        data    = conf_sock.recv (BUF_SIZE)
        status  = str (data)
    return status

def bind_id (id, activation_frame, callback = None):
    global callbacks
    if callback:
        callbacks.append ((id, activation_frame, callback))

def trigger_loop ():
    global callbacks
    global tr_sock

    # sort list based on activation frame
    callbacks.sort (key=lambda t: t[1])
    print (callbacks)

    i = 0
    while (i < len (callbacks)):
        func = callbacks[i][2]
        data = tr_sock.recv (BUF_SIZE)
        func    ()
        print   (data)
        i = i+1
        
