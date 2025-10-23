import os
import logging
import pickle
from typing import List, Dict, Tuple, Optional
import numpy as np
import faiss
from fastapi import UploadFile, File, HTTPException
from PyPDF2 import PdfReader
import re
from sentence_transformers import SentenceTransformer
import uuid
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """
    A class to process PDF documents for the educational mentorship platform.
    Handles text extraction, chunking, embedding generation, and storage in FAISS.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", dimension: int = 384):
        """
        Initialize the PDF processor with embedding model and FAISS index.
        
        Args:
            model_name: Name of the sentence transformer model to use
            dimension: Dimension of the embeddings
        """
        self.dimension = dimension
        self.model = SentenceTransformer(model_name)
        self.index_file = "faiss_index.bin"
        self.chunk_map_file = "chunk_map.pkl"
        self.documents_file = "documents.pkl"
        
        # Initialize or load FAISS index
        if os.path.exists(self.index_file):
            self.index = faiss.read_index(self.index_file)
            logger.info(f"Loaded existing FAISS index with {self.index.ntotal} vectors")
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            logger.info("Created new FAISS index")
        
        # Load or initialize chunk map
        if os.path.exists(self.chunk_map_file):
            with open(self.chunk_map_file, "rb") as f:
                self.chunk_map = pickle.load(f)
            logger.info(f"Loaded existing chunk map with {len(self.chunk_map)} chunks")
        else:
            self.chunk_map = {}
            logger.info("Initialized new chunk map")
            
        # Load or initialize documents map
        if os.path.exists(self.documents_file):
            with open(self.documents_file, "rb") as f:
                self.documents = pickle.load(f)
            logger.info(f"Loaded existing documents map with {len(self.documents)} documents")
        else:
            self.documents = {}
            logger.info("Initialized new documents map")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as a string
        """
        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            logger.info(f"Extracted {len(text)} characters from {pdf_path}")
            return text
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing extra whitespace and special characters.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'\/\@\#\$\%\^\&\*\+\=\~\`]', '', text)
        return text.strip()
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into chunks of specified size with overlap.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum size of each chunk in words
            overlap: Number of overlapping words between chunks
            
        Returns:
            List of text chunks
        """
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
            
        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks
    
    def generate_embeddings(self, chunks: List[str]) -> np.ndarray:
        """
        Generate embeddings for text chunks.
        
        Args:
            chunks: List of text chunks
            
        Returns:
            Numpy array of embeddings
        """
        try:
            embeddings = self.model.encode(chunks, convert_to_numpy=True)
            logger.info(f"Generated embeddings for {len(chunks)} chunks")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error generating embeddings: {str(e)}")
    
    def add_to_index(self, embeddings: np.ndarray, chunks: List[str], document_id: str) -> int:
        """
        Add embeddings and chunks to FAISS index and chunk map.
        
        Args:
            embeddings: Numpy array of embeddings
            chunks: List of text chunks
            document_id: ID of the source document
            
        Returns:
            Number of vectors added to index
        """
        try:
            # Ensure embeddings are float32
            embeddings = embeddings.astype(np.float32)
            
            # Get starting ID for new vectors
            start_id = self.index.ntotal
            
            # Add embeddings to index
            self.index.add(embeddings)
            
            # Update chunk map with document ID reference
            for i, chunk in enumerate(chunks):
                chunk_id = start_id + i
                self.chunk_map[chunk_id] = {
                    "text": chunk,
                    "document_id": document_id
                }
            
            # Save updated index and chunk map
            faiss.write_index(self.index, self.index_file)
            with open(self.chunk_map_file, "wb") as f:
                pickle.dump(self.chunk_map, f)
                
            logger.info(f"Added {len(chunks)} vectors to index")
            return len(chunks)
        except Exception as e:
            logger.error(f"Error adding to index: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error updating index: {str(e)}")
    
    def process_pdf(self, pdf_file: UploadFile, chunk_size: int = 500, overlap: int = 50) -> Dict:
        """
        Process a PDF file: extract text, chunk, generate embeddings, and store in FAISS.
        
        Args:
            pdf_file: Uploaded PDF file
            chunk_size: Maximum size of each chunk in words
            overlap: Number of overlapping words between chunks
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Generate unique document ID
            document_id = str(uuid.uuid4())
            
            # Save uploaded file temporarily
            temp_path = f"temp_{document_id}.pdf"
            with open(temp_path, "wb") as f:
                f.write(pdf_file.file.read())
            
            # Extract text from PDF
            raw_text = self.extract_text_from_pdf(temp_path)
            
            # Clean text
            cleaned_text = self.clean_text(raw_text)
            
            # Chunk text
            chunks = self.chunk_text(cleaned_text, chunk_size, overlap)
            
            # Generate embeddings
            embeddings = self.generate_embeddings(chunks)
            
            # Add to index
            vectors_added = self.add_to_index(embeddings, chunks, document_id)
            
            # Store document metadata
            self.documents[document_id] = {
                "filename": pdf_file.filename,
                "upload_date": str(pd.Timestamp.now()),
                "processed_status": "completed",
                "chunk_count": len(chunks),
                "total_characters": len(cleaned_text)
            }
            
            # Save documents map
            with open(self.documents_file, "wb") as f:
                pickle.dump(self.documents, f)
            
            # Clean up temporary file
            os.remove(temp_path)
            
            return {
                "document_id": document_id,
                "filename": pdf_file.filename,
                "chunks_created": len(chunks),
                "vectors_added": vectors_added,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    
    def search_similar_content(self, query: str, k: int = 5) -> List[Dict]:
        """
        Search for content similar to the query.
        
        Args:
            query: Search query text
            k: Number of results to return
            
        Returns:
            List of similar content chunks with distances
        """
        try:
            # Generate embedding for query
            query_embedding = self.model.encode([query], convert_to_numpy=True)
            query_embedding = query_embedding.astype(np.float32)
            
            # Search in FAISS index
            distances, indices = self.index.search(query_embedding, k)
            
            # Format results
            results = []
            for idx, dist in zip(indices[0], distances[0]):
                if idx in self.chunk_map:
                    chunk_data = self.chunk_map[idx]
                    document_id = chunk_data["document_id"]
                    document_info = self.documents.get(document_id, {})
                    
                    results.append({
                        "chunk_id": int(idx),
                        "text": chunk_data["text"],
                        "document_id": document_id,
                        "document_filename": document_info.get("filename", "Unknown"),
                        "distance": float(dist)
                    })
            
            logger.info(f"Found {len(results)} results for query: {query[:50]}...")
            return results
        except Exception as e:
            logger.error(f"Error searching content: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error searching content: {str(e)}")
    
    def get_document_info(self, document_id: str) -> Optional[Dict]:
        """
        Get information about a processed document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            Document information dictionary or None if not found
        """
        return self.documents.get(document_id)
    
    def get_all_documents(self) -> List[Dict]:
        """
        Get information about all processed documents.
        
        Returns:
            List of document information dictionaries
        """
        return [
            {"document_id": doc_id, **info}
            for doc_id, info in self.documents.items()
        ]
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document and its associated chunks from the index.
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if document_id not in self.documents:
                logger.warning(f"Document {document_id} not found")
                return False
            
            # Find all chunks belonging to this document
            chunks_to_remove = [
                chunk_id for chunk_id, chunk_data in self.chunk_map.items()
                if chunk_data["document_id"] == document_id
            ]
            
            if not chunks_to_remove:
                logger.warning(f"No chunks found for document {document_id}")
                return False
            
            # Remove chunks from chunk map
            for chunk_id in chunks_to_remove:
                del self.chunk_map[chunk_id]
            
            # Remove document from documents map
            del self.documents[document_id]
            
            # Save updated maps
            with open(self.chunk_map_file, "wb") as f:
                pickle.dump(self.chunk_map, f)
            with open(self.documents_file, "wb") as f:
                pickle.dump(self.documents, f)
            
            # Note: For simplicity, we're not rebuilding the FAISS index here
            # In a production system, you would want to rebuild the index without
            # the deleted vectors or mark them as invalid
            logger.info(f"Deleted document {document_id} and {len(chunks_to_remove)} chunks")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            return False

# Initialize the PDF processor (lazy initialization to avoid import issues)
pdf_processor = None

def get_pdf_processor():
    global pdf_processor
    if pdf_processor is None:
        pdf_processor = PDFProcessor()
    return pdf_processor