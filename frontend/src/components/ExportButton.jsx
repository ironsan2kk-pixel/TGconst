import { Download } from 'lucide-react'

export default function ExportButton({ onClick, loading = false, label = 'Экспорт CSV' }) {
  return (
    <button
      onClick={onClick}
      disabled={loading}
      className="btn btn-secondary flex items-center gap-2"
    >
      {loading ? (
        <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
      ) : (
        <Download className="w-4 h-4" />
      )}
      {label}
    </button>
  )
}

// Helper function to download blob
export function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
}
