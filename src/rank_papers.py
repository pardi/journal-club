"""
Rank papers by relevance using semantic similarity and other factors.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

import numpy as np
from sentence_transformers import SentenceTransformer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PaperRanker:
    """Rank papers by relevance to research interests."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the ranker.

        Args:
            model_name: Name of the sentence-transformers model to use
        """
        logger.info(f"Loading sentence transformer model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.interest_embedding = None

    def set_research_interests(self, interests: str):
        """
        Set and encode research interests.

        Args:
            interests: Description of research interests
        """
        logger.info("Encoding research interests")
        self.interest_embedding = self.model.encode(interests, convert_to_tensor=False)

    def compute_semantic_similarity(
        self, papers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Compute semantic similarity between papers and research interests.

        Args:
            papers: List of paper dictionaries

        Returns:
            Papers with added 'similarity_score' field
        """
        if self.interest_embedding is None:
            raise ValueError(
                "Research interests not set. Call set_research_interests() first."
            )

        logger.info(f"Computing semantic similarity for {len(papers)} papers")

        # Create text representations of papers (title + abstract)
        paper_texts = [f"{p['title']} {p['abstract']}" for p in papers]

        # Encode papers
        paper_embeddings = self.model.encode(paper_texts, convert_to_tensor=False)

        # Compute cosine similarity
        similarities = np.dot(paper_embeddings, self.interest_embedding) / (
            np.linalg.norm(paper_embeddings, axis=1)
            * np.linalg.norm(self.interest_embedding)
        )

        # Add similarity scores to papers
        for paper, similarity in zip(papers, similarities):
            paper["similarity_score"] = float(similarity)

        return papers

    def apply_keyword_bonus(
        self, papers: List[Dict[str, Any]], keywords: List[str], bonus: float = 0.05
    ) -> List[Dict[str, Any]]:
        """
        Add bonus score for papers matching important keywords.

        Args:
            papers: List of paper dictionaries
            keywords: List of important keywords
            bonus: Bonus score per keyword match

        Returns:
            Papers with updated scores
        """
        logger.info(f"Applying keyword bonus for {len(keywords)} keywords")

        for paper in papers:
            title_lower = paper["title"].lower()
            matches = sum(1 for keyword in keywords if keyword.lower() in title_lower)
            if matches > 0:
                paper["keyword_matches"] = matches
                paper["similarity_score"] += bonus * matches
            else:
                paper["keyword_matches"] = 0

        return papers

    def apply_recency_weight(
        self, papers: List[Dict[str, Any]], weight: float = 0.1
    ) -> List[Dict[str, Any]]:
        """
        Add weight for more recent papers.

        Args:
            papers: List of paper dictionaries
            weight: Maximum weight for newest papers

        Returns:
            Papers with updated scores
        """
        if not papers:
            return papers

        logger.info("Applying recency weight")

        # Get publication dates
        dates = [datetime.fromisoformat(p["published"]) for p in papers]
        min_date = min(dates)
        max_date = max(dates)
        date_range = (max_date - min_date).total_seconds()

        # Avoid division by zero
        if date_range == 0:
            date_range = 1

        # Apply recency weight
        for paper in papers:
            paper_date = datetime.fromisoformat(paper["published"])
            recency_factor = (paper_date - min_date).total_seconds() / date_range
            paper["recency_score"] = recency_factor * weight
            paper["similarity_score"] += paper["recency_score"]

        return papers

    def filter_read_papers(
        self,
        papers: List[Dict[str, Any]],
        read_papers_file: str = "data/read_papers.json",
    ) -> List[Dict[str, Any]]:
        """
        Filter out papers that have already been read.

        Args:
            papers: List of paper dictionaries
            read_papers_file: Path to file tracking read papers

        Returns:
            Filtered list of papers
        """
        if not os.path.exists(read_papers_file):
            logger.info("No read papers file found, returning all papers")
            return papers

        try:
            with open(read_papers_file, "r") as f:
                read_data = json.load(f)
                read_ids = set(read_data.get("paper_ids", []))
        except Exception as e:
            logger.warning(f"Error reading read_papers file: {e}")
            return papers

        filtered_papers = [p for p in papers if p["id"] not in read_ids]
        removed_count = len(papers) - len(filtered_papers)

        logger.info(f"Filtered out {removed_count} previously read papers")
        return filtered_papers

    def rank_papers(
        self,
        papers: List[Dict[str, Any]],
        keywords: List[str] = None,
        min_threshold: float = 0.3,
        top_n: int = 10,
        keyword_bonus: float = 0.05,
        recency_weight: float = 0.1,
        filter_read: bool = True,
        read_papers_file: str = "data/read_papers.json",
    ) -> List[Dict[str, Any]]:
        """
        Rank papers by relevance.

        Args:
            papers: List of paper dictionaries
            keywords: Important keywords for bonus scoring
            min_threshold: Minimum similarity threshold
            top_n: Number of top papers to return
            keyword_bonus: Bonus score per keyword match
            recency_weight: Weight for recency scoring
            filter_read: Whether to filter out previously read papers
            read_papers_file: Path to file tracking read papers

        Returns:
            Ranked list of top papers
        """
        if not papers:
            logger.warning("No papers to rank")
            return []

        # Filter read papers
        if filter_read:
            papers = self.filter_read_papers(papers, read_papers_file)

        if not papers:
            logger.warning("No new papers after filtering")
            return []

        # Compute semantic similarity
        papers = self.compute_semantic_similarity(papers)

        # Apply keyword bonus
        if keywords:
            papers = self.apply_keyword_bonus(papers, keywords, keyword_bonus)

        # Apply recency weight
        papers = self.apply_recency_weight(papers, recency_weight)

        # Filter by threshold
        papers = [p for p in papers if p["similarity_score"] >= min_threshold]
        logger.info(f"{len(papers)} papers above threshold {min_threshold}")

        # Sort by score
        papers.sort(key=lambda x: x["similarity_score"], reverse=True)

        # Return top N
        top_papers = papers[:top_n]
        logger.info(f"Returning top {len(top_papers)} papers")

        return top_papers


