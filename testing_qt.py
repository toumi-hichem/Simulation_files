import numpy as np
from math import sqrt as sq
from pprint import pprint

def is_close_to_path(cell_center, path_points, threshold_distance):
    distances = []
    for p in path_points:
        distances.append(sq(abs((cell_center[0] - p[0])^2 + (cell_center[1] - p[1])^2)))
    dist = []
    for d in range(len(distances)):
        if distances[d] < threshold_distance:
            dist.append(d)
    dist.sort(key=lambda x : distances[x])
    return dist

t = [[603, 552], [603, 551], [603, 547], [603, 542], [603, 527], [603, 503], [603, 470], [603, 434], [600, 379], [595, 332], [593, 295], [593, 278], [591, 262], [591, 253], [591, 246], [591, 239], [591, 234], [591, 226], [591, 217], [591, 206], [591, 195], [591, 184], [591, 177], [591, 168], [591, 165], [591, 160], [591, 156], [591, 153], [591, 150]]
x = is_close_to_path([640, 400], t, 10)
print(x)