# Deployment Guide

This guide explains how to deploy and use the journal_club (arXiv Paper Recommendation System).

## Quick Start

The system is already configured and ready to run. Simply push to GitHub and enable Actions.

### Local Testing

```bash
# Activate virtual environment
source venv/bin/activate

# Generate a digest
python src/generate_digest.py

# View the results
cat output/digest_latest.md
# Or open output/digest_latest.html in a browser
```

### Deploy to GitHub

```bash
# If not already done, push to your GitHub repository
git push origin master
```

### Enable GitHub Actions

1. Go to your repository on GitHub
2. Click on the "Actions" tab
3. If prompted, click "I understand my workflows, go ahead and enable them"
4. The workflow will now run automatically every Monday at 9 AM UTC
5. You can also trigger it manually by clicking "Run workflow"

## Configuration

### Customize Research Topics

Edit `config/topics.yaml` to match your research interests:

```yaml
topics:
  - name: "Your Topic Name"
    query: "cat:cs.XX AND (keyword1 OR keyword2)"
    categories: ["cs.XX", "cs.YY"]
    keywords:
      - keyword1
      - keyword2

research_interests: |
  Describe your research interests here. This text is used for
  semantic similarity matching with paper abstracts.
```

### Adjust Ranking Parameters

In `config/topics.yaml`, under the `ranking` section:

```yaml
ranking:
  min_relevance_threshold: 0.3  # Minimum similarity score (0-1)
  top_n_papers: 10              # Number of papers to include
  recency_weight: 0.1           # Boost for newer papers
  keyword_bonus: 0.05           # Bonus per keyword match
```

### Change Schedule

Edit `.github/workflows/weekly-digest.yml`:

```yaml
on:
  schedule:
    - cron: '0 9 * * 1'  # Monday 9 AM UTC
    # Format: minute hour day-of-month month day-of-week
```

Examples:
- Daily: `'0 9 * * *'`
- Twice weekly: `'0 9 * * 1,4'` (Monday and Thursday)
- Monthly: `'0 9 1 * *'` (1st of each month)

## Troubleshooting

### GitHub Actions fails with permission error

The workflow has been fixed with proper permissions. If you still see issues:

1. Go to Settings → Actions → General
2. Under "Workflow permissions", select "Read and write permissions"
3. Click "Save"

### No papers found

- Check that your query syntax is correct for arXiv
- Try broadening your search terms
- Check the arXiv API is accessible: https://export.arxiv.org/api/query?search_query=all

### Papers not relevant

- Update `research_interests` in `config/topics.yaml` to better describe your work
- Add more specific keywords
- Increase `min_relevance_threshold` in ranking config

## Features

- **Automatic fetching**: Pulls papers from arXiv based on your topics
- **Smart ranking**: Uses AI to match papers to your interests
- **Duplicate detection**: Tracks read papers to avoid showing them again
- **Multiple formats**: Generates both Markdown and HTML versions
- **Zero cost**: Runs entirely on free services

## File Structure

```
journal_club/
├── .github/workflows/
│   └── weekly-digest.yml     # Automation configuration
├── config/
│   └── topics.yaml           # Your research topics and settings
├── data/
│   └── read_papers.json      # Tracks papers you've seen
├── output/
│   ├── digest_YYYY-MM-DD.md  # Dated digests
│   ├── digest_latest.md      # Most recent digest
│   └── digest_YYYY-MM-DD.html # HTML versions
├── src/
│   ├── fetch_papers.py       # arXiv API integration
│   ├── rank_papers.py        # Ranking algorithm
│   ├── generate_digest.py    # Main orchestrator
│   └── utils.py              # Helper functions
└── requirements.txt          # Python dependencies
```

## Support

For issues or questions:
- Check the GitHub Actions logs for error messages
- Review the TODO.md for implementation details
- File an issue on the repository
