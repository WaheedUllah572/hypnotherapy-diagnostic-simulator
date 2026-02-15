import { useState, useRef, useEffect } from "react";
import axios from "axios";

export default function ChatPanel({ onEndSession, isActive, setChatHistory, clientType }) {
  const [msg, setMsg] = useState("");
  const [chat, setChat] = useState([
    { role: "client", text: "I’ve been feeling constantly anxious and overwhelmed lately." }
  ]);
  const [typing, setTyping] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    setChatHistory(chat);
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat, typing]);

  const send = async () => {
    if (!msg.trim() || !isActive) return;

    if (msg.trim().toUpperCase() === "TUTOR MODE") {
      onEndSession();
      return;
    }

    setChat(c => [...c, { role: "therapist", text: msg }]);
    setMsg("");
    setTyping(true);

    try {
      const res = await axios.post("https://hypnotherapy-diagnostic-simulator.onrender.com/chat", {
        text: msg,
        clientType: clientType
      });

      if (res.data.safety_flag) {
        setChat(c => [...c, { role: "tutor", text: res.data.reply }]);
        onEndSession();
      } else {
        setChat(c => [...c, { role: "client", text: res.data.reply }]);
      }
    } catch {
      setChat(c => [...c, { role: "client", text: "Client pauses and seems unsure…" }]);
    }

    setTyping(false);
  };

  return (
    <div className="flex flex-col h-[640px]">
      <div className="flex-1 overflow-y-auto space-y-6 pr-2">
        {chat.map((c, i) => (
          <div key={i} className={`flex ${c.role === "therapist" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[75%] p-5 rounded-2xl shadow-sm border ${
              c.role === "tutor" ? "bg-red-50 border-red-300" : "bg-white border-slate-200"
            }`}>
              <p className="text-[11px] uppercase tracking-wide text-slate-400 mb-1">
                {c.role === "therapist"
                  ? "Your Response (Student)"
                  : c.role === "tutor"
                  ? "Tutor"
                  : "Client"}
              </p>
              <p className="text-sm text-slate-800">{c.text}</p>
            </div>
          </div>
        ))}
        {typing && <div className="text-xs text-slate-400">Client is thinking…</div>}
        <div ref={bottomRef} />
      </div>

      <div className="pt-6 border-t border-slate-200 mt-6">
        <textarea
          rows={3}
          value={msg}
          disabled={!isActive}
          onChange={e => setMsg(e.target.value)}
          className="w-full rounded-2xl border border-slate-300 p-4 text-sm"
          placeholder="Ask safe diagnostic questions..."
        />

        <div className="flex justify-between mt-4">
          <button
            onClick={onEndSession}
            disabled={!isActive}
            className="bg-slate-700 text-white px-4 py-2 rounded-xl text-sm"
          >
            End Session
          </button>

          <button
            onClick={send}
            disabled={!isActive}
            className="bg-brand-600 text-white px-6 py-2 rounded-xl text-sm"
          >
            Respond
          </button>
        </div>
      </div>
    </div>
  );
}