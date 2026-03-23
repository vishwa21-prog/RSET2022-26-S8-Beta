import os
import torch
from torch.utils.data import DataLoader
from torchvision import transforms
from torch import nn, optim
from tqdm import tqdm

from preprocessing.dataset_loader import LipReadingDataset
from models.cnn_lstm_classifier import LipReadingClassifier


# ---------------- DEVICE ----------------
device = "cuda" if torch.cuda.is_available() else "cpu"

# ---------------- PATHS ----------------
TRAIN_CSV = r"C:\Silent Speech Recognition Project\Dataset\manifest_custom_train.csv"
VAL_CSV   = r"C:\Silent Speech Recognition Project\Dataset\manifest_custom_test.csv"

GRID_BACKUP = r"C:\Silent Speech Recognition Project\models\checkpoints\backup.pt"

CKPT_DIR = r"C:\Silent Speech Recognition Project\models\checkpoints_classifier"
os.makedirs(CKPT_DIR, exist_ok=True)

# ---------------- CONFIG ----------------
BATCH_SIZE = 8
EPOCHS = 25
LR = 1e-4
MAX_FRAMES = 75


def main():

    print("Device:", device)

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5,0.5,0.5],
                             std=[0.5,0.5,0.5])
    ])

    train_ds = LipReadingDataset(TRAIN_CSV,
                                 max_frames=MAX_FRAMES,
                                 transform=transform)

    val_ds = LipReadingDataset(VAL_CSV,
                               max_frames=MAX_FRAMES,
                               transform=transform)

    num_classes = len(train_ds.words)
    print("Detected words:", train_ds.words)

    train_loader = DataLoader(train_ds,
                              batch_size=BATCH_SIZE,
                              shuffle=True)

    val_loader = DataLoader(val_ds,
                            batch_size=BATCH_SIZE,
                            shuffle=False)

    model = LipReadingClassifier(num_classes=num_classes).to(device)

    # -------- LOAD GRID BACKUP WEIGHTS --------
    print("Loading GRID backbone from backup.pt")
    ckpt = torch.load(GRID_BACKUP, map_location=device)
    old_state = ckpt["model"]

    new_state = model.state_dict()

    # Copy matching layers (CNN + LSTM only)
    for k in new_state.keys():
        if k in old_state and "classifier" not in k:
            new_state[k] = old_state[k]

    model.load_state_dict(new_state)

    # -------- FREEZE MOST OF CNN --------
    for param in model.cnn.parameters():
        param.requires_grad = False

    for name, param in model.cnn.encoder.named_parameters():
        if "layer4" in name:
            param.requires_grad = True

    criterion = nn.CrossEntropyLoss()

    optimizer = optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=LR
    )

    best_acc = 0.0

    # -------- TRAIN LOOP --------
    for epoch in range(1, EPOCHS + 1):

        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for x, y in tqdm(train_loader, desc=f"Epoch {epoch}/{EPOCHS}"):

            x = x.to(device)
            y = y.to(device)

            optimizer.zero_grad()

            logits = model(x)
            loss = criterion(logits, y)

            loss.backward()
            optimizer.step()

            running_loss += loss.item()

            preds = logits.argmax(dim=1)
            correct += (preds == y).sum().item()
            total += y.size(0)

        train_loss = running_loss / len(train_loader)
        train_acc = correct / total

        # -------- VALIDATION --------
        model.eval()
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for x, y in val_loader:
                x = x.to(device)
                y = y.to(device)

                logits = model(x)
                preds = logits.argmax(dim=1)

                val_correct += (preds == y).sum().item()
                val_total += y.size(0)

        val_acc = val_correct / val_total

        print(f"Epoch {epoch} | "
              f"Train Loss: {train_loss:.3f} | "
              f"Train Acc: {train_acc:.3f} | "
              f"Val Acc: {val_acc:.3f}")

        if val_acc > best_acc:
            best_acc = val_acc
            torch.save({
                "model": model.state_dict(),
                "best_acc": best_acc
            }, os.path.join(CKPT_DIR, "best_classifier.pt"))
            print("Saved best classifier")

    print("Training Complete")


if __name__ == "__main__":
    main()