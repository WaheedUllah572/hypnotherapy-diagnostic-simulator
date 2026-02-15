export default function Sidebar({ client }) {
  return (
    <div className="space-y-8 text-sm">

      {/* CLIENT PROFILE */}
      <div>
        <h3 className="text-sm font-semibold text-slate-900 mb-2">
          Client Profile
        </h3>
        <div className="p-4 bg-slate-100 rounded-xl border">
          <p className="font-medium text-slate-800">
            {client.name}
          </p>
          <p className="text-slate-600 text-xs mt-1">
            “{client.problem}”
          </p>
        </div>
      </div>

      {/* TRAINING GUIDANCE */}
      <div>
        <h4 className="text-sm font-semibold text-slate-900 mb-2">
          Training Guidance
        </h4>
        <div className="space-y-3 text-xs text-slate-600 leading-relaxed">

          <p>
            Your role is to act as the therapist. The simulator will act as the client.
          </p>

          <p>
            You are currently in the <strong>pre-hypnosis diagnostic phase</strong>.
            This is an assessment stage only — no induction or treatment should occur.
          </p>

          <p>
            Use the conversation to gather structured clinical information and determine:
          </p>

          <ul className="list-disc ml-5 space-y-1">
            <li>
              The most appropriate treatment approach:
              <br />
              Cognitive Behavioural Hypnotherapy (CBH)  
              Solution-Focused Hypnotherapy  
              Ericksonian / Indirect Hypnotherapy  
              Regression (Level 2 only)
            </li>
            <li>
              The dominant client modality:
              Visual / Auditory / Kinaesthetic
            </li>
            <li>
              The client’s core objective
            </li>
          </ul>

          <p>
            You must also:
          </p>

          <ul className="list-disc ml-5 space-y-1">
            <li>Clarify suitability and screen for safety concerns</li>
            <li>Respond to client questions about hypnotherapy</li>
            <li>Provide reassurance and confirm readiness before proceeding</li>
          </ul>

          <p>
            When you believe all objectives have been achieved, type
            <strong> TUTOR MODE </strong>
            in the chat to conclude the session.
          </p>

          <p className="text-slate-500">
            Safety Note: If a significant risk issue emerges, the system may interrupt the session.
          </p>

        </div>
      </div>

    </div>
  );
}