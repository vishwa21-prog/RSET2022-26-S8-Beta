
# ResNet-18 backbone (frozen) + BiLSTM + CTC head
import torch
import torch.nn as nn
import torchvision.models as tvmodels
# ---------------------------
# Character tokenizer for CTC
# ---------------------------
class TextTokenizer:
    """
    Character-level tokenizer for CTC.
    Includes lowercase letters, digits, space, apostrophe.
    Index 0 reserved for CTC blank.
    """
    def __init__(self):
        chars = list("abcdefghijklmnopqrstuvwxyz0123456789 '")
        self.blank = 0
        self.chars = ["<blank>"] + chars
        self.stoi = {ch: i for i, ch in enumerate(self.chars)}
        self.itos = {i: ch for i, ch in enumerate(self.chars)}

    @property
    def vocab_size(self):
        return len(self.chars)

    def text_to_int(self, text: str):
        text = text.lower()
        return [self.stoi[c] for c in text if c in self.stoi]

    def int_to_text(self, ids):
        return "".join(self.itos[i] for i in ids if i != self.blank)
# ---------------------------
# ResNet-18 backbone (frozen per-frame CNN)
# ---------------------------
class ResNetBackbone(nn.Module):
    """
    Use ResNet-18 as per-frame feature extractor.
    CNN is FROZEN so earlier trained features are preserved.
    """
    def __init__(self, out_dim=256, pretrained=True):
        super().__init__()

        # Load ResNet
        try:
            resnet = tvmodels.resnet18(pretrained=pretrained)
        except TypeError:
            resnet = tvmodels.resnet18(weights=tvmodels.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None)

        #Freeze all CNN parameters
        for param in resnet.parameters():
            param.requires_grad = False

        # Remove the final classification layer
        modules = list(resnet.children())[:-1]
        self.encoder = nn.Sequential(*modules)
        feat_dim = resnet.fc.in_features  # typically 512

        # Trainable projection to smaller latent space
        self.proj = nn.Linear(feat_dim, out_dim)

    def forward(self, x):
        # x: (B*T, 3, 64, 64)
        h = self.encoder(x)         
        h = h.flatten(1)            
        h = self.proj(h)            
        return h
# ---------------------------
# CNN + BiLSTM + CTC HEAD
# ---------------------------
class LipReadingCTC(nn.Module):
    """
    Input:  (B, T, 3, 64, 64)
    Output: (T, B, vocab) — log probabilities for CTC
    """
    def __init__(self, cnn_dim=256, rnn_dim=256, num_layers=2, dropout=0.1, vocab_size=40, pretrained_backbone=True):
        super().__init__()

        # Frozen CNN
        self.cnn = ResNetBackbone(out_dim=cnn_dim, pretrained=pretrained_backbone)

        # BiLSTM (trainable!)
        self.bi_lstm = nn.LSTM(
            input_size=cnn_dim,
            hidden_size=rnn_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout,
            bidirectional=True
        )

        # Classification layer → vocabulary tokens
        self.classifier = nn.Linear(rnn_dim * 2, vocab_size)
        self.log_softmax = nn.LogSoftmax(dim=-1)

    def forward(self, x):
        B, T, C, H, W = x.shape
        x = x.reshape(B * T, C, H, W)
        feats = self.cnn(x)             
        feats = feats.reshape(B, T, -1)

        seq, _ = self.bi_lstm(feats)
        logits = self.classifier(seq)
        log_probs = self.log_softmax(logits)

        return log_probs.transpose(0, 1)
# ---------------------------
# Self test
# ---------------------------
if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = TextTokenizer()
    model = LipReadingCTC(vocab_size=tokenizer.vocab_size, pretrained_backbone=False).to(device)

    dummy = torch.randn(2, 75, 3, 64, 64).to(device)
    out = model(dummy)
    print("Output shape:", tuple(out.shape))
    print("Total parameters:", sum(p.numel() for p in model.parameters()))