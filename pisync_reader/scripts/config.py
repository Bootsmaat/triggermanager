from genericpath import exists
import json
from os.path import dirname
from os.path import exists
from tkinter import W

FilePath = dirname (__file__)
CONFIG_PATH = '{}/config.json'.format (FilePath)

def save(file, data):
    with open(file, 'w') as wf:
        json.dump(data, wf, indent=4)
    
def load(file):
    data = None

    with open(file, 'r') as rf:
        data = json.load(rf)

    return data

# maybe better as a namedtuple
# object storing all settings

# responsible for reading/writing of config obj
class configurator():
    def __init__(self) -> None:

        if (not self.checkIfValidConfigExists()):
            self.c = self.createDefaultFile()
        else:
            self.c = self.getConfig()

    # TODO check for validness as well
    def checkIfValidConfigExists(self):
        return (exists(CONFIG_PATH))

    def createDefaultFile(self):
        # definition of config structure
        c = {
            "rpi_addr": "empty",
            "fiz_layout": "empty"
        }

        self.saveConfig(c)
        return c

    def getConfig(self):
        global CONFIG_PATH
        print (CONFIG_PATH)
        with open(CONFIG_PATH, 'r') as rf:
            c = json.load(rf)
            return c

    def saveConfig(self, config):
        print (CONFIG_PATH)
        with open(CONFIG_PATH, 'w') as wf:
            json.dump(config, wf, indent=4)

    def get_rpi_addr(self):
        return self.c['rpi_addr']
    
    def get_fiz_layout(self):
        return self.c['fiz_layout']
