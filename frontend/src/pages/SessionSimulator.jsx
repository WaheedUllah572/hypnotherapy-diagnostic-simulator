import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import ChatPanel from "../components/ChatPanel";
import ReflectionForm from "../components/ReflectionForm";
import TutorMode from "../components/TutorMode";

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

  useEffect(() => {
    const random =
      clientProfiles[Math.floor(Math.random() * clientProfiles.length)];
    setClient(random);
  }, []);

  const [submission, setSubmission] = useState({
    chosenApproach: "",
    clientModality: "",
    clientObjective: "",
    clientReassurance: ""
  });

  return (
    <div className="min-h-screen">
      <div className="header-bar text-white px-8 py-5">
        <div className="max-w-[1500px] mx-auto flex justify-between">
          <h1 className="text-lg tracking-wider font-medium">
            HYPNOTHERAPY DIAGNOSTIC TRAINING SIMULATOR
          </h1>
          <span className="text-sm opacity-90">
            Pre-Hypnosis Assessment
          </span>
        </div>
      </div>

      <div className="max-w-[1500px] mx-auto px-8 py-12">
        <h2 className="text-3xl font-semibold mb-12">
          Client Presentation Session
        </h2>

        <div className="grid grid-cols-12 gap-12">

          {/* LEFT PANEL */}
          <aside className="col-span-3">
            <div className="surface p-7 lift">
              <Sidebar client={client} />
            </div>
          </aside>

          {/* MAIN PANEL */}
          <main className="col-span-6">
            <div className="glass p-8 lift">

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
                />
              )}

            </div>
          </main>

          {/* RIGHT PANEL (EMPTY DURING SESSION) */}
          <aside className="col-span-3" />

        </div>
      </div>
    </div>
  );
}