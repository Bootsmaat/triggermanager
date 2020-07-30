from collections import namedtuple

# define list tuple
trigger_t = namedtuple (
    "trigger_t",
    [
        'id',
        'name',
        'path',
        'enabled',
        'activation_frame'
    ])

# globals
trigger_list = []
id_counter   = 0

# function definitions
def add_trigger ():
    global id_counter

    _id         = id_counter
    id_counter  = id_counter + 1

    trigger = trigger_t (
        id                  =  _id,
        name                = "trigger_%i" % _id,
        path                = "No file set",
        enabled             = 0,
        activation_frame    = 0
    )

    trigger_list.append (trigger)

def remove_trigger (id):
    for tr in trigger_list:
        if (tr.id == id):
            trigger_list.remove (tr)
            return
        pass