import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'
import HomePage from './pages/HomePage'
import ScannerPage from './pages/ScannerPage'
import DatabasePage from './pages/DatabasePage'
import Navbar from './components/Navbar'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/scanner" element={<ScannerPage />} />
          <Route path="/database" element={<DatabasePage />} />
        </Routes>
      </div>
    </Router>
  )
}

  // Cleanup function to revoke object URLs
  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl)
      }
    }
  }, [previewUrl])

  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    if (file) {
      console.log('File selected:', file.name, file.type, file.size)
      
      // Validate file type
      if (!file.type.startsWith('image/')) {
        alert('Please select a valid image file (PNG, JPG, JPEG)')
        return
      }
      
      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB')
        return
      }
      
      setSelectedFile(file)
      
      // Clean up previous URL to prevent memory leaks
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl)
      }
      
      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
      setResults(null)
      console.log('Preview URL created:', url)
    }
  }

  const analyzeImage = async () => {
    if (!selectedFile) return

    setLoading(true)
    setEmailSent(false)
    setSendingEmail(false)
    const formData = new FormData()
    formData.append('image', selectedFile)

    try {
      const response = await fetch('http://localhost:5000/analyze-id', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()
      setResults(data)
    } catch (error) {
      console.error('Error analyzing image:', error)
      setResults({
        success: false,
        error: 'Failed to connect to server',
        message: 'Please make sure the backend server is running'
      })
    } finally {
      setLoading(false)
    }
  }

  const startWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true })
      setWebcamStream(stream)
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }
    } catch (error) {
      console.error('Error accessing webcam:', error)
      alert('Error accessing webcam. Please check permissions.')
    }
  }

  const stopWebcam = () => {
    if (webcamStream) {
      webcamStream.getTracks().forEach(track => track.stop())
      setWebcamStream(null)
    }
  }

  const captureImage = async () => {
    if (!videoRef.current || !canvasRef.current) return

    const canvas = canvasRef.current
    const video = videoRef.current
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    
    const ctx = canvas.getContext('2d')
    ctx.drawImage(video, 0, 0)
    
    const imageDataUrl = canvas.toDataURL('image/jpeg')
    
    setLoading(true)
    setEmailSent(false)
    setSendingEmail(false)
    try {
      const response = await fetch('http://localhost:5000/analyze-webcam', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image: imageDataUrl }),
      })

      const data = await response.json()
      setResults(data)
    } catch (error) {
      console.error('Error analyzing webcam image:', error)
      setResults({
        success: false,
        error: 'Failed to connect to server',
        message: 'Please make sure the backend server is running'
      })
    } finally {
      setLoading(false)
    }
  }

  const clearResults = () => {
    setResults(null)
    setSelectedFile(null)
    setPreviewUrl(null)
    setEmailSent(false)
    setSendingEmail(false)
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      // You could add a toast notification here
      console.log('Copied to clipboard:', text)
    })
  }

  const copyAllText = () => {
    if (results?.all_text) {
      const allText = results.all_text.join('\n')
      copyToClipboard(allText)
    }
  }

  const sendNotificationEmail = async () => {
    if (!results.person_identified || !results.person_data || !results.cache_key) {
      alert('Cannot send email: Missing required data')
      return
    }

    setSendingEmail(true)
    setEmailSent(false)

    try {
      const response = await fetch('http://localhost:5000/send-notification-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          person_id: results.person_data.person_id,
          cache_key: results.cache_key,
          scan_results: results.data
        })
      })

      const data = await response.json()

      if (data.success) {
        setEmailSent(true)
        alert(`✅ Email sent successfully to ${results.person_data.name} (${results.person_data.email})`)
      } else {
        alert(`❌ Failed to send email: ${data.message || data.error}`)
      }
    } catch (error) {
      console.error('Error sending email:', error)
      alert('❌ Error sending email. Please check your connection and try again.')
    } finally {
      setSendingEmail(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Doc Scanner
          </h1>
          <p className="text-gray-600">
            Upload an image or use your webcam to extract information from Docs
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-lg p-1 shadow-md">
            <button
              onClick={() => {
                setActiveTab('upload')
                stopWebcam()
                clearResults()
              }}
              className={`px-6 py-2 rounded-md transition-all ${
                activeTab === 'upload'
                  ? 'bg-blue-500 text-white shadow-md'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Upload Image
            </button>
            <button
              onClick={() => {
                setActiveTab('webcam')
                clearResults()
              }}
              className={`px-6 py-2 rounded-md transition-all ${
                activeTab === 'webcam'
                  ? 'bg-blue-500 text-white shadow-md'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Use Webcam
            </button>
          </div>
        </div>

        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Input Section */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              {activeTab === 'upload' ? (
                <div>
                  <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                    Upload Doc
                  </h2>
                  
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleFileSelect}
                      className="hidden"
                      id="file-upload"
                    />
                    <label htmlFor="file-upload" className="cursor-pointer">
                      <div className="text-gray-500 mb-4">
                        <svg className="mx-auto h-12 w-12" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                          <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                      </div>
                      <p className="text-lg">Click to upload an image</p>
                      <p className="text-sm text-gray-400">PNG, JPG, JPEG up to 10MB</p>
                    </label>
                  </div>

                  {previewUrl && (
                    <div className="mt-6">
                      <div className="relative">
                        <img
                          src={previewUrl}
                          alt="Doc Preview"
                          className="w-full h-48 object-contain border rounded-lg bg-gray-50"
                          onLoad={() => console.log('Image loaded successfully')}
                          onError={(e) => {
                            console.error('Image load error:', e)
                            alert('Error loading image preview')
                          }}
                        />
                        {selectedFile && (
                          <div className="absolute top-2 right-2 bg-black bg-opacity-75 text-white text-xs px-2 py-1 rounded">
                            {selectedFile.name}
                          </div>
                        )}
                      </div>
                      <button
                        onClick={analyzeImage}
                        disabled={loading}
                        className="w-full mt-4 bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                      >
                        {loading ? (
                          <>
                            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Analyzing...
                          </>
                        ) : (
                          'Analyze Doc'
                        )}
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <div>
                  <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                    Webcam Scanner
                  </h2>
                  
                  <div className="space-y-4">
                    {!webcamStream ? (
                      <button
                        onClick={startWebcam}
                        className="w-full bg-green-500 hover:bg-green-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
                      >
                        Start Webcam
                      </button>
                    ) : (
                      <div>
                        <video
                          ref={videoRef}
                          autoPlay
                          playsInline
                          className="w-full rounded-lg border"
                        />
                        <canvas ref={canvasRef} className="hidden" />
                        <div className="flex gap-2 mt-4">
                          <button
                            onClick={captureImage}
                            disabled={loading}
                            className="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:opacity-50"
                          >
                            {loading ? 'Analyzing...' : 'Capture & Analyze'}
                          </button>
                          <button
                            onClick={stopWebcam}
                            className="bg-red-500 hover:bg-red-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
                          >
                            Stop
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Results Section */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                Extracted Information
              </h2>
              
              {!results && !loading ? (
                <div className="text-center py-12">
                  <div className="text-gray-400 mb-4">
                    <svg className="mx-auto h-16 w-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <p className="text-gray-500">No results yet. Upload an image or use webcam to start scanning.</p>
                </div>
              ) : loading ? (
                <div className="text-center py-12">
                  <div className="text-blue-500 mb-4">
                    <svg className="mx-auto h-16 w-16 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  </div>
                  <p className="text-blue-600 font-semibold">Processing with AWS Textract...</p>
                  <p className="text-gray-500 text-sm mt-2">Analyzing document structure and extracting text</p>
                </div>
              ) : results.success ? (
                <div className="space-y-6">
                  {/* Person Identification Section */}
                  {results.person_identified && results.person_data && (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <h3 className="text-lg font-semibold text-green-800 mb-2 flex items-center">
                        <svg className="w-5 h-5 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                        Person Identified ✅
                      </h3>
                      <div className="grid grid-cols-1 gap-2 text-sm mb-4">
                        <div><strong>Name:</strong> {results.person_data.name}</div>
                        <div><strong>Roll Number:</strong> {results.person_data.roll_number || 'Not available'}</div>
                        <div><strong>Branch:</strong> {results.person_data.branch || 'Not available'}</div>
                        <div><strong>Email:</strong> {results.person_data.email || 'Not available'}</div>
                      </div>
                      
                      {/* Email Notification Section */}
                      {results.person_data.email && results.smtp_enabled ? (
                        <div className="border-t border-green-200 pt-3">
                          <div className="flex items-center justify-between">
                            <div className="text-sm text-green-700">
                              <strong>📧 Email Notification:</strong> Would you like to send the scanned document to this person?
                            </div>
                          </div>
                          <div className="mt-2 flex gap-2">
                            {!emailSent ? (
                              <button
                                onClick={sendNotificationEmail}
                                disabled={sendingEmail}
                                className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                                  sendingEmail
                                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                    : 'bg-blue-600 text-white hover:bg-blue-700'
                                }`}
                              >
                                {sendingEmail ? (
                                  <span className="flex items-center">
                                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Sending Email...
                                  </span>
                                ) : (
                                  '📧 Send Email with Scan'
                                )}
                              </button>
                            ) : (
                              <div className="flex items-center text-green-700 font-medium text-sm">
                                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                                </svg>
                                Email sent successfully!
                              </div>
                            )}
                          </div>
                        </div>
                      ) : results.person_data.email && !results.smtp_enabled ? (
                        <div className="border-t border-green-200 pt-3">
                          <div className="text-sm text-yellow-600">
                            ⚠️ Email sending is not configured. Please contact administrator.
                          </div>
                        </div>
                      ) : (
                        <div className="border-t border-green-200 pt-3">
                          <div className="text-sm text-gray-600">
                            ❌ No email address available for this person.
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {!results.person_identified && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <h3 className="text-lg font-semibold text-yellow-800 mb-2 flex items-center">
                        <svg className="w-5 h-5 mr-2 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                        </svg>
                        Person Not Found in Database
                      </h3>
                      <p className="text-yellow-700 text-sm">
                        The scanned person is not registered in our database. Please contact administration to register this person.
                      </p>
                    </div>
                  )}

                  {/* Extracted Data Section */}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-700 mb-3 flex items-center">
                      <svg className="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                      Extracted Information
                    </h3>
                    <div className="space-y-3">
                      {Object.entries(results.data).map(([key, value]) => (
                        <div key={key} className="border-l-4 border-blue-500 pl-4 py-2 bg-blue-50 rounded-r-lg">
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <h4 className="font-semibold text-gray-800">
                                {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                              </h4>
                              <p className="text-gray-700 mt-1">{value.value}</p>
                            </div>
                            <span className={`text-sm px-2 py-1 rounded-full ${
                              value.confidence >= 80 ? 'bg-green-100 text-green-800' :
                              value.confidence >= 60 ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {value.confidence}%
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* All Text Section */}
                  {results.all_text && results.all_text.length > 0 && (
                    <div>
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="text-lg font-semibold text-gray-700 flex items-center">
                          <svg className="w-5 h-5 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                          </svg>
                          All Detected Text ({results.total_lines} lines)
                        </h3>
                        <button
                          onClick={copyAllText}
                          className="text-sm bg-green-100 hover:bg-green-200 text-green-700 px-3 py-1 rounded-lg transition-colors flex items-center"
                        >
                          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                          Copy All
                        </button>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-4 max-h-60 overflow-y-auto">
                        <div className="space-y-2">
                          {results.all_text.map((text, index) => (
                            <div key={index} className="flex items-start hover:bg-gray-100 rounded px-2 py-1 transition-colors group">
                              <span className="text-xs text-gray-400 mr-3 mt-1 min-w-[2rem]">
                                {index + 1}
                              </span>
                              <span className="text-gray-700 flex-1 font-mono text-sm">
                                {text || '<empty line>'}
                              </span>
                              <button
                                onClick={() => copyToClipboard(text)}
                                className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-gray-600 transition-all ml-2"
                                title="Copy this line"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                </svg>
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Summary Stats */}
                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">Analysis Summary</h3>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Structured Fields Found:</span>
                        <span className="font-semibold text-blue-600 ml-2">
                          {Object.keys(results.data).length}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">Total Text Lines:</span>
                        <span className="font-semibold text-green-600 ml-2">
                          {results.total_lines || 0}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">Avg Confidence:</span>
                        <span className="font-semibold text-yellow-600 ml-2">
                          {Object.values(results.data).length > 0 
                            ? Math.round(Object.values(results.data).reduce((sum, item) => sum + item.confidence, 0) / Object.values(results.data).length)
                            : 0}%
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">Processing Status:</span>
                        <span className="font-semibold text-green-600 ml-2">Complete</span>
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-3">
                    <button
                      onClick={clearResults}
                      className="flex-1 bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                    >
                      Clear Results
                    </button>
                    <button
                      onClick={() => {
                        const dataStr = JSON.stringify(results, null, 2);
                        const dataBlob = new Blob([dataStr], {type: 'application/json'});
                        const url = URL.createObjectURL(dataBlob);
                        const link = document.createElement('a');
                        link.href = url;
                        link.download = 'textract-results.json';
                        link.click();
                      }}
                      className="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                    >
                      Download JSON
                    </button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="text-red-500 mb-4">
                    <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold text-red-600 mb-2">Error</h3>
                  <p className="text-red-500 mb-4">{results.message}</p>
                  {results.error && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                      <p className="text-sm text-red-600 font-mono">{results.error}</p>
                    </div>
                  )}
                  <button
                    onClick={clearResults}
                    className="bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                  >
                    Try Again
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App