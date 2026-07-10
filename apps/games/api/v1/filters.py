"""
FilterSets for apps.games API v1.

Uses django-filter for declarative queryset filtering.
These are used by the ViewSets to parse query parameters.
"""

import django_filters

from apps.games.models import Bundle, Game


class GameFilterSet(django_filters.FilterSet):
    """
    Filters for the Game list endpoint.

    Usage examples:
        ?game_type=dlc
        ?release_status=released
        ?is_active=true
        ?genres=<uuid1>,<uuid2>
        ?platforms=<uuid>
        ?developers=<uuid>
        ?publishers=<uuid>
        ?franchise=<uuid>
        ?base_game=<uuid>       (find all DLC/expansions for a game)
        ?tags=<uuid>
        ?features=<uuid>
        ?release_date_after=2025-01-01
        ?release_date_before=2025-12-31
        ?search=witcher          (searches title and short_description)
        ?ordering=-release_date  (sort by newest first)
    """

    # ── Exact filters ──
    game_type = django_filters.ChoiceFilter(choices=Game.GameType.choices)
    release_status = django_filters.ChoiceFilter(choices=Game.ReleaseStatus.choices)
    is_active = django_filters.BooleanFilter()
    franchise = django_filters.UUIDFilter(field_name="franchise__id")
    base_game = django_filters.UUIDFilter(field_name="base_game__id")

    # ── Relation filters (accept comma-separated UUIDs) ──
    genres = django_filters.UUIDFilter(field_name="genres__id")
    tags = django_filters.UUIDFilter(field_name="tags__id")
    features = django_filters.UUIDFilter(field_name="features__id")
    platforms = django_filters.UUIDFilter(field_name="platforms__id")
    developers = django_filters.UUIDFilter(field_name="developers__id")
    publishers = django_filters.UUIDFilter(field_name="publishers__id")

    # ── Date range ──
    release_date_after = django_filters.DateFilter(
        field_name="release_date", lookup_expr="gte"
    )
    release_date_before = django_filters.DateFilter(
        field_name="release_date", lookup_expr="lte"
    )

    class Meta:
        model = Game
        fields = []  # All filters declared above


class BundleFilterSet(django_filters.FilterSet):
    """
    Filters for the Bundle list endpoint.

    Usage examples:
        ?is_active=true
        ?search=deluxe
    """

    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Bundle
        fields = []
