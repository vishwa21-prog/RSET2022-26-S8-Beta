import os
import glob
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torch.nn.utils.rnn import pad_sequence, pack_padded_sequence
from sklearn.preprocessing import LabelEncoder

class SmartSignDataset(Dataset):
    def __init__(self, data_dir, max_len=100, augment_factor=10):
        self.data_list = []
        self.raw_labels = []
        self.augment_factor = augment_factor
        
        csv_files = glob.glob(os.path.join(data_dir, "*_cleaned.csv"))
        print(f" Found {len(csv_files)} files. filtering useful keypoints...")
        
        for csv_path in csv_files:
            try:
                # 1. Load Data
                df = pd.read_csv(csv_path)
                
                # Filter useful columns (Hands + Body) to reduce input size
                cols = [c for c in df.columns if ('_x' in c or '_y' in c) and ('_z' not in c)]
                cols = [c for c in cols if 'hand' in c or 'pose' in c or 'body' in c or 'face' in c]
                
                # Load numeric data
                df = df[cols].apply(pd.to_numeric, errors='coerce').fillna(0)
                
                # Force to float32 initially
                base_features = df.values.astype(np.float32)

                if len(base_features) == 0: continue

                # Load Label
                base_name = os.path.basename(csv_path).replace("_cleaned.csv", "")
                label_path = os.path.join(data_dir, f"{base_name}_label.txt")
                
                label = "Unknown"
                if os.path.exists(label_path):
                    with open(label_path, 'r') as f:
                        label = f.read().strip()
                
                # 3. ADD ORIGINAL DATA
                self.add_sample(base_features, label, max_len)
                
                # 4. DATA AUGMENTATION
                for _ in range(augment_factor):
                    aug_features = self.augment_data(base_features)
                    self.add_sample(aug_features, label, max_len)
                    
            except Exception as e:
                print(f"Skipping {csv_path}: {e}")

        self.le = LabelEncoder()
        self.encoded_labels = self.le.fit_transform(self.raw_labels)
        self.num_classes = len(self.le.classes_)
        
        self.input_dim = self.data_list[0].shape[1]
        print(f"   Data Loaded.")
        print(f"   Original Files: {len(csv_files)}")
        print(f"   Total Samples: {len(self.data_list)}")
        print(f"   Input Features: {self.input_dim}")

    def add_sample(self, features, label, max_len):
        if len(features) > max_len:
            indices = np.linspace(0, len(features)-1, max_len).astype(int)
            features = features[indices]
            
        # FIX: Explicitly cast to Float (float32) for PyTorch
        self.data_list.append(torch.tensor(features, dtype=torch.float32))
        self.raw_labels.append(label)

    def augment_data(self, features):
        """Creates a variation of the sign with float32 safety"""
        feat = features.copy()
        
        # Jitter (Noise) - Ensure cast to float32
        noise = np.random.normal(0, 0.005, feat.shape).astype(np.float32)
        feat = feat + noise
        
        # Scaling
        scale = np.random.uniform(0.9, 1.1)
        feat = feat * scale
        
        # Return as float32
        return feat.astype(np.float32)

    def __len__(self):
        return len(self.data_list)

    def __getitem__(self, idx):
        return self.data_list[idx], self.encoded_labels[idx]

def pad_collate_fn(batch):
    batch.sort(key=lambda x: len(x[0]), reverse=True)
    (xx, yy) = zip(*batch)
    lengths = torch.tensor([len(x) for x in xx])
    xx_pad = pad_sequence(xx, batch_first=True, padding_value=0)
    yy = torch.tensor(yy, dtype=torch.long)
    return xx_pad, yy, lengths


#LSTM MODEL

class SignLanguageLSTM(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_classes):
        super(SignLanguageLSTM, self).__init__()
        
        self.lstm = nn.LSTM(
            input_dim, 
            hidden_dim, 
            num_layers=2, 
            batch_first=True, 
            dropout=0.3,
            bidirectional=True 
        )
        
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
            nn.ReLU(),
            nn.BatchNorm1d(64),
            nn.Linear(64, num_classes)
        )

    def forward(self, x, lengths):
        # x is already float32 thanks to the fix in dataset
        packed_x = pack_padded_sequence(x, lengths, batch_first=True)
        packed_out, (hn, cn) = self.lstm(packed_x)
        
        final_fwd = hn[-2, :, :]
        final_bwd = hn[-1, :, :]
        cat_state = torch.cat((final_fwd, final_bwd), dim=1)
        
        out = self.fc(cat_state)
        return out

# training

def train_augmented():
    DATA_PATH = r"C:\Users\elwin\Desktop\Code\Final Project\Dataset\grp dset\processed"
    
    # 1. Load Data
    try:
        dataset = SmartSignDataset(DATA_PATH, augment_factor=15)
    except Exception as e:
        print(e)
        return

    train_loader = DataLoader(dataset, batch_size=32, shuffle=True, collate_fn=pad_collate_fn)
    
    # 2. Setup Model
    model = SignLanguageLSTM(
        input_dim=dataset.input_dim,
        hidden_dim=128,
        num_classes=dataset.num_classes
    )
    
    optimizer = optim.Adam(model.parameters(), lr=0.005) 
    criterion = nn.CrossEntropyLoss()
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=5, factor=0.5)

    print("\n Training with Augmented Data (Float32 Fixed)...")
    
    EPOCHS = 100
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for x, y, lengths in train_loader:
            optimizer.zero_grad()
            
            # Forward pass
            outputs = model(x, lengths)
            loss = criterion(outputs, y)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            _, preds = torch.max(outputs, 1)
            correct += (preds == y).sum().item()
            total += y.size(0)
            
        avg_loss = total_loss / len(train_loader)
        acc = 100 * correct / total
        
        scheduler.step(avg_loss)
        
        # Logging
        if (epoch+1) % 5 == 0 or epoch == 0:
            current_lr = optimizer.param_groups[0]['lr']
            print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {avg_loss:.4f} | Acc: {acc:.2f}% | LR: {current_lr:.5f}")
            
        # Early Stopping check
        if acc >= 99.5:
            print(f"\n Success! Converged at Epoch {epoch+1}")
            break

    torch.save(model.state_dict(), "sign_language_lstm_aug.pth")
    print("Model saved to sign_language_lstm_aug.pth")

if __name__ == "__main__":
    train_augmented()