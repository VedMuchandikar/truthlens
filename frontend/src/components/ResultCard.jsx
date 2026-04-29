import VerdictBadge from './VerdictBadge'
import ConfidenceMeter from './ConfidenceMeter'
import TopFeatures from './TopFeatures'

export default function ResultCard({ result }) {
    if (!result) return null

    return (
        <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-5 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="flex items-center justify-between flex-wrap gap-3">
                <VerdictBadge verdict={result.verdict} />
                <span className="text-xs text-gray-400">ID #{result.id}</span>
            </div>

            <ConfidenceMeter confidence={result.confidence} verdict={result.verdict} />

            {result.probabilities && (
                <div className="grid grid-cols-2 gap-2">
                    {Object.entries(result.probabilities).map(([label, prob]) => (
                        <div key={label} className="bg-gray-50 rounded-lg px-3 py-2 text-center">
                            <p className="text-xs text-gray-500">{label}</p>
                            <p className="text-base font-semibold text-gray-800">
                                {Math.round(prob * 100)}%
                            </p>
                        </div>
                    ))}
                </div>
            )}

            <TopFeatures features={result.topFeatures} />

            <p className="text-xs text-gray-400 text-right">
                Analyzed at {new Date(result.analyzedAt).toLocaleTimeString()}
            </p>
        </div>
    )
}