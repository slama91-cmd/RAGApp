import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useToast } from '../components/ToastContainer';
import { getDocuments, getContent, getTests, getStudents } from '../services/api';

const Dashboard = () => {
  const [documents, setDocuments] = useState([]);
  const [content, setContent] = useState([]);
  const [tests, setTests] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const { showToast } = useToast();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load all data in parallel
      const [documentsResponse, contentResponse, testsResponse, studentsResponse] = await Promise.all([
        getDocuments(),
        getContent(),
        getTests(),
        getStudents()
      ]);

      setDocuments(documentsResponse.documents || []);
      setContent(contentResponse.content || []);
      setTests(testsResponse.tests || []);
      setStudents(studentsResponse.students || []);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      showToast('Error', 'Failed to load dashboard data', 'danger');
    } finally {
      setLoading(false);
    }
  };

  const getRecentActivities = () => {
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
    return activities
      .sort((a, b) => new Date(b.date) - new Date(a.date))
      .slice(0, 5);
  };

  const recentActivities = getRecentActivities();

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
      <h1>Dashboard</h1>
      
      <div className="row">
        <div className="col-md-3">
          <div className="card text-white bg-primary mb-3">
            <div className="card-header">Documents</div>
            <div className="card-body">
              <h5 className="card-title">{documents.length}</h5>
              <p className="card-text">Uploaded Documents</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-white bg-success mb-3">
            <div className="card-header">Content</div>
            <div className="card-body">
              <h5 className="card-title">{content.length}</h5>
              <p className="card-text">Generated Content</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-white bg-info mb-3">
            <div className="card-header">Tests</div>
            <div className="card-body">
              <h5 className="card-title">{tests.length}</h5>
              <p className="card-text">Created Tests</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-white bg-warning mb-3">
            <div className="card-header">Students</div>
            <div className="card-body">
              <h5 className="card-title">{students.length}</h5>
              <p className="card-text">Registered Students</p>
            </div>
          </div>
        </div>
      </div>

      <div className="row mt-4">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">Recent Activity</div>
            <div className="card-body">
              <ul className="list-group">
                {recentActivities.length > 0 ? (
                  recentActivities.map((activity, index) => (
                    <li key={index} className="list-group-item">
                      {activity.text}
                    </li>
                  ))
                ) : (
                  <li className="list-group-item">No recent activity</li>
                )}
              </ul>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">Quick Actions</div>
            <div className="card-body">
              <div className="d-grid gap-2">
                <Link to="/documents" className="btn btn-primary">Upload Document</Link>
                <Link to="/content" className="btn btn-success">Generate Content</Link>
                <Link to="/tests" className="btn btn-info">Create Test</Link>
                <Link to="/progress" className="btn btn-warning">View Progress</Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;