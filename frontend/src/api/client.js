// Owned by Module 1 (Shreelakshmi).
// Fetch wrappers for the AccessLens backend API.

import mockScanResponse from "../mocks/mockScanResponse.json";

const BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const USE_MOCK_DATA =
  import.meta.env.VITE_USE_MOCK_DATA === "true";

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ---------------------------------------------------------
// ACCESSIBILITY SCAN
// ---------------------------------------------------------

export async function scanUrl(url) {
  if (USE_MOCK_DATA) {
    await wait(1200);

    return {
      ...mockScanResponse,
      url,
    };
  }

  const res = await fetch(`${BASE_URL}/api/scan`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      url,
    }),
  });

  if (!res.ok) {
    throw new Error(`Scan failed: ${res.status}`);
  }

  return res.json();
}

// ---------------------------------------------------------
// GEMINI AI ENRICHMENT
// ---------------------------------------------------------

export async function enrichViolations(violations) {
  const res = await fetch(`${BASE_URL}/api/enrich`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      violations,
    }),
  });

  if (!res.ok) {
    throw new Error(`Enrich failed: ${res.status}`);
  }

  return res.json();
}

// ---------------------------------------------------------
// PDF REPORT EXPORT
// ---------------------------------------------------------

export async function exportReport(scanData, enrichmentData) {
  const res = await fetch(`${BASE_URL}/api/report/export`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      scan_data: scanData,

      enrichment_data: {
        enrichedViolations: Object.values(enrichmentData || {}),
      },
    }),
  });

  if (!res.ok) {
    let errorMessage = `Export failed: ${res.status}`;

    try {
      const errorData = await res.json();

      if (errorData?.detail) {
        errorMessage = errorData.detail;
      }
    } catch {
      // Response wasn't JSON.
    }

    throw new Error(errorMessage);
  }

  const blob = await res.blob();

  if (blob.type && !blob.type.includes("application/pdf")) {
    throw new Error(
      "The server did not return a PDF file."
    );
  }

  return blob;
}