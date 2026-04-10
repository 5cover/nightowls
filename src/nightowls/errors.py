from __future__ import annotations


class NightowlsError(Exception):
    """Base exception for nightowls."""


class ConfigError(NightowlsError):
    """Raised when configuration loading or validation fails."""


class RepoError(NightowlsError):
    """Raised when repository access fails."""
