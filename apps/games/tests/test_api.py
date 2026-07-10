"""
Comprehensive API endpoint tests for apps.games.

Tests cover the full permission matrix (admin, owner, developer, end_user,
anonymous) for every ViewSet. Uses pytest-django + factory-boy + simplejwt.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.games.models import Game, Tag
from apps.games.tests.factories import (
    BundleFactory,
    DeveloperFactory,
    DeveloperMembershipFactory,
    GameFactory,
    GenreFactory,
    PlatformFactory,
    PublisherFactory,
    PublisherMembershipFactory,
    SystemRequirementFactory,
    TagFactory,
    make_admin_user,
    make_developer_user,
    make_end_user,
    make_owner_user,
)


# ── Helpers ──────────────────────────────────────────────────────────


def get_auth_header(user):
    """Return a dict suitable for APIClient ``**extra`` to set the JWT bearer token."""
    token = RefreshToken.for_user(user)
    return {"HTTP_AUTHORIZATION": f"Bearer {token.access_token}"}


# ── Fixtures ─────────────────────────────────────────────────────────


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user():
    return make_admin_user()


@pytest.fixture
def developer_user():
    return make_developer_user()


@pytest.fixture
def owner_user():
    return make_owner_user()


@pytest.fixture
def end_user_user():
    return make_end_user()


# =====================================================================
#  DeveloperViewSet — /api/v1/games/developers/
# =====================================================================


@pytest.mark.django_db
class TestDeveloperAPI:
    """Developer CRUD: public read, admin-only write."""

    URL = "/api/v1/games/developers/"

    # ── List / Retrieve (public) ────────────────────────────────────

    def test_list_returns_200_for_anon(self, api_client):
        DeveloperFactory.create_batch(3)
        resp = api_client.get(self.URL)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 3

    def test_detail_returns_200_for_anon(self, api_client):
        dev = DeveloperFactory()
        resp = api_client.get(f"{self.URL}{dev.id}/")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["name"] == dev.name

    # ── Create permissions ──────────────────────────────────────────

    def test_create_returns_401_for_anon(self, api_client):
        payload = {"name": "New Dev", "slug": "new-dev"}
        resp = api_client.post(self.URL, payload)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_returns_403_for_end_user(self, api_client, end_user_user):
        payload = {"name": "New Dev", "slug": "new-dev"}
        resp = api_client.post(self.URL, payload, **get_auth_header(end_user_user))
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_create_returns_403_for_developer(self, api_client, developer_user):
        payload = {"name": "New Dev", "slug": "new-dev"}
        resp = api_client.post(self.URL, payload, **get_auth_header(developer_user))
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_create_returns_201_for_admin(self, api_client, admin_user):
        payload = {"name": "New Dev", "slug": "new-dev", "country": "US"}
        resp = api_client.post(self.URL, payload, **get_auth_header(admin_user))
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["name"] == "New Dev"

    # ── Update permissions ──────────────────────────────────────────

    def test_put_returns_403_for_non_admin(self, api_client, end_user_user):
        dev = DeveloperFactory()
        payload = {"name": "Updated", "slug": dev.slug}
        resp = api_client.put(
            f"{self.URL}{dev.id}/", payload, **get_auth_header(end_user_user)
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_put_returns_200_for_admin(self, api_client, admin_user):
        dev = DeveloperFactory()
        payload = {
            "name": "Updated Studio",
            "slug": dev.slug,
            "website": dev.website,
            "country": "GB",
            "verified": True,
        }
        resp = api_client.put(
            f"{self.URL}{dev.id}/", payload, format="json",
            **get_auth_header(admin_user)
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["name"] == "Updated Studio"

    # ── Delete permissions ──────────────────────────────────────────

    def test_delete_returns_403_for_non_admin(self, api_client, developer_user):
        dev = DeveloperFactory()
        resp = api_client.delete(
            f"{self.URL}{dev.id}/", **get_auth_header(developer_user)
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_returns_204_for_admin(self, api_client, admin_user):
        dev = DeveloperFactory()
        resp = api_client.delete(
            f"{self.URL}{dev.id}/", **get_auth_header(admin_user)
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT


# =====================================================================
#  GenreViewSet — /api/v1/games/genres/
# =====================================================================


@pytest.mark.django_db
class TestGenreAPI:
    """Genre CRUD: public read, admin-only write (same pattern as Developer)."""

    URL = "/api/v1/games/genres/"

    def test_list_returns_200_for_anon(self, api_client):
        GenreFactory.create_batch(2)
        resp = api_client.get(self.URL)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 2

    def test_detail_returns_200_for_anon(self, api_client):
        genre = GenreFactory()
        resp = api_client.get(f"{self.URL}{genre.id}/")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["name"] == genre.name

    def test_create_returns_401_for_anon(self, api_client):
        resp = api_client.post(self.URL, {"name": "RPG", "slug": "rpg"})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_returns_403_for_end_user(self, api_client, end_user_user):
        resp = api_client.post(
            self.URL, {"name": "RPG", "slug": "rpg"}, **get_auth_header(end_user_user)
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_create_returns_201_for_admin(self, api_client, admin_user):
        resp = api_client.post(
            self.URL, {"name": "RPG", "slug": "rpg"}, **get_auth_header(admin_user)
        )
        assert resp.status_code == status.HTTP_201_CREATED

    def test_put_returns_403_for_non_admin(self, api_client, developer_user):
        genre = GenreFactory()
        resp = api_client.put(
            f"{self.URL}{genre.id}/",
            {"name": "Updated", "slug": genre.slug},
            **get_auth_header(developer_user),
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_put_returns_200_for_admin(self, api_client, admin_user):
        genre = GenreFactory()
        resp = api_client.put(
            f"{self.URL}{genre.id}/",
            {"name": "Strategy", "slug": "strategy"},
            format="json",
            **get_auth_header(admin_user),
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["name"] == "Strategy"

    def test_delete_returns_403_for_non_admin(self, api_client, end_user_user):
        genre = GenreFactory()
        resp = api_client.delete(
            f"{self.URL}{genre.id}/", **get_auth_header(end_user_user)
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_returns_204_for_admin(self, api_client, admin_user):
        genre = GenreFactory()
        resp = api_client.delete(
            f"{self.URL}{genre.id}/", **get_auth_header(admin_user)
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT


# =====================================================================
#  TagViewSet — /api/v1/games/tags/  (special permissions)
# =====================================================================


@pytest.mark.django_db
class TestTagAPI:
    """
    Tags have special semantics:
    - Any authenticated user can create (end_user → auto is_approved=False).
    - Admin tags → auto is_approved=True.
    - Non-admin list only sees approved tags.
    - Approve action: admin-only.
    """

    URL = "/api/v1/games/tags/"

    # ── List ────────────────────────────────────────────────────────

    def test_list_returns_200_for_anon(self, api_client):
        TagFactory(is_approved=True)
        TagFactory(is_approved=False)
        resp = api_client.get(self.URL)
        assert resp.status_code == status.HTTP_200_OK
        # Anon only sees approved tags
        assert resp.data["count"] == 1

    def test_list_non_admin_only_sees_approved(self, api_client, end_user_user):
        TagFactory(is_approved=True)
        TagFactory(is_approved=False)
        resp = api_client.get(self.URL, **get_auth_header(end_user_user))
        assert resp.data["count"] == 1

    def test_list_admin_sees_all_tags(self, api_client, admin_user):
        TagFactory(is_approved=True)
        TagFactory(is_approved=False)
        resp = api_client.get(self.URL, **get_auth_header(admin_user))
        assert resp.data["count"] == 2

    # ── Create ──────────────────────────────────────────────────────

    def test_create_returns_401_for_anon(self, api_client):
        resp = api_client.post(self.URL, {"name": "Open World", "slug": "open-world"})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_by_end_user_sets_is_approved_false(self, api_client, end_user_user):
        resp = api_client.post(
            self.URL,
            {"name": "Open World", "slug": "open-world"},
            **get_auth_header(end_user_user),
        )
        assert resp.status_code == status.HTTP_201_CREATED
        tag = Tag.objects.get(slug="open-world")
        assert tag.is_approved is False

    def test_create_by_admin_sets_is_approved_true(self, api_client, admin_user):
        resp = api_client.post(
            self.URL,
            {"name": "Sandbox", "slug": "sandbox"},
            **get_auth_header(admin_user),
        )
        assert resp.status_code == status.HTTP_201_CREATED
        tag = Tag.objects.get(slug="sandbox")
        assert tag.is_approved is True

    # ── Approve action ──────────────────────────────────────────────

    def test_approve_returns_403_for_non_admin(self, api_client, end_user_user):
        tag = TagFactory(is_approved=False)
        resp = api_client.post(
            f"{self.URL}{tag.id}/approve/", **get_auth_header(end_user_user)
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_approve_returns_200_for_admin(self, api_client, admin_user):
        tag = TagFactory(is_approved=False)
        resp = api_client.post(
            f"{self.URL}{tag.id}/approve/", **get_auth_header(admin_user)
        )
        assert resp.status_code == status.HTTP_200_OK
        tag.refresh_from_db()
        assert tag.is_approved is True

    # ── Update / Delete (admin-only) ────────────────────────────────

    def test_put_returns_403_for_non_admin(self, api_client, developer_user):
        tag = TagFactory()
        resp = api_client.put(
            f"{self.URL}{tag.id}/",
            {"name": "Updated", "slug": tag.slug},
            **get_auth_header(developer_user),
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_put_returns_200_for_admin(self, api_client, admin_user):
        tag = TagFactory()
        resp = api_client.put(
            f"{self.URL}{tag.id}/",
            {"name": "Updated Tag", "slug": tag.slug},
            **get_auth_header(admin_user),
        )
        assert resp.status_code == status.HTTP_200_OK

    def test_delete_returns_403_for_non_admin(self, api_client, end_user_user):
        tag = TagFactory()
        resp = api_client.delete(
            f"{self.URL}{tag.id}/", **get_auth_header(end_user_user)
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_returns_204_for_admin(self, api_client, admin_user):
        tag = TagFactory()
        resp = api_client.delete(
            f"{self.URL}{tag.id}/", **get_auth_header(admin_user)
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT


# =====================================================================
#  GameViewSet — /api/v1/games/games/  (most important)
# =====================================================================


@pytest.mark.django_db
class TestGameAPI:
    """
    Game catalog CRUD with complex permission model:
    - GET: public
    - POST: developer/owner/admin
    - PUT/DELETE: owner/admin (object-level via DeveloperMembership)
    - Soft-delete sets is_active=False
    """

    URL = "/api/v1/games/games/"

    # ── Helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _game_payload(developer, publisher, genre, platform, **overrides):
        """Build a valid game creation payload."""
        data = {
            "title": "Test Game",
            "slug": "test-game",
            "game_type": "base_game",
            "short_description": "A test game.",
            "description": "Full description of the test game.",
            "developer_ids": [str(developer.id)],
            "publisher_ids": [str(publisher.id)],
            "genre_ids": [str(genre.id)],
            "platform_ids": [str(platform.id)],
        }
        data.update(overrides)
        return data

    @pytest.fixture
    def catalog_prereqs(self):
        """Create the minimum related objects needed to create a game."""
        return {
            "developer": DeveloperFactory(),
            "publisher": PublisherFactory(),
            "genre": GenreFactory(),
            "platform": PlatformFactory(),
        }

    # ── List (public) ───────────────────────────────────────────────

    def test_list_returns_200_for_anon(self, api_client):
        GameFactory.create_batch(3)
        resp = api_client.get(self.URL)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 3

    def test_list_returns_paginated_results(self, api_client):
        GameFactory.create_batch(3)
        resp = api_client.get(self.URL)
        assert "count" in resp.data
        assert "results" in resp.data

    # ── Detail (public) ─────────────────────────────────────────────

    def test_detail_returns_200_for_anon(self, api_client):
        game = GameFactory()
        resp = api_client.get(f"{self.URL}{game.id}/")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["title"] == game.title

    def test_detail_returns_nested_data(self, api_client):
        dev = DeveloperFactory()
        genre = GenreFactory()
        game = GameFactory(developers=[dev], genres=[genre])
        resp = api_client.get(f"{self.URL}{game.id}/")
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["developers"]) == 1
        assert resp.data["developers"][0]["name"] == dev.name

    # ── Create permissions ──────────────────────────────────────────

    def test_create_returns_401_for_anon(self, api_client, catalog_prereqs):
        payload = self._game_payload(**catalog_prereqs)
        resp = api_client.post(self.URL, payload, format="json")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_returns_403_for_end_user(
        self, api_client, end_user_user, catalog_prereqs
    ):
        payload = self._game_payload(**catalog_prereqs)
        resp = api_client.post(
            self.URL, payload, format="json", **get_auth_header(end_user_user)
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_create_returns_201_for_developer(
        self, api_client, developer_user, catalog_prereqs
    ):
        payload = self._game_payload(**catalog_prereqs)
        resp = api_client.post(
            self.URL, payload, format="json", **get_auth_header(developer_user)
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["title"] == "Test Game"

    def test_create_returns_201_for_admin(
        self, api_client, admin_user, catalog_prereqs
    ):
        payload = self._game_payload(**catalog_prereqs, slug="admin-game")
        resp = api_client.post(
            self.URL, payload, format="json", **get_auth_header(admin_user)
        )
        assert resp.status_code == status.HTTP_201_CREATED

    def test_create_game_links_developer_and_publisher(
        self, api_client, developer_user, catalog_prereqs
    ):
        payload = self._game_payload(**catalog_prereqs)
        resp = api_client.post(
            self.URL, payload, format="json", **get_auth_header(developer_user)
        )
        assert resp.status_code == status.HTTP_201_CREATED
        game = Game.objects.get(slug="test-game")
        assert game.developers.count() == 1
        assert game.publishers.count() == 1

    # ── Update permissions (object-level ownership) ─────────────────

    def test_put_returns_403_for_non_owner_developer(
        self, api_client, developer_user, catalog_prereqs
    ):
        """A developer who does NOT own the game cannot update it."""
        game = GameFactory(
            developers=[catalog_prereqs["developer"]],
            publishers=[catalog_prereqs["publisher"]],
        )
        # developer_user has NO membership linking to this developer
        payload = self._game_payload(**catalog_prereqs, title="Hacked Title")
        resp = api_client.put(
            f"{self.URL}{game.id}/",
            payload,
            format="json",
            **get_auth_header(developer_user),
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_put_returns_200_for_game_owner(
        self, api_client, developer_user, catalog_prereqs
    ):
        """A developer who IS a member of the game's dev org can update it."""
        dev = catalog_prereqs["developer"]
        pub = catalog_prereqs["publisher"]
        DeveloperMembershipFactory(user=developer_user, developer=dev)
        game = GameFactory(
            developers=[dev],
            publishers=[pub],
            genres=[catalog_prereqs["genre"]],
            platforms=[catalog_prereqs["platform"]],
        )
        payload = self._game_payload(
            **catalog_prereqs, title="Updated Title", slug=game.slug
        )
        resp = api_client.put(
            f"{self.URL}{game.id}/",
            payload,
            format="json",
            **get_auth_header(developer_user),
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["title"] == "Updated Title"

    def test_put_returns_200_for_admin(
        self, api_client, admin_user, catalog_prereqs
    ):
        """Admin can update any game regardless of ownership."""
        game = GameFactory(
            developers=[catalog_prereqs["developer"]],
            publishers=[catalog_prereqs["publisher"]],
        )
        payload = self._game_payload(
            **catalog_prereqs, title="Admin Update", slug=game.slug
        )
        resp = api_client.put(
            f"{self.URL}{game.id}/",
            payload,
            format="json",
            **get_auth_header(admin_user),
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["title"] == "Admin Update"

    # ── Soft-delete ─────────────────────────────────────────────────

    def test_delete_returns_204_for_owner_and_soft_deletes(
        self, api_client, developer_user
    ):
        dev = DeveloperFactory()
        DeveloperMembershipFactory(user=developer_user, developer=dev)
        game = GameFactory(developers=[dev])
        resp = api_client.delete(
            f"{self.URL}{game.id}/", **get_auth_header(developer_user)
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        game.refresh_from_db()
        assert game.is_active is False  # soft-deleted, not hard-deleted

    def test_delete_returns_403_for_non_owner(
        self, api_client, developer_user
    ):
        game = GameFactory(developers=[DeveloperFactory()])
        resp = api_client.delete(
            f"{self.URL}{game.id}/", **get_auth_header(developer_user)
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_returns_204_for_admin(self, api_client, admin_user):
        game = GameFactory()
        resp = api_client.delete(
            f"{self.URL}{game.id}/", **get_auth_header(admin_user)
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    # ── /my-games/ action ───────────────────────────────────────────

    def test_my_games_returns_401_for_anon(self, api_client):
        resp = api_client.get(f"{self.URL}my-games/")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_my_games_returns_200_for_authenticated(
        self, api_client, developer_user
    ):
        resp = api_client.get(
            f"{self.URL}my-games/", **get_auth_header(developer_user)
        )
        assert resp.status_code == status.HTTP_200_OK

    def test_my_games_returns_only_owned_games(
        self, api_client, developer_user
    ):
        dev = DeveloperFactory()
        DeveloperMembershipFactory(user=developer_user, developer=dev)
        owned_game = GameFactory(developers=[dev])
        GameFactory()  # someone else's game
        resp = api_client.get(
            f"{self.URL}my-games/", **get_auth_header(developer_user)
        )
        assert resp.status_code == status.HTTP_200_OK
        slugs = [g["slug"] for g in resp.data["results"]]
        assert owned_game.slug in slugs
        assert len(resp.data["results"]) == 1

    def test_my_games_via_publisher_membership(
        self, api_client, developer_user
    ):
        pub = PublisherFactory()
        PublisherMembershipFactory(user=developer_user, publisher=pub)
        owned_game = GameFactory(publishers=[pub])
        resp = api_client.get(
            f"{self.URL}my-games/", **get_auth_header(developer_user)
        )
        ids = [g["id"] for g in resp.data["results"]]
        assert str(owned_game.id) in ids

    # ── /{id}/related-content/ action ───────────────────────────────

    def test_related_content_returns_dlcs(self, api_client):
        base = GameFactory()
        dlc = GameFactory(game_type=Game.GameType.DLC, base_game=base)
        GameFactory()  # unrelated game
        resp = api_client.get(f"{self.URL}{base.id}/related-content/")
        assert resp.status_code == status.HTTP_200_OK
        slugs = [g["slug"] for g in resp.data["results"]]
        assert dlc.slug in slugs
        assert len(resp.data["results"]) == 1

    def test_related_content_excludes_inactive(self, api_client):
        base = GameFactory()
        GameFactory(
            game_type=Game.GameType.DLC, base_game=base, is_active=False
        )
        resp = api_client.get(f"{self.URL}{base.id}/related-content/")
        assert resp.data["count"] == 0


# =====================================================================
#  BundleViewSet — /api/v1/games/bundles/
# =====================================================================


@pytest.mark.django_db
class TestBundleAPI:
    """Bundles: public read, admin-only write."""

    URL = "/api/v1/games/bundles/"

    def test_list_returns_200_for_anon(self, api_client):
        BundleFactory.create_batch(2)
        resp = api_client.get(self.URL)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 2

    def test_detail_returns_200_for_anon(self, api_client):
        bundle = BundleFactory()
        resp = api_client.get(f"{self.URL}{bundle.id}/")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["name"] == bundle.name

    def test_create_returns_401_for_anon(self, api_client):
        resp = api_client.post(
            self.URL,
            {"name": "Summer Sale", "slug": "summer-sale"},
            format="json",
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_returns_403_for_developer(self, api_client, developer_user):
        resp = api_client.post(
            self.URL,
            {"name": "Summer Sale", "slug": "summer-sale"},
            format="json",
            **get_auth_header(developer_user),
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_create_returns_201_for_admin(self, api_client, admin_user):
        game = GameFactory()
        payload = {
            "name": "Summer Sale Bundle",
            "slug": "summer-sale-bundle",
            "description": "Great deals!",
            "game_ids": [str(game.id)],
        }
        resp = api_client.post(
            self.URL, payload, format="json", **get_auth_header(admin_user)
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["name"] == "Summer Sale Bundle"

    def test_create_bundle_with_games(self, api_client, admin_user):
        g1 = GameFactory()
        g2 = GameFactory()
        payload = {
            "name": "Mega Bundle",
            "slug": "mega-bundle",
            "game_ids": [str(g1.id), str(g2.id)],
        }
        resp = api_client.post(
            self.URL, payload, format="json", **get_auth_header(admin_user)
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert len(resp.data["items"]) == 2

    def test_put_returns_403_for_non_admin(self, api_client, end_user_user):
        bundle = BundleFactory()
        resp = api_client.put(
            f"{self.URL}{bundle.id}/",
            {"name": "Hacked", "slug": bundle.slug},
            format="json",
            **get_auth_header(end_user_user),
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_put_returns_200_for_admin(self, api_client, admin_user):
        bundle = BundleFactory()
        resp = api_client.put(
            f"{self.URL}{bundle.id}/",
            {
                "name": "Updated Bundle",
                "slug": bundle.slug,
                "description": "Updated desc",
            },
            format="json",
            **get_auth_header(admin_user),
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["name"] == "Updated Bundle"

    def test_delete_returns_403_for_non_admin(self, api_client, developer_user):
        bundle = BundleFactory()
        resp = api_client.delete(
            f"{self.URL}{bundle.id}/", **get_auth_header(developer_user)
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_returns_204_for_admin(self, api_client, admin_user):
        bundle = BundleFactory()
        resp = api_client.delete(
            f"{self.URL}{bundle.id}/", **get_auth_header(admin_user)
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT


# =====================================================================
#  SystemRequirementViewSet — /api/v1/games/system-requirements/
# =====================================================================


@pytest.mark.django_db
class TestSystemRequirementAPI:
    """System requirements: public read, owner/admin write."""

    URL = "/api/v1/games/system-requirements/"

    def test_list_returns_200_for_anon(self, api_client):
        SystemRequirementFactory()
        resp = api_client.get(self.URL)
        assert resp.status_code == status.HTTP_200_OK

    def test_detail_returns_200_for_anon(self, api_client):
        sr = SystemRequirementFactory()
        resp = api_client.get(f"{self.URL}{sr.id}/")
        assert resp.status_code == status.HTTP_200_OK

    def test_create_returns_401_for_anon(self, api_client):
        game = GameFactory()
        platform = PlatformFactory()
        payload = {
            "game_id": str(game.id),
            "platform_id": str(platform.id),
            "tier": "minimum",
            "os_version": "Windows 10",
            "cpu": "Intel i5",
            "ram_gb": 8,
        }
        resp = api_client.post(self.URL, payload, format="json")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_returns_201_for_admin(self, api_client, admin_user):
        game = GameFactory()
        platform = PlatformFactory()
        payload = {
            "game_id": str(game.id),
            "platform_id": str(platform.id),
            "tier": "minimum",
            "os_version": "Windows 10",
            "cpu": "Intel i5",
            "gpu": "GTX 1060",
            "ram_gb": 8,
            "storage_gb": 50,
        }
        resp = api_client.post(
            self.URL, payload, format="json", **get_auth_header(admin_user)
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["tier"] == "minimum"

    def test_create_returns_201_for_game_owner(
        self, api_client, developer_user
    ):
        dev = DeveloperFactory()
        DeveloperMembershipFactory(user=developer_user, developer=dev)
        game = GameFactory(developers=[dev])
        platform = PlatformFactory()
        payload = {
            "game_id": str(game.id),
            "platform_id": str(platform.id),
            "tier": "recommended",
            "cpu": "Intel i7",
            "ram_gb": 16,
        }
        resp = api_client.post(
            self.URL,
            payload,
            format="json",
            **get_auth_header(developer_user),
        )
        assert resp.status_code == status.HTTP_201_CREATED


# =====================================================================
#  PublisherViewSet — /api/v1/games/publishers/
# =====================================================================


@pytest.mark.django_db
class TestPublisherAPI:
    """Publisher CRUD: public read, admin-only write."""

    URL = "/api/v1/games/publishers/"

    def test_list_returns_200_for_anon(self, api_client):
        PublisherFactory.create_batch(2)
        resp = api_client.get(self.URL)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 2

    def test_detail_returns_200_for_anon(self, api_client):
        pub = PublisherFactory()
        resp = api_client.get(f"{self.URL}{pub.id}/")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["name"] == pub.name

    def test_create_returns_401_for_anon(self, api_client):
        resp = api_client.post(
            self.URL, {"name": "Pub", "slug": "pub"}, format="json"
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_returns_201_for_admin(self, api_client, admin_user):
        resp = api_client.post(
            self.URL,
            {"name": "Big Pub", "slug": "big-pub"},
            format="json",
            **get_auth_header(admin_user),
        )
        assert resp.status_code == status.HTTP_201_CREATED

    def test_delete_returns_204_for_admin(self, api_client, admin_user):
        pub = PublisherFactory()
        resp = api_client.delete(
            f"{self.URL}{pub.id}/", **get_auth_header(admin_user)
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT
