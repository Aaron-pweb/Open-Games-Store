"""
Tests for apps.core.permissions.

Uses APIRequestFactory to build mock requests and calls permission
.has_permission() / .has_object_permission() directly, without routing
through a view.
"""

import pytest
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIRequestFactory

from apps.core.permissions import (
    IsAdminRole,
    IsDeveloperOrAdmin,
    IsEndUserOrAbove,
    IsOwnerOrAdmin,
    ReadOnly,
)
from apps.games.tests.factories import (
    DeveloperFactory,
    DeveloperMembershipFactory,
    GameFactory,
    GameMediaFactory,
    PublisherFactory,
    PublisherMembershipFactory,
    make_admin_user,
    make_developer_user,
    make_end_user,
    make_owner_user,
)

factory = APIRequestFactory()


# ── Helpers ──────────────────────────────────────────────────────────

def _get_request(user=None):
    """Return a GET request with the given user attached."""
    request = factory.get("/fake-url/")
    request.user = user or AnonymousUser()
    return request


def _post_request(user=None):
    """Return a POST request with the given user attached."""
    request = factory.post("/fake-url/")
    request.user = user or AnonymousUser()
    return request


def _put_request(user=None):
    """Return a PUT request with the given user attached."""
    request = factory.put("/fake-url/")
    request.user = user or AnonymousUser()
    return request


def _delete_request(user=None):
    """Return a DELETE request with the given user attached."""
    request = factory.delete("/fake-url/")
    request.user = user or AnonymousUser()
    return request


def _patch_request(user=None):
    """Return a PATCH request with the given user attached."""
    request = factory.patch("/fake-url/")
    request.user = user or AnonymousUser()
    return request


# ── TestIsAdminRole ──────────────────────────────────────────────────


@pytest.mark.django_db
class TestIsAdminRole:
    """IsAdminRole: only authenticated users with the 'admin' role."""

    permission = IsAdminRole()

    def test_admin_allowed(self):
        request = _get_request(make_admin_user())
        assert self.permission.has_permission(request, None) is True

    def test_admin_allowed_post(self):
        request = _post_request(make_admin_user())
        assert self.permission.has_permission(request, None) is True

    def test_developer_denied(self):
        request = _get_request(make_developer_user())
        assert self.permission.has_permission(request, None) is False

    def test_owner_denied(self):
        request = _get_request(make_owner_user())
        assert self.permission.has_permission(request, None) is False

    def test_end_user_denied(self):
        request = _get_request(make_end_user())
        assert self.permission.has_permission(request, None) is False

    def test_anonymous_denied(self):
        request = _get_request()
        assert self.permission.has_permission(request, None) is False


# ── TestReadOnly ─────────────────────────────────────────────────────


@pytest.mark.django_db
class TestReadOnly:
    """ReadOnly: allows GET/HEAD/OPTIONS only."""

    permission = ReadOnly()

    def test_get_allowed(self):
        request = _get_request()
        assert self.permission.has_permission(request, None) is True

    def test_head_allowed(self):
        request = factory.head("/fake-url/")
        request.user = AnonymousUser()
        assert self.permission.has_permission(request, None) is True

    def test_options_allowed(self):
        request = factory.options("/fake-url/")
        request.user = AnonymousUser()
        assert self.permission.has_permission(request, None) is True

    def test_post_denied(self):
        request = _post_request()
        assert self.permission.has_permission(request, None) is False

    def test_put_denied(self):
        request = _put_request()
        assert self.permission.has_permission(request, None) is False

    def test_patch_denied(self):
        request = _patch_request()
        assert self.permission.has_permission(request, None) is False

    def test_delete_denied(self):
        request = _delete_request()
        assert self.permission.has_permission(request, None) is False

    def test_post_denied_even_for_admin(self):
        """ReadOnly is method-based, not role-based."""
        request = _post_request(make_admin_user())
        assert self.permission.has_permission(request, None) is False


# ── TestIsEndUserOrAbove ─────────────────────────────────────────────


