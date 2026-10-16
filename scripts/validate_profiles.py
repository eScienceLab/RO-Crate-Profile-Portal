import sys
import argparse
import requests

from rocrate_validator import services
from rocrate_validator.models import ValidationResult
from rocrate_validator.utils.io_helpers.output.console import Console
from rocrate_validator.utils.io_helpers.output.text import TextOutputFormatter

from utils import (
    get_profile_urls,
    get_changed_profile_urls,
    skip_profile,
    get_skipped_checks,
    validate_url_content_type,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Validate profile RO Crates")
    parser.add_argument("--changed-only", action="store_true")
    parser.add_argument("--base-sha")
    parser.add_argument("--head-sha")

    args = parser.parse_args()

    if args.changed_only and (not args.base_sha or not args.head_sha):
        parser.error("--changed-only requires both --base-sha and --head-sha")

    return args


def main():
    invalid_count = 0
    skipped_count = 0
    error_count = 0

    args = parse_args()
    console = Console()
    console.register_formatter(TextOutputFormatter())

    if args.changed_only:
        profile_urls = get_changed_profile_urls(args.base_sha, args.head_sha)
    else:
        profile_urls = get_profile_urls()

    for url in profile_urls:
        print(url)
        if skip_profile(url):
            skipped_count +=1
            print("  Profile skipped.\n")
            continue

        try:
            validate_url_content_type(url)
        except ValueError as e:
            error_count += 1
            print(str(e))
            continue

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
            error_msgs.append("  The conformance to the profile(s) could not be verified.")
        for profile in profiles:
            settings["profile_identifier"] = profile.identifier
            result = services.validate(settings)
            if result.has_issues():
                error_msgs.append(result)

        if error_msgs:
            invalid_count += 1
            for msg in error_msgs:
                if isinstance(msg, ValidationResult):
                    console.print(msg)
                else: 
                    print(msg)
        else:
            print("  Profile valid.")
        if skip_checks:
            print(f"  Skipped checks: {skip_checks}.")
        print()

    if skipped_count != 0:
        print(f"{skipped_count} profiles skipped.")
    if invalid_count != 0:
        print(f"{invalid_count} profiles have invalid crate metadata.")
    if error_count != 0:
        print(f"Error occured during validation for {error_count} profiles.")
    if invalid_count + error_count != 0:
        return 1

if __name__ == "__main__":
    sys.exit(main())
