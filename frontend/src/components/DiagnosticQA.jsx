import { useState } from "react";

export default function DiagnosticQA({
  processes,
  correctProcess,
  goal,
  evaluation
}) {
  const [answer, setAnswer] = useState("");

  const answeredCorrectly = answer === correctProcess;

  return (
    <div className="space-y-8">
      <h3 className="text-lg font-semibold">Diagnostic Review</h3>

      <div className="bg-slate-50 border rounded-2xl p-5 text-sm">
        <p><strong>Session goal:</strong> {goal}</p>
        <p className="mt-2">
          <strong>Approach used:</strong>{" "}
          {evaluation.selectedProcess || "Not selected"}
        </p>
      </div>

      <div>
        <p className="text-sm mb-2 font-medium">
          Which therapeutic process was MOST appropriate?
        </p>
        <select
          value={answer}
          onChange={e => setAnswer(e.target.value)}
          className="w-full rounded-xl border p-3 text-sm"
        >
          <option value="">Select approach…</option>
          {processes.map(p => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
      </div>

      {answer && (
        <div className={`p-5 rounded-2xl border text-sm ${
          answeredCorrectly
            ? "bg-green-50 border-green-200"
            : "bg-amber-50 border-amber-200"
        }`}>
          {answeredCorrectly
            ? "Correct. CBT targets anxiety-driven cognitive patterns affecting work functioning."
            : "Reconsider. Anxiety linked to thought patterns benefits from cognitive restructuring."}
        </div>
      )}
    </div>
  );
}
