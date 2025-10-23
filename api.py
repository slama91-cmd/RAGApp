from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import os
import logging
import uvicorn

# Import our modules
from pdf_processor import get_pdf_processor
from content_generator import get_content_generator
from test_generator import get_test_generator
from test_evaluator import get_test_evaluator
from progress_tracker import get_progress_tracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Educational Mentorship Platform API",
    description="API for AI-powered educational mentorship platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For POC, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != os.getenv("EDU_API_KEY", "edu-api-key-1234"):
        raise HTTPException(
            status_code=403, detail="Could not validate credentials"
        )
    return api_key

# Pydantic models for request/response
class StudentRegistration(BaseModel):
    name: str
    email: str

class TestSubmission(BaseModel):
    student_id: str
    test_id: str
    answers: Dict[str, Any]

class ContentGenerationRequest(BaseModel):
    document_id: str
    include_lesson_plan: bool = True

class TestGenerationRequest(BaseModel):
    content_id: str
    num_questions: int = 10
    test_title: Optional[str] = None
    difficulty: str = "medium"

class LearningPathRequest(BaseModel):
    student_id: str
    content_ids: Optional[List[str]] = None

# Document Management Endpoints

@app.post("/documents/upload", dependencies=[Depends(get_api_key)])
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a PDF document.
    """
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        result = get_pdf_processor().process_pdf(file)
        return result
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{document_id}", dependencies=[Depends(get_api_key)])
async def get_document(document_id: str):
    """
    Get information about a processed document.
    """
    try:
        document = get_pdf_processor().get_document_info(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents", dependencies=[Depends(get_api_key)])
async def get_all_documents():
    """
    Get information about all processed documents.
    """
    try:
        documents = get_pdf_processor().get_all_documents()
        return {"documents": documents}
    except Exception as e:
        logger.error(f"Error getting documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{document_id}", dependencies=[Depends(get_api_key)])
async def delete_document(document_id: str):
    """
    Delete a document and its associated data.
    """
    try:
        success = get_pdf_processor().delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"status": "success", "message": "Document deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Content Generation Endpoints

@app.post("/content/generate", dependencies=[Depends(get_api_key)])
async def generate_content(request: ContentGenerationRequest):
    """
    Generate educational content from a document.
    """
    try:
        content = get_content_generator().create_educational_content(
            document_id=request.document_id,
            include_lesson_plan=request.include_lesson_plan
        )
        if not content:
            raise HTTPException(status_code=404, detail="Document not found or no content generated")
        return content
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/content/{content_id}", dependencies=[Depends(get_api_key)])
async def get_content(content_id: str):
    """
    Get educational content by ID.
    """
    try:
        content = get_content_generator().get_content(content_id)
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        return content
    except Exception as e:
        logger.error(f"Error getting content {content_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/content", dependencies=[Depends(get_api_key)])
async def get_all_content():
    """
    Get all generated educational content.
    """
    try:
        content_list = get_content_generator().get_all_content()
        return {"content": content_list}
    except Exception as e:
        logger.error(f"Error getting content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/content/{content_id}", dependencies=[Depends(get_api_key)])
async def delete_content(content_id: str):
    """
    Delete educational content.
    """
    try:
        success = get_content_generator().delete_content(content_id)
        if not success:
            raise HTTPException(status_code=404, detail="Content not found")
        return {"status": "success", "message": "Content deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting content {content_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Test Management Endpoints

@app.post("/tests/generate", dependencies=[Depends(get_api_key)])
async def generate_test(request: TestGenerationRequest):
    """
    Generate a test from educational content.
    """
    try:
        test = get_test_generator().create_test_from_content(
            content_id=request.content_id,
            num_questions=request.num_questions,
            test_title=request.test_title,
            difficulty=request.difficulty
        )
        if not test:
            raise HTTPException(status_code=404, detail="Content not found or no test generated")
        return test
    except Exception as e:
        logger.error(f"Error generating test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tests/{test_id}", dependencies=[Depends(get_api_key)])
async def get_test(test_id: str):
    """
    Get a test by ID.
    """
    try:
        test = get_test_generator().get_test(test_id)
        if not test:
            raise HTTPException(status_code=404, detail="Test not found")
        return test
    except Exception as e:
        logger.error(f"Error getting test {test_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tests", dependencies=[Depends(get_api_key)])
async def get_all_tests():
    """
    Get all generated tests.
    """
    try:
        tests = get_test_generator().get_all_tests()
        return {"tests": tests}
    except Exception as e:
        logger.error(f"Error getting tests: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/tests/{test_id}", dependencies=[Depends(get_api_key)])
async def delete_test(test_id: str):
    """
    Delete a test.
    """
    try:
        success = get_test_generator().delete_test(test_id)
        if not success:
            raise HTTPException(status_code=404, detail="Test not found")
        return {"status": "success", "message": "Test deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting test {test_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Student Management Endpoints

@app.post("/students/register", dependencies=[Depends(get_api_key)])
async def register_student(student: StudentRegistration):
    """
    Register a new student.
    """
    try:
        registered_student = get_test_evaluator().register_student(
            name=student.name,
            email=student.email
        )
        if not registered_student:
            raise HTTPException(status_code=400, detail="Failed to register student")
        return registered_student
    except Exception as e:
        logger.error(f"Error registering student: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/students/{student_id}", dependencies=[Depends(get_api_key)])
async def get_student(student_id: str):
    """
    Get student information.
    """
    try:
        student = get_test_evaluator().get_student(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return student
    except Exception as e:
        logger.error(f"Error getting student {student_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/students", dependencies=[Depends(get_api_key)])
async def get_all_students():
    """
    Get all registered students.
    """
    try:
        test_evaluator_instance = get_test_evaluator()
        students = list(test_evaluator_instance.students.values())
        return {"students": students}
    except Exception as e:
        logger.error(f"Error getting students: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Test Submission and Evaluation Endpoints

@app.post("/tests/submit", dependencies=[Depends(get_api_key)])
async def submit_test(submission: TestSubmission):
    """
    Submit student answers for a test.
    """
    try:
        result = get_test_evaluator().submit_test_answers(
            student_id=submission.student_id,
            test_id=submission.test_id,
            answers=submission.answers
        )
        if not result:
            raise HTTPException(status_code=400, detail="Failed to submit test")
        return result
    except Exception as e:
        logger.error(f"Error submitting test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluations/{submission_id}", dependencies=[Depends(get_api_key)])
async def evaluate_submission(submission_id: str):
    """
    Evaluate a student's test submission.
    """
    try:
        evaluation = get_test_evaluator().evaluate_submission(submission_id)
        if not evaluation:
            raise HTTPException(status_code=404, detail="Submission not found or evaluation failed")
        return evaluation
    except Exception as e:
        logger.error(f"Error evaluating submission {submission_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/evaluations/{evaluation_id}", dependencies=[Depends(get_api_key)])
async def get_evaluation(evaluation_id: str):
    """
    Get an evaluation by ID.
    """
    try:
        evaluation = get_test_evaluator().get_evaluation(evaluation_id)
        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        return evaluation
    except Exception as e:
        logger.error(f"Error getting evaluation {evaluation_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/students/{student_id}/evaluations", dependencies=[Depends(get_api_key)])
async def get_student_evaluations(student_id: str):
    """
    Get all evaluations for a specific student.
    """
    try:
        evaluations = get_test_evaluator().get_student_evaluations(student_id)
        return {"evaluations": evaluations}
    except Exception as e:
        logger.error(f"Error getting evaluations for student {student_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Progress Tracking Endpoints

@app.get("/students/{student_id}/progress", dependencies=[Depends(get_api_key)])
async def get_student_progress(student_id: str):
    """
    Get progress summary for a specific student.
    """
    try:
        progress = get_progress_tracker().get_student_progress_summary(student_id)
        if not progress:
            raise HTTPException(status_code=404, detail="Student not found or no progress data")
        return progress
    except Exception as e:
        logger.error(f"Error getting progress for student {student_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/students/{student_id}/progress", dependencies=[Depends(get_api_key)])
async def update_student_progress(
    student_id: str,
    content_id: Optional[str] = None,
    test_id: Optional[str] = None,
    evaluation_id: Optional[str] = None
):
    """
    Update student progress based on content interaction or test completion.
    """
    try:
        progress = get_progress_tracker().update_student_progress(
            student_id=student_id,
            content_id=content_id,
            test_id=test_id,
            evaluation_id=evaluation_id
        )
        if not progress:
            raise HTTPException(status_code=404, detail="Student not found")
        return progress
    except Exception as e:
        logger.error(f"Error updating progress for student {student_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/learning-paths/generate", dependencies=[Depends(get_api_key)])
async def generate_learning_path(request: LearningPathRequest):
    """
    Generate a personalized learning path for a student.
    """
    try:
        learning_path = get_progress_tracker().generate_learning_path(
            student_id=request.student_id,
            content_ids=request.content_ids
        )
        if not learning_path:
            raise HTTPException(status_code=404, detail="Student not found or no learning path generated")
        return learning_path
    except Exception as e:
        logger.error(f"Error generating learning path: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/students/{student_id}/learning-path", dependencies=[Depends(get_api_key)])
async def get_student_learning_path(student_id: str):
    """
    Get the active learning path for a student.
    """
    try:
        learning_path = get_progress_tracker().get_student_learning_path(student_id)
        if not learning_path:
            raise HTTPException(status_code=404, detail="No active learning path found for student")
        return learning_path
    except Exception as e:
        logger.error(f"Error getting learning path for student {student_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/learning-paths/{student_id}/milestones/{milestone_id}", dependencies=[Depends(get_api_key)])
async def update_milestone_completion(
    student_id: str,
    milestone_id: str,
    completed: bool = True
):
    """
    Update the completion status of a milestone in a student's learning path.
    """
    try:
        success = get_progress_tracker().update_milestone_completion(
            student_id=student_id,
            milestone_id=milestone_id,
            completed=completed
        )
        if not success:
            raise HTTPException(status_code=404, detail="Student, learning path, or milestone not found")
        return {"status": "success", "message": "Milestone updated successfully"}
    except Exception as e:
        logger.error(f"Error updating milestone {milestone_id} for student {student_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics and Insights Endpoints

@app.post("/analytics/generate", dependencies=[Depends(get_api_key)])
async def generate_analytics(student_id: Optional[str] = None):
    """
    Generate analytics data for student progress.
    """
    try:
        analytics = get_progress_tracker().generate_progress_analytics(student_id=student_id)
        if not analytics:
            raise HTTPException(status_code=400, detail="Failed to generate analytics")
        return analytics
    except Exception as e:
        logger.error(f"Error generating analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/{analytics_id}", dependencies=[Depends(get_api_key)])
async def get_analytics(analytics_id: str):
    """
    Get analytics by ID.
    """
    try:
        analytics = get_progress_tracker().get_analytics(analytics_id)
        if not analytics:
            raise HTTPException(status_code=404, detail="Analytics not found")
        return analytics
    except Exception as e:
        logger.error(f"Error getting analytics {analytics_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/students/{student_id}/analytics", dependencies=[Depends(get_api_key)])
async def get_student_analytics(student_id: str):
    """
    Get all analytics for a specific student.
    """
    try:
        analytics = get_progress_tracker().get_student_analytics(student_id)
        return {"analytics": analytics}
    except Exception as e:
        logger.error(f"Error getting analytics for student {student_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/students/{student_id}/recommendations", dependencies=[Depends(get_api_key)])
async def get_learning_recommendations(student_id: str):
    """
    Get personalized learning recommendations for a student.
    """
    try:
        recommendations = get_test_evaluator().generate_learning_recommendations(student_id)
        if not recommendations:
            raise HTTPException(status_code=404, detail="Student not found or no recommendations generated")
        return recommendations
    except Exception as e:
        logger.error(f"Error getting recommendations for student {student_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Search Endpoints

@app.post("/search", dependencies=[Depends(get_api_key)])
async def search_content(query: str, k: int = 5):
    """
    Search for content similar to the query.
    """
    try:
        results = get_pdf_processor().search_similar_content(query, k)
        return {"results": results}
    except Exception as e:
        logger.error(f"Error searching content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Health Check Endpoint

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy", "message": "Educational Mentorship Platform API is running"}

# Root endpoint

@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Educational Mentorship Platform API",
        "version": "1.0.0",
        "endpoints": {
            "documents": "/documents",
            "content": "/content",
            "tests": "/tests",
            "students": "/students",
            "evaluations": "/evaluations",
            "progress": "/progress",
            "learning-paths": "/learning-paths",
            "analytics": "/analytics",
            "search": "/search"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")