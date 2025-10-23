import React, { useState, useEffect } from 'react';
import Modal from 'react-bootstrap/Modal';
import { useToast } from '../components/ToastContainer';
import { getDocuments, getContent, generateContent, deleteContent } from '../services/api';

const Content = () => {
  const [documents, setDocuments] = useState([]);
  const [content, setContent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState('');
  const [includeLessonPlan, setIncludeLessonPlan] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedContent, setSelectedContent] = useState(null);
  const { showToast } = useToast();

  useEffect(() => {
    loadContent();
  }, []);

  const loadContent = async () => {
    try {
      setLoading(true);
      
      // Load documents for dropdown
      const documentsResponse = await getDocuments();
      setDocuments(documentsResponse.documents || []);
      
      // Load content
      const contentResponse = await getContent();
      setContent(contentResponse.content || []);
    } catch (error) {
      console.error('Failed to load content:', error);
      showToast('Error', 'Failed to load content', 'danger');
    } finally {
      setLoading(false);
    }
  };

  const handleContentGeneration = async (event) => {
    event.preventDefault();
    
    if (!selectedDocument) {
      showToast('Error', 'Please select a document', 'danger');
      return;
    }
    
    try {
      setGenerating(true);
      showToast('Generating', 'Generating content...', 'info');
      
      await generateContent(selectedDocument, includeLessonPlan);
      showToast('Success', 'Content generated successfully', 'success');
      
      // Reset form
      setSelectedDocument('');
      setIncludeLessonPlan(true);
      
      // Reload content
      loadContent();
    } catch (error) {
      console.error('Content generation failed:', error);
      showToast('Error', error.message, 'danger');
    } finally {
      setGenerating(false);
    }
  };

  const handleDeleteContent = async (contentId) => {
    if (!window.confirm('Are you sure you want to delete this content?')) {
      return;
    }
    
    try {
      await deleteContent(contentId);
      showToast('Success', 'Content deleted successfully', 'success');
      
      // Reload content
      loadContent();
    } catch (error) {
      console.error('Failed to delete content:', error);
      showToast('Error', error.message, 'danger');
    }
  };

  const handleViewContent = (contentItem) => {
    setSelectedContent(contentItem);
    setShowModal(true);
  };

  const getDocumentName = (documentId) => {
    const doc = documents.find(d => d.document_id === documentId);
    return doc ? doc.filename : 'Unknown';
  };

  const renderContentModal = () => {
    if (!selectedContent) return null;

    return (
      <Modal show={showModal} onHide={() => setShowModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>{selectedContent.title}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <div className="mb-3">
            <p><strong>Document:</strong> {getDocumentName(selectedContent.document_id)}</p>
            <p><strong>Created:</strong> {new Date(selectedContent.created_date).toLocaleDateString()}</p>
            <p><strong>Topics:</strong> {selectedContent.topics ? selectedContent.topics.join(', ') : 'N/A'}</p>
          </div>
          
          {/* Add content outline */}
          {selectedContent.content_outline && (
            <>
              <h5>Content Outline</h5>
              
              {/* Add introduction */}
              {selectedContent.content_outline.introduction && (
                <div className="content-section">
                  <h6>Introduction</h6>
                  <p>{selectedContent.content_outline.introduction.overview}</p>
                  <p><strong>Objectives:</strong></p>
                  <ul>
                    {selectedContent.content_outline.introduction.objectives.map((obj, index) => (
                      <li key={index}>{obj}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Add sections */}
              {selectedContent.content_outline.sections && (
                selectedContent.content_outline.sections.map((section, index) => (
                  <div key={index} className="content-section">
                    <h6>{section.title}</h6>
                    <div className="section-content">
                      <p><strong>Summary:</strong> {section.content_summary}</p>
                      <p><strong>Key Points:</strong></p>
                      <ul>
                        {section.key_points.map((point, idx) => (
                          <li key={idx}>{point}</li>
                        ))}
                      </ul>
                    </div>
                    <div className="section-questions">
                      <p><strong>Study Questions:</strong></p>
                      <ul>
                        {section.study_questions.map((q, idx) => (
                          <li key={idx} className="study-question">{q.question}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))
              )}
              
              {/* Add conclusion */}
              {selectedContent.content_outline.conclusion && (
                <div className="content-section">
                  <h6>Conclusion</h6>
                  <p>{selectedContent.content_outline.conclusion.summary}</p>
                  <p><strong>Next Steps:</strong></p>
                  <ul>
                    {selectedContent.content_outline.conclusion.next_steps.map((step, index) => (
                      <li key={index}>{step}</li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
          
          {/* Add lesson plan if available */}
          {selectedContent.lesson_plan && (
            <>
              <h5>Lesson Plan</h5>
              <p><strong>Duration:</strong> {selectedContent.lesson_plan.duration_days} days</p>
              
              {selectedContent.lesson_plan.daily_schedule && (
                <div className="accordion" id="lessonPlanAccordion">
                  {selectedContent.lesson_plan.daily_schedule.map((day, index) => (
                    <div key={index} className="accordion-item">
                      <h2 className="accordion-header" id={`heading${index}`}>
                        <button 
                          className="accordion-button collapsed" 
                          type="button" 
                          data-bs-toggle="collapse" 
                          data-bs-target={`#collapse${index}`}
                        >
                          Day {day.day}: {day.topics.join(', ')}
                        </button>
                      </h2>
                      <div 
                        id={`collapse${index}`} 
                        className="accordion-collapse collapse" 
                        data-bs-parent="#lessonPlanAccordion"
                      >
                        <div className="accordion-body">
                          <p><strong>Topics:</strong> {day.topics.join(', ')}</p>
                          <p><strong>Activities:</strong></p>
                          <ul>
                            {day.activities.map((activity, idx) => (
                              <li key={idx}>{activity}</li>
                            ))}
                          </ul>
                          <p><strong>Estimated Time:</strong> {day.estimated_time}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
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
      <h1>Educational Content</h1>
      
      <div className="card mb-4">
        <div className="card-header">Generate New Content</div>
        <div className="card-body">
          <form onSubmit={handleContentGeneration}>
            <div className="mb-3">
              <label htmlFor="document-select" className="form-label">Select Document</label>
              <select 
                className="form-select" 
                id="document-select" 
                value={selectedDocument}
                onChange={(e) => setSelectedDocument(e.target.value)}
                required
                disabled={generating}
              >
                <option value="">Choose a document...</option>
                {documents.map(doc => (
                  <option key={doc.document_id} value={doc.document_id}>
                    {doc.filename}
                  </option>
                ))}
              </select>
            </div>
            <div className="mb-3 form-check">
              <input 
                type="checkbox" 
                className="form-check-input" 
                id="include-lesson-plan" 
                checked={includeLessonPlan}
                onChange={(e) => setIncludeLessonPlan(e.target.checked)}
                disabled={generating}
              />
              <label className="form-check-label" htmlFor="include-lesson-plan">
                Include Lesson Plan
              </label>
            </div>
            <button 
              type="submit" 
              className="btn btn-success" 
              disabled={generating}
            >
              {generating ? 'Generating...' : 'Generate Content'}
            </button>
          </form>
        </div>
      </div>

      <div className="card">
        <div className="card-header">Generated Content</div>
        <div className="card-body">
          <div className="table-responsive">
            <table className="table table-striped">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Document</th>
                  <th>Created Date</th>
                  <th>Topics</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {content.length > 0 ? (
                  content.map(item => (
                    <tr key={item.id}>
                      <td>{item.title}</td>
                      <td>{getDocumentName(item.document_id)}</td>
                      <td>{new Date(item.created_date).toLocaleDateString()}</td>
                      <td>
                        {item.topics ? item.topics.map((topic, index) => (
                          <span key={index} className="topic-tag">{topic}</span>
                        )) : 'N/A'}
                      </td>
                      <td>
                        <div className="action-buttons">
                          <button 
                            className="btn btn-sm btn-primary" 
                            onClick={() => handleViewContent(item)}
                          >
                            View
                          </button>
                          <button 
                            className="btn btn-sm btn-danger" 
                            onClick={() => handleDeleteContent(item.id)}
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="5" className="text-center">No content generated yet</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {renderContentModal()}
    </div>
  );
};

export default Content;