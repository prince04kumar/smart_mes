import { useState, useRef, useEffect } from 'react'
import { Camera, Upload, RotateCcw, Scan } from 'lucide-react'

function ScannerPage() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('upload')
  const [webcamStream, setWebcamStream] = useState(null)
  const [sendingEmail, setSendingEmail] = useState(false)
  const [emailSent, setEmailSent] = useState(false)
  const videoRef = useRef(null)
  const canvasRef = useRef(null)

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
        body: formData
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log('Analysis result:', data)
      setResults(data)
    } catch (error) {
      console.error('Error analyzing image:', error)
      alert('Error analyzing image. Please check your connection and try again.')
    } finally {
      setLoading(false)
    }
  }

  const startWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          facingMode: 'environment',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        } 
      })
      setWebcamStream(stream)
      
      // Wait for video element to be ready
      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream
          videoRef.current.play()
        }
      }, 100)
    } catch (error) {
      console.error('Error accessing webcam:', error)
      alert('Unable to access webcam. Please ensure you have granted camera permissions.')
    }
  }

  const stopWebcam = () => {
    if (webcamStream) {
      webcamStream.getTracks().forEach(track => track.stop())
      setWebcamStream(null)
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null
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
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: imageDataUrl })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log('Webcam analysis result:', data)
      setResults(data)
    } catch (error) {
      console.error('Error analyzing webcam image:', error)
      alert('Error analyzing webcam image. Please try again.')
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
          <h1 className="text-4xl font-bold text-gray-800 mb-2 flex items-center justify-center">
            <Scan className="w-10 h-10 mr-3 text-blue-600" />
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
              className={`px-6 py-3 rounded-md font-medium transition-all duration-200 flex items-center ${
                activeTab === 'upload'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Upload className="w-5 h-5 mr-2" />
              Upload Image
            </button>
            <button
              onClick={() => {
                setActiveTab('webcam')
                clearResults()
                startWebcam()
              }}
              className={`px-6 py-3 rounded-md font-medium transition-all duration-200 flex items-center ${
                activeTab === 'webcam'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Camera className="w-5 h-5 mr-2" />
              Use Webcam
            </button>
          </div>
        </div>

        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Input Section */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              {activeTab === 'upload' ? (
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold text-gray-800 mb-4">Upload Doc Image</h2>
                  
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleFileSelect}
                      className="hidden"
                      id="file-upload"
                    />
                    <label htmlFor="file-upload" className="cursor-pointer">
                      <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                      <p className="text-gray-600 mb-2">Click to select an image or drag and drop</p>
                      <p className="text-sm text-gray-500">Supports: PNG, JPG, JPEG (Max 10MB)</p>
                    </label>
                  </div>

                  {previewUrl && (
                    <div className="space-y-4">
                      <img
                        src={previewUrl}
                        alt="Preview"
                        className="w-full max-h-64 object-contain rounded-lg border"
                      />
                      <div className="flex gap-3">
                        <button
                          onClick={analyzeImage}
                          disabled={loading}
                          className={`flex-1 py-3 px-4 rounded-lg font-medium transition-colors ${
                            loading
                              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                              : 'bg-blue-600 text-white hover:bg-blue-700'
                          }`}
                        >
                          {loading ? (
                            <span className="flex items-center justify-center">
                              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                              Analyzing...
                            </span>
                          ) : (
                            'Analyze Image'
                          )}
                        </button>
                        <button
                          onClick={clearResults}
                          className="px-4 py-3 text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                        >
                          <RotateCcw className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold text-gray-800 mb-4">Webcam Scanner</h2>
                  
                  <div className="relative bg-gray-900 rounded-lg overflow-hidden">
                    <video
                      ref={videoRef}
                      autoPlay
                      playsInline
                      className="w-full h-64 object-cover"
                    />
                    {!webcamStream && (
                      <div className="absolute inset-0 flex items-center justify-center bg-gray-800">
                        <div className="text-center text-white">
                          <Camera className="w-12 h-12 mx-auto mb-4 opacity-50" />
                          <p>Camera not started</p>
                        </div>
                      </div>
                    )}
                  </div>

                  <canvas ref={canvasRef} className="hidden" />

                  <div className="flex gap-3">
                    {webcamStream ? (
                      <>
                        <button
                          onClick={captureImage}
                          disabled={loading}
                          className={`flex-1 py-3 px-4 rounded-lg font-medium transition-colors ${
                            loading
                              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                              : 'bg-green-600 text-white hover:bg-green-700'
                          }`}
                        >
                          {loading ? 'Processing...' : 'Capture & Analyze'}
                        </button>
                        <button
                          onClick={stopWebcam}
                          className="px-4 py-3 text-red-600 bg-red-100 rounded-lg hover:bg-red-200 transition-colors"
                        >
                          Stop Camera
                        </button>
                      </>
                    ) : (
                      <button
                        onClick={startWebcam}
                        className="flex-1 py-3 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        Start Camera
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Results Section */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Analysis Results</h2>
              
              {loading ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
                  <p className="text-gray-500 text-sm mt-2">Analyzing document structure and extracting text</p>
                </div>
              ) : results?.success ? (
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
                  {results.data && Object.keys(results.data).length > 0 && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <h3 className="text-lg font-semibold text-blue-800 mb-3">Extracted Information</h3>
                      <div className="grid grid-cols-1 gap-2 text-sm">
                        {Object.entries(results.data).map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span className="font-medium text-blue-700">{key}:</span>
                            <span className="text-blue-600">
                              {value.value || 'Not detected'} 
                              {value.confidence && (
                                <span className="text-xs ml-1">({value.confidence}%)</span>
                              )}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : results && !results.success ? (
                <div className="text-center py-8">
                  <div className="text-red-600 mb-2">❌ Analysis Failed</div>
                  <p className="text-gray-600 text-sm">{results.message || 'Unknown error occurred'}</p>
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <Scan className="w-16 h-16 mx-auto mb-4 opacity-30" />
                  <p>Upload an image or use webcam to start scanning</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ScannerPage