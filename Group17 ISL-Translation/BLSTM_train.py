import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torch.nn.utils.rnn import pad_sequence
from pose_format import Pose
import pandas as pd
import numpy as np
import os
import json
from tqdm import tqdm

# --- 1. HEAVY AUGMENTATION ---
class PoseAugmentor:
    @staticmethod
    def apply(data):
        # Random Rotation (-10 to 10 degrees)
        angle = np.radians(np.random.uniform(-10, 10))
        c, s = np.cos(angle), np.sin(angle)
        rot_matrix = np.array([[c, -s], [s, c]])
        data = np.dot(data, rot_matrix)
        
        # Random Scaling (90% to 110%)
        data *= np.random.uniform(0.9, 1.1)
        
        # Random Jitter (Noise)
        data += np.random.normal(0, 0.002, data.shape)
        return data

# --- 2. DYNAMIC DATASET ---
class DynamicPoseDataset(Dataset):
    def __init__(self, manifest_path, pose_dir):
        self.df = pd.read_csv(manifest_path)
        # Fix for potential NaN/Float label errors
        self.df['text'] = self.df['text'].fillna("missing_label").astype(str)
        self.pose_dir = pose_dir
        
        self.unique_labels = sorted(self.df['text'].unique().tolist())
        self.label_to_id = {label: i for i, label in enumerate(self.unique_labels)}
        
        with open("label_map.json", "w") as f:
            json.dump(self.unique_labels, f)
            
        # 133 WholeBody Landmark Indices
        self.indices = list(range(33)) + list(range(33+468, 33+468+42)) + [33+i for i in [0,4,7,8,10,13,14,17,21,33,37,39,40,46,52,53,54,55,58,61,63,64,65,66,67,70,78,80,81,82,84,87,88,91,93,95,103,105,107,109,127,132,133,136,144,145,146,148,149,150,152,153,154,155,157,158,159,160]]

    def __len__(self): return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        pose_path = os.path.join(self.pose_dir, str(row['uid']) + ".pose")
        
        with open(pose_path, "rb") as f:
            p = Pose.read(f.read())
            # FIX: Convert MaskedArray to standard numpy
            raw_data = np.array(p.body.data)
            data = raw_data[:, 0, self.indices, :2]
            
        # Apply Augmentation
        data = PoseAugmentor.apply(data)
            
        # Normalization (Neck center)
        neck = (data[:, 11, :] + data[:, 12, :]) / 2
        data = (data - neck[:, np.newaxis, :]).reshape(len(data), -1) 
        
        return torch.tensor(data).float(), self.label_to_id[row['text']]

# --- 3. DYNAMIC PADDING LOGIC ---
def collate_fn(batch):
    batch.sort(key=lambda x: len(x[0]), reverse=True)
    sequences, labels = zip(*batch)
    lengths = torch.tensor([len(s) for s in sequences])
    padded_seqs = pad_sequence(sequences, batch_first=True, padding_value=0)
    return padded_seqs, torch.tensor(labels), lengths

# --- 4. MASKED ATTENTION MODEL ---
class AttentionLSTM(nn.Module):
    def __init__(self, input_dim=266, hidden_dim=256, num_classes=1000):
        super(AttentionLSTM, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers=2, batch_first=True, bidirectional=True)
        self.attention = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1)
        )
        self.fc = nn.Linear(hidden_dim * 2, num_classes)

    def forward(self, x, lengths):
        lstm_out, _ = self.lstm(x)
        
        # Masking logic to ignore padding
        mask = torch.arange(x.size(1)).expand(len(lengths), x.size(1)).to(x.device) < lengths.unsqueeze(1)
        attn_logits = self.attention(lstm_out).squeeze(-1)
        attn_logits[~mask] = -float('inf') 
        weights = F.softmax(attn_logits, dim=1).unsqueeze(-1)
        
        context = torch.sum(weights * lstm_out, dim=1)
        return self.fc(context)

# --- 5. TRAINING LOOP ---
def train():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on: {device}")
    
    MANIFEST = "/home/elwin/Desktop/final_project/final_pjkt/demo_setup/demo_manifest.csv"
    POSE_DIR = "/home/elwin/Downloads/iSign-poses_v1.1"
    
    dataset = DynamicPoseDataset(MANIFEST, POSE_DIR)
    loader = DataLoader(dataset, batch_size=16, shuffle=True, collate_fn=collate_fn, pin_memory=True)
    
    model = AttentionLSTM(num_classes=len(dataset.unique_labels)).to(device)
    optimizer = optim.Adam(model.parameters(), lr=0.0005)
    criterion = nn.CrossEntropyLoss()
    scaler = torch.cuda.amp.GradScaler() 

    model.train()
    for epoch in range(100):
        epoch_loss = 0
        for data, target, lengths in tqdm(loader, desc=f"Epoch {epoch+1}"):
            data, target, lengths = data.to(device), target.to(device), lengths.to(device)
            optimizer.zero_grad()
            
            with torch.cuda.amp.autocast():
                output = model(data, lengths)
                loss = criterion(output, target)
            
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            epoch_loss += loss.item()
            
        print(f"Loss: {epoch_loss/len(loader):.4f}")
        
    torch.save(model.state_dict(), "demo_model.pth")
    print("Training Complete! Saved 'demo_model.pth' and 'label_map.json'")

if __name__ == "__main__":
    train()
