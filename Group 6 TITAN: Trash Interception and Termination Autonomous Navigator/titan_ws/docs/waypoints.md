# TITAN Feature: Waypoint System

The Waypoint System is your "digital bookmark" manager for locations. Instead of typing coordinates, you can simply tell the robot: "Go to the charging station."

## ⚙️ Data Structure
Waypoints are stored in `~/titan_ws/src/titan_bringup/config/waypoints.yaml`. Each entry looks like this:
```yaml
- name: "Kitchen"
  x: 1.25
  y: -0.85
  theta: 3.14  # Orientation in Radians
```

## 🧠 How it Works
- **Save (`s` key)**: Captures the current `odom` frame coordinates and appends them to the YAML file.
- **Navigate (`Enter`)**: Sends a `PoseStamped` message to the Nav2 `goal_pose` topic. The robot then plans a path to these exact coordinates.
- **Set Pose (`p` key)**: Sends a `PoseWithCovarianceStamped` message to the `/initialpose` topic. This is used to "tell" the robot where it is when it first starts up.

## 🛠️ Pro Usage Guides
### 1. Manually Editing Waypoints
You can open the `waypoints.yaml` in any text editor to manually fine-tune coordinates or rename locations. The TUI will reload the file every time you enter the menu.

### 2. Creating a "Pose Estimate" Waypoint
It's a good idea to save a waypoint called `start_point` exactly where you usually put the robot when you power it on. This way, you can just press **`p`** on `start_point` to perfectly align the robot with the map every time!

### 3. The "Relocalize" Strategy
If your robot gets "lost" (thinks it's in a wall), drive it manually to a known location (like the "Entryway"). In the Waypoint menu, highlight "Entryway" and press **`p`**. This instantly fixes the robot's internal "Map Alignment."

## 🆘 Troubleshooting
- **Waypoints List Empty**: Ensure the `waypoints.yaml` file exists and is not corrupted (valid YAML format).
- **Robot Drives to Wrong Spot**: The robot's coordinates are relative to the *Start Position* of the mapping session. Always start mapping and navigation from the same physical spot if possible.
- **Delete Warning**: Deleting a waypoint in the TUI is permanent and updates the file immediately.

> [!TIP]
> **Orientation Matters**: When saving a waypoint, the direction the robot is facing (Theta) is saved too! If you want the robot to "back into" a dock, face it *away* from the dock when saving.
