# CMS Migration Scraper

Scrapes any CMS page and uses Claude AI to extract all content fields into structured JSON — so content authors copy-paste instead of re-type during migrations.

---

## How It Works

1. You give it a URL (or a list of URLs)
2. It fetches the page HTML and strips all noise (scripts, nav, ads, etc.)
3. Claude AI reads the cleaned HTML and identifies every meaningful content field
4. Output: one JSON file per page, ready for content authors

No CSS selectors. No manual field mapping. Claude figures it out.

---

## Quick Start

### Prerequisites
- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com/)

### Setup
```bash
# 1. Clone or unzip the project
cd migration-scraper

# 2. Install dependencies
pip install -e .

# 3. Add your API key
cp .env.example .env
# Edit .env and set: ANTHROPIC_API_KEY=sk-ant-...
```

### Run

**Preview a single page (prints to terminal, no files written):**
```bash
python -m scraper.cli preview https://example.com/blog/post-1
```

**Scrape one or more pages → writes JSON to ./output/:**
```bash
python -m scraper.cli scrape --url https://example.com/blog/post-1
python -m scraper.cli scrape --url https://example.com/p1 --url https://example.com/p2
```

**Scrape from a list of URLs (one per line):**
```bash
python -m scraper.cli scrape --url-file urls.txt
```

---

## Output

Each page produces a JSON file in `./output/pages/`:

```json
{
  "_meta": {
    "url": "https://example.com/blog/post-1",
    "scraped_at": "2026-04-16T10:30:00"
  },
  "hero_title": "10 Tips for Better Banking",
  "body_content": "<p>Managing your finances...</p>",
  "author_name": "Jane Smith",
  "publish_date": "2025-03-15",
  "tags": ["banking", "personal finance"],
  "cta_text": "Open an Account"
}
```

Content authors copy values directly into the new CMS — no re-typing.

---

## Current Cost (Pure AI Approach)

Using `claude-sonnet-4-6`. Average page after HTML cleaning: ~4,000 input tokens, ~800 output tokens.

| Scale | Estimated Cost |
|-------|---------------|
| 10 pages | ~$0.25 |
| 100 pages | ~$2.50 |
| 1,000 pages | ~$25 |

*Prompt caching is already enabled — system prompt is cached across all pages in a run, saving ~10% on top.*

---

## Roadmap & Improvements

### Option 1 — Template Schema Mapping *(Recommended next step)*
**What:** Define the target CMS field names in a YAML file. Claude maps extracted content to those exact field names instead of guessing.

**Why:** Ensures output JSON keys match the new CMS's content model exactly. Authors get `hero_title` not `main_heading`.

**Cost impact:** ~15% cheaper (fewer output tokens since Claude has a schema to fill).

**LOE:** 2–3 days

```yaml
# config/templates/blog_post.yaml
fields:
  - name: hero_title       # exact field name in new CMS
  - name: body_content
  - name: author_name
  - name: publish_date
```

---

### Option 2 — Hybrid CSS + AI Extraction
**What:** Define CSS selectors for predictable fields (title, date, image). Claude only handles ambiguous/complex fields (body content, tags, CTAs).

**Why:** Deterministic extraction for structured fields. AI only where needed.

**Cost impact:** ~40% cheaper ($15 per 1,000 pages vs $25).

**LOE:** 1 week (includes template YAML system)

---

### Option 3 — JS-Rendered Pages (Playwright)
**What:** Add Playwright browser automation for CMS pages built on React/Vue/Angular where HTML isn't in the page source.

**Why:** Currently only works on server-rendered pages. Many modern CMSs need this.

**Cost impact:** No change to AI cost. Slower scraping (~3–5 sec/page vs ~0.5 sec).

**LOE:** 2 days

---

### Option 4 — Web UI
**What:** Simple browser-based interface — paste URLs, click Scrape, download ZIP of JSON files.

**Why:** Non-technical users (project managers, content leads) can run it without touching a terminal.

**Cost impact:** None.

**LOE:** 3–4 days (Streamlit). Can be hosted free on [Streamlit Community Cloud](https://streamlit.io/cloud).

---

## Distribution Options

| Option | Effort | Who can run it |
|--------|--------|----------------|
| **Zip file** (current) | None | Anyone with Python + API key |
| **GitHub repo** | 30 min | Anyone with Python + API key |
| **Streamlit Cloud** (free hosting) | 3–4 days | Anyone with a browser |

For internal use now: share as a zip. For broader rollout: Streamlit Cloud is free and requires no infrastructure.

---

## Project Structure

```
migration-scraper/
├── scraper/
│   ├── cli.py          # CLI entry point
│   ├── fetcher.py      # HTTP page fetch
│   ├── cleaner.py      # HTML noise removal
│   ├── extractor.py    # Claude AI field extraction
│   └── output.py       # JSON file writer
├── .env.example        # API key template
└── pyproject.toml      # Dependencies
```
