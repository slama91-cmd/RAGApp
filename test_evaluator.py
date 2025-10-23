import os
import logging
import pickle
import uuid
import re
from typing import List, Dict, Optional, Tuple, Union
import json
from datetime import datetime
import pandas as pd
from collections import Counter

from test_generator import get_test_generator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class TestEvaluator:
    """
    A class to evaluate student test submissions and provide feedback.
    Handles automated scoring, answer analysis, and personalized feedback generation.
    """
    
    def __init__(self):
        """Initialize the test evaluator."""
        self.evaluations_file = "test_evaluations.pkl"
        self.student_answers_file = "student_answers.pkl"
        self.students_file = "students.pkl"
        
        # Load or initialize evaluations storage
        if os.path.exists(self.evaluations_file):
            with open(self.evaluations_file, "rb") as f:
                self.evaluations = pickle.load(f)
            logger.info(f"Loaded existing evaluations with {len(self.evaluations)} items")
        else:
            self.evaluations = {}
            logger.info("Initialized new evaluations storage")
            
        # Load or initialize student answers storage
        if os.path.exists(self.student_answers_file):
            with open(self.student_answers_file, "rb") as f:
                self.student_answers = pickle.load(f)
            logger.info(f"Loaded existing student answers with {len(self.student_answers)} items")
        else:
            self.student_answers = {}
            logger.info("Initialized new student answers storage")
            
        # Load or initialize students storage
        if os.path.exists(self.students_file):
            with open(self.students_file, "rb") as f:
                self.students = pickle.load(f)
            logger.info(f"Loaded existing students with {len(self.students)} items")
        else:
            self.students = {}
            logger.info("Initialized new students storage")
    
    def register_student(self, name: str, email: str) -> Dict:
        """
        Register a new student in the system.
        
        Args:
            name: Student's name
            email: Student's email
            
        Returns:
            Student dictionary
        """
        try:
            # Check if student with this email already exists
            for student_id, student in self.students.items():
                if student.get("email") == email:
                    logger.warning(f"Student with email {email} already exists")
                    return student
            
            # Create new student
            student_id = str(uuid.uuid4())
            student = {
                "id": student_id,
                "name": name,
                "email": email,
                "registered_date": str(datetime.now()),
                "test_history": []
            }
            
            # Store the student
            self.students[student_id] = student
            
            # Save to file
            with open(self.students_file, "wb") as f:
                pickle.dump(self.students, f)
            
            logger.info(f"Registered new student {name} with ID {student_id}")
            return student
        except Exception as e:
            logger.error(f"Error registering student {name}: {str(e)}")
            return {}
    
    def submit_test_answers(self, student_id: str, test_id: str, answers: Dict) -> Dict:
        """
        Submit student answers for a test.
        
        Args:
            student_id: ID of the student
            test_id: ID of the test
            answers: Dictionary of question_id -> answer
            
        Returns:
            Submission confirmation dictionary
        """
        try:
            # Check if student exists
            if student_id not in self.students:
                logger.error(f"Student {student_id} not found")
                return {}
            
            # Get the test
            test = get_test_generator().get_test(test_id)
            if not test:
                logger.error(f"Test {test_id} not found")
                return {}
            
            # Create submission record
            submission_id = str(uuid.uuid4())
            submission = {
                "id": submission_id,
                "student_id": student_id,
                "test_id": test_id,
                "answers": answers,
                "submitted_at": str(datetime.now()),
                "status": "submitted"
            }
            
            # Store the submission
            self.student_answers[submission_id] = submission
            
            # Update student's test history
            self.students[student_id]["test_history"].append({
                "test_id": test_id,
                "submission_id": submission_id,
                "submitted_at": str(datetime.now()),
                "status": "submitted"
            })
            
            # Save to files
            with open(self.student_answers_file, "wb") as f:
                pickle.dump(self.student_answers, f)
            with open(self.students_file, "wb") as f:
                pickle.dump(self.students, f)
            
            logger.info(f"Student {student_id} submitted answers for test {test_id}")
            return submission
        except Exception as e:
            logger.error(f"Error submitting test answers: {str(e)}")
            return {}
    
    def evaluate_submission(self, submission_id: str) -> Dict:
        """
        Evaluate a student's test submission.
        
        Args:
            submission_id: ID of the submission
            
        Returns:
            Evaluation results dictionary
        """
        try:
            # Get the submission
            submission = self.student_answers.get(submission_id)
            if not submission:
                logger.error(f"Submission {submission_id} not found")
                return {}
            
            # Get the test
            test_id = submission.get("test_id")
            test = get_test_generator().get_test(test_id)
            if not test:
                logger.error(f"Test {test_id} not found")
                return {}
            
            # Get the student
            student_id = submission.get("student_id")
            student = self.students.get(student_id)
            if not student:
                logger.error(f"Student {student_id} not found")
                return {}
            
            # Get the answers
            student_answers = submission.get("answers", {})
            
            # Evaluate each answer
            results = {
                "submission_id": submission_id,
                "student_id": student_id,
                "test_id": test_id,
                "evaluated_at": str(datetime.now()),
                "question_results": [],
                "total_score": 0,
                "max_score": test.get("total_points", 0),
                "percentage": 0,
                "feedback": ""
            }
            
            # Process each question
            for question in test.get("questions", []):
                question_id = question.get("id")
                student_answer = student_answers.get(question_id)
                
                # Evaluate the answer
                question_result = self._evaluate_question_answer(question, student_answer)
                results["question_results"].append(question_result)
                results["total_score"] += question_result.get("score", 0)
            
            # Calculate percentage
            if results["max_score"] > 0:
                results["percentage"] = (results["total_score"] / results["max_score"]) * 100
            
            # Generate overall feedback
            results["feedback"] = self._generate_overall_feedback(results, test, student)
            
            # Store the evaluation
            evaluation_id = str(uuid.uuid4())
            evaluation = {
                "id": evaluation_id,
                **results
            }
            self.evaluations[evaluation_id] = evaluation
            
            # Update submission status
            submission["status"] = "evaluated"
            submission["evaluation_id"] = evaluation_id
            
            # Update student's test history
            for history_item in self.students[student_id]["test_history"]:
                if history_item.get("submission_id") == submission_id:
                    history_item["status"] = "evaluated"
                    history_item["evaluation_id"] = evaluation_id
                    history_item["score"] = results["total_score"]
                    history_item["percentage"] = results["percentage"]
                    break
            
            # Save to files
            with open(self.evaluations_file, "wb") as f:
                pickle.dump(self.evaluations, f)
            with open(self.student_answers_file, "wb") as f:
                pickle.dump(self.student_answers, f)
            with open(self.students_file, "wb") as f:
                pickle.dump(self.students, f)
            
            logger.info(f"Evaluated submission {submission_id} for student {student_id}")
            return evaluation
        except Exception as e:
            logger.error(f"Error evaluating submission {submission_id}: {str(e)}")
            return {}
    
    def _evaluate_question_answer(self, question: Dict, student_answer: Union[str, int, None]) -> Dict:
        """
        Evaluate a student's answer to a specific question.
        
        Args:
            question: Question dictionary
            student_answer: Student's answer
            
        Returns:
            Question evaluation result dictionary
        """
        try:
            question_type = question.get("type")
            question_id = question.get("id")
            max_points = question.get("max_points", 1)
            
            result = {
                "question_id": question_id,
                "question_type": question_type,
                "student_answer": student_answer,
                "score": 0,
                "max_points": max_points,
                "is_correct": False,
                "feedback": ""
            }
            
            if question_type == "multiple_choice":
                # For multiple choice, check if the selected option matches the correct answer
                correct_answer = question.get("correct_answer")
                if student_answer == correct_answer:
                    result["score"] = max_points
                    result["is_correct"] = True
                    result["feedback"] = "Correct! Well done."
                else:
                    result["score"] = 0
                    result["is_correct"] = False
                    result["feedback"] = f"Incorrect. The correct answer is option {correct_answer + 1}."
            
            elif question_type == "short_answer":
                # For short answer, evaluate based on keywords and similarity
                sample_answer = question.get("sample_answer", "")
                keywords = question.get("keywords", [])
                
                if student_answer and isinstance(student_answer, str):
                    # Calculate score based on keyword presence
                    student_words = re.findall(r'\b\w+\b', student_answer.lower())
                    keyword_matches = sum(1 for keyword in keywords if keyword in student_words)
                    
                    # Calculate score as a percentage of keywords matched
                    if keywords:
                        keyword_percentage = keyword_matches / len(keywords)
                        result["score"] = int(max_points * keyword_percentage)
                    else:
                        # If no keywords, use a simple length-based heuristic
                        if len(student_answer) > 20:
                            result["score"] = max_points // 2
                        else:
                            result["score"] = max_points // 4
                    
                    # Determine if it's correct (at least 80% of max points)
                    result["is_correct"] = result["score"] >= (max_points * 0.8)
                    
                    # Generate feedback
                    if result["is_correct"]:
                        result["feedback"] = "Good answer! You've covered the key points."
                    else:
                        missing_keywords = [k for k in keywords if k not in student_words]
                        if missing_keywords:
                            result["feedback"] = f"Your answer is missing some key points. Consider including: {', '.join(missing_keywords[:3])}"
                        else:
                            result["feedback"] = "Your answer could be more detailed. Try to expand on the key concepts."
                else:
                    result["score"] = 0
                    result["is_correct"] = False
                    result["feedback"] = "No answer provided."
            
            elif question_type == "essay":
                # For essay questions, use a simple heuristic based on length and keyword presence
                if student_answer and isinstance(student_answer, str):
                    # Get keywords from the question topic
                    topic = question.get("topic", "")
                    topic_keywords = re.findall(r'\b\w+\b', topic.lower())
                    
                    # Calculate score based on length and keyword presence
                    word_count = len(student_answer.split())
                    keyword_matches = sum(1 for keyword in topic_keywords if keyword in student_answer.lower())
                    
                    # Base score on length (up to a point)
                    length_score = min(max_points * 0.5, max_points * (word_count / 300))
                    
                    # Add score for keyword matches
                    keyword_score = 0
                    if topic_keywords:
                        keyword_score = max_points * 0.5 * (keyword_matches / len(topic_keywords))
                    
                    result["score"] = int(length_score + keyword_score)
                    
                    # Determine if it's correct (at least 60% of max points for essays)
                    result["is_correct"] = result["score"] >= (max_points * 0.6)
                    
                    # Generate feedback
                    if result["is_correct"]:
                        result["feedback"] = "Good essay! You've addressed the topic well."
                    else:
                        if word_count < 200:
                            result["feedback"] = "Your essay is too short. Try to expand on your points with more detail and examples."
                        else:
                            result["feedback"] = "Your essay could be improved by focusing more directly on the topic and including relevant examples."
                else:
                    result["score"] = 0
                    result["is_correct"] = False
                    result["feedback"] = "No essay provided."
            
            else:
                # Unknown question type
                result["score"] = 0
                result["is_correct"] = False
                result["feedback"] = "Unable to evaluate this question type."
            
            return result
        except Exception as e:
            logger.error(f"Error evaluating question answer: {str(e)}")
            return {
                "question_id": question.get("id", "unknown"),
                "question_type": question.get("type", "unknown"),
                "student_answer": student_answer,
                "score": 0,
                "max_points": question.get("max_points", 1),
                "is_correct": False,
                "feedback": "Error evaluating answer."
            }
    
    def _generate_overall_feedback(self, evaluation: Dict, test: Dict, student: Dict) -> str:
        """
        Generate overall feedback for a test evaluation.
        
        Args:
            evaluation: Evaluation results dictionary
            test: Test dictionary
            student: Student dictionary
            
        Returns:
            Overall feedback string
        """
        try:
            percentage = evaluation.get("percentage", 0)
            student_name = student.get("name", "Student")
            
            # Generate feedback based on performance
            if percentage >= 90:
                feedback = f"Excellent work, {student_name}! You've demonstrated a strong understanding of the material with a score of {percentage:.1f}%. "
                feedback += "Keep up the great work and consider exploring more advanced topics."
            elif percentage >= 80:
                feedback = f"Great job, {student_name}! You scored {percentage:.1f}%, showing a good grasp of the material. "
                feedback += "Review the questions you missed to solidify your understanding."
            elif percentage >= 70:
                feedback = f"Good effort, {student_name}! You scored {percentage:.1f}%, which shows you understand many of the key concepts. "
                feedback += "Focus on the areas where you lost points to improve your knowledge."
            elif percentage >= 60:
                feedback = f"You're on the right track, {student_name}, with a score of {percentage:.1f}%. "
                feedback += "Spend more time studying the material, particularly the topics where you struggled."
            else:
                feedback = f"You scored {percentage:.1f}%, {student_name}. This suggests you need to review the material more thoroughly. "
                feedback += "Consider going back to the source material and seeking additional help on challenging topics."
            
            # Add specific recommendations based on question types
            question_results = evaluation.get("question_results", [])
            
            # Analyze performance by question type
            type_performance = {}
            for result in question_results:
                q_type = result.get("question_type", "unknown")
                if q_type not in type_performance:
                    type_performance[q_type] = {"correct": 0, "total": 0}
                
                type_performance[q_type]["total"] += 1
                if result.get("is_correct", False):
                    type_performance[q_type]["correct"] += 1
            
            # Add recommendations based on question type performance
            for q_type, perf in type_performance.items():
                if perf["total"] > 0:
                    accuracy = perf["correct"] / perf["total"]
                    if accuracy < 0.5:
                        if q_type == "multiple_choice":
                            feedback += " You struggled with multiple choice questions. Try to read each option carefully and eliminate obviously wrong answers."
                        elif q_type == "short_answer":
                            feedback += " Your short answers need improvement. Focus on including key terms and being more concise."
                        elif q_type == "essay":
                            feedback += " Your essay answers need work. Practice structuring your essays with clear introductions, body paragraphs, and conclusions."
            
            return feedback
        except Exception as e:
            logger.error(f"Error generating overall feedback: {str(e)}")
            return "Unable to generate feedback at this time."
    
    def get_evaluation(self, evaluation_id: str) -> Optional[Dict]:
        """
        Retrieve an evaluation by ID.
        
        Args:
            evaluation_id: ID of the evaluation
            
        Returns:
            Evaluation dictionary or None if not found
        """
        return self.evaluations.get(evaluation_id)
    
    def get_student(self, student_id: str) -> Optional[Dict]:
        """
        Retrieve a student by ID.
        
        Args:
            student_id: ID of the student
            
        Returns:
            Student dictionary or None if not found
        """
        return self.students.get(student_id)
    
    def get_student_evaluations(self, student_id: str) -> List[Dict]:
        """
        Get all evaluations for a specific student.
        
        Args:
            student_id: ID of the student
            
        Returns:
            List of evaluation dictionaries
        """
        return [
            evaluation for evaluation in self.evaluations.values()
            if evaluation.get("student_id") == student_id
        ]
    
    def get_student_progress(self, student_id: str) -> Dict:
        """
        Get progress summary for a specific student.
        
        Args:
            student_id: ID of the student
            
        Returns:
            Student progress dictionary
        """
        try:
            # Get student information
            student = self.students.get(student_id)
            if not student:
                return {}
            
            # Get all evaluations for the student
            evaluations = self.get_student_evaluations(student_id)
            
            # Calculate statistics
            total_tests = len(evaluations)
            if total_tests == 0:
                return {
                    "student_id": student_id,
                    "student_name": student.get("name", ""),
                    "total_tests": 0,
                    "average_score": 0,
                    "highest_score": 0,
                    "lowest_score": 0,
                    "recent_performance": []
                }
            
            scores = [eval.get("percentage", 0) for eval in evaluations]
            average_score = sum(scores) / len(scores)
            highest_score = max(scores)
            lowest_score = min(scores)
            
            # Get recent performance (last 5 tests)
            recent_evaluations = sorted(
                evaluations, 
                key=lambda x: x.get("evaluated_at", ""), 
                reverse=True
            )[:5]
            
            recent_performance = [
                {
                    "test_id": eval.get("test_id", ""),
                    "evaluation_id": eval.get("id", ""),
                    "date": eval.get("evaluated_at", ""),
                    "score": eval.get("percentage", 0)
                }
                for eval in recent_evaluations
            ]
            
            # Analyze performance by question type
            type_performance = {}
            for evaluation in evaluations:
                for result in evaluation.get("question_results", []):
                    q_type = result.get("question_type", "unknown")
                    if q_type not in type_performance:
                        type_performance[q_type] = {"correct": 0, "total": 0}
                    
                    type_performance[q_type]["total"] += 1
                    if result.get("is_correct", False):
                        type_performance[q_type]["correct"] += 1
            
            # Calculate accuracy by question type
            type_accuracy = {}
            for q_type, perf in type_performance.items():
                if perf["total"] > 0:
                    type_accuracy[q_type] = perf["correct"] / perf["total"]
            
            return {
                "student_id": student_id,
                "student_name": student.get("name", ""),
                "total_tests": total_tests,
                "average_score": average_score,
                "highest_score": highest_score,
                "lowest_score": lowest_score,
                "recent_performance": recent_performance,
                "performance_by_question_type": type_accuracy
            }
        except Exception as e:
            logger.error(f"Error getting student progress for {student_id}: {str(e)}")
            return {}
    
    def generate_learning_recommendations(self, student_id: str) -> Dict:
        """
        Generate personalized learning recommendations for a student.
        
        Args:
            student_id: ID of the student
            
        Returns:
            Learning recommendations dictionary
        """
        try:
            # Get student progress
            progress = self.get_student_progress(student_id)
            if not progress:
                return {}
            
            # Get student information
            student = self.students.get(student_id)
            if not student:
                return {}
            
            student_name = student.get("name", "Student")
            average_score = progress.get("average_score", 0)
            
            # Generate recommendations based on performance
            recommendations = {
                "student_id": student_id,
                "student_name": student_name,
                "generated_at": str(datetime.now()),
                "overall_recommendations": [],
                "topic_recommendations": [],
                "study_strategies": []
            }
            
            # Overall recommendations based on average score
            if average_score >= 90:
                recommendations["overall_recommendations"].append(
                    "You're performing excellently! Consider exploring more advanced topics or taking on challenging projects."
                )
            elif average_score >= 80:
                recommendations["overall_recommendations"].append(
                    "You're doing well! Focus on reviewing your mistakes to solidify your understanding."
                )
            elif average_score >= 70:
                recommendations["overall_recommendations"].append(
                    "You have a good foundation but need to strengthen your knowledge in some areas."
                )
            elif average_score >= 60:
                recommendations["overall_recommendations"].append(
                    "You need to spend more time with the material. Consider forming a study group or seeking additional help."
                )
            else:
                recommendations["overall_recommendations"].append(
                    "You're struggling with the material. It's important to go back to basics and build a stronger foundation."
                )
            
            # Analyze performance by question type
            type_performance = progress.get("performance_by_question_type", {})
            
            for q_type, accuracy in type_performance.items():
                if accuracy < 0.6:
                    if q_type == "multiple_choice":
                        recommendations["topic_recommendations"].append(
                            "Practice multiple choice questions by eliminating wrong answers and looking for key terms."
                        )
                    elif q_type == "short_answer":
                        recommendations["topic_recommendations"].append(
                            "Work on your short answer responses by focusing on key terms and being more concise."
                        )
                    elif q_type == "essay":
                        recommendations["topic_recommendations"].append(
                            "Improve your essay writing by practicing structure and including specific examples."
                        )
            
            # General study strategies
            recommendations["study_strategies"].append(
                "Review your incorrect answers to understand where you went wrong."
            )
            recommendations["study_strategies"].append(
                "Create a study schedule and stick to it, reviewing material regularly."
            )
            recommendations["study_strategies"].append(
                "Try teaching the concepts to someone else, which can reveal gaps in your understanding."
            )
            
            if average_score < 70:
                recommendations["study_strategies"].append(
                    "Consider seeking additional help from a teacher, tutor, or study group."
                )
            
            return recommendations
        except Exception as e:
            logger.error(f"Error generating learning recommendations for {student_id}: {str(e)}")
            return {}

# Initialize the test evaluator (lazy initialization to avoid import issues)
test_evaluator = None

def get_test_evaluator():
    global test_evaluator
    if test_evaluator is None:
        test_evaluator = TestEvaluator()
    return test_evaluator