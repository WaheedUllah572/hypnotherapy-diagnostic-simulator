import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import ChatPanel from "../components/ChatPanel";
import ReflectionForm from "../components/ReflectionForm";
import TutorMode from "../components/TutorMode";
import ProgressDashboard from "../components/ProgressDashboard";

const clientProfiles = [
  {
    name: "Claire",
    condition: "Motorway Driving Anxiety",
    problem: "Fear of driving on motorways",
    goal: "Feel calm and confident when driving again",
    symptoms: [
      "motorway panic",
      "fear of losing control",
      "avoidance driving"
    ],
    type: "CBH"
  },

  {
    name: "Daniel",
    condition: "Work Performance Anxiety",
    problem: "Anxiety around work performance",
    goal: "Feel calmer and more confident at work",
    symptoms: [
      "performance anxiety",
      "fear of failure",
      "work stress"
    ],
    type: "SH"
  },

  {
    name: "Sophie",
    condition: "Crowd / Environmental Anxiety",
    problem: "Overwhelm in crowded places",
    goal: "Feel calmer in busy environments",
    symptoms: [
      "crowd anxiety",
      "sensory overwhelm",
      "escape response"
    ],
    type: "Ericksonian"
  },

  {
    name: "Mark",
    condition: "Sleep Anxiety / Night-Time Overthinking",
    problem: "Sleep anxiety and racing thoughts",
    goal: "Sleep peacefully again",
    symptoms: [
      "night-time overthinking",
      "difficulty switching off",
      "fatigue"
    ],
    type: "Regression"
  }
];
export default function SessionSimulator() {
  const [stage, setStage] = useState("session");
  const [client, setClient] = useState(clientProfiles[0]);
  const [chatHistory, setChatHistory] = useState([]);

  const [stateData, setStateData] = useState(null); // ✅ NEW

  const [submission, setSubmission] = useState({
    chosenApproach: "",
    clientModality: "",
    clientObjective: "",
    clientReassurance: ""
  });

  useEffect(() => {
    randomiseClient();
  }, []);

  const randomiseClient = () => {
    let newClient;
    do {
      newClient =
        clientProfiles[Math.floor(Math.random() * clientProfiles.length)];
    } while (newClient.name === client.name);

    setClient(newClient);
  };

  const resetSession = () => {
    randomiseClient();
    setChatHistory([]);
    setSubmission({
      chosenApproach: "",
      clientModality: "",
      clientObjective: "",
      clientReassurance: ""
    });
    setStage("session");
    setStateData(null); // ✅ reset
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-slate-100 to-teal-100">
      <div className="header-bar text-white px-8 py-5 sticky top-0 z-50">
        <div className="max-w-[1500px] mx-auto flex justify-between">
          <h1 className="text-lg tracking-wider font-medium">
            HYPNOTHERAPY DIAGNOSTIC TRAINING SIMULATOR
          </h1>
          <span className="text-sm opacity-90">
            Pre-Hypnosis Assessment
          </span>
        </div>
      </div>

      <div className="max-w-[1500px] mx-auto px-8 py-6">
        <h2 className="text-3xl font-semibold mb-6">
          Client Presentation Session
        </h2>

        <div className="grid grid-cols-12 gap-8">
          {/* LEFT */}
          <aside className="col-span-4">
            <div className="surface p-7 lift h-[650px] overflow-y-auto">
              <Sidebar client={client} />
            </div>
          </aside>

          {/* CENTER */}
          <main className="col-span-6">
            <div className="glass p-6 lift">
              {stage === "session" && (
                <ChatPanel
                  isActive={true}
                  onEndSession={() => setStage("reflection")}
                  setChatHistory={setChatHistory}
                  clientType={client.name}
                  setStateData={setStateData} // ✅ PASS STATE
                />
              )}

              {stage === "reflection" && (
                <ReflectionForm
                  submission={submission}
                  setSubmission={setSubmission}
                  onSubmit={() => setStage("tutor")}
                />
              )}

              {stage === "tutor" && (
                <TutorMode
                  submission={submission}
                  chatHistory={chatHistory}
                  resetSession={resetSession}
                  client={client}
                />
              )}
            </div>
          </main>

          {/* RIGHT */}
          <aside className="col-span-2 space-y-4">
            <ProgressDashboard />

            {/* ✅ SIMPLE STATE DISPLAY (MINIMAL UI — SAFE CHANGE) */}
            {stateData && (
              <div className="bg-white p-4 rounded-xl shadow border text-xs">
                <h3 className="font-semibold mb-2">Client State</h3>
                <p>Trust: {stateData.trust}</p>
                <p>Distress: {stateData.distress}</p>
                <p>Engagement: {stateData.engagement}</p>
                <p>Resistance: {stateData.resistance}</p>
              </div>
            )}
          </aside>
        </div>
      </div>
    </div>
  );
}