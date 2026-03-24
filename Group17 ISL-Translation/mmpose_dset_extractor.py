import os
import glob
import pandas as pd
import numpy as np
from tqdm import tqdm
from ultralytics import YOLO
from mmpose.apis import inference_topdown, init_model
from mmpose.utils import register_all_modules

# Register all MMPose modules
register_all_modules()

def process_corpus_to_dset(source_root, target_root):
    # 1. Initialize Models
    # Detection: YOLOv8 (to find the person)
    det_model = YOLO('yolov8n.pt') 
    
    # Pose: RTMPose-m WholeBody (133 joints: Pose + Hands + Face)
    config_file = 'configs/wholebody_2d_keypoint/rtmpose/coco-wholebody/rtmpose-m_8xb64-270e_coco-wholebody-256x192.py'
    checkpoint_file = 'https://download.openmmlab.com/mmpose/v1/projects/rtmpose/rtmpose-m_simcc-coco-wholebody_pt-aic-coco_270e-256x192-8e10f20f_20230123.pth'
    pose_model = init_model(config_file, checkpoint_file, device='cuda:0')

    # 2. Find all images
    image_paths = glob.glob(os.path.join(source_root, "**", "*.jpg"), recursive=True)
    print(f"Found {len(image_paths)} images.")

    for img_path in tqdm(image_paths, desc="Processing to dset"):
        # Create target path
        relative_path = os.path.relpath(img_path, source_root)
        target_csv_path = os.path.join(target_root, relative_path).replace('.jpg', '.csv')
        
        # Ensure the subfolder exists in the target directory
        os.makedirs(os.path.dirname(target_csv_path), exist_ok=True)

        if os.path.exists(target_csv_path):
            continue

        # 3. Detect Person
        det_results = det_model(img_path, verbose=False)[0]
        boxes = det_results.boxes.xyxy.cpu().numpy()
        
        if len(boxes) == 0:
            continue

        # 4. Estimate Pose (WholeBody)
        # Using the largest detected box
        pose_results = inference_topdown(pose_model, img_path, boxes[0:1])
        
        # 5. Extract and Save
        # RTMPose-WholeBody outputs 133 points
        keypoints = pose_results[0].pred_instances.keypoints[0]
        scores = pose_results[0].pred_instances.keypoint_scores[0]
        
        data_dict = {}
        for i, (kp, score) in enumerate(zip(keypoints, scores)):
            data_dict[f'joint_{i}_x'] = [kp[0]]
            data_dict[f'joint_{i}_y'] = [kp[1]]
            data_dict[f'joint_{i}_score'] = [score]
            
        df = pd.DataFrame(data_dict)
        df.to_csv(target_csv_path, index=False)

if __name__ == "__main__":
    SOURCE = "/home/elwin/Desktop/final_project/final_pjkt/Dataset/ISL_CSLRT_Corpus/ISL_CSLRT_Corpus/Frames_Word_Level"
    TARGET = "/home/elwin/Desktop/final_project/final_pjkt/transformer/dset"
    
    process_corpus_to_dset(SOURCE, TARGET)
