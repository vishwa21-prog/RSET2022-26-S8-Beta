# TITAN Feature: Teleoperation (Manual Control)

Teleoperation (Teleop) is the direct manual control system for your robot. It allows you to drive TITAN like a remote-controlled vehicle.

## ⚙️ Technical Logic
- **Topic Published**: `/cmd_vel`
- **Message Type**: `geometry_msgs/Twist`
- **Output Units**: 
  - **Linear Velocity**: Meters per second (m/s).
  - **Angular Velocity**: Radians per second (rad/s).
- **Communication Flow**: `TRIDENT TUI` (Rust) → `ROS 2 Topic` → `Arduino Bridge Node` (Python) → `Serial PWM` → `Motor Driver`.

## 🧩 How it Works
The TUI listens for raw keyboard events. When you press an arrow key, it calculates a "Target Velocity" based on your settings.
- **Linear Logic**: Pressing `Up` sets the forward X velocity to your `Linear Speed` (Default 0.1 m/s).
- **Angular Logic**: Pressing `Left` sets the rotation Z velocity to your `Angular Turn` (Default 0.5 rad/s).
- **Safety**: As soon as you release the key, the TUI immediately sends a "Zero" message (`0.0 m/s`), causing the robot to stop.

## 🛠️ Step-by-Step Usage
1.  Navigate to **`[Robot] TELEOP (MANUAL CONTROL)`**.
2.  **To Drive**: Use **Arrow Keys** or **WASD** (if supported).
3.  **To Configure**: Select the menu item and press **Enter**.
    - Use **Up/Down** to highlight a field.
    - Type a number (e.g., `0.3`).
    - Use the **Backspace** key to correct mistakes.
    - Press **Enter** to confirm.
4.  **Verification**: You can watch the `Telemetry` panel at the top while driving to see your exact (X, Y) coordinates change.

## 🆘 Troubleshooting
- **Robot Moves Slowly**: Your `Linear Speed` might be set too low. Increase it to `0.2` or `0.3`.
- **Robot Turns the Wrong Way**: Your encoders or motor pins might be swapped. You can reverse the direction in the `arduino_bridge_node.py` if needed.
- **Jerky Motion**: This usually means the Bluetooth or WiFi connection to your robot is lagging. Move closer to the Access Point for a smoother experience.

> [!TIP]
> **Pro Tip**: If you are in a small room, use a low speed (0.1). If you are in a large open space, you can comfortably bump the speed up to 0.5 for faster transit.
