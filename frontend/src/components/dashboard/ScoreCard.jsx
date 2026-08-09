function ScoreCard({ score, categoryCounts }) {
  let message = "Needs improvement";

  if (score >= 90) {
    message = "Excellent accessibility";
  } else if (score >= 70) {
    message = "Good accessibility";
  } else if (score >= 50) {
    message = "Needs improvement";
  } else {
    message = "Poor accessibility";
  }

  return (
    <div className="bg-white rounded-2xl border shadow-sm p-6 h-full">

      <p className="text-sm text-gray-500">
        Accessibility Score
      </p>

      <div className="flex items-end gap-2 mt-2">
        <span className="text-5xl font-bold text-gray-900">
          {score}
        </span>

        <span className="text-gray-500 mb-2">
          / 100
        </span>
      </div>

      <p className="text-lg font-semibold text-gray-700 mt-2">
        {message}
      </p>

      <div className="grid grid-cols-3 gap-3 mt-8">

        <div className="bg-red-50 rounded-xl p-4">
          <p className="text-xs text-gray-500">
            Critical
          </p>

          <p className="text-2xl font-bold text-red-600">
            {categoryCounts.critical}
          </p>
        </div>

        <div className="bg-yellow-50 rounded-xl p-4">
          <p className="text-xs text-gray-500">
            Moderate
          </p>

          <p className="text-2xl font-bold text-yellow-600">
            {categoryCounts.moderate}
          </p>
        </div>

        <div className="bg-blue-50 rounded-xl p-4">
          <p className="text-xs text-gray-500">
            Minor
          </p>

          <p className="text-2xl font-bold text-blue-600">
            {categoryCounts.minor}
          </p>
        </div>

      </div>

    </div>
  );
}

export default ScoreCard;