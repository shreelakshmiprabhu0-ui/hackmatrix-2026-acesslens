// Owned by Module 1. Friendly error state for when the scan request
// itself fails (network error, backend down, non-2xx response) — as
// opposed to UrlForm's inline validation error for bad input.

function ScanErrorBanner({ message, onRetry }) {
  return (
    <div
      role="alert"
      className="mt-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
    >
      <p className="font-medium">We couldn't scan that site.</p>
      <p className="mt-1">{message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-2 rounded font-medium text-red-700 underline underline-offset-2 hover:text-red-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500"
        >
          Dismiss
        </button>
      )}
    </div>
  )
}

export default ScanErrorBanner
