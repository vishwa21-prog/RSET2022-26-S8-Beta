import os
import csv

DATASET_ROOT = r"C:\Silent Speech Recognition Project\Dataset\custom_processed1"
OUT_TRAIN = r"C:\Silent Speech Recognition Project\Dataset\manifest_custom_train.csv"
OUT_TEST = r"C:\Silent Speech Recognition Project\Dataset\manifest_custom_test.csv"

train_rows = []
test_rows = []

for speaker in sorted(os.listdir(DATASET_ROOT)):

    speaker_path = os.path.join(DATASET_ROOT, speaker)
    if not os.path.isdir(speaker_path):
        continue

    print(f"Processing {speaker}")

    for word in sorted(os.listdir(speaker_path)):

        word_path = os.path.join(speaker_path, word)
        if not os.path.isdir(word_path):
            continue

        for split in ["train", "test"]:

            split_path = os.path.join(word_path, split)
            if not os.path.isdir(split_path):
                continue

            for clip in sorted(os.listdir(split_path)):

                clip_path = os.path.join(split_path, clip)

                if os.path.isdir(clip_path):

                    row = {
                        "frames_dir": clip_path,
                        "transcript": word.lower()
                    }

                    if split == "train":
                        train_rows.append(row)
                    else:
                        test_rows.append(row)

# Write train CSV
with open(OUT_TRAIN, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["frames_dir", "transcript"])
    writer.writeheader()
    writer.writerows(train_rows)

# Write test CSV
with open(OUT_TEST, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["frames_dir", "transcript"])
    writer.writeheader()
    writer.writerows(test_rows)

print("\n================================")
print("Total Train samples:", len(train_rows))
print("Total Test samples :", len(test_rows))
print("================================")