# Journal Club: arXiv Paper Recommendation System

A free, automated system to curate weekly/daily must-read research papers from arXiv based on your research interests.

## 🔗 View Latest Digest

**Live Site:** https://pardi.github.io/journal-club/

The digests are automatically updated every Monday at 9 AM UTC.

## Features

- Automatically fetch papers from arXiv based on configurable topics
- Rank papers using semantic similarity to your research interests
- Generate formatted digests (Markdown, HTML, plain text)
- Track previously read papers to avoid duplicates

## Requirements

- Python 3.8+
- pip

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/journal_club.git
cd journal_club

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. Edit `config/topics.yaml` to define your research interests:

```yaml
topics:
  - name: "Robotics Manipulation"
    query: "cat:cs.RO AND (manipulation OR grasping OR dexterous)"
    categories: ["cs.RO", "cs.CV"]
  - name: "Computer Vision"
    query: "cat:cs.CV AND (3D OR reconstruction OR SLAM)"
    categories: ["cs.CV"]
```

## Usage

### Manual Run

```bash
# Generate a new digest
python src/generate_digest.py

# Check the output
cat output/digest_latest.md
```

## Project Structure

```
journal_club/
├── src/
│   ├── fetch_papers.py      # Fetch papers from arXiv API
│   ├── rank_papers.py        # Rank papers by relevance
│   ├── generate_digest.py    # Generate formatted digest
│   └── utils.py              # Utility functions
├── config/
│   └── topics.yaml           # Topic configuration
├── data/
│   └── read_papers.json      # Track read papers
├── output/                   # Generated digests
├── requirements.txt          # Python dependencies
└── README.md
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

