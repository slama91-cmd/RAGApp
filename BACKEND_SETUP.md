# Backend Setup and Running Instructions

This guide will help you set up and run the Python backend for the EduMentor AI platform.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation Steps

### 1. Install Python Dependencies

Navigate to the project root directory and install the required Python packages:

```bash
pip install -r requirements.txt
```

This will install all the necessary packages including:
- FastAPI for the web framework
- Uvicorn for the ASGI server
- FAISS for vector similarity search
- PyPDF2 for PDF processing
- Sentence transformers for text embeddings
- And other required libraries

### 2. Set Up Environment Variables (Optional)

The backend uses an API key for authentication. By default, it uses `"edu-api-key-1234"`. If you want to change this, you can set it as an environment variable:

```bash
export EDU_API_KEY="your-custom-api-key"
```

Or create a `.env` file in the root directory:

```
EDU_API_KEY=your-custom-api-key
```

## Running the Backend

### Option 1: Direct Python Execution

You can run the backend directly using Python:

```bash
python api.py
```

This will start the FastAPI server on `http://localhost:8000`.

### Option 2: Using Uvicorn

For better performance, you can use Uvicorn directly:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` flag enables auto-reloading when you make changes to the code, which is useful for development.

### Option 3: Using Gunicorn (Production)

For production deployment, you can use Gunicorn with Uvicorn workers:

```bash
pip install gunicorn
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

This runs the app with 4 worker processes for better performance.

## API Documentation

Once the backend is running, you can access:

- **Interactive API Documentation**: `http://localhost:8000/docs`
- **Alternative API Documentation**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

These provide a complete overview of all available endpoints, their parameters, and response formats.

## API Endpoints

The backend provides the following main endpoints:

### Document Management
- `POST /documents/upload` - Upload and process a PDF document
- `GET /documents` - Get all processed documents
- `GET /documents/{document_id}` - Get a specific document
- `DELETE /documents/{document_id}` - Delete a document

### Content Generation
- `POST /content/generate` - Generate educational content from a document
- `GET /content` - Get all generated content
- `GET /content/{content_id}` - Get specific content
- `DELETE /content/{content_id}` - Delete content

### Test Management
- `POST /tests/generate` - Generate a test from content
- `GET /tests` - Get all tests
- `GET /tests/{test_id}` - Get a specific test
- `DELETE /tests/{test_id}` - Delete a test

### Student Management
- `POST /students/register` - Register a new student
- `GET /students` - Get all students
- `GET /students/{student_id}` - Get a specific student

### Progress Tracking
- `GET /students/{student_id}/progress` - Get student progress
- `POST /learning-paths/generate` - Generate learning path
- `GET /students/{student_id}/learning-path` - Get student learning path

### Test Evaluation
- `POST /tests/submit` - Submit test answers
- `POST /evaluations/{submission_id}` - Evaluate submission
- `GET /students/{student_id}/recommendations` - Get learning recommendations

### Health Check
- `GET /health` - Health check endpoint
- `GET /` - Root endpoint with API information

## Authentication

All API endpoints (except health check and root) require an API key passed in the `X-API-Key` header:

```
X-API-Key: edu-api-key-1234
```

## Running Both Frontend and Backend

To run the complete application:

1. **Terminal 1 - Backend**:
   ```bash
   python api.py
   ```

2. **Terminal 2 - Frontend**:
   ```bash
   cd frontend-react
   npm install
   npm run dev
   ```

The frontend will be available at `http://localhost:3000` and will automatically connect to the backend at `http://localhost:8000`.

## Troubleshooting

### Port Already in Use

If you get an error that the port is already in use:

1. Find the process using the port:
   ```bash
   lsof -i :8000
   ```

2. Kill the process:
   ```bash
   kill -9 <PID>
   ```

### Module Import Errors

If you encounter import errors:

1. Make sure you're in the correct directory
2. Install all dependencies: `pip install -r requirements.txt`
3. Check that you're using Python 3.8 or higher

### CORS Issues

If you encounter CORS errors when connecting from the frontend:

1. The backend is configured to allow all origins (`allow_origins=["*"]`)
2. Make sure the backend is running on port 8000
3. Check that the frontend is configured to proxy requests to the backend

## Production Deployment

For production deployment, consider:

1. Using a production WSGI server like Gunicorn
2. Setting up a reverse proxy like Nginx
3. Using environment variables for configuration
4. Setting up proper logging and monitoring
5. Using HTTPS instead of HTTP
6. Implementing proper authentication and authorization

## Performance Considerations

The backend uses FAISS for efficient similarity search and is optimized for handling educational content. For large-scale deployments:

1. Consider using a GPU for faster embeddings
2. Implement caching for frequently accessed content
3. Use a database for persistent storage instead of in-memory storage
4. Set up proper indexing for faster search