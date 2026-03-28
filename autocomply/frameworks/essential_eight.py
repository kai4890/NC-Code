"""
ASD Essential Eight controls for AutoComply.

Contains all 8 ASD Essential Eight mitigation strategies at Maturity Level 2,
as published by the Australian Signals Directorate (ASD).
"""

from typing import Dict, List


def get_controls() -> List[Dict[str, str]]:
    """Return the list of ASD Essential Eight controls at Maturity Level 2.

    Each control is a dict with three keys:
        control_id   — Essential Eight reference (e.g. "E8.1")
        control_text — Full "shall" requirement statement
        framework    — Always "Essential Eight"

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
            "framework": "Essential Eight",
        },
        {
            "control_id": "E8.2",
            "control_text": (
                "Applications shall be patched and updated within 30 days of a security "
                "patch release to remediate vulnerabilities in internet-facing services, "
                "office productivity suites and web browsers."
            ),
            "framework": "Essential Eight",
        },
        {
            "control_id": "E8.3",
            "control_text": (
                "Microsoft Office macro settings shall be configured to block macros "
                "originating from the internet, with only digitally signed macros from "
                "trusted publishers permitted to execute."
            ),
            "framework": "Essential Eight",
        },
        {
            "control_id": "E8.4",
            "control_text": (
                "User application hardening shall be implemented to disable or remove "
                "unneeded features in web browsers, office productivity suites and PDF "
                "viewers to reduce the attack surface available to adversaries."
            ),
            "framework": "Essential Eight",
        },
        {
            "control_id": "E8.5",
            "control_text": (
                "Administrative privileges shall be restricted to only those users who "
                "require privileged access, with separate privileged accounts used, and "
                "just-in-time and just-enough-access principles enforced."
            ),
            "framework": "Essential Eight",
        },
        {
            "control_id": "E8.6",
            "control_text": (
                "Operating systems shall be patched within 30 days of a security patch "
                "release, and unsupported operating systems shall be replaced to maintain "
                "protection against known vulnerabilities."
            ),
            "framework": "Essential Eight",
        },
        {
            "control_id": "E8.7",
            "control_text": (
                "Multi-factor authentication shall be implemented for all remote access "
                "connections, all privileged user accounts, and access to important data "
                "repositories and cloud services."
            ),
            "framework": "Essential Eight",
        },
        {
            "control_id": "E8.8",
            "control_text": (
                "Regular backups of important data, software and configuration settings "
                "shall be performed and tested for successful restoration to ensure "
                "data recovery capability in the event of a cyber incident."
            ),
            "framework": "Essential Eight",
        },
    ]
