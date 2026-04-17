import json
import anthropic

SYSTEM_PROMPT = """You are a CMS content extraction specialist. You will be given the HTML of a CMS page.
Your job is to extract all meaningful content fields that a content author would need to re-enter in a new CMS.

Rules:
- Extract only what is present in the HTML. Never invent or paraphrase content.
- Use clear, snake_case field names that describe the content (e.g. hero_title, body_content, author_name).
- For images, return the full URL.
- For rich text / body content, return clean HTML (remove inline styles, ads, unrelated elements).
- For lists (tags, features, etc.), return an array of strings.
- Skip navigation, footer, cookie banners, ads, and other non-content elements.
- You MUST call the extract_content tool with your results."""

EXTRACT_TOOL = {
    "name": "extract_content",
    "description": "Store the extracted CMS content fields",
    "input_schema": {
        "type": "object",
        "properties": {
            "fields": {
                "type": "object",
                "description": "Key-value pairs of field_name -> field_value. Values can be strings, arrays, or null.",
                "additionalProperties": True,
            }
        },
        "required": ["fields"],
    },
}


def extract_fields(url: str, cleaned_html: str, client: anthropic.Anthropic) -> dict:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=[{
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }],
        tools=[EXTRACT_TOOL],
        tool_choice={"type": "tool", "name": "extract_content"},
        messages=[{
            "role": "user",
            "content": f"Page URL: {url}\n\nHTML:\n{cleaned_html}",
        }],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "extract_content":
            return block.input.get("fields", {})

    return {}
