"""
Domain-term keyword rules for AutoComply hybrid scoring.

Provides DOMAIN_TERMS (category → keyword list), CONTROL_CATEGORIES (control
ID → relevant category keys), and keyword_score() for lightweight lexical
signal to complement semantic embedding similarity.
"""

from typing import Dict, List

# ---------------------------------------------------------------------------
# Domain vocabulary — one list per compliance category
# ---------------------------------------------------------------------------

DOMAIN_TERMS: Dict[str, List[str]] = {
    "policy_governance": [
        "policy", "policies", "governance", "framework", "procedure", "procedures",
        "standard", "standards", "directive", "guideline", "guidelines", "approved",
        "documented", "communicated", "reviewed", "published", "compliance",
        "requirements", "obligations", "roles", "responsibilities", "management",
    ],
    "access_control": [
        "access", "authentication", "authorisation", "authorization", "privilege",
        "privileges", "privileged", "least privilege", "mfa", "multi-factor",
        "multifactor", "password", "credential", "credentials", "provisioning",
        "deprovisioning", "revoking", "remote access", "vpn", "identity",
        "role-based", "rbac", "account", "user account", "single sign-on", "sso",
    ],
    "risk_management": [
        "risk", "risks", "risk assessment", "risk register", "threat", "threats",
        "vulnerability", "vulnerabilities", "mitigation", "treatment", "residual",
        "likelihood", "impact", "exposure", "risk appetite", "risk tolerance",
        "risk management", "risk analysis",
    ],
    "incident_response": [
        "incident", "incidents", "breach", "breaches", "compromise", "response",
        "reporting", "notification", "triage", "escalation", "containment",
        "eradication", "recovery", "lessons learned", "post-incident", "forensic",
        "investigation", "detect", "detection",
    ],
    "encryption": [
        "encryption", "encrypted", "encrypt", "cryptographic", "cryptography",
        "key management", "keys", "aes", "tls", "ssl", "cipher", "hashing",
        "hash", "at rest", "in transit", "pki", "certificate", "digital signature",
        "decryption",
    ],
    "backup_continuity": [
        "backup", "backups", "restore", "restoration", "recovery", "disaster recovery",
        "business continuity", "bcp", "dr plan", "rto", "rpo", "archive", "retention",
        "offsite", "replication", "continuity", "failover", "resilience",
    ],
    "patch_management": [
        "patch", "patches", "patching", "update", "updates", "vulnerability",
        "cve", "remediation", "security update", "hotfix", "firmware", "version",
        "upgrade", "exploit", "mitigation", "release", "fix",
    ],
    "application_control": [
        "application control", "allowlist", "whitelist", "blacklist", "denylist",
        "executable", "executables", "library", "libraries", "scripts", "macro",
        "macros", "sandboxing", "code signing", "hardening", "browser", "pdf viewer",
        "office", "unapproved software",
    ],
    "asset_management": [
        "asset", "assets", "inventory", "register", "asset register", "hardware",
        "software", "information assets", "lifecycle", "decommission", "ownership",
        "classification", "labelling", "cmdb",
    ],
    "supplier_management": [
        "supplier", "suppliers", "vendor", "vendors", "third-party", "third party",
        "contractor", "contractors", "sub-contractor", "supply chain", "procurement",
        "outsourcing", "agreement", "contract", "due diligence",
    ],
    "physical_security": [
        "physical security", "physical access", "perimeter", "cctv", "badge",
        "visitor", "facility", "secure area", "clean desk", "screen lock",
        "tailgating", "lockable", "server room", "data centre", "data center",
        "restricted area",
    ],
    "disp_specific": [
        "disp", "defence industry", "security clearance", "clearance", "classified",
        "secret", "official", "protected", "adf", "australian defence", "dsm",
        "security officer", "personnel security", "defence security",
    ],
    "essential_eight": [
        "essential eight", "asd", "acsc", "australian signals directorate",
        "maturity level", "application control", "multi-factor", "mfa",
        "admin privileges", "macro", "patch", "backup", "hardening",
    ],
    "awareness_training": [
        "awareness", "training", "education", "security awareness", "phishing",
        "social engineering", "induction", "onboarding", "refresher",
        "annual training", "security culture", "staff training", "e-learning",
        "insider threat",
    ],
    "audit_logging": [
        "audit", "log", "logging", "monitoring", "siem", "event", "review",
        "audit trail", "accountability", "non-repudiation", "detection", "alerting",
        "alert", "retention", "centralized", "audit log", "security log",
    ],
}

