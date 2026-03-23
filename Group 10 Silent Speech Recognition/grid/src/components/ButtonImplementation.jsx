import React, { useState } from 'react'

const ButtonImplementation = () => {
  const [selectedFile, setSelectedFile] = useState(null)

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    setSelectedFile(file)
  }

  const [loading, setLoading] = useState(false)
  const [prediction, setPrediction] = useState(null)
  const [error, setError] = useState(null)

  const handlePredict = async () => {
    if (!selectedFile) return
    setLoading(true)
    setPrediction(null)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('video', selectedFile)

      const resp = await fetch('http://localhost:10000/predict', {
        method: 'POST',
        body: formData,
      })

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}))
        throw new Error(err.error || `Server responded ${resp.status}`)
      }

      const data = await resp.json()
      setPrediction(data.prediction)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="min-h-screen flex flex-col items-center justify-center bg-black text-[#64dfdf] px-6 py-12">
      <h1 className="text-3xl md:text-5xl font-bold mb-6 text-center">Upload Your Silent Speech Video</h1>
      <p className="text-[1.5rem] text-gray-300 mb-8 text-center max-w-2xl">
        Choose a video file to begin processing with our silent speech recognition system.
      </p>

      {/* File Input */}
      <label className="bg-black text-gray-200 border border-gray-200 px-4 py-2 rounded-lg cursor-pointer">
        Choose a file
        <input
          type="file"
          accept="video/*"
          onChange={handleFileChange}
          className="hidden"
        />
      </label>

      {/* File Name Display */}
      {selectedFile && (
        <p className="mt-4 text-gray-300 text-center">
          Selected file: <span className="text-[#64dfdf] font-medium">{selectedFile.name}</span>
        </p>
      )}

      {/* Predict Button */}
      {selectedFile && (
        <div className="mt-6 flex flex-col items-center">
          <button
            onClick={handlePredict}
            disabled={loading}
            className="bg-[#64dfdf] text-black px-6 py-2 rounded-lg font-semibold hover:opacity-90 disabled:opacity-60"
          >
            {loading ? 'Predicting...' : 'Predict'}
          </button>

          {prediction && (
            <div className="mt-4 bg-gray-900 border border-gray-700 p-4 rounded-md max-w-xl text-center">
              <h3 className="text-lg font-semibold mb-2">Prediction</h3>
              <p className="text-[#64dfdf]">{prediction}</p>
            </div>
          )}

          {error && (
            <div className="mt-4 text-sm text-red-400">Error: {error}</div>
          )}
        </div>
      )}
    </section>
  )
}

export default ButtonImplementation