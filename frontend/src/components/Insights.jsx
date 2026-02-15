import MetricCard from "./MetricCard";

export default function Insights({ evaluation, onContinue }) {
  const {
    empathyScore = 0,
    structureScore = 0,
    processMatch = false,
    goalMatch = false,
    selectedProcess = "",
    usedTutorHelp = false
  } = evaluation || {};

  // 🧠 Build adaptive educational feedback
  const feedback = [];

  if (!selectedProcess) {
    feedback.push("No therapeutic approach was selected during the session.");
  }

  if (!processMatch) {
    feedback.push(
      "The selected therapeutic process did not fully align with the client’s anxiety presentation. Consider modalities that directly address cognitive patterns and emotional regulation."
    );
  } else {
    feedback.push(
      "Good clinical reasoning — the chosen therapeutic approach aligns well with the client’s anxiety presentation."
    );
  }

  if (!goalMatch) {
    feedback.push(
      "The intervention strategy did not clearly connect to the functional session goal. Aim to link therapeutic techniques directly to the client's real-world outcome."
    );
  } else {
    feedback.push(
      "The selected approach supports the client’s stated goal and functional outcome."
    );
  }

  if (empathyScore < 3) {
    feedback.push(
      "Increase emotional reflection before introducing techniques. Early validation strengthens therapeutic alliance."
    );
  } else if (empathyScore >= 4) {
    feedback.push("Empathy was expressed clearly and supported rapport development.");
  }

  if (structureScore < 3) {
    feedback.push(
      "Session structure could be clearer. Try moving through exploration → clarification → intervention planning."
    );
  } else {
    feedback.push("Session structure followed a logical therapeutic progression.");
  }

  if (usedTutorHelp) {
    feedback.push(
      "Tutor assistance was used during the session. Work toward more independent clinical decision-making."
    );
  }

  return (
    <div className="space-y-8">

      <h3 className="text-lg font-semibold text-slate-900">Tutor Review</h3>

      {/* 📊 METRIC SCORES */}
      <MetricCard title="Empathy" value={empathyScore} />
      <MetricCard title="Clinical Structure" value={structureScore} />
      <MetricCard title="Therapeutic Process Selection" value={processMatch ? 5 : 2} />
      <MetricCard title="Goal Alignment" value={goalMatch ? 5 : 2} />

      {/* 🧠 EDUCATIONAL FEEDBACK */}
      <div className="bg-slate-50 border border-slate-200 rounded-2xl p-5 text-sm text-slate-700 space-y-3 leading-relaxed">
        <div>
          <span className="font-medium">Selected approach:</span>{" "}
          {selectedProcess || "Not selected"}
        </div>

        {feedback.map((item, i) => (
          <p key={i}>• {item}</p>
        ))}
      </div>

      {/* ➡ CONTINUE */}
      {onContinue && (
        <button
          onClick={onContinue}
          className="bg-brand-600 hover:bg-brand-700 text-white px-6 py-2 rounded-xl text-sm font-medium"
        >
          Continue to Diagnostic Review
        </button>
      )}

    </div>
  );
}
