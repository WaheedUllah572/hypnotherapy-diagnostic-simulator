import { useEffect, useState } from "react";

export default function ReflectionForm({ submission, setSubmission, onSubmit }) {
  const [local, setLocal] = useState({
  chosenApproach: submission.chosenApproach || "",
  clientModality: submission.clientModality || "",
  clientObjective: submission.clientObjective || "",
  clientReassurance: submission.clientReassurance || ""
});
  useEffect(() => {
    setLocal(prev => ({
      ...prev,
      ...submission
    }));
  }, [submission]);

  const update = (field, value) => {
    setLocal(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = () => {
    setSubmission(local);
    onSubmit();
  };

  return (
    <div className="space-y-8">
      <h3 className="text-lg font-semibold text-slate-900">
        End-of-Session Clinical Reflection
      </h3>

      {/* QUESTION 1 */}
      <div>
        <label className="block text-sm font-semibold text-slate-800 mb-2">
          QUESTION 1 — Identify the most appropriate treatment approach and describe what informed this.
        </label>
        <textarea
          className="w-full p-3 border rounded-xl"
          rows={4}
          value={local.chosenApproach}
          onChange={e => update("chosenApproach", e.target.value)}
        />
      </div>

      {/* QUESTION 2 */}
      <div>
        <label className="block text-sm font-semibold text-slate-800 mb-2">
          QUESTION 2 — Describe the client relaxation modality and how you identified it.
        </label>
        <textarea
          className="w-full p-3 border rounded-xl"
          rows={4}
          value={local.clientModality}
          onChange={e => update("clientModality", e.target.value)}
        />
      </div>

      {/* QUESTION 3 */}
      <div>
        <label className="block text-sm font-semibold text-slate-800 mb-2">
          QUESTION 3 — State the client’s core objective.
        </label>
        <textarea
          className="w-full p-3 border rounded-xl"
          rows={3}
          value={local.clientObjective}
          onChange={e => update("clientObjective", e.target.value)}
        />
      </div>

      {/* QUESTION 4 */}
      <div>
        <label className="block text-sm font-semibold text-slate-800 mb-2">
          QUESTION 4 — Demonstrate how you:
        </label>

        <ul className="text-xs text-slate-600 mb-2 list-disc ml-5 space-y-1">
          <li>Clarified suitability and screened for safety concerns</li>
          <li>Responded to client questions</li>
          <li>Provided reassurance and confirmed readiness</li>
        </ul>

      

<textarea
  className="w-full p-3 border rounded-xl"
  rows={5}
  value={local.clientReassurance}
  onChange={e => update("clientReassurance", e.target.value)}
  placeholder="Explain how you assessed safety (risk, medical history), addressed any client concerns, reassured them, and confirmed they were ready to proceed..."
/>      </div>

      <button
        onClick={handleSubmit}
        className="bg-brand-600 text-white px-6 py-2 rounded-xl"
      >
        Submit for Tutor Review
      </button>
    </div>
  );
}