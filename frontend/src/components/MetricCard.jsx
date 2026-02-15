export default function MetricCard({ title, value }) {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
      <div className="flex justify-between text-xs text-slate-500 mb-2">
        <span>{title}</span>
        <span>{value}/5</span>
      </div>

      <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-brand-400 to-brand-600"
          style={{ width: `${value * 20}%` }}
        />
      </div>
    </div>
  );
}
