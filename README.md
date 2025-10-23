# Educational Mentorship Platform

An AI-powered educational mentorship platform that processes PDF documents to generate educational content, create tests, evaluate student responses, and provide personalized feedback.

## Features

- **Document Processing**: Upload and process PDF documents for educational content
- **Content Generation**: Automatically generate structured educational content from documents
- **Test Creation**: Create various types of questions (multiple choice, short answer, essay) from content
- **Student Evaluation**: Automated test correction and scoring
- **Progress Tracking**: Monitor student progress and performance analytics
- **Personalized Feedback**: Generate learning recommendations based on performance
- **Learning Paths**: Create personalized learning plans for students

## Architecture

The platform consists of the following components:

1. **Backend API** (FastAPI)
   - Document processing endpoints
   - Content generation endpoints
   - Test management endpoints
   - Student progress tracking endpoints
   - Analytics and insights endpoints

2. **Core Modules**
   - `pdf_processor.py`: Handles PDF text extraction, chunking, and vector embedding
   - `content_generator.py`: Generates educational content and lesson plans
   - `test_generator.py`: Creates various types of assessment questions
   - `test_evaluator.py`: Evaluates student responses and provides feedback
   - `progress_tracker.py`: Tracks student progress and generates analytics

3. **Frontend Interface**
   - Simple web interface built with HTML, CSS, and JavaScript
   - Bootstrap for responsive design
   - Interactive dashboard and management tools

4. **Vector Database**
   - FAISS for efficient similarity search
   - Sentence transformers for text embeddings

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Educational-Mentorship-Platform
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download spaCy model:
   ```bash
   python -m spacy download en_core_web_sm
   ```

## Usage

### Starting the Backend API

1. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. Start the API server:
   ```bash
   python api.py
   ```

   The API will be available at `http://localhost:8000`

3. Access the API documentation at `http://localhost:8000/docs`

### Using the Frontend Interface

1. Open `frontend/index.html` in a web browser
2. The interface provides the following sections:
   - **Dashboard**: Overview of platform statistics and recent activity
   - **Documents**: Upload and manage PDF documents
   - **Content**: Generate and view educational content
   - **Tests**: Create and manage assessments
   - **Progress**: Track student progress and generate learning paths

### API Usage Examples

#### Upload a Document

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "X-API-Key: edu-api-key-1234" \
  -F "file=@example.pdf"
```

#### Generate Content

```bash
curl -X POST "http://localhost:8000/content/generate" \
  -H "X-API-Key: edu-api-key-1234" \
  -H "Content-Type: application/json" \
  -d '{"document_id": "doc123", "include_lesson_plan": true}'
```

#### Create a Test

```bash
curl -X POST "http://localhost:8000/tests/generate" \
  -H "X-API-Key: edu-api-key-1234" \
  -H "Content-Type: application/json" \
  -d '{"content_id": "content123", "num_questions": 10, "difficulty": "medium"}'
```

#### Register a Student

```bash
curl -X POST "http://localhost:8000/students/register" \
  -H "X-API-Key: edu-api-key-1234" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'
```

## Configuration

### Environment Variables

- `EDU_API_KEY`: API key for authentication (default: "edu-api-key-1234")
- `FAISS_API_KEY`: API key for FAISS service (default: "1234a")

### Customization

- Adjust chunk size and overlap in `pdf_processor.py`
- Modify content generation templates in `content_generator.py`
- Customize test question types in `test_generator.py`
- Change evaluation criteria in `test_evaluator.py`

## Development

### Project Structure

```
Educational-Mentorship-Platform/
├── api.py                    # Main FastAPI application
├── pdf_processor.py          # PDF processing module
├── content_generator.py      # Content generation module
├── test_generator.py         # Test generation module
├── test_evaluator.py         # Test evaluation module
├── progress_tracker.py       # Progress tracking module
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── architecture_design.md    # System architecture documentation
├── README.md                 # This file
└── frontend/                 # Frontend interface
    ├── index.html           # Main HTML file
    ├── styles.css           # CSS styles
    └── app.js               # JavaScript functionality
```

### Adding New Features

1. **New Question Types**: Extend `test_generator.py` with new question generation methods
2. **Additional Analytics**: Add new analytics functions in `progress_tracker.py`
3. **Enhanced Content Types**: Modify `content_generator.py` to support new content formats
4. **API Endpoints**: Add new endpoints in `api.py` following the existing pattern

### Testing

Run the test suite:
```bash
python -m pytest tests/
```

## Limitations and Future Enhancements

### Current Limitations

- Simple text extraction from PDFs (no complex formatting or images)
- Basic content generation without advanced NLP models
- Limited question types and evaluation methods
- Simple frontend interface without advanced features

### Future Enhancements

- Integration with advanced LLMs for content generation
- Support for more document formats (DOCX, PPT, etc.)
- Advanced question types with automatic grading
- Real-time collaboration features
- Mobile application
- Integration with learning management systems (LMS)
- Advanced analytics and reporting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues, please create an issue in the GitHub repository.