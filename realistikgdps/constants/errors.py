from __future__ import annotations

from enum import Enum


class ServiceError(str, Enum):
    AUTH_NOT_FOUND = "auth.not_found"
    AUTH_PASSWORD_MISMATCH = "auth.password_mismatch"
    PROFILE_USER_BLOCKED = "profile.user_blocked"
    PROFILE_USER_NOT_FOUND = "profile.user_not_found"
    PROFILE_BLOCKED_BY_USER = "profile.blocked_by_user"