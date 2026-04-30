import React from "react";

const Bar = ({ label, value, color }) => {
  return (
    <div className="mb-3">
      <div className="flex justify-between text-xs mb-1">
        <span>{label}</span>
        <span>{value}</span>
      </div>
      <div className="w-full bg-slate-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full ${color}`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
};

export default function StatePanel({ state }) {
  if (!state) return null;

  return (
    <div className="bg-white p-4 rounded-xl shadow border">
      <h3 className="text-sm font-semibold mb-3">Client State</h3>

      <Bar label="Trust" value={state.trust} color="bg-green-500" />
      <Bar label="Distress" value={state.distress} color="bg-red-500" />
      <Bar label="Engagement" value={state.engagement} color="bg-blue-500" />
      <Bar label="Resistance" value={state.resistance} color="bg-yellow-500" />

      {state.risk_flag !== "none" && (
        <div className="text-red-600 text-xs mt-2">
          ⚠ Risk detected: {state.risk_flag}
        </div>
      )}
    </div>
  );
}