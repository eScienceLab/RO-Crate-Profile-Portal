import requests

from rocrate_validator import services

from utils import get_profile_urls, validate_url_content_type


def main():
    profile_urls = get_profile_urls()

    for url in profile_urls:
        validate_url_content_type(url)

        headers = {"Accept": "application/ld+json, application/json"}
        response = requests.get(url, headers=headers, allow_redirects=True)
        response.raise_for_status()
        crate_metadata = response.json()

        settings = services.ValidationSettings(metadata_only=True, metadata_dict=crate_metadata)
        result = services.validate(settings)
        if result.has_issues():
            print(url)
            for issue in result.get_issues():
                print(f"Detected issue of severity {issue.severity.name} with check \"{issue.check.identifier}\": {issue.message}")

if __name__ == "__main__":
    main()