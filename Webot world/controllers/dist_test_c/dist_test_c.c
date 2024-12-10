#include <webots/robot.h>
#include <webots/distance_sensor.h>

#define TIME_STEP 64 // milliseconds between simulation steps (adjustable)

int main(int argc, char *argv[]) {
  // Initialize the robot instance
  WbDeviceTag distance_sensor;
  wb_robot_init();

  // Get the distance sensor handle (assuming the sensor name is "distance_sensor")
  distance_sensor = wb_robot_get_device("cell_0_0_dist_0");
  if (distance_sensor == 0) {
    printf("Error: Could not find distance sensor 'distance_sensor'\n");
    return 1;
  }

  // Enable the distance sensor (optional, some sensors are enabled by default)
  wb_distance_sensor_enable(distance_sensor, TIME_STEP);

  // Main simulation loop
  while (wb_robot_step(TIME_STEP) != -1) {
    // Read the distance sensor value
    double distance = wb_distance_sensor_get_value(distance_sensor);

    // Print the distance (you can replace this with your desired processing)
    printf("Distance: %f\n", distance);
  }

  // Cleanup (optional)
  wb_distance_sensor_disable(distance_sensor);
  wb_robot_cleanup();

  return 0;
}
