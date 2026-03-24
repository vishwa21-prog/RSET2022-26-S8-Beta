# TITAN Feature: Autonomous Navigation

Autonomous Navigation is the "brain" of the TITAN robot. It uses the saved map to calculate a safe path to a target and drives the robot there while avoiding obstacles.

## ⚙️ Technical Design
- **Core Software**: Nav2 (Navigation 2 Stack).
- **Navigation Planners**: 
  - **Global Planner**: Uses the `A*` algorithm to find the overall shortest path on the map.
  - **Local Planner**: Uses the `RPP` (Regulated Pure Pursuit) algorithm to stay on that path while dodging new obstacles.
- **Safety Buffers (Costmaps)**: 
  - **Global Costmap**: Based on the static map (walls, furniture).
  - **Local Costmap**: A rolling window of **3x3 meters** around the robot that updates in real-time as the LiDAR sees new objects.
- **Goal Tolerance**: The robot considers itself "arrived" when it is within **5cm** of the target.

## 🧠 How it Works
1.  **Localization (AMCL)**: The robot constantly compares its current LiDAR scans to the saved map to know where it is (`X, Y, Theta`).
2.  **Path Planning**: When you set a goal, the robot draws a "green line" (Global Path).
3.  **Real-Time Avoidance**: If you walk in front of TITAN while it's moving, the LiDAR will "see" you. The local costmap will turn that area into a "lethal" zone, and the robot will steer around you.
4.  **Recovery Behaviors**: If the robot gets stuck in a tight corner, it will automatically try to "spin" or "back up" to clear its path.

## 🛠️ Step-by-Step Usage
1.  Open TRIDENT and select **`[Robot] START NAV2`**.
2.  **Select your Map**: Pick the `.yaml` file you saved during mapping.
3.  **Localize**: Look at RViz. If the robot's position is wrong:
    - In TRIDENT, go to **`WAYPOINTS / NAV`**.
    - Find a waypoint that represents the robot's *actual* physical location.
    - Press **`p`** to "teleport" the estimated position to that spot.
4.  **Set Goal**: Highlight a waypoint and press **`Enter`**.

## 🆘 Troubleshooting
- **Robot Not Moving**: Check if the "Emergency Kill" or "Stop" state is active. Ensure you clicked **`[Robot] START BRINGUP`** first.
- **"Robot Stuck" or "Spinning"**: The robot's path might be blocked by an object not on the map. Move the object or the robot manually using Teleop.
- **Position Deviating on Map**: If the robot "teleports" on the map, it's losing its localization. Drive it slowly to a known corner to let the scan matching "snap" back.

> [!WARNING]
> TITAN is smart, but it can't see "glass" walls or "voids" (like stairs). Always monitor the robot when it's driving autonomously in new environments!
