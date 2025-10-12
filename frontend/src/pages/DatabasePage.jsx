import { useState, useEffect } from 'react'
import { 
  Users, Plus, Search, Edit, Trash2, Mail, Phone, 
  BookOpen, Hash, Calendar, Eye, Download, Filter 
} from 'lucide-react'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { useAuth } from '../context/AuthContext'
import API_BASE_URL from '../config/api'
import useDocumentTitle from '../hooks/useDocumentTitle'

function DatabasePage() {
  useDocumentTitle('Database');
  const { getAuthHeader } = useAuth()
  const [persons, setPersons] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)
  const [selectedPerson, setSelectedPerson] = useState(null)
  const [showDetailsModal, setShowDetailsModal] = useState(false)
  const [filterBranch, setFilterBranch] = useState('')
  
  // Form state for adding/editing persons
  const [formData, setFormData] = useState({
    name: '',
    roll_number: '',
    branch: '',
    email: '',
    phone: ''
  })

  // Fetch all persons from database
  const fetchPersons = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/persons`, {
        headers: getAuthHeader()
      })
      if (response.ok) {
        const data = await response.json()
        setPersons(data.data || [])
      } else {
        console.error('Failed to fetch persons')
      }
    } catch (error) {
      console.error('Error fetching persons:', error)
    } finally {
      setLoading(false)
    }
  }

  // Add new person
  const addPerson = async (personData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/create-person`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeader()
        },
        body: JSON.stringify(personData)
      })
      
      if (response.ok) {
        const data = await response.json()
        alert(`✅ ${personData.name} added successfully!`)
        fetchPersons() // Refresh the list
        setShowAddModal(false)
        resetForm()
      } else {
        const error = await response.json()
        alert(`❌ Failed to add person: ${error.message || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Error adding person:', error)
      alert('❌ Error adding person. Please try again.')
    }
  }

  const resetForm = () => {
    setFormData({
      name: '',
      roll_number: '',
      branch: '',
      email: '',
      phone: ''
    })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    // Basic validation
    if (!formData.name.trim()) {
      alert('Name is required')
      return
    }
    
    addPerson(formData)
  }

  // Filter and search functionality
  const filteredPersons = persons.filter(person => {
    const matchesSearch = person.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         person.roll_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         person.email?.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesBranch = !filterBranch || person.branch === filterBranch
    
    return matchesSearch && matchesBranch
  })

  // Get unique branches for filter
  const branches = [...new Set(persons.map(p => p.branch).filter(Boolean))]

  // View person details
  const viewPersonDetails = (person) => {
    setSelectedPerson(person)
    setShowDetailsModal(true)
  }

  // Export data as JSON
  const exportData = () => {
    const dataStr = JSON.stringify(filteredPersons, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
    
    const exportFileDefaultName = `students_${new Date().toISOString().split('T')[0]}.json`
    
    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
  }

  useEffect(() => {
    fetchPersons()
  }, [])

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <Card className="mb-8">
          <CardHeader>
            <div className="flex flex-col md:flex-row md:items-center md:justify-between">
              <div className="mb-4 md:mb-0">
                <CardTitle className="text-3xl flex items-center">
                  <Users className="w-8 h-8 mr-3 text-primary" />
                  Database Management
                </CardTitle>
                <CardDescription className="mt-1">
                  Manage student and staff records in the Doc system
                </CardDescription>
              </div>
              
              <div className="flex gap-3">
                <Button
                  onClick={exportData}
                  variant="outline"
                  className="text-emerald-600 hover:text-emerald-700"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Export Data
                </Button>
                <Button
                  onClick={() => setShowAddModal(true)}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Person
                </Button>
              </div>
            </div>
          </CardHeader>

          {/* Stats */}
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-primary/10 p-4 rounded-lg">
                <div className="text-2xl font-bold text-primary">{persons.length}</div>
                <div className="text-muted-foreground text-sm">Total Records</div>
              </div>
              <div className="bg-emerald-500/10 p-4 rounded-lg">
                <div className="text-2xl font-bold text-emerald-600">{branches.length}</div>
                <div className="text-muted-foreground text-sm">Departments</div>
              </div>
              <div className="bg-purple-500/10 p-4 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {persons.filter(p => p.email).length}
                </div>
                <div className="text-muted-foreground text-sm">With Email</div>
              </div>
              <div className="bg-yellow-500/10 p-4 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">
                  {filteredPersons.length}
                </div>
                <div className="text-muted-foreground text-sm">Filtered Results</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Search and Filter */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground" />
                  <Input
                    type="text"
                  placeholder="Search by name, roll number, or email..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            <div className="md:w-48">
              <div className="relative">
                <Filter className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <select
                  value={filterBranch}
                  onChange={(e) => setFilterBranch(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
                >
                  <option value="">All Branches</option>
                  {branches.map(branch => (
                    <option key={branch} value={branch}>{branch}</option>
                  ))}
                </select>
              </div>
            </div>
            </div>
          </CardContent>
        </Card>

        {/* Persons Table */}
        <Card className="overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              <span className="ml-2 text-muted-foreground">Loading...</span>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Student
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Roll Number
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Branch
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Contact
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredPersons.map((person) => (
                      <tr key={person._id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
                              {person.name.charAt(0).toUpperCase()}
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900">
                                {person.name}
                              </div>
                              <div className="text-sm text-gray-500">
                                Added {new Date(person.created_at).toLocaleDateString()}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center text-sm text-gray-900">
                            <Hash className="w-4 h-4 mr-1 text-gray-400" />
                            {person.roll_number || 'N/A'}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center text-sm text-gray-900">
                            <BookOpen className="w-4 h-4 mr-1 text-gray-400" />
                            {person.branch || 'N/A'}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <div className="space-y-1">
                            {person.email && (
                              <div className="flex items-center">
                                <Mail className="w-4 h-4 mr-1 text-gray-400" />
                                {person.email}
                              </div>
                            )}
                            {person.phone && (
                              <div className="flex items-center">
                                <Phone className="w-4 h-4 mr-1 text-gray-400" />
                                {person.phone}
                              </div>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex space-x-2">
                            <button
                              onClick={() => viewPersonDetails(person)}
                              className="text-blue-600 hover:text-blue-900 p-1 rounded"
                              title="View Details"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                            <button
                              className="text-green-600 hover:text-green-900 p-1 rounded"
                              title="Edit"
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                            <button
                              className="text-red-600 hover:text-red-900 p-1 rounded"
                              title="Delete"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {filteredPersons.length === 0 && !loading && (
                <div className="text-center py-12">
                  <Users className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No persons found</h3>
                  <p className="text-gray-500">
                    {searchTerm || filterBranch 
                      ? 'Try adjusting your search or filter criteria'
                      : 'Get started by adding your first person to the database'
                    }
                  </p>
                </div>
              )}
            </>
          )}
        </Card>
      </div>

      {/* Add Person Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full mx-4">
            <div className="p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
                <Plus className="w-6 h-6 mr-2 text-blue-600" />
                Add New Person
              </h2>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Full Name *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter full name"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Roll Number
                  </label>
                  <input
                    type="text"
                    value={formData.roll_number}
                    onChange={(e) => setFormData({...formData, roll_number: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter roll number"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Branch/Department
                  </label>
                  <input
                    type="text"
                    value={formData.branch}
                    onChange={(e) => setFormData({...formData, branch: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., Computer Science, ECE"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter email address"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({...formData, phone: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter phone number"
                  />
                </div>
                
                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowAddModal(false)
                      resetForm()
                    }}
                    className="flex-1 px-4 py-2 text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Add Person
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Person Details Modal */}
      {showDetailsModal && selectedPerson && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full mx-4 max-h-90vh overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-800 flex items-center">
                  <Eye className="w-6 h-6 mr-2 text-blue-600" />
                  Person Details
                </h2>
                <button
                  onClick={() => setShowDetailsModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="space-y-6">
                {/* Basic Info */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">Basic Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-600">Full Name</label>
                      <div className="text-gray-800">{selectedPerson.name}</div>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-600">Roll Number</label>
                      <div className="text-gray-800">{selectedPerson.roll_number || 'N/A'}</div>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-600">Branch/Department</label>
                      <div className="text-gray-800">{selectedPerson.branch || 'N/A'}</div>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-600">Database ID</label>
                      <div className="text-gray-800 font-mono text-sm">{selectedPerson._id}</div>
                    </div>
                  </div>
                </div>

                {/* Contact Info */}
                <div className="bg-blue-50 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">Contact Information</h3>
                  <div className="space-y-2">
                    <div className="flex items-center">
                      <Mail className="w-4 h-4 mr-2 text-gray-600" />
                      <span className="text-gray-800">{selectedPerson.email || 'No email provided'}</span>
                    </div>
                    <div className="flex items-center">
                      <Phone className="w-4 h-4 mr-2 text-gray-600" />
                      <span className="text-gray-800">{selectedPerson.phone || 'No phone provided'}</span>
                    </div>
                  </div>
                </div>

                {/* Timestamps */}
                <div className="bg-green-50 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">Record Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex items-center">
                      <Calendar className="w-4 h-4 mr-2 text-gray-600" />
                      <div>
                        <div className="text-sm font-medium text-gray-600">Created</div>
                        <div className="text-gray-800">{new Date(selectedPerson.created_at).toLocaleString()}</div>
                      </div>
                    </div>
                    <div className="flex items-center">
                      <Calendar className="w-4 h-4 mr-2 text-gray-600" />
                      <div>
                        <div className="text-sm font-medium text-gray-600">Updated</div>
                        <div className="text-gray-800">{new Date(selectedPerson.updated_at).toLocaleString()}</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Scan History */}
                {selectedPerson.scan_history && selectedPerson.scan_history.length > 0 && (
                  <div className="bg-purple-50 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-gray-800 mb-3">
                      Scan History ({selectedPerson.scan_history.length} scans)
                    </h3>
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {selectedPerson.scan_history.slice(-5).map((scan, index) => (
                        <div key={index} className="bg-white p-2 rounded border">
                          <div className="flex justify-between items-center">
                            <span className="text-sm font-medium">
                              {scan.source === 'webcam' ? '📷 Webcam' : '📁 Upload'} Scan
                            </span>
                            <span className="text-xs text-gray-500">
                              {new Date(scan.timestamp).toLocaleString()}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="flex justify-end pt-6">
                <button
                  onClick={() => setShowDetailsModal(false)}
                  className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default DatabasePage