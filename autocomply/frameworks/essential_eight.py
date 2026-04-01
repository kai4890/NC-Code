"""
ASD Essential Eight controls for AutoComply.

Contains all 8 ASD Essential Eight mitigation strategies at Maturity Levels 1, 2, and 3,
as published by the Australian Signals Directorate (ASD).
"""

from typing import Dict, List


def get_ml1_controls() -> List[Dict[str, str]]:
    """Return the list of ASD Essential Eight controls at Maturity Level 1.

    Returns:
        List of 8 control dicts.
    """
    return [
        {
            "control_id": "E8.1-ML1",
            "control_text": (
                "Application control shall be implemented to prevent execution of "
                "unapproved or malicious programs including executables, software libraries, "
                "scripts and installers."
            ),
            "framework": "Essential Eight ML1",
        },
        {
            "control_id": "E8.2-ML1",
            "control_text": (
                "Applications and devices shall be patched or updated within one month of "
                "a vulnerability being identified."
            ),
            "framework": "Essential Eight ML1",
        },
        {
            "control_id": "E8.3-ML1",
            "control_text": (
                "Microsoft Office macro settings shall be configured to block macros "
                "originating from the internet."
            ),
            "framework": "Essential Eight ML1",
        },
        {
            "control_id": "E8.4-ML1",
            "control_text": (
                "User application hardening shall be implemented to disable unneeded "
                "features in web browsers, Microsoft Office, and PDF viewers."
            ),
            "framework": "Essential Eight ML1",
        },
        {
            "control_id": "E8.5-ML1",
            "control_text": (
                "Administrative privileges shall be restricted to only those users who "
                "require them to perform their assigned duties."
            ),
            "framework": "Essential Eight ML1",
        },
        {
            "control_id": "E8.6-ML1",
            "control_text": (
                "Operating systems shall be patched or updated within one month of a "
                "vulnerability being identified, and unsupported operating systems shall "
                "not be used."
            ),
            "framework": "Essential Eight ML1",
        },
        {
            "control_id": "E8.7-ML1",
            "control_text": (
                "Multi-factor authentication shall be implemented for users authenticating "
                "to internet-facing services and third-party cloud services."
            ),
            "framework": "Essential Eight ML1",
        },
        {
            "control_id": "E8.8-ML1",
            "control_text": (
                "Backups of important data, software and configuration settings shall be "
                "performed and retained in a non-rewritable and non-erasable manner."
            ),
            "framework": "Essential Eight ML1",
        },
    ]


def get_ml3_controls() -> List[Dict[str, str]]:
    """Return the list of ASD Essential Eight controls at Maturity Level 3.

    Returns:
        List of 8 control dicts.
    """
    return [
        {
            "control_id": "E8.1-ML3",
            "control_text": (
                "Application control shall be implemented on all endpoints and servers to "
                "restrict execution to an approved allowlist. Microsoft's recommended block "
                "rules shall be implemented to prevent execution of unapproved applications."
            ),
            "framework": "Essential Eight ML3",
        },
        {
            "control_id": "E8.2-ML3",
            "control_text": (
                "Applications and devices shall be patched, updated or mitigated within 48 "
                "hours of a vulnerability with an extreme risk rating being identified."
            ),
            "framework": "Essential Eight ML3",
        },
        {
            "control_id": "E8.3-ML3",
            "control_text": (
                "Microsoft Office macro settings shall be configured to block macros "
                "originating from the internet, and only allow execution of digitally "
                "signed macros verified by a designated technical authority."
            ),
            "framework": "Essential Eight ML3",
        },
        {
            "control_id": "E8.4-ML3",
            "control_text": (
                "User application hardening shall be implemented to disable unneeded "
                "features, restrict Microsoft Office from creating executable content, "
                "and prevent web browsers from processing web advertisements."
            ),
            "framework": "Essential Eight ML3",
        },
        {
            "control_id": "E8.5-ML3",
            "control_text": (
                "Administrative privileges shall be strictly controlled, with privileged "
                "access restricted to dedicated privileged administrative workstations "
                "utilising just-in-time and just-enough-access principles."
            ),
            "framework": "Essential Eight ML3",
        },
        {
            "control_id": "E8.6-ML3",
            "control_text": (
                "Operating systems shall be patched or mitigated within 48 hours of a "
                "vulnerability with an extreme risk rating being identified. Unsupported "
                "operating systems must be strictly isolated."
            ),
            "framework": "Essential Eight ML3",
        },
        {
            "control_id": "E8.7-ML3",
            "control_text": (
                "Phishing-resistant multi-factor authentication shall be enforced for all "
                "users authenticating to internet-facing services, third-party cloud "
                "services, and for all remote access."
            ),
            "framework": "Essential Eight ML3",
        },
        {
            "control_id": "E8.8-ML3",
            "control_text": (
                "Backups shall be performed at least daily, retained in an isolated, "
                "non-rewritable and non-erasable manner, and tested at least quarterly."
            ),
            "framework": "Essential Eight ML3",
        },
    ]


def get_controls() -> List[Dict[str, str]]:
    """Return the list of ASD Essential Eight controls at Maturity Level 2.

    Each control is a dict with three keys:
        control_id   — Essential Eight reference (e.g. "E8.1")
        control_text — Full "shall" requirement statement
        framework    — Always "Essential Eight ML2"

    Returns:
        List of 8 control dicts.
    """
    return [
        {
            "control_id": "E8.1",
            "control_text": (
                "Application control shall be implemented to prevent execution of "
                "unauthorised software, scripts, executables and libraries on workstations "
                "and servers, using an approved allowlist."
            ),
            "framework": "Essential Eight ML2",
        },
        {
            "control_id": "E8.2",
            "control_text": (
                "Applications shall be patched and updated within 30 days of a security "
                "patch release to remediate vulnerabilities in internet-facing services, "
                "office productivity suites and web browsers."
            ),
            "framework": "Essential Eight ML2",
        },
        {
            "control_id": "E8.3",
            "control_text": (
                "Microsoft Office macro settings shall be configured to block macros "
                "originating from the internet, with only digitally signed macros from "
                "trusted publishers permitted to execute."
            ),
            "framework": "Essential Eight ML2",
        },
        {
            "control_id": "E8.4",
            "control_text": (
                "User application hardening shall be implemented to disable or remove "
                "unneeded features in web browsers, office productivity suites and PDF "
                "viewers to reduce the attack surface available to adversaries."
            ),
            "framework": "Essential Eight ML2",
        },
        {
            "control_id": "E8.5",
            "control_text": (
                "Administrative privileges shall be restricted to only those users who "
                "require privileged access, with separate privileged accounts used, and "
                "just-in-time and just-enough-access principles enforced."
            ),
            "framework": "Essential Eight ML2",
        },
        {
            "control_id": "E8.6",
            "control_text": (
                "Operating systems shall be patched within 30 days of a security patch "
                "release, and unsupported operating systems shall be replaced to maintain "
                "protection against known vulnerabilities."
            ),
            "framework": "Essential Eight ML2",
        },
        {
            "control_id": "E8.7",
            "control_text": (
                "Multi-factor authentication shall be implemented for all remote access "
                "connections, all privileged user accounts, and access to important data "
                "repositories and cloud services."
            ),
            "framework": "Essential Eight ML2",
        },
        {
            "control_id": "E8.8",
            "control_text": (
                "Regular backups of important data, software and configuration settings "
                "shall be performed and tested for successful restoration to ensure "
                "data recovery capability in the event of a cyber incident."
            ),
            "framework": "Essential Eight ML2",
        },
    ]
