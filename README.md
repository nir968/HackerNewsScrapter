# 🚀 HackerNews Scraper Pipeline

A simple, robust Python tool to grab the newest posts from HackerNews. Filter by points, and stop exactly when you hit your post limit.

## 🛠️ Get Started

### 1\. Setup

Get your environment ready and install the necessary dependencies:

```bash
# Activate your environment first
.\venv\Scripts\Activate

# Install everything you need (requests, BeautifulSoup, and testing tools)
pip install requests beautifulsoup4 pytest requests-mock
```

### 2\. How to Run

Run the script using `python main.py`, customizing the process with the following options:

| Option | What it does | Example |
| :--- | :--- | :--- |
| `--min-score` | Minimum points required for a post. | `50` |
| `--max-posts` | **STOPS** the scraper immediately after collecting this many posts. | `15` |
| `--skip-pages` | Pages to completely ignore (e.g., to skip page 3 and 5). | `3 5` |

**Example Command:**

```bash
python main.py --min-score 100 --max-posts 12 --output-file cool_posts.csv
```

## ✅ Verification & Testing

This project is fully tested. Running the unit tests confirms that the parsing, filtering, and the crucial stopping mechanism all work perfectly.

```bash
# Run all verification tests
pytest
```

**If you see this, you’re good to go:**

```
===================== 5 passed in 0.xxs =====================
```

## ✨ Core Features

  * **Smart Stopping:** Guarantees the scraper stops exactly at the `--max-posts` limit.
  * **Reliable Parsing:** Accurate extraction of Title, Author, Points, and Comments.
  * **Full Coverage:** Unit tests ensure logic remains sound even if site data changes.
