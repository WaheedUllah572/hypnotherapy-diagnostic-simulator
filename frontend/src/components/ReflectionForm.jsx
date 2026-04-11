import { useEffect, useState } from "react";

export default function ReflectionForm({ submission, setSubmission, onSubmit }) {
  const [local, setLocal] = useState({
    chosenApproach: "",
    clientModality: "",
    clientObjective: "",
    clientReassurance: "",
    ...submission
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

      <div>
        <label>QUESTION 1</label>
        <textarea value={local.chosenApproach} onChange={e => update("chosenApproach", e.target.value)} />
      </div>

      <div>
        <label>QUESTION 2</label>
        <textarea value={local.clientModality} onChange={e => update("clientModality", e.target.value)} />
      </div>

      <div>
        <label>QUESTION 3</label>
        <textarea value={local.clientObjective} onChange={e => update("clientObjective", e.target.value)} />
      </div>

      <div>
        <label>QUESTION 4</label>
        <textarea value={local.clientReassurance} onChange={e => update("clientReassurance", e.target.value)} />
      </div>

      <button onClick={handleSubmit}>
        Submit for Tutor Review
      </button>
    </div>
  );
}