// API Configuration
const API_BASE_URL = 'http://localhost:8000';
const API_KEY = 'edu-api-key-1234';

// Global state
let currentPage = 'dashboard';
let documents = [];
let content = [];
let tests = [];
let students = [];
let selectedStudent = null;

// DOM Elements
const pages = document.querySelectorAll('.page');
const navLinks = document.querySelectorAll('.nav-link');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Set up navigation
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const pageName = this.getAttribute('data-page');
            showPage(pageName);
        });
    });

    // Set up form submissions
    document.getElementById('upload-form').addEventListener('submit', handleDocumentUpload);
    document.getElementById('content-form').addEventListener('submit', handleContentGeneration);
    document.getElementById('test-form').addEventListener('submit', handleTestCreation);
    document.getElementById('student-form').addEventListener('submit', handleStudentRegistration);

    // Set up student selection for progress tracking
    document.getElementById('student-select').addEventListener('change', handleStudentSelection);

    // Load initial data
    loadDashboardData();
});

// Page navigation
function showPage(pageName) {
    // Hide all pages
    pages.forEach(page => {
        page.style.display = 'none';
    });

    // Show selected page
    document.getElementById(`${pageName}-page`).style.display = 'block';

    // Update active nav link
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-page') === pageName) {
            link.classList.add('active');
        }
    });

    currentPage = pageName;

    // Load page-specific data
    switch (pageName) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'documents':
            loadDocuments();
            break;
        case 'content':
            loadContent();
            break;
        case 'tests':
            loadTests();
            break;
        case 'progress':
            loadProgressData();
            break;
    }
}

// API Helper Functions
async function apiRequest(endpoint, options = {}) {
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
        showToast('Error', error.message, 'danger');
        throw error;
    }
}

// Toast notification
function showToast(title, message, type = 'info') {
    const toastElement = document.getElementById('toast');
    const toastTitle = document.getElementById('toast-title');
    const toastMessage = document.getElementById('toast-message');

    toastTitle.textContent = title;
    toastMessage.textContent = message;

    // Set toast color based on type
    toastElement.className = `toast bg-${type === 'danger' ? 'danger' : type === 'success' ? 'success' : 'primary'} text-white`;

    const toast = new bootstrap.Toast(toastElement);
    toast.show();
}

// Dashboard Functions
async function loadDashboardData() {
    try {
        // Load documents
        const documentsResponse = await apiRequest('/documents');
        documents = documentsResponse.documents || [];
        document.getElementById('document-count').textContent = documents.length;

        // Load content
        const contentResponse = await apiRequest('/content');
        content = contentResponse.content || [];
        document.getElementById('content-count').textContent = content.length;

        // Load tests
        const testsResponse = await apiRequest('/tests');
        tests = testsResponse.tests || [];
        document.getElementById('test-count').textContent = tests.length;

        // Load students
        const studentsResponse = await apiRequest('/students');
        students = studentsResponse.students || [];
        document.getElementById('student-count').textContent = students.length;

        // Load recent activity (simplified for POC)
        updateRecentActivity();
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
    }
}

function updateRecentActivity() {
    const activityList = document.getElementById('recent-activity');
    activityList.innerHTML = '';

    if (documents.length === 0 && content.length === 0 && tests.length === 0 && students.length === 0) {
        activityList.innerHTML = '<li class="list-group-item">No recent activity</li>';
        return;
    }

    // Combine and sort recent activities (simplified for POC)
    const activities = [];

    // Add document uploads
    documents.forEach(doc => {
        activities.push({
            type: 'document',
            text: `Document uploaded: ${doc.filename}`,
            date: doc.upload_date
        });
    });

    // Add content generation
    content.forEach(item => {
        activities.push({
            type: 'content',
            text: `Content generated: ${item.title}`,
            date: item.created_date
        });
    });

    // Add test creation
    tests.forEach(test => {
        activities.push({
            type: 'test',
            text: `Test created: ${test.title}`,
            date: test.created_date
        });
    });

    // Add student registration
    students.forEach(student => {
        activities.push({
            type: 'student',
            text: `Student registered: ${student.name}`,
            date: student.registered_date
        });
    });

    // Sort by date (newest first) and take the first 5
    activities.sort((a, b) => new Date(b.date) - new Date(a.date));
    const recentActivities = activities.slice(0, 5);

    // Display activities
    recentActivities.forEach(activity => {
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item';
        listItem.textContent = activity.text;
        activityList.appendChild(listItem);
    });
}

