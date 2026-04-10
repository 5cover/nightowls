from __future__ import annotations

import unittest

from nightowls.members import Identity, resolve_member_name


class MemberMatchingTests(unittest.TestCase):
    def test_first_match_wins(self) -> None:
        rules = [
            ["A", {"email": {"regex": "@example\\.com$"}}],
            ["B", {"email": "john@example.com"}],
        ]
        identity = Identity(name="john", email="john@example.com")
        self.assertEqual(resolve_member_name(identity, rules), "A")

    def test_falls_back_to_identity_name(self) -> None:
        identity = Identity(name="fallback", email="fallback@example.com")
        self.assertEqual(resolve_member_name(identity, []), "fallback")


if __name__ == "__main__":
    unittest.main()
