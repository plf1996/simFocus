"""
Text embedding service for semantic similarity calculations.
Uses OpenAI Embeddings API for efficient text encoding.

Optimized with caching and improved text weighting.
"""
import logging
import hashlib
import json
from typing import List, Dict, Any, Optional, Tuple
from functools import lru_cache
from collections import OrderedDict
import numpy as np
import httpx

logger = logging.getLogger(__name__)


class LRUCache:
    """Simple LRU cache with size limit"""

    def __init__(self, maxsize: int = 1000):
        self.cache = OrderedDict()
        self.maxsize = maxsize

    def get(self, key: str) -> Optional[np.ndarray]:
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def put(self, key: str, value: np.ndarray):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.maxsize:
            # Remove oldest (first) item
            self.cache.popitem(last=False)


class EmbeddingService:
    """Service for computing text embeddings and similarities using OpenAI API"""

    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        """
        Initialize embedding service

        Args:
            api_key: OpenAI API key
            base_url: Custom base URL for OpenAI-compatible API
            model: Embedding model name (default: text-embedding-3-small)
        """
        self.api_key = api_key
        self.base_url = base_url or "https://api.openai.com/v1"
        self.model = model or "text-embedding-3-small"
        self.embedding_dim = None  # Will be detected from first API response
        self._client = None
        # Cache for embeddings
        self._text_cache = LRUCache(maxsize=2000)

    def _get_client(self):
        """Get HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client

    def _cache_key(self, text: str) -> str:
        """Generate cache key from text"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    async def encode_text(self, text: str, provider_name: str = None, use_cache: bool = True) -> np.ndarray:
        """
        Encode text to embedding vector using OpenAI API

        Args:
            text: Input text string
            provider_name: Optional provider name from LLM orchestrator
            use_cache: Whether to use cache (default: True)

        Returns:
            Embedding vector (numpy array)
        """
        if not text or not text.strip():
            # Return zero vector with detected dimension, or default 1536
            dim = self.embedding_dim if self.embedding_dim else 1536
            return np.zeros(dim)

        # Check cache
        if use_cache:
            cache_key = self._cache_key(text)
            cached = self._text_cache.get(cache_key)
            if cached is not None:
                return cached

        try:
            client = self._get_client()

            # Use custom base URL if provided (for DeepSeek, etc.)
            url = f"{self.base_url}/embeddings"

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "input": text[:8000],  # Limit text length
                "model": self.model  # Use configured model
            }

            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()

            data = response.json()
            embedding = np.array(data["data"][0]["embedding"], dtype=np.float32)

            # Detect and set embedding dimension from first response
            if self.embedding_dim is None:
                self.embedding_dim = len(embedding)
                logger.info(f"Detected embedding dimension: {self.embedding_dim} for model {self.model}")

            # Cache the result
            if use_cache:
                self._text_cache.put(cache_key, embedding)

            return embedding

        except Exception as e:
            # Try to get more detailed error info
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    logger.error(f"Failed to encode text: {e} - Detail: {error_detail}")
                except:
                    logger.error(f"Failed to encode text: {e} - Response: {e.response.text[:200]}")
            else:
                logger.error(f"Failed to encode text: {e}")
            # Return zero vector on error
            dim = self.embedding_dim if self.embedding_dim else 1536
            return np.zeros(dim)

    async def encode_texts_batch(self, texts: List[str], provider_name: str = None, use_cache: bool = True) -> np.ndarray:
        """
        Encode multiple texts in batch using OpenAI API

        Args:
            texts: List of text strings
            provider_name: Optional provider name
            use_cache: Whether to use cache (default: True)

        Returns:
            Matrix of embeddings (N x D)
        """
        if not texts:
            dim = self.embedding_dim if self.embedding_dim else 1536
            return np.array([]).reshape(0, dim)

        # Filter empty texts
        cleaned_texts = [t if t and t.strip() else " " for t in texts]

        # Check cache for each text
        embeddings = []
        uncached_indices = []
        uncached_texts = []

        if use_cache:
            for i, text in enumerate(cleaned_texts):
                cache_key = self._cache_key(text)
                cached = self._text_cache.get(cache_key)
                if cached is not None:
                    embeddings.append((i, cached))
                else:
                    uncached_indices.append(i)
                    uncached_texts.append(text)
        else:
            uncached_indices = list(range(len(cleaned_texts)))
            uncached_texts = cleaned_texts

        # Encode uncached texts in batch
        if uncached_texts:
            try:
                client = self._get_client()
                url = f"{self.base_url}/embeddings"

                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

                # Process in batches of 10 (API limit for Alibaba DashScope)
                batch_size = 10
                all_new_embeddings = []

                for i in range(0, len(uncached_texts), batch_size):
                    batch = uncached_texts[i:i + batch_size]

                    payload = {
                        "input": batch,
                        "model": self.model
                    }

                    response = await client.post(url, headers=headers, json=payload)
                    response.raise_for_status()

                    data = response.json()
                    batch_embeddings = [np.array(item["embedding"], dtype=np.float32) for item in data["data"]]

                    # Detect embedding dimension from first response
                    if self.embedding_dim is None and batch_embeddings:
                        self.embedding_dim = len(batch_embeddings[0])
                        logger.info(f"Detected embedding dimension: {self.embedding_dim} for model {self.model}")

                    all_new_embeddings.extend(batch_embeddings)

                # Cache new embeddings
                for idx, text, emb in zip(uncached_indices, uncached_texts, all_new_embeddings):
                    if use_cache:
                        cache_key = self._cache_key(text)
                        self._text_cache.put(cache_key, emb)
                    embeddings.append((idx, emb))

            except Exception as e:
                # Try to get more detailed error info
                if hasattr(e, 'response') and e.response is not None:
                    try:
                        error_detail = e.response.json()
                        logger.error(f"Failed to encode texts batch: {e} - Detail: {error_detail}")
                    except:
                        logger.error(f"Failed to encode texts batch: {e} - Response: {e.response.text[:200]}")
                else:
                    logger.error(f"Failed to encode texts batch: {e}")
                # Return zero vectors for failed batch
                dim = self.embedding_dim if self.embedding_dim else 1536
                for idx in uncached_indices:
                    embeddings.append((idx, np.zeros(dim)))

        # Sort by original index and return
        embeddings.sort(key=lambda x: x[0])
        result = np.array([emb for _, emb in embeddings], dtype=np.float32)

        return result

    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score (0-1, higher is more similar)
        """
        # Normalize vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        # Dot product of normalized vectors = cosine similarity
        return float(np.dot(embedding1, embedding2) / (norm1 * norm2))

    def compute_similarities(
        self,
        query_embedding: np.ndarray,
        candidate_embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Compute similarities between query and multiple candidates

        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: Matrix of candidate embeddings

        Returns:
            Array of similarity scores
        """
        if candidate_embeddings.size == 0:
            return np.array([])

        # Normalize query
        query_norm = np.linalg.norm(query_embedding)
        if query_norm == 0:
            return np.zeros(candidate_embeddings.shape[0])

        query_normalized = query_embedding / query_norm

        # Normalize candidates
        candidate_norms = np.linalg.norm(candidate_embeddings, axis=1, keepdims=True)
        # Avoid division by zero
        candidate_norms = np.where(candidate_norms == 0, 1, candidate_norms)
        candidates_normalized = candidate_embeddings / candidate_norms

        # Compute cosine similarity
        similarities = np.dot(candidates_normalized, query_normalized)

        return similarities

    def clear_cache(self):
        """Clear the embedding cache and reset dimension"""
        self._text_cache = LRUCache(maxsize=2000)
        self.embedding_dim = None  # Reset dimension to allow re-detection
        logger.info("Embedding cache cleared and dimension reset")

    async def close(self):
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None


