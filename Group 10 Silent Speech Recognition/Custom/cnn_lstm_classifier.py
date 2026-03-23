# cnn_lstm_classifier.py
# ResNet-18 backbone + BiLSTM + Word Classification Head

import torch
import torch.nn as nn
import torchvision.models as tvmodels


# ---------------------------
# ResNet-18 backbone (same as before)
# ---------------------------
class ResNetBackbone(nn.Module):
    def __init__(self, out_dim=256, pretrained=True):
        super().__init__()

        try:
            resnet = tvmodels.resnet18(pretrained=pretrained)
        except TypeError:
            resnet = tvmodels.resnet18(
                weights=tvmodels.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
            )

        # Freeze CNN
        for param in resnet.parameters():
            param.requires_grad = False

        modules = list(resnet.children())[:-1]
        self.encoder = nn.Sequential(*modules)
        feat_dim = resnet.fc.in_features  # 512

        self.proj = nn.Linear(feat_dim, out_dim)

    def forward(self, x):
        h = self.encoder(x)
        h = h.flatten(1)
        h = self.proj(h)
        return h


# ---------------------------
# CNN + BiLSTM + Word Classifier
# ---------------------------
class LipReadingClassifier(nn.Module):
    """
    Input:  (B, T, 3, 64, 64)
    Output: (B, num_classes)
    """

    def __init__(self,
                 num_classes,
                 cnn_dim=256,
                 rnn_dim=256,
                 num_layers=2,
                 dropout=0.1,
                 pretrained_backbone=True):
        super().__init__()

        self.cnn = ResNetBackbone(out_dim=cnn_dim,
                                  pretrained=pretrained_backbone)

        self.bi_lstm = nn.LSTM(
            input_size=cnn_dim,
            hidden_size=rnn_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout,
            bidirectional=True
        )

        # Final word classifier
        self.classifier = nn.Linear(rnn_dim * 2, num_classes)

    def forward(self, x):
        B, T, C, H, W = x.shape

        x = x.reshape(B * T, C, H, W)
        feats = self.cnn(x)
        feats = feats.reshape(B, T, -1)

        seq, _ = self.bi_lstm(feats)

        # 🔥 Temporal pooling (mean over time)
        pooled = seq.mean(dim=1)

        logits = self.classifier(pooled)

        return logits


# ---------------------------
# Self test
# ---------------------------
if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"

    model = LipReadingClassifier(num_classes=5).to(device)

    dummy = torch.randn(2, 75, 3, 64, 64).to(device)
    out = model(dummy)

    print("Output shape:", out.shape)
    print("Total parameters:", sum(p.numel() for p in model.parameters()))