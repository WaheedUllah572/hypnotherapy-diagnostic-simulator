import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import ChatPanel from "../components/ChatPanel";
import ReflectionForm from "../components/ReflectionForm";
import TutorMode from "../components/TutorMode";
import ProgressDashboard from "../components/ProgressDashboard";

const clientProfiles = [
  { name: "Claire", problem: "Fear of driving on motorways", type: "CBH" },
  { name: "Daniel", problem: "Work performance anxiety", type: "SH" },
  { name: "Sophie", problem: "Panic in crowded spaces", type: "Ericksonian" },
  { name: "Mark", problem: "Sleep anxiety and racing thoughts", type: "Regression" }
];

export default function SessionSimulator() {
  const [stage, setStage] = useState("session");
  const [client, setClient] = useState(clientProfiles[0]);
  const [chatHistory, setChatHistory] = useState([]);

  const [submission, setSubmission] = useState({
    chosenApproach: "",
    clientModality: "",
    clientObjective: "",
    clientReassurance: ""
  });

  useEffect(() => {
    randomiseClient();
  }, []);

  // Never repeat same client twice
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
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-slate-100 to-teal-100">
      {/* HEADER */}
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
            <div className="glass p-6 lift h-[650px]">
              {stage === "session" && (
                <ChatPanel
                  isActive={true}
                  onEndSession={() => setStage("reflection")}
                  setChatHistory={setChatHistory}
                  clientType={client.type}
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
          <aside className="col-span-2">
            <ProgressDashboard />
          </aside>
        </div>
      </div>
    </div>
  );
}