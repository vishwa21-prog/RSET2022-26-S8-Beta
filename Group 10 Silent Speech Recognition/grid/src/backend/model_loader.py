import torch
from cnn_lstm_ctc import LipReadingCTC, TextTokenizer
from video_preprocess import preprocess_video
from beam_search_decoder import ctc_beam_search

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_PATH = "models/lipreader_s1_s10.pth"

# -------------------- LOAD MODEL --------------------
def load_model():
    checkpoint = torch.load(MODEL_PATH, map_location=DEVICE)

    tokenizer = TextTokenizer()
    tokenizer.chars = checkpoint["tokenizer_vocab"]
    tokenizer.itos = {i: c for i, c in enumerate(tokenizer.chars)}
    tokenizer.stoi = {c: i for i, c in enumerate(tokenizer.chars)}

    model = LipReadingCTC(vocab_size=len(tokenizer.chars)).to(DEVICE)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    return model, tokenizer

# -------------------- INFERENCE --------------------
def infer_video(video_path, model, tokenizer, beam_width=10):
    frames = preprocess_video(video_path)  # (T, 3, 64,64)
    frames = frames.unsqueeze(0).to(DEVICE)  # (1,T,C,H,W)

    with torch.no_grad():
        log_probs = model(frames)  # (T,1,V)
        log_probs = log_probs.squeeze(1)  # (T,V)

    # ---- USE BEAM SEARCH ----
    prediction = ctc_beam_search(log_probs.cpu(), beam_width, tokenizer)
    return prediction
