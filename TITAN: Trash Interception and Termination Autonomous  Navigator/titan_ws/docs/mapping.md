# TITAN Feature: Mapping (SLAM)

Mapping (Simultaneous Localization and Mapping) is what allows TITAN to "understand" its surroundings. It creates a high-resolution 2D occupancy grid where Black pixels are walls, White pixels are clear space, and Gray pixels are unknown.

## ⚙️ Technical Design
- **Core Algorithm**: SLAM Toolbox (Asynchronous Online mode).
- **Update Frequency**: Every **0.05 meters** of travel or **0.08 radians** of rotation.
- **Resolution**: **0.05 meters (5cm)** per pixel in the map.
- **Stability**: Uses Scan-to-Map matching to correct for the wheel slippage that occurs on carpets and uneven tiles.

## 🧩 How it Works
1.  **Scan Matching**: Each time the LiDAR sends a scan, SLAM Toolbox tries to "fit" that scan into the existing map like a puzzle piece.
2.  **Odometry Integration**: The robot uses wheel rotations to estimate where it moved. However, because wheels slip, this estimate is always slightly wrong. SLAM corrects this by comparing the "expected" position with the actual "best fit" of the laser scan.
3.  **Loop Closure**: If you drive the robot back to a room it has seen before, the software recognizes the patterns and "snaps" the map into perfect alignment, removing any accumulated drift.

## 🛠️ Step-by-Step Usage
1.  Clear the room of small movable objects (like shoes) that might confuse the LiDAR.
2.  In TRIDENT, select **`[Robot] START MAPPING (SLAM TOOLBOX)`**.
3.  **Move the robot slowly**. Sudden jerks or fast spins can break the "Lock" the software has on the walls.
4.  Drive in a complete loop if possible.
5.  **Save your work**: Select **`[Sys] SAVE CURRENT MAP`**. 
    - Type a name like `first_floor`. 
    - This creates `first_floor.yaml` and `first_floor.pgm` in your `maps` directory.

## 🆘 Troubleshooting
- **"Ghosting" (Double Walls)**: This happens when the SLAM loses track due to fast movement. Press **`r`** to reset Odometry and drive slower.
- **Map Not Updating**: Check if the Lidar is spinning. If it is, ensure the `arduino_bridge` is running (Bringup must be active).
- **Map Looks Rotated**: The robot always starts mapping at X=0, Y=0, Heading=0. Ensure the robot is pointing "Forward" relative to your room's orientation when you start.

> [!TIP]
> **Pro Tip**: When mapping a new room, drive along the edges of the walls first to define the perimeter, then move into the center.
