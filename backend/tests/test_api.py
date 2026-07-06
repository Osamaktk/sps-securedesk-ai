import os
import re
import sys
from datetime import datetime, timezone
from typing import Any

try:
    import requests
except ImportError:
    print("Missing dependency: requests")
    print("Install it with: pip install requests")
    sys.exit(1)


BASE_URL = os.getenv("SECUREDESK_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
CURRENT_YEAR = "2026"
PASSWORD = "Test1234!"
ACCOUNTS = {
    "intern": {"email": "intern@sps.com", "password": PASSWORD},
    "agent": {"email": "agent@sps.com", "password": PASSWORD},
    "secadmin": {"email": "secadmin@sps.com", "password": PASSWORD},
}


class ApiTestRunner:
    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0
        self.failures: list[str] = []
        self.tokens: dict[str, str] = {}
        self.portal_ticket_id: str | None = None
        self.portal_ticket_number: str | None = None
        self.high_risk_ticket_id: str | None = None
        self.email_ticket_id: str | None = None

    def headers(self, role: str | None = None) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if role:
            token = self.tokens.get(role)
            if token:
                headers["Authorization"] = f"Bearer {token}"
        return headers

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        return requests.request(method, f"{BASE_URL}{path}", timeout=15, **kwargs)

    def run(self, test_number: int, label: str, func: Any) -> None:
        full_label = f"Test {test_number} — {label}"
        try:
            errors = func()
        except Exception as exc:
            errors = [f"Unexpected exception: {exc}"]

        if errors:
            self.failed += 1
            message = "; ".join(errors)
            self.failures.append(f"{full_label}: {message}")
            print(f"[FAIL] {full_label} | {message}")
            return

        self.passed += 1
        print(f"[PASS] {full_label}")

    def summary(self) -> None:
        line = "=" * 70
        print(line)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed")
        print(line)
        if self.failures:
            print("Failed tests:")
            for failure in self.failures:
                print(f"- {failure}")


def response_json(response: requests.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return response.text


def expect_status(response: requests.Response, expected: int | tuple[int, ...]) -> list[str]:
    expected_values = expected if isinstance(expected, tuple) else (expected,)
    if response.status_code not in expected_values:
        return [f"Expected status {expected_values} got {response.status_code}; body={response_json(response)}"]
    return []


def parse_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def expect_sla_hours(created_at: str, sla_due_at: str, expected_hours: int, tolerance_seconds: int = 180) -> list[str]:
    created = parse_datetime(created_at)
    due = parse_datetime(sla_due_at)
    actual_seconds = (due - created).total_seconds()
    expected_seconds = expected_hours * 3600
    if abs(actual_seconds - expected_seconds) > tolerance_seconds:
        actual_hours = round(actual_seconds / 3600, 2)
        return [f"Expected SLA about {expected_hours}h got {actual_hours}h"]
    return []


def expect_sla_from_now(sla_due_at: str, expected_hours: int, tolerance_seconds: int = 300) -> list[str]:
    due = parse_datetime(sla_due_at)
    now = datetime.now(timezone.utc)
    actual_seconds = (due - now).total_seconds()
    expected_seconds = expected_hours * 3600
    if abs(actual_seconds - expected_seconds) > tolerance_seconds:
        actual_hours = round(actual_seconds / 3600, 2)
        return [f"Expected SLA about {expected_hours}h from now got {actual_hours}h"]
    return []


def ticket_number_suffix(ticket_number: str) -> int:
    return int(ticket_number.rsplit("-", 1)[-1])


def main() -> None:
    runner = ApiTestRunner()

    def test_1_health() -> list[str]:
        response = runner.request("GET", "/health")
        errors = expect_status(response, 200)
        data = response_json(response)
        if isinstance(data, dict) and data.get("status") != "ok":
            errors.append(f"Expected body status=ok got {data}")
        elif not isinstance(data, dict):
            errors.append(f"Expected JSON object got {data}")
        return errors

    def test_2_login_accounts() -> list[str]:
        errors = []
        for role, credentials in ACCOUNTS.items():
            response = runner.request("POST", "/auth/login", json=credentials)
            if response.status_code != 200:
                errors.append(f"Expected {role} login status 200 got {response.status_code}; body={response_json(response)}")
                continue
            data = response_json(response)
            token = data.get("access_token") if isinstance(data, dict) else None
            if not token:
                errors.append(f"Expected {role} access_token got {data}")
                continue
            runner.tokens[role] = token
        return errors

    def test_3_create_intern_ticket() -> list[str]:
        if "intern" not in runner.tokens:
            return ["Expected intern token from Test 2 got missing token"]

        body = {
            "source": "portal_form",
            "subject": "Test portal form ticket",
            "description": "Testing the portal form channel",
            "category": "general_it",
            "requester_email": "intern@sps.com",
        }
        response = runner.request("POST", "/tickets", headers=runner.headers("intern"), json=body)
        errors = expect_status(response, 201)
        if errors:
            return errors

        data = response_json(response)
        runner.portal_ticket_id = data.get("id")
        runner.portal_ticket_number = data.get("ticket_number")

        if not str(data.get("ticket_number", "")).startswith(f"SPS-{CURRENT_YEAR}-"):
            errors.append(f"Expected ticket_number starts with SPS-{CURRENT_YEAR}- got {data.get('ticket_number')}")
        if data.get("source") != "portal_form":
            errors.append(f"Expected source=portal_form got {data.get('source')}")
        if data.get("status") != "open":
            errors.append(f"Expected status=open got {data.get('status')}")
        if data.get("risk_level") != "standard":
            errors.append(f"Expected risk_level=standard got {data.get('risk_level')}")
        errors.extend(expect_sla_hours(data.get("created_at", ""), data.get("sla_due_at", ""), 24))

        timeline = data.get("timeline_events")
        if not isinstance(timeline, list) or len(timeline) != 1:
            errors.append(f"Expected timeline_events length 1 got {timeline}")
        elif timeline[0].get("event_type") != "ticket_created":
            errors.append(f"Expected first event_type=ticket_created got {timeline[0].get('event_type')}")
        return errors

    def test_4_create_high_risk_ticket() -> list[str]:
        if "agent" not in runner.tokens:
            return ["Expected agent token from Test 2 got missing token"]

        body = {
            "source": "chat",
            "subject": "Need admin access to production",
            "description": "Requesting admin privileges on production server",
            "category": "identity_access",
            "requester_email": "agent@sps.com",
        }
        response = runner.request("POST", "/tickets", headers=runner.headers("agent"), json=body)
        errors = expect_status(response, 201)
        if errors:
            return errors

        data = response_json(response)
        runner.high_risk_ticket_id = data.get("id")
        if data.get("risk_level") != "high":
            errors.append(f"Expected risk_level=high got {data.get('risk_level')}")
        if data.get("status") != "waiting_approval":
            errors.append(f"Expected status=waiting_approval got {data.get('status')}")
        return errors

    def test_5_create_email_ticket() -> list[str]:
        if "agent" not in runner.tokens:
            return ["Expected agent token from Test 2 got missing token"]

        body = {
            "source": "email",
            "subject": "Phishing email received",
            "description": "I received a suspicious email asking for my password",
            "category": "cybersecurity",
            "priority": "critical",
            "requester_email": "user@sps.com",
        }
        response = runner.request("POST", "/tickets", headers=runner.headers("agent"), json=body)
        errors = expect_status(response, 201)
        if errors:
            return errors

        data = response_json(response)
        runner.email_ticket_id = data.get("id")
        if data.get("source") != "email":
            errors.append(f"Expected source=email got {data.get('source')}")
        if data.get("team") != "security":
            errors.append(f"Expected team=security got {data.get('team')}")
        if data.get("priority") != "critical":
            errors.append(f"Expected priority=critical got {data.get('priority')}")
        errors.extend(expect_sla_hours(data.get("created_at", ""), data.get("sla_due_at", ""), 4))
        return errors

    def test_6_intern_filtering() -> list[str]:
        if "intern" not in runner.tokens:
            return ["Expected intern token from Test 2 got missing token"]

        response = runner.request("GET", "/tickets", headers=runner.headers("intern"))
        errors = expect_status(response, 200)
        if errors:
            return errors

        tickets = response_json(response)
        if not isinstance(tickets, list):
            return [f"Expected list got {tickets}"]
        wrong_requesters = [ticket.get("requester_email") for ticket in tickets if ticket.get("requester_email") != "intern@sps.com"]
        if wrong_requesters:
            errors.append(f"Expected all requester_email=intern@sps.com got {wrong_requesters}")
        ids = {ticket.get("id") for ticket in tickets}
        if runner.high_risk_ticket_id in ids:
            errors.append(f"Expected intern list not to contain high_risk_ticket_id got {runner.high_risk_ticket_id}")
        return errors

    def test_7_agent_filtering() -> list[str]:
        if "agent" not in runner.tokens:
            return ["Expected agent token from Test 2 got missing token"]

        response = runner.request("GET", "/tickets", headers=runner.headers("agent"))
        errors = expect_status(response, 200)
        if errors:
            return errors

        tickets = response_json(response)
        if not isinstance(tickets, list):
            return [f"Expected list got {tickets}"]
        if len(tickets) < 3:
            errors.append(f"Expected at least 3 tickets got {len(tickets)}")
        requesters = {ticket.get("requester_email") for ticket in tickets}
        if "intern@sps.com" not in requesters or "agent@sps.com" not in requesters:
            errors.append(f"Expected tickets from intern and agent got requesters={sorted(requesters)}")
        return errors

    def test_8_get_single_ticket() -> list[str]:
        if not runner.portal_ticket_id or not runner.portal_ticket_number:
            return ["Expected ticket_id and ticket_number from Test 3 got missing values"]

        response = runner.request("GET", f"/tickets/{runner.portal_ticket_id}", headers=runner.headers("intern"))
        errors = expect_status(response, 200)
        if errors:
            return errors

        data = response_json(response)
        if data.get("ticket_number") != runner.portal_ticket_number:
            errors.append(f"Expected ticket_number={runner.portal_ticket_number} got {data.get('ticket_number')}")
        if not isinstance(data.get("timeline_events"), list) or len(data.get("timeline_events")) < 1:
            errors.append(f"Expected timeline_events list with at least 1 event got {data.get('timeline_events')}")
        if data.get("attachments") != []:
            errors.append(f"Expected attachments=[] got {data.get('attachments')}")
        return errors

    def test_9_append_timeline_event() -> list[str]:
        if not runner.portal_ticket_id:
            return ["Expected ticket_id from Test 3 got missing value"]

        body = {
            "event_type": "agent_reply_portal",
            "content": "We are looking into your laptop issue",
            "is_public": True,
            "channel": "portal",
        }
        response = runner.request("POST", f"/tickets/{runner.portal_ticket_id}/events", headers=runner.headers("agent"), json=body)
        errors = expect_status(response, 201)
        if errors:
            return errors

        data = response_json(response)
        if data.get("event_type") != "agent_reply_portal":
            errors.append(f"Expected event_type=agent_reply_portal got {data.get('event_type')}")
        if data.get("is_public") is not True:
            errors.append(f"Expected is_public=true got {data.get('is_public')}")
        return errors

    def test_10_internal_note() -> list[str]:
        if not runner.portal_ticket_id:
            return ["Expected ticket_id from Test 3 got missing value"]

        body = {
            "event_type": "internal_note",
            "content": "This is an internal note for agents only",
            "is_public": False,
            "channel": "portal",
        }
        response = runner.request("POST", f"/tickets/{runner.portal_ticket_id}/events", headers=runner.headers("agent"), json=body)
        errors = expect_status(response, 201)
        if errors:
            return errors

        data = response_json(response)
        if data.get("is_public") is not False:
            errors.append(f"Expected is_public=false got {data.get('is_public')}")
        return errors

    def test_11_patch_ticket() -> list[str]:
        if not runner.portal_ticket_id:
            return ["Expected ticket_id from Test 3 got missing value"]

        body = {"status": "in_progress", "priority": "high"}
        response = runner.request("PATCH", f"/tickets/{runner.portal_ticket_id}", headers=runner.headers("agent"), json=body)
        errors = expect_status(response, 200)
        if errors:
            return errors

        data = response_json(response)
        if data.get("status") != "in_progress":
            errors.append(f"Expected status=in_progress got {data.get('status')}")
        if data.get("priority") != "high":
            errors.append(f"Expected priority=high got {data.get('priority')}")
        errors.extend(expect_sla_from_now(data.get("sla_due_at", ""), 8))
        return errors

    def test_12_intern_cannot_patch() -> list[str]:
        if not runner.portal_ticket_id:
            return ["Expected ticket_id from Test 3 got missing value"]

        response = runner.request(
            "PATCH",
            f"/tickets/{runner.portal_ticket_id}",
            headers=runner.headers("intern"),
            json={"status": "resolved"},
        )
        return expect_status(response, 403)

    def test_13_approve_high_risk() -> list[str]:
        if not runner.high_risk_ticket_id:
            return ["Expected high_risk_ticket_id from Test 4 got missing value"]

        body = {
            "decision": "approved",
            "reason": "Access approved by security admin after review",
        }
        response = runner.request(
            "POST",
            f"/tickets/{runner.high_risk_ticket_id}/approve",
            headers=runner.headers("secadmin"),
            json=body,
        )
        errors = expect_status(response, 200)
        if errors:
            return errors

        data = response_json(response)
        if data.get("status") != "in_progress":
            errors.append(f"Expected status=in_progress got {data.get('status')}")
        return errors

    def test_14_reject_high_risk() -> list[str]:
        if "agent" not in runner.tokens or "secadmin" not in runner.tokens:
            return ["Expected agent and secadmin tokens from Test 2 got missing token"]

        create_body = {
            "source": "portal_form",
            "subject": "Need root access to database",
            "description": "Requesting root database access",
            "category": "identity_access",
            "requester_email": "agent@sps.com",
        }
        create_response = runner.request("POST", "/tickets", headers=runner.headers("agent"), json=create_body)
        errors = expect_status(create_response, 201)
        if errors:
            return errors

        new_ticket_id = response_json(create_response).get("id")
        approve_body = {
            "decision": "rejected",
            "reason": "Root database access not permitted per security policy",
        }
        approve_response = runner.request(
            "POST",
            f"/tickets/{new_ticket_id}/approve",
            headers=runner.headers("secadmin"),
            json=approve_body,
        )
        errors.extend(expect_status(approve_response, 200))
        if errors:
            return errors

        data = response_json(approve_response)
        if data.get("status") != "closed":
            errors.append(f"Expected status=closed got {data.get('status')}")
        return errors

    def test_15_management_report() -> list[str]:
        if "secadmin" not in runner.tokens:
            return ["Expected secadmin token from Test 2 got missing token"]

        response = runner.request("GET", "/reports/summary", headers=runner.headers("secadmin"))
        errors = expect_status(response, 200)
        if errors:
            return errors

        data = response_json(response)
        if "total_tickets" not in data:
            errors.append(f"Expected total_tickets in response got {data}")
        by_source = data.get("by_source")
        if not isinstance(by_source, dict):
            errors.append(f"Expected by_source object got {by_source}")
        else:
            for key in ("email", "portal_form", "chat"):
                if key not in by_source:
                    errors.append(f"Expected by_source key {key} got keys={sorted(by_source)}")
            if "total_tickets" in data and sum(by_source.values()) != data.get("total_tickets"):
                errors.append(f"Expected by_source counts add to total_tickets got {sum(by_source.values())} vs {data.get('total_tickets')}")
        if data.get("high_risk_total", 0) < 2:
            errors.append(f"Expected high_risk_total at least 2 got {data.get('high_risk_total')}")
        return errors

    def test_16_unauthorized_access() -> list[str]:
        response = runner.request("GET", "/tickets")
        return expect_status(response, (401, 403))

    def test_17_ticket_number_sequence() -> list[str]:
        if "agent" not in runner.tokens:
            return ["Expected agent token from Test 2 got missing token"]

        response = runner.request("GET", "/tickets", headers=runner.headers("agent"))
        errors = expect_status(response, 200)
        if errors:
            return errors

        tickets = response_json(response)
        if not isinstance(tickets, list):
            return [f"Expected list got {tickets}"]

        ticket_numbers = [ticket.get("ticket_number") for ticket in tickets]
        pattern = re.compile(rf"^SPS-{CURRENT_YEAR}-\d{{3}}$")
        invalid_numbers = [number for number in ticket_numbers if not isinstance(number, str) or not pattern.match(number)]
        if invalid_numbers:
            errors.append(f"Expected all ticket_numbers follow SPS-{CURRENT_YEAR}-NNN got {invalid_numbers}")

        if len(ticket_numbers) != len(set(ticket_numbers)):
            errors.append(f"Expected no duplicate ticket_numbers got {ticket_numbers}")

        valid_suffixes = sorted(ticket_number_suffix(number) for number in ticket_numbers if isinstance(number, str) and pattern.match(number))
        if valid_suffixes:
            expected_sequence = list(range(valid_suffixes[0], valid_suffixes[-1] + 1))
            if valid_suffixes != expected_sequence:
                errors.append(f"Expected sequential ticket numbers with no gaps got suffixes={valid_suffixes}")
        return errors

    tests = [
        (1, "Health check", test_1_health),
        (2, "Login all 3 accounts", test_2_login_accounts),
        (3, "Create ticket as intern (portal_form)", test_3_create_intern_ticket),
        (4, "Create high-risk ticket (identity_access)", test_4_create_high_risk_ticket),
        (5, "Create email source ticket", test_5_create_email_ticket),
        (6, "Role filtering (intern sees own tickets only)", test_6_intern_filtering),
        (7, "Role filtering (agent sees all tickets)", test_7_agent_filtering),
        (8, "Get single ticket with timeline", test_8_get_single_ticket),
        (9, "Append timeline event", test_9_append_timeline_event),
        (10, "Internal note (not visible to requester)", test_10_internal_note),
        (11, "Update ticket fields (PATCH)", test_11_patch_ticket),
        (12, "Intern cannot PATCH tickets (role guard)", test_12_intern_cannot_patch),
        (13, "Approve high-risk ticket", test_13_approve_high_risk),
        (14, "Reject a high-risk ticket", test_14_reject_high_risk),
        (15, "Management report", test_15_management_report),
        (16, "Unauthorized access (no token)", test_16_unauthorized_access),
        (17, "Ticket number sequence check", test_17_ticket_number_sequence),
    ]

    print(f"Running SPS SecureDesk AI API tests against {BASE_URL}")
    for test_number, label, func in tests:
        runner.run(test_number, label, func)
    runner.summary()


if __name__ == "__main__":
    main()
