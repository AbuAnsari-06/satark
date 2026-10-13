import { useState, useRef, useEffect } from 'react'
import Header from './components/Header'
import InputCard from './components/InputCard'
import SampleChips from './components/SampleChips'
import LoadingSkeleton from './components/LoadingSkeleton'
import RiskGauge from './components/RiskGauge'
import HighlightedMessage from './components/HighlightedMessage'
import ScoreBreakdown from './components/ScoreBreakdown'
import ScamExplainer from './components/ScamExplainer'
import LinkInspector from './components/LinkInspector'
import ActionableGuidance from './components/ActionableGuidance'
import Footer from './components/Footer'
import { analyzeMessageOrScreenshot } from './api'
import { AlertCircle } from 'lucide-react'

function App() {
  const [lang, setLang] = useState('en')
  const [text, setText] = useState('')
  const [imageFile, setImageFile] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const resultRef = useRef(null)

  const handleSelectSample = (sampleText) => {
    setText(sampleText)
    if (imagePreview) {
      URL.revokeObjectURL(imagePreview)
    }
    setImageFile(null)
    setImagePreview(null)
    setError(null)
  }

  const handleReset = () => {
    setText('')
    if (imagePreview) {
      URL.revokeObjectURL(imagePreview)
    }
    setImageFile(null)
    setImagePreview(null)
    setError(null)
    setResult(null)
  }

  const handleAnalyze = async () => {
    if (!text.trim() && !imageFile) return

    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      const data = await analyzeMessageOrScreenshot({
        text: text.trim() ? text : undefined,
        image: imageFile || undefined,
      })
      setResult(data)
    } catch (err) {
      setError(err.message || "Failed to analyze message.")
    } finally {
      setIsLoading(false)
    }
  }

  // Smooth scroll to result card on completion
  useEffect(() => {
    if (result && resultRef.current) {
      resultRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, [result])

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900 antialiased selection:bg-blue-100 selection:text-blue-900">
      <Header lang={lang} setLang={setLang} />

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 py-6 sm:py-10 space-y-8">
        {/* Error notification banner */}
        {error && (
          <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 flex items-start gap-3 shadow-xs">
            <AlertCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
            <div className="text-sm">
              <p className="font-semibold">{lang === 'hi' ? 'त्रुटि (Error)' : 'Analysis Request Error'}</p>
              <p className="mt-0.5 text-red-700">{error}</p>
            </div>
          </div>
        )}

        {/* Input Card with sample chips */}
        <InputCard
          text={text}
          setText={setText}
          imageFile={imageFile}
          setImageFile={setImageFile}
          imagePreview={imagePreview}
          setImagePreview={setImagePreview}
          onAnalyze={handleAnalyze}
          isLoading={isLoading}
          lang={lang}
        >
          <SampleChips onSelectSample={handleSelectSample} lang={lang} />
        </InputCard>

        {/* Shimmer loading skeleton */}
        {isLoading && <LoadingSkeleton lang={lang} />}

        {/* Complete Result Card Section */}
        {result && (
          <div
            ref={resultRef}
            id="analysis-result-container"
            className="space-y-6 pt-2 animate-fadeIn transition-all"
          >
            {/* 1. Verdict Banner & Risk Gauge */}
            <RiskGauge
              verdict={result.verdict}
              riskScore={result.risk_score}
              aiAvailable={result.ai_available}
              lang={lang}
            />

            {/* 2. Message View with In-Context Phrase Highlighting */}
            <HighlightedMessage
              text={result.extracted_text}
              suspiciousPhrases={result.suspicious_phrases}
              verdict={result.verdict}
              lang={lang}
            />

            {/* 3. Score Breakdown & Red Flags */}
            <ScoreBreakdown
              scoreBreakdown={result.score_breakdown}
              redFlags={result.red_flags}
              aiAvailable={result.ai_available}
              lang={lang}
            />

            {/* 4. Scam Taxonomy & Educational Explainer */}
            <ScamExplainer
              scamType={result.scam_type}
              howItWorks={result.how_it_works}
              explanationEn={result.explanation_en}
              explanationHi={result.explanation_hi}
              verdict={result.verdict}
              lang={lang}
            />

            {/* 5. Local Link Inspector Table */}
            <LinkInspector links={result.links} lang={lang} />

            {/* 6. Actionable Guidance, Helplines & Sharing Tools */}
            <ActionableGuidance
              nextSteps={result.next_steps}
              familyAlert={result.family_alert}
              reportSummary={result.report_summary}
              verdict={result.verdict}
              lang={lang}
            />
          </div>
        )}
      </main>

      {/* Footer & Reset Controls */}
      <Footer hasResult={!!result} onReset={handleReset} lang={lang} />
    </div>
  )
}

export default App
