"""from controller import Supervisor

supervisor = Supervisor()
root = supervisor.getRoot()
time_step = int(supervisor.getBasicTimeStep())

BOX_PROTO =
Solid {
  translation 0 0.1 0
  rotation 0 1 0 0
  children [
    Shape {
      appearance Appearance {
        material Material {
          diffuseColor 1 0 0
        }
      }
      geometry Box {
        size 0.1 0.1 0.1
      }
    }
  ]
  name "box"
}

i = 50
while supervisor.step(time_step) != -1:
    print(i)
    i -= 1
    if not i:
        box_node = supervisor.getField('children').importMFNodeFromString(-1, BOX_PROTO)
        box_translation = box_node.getField('translation')
        current_position = box_translation.getSFVec3f()
        print(f'Current pos: {current_position}')
"""

import sys
sys.path.append(r'C:\Users\toupa\Desktop\ESE - S1\PFE\Simulation_files')
from controller import Supervisor
from shared_data import SharedData, shared_mem
import logging
# Initialize the supervisor
supervisor = Supervisor()

# Get the basic time step of the current world.
timestep = int(supervisor.getBasicTimeStep())


def monitor():
    data = shared_mem.retrieve_data()
    pack = data[SharedData.simulation_information]['spawn_package']
    if pack:
        create_box(supervisor, pack['position'], pack['size'], pack['color'])



# Function to create a new box
def create_box(supervisor, position, size, color):
    # Define the box's proto string
    box_proto = """
    Solid {
      translation %f %f %f
      children [
        Shape {
          appearance Appearance {
            material Material {
              diffuseColor %f %f %f
            }
          }
          geometry Box {
            size %f %f %f
          }
        }
      ]
      boundingObject Box {
        size %f %f %f
      }
    }
    """ % (position[0], position[1], position[2], color[0], color[1], color[2], size[0], size[1], size[2], size[0], size[1], size[2])

    # Import the box into the world
    root = supervisor.getRoot()
    root.getField("children").importMFNodeFromString(-1, box_proto)

# Define the position, size, and color of the box
position = [0, 0.5, 0.3]
size = [0.2, 0.2, 0.2]
color = [1, 0, 0]  # Red color

# Create the box
create_box(supervisor, position, size, color)

# Run the simulation loop
while supervisor.step(timestep) != -1:
    pass
