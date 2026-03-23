# TITAN Feature: Diagnostics & Status

The Diagnostics system is TITAN's "medical monitor." It keeps you informed of the robot's health in real-time.

## ⚙️ Technical Specification
- **Monitoring Layer**: Integrated directly into the TRIDENT TUI.
- **Power Tracking**: Monitors the main battery voltage via the Arduino's Analog-to-Digital Converter (ADC).
- **Log Buffering**: Keeps a rolling window of the last 100 ROS 2 log entries.

## 🧩 How it Works
### 1. The Color-Coded Status System
The TUI automatically highlights keywords to show you the state of the robot:
- 🟢 **Green (OK/CONNECTED/STABLE)**: All systems normal.
- 🟡 **Yellow (LOW/WARNING)**: System needs attention soon (low battery, slow sensor response).
- 🔴 **Red (NOT FOUND/DISCONNECTED/CRITICAL)**: Total failure. Stop immediately and check cables.
- ⚪ **Gray**: Standby or informational status.

### 2. Power Supply Monitoring
The `STABLE` battery status is calculated based on these thresholds:
- **12.0V - 12.6V**: Full Battery (Green).
- **11.1V - 11.9V**: Low Battery (Yellow) - Head back to the dock!
- **Below 11.0V**: Critical (Red) - Power down immediately to protect the LiPo cells.

### 3. Telemetry Tracking
The `TELEMETRY` panel in the TUI shows:
- **X / Y**: The robot's position relative to its start point (in meters).
- **TH (Theta)**: The robot's heading (in degrees). **0°** is directly forward.

## 🛠️ Step-by-Step Usage
1.  **Check for Red**: When you launch `trident`, look at the `POWER SUPPLY` line. If it says `DISCONNECTED`, your Arduino is not plugged in.
2.  **Monitor the Logs**: If the robot isn't responding, scroll down to the `SYSTEM LOGS` panel.
3.  **Read Errors**: Look for errors like `Serial Error` or `LiDAR Timeout` to diagnose hardware issues without needing to SSH into the robot.

## 🆘 Troubleshooting
- **Voltage Reads 0.0V**: The battery sensing wire is disconnected from the Arduino.
- **Logs are Empty**: You haven't started any BRINGUP or NAVIGATION nodes yet.
- **Position (X, Y) is "Blinking"**: This points to a high-speed communication delay. Check your WiFi signal.

> [!IMPORTANT]
> Never ignore a **RED** status warning. Driving the robot with a critical battery level (below 11V) can permanently damage your battery cells!
