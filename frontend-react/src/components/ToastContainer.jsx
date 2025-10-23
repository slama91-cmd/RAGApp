import React, { createContext, useContext, useState, useCallback } from 'react';
import Toast from 'react-bootstrap/Toast';

const ToastContext = createContext();

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const showToast = useCallback((title, message, type = 'info') => {
    const id = Date.now();
    const newToast = { id, title, message, type };
    
    setToasts(prev => [...prev, newToast]);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
      setToasts(prev => prev.filter(toast => toast.id !== id));
    }, 5000);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div className="position-fixed bottom-0 end-0 p-3" style={{ zIndex: 11 }}>
        {toasts.map(toast => (
          <Toast
            key={toast.id}
            onClose={() => removeToast(toast.id)}
            show={true}
            bg={toast.type === 'danger' ? 'danger' : toast.type === 'success' ? 'success' : 'primary'}
            text="white"
          >
            <Toast.Header closeButton={true}>
              <strong className="me-auto">{toast.title}</strong>
            </Toast.Header>
            <Toast.Body>{toast.message}</Toast.Body>
          </Toast>
        ))}
      </div>
    </ToastContext.Provider>
  );
};

const ToastContainer = () => {
  return <ToastProvider />;
};

export default ToastContainer;