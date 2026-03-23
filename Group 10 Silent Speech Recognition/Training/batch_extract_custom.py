import cv2
import mediapipe as mp
import os
from tqdm import tqdm

# --------------------------------
# PATHS
# --------------------------------
INPUT_ROOT = r"C:\Silent Speech Recognition Project\Dataset\custom_dataset"
OUTPUT_ROOT = r"C:\Silent Speech Recognition Project\Dataset\custom_processed1"

os.makedirs(OUTPUT_ROOT, exist_ok=True)

# --------------------------------
# MediaPipe Setup
# --------------------------------
mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# --------------------------------
# Process Single Video
# --------------------------------
def process_video(video_path, output_dir):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"❌ Cannot open video: {video_path}")
        return

    os.makedirs(output_dir, exist_ok=True)

    frame_idx = 0
    saved_frames = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        if results.multi_face_landmarks:
            h, w, _ = frame.shape
            face = results.multi_face_landmarks[0]

            lip_indices = [61, 291, 0, 17, 13, 14]
            pts = []

            for idx in lip_indices:
                x = int(face.landmark[idx].x * w)
                y = int(face.landmark[idx].y * h)
                pts.append((x, y))

            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]

            pad = 10
            x_min = max(min(xs) - pad, 0)
            y_min = max(min(ys) - pad, 0)
            x_max = min(max(xs) + pad, w)
            y_max = min(max(ys) + pad, h)

            lips = frame[y_min:y_max, x_min:x_max]

            if lips.size > 0:
                lips = cv2.resize(lips, (64, 64))
                save_path = os.path.join(output_dir, f"frame_{frame_idx:04d}.jpg")
                cv2.imwrite(save_path, lips)
                saved_frames += 1

        frame_idx += 1

    cap.release()

    if saved_frames == 0:
        print(f"⚠️ No lips detected → deleting {output_dir}")
        try:
            os.rmdir(output_dir)
        except:
            pass


# --------------------------------
# ONLY PROCESS SPEAKERS 6,7,8
# --------------------------------
for speaker in ["speaker 9", "speaker 10", "speaker 11"]:

    speaker_path = os.path.join(INPUT_ROOT, speaker)
    if not os.path.isdir(speaker_path):
        print(f"⚠️ Missing folder: {speaker}")
        continue

    for word in os.listdir(speaker_path):

        word_path = os.path.join(speaker_path, word)
        if not os.path.isdir(word_path):
            continue

        for split in ["train", "test"]:

            split_path = os.path.join(word_path, split)
            if not os.path.isdir(split_path):
                continue

            videos = os.listdir(split_path)

            for video in tqdm(videos, desc=f"{speaker}/{word}/{split}"):

                if not video.lower().endswith((".mp4", ".mov", ".avi", ".mpg")):
                    continue

                video_path = os.path.join(split_path, video)

                output_dir = os.path.join(
                    OUTPUT_ROOT,
                    speaker,
                    word,
                    split,
                    video.replace(".", "_")
                )

                process_video(video_path, output_dir)

print("\n✅ Speakers 6, 7, 8 processed successfully!")
print("📁 Output saved at:", OUTPUT_ROOT)