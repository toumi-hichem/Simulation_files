import numpy as np

# Constants
rows, cols = 5, 5
angles = np.linspace(0, 360, num=rows*cols, endpoint=False)  # Generate angles from 0 to 360

# Initialize the 2D array
vector_array = [[None for _ in range(cols)] for _ in range(rows)]

# Function to convert angle to unit vector
def angle_to_unit_vector(angle):
    radian = np.radians(angle)
    x = np.cos(radian)
    y = np.sin(radian)
    return [x, y, 0]

# Populate the array
index = 0
for i in range(rows):
    for j in range(cols):
        vector_array[i][j] = angle_to_unit_vector(angles[index])
        index += 1

# Print the array
for row in vector_array:
    print(row)

print(vector_array)