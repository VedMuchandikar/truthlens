export default function TopFeatures({ features }) {
    if (!features || features.length === 0) return null

    // Only show words that pushed toward SCAM (positive weight)
    const flagged = features.filter(f => f.weight > 0).slice(0, 6)
    if (flagged.length === 0) return null

    return (
        <div className="mt-4">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                Flagged signals
            </p>
            <div className="flex flex-wrap gap-2">
                {flagged.map((f) => (
                    <span
                        key={f.word}
                        className="px-2.5 py-1 bg-red-50 text-red-700 border border-red-200 rounded-md text-xs font-mono"
                        title={`Weight: ${f.weight.toFixed(3)}`}
                    >
            {f.word}
          </span>
                ))}
            </div>
        </div>
    )
}