import cv2
import mediapipe as mp
import os
from tqdm import tqdm

# -----------------------------
# PATHS (adjusted for your setup)
# -----------------------------
# Paths
input_dir = r"C:\Silent Speech Recognition Project\Dataset\s15video\s15"
output_base = r"C:\Silent Speech Recognition Project\Dataset\s15_processed"

os.makedirs(output_base, exist_ok=True)

# -----------------------------
# Mediapipe setup
# -----------------------------
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    min_detection_confidence=0.5
)

# -----------------------------
# Function to process one video
# -----------------------------
def process_video(video_path, output_dir):
    cap = cv2.VideoCapture(video_path)
    frame_idx = 0
    os.makedirs(output_dir, exist_ok=True)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert BGR → RGB (for MediaPipe)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            h, w, _ = frame.shape
            for face_landmarks in results.multi_face_landmarks:
                mouth_points = []
                for idx in [61, 291, 0, 17, 13, 14]:  # lip keypoints
                    x = int(face_landmarks.landmark[idx].x * w)
                    y = int(face_landmarks.landmark[idx].y * h)
                    mouth_points.append((x, y))

                # Bounding box
                x_min = max(min([p[0] for p in mouth_points]) - 10, 0)
                y_min = max(min([p[1] for p in mouth_points]) - 10, 0)
                x_max = min(max([p[0] for p in mouth_points]) + 10, w)
                y_max = min(max([p[1] for p in mouth_points]) + 10, h)

                # Crop lips
                lips = frame[y_min:y_max, x_min:x_max]
                if lips.size > 0:
                    lips = cv2.resize(lips, (64, 64))
                    cv2.imwrite(f"{output_dir}/frame_{frame_idx:04d}.jpg", lips)

        frame_idx += 1

    cap.release()

# -----------------------------
# Loop over all videos in folder
# -----------------------------
for video_file in tqdm(os.listdir(input_dir)):
    if video_file.endswith(".mpg"):
        video_path = os.path.join(input_dir, video_file)
        output_dir = os.path.join(output_base, video_file.replace(".mpg", ""))
        process_video(video_path, output_dir)

print("All videos processed. Lip frames saved in:", output_base)
