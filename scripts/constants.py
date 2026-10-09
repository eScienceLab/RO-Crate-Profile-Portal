# Mapping of permitted profiles or checks to skip
# Usage:
# Add the profile url as a key and specify any exceptions:
# - "skip_profile": True to skip validation for the entire profile
# - "skip_checks": A list of Fully-Qualified-Check-IDs in the format
#   <Profile-ID>_<Requirement_#>.<RequirementCheck_#>, e.g. ro-crate-1.3_11.1
VALIDATION_EXCEPTIONS = {
    "https://w3id.org/ro/crate/1.3": {
        "skip_profile": True
    },
    "https://w3id.org/ro/wfrun/process/0.6": {
        "skip_checks": ["ro-crate-1.2_20.1"]
    }
}