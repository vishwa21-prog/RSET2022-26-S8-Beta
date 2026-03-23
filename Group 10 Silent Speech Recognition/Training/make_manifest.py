import os
import csv
from glob import glob

VIDEO_DIR = r"C:\Silent Speech Recognition Project\Dataset\s15video\s15"
ALIGN_DIR = r"C:\Silent Speech Recognition Project\Dataset\align15\align"
FRAMES_BASE = r"C:\Silent Speech Recognition Project\Dataset\s15_processed"
OUT_CSV = r"C:\Silent Speech Recognition Project\Dataset\manifest_s15.csv"



os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)

def read_alignment(base_name):
    """Reads GRID alignment file and returns a transcript string (words only)."""
    
    for ext in (".align", ".txt", ".lab"):
        path = os.path.join(ALIGN_DIR, base_name + ext)
        if os.path.isfile(path):
            words = []
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    parts = line.strip().split()
                    # Expect lines like: start end label
                    if len(parts) >= 3:
                        label = parts[-1]
                        if label.lower() not in {"sil", "sp"}:
                            words.append(label)
            return " ".join(words)
    return ""  # no alignment found

rows = []
mpg_files = sorted([f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(".mpg")])

for fname in mpg_files:
    base = os.path.splitext(fname)[0]
    video_path = os.path.join(VIDEO_DIR, fname)
    frames_dir = os.path.join(FRAMES_BASE, base)  # where your frames were saved
    transcript = read_alignment(base)

    if not os.path.isdir(frames_dir):
        # frames not found (maybe detection failed) — skip
        continue

    rows.append({
        "id": base,
        "video_path": video_path,
        "frames_dir": frames_dir,
        "transcript": transcript
    })

# Write CSV
with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "video_path", "frames_dir", "transcript"])
    writer.writeheader()
    writer.writerows(rows)

print(f" Wrote {len(rows)} entries to {OUT_CSV}")
