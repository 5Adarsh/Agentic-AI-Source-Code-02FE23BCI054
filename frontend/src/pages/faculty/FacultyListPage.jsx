import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getFaculty } from '../../api/faculty'
import Card from '../../components/ui/Card'
import Table from '../../components/ui/Table'
import EmptyState from '../../components/ui/EmptyState'
import SearchInput from '../../components/ui/SearchInput'
import Spinner from '../../components/ui/Spinner'
import Badge from '../../components/ui/Badge'

export default function FacultyListPage() {
  const [facultyList, setFacultyList] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const data = await getFaculty({ search })
        setFacultyList(data || [])
      } catch (err) {
        setFacultyList([])
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [search])

  const columns = [
    {
      header: 'Faculty Name',
      accessor: 'full_name',
      render: (row) => (
        <Link to={`/faculty/${row.id}`} className="font-semibold text-indigo-600 hover:underline">
          {row.full_name}
        </Link>
      ),
    },
    { header: 'Faculty ID', accessor: 'faculty_id' },
    { header: 'Email', accessor: 'email' },
    { header: 'Designation', accessor: 'designation' },
    {
      header: 'ORCID',
      accessor: 'orcid',
      render: (row) => {
        const clean = row.orcid ? row.orcid.replace(/^https?:\/\/orcid\.org\//, '').trim() : null
        return clean ? (
          <a
            href={`https://orcid.org/${clean}`}
            target="_blank"
            rel="noreferrer"
            className="text-xs font-mono text-emerald-600 font-semibold hover:underline flex items-center gap-1"
          >
            <span>🔗</span> {clean}
          </a>
        ) : (
          <span className="text-slate-400 text-xs">—</span>
        )
      },
    },
    {
      header: 'Status',
      accessor: 'is_active',
      render: (row) => (
        <Badge status={row.is_active ? 'verified' : 'unverified'}>
          {row.is_active ? 'Active' : 'Inactive'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Faculty Roster</h1>
          <p className="text-xs text-slate-500 mt-1">
            Registered academic faculty and scholarly profile identifiers
          </p>
        </div>
        <Link
          to="/faculty/new"
          className="inline-flex items-center px-4 py-2 text-xs font-semibold rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm transition-colors"
        >
          + Add Faculty Member
        </Link>
      </div>

      <div className="max-w-md">
        <SearchInput value={search} onChange={setSearch} placeholder="Search faculty name or ID..." />
      </div>

      {loading ? (
        <Spinner size="lg" className="py-12" />
      ) : facultyList.length === 0 ? (
        <EmptyState
          icon="👨‍🏫"
          title="No Faculty Members Registered"
          description="Register your first faculty member or run the Faculty Profile Agent to link institutional profiles."
          action={
            <Link
              to="/faculty/new"
              className="inline-flex items-center px-4 py-2 text-xs font-medium rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 transition-colors"
            >
              Register Faculty
            </Link>
          }
        />
      ) : (
        <Card className="p-0">
          <Table columns={columns} data={facultyList} />
        </Card>
      )}
    </div>
  )
}
