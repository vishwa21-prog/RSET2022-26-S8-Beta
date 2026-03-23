import React, { useRef, useEffect, useState } from "react";
import { FaceMesh } from "@mediapipe/face_mesh";

const LiveCamera = () => {

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const speaking = useRef(false);
  const silenceFrames = useRef(0);

  const baseline = useRef(null);
  const movementHistory = useRef([]);
  const smoothBox = useRef(null);

  const animationRef = useRef(null);

  const [status, setStatus] = useState("Waiting...");
  const [prediction, setPrediction] = useState(null);
  const [confidence, setConfidence] = useState(null);
  const [lipsDetected, setLipsDetected] = useState(false);

  // =========================
  // CAMERA INIT
  // =========================

  useEffect(() => {

    const startCamera = async () => {

      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 960, height: 720 },
        audio: false
      });

      streamRef.current = stream;
      videoRef.current.srcObject = stream;

      videoRef.current.onloadedmetadata = () => {
        videoRef.current.play();
        initFaceMesh();
      };

    };

    startCamera();

    return () => {

      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }

      cancelAnimationFrame(animationRef.current);

    };

  }, []);

  // =========================
  // MEDIAPIPE INIT
  // =========================

  const initFaceMesh = () => {

    const faceMesh = new FaceMesh({
      locateFile: (file) =>
        `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh@0.4/${file}`
    });

    faceMesh.setOptions({
      maxNumFaces: 1,
      refineLandmarks: true,
      minDetectionConfidence: 0.3,
      minTrackingConfidence: 0.3
    });

    faceMesh.onResults(onResults);

    const processFrame = async () => {

      if (videoRef.current && videoRef.current.readyState === 4) {
        await faceMesh.send({ image: videoRef.current });
      }

      animationRef.current = requestAnimationFrame(processFrame);

    };

    processFrame();

  };

  // =========================
  // FACE RESULTS
  // =========================

  const onResults = (results) => {

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    if (!results.multiFaceLandmarks) {

      setLipsDetected(false);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      return;

    }

    const landmarks = results.multiFaceLandmarks[0];

    drawLipBoundingBox(landmarks);
    detectSpeech(landmarks);

  };

  // =========================
  // ROBUST LIP BOUNDING BOX
  // =========================

  const drawLipBoundingBox = (landmarks) => {

    const canvas = canvasRef.current;
    const video = videoRef.current;
    const ctx = canvas.getContext("2d");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Larger mouth landmark set
    const lipIndices = [
      61,146,91,181,84,17,
      314,405,321,375,291,
      78,95,88,178,87,14,
      317,402,318,324,308
    ];

    const xs = lipIndices.map(i => landmarks[i].x * canvas.width);
    const ys = lipIndices.map(i => landmarks[i].y * canvas.height);

    let xMin = Math.min(...xs);
    let xMax = Math.max(...xs);
    let yMin = Math.min(...ys);
    let yMax = Math.max(...ys);

    // fallback when face is far
    if ((xMax - xMin) < 30) {

      const faceXs = landmarks.map(p => p.x * canvas.width);
      const faceYs = landmarks.map(p => p.y * canvas.height);

      xMin = Math.min(...faceXs);
      xMax = Math.max(...faceXs);
      yMin = Math.min(...faceYs);
      yMax = Math.max(...faceYs);

      // focus lower face (mouth region)
      yMin = yMin + (yMax - yMin) * 0.45;

    }

    const padding = 15;

    const box = {
      x: xMin - padding,
      y: yMin - padding,
      w: (xMax - xMin) + padding * 2,
      h: (yMax - yMin) + padding * 2
    };

    if (!smoothBox.current) {
      smoothBox.current = box;
    } else {

      smoothBox.current.x = 0.6 * smoothBox.current.x + 0.4 * box.x;
      smoothBox.current.y = 0.6 * smoothBox.current.y + 0.4 * box.y;
      smoothBox.current.w = 0.6 * smoothBox.current.w + 0.4 * box.w;
      smoothBox.current.h = 0.6 * smoothBox.current.h + 0.4 * box.h;

    }

    ctx.strokeStyle = "#00FFFF";
    ctx.lineWidth = 3;

    ctx.strokeRect(
      smoothBox.current.x,
      smoothBox.current.y,
      smoothBox.current.w,
      smoothBox.current.h
    );

    setLipsDetected(true);

  };

  // =========================
  // SMART LIP MOTION DETECTOR
  // =========================

  const detectSpeech = (landmarks) => {

    const upperLip = landmarks[13];
    const lowerLip = landmarks[14];
    const chin = landmarks[152];
    const nose = landmarks[1];

    const lipDistance = Math.abs(upperLip.y - lowerLip.y);
    const faceHeight = Math.abs(chin.y - nose.y);

    const normalizedDistance = lipDistance / faceHeight;

    if (baseline.current === null) {
      baseline.current = normalizedDistance;
      return;
    }

    baseline.current =
      0.98 * baseline.current + 0.02 * normalizedDistance;

    const movement = normalizedDistance - baseline.current;

    movementHistory.current.push(movement);

    if (movementHistory.current.length > 5)
      movementHistory.current.shift();

    const avgMovement =
      movementHistory.current.reduce((a,b)=>a+b,0) /
      movementHistory.current.length;

    const START_THRESHOLD = 0.015;
    const STOP_THRESHOLD = 0.008;
    const SILENCE_FRAMES = 12;

    if (avgMovement > START_THRESHOLD) {

      silenceFrames.current = 0;

      if (!speaking.current) {
        startRecording();
      }

    }
    else if (avgMovement < STOP_THRESHOLD) {

      silenceFrames.current++;

      if (silenceFrames.current > SILENCE_FRAMES && speaking.current) {
        stopRecording();
      }

    }

  };

  // =========================
  // START RECORDING
  // =========================

  const startRecording = () => {

    speaking.current = true;

    setStatus("Speaking...");
    setPrediction(null);
    setConfidence(null);

    const recorder = new MediaRecorder(streamRef.current);

    mediaRecorderRef.current = recorder;
    chunksRef.current = [];

    recorder.ondataavailable = (event) => {

      if (event.data.size > 0) {
        chunksRef.current.push(event.data);
      }

    };

    recorder.onstop = sendToBackend;

    recorder.start();

  };

  // =========================
  // STOP RECORDING
  // =========================

  const stopRecording = () => {

    speaking.current = false;
    setStatus("Processing...");

    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }

  };

  // =========================
  // SEND VIDEO TO BACKEND
  // =========================

  const sendToBackend = async () => {

    const blob = new Blob(chunksRef.current, { type:"video/webm" });

    const formData = new FormData();
    formData.append("video", blob, "live.webm");

    try {

      const response = await fetch("http://localhost:10000/predict", {
        method:"POST",
        body:formData
      });

      const data = await response.json();

      setPrediction(data.prediction);
      setConfidence(data.confidence);
      setStatus("Done");

    }
    catch(err) {

      console.error(err);
      setStatus("Backend Error");

    }

  };

  // =========================
  // UI
  // =========================

  return (

    <div className="min-h-screen flex flex-col items-center justify-center bg-black text-white">

      {!lipsDetected &&
        <p className="text-red-400 mb-2">
          Lips Not Detected — Adjust Face Position
        </p>
      }

      <div className="relative">

        <video
          ref={videoRef}
          autoPlay
          playsInline
          className="w-96 h-72 border-2 border-cyan-400 rounded-lg"
        />

        <canvas
          ref={canvasRef}
          className="absolute top-0 left-0 w-96 h-72 pointer-events-none"
        />

      </div>

      <p className="mt-4 text-lg">{status}</p>

      {prediction &&

        <div className="mt-6 bg-gray-900 p-4 rounded-lg text-center">

          <p className="text-cyan-400 text-xl font-bold">
            {prediction}
          </p>

          {confidence &&
            <p className="text-sm mt-2">
              Confidence: {(confidence*100).toFixed(2)}%
            </p>
          }

        </div>

      }

    </div>

  );

};

export default LiveCamera;