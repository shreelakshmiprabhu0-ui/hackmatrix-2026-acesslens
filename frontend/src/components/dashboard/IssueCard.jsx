function IssueCard({ violation, enrichment }) {
  const severityStyles = {
    Critical: {
      badge: "bg-red-50 text-red-700 border-red-200",
      dot: "bg-red-500",
    },

    Moderate: {
      badge: "bg-amber-50 text-amber-700 border-amber-200",
      dot: "bg-amber-500",
    },

    Minor: {
      badge: "bg-blue-50 text-blue-700 border-blue-200",
      dot: "bg-blue-500",
    },
  };

  const style =
    severityStyles[violation.severity] ||
    severityStyles.Minor;

  return (
    <article className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition">

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">

        <div className="flex gap-4">

          <div className={`w-3 h-3 rounded-full ${style.dot} mt-2`} />

          <div>

            <h4 className="text-lg font-bold text-slate-900">
              {violation.title}
            </h4>

            <p className="text-xs text-slate-400 mt-1 font-mono">
              Rule ID: {violation.id}
            </p>

          </div>

        </div>

        <span
          className={`self-start px-3 py-1.5 rounded-full text-xs font-bold border ${style.badge}`}
        >
          {violation.severity}
        </span>

      </div>

      {/* Description */}
      <p className="text-sm leading-6 text-slate-600 mt-5 ml-7">
        {violation.description}
      </p>

      {/* Metadata */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6 ml-7">

        <div className="rounded-xl bg-slate-50 border border-slate-100 p-4">

          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
            WCAG Criteria
          </p>

          <p className="text-sm font-semibold text-slate-800 mt-2">
            {violation.wcagCriteria.join(", ")}
          </p>

        </div>

        <div className="rounded-xl bg-slate-50 border border-slate-100 p-4">

          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
            Affected Elements
          </p>

          <p className="text-sm font-semibold text-slate-800 mt-2">
            {violation.affectedNodes} elements
          </p>

        </div>

      </div>

      {/* AI Section */}
      <div className="mt-6 ml-7 rounded-2xl border border-violet-100 bg-violet-50/50 p-5">

        <div className="flex items-center gap-2">

          <div className="w-8 h-8 rounded-lg bg-violet-100 flex items-center justify-center">
            ✨
          </div>

          <div>
            <p className="text-sm font-bold text-violet-900">
              AI-Powered Explanation
            </p>

            <p className="text-xs text-violet-600">
              Plain-English accessibility guidance
            </p>
          </div>

        </div>

        {enrichment ? (

          <div className="mt-4 space-y-3 text-sm text-slate-600">

            {enrichment.plainEnglish && (
              <p>
                <strong>What it means:</strong>{" "}
                {enrichment.plainEnglish}
              </p>
            )}

            {enrichment.whyItMatters && (
              <p>
                <strong>Why it matters:</strong>{" "}
                {enrichment.whyItMatters}
              </p>
            )}

            {enrichment.whoIsAffected && (
              <p>
                <strong>Who is affected:</strong>{" "}
                {enrichment.whoIsAffected}
              </p>
            )}

            {enrichment.suggestedFix && (
              <div className="mt-4 p-4 bg-white rounded-xl border border-violet-100">

                <p className="text-xs font-bold text-violet-700 uppercase tracking-wide">
                  Suggested Fix
                </p>

                <p className="text-sm text-slate-700 mt-2">
                  {enrichment.suggestedFix}
                </p>

              </div>
            )}

          </div>

        ) : (

          <div className="mt-4 p-4 rounded-xl bg-white border border-violet-100">

            <p className="text-sm text-slate-500">
              AI explanation will appear here after enrichment.
            </p>

            <div className="flex items-center gap-2 mt-3">

              <div className="w-2 h-2 rounded-full bg-violet-400 animate-pulse" />

              <span className="text-xs text-violet-600">
                Waiting for AI analysis...
              </span>

            </div>

          </div>

        )}

      </div>

    </article>
  );
}

export default IssueCard;