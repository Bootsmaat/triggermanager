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

# function definitions
def add_trigger ():
    _id = len (trigger_list)
    trigger = trigger_t (
        id                  =  _id,
        name                = "trigger_%i" % _id,
        path                = "No file set",
        enabled             = 0,
        activation_frame    = 0
    )

    trigger_list.append (trigger)