@pytest.mark.django_db
class TestIsEndUserOrAbove:
    """IsEndUserOrAbove: any authenticated user passes."""

    permission = IsEndUserOrAbove()

    def test_end_user_allowed(self):
        request = _get_request(make_end_user())
        assert self.permission.has_permission(request, None) is True

    def test_developer_allowed(self):
        request = _get_request(make_developer_user())
        assert self.permission.has_permission(request, None) is True

    def test_owner_allowed(self):
        request = _get_request(make_owner_user())
        assert self.permission.has_permission(request, None) is True

    def test_admin_allowed(self):
        request = _get_request(make_admin_user())
        assert self.permission.has_permission(request, None) is True

    def test_anonymous_denied(self):
        request = _get_request()
        assert self.permission.has_permission(request, None) is False

    def test_post_allowed_for_authenticated(self):
        request = _post_request(make_end_user())
        assert self.permission.has_permission(request, None) is True

    def test_post_denied_for_anonymous(self):
        request = _post_request()
        assert self.permission.has_permission(request, None) is False


# ── TestIsOwnerOrAdmin ───────────────────────────────────────────────


@pytest.mark.django_db
class TestIsOwnerOrAdmin:
    """
    IsOwnerOrAdmin:
    - has_permission: safe methods → True; unsafe → must be authenticated.
    - has_object_permission: safe → True; admin → True;
      otherwise check Developer/Publisher membership.
    """

    permission = IsOwnerOrAdmin()

    # ── has_permission ───────────────────────────────────────────────

    def test_get_allowed_for_anonymous(self):
        request = _get_request()
        assert self.permission.has_permission(request, None) is True

    def test_post_denied_for_anonymous(self):
        request = _post_request()
        assert self.permission.has_permission(request, None) is False

    def test_post_allowed_for_authenticated(self):
        request = _post_request(make_end_user())
        assert self.permission.has_permission(request, None) is True

    def test_put_allowed_for_authenticated(self):
        request = _put_request(make_developer_user())
        assert self.permission.has_permission(request, None) is True

    def test_delete_denied_for_anonymous(self):
        request = _delete_request()
        assert self.permission.has_permission(request, None) is False

    # ── has_object_permission: Game objects ──────────────────────────

    def test_get_object_always_allowed(self):
        """Safe method → True regardless of ownership."""
        game = GameFactory()
        request = _get_request()
        assert self.permission.has_object_permission(request, None, game) is True

    def test_admin_can_modify_any_game(self):
        game = GameFactory()
        request = _put_request(make_admin_user())
        assert self.permission.has_object_permission(request, None, game) is True

    def test_developer_member_can_modify_own_game(self):
        """User linked to a developer on the game can modify it."""
        developer = DeveloperFactory()
        user = make_developer_user()
        DeveloperMembershipFactory(user=user, developer=developer)
        game = GameFactory(developers=[developer])

        request = _put_request(user)
        assert self.permission.has_object_permission(request, None, game) is True

    def test_publisher_member_can_modify_own_game(self):
        """User linked to a publisher on the game can modify it."""
        publisher = PublisherFactory()
        user = make_owner_user()
        PublisherMembershipFactory(user=user, publisher=publisher)
        game = GameFactory(publishers=[publisher])

        request = _patch_request(user)
        assert self.permission.has_object_permission(request, None, game) is True

    def test_non_member_cannot_modify_game(self):
        """User with no membership on the game is denied."""
        game = GameFactory()
        user = make_developer_user()  # has role but no membership

        request = _put_request(user)
        assert self.permission.has_object_permission(request, None, game) is False

    def test_member_of_other_developer_cannot_modify(self):
        """Membership on a *different* developer doesn't grant access."""
        dev_on_game = DeveloperFactory()
        dev_other = DeveloperFactory()

        user = make_developer_user()
        DeveloperMembershipFactory(user=user, developer=dev_other)
        game = GameFactory(developers=[dev_on_game])

        request = _put_request(user)
        assert self.permission.has_object_permission(request, None, game) is False

    def test_delete_requires_membership(self):
        """DELETE is an unsafe method and also requires ownership."""
        developer = DeveloperFactory()
        user = make_developer_user()
        DeveloperMembershipFactory(user=user, developer=developer)
        game = GameFactory(developers=[developer])

        request = _delete_request(user)
        assert self.permission.has_object_permission(request, None, game) is True

    # ── has_object_permission: child objects (GameMedia) ─────────────

    def test_child_object_admin_allowed(self):
        """Admin can modify a child object like GameMedia."""
        media = GameMediaFactory()
        request = _put_request(make_admin_user())
        assert self.permission.has_object_permission(request, None, media) is True

    def test_child_object_owner_member_allowed(self):
        """Owner through developer membership on the game's media."""
        developer = DeveloperFactory()
        user = make_developer_user()
        DeveloperMembershipFactory(user=user, developer=developer)
        game = GameFactory(developers=[developer])
        media = GameMediaFactory(game=game)

        request = _patch_request(user)
        assert self.permission.has_object_permission(request, None, media) is True

    def test_child_object_non_member_denied(self):
        """Non-member cannot modify a child object."""
        media = GameMediaFactory()
        user = make_developer_user()

        request = _put_request(user)
        assert self.permission.has_object_permission(request, None, media) is False

    def test_child_object_get_always_allowed(self):
        """Safe method on child object always allowed."""
        media = GameMediaFactory()
        request = _get_request()
        assert self.permission.has_object_permission(request, None, media) is True


