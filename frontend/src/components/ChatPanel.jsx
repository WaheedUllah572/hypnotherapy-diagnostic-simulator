import { useState, useRef, useEffect } from "react";
import axios from "axios";

export default function ChatPanel({
  onEndSession,
  isActive,
  setChatHistory,
  clientType
}) {
  const [msg, setMsg] = useState("");
  const [chat, setChat] = useState([
    {
      role: "client",
      text: "Hello"
    }
  ]);
  const [typing, setTyping] = useState(false);
  const [listening, setListening] = useState(false);

  const chatContainerRef = useRef(null);
  const recognitionRef = useRef(null);

  // ✅ CRITICAL FIX: persistent response control
  const respondedRef = useRef(false);

  useEffect(() => {
    setChatHistory(chat);

    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTo({
        top: chatContainerRef.current.scrollHeight,
        behavior: "smooth"
      });
    }
  }, [chat, typing]);

  const startListening = () => {
    if (!("webkitSpeechRecognition" in window)) {
      alert("Microphone not supported in this browser");
      return;
    }

    const recognition = new window.webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-GB";

    recognition.onstart = () => setListening(true);

    recognition.onresult = (event) => {
      let transcript = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      setMsg(transcript);
    };

    recognition.onerror = () => {
      setListening(false);
      recognition.stop();
    };

    recognition.onend = () => setListening(false);

    recognition.start();
    recognitionRef.current = recognition;

    setTimeout(() => {
      recognition.stop();
    }, 6000);
  };

  // ✅ SAFE API CALL WITH RETRY
  const callAPI = async (payload, retry = 0) => {
    try {
      return await axios.post(
        "https://hypnotherapy-diagnostic-simulator.onrender.com/chat",
        payload,
        { timeout: 10000 } // ✅ frontend timeout
      );
    } catch (err) {
      if (retry < 1) {
        return callAPI(payload, retry + 1); // ✅ retry once only
      }
      throw err;
    }
  };

  const send = async () => {
    const cleanMsg = msg.trim();

    if (cleanMsg.length < 5 || !isActive) return;

    const userMessage = cleanMsg;

    const updatedChat = [...chat, { role: "therapist", text: userMessage }];
    setChat(updatedChat);
    setMsg("");
    setTyping(true);

    // ✅ RESET CONTROL FLAG
    respondedRef.current = false;

    const failSafe = setTimeout(() => {
      if (!respondedRef.current) {
        respondedRef.current = true;

        setChat(c => [
          ...c,
          {
            role: "client",
            text: "The client pauses… you may need to rephrase your question."
          }
        ]);

        setTyping(false);
      }
    }, 12000);

    try {
      const res = await callAPI({
        text: userMessage,
        clientType: clientType,
        history: updatedChat
      });

      // ✅ BLOCK DUPLICATES
      if (!respondedRef.current) {
        respondedRef.current = true;
        clearTimeout(failSafe);

        setTimeout(() => {
          setChat(c => [...c, { role: "client", text: res.data.reply }]);
          setTyping(false);
        }, 600);
      }

    } catch (err) {
      if (!respondedRef.current) {
        respondedRef.current = true;
        clearTimeout(failSafe);

        setChat(c => [
          ...c,
          {
            role: "client",
            text: "The client seems unsure how to respond… try asking differently."
          }
        ]);

        setTyping(false);
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div className="h-full flex flex-col">

      {/* CHAT */}
      <div
        ref={chatContainerRef}
        className="overflow-y-auto px-2 pt-2 pb-4"
      >
        {chat.map((c, i) => (
          <div
            key={i}
            className={`flex mb-6 ${
              c.role === "therapist" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[75%] p-5 rounded-2xl shadow-sm border ${
                c.role === "tutor"
                  ? "bg-amber-50 border-amber-200"
                  : "bg-white border-slate-200"
              }`}
            >
              <p className="text-[11px] uppercase tracking-wide text-slate-400 mb-1">
                {c.role === "therapist"
                  ? "Your Response (Student)"
                  : c.role === "tutor"
                  ? "Tutor"
                  : "Client"}
              </p>

              <p className="text-sm text-slate-800 whitespace-pre-line">
                {c.text}
              </p>
            </div>
          </div>
        ))}

        {typing && (
          <div className="text-xs text-slate-400 italic animate-pulse mb-4">
            Client is typing…
          </div>
        )}
      </div>

      {/* INPUT */}
      <div className="border-t border-slate-200 bg-white p-3 sticky bottom-0">

        <textarea
          rows={2}
          value={msg}
          disabled={!isActive}
          onChange={e => setMsg(e.target.value)}
          onKeyDown={handleKeyDown}
          className="w-full rounded-xl border border-slate-300 p-3 text-sm"
          placeholder="Type your response..."
        />

        <div className="flex justify-between items-center mt-2">

          <button
            onClick={onEndSession}
            disabled={!isActive}
            className="bg-slate-700 text-white px-4 py-2 rounded-xl text-sm"
          >
            TUTOR MODE
          </button>

          <div className="flex gap-2 items-center">
            <button
              onClick={startListening}
              className="bg-slate-500 text-white px-3 py-2 rounded-xl text-sm"
            >
              🎤 Speak
            </button>

            {listening && (
              <span className="text-xs text-red-500">Listening...</span>
            )}

            <button
              onClick={send}
              disabled={!isActive}
              className="bg-brand-600 text-white px-5 py-2 rounded-xl text-sm"
            >
              Respond
            </button>
          </div>

        </div>
      </div>

    </div>
  );
}