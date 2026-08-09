export function exportReport(scanData, enrichment = {}) {
  const report = {
    generatedAt: new Date().toISOString(),

    url: scanData.url,

    accessibilityScore: scanData.overallScore,

    categoryCounts: scanData.categoryCounts,

    violations: scanData.violations,

    aiEnrichment: enrichment,
  };

  const json = JSON.stringify(report, null, 2);

  const blob = new Blob([json], {
    type: "application/json",
  });

  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");

  link.href = url;

  link.download = "accesslens-report.json";

  document.body.appendChild(link);

  link.click();

  document.body.removeChild(link);

  URL.revokeObjectURL(url);
}