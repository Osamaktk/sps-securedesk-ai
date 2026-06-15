import unittest
from unittest.mock import patch

from ai.config.settings import Settings
from ai.llm.router import (
    LLMGenerationError,
    generate_response_with_provider,
)


class LLMRouterTests(unittest.TestCase):
    def test_selected_provider_is_used_first(self) -> None:
        calls: list[str] = []

        def anthropic(system: str, user: str, settings: Settings) -> str:
            del system, user, settings
            calls.append("anthropic")
            return "anthropic response"

        providers = {
            "anthropic": anthropic,
            "openrouter": self._unexpected_provider,
            "groq": self._unexpected_provider,
        }
        settings = Settings(llm_provider="anthropic", _env_file=None)

        with patch("ai.llm.router.PROVIDER_CLIENTS", providers):
            result = generate_response_with_provider("system", "user", settings)

        self.assertEqual(result.text, "anthropic response")
        self.assertEqual(result.provider, "anthropic")
        self.assertEqual(calls, ["anthropic"])

    def test_failure_falls_back_in_canonical_order(self) -> None:
        calls: list[str] = []

        def failing(name: str):
            def provider(system: str, user: str, settings: Settings) -> str:
                del system, user, settings
                calls.append(name)
                raise RuntimeError(f"{name} unavailable")

            return provider

        def groq(system: str, user: str, settings: Settings) -> str:
            del system, user, settings
            calls.append("groq")
            return "fallback response"

        providers = {
            "anthropic": failing("anthropic"),
            "openrouter": failing("openrouter"),
            "groq": groq,
        }
        settings = Settings(llm_provider="anthropic", _env_file=None)

        with patch("ai.llm.router.PROVIDER_CLIENTS", providers):
            result = generate_response_with_provider("system", "user", settings)

        self.assertEqual(result.provider, "groq")
        self.assertEqual(calls, ["anthropic", "openrouter", "groq"])

    def test_all_provider_errors_are_reported(self) -> None:
        def fail(system: str, user: str, settings: Settings) -> str:
            del system, user, settings
            raise ValueError("API key is not configured")

        providers = {name: fail for name in ("anthropic", "openrouter", "groq")}
        settings = Settings(llm_provider="openrouter", _env_file=None)

        with patch("ai.llm.router.PROVIDER_CLIENTS", providers):
            with self.assertRaises(LLMGenerationError) as raised:
                generate_response_with_provider("system", "user", settings)

        message = str(raised.exception)
        self.assertIn("anthropic", message)
        self.assertIn("openrouter", message)
        self.assertIn("groq", message)

    @staticmethod
    def _unexpected_provider(
        system: str,
        user: str,
        settings: Settings,
    ) -> str:
        del system, user, settings
        raise AssertionError("Unexpected provider call")


if __name__ == "__main__":
    unittest.main()
