# TITAN Feature: Bringup (Hardware Ignition)

The **Bringup** system is the critical "ignition" sequence for the TITAN robot. It bridges the gap between high-level ROS 2 commands and physical hardware.

## ⚙️ Technical Specification
- **Nodes Launched**: `arduino_bridge`, `ydlidar_ros2_driver_node`, `robot_state_publisher`, `joint_state_publisher`.
- **Serial Communication**: Uses a custom binary protocol at **115,200 baud**.
- **Lidar Scanning**: Rotates at **~7Hz** providing a 360-degree point cloud.
- **Odometry Frequency**: Published at **100Hz** for high-precision motion tracking.

## 🧠 How it Works
1.  **Hardware Connection**: The `arduino_bridge` node looks for a device at `/dev/arduino`. It establishes a binary link to receive wheel encoder ticks and send motor PWM values.
2.  **Environment Perception**: The `ydlidar` driver activates the laser scanner. It converts raw laser reflections into standard ROS 2 `LaserScan` messages on the `/scan` topic.
3.  **Coordinate Frames (TF)**: `robot_state_publisher` takes the URDF (Unified Robot Description Format) and calculates the exact position of every sensor. This allows the robot to know, for example, exactly where the Lidar is relative to the drive wheels.

## 🛠️ How to Use
1.  Power on the robot's main battery and wait for the Jetson Nano to boot.
2.  Launch TRIDENT: type `trident` in your terminal.
3.  Select **`[Robot] START BRINGUP`** and press Enter.
4.  **Verification**: 
    - Check the `SYSTEM LOGS` panel. You should see `Connected to Arduino (Binary Mode)`.
    - If successful, the `Telemetry` panel at the top will start showing `X: 0.00 Y: 0.00`.

## 🆘 Troubleshooting
- **"Serial Error" or "Permission Denied"**: Ensure your user is in the `dialout` group or check if the USB cable is disconnected. 
- **"Lidar Timeout"**: The Lidar requires a high-current USB port. Ensure it is plugged into the blue USB 3.0 ports on the Nano.
- **Red Status in TUI**: If the Bringup status is red, it means one of the core nodes (like the bridge) crashed. Use the **`[Sys] REBUILD WORKSPACE`** command to ensure all code is current and compiled.

> [!IMPORTANT]
> Always run Bringup first! Without it, the robot is "blind" and "paralyzed," meaning Mapping and Navigation will have no data to work with.
