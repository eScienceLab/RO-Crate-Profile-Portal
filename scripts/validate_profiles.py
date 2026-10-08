import os
import argparse
import requests

from dotenv import load_dotenv
from rocrate_validator import services

from utils import get_profile_urls, get_changed_profile_urls, validate_url_content_type


def main(changed_only):
    invalid_count = 0

    if changed_only:
        profile_urls = get_changed_profile_urls(os.getenv('BASE_SHA'), os.getenv('HEAD_SHA'))
    else:
        profile_urls = get_profile_urls()

    for url in profile_urls:
        validate_url_content_type(url)

        headers = {"Accept": "application/ld+json, application/json"}
        response = requests.get(url, headers=headers, allow_redirects=True)
        response.raise_for_status()
        crate_metadata = response.json()

        error_msgs = []

        settings = {
            "metadata_only": True,
            "metadata_dict": crate_metadata,
        }
        profiles = services.detect_profiles(settings)
        if not profiles:
            error_msgs.append("The conformance to the profile(s) could not be verified.")

        for profile in profiles:
            settings["profile_identifier"] = profile.identifier
            result = services.validate(settings)
            if result.has_issues():
                for issue in result.get_issues():
                    error_msgs.append(f"Detected issue of severity {issue.severity.name} with check \"{issue.check.identifier}\": {issue.message}")

        if error_msgs:
            invalid_count += 1
            print(url)
            for msg in error_msgs:
                print(msg)

    if invalid_count != 0:
        raise ValueError(f"{invalid_count} invalid crate metadata found.")

if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="Validate profile RO Crates")
    parser.add_argument("--changed-only", action="store_true")
    args = parser.parse_args()
    main(args.changed_only)
