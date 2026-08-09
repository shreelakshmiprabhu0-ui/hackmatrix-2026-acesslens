// Owned by Module 1. The URL input + "Scan Website" button. Handles its
// own client-side validation (empty / malformed URL) and reports a
// clean, normalized URL up to Home.jsx via onSubmit — Home.jsx owns
// what happens next (calling the API, navigating, etc.).

import { useId, useState } from 'react'
import Spinner from './Spinner.jsx'
import { validateUrl } from './urlValidation.js'

function UrlForm({ onSubmit, isSubmitting }) {
  const [value, setValue] = useState('')
  const [error, setError] = useState('')
  const inputId = useId()
  const errorId = useId()

  function handleChange(event) {
    setValue(event.target.value)
    if (error) setError('')
  }

  function handleSubmit(event) {
    event.preventDefault()
    if (isSubmitting) return

    const result = validateUrl(value)
    if (!result.valid) {
      setError(result.error)
      return
    }

    setError('')
    onSubmit(result.url)
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      <label
        htmlFor={inputId}
        className="mb-1.5 block text-sm font-medium text-slate-700"
      >
        Website URL
      </label>

      <div className="flex flex-col gap-3 sm:flex-row">
        <input
          id={inputId}
          name="url"
          type="text"
          inputMode="url"
          autoComplete="url"
          autoCapitalize="none"
          autoCorrect="off"
          spellCheck="false"
          placeholder="https://example.com"
          value={value}
          onChange={handleChange}
          disabled={isSubmitting}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={error ? errorId : undefined}
          className={`w-full flex-1 rounded-lg border bg-white px-4 py-2.5 text-slate-900 shadow-sm outline-none transition placeholder:text-slate-400 focus-visible:ring-2 focus-visible:ring-offset-1 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-400 ${
            error
              ? 'border-red-400 focus-visible:ring-red-400'
              : 'border-slate-300 focus-visible:ring-indigo-500'
          }`}
        />

        <button
          type="submit"
          disabled={isSubmitting}
          className="inline-flex shrink-0 items-center justify-center gap-2 rounded-lg bg-indigo-600 px-6 py-2.5 font-semibold text-white shadow-sm transition hover:bg-indigo-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-1 disabled:cursor-not-allowed disabled:bg-indigo-300"
        >
          {isSubmitting ? (
            <>
              <Spinner className="h-4 w-4" />
              Scanning…
            </>
          ) : (
            'Scan Website'
          )}
        </button>
      </div>

      {error && (
        <p id={errorId} role="alert" className="mt-2 text-sm text-red-600">
          {error}
        </p>
      )}
    </form>
  )
}

export default UrlForm
