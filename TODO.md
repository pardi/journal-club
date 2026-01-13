# arXiv Paper Recommendation System - TODO

A free, automated system to curate weekly/daily must-read research papers from arXiv.

---

## Phase 1: Core Setup (Week 1)

### Project Infrastructure
- [ ] Initialize Git repository
- [ ] Create GitHub repository (free tier)
- [ ] Set up project structure:
  ```
  paper-digest/
  ├── src/
  │   ├── fetch_papers.py
  │   ├── rank_papers.py
  │   ├── generate_digest.py
  │   └── utils.py
  ├── config/
  │   └── topics.yaml
  ├── data/
  │   └── read_papers.json
  ├── output/
  ├── requirements.txt
  ├── README.md
  └── .github/workflows/
  ```

### Environment Setup
- [ ] Create `requirements.txt`:
  ```
  arxiv
  sentence-transformers
  numpy
  pyyaml
  requests
  ```
- [ ] Test local installation with `pip install -r requirements.txt`
- [ ] Document Python version requirement (3.8+)

---

## Phase 2: Paper Fetching (Week 1-2)

### arXiv API Integration
- [ ] Implement `fetch_papers.py`:
  - [ ] Connect to arXiv API (free, no API key needed)
  - [ ] Query by topic/keywords
  - [ ] Filter by date range (last 7 days default)
  - [ ] Filter by categories (cs.RO, cs.CV, cs.AI, cs.LG)
  - [ ] Extract metadata: title, authors, abstract, URL, date, categories
  - [ ] Handle API rate limits (3 requests/second)
  - [ ] Add retry logic with exponential backoff

### Configuration System
- [ ] Create `config/topics.yaml`:
  ```yaml
  topics:
    - name: "Robotics Manipulation"
      query: "cat:cs.RO AND (manipulation OR grasping OR dexterous)"
      categories: ["cs.RO", "cs.CV"]
    - name: "Computer Vision"
      query: "cat:cs.CV AND (3D OR reconstruction OR SLAM)"
      categories: ["cs.CV"]
  ```
- [ ] Load configuration in Python
- [ ] Support multiple topic tracking

### Testing
- [ ] Test with sample queries
- [ ] Verify paper metadata extraction
- [ ] Check date filtering works correctly

---

## Phase 3: Ranking System (Week 2)

### Semantic Similarity
- [ ] Implement `rank_papers.py`:
  - [ ] Load sentence-transformers model (all-MiniLM-L6-v2 - small & fast)
  - [ ] Create embeddings for research interest description
  - [ ] Compute embeddings for paper title + abstract
  - [ ] Calculate cosine similarity scores
  - [ ] Sort papers by relevance

### Additional Scoring Factors
- [ ] Keyword matching bonus:
  - [ ] Define important keywords per topic
  - [ ] Add bonus score for keyword matches in title
- [ ] Recency weighting:
  - [ ] Newer papers get slight boost
- [ ] Author reputation (optional):
  - [ ] Manual list of known important researchers
  - [ ] Bonus score if author on list

### Filtering
- [ ] Set minimum relevance threshold (configurable)
- [ ] Exclude previously read papers:
  - [ ] Maintain `data/read_papers.json`
  - [ ] Check paper ID against history
- [ ] Limit to top N papers (default: 10)

---

## Phase 4: Digest Generation (Week 2-3)

### Output Formatting
- [ ] Implement `generate_digest.py`:
  - [ ] Create Markdown digest with:
    - [ ] Date header
    - [ ] Numbered list of papers
    - [ ] Title (linked to arXiv)
    - [ ] Authors (first 3-5)
    - [ ] Publication date
    - [ ] Abstract preview (first 300 chars)
    - [ ] Relevance score
    - [ ] Categories/tags
  - [ ] Save to `output/digest_YYYY-MM-DD.md`

### Alternative Formats
- [ ] Add HTML generation option
  - [ ] Simple CSS styling
  - [ ] Responsive design
  - [ ] Clickable links
- [ ] Add plain text format for email

### Read Tracking
- [ ] Update `data/read_papers.json` with displayed papers
- [ ] Add timestamp and topic metadata

---

## Phase 5: Automation (Week 3)

### GitHub Actions (Free)
- [ ] Create `.github/workflows/weekly-digest.yml`:
  ```yaml
  name: Weekly Paper Digest
  on:
    schedule:
      - cron: '0 9 * * 1'  # Monday 9 AM UTC
    workflow_dispatch:  # Manual trigger
  
  jobs:
    generate:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - uses: actions/setup-python@v4
          with:
            python-version: '3.10'
        - name: Install dependencies
          run: pip install -r requirements.txt
        - name: Generate digest
          run: python src/generate_digest.py
        - name: Commit results
          run: |
            git config user.name github-actions
            git config user.email github-actions@github.com
            git add output/ data/
            git commit -m "Weekly digest $(date +%Y-%m-%d)" || exit 0
            git push
  ```
- [ ] Test with manual workflow trigger
- [ ] Verify scheduled execution

### Alternative: Personal Computer Cron
- [ ] Create bash script `run_digest.sh`:
  ```bash
  #!/bin/bash
  cd /path/to/paper-digest
  source venv/bin/activate
  python src/generate_digest.py
  git add output/ data/
  git commit -m "Digest $(date +%Y-%m-%d)"
  git push
  ```
- [ ] Make executable: `chmod +x run_digest.sh`
- [ ] Add to crontab: `0 9 * * 1 /path/to/run_digest.sh`

---

## Phase 6: Delivery (Week 3-4)

### Free Delivery Options

#### Option A: GitHub Pages (Recommended)
- [ ] Enable GitHub Pages in repo settings
- [ ] Create `index.html` that lists all digests
- [ ] Auto-generate index in workflow
- [ ] Access at `username.github.io/paper-digest`