# Global singleton instance
_embedding_service: EmbeddingService = None


def get_embedding_service() -> EmbeddingService:
    """Get or create global embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        # Get API key from environment - strictly use provided parameter names
        import os
        api_key = os.getenv("Embedding_API_KEY", "")
        base_url = os.getenv("Embedding_BASR_URL", "")
        model = os.getenv("Embedding_MODEl", "text-embedding-v3")

        if not api_key:
            logger.warning("No Embedding API key found, embeddings will return zero vectors")

        _embedding_service = EmbeddingService(api_key=api_key, base_url=base_url, model=model)
    return _embedding_service


def build_character_text(character: Dict[str, Any], enhanced: bool = True) -> str:
    """
    Build searchable text from character configuration

    Args:
        character: Character dictionary with config field
        enhanced: Whether to use enhanced text building with weights

    Returns:
        Combined text for embedding
    """
    config = character.get("config", {})
    parts = []

    if enhanced:
        # Enhanced version with weighted sections
        # Basic info (medium weight)
        name = character.get("name", "")
        if name:
            parts.append(f"【角色】{name}")

        profession = config.get("profession", "")
        if profession:
            parts.append(f"【职业】{profession}")

        # Knowledge fields (high weight) - repeat for emphasis
        knowledge = config.get("knowledge", {})
        fields = knowledge.get("fields", [])
        if fields:
            fields_text = " ".join(fields)
            parts.append(f"【专业领域】{fields_text}")
            parts.append(f"【擅长】{fields_text}")  # Repeat for higher weight

        # Experience (medium weight)
        experience_years = knowledge.get("experience_years", 0)
        if experience_years > 0:
            parts.append(f"【经验】{experience_years}年工作经验")

        # Representative views (high weight)
        views = knowledge.get("representative_views", [])
        if views:
            views_text = " ".join(views)
            parts.append(f"【观点】{views_text}")
            parts.append(f"【见解】{views_text}")  # Repeat for emphasis

        # Personality traits (low-medium weight)
        personality = config.get("personality", {})
        if personality:
            traits = []
            if personality.get("openness", 0) > 6:
                traits.append("开放")
            if personality.get("rigor", 0) > 6:
                traits.append("严谨")
            if personality.get("critical_thinking", 0) > 6:
                traits.append("批判思维")
            if personality.get("optimism", 0) > 6:
                traits.append("乐观")
            if personality.get("leadership", 0) > 6:
                traits.append("领导力")
            if traits:
                parts.append(f"【性格】{' '.join(traits)}")

        # Background (low weight)
        background = knowledge.get("background", "")
        if background:
            parts.append(f"【背景】{background}")

        # Achievements (medium weight)
        achievements = knowledge.get("achievements", [])
        if achievements:
            parts.append(f"【成就】{' '.join(achievements)}")
    else:
        # Simple version (original)
        name = character.get("name", "")
        if name:
            parts.append(f"角色名称：{name}")

        profession = config.get("profession", "")
        if profession:
            parts.append(f"职业：{profession}")

        knowledge = config.get("knowledge", {})
        fields = knowledge.get("fields", [])
        if fields:
            parts.append(f"专业领域：{', '.join(fields)}")

        experience_years = knowledge.get("experience_years", 0)
        if experience_years > 0:
            parts.append(f"工作经验：{experience_years}年")

        views = knowledge.get("representative_views", [])
        if views:
            parts.append(f"代表观点：{', '.join(views)}")

        personality = config.get("personality", {})
        if personality:
            traits = []
            if personality.get("openness", 0) > 7:
                traits.append("开放包容")
            if personality.get("rigor", 0) > 7:
                traits.append("严谨细致")
            if personality.get("critical_thinking", 0) > 7:
                traits.append("批判性思维强")
            if personality.get("optimism", 0) > 7:
                traits.append("积极乐观")
            if traits:
                parts.append(f"性格特点：{', '.join(traits)}")

    return " ".join(parts)


def build_topic_text(topic: Dict[str, Any], enhanced: bool = True) -> str:
    """
    Build searchable text from topic

    Args:
        topic: Topic dictionary with title and description
        enhanced: Whether to use enhanced text building

    Returns:
        Combined text for embedding
    """
    parts = []

    title = topic.get("title", "")
    description = topic.get("description", "")

    if enhanced:
        # Enhanced version - repeat keywords for emphasis
        if title:
            # Extract key terms from title (simple approach: split by common delimiters)
            parts.append(f"【议题】{title}")
            parts.append(f"【讨论】{title}")  # Repeat for weight

            # Add individual terms
            terms = []
            for delimiter in ["、", "，", " ", "与", "和", "的"]:
                if delimiter in title:
                    terms.extend([t.strip() for t in title.split(delimiter) if t.strip()])
                    break
            if not terms:
                terms = [title]
            parts.append(f"【关键词】{' '.join(terms)}")

        if description:
            parts.append(f"【内容】{description}")
            parts.append(f"【详情】{description}")  # Repeat for weight
    else:
        # Simple version (original)
        if title:
            parts.append(f"议题：{title}")
        if description:
            parts.append(f"描述：{description}")

    return " ".join(parts)


def compute_weighted_score(
    similarity: float,
    character: Dict[str, Any],
    weights: Dict[str, float] = None
) -> float:
    """
    Compute weighted recommendation score considering multiple factors

    Args:
        similarity: Semantic similarity score (0-1)
        character: Character dictionary
        weights: Optional weight configuration

    Returns:
        Weighted score (0-1)
    """
    if weights is None:
        weights = {
            "similarity": 0.7,      # Semantic similarity weight
            "usage_count": 0.2,     # Usage count weight (popularity)
            "rating": 0.1           # Rating weight
        }

    # Base similarity score
    score = similarity * weights["similarity"]

    # Normalize and add usage count bonus
    usage_count = character.get("usage_count", 0) or 0
    usage_bonus = min(usage_count / 100.0, 1.0)  # Cap at 100 uses
    score += usage_bonus * weights["usage_count"]

    # Normalize and add rating bonus
    rating_avg = character.get("rating_avg", 0) or 0
    rating_count = character.get("rating_count", 0) or 0
    if rating_count > 0:
        rating_bonus = (rating_avg / 5.0)  # Assume 5-point scale
        # Apply rating confidence weighting based on count
        confidence = min(rating_count / 10.0, 1.0)  # Full confidence at 10+ ratings
        score += rating_bonus * confidence * weights["rating"]

    return min(score, 1.0)  # Cap at 1.0
