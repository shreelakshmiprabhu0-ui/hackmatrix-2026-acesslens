function SeverityFilter({
  selectedSeverity,
  onChange,
  categoryCounts,
}) {
  const filters = [
    {
      name: "All",
      count:
        categoryCounts.critical +
        categoryCounts.moderate +
        categoryCounts.minor,
    },
    {
      name: "Critical",
      count: categoryCounts.critical,
    },
    {
      name: "Moderate",
      count: categoryCounts.moderate,
    },
    {
      name: "Minor",
      count: categoryCounts.minor,
    },
  ];

  return (
    <div className="flex flex-wrap gap-2">

      {filters.map((filter) => (
        <button
          key={filter.name}
          onClick={() => onChange(filter.name)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
            selectedSeverity === filter.name
              ? "bg-gray-900 text-white"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          }`}
        >
          {filter.name}

          <span className="ml-2 opacity-70">
            {filter.count}
          </span>
        </button>
      ))}

    </div>
  );
}

export default SeverityFilter;