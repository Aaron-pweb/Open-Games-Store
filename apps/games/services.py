"""
Services for apps.games — write / business-logic functions.

Services accept explicit keyword-only arguments (not serializer data
or request objects), perform validation, and return the created/updated
instance. This makes them callable from views, Celery tasks, management
commands, and the admin shell without coupling to HTTP.

Convention:
    create_<model>()  → creates and returns a new instance
    update_<model>()  → updates fields on an existing instance
    Specialised verbs for non-CRUD actions (soft_delete_game, approve_tag)
"""

import uuid
from datetime import date

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

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


# ── Developer ────────────────────────────────────────────────────────


def create_developer(
    *,
    name: str,
    slug: str,
    website: str = "",
    country: str = "",
    verified: bool = False,
) -> Developer:
    developer = Developer(
        name=name,
        slug=slug,
        website=website,
        country=country,
        verified=verified,
    )
    developer.full_clean()
    developer.save()
    return developer


def update_developer(*, instance: Developer, data: dict) -> Developer:
    """
    Update a developer with the provided fields.
    ``data`` is a dict of field_name → new_value (only fields being changed).
    """
    for field, value in data.items():
        setattr(instance, field, value)
    instance.full_clean()
    instance.save(update_fields=[*data.keys(), "updated_at"])
    return instance


# ── Publisher ────────────────────────────────────────────────────────


def create_publisher(
    *,
    name: str,
    slug: str,
    website: str = "",
    revenue_share_percent=70.00,
) -> Publisher:
    publisher = Publisher(
        name=name,
        slug=slug,
        website=website,
        revenue_share_percent=revenue_share_percent,
    )
    publisher.full_clean()
    publisher.save()
    return publisher


def update_publisher(*, instance: Publisher, data: dict) -> Publisher:
    for field, value in data.items():
        setattr(instance, field, value)
    instance.full_clean()
    instance.save(update_fields=[*data.keys(), "updated_at"])
    return instance


# ── Franchise ────────────────────────────────────────────────────────


def create_franchise(*, name: str, slug: str) -> Franchise:
    franchise = Franchise(name=name, slug=slug)
    franchise.full_clean()
    franchise.save()
    return franchise


def update_franchise(*, instance: Franchise, data: dict) -> Franchise:
    for field, value in data.items():
        setattr(instance, field, value)
    instance.full_clean()
    instance.save(update_fields=[*data.keys(), "updated_at"])
    return instance


# ── Genre ────────────────────────────────────────────────────────────


def create_genre(*, name: str, slug: str) -> Genre:
    genre = Genre(name=name, slug=slug)
    genre.full_clean()
    genre.save()
    return genre


def update_genre(*, instance: Genre, data: dict) -> Genre:
    for field, value in data.items():
        setattr(instance, field, value)
    instance.full_clean()
    instance.save(update_fields=[*data.keys(), "updated_at"])
    return instance


# ── Tag ──────────────────────────────────────────────────────────────


def create_tag(
    *,
    name: str,
    slug: str,
    is_approved: bool = True,
    created_by_user=None,
) -> Tag:
    """
    If created_by_user is a non-admin, force is_approved=False
    so the tag goes through moderation.
    """
    if created_by_user and not created_by_user.is_admin_role:
        is_approved = False
    tag = Tag(name=name, slug=slug, is_approved=is_approved)
    tag.full_clean()
    tag.save()
    return tag


def update_tag(*, instance: Tag, data: dict) -> Tag:
    for field, value in data.items():
        setattr(instance, field, value)
    instance.full_clean()
    instance.save(update_fields=[*data.keys(), "updated_at"])
    return instance


def approve_tag(*, instance: Tag) -> Tag:
    """Admin-only action to approve a community-suggested tag."""
    instance.is_approved = True
    instance.save(update_fields=["is_approved", "updated_at"])
    return instance


# ── Feature ──────────────────────────────────────────────────────────


def create_feature(*, name: str, icon_key: str = "") -> Feature:
    feature = Feature(name=name, icon_key=icon_key)
    feature.full_clean()
    feature.save()
    return feature


