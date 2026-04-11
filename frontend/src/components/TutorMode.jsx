import axios from "axios";
import { useEffect, useState, useRef } from "react";

export default function TutorMode({ submission, chatHistory, resetSession, client }) {
  const [feedback, setFeedback] = useState("Tutor analysing clinical reasoning…");
  const [score, setScore] = useState(null);
  const [detectedModality, setDetectedModality] = useState(null);
  const hasSubmitted = useRef(false);

  useEffect(() => {
    if (hasSubmitted.current) return;
    hasSubmitted.current = true;

    const fetchFeedback = async (retry = 0) => {
      try {
        const res = await axios.post(
          "https://hypnotherapy-diagnostic-simulator.onrender.com/tutor-review",
          {
            submission,
            chatHistory,
            clientName: client.name
          }
        );

        if (!res || !res.data) {
          throw new Error("Invalid response");
        }

        setFeedback(res.data.feedback || "No feedback available.");
        setScore(res.data.score || null);
        setDetectedModality(res.data.detected_modality || null);

        window.dispatchEvent(new Event("progressUpdated"));

      } catch (err) {
        if (retry < 2) {
          setTimeout(() => fetchFeedback(retry + 1), 2000);
        } else {
          setFeedback("Tutor feedback unavailable.");
        }
      }
    };

    fetchFeedback();
  }, []);

  return (
    <div className="space-y-8">
      <h3 className="text-lg font-semibold text-slate-900">
        Tutor Mode Evaluation
      </h3>

      {score && (
        <div className="bg-white border border-slate-200 p-6 rounded-xl text-sm">
          <p className="font-semibold">
            Total Score: {score.total} / 4
          </p>
        </div>
      )}

      {detectedModality && (
        <div className="bg-white border border-slate-200 p-6 rounded-xl text-sm">
          <p className="font-semibold">
            Client Relaxation Modality: {detectedModality}
          </p>
        </div>
      )}

      {/* ✅ FIXED FEEDBACK DISPLAY */}
      <div className="bg-slate-50 border border-slate-200 p-6 rounded-xl text-sm whitespace-pre-line leading-relaxed">
        {feedback}
      </div>

      <div className="flex justify-end">
        <button
          onClick={resetSession}
          className="bg-slate-700 text-white px-6 py-2 rounded-xl text-sm"
        >
          RESET — Start New Client Session
        </button>
      </div>
    </div>
  );
}