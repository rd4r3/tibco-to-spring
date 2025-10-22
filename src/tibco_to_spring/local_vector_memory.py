import sqlite3
import faiss
import json
import numpy as np
import os
from typing import List, Optional, Union
from sentence_transformers import SentenceTransformer
from crewai.memory.storage.interface import Storage
from tibco_to_spring.logging_config import get_logger

# Set up logging
logger = get_logger(__name__)

CREW_MEMORY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "crew_memory.db"))

class LocalVectorMemory(Storage):
    def __init__(self, db_path=CREW_MEMORY_PATH, embedding_model="all-MiniLM-L6-v2"):
        self.conn = sqlite3.connect(db_path)
        self._init_tables()
        self.model = SentenceTransformer(embedding_model)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(self.dimension)
        self.embeddings = []
        self.metadata = []
        self._load_persistent_memory()  # Load persistent memory

    def _init_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent TEXT,
                metadata TEXT,
                content TEXT
            )
        """)
        self.conn.commit()

    def save(self, value: str, metadata: Optional[Union[str, dict]] = None, agent: Optional[str] = None):
        if isinstance(metadata, str):
            metadata_dict = {"value": metadata}
        elif isinstance(metadata, dict):
            metadata_dict = metadata
        else:
            metadata_dict = {}

        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO memory (agent, metadata, content) VALUES (?, ?, ?)",
            (agent, json.dumps(metadata_dict), value)
        )
        self.conn.commit()

        embedding = self.model.encode(value)
        self.index.add(np.array([embedding]).astype("float32"))
        self.embeddings.append(embedding)
        self.metadata.append({
            "agent": agent,
            "metadata": metadata_dict,
            "content": value
        })

    def search(self, query: str, limit: int = 10, score_threshold: float = 0.5) -> List[dict]:
        if not self.metadata:
            return []

        query_embedding = self.model.encode(query)
        D, I = self.index.search(np.array([query_embedding]).astype("float32"), limit)

        results = []
        for dist, idx in zip(D[0], I[0]):
            if idx < len(self.metadata) and dist <= score_threshold:
                item = self.metadata[idx]
                if isinstance(item, str):
                    try:
                        item = json.loads(item)
                    except Exception as e:
                        print(f"Error parsing metadata at index {idx}: {e}")
                        continue
                if isinstance(item, dict):
                    results.append(item)
        return results


    def reset(self):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM memory")
        self.conn.commit()

        self.index.reset()
        self.embeddings.clear()
        self.metadata.clear()

    def _load_persistent_memory(self):
        """
        Load all persisted memory items from SQLite database into memory.
        This method:
        1. Retrieves all memory records from the SQLite database
        2. Rebuilds the FAISS index with all persisted embeddings
        3. Populates the in-memory metadata list with all persisted records
        This ensures that all previously stored memory is available for
        both vector search and metadata queries when the application starts.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT agent, metadata, content FROM memory")
        rows = cursor.fetchall()

        # Prepare batches for more efficient processing
        embeddings_batch = []
        metadata_batch = []

        for agent, metadata_str, content in rows:
            try:
                metadata = json.loads(metadata_str) if metadata_str else {}
                embedding = self.model.encode(content)

                # Store for batch processing
                embeddings_batch.append(embedding)
                metadata_batch.append({
                    "agent": agent,
                    "metadata": metadata,
                    "content": content
                })

                # Log the loaded item
                logger.debug("Loading memory item: agent=%s, metadata_keys=%s, content_length=%d",
                            agent, list(metadata.keys()) if metadata else [], len(content))

            except json.JSONDecodeError as e:
                logger.error("JSON decode error for metadata '%s': %s", metadata_str, e)
                continue
            except Exception as e:
                logger.error("Error loading memory item: %s", e)
                continue

        # Add all embeddings to FAISS index in one batch
        if embeddings_batch:
            self.index.add(np.array(embeddings_batch).astype("float32"))
            self.embeddings.extend(embeddings_batch)
            self.metadata.extend(metadata_batch)

            logger.info("Successfully loaded %d memory items", len(embeddings_batch))
        else:
            logger.warning("No memory items were loaded from the database")
