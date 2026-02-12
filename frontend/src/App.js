

import React, { useEffect, useRef, useState } from "react";
import "./App.css";

let audioContext, processor, input, streamRef, pcmChunks = [];

function App() {
  const audioWs = useRef(null);
  const videoWs = useRef(null);
  const videoRef = useRef(null);
  const recorderRef = useRef(null);
  const videoStreamRef = useRef(null);

  // 🔴 ADD THIS
  const locationRef = useRef(null);

  const [started, setStarted] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [question, setQuestion] = useState("");
  const [status, setStatus] = useState("");
  const [result, setResult] = useState(null);
  const [location, setLocation] = useState(null);

const BASE_URL = process.env.REACT_APP_API_BASE;
const WS_BASE = BASE_URL.replace("https", "wss");

  /* ---------------- LOCATION ---------------- */
  const getLocation = () => {
    return new Promise((resolve) => {
      if (!navigator.geolocation) {
        resolve("Location not supported");
        return;
      }

      navigator.geolocation.getCurrentPosition(
        async (pos) => {
          const { latitude, longitude } = pos.coords;

          try {
            const res = await fetch(
              `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`
            );
            const data = await res.json();

            resolve(
              `${data.address.city || data.address.town || data.address.village || ""}, ` +
              `${data.address.state || ""}, ` +
              `${data.address.country || ""}`
            );
          } catch {
            resolve(`${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);
          }
        },
        () => resolve("Location access denied")
      );
    });
  };

  /* ---------------- VIDEO ---------------- */
  const startVideoRecording = async () => {
    const ws = new WebSocket(`${WS_BASE}/ws/claim/video`);

    videoWs.current = ws;

    const stream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true
    });

    videoStreamRef.current = stream;
    videoRef.current.srcObject = stream;

    const recorder = new MediaRecorder(stream, { mimeType: "video/webm" });

    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) {
        e.data.arrayBuffer().then((buf) => ws.send(buf));
      }
    };

    recorder.start(1000);
    recorderRef.current = recorder;
  };

  const stopVideoRecording = () => {
    recorderRef.current?.stop();
    recorderRef.current = null;

    videoStreamRef.current?.getTracks().forEach((t) => t.stop());
    videoStreamRef.current = null;

    videoWs.current?.close();
    videoWs.current = null;
  };

  /* ---------------- START INTERVIEW ---------------- */
  const startInterview = async () => {
    setStarted(true);
    setCompleted(false);
    setQuestion("Connecting...");
    setStatus("");
    setResult(null);

    const loc = await getLocation();

    // 🔴 STORE IN BOTH STATE AND REF
    setLocation(loc);
    locationRef.current = loc;

    await startVideoRecording();
  };

  /* ---------------- AUDIO WS ---------------- */
  useEffect(() => {
    if (!started) return;

    const ws = new WebSocket(`${WS_BASE}/ws/claim/audio`);

    ws.binaryType = "arraybuffer";

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);

      if (data.type === "question") {
        setQuestion(data.question);
        setStatus("");
      }

      if (data.type === "completed") {
        setCompleted(true);
        setQuestion("Interview completed");
        setStatus("Thank you.");

        stopVideoRecording();

        fetch(`${BASE_URL}/claim/result`)

          .then((res) => res.json())
          .then(setResult);

        // 🔴 USE REF, NOT STATE
        fetch(`${BASE_URL}/claim/upload`, {

          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            location: locationRef.current
          })
        });

        ws.close();
      }
    };

    audioWs.current = ws;
    return () => ws.close();

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [started]);

  /* ---------------- AUDIO ---------------- */
  const startRecording = async () => {
    if (!started || completed) return;

    streamRef = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioContext = new AudioContext({ sampleRate: 48000 });

    input = audioContext.createMediaStreamSource(streamRef);
    processor = audioContext.createScriptProcessor(4096, 1, 1);
    pcmChunks = [];

    processor.onaudioprocess = (e) =>
      pcmChunks.push(new Float32Array(e.inputBuffer.getChannelData(0)));

    input.connect(processor);
    processor.connect(audioContext.destination);
    setStatus("Listening…");
  };

  const stopRecording = () => {
    if (!started || completed) return;

    processor.disconnect();
    input.disconnect();
    audioContext.close();
    streamRef.getTracks().forEach((t) => t.stop());

    const flat = pcmChunks.flatMap((c) => Array.from(c));
    const pcm16 = new Int16Array(flat.map((v) => v * 32767));

    audioWs.current.send(pcm16.buffer);
    setStatus("Processing…");
  };

  const resetInterview = () => {
    setStarted(false);
    setCompleted(false);
    setQuestion("");
    setStatus("");
    setResult(null);
    setLocation(null);
    locationRef.current = null;
  };

  return (
    <div className="page">
      <div className="container">
        <h1 className="title">ClaimSure AI</h1>
        <p className="subtitle">Automated Insurance Claim Interview</p>

        {!started && (
          <div className="start-box">
            <button className="primary-btn" onClick={startInterview}>
              Start Interview
            </button>
          </div>
        )}

        {started && (
          <>
            {location && <div className="location">📍 {location}</div>}

            <div className="card">
              <div className="video-box">
                <video ref={videoRef} autoPlay muted playsInline />
                <span className="video-label">Identity Verification</span>
              </div>

              <div className="interview-box">
                <div className="question">{question}</div>

                <button
                  className="mic-btn"
                  disabled={completed}
                  onMouseDown={startRecording}
                  onMouseUp={stopRecording}
                >
                  Hold to Speak
                </button>

                <div className="status">{status}</div>
              </div>
            </div>
          </>
        )}

        {completed && result && (
          <div className="result-card">
            <h2>Interview Summary</h2>

            {result.qa.map((item, i) => (
              <div key={i} className="qa-item">
                <strong>Q:</strong> {item.question}
                <br />
                <strong>A:</strong> {item.answer}
              </div>
            ))}

            <button className="secondary-btn" onClick={resetInterview}>
              Start New Interview
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
