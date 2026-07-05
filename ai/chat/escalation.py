import re
from dataclasses import dataclass

from ai.config.constants import TicketPrefillCategory
from ai.schemas.chat import ChatResponse, TicketPrefill


SECURITY_PATTERNS = (
    r"\bphish(?:ing|ed)?\b",
    r"\bsecurity threat\b",
    r"\bcyber(?:\s|-)?attack\b",
    r"\bmalware\b",
    r"\bransomware\b",
    r"\bdata (?:leak|breach)\b",
    r"\bcompromised\b",
    r"\bunauthori[sz]ed access\b",
    r"\bstolen credentials?\b",
)

PRIVILEGED_ACCESS_PATTERNS = (
    r"\badmin(?:istrator)? access\b",
    r"\badmin(?:istrator)? rights?\b",
    r"\bproduction access\b",
    r"\baccess to (?:the )?production\b",
    r"\broot access\b",
    r"\bsudo\b",
    r"\bprivilege(?:d|s)?\b",
    r"\bassign .{0,20}(?:permission|role)\b",
    r"\b(?:permission|role).{0,20}(?:assign|grant)\b",
    r"\bpermission assignment\b",
    r"\brole assignment\b",
    r"\baccount unlock\b",
    r"\baccount (?:is )?locked\b",
    r"\bunlock (?:my|the|this|an?) account\b",
    r"\breset .{0,40}(?:admin|root|privileged).{0,20}password\b",
    r"\b(?:admin|root|privileged).{0,40}password reset\b",
    r"\bpassword reset.{0,40}(?:admin|root|privileged) account\b",
)

OTHER_USER_TICKET_PATTERNS = (
    r"\b(?:another|other) user(?:'s|s')? ticket\b",
    r"\bsomeone else(?:'s)? ticket\b",
    r"\b(?:show|read|view|open|get).{0,30}\buser .{0,30}\bticket\b",
    r"\b(?:show|read|view|open|get).{0,30}\b(?:his|her|their) ticket\b",
    r"\b(?:show|read|view|open|get)\s+(?!my\b)[\w-]+'s ticket\b",
)


@dataclass(frozen=True)
class EscalationDecision:
    required: bool
    response: str = ""
    ticket_prefill: TicketPrefill | None = None
    reason: str | None = None


def _matches_any(message: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, message, flags=re.IGNORECASE) for pattern in patterns)


GREETING_PATTERNS = (
    r"^\s*(hi|hello|hey|good\s+(morning|afternoon|evening)|howdy|greetings|what'?s\s+up|good\s+day)\s*$",
    r"^\s*(help|support|assist)\s*$",
    r"^\s*(start|begin|menu|categories|topics|issues)\s*$",
)

SMALL_TALK_PATTERNS = (
    r"^\s*(thanks?|thank you|thx|ty|appreciate)\s*$",
    r"^\s*(ok|okay|got it|understood|alright)\s*$",
    r"^\s*(bye|goodbye|see you|later|exit|quit|close)\s*$",
)


def _is_greeting(message: str) -> bool:
    return any(re.search(p, message, flags=re.IGNORECASE) for p in GREETING_PATTERNS)


def _is_small_talk(message: str) -> bool:
    return any(re.search(p, message, flags=re.IGNORECASE) for p in SMALL_TALK_PATTERNS)


CATEGORY_TREE: list[dict] = [
    {
        "id": "security",
        "label": "Security",
        "icon": "SH",
        "subcategories": [
            {"id": "phishing", "label": "Phishing & Suspicious Email", "keywords": ["phishing", "suspicious", "email", "link", "scam"]},
            {"id": "malware", "label": "Malware or Virus", "keywords": ["malware", "virus", "infected", "ransomware"]},
            {"id": "breach", "label": "Data Breach or Compromise", "keywords": ["breach", "compromised", "unauthorized access", "stolen"]},
        ],
    },
    {
        "id": "it_access",
        "label": "IT & Access",
        "icon": "IT",
        "subcategories": [
            {"id": "password", "label": "Password Reset", "keywords": ["password", "reset", "forgot", "locked"]},
            {"id": "laptop", "label": "Laptop Setup or Issue", "keywords": ["laptop", "computer", "device", "new hire", "onboarding"]},
            {"id": "access", "label": "Account or Access Request", "keywords": ["access", "permission", "account", "role", "grant"]},
        ],
    },
    {
        "id": "cloud",
        "label": "Cloud",
        "icon": "CL",
        "subcategories": [
            {"id": "azalio", "label": "Azalio Platform", "keywords": ["azalio", "platform", "environment"]},
            {"id": "cloud_access", "label": "Cloud Access & Provisioning", "keywords": ["cloud", "vm", "virtual machine", "aws", "azure", "provision"]},
            {"id": "myid", "label": "MYID Overview", "keywords": ["myid", "identity", "overview"]},
        ],
    },
    {
        "id": "email",
        "label": "Email",
        "icon": "EM",
        "subcategories": [
            {"id": "email_config", "label": "Email Configuration", "keywords": ["email", "configuration", "setup", "outlook", "mail"]},
        ],
    },
    {
        "id": "network",
        "label": "Network",
        "icon": "NW",
        "subcategories": [
            {"id": "vpn", "label": "VPN Setup", "keywords": ["vpn", "remote", "connection", "connect"]},
        ],
    },
    {
        "id": "hr",
        "label": "HR & Onboarding",
        "icon": "HR",
        "subcategories": [
            {"id": "intern", "label": "Intern Onboarding", "keywords": ["intern", "internship", "onboarding", "new hire"]},
        ],
    },
]


