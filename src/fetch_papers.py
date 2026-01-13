"""
Fetch papers from arXiv API based on configured topics.
"""

import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import arxiv

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ArxivFetcher:
    """Fetch papers from arXiv API."""

    def __init__(self, days_back: int = 7, max_results: int = 100):
        """
        Initialize the fetcher.

        Args:
            days_back: Number of days to look back for papers
            max_results: Maximum number of results to fetch per query
        """
        self.days_back = days_back
        self.max_results = max_results
        self.rate_limit_delay = 3  # arXiv allows 3 requests per second

    def fetch_papers(
        self, query: str, categories: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch papers from arXiv based on query.

        Args:
            query: Search query string
            categories: List of arXiv categories to filter by

        Returns:
            List of paper dictionaries with metadata
        """
        logger.info(f"Fetching papers for query: {query}")

        # Calculate date filter (make it timezone-aware)
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.days_back)

        papers = []
        retry_count = 0
        max_retries = 3

        while retry_count < max_retries:
            try:
                # Create search object
                search = arxiv.Search(
                    query=query,
                    max_results=self.max_results,
                    sort_by=arxiv.SortCriterion.SubmittedDate,
                    sort_order=arxiv.SortOrder.Descending,
                )

                # Fetch results
                for result in search.results():
                    # Filter by date
                    if result.published < cutoff_date:
                        continue

                    # Filter by categories if specified
                    # Handle both string and object category formats
                    if categories:
                        paper_categories = []
                        for cat in result.categories:
                            if isinstance(cat, str):
                                paper_categories.append(cat)
                            else:
                                paper_categories.append(cat.term)
                        if not any(cat in categories for cat in paper_categories):
                            continue

                    # Extract paper metadata
                    # Handle both string and object category formats
                    result_categories = []
                    for cat in result.categories:
                        if isinstance(cat, str):
                            result_categories.append(cat)
                        else:
                            result_categories.append(cat.term)

                    paper = {
                        "id": result.entry_id.split("/")[-1],
                        "title": result.title,
                        "authors": [author.name for author in result.authors],
                        "abstract": result.summary.replace("\n", " "),
                        "url": result.entry_id,
                        "pdf_url": result.pdf_url,
                        "published": result.published.isoformat(),
                        "categories": result_categories,
                        "primary_category": result.primary_category,
                    }

                    papers.append(paper)

                logger.info(f"Fetched {len(papers)} papers")
                break

            except Exception as e:
                retry_count += 1
                logger.warning(
                    f"Error fetching papers (attempt {retry_count}/{max_retries}): {e}"
                )
                if retry_count < max_retries:
                    wait_time = 2**retry_count  # Exponential backoff
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("Max retries reached. Returning partial results.")

        # Rate limiting
        time.sleep(1 / self.rate_limit_delay)

        return papers

    def fetch_multiple_topics(
        self, topics: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch papers for multiple topics.

        Args:
            topics: List of topic configurations with 'name', 'query', and optional 'categories'

        Returns:
            Dictionary mapping topic names to lists of papers
        """
        results = {}

        for topic in topics:
            topic_name = topic["name"]
            query = topic["query"]
            categories = topic.get("categories", None)

            logger.info(f"Fetching papers for topic: {topic_name}")
            papers = self.fetch_papers(query, categories)
            results[topic_name] = papers

        return results


def main():
    """Example usage of the ArxivFetcher."""
    # Example configuration
    topics = [
        {
            "name": "Robotics Manipulation",
            "query": "cat:cs.RO AND (manipulation OR grasping OR dexterous)",
            "categories": ["cs.RO", "cs.CV"],
        },
        {
            "name": "Computer Vision",
            "query": "cat:cs.CV AND (3D OR reconstruction OR SLAM)",
            "categories": ["cs.CV"],
        },
    ]

    fetcher = ArxivFetcher(days_back=7, max_results=50)
    results = fetcher.fetch_multiple_topics(topics)

    # Print summary
    for topic_name, papers in results.items():
        print(f"\n{topic_name}: {len(papers)} papers")
        for i, paper in enumerate(papers[:3], 1):
            print(f"  {i}. {paper['title'][:80]}...")


if __name__ == "__main__":
    main()
