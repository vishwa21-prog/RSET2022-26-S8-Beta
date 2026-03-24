import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Camera, VideoOff, Play, Square, Download } from 'lucide-react';

export default function CameraFeed() {
  const [isActive, setIsActive] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recordedVideoUrl, setRecordedVideoUrl] = useState(null);
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  // Simulate starting the webcam
  const toggleCamera = () => {
    setIsActive(!isActive);
    if (isActive) {
      // If turning off, make sure to stop recording
      if (isRecording) stopRecording();
      setRecordedVideoUrl(null);
    }
  };

  const startRecording = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      chunksRef.current = [];
      const stream = videoRef.current.srcObject;
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'video/webm' });
        const url = URL.createObjectURL(blob);
        setRecordedVideoUrl(url);
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
      setRecordedVideoUrl(null);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const [errorMsg, setErrorMsg] = useState('');

  const startCameraSystem = async () => {
    try {
      setErrorMsg('');
      if (isActive && videoRef.current) {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error("Error accessing camera:", err);
      if (err.name === 'NotAllowedError') {
        setErrorMsg("Camera access was denied. Please click the camera icon in your browser's address bar to allow access.");
      } else if (err.name === 'NotFoundError') {
        setErrorMsg("No camera device was found on this system.");
      } else {
        setErrorMsg("Could not access camera: " + err.message);
      }
      setIsActive(false);
    }
  };

  useEffect(() => {
    if (isActive) {
      startCameraSystem();
    } else {
        // cleanup if inactive
        if (videoRef.current && videoRef.current.srcObject) {
            const tracks = videoRef.current.srcObject.getTracks();
            tracks.forEach(track => track.stop());
            videoRef.current.srcObject = null;
        }
        if (isRecording && mediaRecorderRef.current) {
            mediaRecorderRef.current.stop();
        }
    }

    return () => {
      // final cleanup on unmount or re-render
      if (videoRef.current && videoRef.current.srcObject) {
          const tracks = videoRef.current.srcObject.getTracks();
          tracks.forEach(track => track.stop());
      }
    };
  }, [isActive]);

  return (
    <div style={{ position: 'relative', width: '100%', height: 'calc(100% - 40px)', borderRadius: 'var(--radius-md)', overflow: 'hidden', background: '#000', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      
      {!isActive ? (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px', color: 'var(--text-tertiary)', textAlign: 'center', padding: '0 20px' }}>
          <VideoOff size={48} strokeWidth={1.5} color={errorMsg ? 'var(--error)' : 'currentColor'} />
          <p>{errorMsg || "Camera feed inactive"}</p>
          <button className="btn btn-primary" onClick={toggleCamera}>
            <Camera size={18} /> Enable Camera
          </button>
        </div>
      ) : (
        <>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            style={{
              position: 'absolute',
              inset: 0,
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              transform: 'scaleX(-1)', // Mirror effect for webcams
            }}
          />
          
          {/* Tracking UI Overlay (Mediapipe Simulation) */}
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{ position: 'absolute', inset: 0, zIndex: 10, pointerEvents: 'none' }}
          >
            {/* Box corners */}
            <div style={{ position: 'absolute', top: 20, left: 20, width: 30, height: 30, borderTop: '2px solid var(--accent-primary)', borderLeft: '2px solid var(--accent-primary)' }}></div>
            <div style={{ position: 'absolute', top: 20, right: 20, width: 30, height: 30, borderTop: '2px solid var(--accent-primary)', borderRight: '2px solid var(--accent-primary)' }}></div>
            <div style={{ position: 'absolute', bottom: 20, left: 20, width: 30, height: 30, borderBottom: '2px solid var(--accent-primary)', borderLeft: '2px solid var(--accent-primary)' }}></div>
            <div style={{ position: 'absolute', bottom: 20, right: 20, width: 30, height: 30, borderBottom: '2px solid var(--accent-primary)', borderRight: '2px solid var(--accent-primary)' }}></div>
            
            {/* Scanning line animation */}
            {isRecording && (
                <motion.div
                animate={{
                    top: ['10%', '90%', '10%'],
                    opacity: [0.5, 0.8, 0.5]
                }}
                transition={{
                    duration: 3,
                    repeat: Infinity,
                    ease: 'linear'
                }}
                style={{
                    position: 'absolute',
                    left: '5%',
                    right: '5%',
                    height: '2px',
                    background: 'linear-gradient(90deg, transparent, var(--accent-secondary), transparent)',
                    boxShadow: '0 0 10px var(--accent-secondary)'
                }}
                />
            )}
          </motion.div>

          <div style={{ position: 'absolute', bottom: 20, display: 'flex', gap: '12px', zIndex: 20, alignItems: 'center' }}>
            {!isRecording ? (
                <button className="btn btn-primary" onClick={startRecording} style={{ background: 'var(--error)' }}>
                  <Play size={18} fill="currentColor" /> Record Sign
                </button>
            ) : (
                <button className="btn" onClick={stopRecording} style={{ background: 'rgba(239, 68, 68, 0.2)', color: 'var(--error)', border: '1px solid rgba(239, 68, 68, 0.5)' }}>
                  <Square size={18} fill="currentColor" /> Stop Recording
                </button>
            )}
            
            {recordedVideoUrl && !isRecording && (
                <a href={recordedVideoUrl} download="sign_recording.webm" className="btn btn-secondary">
                  <Download size={18} /> Save Video
                </a>
            )}

            <button className="btn btn-secondary" style={{ marginLeft: '12px' }} onClick={toggleCamera}>
              Turn Off
            </button>
          </div>
          
          {/* Recording indicator */}
          {isRecording && (
            <div style={{ position: 'absolute', top: 20, right: 20, zIndex: 20, display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(0,0,0,0.5)', padding: '4px 12px', borderRadius: '20px', fontSize: '0.85rem' }}>
                <div className="status-dot recording"></div>
                REC
            </div>
          )}
        </>
      )}
    </div>
  );
}