def update_feature(*, instance: Feature, data: dict) -> Feature:
    for field, value in data.items():
        setattr(instance, field, value)
    instance.full_clean()
    instance.save(update_fields=[*data.keys(), "updated_at"])
    return instance


# ── Platform ─────────────────────────────────────────────────────────


def create_platform(*, name: str) -> Platform:
    platform = Platform(name=name)
    platform.full_clean()
    platform.save()
    return platform


def update_platform(*, instance: Platform, data: dict) -> Platform:
    for field, value in data.items():
        setattr(instance, field, value)
    instance.full_clean()
    instance.save(update_fields=[*data.keys(), "updated_at"])
    return instance


# ── Language ─────────────────────────────────────────────────────────


def create_language(*, code: str, name: str) -> Language:
    language = Language(code=code, name=name)
    language.full_clean()
    language.save()
    return language


def update_language(*, instance: Language, data: dict) -> Language:
    for field, value in data.items():
        setattr(instance, field, value)
    instance.full_clean()
    instance.save(update_fields=[*data.keys(), "updated_at"])
    return instance


# ── AgeRatingBoard ───────────────────────────────────────────────────


def create_age_rating_board(*, name: str, region: str) -> AgeRatingBoard:
    board = AgeRatingBoard(name=name, region=region)
    board.full_clean()
    board.save()
    return board


def update_age_rating_board(*, instance: AgeRatingBoard, data: dict) -> AgeRatingBoard:
    for field, value in data.items():
        setattr(instance, field, value)
    instance.full_clean()
    instance.save(update_fields=[*data.keys(), "updated_at"])
    return instance


# ── ContentDescriptor ────────────────────────────────────────────────


def create_content_descriptor(*, name: str) -> ContentDescriptor:
    descriptor = ContentDescriptor(name=name)
    descriptor.full_clean()
    descriptor.save()
    return descriptor


def update_content_descriptor(*, instance: ContentDescriptor, data: dict) -> ContentDescriptor:
    for field, value in data.items():
        setattr(instance, field, value)
    instance.full_clean()
    instance.save(update_fields=[*data.keys(), "updated_at"])
    return instance


# ── AgeRating (FK + M2M) ────────────────────────────────────────────


def create_age_rating(
    *,
    board_id: uuid.UUID,
    value: str,
    descriptor_ids: list[uuid.UUID] | None = None,
) -> AgeRating:
    board = get_object_or_404(AgeRatingBoard, pk=board_id)
    age_rating = AgeRating(board=board, value=value)
    age_rating.full_clean()
    age_rating.save()
    if descriptor_ids:
        age_rating.descriptors.set(descriptor_ids)
    return age_rating


def update_age_rating(*, instance: AgeRating, data: dict) -> AgeRating:
    descriptor_ids = data.pop("descriptor_ids", None)
    if "board_id" in data:
        data["board"] = get_object_or_404(AgeRatingBoard, pk=data.pop("board_id"))
    for field, value in data.items():
        setattr(instance, field, value)
    instance.full_clean()
    instance.save()
    if descriptor_ids is not None:
        instance.descriptors.set(descriptor_ids)
    return instance


# ── Game (self-FK + 7 M2M relations) ────────────────────────────────


