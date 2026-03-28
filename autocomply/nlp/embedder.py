"""
Embedding engine for AutoComply.

Loads the sentence-transformers model ``all-MiniLM-L6-v2`` and provides
methods to encode framework controls and document clauses into dense vector
representations for downstream cosine-similarity matching.

Design principle
----------------
The model is loaded once as a module-level singleton (``_model``).
Framework controls are embedded once at startup and the embeddings cached
inside :class:`Embedder` instances.  Document clauses are embedded on each
analysis run (they change with every upload).
"""

import logging
from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level singleton — one model instance per Python process
# ---------------------------------------------------------------------------
MODEL_NAME = "BAAI/bge-small-en-v1.5"
_model: Optional[SentenceTransformer] = None


def get_model() -> SentenceTransformer:
    """Return the singleton :class:`SentenceTransformer` model instance.

    The model is downloaded on first call and cached in memory for the
    lifetime of the process.

    Returns:
        Loaded :class:`SentenceTransformer` model.
    """
    global _model
    if _model is None:
        logger.info("Loading sentence-transformers model: %s", MODEL_NAME)
        _model = SentenceTransformer(MODEL_NAME)
        logger.info("Model loaded successfully.")
    return _model


# ---------------------------------------------------------------------------
# Embedder class
# ---------------------------------------------------------------------------

class Embedder:
    """Manages vector embeddings for framework controls and document clauses.

    Controls are embedded once at construction / on the first call to
    :meth:`embed_controls` and the result cached.  Document clauses are
    embedded on demand via :meth:`embed_clauses`.

    All embeddings are L2-normalised so that cosine similarity reduces to
    a simple dot product, which is both faster and numerically stable.
    """

    def __init__(self) -> None:
        """Initialise the embedder and acquire the singleton model."""
        self.model: SentenceTransformer = get_model()
        self._control_embeddings: Optional[np.ndarray] = None
        self._control_texts: List[str] = []

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def embed_controls(self, control_texts: List[str]) -> np.ndarray:
        """Encode a list of control requirement strings into embeddings.

        The results are cached so that subsequent calls with the *same*
        list return immediately without re-encoding.

        Args:
            control_texts: List of control requirement text strings.

        Returns:
            ``numpy.ndarray`` of shape ``(n_controls, embedding_dim)``,
            L2-normalised.
        """
        if not control_texts:
            raise ValueError("control_texts must not be empty.")

        # Return cached result if the input is unchanged
        if control_texts == self._control_texts and self._control_embeddings is not None:
            logger.debug("Returning cached control embeddings.")
            return self._control_embeddings

        logger.info("Embedding %d framework controls…", len(control_texts))
        self._control_texts = list(control_texts)
        self._control_embeddings = self.model.encode(
            control_texts,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True,  # L2-normalise for cosine similarity
            convert_to_numpy=True,
        )
        logger.info("Control embeddings cached  (shape: %s).", self._control_embeddings.shape)
        return self._control_embeddings

    def embed_clauses(self, clause_texts: List[str]) -> np.ndarray:
        """Encode a list of document clause strings into embeddings.

        Args:
            clause_texts: List of document clause strings.

        Returns:
            ``numpy.ndarray`` of shape ``(n_clauses, embedding_dim)``,
            L2-normalised.

        Raises:
            ValueError: If ``clause_texts`` is empty.
        """
        if not clause_texts:
            raise ValueError("clause_texts must not be empty.")

        logger.info("Embedding %d document clauses…", len(clause_texts))
        embeddings = self.model.encode(
            clause_texts,
            batch_size=64,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        logger.info("Clause embeddings computed  (shape: %s).", embeddings.shape)
        return embeddings

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def control_embeddings(self) -> Optional[np.ndarray]:
        """Cached control embeddings, or ``None`` if not yet computed."""
        return self._control_embeddings
