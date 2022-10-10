import pymel.core as pm
import importlib
import mimic_utils
import mimic_io
importlib.reload(mimic_utils)
importlib.reload(mimic_io)

def get_robot_selection():
    """
    Gets the selected robot
    Checks to make sure only a single robot is selected
    """
    
    robots = mimic_utils.get_robot_roots()
    if len(robots) != 1:
        pm.error('Select a single robot')
        
    robot = robots[0]
    
    return robot


def add_frame_as_output(robot):
    """
    Adds a digital output field to the robot for frame values
    Increments IO number and postproc ID based on previous IOs already added to the robot
    """
    
    io_numbers = []
    robots_ios = mimic_io.get_io_names(robot)
    
    target_ctrl_path = mimic_utils.get_target_ctrl_path(robot)
            
    for io_name in robots_ios:
        io_numbers.append(pm.getAttr('{}.{}_ioNumber'.format(target_ctrl_path, io_name)))
    
    
    io_number = 1
    
    if io_numbers:
        io_number = max(io_numbers) + 1
    
    postproc_id = int(16*io_number - 16)
    
    
    fiz_attrs = ['frame']
    
    for attr in fiz_attrs:
        
        io_param_dict = {}
        
        io_param_dict['IO Name'] = attr
        io_param_dict['Postproc ID'] = str(postproc_id)
        io_param_dict['IO Number'] = io_number
        io_param_dict['Type'] = 'digital'
        io_param_dict['Resolution'] = '16-bit'
        io_param_dict['Ignore'] = False
        
        mimic_io.add_io(io_params=io_param_dict)
        
        io_number += 1
        postproc_id += 16
    
    return 


def connect_frame_attr(robot):
    """
    Adds an expression to the frame output attribute that actually puts the frame number
    """
    
    # Get time node
    time_node = pm.ls('time1', type='time')[0]
    
    time_attr = '{}.outTime'.format(time_node)
    frame_io_attr = '{}|robot_GRP|target_CTRL.frame_value'.format(robot)
    
    pm.connectAttr(time_attr, frame_io_attr)
    
    
robot = get_robot_selection()
add_frame_as_output(robot)
connect_frame_attr(robot)
