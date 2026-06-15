from enum import Enum


class TicketCategory(str, Enum):
    ACCESS_AND_IDENTITY = "access_and_identity"
    HARDWARE = "hardware"
    SOFTWARE = "software"
    NETWORK = "network"
    EMAIL = "email"
    SECURITY = "security"
    OTHER = "other"


class TicketPrefillCategory(str, Enum):
    CLOUD = "cloud"
    CYBERSECURITY = "cybersecurity"
    IDENTITY_ACCESS = "identity_access"
    DEVOPS = "devops"
    INTERNSHIP_HR = "internship_hr"
    GENERAL_IT = "general_it"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SupportTeam(str, Enum):
    SERVICE_DESK = "service_desk"
    IDENTITY_AND_ACCESS = "identity_and_access"
    INFRASTRUCTURE = "infrastructure"
    APPLICATION_SUPPORT = "application_support"
    NETWORK_OPERATIONS = "network_operations"
    SECURITY_OPERATIONS = "security_operations"


ALLOWED_CATEGORIES = tuple(item.value for item in TicketCategory)
ALLOWED_TICKET_PREFILL_CATEGORIES = tuple(
    item.value for item in TicketPrefillCategory
)
ALLOWED_PRIORITIES = tuple(item.value for item in TicketPriority)
ALLOWED_RISKS = tuple(item.value for item in RiskLevel)
ALLOWED_TEAMS = tuple(item.value for item in SupportTeam)

RISK_KEYWORDS = frozenset(
    {
        "breach",
        "compromised",
        "data leak",
        "exfiltration",
        "malware",
        "phishing",
        "ransomware",
        "stolen credentials",
        "unauthorized access",
        "zero-day",
    }
)
