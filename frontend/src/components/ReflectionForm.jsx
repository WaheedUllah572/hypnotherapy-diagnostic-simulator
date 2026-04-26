import { useEffect, useState } from "react";

export default function ReflectionForm({ submission, setSubmission, onSubmit }) {

  const [local, setLocal] = useState({
    chosenApproach: "",
    clientModality: "",
    clientObjective: "",
    clientReassurance: ""
  });

  useEffect(() => {
    if (submission) {
      setLocal({
        chosenApproach: submission.chosenApproach || "",
        clientModality: submission.clientModality || "",
        clientObjective: submission.clientObjective || "",
        clientReassurance: submission.clientReassurance || ""
      });
    }
  }, [submission]);

  const update = (field, value) => {
    setLocal(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = () => {
    setSubmission(local);
    onSubmit();
  };

  return (
    <div className="bg-white p-6 rounded-xl space-y-8">

      <h3 className="text-lg font-semibold text-slate-900">
        End-of-Session Clinical Reflection
      </h3>

      {/* Q1 */}
      <div>
        <label className="block text-sm font-semibold text-slate-800 mb-2">
          QUESTION 1 — Identify the most appropriate treatment approach and describe what informed this.
        </label>
        <textarea className="w-full p-3 border rounded-xl" rows={4}
          value={local.chosenApproach || ""}
          onChange={e => update("chosenApproach", e.target.value)}
        />
      </div>

      {/* Q2 */}
      <div>
        <label className="block text-sm font-semibold text-slate-800 mb-2">
          QUESTION 2 — Describe the client relaxation modality and how you identified it.
        </label>
        <textarea className="w-full p-3 border rounded-xl" rows={4}
          value={local.clientModality || ""}
          onChange={e => update("clientModality", e.target.value)}
        />
      </div>

      {/* Q3 */}
      <div>
        <label className="block text-sm font-semibold text-slate-800 mb-2">
          QUESTION 3 — State the client’s core objective.
        </label>
        <textarea className="w-full p-3 border rounded-xl" rows={3}
          value={local.clientObjective || ""}
          onChange={e => update("clientObjective", e.target.value)}
        />
      </div>

      {/* ✅ Q4 — EXACT SAME STRUCTURE */}
      <div>
        <label className="block text-sm font-semibold text-slate-800 mb-2">
          QUESTION 4 — Demonstrate how you clarified suitability, responded to the client, and confirmed readiness.
        </label>

        <textarea
          className="w-full p-3 border rounded-xl"
          rows={5}
          value={local.clientReassurance || ""}
          onChange={e => update("clientReassurance", e.target.value)}
          placeholder="Explain how you assessed safety, reassured the client, and confirmed readiness..."
        />
      </div>

      <button
        onClick={handleSubmit}
        className="bg-brand-600 text-white px-6 py-2 rounded-xl"
      >
        Submit for Tutor Review
      </button>

    </div>
  );
}