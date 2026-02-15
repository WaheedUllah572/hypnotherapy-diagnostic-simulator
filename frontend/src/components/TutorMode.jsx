import axios from "axios";
import { useEffect, useState } from "react";

export default function TutorMode({ submission, chatHistory }) {
  const [feedback, setFeedback] = useState("Tutor analysing clinical reasoning…");

  useEffect(() => {
    const fetchFeedback = async () => {
      try {
        const res = await axios.post("http://127.0.0.1:8001/tutor-review", {
          submission,
          chatHistory
        });
        setFeedback(res.data.feedback);
      } catch {
        setFeedback("Tutor feedback unavailable.");
      }
    };

    fetchFeedback();
  }, [submission, chatHistory]);

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-slate-900">
        Tutor Mode Evaluation
      </h3>
      <div className="bg-slate-50 border p-5 rounded-xl text-sm leading-relaxed">
        {feedback}
      </div>
    </div>
  );
}