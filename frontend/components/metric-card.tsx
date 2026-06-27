type MetricCardProps = {
  label: string;
  value: string;
  tone?: "neutral" | "good" | "warn";
};

const tones = {
  neutral: "border-ink/10 bg-white",
  good: "border-moss/25 bg-moss/10",
  warn: "border-coral/25 bg-coral/10"
};

export function MetricCard({ label, value, tone = "neutral" }: MetricCardProps) {
  return (
    <div className={`rounded-lg border p-4 shadow-sm ${tones[tone]}`}>
      <p className="text-sm text-ink/60">{label}</p>
      <p className="mt-2 text-2xl font-semibold tracking-normal text-ink">{value}</p>
    </div>
  );
}

