import os
import click
import anthropic
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import track
from rich.table import Table

from scraper.fetcher import fetch_html
from scraper.cleaner import clean_html
from scraper.extractor import extract_fields
from scraper.output import save_result

load_dotenv()
console = Console(force_terminal=True)


@click.group()
def main():
    """CMS Migration Scraper - extract structured content from CMS pages using AI."""
    pass


@main.command()
@click.option("--url", multiple=True, help="URL(s) to scrape")
@click.option("--url-file", type=click.Path(exists=True), help="File with one URL per line")
@click.option("--output-dir", default="./output", show_default=True, help="Output directory")
def scrape(url, url_file, output_dir):
    """Scrape CMS pages and extract content fields to JSON."""
    urls = list(url)

    if url_file:
        with open(url_file) as f:
            urls += [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not urls:
        click.echo("Error: No URLs provided. Use --url or --url-file.")
        raise click.Abort()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        click.echo("Error: ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key.")
        raise click.Abort()

    client = anthropic.Anthropic(api_key=api_key)
    out_dir = Path(output_dir)
    results = []

    click.echo(f"Scraping {len(urls)} page(s)...")

    for i, u in enumerate(urls, 1):
        click.echo(f"[{i}/{len(urls)}] {u}")
        try:
            click.echo("  Fetching HTML...")
            html = fetch_html(u)
            cleaned = clean_html(html)
            click.echo(f"  Cleaned: {len(html):,} -> {len(cleaned):,} chars. Calling Claude...")
            fields = extract_fields(u, cleaned, client)
            path = save_result(u, fields, out_dir)
            click.echo(f"  Done: {len(fields)} fields -> {path}")
            results.append((u, "success", str(path), len(fields)))
        except Exception as e:
            click.echo(f"  Failed: {e}")
            results.append((u, "failed", str(e), 0))

    click.echo(f"\nOutput directory: {out_dir.resolve()}")
    click.echo(f"Success: {sum(1 for r in results if r[1] == 'success')}/{len(results)}")


@main.command()
@click.argument("url")
def preview(url):
    """Scrape a single URL and print extracted fields to stdout (no file written)."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        click.echo("Error: ANTHROPIC_API_KEY not set.")
        raise click.Abort()

    client = anthropic.Anthropic(api_key=api_key)

    click.echo(f"Fetching {url}...")
    html = fetch_html(url)
    cleaned = clean_html(html)
    click.echo(f"Cleaned: {len(html):,} -> {len(cleaned):,} chars")
    click.echo("Calling Claude...")

    fields = extract_fields(url, cleaned, client)

    click.echo(f"\nExtracted {len(fields)} fields:\n")
    for name, value in fields.items():
        display = str(value)
        if len(display) > 200:
            display = display[:200] + "..."
        click.echo(f"  {name}: {display}")


if __name__ == "__main__":
    main()
