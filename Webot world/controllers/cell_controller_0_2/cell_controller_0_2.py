"""cell_controller_0_2 controller."""
import pickle
import sys

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from pprint import pprint
import sys
import os
import subprocess

# Python installation file
print("Python Installation File:", sys.executable)

# List of installed libraries
print("\nInstalled Libraries:")
installed_packages = subprocess.check_output([sys.executable, "-m", "pip", "list"], text=True)
print(installed_packages)

# Active virtual environment
venv = os.environ.get("VIRTUAL_ENV")
if venv:
    print("\nVirtual Environment in Use:", venv)
else:
    print("\nNo Virtual Environment in Use")

sys.path.append(r'C:\Program Files\Webots\lib\controller\python')
sys.path.append(r'C:\Users\User\PycharmProjects\Simulation_files')
from shared_data import SharedData, shared_mem
from controller import Robot
# from WBWorldGenerator import Robot as py_robot_binding
from math import sin, cos, sqrt, tan, pi
import math
import numpy as np


def calculate_motor_speeds(x, y, o):
    """
  Calculates the desired motor speeds for each wheel based on input forces.

  Args:
      wheel_radius (float): Radius of each wheel (meters).
      wheel_base (float): Distance between wheels (meters).
      x (float): Translation force in x-direction (meters/second).
      y (float): Translation force in y-direction (meters/second).
      o (float): Rotational force (radians/second).

  Returns:
      tuple(float, float, float): Desired speeds for left, right, and middle wheels (radians/second).
  """

    # Calculate linear velocities in robot frame
    v_x = x
    v_y = y
    wheel_radius = 0.027
    wheel_base = 0.02
    # Calculate angular velocity
    omega = o

    # Kinematic model for three-wheeled robot (omni-directional)
    # Assuming a triangular wheel base with middle wheel

    # Left wheel velocity
    v_l = v_x + v_y + (wheel_base / 2) * omega

    # Right wheel velocity
    v_r = v_x + v_y - (wheel_base / 2) * omega

    # Middle wheel velocity (assuming it can only rotate)
    v_m = omega

    # Convert linear velocities to motor speeds (assuming same motor constants for all wheels)
    omega_l = v_l / wheel_radius
    omega_r = v_r / wheel_radius
    omega_m = v_m / wheel_radius

    magnitude = math.sqrt(omega_l ** 2 + omega_r ** 2 + omega_m ** 2)

    # Check if normalization is necessary (avoid division by zero)
    if magnitude > 0:
        # Normalize the speed vector
        omega_l /= magnitude
        omega_r /= magnitude
        omega_m /= magnitude

    return omega_l, omega_r, omega_m


def move(x, y, w, motor_1, motor_2, motor_3):
    if x is None or y is None:
        return None
    o1 = 30  # * (pi / 180.0)
    o2 = 150  # * (pi / 180.0)
    o3 = 270  # * (pi / 180.0)

    A = np.array([[cos(o1), cos(o2), cos(o3)],
                  [sin(o1), sin(o2), sin(o3)],
                  [1, 1, 1]])

    order = np.array([[x], [y], [w]])
    ans = A.dot(order)
    B = np.array([[0, 1, R],
                  [-0.866025, -0.5, R],
                  [0.866025, -0.5, R]])
    # ans = B.dot(order)
    # ans = calculate_motor_speeds(x, y, w)
    motor_1.setVelocity(ans[0] * max_speed)
    motor_2.setVelocity(ans[1] * max_speed)
    motor_3.setVelocity(ans[2] * max_speed)


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


robot = Robot()

# create the Robot instance.
robot.timeStep = 64
timestep = 64
max_speed = 6.28
time_between_sensor_capture = 10
R = 0.09
# get the time step of the current world.
data = shared_mem.retrieve_data()
max_rows = data[SharedData.simulation_information]['rows']
max_cols = data[SharedData.simulation_information]['cols']


def set_vector_field():
    print(F"data: {data}")
    vector_field = data[SharedData.vector_field]
    print(vector_field)
    for ii in range(0, max_rows):  # range(len(vector_field)):
        for j in range(0, max_cols):  # range(len(vector_field[0])):
            t = vector_field[ii][j]
            if t[0] is None: command(ii, j, 0, 0, 0)
            print(ii, j)
            command(ii, j, t[0], t[1], t[2])
    return vector_field


# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
#  motor = robot.getDevice('motorname')
#  ds = robot.getDevice('dsname')
#  ds.enable(timestep)


# Main loop:
# - perform simulation steps until Webots is stopping the controller
# data_filename = r'C:\Users\toupa\Desktop\ESE - S1\PFE\3D\New folder\controllers\dataexchange.pkl'
# vector_field = load_lists_from_file(data_filename)
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

# Enter here exit cleanup code.
print("loop finished")
