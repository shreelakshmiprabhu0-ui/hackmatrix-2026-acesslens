function ScoreGauge({ score }) {
  const radius = 70;

  const circumference = 2 * Math.PI * radius;

  const progress =
    circumference - (score / 100) * circumference;

  const scoreColor =
    score >= 90
      ? "stroke-emerald-500"
      : score >= 70
      ? "stroke-green-500"
      : score >= 50
      ? "stroke-amber-500"
      : "stroke-red-500";

  const textColor =
    score >= 90
      ? "text-emerald-600"
      : score >= 70
      ? "text-green-600"
      : score >= 50
      ? "text-amber-600"
      : "text-red-600";

  return (
    <div className="relative w-48 h-48">

      <svg
        className="w-full h-full -rotate-90"
        viewBox="0 0 180 180"
      >

        {/* Background */}
        <circle
          cx="90"
          cy="90"
          r={radius}
          strokeWidth="13"
          fill="none"
          className="stroke-slate-100"
        />

        {/* Progress */}
        <circle
          cx="90"
          cy="90"
          r={radius}
          strokeWidth="13"
          fill="none"
          strokeLinecap="round"
          className={`${scoreColor} transition-all duration-700`}
          strokeDasharray={circumference}
          strokeDashoffset={progress}
        />

      </svg>

      <div className="absolute inset-0 flex flex-col items-center justify-center">

        <span className={`text-5xl font-bold ${textColor}`}>
          {score}
        </span>

        <span className="text-sm text-slate-400 font-medium">
          out of 100
        </span>

      </div>

    </div>
  );
}

export default ScoreGauge;