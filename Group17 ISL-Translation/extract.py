import pandas as pd
import os
from tqdm import tqdm

def prepare_demo_data(master_csv, video_dir, pose_dir, output_dir, num_samples=1000):
    """
    Filters the master iSign CSV to find valid pairs of videos and pose files.
    Creates a smaller manifest for rapid training/demo.
    """
    if not os.path.exists(master_csv):
        print(f"ERROR: CSV file not found at {master_csv}")
        return

    # 1. Load the master CSV
    df = pd.read_csv(master_csv)
    
    # 2. Shuffle the dataset to get a diverse range of sentences
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    demo_list = []
    count = 0
    
    print(f"Scanning for {num_samples} valid matches in {master_csv}...")
    
    # 3. Iterate and verify file existence
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        if count >= num_samples:
            break
            
        # The unique ID from your CSV
        uid = str(row['uid'])
        
        # Construct expected filenames
        video_name = uid + ".mp4"
        pose_name = uid + ".pose"
        
        video_path = os.path.join(video_dir, video_name)
        pose_path = os.path.join(pose_dir, pose_name)
        
        # Only add to manifest if BOTH files actually exist on the disk
        if os.path.exists(video_path) and os.path.exists(pose_path):
            demo_list.append(row)
            count += 1
            
    if not demo_list:
        print("ERROR: No matching files found! Please check your VIDEO_ROOT and POSE_ROOT paths.")
        return

    # 4. Save the new demo manifest
    demo_df = pd.DataFrame(demo_list)
    os.makedirs(output_dir, exist_ok=True)
    manifest_path = os.path.join(output_dir, "demo_manifest.csv")
    demo_df.to_csv(manifest_path, index=False)
    
    print(f"\nSUCCESS! Created demo manifest with {len(demo_df)} samples.")
    print(f"Manifest saved to: {manifest_path}")

# --- PATH CONFIGURATION ---
# Adjust these paths if your external drive or folders are mounted elsewhere
MASTER_CSV = "/home/elwin/Downloads/iSign_v1.1.csv"
VIDEO_ROOT = "/home/elwin/Downloads/iSign_videos/iSign-videos_v1.1"
POSE_ROOT = "/home/elwin/Downloads/iSign-poses_v1.1"
OUTPUT_DIR = "/home/elwin/Desktop/final_project/final_pjkt/demo_setup"

if __name__ == "__main__":
    prepare_demo_data(MASTER_CSV, VIDEO_ROOT, POSE_ROOT, OUTPUT_DIR)
