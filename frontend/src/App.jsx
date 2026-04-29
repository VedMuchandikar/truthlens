import { useState } from 'react'
import { analyzeText } from './api/analyzer'
import ResultCard from './components/ResultCard'
import { Loader2, Shield, AlertTriangle } from 'lucide-react'

const INPUT_TYPES = ['TEXT', 'WHATSAPP', 'EMAIL', 'URL']

export default function App() {
  const [text, setText] = useState('')
  const [inputType, setInputType] = useState('TEXT')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleAnalyze = async () => {
    if (!text.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const data = await analyzeText(text, inputType)
      setResult(data)
    } catch (err) {
      const msg = err.response?.data?.message ?? err.message ?? 'Something went wrong.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      handleAnalyze()
    }
  }

  return (
      <div className="min-h-screen bg-gray-50 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="max-w-2xl mx-auto flex items-center gap-3">
            <Shield className="text-blue-600" size={24} />
            <span className="text-xl font-semibold text-gray-900">TruthLens</span>
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-medium">
            Phase 1
          </span>
          </div>
        </header>

        {/* Main */}
        <main className="flex-1 flex items-start justify-center px-4 py-10">
          <div className="w-full max-w-2xl space-y-6">
            {/* Hero */}
            <div className="text-center">
              <h1 className="text-3xl font-bold text-gray-900">Is this real?</h1>
              <p className="text-gray-500 mt-2 text-base">
                Paste any message, forward, or text — we'll tell you if it's a scam.
              </p>
            </div>

            {/* Input card */}
            <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-sm space-y-4">
              {/* Input type selector */}
              <div className="flex gap-2 flex-wrap">
                {INPUT_TYPES.map((type) => (
                    <button
                        key={type}
                        onClick={() => setInputType(type)}
                        className={`px-3 py-1 rounded-lg text-xs font-semibold border transition-colors ${
                            inputType === type
                                ? 'bg-blue-600 text-white border-blue-600'
                                : 'bg-white text-gray-600 border-gray-200 hover:border-blue-300'
                        }`}
                    >
                      {type}
                    </button>
                ))}
              </div>

              {/* Textarea */}
              <textarea
                  className="w-full h-36 resize-none rounded-xl border border-gray-200 bg-gray-50 p-4 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                  placeholder={
                    inputType === 'WHATSAPP'
                        ? "Paste WhatsApp forward here..."
                        : inputType === 'EMAIL'
                            ? "Paste suspicious email content here..."
                            : "Paste any text, message, or news headline here... (Ctrl+Enter to analyze)"
                  }
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  onKeyDown={handleKeyDown}
              />

              {/* Analyze button */}
              <button
                  onClick={handleAnalyze}
                  disabled={loading || !text.trim()}
                  className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-blue-600 text-white font-semibold text-sm hover:bg-blue-700 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {loading ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      Analyzing...
                    </>
                ) : (
                    'Analyze'
                )}
              </button>
            </div>

            {/* Error state */}
            {error && (
                <div className="flex gap-3 items-start bg-red-50 border border-red-200 rounded-xl p-4">
                  <AlertTriangle size={18} className="text-red-500 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-red-700">{error}</p>
                </div>
            )}

            {/* Result */}
            <ResultCard result={result} />

            {/* Sample inputs */}
            {!result && !loading && (
                <div className="space-y-2">
                  <p className="text-xs text-gray-400 font-semibold uppercase tracking-wide">
                    Try these samples
                  </p>
                  {[
                    { label: 'Scam SMS', text: 'Congratulations! You\'ve won ₹50,000. Click bit.ly/clm to claim your prize now before it expires!' },
                    { label: 'Genuine', text: 'Hey, are we still meeting for lunch at 1pm? Let me know if you need to reschedule.' },
                    { label: 'Phishing', text: 'URGENT: Your bank account has been suspended. Verify your details immediately at secure-bank-login.xyz' },
                  ].map((s) => (
                      <button
                          key={s.label}
                          onClick={() => setText(s.text)}
                          className="w-full text-left px-4 py-3 bg-white border border-gray-200 rounded-xl text-sm text-gray-600 hover:border-blue-300 hover:text-gray-900 transition-colors"
                      >
                        <span className="font-medium text-gray-800">{s.label}:</span> {s.text.slice(0, 70)}...
                      </button>
                  ))}
                </div>
            )}
          </div>
        </main>
      </div>
  )
}