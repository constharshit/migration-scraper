import os
import json
import zipfile
import io
import streamlit as st
import anthropic

from scraper.fetcher import fetch_html
from scraper.cleaner import clean_html
from scraper.extractor import extract_fields

st.set_page_config(page_title="CMS Migration Scraper", page_icon="🔍", layout="wide")

st.title("CMS Migration Scraper")
st.caption("Paste URLs → Claude AI extracts all content fields → Download JSON for your content authors")

# API key — use Streamlit secrets in production, manual input as fallback
api_key = st.secrets.get("ANTHROPIC_API_KEY", "") if hasattr(st, "secrets") else ""
if not api_key:
    api_key = st.sidebar.text_input("Anthropic API Key", type="password",
                                     help="Get yours at console.anthropic.com")

st.sidebar.markdown("---")
st.sidebar.markdown("**How it works**")
st.sidebar.markdown("1. Paste one URL per line\n2. Click Scrape\n3. Download JSON files\n\nClaude AI identifies and extracts every content field automatically.")

# URL input
urls_input = st.text_area(
    "URLs to scrape (one per line)",
    height=150,
    placeholder="https://example.com/blog/post-1\nhttps://example.com/blog/post-2",
)

scrape_btn = st.button("Scrape", type="primary", disabled=not api_key)

if scrape_btn:
    urls = [u.strip() for u in urls_input.splitlines() if u.strip() and not u.startswith("#")]

    if not urls:
        st.warning("Please enter at least one URL.")
    else:
        client = anthropic.Anthropic(api_key=api_key)
        results = {}
        errors = {}

        progress = st.progress(0, text="Starting...")
        status = st.empty()

        for i, url in enumerate(urls):
            status.text(f"Processing {url}")
            try:
                html = fetch_html(url)
                cleaned = clean_html(html)
                fields = extract_fields(url, cleaned, client)
                results[url] = {
                    "_meta": {"url": url, "status": "success"},
                    **fields
                }
            except Exception as e:
                errors[url] = str(e)
                results[url] = {"_meta": {"url": url, "status": "failed", "error": str(e)}}

            progress.progress((i + 1) / len(urls), text=f"{i+1}/{len(urls)} done")

        status.empty()
        progress.empty()

        # Results
        success_count = len(urls) - len(errors)
        st.success(f"Done — {success_count}/{len(urls)} pages scraped successfully")

        if errors:
            with st.expander(f"{len(errors)} failed"):
                for url, err in errors.items():
                    st.error(f"{url}: {err}")

        # Preview results
        for url, data in results.items():
            meta = data.get("_meta", {})
            fields = {k: v for k, v in data.items() if k != "_meta"}
            label = f"{'✅' if meta.get('status') == 'success' else '❌'} {url}"
            with st.expander(label, expanded=len(urls) == 1):
                if fields:
                    for field, value in fields.items():
                        st.markdown(f"**{field}**")
                        if isinstance(value, list):
                            st.write(value)
                        elif isinstance(value, str) and len(value) > 200:
                            st.text_area("", value, height=100, key=f"{url}_{field}", label_visibility="collapsed")
                        else:
                            st.write(value)
                        st.divider()

        # Download as ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for url, data in results.items():
                filename = (url.replace("https://", "")
                              .replace("http://", "")
                              .replace("/", "__")[:100]) + ".json"
                zf.writestr(filename, json.dumps(data, indent=2, ensure_ascii=False))
        zip_buffer.seek(0)

        st.download_button(
            label="Download all as ZIP",
            data=zip_buffer,
            file_name="migration_content.zip",
            mime="application/zip",
        )
