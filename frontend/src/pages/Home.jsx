// Owned by Module 1 (Shreelakshmi). URL input + scan-initiation flow.
// Client-side validation lives in UrlForm/urlValidation.js; this page
// owns the scan lifecycle (loading, API errors) and handing the result
// off to the Results page.

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import LoadingState from '../components/input/LoadingState.jsx'
import ScanErrorBanner from '../components/input/ScanErrorBanner.jsx'
import UrlForm from '../components/input/UrlForm.jsx'
import { scanUrl } from '../api/client.js'

function Home() {
  const navigate = useNavigate()
  const [isScanning, setIsScanning] = useState(false)
  const [scanningUrl, setScanningUrl] = useState('')
  const [apiError, setApiError] = useState('')

  async function handleScan(url) {
    setApiError('')
    setScanningUrl(url)
    setIsScanning(true)

    try {
      const scanResult = await scanUrl(url)
      // Hand the scan response to the Results page via router state —
      // the M1/M2 integration point from the execution plan. M2 reads
      // it from `useLocation().state?.scanResult` on the Results page.
      navigate('/results', { state: { scanResult } })
    } catch (err) {
      setApiError(
        "We couldn't complete the scan. Check the URL and your connection, then try again."
      )
    } finally {
      setIsScanning(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-5 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-slate-900 text-white flex items-center justify-center font-bold text-lg">
            A
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">AccessLens</h1>
            <p className="text-xs text-slate-500">Web Accessibility Analyzer</p>
          </div>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-6 py-16">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-slate-900 sm:text-3xl">
            Scan any website for accessibility issues
          </h2>
          <p className="mt-2 text-slate-600">
            Enter a public website URL and AccessLens will audit it for
            accessibility issues and explain them in plain English.
          </p>
        </div>

        <div className="mt-8 rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <UrlForm onSubmit={handleScan} isSubmitting={isScanning} />

          {isScanning && <LoadingState url={scanningUrl} />}

          {apiError && !isScanning && (
            <ScanErrorBanner message={apiError} onRetry={() => setApiError('')} />
          )}
        </div>
      </main>
    </div>
  )
}

export default Home
