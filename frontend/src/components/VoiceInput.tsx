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
      className={`px-6 py-3 rounded-full transition-all font-semibold text-sm flex items-center justify-center gap-2 min-w-fit font-geist ${
        rec
          ? "bg-rose-600 hover:bg-rose-700 text-white shadow-sm animate-pulse-soft"
          : "bg-slate-100 border border-slate-300 text-slate-900 hover:bg-slate-200 shadow-sm"
      }`}
      title={rec ? "Parar gravação" : "Iniciar gravação"}
    >
      {rec ? (
        <>
          <MicOff size={18} />
          <span className="hidden sm:inline">Parar</span>
        </>
      ) : (
        <>
          <Mic size={18} />
          <span className="hidden sm:inline">Falar</span>
        </>
      )}
    </button>
  );
}
