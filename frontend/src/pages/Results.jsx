import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import IssueList from "../components/dashboard/IssueList";
import SeverityFilter from "../components/dashboard/SeverityFilter";
import ScoreGauge from "../components/charts/ScoreGauge";

import {
  exportReport,
  enrichViolations,
} from "../api/client";

function Results() {
  const location = useLocation();
  const navigate = useNavigate();

  // Real scan data is handed off from Home.jsx via router state
  const data = location.state?.scanResult;

  const [selectedSeverity, setSelectedSeverity] =
    useState("All");

  const [enrichment, setEnrichment] = useState({});

  const [enrichError, setEnrichError] = useState("");

  const [isExporting, setIsExporting] = useState(false);

  // Prevent duplicate enrichment requests in React StrictMode.
  const enrichRequestKeyRef = useRef(null);

  // ---------------------------------------------------------
  // GEMINI ENRICHMENT
  // ---------------------------------------------------------

  useEffect(() => {
    if (
      !data ||
      !data.violations ||
      data.violations.length === 0
    ) {
      return;
    }

    const requestKey = data.violations
      .map((v) => v.id)
      .join(",");

    // Prevent duplicate requests for the same scan.
    if (enrichRequestKeyRef.current === requestKey) {
      return;
    }

    enrichRequestKeyRef.current = requestKey;

    async function loadEnrichment() {
      setEnrichError("");

      try {
        const violationsForEnrichment =
          data.violations.map((v) => ({
            id: v.id,
            title: v.title,
            description: v.description,
            impact: v.impact,
            wcagCriteria: v.wcagCriteria,
          }));

        const result = await enrichViolations(
          violationsForEnrichment
        );

        // Convert:
        //
        // {
        //   enrichedViolations: [
        //     { id: "target-size", ... },
        //     { id: "color-contrast", ... }
        //   ]
        // }
        //
        // into:
        //
        // {
        //   "target-size": { ... },
        //   "color-contrast": { ... }
        // }

        const byId = {};

        for (const item of result.enrichedViolations || []) {
          byId[item.id] = item;
        }

        setEnrichment(byId);
      } catch (err) {
        console.error("Enrichment failed:", err);

        setEnrichError(
          "AI explanations couldn't be loaded right now. The scan results below are still accurate."
        );

        // Allow retry after a failed request.
        enrichRequestKeyRef.current = null;
      }
    }

    loadEnrichment();
  }, [data]);

  // ---------------------------------------------------------
  // REDIRECT IF NO SCAN DATA
  // ---------------------------------------------------------

  useEffect(() => {
    if (!data) {
      navigate("/", { replace: true });
    }
  }, [data, navigate]);

  if (!data) {
    return null;
  }

  // ---------------------------------------------------------
  // FILTERING
  // ---------------------------------------------------------

  const filteredViolations =
    selectedSeverity === "All"
      ? data.violations
      : data.violations.filter(
          (issue) =>
            issue.severity.toLowerCase() ===
            selectedSeverity.toLowerCase()
        );

  // ---------------------------------------------------------
  // PDF EXPORT
  // ---------------------------------------------------------

  const handleExport = async () => {
    if (isExporting) {
      return;
    }

    setIsExporting(true);

    try {
      const pdfBlob = await exportReport(
        data,
        enrichment
      );

      // Create temporary browser URL for the PDF.
      const url = window.URL.createObjectURL(pdfBlob);

      // Create download link.
      const link = document.createElement("a");

      link.href = url;
      link.download = "accesslens_report.pdf";

      document.body.appendChild(link);

      link.click();

      link.remove();

      // Release the temporary object URL.
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error(
        "Report export failed:",
        error
      );

      alert(
        error?.message ||
          "Unable to export the accessibility report right now."
      );
    } finally {
      setIsExporting(false);
    }
  };

  // ---------------------------------------------------------
  // RETRY GEMINI ENRICHMENT
  // ---------------------------------------------------------

  const handleRetryEnrichment = async () => {
    const requestKey = data.violations
      .map((v) => v.id)
      .join(",");

    enrichRequestKeyRef.current = requestKey;

    setEnrichError("");

    try {
      const violationsForEnrichment =
        data.violations.map((v) => ({
          id: v.id,
          title: v.title,
          description: v.description,
          impact: v.impact,
          wcagCriteria: v.wcagCriteria,
        }));

      const result = await enrichViolations(
        violationsForEnrichment
      );

      const byId = {};

      for (const item of result.enrichedViolations || []) {
        byId[item.id] = item;
      }

      setEnrichment(byId);
    } catch (err) {
      console.error(
        "Enrichment retry failed:",
        err
      );

      setEnrichError(
        "AI explanations couldn't be loaded right now. The scan results below are still accurate."
      );

      // Allow another retry.
      enrichRequestKeyRef.current = null;
    }
  };

  // ---------------------------------------------------------
  // UI
  // ---------------------------------------------------------

  return (
    <div className="min-h-screen bg-slate-50">

      {/* ---------------------------------------------------
          HEADER
      --------------------------------------------------- */}

      <header className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-5 flex items-center justify-between">

          <div className="flex items-center gap-3">

            <button
              onClick={() => navigate("/")}
              className="w-10 h-10 rounded-xl bg-slate-900 text-white flex items-center justify-center font-bold text-lg"
              aria-label="Scan another website"
            >
              A
            </button>

            <div>

              <h1 className="text-xl font-bold text-slate-900">
                AccessLens
              </h1>

              <p className="text-xs text-slate-500">
                Web Accessibility Analyzer
              </p>

            </div>

          </div>

          <button
            onClick={() => navigate("/")}
            className="hidden sm:block text-sm text-slate-500 hover:text-slate-800"
          >
            Scan another site
          </button>

        </div>
      </header>

      {/* ---------------------------------------------------
          MAIN
      --------------------------------------------------- */}

      <main className="max-w-7xl mx-auto px-6 py-10">

        {/* -------------------------------------------------
            PAGE HEADING
        ------------------------------------------------- */}

        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-5 mb-8">

          <div>

            <div className="flex items-center gap-2 mb-3">

              <span className="px-3 py-1 rounded-full bg-slate-200 text-slate-700 text-xs font-semibold">
                Accessibility Scan
              </span>

              <span className="text-xs text-slate-400">
                Lighthouse analysis
              </span>

            </div>

            <h2 className="text-4xl font-bold tracking-tight text-slate-900">
              Accessibility Results
            </h2>

            <p className="text-slate-500 mt-2 break-all">
              {data.url}
            </p>

          </div>

          {/* -------------------------------------------------
              EXPORT BUTTON
          ------------------------------------------------- */}

          <button
            onClick={handleExport}
            disabled={isExporting}
            className="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-slate-900 text-white font-semibold shadow-sm hover:bg-slate-800 transition disabled:opacity-60 disabled:cursor-not-allowed"
          >

            <span>
              {isExporting ? "⏳" : "↓"}
            </span>

            {isExporting
              ? "Generating PDF..."
              : "Export Report"}

          </button>

        </div>

        {/* -------------------------------------------------
            ENRICHMENT ERROR
        ------------------------------------------------- */}

        {enrichError && (
          <div
            role="status"
            className="mb-8 flex items-center justify-between gap-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800"
          >

            <span>
              {enrichError}
            </span>

            <button
              onClick={handleRetryEnrichment}
              className="shrink-0 rounded font-medium text-amber-900 underline underline-offset-2 hover:text-amber-950"
            >
              Retry
            </button>

          </div>
        )}

        {/* -------------------------------------------------
            SCORE OVERVIEW
        ------------------------------------------------- */}

        <section className="grid grid-cols-1 lg:grid-cols-5 gap-6 mb-10">

          {/* SCORE */}

          <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 shadow-sm p-8 flex flex-col items-center justify-center">

            <p className="text-sm font-semibold text-slate-500 uppercase tracking-wider">
              Accessibility Score
            </p>

            <div className="mt-5">
              <ScoreGauge
                score={data.overallScore}
              />
            </div>

            <div className="mt-4 text-center">

              <p className="text-lg font-bold text-slate-900">

                {data.overallScore >= 90
                  ? "Excellent accessibility"
                  : data.overallScore >= 70
                  ? "Good accessibility"
                  : data.overallScore >= 50
                  ? "Needs improvement"
                  : "Poor accessibility"}

              </p>

              <p className="text-sm text-slate-500 mt-1">
                Based on automated accessibility checks
              </p>

            </div>

          </div>

          {/* BREAKDOWN */}

          <div className="lg:col-span-3 bg-white rounded-2xl border border-slate-200 shadow-sm p-8">

            <div className="flex items-center justify-between mb-6">

              <div>

                <h3 className="text-xl font-bold text-slate-900">
                  Issue Overview
                </h3>

                <p className="text-sm text-slate-500 mt-1">
                  {data.violations.length} accessibility issues detected
                </p>

              </div>

            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">

              {/* CRITICAL */}

              <div className="rounded-2xl bg-red-50 border border-red-100 p-5">

                <div className="flex items-center gap-2">

                  <div className="w-2.5 h-2.5 rounded-full bg-red-500" />

                  <span className="text-sm font-semibold text-red-700">
                    Critical
                  </span>

                </div>

                <p className="text-4xl font-bold text-red-700 mt-4">
                  {data.categoryCounts.critical}
                </p>

                <p className="text-xs text-red-600 mt-1">
                  Requires immediate attention
                </p>

              </div>

              {/* MODERATE */}

              <div className="rounded-2xl bg-amber-50 border border-amber-100 p-5">

                <div className="flex items-center gap-2">

                  <div className="w-2.5 h-2.5 rounded-full bg-amber-500" />

                  <span className="text-sm font-semibold text-amber-700">
                    Moderate
                  </span>

                </div>

                <p className="text-4xl font-bold text-amber-700 mt-4">
                  {data.categoryCounts.moderate}
                </p>

                <p className="text-xs text-amber-600 mt-1">
                  Should be addressed
                </p>

              </div>

              {/* MINOR */}

              <div className="rounded-2xl bg-blue-50 border border-blue-100 p-5">

                <div className="flex items-center gap-2">

                  <div className="w-2.5 h-2.5 rounded-full bg-blue-500" />

                  <span className="text-sm font-semibold text-blue-700">
                    Minor
                  </span>

                </div>

                <p className="text-4xl font-bold text-blue-700 mt-4">
                  {data.categoryCounts.minor}
                </p>

                <p className="text-xs text-blue-600 mt-1">
                  Recommended improvements
                </p>

              </div>

            </div>

            {/* SUMMARY */}

            <div className="mt-6 p-4 rounded-xl bg-slate-50 border border-slate-100">

              <div className="flex items-start gap-3">

                <div className="text-lg">
                  💡
                </div>

                <div>

                  <p className="text-sm font-semibold text-slate-800">
                    Accessibility insight
                  </p>

                  <p className="text-sm text-slate-500 mt-1">
                    Fixing the critical issues first can significantly
                    improve the accessibility of this website.
                  </p>

                </div>

              </div>

            </div>

          </div>

        </section>

        {/* -------------------------------------------------
            ISSUES
        ------------------------------------------------- */}

        <section>

          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-5">

            <div>

              <h3 className="text-2xl font-bold text-slate-900">
                Accessibility Issues
              </h3>

              <p className="text-sm text-slate-500 mt-1">
                Review each issue and its recommended solution.
              </p>

            </div>

            <SeverityFilter
              selectedSeverity={selectedSeverity}
              onChange={setSelectedSeverity}
              categoryCounts={data.categoryCounts}
            />

          </div>

          <IssueList
            violations={filteredViolations}
            enrichment={enrichment}
          />

        </section>

      </main>

      {/* ---------------------------------------------------
          FOOTER
      --------------------------------------------------- */}

      <footer className="border-t border-slate-200 bg-white mt-16">

        <div className="max-w-7xl mx-auto px-6 py-6 text-center">

          <p className="text-sm text-slate-500">
            AccessLens · Making the web more accessible
          </p>

        </div>

      </footer>

    </div>
  );
}

export default Results;