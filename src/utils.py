"""
Utility functions for the paper digest system.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def format_authors(authors: List[str], max_authors: int = 5) -> str:
    """
    Format author list for display.

    Args:
        authors: List of author names
        max_authors: Maximum number of authors to show

    Returns:
        Formatted author string
    """
    if len(authors) <= max_authors:
        return ", ".join(authors)
    else:
        shown = ", ".join(authors[:max_authors])
        remaining = len(authors) - max_authors
        return f"{shown}, et al. (+{remaining} more)"


def save_read_papers(paper_ids: List[str], data_file: str = "data/read_papers.json"):
    """
    Save paper IDs to read papers tracking file.

    Args:
        paper_ids: List of paper IDs to mark as read
        data_file: Path to tracking file
    """
    os.makedirs(os.path.dirname(data_file), exist_ok=True)

    # Load existing data
    if os.path.exists(data_file):
        try:
            with open(data_file, "r") as f:
                data = json.load(f)
        except Exception as e:
            logger.warning(f"Error loading read papers file: {e}")
            data = {"paper_ids": [], "history": []}
    else:
        data = {"paper_ids": [], "history": []}

    # Add new paper IDs
    existing_ids = set(data.get("paper_ids", []))
    new_ids = [pid for pid in paper_ids if pid not in existing_ids]

    if new_ids:
        data["paper_ids"].extend(new_ids)

        # Add to history
        history_entry = {
            "date": datetime.now().isoformat(),
            "paper_ids": new_ids,
            "count": len(new_ids),
        }
        data.setdefault("history", []).append(history_entry)

        # Save
        with open(data_file, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Added {len(new_ids)} papers to read history")
    else:
        logger.info("No new papers to add to history")


def create_html_digest(papers: List[Dict[str, Any]], output_file: str):
    """
    Generate HTML formatted digest.

    Args:
        papers: List of ranked papers
        output_file: Path to save HTML file
    """
    logger.info("Generating HTML digest")

    date_str = datetime.now().strftime("%Y-%m-%d")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>arXiv Paper Digest - {date_str}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .meta {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 30px;
        }}
        .paper {{
            margin-bottom: 30px;
            padding: 20px;
            background-color: #fafafa;
            border-left: 4px solid #3498db;
            border-radius: 4px;
        }}
        .paper h2 {{
            color: #2c3e50;
            margin-top: 0;
            font-size: 1.3em;
        }}
        .paper h2 a {{
            color: #2c3e50;
            text-decoration: none;
        }}
        .paper h2 a:hover {{
            color: #3498db;
        }}
        .paper-meta {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin: 10px 0;
        }}
        .paper-meta strong {{
            color: #555;
        }}
        .abstract {{
            margin: 15px 0;
            color: #555;
        }}
        .links {{
            margin-top: 15px;
        }}
        .links a {{
            display: inline-block;
            padding: 6px 12px;
            margin-right: 10px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        .links a:hover {{
            background-color: #2980b9;
        }}
        .score {{
            display: inline-block;
            padding: 4px 8px;
            background-color: #2ecc71;
            color: white;
            border-radius: 3px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        .topic-tag {{
            display: inline-block;
            padding: 4px 8px;
            background-color: #9b59b6;
            color: white;
            border-radius: 3px;
            font-size: 0.85em;
            margin-left: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>arXiv Paper Digest - {date_str}</h1>
        <p class="meta">Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p class="meta">Found {len(papers)} relevant papers.</p>
        <hr>
"""

    for i, paper in enumerate(papers, 1):
        authors_str = format_authors(paper["authors"], max_authors=5)
        pub_date = datetime.fromisoformat(paper["published"]).strftime("%Y-%m-%d")
        categories = ", ".join(paper["categories"][:3])

        abstract = paper["abstract"][:300]
        if len(paper["abstract"]) > 300:
            abstract += "..."

        matched_topic = paper.get("matched_topic", "")
        topic_tag = (
            f'<span class="topic-tag">{matched_topic}</span>' if matched_topic else ""
        )

        html += f"""
        <div class="paper">
            <h2>{i}. <a href="{paper["url"]}" target="_blank">{paper["title"]}</a></h2>

            <div class="paper-meta">
                <strong>Authors:</strong> {authors_str}
            </div>

            <div class="paper-meta">
                <strong>Published:</strong> {pub_date} |
                <strong>Categories:</strong> {categories}
            </div>

            <div class="paper-meta">
                <span class="score">Relevance: {paper["similarity_score"]:.3f}</span>
                {topic_tag}
"""

        if paper.get("keyword_matches", 0) > 0:
            html += f" <em>(Keyword matches: {paper['keyword_matches']})</em>"

        html += f"""
            </div>

            <div class="abstract">
                <strong>Abstract:</strong> {abstract}
            </div>

            <div class="links">
                <a href="{paper["pdf_url"]}" target="_blank">PDF</a>
                <a href="{paper["url"]}" target="_blank">arXiv Page</a>
            </div>
        </div>
"""

    html += """
    </div>
</body>
</html>
"""

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        f.write(html)

    logger.info(f"Saved HTML digest to {output_file}")


def load_config(config_file: str = "config/topics.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_file: Path to config file

    Returns:
        Configuration dictionary
    """
    import yaml

    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
            return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        raise
