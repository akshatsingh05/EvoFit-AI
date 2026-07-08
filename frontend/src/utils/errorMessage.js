/**
 * Safely extracts a human-readable message from an axios error.
 *
 * FastAPI's `detail` field is a plain string for most errors (e.g. "Incorrect
 * email or password") but is a LIST of validation-error objects
 * (`{type, loc, msg, ...}`) for 422 request-validation failures. Rendering
 * that list directly as a React child (e.g. `{err.response?.data?.detail}`)
 * throws "Objects are not valid as a React child" and crashes the page --
 * this normalizes both shapes into a single string every caller can safely
 * render.
 */
export function getErrorMessage(err, fallback = 'Something went wrong. Please try again.') {
  const detail = err?.response?.data?.detail

  if (typeof detail === 'string' && detail.trim()) {
    return detail
  }

  if (Array.isArray(detail) && detail.length > 0) {
    return detail
      .map((item) => (typeof item?.msg === 'string' ? item.msg : null))
      .filter(Boolean)
      .join(' ') || fallback
  }

  return fallback
}
