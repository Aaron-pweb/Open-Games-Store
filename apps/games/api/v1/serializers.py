"""
Serializers for apps.games API v1.

Naming conventions:
    <Model>Serializer         → standard read/write (leaf models)
    <Model>ListSerializer     → lightweight read-only (for list views)
    <Model>DetailSerializer   → full read-only (for detail views)
    <Model>WriteSerializer    → write-only (for create/update)
"""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer

from apps.games.models import (
    AgeRating,
    AgeRatingBoard,
    Bundle,
    BundleItem,
    ContentDescriptor,
    Developer,
    DeveloperMembership,
    Feature,
    Franchise,
    Game,
    GameLanguageSupport,
    GameMedia,
    Genre,
    Language,
    Platform,
    Publisher,
    PublisherMembership,
    SystemRequirement,
    Tag,
)


# ── Leaf model serializers ───────────────────────────────────────────


class DeveloperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Developer
        fields = [
            "id", "name", "slug", "website", "country",
            "verified", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = [
            "id", "name", "slug", "website",
            "revenue_share_percent", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class FranchiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Franchise
        fields = ["id", "name", "slug", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name", "slug", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug", "is_approved", "created_at", "updated_at"]
        read_only_fields = ["id", "is_approved", "created_at", "updated_at"]


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ["id", "name", "icon_key", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ["id", "name", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ["id", "code", "name", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class AgeRatingBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgeRatingBoard
        fields = ["id", "name", "region", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ContentDescriptorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentDescriptor
        fields = ["id", "name", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


# ── Membership serializers ───────────────────────────────────────────


class DeveloperMembershipSerializer(serializers.ModelSerializer):
    developer = DeveloperSerializer(read_only=True)
    developer_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = DeveloperMembership
        fields = [
            "id", "user", "developer", "developer_id",
            "role", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class PublisherMembershipSerializer(serializers.ModelSerializer):
    publisher = PublisherSerializer(read_only=True)
    publisher_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = PublisherMembership
        fields = [
            "id", "user", "publisher", "publisher_id",
            "role", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


# ── Composed model serializers ───────────────────────────────────────


class AgeRatingSerializer(serializers.ModelSerializer):
    """Read: nested board + descriptors. Write: accepts IDs."""

    board = AgeRatingBoardSerializer(read_only=True)
    board_id = serializers.UUIDField(write_only=True)
    descriptors = ContentDescriptorSerializer(many=True, read_only=True)
    descriptor_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = AgeRating
        fields = [
            "id", "board", "board_id", "value",
            "descriptors", "descriptor_ids",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class GameLanguageSupportSerializer(serializers.ModelSerializer):
    language = LanguageSerializer(read_only=True)
    language_id = serializers.UUIDField(write_only=True)
    game_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = GameLanguageSupport
        fields = [
            "id", "game_id", "language", "language_id",
            "interface", "audio", "subtitles",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SystemRequirementSerializer(serializers.ModelSerializer):
    platform = PlatformSerializer(read_only=True)
    platform_id = serializers.UUIDField(write_only=True)
    game_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = SystemRequirement
        fields = [
            "id", "game_id", "platform", "platform_id", "tier",
            "os_version", "cpu", "gpu", "ram_gb", "storage_gb", "notes",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class GameMediaSerializer(serializers.ModelSerializer):
    game_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = GameMedia
        fields = [
            "id", "game_id", "media_type", "url",
            "thumbnail_url", "order",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# ── Bundle serializers ───────────────────────────────────────────────


class BundleItemSerializer(serializers.ModelSerializer):
    """Read: nested game summary. Write: just game_id."""

    game_title = serializers.CharField(source="game.title", read_only=True)
    game_slug = serializers.CharField(source="game.slug", read_only=True)
    game_id = serializers.UUIDField(source="game.id", read_only=True)

    class Meta:
        model = BundleItem
        fields = ["id", "game_id", "game_title", "game_slug"]
        read_only_fields = ["id"]


class BundleSerializer(serializers.ModelSerializer):
    items = BundleItemSerializer(
        source="bundleitem_set", many=True, read_only=True
    )

    class Meta:
        model = Bundle
        fields = [
            "id", "name", "slug", "description",
            "starts_at", "ends_at", "is_active",
            "items", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BundleWriteSerializer(serializers.ModelSerializer):
    game_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
    )

    class Meta:
        model = Bundle
        fields = [
            "name", "slug", "description",
            "starts_at", "ends_at", "is_active",
            "game_ids",
        ]


# ── Game serializers ─────────────────────────────────────────────────


class GameMinimalSerializer(serializers.ModelSerializer):
    """Ultra-light serializer for nested references (e.g., base_game, related_content)."""

    class Meta:
        model = Game
        fields = [
            "id", "title", "slug", "game_type", "release_status",
        ]
        read_only_fields = fields


@extend_schema_serializer(
    exclude_fields=[],
)
class GameListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views — game card data."""

    developers = DeveloperSerializer(many=True, read_only=True)
    publishers = PublisherSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    platforms = PlatformSerializer(many=True, read_only=True)
    franchise = FranchiseSerializer(read_only=True)

    class Meta:
        model = Game
        fields = [
            "id", "title", "slug", "game_type",
            "release_status", "release_date",
            "short_description", "is_active",
            "developers", "publishers", "genres",
            "platforms", "franchise",
            "created_at", "updated_at",
        ]
        read_only_fields = fields


class GameDetailSerializer(serializers.ModelSerializer):
    """Full serializer for detail views — all nested relations."""

    developers = DeveloperSerializer(many=True, read_only=True)
    publishers = PublisherSerializer(many=True, read_only=True)
    franchise = FranchiseSerializer(read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    features = FeatureSerializer(many=True, read_only=True)
    platforms = PlatformSerializer(many=True, read_only=True)
    age_rating = AgeRatingSerializer(read_only=True)
    base_game = GameMinimalSerializer(read_only=True)

    language_support = GameLanguageSupportSerializer(
        source="gamelanguagesupport_set", many=True, read_only=True
    )
    system_requirements = SystemRequirementSerializer(
        many=True, read_only=True
    )
    media = GameMediaSerializer(many=True, read_only=True)
    related_content = GameMinimalSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = [
            "id", "title", "slug", "game_type",
            "base_game", "release_status", "release_date",
            "short_description", "description", "is_active",
            "developers", "publishers", "franchise",
            "genres", "tags", "features", "platforms",
            "age_rating", "language_support",
            "system_requirements", "media",
            "related_content",
            "created_at", "updated_at",
        ]
        read_only_fields = fields


class GameWriteSerializer(serializers.Serializer):
    """
    Write serializer for creating/updating Games.
    Accepts IDs for all relations — the service layer resolves them.
    """

    title = serializers.CharField(max_length=255)
    slug = serializers.SlugField(max_length=255)
    game_type = serializers.ChoiceField(
        choices=Game.GameType.choices,
        default=Game.GameType.BASE_GAME,
    )
    base_game_id = serializers.UUIDField(required=False, allow_null=True)
    franchise_id = serializers.UUIDField(required=False, allow_null=True)
    age_rating_id = serializers.UUIDField(required=False, allow_null=True)
    short_description = serializers.CharField(max_length=500)
    description = serializers.CharField()
    release_status = serializers.ChoiceField(
        choices=Game.ReleaseStatus.choices,
        default=Game.ReleaseStatus.ANNOUNCED,
    )
    release_date = serializers.DateField(required=False, allow_null=True)
    is_active = serializers.BooleanField(default=True)

    # M2M IDs
    developer_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False
    )
    publisher_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False
    )
    genre_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False
    )
    tag_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False
    )
    feature_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False
    )
    platform_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False
    )
