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
import time
from os.path import dirname
from os.path import basename
from os.path import exists
from os.path import join as pathjoin
from pprint import pprint

import configparser

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
import pisync_reader_module
importlib.reload (pisync_reader_module)


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


class pisync_reader_window (pisync_reader_UI_form, pisync_reader_UI_base):
    """
    Mainwindow GUI for KUKA live robot reader.
    """
    
    def __init__ (self, controller, parent=None):
        # Basic setup
        super (pisync_reader_window, self).__init__(parent)
        self.debug = False
        self.controller = controller
        self.current_tab = 0
        # Setup the ui window
        self.setupUi (self)
        self.connectButton.clicked.connect(self.__connect)
        self.activateRead.clicked.connect(self.activate_continues_read_update)
        self.activateRead.setChecked (False)
        self.hostField.editingFinished.connect(self.__validatehostdata)
        #self.writegroup = self.Modes.widget(1).children()[0]
        #self.OvOverride_slider = SliderSet_Widget (controller._set_BM_OV_PRO, parent=self.writegroup, description="KRC Velocity override", unit="%", scale=1, value=controller._get_BM_OV_PRO (), value_min=1, value_max=25, x=7, y=82)
        ## The select mimic robot menu
        #self.mimicRobotsComboBox.activated.connect (self.select_robot)
        #self.robotIKHandleMenu.activated.connect (self.__select_ik_handle)
        ## Register callbacks for events in maya
        #self.scene_changed_job = cmds.scriptJob(event=['PostSceneRead', self.__scene_changed], killWithScene=True)
        #self.snapIkToFkButton.clicked.connect (self.__snap_ik_to_fk)
        ## Hookup the ui elements to actions
        #self.sampleReadButton.clicked.connect(self.__read)
        #self.Modes.currentChanged.connect (self.switch_tab)
        #self.enable_disable_tabs (False)
        #self.clear_MemoryR2AButton.clicked.connect (self.__clear_memory_r2a)
        #self.clear_MemoryR2AButton.setEnabled (False)
        #self.activateWrite.clicked.connect(self.__activate_live_position)
        #self.sampleWriteButton.clicked.connect(self.__write)
        #self.sampleWriteButton.setEnabled (False)
        #self.activateTCPControl.clicked.connect(self.__activate_tcp_control)
        #self.activateTCPControl.setEnabled (False)
        #self.newMotionpathButton.clicked.connect(self.__new_motionpath)
        #self.motionpathComboBox.activated.connect (self.__edit_motion_path)
        #self.setconnectionstatus ("Connect", UI_RED_GRADE, False)
        #self.portField.editingFinished.connect(self.__validateportdata)
        #self.emilyFileListBox.activated.connect (self.__select_emily_file)
        #self.uploadEmilyFileButton.clicked.connect (self.__upload_emily_file)
        #self.load_EmilyButton.clicked.connect (self.__load_emily)
        #self.to_startEmilyButton.clicked.connect (self.__to_start_emily)
        #self.run_EmilyButton.clicked.connect (self.__run_emily)
        #self.unload_EmilyButton.clicked.connect (self.__unload_emily)
        #self.label_Ready2AnimateStatus.setText ('Ready2Animate Status')
        #self.emilyFileNameInput.editingFinished.connect (self.__set_emily_filename)
        #self.frame.hide ()
        #self.uploadProgressBar.hide ()
        #self.Modes.setCurrentIndex (0)
        #self.switch_tab (0)

    def __connect (self):
        """
        """
        pass


    def activate_continues_read_update (self):
        """
        """
        pass


    def __validatehostdata (self):
        """
        """
        pass

     
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
        self.mainwindow = pisync_reader_window (self, maya_window_pointer)


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
    #OpenMayaUI.MQtCore
    if exists(Geometry):
        settings_obj = QSettings(Geometry, QSettings.IniFormat)
        live_connection_gui.mainwindow.restoreGeometry(settings_obj.value("windowGeometry"))

    print ("default: {}".format (default))
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
    #import mimic_utils
    import sys
    sys.dont_write_bytecode = True  # don't write PYCs

    # Build the UI itself
    start_ui ()