#### Option B: Email via GitHub Actions
- [ ] Set up free email service account (Gmail, Outlook)
- [ ] Add credentials as GitHub Secrets
- [ ] Use action to send email:
  ```yaml
  - name: Send email
    uses: dawidd6/action-send-mail@v3
    with:
      server_address: smtp.gmail.com
      server_port: 465
      username: ${{secrets.MAIL_USERNAME}}
      password: ${{secrets.MAIL_PASSWORD}}
      subject: Weekly Paper Digest
      body: file://output/digest_latest.md
      to: your@email.com
      from: Paper Digest Bot
  ```

#### Option C: Telegram Bot (Free)
- [ ] Create Telegram bot via @BotFather
- [ ] Get bot token (free)
- [ ] Add token to GitHub Secrets
- [ ] Send digest via Telegram API:
  ```python
  import requests
  
  def send_telegram(bot_token, chat_id, message):
      url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
      requests.post(url, json={"chat_id": chat_id, "text": message})
  ```

#### Option D: RSS Feed
- [ ] Generate `output/feed.xml` in Atom/RSS format
- [ ] Commit to GitHub
- [ ] Subscribe with any RSS reader (Feedly, Inoreader free tier)

---

## Phase 7: Enhancements (Optional)

### Better Summaries
- [ ] Add Claude API integration for summaries (free tier: limited)
- [ ] Alternative: Use free Hugging Face models locally
- [ ] Generate 2-3 sentence summaries

### Code Detection
- [ ] Check paper text for GitHub/code mentions
- [ ] Use GitHub API (free) to verify repo exists
- [ ] Add "📦 Code Available" badge

### Citation Tracking
- [ ] Integrate Semantic Scholar API (free):
  - [ ] Get citation counts
  - [ ] Track citation velocity
  - [ ] Identify highly-cited papers quickly
- [ ] Add citation count to digest

### Multi-Source Support
- [ ] Add OpenReview.net papers (ICLR, NeurIPS)
- [ ] Add Papers with Code API
- [ ] Add bioRxiv for bio/med papers

### Analytics Dashboard
- [ ] Track papers per topic over time
- [ ] Identify trending keywords
- [ ] Plot weekly paper counts
- [ ] Generate monthly summary report

### Notification System
- [ ] Discord webhook integration (free)
- [ ] Slack webhook (free)
- [ ] Push notifications via Pushover (free tier)

---

## Phase 8: Testing & Polish (Week 4)

### Testing
- [ ] Test with various arXiv queries
- [ ] Verify ranking quality
- [ ] Test automation runs successfully
- [ ] Check all file paths work in GitHub Actions
- [ ] Test manual workflow trigger

### Documentation
- [ ] Write comprehensive README.md:
  - [ ] Installation instructions
  - [ ] Configuration guide
  - [ ] Usage examples
  - [ ] Customization options
  - [ ] Troubleshooting
- [ ] Add inline code comments
- [ ] Create example configuration files
- [ ] Add screenshots/examples to README

### Code Quality
- [ ] Add error handling
- [ ] Add logging (to file and console)
- [ ] Add input validation
- [ ] Handle edge cases (no papers found, API errors)

---

## Phase 9: Launch (Week 4+)

### Deployment
- [ ] Push to GitHub
- [ ] Enable GitHub Actions
- [ ] Run first automated digest
- [ ] Verify delivery method works
- [ ] Set up monitoring (check GitHub Actions logs)

### Iteration
- [ ] Collect first month of digests
- [ ] Review paper quality
- [ ] Adjust relevance thresholds
- [ ] Refine topic queries
- [ ] Add/remove categories

---

## Maintenance

### Weekly
- [ ] Check GitHub Actions ran successfully
- [ ] Skim digest quality
- [ ] Mark false positives

### Monthly
- [ ] Review and update topic queries
- [ ] Check for new relevant arXiv categories
- [ ] Update keyword lists
- [ ] Review read paper history (clean old entries?)

### As Needed
- [ ] Update dependencies: `pip list --outdated`
- [ ] Check arXiv API changes
- [ ] Add new topics of interest

---

## Cost Breakdown (All Free!)

- **arXiv API**: Free, unlimited
- **GitHub**: Free (public repos, 2000 Actions minutes/month)
- **GitHub Pages**: Free hosting
- **Sentence Transformers**: Free, runs locally or in Actions
- **Semantic Scholar API**: Free (rate limited)
- **Telegram Bot**: Free
- **RSS hosting**: Free (via GitHub)
- **Email via Gmail/Outlook**: Free personal account

**Total Monthly Cost: $0**

---

## Quick Start Commands

```bash
# Clone and setup
git clone https://github.com/yourusername/paper-digest.git
cd paper-digest
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure topics
cp config/topics.example.yaml config/topics.yaml
# Edit config/topics.yaml with your interests

# Test run
python src/fetch_papers.py
python src/rank_papers.py
python src/generate_digest.py

# Check output
cat output/digest_latest.md
```

---

## Success Metrics

- [ ] System runs automatically every week without intervention
- [ ] 80%+ of top 10 papers are relevant to interests
- [ ] Discovering at least 2-3 genuinely interesting papers per week
- [ ] Zero manual work required after initial setup
- [ ] Total time savings: 30+ minutes per week of manual paper searching

---

## Future Ideas

- Mobile app for digest viewing
- Collaborative filtering (learn from what papers you actually read)
- Integration with Zotero/Mendeley for automatic library import
- Paper relationship graphs (citations, similar papers)
- Community sharing (share your digests with others)
- Machine learning to improve ranking over time
