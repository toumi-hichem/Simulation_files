import numpy as np
from math import cos, sin, radians
from pprint import pprint

if __name__ == '__main__':
    v_x, v_y = cos(radians(0)), sin(radians(0))
    r = 0

    T = np.array([
        [-np.sin(np.pi / 6), np.cos(np.pi / 6), r],
        [-np.sin(5 * np.pi / 6), np.cos(5 * np.pi / 6), r],
        [-np.sin(3 * np.pi / 2), np.cos(3 * np.pi / 2), r]
    ])
    T3 = np.array([
        [1, 0, -r],
        [-0.5, np.sqrt(3) / 2, -r],
        [-0.5, -np.sqrt(3) / 2, -r]
    ])

    V = np.array([v_x, v_y, 0])

    # Calculate wheel speeds
    wheel_speeds = np.dot(T, V) * 1
    wheel_speeds3 = np.dot(T3, V) * 1

    print(f'Wheel speeds: {wheel_speeds}')
    print(f'Wheel speeds3: {wheel_speeds3}')
    pprint(T.tolist())

