import { useId } from "react";
import { motion } from "framer-motion";

export function ConfidenceRing({ value, size = 40 }: { value: number; size?: number }) {
  const stroke = 3;
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const offset = c - (value / 100) * c;
  const gradientId = useId();

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90 overflow-visible">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="rgba(245,243,238,0.08)" strokeWidth={stroke} />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={`url(#${gradientId})`}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={c}
          initial={{ strokeDashoffset: c }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: [0.65, 0, 0.35, 1] }}
          style={{ filter: `drop-shadow(0 0 3px rgba(227,196,107,0.5))` }}
        />
        <defs>
          <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#E3C46B" />
            <stop offset="100%" stopColor="#C9A227" />
          </linearGradient>
        </defs>
      </svg>
      <span className="absolute font-mono text-[10px] tabular-nums text-[var(--color-gold-200)]">{value}</span>
    </div>
  );
}
