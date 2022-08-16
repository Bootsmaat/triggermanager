import struct

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

# port settings
CONF_PORT   = 8081
BUF_SIZE    = 32
TIMEOUT     = 1

def construct_packet(opc, **kwargs):
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