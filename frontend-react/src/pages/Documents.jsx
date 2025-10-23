import React, { useState, useEffect } from 'react';
import { useToast } from '../components/ToastContainer';
import { getDocuments, uploadDocument, deleteDocument } from '../services/api';

const Documents = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const { showToast } = useToast();

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const response = await getDocuments();
      setDocuments(response.documents || []);
    } catch (error) {
      console.error('Failed to load documents:', error);
      showToast('Error', 'Failed to load documents', 'danger');
    } finally {
      setLoading(false);
    }
  };

  const handleDocumentUpload = async (event) => {
    event.preventDefault();
    
    const fileInput = event.target.elements['document-file'];
    const file = fileInput.files[0];
    
    if (!file) {
      showToast('Error', 'Please select a file', 'danger');
      return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      setUploading(true);
      showToast('Uploading', 'Uploading document...', 'info');
      
      await uploadDocument(formData);
      showToast('Success', 'Document uploaded successfully', 'success');
      
      // Reset form
      fileInput.value = '';
      
      // Reload documents
      loadDocuments();
    } catch (error) {
      console.error('Document upload failed:', error);
      showToast('Error', error.message, 'danger');
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteDocument = async (documentId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }
    
    try {
      await deleteDocument(documentId);
      showToast('Success', 'Document deleted successfully', 'success');
      
      // Reload documents
      loadDocuments();
    } catch (error) {
      console.error('Failed to delete document:', error);
      showToast('Error', error.message, 'danger');
    }
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
      <h1>Documents</h1>
      
      <div className="card mb-4">
        <div className="card-header">Upload New Document</div>
        <div className="card-body">
          <form onSubmit={handleDocumentUpload}>
            <div className="mb-3">
              <label htmlFor="document-file" className="form-label">Select PDF Document</label>
              <input 
                type="file" 
                className="form-control" 
                id="document-file" 
                accept=".pdf" 
                required 
                disabled={uploading}
              />
            </div>
            <button 
              type="submit" 
              className="btn btn-primary" 
              disabled={uploading}
            >
              {uploading ? 'Uploading...' : 'Upload'}
            </button>
          </form>
        </div>
      </div>

      <div className="card">
        <div className="card-header">Uploaded Documents</div>
        <div className="card-body">
          <div className="table-responsive">
            <table className="table table-striped">
              <thead>
                <tr>
                  <th>Filename</th>
                  <th>Upload Date</th>
                  <th>Chunks</th>
                  <th>Characters</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {documents.length > 0 ? (
                  documents.map(doc => (
                    <tr key={doc.document_id}>
                      <td>{doc.filename}</td>
                      <td>{new Date(doc.upload_date).toLocaleDateString()}</td>
                      <td>{doc.chunk_count}</td>
                      <td>{doc.total_characters}</td>
                      <td>
                        <div className="action-buttons">
                          <button 
                            className="btn btn-sm btn-danger" 
                            onClick={() => handleDeleteDocument(doc.document_id)}
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="5" className="text-center">No documents uploaded yet</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Documents;