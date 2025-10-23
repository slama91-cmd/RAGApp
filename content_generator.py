import os
import logging
import pickle
import uuid
from typing import List, Dict, Optional, Tuple
import json
from datetime import datetime
import pandas as pd

from pdf_processor import get_pdf_processor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class ContentGenerator:
    """
    A class to generate educational content from processed PDF documents.
    Creates structured learning materials, lesson plans, and study guides.
    """
    
    def __init__(self):
        """Initialize the content generator."""
        self.content_file = "generated_content.pkl"
        self.lesson_plans_file = "lesson_plans.pkl"
        
        # Load or initialize content storage
        if os.path.exists(self.content_file):
            with open(self.content_file, "rb") as f:
                self.generated_content = pickle.load(f)
            logger.info(f"Loaded existing content storage with {len(self.generated_content)} items")
        else:
            self.generated_content = {}
            logger.info("Initialized new content storage")
            
        # Load or initialize lesson plans storage
        if os.path.exists(self.lesson_plans_file):
            with open(self.lesson_plans_file, "rb") as f:
                self.lesson_plans = pickle.load(f)
            logger.info(f"Loaded existing lesson plans with {len(self.lesson_plans)} items")
        else:
            self.lesson_plans = {}
            logger.info("Initialized new lesson plans storage")
    
    def extract_key_topics(self, document_id: str, num_topics: int = 5) -> List[str]:
        """
        Extract key topics from a document using the processed chunks.
        
        Args:
            document_id: ID of the document
            num_topics: Number of key topics to extract
            
        Returns:
            List of key topics
        """
        try:
            # Get all chunks for the document
            pdf_processor_instance = get_pdf_processor()
            document_chunks = [
                chunk_data["text"] for chunk_data in pdf_processor_instance.chunk_map.values()
                if chunk_data["document_id"] == document_id
            ]
            
            if not document_chunks:
                logger.warning(f"No chunks found for document {document_id}")
                return []
            
            # Combine all chunks for analysis
            full_text = " ".join(document_chunks)
            
            # Simple topic extraction based on frequency and importance
            # In a production system, you would use more sophisticated NLP techniques
            words = full_text.lower().split()
            word_freq = {}
            
            # Filter out common words
            stop_words = {
                "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
                "of", "with", "by", "is", "are", "was", "were", "be", "been", "being",
                "have", "has", "had", "do", "does", "did", "will", "would", "could", "should"
            }
            
            for word in words:
                if len(word) > 3 and word not in stop_words:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Sort by frequency and get top topics
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            topics = [word for word, freq in sorted_words[:num_topics]]
            
            logger.info(f"Extracted {len(topics)} topics from document {document_id}")
            return topics
        except Exception as e:
            logger.error(f"Error extracting topics from document {document_id}: {str(e)}")
            return []
    
    def generate_content_outline(self, document_id: str, topics: List[str]) -> Dict:
        """
        Generate a structured outline for educational content based on topics.
        
        Args:
            document_id: ID of the document
            topics: List of key topics
            
        Returns:
            Content outline dictionary
        """
        try:
            pdf_processor_instance = get_pdf_processor()
            outline = {
                "title": f"Study Guide: {pdf_processor_instance.documents[document_id]['filename']}",
                "document_id": document_id,
                "introduction": {
                    "overview": "This study guide covers the key concepts and topics from the source material.",
                    "objectives": [
                        "Understand the fundamental concepts presented in the material",
                        "Apply the knowledge to solve problems",
                        "Analyze and evaluate complex scenarios related to the topics"
                    ]
                },
                "sections": []
            }
            
            # Create a section for each topic
            for i, topic in enumerate(topics):
                # Find relevant chunks for this topic
                relevant_chunks = self._find_relevant_chunks(document_id, topic)
                
                section = {
                    "id": i + 1,
                    "title": topic.capitalize(),
                    "key_points": self._extract_key_points(relevant_chunks),
                    "content_summary": self._generate_section_summary(relevant_chunks),
                    "study_questions": self._generate_study_questions(topic, relevant_chunks)
                }
                
                outline["sections"].append(section)
            
            # Add conclusion
            outline["conclusion"] = {
                "summary": "This guide has covered the main topics from the source material.",
                "next_steps": [
                    "Review the key points for each section",
                    "Complete the practice questions",
                    "Apply the concepts to real-world scenarios"
                ]
            }
            
            logger.info(f"Generated content outline for document {document_id}")
            return outline
        except Exception as e:
            logger.error(f"Error generating content outline for document {document_id}: {str(e)}")
            return {}
    
    def _find_relevant_chunks(self, document_id: str, topic: str, max_chunks: int = 5) -> List[str]:
        """
        Find chunks most relevant to a specific topic.
        
        Args:
            document_id: ID of the document
            topic: Topic to search for
            max_chunks: Maximum number of chunks to return
            
        Returns:
            List of relevant chunk texts
        """
        try:
            # Search for chunks containing the topic
            pdf_processor_instance = get_pdf_processor()
            search_results = pdf_processor_instance.search_similar_content(topic, k=max_chunks * 2)
            
            # Filter results to only include chunks from the specified document
            relevant_chunks = [
                result["text"] for result in search_results
                if result["document_id"] == document_id
            ][:max_chunks]
            
            return relevant_chunks
        except Exception as e:
            logger.error(f"Error finding relevant chunks for topic {topic}: {str(e)}")
            return []
    
    def _extract_key_points(self, chunks: List[str]) -> List[str]:
        """
        Extract key points from a list of text chunks.
        
        Args:
            chunks: List of text chunks
            
        Returns:
            List of key points
        """
        try:
            # Simple key point extraction based on sentence importance
            # In a production system, you would use more sophisticated NLP techniques
            all_text = " ".join(chunks)
            sentences = all_text.split(". ")
            
            # Filter sentences that might contain key points
            key_points = []
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 20 and len(sentence) < 200:
                    # Simple heuristic: sentences with certain keywords might be key points
                    if any(keyword in sentence.lower() for keyword in 
                           ["important", "key", "essential", "critical", "main", "primary", "fundamental"]):
                        key_points.append(sentence)
            
            # If we didn't find enough key points with keywords, just take some sentences
            if len(key_points) < 3:
                key_points = [s.strip() for s in sentences if len(s.strip()) > 20][:5]
            
            logger.info(f"Extracted {len(key_points)} key points")
            return key_points
        except Exception as e:
            logger.error(f"Error extracting key points: {str(e)}")
            return []
    
    def _generate_section_summary(self, chunks: List[str]) -> str:
        """
        Generate a summary for a section based on relevant chunks.
        
        Args:
            chunks: List of text chunks
            
        Returns:
            Section summary
        """
        try:
            # Simple summary generation
            # In a production system, you would use an LLM for better summaries
            all_text = " ".join(chunks)
            
            # Extract the first few sentences as a simple summary
            sentences = all_text.split(". ")
            summary = ". ".join(sentences[:3]) + "."
            
            logger.info(f"Generated section summary of length {len(summary)}")
            return summary
        except Exception as e:
            logger.error(f"Error generating section summary: {str(e)}")
            return ""
    
    def _generate_study_questions(self, topic: str, chunks: List[str]) -> List[Dict]:
        """
        Generate study questions for a topic based on relevant chunks.
        
        Args:
            topic: The topic for questions
            chunks: List of text chunks
            
        Returns:
            List of study question dictionaries
        """
        try:
            questions = []
            
            # Simple question generation templates
            templates = [
                f"What is the importance of {topic} in this context?",
                f"Explain the key concepts related to {topic}.",
                f"How does {topic} relate to other concepts in the material?",
                f"What are the main applications of {topic}?",
                f"Describe the process or methodology involving {topic}."
            ]
            
            # Create questions from templates
            for i, template in enumerate(templates):
                questions.append({
                    "id": i + 1,
                    "question": template,
                    "type": "short_answer",
                    "difficulty": "medium"
                })
            
            logger.info(f"Generated {len(questions)} study questions for topic {topic}")
            return questions
        except Exception as e:
            logger.error(f"Error generating study questions for topic {topic}: {str(e)}")
            return []
    
    def generate_lesson_plan(self, document_id: str, duration_days: int = 7) -> Dict:
        """
        Generate a lesson plan for studying a document over a specified duration.
        
        Args:
            document_id: ID of the document
            duration_days: Number of days for the lesson plan
            
        Returns:
            Lesson plan dictionary
        """
        try:
            # Extract key topics
            topics = self.extract_key_topics(document_id)
            
            if not topics:
                logger.warning(f"No topics found for document {document_id}")
                return {}
            
            # Create lesson plan
            pdf_processor_instance = get_pdf_processor()
            lesson_plan = {
                "id": str(uuid.uuid4()),
                "document_id": document_id,
                "title": f"Lesson Plan: {pdf_processor_instance.documents[document_id]['filename']}",
                "duration_days": duration_days,
                "created_date": str(datetime.now()),
                "daily_schedule": []
            }
            
            # Distribute topics across days
            topics_per_day = max(1, len(topics) // duration_days)
            
            for day in range(duration_days):
                start_idx = day * topics_per_day
                end_idx = start_idx + topics_per_day
                day_topics = topics[start_idx:end_idx]
                
                # If we're on the last day, include any remaining topics
                if day == duration_days - 1:
                    day_topics = topics[start_idx:]
                
                daily_schedule = {
                    "day": day + 1,
                    "topics": day_topics,
                    "activities": [
                        "Read the relevant sections from the source material",
                        "Review the key points for each topic",
                        "Answer the study questions",
                        "Take notes on important concepts"
                    ],
                    "estimated_time": "2-3 hours"
                }
                
                lesson_plan["daily_schedule"].append(daily_schedule)
            
            # Add assessment day
            if duration_days > 1:
                lesson_plan["daily_schedule"].append({
                    "day": duration_days + 1,
                    "topics": ["Review and Assessment"],
                    "activities": [
                        "Review all topics covered",
                        "Complete practice test",
                        "Review incorrect answers",
                        "Focus on areas that need improvement"
                    ],
                    "estimated_time": "3-4 hours"
                })
                lesson_plan["duration_days"] += 1
            
            logger.info(f"Generated lesson plan for document {document_id} with {duration_days} days")
            return lesson_plan
        except Exception as e:
            logger.error(f"Error generating lesson plan for document {document_id}: {str(e)}")
            return {}
    
    def create_educational_content(self, document_id: str, include_lesson_plan: bool = True) -> Dict:
        """
        Create complete educational content from a document.
        
        Args:
            document_id: ID of the document
            include_lesson_plan: Whether to include a lesson plan
            
        Returns:
            Complete educational content dictionary
        """
        try:
            # Check if document exists
            pdf_processor_instance = get_pdf_processor()
            if document_id not in pdf_processor_instance.documents:
                logger.error(f"Document {document_id} not found")
                return {}
            
            # Extract key topics
            topics = self.extract_key_topics(document_id)
            
            if not topics:
                logger.error(f"No topics found for document {document_id}")
                return {}
            
            # Generate content outline
            content_outline = self.generate_content_outline(document_id, topics)
            
            # Create educational content
            content_id = str(uuid.uuid4())
            educational_content = {
                "id": content_id,
                "document_id": document_id,
                "title": content_outline["title"],
                "created_date": str(datetime.now()),
                "content_outline": content_outline,
                "topics": topics
            }
            
            # Add lesson plan if requested
            if include_lesson_plan:
                lesson_plan = self.generate_lesson_plan(document_id)
                educational_content["lesson_plan"] = lesson_plan
            
            # Store the content
            self.generated_content[content_id] = educational_content
            
            # Save to file
            with open(self.content_file, "wb") as f:
                pickle.dump(self.generated_content, f)
            
            # Store lesson plan separately if generated
            if include_lesson_plan and lesson_plan:
                self.lesson_plans[lesson_plan["id"]] = lesson_plan
                with open(self.lesson_plans_file, "wb") as f:
                    pickle.dump(self.lesson_plans, f)
            
            logger.info(f"Created educational content {content_id} for document {document_id}")
            return educational_content
        except Exception as e:
            logger.error(f"Error creating educational content for document {document_id}: {str(e)}")
            return {}
    
    def get_content(self, content_id: str) -> Optional[Dict]:
        """
        Retrieve educational content by ID.
        
        Args:
            content_id: ID of the content
            
        Returns:
            Educational content dictionary or None if not found
        """
        return self.generated_content.get(content_id)
    
    def get_all_content(self) -> List[Dict]:
        """
        Get all generated educational content.
        
        Returns:
            List of educational content dictionaries
        """
        return [
            {"content_id": content_id, **content}
            for content_id, content in self.generated_content.items()
        ]
    
    def get_lesson_plan(self, lesson_plan_id: str) -> Optional[Dict]:
        """
        Retrieve a lesson plan by ID.
        
        Args:
            lesson_plan_id: ID of the lesson plan
            
        Returns:
            Lesson plan dictionary or None if not found
        """
        return self.lesson_plans.get(lesson_plan_id)
    
    def get_all_lesson_plans(self) -> List[Dict]:
        """
        Get all generated lesson plans.
        
        Returns:
            List of lesson plan dictionaries
        """
        return [
            {"lesson_plan_id": lesson_plan_id, **lesson_plan}
            for lesson_plan_id, lesson_plan in self.lesson_plans.items()
        ]
    
    def delete_content(self, content_id: str) -> bool:
        """
        Delete educational content by ID.
        
        Args:
            content_id: ID of the content to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if content_id not in self.generated_content:
                logger.warning(f"Content {content_id} not found")
                return False
            
            # Get the content to check if it has an associated lesson plan
            content = self.generated_content[content_id]
            
            # Delete the content
            del self.generated_content[content_id]
            
            # Save updated content storage
            with open(self.content_file, "wb") as f:
                pickle.dump(self.generated_content, f)
            
            # If the content had a lesson plan, delete it too
            if "lesson_plan" in content and "id" in content["lesson_plan"]:
                lesson_plan_id = content["lesson_plan"]["id"]
                if lesson_plan_id in self.lesson_plans:
                    del self.lesson_plans[lesson_plan_id]
                    with open(self.lesson_plans_file, "wb") as f:
                        pickle.dump(self.lesson_plans, f)
            
            logger.info(f"Deleted content {content_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting content {content_id}: {str(e)}")
            return False

# Initialize the content generator (lazy initialization to avoid import issues)
content_generator = None

def get_content_generator():
    global content_generator
    if content_generator is None:
        content_generator = ContentGenerator()
    return content_generator