import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import {
  PaperAirplaneIcon,
  ArrowPathIcon,
  MicrophoneIcon,
  SpeakerXMarkIcon,
} from "@heroicons/react/24/solid";
import ReactMarkdown from "react-markdown";

export default function ChatbotPage() {
  const [input, setInput] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const [micEnabled, setMicEnabled] = useState(true);
  const chatEndRef = useRef(null);
  const recognitionRef = useRef(null);

  // 🔊 REMOVE EMOJIS + MARKDOWN BEFORE SPEECH
  const cleanForSpeech = (text) => {
    return text
      .replace(/[\u{1F300}-\u{1FAFF}]/gu, "")
      .replace(/\*\*/g, "")
      .replace(/`/g, "")
      .replace(/•/g, "")
      .replace(/\n/g, ". ");
  };

  // 🎤 Speech Recognition
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.continuous = false;

    recognition.onstart = () => setListening(true);
    recognition.onend = () => setListening(false);

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
    };

    recognitionRef.current = recognition;
  }, []);

  const toggleMic = () => {
    if (!recognitionRef.current) return;
    listening ? recognitionRef.current.stop() : recognitionRef.current.start();
  };

  // 🚀 Send Message
  const sendMessage = async (customMessage = null) => {
    const messageToSend = customMessage || input;
    if (!messageToSend.trim()) return;

    const timestamp = new Date().toLocaleTimeString();

    setHistory((prev) => [
      ...prev,
      {
        user: messageToSend,
        bot: "typing...",
        time: timestamp,
      },
    ]);

    setInput("");
    setLoading(true);

    try {
      const res = await axios.post("http://localhost:8000/chat", {
        message: messageToSend,
        session_id: "user-session-1",
      });

      const reply = res.data.reply || "No reply received.";
      const pending = res.data.context?.pending_trip_confirmation;

      setHistory((prev) => {
        const newHistory = [...prev];
        newHistory[newHistory.length - 1] = {
          ...newHistory[newHistory.length - 1],
          bot: reply,
          pendingConfirmation: pending || null,
        };
        return newHistory;
      });

      // 🔊 SPEECH
      if (micEnabled && reply && reply !== "typing...") {
        const utterance = new SpeechSynthesisUtterance(
          cleanForSpeech(reply)
        );
        utterance.lang = "en-US";
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utterance);
      }
    } catch {
      setHistory((prev) => {
        const newHistory = [...prev];
        newHistory[newHistory.length - 1].bot =
          "Error connecting to server.";
        return newHistory;
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !loading) sendMessage();
  };

  const clearChat = () => setHistory([]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-white to-purple-100 flex justify-center items-center p-6 font-sans">
      <div className="w-full max-w-5xl bg-white/70 backdrop-blur-xl shadow-2xl rounded-3xl border border-gray-200 p-6 flex flex-col relative overflow-hidden">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-3xl font-extrabold flex items-center gap-2">
            🤖{" "}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 text-transparent bg-clip-text drop-shadow">
              Max, your AI Tax Agent
            </span>
          </h2>

          <div className="flex gap-2">
            <button
              onClick={() => setMicEnabled((prev) => !prev)}
              className={`flex items-center gap-2 px-4 py-2 rounded-full shadow-md transition ${
                micEnabled
                  ? "bg-gradient-to-r from-green-500 to-emerald-600 text-white"
                  : "bg-gray-300 text-gray-800"
              }`}
            >
              {micEnabled ? (
                <>
                  <MicrophoneIcon className="h-5 w-5" /> Mic On
                </>
              ) : (
                <>
                  <SpeakerXMarkIcon className="h-5 w-5" /> Mic Off
                </>
              )}
            </button>

            <button
              onClick={clearChat}
              className="flex items-center gap-1 px-4 py-2 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-full shadow-md hover:scale-105 transition"
            >
              <ArrowPathIcon className="h-4 w-4" /> Clear
            </button>
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto rounded-2xl p-6 bg-gradient-to-br from-gray-50 to-gray-100 shadow-inner space-y-6">
          {history.map((h, idx) => (
            <div key={idx} className="space-y-3">
              <div className="flex justify-end">
                <div className="px-5 py-3 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-3xl shadow-lg max-w-lg text-sm">
                  {h.user}
                </div>
              </div>

              <div className="flex justify-start">
                <div className="px-5 py-3 bg-white/90 border border-gray-200 text-gray-800 rounded-3xl shadow-md max-w-lg text-sm">
                  {h.bot === "typing..."
                    ? "..."
                    : <ReactMarkdown>{h.bot}</ReactMarkdown>}

                  {/* ✅ Confirmation Buttons */}
                  {h.pendingConfirmation && (
                    <div className="mt-4 flex gap-3">
                      <button
                        onClick={() => sendMessage("CONFIRM")}
                        className="px-4 py-2 bg-green-600 text-white rounded-full text-xs shadow hover:scale-105 transition"
                      >
                        Confirm
                      </button>

                      <button
                        onClick={() => sendMessage("EDIT")}
                        className="px-4 py-2 bg-blue-600 text-white rounded-full text-xs shadow hover:scale-105 transition"
                      >
                        Edit
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
          <div ref={chatEndRef}></div>
        </div>

        {/* Input Area */}
        <div className="flex items-center mt-4 bg-white/90 border border-gray-200 rounded-full px-4 py-2 shadow-lg gap-3">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1 px-4 py-2 bg-transparent outline-none text-gray-700 text-sm"
            placeholder={listening ? "Listening..." : "Ask a tax question..."}
          />

          <button
            onClick={toggleMic}
            className={`p-2 rounded-full transition ${
              listening
                ? "bg-red-500 text-white animate-pulse"
                : "bg-gradient-to-r from-green-500 to-emerald-600 text-white"
            }`}
          >
            <MicrophoneIcon className="h-5 w-5" />
          </button>

          <button
            onClick={() => sendMessage()}
            disabled={loading}
            className="px-5 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-full flex items-center gap-2"
          >
            <PaperAirplaneIcon className="h-5 w-5 rotate-90" />
            {loading ? "Sending..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}