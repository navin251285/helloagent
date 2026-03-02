import { useMemo, useState } from 'react'

const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  `${window.location.protocol}//${window.location.hostname}:8000`

function App() {
  const [value, setValue] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const parsed = useMemo(() => {
    if (value.trim() === '') return null
    return Number(value)
  }, [value])

  const clientValidationError = useMemo(() => {
    if (value.trim() === '') return 'Please enter a number.'
    if (!Number.isFinite(parsed)) return 'Please enter a valid number.'
    if (!Number.isInteger(parsed)) return 'Only whole numbers are allowed.'
    if (parsed < 0) return 'Number must be 0 or greater.'
    if (parsed > 1_000_000_000_000) return 'Number must be less than or equal to 1,000,000,000,000.'
    return ''
  }, [value, parsed])

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setResult(null)

    if (clientValidationError) {
      setError(clientValidationError)
      return
    }

    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/api/prime`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ number: parsed })
      })

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}))
        throw new Error(payload?.detail?.[0]?.msg || 'Unable to validate number right now.')
      }

      const payload = await response.json()
      setResult(payload)
    } catch (submissionError) {
      setError(submissionError.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="page" aria-labelledby="page-title">
      <section className="card">
        <p className="eyebrow">Number Intelligence</p>
        <h1 id="page-title">Prime Aura</h1>
        <p className="subtitle">Type any whole number and instantly see whether it is prime.</p>

        <form className="prime-form" onSubmit={handleSubmit} noValidate>
          <label htmlFor="prime-input">Enter a whole number</label>
          <div className="input-wrap">
            <input
              id="prime-input"
              type="number"
              inputMode="numeric"
              min="0"
              max="1000000000000"
              placeholder="e.g. 97"
              value={value}
              onChange={(event) => setValue(event.target.value)}
              aria-describedby="validation-message"
              required
            />
            <button type="submit" disabled={loading}>
              {loading ? 'Checking…' : 'Validate'}
            </button>
          </div>
        </form>

        <p id="validation-message" className="message error" role="alert" aria-live="assertive">
          {error}
        </p>

        {result && (
          <section
            className={`result ${result.is_prime ? 'success' : 'neutral'}`}
            aria-live="polite"
            aria-atomic="true"
          >
            <p className="result-number">Number: {result.number}</p>
            <p className="result-text">{result.message}</p>
          </section>
        )}
      </section>
    </main>
  )
}

export default App
