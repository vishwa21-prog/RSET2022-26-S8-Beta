import os
import glob
import cv2
import torch
import numpy as np
from torchvision import transforms

from models.cnn_lstm_classifier import LipReadingClassifier
from preprocessing.dataset_loader import LipReadingDataset


# ---------------- CONFIG ----------------
FRAME_FOLDER = r"C:\Silent Speech Recognition Project\Dataset\custom_processed1\speaker 5\pain\test\IMG_2184_MOV"

MODEL_PATH = r"C:\Silent Speech Recognition Project\models\checkpoints_classifier\best_classifier.pt"

TRAIN_CSV = r"C:\Silent Speech Recognition Project\Dataset\manifest_custom_train.csv"

MAX_FRAMES = 75

device = "cuda" if torch.cuda.is_available() else "cpu"


# ---------------- LOAD WORD LIST ----------------
dataset = LipReadingDataset(TRAIN_CSV, max_frames=MAX_FRAMES)
words = dataset.words


# ---------------- LOAD MODEL ----------------
model = LipReadingClassifier(num_classes=len(words)).to(device)

ckpt = torch.load(MODEL_PATH, map_location=device)
model.load_state_dict(ckpt["model"])

model.eval()


# ---------------- TRANSFORM ----------------
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5,0.5,0.5],
                         std=[0.5,0.5,0.5])
])


# ---------------- LOAD FRAMES ----------------
frame_files = sorted(glob.glob(os.path.join(FRAME_FOLDER, "*.jpg")))

frames = []

for f in frame_files:

    img = cv2.imread(f)

    img = cv2.resize(img,(64,64))
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

    frames.append(transform(img))


if len(frames) == 0:
    raise ValueError("No frames found")


# ---------------- RESAMPLE TO 75 ----------------
indices = np.linspace(
    0,
    len(frames)-1,
    MAX_FRAMES
).astype(int)

frames = [frames[i] for i in indices]


# ---------------- MODEL INFERENCE ----------------
x = torch.stack(frames).unsqueeze(0).to(device)

with torch.no_grad():

    logits = model(x)

    probs = torch.softmax(logits, dim=1)

    idx = probs.argmax(dim=1).item()

    confidence = probs[0, idx].item()


print("\nPrediction:", words[idx])
print("Confidence:", round(confidence*100,2), "%")