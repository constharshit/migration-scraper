from bs4 import BeautifulSoup, Comment

REMOVE_TAGS = {
    "script", "style", "noscript", "iframe", "svg",
    "link", "head", "nav", "footer", "aside",
    "form", "input", "button", "canvas",
}


def clean_html(html: str, max_chars: int = 60_000) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in REMOVE_TAGS:
        for el in soup.find_all(tag):
            el.decompose()

    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()

    # Strip most attributes, keep only semantic ones
    keep_attrs = {"href", "src", "alt", "datetime", "content"}
    for tag in soup.find_all(True):
        for attr in list(tag.attrs):
            if attr not in keep_attrs:
                del tag.attrs[attr]

    cleaned = str(soup)
    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars] + "\n<!-- [truncated] -->"
    return cleaned