def _category_tree_response(message: str) -> ChatResponse | None:
    if _is_greeting(message):
        return ChatResponse(
            response=(
                "Hello! I am the SPS SecureDesk AI assistant. "
                "I can help with common IT and security questions using our knowledge base. "
                "Choose a category below to get started, or describe your issue directly."
            ),
            sources=[],
            escalate=False,
            suggested_categories=CATEGORY_TREE,
        )
    if _is_small_talk(message):
        lower = message.strip().lower()
        if any(p in lower for p in ("bye", "goodbye", "see you", "later", "exit", "quit", "close")):
            return ChatResponse(
                response="Goodbye! If you need help later, just start a new chat.",
                sources=[],
                escalate=False,
                suggested_categories=None,
            )
        return ChatResponse(
            response="Feel free to browse the categories below or describe your issue.",
            sources=[],
            escalate=False,
            suggested_categories=CATEGORY_TREE,
        )
    return None


def _subject(message: str, fallback: str) -> str:
    compact = " ".join(message.split())
    return (compact[:197] + "...") if len(compact) > 200 else (compact or fallback)


def _ticket_excerpt(message: str) -> str:
    compact = " ".join(message.split())
    return compact[:1_500]


def assess_escalation(
    message: str,
    *,
    repeated_count: int = 1,
) -> EscalationDecision:
    if _matches_any(message, OTHER_USER_TICKET_PATTERNS):
        return EscalationDecision(
            required=True,
            response=(
                "I cannot access or discuss another user's tickets. "
                "A support agent can review your authorized request."
            ),
            ticket_prefill=TicketPrefill(
                subject="Request involving another user's ticket",
                description=(
                    "The request involves another user's ticket and requires identity "
                    "and authorization verification by a support agent."
                ),
                category=TicketPrefillCategory.IDENTITY_ACCESS,
            ),
            reason="other_user_ticket",
        )

    if _matches_any(message, SECURITY_PATTERNS):
        return EscalationDecision(
            required=True,
            response=(
                "This may be a security incident and requires the security team. "
                "Would you like me to create a high-priority support ticket?"
            ),
            ticket_prefill=TicketPrefill(
                subject=_subject(message, "Potential security incident"),
                description=(
                    f"User reported a potential security incident: {_ticket_excerpt(message)} "
                    "This requires immediate review by the security team."
                ),
                category=TicketPrefillCategory.CYBERSECURITY,
            ),
            reason="security",
        )

    if _matches_any(message, PRIVILEGED_ACCESS_PATTERNS):
        return EscalationDecision(
            required=True,
            response="This requires a support agent.",
            ticket_prefill=TicketPrefill(
                subject=_subject(message, "Privileged access request"),
                description=(
                    f"User requested a privileged account or access action: "
                    f"{_ticket_excerpt(message)} This requires human approval."
                ),
                category=TicketPrefillCategory.IDENTITY_ACCESS,
            ),
            reason="privileged_access",
        )

    if repeated_count >= 3:
        return EscalationDecision(
            required=True,
            response=(
                "This issue remains unresolved after repeated attempts and requires "
                "a support agent."
            ),
            ticket_prefill=TicketPrefill(
                subject=_subject(message, "Repeated unresolved helpdesk question"),
                description=(
                    "The user asked the same question three times without resolution. "
                    "A support agent should review the request and conversation."
                ),
                category=TicketPrefillCategory.GENERAL_IT,
            ),
            reason="repeated_question",
        )

    return EscalationDecision(required=False)


def no_answer_escalation(message: str) -> EscalationDecision:
    return EscalationDecision(
        required=True,
        response=(
            "I do not have this in our knowledge base. "
            "Would you like me to create a support ticket?"
        ),
        ticket_prefill=TicketPrefill(
            subject=_subject(message, "Knowledge-base answer unavailable"),
            description=(
                f"No sufficiently relevant knowledge-base answer was found for: "
                f"{_ticket_excerpt(message)}"
            ),
            category=TicketPrefillCategory.GENERAL_IT,
        ),
        reason="no_kb_answer",
    )


def guardrail_escalation(message: str) -> EscalationDecision:
    return EscalationDecision(
        required=True,
        response=(
            "I cannot provide a safe knowledge-base-grounded answer. "
            "Would you like me to create a support ticket?"
        ),
        ticket_prefill=TicketPrefill(
            subject=_subject(message, "AI response requires agent review"),
            description=(
                "The AI response did not pass grounding or safety validation. "
                f"User question: {_ticket_excerpt(message)}"
            ),
            category=TicketPrefillCategory.GENERAL_IT,
        ),
        reason="guardrail",
    )
