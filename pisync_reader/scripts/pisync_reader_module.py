# -*- coding: utf-8 -*-
# 
# Copyright (C) Bootsmaat and/or its licensors
# All Rights Reserved
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
#
# Written by Paul Boots <bootsch@acm.org>
#

# Import python lib
from pickle import FRAME
import time
from os.path import dirname
from os.path import basename
from os.path import exists
from os.path import join as pathjoin
from pprint import pprint
from time import sleep

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator

import configparser

# Import triggermanager related items
import conman
from config import *
from fizwatcher import fiz_watcher
import fizprotocol as fp

# Import maya related python libs
from maya import mel, cmds, OpenMayaUI
try:
    import pymel.core as pm
    
    MAYA_IS_RUNNING = True
except ImportError:  # Maya is not running
    pm = None
    MAYA_IS_RUNNING = False

import importlib

import mimic_utils
import maya.OpenMaya as OpenMaya

# Import my related libs
from init_ui import *

# Initialize TriggerManager related items
cm = conman.conman()
cf = configurator()
trigger_loop_enabled = False
cb_i = 0

# Global variables
debug = True

FilePath = dirname (__file__)
Geometry = pathjoin (FilePath, ".geometry")

pisync_reader_UI_form, pisync_reader_UI_base = loadUiType ('{}/pisync_reader.ui'.format (FilePath))

WINDOW_TITLE = "PiSync Reader"
global PSR
PSR = None

# Stylesheet definitions used to color the buttons.
UI_RED_GRADE = "background-color: qlineargradient(spread:reflect, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(133, 10, 10, 255), stop:0.1 rgba(192, 30, 30, 255), stop:0.3 rgba(225, 50, 50, 255), stop:0.49 rgba(240, 75, 75, 255), stop:0.51 rgba(240, 75, 75, 255), stop:0.7 rgba(225, 50, 50, 255), stop:0.9 rgba(192, 30, 30, 255), stop:1 rgba(133, 10, 10, 255));color: rgb(10, 10, 10);"
UI_GREEN_GRADE = "background-color: qlineargradient(spread:reflect, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(10, 133, 10, 255), stop:0.1 rgba(30, 192, 30, 255), stop:0.3 rgba(50, 225, 50, 255), stop:0.49 rgba(75, 240, 75, 255), stop:0.51 rgba(75, 240, 75, 255), stop:0.7 rgba(50, 225, 50, 255), stop:0.9 rgba(30, 192, 30, 255), stop:1 rgba(10, 133, 10, 255));color: rgb(10, 10, 10);"
UI_YELLOW_GRADE = "background-color: qlineargradient(spread:reflect, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(133, 133, 10, 255), stop:0.1 rgba(192, 192, 30, 255), stop:0.3 rgba(225, 225, 50, 255), stop:0.49 rgba(240, 240, 75, 255), stop:0.51 rgba(240, 240, 75, 255), stop:0.7 rgba(225, 225, 50, 255), stop:0.9 rgba(192, 192, 30, 255), stop:1 rgba(133, 133, 10, 255));color: rgb(10, 10, 10);"
UI_GRAY_GRADE = "background-color: qlineargradient(spread:reflect, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(103, 103, 103, 255), stop:0.1 rgba(182, 182, 182, 255), stop:0.3 rgba(215, 215, 215, 255), stop:0.49 rgba(235, 235, 235, 255), stop:0.51 rgba(235, 235, 235, 255), stop:0.7 rgba(215, 215, 215, 255), stop:0.9 rgba(182, 182, 182, 255), stop:1 rgba(103, 103, 103, 255));color: rgb(10, 10, 10);"
UI_BLACK_GRADE = "background-color: qlineargradient(spread:reflect, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(30, 30, 30, 255), stop:0.1 rgba(68, 68, 68, 255), stop:0.3 rgba(90, 90, 90, 255), stop:0.49 rgba(115, 115, 115, 255), stop:0.51 rgba(115, 115, 115, 255), stop:0.7 rgba(90, 90, 90, 255), stop:0.9 rgba(68, 68, 68, 255), stop:1 rgba(30, 30, 30, 255));color: rgb(10, 10, 10);"


def set_current_time (value):
    cmds.currentTime (value)

class pisync_value_box ():
    """
    Class used to set values in the gui from the thread that connects and tracks pisync.
    """
    def __init__(self, gui_element, cmd=None):
        self.gui_box = gui_element
        self.value = -2
        self.cmd = cmd

    def set (self, value):
        self.value = value
        print ("Type of value: {} with value {}".format (type(value), value))
        cmds.evalDeferred (self.set_value)
        
    def set_value (self):
        self.gui_box.setText (str (self.value))
        if self.cmd:
            self.cmd (self.value)


FRAMEBOX = None
FOCUSBOX = None
IRISBOX  = None
ZOOMBOX  = None

