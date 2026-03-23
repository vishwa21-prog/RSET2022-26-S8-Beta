import cv2
import torch
import mediapipe as mp
from collections import deque
from torchvision import transforms
import time

from preprocessing.dataset_loader import LipReadingDataset
from models.cnn_lstm_classifier import LipReadingClassifier


# ---------------- CONFIG ----------------
MODEL_PATH = r"C:\Silent Speech Recognition Project\models\checkpoints_classifier\best_classifier.pt"
TRAIN_CSV = r"C:\Silent Speech Recognition Project\Dataset\manifest_custom_train.csv"

MAX_FRAMES = 30      # reduced for faster realtime
CONF_THRESHOLD = 0.60
SLIDE_STEP = 10
COOLDOWN = 1.5

device = "cuda" if torch.cuda.is_available() else "cpu"


# ---------------- LOAD WORD LIST ----------------
dataset = LipReadingDataset(TRAIN_CSV, max_frames=MAX_FRAMES)
words = dataset.words


# ---------------- LOAD MODEL ----------------
model = LipReadingClassifier(num_classes=len(words)).to(device)

ckpt = torch.load(MODEL_PATH, map_location=device)
model.load_state_dict(ckpt["model"])

model.eval()


# ---------------- IMAGE TRANSFORM ----------------
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5,0.5,0.5],
                         std=[0.5,0.5,0.5])
])


# ---------------- MEDIAPIPE SETUP ----------------
mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


# ---------------- BUFFER ----------------
buffer = deque(maxlen=MAX_FRAMES)


# ---------------- LIP EXTRACTION ----------------
def extract_lips(frame, landmarks):

    h, w, _ = frame.shape

    lip_indices = [61, 291, 0, 17, 13, 14]

    pts = []

    for idx in lip_indices:
        x = int(landmarks[idx].x * w)
        y = int(landmarks[idx].y * h)
        pts.append((x,y))

    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]

    pad = 10

    x_min = max(min(xs)-pad,0)
    y_min = max(min(ys)-pad,0)

    x_max = min(max(xs)+pad,w)
    y_max = min(max(ys)+pad,h)

    crop = frame[y_min:y_max, x_min:x_max]

    return crop,(x_min,y_min,x_max,y_max)


# ---------------- MOUTH OPEN CHECK ----------------
def mouth_open(landmarks, frame):

    h, w, _ = frame.shape

    top = landmarks[13]
    bottom = landmarks[14]

    top_y = int(top.y * h)
    bottom_y = int(bottom.y * h)

    distance = abs(bottom_y - top_y)

    return distance > 3   # reduced threshold


# ---------------- CAMERA ----------------
cap = cv2.VideoCapture(0)

last_prediction = "None"
status = "Idle"

last_prediction_time = 0

print("Press Q to quit")


# ---------------- MAIN LOOP ----------------
while True:

    ret, frame = cap.read()

    if not ret:
        break

    display = frame.copy()

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = face_mesh.process(rgb)


    if results.multi_face_landmarks:

        landmarks = results.multi_face_landmarks[0].landmark

        if mouth_open(landmarks, frame):

            lips, box = extract_lips(frame, landmarks)

            x1,y1,x2,y2 = box

            cv2.rectangle(display,(x1,y1),(x2,y2),(0,255,0),2)

            if lips.size > 0:

                lips = cv2.resize(lips,(64,64))
                lips = cv2.cvtColor(lips,cv2.COLOR_BGR2RGB)

                tensor = transform(lips)

                buffer.append(tensor)

                status = "Lips Detected"

                print("Buffer:", len(buffer))

        else:

            status = "Mouth Closed"

    else:

        status = "Face Not Detected"
        buffer.clear()


    # ---------------- REALTIME PREDICTION ----------------
    if len(buffer) == MAX_FRAMES:

        current_time = time.time()

        if current_time - last_prediction_time > COOLDOWN:

            frames = list(buffer)

            x = torch.stack(frames).unsqueeze(0).to(device)

            print("Model input shape:", x.shape)

            with torch.no_grad():

                logits = model(x)

                probs = torch.softmax(logits, dim=1)

                confidence, idx = torch.max(probs, dim=1)

                confidence = confidence.item()
                idx = idx.item()

            if confidence < CONF_THRESHOLD:

                last_prediction = "Unknown"

            else:

                last_prediction = words[idx]

            print("Predicted:", last_prediction,
                  "| confidence:", round(confidence,2))

            last_prediction_time = current_time

            # sliding window
            for _ in range(SLIDE_STEP):
                if len(buffer) > 0:
                    buffer.popleft()


    # ---------------- DISPLAY ----------------
    cv2.putText(display,
                f"Status: {status}",
                (30,50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,255,255),
                2)

    cv2.putText(display,
                f"Prediction: {last_prediction}",
                (30,100),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (255,255,0),
                3)

    cv2.imshow("Lip Reader", display)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()