import { useState } from 'react'

export function usePagination(initialPage = 1, initialPageSize = 20) {
  const [page, setPage] = useState(initialPage)
  const [pageSize, setPageSize] = useState(initialPageSize)

  const nextPage = () => setPage((p) => p + 1)
  const prevPage = () => setPage((p) => Math.max(1, p - 1))
  const goToPage = (p) => setPage(Math.max(1, p))

  return {
    page,
    pageSize,
    setPage,
    setPageSize,
    nextPage,
    prevPage,
    goToPage,
  }
}
