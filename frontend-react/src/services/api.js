// API Configuration
const API_BASE_URL = 'http://localhost:8000';
const API_KEY = 'edu-api-key-1234';

// API Helper Functions
export const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
    ...options.headers
  };

  const config = {
    headers,
    ...options
  };

  // Handle file uploads
  if (options.body instanceof FormData) {
    delete headers['Content-Type']; // Let browser set it for FormData
  }

  try {
    const response = await fetch(url, config);
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('API Request failed:', error);
    throw error;
  }
};

// Document API calls
export const getDocuments = () => apiRequest('/documents');
export const uploadDocument = (formData) => {
  return fetch(`${API_BASE_URL}/documents/upload`, {
    method: 'POST',
    headers: {
      'X-API-Key': API_KEY
    },
    body: formData
  }).then(response => {
    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
    }
    return response.json();
  });
};
export const deleteDocument = (documentId) => apiRequest(`/documents/${documentId}`, { method: 'DELETE' });

// Content API calls
export const getContent = () => apiRequest('/content');
export const generateContent = (documentId, includeLessonPlan) => 
  apiRequest('/content/generate', {
    method: 'POST',
    body: JSON.stringify({
      document_id: documentId,
      include_lesson_plan: includeLessonPlan
    })
  });
export const deleteContent = (contentId) => apiRequest(`/content/${contentId}`, { method: 'DELETE' });

// Test API calls
export const getTests = () => apiRequest('/tests');
export const generateTest = (contentId, testTitle, questionCount, difficulty) => 
  apiRequest('/tests/generate', {
    method: 'POST',
    body: JSON.stringify({
      content_id: contentId,
      test_title: testTitle || undefined,
      num_questions: questionCount,
      difficulty: difficulty
    })
  });
export const deleteTest = (testId) => apiRequest(`/tests/${testId}`, { method: 'DELETE' });

// Student API calls
export const getStudents = () => apiRequest('/students');
export const registerStudent = (name, email) => 
  apiRequest('/students/register', {
    method: 'POST',
    body: JSON.stringify({
      name: name,
      email: email
    })
  });
export const getStudentProgress = (studentId) => apiRequest(`/students/${studentId}/progress`);
export const getStudentLearningPath = (studentId) => apiRequest(`/students/${studentId}/learning-path`);
export const getStudentRecommendations = (studentId) => apiRequest(`/students/${studentId}/recommendations`);
export const generateLearningPath = (studentId) => 
  apiRequest('/learning-paths/generate', {
    method: 'POST',
    body: JSON.stringify({
      student_id: studentId
    })
  });