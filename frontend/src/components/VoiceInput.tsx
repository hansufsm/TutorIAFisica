"use client";
import { useState } from "react";
import { Mic, MicOff } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function VoiceInput({
  onTranscript,
}: {
  onTranscript: (t: string) => void;
}) {
  const [rec, setRec] = useState(false);
  const [mr, setMr] = useState<MediaRecorder | null>(null);

  async function start() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks: BlobPart[] = [];
      recorder.ondataavailable = (e) => chunks.push(e.data);
      recorder.onstop = async () => {
        const blob = new Blob(chunks, { type: "audio/webm" });
        const fd = new FormData();
        fd.append("file", blob, "audio.webm");
        try {
          const res = await fetch(`${API}/tutor/transcribe`, {
            method: "POST",
            body: fd,
          });
          if (!res.ok) throw new Error("Transcription failed");
          const { text } = await res.json();
          onTranscript(text);
        } catch (err) {
          console.error("Transcription error:", err);
        }
      };
      recorder.start();
      setMr(recorder);
      setRec(true);
    } catch (err) {
      console.error("Microphone access denied:", err);
    }
  }

  function stop() {
    if (mr) {
      mr.stop();
      mr.stream?.getTracks?.().forEach?.((t) => t.stop?.());
    }
    setRec(false);
  }

  return (
    <button
      onClick={rec ? stop : start}
      className={`p-3 rounded-xl border transition-all ${
        rec
          ? "bg-red-600 border-red-400 animate-pulse"
          : "bg-gray-800 border-gray-700 hover:border-blue-500"
      }`}
      title={rec ? "Parar" : "Falar"}
    >
      {rec ? <MicOff size={18} /> : <Mic size={18} />}
    </button>
  );
}
