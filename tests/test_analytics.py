"""Tests for IP anonymization in analytics service."""
import pytest

from app.services.analytics import anonymize_ip


class TestIPAnonymization:
    def test_ipv4_last_octet_masked(self) -> None:
        assert anonymize_ip("192.168.1.100") == "192.168.1.0"

    def test_ipv4_already_zero(self) -> None:
        assert anonymize_ip("10.0.0.0") == "10.0.0.0"

    def test_ipv4_different_addresses(self) -> None:
        assert anonymize_ip("8.8.8.8") == "8.8.8.0"
        assert anonymize_ip("1.2.3.4") == "1.2.3.0"

    def test_ipv6_anonymized(self) -> None:
        result = anonymize_ip("2001:db8::1")
        assert result is not None
        assert isinstance(result, str)
        # Should not be the original
        assert result != "2001:db8::1"

    def test_invalid_ip_returns_fallback(self) -> None:
        result = anonymize_ip("not-an-ip")
        assert result == "0.0.0.0"

    def test_empty_string_returns_fallback(self) -> None:
        result = anonymize_ip("")
        assert result == "0.0.0.0"
