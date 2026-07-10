"""
Reusable permission classes for the Open-Games-Store API.

These live in the shared kernel (apps.core) so every app can import them
without circular dependencies.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminRole(BasePermission):
    """Allows access only to users with the 'admin' role."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_admin_role
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission:
    - Safe methods (GET, HEAD, OPTIONS): allow anyone.
    - Unsafe methods: allow if the user is admin OR owns the object
      through Developer/Publisher membership.

    Works for Game objects directly and for Game child objects
    (SystemRequirement, GameMedia, GameLanguageSupport) by following
    the .game FK.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_admin_role:
            return True
        # For Game objects (they have a 'developers' M2M)
        if hasattr(obj, "developers"):
            return request.user.has_game_access(obj)
        # For Game child objects (SystemRequirement, GameMedia, etc.)
        if hasattr(obj, "game"):
            return request.user.has_game_access(obj.game)
        return False


class IsDeveloperOrAdmin(BasePermission):
    """
    View-level: allows create if user has 'developer', 'owner', or 'admin' role.
    Object-level: defers to ownership check (same as IsOwnerOrAdmin).

    Use this on endpoints where developers need to create new resources
    but can only modify their own.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not (request.user and request.user.is_authenticated):
            return False
        return (
            request.user.is_admin_role
            or request.user.is_owner_role
            or request.user.is_developer_role
        )

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_admin_role:
            return True
        if hasattr(obj, "developers"):
            return request.user.has_game_access(obj)
        if hasattr(obj, "game"):
            return request.user.has_game_access(obj.game)
        return False


class ReadOnly(BasePermission):
    """Allows read-only access to any user, including unauthenticated."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsEndUserOrAbove(BasePermission):
    """Any authenticated user (end_user, developer, owner, admin)."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
