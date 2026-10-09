import requests
import subprocess
import validators

from constants import VALIDATION_EXCEPTIONS


def get_profile_urls():
    with open("profile_urls.txt", "r") as file:
        profile_urls = [line.strip() for line in file if line.strip()]
    return profile_urls

def get_changed_profile_urls(base_sha, head_sha):
    result = subprocess.run(
        ["git", "diff", "--unified=0", base_sha, head_sha, "--", "profile_urls.txt"],
        capture_output=True,
        text=True,
        check=True,
    )
    profile_urls = []
    for line in result.stdout.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            profile_urls.append(line[1:])
    return profile_urls

def skip_profile(profile_url):
    return VALIDATION_EXCEPTIONS.get(profile_url, {}).get("skip_profile", False)

def get_skipped_checks(profile_url):
    return VALIDATION_EXCEPTIONS.get(profile_url, {}).get("skip_checks", [])

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