class pisync_reader_window (pisync_reader_UI_form, pisync_reader_UI_base):
    """
    Mainwindow GUI for KUKA live robot reader.
    """
    
    def __init__ (self, controller, parent=None):
        global FRAMEBOX
        global FOCUSBOX
        global IRISBOX
        global ZOOMBOX
        # Basic setup
        super (pisync_reader_window, self).__init__(parent)
        self.debug = False
        self.controller = controller
        self.current_tab = 0
        # Setup the ui window
        self.setupUi (self)
        self.activateRead.setEnabled (False)
        self.connectButton.clicked.connect(self.controller.connect)
        self.activateRead.clicked.connect(self.controller.toggle_trigger_loop)
        self.activateRead.setChecked (False)
        self.hostField.editingFinished.connect(self.validatehostdata)
        self.frameValue.setText ("-1")
        self.focusValue.setText ("-1")

        self.ip_range = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        self.reg_ex_pattern = "^" + self.ip_range + "(\\." + self.ip_range + ")" + "(\\." + self.ip_range + ")" + "(\\." + self.ip_range + ")$"
        self.reg_ex = QRegExp(self.reg_ex_pattern)
        self.input_validator = QRegExpValidator(self.reg_ex, self.hostField)
        self.hostField.setValidator(self.input_validator)

        FRAMEBOX = pisync_value_box (self.frameValue, set_current_time)
        FOCUSBOX = pisync_value_box (self.focusValue)
        IRISBOX  = pisync_value_box (self.irisValue)
        ZOOMBOX  = pisync_value_box (self.zoomValue)


    def activate_continues_read_update (self):
        """
        """
        pass


    def validatehostdata (self):
        """
        """
        # Must be valid ip or hostname
        host = self.hostField.text()
        self.controller.set_ip_address (host)
        #print ('Host address: {}'.format (host))
        self.setFocus()
     


class pisync_reader_controller ():
    """
    Controller for the pisync connection
    """
    __version__ = "0.0.9"
    def __init__ (self, maya_window_pointer):
        """
        Initialize the live robot connection.
        Default ini file will be used when no other parameters are passed.
        """
        global cf

        self.ip_address = cf.c['rpi_addr']
        self.mainwindow = pisync_reader_window (self, maya_window_pointer)
        self.mainwindow.hostField.setText (self.ip_address)

    def set_ip_address (self, ip_address):
        """
        Set ip address on user entry in host field.
        """
        global cf

        if ip_address != self.ip_address:
            self.ip_address = ip_address
            cf.c['rpi_addr'] = self.ip_address
            cf.saveConfig (cf.c)
            self.fiz_watcher = None


    def connect (self):
        """
        Connect to PiSync on the give ip address.
        """
        global FRAMEBOX
        global FOCUSBOX
        global IRISBOX
        global ZOOMBOX

        if self.mainwindow.connectButton.text () == "Connect":
            # Connect to pisync
            print ("Connect to {}".format (self.mainwindow.hostField.text()))
            global cm

            try:
                cm = conman.conman(
                    generic_cb= lambda a: print(f'{a} received'),
                    conn_error_cb= lambda a: self.on_connection_error_event(a, "what do we want with this"),
                    status_update_cb= lambda a: self.on_status_update(a)
                )

                cm.connect(self.ip_address)

                sleep(.1)
                self.fiz_watcher = fiz_watcher(self.ip_address, FOCUSBOX, IRISBOX, ZOOMBOX, FRAMEBOX)
                self.fiz_watcher.start()

                cm.send_fiz_config(cf.c['fiz_layout'])

            except BaseException as e:
                print ("Exception {}".format (e))
                self.mainwindow.connectButton.setChecked (False)
                #raise e
            else:
                print ("Connected")
                self.mainwindow.connectButton.setText ("Connected")
                self.mainwindow.activateRead.setEnabled (True)
        else:
            # Disconnect
            print ("Disconnect from pisync")
            cm.cleanup()
            self.mainwindow.connectButton.setText ("Connect")
            self.mainwindow.activateRead.setEnabled (False)

    def toggle_trigger_loop(self, widget = None):
        global trigger_loop_enabled, cb_i

        if trigger_loop_enabled:
            cm.send_signal.clear()
            cm.send_opc(fp.OP_STOP)
            self.mainwindow.connectButton.setEnabled (True)
        else:
            cb_i = 0 # make sure we start with the first trigger
            cm.send_signal.clear()
            cm.send_opc(fp.OP_START)
            self.mainwindow.connectButton.setEnabled (False)
    
        trigger_loop_enabled = not trigger_loop_enabled

    def on_connection_error_event (self, error, connection_widget):
        print ("Connection widget {} with error {}".format (connection_widget, error))
        #connection_widget['image'] = img_icon_grey

    def on_status_update(self, status):
        print ("Connection status update {}".format (status))
        #btn_refresh['bg'] = 'green' if status[0] else 'red'


def start_ui ():
    """
    Start the UI in maya.
    """
    
    maya_window_pointer = wrapinstance ((OpenMayaUI.MQtUtil.mainWindow ()))

    window_name         = '{} v{}'.format (WINDOW_TITLE, pisync_reader_controller.__version__)
    dock_control        = '{} v{} Dock'.format (WINDOW_TITLE, pisync_reader_controller.__version__)
    
    if cmds.window (window_name, exists=True):
        cmds.deleteUI (window_name)
    
    if cmds.window (window_name, exists=True):
        cmds.deleteUI (dock_control)
    
    live_connection_gui = pisync_reader_controller (maya_window_pointer)
    live_connection_gui.mainwindow.setWindowTitle (window_name)

    # Restore window's previous geometry from file
    if exists(Geometry):
        settings_obj = QSettings(Geometry, QSettings.IniFormat)
        live_connection_gui.mainwindow.restoreGeometry(settings_obj.value("windowGeometry"))

    global PSR
    PSR = live_connection_gui
    live_connection_gui.mainwindow.show()


def run ():
    """
    Run the Live robot connetion module.
    Do initial checks and imports and create the GUI.
    """
    print ("Loading Live PiSync connection GUI; {}".format (__file__))
    # Perform preliminary checks
    import sys
    sys.dont_write_bytecode = True  # don't write PYCs

    # Build the UI itself
    start_ui ()