# ---------------------------------------------------------------------------
# Control → category mappings
# (each control ID maps to the 1–3 categories most relevant to its requirement)
# ---------------------------------------------------------------------------

CONTROL_CATEGORIES: Dict[str, List[str]] = {
    # ISO 27001 Annex A
    "A.5.1":  ["policy_governance"],
    "A.6.1":  ["policy_governance"],
    "A.6.2":  ["access_control", "policy_governance"],
    "A.7.2":  ["awareness_training"],
    "A.8.1":  ["asset_management"],
    "A.9.1":  ["access_control", "policy_governance"],
    "A.9.2":  ["access_control"],
    "A.9.4":  ["access_control"],
    "A.10.1": ["encryption"],
    "A.11.1": ["physical_security"],
    "A.12.1": ["policy_governance"],
    "A.12.3": ["backup_continuity"],
    "A.12.6": ["patch_management"],
    "A.13.1": ["access_control"],
    "A.14.1": ["policy_governance"],
    "A.15.1": ["supplier_management"],
    "A.16.1": ["incident_response"],
    "A.17.1": ["backup_continuity"],
    "A.18.1": ["policy_governance"],
    "A.18.2": ["audit_logging", "policy_governance"],
    # DISP
    "DISP.1":  ["disp_specific"],
    "DISP.2":  ["physical_security", "disp_specific"],
    "DISP.3":  ["disp_specific", "access_control"],
    "DISP.4":  ["disp_specific", "access_control", "encryption"],
    "DISP.5":  ["policy_governance", "disp_specific"],
    "DISP.6":  ["encryption", "disp_specific"],
    "DISP.7":  ["incident_response", "disp_specific"],
    "DISP.8":  ["supplier_management", "disp_specific"],
    "DISP.9":  ["audit_logging", "disp_specific"],
    "DISP.10": ["awareness_training", "disp_specific"],
    # Essential Eight ML1
    "E8.1-ML1": ["application_control", "essential_eight"],
    "E8.2-ML1": ["patch_management", "essential_eight"],
    "E8.3-ML1": ["application_control", "essential_eight"],
    "E8.4-ML1": ["application_control", "essential_eight"],
    "E8.5-ML1": ["access_control", "essential_eight"],
    "E8.6-ML1": ["patch_management", "essential_eight"],
    "E8.7-ML1": ["access_control", "essential_eight"],
    "E8.8-ML1": ["backup_continuity", "essential_eight"],
    # Essential Eight ML2
    "E8.1": ["application_control", "essential_eight"],
    "E8.2": ["patch_management", "essential_eight"],
    "E8.3": ["application_control", "essential_eight"],
    "E8.4": ["application_control", "essential_eight"],
    "E8.5": ["access_control", "essential_eight"],
    "E8.6": ["patch_management", "essential_eight"],
    "E8.7": ["access_control", "essential_eight"],
    "E8.8": ["backup_continuity", "essential_eight"],
    # Essential Eight ML3
    "E8.1-ML3": ["application_control", "essential_eight"],
    "E8.2-ML3": ["patch_management", "essential_eight"],
    "E8.3-ML3": ["application_control", "essential_eight"],
    "E8.4-ML3": ["application_control", "essential_eight"],
    "E8.5-ML3": ["access_control", "essential_eight"],
    "E8.6-ML3": ["patch_management", "essential_eight"],
    "E8.7-ML3": ["access_control", "essential_eight"],
    "E8.8-ML3": ["backup_continuity", "essential_eight"],
}

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def keyword_score(control_id: str, clause: str) -> float:
    """Return a lexical relevance score between 0.0 and 1.0.

    Collects all domain terms for the control's categories, counts how many
    distinct terms appear in the clause (case-insensitive), and normalises so
    that 8 or more matches → 1.0.

    Args:
        control_id: Framework control ID (e.g. "A.9.1", "DISP.4", "E8.2-ML1").
        clause:     Document clause string to score.

    Returns:
        Float in [0.0, 1.0]. Returns 0.0 for unknown control IDs.
    """
    categories = CONTROL_CATEGORIES.get(control_id)
    if not categories:
        return 0.0

    clause_lower = clause.lower()
    terms: List[str] = []
    for cat in categories:
        terms.extend(DOMAIN_TERMS.get(cat, []))

    hits = sum(1 for term in set(terms) if term in clause_lower)
    return min(hits / 8.0, 1.0)
