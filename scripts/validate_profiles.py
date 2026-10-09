import os
import argparse
import requests

from dotenv import load_dotenv
from rocrate_validator import services

from utils import (
    get_profile_urls,
    get_changed_profile_urls,
    skip_profile,
    get_skipped_checks,
    validate_url_content_type,
)


def main(changed_only):
    invalid_count = 0
    skipped_count = 0
    error_count = 0

    if changed_only:
        profile_urls = get_changed_profile_urls(os.getenv('BASE_SHA'), os.getenv('HEAD_SHA'))
    else:
        profile_urls = get_profile_urls()

    for url in profile_urls:
        print(url)
        if skip_profile(url):
            skipped_count +=1
            print("skipped")
            continue

        try:
            validate_url_content_type(url)
        except ValueError as e:
            print(str(e))

        headers = {"Accept": "application/ld+json, application/json"}
        response = requests.get(url, headers=headers, allow_redirects=True)
        response.raise_for_status()
        crate_metadata = response.json()

        error_msgs = []

        settings = {
            "metadata_only": True,
            "metadata_dict": crate_metadata,
        }
        if skip_checks := get_skipped_checks(url):
            settings["skip_checks"] = skip_checks

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
            for msg in error_msgs:
                print(msg)

    if skipped_count != 0:
        print(f"{skipped_count} profiles skipped.")
    error_message = ""
    if invalid_count != 0:
        error_message += f"{invalid_count} invalid crate metadata found.\n"
    if error_count != 0:
        error_message += f"Error occured during validation for {error_count} profile(s).\n"
    if error_message:
        raise ValueError(error_message)

if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="Validate profile RO Crates")
    parser.add_argument("--changed-only", action="store_true")
    args = parser.parse_args()
    main(args.changed_only)
