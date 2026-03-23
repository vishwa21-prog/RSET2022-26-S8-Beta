import os

root = "custom_dataset"

for spk in os.listdir(root):
    spk_path = os.path.join(root, spk)
    if not os.path.isdir(spk_path):
        continue

    print("\nSpeaker:", spk)

    for word in os.listdir(spk_path):
        word_path = os.path.join(spk_path, word)

        train_path = os.path.join(word_path, "train")
        test_path = os.path.join(word_path, "test")

        train_count = len(os.listdir(train_path)) if os.path.exists(train_path) else 0
        test_count = len(os.listdir(test_path)) if os.path.exists(test_path) else 0

        print(f"  {word} -> Train: {train_count}, Test: {test_count}")