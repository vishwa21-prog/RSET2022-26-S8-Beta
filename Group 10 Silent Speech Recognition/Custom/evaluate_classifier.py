import torch
from torch.utils.data import DataLoader
from torchvision import transforms
from tqdm import tqdm

from preprocessing.dataset_loader import LipReadingDataset
from models.cnn_lstm_classifier import LipReadingClassifier


# ---------------- CONFIG ----------------
MODEL_PATH = r"C:\Silent Speech Recognition Project\models\checkpoints_classifier\best_classifier.pt"
TEST_CSV = r"C:\Silent Speech Recognition Project\Dataset\manifest_custom_test.csv"
MAX_FRAMES = 75
BATCH_SIZE = 8

device = "cuda" if torch.cuda.is_available() else "cpu"


def main():

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5,0.5,0.5],
                             std=[0.5,0.5,0.5])
    ])

    # Load test dataset
    test_ds = LipReadingDataset(TEST_CSV,
                                max_frames=MAX_FRAMES,
                                transform=transform)

    test_loader = DataLoader(test_ds,
                             batch_size=BATCH_SIZE,
                             shuffle=False)

    print("Detected words:", test_ds.words)

    # Load model
    model = LipReadingClassifier(num_classes=len(test_ds.words)).to(device)
    checkpoint = torch.load(MODEL_PATH, map_location=device)
    model.load_state_dict(checkpoint["model"])
    model.eval()

    correct = 0
    total = 0

    print("\n--- Detailed Predictions ---\n")

    with torch.no_grad():
        for x, y in tqdm(test_loader, desc="Evaluating"):
            x = x.to(device)
            y = y.to(device)

            logits = model(x)
            probs = torch.softmax(logits, dim=1)
            preds = probs.argmax(dim=1)

            for i in range(x.size(0)):
                pred_idx = preds[i].item()
                true_idx = y[i].item()

                pred_word = test_ds.idx2word[pred_idx]
                true_word = test_ds.idx2word[true_idx]

                confidence = probs[i, pred_idx].item()

                if pred_idx == true_idx:
                    print(f"✓ True: {true_word:<10} | Pred: {pred_word:<10} | Conf: {confidence:.3f}")
                else:
                    print(f"✗ True: {true_word:<10} | Pred: {pred_word:<10} | Conf: {confidence:.3f}")

            correct += (preds == y).sum().item()
            total += y.size(0)

    accuracy = correct / total

    print("\n----------------------------")
    print("Final Test Accuracy:", round(accuracy * 100, 2), "%")
    print("----------------------------")


if __name__ == "__main__":
    main()