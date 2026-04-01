import axios from "axios";
import { useEffect, useState } from "react";

export default function ProgressDashboard() {
  const [progress, setProgress] = useState(null);

  const fetchProgress = async () => {
    try {
      const res = await axios.get("https://hypnotherapy-diagnostic-simulator.onrender.com/progress");
      setProgress(res.data);
    } catch {
      setProgress(null);
    }
  };

  useEffect(() => {
    fetchProgress();

    // Listen for updates after tutor review
    const handleUpdate = () => {
      fetchProgress();
    };

    window.addEventListener("progressUpdated", handleUpdate);

    return () => {
      window.removeEventListener("progressUpdated", handleUpdate);
    };
  }, []);

  if (!progress) {
    return <div>Loading progress...</div>;
  }

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