def create_game(
    *,
    title: str,
    slug: str,
    game_type: str = Game.GameType.BASE_GAME,
    base_game_id: uuid.UUID | None = None,
    franchise_id: uuid.UUID | None = None,
    age_rating_id: uuid.UUID | None = None,
    short_description: str,
    description: str,
    release_status: str = Game.ReleaseStatus.ANNOUNCED,
    release_date: date | None = None,
    is_active: bool = True,
    # M2M IDs
    developer_ids: list[uuid.UUID] | None = None,
    publisher_ids: list[uuid.UUID] | None = None,
    genre_ids: list[uuid.UUID] | None = None,
    tag_ids: list[uuid.UUID] | None = None,
    feature_ids: list[uuid.UUID] | None = None,
    platform_ids: list[uuid.UUID] | None = None,
) -> Game:
    # ── Business rule validation ──
    if game_type != Game.GameType.BASE_GAME and not base_game_id:
        raise ValidationError(
            "DLC, expansions, soundtracks, and demos must reference a base_game."
        )
    if game_type == Game.GameType.BASE_GAME and base_game_id:
        raise ValidationError("A base game cannot have a base_game reference.")

    # ── Resolve FKs ──
    base_game = get_object_or_404(Game, pk=base_game_id) if base_game_id else None
    franchise = get_object_or_404(Franchise, pk=franchise_id) if franchise_id else None
    age_rating = get_object_or_404(AgeRating, pk=age_rating_id) if age_rating_id else None

    game = Game(
        title=title,
        slug=slug,
        game_type=game_type,
        base_game=base_game,
        franchise=franchise,
        age_rating=age_rating,
        short_description=short_description,
        description=description,
        release_status=release_status,
        release_date=release_date,
        is_active=is_active,
    )
    game.full_clean()
    game.save()

    # ── Set M2M relations ──
    if developer_ids:
        game.developers.set(developer_ids)
    if publisher_ids:
        game.publishers.set(publisher_ids)
    if genre_ids:
        game.genres.set(genre_ids)
    if tag_ids:
        game.tags.set(tag_ids)
    if feature_ids:
        game.features.set(feature_ids)
    if platform_ids:
        game.platforms.set(platform_ids)

    return game


def update_game(*, instance: Game, data: dict) -> Game:
    """Update game scalar fields and M2M relations."""
    # ── Extract M2M fields (handled separately) ──
    m2m_fields = {
        "developer_ids": "developers",
        "publisher_ids": "publishers",
        "genre_ids": "genres",
        "tag_ids": "tags",
        "feature_ids": "features",
        "platform_ids": "platforms",
    }
    m2m_updates = {}
    for id_key, relation_name in m2m_fields.items():
        if id_key in data:
            m2m_updates[relation_name] = data.pop(id_key)

    # ── Resolve FK fields ──
    fk_mappings = {
        "base_game_id": ("base_game", Game),
        "franchise_id": ("franchise", Franchise),
        "age_rating_id": ("age_rating", AgeRating),
    }
    for id_key, (field_name, model_class) in fk_mappings.items():
        if id_key in data:
            raw_value = data.pop(id_key)
            data[field_name] = (
                get_object_or_404(model_class, pk=raw_value) if raw_value else None
            )

    # ── Business rule re-validation ──
    game_type = data.get("game_type", instance.game_type)
    base_game = data.get("base_game", instance.base_game)
    if game_type != Game.GameType.BASE_GAME and not base_game:
        raise ValidationError(
            "DLC, expansions, soundtracks, and demos must reference a base_game."
        )
    if game_type == Game.GameType.BASE_GAME and base_game:
        raise ValidationError("A base game cannot have a base_game reference.")

    for field, value in data.items():
        setattr(instance, field, value)
    instance.full_clean()
    instance.save()

    for relation_name, ids in m2m_updates.items():
        getattr(instance, relation_name).set(ids)

    return instance


def soft_delete_game(*, instance: Game) -> Game:
    """Soft-delete: set is_active=False. Never hard-delete sellable content."""
    instance.is_active = False
    instance.save(update_fields=["is_active", "updated_at"])
    return instance


# ── GameLanguageSupport ──────────────────────────────────────────────


def create_game_language_support(
    *,
    game_id: uuid.UUID,
    language_id: uuid.UUID,
    interface: bool = False,
    audio: bool = False,
    subtitles: bool = False,
) -> GameLanguageSupport:
    game = get_object_or_404(Game, pk=game_id)
    language = get_object_or_404(Language, pk=language_id)
    support = GameLanguageSupport(
        game=game,
        language=language,
        interface=interface,
        audio=audio,
        subtitles=subtitles,
    )
    support.full_clean()
    support.save()
    return support


