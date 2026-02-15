import { useEffect, useState } from "react";

export default function ReflectionForm({ submission, setSubmission, onSubmit }) {
  const [local, setLocal] = useState(submission);

  useEffect(() => {
    setLocal(submission);
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

      <textarea
        className="w-full mt-2 p-3 border rounded-xl"
        rows={3}
        value={local.chosenApproach}
        onChange={e => update("chosenApproach", e.target.value)}
        placeholder="Chosen hypnotherapy approach and why"
      />

      <textarea
        className="w-full mt-2 p-3 border rounded-xl"
        rows={3}
        value={local.clientModality}
        onChange={e => update("clientModality", e.target.value)}
        placeholder="Client dominant modality and why"
      />

      <textarea
        className="w-full mt-2 p-3 border rounded-xl"
        rows={3}
        value={local.clientObjective}
        onChange={e => update("clientObjective", e.target.value)}
        placeholder="Client core objective"
      />

      <textarea
        className="w-full mt-2 p-3 border rounded-xl"
        rows={3}
        value={local.clientReassurance}
        onChange={e => update("clientReassurance", e.target.value)}
        placeholder="How you reassured the client and confirmed they were ready to proceed"
      />

      <button onClick={handleSubmit} className="bg-brand-600 text-white px-6 py-2 rounded-xl">
        Submit for Tutor Review
      </button>
    </div>
  );
}