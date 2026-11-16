import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getFaculty } from '../../api/faculty'
import { triggerAgent } from '../../api/agents'
import Card from '../../components/ui/Card'
import FileUpload from '../../components/ui/FileUpload'
import Select from '../../components/ui/Select'
import Button from '../../components/ui/Button'
import Alert from '../../components/ui/Alert'

export default function ImportPage() {
  const [facultyList, setFacultyList] = useState([])
  const [selectedFaculty, setSelectedFaculty] = useState('')
  const [file, setFile] = useState(null)
  const [csvText, setCsvText] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState(null)
  const [error, setError] = useState(null)

  const navigate = useNavigate()

  useEffect(() => {
    async function load() {
      try {
        const list = await getFaculty()
        setFacultyList(list || [])
        if (list && list.length > 0) {
          setSelectedFaculty(list[0].id)
        }
      } catch (err) {
        // Faculty list may be empty initially
      }
    }
    load()
  }, [])

  const handleFileSelect = (selectedFile) => {
    setFile(selectedFile)
    const reader = new FileReader()
    reader.onload = (e) => {
      setCsvText(e.target.result)
    }
    reader.readAsText(selectedFile)
  }

  const handleHarvest = async () => {
    if (!csvText && !selectedFaculty) {
      setError('Please provide a Google Scholar CSV file or select a faculty profile.')
      return
    }

    setLoading(true)
    setError(null)
    setMessage(null)

    try {
      await triggerAgent('scholar_harvest_agent', {
        faculty_id: selectedFaculty || null,
        scholar_csv_content: csvText,
      })
      setMessage('Google Scholar Harvest Agent successfully triggered! Ingesting records.')
      setTimeout(() => {
        navigate('/agents')
      }, 1500)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to dispatch Harvest Agent.')
    } finally {
      setLoading(false)
    }
  }

  const facultyOptions = facultyList.map((f) => ({
    label: `${f.full_name} (${f.faculty_id})`,
    value: f.id,
  }))

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900">Import & Harvest Publications</h1>
        <p className="text-xs text-slate-500 mt-1">
          Upload faculty Google Scholar CSV export or trigger automated API retrieval
        </p>
      </div>

      {message && <Alert type="success" message={message} />}
      {error && <Alert type="error" message={error} onClose={() => setError(null)} />}

      <Card title="Google Scholar CSV Upload">
        <div className="space-y-4">
          <Select
            label="Associate With Faculty Member"
            options={facultyOptions}
            value={selectedFaculty}
            onChange={(e) => setSelectedFaculty(e.target ? e.target.value : e)}
            placeholder={facultyList.length === 0 ? 'No registered faculty found' : 'Select faculty member'}
          />

          <div>
            <label className="text-xs font-medium text-slate-700 block mb-1">
              Google Scholar CSV File
            </label>
            <FileUpload
              onFileSelect={handleFileSelect}
              accept=".csv"
              label="Drop Google Scholar CSV export here"
            />
          </div>

          <div className="pt-2 flex justify-end">
            <Button
              onClick={handleHarvest}
              isLoading={loading}
              disabled={!csvText && !selectedFaculty}
            >
              Dispatch Scholar Harvest Agent
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}
