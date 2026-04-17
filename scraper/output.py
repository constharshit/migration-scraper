import json
from pathlib import Path
from datetime import datetime, timezone


def save_result(url: str, fields: dict, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_name = (
        url.replace("https://", "")
           .replace("http://", "")
           .replace("/", "__")
           .replace("?", "_")
           .replace("=", "-")
           [:120]
    )

    data = {
        "_meta": {
            "url": url,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        },
        **fields,
    }

    path = output_dir / f"{safe_name}.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
