import { useState } from 'react'

export default function App() {
  const [n, setN] = useState(17)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const apiBase =
    import.meta.env.VITE_API_URL ||
    `http://${window.location.hostname}:8000/is_prime`

  async function handleCheck() {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await fetch(apiBase, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ n: Number(n) })
      })
      if (!res.ok) throw new Error(await res.text())
      const data = await res.json()
      setResult(data)
    } catch (err) {
      setError(String(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <div className="header">
        <h1>Prime Checker</h1>
      </div>

      <div className="form-row">
        <label>Number</label>
        <input type="number" value={n} onChange={(e) => setN(e.target.value)} />
      </div>

      <div className="buttons">
        <button onClick={handleCheck} disabled={loading}>CHECK</button>
      </div>

      {loading && <div className="status">Loading…</div>}
      {error && <div className="error">Error: {error}</div>}
      {result && (
        <div className="result">
          {result.is_prime ? 'Yes, it is prime.' : 'No, it is not prime.'}
        </div>
      )}
    </div>
  )
}