# ── TestIsDeveloperOrAdmin ───────────────────────────────────────────


@pytest.mark.django_db
class TestIsDeveloperOrAdmin:
    """
    IsDeveloperOrAdmin:
    - has_permission: safe → True; unsafe → auth + (admin OR owner OR developer role).
    - has_object_permission: mirrors IsOwnerOrAdmin object-level logic.
    """

    permission = IsDeveloperOrAdmin()

    # ── has_permission ───────────────────────────────────────────────

    def test_get_allowed_for_anonymous(self):
        request = _get_request()
        assert self.permission.has_permission(request, None) is True

    def test_post_denied_for_anonymous(self):
        request = _post_request()
        assert self.permission.has_permission(request, None) is False

    def test_post_allowed_for_admin(self):
        request = _post_request(make_admin_user())
        assert self.permission.has_permission(request, None) is True

    def test_post_allowed_for_owner(self):
        request = _post_request(make_owner_user())
        assert self.permission.has_permission(request, None) is True

    def test_post_allowed_for_developer(self):
        request = _post_request(make_developer_user())
        assert self.permission.has_permission(request, None) is True

    def test_post_denied_for_end_user(self):
        """end_user role is NOT sufficient for create."""
        request = _post_request(make_end_user())
        assert self.permission.has_permission(request, None) is False

    def test_put_denied_for_end_user(self):
        request = _put_request(make_end_user())
        assert self.permission.has_permission(request, None) is False

    def test_delete_allowed_for_developer(self):
        request = _delete_request(make_developer_user())
        assert self.permission.has_permission(request, None) is True

    # ── has_object_permission: Game objects ──────────────────────────

    def test_object_get_always_allowed(self):
        game = GameFactory()
        request = _get_request()
        assert self.permission.has_object_permission(request, None, game) is True

    def test_object_admin_can_modify_any(self):
        game = GameFactory()
        request = _put_request(make_admin_user())
        assert self.permission.has_object_permission(request, None, game) is True

    def test_object_member_can_modify_own(self):
        developer = DeveloperFactory()
        user = make_developer_user()
        DeveloperMembershipFactory(user=user, developer=developer)
        game = GameFactory(developers=[developer])

        request = _put_request(user)
        assert self.permission.has_object_permission(request, None, game) is True

    def test_object_non_member_denied(self):
        game = GameFactory()
        user = make_developer_user()

        request = _put_request(user)
        assert self.permission.has_object_permission(request, None, game) is False

    def test_object_wrong_developer_denied(self):
        """Membership on the wrong developer studio is not enough."""
        dev_on_game = DeveloperFactory()
        dev_other = DeveloperFactory()
        user = make_developer_user()
        DeveloperMembershipFactory(user=user, developer=dev_other)
        game = GameFactory(developers=[dev_on_game])

        request = _patch_request(user)
        assert self.permission.has_object_permission(request, None, game) is False

    # ── has_object_permission: child objects (GameMedia) ─────────────

    def test_child_admin_can_modify(self):
        media = GameMediaFactory()
        request = _put_request(make_admin_user())
        assert self.permission.has_object_permission(request, None, media) is True

    def test_child_member_can_modify(self):
        developer = DeveloperFactory()
        user = make_developer_user()
        DeveloperMembershipFactory(user=user, developer=developer)
        game = GameFactory(developers=[developer])
        media = GameMediaFactory(game=game)

        request = _delete_request(user)
        assert self.permission.has_object_permission(request, None, media) is True

    def test_child_non_member_denied(self):
        media = GameMediaFactory()
        user = make_developer_user()

        request = _delete_request(user)
        assert self.permission.has_object_permission(request, None, media) is False

    def test_child_get_always_allowed(self):
        media = GameMediaFactory()
        request = _get_request()
        assert self.permission.has_object_permission(request, None, media) is True
