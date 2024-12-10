"""cell_controller_0_2 controller."""

import sys
from math import sin, cos, sqrt, tan, pi, radians
import math
import numpy as np
from pprint import pprint


sys.path.append(r'C:\Program Files\Webots\lib\controller\python')
sys.path.append(r'C:\Users\User\PycharmProjects\Simulation_files')

from loggerClass import logger
from shared_data import SharedData, shared_mem
from controller import Robot
from controller import Supervisor
import logging


# functions

def move(x, y, w, name_x, name_y):
    # wheel_speeds = inverse_kinematics(x, y, w)
    if x is None or y is None:
        return None
    # Example usage
    v_x = x  # .0  # Linear velocity in x direction
    v_y = y  # 0.5  # Linear velocity in y direction
    omega = 0.0  # Angular velocity
    r = 0.00  # Distance from center to wheel (example value)
    logger.info(f'Current sys info:\n{data[SharedData.simulation_information]}')
    if 'mode' not in data[SharedData.simulation_information].keys():
        print("not ON yet")
        return
    elif data[SharedData.simulation_information]['mode'] == 'manual':
        v_x = y  # .0  # Linear velocity in x direction
        v_y = -x
        Tljk = np.array([
            [1, 0, 0],
            [-0.5, np.sqrt(3) / 2, 0],
            [-0.5, -np.sqrt(3) / 2, 0]
        ])
        #counter 30
        T = np.array([
            [1, -np.sqrt(0.5), 0],
            [0.5, 0.5, 0],
            [0.5, 0.5, 0]
        ])
        #30 deg
        Tdafad = np.array([
            [1.0, -0.5 * np.sqrt(3), 0],
            [0.5, 0.5, 0],
            [0.5, 0.5, 0]
        ])
    elif data[SharedData.simulation_information]['mode'] == 'auto':

        # Transformation matrix
        T = np.array([
            [-np.sin(np.pi / 6), np.cos(np.pi / 6), r],
            [-np.sin(5 * np.pi / 6), np.cos(5 * np.pi / 6), r],
            [-np.sin(3 * np.pi / 2), np.cos(3 * np.pi / 2), r]
        ])


    # Velocity vector
    V = np.array([v_x, v_y, omega])

    # Calculate wheel speeds
    wheel_speeds = np.dot(T, V) * 1

    list_of_motors[name_x][name_y][0].setVelocity(wheel_speeds[0] * max_speed)
    list_of_motors[name_x][name_y][1].setVelocity(wheel_speeds[1] * max_speed)
    list_of_motors[name_x][name_y][2].setVelocity(wheel_speeds[2] * max_speed)


def command(name_x, name_y, x, y, w):
    name = f'cell_{name_x}_{name_y}'


    move(x, y, w, name_x, name_y)
    return name


def set_vector_field(vec_field_to_set_):
    vector_field = vec_field_to_set_
    for ii in range(0, max_rows):  # range(len(vector_field)):
        for j in range(0, max_cols):  # range(len(vector_field[0])):
            t = vector_field[ii][j]
            if t[0] is None: command(ii, j, 0, 0, 0)
            command(ii, j, t[0], t[1], t[2])
    print(f'Vec field: {vector_field}')
    return vector_field


def get_sensor_data():
    data[SharedData.sensor_field] = []
    print(f'Sensor data: ')
    for ii in range(max_rows):
        data[SharedData.sensor_field].append([])
        for j in range(max_cols):
            val = 1 if list_of_sensors[ii][j].getValue() < 0.5 else 0  # true means highlight, false means no # 1 -> false
            data[SharedData.sensor_field][ii].append(val)  # TODO: T/F better?
            print(val, end="-")
        print('\n')
    print(f'Stored data')
    shared_mem.store_data(data)


def get_motor_list():
    list_of_motors = []
    list_of_sensors = []

    for i in range(max_rows):
        list_of_motors.append([])
        list_of_sensors.append([])
        for j in range(max_cols):
            name = f'cell_{i}_{j}'
            motor_1_node = robot.getDevice(name + "_m1")
            motor_2_node = robot.getDevice(name + "_m2")
            motor_3_node = robot.getDevice(name + "_m3")
            motor_1_node.setVelocity(0)
            motor_2_node.setVelocity(0)
            motor_3_node.setVelocity(0)

            motor_1_node.setPosition(float('inf'))
            motor_2_node.setPosition(float('inf'))
            motor_3_node.setPosition(float('inf'))

            list_of_motors[i].append([motor_1_node, motor_2_node, motor_3_node])

            sensor_name = f'{name}_dist_0'
            distance_sensor = robot.getDevice(sensor_name)
            distance_sensor.enable(timestep)
            list_of_sensors[i].append(distance_sensor)
    return list_of_motors, list_of_sensors


# ----------------------------------------------------------------
BOX_PROTO = F'''
SolidBox {{
  translation 0 0 0.3
  name "box_blue"
  size 0.3 0.3 0.2
  contactMaterial "InteriorWheelMat"
  appearance PBRAppearance {{
    baseColor 0.192157 0.447059 1
    roughness 0.5
    metalness 0
  }}
  physics Physics {{
  }}
}}
'''
# ----------------------------------------------------------------
# load values
robot = Robot()
# box_node = root.getField('children').importMFNodeFromString(-1, BOX_PROTO)


# create the Robot instance.
timestep = 64
robot.timeStep = timestep
max_speed = 6.28
time_between_sensor_capture = 2
R = 0.09
# extract data
data = shared_mem.retrieve_data()
max_rows, max_cols = 1, 1

try:
    max_rows = data[SharedData.simulation_information]['rows']
    max_cols = data[SharedData.simulation_information]['cols']
except:
    print('Not connected to shared mem')
    sys.exit("Not connected to shared mem")
once = True
# ----------------------------------------------------------------
# main loop
i = time_between_sensor_capture  # [ 0.98      -0.0869873 -0.9530127] for 200
'''O = 180
basic_dir = [cos(O), sin(O), 0]
vec_field_to_set = [[basic_dir for idgml in range(max_rows)] for burbur in range(max_cols)]'''
while robot.step(timestep) != -1:
    if once:
        once = False
        list_of_motors, list_of_sensors = get_motor_list()
    # Read the sensors:
    # Enter here functions to read sensor data, like:
    #  val = ds.getValue()
    if i == 0:
        data = shared_mem.retrieve_data()
        vec_field_to_set = data[SharedData.vector_field]
        set_vector_field(vec_field_to_set)
        get_sensor_data()
        i = time_between_sensor_capture
    else:
        i -= 1
    # Process sensor data here.

    # Enter here functions to send actuator commands, like:
    #  motor.setPosition(10.0)
    pass
