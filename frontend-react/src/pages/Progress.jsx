import React, { useState, useEffect } from 'react';
import Modal from 'react-bootstrap/Modal';
import { useToast } from '../components/ToastContainer';
import { 
  getStudents, 
  registerStudent, 
  getStudentProgress, 
  getStudentLearningPath,
  getStudentRecommendations,
  generateLearningPath 
} from '../services/api';

const Progress = () => {
  const [students, setStudents] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState('');
  const [studentProgress, setStudentProgress] = useState(null);
  const [learningPath, setLearningPath] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);
  const [registering, setRegistering] = useState(false);
  const [showRecommendationsModal, setShowRecommendationsModal] = useState(false);
  const [studentName, setStudentName] = useState('');
  const [studentEmail, setStudentEmail] = useState('');
  const { showToast } = useToast();

  useEffect(() => {
    loadProgressData();
  }, []);

  const loadProgressData = async () => {
    try {
      setLoading(true);
      const response = await getStudents();
      setStudents(response.students || []);
    } catch (error) {
      console.error('Failed to load progress data:', error);
      showToast('Error', 'Failed to load students', 'danger');
    } finally {
      setLoading(false);
    }
  };

  const handleStudentRegistration = async (event) => {
    event.preventDefault();
    
    try {
      setRegistering(true);
      showToast('Registering', 'Registering student...', 'info');
      
      await registerStudent(studentName, studentEmail);
      showToast('Success', 'Student registered successfully', 'success');
      
      // Reset form
      setStudentName('');
      setStudentEmail('');
      
      // Reload progress data
      loadProgressData();
    } catch (error) {
      console.error('Student registration failed:', error);
      showToast('Error', error.message, 'danger');
    } finally {
      setRegistering(false);
    }
  };

  const handleStudentSelection = async (studentId) => {
    setSelectedStudent(studentId);
    
    if (!studentId) {
      setStudentProgress(null);
      setLearningPath(null);
      return;
    }
    
    try {
      // Load student progress
      const progressResponse = await getStudentProgress(studentId);
      setStudentProgress(progressResponse);
      
      // Load learning path if available
      try {
        const learningPathResponse = await getStudentLearningPath(studentId);
        setLearningPath(learningPathResponse);
      } catch (error) {
        // It's okay if there's no learning path yet
        setLearningPath(null);
      }
    } catch (error) {
      console.error('Failed to load student progress:', error);
      showToast('Error', error.message, 'danger');
    }
  };

  const handleGenerateLearningPath = async () => {
    if (!selectedStudent) {
      showToast('Error', 'Please select a student first', 'danger');
      return;
    }
    
    try {
      showToast('Generating', 'Generating learning path...', 'info');
      
      await generateLearningPath(selectedStudent);
      showToast('Success', 'Learning path generated successfully', 'success');
      
      // Reload learning path
      const learningPathResponse = await getStudentLearningPath(selectedStudent);
      setLearningPath(learningPathResponse);
    } catch (error) {
      console.error('Learning path generation failed:', error);
      showToast('Error', error.message, 'danger');
    }
  };

  const handleGenerateRecommendations = async () => {
    if (!selectedStudent) {
      showToast('Error', 'Please select a student first', 'danger');
      return;
    }
    
    try {
      showToast('Generating', 'Generating recommendations...', 'info');
      
      const response = await getStudentRecommendations(selectedStudent);
      setRecommendations(response);
      setShowRecommendationsModal(true);
    } catch (error) {
      console.error('Recommendation generation failed:', error);
      showToast('Error', error.message, 'danger');
    }
  };

  const getPerformanceTrend = (trend) => {
    switch (trend) {
      case 'improving':
        return { text: 'Improving ↗️', class: 'trend-up' };
      case 'declining':
        return { text: 'Declining ↘️', class: 'trend-down' };
      case 'stable':
        return { text: 'Stable →', class: 'trend-stable' };
      case 'no_tests':
        return { text: 'No tests taken', class: '' };
      default:
        return { text: 'N/A', class: '' };
    }
  };

  const renderProgressDetails = () => {
    if (!studentProgress) return null;

    const contentCompletion = studentProgress.content_progress.completion_rate || 0;
    const averageScore = studentProgress.test_performance.average_score || 0;
    const trend = getPerformanceTrend(studentProgress.test_performance.performance_trend);

    return (
      <div id="student-progress-details">
        <div className="row">
          <div className="col-md-6">
            <h5>Performance Summary</h5>
            <div className="mb-3">
              <label className="form-label">
                Content Completion: <span>{contentCompletion.toFixed(1)}%</span>
              </label>
              <div className="progress">
                <div 
                  className="progress-bar" 
                  role="progressbar" 
                  style={{ width: `${contentCompletion}%` }}
                ></div>
              </div>
            </div>
            <div className="mb-3">
              <label className="form-label">
                Average Test Score: <span>{averageScore.toFixed(1)}%</span>
              </label>
              <div className="progress">
                <div 
                  className="progress-bar bg-info" 
                  role="progressbar" 
                  style={{ width: `${averageScore}%` }}
                ></div>
              </div>
            </div>
            <div className="mb-3">
              <p><strong>Tests Taken:</strong> {studentProgress.test_performance.total_tests || 0}</p>
              <p><strong>Highest Score:</strong> {(studentProgress.test_performance.highest_score || 0).toFixed(1)}%</p>
              <p><strong>Performance Trend:</strong> <span className={trend.class}>{trend.text}</span></p>
            </div>
          </div>
          <div className="col-md-6">
            <h5>Strengths & Weaknesses</h5>
            <div className="mb-3">
              <h6>Strengths:</h6>
              <ul id="strengths-list">
                {studentProgress.strengths && studentProgress.strengths.length > 0 ? (
                  studentProgress.strengths.map((strength, index) => (
                    <li key={index} className="strength">{strength}</li>
                  ))
                ) : (
                  <li>No strengths identified</li>
                )}
              </ul>
            </div>
            <div className="mb-3">
              <h6>Weaknesses:</h6>
              <ul id="weaknesses-list">
                {studentProgress.weaknesses && studentProgress.weaknesses.length > 0 ? (
                  studentProgress.weaknesses.map((weakness, index) => (
                    <li key={index} className="weakness">{weakness}</li>
                  ))
                ) : (
                  <li>No weaknesses identified</li>
                )}
              </ul>
            </div>
          </div>
        </div>
        <div className="mt-3">
          <button className="btn btn-primary me-2" onClick={handleGenerateLearningPath}>
            Generate Learning Path
          </button>
          <button className="btn btn-info" onClick={handleGenerateRecommendations}>
            Get Recommendations
          </button>
        </div>
      </div>
    );
  };

  const renderLearningPath = () => {
    if (!learningPath) {
      return (
        <div id="learning-path-container">
          <p className="text-center">
            {selectedStudent ? 'No learning path available for this student' : 'Select a student to view their learning path'}
          </p>
        </div>
      );
    }

    return (
      <div id="learning-path-container">
        <h5>{learningPath.title}</h5>
        <p>{learningPath.description}</p>
        <p><strong>Estimated Completion Time:</strong> {learningPath.estimated_completion_time}</p>
        
        {learningPath.milestones && (
          <>
            <h6 className="mt-3">Milestones</h6>
            
            {learningPath.milestones.map((milestone, index) => {
              const statusClass = milestone.completed ? 'completed' : '';
              const statusText = milestone.completed ? 'Completed' : 'Pending';
              const statusBadgeClass = milestone.completed ? 'status-completed' : 'status-pending';
              
              return (
                <div key={index} className={`milestone ${statusClass}`}>
                  <div className="milestone-title">
                    Milestone {milestone.number}: {milestone.title}
                  </div>
                  <div className="milestone-description">{milestone.description}</div>
                  <div className={`milestone-status ${statusBadgeClass}`}>{statusText}</div>
                </div>
              );
            })}
          </>
        )}
      </div>
    );
  };

  const renderRecommendationsModal = () => {
    if (!recommendations) return null;

    return (
      <Modal show={showRecommendationsModal} onHide={() => setShowRecommendationsModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Learning Recommendations</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <div className="mb-3">
            <p><strong>Student:</strong> {recommendations.student_name}</p>
            <p><strong>Generated:</strong> {new Date(recommendations.generated_at).toLocaleDateString()}</p>
          </div>
          
          {recommendations.overall_recommendations && (
            <>
              <h5>Overall Recommendations</h5>
              <ul>
                {recommendations.overall_recommendations.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </>
          )}
          
          {recommendations.topic_recommendations && (
            <>
              <h5>Topic Recommendations</h5>
              <ul>
                {recommendations.topic_recommendations.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </>
          )}
          
          {recommendations.study_strategies && (
            <>
              <h5>Study Strategies</h5>
              <ul>
                {recommendations.study_strategies.map((strategy, index) => (
                  <li key={index}>{strategy}</li>
                ))}
              </ul>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <button className="btn btn-secondary" onClick={() => setShowRecommendationsModal(false)}>
            Close
          </button>
        </Modal.Footer>
      </Modal>
    );
  };

  if (loading) {
    return (
      <div className="spinner-container">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <h1>Student Progress</h1>
      
      <div className="card mb-4">
        <div className="card-header">Register New Student</div>
        <div className="card-body">
          <form onSubmit={handleStudentRegistration}>
            <div className="mb-3">
              <label htmlFor="student-name" className="form-label">Student Name</label>
              <input 
                type="text" 
                className="form-control" 
                id="student-name" 
                value={studentName}
                onChange={(e) => setStudentName(e.target.value)}
                required
                disabled={registering}
              />
            </div>
            <div className="mb-3">
              <label htmlFor="student-email" className="form-label">Student Email</label>
              <input 
                type="email" 
                className="form-control" 
                id="student-email" 
                value={studentEmail}
                onChange={(e) => setStudentEmail(e.target.value)}
                required
                disabled={registering}
              />
            </div>
            <button 
              type="submit" 
              className="btn btn-warning" 
              disabled={registering}
            >
              {registering ? 'Registering...' : 'Register Student'}
            </button>
          </form>
        </div>
      </div>

      <div className="card mb-4">
        <div className="card-header">Student Progress</div>
        <div className="card-body">
          <div className="mb-3">
            <label htmlFor="student-select" className="form-label">Select Student</label>
            <select 
              className="form-select" 
              id="student-select"
              value={selectedStudent}
              onChange={(e) => handleStudentSelection(e.target.value)}
            >
              <option value="">Choose a student...</option>
              {students.map(student => (
                <option key={student.id} value={student.id}>
                  {student.name} ({student.email})
                </option>
              ))}
            </select>
          </div>
          
          {selectedStudent && renderProgressDetails()}
        </div>
      </div>

      <div className="card">
        <div className="card-header">Learning Path</div>
        <div className="card-body">
          {renderLearningPath()}
        </div>
      </div>

      {renderRecommendationsModal()}
    </div>
  );
};

export default Progress;