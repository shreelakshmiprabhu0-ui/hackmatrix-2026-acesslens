// Owned by Module 1 (Shreelakshmi). Fetch wrappers for the backend API,
// matching docs/API_CONTRACT.md.

import mockScanResponse from '../mocks/mockScanResponse.json'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Module 3's real /api/scan isn't live yet, so scanUrl() serves the
// shared mock fixture instead. This is the ONLY thing that needs to
// change once the backend is ready — flip this to false. Every caller
// (UrlForm -> Home.jsx -> scanUrl()) stays exactly the same either way,
// since both branches return a promise that resolves to a ScanResponse
// shaped object matching docs/API_CONTRACT.md.
const USE_MOCK_DATA = true

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export async function scanUrl(url) {
  if (USE_MOCK_DATA) {
    await wait(1200) // simulate real scan latency so the loading state is testable
    return { ...mockScanResponse, url }
  }

  const res = await fetch(`${BASE_URL}/api/scan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  })
  if (!res.ok) throw new Error(`Scan failed: ${res.status}`)
  return res.json()
}

export async function enrichViolations(violations) {
  const res = await fetch(`${BASE_URL}/api/enrich`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ violations }),
  })
  if (!res.ok) throw new Error(`Enrich failed: ${res.status}`)
  return res.json()
}

export async function exportReport(payload) {
  // Not implemented yet — POST /api/report/export is future scope
  // for this setup step. Placeholder so M2 can wire the button now.
  throw new Error('exportReport() not implemented yet')
}
