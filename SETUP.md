# EduMentor AI - Complete Setup Guide

This guide will help you set up the entire EduMentor AI application, including both the backend API and the React frontend.

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- pip and npm/yarn package managers

## Backend Setup

### 1. Install Python Dependencies

Navigate to the root directory and install the required Python packages:

```bash
pip install -r requirements.txt

### 3. Fix Dependency Issues (If Needed)

If you encounter import errors related to `sentence-transformers`, `timm`, or `huggingface-hub`, run the comprehensive fix script:

```bash
./fix-all-dependencies.sh
```

This will install compatible versions of all ML/AI packages including PyTorch, Transformers, and their dependencies.
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory:

```
EDU_API_KEY=edu-api-key-1234
```

### 3. Run the Backend API

Start the FastAPI server:

```bash
python api.py
```

The API will be available at `http://localhost:8000`.

### 4. Access API Documentation

Open your browser and navigate to `http://localhost:8000/docs` to view the interactive API documentation.

## Frontend Setup

### 1. Navigate to Frontend Directory

```bash
cd frontend-react
```

### 2. Install Node.js Dependencies

```bash
npm install
```

### 3. Set Up Environment Variables (Optional)

Create a `.env` file in the `frontend-react` directory:

```
VITE_API_BASE_URL=http://localhost:8000
VITE_API_KEY=edu-api-key-1234
```

### 4. Start the Development Server

```bash
npm run dev
```

The React application will be available at `http://localhost:3000`.

## Running Both Services

For development, you'll need to run both the backend and frontend services simultaneously:

### Option 1: Two Terminal Windows

1. **Terminal 1 - Backend**:
   ```bash
   python api.py
   ```

2. **Terminal 2 - Frontend**:
   ```bash
   cd frontend-react
   npm run dev
   ```

### Option 2: Using the Startup Script

For convenience, you can use the provided startup script to run both services with a single command:

```bash
./start-app.sh
```

This script will:
- Check and install dependencies if needed
- Start the backend API server
- Start the frontend development server
- Display URLs for both services

### Option 3: Using a Process Manager

You can use tools like `concurrently` or `npm-run-all` to run both services with a single command:

1. Install concurrently in the root directory:
   ```bash
   npm install -g concurrently
   ```

2. Add a script to the root package.json (create one if it doesn't exist):
   ```json
   {
     "scripts": {
       "dev": "concurrently \"python api.py\" \"cd frontend-react && npm run dev\""
     }
   }
   ```

3. Run both services:
   ```bash
   npm run dev
   ```

## Building for Production

### Backend

The backend is ready for production deployment. You can use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn api:app --host 0.0.0.0 --port 8000
```

### Frontend

Build the React application for production:

```bash
cd frontend-react
npm run build
```

The built files will be in the `frontend-react/dist` directory. You can serve these files with any static web server.

## Testing the Application

### Backend Testing

The FastAPI API includes interactive documentation at `http://localhost:8000/docs` where you can test all endpoints.

### Frontend Testing

Run the build test to ensure the React application builds correctly:

```bash
cd frontend-react
./test-build.sh
```

## Troubleshooting

### Common Issues

1. **Import Errors in Backend**:
   - Make sure all Python dependencies are installed: `pip install -r requirements.txt`
   - If you encounter errors with `sentence-transformers`, `timm`, or `huggingface-hub`, run: `./fix-all-dependencies.sh`
   - Check for circular imports in the Python modules

2. **Frontend Build Failures**:
   - Ensure you're using Node.js 16 or higher
   - Delete `node_modules` and run `npm install` again
   - Check for syntax errors in React components

3. **CORS Issues**:
   - The backend is configured to allow all origins for development
   - For production, update the CORS middleware in `api.py` with specific origins

4. **API Connection Issues**:
   - Ensure the backend is running on port 8000
   - Check the API base URL configuration in `frontend-react/vite.config.js`

### Port Conflicts

If you need to change the default ports:

- **Backend**: Modify the port in `api.py` (line 554)
- **Frontend**: Modify the port in `frontend-react/vite.config.js`

## Architecture Overview

### Backend Architecture

- **FastAPI**: Modern, fast web framework for building APIs
- **PDF Processing**: Handles document upload and text extraction
- **Content Generation**: Creates educational content from documents
- **Test Generation**: Creates tests from educational content
- **Test Evaluation**: Evaluates student submissions
- **Progress Tracking**: Tracks student progress and generates learning paths

### Frontend Architecture

- **React 18**: Modern React with hooks and functional components
- **React Router**: Client-side routing
- **Vite**: Fast build tool and development server
- **Bootstrap 5**: UI framework for responsive design
- **Axios**: HTTP client for API communication

## Data Flow

1. **Document Upload**: User uploads PDF → Backend processes and stores → Updates UI
2. **Content Generation**: User selects document → Backend generates content → Displays in UI
3. **Test Creation**: User selects content → Backend creates test → Shows in UI
4. **Student Progress**: System tracks interactions → Generates insights → Displays analytics

## Security Considerations

- The API uses an API key for authentication (configured in `.env`)
- For production, implement proper user authentication and authorization
- Use HTTPS in production environments
- Validate and sanitize all user inputs

## Performance Considerations

- The backend uses lazy initialization for expensive operations
- The frontend implements proper loading states and error handling
- Consider implementing caching for frequently accessed data
- For large-scale deployments, consider using a database instead of pickle files

## Contributing

When making changes to the codebase:

1. Follow the existing code style and structure
2. Test both backend and frontend after changes
3. Update documentation as needed
4. Ensure all features work end-to-end

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the API documentation at `/docs`
3. Check browser console for frontend errors
4. Check server logs for backend errors