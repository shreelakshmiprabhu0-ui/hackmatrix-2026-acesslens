// Owned by Module 1. Loading indicator shown below the form while a
// scan is in flight. role="status" + aria-live so screen reader users
// get an announcement without anything having to move focus.

import Spinner from './Spinner.jsx'

function LoadingState({ url }) {
  return (
    <div
      role="status"
      aria-live="polite"
      className="mt-6 flex items-center gap-3 rounded-lg border border-indigo-100 bg-indigo-50 px-4 py-3 text-sm text-indigo-800"
    >
      <Spinner className="h-5 w-5 text-indigo-600" />
      <span>
        Scanning <span className="font-medium break-all">{url}</span> for
        accessibility issues — this can take a few seconds…
      </span>
    </div>
  )
}

export default LoadingState
