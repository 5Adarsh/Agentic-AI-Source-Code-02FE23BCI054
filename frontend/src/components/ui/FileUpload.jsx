import { useState, useRef } from 'react'

export default function FileUpload({ onFileSelect, accept = '.csv', label = 'Upload CSV File' }) {
  const [dragActive, setDragActive] = useState(false)
  const [fileName, setFileName] = useState(null)
  const inputRef = useRef(null)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      setFileName(file.name)
      onFileSelect(file)
    }
  }

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      setFileName(file.name)
      onFileSelect(file)
    }
  }

  return (
    <div
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
        dragActive ? 'border-indigo-500 bg-indigo-50/30' : 'border-slate-300 hover:border-slate-400 bg-slate-50/50'
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        onChange={handleChange}
        className="hidden"
      />
      <div className="flex flex-col items-center">
        <span className="text-3xl mb-2">📁</span>
        <p className="text-sm font-medium text-slate-800">{fileName || label}</p>
        <p className="text-xs text-slate-500 mt-1">
          Drag and drop or click to browse (supports {accept})
        </p>
      </div>
    </div>
  )
}
