import axios from "axios";
import { useEffect, useState } from "react";

export default function ProgressDashboard() {
  const [progress, setProgress] = useState({
    sessionsCompleted: 0,
    averageScore: 0,
    personasCompleted: []
  });

  const fetchProgress = async () => {
    try {
      const res = await axios.get("https://hypnotherapy-diagnostic-simulator.onrender.com/progress");
      setProgress(res.data);
    } catch {
      // keep default values so box still shows
    }
  };

  useEffect(() => {
    fetchProgress();

    const handleUpdate = () => {
      fetchProgress();
    };

    window.addEventListener("progressUpdated", handleUpdate);

    return () => {
      window.removeEventListener("progressUpdated", handleUpdate);
    };
  }, []);

  return (
    <div className="surface p-6 lift">
      <h3 className="font-semibold mb-4">Student Progress</h3>

      <p>Sessions Completed: {progress.sessionsCompleted}</p>
      <p>Average Score: {progress.averageScore} / 4</p>

      <div className="mt-4">
        <p className="font-semibold">Personas Completed:</p>
        {progress.personasCompleted.length === 0 ? (
          <p className="text-sm text-slate-500">None yet</p>
        ) : (
          progress.personasCompleted.map((p, i) => (
            <p key={i}>✓ {p}</p>
          ))
        )}
      </div>
    </div>
  );
}