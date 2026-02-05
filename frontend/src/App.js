import React, { useEffect, useRef, useState } from "react";
import "./App.css";

let audioContext, processor, input, streamRef, pcmChunks = [];

function App() {
  const audioWs = useRef(null);
  const videoWs = useRef(null);
  const videoRef = useRef(null);
  const recorderRef = useRef(null);
  const videoStreamRef = useRef(null);

  const [started, setStarted] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [question, setQuestion] = useState("");
  const [status, setStatus] = useState("");
  const [result, setResult] = useState(null);

  /* ---------------- VIDEO CONTROL ---------------- */
  const startVideoRecording = async () => {
    const ws = new WebSocket("ws://localhost:8000/ws/claim/video");
    videoWs.current = ws;

    const stream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true
    });

    videoStreamRef.current = stream;
    videoRef.current.srcObject = stream;

    const recorder = new MediaRecorder(stream, { mimeType: "video/webm" });

    recorder.ondataavailable = e => {
      if (e.data.size > 0) {
        e.data.arrayBuffer().then(buf => ws.send(buf));
      }
    };

    recorder.start(1000);
    recorderRef.current = recorder;
  };

  const stopVideoRecording = () => {
    recorderRef.current?.stop();
    recorderRef.current = null;

    videoStreamRef.current?.getTracks().forEach(t => t.stop());
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

    await startVideoRecording();
  };

  /* ---------------- AUDIO WS ---------------- */
  useEffect(() => {
    if (!started) return;

    const ws = new WebSocket("ws://localhost:8000/ws/claim/audio");
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
        setStatus("Thank you. You may close this window.");

        // 🔴 THIS IS THE ONLY PLACE VIDEO STOPS
        stopVideoRecording();

        fetch("http://localhost:8000/claim/result")
          .then(res => res.json())
          .then(setResult);

        ws.close();
      }
    };

    audioWs.current = ws;
    return () => ws.close();
  }, [started]);

  /* ---------------- AUDIO RECORD ---------------- */
  const startRecording = async () => {
    if (!started || completed) return;

    streamRef = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioContext = new AudioContext({ sampleRate: 48000 });

    input = audioContext.createMediaStreamSource(streamRef);
    processor = audioContext.createScriptProcessor(4096, 1, 1);
    pcmChunks = [];

    processor.onaudioprocess = e =>
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
    streamRef.getTracks().forEach(t => t.stop());

    const flat = pcmChunks.flatMap(c => Array.from(c));
    const pcm16 = new Int16Array(flat.map(v => v * 32767));

    audioWs.current.send(pcm16.buffer);
    setStatus("Processing…");
  };

  /* ---------------- RESET (UI ONLY) ---------------- */
  const resetInterview = () => {
    setStarted(false);
    setCompleted(false);
    setQuestion("");
    setStatus("");
    setResult(null);
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
        )}

        {completed && result && (
          <div className="result-card">
            <h2>Interview Summary</h2>

            {result.qa.map((item, i) => (
              <div key={i} className="qa-item">
                <strong>Q:</strong> {item.question}<br />
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
