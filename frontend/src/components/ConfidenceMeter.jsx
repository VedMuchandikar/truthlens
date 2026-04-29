export default function ConfidenceMeter({ confidence, verdict }) {
    const pct = Math.round(confidence * 100)
    const color =
        verdict === 'SCAM' ? 'bg-red-500'
            : verdict === 'SUSPICIOUS' ? 'bg-amber-500'
                : 'bg-green-500'

    return (
        <div className="w-full">
            <div className="flex justify-between text-xs text-gray-500 mb-1">
                <span>Confidence</span>
                <span className="font-semibold text-gray-700">{pct}%</span>
            </div>
            <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
                <div
                    className={`h-full rounded-full transition-all duration-700 ${color}`}
                    style={{ width: `${pct}%` }}
                />
            </div>
        </div>
    )
}