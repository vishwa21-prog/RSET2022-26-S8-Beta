import cv2
import os
import numpy as np
from skimage.metrics import structural_similarity as ssim

# Allow duplicate library loading (for some environments)
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Output folder for frames
output_folder = 'filtered_frames'
os.makedirs(output_folder, exist_ok=True)

# Start capturing from the webcam (change 0 to filename for video file)
cap = cv2.VideoCapture(0)

frame_count = 0
saved_count = 0
prev_gray = None
SSIM_THRESHOLD = 0.90  # Tune this for more or less strict filtering

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert current frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if prev_gray is None:
        # Save first frame unconditionally
        frame_filename = os.path.join(output_folder, f'frame_{saved_count:04d}.jpg')
        cv2.imwrite(frame_filename, frame)
        saved_count += 1
    else:
        # Compute SSIM between current and previous grayscale frames
        score, _ = ssim(gray, prev_gray, full=True)

        if score < SSIM_THRESHOLD:
            # Save only if SSIM is below threshold (i.e., frame is different)
            frame_filename = os.path.join(output_folder, f'frame_{saved_count:04d}.jpg')
            cv2.imwrite(frame_filename, frame)
            saved_count += 1

    # Update previous frame
    prev_gray = gray.copy()
    frame_count += 1

cap.release()
print(f'Total frames read: {frame_count}')
print(f'Non-redundant frames saved: {saved_count}')
