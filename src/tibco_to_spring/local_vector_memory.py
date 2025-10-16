import sqlite3
import faiss
import numpy as np
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from crewai.memory.storage.interface import Storage


class LocalVectorMemory(Storage):
    def __init__(self, db_path="crew_memory.db", embedding_model="all-MiniLM-L6-v2"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._init_tables()
        self.model = SentenceTransformer(embedding_model)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(self.dimension)
        self.embeddings = []
        self.metadata = []

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
        # Add metadata column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE memory ADD COLUMN metadata TEXT")
        except sqlite3.OperationalError:
            # Column already exists
            pass
        self.conn.commit()

    def save(self, value: str, metadata: Optional[str] = None, agent: Optional[str] = None):
        # Save to SQLite
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO memory (agent, metadata, content) VALUES (?, ?, ?)",
            (agent, metadata, value)
        )
        self.conn.commit()

        # Save to FAISS
        embedding = self.model.encode(value)
        self.index.add(np.array([embedding]).astype("float32"))
        self.embeddings.append(embedding)
        self.metadata.append({
            "agent": agent,
            "metadata": metadata,
            "content": value
        })

    def search(self, query: str, limit: int = 10, score_threshold: float = 0.5) -> List[str]:
        if not self.metadata:
            return []

        query_embedding = self.model.encode(query)
        D, I = self.index.search(np.array([query_embedding]).astype("float32"), limit)

        results = []
        for dist, idx in zip(D[0], I[0]):
            if idx < len(self.metadata) and dist <= score_threshold:
                results.append(self.metadata[idx]["content"])
        return results

    def reset(self):
        # Clear SQLite
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM memory")
        self.conn.commit()

        # Clear FAISS and in-memory cache
        self.index.reset()
        self.embeddings.clear()
        self.metadata.clear()
