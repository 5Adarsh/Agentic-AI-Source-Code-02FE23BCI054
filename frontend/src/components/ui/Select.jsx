export default function Select({
  label,
  options = [],
  value,
  onChange,
  placeholder = 'Select...',
  className = '',
}) {
  const handleChange = (e) => {
    if (!onChange) return
    // Support both `(e) => set(e.target.value)` and direct `(val) => set(val)`
    onChange(e)
  }

  return (
    <div className={`flex flex-col gap-1 ${className}`}>
      {label && <label className="text-xs font-semibold text-slate-700">{label}</label>}
      <select
        value={value}
        onChange={handleChange}
        className="px-3 py-2 border border-slate-300 rounded-lg text-xs bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 shadow-xs"
      >
        {placeholder && <option value="">{placeholder}</option>}
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  )
}