def update_game_language_support(
    *, instance: GameLanguageSupport, data: dict
) -> GameLanguageSupport:
    for field, value in data.items():
        setattr(instance, field, value)
    instance.full_clean()
    instance.save(update_fields=[*data.keys(), "updated_at"])
    return instance


# ── SystemRequirement ────────────────────────────────────────────────


def create_system_requirement(
    *,
    game_id: uuid.UUID,
    platform_id: uuid.UUID,
    tier: str,
    os_version: str = "",
    cpu: str = "",
    gpu: str = "",
    ram_gb: int | None = None,
    storage_gb: int | None = None,
    notes: str = "",
) -> SystemRequirement:
    game = get_object_or_404(Game, pk=game_id)
    platform = get_object_or_404(Platform, pk=platform_id)
    req = SystemRequirement(
        game=game,
        platform=platform,
        tier=tier,
        os_version=os_version,
        cpu=cpu,
        gpu=gpu,
        ram_gb=ram_gb,
        storage_gb=storage_gb,
        notes=notes,
    )
    req.full_clean()
    req.save()
    return req


def update_system_requirement(
    *, instance: SystemRequirement, data: dict
) -> SystemRequirement:
    if "platform_id" in data:
        data["platform"] = get_object_or_404(Platform, pk=data.pop("platform_id"))
    for field, value in data.items():
        setattr(instance, field, value)
    instance.full_clean()
    instance.save()
    return instance


# ── GameMedia ────────────────────────────────────────────────────────


def create_game_media(
    *,
    game_id: uuid.UUID,
    media_type: str,
    url: str,
    thumbnail_url: str = "",
    order: int = 0,
) -> GameMedia:
    game = get_object_or_404(Game, pk=game_id)
    media = GameMedia(
        game=game,
        media_type=media_type,
        url=url,
        thumbnail_url=thumbnail_url,
        order=order,
    )
    media.full_clean()
    media.save()
    return media


def update_game_media(*, instance: GameMedia, data: dict) -> GameMedia:
    for field, value in data.items():
        setattr(instance, field, value)
    instance.full_clean()
    instance.save(update_fields=[*data.keys(), "updated_at"])
    return instance


# ── Bundle ───────────────────────────────────────────────────────────


def create_bundle(
    *,
    name: str,
    slug: str,
    description: str = "",
    starts_at=None,
    ends_at=None,
    is_active: bool = True,
    game_ids: list[uuid.UUID] | None = None,
) -> Bundle:
    bundle = Bundle(
        name=name,
        slug=slug,
        description=description,
        starts_at=starts_at,
        ends_at=ends_at,
        is_active=is_active,
    )
    bundle.full_clean()
    bundle.save()
    if game_ids:
        for gid in game_ids:
            BundleItem.objects.create(bundle=bundle, game_id=gid)
    return bundle


def update_bundle(*, instance: Bundle, data: dict) -> Bundle:
    game_ids = data.pop("game_ids", None)
    for field, value in data.items():
        setattr(instance, field, value)
    instance.full_clean()
    instance.save()
    if game_ids is not None:
        # Replace all bundle items
        instance.bundleitem_set.all().delete()
        for gid in game_ids:
            BundleItem.objects.create(bundle=instance, game_id=gid)
    return instance


# ── Membership services ──────────────────────────────────────────────


def create_developer_membership(
    *,
    user_id: uuid.UUID,
    developer_id: uuid.UUID,
    role: str = DeveloperMembership.MemberRole.MEMBER,
) -> DeveloperMembership:
    membership = DeveloperMembership(
        user_id=user_id,
        developer_id=developer_id,
        role=role,
    )
    membership.full_clean()
    membership.save()
    return membership


def create_publisher_membership(
    *,
    user_id: uuid.UUID,
    publisher_id: uuid.UUID,
    role: str = PublisherMembership.MemberRole.MEMBER,
) -> PublisherMembership:
    membership = PublisherMembership(
        user_id=user_id,
        publisher_id=publisher_id,
        role=role,
    )
    membership.full_clean()
    membership.save()
    return membership
