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
      className={`p-3 rounded-xl transition-all font-semibold text-sm flex items-center justify-center gap-2 min-w-fit ${
        rec
          ? "bg-gradient-to-r from-red-600 to-red-500 hover:from-red-500 hover:to-red-400 shadow-lg shadow-red-500/30 animate-pulse-subtle border border-red-400/50"
          : "bg-slate-800/60 border border-slate-700 hover:bg-slate-700/60 hover:border-slate-600 shadow-md hover:shadow-lg hover:shadow-blue-500/10"
      }`}
      title={rec ? "Parar gravação (Esc)" : "Iniciar gravação"}
    >
      {rec ? (
        <>
          <MicOff size={18} />
          <span className="hidden sm:inline text-xs">Parar</span>
        </>
      ) : (
        <>
          <Mic size={18} />
          <span className="hidden sm:inline text-xs">Falar</span>
        </>
      )}
    </button>
  );
}
