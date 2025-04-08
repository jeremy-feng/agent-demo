"""A tool to convert a website into LLM-ready markdown text."""

import requests


def web_to_markdown(url: str) -> str:
    """Convert website into LLM-ready markdown text.

    This tool uses the md.dhr.wtf API to convert website into LLM-ready markdown text.
    The API is free for up to 5 requests per minute.

    Args:
        url: The url of the website to convert.

    Returns:
        The markdown text of the website.
    """
    response = requests.get(f"https://md.dhr.wtf/?url={url}")
    return response.text
