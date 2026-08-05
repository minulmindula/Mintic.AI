from typing import Any, Optional

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from src.config import Settings, settings as default_settings


class DocumentVectorStore:
    """
    Vector store manager utilizing Qdrant for storing and retrieving financial documents.
    """

    COLLECTION_NAME: str = "financial_docs"

    def __init__(
        self,
        client: Optional[QdrantClient] = None,
        config: Optional[Settings] = None,
        vector_size: int = 1536,
    ) -> None:
        """Initialize the DocumentVectorStore and ensure the financial_docs collection exists."""
        self.config: Settings = config or default_settings
        self.client: QdrantClient = client or QdrantClient(
            location=self.config.QDRANT_LOCATION
        )
        self.vector_size: int = vector_size
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Ensures that the 'financial_docs' collection exists in Qdrant."""
        collections = [
            col.name for col in self.client.get_collections().collections
        ]
        if self.COLLECTION_NAME not in collections:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )

    def upsert_document(
        self,
        doc_id: int,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        """
        Upserts a document point into the financial_docs collection.

        Args:
            doc_id: Unique point ID integer.
            vector: High-dimensional embedding vector matching vector_size.
            payload: Metadata dictionary associated with document.
        """
        point = PointStruct(
            id=doc_id,
            vector=vector,
            payload=payload,
        )
        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=[point],
        )

    def search_similar(
        self, query_vector: list[float], limit: int = 5
    ) -> list[Any]:
        """
        Searches financial_docs for documents similar to query_vector.

        Args:
            query_vector: Query embedding vector.
            limit: Maximum number of matches to return.

        Returns:
            List of matching ScoredPoint search results.
        """
        return list(
            self.client.query_points(
                collection_name=self.COLLECTION_NAME,
                query=query_vector,
                limit=limit,
            ).points
        )
