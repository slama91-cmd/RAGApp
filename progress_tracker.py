import os
import logging
import pickle
import uuid
from typing import List, Dict, Optional, Tuple, Union
import json
from datetime import datetime, timedelta
import pandas as pd
from collections import defaultdict, Counter

from test_evaluator import get_test_evaluator
from content_generator import get_content_generator
from test_generator import get_test_generator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class ProgressTracker:
    """
    A class to track student progress, generate analytics, and provide insights.
    Handles performance tracking, learning path recommendations, and progress visualization.
    """
    
    def __init__(self):
        """Initialize the progress tracker."""
        self.progress_data_file = "student_progress_data.pkl"
        self.learning_paths_file = "learning_paths.pkl"
        self.analytics_file = "progress_analytics.pkl"
        
        # Load or initialize progress data storage
        if os.path.exists(self.progress_data_file):
            with open(self.progress_data_file, "rb") as f:
                self.progress_data = pickle.load(f)
            logger.info(f"Loaded existing progress data with {len(self.progress_data)} items")
        else:
            self.progress_data = {}
            logger.info("Initialized new progress data storage")
            
        # Load or initialize learning paths storage
        if os.path.exists(self.learning_paths_file):
            with open(self.learning_paths_file, "rb") as f:
                self.learning_paths = pickle.load(f)
            logger.info(f"Loaded existing learning paths with {len(self.learning_paths)} items")
        else:
            self.learning_paths = {}
            logger.info("Initialized new learning paths storage")
            
        # Load or initialize analytics storage
        if os.path.exists(self.analytics_file):
            with open(self.analytics_file, "rb") as f:
                self.analytics = pickle.load(f)
            logger.info(f"Loaded existing analytics with {len(self.analytics)} items")
        else:
            self.analytics = {}
            logger.info("Initialized new analytics storage")
    
    def update_student_progress(self, student_id: str, content_id: str = None, test_id: str = None, 
                               evaluation_id: str = None) -> Dict:
        """
        Update student progress based on content interaction or test completion.
        
        Args:
            student_id: ID of the student
            content_id: Optional ID of the content being studied
            test_id: Optional ID of the test taken
            evaluation_id: Optional ID of the test evaluation
            
        Returns:
            Updated progress data dictionary
        """
        try:
            # Initialize progress data for student if not exists
            if student_id not in self.progress_data:
                self.progress_data[student_id] = {
                    "student_id": student_id,
                    "content_progress": {},
                    "test_history": [],
                    "strengths": [],
                    "weaknesses": [],
                    "last_updated": str(datetime.now()),
                    "learning_goals": []
                }
            
            # Update content progress
            if content_id:
                if content_id not in self.progress_data[student_id]["content_progress"]:
                    self.progress_data[student_id]["content_progress"][content_id] = {
                        "started_at": str(datetime.now()),
                        "completed": False,
                        "progress_percentage": 0
                    }
                
                # Update progress percentage (simplified for POC)
                current_progress = self.progress_data[student_id]["content_progress"][content_id]["progress_percentage"]
                new_progress = min(100, current_progress + 25)  # Increment by 25% for each interaction
                
                self.progress_data[student_id]["content_progress"][content_id]["progress_percentage"] = new_progress
                
                if new_progress >= 100:
                    self.progress_data[student_id]["content_progress"][content_id]["completed"] = True
                    self.progress_data[student_id]["content_progress"][content_id]["completed_at"] = str(datetime.now())
            
            # Update test history
            if test_id and evaluation_id:
                # Get evaluation details
                evaluation = get_test_evaluator().get_evaluation(evaluation_id)
                if evaluation:
                    test_record = {
                        "test_id": test_id,
                        "evaluation_id": evaluation_id,
                        "taken_at": evaluation.get("evaluated_at", str(datetime.now())),
                        "score": evaluation.get("percentage", 0),
                        "total_points": evaluation.get("total_score", 0),
                        "max_points": evaluation.get("max_score", 0)
                    }
                    
                    self.progress_data[student_id]["test_history"].append(test_record)
                    
                    # Update strengths and weaknesses based on question performance
                    self._update_strengths_weaknesses(student_id, evaluation)
            
            # Update last updated timestamp
            self.progress_data[student_id]["last_updated"] = str(datetime.now())
            
            # Save to file
            with open(self.progress_data_file, "wb") as f:
                pickle.dump(self.progress_data, f)
            
            logger.info(f"Updated progress for student {student_id}")
            return self.progress_data[student_id]
        except Exception as e:
            logger.error(f"Error updating progress for student {student_id}: {str(e)}")
            return {}
    
    def _update_strengths_weaknesses(self, student_id: str, evaluation: Dict):
        """
        Update student's strengths and weaknesses based on test evaluation.
        
        Args:
            student_id: ID of the student
            evaluation: Test evaluation dictionary
        """
        try:
            # Get question results
            question_results = evaluation.get("question_results", [])
            
            # Group results by topic
            topic_performance = defaultdict(lambda: {"correct": 0, "total": 0})
            
            for result in question_results:
                # Get question details
                question_id = result.get("question_id")
                question = get_test_generator().get_question(question_id)
                
                if question:
                    topic = question.get("topic", "unknown")
                    topic_performance[topic]["total"] += 1
                    
                    if result.get("is_correct", False):
                        topic_performance[topic]["correct"] += 1
            
            # Calculate accuracy for each topic
            topic_accuracy = {}
            for topic, perf in topic_performance.items():
                if perf["total"] > 0:
                    accuracy = perf["correct"] / perf["total"]
                    topic_accuracy[topic] = accuracy
            
            # Update strengths (topics with accuracy >= 80%)
            strengths = [topic for topic, accuracy in topic_accuracy.items() if accuracy >= 0.8]
            
            # Update weaknesses (topics with accuracy < 60%)
            weaknesses = [topic for topic, accuracy in topic_accuracy.items() if accuracy < 0.6]
            
            # Update progress data
            current_strengths = self.progress_data[student_id].get("strengths", [])
            current_weaknesses = self.progress_data[student_id].get("weaknesses", [])
            
            # Add new strengths and weaknesses
            for strength in strengths:
                if strength not in current_strengths:
                    current_strengths.append(strength)
            
            for weakness in weaknesses:
                if weakness not in current_weaknesses:
                    current_weaknesses.append(weakness)
            
            self.progress_data[student_id]["strengths"] = current_strengths
            self.progress_data[student_id]["weaknesses"] = current_weaknesses
            
            logger.info(f"Updated strengths and weaknesses for student {student_id}")
        except Exception as e:
            logger.error(f"Error updating strengths and weaknesses for student {student_id}: {str(e)}")
    
    def get_student_progress_summary(self, student_id: str) -> Dict:
        """
        Get a comprehensive summary of a student's progress.
        
        Args:
            student_id: ID of the student
            
        Returns:
            Student progress summary dictionary
        """
        try:
            # Get progress data
            progress = self.progress_data.get(student_id, {})
            if not progress:
                return {}
            
            # Get student information
            student = get_test_evaluator().students.get(student_id, {})
            student_name = student.get("name", "Unknown Student")
            
            # Calculate content progress statistics
            content_progress = progress.get("content_progress", {})
            total_content = len(content_progress)
            completed_content = sum(1 for cp in content_progress.values() if cp.get("completed", False))
            content_completion_rate = (completed_content / total_content * 100) if total_content > 0 else 0
            
            # Calculate test performance statistics
            test_history = progress.get("test_history", [])
            total_tests = len(test_history)
            
            if total_tests > 0:
                test_scores = [test.get("score", 0) for test in test_history]
                average_test_score = sum(test_scores) / len(test_scores)
                highest_test_score = max(test_scores)
                lowest_test_score = min(test_scores)
                
                # Calculate recent performance trend (last 3 tests)
                recent_tests = sorted(test_history, key=lambda x: x.get("taken_at", ""), reverse=True)[:3]
                recent_scores = [test.get("score", 0) for test in recent_tests]
                recent_average = sum(recent_scores) / len(recent_scores) if recent_scores else 0
                
                # Determine trend
                if len(recent_scores) >= 2:
                    if recent_scores[0] > recent_scores[-1]:
                        performance_trend = "improving"
                    elif recent_scores[0] < recent_scores[-1]:
                        performance_trend = "declining"
                    else:
                        performance_trend = "stable"
                else:
                    performance_trend = "insufficient_data"
            else:
                average_test_score = 0
                highest_test_score = 0
                lowest_test_score = 0
                recent_average = 0
                performance_trend = "no_tests"
            
            # Get strengths and weaknesses
            strengths = progress.get("strengths", [])
            weaknesses = progress.get("weaknesses", [])
            
            # Create summary
            summary = {
                "student_id": student_id,
                "student_name": student_name,
                "content_progress": {
                    "total_content": total_content,
                    "completed_content": completed_content,
                    "completion_rate": content_completion_rate
                },
                "test_performance": {
                    "total_tests": total_tests,
                    "average_score": average_test_score,
                    "highest_score": highest_test_score,
                    "lowest_score": lowest_test_score,
                    "recent_average": recent_average,
                    "performance_trend": performance_trend
                },
                "strengths": strengths,
                "weaknesses": weaknesses,
                "last_updated": progress.get("last_updated", "")
            }
            
            return summary
        except Exception as e:
            logger.error(f"Error getting progress summary for student {student_id}: {str(e)}")
            return {}
    
    def generate_learning_path(self, student_id: str, content_ids: List[str] = None) -> Dict:
        """
        Generate a personalized learning path for a student.
        
        Args:
            student_id: ID of the student
            content_ids: Optional list of content IDs to include in the path
            
        Returns:
            Learning path dictionary
        """
        try:
            # Get student progress
            progress = self.progress_data.get(student_id, {})
            if not progress:
                return {}
            
            # Get student information
            student = get_test_evaluator().students.get(student_id, {})
            student_name = student.get("name", "Unknown Student")
            
            # Get weaknesses to focus on
            weaknesses = progress.get("weaknesses", [])
            
            # If no content IDs provided, get all available content
            if not content_ids:
                content_generator_instance = get_content_generator()
                content_ids = list(content_generator_instance.generated_content.keys())
            
            # Filter content based on weaknesses
            recommended_content = []
            content_generator_instance = get_content_generator()
            for content_id in content_ids:
                content = content_generator_instance.get_content(content_id)
                if content:
                    content_topics = content.get("topics", [])
                    
                    # Check if content addresses any weaknesses
                    relevance_score = sum(1 for topic in content_topics if topic in weaknesses)
                    
                    if relevance_score > 0 or not weaknesses:
                        recommended_content.append({
                            "content_id": content_id,
                            "title": content.get("title", ""),
                            "topics": content_topics,
                            "relevance_score": relevance_score,
                            "priority": "high" if relevance_score > 0 else "medium"
                        })
            
            # Sort by relevance score
            recommended_content.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            # Create learning path
            learning_path_id = str(uuid.uuid4())
            learning_path = {
                "id": learning_path_id,
                "student_id": student_id,
                "student_name": student_name,
                "created_at": str(datetime.now()),
                "title": f"Personalized Learning Path for {student_name}",
                "description": f"This learning path is designed to address your specific needs and help you improve in areas where you're struggling.",
                "content_items": recommended_content,
                "estimated_completion_time": self._estimate_completion_time(recommended_content),
                "milestones": self._create_milestones(recommended_content),
                "status": "active"
            }
            
            # Store the learning path
            self.learning_paths[learning_path_id] = learning_path
            
            # Save to file
            with open(self.learning_paths_file, "wb") as f:
                pickle.dump(self.learning_paths, f)
            
            logger.info(f"Generated learning path {learning_path_id} for student {student_id}")
            return learning_path
        except Exception as e:
            logger.error(f"Error generating learning path for student {student_id}: {str(e)}")
            return {}
    
    def _estimate_completion_time(self, content_items: List[Dict]) -> str:
        """
        Estimate the time required to complete a set of content items.
        
        Args:
            content_items: List of content item dictionaries
            
        Returns:
            Estimated completion time as a string
        """
        try:
            # Simple estimation: 2 hours per content item
            total_hours = len(content_items) * 2
            
            if total_hours < 24:
                return f"{total_hours} hours"
            else:
                days = total_hours // 24
                remaining_hours = total_hours % 24
                return f"{days} days and {remaining_hours} hours"
        except Exception as e:
            logger.error(f"Error estimating completion time: {str(e)}")
            return "Unknown"
    
    def _create_milestones(self, content_items: List[Dict]) -> List[Dict]:
        """
        Create milestones for a learning path.
        
        Args:
            content_items: List of content item dictionaries
            
        Returns:
            List of milestone dictionaries
        """
        try:
            milestones = []
            
            # Create a milestone for every 3 content items
            for i in range(0, len(content_items), 3):
                milestone_content = content_items[i:i+3]
                milestone_number = (i // 3) + 1
                
                milestone = {
                    "id": str(uuid.uuid4()),
                    "number": milestone_number,
                    "title": f"Milestone {milestone_number}",
                    "description": f"Complete the next set of learning materials",
                    "content_ids": [item["content_id"] for item in milestone_content],
                    "completed": False
                }
                
                milestones.append(milestone)
            
            # Add a final milestone
            if milestones:
                final_milestone = {
                    "id": str(uuid.uuid4()),
                    "number": len(milestones) + 1,
                    "title": "Final Assessment",
                    "description": "Complete a comprehensive test to evaluate your understanding",
                    "content_ids": [],
                    "completed": False,
                    "is_assessment": True
                }
                milestones.append(final_milestone)
            
            return milestones
        except Exception as e:
            logger.error(f"Error creating milestones: {str(e)}")
            return []
    
    def get_student_learning_path(self, student_id: str) -> Optional[Dict]:
        """
        Get the active learning path for a student.
        
        Args:
            student_id: ID of the student
            
        Returns:
            Learning path dictionary or None if not found
        """
        try:
            # Find the active learning path for the student
            for path_id, path in self.learning_paths.items():
                if path.get("student_id") == student_id and path.get("status") == "active":
                    return path
            
            return None
        except Exception as e:
            logger.error(f"Error getting learning path for student {student_id}: {str(e)}")
            return None
    
    def update_milestone_completion(self, student_id: str, milestone_id: str, completed: bool = True) -> bool:
        """
        Update the completion status of a milestone in a student's learning path.
        
        Args:
            student_id: ID of the student
            milestone_id: ID of the milestone
            completed: Whether the milestone is completed
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the student's learning path
            learning_path = self.get_student_learning_path(student_id)
            if not learning_path:
                logger.warning(f"No active learning path found for student {student_id}")
                return False
            
            # Find and update the milestone
            milestones = learning_path.get("milestones", [])
            milestone_found = False
            
            for milestone in milestones:
                if milestone.get("id") == milestone_id:
                    milestone["completed"] = completed
                    if completed:
                        milestone["completed_at"] = str(datetime.now())
                    milestone_found = True
                    break
            
            if not milestone_found:
                logger.warning(f"Milestone {milestone_id} not found in learning path for student {student_id}")
                return False
            
            # Check if all milestones are completed
            all_completed = all(m.get("completed", False) for m in milestones)
            
            # Update learning path status if all milestones are completed
            if all_completed:
                learning_path["status"] = "completed"
                learning_path["completed_at"] = str(datetime.now())
            
            # Save to file
            with open(self.learning_paths_file, "wb") as f:
                pickle.dump(self.learning_paths, f)
            
            logger.info(f"Updated milestone {milestone_id} for student {student_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating milestone {milestone_id} for student {student_id}: {str(e)}")
            return False
    
    def generate_progress_analytics(self, student_id: str = None) -> Dict:
        """
        Generate analytics data for student progress.
        
        Args:
            student_id: Optional ID of a specific student. If None, generate analytics for all students.
            
        Returns:
            Analytics data dictionary
        """
        try:
            analytics_id = str(uuid.uuid4())
            generated_at = str(datetime.now())
            
            if student_id:
                # Generate analytics for a specific student
                progress_summary = self.get_student_progress_summary(student_id)
                if not progress_summary:
                    return {}
                
                # Get test history for trend analysis
                progress_data = self.progress_data.get(student_id, {})
                test_history = progress_data.get("test_history", [])
                
                # Sort tests by date
                sorted_tests = sorted(test_history, key=lambda x: x.get("taken_at", ""))
                
                # Create trend data
                trend_data = [
                    {
                        "date": test.get("taken_at", ""),
                        "score": test.get("score", 0)
                    }
                    for test in sorted_tests
                ]
                
                analytics = {
                    "id": analytics_id,
                    "type": "student",
                    "student_id": student_id,
                    "generated_at": generated_at,
                    "progress_summary": progress_summary,
                    "trend_data": trend_data,
                    "insights": self._generate_student_insights(student_id)
                }
            else:
                # Generate analytics for all students
                test_evaluator_instance = get_test_evaluator()
                all_students = list(test_evaluator_instance.students.keys())
                
                # Calculate overall statistics
                total_students = len(all_students)
                active_students = len([s for s in all_students if s in self.progress_data])
                
                # Calculate average performance metrics
                all_test_scores = []
                all_content_completion_rates = []
                
                for s_id in all_students:
                    progress = self.progress_data.get(s_id, {})
                    test_history = progress.get("test_history", [])
                    
                    # Add test scores
                    for test in test_history:
                        all_test_scores.append(test.get("score", 0))
                    
                    # Calculate content completion rate
                    content_progress = progress.get("content_progress", {})
                    total_content = len(content_progress)
                    completed_content = sum(1 for cp in content_progress.values() if cp.get("completed", False))
                    completion_rate = (completed_content / total_content * 100) if total_content > 0 else 0
                    all_content_completion_rates.append(completion_rate)
                
                # Calculate averages
                avg_test_score = sum(all_test_scores) / len(all_test_scores) if all_test_scores else 0
                avg_completion_rate = sum(all_content_completion_rates) / len(all_content_completion_rates) if all_content_completion_rates else 0
                
                # Create performance distribution
                score_distribution = self._create_distribution(all_test_scores)
                completion_distribution = self._create_distribution(all_content_completion_rates)
                
                analytics = {
                    "id": analytics_id,
                    "type": "overall",
                    "generated_at": generated_at,
                    "summary": {
                        "total_students": total_students,
                        "active_students": active_students,
                        "average_test_score": avg_test_score,
                        "average_completion_rate": avg_completion_rate
                    },
                    "score_distribution": score_distribution,
                    "completion_distribution": completion_distribution,
                    "insights": self._generate_overall_insights()
                }
            
            # Store analytics
            self.analytics[analytics_id] = analytics
            
            # Save to file
            with open(self.analytics_file, "wb") as f:
                pickle.dump(self.analytics, f)
            
            logger.info(f"Generated progress analytics {analytics_id}")
            return analytics
        except Exception as e:
            logger.error(f"Error generating progress analytics: {str(e)}")
            return {}
    
    def _create_distribution(self, values: List[float]) -> Dict:
        """
        Create a distribution of values into ranges.
        
        Args:
            values: List of numeric values
            
        Returns:
            Distribution dictionary
        """
        try:
            if not values:
                return {}
            
            # Define ranges
            ranges = [
                (0, 20),
                (20, 40),
                (40, 60),
                (60, 80),
                (80, 100)
            ]
            
            distribution = {}
            
            for range_min, range_max in ranges:
                count = sum(1 for value in values if range_min <= value < range_max)
                distribution[f"{range_min}-{range_max}"] = count
            
            return distribution
        except Exception as e:
            logger.error(f"Error creating distribution: {str(e)}")
            return {}
    
    def _generate_student_insights(self, student_id: str) -> List[str]:
        """
        Generate insights for a specific student.
        
        Args:
            student_id: ID of the student
            
        Returns:
            List of insight strings
        """
        try:
            insights = []
            
            # Get progress data
            progress = self.progress_data.get(student_id, {})
            if not progress:
                return ["No progress data available for this student."]
            
            # Get test history
            test_history = progress.get("test_history", [])
            
            if len(test_history) >= 3:
                # Analyze recent performance
                recent_tests = sorted(test_history, key=lambda x: x.get("taken_at", ""), reverse=True)[:3]
                recent_scores = [test.get("score", 0) for test in recent_tests]
                
                # Check for improving trend
                if recent_scores[0] > recent_scores[-1] + 10:
                    insights.append("Student shows significant improvement in recent tests.")
                elif recent_scores[0] < recent_scores[-1] - 10:
                    insights.append("Student's performance has declined in recent tests.")
                else:
                    insights.append("Student's performance has been consistent in recent tests.")
            else:
                insights.append("Student has taken fewer than 3 tests. More data needed for trend analysis.")
            
            # Analyze strengths and weaknesses
            strengths = progress.get("strengths", [])
            weaknesses = progress.get("weaknesses", [])
            
            if strengths:
                insights.append(f"Student demonstrates strength in: {', '.join(strengths[:3])}.")
            
            if weaknesses:
                insights.append(f"Student should focus on improving: {', '.join(weaknesses[:3])}.")
            
            # Analyze content progress
            content_progress = progress.get("content_progress", {})
            total_content = len(content_progress)
            completed_content = sum(1 for cp in content_progress.values() if cp.get("completed", False))
            
            if total_content > 0:
                completion_rate = (completed_content / total_content) * 100
                
                if completion_rate >= 80:
                    insights.append("Student has completed most of the assigned content.")
                elif completion_rate >= 50:
                    insights.append("Student is making good progress through the content.")
                else:
                    insights.append("Student should spend more time engaging with the learning materials.")
            
            return insights
        except Exception as e:
            logger.error(f"Error generating insights for student {student_id}: {str(e)}")
            return ["Unable to generate insights at this time."]
    
    def _generate_overall_insights(self) -> List[str]:
        """
        Generate overall insights for all students.
        
        Returns:
            List of insight strings
        """
        try:
            insights = []
            
            # Get all students
            test_evaluator_instance = get_test_evaluator()
            all_students = list(test_evaluator_instance.students.keys())
            
            if not all_students:
                return ["No students registered in the system."]
            
            # Calculate engagement metrics
            active_students = len([s for s in all_students if s in self.progress_data])
            engagement_rate = (active_students / len(all_students)) * 100
            
            if engagement_rate >= 80:
                insights.append("High student engagement with the platform.")
            elif engagement_rate >= 50:
                insights.append("Moderate student engagement. Consider strategies to increase participation.")
            else:
                insights.append("Low student engagement. Immediate action needed to improve participation.")
            
            # Calculate average performance metrics
            all_test_scores = []
            all_content_completion_rates = []
            
            for s_id in all_students:
                progress = self.progress_data.get(s_id, {})
                test_history = progress.get("test_history", [])
                
                # Add test scores
                for test in test_history:
                    all_test_scores.append(test.get("score", 0))
                
                # Calculate content completion rate
                content_progress = progress.get("content_progress", {})
                total_content = len(content_progress)
                completed_content = sum(1 for cp in content_progress.values() if cp.get("completed", False))
                completion_rate = (completed_content / total_content * 100) if total_content > 0 else 0
                all_content_completion_rates.append(completion_rate)
            
            # Analyze test performance
            if all_test_scores:
                avg_test_score = sum(all_test_scores) / len(all_test_scores)
                
                if avg_test_score >= 80:
                    insights.append("Students are performing well on assessments overall.")
                elif avg_test_score >= 60:
                    insights.append("Student performance is average. Room for improvement.")
                else:
                    insights.append("Student performance is below average. Consider reviewing teaching methods.")
            
            # Analyze content completion
            if all_content_completion_rates:
                avg_completion_rate = sum(all_content_completion_rates) / len(all_content_completion_rates)
                
                if avg_completion_rate >= 80:
                    insights.append("Students are completing most of the learning materials.")
                elif avg_completion_rate >= 50:
                    insights.append("Moderate content completion rates. Consider making content more engaging.")
                else:
                    insights.append("Low content completion rates. Review content relevance and accessibility.")
            
            return insights
        except Exception as e:
            logger.error(f"Error generating overall insights: {str(e)}")
            return ["Unable to generate insights at this time."]
    
    def get_analytics(self, analytics_id: str) -> Optional[Dict]:
        """
        Retrieve analytics by ID.
        
        Args:
            analytics_id: ID of the analytics
            
        Returns:
            Analytics dictionary or None if not found
        """
        return self.analytics.get(analytics_id)
    
    def get_student_analytics(self, student_id: str) -> List[Dict]:
        """
        Get all analytics for a specific student.
        
        Args:
            student_id: ID of the student
            
        Returns:
            List of analytics dictionaries
        """
        return [
            analytics for analytics in self.analytics.values()
            if analytics.get("student_id") == student_id
        ]

# Initialize the progress tracker (lazy initialization to avoid import issues)
progress_tracker = None

def get_progress_tracker():
    global progress_tracker
    if progress_tracker is None:
        progress_tracker = ProgressTracker()
    return progress_tracker