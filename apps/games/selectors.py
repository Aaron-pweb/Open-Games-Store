"""
Selectors for apps.games — read-only query functions.

Selectors return QuerySet objects (lazy, not evaluated) so views
can chain pagination, filtering, or annotation on top.

Convention:
    get_<plural>()     → returns a QuerySet (for list views)
    get_<singular>_by_id()  → returns a single object or raises Http404
"""

import uuid

from django.db import models
from django.shortcuts import get_object_or_404

from apps.games.models import (
    AgeRating,
    AgeRatingBoard,
    Bundle,
    ContentDescriptor,
    Developer,
    Feature,
    Franchise,
    Game,
    GameLanguageSupport,
    GameMedia,
    Genre,
    Language,
    Platform,
    Publisher,
    SystemRequirement,
    Tag,
)


# ── Developer ────────────────────────────────────────────────────────


def get_developers(*, is_verified: bool | None = None):
    """Return all developers, optionally filtered by verification status."""
    qs = Developer.objects.all().order_by("name")
    if is_verified is not None:
        qs = qs.filter(verified=is_verified)
    return qs


def get_developer_by_id(*, developer_id: uuid.UUID) -> Developer:
    """Return a single developer or raise Http404."""
    return get_object_or_404(Developer, pk=developer_id)


# ── Publisher ────────────────────────────────────────────────────────


def get_publishers():
    return Publisher.objects.all().order_by("name")


def get_publisher_by_id(*, publisher_id: uuid.UUID) -> Publisher:
    return get_object_or_404(Publisher, pk=publisher_id)


# ── Franchise ────────────────────────────────────────────────────────


def get_franchises():
    return Franchise.objects.all().order_by("name")


def get_franchise_by_id(*, franchise_id: uuid.UUID) -> Franchise:
    return get_object_or_404(Franchise, pk=franchise_id)


# ── Genre ────────────────────────────────────────────────────────────


def get_genres():
    return Genre.objects.all().order_by("name")


def get_genre_by_id(*, genre_id: uuid.UUID) -> Genre:
    return get_object_or_404(Genre, pk=genre_id)


# ── Tag ──────────────────────────────────────────────────────────────


def get_tags(*, is_approved: bool | None = None):
    """
    Return tags. Public endpoints should pass is_approved=True
    to hide unapproved community suggestions.
    """
    qs = Tag.objects.all().order_by("name")
    if is_approved is not None:
        qs = qs.filter(is_approved=is_approved)
    return qs


def get_tag_by_id(*, tag_id: uuid.UUID) -> Tag:
    return get_object_or_404(Tag, pk=tag_id)


# ── Feature ──────────────────────────────────────────────────────────


def get_features():
    return Feature.objects.all().order_by("name")


def get_feature_by_id(*, feature_id: uuid.UUID) -> Feature:
    return get_object_or_404(Feature, pk=feature_id)


# ── Platform ─────────────────────────────────────────────────────────


def get_platforms():
    return Platform.objects.all().order_by("name")


def get_platform_by_id(*, platform_id: uuid.UUID) -> Platform:
    return get_object_or_404(Platform, pk=platform_id)


# ── Language ─────────────────────────────────────────────────────────


def get_languages():
    return Language.objects.all().order_by("name")


def get_language_by_id(*, language_id: uuid.UUID) -> Language:
    return get_object_or_404(Language, pk=language_id)


# ── AgeRatingBoard ───────────────────────────────────────────────────


def get_age_rating_boards():
    return AgeRatingBoard.objects.all().order_by("name")


def get_age_rating_board_by_id(*, board_id: uuid.UUID) -> AgeRatingBoard:
    return get_object_or_404(AgeRatingBoard, pk=board_id)


# ── ContentDescriptor ────────────────────────────────────────────────


def get_content_descriptors():
    return ContentDescriptor.objects.all().order_by("name")


def get_content_descriptor_by_id(*, descriptor_id: uuid.UUID) -> ContentDescriptor:
    return get_object_or_404(ContentDescriptor, pk=descriptor_id)


# ── AgeRating (composed — needs prefetching) ─────────────────────────


def get_age_ratings():
    return (
        AgeRating.objects
        .select_related("board")
        .prefetch_related("descriptors")
        .all()
    )


def get_age_rating_by_id(*, rating_id: uuid.UUID) -> AgeRating:
    return get_object_or_404(
        AgeRating.objects.select_related("board").prefetch_related("descriptors"),
        pk=rating_id,
    )


# ── Game ─────────────────────────────────────────────────────────────


def get_games():
    """
    Return the game catalog optimized for list views.
    Prefetches relations commonly shown on game cards.
    Does NOT prefetch everything — the detail view has its own selector.
    """
    return (
        Game.objects
        .select_related("franchise", "age_rating", "age_rating__board")
        .prefetch_related("developers", "publishers", "genres", "platforms")
        .order_by("-release_date", "title")
    )


def get_game_by_id(*, game_id: uuid.UUID) -> Game:
    """
    Return a single game with ALL relations prefetched for the detail view.
    Intentionally heavier than the list selector.
    """
    return get_object_or_404(
        Game.objects
        .select_related("franchise", "age_rating", "age_rating__board", "base_game")
        .prefetch_related(
            "developers",
            "publishers",
            "genres",
            "tags",
            "features",
            "platforms",
            "gamelanguagesupport_set__language",
            "system_requirements__platform",
            "media",
            "related_content",
            "bundles",
        ),
        pk=game_id,
    )


def get_games_for_user(*, user):
    """
    Return only games the user owns through Developer/Publisher membership.
    Used by the /my-games/ endpoint.
    """
    dev_ids = user.developer_memberships.values_list("developer_id", flat=True)
    pub_ids = user.publisher_memberships.values_list("publisher_id", flat=True)
    return (
        Game.objects
        .filter(
            models.Q(developers__id__in=dev_ids)
            | models.Q(publishers__id__in=pub_ids)
        )
        .distinct()
        .select_related("franchise")
        .prefetch_related("developers", "publishers", "genres", "platforms")
        .order_by("-updated_at")
    )


def get_game_related_content(*, game_id: uuid.UUID):
    """Return DLC/expansions/soundtracks/demos for a base game."""
    return (
        Game.objects
        .filter(base_game_id=game_id, is_active=True)
        .select_related("franchise")
        .prefetch_related("developers", "genres", "platforms")
        .order_by("game_type", "title")
    )


# ── Game child objects ───────────────────────────────────────────────


def get_game_system_requirements(*, game_id: uuid.UUID):
    return (
        SystemRequirement.objects
        .filter(game_id=game_id)
        .select_related("platform")
        .order_by("platform__name", "tier")
    )


def get_game_media(*, game_id: uuid.UUID):
    return GameMedia.objects.filter(game_id=game_id).order_by("order")


def get_game_language_support(*, game_id: uuid.UUID):
    return (
        GameLanguageSupport.objects
        .filter(game_id=game_id)
        .select_related("language")
        .order_by("language__name")
    )


# ── Bundle ───────────────────────────────────────────────────────────


def get_bundles():
    return (
        Bundle.objects
        .prefetch_related("bundleitem_set__game")
        .order_by("name")
    )


def get_bundle_by_id(*, bundle_id: uuid.UUID) -> Bundle:
    return get_object_or_404(
        Bundle.objects.prefetch_related("bundleitem_set__game"),
        pk=bundle_id,
    )
