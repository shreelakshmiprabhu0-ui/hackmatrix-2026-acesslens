// Owned by Module 1. Client-side validation for the scan URL input.
// Kept separate from UrlForm so the validation rules are easy to find
// and unit-test independently of the component.

/**
 * Validates a raw string typed into the URL input.
 *
 * Accepts URLs typed without a protocol (e.g. "example.com") and
 * normalizes them to "https://example.com". Rejects empty input,
 * non-URL strings, non-http(s) protocols, and hostnames with no dot
 * (since AccessLens scans public websites, not bare hostnames).
 *
 * @param {string} rawInput
 * @returns {{ valid: true, url: string } | { valid: false, error: string }}
 */
export function validateUrl(rawInput) {
  const trimmed = (rawInput ?? '').trim()

  if (!trimmed) {
    return { valid: false, error: 'Please enter a website URL.' }
  }

  // Only add a protocol if the user didn't type one at all — if they typed
  // a non-http(s) scheme (e.g. "ftp://…"), leave it as-is so it's rejected
  // by the protocol check below with an accurate message, instead of being
  // mangled into "https://ftp://…".
  const hasScheme = /^[a-z][a-z0-9+.-]*:\/\//i.test(trimmed)
  const candidate = hasScheme ? trimmed : `https://${trimmed}`

  let parsed
  try {
    parsed = new URL(candidate)
  } catch {
    return {
      valid: false,
      error: 'Enter a valid website URL, e.g. https://example.com',
    }
  }

  if (!['http:', 'https:'].includes(parsed.protocol)) {
    return { valid: false, error: 'URL must start with http:// or https://' }
  }

  if (!parsed.hostname.includes('.')) {
    return {
      valid: false,
      error: 'Enter a full website address, e.g. https://example.com',
    }
  }

  return { valid: true, url: parsed.toString() }
}
