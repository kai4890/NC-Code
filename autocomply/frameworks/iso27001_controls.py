"""
ISO 27001 Annex A controls for AutoComply.

Contains 20 hardcoded ISO 27001:2022 Annex A "shall" requirements used as
the reference baseline for semantic gap analysis.
"""

from typing import Dict, List


def get_controls() -> List[Dict[str, str]]:
    """Return the list of ISO 27001 Annex A controls.

    Each control is a dict with three keys:
        control_id   — Annex A reference (e.g. "A.5.1")
        control_text — Full "shall" requirement statement
        framework    — Always "ISO 27001"

    Returns:
        List of 20 control dicts.
    """
    return [
        {
            "control_id": "A.5.1",
            "control_text": (
                "Information security policies shall be defined, approved by management, "
                "published and communicated to all employees and relevant external parties."
            ),
            "framework": "ISO 27001",
        },
        {
            "control_id": "A.6.1",
            "control_text": (
                "Information security roles and responsibilities shall be assigned, "
                "clearly defined and documented across the organisation."
            ),
            "framework": "ISO 27001",
        },
        {
            "control_id": "A.6.2",
            "control_text": (
                "Mobile device and remote working policies shall be defined and implemented "
                "to manage the risks of using mobile devices and working remotely."
            ),
            "framework": "ISO 27001",
        },
        {
            "control_id": "A.7.2",
            "control_text": (
                "All employees and contractors shall receive appropriate security awareness "
                "education and training relevant to their role and the organisation's "
                "information security requirements."
            ),
            "framework": "ISO 27001",
        },
        {
            "control_id": "A.8.1",
            "control_text": (
                "Assets associated with information and information processing facilities "
                "shall be identified, inventoried and ownership assigned."
            ),
            "framework": "ISO 27001",
        },
        {
            "control_id": "A.9.1",
            "control_text": (
                "An access control policy shall be established, documented and reviewed "
                "based on business and information security requirements."
            ),
            "framework": "ISO 27001",
        },
        {
            "control_id": "A.9.2",
            "control_text": (
                "User access provisioning shall be formally managed through a documented "
                "process for assigning and revoking access rights to information systems."
            ),
            "framework": "ISO 27001",
        },
        {
            "control_id": "A.9.4",
            "control_text": (
                "Information systems and applications shall restrict access to authorised "
                "users only and prevent unauthorised access to system functions."
            ),
            "framework": "ISO 27001",
        },
        {
            "control_id": "A.10.1",
            "control_text": (
                "A cryptographic controls policy shall be implemented and maintained to "
                "govern the use of encryption and key management for protection of information."
            ),
            "framework": "ISO 27001",
        },
        {
            "control_id": "A.11.1",
            "control_text": (
                "Physical security perimeters shall be defined and used to protect areas "
                "containing sensitive or critical information and information processing facilities."
            ),
            "framework": "ISO 27001",
        },
        {
            "control_id": "A.12.1",
            "control_text": (
                "Operating procedures for information processing facilities shall be "
                "documented, maintained and made available to all users who need them."
            ),
            "framework": "ISO 27001",
        },
        {
            "control_id": "A.12.3",
            "control_text": (
                "Backup copies of information, software and system images shall be taken "
                "and regularly tested for restoration in accordance with an agreed backup policy."
            ),
            "framework": "ISO 27001",
        },
        {
            "control_id": "A.12.6",
            "control_text": (
                "Technical vulnerabilities of information systems shall be managed by "
                "evaluating exposure to vulnerabilities and applying appropriate mitigation measures."
            ),
            "framework": "ISO 27001",
        },
        {
            "control_id": "A.13.1",
            "control_text": (
                "Networks shall be managed and controlled to protect information in systems "
                "and applications through implemented network security controls."
            ),
            "framework": "ISO 27001",
        },
        {
            "control_id": "A.14.1",
            "control_text": (
                "Information security requirements shall be included in requirements for new "
                "information systems or enhancements to existing information systems."
            ),
            "framework": "ISO 27001",
        },
        {
            "control_id": "A.15.1",
            "control_text": (
                "Information security requirements for mitigating risks associated with "
                "supplier access shall be agreed and documented in supplier agreements."
            ),
            "framework": "ISO 27001",
        },
        {
            "control_id": "A.16.1",
            "control_text": (
                "Information security incidents shall be reported, assessed and responded "
                "to in a consistent and effective manner, with lessons learned documented."
            ),
            "framework": "ISO 27001",
        },
        {
            "control_id": "A.17.1",
            "control_text": (
                "Business continuity planning shall include information security continuity "
                "to ensure the continuity of security controls during adverse situations."
            ),
            "framework": "ISO 27001",
        },
        {
            "control_id": "A.18.1",
            "control_text": (
                "Legal, statutory, regulatory and contractual requirements relevant to "
                "information security shall be identified and documented for each information system."
            ),
            "framework": "ISO 27001",
        },
        {
            "control_id": "A.18.2",
            "control_text": (
                "Information security practices shall be independently reviewed at planned "
                "intervals or when significant changes occur to ensure continued suitability."
            ),
            "framework": "ISO 27001",
        },
    ]
