"""celluvoyer_controller_0_1 controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot, DistanceSensor
from math import sin, cos, sqrt, tan, pi
import numpy as np
from numpy.linalg import inv
# create the Robot instance.
robot = Robot()
robot.timeStep = 32

# get the time step of the current world.

def move(x, y, w):
    o1 = 0   * ( pi / 180.0 )
    o2 = 120 * ( pi / 180.0 )
    o3 = 240 * ( pi / 180.0 )

    A = np.array([[cos(o1), cos(o2), cos(o3)],
                  [sin(o1), sin(o2), sin(o3)],
                  [1, 1, 1]])
    order = np.array([[x],[y], [w]])
    ans = A.dot(order)

    motor_1.setVelocity(ans[0] * max_speed)
    motor_2.setVelocity(ans[1] * max_speed)
    motor_3.setVelocity(ans[2] * max_speed)

"""def move (x, y, w):
    l = sqrt(x*x + y*y)
    o = tan (x/y)
    ans = [l*cos(30 - o), l*cos(150 - o), l*cos(120*2 + 30 - o)]
    motor_1.setVelocity(ans[0] * max_speed)
    motor_2.setVelocity(ans[1] * max_speed)
    motor_3.setVelocity(ans[2] * max_speed)
"""
timestep = 32
max_speed = 6.28
"""
motor_1 = robot.getDevice("cell_0_0_m1")
motor_2 = robot.getDevice("cell_0_0_m2")
motor_3 = robot.getDevice("cell_0_0_m3")

motor_1.setPosition(float("inf"))
motor_2.setPosition(float("inf"))
motor_3.setPosition(float("inf"))
"""

dist_1 = robot.getDevice("cell_0_0_dist_0")
dist_1.enable(32)

print(dist_1)
#move(0, 0.2, 0.4)
print(vars(robot))
#motor_1.setVelocity(-1)
#motor_2.setVelocity(-1)
#motor_3.setVelocity(-1)

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
#  motor = robot.getDevice('motorname')
#  ds = robot.getDevice('dsname')
#  ds.enable(timestep)
i = 0
# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep) != -1:
    # Read the sensors:
    # Enter here functions to read sensor data, like:
    #  val = ds.getValue()
    if i == 20:
        print(dist_1.getValue())
        i = 0
    # Process sensor data here.
    i += 1
    # Enter here functions to send actuator commands, like:
    #  motor.setPosition(10.0)
    pass

# Enter here exit cleanup code.
