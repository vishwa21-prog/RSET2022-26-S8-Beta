import os
import pandas as pd  # FIXED: Proper import
import numpy as np
import pickle
from tqdm import tqdm

def create_sequence_pickle(base_path, output_path):
    dataset = []
    # Get labels and sort them
    labels = sorted([f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))])
    
    print(f"Processing {len(labels)} classes...")

    for label in tqdm(labels):
        label_path = os.path.join(base_path, label)
        
        # Get all CSVs
        csv_files = [f for f in os.listdir(label_path) if f.endswith('.csv')]
        
        # Robust sorting function
        def extract_number(filename):
            nums = ''.join(filter(str.isdigit, filename))
            return int(nums) if nums else 0

        csv_files.sort(key=extract_number)

        video_sequence = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(os.path.join(label_path, csv_file))
                
                # Column names for 133 joints (x and y)
                cols = []
                for i in range(133):
                    cols.extend([f'joint_{i}_x', f'joint_{i}_y'])
                
                if all(col in df.columns for col in cols):
                    # Shape: (133, 2)
                    frame_data = df[cols].values.reshape(133, 2)
                    
                    # --- OPTIONAL: RELATIVE CENTERING ---
                    # Joint 17 is usually the Neck/Chest. 
                    # Centering makes the model care about MOVEment, not screen position.
                    neck = frame_data[17, :]
                    frame_data = frame_data - neck
                    
                    video_sequence.append(frame_data)
            except Exception as e:
                continue
        
        # Save the whole video as one sample
        if len(video_sequence) > 0:
            dataset.append({
                'label': label,
                'data': np.array(video_sequence) # Shape: (Total_Frames, 133, 2)
            })

    with open(output_path, 'wb') as f:
        pickle.dump(dataset, f)
    
    print(f"\nSUCCESS: Created dataset with {len(dataset)} samples.")
    # Show the shape of the first sample to verify
    if len(dataset) > 0:
        print(f"Sample 0 Shape: {dataset[0]['data'].shape}")

# Run
BASE_DIR = "/home/elwin/Desktop/final_project/final_pjkt/transformer/dset"
create_sequence_pickle(BASE_DIR, "isl_mmpose_dataset.pkl")
