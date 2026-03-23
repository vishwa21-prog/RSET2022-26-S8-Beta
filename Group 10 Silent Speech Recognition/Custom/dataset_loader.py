import os
import csv
import glob
import torch
from torch.utils.data import Dataset
from PIL import Image


class LipReadingDataset(Dataset):
    def __init__(self, csv_path, max_frames=75, transform=None):
        self.samples = []
        self.max_frames = max_frames
        self.transform = transform

        words = set()

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                transcript = row["transcript"].lower()
                words.add(transcript)
                self.samples.append({
                    "frames_dir": row["frames_dir"],
                    "transcript": transcript
                })

        # 🔥 Build word-to-index mapping
        self.words = sorted(list(words))
        self.word2idx = {w: i for i, w in enumerate(self.words)}
        self.idx2word = {i: w for w, i in self.word2idx.items()}

        print("Detected words:", self.words)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]
        frames_dir = sample["frames_dir"]
        transcript = sample["transcript"]

        frame_files = sorted(
            glob.glob(os.path.join(frames_dir, "*.jpg"))
        )

        frames = []

        for f in frame_files[:self.max_frames]:
            try:
                img = Image.open(f).convert("RGB")

                if self.transform:
                    img = self.transform(img)

                frames.append(img)

            except:
                continue

        if len(frames) == 0:
            dummy = torch.zeros(3, 64, 64)
            frames = [dummy.clone() for _ in range(self.max_frames)]

        while len(frames) < self.max_frames:
            frames.append(frames[-1].clone())

        frames = torch.stack(frames)  # (T, C, H, W)

        label = self.word2idx[transcript]

        return frames, label