import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navbar = () => {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path || (path === '/dashboard' && location.pathname === '/');
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-primary">
      <div className="container">
        <Link className="navbar-brand" to="/">EduMentor AI</Link>
        <button 
          className="navbar-toggler" 
          type="button" 
          data-bs-toggle="collapse" 
          data-bs-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav">
            <li className="nav-item">
              <Link 
                className={`nav-link ${isActive('/dashboard') ? 'active' : ''}`} 
                to="/dashboard"
              >
                Dashboard
              </Link>
            </li>
            <li className="nav-item">
              <Link 
                className={`nav-link ${isActive('/documents') ? 'active' : ''}`} 
                to="/documents"
              >
                Documents
              </Link>
            </li>
            <li className="nav-item">
              <Link 
                className={`nav-link ${isActive('/content') ? 'active' : ''}`} 
                to="/content"
              >
                Content
              </Link>
            </li>
            <li className="nav-item">
              <Link 
                className={`nav-link ${isActive('/tests') ? 'active' : ''}`} 
                to="/tests"
              >
                Tests
              </Link>
            </li>
            <li className="nav-item">
              <Link 
                className={`nav-link ${isActive('/progress') ? 'active' : ''}`} 
                to="/progress"
              >
                Progress
              </Link>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;