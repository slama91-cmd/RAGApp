import os
import logging
import pickle
import uuid
import random
from typing import List, Dict, Optional, Tuple, Union
import json
from datetime import datetime
import pandas as pd

from pdf_processor import get_pdf_processor
from content_generator import get_content_generator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class TestGenerator:
    """
    A class to generate tests and assessments from educational content.
    Creates various types of questions including multiple choice, short answer, and essay questions.
    """
    
    def __init__(self):
        """Initialize the test generator."""
        self.tests_file = "generated_tests.pkl"
        self.questions_file = "test_questions.pkl"
        
        # Load or initialize tests storage
        if os.path.exists(self.tests_file):
            with open(self.tests_file, "rb") as f:
                self.generated_tests = pickle.load(f)
            logger.info(f"Loaded existing tests storage with {len(self.generated_tests)} items")
        else:
            self.generated_tests = {}
            logger.info("Initialized new tests storage")
            
        # Load or initialize questions storage
        if os.path.exists(self.questions_file):
            with open(self.questions_file, "rb") as f:
                self.test_questions = pickle.load(f)
            logger.info(f"Loaded existing test questions with {len(self.test_questions)} items")
        else:
            self.test_questions = {}
            logger.info("Initialized new test questions storage")
    
    def generate_multiple_choice_question(self, topic: str, context: str, difficulty: str = "medium") -> Dict:
        """
        Generate a multiple choice question for a given topic and context.
        
        Args:
            topic: The topic for the question
            context: Context text from the content
            difficulty: Difficulty level (easy, medium, hard)
            
        Returns:
            Multiple choice question dictionary
        """
        try:
            # Extract key information from context
            sentences = context.split(". ")
            if len(sentences) < 2:
                return {}
            
            # Select a sentence that might contain a key fact
            key_sentence = random.choice([s for s in sentences if len(s) > 20 and len(s) < 100])
            
            # Create question based on the key sentence
            question_templates = [
                f"According to the text, which of the following is true about {topic}?",
                f"Based on the information provided, what can be inferred about {topic}?",
                f"The text suggests that {topic} is primarily associated with:",
                f"Which statement best describes the role of {topic} as presented in the text?",
                f"What is the main characteristic of {topic} mentioned in the text?"
            ]
            
            question_text = random.choice(question_templates)
            
            # Generate correct answer based on the key sentence
            correct_answer = key_sentence.strip()
            
            # Generate distractors (wrong answers)
            distractors = []
            for _ in range(3):
                # Create variations of the correct answer or related but incorrect statements
                if random.random() < 0.5:
                    # Modify the correct answer
                    words = correct_answer.split()
                    if len(words) > 5:
                        # Remove or replace a key word
                        modified = words.copy()
                        idx = random.randint(1, len(words) - 2)
                        modified[idx] = "NOT " + modified[idx] if random.random() < 0.5 else "different"
                        distractors.append(" ".join(modified))
                else:
                    # Use a different sentence as a distractor
                    other_sentence = random.choice([s for s in sentences if s != key_sentence and len(s) > 20])
                    distractors.append(other_sentence.strip())
            
            # Ensure we have 3 distractors
            while len(distractors) < 3:
                distractors.append(f"This is not related to {topic}")
            
            # Combine correct answer and distractors
            options = [correct_answer] + distractors[:3]
            random.shuffle(options)
            
            # Find the index of the correct answer
            correct_index = options.index(correct_answer)
            
            # Create the question dictionary
            question = {
                "id": str(uuid.uuid4()),
                "type": "multiple_choice",
                "topic": topic,
                "difficulty": difficulty,
                "question_text": question_text,
                "options": options,
                "correct_answer": correct_index,
                "explanation": f"The correct answer is based on the information provided in the text about {topic}."
            }
            
            logger.info(f"Generated multiple choice question for topic {topic}")
            return question
        except Exception as e:
            logger.error(f"Error generating multiple choice question for topic {topic}: {str(e)}")
            return {}
    
    def generate_short_answer_question(self, topic: str, context: str, difficulty: str = "medium") -> Dict:
        """
        Generate a short answer question for a given topic and context.
        
        Args:
            topic: The topic for the question
            context: Context text from the content
            difficulty: Difficulty level (easy, medium, hard)
            
        Returns:
            Short answer question dictionary
        """
        try:
            # Extract key information from context
            sentences = context.split(". ")
            if len(sentences) < 2:
                return {}
            
            # Select a sentence that might contain a key fact
            key_sentence = random.choice([s for s in sentences if len(s) > 20 and len(s) < 100])
            
            # Create question based on the key sentence
            question_templates = [
                f"Explain the concept of {topic} as described in the text.",
                f"What are the key features of {topic} mentioned in the text?",
                f"Describe the role of {topic} according to the information provided.",
                f"How does the text define {topic}?",
                f"What is the significance of {topic} in the context of the material?"
            ]
            
            question_text = random.choice(question_templates)
            
            # Create a sample answer based on the key sentence
            sample_answer = key_sentence.strip()
            
            # Create the question dictionary
            question = {
                "id": str(uuid.uuid4()),
                "type": "short_answer",
                "topic": topic,
                "difficulty": difficulty,
                "question_text": question_text,
                "sample_answer": sample_answer,
                "keywords": self._extract_keywords(sample_answer),
                "max_points": 5
            }
            
            logger.info(f"Generated short answer question for topic {topic}")
            return question
        except Exception as e:
            logger.error(f"Error generating short answer question for topic {topic}: {str(e)}")
            return {}
    
    def generate_essay_question(self, topic: str, context: str, difficulty: str = "hard") -> Dict:
        """
        Generate an essay question for a given topic and context.
        
        Args:
            topic: The topic for the question
            context: Context text from the content
            difficulty: Difficulty level (easy, medium, hard)
            
        Returns:
            Essay question dictionary
        """
        try:
            # Create question based on the topic
            question_templates = [
                f"Discuss the importance of {topic} in the broader context of the subject matter.",
                f"Analyze the various aspects of {topic} presented in the text and evaluate their significance.",
                f"Compare and contrast different perspectives on {topic} as implied by the material.",
                f"Critically evaluate the role of {topic} based on the information provided.",
                f"Explain how {topic} relates to other concepts discussed in the material and provide examples."
            ]
            
            question_text = random.choice(question_templates)
            
            # Create guidelines for the essay
            guidelines = [
                "Your essay should have a clear introduction, body, and conclusion.",
                "Support your arguments with specific examples from the text.",
                "Demonstrate critical thinking and analysis of the concepts.",
                "Ensure your essay is well-structured and coherent."
            ]
            
            # Create the question dictionary
            question = {
                "id": str(uuid.uuid4()),
                "type": "essay",
                "topic": topic,
                "difficulty": difficulty,
                "question_text": question_text,
                "guidelines": guidelines,
                "suggested_length": "300-500 words",
                "max_points": 20
            }
            
            logger.info(f"Generated essay question for topic {topic}")
            return question
        except Exception as e:
            logger.error(f"Error generating essay question for topic {topic}: {str(e)}")
            return {}
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text for use in evaluating short answers.
        
        Args:
            text: Text to extract keywords from
            
        Returns:
            List of keywords
        """
        try:
            # Simple keyword extraction
            words = text.lower().split()
            
            # Filter out common words
            stop_words = {
                "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
                "of", "with", "by", "is", "are", "was", "were", "be", "been", "being",
                "have", "has", "had", "do", "does", "did", "will", "would", "could", "should"
            }
            
            keywords = [
                word for word in words 
                if len(word) > 3 and word not in stop_words and word.isalnum()
            ]
            
            # Return unique keywords
            return list(set(keywords))
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return []
    
    def generate_questions_for_topic(self, topic: str, context: str, num_questions: int = 5, 
                                    question_types: List[str] = None) -> List[Dict]:
        """
        Generate a mix of questions for a given topic.
        
        Args:
            topic: The topic for the questions
            context: Context text from the content
            num_questions: Number of questions to generate
            question_types: List of question types to include
            
        Returns:
            List of question dictionaries
        """
        try:
            if question_types is None:
                question_types = ["multiple_choice", "short_answer", "essay"]
            
            questions = []
            
            # Determine the distribution of question types
            if num_questions <= 3:
                # For small numbers, try to include one of each type
                distribution = {q_type: 1 for q_type in question_types[:num_questions]}
            else:
                # For larger numbers, distribute more evenly
                distribution = {}
                remaining = num_questions
                
                # Give each type at least one question
                for q_type in question_types:
                    distribution[q_type] = 1
                    remaining -= 1
                
                # Distribute remaining questions
                while remaining > 0:
                    for q_type in question_types:
                        if remaining <= 0:
                            break
                        distribution[q_type] += 1
                        remaining -= 1
            
            # Generate questions based on distribution
            for q_type, count in distribution.items():
                for _ in range(count):
                    if q_type == "multiple_choice":
                        question = self.generate_multiple_choice_question(topic, context)
                    elif q_type == "short_answer":
                        question = self.generate_short_answer_question(topic, context)
                    elif q_type == "essay":
                        question = self.generate_essay_question(topic, context)
                    else:
                        continue
                    
                    if question:
                        questions.append(question)
                        # Store the question
                        self.test_questions[question["id"]] = question
            
            # Save questions to file
            with open(self.questions_file, "wb") as f:
                pickle.dump(self.test_questions, f)
            
            logger.info(f"Generated {len(questions)} questions for topic {topic}")
            return questions
        except Exception as e:
            logger.error(f"Error generating questions for topic {topic}: {str(e)}")
            return []
    
    def create_test_from_content(self, content_id: str, num_questions: int = 10, 
                                test_title: str = None, difficulty: str = "medium") -> Dict:
        """
        Create a test from educational content.
        
        Args:
            content_id: ID of the educational content
            num_questions: Number of questions to include
            test_title: Optional title for the test
            difficulty: Overall difficulty level
            
        Returns:
            Test dictionary
        """
        try:
            # Get the content
            content = get_content_generator().get_content(content_id)
            if not content:
                logger.error(f"Content {content_id} not found")
                return {}
            
            # Get topics from the content
            topics = content.get("topics", [])
            if not topics:
                logger.error(f"No topics found in content {content_id}")
                return {}
            
            # Get document ID from content
            document_id = content.get("document_id")
            if not document_id:
                logger.error(f"No document ID found in content {content_id}")
                return {}
            
            # Get document chunks for context
            pdf_processor_instance = get_pdf_processor()
            document_chunks = [
                chunk_data["text"] for chunk_data in pdf_processor_instance.chunk_map.values()
                if chunk_data["document_id"] == document_id
            ]
            
            if not document_chunks:
                logger.error(f"No chunks found for document {document_id}")
                return {}
            
            # Combine chunks for context
            full_context = " ".join(document_chunks)
            
            # Generate questions for each topic
            all_questions = []
            questions_per_topic = max(1, num_questions // len(topics))
            
            for topic in topics:
                # Find relevant context for this topic
                relevant_chunks = self._find_relevant_chunks_for_topic(document_id, topic)
                topic_context = " ".join(relevant_chunks)
                
                # Generate questions for this topic
                topic_questions = self.generate_questions_for_topic(
                    topic, topic_context, questions_per_topic
                )
                all_questions.extend(topic_questions)
            
            # If we don't have enough questions, generate more from the full context
            if len(all_questions) < num_questions:
                additional_questions = self.generate_questions_for_topic(
                    topics[0], full_context, num_questions - len(all_questions)
                )
                all_questions.extend(additional_questions)
            
            # Limit to the requested number of questions
            all_questions = all_questions[:num_questions]
            
            # Create the test
            test_id = str(uuid.uuid4())
            test = {
                "id": test_id,
                "content_id": content_id,
                "title": test_title or f"Test on {content['title']}",
                "created_date": str(datetime.now()),
                "difficulty": difficulty,
                "question_ids": [q["id"] for q in all_questions],
                "total_points": sum(q.get("max_points", 1) for q in all_questions),
                "time_limit_minutes": self._calculate_time_limit(all_questions),
                "instructions": [
                    "Read each question carefully before answering.",
                    "For multiple choice questions, select the best answer.",
                    "For short answer questions, provide concise but complete responses.",
                    "For essay questions, ensure your answer is well-structured and comprehensive."
                ]
            }
            
            # Store the test
            self.generated_tests[test_id] = test
            
            # Save tests to file
            with open(self.tests_file, "wb") as f:
                pickle.dump(self.generated_tests, f)
            
            logger.info(f"Created test {test_id} with {len(all_questions)} questions")
            return test
        except Exception as e:
            logger.error(f"Error creating test from content {content_id}: {str(e)}")
            return {}
    
    def _find_relevant_chunks_for_topic(self, document_id: str, topic: str, max_chunks: int = 5) -> List[str]:
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
    
    def _calculate_time_limit(self, questions: List[Dict]) -> int:
        """
        Calculate an appropriate time limit for a test based on the questions.
        
        Args:
            questions: List of question dictionaries
            
        Returns:
            Time limit in minutes
        """
        try:
            total_minutes = 0
            
            for question in questions:
                q_type = question.get("type", "short_answer")
                difficulty = question.get("difficulty", "medium")
                
                # Base time per question type
                if q_type == "multiple_choice":
                    base_time = 1
                elif q_type == "short_answer":
                    base_time = 3
                elif q_type == "essay":
                    base_time = 10
                else:
                    base_time = 2
                
                # Adjust for difficulty
                if difficulty == "easy":
                    time_multiplier = 0.8
                elif difficulty == "hard":
                    time_multiplier = 1.5
                else:  # medium
                    time_multiplier = 1.0
                
                total_minutes += base_time * time_multiplier
            
            # Add some buffer time
            total_minutes = int(total_minutes * 1.2)
            
            # Ensure minimum time
            return max(10, total_minutes)
        except Exception as e:
            logger.error(f"Error calculating time limit: {str(e)}")
            return 30  # Default to 30 minutes
    
    def get_test(self, test_id: str) -> Optional[Dict]:
        """
        Retrieve a test by ID.
        
        Args:
            test_id: ID of the test
            
        Returns:
            Test dictionary or None if not found
        """
        try:
            test = self.generated_tests.get(test_id)
            if not test:
                return None
            
            # Get the full questions for the test
            questions = []
            for question_id in test.get("question_ids", []):
                question = self.test_questions.get(question_id)
                if question:
                    questions.append(question)
            
            # Create a copy of the test with the full questions
            test_with_questions = test.copy()
            test_with_questions["questions"] = questions
            
            return test_with_questions
        except Exception as e:
            logger.error(f"Error retrieving test {test_id}: {str(e)}")
            return None
    
    def get_all_tests(self) -> List[Dict]:
        """
        Get all generated tests.
        
        Returns:
            List of test dictionaries
        """
        return [
            {"test_id": test_id, **test}
            for test_id, test in self.generated_tests.items()
        ]
    
    def get_question(self, question_id: str) -> Optional[Dict]:
        """
        Retrieve a question by ID.
        
        Args:
            question_id: ID of the question
            
        Returns:
            Question dictionary or None if not found
        """
        return self.test_questions.get(question_id)
    
    def delete_test(self, test_id: str) -> bool:
        """
        Delete a test by ID.
        
        Args:
            test_id: ID of the test to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if test_id not in self.generated_tests:
                logger.warning(f"Test {test_id} not found")
                return False
            
            # Get the test to check its questions
            test = self.generated_tests[test_id]
            question_ids = test.get("question_ids", [])
            
            # Delete the test
            del self.generated_tests[test_id]
            
            # Save updated tests storage
            with open(self.tests_file, "wb") as f:
                pickle.dump(self.generated_tests, f)
            
            # Note: We're not deleting the questions themselves as they might be used in other tests
            # In a production system, you might want to implement reference counting or similar
            
            logger.info(f"Deleted test {test_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting test {test_id}: {str(e)}")
            return False

# Initialize the test generator (lazy initialization to avoid import issues)
test_generator = None

def get_test_generator():
    global test_generator
    if test_generator is None:
        test_generator = TestGenerator()
    return test_generator