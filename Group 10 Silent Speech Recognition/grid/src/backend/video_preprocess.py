

import cv2
import numpy as np
import torch
from typing import Tuple
import mediapipe as mp


MAX_FRAMES = 75
IMG_SIZE = (64, 64)   
MEAN = [0.5, 0.5, 0.5]
STD  = [0.5, 0.5, 0.5]

mp_face_mesh = mp.solutions.face_mesh

def _normalize_tensor(img_tensor: torch.Tensor) -> torch.Tensor:
    """
    img_tensor: (C,H,W) values in [0,1]
    returns normalized tensor (C,H,W)
    """
    for i in range(3):
        img_tensor[i] = (img_tensor[i] - MEAN[i]) / STD[i]
    return img_tensor

def _center_crop_rgb(frame: np.ndarray, out_size: Tuple[int,int]) -> np.ndarray:
    h, w, _ = frame.shape
    ow, oh = out_size
    cx, cy = w // 2, h // 2
    x1 = max(cx - ow//2, 0)
    y1 = max(cy - oh//2, 0)
    x2 = min(x1 + ow, w)
    y2 = min(y1 + oh, h)
    crop = frame[y1:y2, x1:x2]
    
    if crop.shape[0] != oh or crop.shape[1] != ow:
        crop = cv2.resize(crop, (ow, oh))
    return crop

def _crop_mouth_from_landmarks(frame: np.ndarray, landmarks, out_size: Tuple[int,int]) -> np.ndarray:
    """
    landmarks: list of face_landmarks.landmark
    We use key lip indices commonly used in MediaPipe (outer lips).
    """
    h, w, _ = frame.shape

    lip_indices = [61, 291, 0, 17, 13, 14]  
    pts = []
    for idx in lip_indices:
        lm = landmarks[idx]
        x = int(lm.x * w)
        y = int(lm.y * h)
        pts.append((x, y))
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    pad = 10
    x_min = max(min(xs) - pad, 0)
    y_min = max(min(ys) - pad, 0)
    x_max = min(max(xs) + pad, w)
    y_max = min(max(ys) + pad, h)

    # if ROI is degenerate, fallback to center crop
    if x_max - x_min <= 0 or y_max - y_min <= 0:
        return _center_crop_rgb(frame, out_size)

    crop = frame[y_min:y_max, x_min:x_max]
    crop = cv2.resize(crop, out_size)
    return crop

def preprocess_video(video_path: str,
                     max_frames: int = MAX_FRAMES,
                     img_size: Tuple[int,int] = IMG_SIZE) -> torch.Tensor:
    """
    Load video, extract up to max_frames mouth crops (RGB), normalize and return tensor:
        (T, C, H, W) with dtype=torch.float32
    Raises RuntimeError if no frames extracted.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    frames_out = []
    with mp_face_mesh.FaceMesh(static_image_mode=False,
                               max_num_faces=1,
                               min_detection_confidence=0.4,
                               min_tracking_confidence=0.4) as face_mesh:

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Convert to RGB for mediapipe
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)

            if results.multi_face_landmarks and len(results.multi_face_landmarks) > 0:
                # use first face
                face_landmarks = results.multi_face_landmarks[0].landmark
                crop = _crop_mouth_from_landmarks(rgb, face_landmarks, img_size)
            else:
                # fallback center crop
                crop = _center_crop_rgb(rgb, img_size)

            # ensure shape
            if crop is None:
                continue

            # convert to float tensor [0,1], C,H,W
            crop = crop.astype(np.float32) / 255.0
            # opencv format to pytorch format
            crop = np.transpose(crop, (2, 0, 1))  
            tensor = torch.from_numpy(crop)       
            tensor = _normalize_tensor(tensor)
            frames_out.append(tensor)

            if len(frames_out) >= max_frames:
                break

    cap.release()

    if len(frames_out) == 0:
        raise RuntimeError(f"No frames extracted from video: {video_path} (face/mouth detection failed)")

    
    frames_tensor = torch.stack(frames_out)  
    return frames_tensor
