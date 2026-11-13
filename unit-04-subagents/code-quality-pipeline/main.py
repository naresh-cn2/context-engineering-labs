"""Target Application for Multi-Agent Code Quality Pipeline.

Simulates an authentication and data retrieval module.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class UserDatabase:
    """Mock user repository."""

    def __init__(self):
        self.users = {
            "alice": {"id": 1, "role": "admin", "token": "secret_token_123"},
            "bob": {"id": 2, "role": "member", "token": "secret_token_456"},
        }

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        # Intentional performance flaw: artificial latency simulating unindexed query
        time.sleep(0.01)
        return self.users.get(username)

    def get_all_users(self) -> List[Dict[str, Any]]:
        return list(self.users.values())


def authenticate_user(db: UserDatabase, username: str, token: str) -> bool:
    """Authenticates a user against token."""
    user = db.get_user(username)
    if not user:
        return False
    # Intentional basic check: compare tokens
    return user["token"] == token


def fetch_user_dashboard(db: UserDatabase, usernames: List[str]) -> List[Dict[str, Any]]:
    """Fetches user information for multiple accounts."""
    results = []
    # Intentional performance flaw: N+1 queries in loop without caching or batching
    for u in usernames:
        user_info = db.get_user(u)
        if user_info:
            results.append(user_info)
    return results

