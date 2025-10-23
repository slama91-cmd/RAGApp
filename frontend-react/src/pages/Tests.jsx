import React, { useState, useEffect } from 'react';
import Modal from 'react-bootstrap/Modal';
import { useToast } from '../components/ToastContainer';
import { getContent, getTests, generateTest, deleteTest } from '../services/api';

const Tests = () => {
  const [content, setContent] = useState([]);
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [selectedContent, setSelectedContent] = useState('');
  const [testTitle, setTestTitle] = useState('');
  const [questionCount, setQuestionCount] = useState(10);
  const [difficulty, setDifficulty] = useState('medium');
  const [showModal, setShowModal] = useState(false);
  const [selectedTest, setSelectedTest] = useState(null);
  const { showToast } = useToast();

  useEffect(() => {
    loadTests();
  }, []);

  const loadTests = async () => {
    try {
      setLoading(true);
      
      // Load content for dropdown
      const contentResponse = await getContent();
      setContent(contentResponse.content || []);
      
      // Load tests
      const testsResponse = await getTests();
      setTests(testsResponse.tests || []);
    } catch (error) {
      console.error('Failed to load tests:', error);
      showToast('Error', 'Failed to load tests', 'danger');
    } finally {
      setLoading(false);
    }
  };

  const handleTestCreation = async (event) => {
    event.preventDefault();
    
    if (!selectedContent) {
      showToast('Error', 'Please select content', 'danger');
      return;
    }
    
    try {
      setCreating(true);
      showToast('Creating', 'Creating test...', 'info');
      
      await generateTest(selectedContent, testTitle, questionCount, difficulty);
      showToast('Success', 'Test created successfully', 'success');
      
      // Reset form
      setSelectedContent('');
      setTestTitle('');
      setQuestionCount(10);
      setDifficulty('medium');
      
      // Reload tests
      loadTests();
    } catch (error) {
      console.error('Test creation failed:', error);
      showToast('Error', error.message, 'danger');
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteTest = async (testId) => {
    if (!window.confirm('Are you sure you want to delete this test?')) {
      return;
    }
    
    try {
      await deleteTest(testId);
      showToast('Success', 'Test deleted successfully', 'success');
      
      // Reload tests
      loadTests();
    } catch (error) {
      console.error('Failed to delete test:', error);
      showToast('Error', error.message, 'danger');
    }
  };

  const handleViewTest = (test) => {
    setSelectedTest(test);
    setShowModal(true);
  };

  const getContentName = (contentId) => {
    const item = content.find(c => c.id === contentId);
    return item ? item.title : 'Unknown';
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy': return 'success';
      case 'medium': return 'warning';
      case 'hard': return 'danger';
      default: return 'secondary';
    }
  };

  const renderTestModal = () => {
    if (!selectedTest) return null;

    return (
      <Modal show={showModal} onHide={() => setShowModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>{selectedTest.title}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <div className="mb-3">
            <p><strong>Content:</strong> {getContentName(selectedTest.content_id)}</p>
            <p><strong>Created:</strong> {new Date(selectedTest.created_date).toLocaleDateString()}</p>
            <p><strong>Difficulty:</strong> <span className={`badge bg-${getDifficultyColor(selectedTest.difficulty)}`}>{selectedTest.difficulty}</span></p>
            <p><strong>Total Points:</strong> {selectedTest.total_points}</p>
          </div>
          
          {/* Add questions */}
          {selectedTest.questions && (
            <>
              <h5>Questions</h5>
              
              {selectedTest.questions.map((question, index) => (
                <div key={index} className="question">
                  <div className="question-type">
                    Question {index + 1} - {question.type.charAt(0).toUpperCase() + question.type.slice(1)} ({question.max_points} points)
                  </div>
                  <div className="question-text">{question.question}</div>
                  
                  {question.type === 'multiple_choice' && question.options && (
                    <div className="question-options">
                      {question.options.map((option, i) => {
                        const isCorrect = i === question.correct_answer;
                        return (
                          <div key={i} className="question-option">
                            {String.fromCharCode(65 + i)}. {option}
                            {isCorrect && <span className="correct-answer"> (Correct Answer)</span>}
                          </div>
                        );
                      })}
                    </div>
                  )}
                  
                  {question.type === 'short_answer' && question.sample_answer && (
                    <p><strong>Sample Answer:</strong> {question.sample_answer}</p>
                  )}
                  
                  {question.type === 'essay' && question.topic && (
                    <p><strong>Topic:</strong> {question.topic}</p>
                  )}
                </div>
              ))}
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <button className="btn btn-secondary" onClick={() => setShowModal(false)}>
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
      <h1>Tests</h1>
      
      <div className="card mb-4">
        <div className="card-header">Create New Test</div>
        <div className="card-body">
          <form onSubmit={handleTestCreation}>
            <div className="mb-3">
              <label htmlFor="content-select" className="form-label">Select Content</label>
              <select 
                className="form-select" 
                id="content-select" 
                value={selectedContent}
                onChange={(e) => setSelectedContent(e.target.value)}
                required
                disabled={creating}
              >
                <option value="">Choose content...</option>
                {content.map(item => (
                  <option key={item.id} value={item.id}>
                    {item.title}
                  </option>
                ))}
              </select>
            </div>
            <div className="mb-3">
              <label htmlFor="test-title" className="form-label">Test Title (Optional)</label>
              <input 
                type="text" 
                className="form-control" 
                id="test-title" 
                placeholder="Leave blank for auto-generated title"
                value={testTitle}
                onChange={(e) => setTestTitle(e.target.value)}
                disabled={creating}
              />
            </div>
            <div className="mb-3">
              <label htmlFor="question-count" className="form-label">Number of Questions</label>
              <input 
                type="number" 
                className="form-control" 
                id="question-count" 
                min="1" 
                max="50" 
                value={questionCount}
                onChange={(e) => setQuestionCount(parseInt(e.target.value))}
                disabled={creating}
              />
            </div>
            <div className="mb-3">
              <label htmlFor="difficulty" className="form-label">Difficulty</label>
              <select 
                className="form-select" 
                id="difficulty"
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                disabled={creating}
              >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>
            <button 
              type="submit" 
              className="btn btn-info" 
              disabled={creating}
            >
              {creating ? 'Creating...' : 'Create Test'}
            </button>
          </form>
        </div>
      </div>

      <div className="card">
        <div className="card-header">Created Tests</div>
        <div className="card-body">
          <div className="table-responsive">
            <table className="table table-striped">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Content</th>
                  <th>Questions</th>
                  <th>Difficulty</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {tests.length > 0 ? (
                  tests.map(test => (
                    <tr key={test.id}>
                      <td>{test.title}</td>
                      <td>{getContentName(test.content_id)}</td>
                      <td>{test.questions ? test.questions.length : 0}</td>
                      <td>
                        <span className={`badge bg-${getDifficultyColor(test.difficulty)}`}>
                          {test.difficulty}
                        </span>
                      </td>
                      <td>
                        <div className="action-buttons">
                          <button 
                            className="btn btn-sm btn-primary" 
                            onClick={() => handleViewTest(test)}
                          >
                            View
                          </button>
                          <button 
                            className="btn btn-sm btn-danger" 
                            onClick={() => handleDeleteTest(test.id)}
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="5" className="text-center">No tests created yet</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {renderTestModal()}
    </div>
  );
};

export default Tests;