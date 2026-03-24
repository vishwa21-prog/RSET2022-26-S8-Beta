# TITAN - ROS 2 Workspace

This is the core ROS 2 workspace for the **TITAN** robot. It contains the hardware drivers, launch configurations, and navigation parameters.

## 📦 Packages
- **`titan_bringup`**: Central launch files, URDF models, and configurations for sensors and base drivers.
- **`ydlidar_ros2_driver`**: ROS 2 driver for the YDLidar X2.
- **`arduino_bridge`**: Refactored serial bridge for motor control and telemetry.

## 🛠️ Installation & Build
Ensure you are running ROS 2 Jazzy on Ubuntu:

```bash
cd ~/titan_ws
colcon build --symlink-install
source install/setup.bash
```

## 🚀 Quick Start
To bring up the robot hardware:
```bash
ros2 launch titan_bringup bringup.launch.py
```

To start SLAM mapping:
```bash
ros2 launch titan_bringup mapping.launch.py
```

## 🗺️ Navigation
To launch the Nav2 stack with a saved map:
```bash
ros2 launch titan_bringup navigation.launch.py
```

## 📖 Detailed Feature Guides
For in-depth explanations on how each system works, refer to our documentation:
- [🚀 **Bringup**](docs/bringup.md): Hardware initialization and core drivers.
- [🗺️ **Mapping**](docs/mapping.md): Building maps with SLAM Toolbox.
- [🤖 **Navigation**](docs/navigation.md): Autonomous path planning and avoidance.
- [📍 **Waypoints**](docs/waypoints.md): Saving and managing key locations.
- [🎮 **Teleop**](docs/teleop.md): Manual control and speed configuration.
- [🏥 **Diagnostics**](docs/diagnostics.md): Monitoring power and system health.
