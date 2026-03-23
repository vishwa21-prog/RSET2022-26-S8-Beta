# Silent Speech Recognition System

Silent Speech Recognition (SSR) is a cutting-edge system designed to empower individuals who cannot speak by enabling communication through visual lip movements. This project showcases an intelligent interface for uploading and processing silent speech videos using a deep learning-based recognition model built with CNN + BiLSTM + CTC decoding.

---

## 🚀 Features

- **Hero Section**: Bold introduction to Silent Speech Recognition with a call-to-action button  
- **About & Technology**: Overview of the deep learning pipeline and visual speech recognition architecture  
- **AI-Powered Prediction**: CNN + BiLSTM + CTC model for silent speech decoding  
- **Video Upload Interface**: Dedicated page for users to upload silent speech videos  
- **Automatic Lip Detection**: MediaPipe-based mouth region extraction for precise preprocessing  
- **Responsive Design**: Fully optimized for desktop and mobile devices  

---

## 🛠 Tech Stack

- **React** (with Hooks)  
- **Tailwind CSS** for styling  
- **Flask** for backend API  
- **PyTorch** for deep learning model implementation  
- **MediaPipe & OpenCV** for video preprocessing  
- **Git & GitHub** for version control  
- **VS Code** as the development environment  

---

## 🧠 Training

This folder contains the **training scripts** for both GRID and custom datasets. It includes:

- Manifest file generation  
- Data preprocessing pipelines  
- Model training scripts  

Supports:
- GRID dataset (sentence-level SSR)  
- Custom datasets for specialized use cases  

---

## 🧩 Custom Module

This folder contains the implementation of a **word-level silent speech recognition system** using a custom dataset.

### 🔍 Key Highlights
- Recognizes a **predefined set of words** from lip movements  
- Designed for **real-time prediction**  

### ⚙️ Components
- **Preprocessing**:
  - Lip region extraction using **MediaPipe FaceMesh**  
- **Model**:
  - CNN + BiLSTM architecture  
- **Inference**:
  - Real-time prediction pipeline  

### 🆚 Difference from GRID Model
- Uses **Softmax classifier** (word-level prediction)  
- Instead of **CTC decoding** (sentence-level)

---


### 🧠 Key Difference

- **GRID Model** focuses on **sequence learning** and generates full sentences using CTC decoding  
- **Custom Module** focuses on **classification**, predicting one word from a predefined set  

---

### 📌 When to Use What?

- Use **GRID Model** for:
  - Full sentence prediction  
  - Research and advanced SSR systems  

- Use **Custom Module** for:
  - Real-time applications  
  - Simpler deployment  
  - Limited vocabulary recognition  

---

## 🔧 Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/Geevar12/SSR.git
   cd SSR

2. Install frontend
   ```bash
   npm install

3. Install backend
   ```bash
   pip install -r src/backend/requirements.txt

4. Run backend
   ```bash
   cd src/backend
   python app.py

5. Run frontend
   ```bash
   npm run dev

Link to Dataset
https://drive.google.com/drive/folders/1PbqqlXbSEULilM3PCOOCn3wLuPdMm1Kz?usp=sharing

Link to Models
https://drive.google.com/drive/folders/1auBp1xlloS6Rxj8Iww8-DuQKB8Gs39Xr?usp=sharing