def main():
    """Example usage of the PaperRanker."""
    # Example papers
    papers = [
        {
            "id": "2301.00001",
            "title": "Deep Learning for Robotic Grasping",
            "abstract": "We present a novel approach for robotic grasping using deep reinforcement learning...",
            "authors": ["John Doe", "Jane Smith"],
            "url": "https://arxiv.org/abs/2301.00001",
            "pdf_url": "https://arxiv.org/pdf/2301.00001",
            "published": "2023-01-01T00:00:00",
            "categories": ["cs.RO", "cs.LG"],
            "primary_category": "cs.RO",
        },
        {
            "id": "2301.00002",
            "title": "3D Scene Reconstruction from RGB-D Images",
            "abstract": "We propose a method for 3D scene reconstruction using RGB-D cameras...",
            "authors": ["Alice Brown"],
            "url": "https://arxiv.org/abs/2301.00002",
            "pdf_url": "https://arxiv.org/pdf/2301.00002",
            "published": "2023-01-02T00:00:00",
            "categories": ["cs.CV"],
            "primary_category": "cs.CV",
        },
    ]

    ranker = PaperRanker()
    ranker.set_research_interests(
        "I am interested in robotics manipulation, grasping, and computer vision for 3D understanding."
    )

    keywords = ["grasping", "manipulation", "3D reconstruction"]
    ranked_papers = ranker.rank_papers(
        papers, keywords=keywords, min_threshold=0.2, top_n=10
    )

    print(f"\nRanked {len(ranked_papers)} papers:")
    for i, paper in enumerate(ranked_papers, 1):
        print(f"{i}. {paper['title']}")
        print(f"   Score: {paper['similarity_score']:.3f}")
        print()


if __name__ == "__main__":
    main()
