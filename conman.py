import socket, sys
from triggers import trigger_t

# globals
CONF_PORT   = 8081
TR_PORT     = 8082
conf_sock   = None
tr_sock     = None

#function definitions
def connect (addr):
    global conf_sock
    conf_sock = socket.socket    (socket.AF_INET, socket.SOCK_STREAM)
    conf_sock.connect            ((addr, TR_PORT))

    tr_sock = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
    tr_sock.connect         ((addr, TR_PORT))

def send_trigger (triggers):
    for t in triggers:
        cmd = "TRSET:%02i:%i" % (t.id, t.activation_frame)
        conf_sock.sendall (cmd)
