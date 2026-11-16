export default function Pagination({ page, totalPages = 1, onNext, onPrev, onPageChange }) {
  if (totalPages <= 1) return null

  return (
    <div className="flex items-center justify-between px-4 py-3 bg-white border-t border-slate-200 sm:px-6">
      <div className="flex justify-between sm:hidden w-full">
        <button
          onClick={onPrev}
          disabled={page <= 1}
          className="px-3 py-1 text-xs border rounded-md disabled:opacity-40"
        >
          Previous
        </button>
        <span className="text-xs self-center">
          Page {page} of {totalPages}
        </span>
        <button
          onClick={onNext}
          disabled={page >= totalPages}
          className="px-3 py-1 text-xs border rounded-md disabled:opacity-40"
        >
          Next
        </button>
      </div>

      <div className="hidden sm:flex sm:items-center sm:justify-between w-full">
        <div>
          <p className="text-xs text-slate-700">
            Page <span className="font-medium">{page}</span> of{' '}
            <span className="font-medium">{totalPages}</span>
          </p>
        </div>
        <div className="inline-flex gap-1">
          <button
            onClick={onPrev}
            disabled={page <= 1}
            className="px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded-md hover:bg-slate-50 disabled:opacity-40"
          >
            Previous
          </button>
          <button
            onClick={onNext}
            disabled={page >= totalPages}
            className="px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded-md hover:bg-slate-50 disabled:opacity-40"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  )
}
