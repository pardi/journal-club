"""
Generate paper digest from arXiv papers.
Main orchestrator that ties together fetching, ranking, and formatting.
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import yaml

from fetch_papers import ArxivFetcher
from rank_papers import PaperRanker
from utils import create_html_digest, format_authors, save_read_papers

# Get project root directory (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DigestGenerator:
    """Generate paper digest."""

    def __init__(self, config_file: str = "config/topics.yaml"):
        """
        Initialize the digest generator.

        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = self.load_config()
        self.fetcher = ArxivFetcher(days_back=7, max_results=100)
        self.ranker = PaperRanker()

        # Set research interests from config
        research_interests = self.config.get("research_interests", "")
        if research_interests:
            self.ranker.set_research_interests(research_interests)
        else:
            logger.warning("No research interests defined in config")

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_file, "r") as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded configuration from {self.config_file}")
                return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise

    def fetch_all_papers(self) -> List[Dict[str, Any]]:
        """Fetch papers for all configured topics."""
        topics = self.config.get("topics", [])
        if not topics:
            logger.warning("No topics configured")
            return []

        all_papers = []
        topic_results = self.fetcher.fetch_multiple_topics(topics)

        # Combine papers from all topics and deduplicate
        seen_ids = set()
        for topic_name, papers in topic_results.items():
            for paper in papers:
                if paper["id"] not in seen_ids:
                    paper["matched_topic"] = topic_name
                    all_papers.append(paper)
                    seen_ids.add(paper["id"])

        logger.info(f"Fetched {len(all_papers)} unique papers across all topics")
        return all_papers

    def rank_all_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank papers using configured parameters."""
        ranking_config = self.config.get("ranking", {})

        # Collect all keywords from topics
        all_keywords = []
        for topic in self.config.get("topics", []):
            all_keywords.extend(topic.get("keywords", []))

        ranked_papers = self.ranker.rank_papers(
            papers,
            keywords=all_keywords,
            min_threshold=ranking_config.get("min_relevance_threshold", 0.3),
            top_n=ranking_config.get("top_n_papers", 10),
            keyword_bonus=ranking_config.get("keyword_bonus", 0.05),
            recency_weight=ranking_config.get("recency_weight", 0.1),
            filter_read=True,
        )

        return ranked_papers

    def generate_markdown_digest(
        self, papers: List[Dict[str, Any]], output_file: str = None
    ) -> str:
        """
        Generate Markdown formatted digest.

        Args:
            papers: List of ranked papers
            output_file: Optional path to save digest

        Returns:
            Markdown formatted string
        """
        logger.info("Generating Markdown digest")

        date_str = datetime.now().strftime("%Y-%m-%d")

        lines = [
            f"# arXiv Paper Digest - {date_str}",
            "",
            f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            f"Found {len(papers)} relevant papers.",
            "",
            "---",
            "",
        ]

        for i, paper in enumerate(papers, 1):
            # Title with link
            lines.append(f"## {i}. [{paper['title']}]({paper['url']})")
            lines.append("")

            # Authors
            authors_str = format_authors(paper["authors"], max_authors=5)
            lines.append(f"**Authors:** {authors_str}")
            lines.append("")

            # Metadata
            pub_date = datetime.fromisoformat(paper["published"]).strftime("%Y-%m-%d")
            lines.append(f"**Published:** {pub_date}")
            lines.append("")

            # Categories
            categories = ", ".join(paper["categories"][:3])
            lines.append(f"**Categories:** {categories}")
            lines.append("")

            # Relevance score
            lines.append(f"**Relevance Score:** {paper['similarity_score']:.3f}")
            if paper.get("keyword_matches", 0) > 0:
                lines.append(f" (Keyword matches: {paper['keyword_matches']})")
            lines.append("")

            # Matched topic
            if "matched_topic" in paper:
                lines.append(f"**Topic:** {paper['matched_topic']}")
                lines.append("")

            # Abstract
            abstract = paper["abstract"][:300]
            if len(paper["abstract"]) > 300:
                abstract += "..."
            lines.append(f"**Abstract:** {abstract}")
            lines.append("")

            # Links
            lines.append(f"[PDF]({paper['pdf_url']}) | [arXiv]({paper['url']})")
            lines.append("")
            lines.append("---")
            lines.append("")

        digest = "\n".join(lines)

        # Save to file if specified
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, "w") as f:
                f.write(digest)
            logger.info(f"Saved digest to {output_file}")

        return digest

    def generate(self):
        """Generate the complete digest."""
        logger.info("=" * 60)
        logger.info("Starting digest generation")
        logger.info("=" * 60)

        # Fetch papers
        papers = self.fetch_all_papers()

        if not papers:
            logger.warning("No papers found. Exiting.")
            return

        # Rank papers
        ranked_papers = self.rank_all_papers(papers)

        if not ranked_papers:
            logger.warning("No papers passed ranking threshold. Exiting.")
            return

        # Generate outputs
        date_str = datetime.now().strftime("%Y-%m-%d")

        # Markdown digest
        md_file = f"output/digest_{date_str}.md"
        self.generate_markdown_digest(ranked_papers, md_file)

        # Also create a "latest" version
        latest_file = "output/digest_latest.md"
        self.generate_markdown_digest(ranked_papers, latest_file)

        # HTML digest
        html_file = f"output/digest_{date_str}.html"
        create_html_digest(ranked_papers, html_file)

        # Update read papers
        save_read_papers([p["id"] for p in ranked_papers])

        logger.info("=" * 60)
        logger.info(f"Digest generation complete!")
        logger.info(f"Markdown: {md_file}")
        logger.info(f"HTML: {html_file}")
        logger.info("=" * 60)


def main():
    """Main entry point."""
    generator = DigestGenerator()
    generator.generate()


if __name__ == "__main__":
    main()
