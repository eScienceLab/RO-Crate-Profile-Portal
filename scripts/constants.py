# Mapping of permitted profiles or checks to skip
# Usage:
# Add the profile url as a key and specify any exceptions:
# - "skip_profile": True to skip validation for the entire profile
# - "skip_checks": A list of Fully-Qualified-Check-IDs in the format
#   <Profile-ID>_<Requirement_#>.<RequirementCheck_#>, e.g. ro-crate-1.3_11.1
VALIDATION_EXCEPTIONS = {
    # RO-Crate 1.2 & 1.3 have:
    #   * previous versions and a citation dataset linked which should not be part of `hasPart` on the root data entity
    #   * `cite-as` and `vann:preferredNamespaceUri` strings which match an entity `@id` but should not be made into cross references
    "https://w3id.org/ro/crate/1.2": {
        "skip_checks": ["ro-crate-1.2_10.0", "ro-crate-1.2_24.1", "ro-crate-1.2_4.3"]
    },
    "https://w3id.org/ro/crate/1.3": {
        "skip_checks": ["ro-crate-1.3_10.0", "ro-crate-1.3_24.1", "ro-crate-1.3_4.3"]
    },
    # WRROC profiles have a citation dataset linked which should not be part of `hasPart` on the root data entity
    "https://w3id.org/ro/wfrun/process/0.6": {
        "skip_checks": ["ro-crate-1.3_10.0", "ro-crate-1.3_24.1"]
    },
    "https://w3id.org/ro/wfrun/workflow/0.6": {
        "skip_checks": ["ro-crate-1.3_10.0", "ro-crate-1.3_24.1"]
    },
    "https://w3id.org/ro/wfrun/provenance/0.6": {
        "skip_checks": ["ro-crate-1.3_10.0", "ro-crate-1.3_24.1"]
    },
    # Workflow RO-Crate includes generic ComputerLanguage entities without a version
    "https://about.workflowhub.eu/Workflow-RO-Crate/ro-crate-metadata.json": {
        "skip_checks": ["ro-crate-1.3_32.0"]
    },
}
