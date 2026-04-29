const config = {
    SCAM: {
        bg: 'bg-red-100',
        text: 'text-red-800',
        border: 'border-red-200',
        label: '🚨 Scam Detected',
    },
    SUSPICIOUS: {
        bg: 'bg-amber-100',
        text: 'text-amber-800',
        border: 'border-amber-200',
        label: '⚠️ Suspicious',
    },
    GENUINE: {
        bg: 'bg-green-100',
        text: 'text-green-800',
        border: 'border-green-200',
        label: '✅ Likely Genuine',
    },
}

export default function VerdictBadge({ verdict }) {
    const c = config[verdict] ?? config.SUSPICIOUS
    return (
        <span className={`inline-flex items-center px-4 py-1.5 rounded-full text-sm font-semibold border ${c.bg} ${c.text} ${c.border}`}>
      {c.label}
    </span>
    )
}