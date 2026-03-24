import torch
import json
import numpy as np
import os
from pose_format import Pose
from train import AttentionLSTM  # Import the class from your train script

def predict_single_video(pose_path, model_path, label_map_path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 1. Load Label Map
    if not os.path.exists(label_map_path):
        print(f"Error: {label_map_path} not found. Run training first.")
        return
    with open(label_map_path, 'r') as f:
        label_map = json.load(f)
    
    # 2. Initialize and Load Model
    # input_dim 266 = 133 joints * 2 (x, y)
    model = AttentionLSTM(input_dim=266, hidden_dim=256, num_classes=len(label_map)).to(device)
    model.load_state_dict(torch.load(model_path))
    model.eval()

    # 3. Process Pose File
    # Same indices used in training for consistency
    indices = list(range(33)) + list(range(33+468, 33+468+42)) + [33+i for i in [0,4,7,8,10,13,14,17,21,33,37,39,40,46,52,53,54,55,58,61,63,64,65,66,67,70,78,80,81,82,84,87,88,91,93,95,103,105,107,109,127,132,133,136,144,145,146,148,149,150,152,153,154,155,157,158,159,160]]
    
    if not os.path.exists(pose_path):
        print(f"Error: Pose file {pose_path} not found.")
        return

    with open(pose_path, "rb") as f:
        p = Pose.read(f.read())
        # Strip the MaskedArray metadata
        raw_data = np.array(p.body.data)
        # Slicing: [Frames, 1st Person, Selected Joints, X&Y]
        data = raw_data[:, 0, indices, :2]
    
    # Capture length for the Attention Mask
    actual_length = len(data)
    
    # Normalization (Centering relative to shoulders)
    neck = (data[:, 11, :] + data[:, 12, :]) / 2
    data = (data - neck[:, np.newaxis, :]).reshape(actual_length, -1)

    # 4. Model Prediction
    with torch.no_grad():
        # Convert to tensor and add Batch dimension: [1, Frames, 266]
        input_tensor = torch.tensor(data).float().unsqueeze(0).to(device)
        # Convert length to tensor: [1]
        length_tensor = torch.tensor([actual_length]).to(device)
        
        # Forward pass with required 'lengths' argument
        output = model(input_tensor, length_tensor)
        predicted_id = torch.argmax(output, dim=1).item()
    
    return label_map[predicted_id]

# --- EXECUTION ---
if __name__ == "__main__":
    # Test file from your iSign dataset
    TEST_POSE = "/home/elwin/Downloads/iSign-poses_v1.1/1782bea75c7d-7.pose"
    MODEL_WEIGHTS = "demo_model.pth"
    LABEL_JSON = "label_map.json"

    result = predict_single_video(TEST_POSE, MODEL_WEIGHTS, LABEL_JSON)
    
    if result:
        print(f"\nTarget File: {os.path.basename(TEST_POSE)}")
        print(f"Model Prediction: {result}")
