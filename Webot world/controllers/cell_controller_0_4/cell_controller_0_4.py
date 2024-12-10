"""cell_controller_0_2 controller."""

import sys
from math import sin, cos, sqrt, tan, pi
import math
import numpy as np

sys.path.append(r'C:\Program Files\Webots\lib\controller\python')
sys.path.append(r'C:\Users\User\PycharmProjects\Simulation_files')

from shared_data import SharedData, shared_mem
from controller import Robot


# functions

def move(x, y, w, motor_1, motor_2, motor_3):
    if x is None or y is None:
        return None
    # Example usage
    v_x = 1.0  # Linear velocity in x direction
    v_y = 0.5  # Linear velocity in y direction
    omega = 0.2  # Angular velocity
    r = 0.1  # Distance from center to wheel (example value)

    # Transformation matrix
    T = np.array([
        [1, 0, -r],
        [-0.5, np.sqrt(3) / 2, -r],
        [-0.5, -np.sqrt(3) / 2, -r]
    ])

    # Velocity vector
    V = np.array([v_x, v_y, omega])

    # Calculate wheel speeds
    wheel_speeds = np.dot(T, V)
    print(f'Wheel speeds: {wheel_speeds}')


    '''o1 = 30  # * (pi / 180.0)
    o2 = 150  # * (pi / 180.0)
    o3 = 270  # * (pi / 180.0)

    A = np.array([[cos(o1), cos(o2), cos(o3)],
                  [sin(o1), sin(o2), sin(o3)],
                  [1, 1, 1]])

    order = np.array([[x], [y], [w]])
    ans = A.dot(order)
    B = np.array([[0, 1, R],
                  [-0.866025, -0.5, R],
                  [0.866025, -0.5, R]])'''
    # ans = B.dot(order)
    # ans = calculate_motor_speeds(x, y, w)
    motor_1.setVelocity(wheel_speeds[0] * max_speed)
    motor_2.setVelocity(wheel_speeds[1] * max_speed)
    motor_3.setVelocity(wheel_speeds[2] * max_speed)


def command(name_x, name_y, x, y, w):
    name = f'cell_{name_x}_{name_y}'
    motor_1 = robot.getDevice(name + "_m1")
    motor_2 = robot.getDevice(name + "_m2")
    motor_3 = robot.getDevice(name + "_m3")

    motor_1.setPosition(float("inf"))
    motor_2.setPosition(float("inf"))
    motor_3.setPosition(float("inf"))

    move(x, y, w, motor_1, motor_2, motor_3)
    return name


def set_vector_field():
    print(F"data: {data}")
    vector_field = data[SharedData.vector_field]
    for ii in range(0, max_rows):  # range(len(vector_field)):
        for j in range(0, max_cols):  # range(len(vector_field[0])):
            t = vector_field[ii][j]
            if t[0] is None: command(ii, j, 0, 0, 0)
            command(ii, j, t[0], t[1], t[2])
    return vector_field


def get_sensor_data():
    data[SharedData.sensor_field] = []
    for ii in range(max_rows):
        data[SharedData.sensor_field].append([])
        for j in range(max_cols):
            t = robot.getDevice(f'cell_{ii}_{j}_dist_0')
            t.enable(timestep)
            val = 1 if t.getValue() < 0.5 else 0  # true means highlight, false means no # 1 -> false
            data[SharedData.sensor_field][ii].append(val)  # TODO: T/F better?
    shared_mem.store_data(data)


# ----------------------------------------------------------------
# load values
robot = Robot()

# create the Robot instance.
timestep = 64
robot.timeStep = timestep
max_speed = 6.28
time_between_sensor_capture = 10
R = 0.09
# extract data
data = shared_mem.retrieve_data()
try:
    max_rows = data[SharedData.simulation_information]['rows']
    max_cols = data[SharedData.simulation_information]['cols']
except:
    print('Not connected to shared mem')    

# ----------------------------------------------------------------
# main loop
i = time_between_sensor_capture
set_vector_field()
while robot.step(timestep) != -1:
    # Read the sensors:
    # Enter here functions to read sensor data, like:
    #  val = ds.getValue()
    if i == 0:
        data = shared_mem.retrieve_data()
        set_vector_field()
        get_sensor_data()

        i = time_between_sensor_capture
    else:
        i -= 1
    # Process sensor data here.

    # Enter here functions to send actuator commands, like:
    #  motor.setPosition(10.0)
    pass
