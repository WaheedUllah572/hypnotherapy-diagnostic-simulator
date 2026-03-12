import axios from "axios";
import { useEffect, useState } from "react";

export default function TutorMode({ submission, chatHistory, resetSession }) {
  const [feedback, setFeedback] = useState("Tutor analysing clinical reasoning…");
  const [score, setScore] = useState(null);

  useEffect(() => {
    const fetchFeedback = async () => {
      try {

        const res = await axios.post(
          "http://localhost:8001/tutor-review",
          {
            submission,
            chatHistory
          }
        );

        const formatted = res.data.feedback.replace(/\n/g, "\n\n");

        setFeedback(formatted);
        setScore(res.data.score);

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

      {score && (
        <div className="bg-white border border-slate-200 p-6 rounded-xl text-sm">
          <h4 className="font-semibold mb-4">Clinical Evaluation Score</h4>

          <div className="space-y-2">
            <p>
              Treatment Approach: {score.breakdown.approach ? "✓ Identified" : "⚠ Missing"}
            </p>

            <p>
              Client Modality: {score.breakdown.modality ? "✓ Identified" : "⚠ Missing"}
            </p>

            <p>
              Client Objective: {score.breakdown.objective ? "✓ Identified" : "⚠ Missing"}
            </p>

            <p>
              Safety & Reassurance: {score.breakdown.safety ? "✓ Present" : "⚠ Missing"}
            </p>

            <p className="mt-4 font-semibold">
              Total Score: {score.total} / 4
            </p>
          </div>
        </div>
      )}

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