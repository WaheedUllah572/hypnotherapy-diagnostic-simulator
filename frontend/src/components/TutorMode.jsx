import axios from "axios";
import { useEffect, useState } from "react";

export default function TutorMode({ submission, chatHistory, resetSession }) {
  const [feedback, setFeedback] = useState("Tutor analysing clinical reasoning…");

  useEffect(() => {
    const fetchFeedback = async () => {
      try {
        const res = await axios.post(
          "https://hypnotherapy-diagnostic-simulator.onrender.com/tutor-review",
          {
            submission,
            chatHistory
          }
        );

        // Improved formatting spacing
        const formatted = res.data.feedback
          .replace(/\n/g, "\n\n");

        setFeedback(formatted);
      } catch {
        setFeedback("Tutor feedback unavailable.");
      }
    };

    fetchFeedback();
  }, [submission, chatHistory]);

  return (
    <div className="space-y-8">
      <h3 className="text-lg font-semibold text-slate-900">
        Tutor Mode Evaluation
      </h3>

      <div className="bg-slate-50 border border-slate-200 p-6 rounded-xl text-sm leading-relaxed whitespace-pre-line">
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