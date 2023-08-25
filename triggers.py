from collections import namedtuple

# define list tuple
trigger_t = namedtuple (
    "trigger_t",
    [
        'id',
        'name',
        'path',
        'enabled',
        'activation_frame',
        'trigger_character'
    ]
)

# globals
trigger_list = []
id_counter   = 0

def get_highest_id (triggers):
    if (len(triggers) == 0):
        return 0

    ids = [tr.id for tr in triggers]
    return max(ids)

def add_trigger ():
    global id_counter

    hi = get_highest_id(trigger_list) + 1

    trigger = trigger_t (
        id                  =  hi,
        name                = "trigger_%i" % hi,
        path                = "No file set",
        enabled             = 1,
        activation_frame    = 0,
        trigger_character = 'h'
    )

    trigger_list.append(trigger)

def add_serial_trigger ():
    global id_counter

    hi = get_highest_id (trigger_list) + 1

    trigger = trigger_t (
        id                  =  hi,
        name                = "trigger_%i" % hi,
        path                = "No file set",
        enabled             = 1,
        activation_frame    = 0,
        trigger_character = 'h'
    )

    trigger_list.append (trigger)

def remove_trigger (id):
    global trigger_list

    for tr in trigger_list:
        if (tr.id == id):
            print ('triggers: removing trigger %i' % tr.id)
            trigger_list.remove (tr)
            return
        pass

def find_trigger_index (id):
    for i in range (0, len (trigger_list)):
        if (trigger_list[i].id == id):
            return i
        if (i == len (trigger_list)):
            return -1

def get_trigger_by_id (id):
    global trigger_list
    trs = [t for t in trigger_list if (id == t.id)]
    return trs[0] if (len (trs) == 1) else None

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
    if 'trigger_character' in kwargs:
        trigger_list[i] = trigger_list[i]._replace (trigger_character=kwargs['trigger_character'])

    print (trigger_list[i])