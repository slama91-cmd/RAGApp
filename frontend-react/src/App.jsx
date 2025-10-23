import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import Content from './pages/Content';
import Tests from './pages/Tests';
import Progress from './pages/Progress';
import { ToastProvider } from './components/ToastContainer';

function App() {
  return (
    <ToastProvider>
      <div className="App">
        <Navbar />
        <div className="container mt-4">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/content" element={<Content />} />
            <Route path="/tests" element={<Tests />} />
            <Route path="/progress" element={<Progress />} />
          </Routes>
        </div>
      </div>
    </ToastProvider>
  );
}

export default App;