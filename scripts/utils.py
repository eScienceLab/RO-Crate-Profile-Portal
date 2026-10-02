import requests
import validators


def get_profile_urls():
    with open("profile_urls.txt", "r") as file:
        profile_urls = [line.strip() for line in file if line.strip()]
    return profile_urls

def validate_url_content_type(url):
    if not validators.url(url):
        raise ValueError(f"{url} is not an URL")

    headers = {"Accept": "application/ld+json, application/json"}

    try:
        response = requests.head(url, headers=headers, allow_redirects=True)
    except requests.RequestException as e:
        raise ValueError(f"Unable to reach {url} (Error: {e})")

    # Fallback
    if response.status_code >= 400:
        response = requests.get(url, headers=headers)

    content_type = response.headers.get("Content-Type", "").lower()
    if "json" not in content_type:
        raise ValueError(f"{url} does not return JSON-LD (Content type: {content_type})")
