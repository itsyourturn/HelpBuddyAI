import os
import warnings
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from typing import List, Dict, Any
import logging
from src.config import Settings

# Suppress deprecation warnings for Chroma
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain_community.vectorstores")

logger = logging.getLogger(__name__)


class ChromaStore:
    """ChromaDB vector store for NCERT Science Class 8 content"""

    def  __init__(self):
        """Initialize ChromaDB store"""
        self.settings = Settings()
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=self.settings.EMBEDDING_MODEL,
            google_api_key=self.settings.GOOGLE_API_KEY
        )

        # Initialize ChromaDB client
        self.client =  chromadb.PersistentClient(
            path=self.settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        self.collection_name = "ncert_science_class8"
        self.vectorstore = None

        # Initialize or load existing vectorstore
        self._initialize_vectorstore()

    def _initialize_vectorstore(self):
        """Initialize or load existing vectorstore"""
        try:
            # Check if collection exists
            collections = self.client.list_collections()
            collection_exists = any(
                col.name == self.collection_name for col in collections
            )

            if collection_exists:
                logger.info("Loading existing vector store...")
                self.vectorstore = Chroma(
                    client=self.client,
                    collection_name= self.collection_name,
                    embedding_function=self.embeddings
                )
                logger.info("Vector store loaded successfully")
            else:
                logger.info(
                    "No existing vector store found. Ready to index PDF."
                )
                self.vectorstore = None

        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            self.vectorstore = None
            
    def is_initialized(self) -> bool:
        """Check if vector store is initialized with data"""
        try:
            if self.vectorstore is None:
                return False
                
            # Try to get collection info to verify it exists and has documents
            collection = self.client.get_collection(self.collection_name)
            count = collection.count()
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking vector store initialization: {str(e)}")
            return False
    
    def index_pdf(self, pdf_path: str = None) -> bool:
        """
        Index NCERT Science Class 8 PDF into vector store

        Args:
            pdf_path: Path to PDF file

        Returns:
            bool: Success status
        """
        try:
            if pdf_path is None:
                pdf_path = self.settings.PDF_PATH
                logger.info(f"Using default PDF path: {pdf_path}")
            
            if not os.path.exists(pdf_path):
                logger.error(f"PDF file not found: {pdf_path}")
                return False
                
            logger.info(f"Loading PDF from {pdf_path}")
            # Load PDF and split into pages
            loader = PyPDFLoader(pdf_path)
            pages = loader.load_and_split()
            
            if not pages:
                logger.error("No pages extracted from PDF")
                return False
                
            logger.info(f"Successfully loaded {len(pages)} pages from PDF")
            logger.info("Initializing Chroma vector store with extracted content")
            
            # Create new collection and add texts
            self.vectorstore = Chroma.from_documents(
                documents=pages,
                embedding=self.embeddings,
                collection_name=self.collection_name,
                client=self.client
            )
            
            if not self.vectorstore:
                logger.error("Vector store initialization failed")
                return False
                
            collection = self.client.get_collection(self.collection_name)
            count = collection.count()
            logger.info(f"Vector store initialized with {count} documents")
            return True
            
        except Exception as e:
            logger.error(f"Error indexing PDF: {str(e)}")
            logger.exception("Detailed error trace:")
            return False

            # Add metadata to chunks
            for i, text in enumerate(texts):
                text.metadata.update({
                    "source": "NCERT Science Class 8",
                    "chunk_id": i,
                    "total_chunks": len(texts),
                    "subject": "Science",
                    "class": "8",
                    "board": "NCERT"
                })

            # Create vectorstore
            logger.info("Creating vector store...")
            self.vectorstore = Chroma.from_documents(
                documents=texts,
                embedding=self.embeddings,
                client=self.client,
                collection_name=self.collection_name,
                persist_directory=self.settings.CHROMA_PERSIST_DIR
            )

            logger.info("PDF indexed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error indexing PDF: {str(e)}")
            return False
    
    def similarity_search(
            self,
            query: str,
            k: int = 5,
            filter_dict: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search in vector store

        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Optional filters

        Returns:
            List of relevant documents with metadata
        """
        try:
            if self.vectorstore is None:
                logger.warning("Vector store not initialized")
                return []
            
            # Perform similarity search
            docs = self.vectorstore.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter_dict
            )

            # Format results - no relevance scoring
            results = []
            for doc, score in docs:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": score
                })

            logger.info(f"Found {len(results)} documents")
            return results
        
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            return []
        
    def get_relevant_context(
            self,
            query: str,
            max_chunks: int = 5
    ) -> str:
        """
        Get relevant context for a query

        Args:
            query: Search query
            max_chunks: Maximum number of chunks to return
        
        Returns:
            Formatted context string
        """
        try:
            logger.info(f"Searching vector store for: '{query}'")
            
            # Search for documents - no relevance filtering
            results = self.similarity_search(query, k=max_chunks)

            if not results:
                logger.info("No documents found in vector store")
                return "No information found in NCERT Science Class 8."
            
            logger.info(f"Found {len(results)} documents in vector store")
            
            # Format context
            context_parts = []
            for i, result in enumerate(results, 1):
                content = result["content"].strip()
                page = result["metadata"].get("page", "Unknown")

                context_parts.append(
                    f"[Context {i} - Page {page}]\n{content}"
                )
            
            final_context = "\n\n".join(context_parts)
            
            return final_context
        
        except Exception as e:
            logger.error(f"Error in vector store search: {str(e)}")
            return "No information found in NCERT Science Class 8."
        
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        try:
            if self.vectorstore is None:
                return {
                    "exists": False,
                    "count": 0,
                    "status": "Not initialized"
                }
            
            collection = self.client.get_collection(self.collection_name)
            count = collection.count()

            return {
                "exists": True,
                "count": count,
                "status": "Ready",
                "collection_name": self.collection_name
            }
        
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return {
                "exists": False,
                "count": 0,
                "status": f"Error: {str(e)}"
            }
        
    def reset_collection(self) -> bool:
        """Reset the collection (delete all data)"""
        try:
            if self.vectorstore is not None:
                self.client.delete_collection(self.collection_name)
                logger.info("Collection reset successfully")
            
            self.vectorstore = None
            return True
    
        except Exception as e:
            logger.error(f"Error resetting collection: {str(e)}")
            return False

    def debug_vector_store_content(self, query: str = None) -> Dict[str, Any]:
        """Debug method to check vector store content"""
        try:
            if self.vectorstore is None:
                return {"error": "Vector store not initialized"}
            
            # Get collection info
            collection = self.client.get_collection(self.collection_name)
            count = collection.count()
            
            result = {
                "total_documents": count,
                "collection_name": self.collection_name,
                "vectorstore_initialized": self.vectorstore is not None
            }
            
            if query:
                # Test search with the query
                search_results = self.similarity_search(query, k=5)
                result["search_results"] = []
                for i, res in enumerate(search_results):
                    result["search_results"].append({
                        "rank": i + 1,
                        "relevance": res["relevance"],
                        "similarity_score": res["similarity_score"],
                        "content_preview": res["content"][:200] + "..." if len(res["content"]) > 200 else res["content"],
                        "page": res["metadata"].get("page", "Unknown")
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"Error debugging vector store: {str(e)}")
            return {"error": str(e)}
