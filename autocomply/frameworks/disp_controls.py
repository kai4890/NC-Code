"""
DISP (Defence Industry Security Program) controls for AutoComply.

Contains 10 hardcoded DISP requirements for Australian Defence sector
organisations.  These reflect the key obligations under the Defence Industry
Security Program administered by the Australian Department of Defence.
"""

from typing import Dict, List


def get_controls() -> List[Dict[str, str]]:
    """Return the list of DISP compliance controls.

    Each control is a dict with three keys:
        control_id   — DISP reference (e.g. "DISP.1")
        control_text — Full "shall" requirement statement
        framework    — Always "DISP"

    Returns:
        List of 10 control dicts.
    """
    return [
        {
            "control_id": "DISP.1",
            "control_text": (
                "The organisation shall hold the appropriate DISP membership level "
                "commensurate with the level of defence work undertaken and the "
                "classification of information accessed."
            ),
            "framework": "DISP",
        },
        {
            "control_id": "DISP.2",
            "control_text": (
                "Physical security controls shall be implemented and maintained for all "
                "areas where defence assets, classified information and sensitive defence "
                "materials are handled or stored."
            ),
            "framework": "DISP",
        },
        {
            "control_id": "DISP.3",
            "control_text": (
                "Personnel security screening shall be conducted for all staff who access "
                "classified defence information, with appropriate security clearances "
                "obtained, maintained and regularly reviewed."
            ),
            "framework": "DISP",
        },
        {
            "control_id": "DISP.4",
            "control_text": (
                "Information and cyber security controls shall meet DISP requirements "
                "and protect classified and sensitive defence information from "
                "unauthorised access, disclosure or compromise."
            ),
            "framework": "DISP",
        },
        {
            "control_id": "DISP.5",
            "control_text": (
                "A security governance framework shall be established, including the "
                "appointment of a Security Officer and documented security policies, "
                "procedures and responsibilities for defence security management."
            ),
            "framework": "DISP",
        },
        {
            "control_id": "DISP.6",
            "control_text": (
                "Classified information shall be stored and transmitted securely in "
                "accordance with Australian Government security classification requirements "
                "and Defence security instructions."
            ),
            "framework": "DISP",
        },
        {
            "control_id": "DISP.7",
            "control_text": (
                "Security incidents, breaches and suspected compromises shall be reported "
                "to Defence Security in a timely manner in accordance with DISP incident "
                "reporting obligations and procedures."
            ),
            "framework": "DISP",
        },
        {
            "control_id": "DISP.8",
            "control_text": (
                "Sub-contractors and third parties engaged in defence work shall meet "
                "equivalent security requirements and hold appropriate DISP membership "
                "or personnel security clearances before accessing defence information."
            ),
            "framework": "DISP",
        },
        {
            "control_id": "DISP.9",
            "control_text": (
                "Annual security reviews shall be conducted to assess ongoing compliance "
                "with DISP requirements and identify areas requiring remediation or "
                "improvement to security controls."
            ),
            "framework": "DISP",
        },
        {
            "control_id": "DISP.10",
            "control_text": (
                "All staff shall receive security awareness training specific to defence "
                "requirements, covering classification handling, insider threat awareness, "
                "foreign interference and DISP obligations."
            ),
            "framework": "DISP",
        },
    ]
