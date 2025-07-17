from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status

from ..db.models import UserRole


def get_user_role(x_role: str = Header(...)) -> UserRole:
    """Retrieve the role from request headers."""
    try:
        return UserRole(x_role)
    except ValueError as exc:  # pragma: no cover - invalid header
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid role") from exc


def require_role(required: UserRole):
    """Return a dependency ensuring the current user has ``required`` role."""

    async def _checker(role: UserRole = Depends(get_user_role)) -> None:
        if role != required:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")

    return Depends(_checker)
