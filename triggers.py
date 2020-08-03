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

def find_trigger_index (id):
    for i in range (0, len (trigger_list)):
        if (trigger_list[i].id == id):
            return i
        if (i == len (trigger_list)):
            return -1

def update_trigger (id, **kwargs):
    i = find_trigger_index (id)

    if 'name' in kwargs:
        trigger_list[i] = trigger_list[i]._replace (name=kwargs['name'])
    if 'path' in kwargs:
        trigger_list[i] = trigger_list[i]._replace (path=kwargs['path'])
    if 'enabled' in kwargs:
        trigger_list[i] = trigger_list[i]._replace (enabled=kwargs['enabled'])
    if 'activation_frame' in kwargs:
        trigger_list[i] = trigger_list[i]._replace (activation_frame=kwargs['activation_frame'])

    print (trigger_list[i])