// Document Functions
async function loadDocuments() {
    try {
        const response = await apiRequest('/documents');
        documents = response.documents || [];
        updateDocumentsTable();
    } catch (error) {
        console.error('Failed to load documents:', error);
    }
}

function updateDocumentsTable() {
    const tableBody = document.getElementById('documents-table');
    tableBody.innerHTML = '';

    if (documents.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="5" class="text-center">No documents uploaded yet</td></tr>';
        return;
    }

    documents.forEach(doc => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${doc.filename}</td>
            <td>${new Date(doc.upload_date).toLocaleDateString()}</td>
            <td>${doc.chunk_count}</td>
            <td>${doc.total_characters}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-danger" onclick="deleteDocument('${doc.document_id}')">Delete</button>
                </div>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

async function handleDocumentUpload(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('document-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showToast('Error', 'Please select a file', 'danger');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showToast('Uploading', 'Uploading document...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/documents/upload`, {
            method: 'POST',
            headers: {
                'X-API-Key': API_KEY
            },
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
        }
        
        const result = await response.json();
        showToast('Success', 'Document uploaded successfully', 'success');
        
        // Reset form
        fileInput.value = '';
        
        // Reload documents
        loadDocuments();
        
        // Update dashboard counts
        document.getElementById('document-count').textContent = documents.length + 1;
    } catch (error) {
        console.error('Document upload failed:', error);
        showToast('Error', error.message, 'danger');
    }
}

async function deleteDocument(documentId) {
    if (!confirm('Are you sure you want to delete this document?')) {
        return;
    }
    
    try {
        await apiRequest(`/documents/${documentId}`, { method: 'DELETE' });
        showToast('Success', 'Document deleted successfully', 'success');
        
        // Reload documents
        loadDocuments();
        
        // Update dashboard counts
        document.getElementById('document-count').textContent = documents.length - 1;
    } catch (error) {
        console.error('Failed to delete document:', error);
        showToast('Error', error.message, 'danger');
    }
}

// Content Functions
async function loadContent() {
    try {
        // Load documents for dropdown
        const documentsResponse = await apiRequest('/documents');
        documents = documentsResponse.documents || [];
        updateDocumentSelect();
        
        // Load content
        const contentResponse = await apiRequest('/content');
        content = contentResponse.content || [];
        updateContentTable();
    } catch (error) {
        console.error('Failed to load content:', error);
    }
}

function updateDocumentSelect() {
    const select = document.getElementById('document-select');
    select.innerHTML = '<option value="">Choose a document...</option>';
    
    documents.forEach(doc => {
        const option = document.createElement('option');
        option.value = doc.document_id;
        option.textContent = doc.filename;
        select.appendChild(option);
    });
}

function updateContentTable() {
    const tableBody = document.getElementById('content-table');
    tableBody.innerHTML = '';
    
    if (content.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="5" class="text-center">No content generated yet</td></tr>';
        return;
    }
    
    content.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.title}</td>
            <td>${getDocumentName(item.document_id)}</td>
            <td>${new Date(item.created_date).toLocaleDateString()}</td>
            <td>${item.topics ? item.topics.join(', ') : 'N/A'}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-primary" onclick="viewContent('${item.id}')">View</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteContent('${item.id}')">Delete</button>
                </div>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

function getDocumentName(documentId) {
    const doc = documents.find(d => d.document_id === documentId);
    return doc ? doc.filename : 'Unknown';
}

async function handleContentGeneration(event) {
    event.preventDefault();
    
    const documentId = document.getElementById('document-select').value;
    const includeLessonPlan = document.getElementById('include-lesson-plan').checked;
    
    if (!documentId) {
        showToast('Error', 'Please select a document', 'danger');
        return;
    }
    
    try {
        showToast('Generating', 'Generating content...', 'info');
        
        const response = await apiRequest('/content/generate', {
            method: 'POST',
            body: JSON.stringify({
                document_id: documentId,
                include_lesson_plan: includeLessonPlan
            })
        });
        
        showToast('Success', 'Content generated successfully', 'success');
        
        // Reset form
        document.getElementById('content-form').reset();
        
        // Reload content
        loadContent();
        
        // Update dashboard counts
        document.getElementById('content-count').textContent = content.length + 1;
    } catch (error) {
        console.error('Content generation failed:', error);
        showToast('Error', error.message, 'danger');
    }
}

function viewContent(contentId) {
    const item = content.find(c => c.id === contentId);
    if (!item) return;
    
    const modal = new bootstrap.Modal(document.getElementById('contentModal'));
    const modalTitle = document.getElementById('contentModalTitle');
    const modalBody = document.getElementById('contentModalBody');
    
    modalTitle.textContent = item.title;
    
    // Build content HTML
    let html = `
        <div class="mb-3">
            <p><strong>Document:</strong> ${getDocumentName(item.document_id)}</p>
            <p><strong>Created:</strong> ${new Date(item.created_date).toLocaleDateString()}</p>
            <p><strong>Topics:</strong> ${item.topics ? item.topics.join(', ') : 'N/A'}</p>
        </div>
    `;
    
    // Add content outline
    if (item.content_outline) {
        html += '<h5>Content Outline</h5>';
        
        // Add introduction
        if (item.content_outline.introduction) {
            html += `
                <div class="content-section">
                    <h6>Introduction</h6>
                    <p>${item.content_outline.introduction.overview}</p>
                    <p><strong>Objectives:</strong></p>
                    <ul>
                        ${item.content_outline.introduction.objectives.map(obj => `<li>${obj}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        // Add sections
        if (item.content_outline.sections) {
            item.content_outline.sections.forEach(section => {
                html += `
                    <div class="content-section">
                        <h6>${section.title}</h6>
                        <div class="section-content">
                            <p><strong>Summary:</strong> ${section.content_summary}</p>
                            <p><strong>Key Points:</strong></p>
                            <ul>
                                ${section.key_points.map(point => `<li>${point}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="section-questions">
                            <p><strong>Study Questions:</strong></p>
                            <ul>
                                ${section.study_questions.map(q => `<li class="study-question">${q.question}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                `;
            });
        }
        
        // Add conclusion
        if (item.content_outline.conclusion) {
            html += `
                <div class="content-section">
                    <h6>Conclusion</h6>
                    <p>${item.content_outline.conclusion.summary}</p>
                    <p><strong>Next Steps:</strong></p>
                    <ul>
                        ${item.content_outline.conclusion.next_steps.map(step => `<li>${step}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
    }
    
    // Add lesson plan if available
    if (item.lesson_plan) {
        html += '<h5>Lesson Plan</h5>';
        html += `<p><strong>Duration:</strong> ${item.lesson_plan.duration_days} days</p>`;
        
        if (item.lesson_plan.daily_schedule) {
            html += '<div class="accordion" id="lessonPlanAccordion">';
            
            item.lesson_plan.daily_schedule.forEach((day, index) => {
                html += `
                    <div class="accordion-item">
                        <h2 class="accordion-header" id="heading${index}">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse${index}">
                                Day ${day.day}: ${day.topics.join(', ')}
                            </button>
                        </h2>
                        <div id="collapse${index}" class="accordion-collapse collapse" data-bs-parent="#lessonPlanAccordion">
                            <div class="accordion-body">
                                <p><strong>Topics:</strong> ${day.topics.join(', ')}</p>
                                <p><strong>Activities:</strong></p>
                                <ul>
                                    ${day.activities.map(activity => `<li>${activity}</li>`).join('')}
                                </ul>
                                <p><strong>Estimated Time:</strong> ${day.estimated_time}</p>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
        }
    }
    
    modalBody.innerHTML = html;
    modal.show();
}

async function deleteContent(contentId) {
    if (!confirm('Are you sure you want to delete this content?')) {
        return;
    }
    
    try {
        await apiRequest(`/content/${contentId}`, { method: 'DELETE' });
        showToast('Success', 'Content deleted successfully', 'success');
        
        // Reload content
        loadContent();
        
        // Update dashboard counts
        document.getElementById('content-count').textContent = content.length - 1;
    } catch (error) {
        console.error('Failed to delete content:', error);
        showToast('Error', error.message, 'danger');
    }
}

// Test Functions
async function loadTests() {
    try {
        // Load content for dropdown
        const contentResponse = await apiRequest('/content');
        content = contentResponse.content || [];
        updateContentSelect();
        
        // Load tests
        const testsResponse = await apiRequest('/tests');
        tests = testsResponse.tests || [];
        updateTestsTable();
    } catch (error) {
        console.error('Failed to load tests:', error);
    }
}

function updateContentSelect() {
    const select = document.getElementById('content-select');
    select.innerHTML = '<option value="">Choose content...</option>';
    
    content.forEach(item => {
        const option = document.createElement('option');
        option.value = item.id;
        option.textContent = item.title;
        select.appendChild(option);
    });
}

function updateTestsTable() {
    const tableBody = document.getElementById('tests-table');
    tableBody.innerHTML = '';
    
    if (tests.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="5" class="text-center">No tests created yet</td></tr>';
        return;
    }
    
    tests.forEach(test => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${test.title}</td>
            <td>${getContentName(test.content_id)}</td>
            <td>${test.questions ? test.questions.length : 0}</td>
            <td><span class="badge bg-${getDifficultyColor(test.difficulty)}">${test.difficulty}</span></td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-primary" onclick="viewTest('${test.id}')">View</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteTest('${test.id}')">Delete</button>
                </div>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

function getContentName(contentId) {
    const item = content.find(c => c.id === contentId);
    return item ? item.title : 'Unknown';
}

function getDifficultyColor(difficulty) {
    switch (difficulty) {
        case 'easy': return 'success';
        case 'medium': return 'warning';
        case 'hard': return 'danger';
        default: return 'secondary';
    }
}

async function handleTestCreation(event) {
    event.preventDefault();
    
    const contentId = document.getElementById('content-select').value;
    const testTitle = document.getElementById('test-title').value;
    const questionCount = parseInt(document.getElementById('question-count').value);
    const difficulty = document.getElementById('difficulty').value;
    
    if (!contentId) {
        showToast('Error', 'Please select content', 'danger');
        return;
    }
    
    try {
        showToast('Creating', 'Creating test...', 'info');
        
        const response = await apiRequest('/tests/generate', {
            method: 'POST',
            body: JSON.stringify({
                content_id: contentId,
                test_title: testTitle || undefined,
                num_questions: questionCount,
                difficulty: difficulty
            })
        });
        
        showToast('Success', 'Test created successfully', 'success');
        
        // Reset form
        document.getElementById('test-form').reset();
        
        // Reload tests
        loadTests();
        
        // Update dashboard counts
        document.getElementById('test-count').textContent = tests.length + 1;
    } catch (error) {
        console.error('Test creation failed:', error);
        showToast('Error', error.message, 'danger');
    }
}

function viewTest(testId) {
    const test = tests.find(t => t.id === testId);
    if (!test) return;
    
    const modal = new bootstrap.Modal(document.getElementById('testModal'));
    const modalTitle = document.getElementById('testModalTitle');
    const modalBody = document.getElementById('testModalBody');
    
    modalTitle.textContent = test.title;
    
    // Build test HTML
    let html = `
        <div class="mb-3">
            <p><strong>Content:</strong> ${getContentName(test.content_id)}</p>
            <p><strong>Created:</strong> ${new Date(test.created_date).toLocaleDateString()}</p>
            <p><strong>Difficulty:</strong> <span class="badge bg-${getDifficultyColor(test.difficulty)}">${test.difficulty}</span></p>
            <p><strong>Total Points:</strong> ${test.total_points}</p>
        </div>
    `;
    
    // Add questions
    if (test.questions) {
        html += '<h5>Questions</h5>';
        
        test.questions.forEach((question, index) => {
            html += `
                <div class="question">
                    <div class="question-type">Question ${index + 1} - ${question.type.charAt(0).toUpperCase() + question.type.slice(1)} (${question.max_points} points)</div>
                    <div class="question-text">${question.question}</div>
            `;
            
            if (question.type === 'multiple_choice' && question.options) {
                html += '<div class="question-options">';
                question.options.forEach((option, i) => {
                    const isCorrect = i === question.correct_answer;
                    html += `
                        <div class="question-option">
                            ${String.fromCharCode(65 + i)}. ${option}
                            ${isCorrect ? ' <span class="correct-answer">(Correct Answer)</span>' : ''}
                        </div>
                    `;
                });
                html += '</div>';
            } else if (question.type === 'short_answer' && question.sample_answer) {
                html += `<p><strong>Sample Answer:</strong> ${question.sample_answer}</p>`;
            } else if (question.type === 'essay' && question.topic) {
                html += `<p><strong>Topic:</strong> ${question.topic}</p>`;
            }
            
            html += '</div>';
        });
    }
    
    modalBody.innerHTML = html;
    modal.show();
}

async function deleteTest(testId) {
    if (!confirm('Are you sure you want to delete this test?')) {
        return;
    }
    
    try {
        await apiRequest(`/tests/${testId}`, { method: 'DELETE' });
        showToast('Success', 'Test deleted successfully', 'success');
        
        // Reload tests
        loadTests();
        
        // Update dashboard counts
        document.getElementById('test-count').textContent = tests.length - 1;
    } catch (error) {
        console.error('Failed to delete test:', error);
        showToast('Error', error.message, 'danger');
    }
}

// Progress Functions
async function loadProgressData() {
    try {
        // Load students
        const studentsResponse = await apiRequest('/students');
        students = studentsResponse.students || [];
        updateStudentSelect();
    } catch (error) {
        console.error('Failed to load progress data:', error);
    }
}

function updateStudentSelect() {
    const select = document.getElementById('student-select');
    select.innerHTML = '<option value="">Choose a student...</option>';
    
    students.forEach(student => {
        const option = document.createElement('option');
        option.value = student.id;
        option.textContent = `${student.name} (${student.email})`;
        select.appendChild(option);
    });
}

async function handleStudentSelection(event) {
    const studentId = event.target.value;
    
    if (!studentId) {
        document.getElementById('student-progress-details').style.display = 'none';
        return;
    }
    
    try {
        selectedStudent = studentId;
        
        // Load student progress
        const progressResponse = await apiRequest(`/students/${studentId}/progress`);
        const progress = progressResponse;
        
        // Update progress display
        updateProgressDisplay(progress);
        
        // Show progress details
        document.getElementById('student-progress-details').style.display = 'block';
        
        // Load learning path if available
        loadLearningPath(studentId);
    } catch (error) {
        console.error('Failed to load student progress:', error);
        showToast('Error', error.message, 'danger');
    }
}

function updateProgressDisplay(progress) {
    // Update content completion
    const contentCompletion = progress.content_progress.completion_rate || 0;
    document.getElementById('content-completion').textContent = `${contentCompletion.toFixed(1)}%`;
    document.getElementById('content-progress-bar').style.width = `${contentCompletion}%`;
    
    // Update test performance
    const averageScore = progress.test_performance.average_score || 0;
    document.getElementById('average-score').textContent = `${averageScore.toFixed(1)}%`;
    document.getElementById('score-progress-bar').style.width = `${averageScore}%`;
    
    // Update other metrics
    document.getElementById('tests-taken').textContent = progress.test_performance.total_tests || 0;
    document.getElementById('highest-score').textContent = `${(progress.test_performance.highest_score || 0).toFixed(1)}%`;
    
    // Update performance trend
    const trend = progress.test_performance.performance_trend;
    let trendText = 'N/A';
    let trendClass = '';
    
    switch (trend) {
        case 'improving':
            trendText = 'Improving ↗️';
            trendClass = 'trend-up';
            break;
        case 'declining':
            trendText = 'Declining ↘️';
            trendClass = 'trend-down';
            break;
        case 'stable':
            trendText = 'Stable →';
            trendClass = 'trend-stable';
            break;
        case 'no_tests':
            trendText = 'No tests taken';
            break;
    }
    
    const trendElement = document.getElementById('performance-trend');
    trendElement.textContent = trendText;
    trendElement.className = trendClass;
    
    // Update strengths and weaknesses
    updateStrengthsWeaknesses(progress.strengths, progress.weaknesses);
}

function updateStrengthsWeaknesses(strengths, weaknesses) {
    const strengthsList = document.getElementById('strengths-list');
    const weaknessesList = document.getElementById('weaknesses-list');
    
    // Update strengths
    strengthsList.innerHTML = '';
    if (strengths && strengths.length > 0) {
        strengths.forEach(strength => {
            const li = document.createElement('li');
            li.className = 'strength';
            li.textContent = strength;
            strengthsList.appendChild(li);
        });
    } else {
        strengthsList.innerHTML = '<li>No strengths identified</li>';
    }
    
    // Update weaknesses
    weaknessesList.innerHTML = '';
    if (weaknesses && weaknesses.length > 0) {
        weaknesses.forEach(weakness => {
            const li = document.createElement('li');
            li.className = 'weakness';
            li.textContent = weakness;
            weaknessesList.appendChild(li);
        });
    } else {
        weaknessesList.innerHTML = '<li>No weaknesses identified</li>';
    }
}

async function loadLearningPath(studentId) {
    try {
        const response = await apiRequest(`/students/${studentId}/learning-path`);
        const learningPath = response;
        
        updateLearningPathDisplay(learningPath);
    } catch (error) {
        // It's okay if there's no learning path yet
        document.getElementById('learning-path-container').innerHTML = 
            '<p class="text-center">No learning path available for this student</p>';
    }
}

function updateLearningPathDisplay(learningPath) {
    const container = document.getElementById('learning-path-container');
    
    let html = `
        <h5>${learningPath.title}</h5>
        <p>${learningPath.description}</p>
        <p><strong>Estimated Completion Time:</strong> ${learningPath.estimated_completion_time}</p>
    `;
    
    if (learningPath.milestones) {
        html += '<h6 class="mt-3">Milestones</h6>';
        
        learningPath.milestones.forEach(milestone => {
            const statusClass = milestone.completed ? 'completed' : '';
            const statusText = milestone.completed ? 'Completed' : 'Pending';
            const statusBadgeClass = milestone.completed ? 'status-completed' : 'status-pending';
            
            html += `
                <div class="milestone ${statusClass}">
                    <div class="milestone-title">Milestone ${milestone.number}: ${milestone.title}</div>
                    <div class="milestone-description">${milestone.description}</div>
                    <div class="milestone-status ${statusBadgeClass}">${statusText}</div>
                </div>
            `;
        });
    }
    
    container.innerHTML = html;
}

async function handleStudentRegistration(event) {
    event.preventDefault();
    
    const name = document.getElementById('student-name').value;
    const email = document.getElementById('student-email').value;
    
    try {
        showToast('Registering', 'Registering student...', 'info');
        
        const response = await apiRequest('/students/register', {
            method: 'POST',
            body: JSON.stringify({
                name: name,
                email: email
            })
        });
        
        showToast('Success', 'Student registered successfully', 'success');
        
        // Reset form
        document.getElementById('student-form').reset();
        
        // Reload progress data
        loadProgressData();
        
        // Update dashboard counts
        document.getElementById('student-count').textContent = students.length + 1;
    } catch (error) {
        console.error('Student registration failed:', error);
        showToast('Error', error.message, 'danger');
    }
}

async function generateLearningPath() {
    if (!selectedStudent) {
        showToast('Error', 'Please select a student first', 'danger');
        return;
    }
    
    try {
        showToast('Generating', 'Generating learning path...', 'info');
        
        const response = await apiRequest('/learning-paths/generate', {
            method: 'POST',
            body: JSON.stringify({
                student_id: selectedStudent
            })
        });
        
        showToast('Success', 'Learning path generated successfully', 'success');
        
        // Reload learning path
        loadLearningPath(selectedStudent);
    } catch (error) {
        console.error('Learning path generation failed:', error);
        showToast('Error', error.message, 'danger');
    }
}

async function generateRecommendations() {
    if (!selectedStudent) {
        showToast('Error', 'Please select a student first', 'danger');
        return;
    }
    
    try {
        showToast('Generating', 'Generating recommendations...', 'info');
        
        const response = await apiRequest(`/students/${selectedStudent}/recommendations`);
        const recommendations = response;
        
        // Display recommendations in a modal
        const modal = new bootstrap.Modal(document.getElementById('contentModal'));
        const modalTitle = document.getElementById('contentModalTitle');
        const modalBody = document.getElementById('contentModalBody');
        
        modalTitle.textContent = 'Learning Recommendations';
        
        let html = `
            <div class="mb-3">
                <p><strong>Student:</strong> ${recommendations.student_name}</p>
                <p><strong>Generated:</strong> ${new Date(recommendations.generated_at).toLocaleDateString()}</p>
            </div>
        `;
        
        if (recommendations.overall_recommendations) {
            html += '<h5>Overall Recommendations</h5>';
            html += '<ul>';
            recommendations.overall_recommendations.forEach(rec => {
                html += `<li>${rec}</li>`;
            });
            html += '</ul>';
        }
        
        if (recommendations.topic_recommendations) {
            html += '<h5>Topic Recommendations</h5>';
            html += '<ul>';
            recommendations.topic_recommendations.forEach(rec => {
                html += `<li>${rec}</li>`;
            });
            html += '</ul>';
        }
        
        if (recommendations.study_strategies) {
            html += '<h5>Study Strategies</h5>';
            html += '<ul>';
            recommendations.study_strategies.forEach(strategy => {
                html += `<li>${strategy}</li>`;
            });
            html += '</ul>';
        }
        
        modalBody.innerHTML = html;
        modal.show();
    } catch (error) {
        console.error('Recommendation generation failed:', error);
        showToast('Error', error.message, 'danger');
    }
}