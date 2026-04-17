# CMS Migration Scraper

Python CLI tool that scrapes CMS pages and uses Claude AI to extract structured content fields into JSON for migration projects.

## Architecture

Pure AI extraction pipeline — no CSS selectors required:

```
URL → fetch_html() → clean_html() → Claude API (tool use) → JSON output
```

- `scraper/fetcher.py` — requests-based HTTP fetch (static/SSR pages only)
- `scraper/cleaner.py` — strips scripts, nav, footer, ads; keeps content structure
- `scraper/extractor.py` — single Claude API call per page using tool use for structured output; system prompt is prompt-cached
- `scraper/output.py` — writes per-page JSON to `./output/`
- `scraper/cli.py` — Click CLI with `preview` (terminal only) and `scrape` (writes files) commands

## Running

```bash
pip install -e .
# Set ANTHROPIC_API_KEY in .env
python -m scraper.cli preview https://example.com/page
python -m scraper.cli scrape --url https://example.com/page
python -m scraper.cli scrape --url-file urls.txt
```

## Key Decisions

- **Tool use over JSON prompting** — `extract_content` tool guarantees schema-compliant output
- **Prompt caching on system prompt** — `cache_control: ephemeral` reduces cost ~10% on batch runs
- **Single API call per page** — all fields extracted in one call, not one call per field
- **HTML cleaning before AI** — reduces token count by ~60–80% before sending to Claude

## Planned Improvements (see README)

1. Template schema YAML — map output keys to target CMS field names
2. Hybrid CSS + AI — CSS selectors for structured fields, AI for complex ones
3. Playwright support — JS-rendered / SPA pages
4. Streamlit web UI — browser-based interface for non-technical users
