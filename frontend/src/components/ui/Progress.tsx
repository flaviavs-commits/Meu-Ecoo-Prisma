type ProgressProps = { value: number; label?: string; className?: string }

export function Progress({ value, label, className = '' }: ProgressProps) {
  const clamped = Math.max(0, Math.min(100, value))
  return <div className={['grid gap-2', className].join(' ')}>{label && <div className="flex justify-between gap-4 text-xs text-texto-secundario"><span>{label}</span><span>{clamped}%</span></div>}<div className="h-2 overflow-hidden rounded-full bg-superficie-alt" role="progressbar" aria-label={label} aria-valuenow={clamped} aria-valuemin={0} aria-valuemax={100}><div className="h-full rounded-full bg-primaria transition-[width] duration-500" style={{ width: `${clamped}%` }} /></div></div>
}
