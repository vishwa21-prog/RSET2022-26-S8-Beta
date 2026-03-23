import os
import argparse
import torch
from torch.utils.data import DataLoader
from torchvision import transforms
from torch import nn, optim
from tqdm import tqdm

from preprocessing.dataset_loader import LipReadingDataset
from models.cnn_lstm_ctc import LipReadingCTC, TextTokenizer

# ---------------- DEVICE ----------------
device = "cuda" if torch.cuda.is_available() else "cpu"

# ---------------- ARGUMENTS ----------------
parser = argparse.ArgumentParser()
parser.add_argument("--epochs", type=int, default=20)
parser.add_argument("--resume_from", type=str, default=None)
args = parser.parse_args()

# ---------------- PATHS ----------------
TRAIN_CSV = r"C:\Silent Speech Recognition Project\Dataset\manifest_custom_train.csv"
VAL_CSV   = r"C:\Silent Speech Recognition Project\Dataset\manifest_custom_test.csv"

CKPT_DIR = r"C:\Silent Speech Recognition Project\models\checkpoints"
os.makedirs(CKPT_DIR, exist_ok=True)

# ---------------- TRAIN CONFIG ----------------
BATCH_SIZE = 4
VAL_BATCH_SIZE = 4
EPOCHS = args.epochs
LR = 1e-5
WEIGHT_DECAY = 1e-4
MAX_FRAMES = 75
RESUME_CKPT = args.resume_from


# ---------------- CER ----------------
def cer(ref, hyp):
    R, H = list(ref), list(hyp)
    dp = [[0]*(len(H)+1) for _ in range(len(R)+1)]

    for i in range(len(R)+1): dp[i][0] = i
    for j in range(len(H)+1): dp[0][j] = j

    for i in range(1,len(R)+1):
        for j in range(1,len(H)+1):
            cost = 0 if R[i-1]==H[j-1] else 1
            dp[i][j] = min(dp[i-1][j]+1,
                           dp[i][j-1]+1,
                           dp[i-1][j-1]+cost)
    return dp[-1][-1]


# ---------------- COLLATE ----------------
def collate_fn(batch, tokenizer):
    frames_list, targets_list = [], []
    input_lengths, target_lengths = [], []
    texts = []

    for frames, text in batch:
        T = min(frames.shape[0], MAX_FRAMES)
        frames = frames[:T]

        frames_list.append(frames)
        input_lengths.append(T)

        tgt = tokenizer.text_to_int(text)
        tgt = torch.tensor(tgt, dtype=torch.long)
        targets_list.append(tgt)
        target_lengths.append(len(tgt))

        texts.append(text)

    maxT = max(input_lengths)
    padded = []

    for fr in frames_list:
        if fr.shape[0] < maxT:
            pad = torch.zeros((maxT - fr.shape[0],) + fr.shape[1:], dtype=fr.dtype)
            fr = torch.cat([fr, pad], dim=0)
        padded.append(fr)

    x = torch.stack(padded)
    y = torch.cat(targets_list)

    return x, y, torch.tensor(input_lengths), torch.tensor(target_lengths), texts


# ---------------- MAIN ----------------
def main():

    print(f"Device: {device}")
    print(f"Epochs: {EPOCHS}")

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

    print(f"Train samples: {len(train_ds)}")
    print(f"Test samples : {len(val_ds)}")

    tokenizer = TextTokenizer()

    train_loader = DataLoader(
        train_ds,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
        collate_fn=lambda b: collate_fn(b, tokenizer)
    )

    val_loader = DataLoader(
        val_ds,
        batch_size=VAL_BATCH_SIZE,
        shuffle=False,
        num_workers=0,
        collate_fn=lambda b: collate_fn(b, tokenizer)
    )

    model = LipReadingCTC(vocab_size=tokenizer.vocab_size).to(device)

    # -------- FREEZE ENTIRE CNN --------
    for param in model.cnn.parameters():
        param.requires_grad = False

    # -------- UNFREEZE ONLY layer4 --------
    for name, param in model.cnn.encoder.named_parameters():
        if "layer4" in name:
            param.requires_grad = True

    # -------- LOAD WEIGHTS BUT RESET EPOCH --------
    best_val_cer = 1e9
    start_epoch = 1

    if RESUME_CKPT and os.path.isfile(RESUME_CKPT):
        print(f"Loading weights from {RESUME_CKPT}")
        ckpt = torch.load(RESUME_CKPT, map_location=device)
        model.load_state_dict(ckpt["model"])
        best_val_cer = ckpt.get("best_val_cer", best_val_cer)
        start_epoch = 1  # 🔥 RESET EPOCH COUNTER

    # -------- LOSS --------
    ctc_loss = nn.CTCLoss(blank=tokenizer.blank, zero_infinity=True)

    optimizer = optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=LR,
        weight_decay=WEIGHT_DECAY
    )

    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="min",
        patience=5
    )

    # -------- TRAINING LOOP --------
    for epoch in range(start_epoch, EPOCHS + 1):

        model.train()
        running_loss = 0.0

        for x, y, in_lens, tgt_lens, _ in tqdm(train_loader,
                                               desc=f"Epoch {epoch}/{EPOCHS}"):

            x, y = x.to(device), y.to(device)
            in_lens, tgt_lens = in_lens.to(device), tgt_lens.to(device)

            optimizer.zero_grad()

            log_probs = model(x)
            loss = ctc_loss(log_probs, y, in_lens, tgt_lens)

            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        train_loss = running_loss / len(train_loader)

        # -------- VALIDATION --------
        model.eval()
        total_cer = 0.0
        total_chars = 0

        with torch.no_grad():
            for x, _, in_lens, _, texts in val_loader:

                x = x.to(device)
                in_lens = in_lens.to(device)

                lp = model(x)
                pred = lp.argmax(-1).transpose(0,1)

                for i in range(pred.size(0)):
                    seq = pred[i][:in_lens[i]].tolist()

                    out, prev = [], None
                    for t in seq:
                        if t != tokenizer.blank and t != prev:
                            out.append(tokenizer.itos[t])
                        prev = t

                    hyp = "".join(out)
                    ref = texts[i].lower()

                    total_cer += cer(ref, hyp)
                    total_chars += len(ref)

        val_cer = total_cer / max(1, total_chars)

        print(f"Epoch {epoch} | Train Loss: {train_loss:.3f} | Test CER: {val_cer:.4f}")

        scheduler.step(val_cer)

        # Save checkpoint
        torch.save({
            "model": model.state_dict(),
            "epoch": epoch,
            "best_val_cer": best_val_cer
        }, os.path.join(CKPT_DIR, f"epoch{epoch:02d}.pt"))

        if val_cer < best_val_cer:
            best_val_cer = val_cer
            torch.save({
                "model": model.state_dict(),
                "epoch": epoch,
                "best_val_cer": best_val_cer
            }, os.path.join(CKPT_DIR, "best.pt"))
            print("Saved best model")

    print("Training Complete")


if __name__ == "__main__":
    main()