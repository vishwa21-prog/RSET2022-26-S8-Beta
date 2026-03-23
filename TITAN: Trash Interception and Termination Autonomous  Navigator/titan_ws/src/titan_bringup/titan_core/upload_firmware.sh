#!/bin/bash

# ==============================
# TITAN Core Firmware Uploader
# ==============================

SKETCH_NAME="titan_ws/src/titan_bringup/titan_core/titan_core.ino"
PORT="/dev/ttyUSB0"   # Change if needed (/dev/ttyUSB1 etc.)
FQBN="arduino:avr:nano:cpu=atmega328old"
CLI=$(which arduino-cli)

echo "=============================="
echo " TITAN Firmware Upload Script "
echo "=============================="

# ------------------------------
# Check arduino-cli exists
# ------------------------------
if [ -z "$CLI" ]; then
    echo "❌ Error: arduino-cli not found in PATH."
    exit 1
fi

# ------------------------------
# Check Arduino core installed
# ------------------------------
CORE_INSTALLED=$($CLI core list | grep "arduino:avr")

if [ -z "$CORE_INSTALLED" ]; then
    echo "⚠️ Arduino AVR core not found. Installing..."
    $CLI core update-index
    $CLI core install arduino:avr

    if [ $? -ne 0 ]; then
        echo "❌ Failed to install arduino:avr core"
        exit 1
    fi
fi

# ------------------------------
# Check port exists
# ------------------------------
if [ ! -e "$PORT" ]; then
    echo "❌ Port $PORT not found!"
    echo "Available ports:"
    ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
    exit 1
fi

# ------------------------------
# Check if port is busy
# ------------------------------
BUSY_PROCESS=$(lsof $PORT 2>/dev/null)

if [ ! -z "$BUSY_PROCESS" ]; then
    echo "⚠️ Port is currently in use:"
    echo "$BUSY_PROCESS"
    echo "👉 Kill the process or stop ROS node using serial."
    exit 1
fi

# ------------------------------
# Compile
# ------------------------------
echo "🔨 Compiling $SKETCH_NAME ..."
$CLI compile --fqbn $FQBN $SKETCH_NAME

if [ $? -ne 0 ]; then
    echo "❌ Compilation failed!"
    exit 1
fi

# ------------------------------
# Upload (Old Bootloader)
# ------------------------------
echo "🚀 Uploading (OLD bootloader)..."
$CLI upload -p $PORT --fqbn $FQBN $SKETCH_NAME

if [ $? -eq 0 ]; then
    echo "✅ SUCCESS! Firmware uploaded (old bootloader)."
    exit 0
fi

# ------------------------------
# Retry with new bootloader
# ------------------------------
echo "🔁 Retrying with NEW bootloader..."
$CLI upload -p $PORT --fqbn arduino:avr:nano:cpu=atmega328 $SKETCH_NAME

if [ $? -eq 0 ]; then
    echo "✅ SUCCESS! Firmware uploaded (new bootloader)."
    exit 0
fi

# ------------------------------
# Final failure message
# ------------------------------
echo "❌ Upload failed on both bootloaders."
echo ""
echo "🔧 Try the following:"
echo "1. Press RESET button while uploading"
echo "2. Try another port (/dev/ttyUSB1)"
echo "3. Check USB cable (data cable)"
echo "4. Ensure no ROS node is using serial"
echo ""

exit 1