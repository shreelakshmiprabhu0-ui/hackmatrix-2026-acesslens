import IssueCard from "./IssueCard";

function IssueList({ violations, enrichment = {} }) {
  if (!violations || violations.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">
          No accessibility issues found for this filter.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {violations.map((violation) => (
        <IssueCard
          key={violation.id}
          violation={violation}
          enrichment={enrichment[violation.id]}
        />
      ))}
    </div>
  );
}

export default IssueList;