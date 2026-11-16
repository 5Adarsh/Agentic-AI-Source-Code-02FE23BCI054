export default function Table({ columns, data = [], emptyMessage = 'No records found' }) {
  if (!data || data.length === 0) {
    return (
      <div className="text-center py-8 text-sm text-slate-500">
        {emptyMessage}
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
        <thead className="bg-slate-50 text-slate-600 font-medium">
          <tr>
            {columns.map((col, idx) => (
              <th key={idx} className="px-4 py-3">
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 bg-white">
          {data.map((row, rowIdx) => (
            <tr key={row.id || rowIdx} className="hover:bg-slate-50 transition-colors">
              {columns.map((col, colIdx) => (
                <td key={colIdx} className="px-4 py-3 text-slate-700">
                  {col.render ? col.render(row) : row[col.accessor]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
