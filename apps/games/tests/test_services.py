"""
Tests for apps.games.services — comprehensive coverage of every
create / update / specialised service function.

Conventions:
    - Every test class or function touching the DB is marked @pytest.mark.django_db
    - Factories come from apps.games.tests.factories
    - ValidationError is django.core.exceptions.ValidationError
    - Http404 is django.http.Http404 (raised by get_object_or_404)
"""

import uuid

import pytest
from django.core.exceptions import ValidationError
from django.http import Http404

from apps.games.models import (
    DeveloperMembership,
    Game,
    GameMedia,
    PublisherMembership,
    SystemRequirement,
)
from apps.games.services import (
    approve_tag,
    create_age_rating,
    create_age_rating_board,
    create_bundle,
    create_content_descriptor,
    create_developer,
    create_developer_membership,
    create_feature,
    create_franchise,
    create_game,
    create_game_language_support,
    create_game_media,
    create_genre,
    create_language,
    create_platform,
    create_publisher,
    create_publisher_membership,
    create_system_requirement,
    create_tag,
    soft_delete_game,
    update_age_rating,
    update_age_rating_board,
    update_bundle,
    update_content_descriptor,
    update_developer,
    update_feature,
    update_franchise,
    update_game,
    update_genre,
    update_language,
    update_platform,
    update_publisher,
    update_tag,
)
from apps.games.tests.factories import (
    AgeRatingBoardFactory,
    AgeRatingFactory,
    ContentDescriptorFactory,
    DeveloperFactory,
    FeatureFactory,
    FranchiseFactory,
    GameFactory,
    GenreFactory,
    LanguageFactory,
    PlatformFactory,
    PublisherFactory,
    TagFactory,
    make_admin_user,
    make_developer_user,
    make_end_user,
)


# ═══════════════════════════════════════════════════════════════════════
# Developer
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestCreateDeveloper:
    def test_basic_creation(self):
        dev = create_developer(name="Valve", slug="valve")
        assert dev.pk is not None
        assert dev.name == "Valve"
        assert dev.slug == "valve"
        assert dev.website == ""
        assert dev.country == ""
        assert dev.verified is False

    def test_full_params(self):
        dev = create_developer(
            name="CD Projekt Red",
            slug="cdpr",
            website="https://cdprojektred.com",
            country="PL",
            verified=True,
        )
        assert dev.website == "https://cdprojektred.com"
        assert dev.country == "PL"
        assert dev.verified is True

    def test_duplicate_slug_raises_validation_error(self):
        create_developer(name="Studio A", slug="duplicate-slug")
        with pytest.raises(ValidationError):
            create_developer(name="Studio B", slug="duplicate-slug")

    def test_full_clean_validates_url(self):
        with pytest.raises(ValidationError):
            create_developer(name="Bad Site", slug="bad-site", website="not-a-url")


@pytest.mark.django_db
class TestUpdateDeveloper:
    def test_partial_update(self):
        dev = DeveloperFactory()
        updated = update_developer(instance=dev, data={"name": "New Name"})
        assert updated.name == "New Name"
        assert updated.pk == dev.pk

    def test_update_verified_flag(self):
        dev = DeveloperFactory(verified=False)
        updated = update_developer(instance=dev, data={"verified": True})
        assert updated.verified is True

    def test_update_enforces_full_clean(self):
        dev = DeveloperFactory()
        with pytest.raises(ValidationError):
            update_developer(instance=dev, data={"website": "invalid-url"})


# ═══════════════════════════════════════════════════════════════════════
# Publisher
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestCreatePublisher:
    def test_basic_creation(self):
        pub = create_publisher(name="EA", slug="ea")
        assert pub.pk is not None
        assert pub.name == "EA"
        assert pub.slug == "ea"
        assert pub.revenue_share_percent == 70.00

    def test_custom_revenue_share(self):
        pub = create_publisher(
            name="Indie Pub", slug="indie-pub", revenue_share_percent=85.00
        )
        assert pub.revenue_share_percent == 85.00

    def test_duplicate_slug_raises_validation_error(self):
        create_publisher(name="Pub A", slug="pub-dup")
        with pytest.raises(ValidationError):
            create_publisher(name="Pub B", slug="pub-dup")


@pytest.mark.django_db
class TestUpdatePublisher:
    def test_partial_update(self):
        pub = PublisherFactory()
        updated = update_publisher(
            instance=pub, data={"name": "Updated Publisher"}
        )
        assert updated.name == "Updated Publisher"

    def test_update_revenue_share(self):
        pub = PublisherFactory(revenue_share_percent=70.00)
        updated = update_publisher(
            instance=pub, data={"revenue_share_percent": 80.00}
        )
        assert updated.revenue_share_percent == 80.00


# ═══════════════════════════════════════════════════════════════════════
# Franchise
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestCreateFranchise:
    def test_basic_creation(self):
        f = create_franchise(name="The Witcher", slug="the-witcher")
        assert f.pk is not None
        assert f.name == "The Witcher"

    def test_duplicate_slug_raises_validation_error(self):
        create_franchise(name="A", slug="dup-franchise")
        with pytest.raises(ValidationError):
            create_franchise(name="B", slug="dup-franchise")


@pytest.mark.django_db
class TestUpdateFranchise:
    def test_partial_update(self):
        f = FranchiseFactory()
        updated = update_franchise(instance=f, data={"name": "New Franchise"})
        assert updated.name == "New Franchise"


# ═══════════════════════════════════════════════════════════════════════
# Genre
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestCreateGenre:
    def test_basic_creation(self):
        g = create_genre(name="RPG", slug="rpg")
        assert g.pk is not None
        assert g.name == "RPG"

    def test_duplicate_slug_raises_validation_error(self):
        create_genre(name="Action", slug="action")
        with pytest.raises(ValidationError):
            create_genre(name="Action 2", slug="action")


@pytest.mark.django_db
class TestUpdateGenre:
    def test_partial_update(self):
        g = GenreFactory()
        updated = update_genre(instance=g, data={"name": "Strategy"})
        assert updated.name == "Strategy"


# ═══════════════════════════════════════════════════════════════════════
# Tag (special moderation logic)
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestCreateTag:
    def test_admin_creates_approved_tag(self):
        admin = make_admin_user()
        tag = create_tag(
            name="Souls-like", slug="souls-like", created_by_user=admin
        )
        assert tag.is_approved is True

    def test_non_admin_creates_unapproved_tag(self):
        end_user = make_end_user()
        tag = create_tag(
            name="Cozy", slug="cozy", is_approved=True, created_by_user=end_user
        )
        assert tag.is_approved is False

    def test_developer_creates_unapproved_tag(self):
        dev_user = make_developer_user()
        tag = create_tag(
            name="Retro", slug="retro", created_by_user=dev_user
        )
        assert tag.is_approved is False

    def test_without_user_creates_approved_tag(self):
        tag = create_tag(name="Open World", slug="open-world")
        assert tag.is_approved is True

    def test_duplicate_slug_raises_validation_error(self):
        create_tag(name="Tag A", slug="dup-tag")
        with pytest.raises(ValidationError):
            create_tag(name="Tag B", slug="dup-tag")


@pytest.mark.django_db
class TestUpdateTag:
    def test_partial_update(self):
        tag = TagFactory()
        updated = update_tag(instance=tag, data={"name": "Renamed Tag"})
        assert updated.name == "Renamed Tag"


@pytest.mark.django_db
class TestApproveTag:
    def test_sets_is_approved_true(self):
        tag = TagFactory(is_approved=False)
        assert tag.is_approved is False
        approved = approve_tag(instance=tag)
        assert approved.is_approved is True
        tag.refresh_from_db()
        assert tag.is_approved is True

    def test_already_approved_tag_stays_approved(self):
        tag = TagFactory(is_approved=True)
        approved = approve_tag(instance=tag)
        assert approved.is_approved is True


# ═══════════════════════════════════════════════════════════════════════
# Feature
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestCreateFeature:
    def test_basic_creation(self):
        f = create_feature(name="Co-op")
        assert f.pk is not None
        assert f.name == "Co-op"
        assert f.icon_key == ""

    def test_with_icon_key(self):
        f = create_feature(name="Cloud Saves", icon_key="cloud-save")
        assert f.icon_key == "cloud-save"

    def test_duplicate_name_raises_validation_error(self):
        create_feature(name="Unique Feature")
        with pytest.raises(ValidationError):
            create_feature(name="Unique Feature")


@pytest.mark.django_db
class TestUpdateFeature:
    def test_partial_update(self):
        f = FeatureFactory()
        updated = update_feature(instance=f, data={"icon_key": "new-icon"})
        assert updated.icon_key == "new-icon"


# ═══════════════════════════════════════════════════════════════════════
# Platform
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestCreatePlatform:
    def test_basic_creation(self):
        p = create_platform(name="windows")
        assert p.pk is not None
        assert p.name == "windows"

    def test_invalid_name_raises_validation_error(self):
        with pytest.raises(ValidationError):
            create_platform(name="playstation")


@pytest.mark.django_db
class TestUpdatePlatform:
    def test_partial_update(self):
        p = PlatformFactory(name="linux")
        updated = update_platform(instance=p, data={"name": "mac"})
        assert updated.name == "mac"


# ═══════════════════════════════════════════════════════════════════════
# Language
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestCreateLanguage:
    def test_basic_creation(self):
        lang = create_language(code="en", name="English")
        assert lang.pk is not None
        assert lang.code == "en"
        assert lang.name == "English"

    def test_duplicate_code_raises_validation_error(self):
        create_language(code="fr", name="French")
        with pytest.raises(ValidationError):
            create_language(code="fr", name="Français")


@pytest.mark.django_db
class TestUpdateLanguage:
    def test_partial_update(self):
        lang = LanguageFactory()
        updated = update_language(instance=lang, data={"name": "Español"})
        assert updated.name == "Español"


# ═══════════════════════════════════════════════════════════════════════
# AgeRatingBoard
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestCreateAgeRatingBoard:
    def test_basic_creation(self):
        board = create_age_rating_board(name="ESRB", region="North America")
        assert board.pk is not None
        assert board.name == "ESRB"
        assert board.region == "North America"

    def test_duplicate_name_raises_validation_error(self):
        create_age_rating_board(name="PEGI", region="Europe")
        with pytest.raises(ValidationError):
            create_age_rating_board(name="PEGI", region="EU")


@pytest.mark.django_db
class TestUpdateAgeRatingBoard:
    def test_partial_update(self):
        board = AgeRatingBoardFactory()
        updated = update_age_rating_board(
            instance=board, data={"region": "Asia"}
        )
        assert updated.region == "Asia"


# ═══════════════════════════════════════════════════════════════════════
# ContentDescriptor
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestCreateContentDescriptor:
    def test_basic_creation(self):
        desc = create_content_descriptor(name="Violence")
        assert desc.pk is not None
        assert desc.name == "Violence"

    def test_duplicate_name_raises_validation_error(self):
        create_content_descriptor(name="Nudity")
        with pytest.raises(ValidationError):
            create_content_descriptor(name="Nudity")


@pytest.mark.django_db
class TestUpdateContentDescriptor:
    def test_partial_update(self):
        desc = ContentDescriptorFactory()
        updated = update_content_descriptor(
            instance=desc, data={"name": "Drug Use"}
        )
        assert updated.name == "Drug Use"


# ═══════════════════════════════════════════════════════════════════════
# AgeRating (FK + M2M)
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestCreateAgeRating:
    def test_without_descriptors(self):
        board = AgeRatingBoardFactory()
        rating = create_age_rating(board_id=board.pk, value="T")
        assert rating.pk is not None
        assert rating.board == board
        assert rating.value == "T"
        assert rating.descriptors.count() == 0

    def test_with_descriptors(self):
        board = AgeRatingBoardFactory()
        d1 = ContentDescriptorFactory(name="Violence A")
        d2 = ContentDescriptorFactory(name="Gambling A")
        rating = create_age_rating(
            board_id=board.pk, value="M", descriptor_ids=[d1.pk, d2.pk]
        )
        assert rating.descriptors.count() == 2
        assert set(rating.descriptors.values_list("pk", flat=True)) == {
            d1.pk,
            d2.pk,
        }

    def test_invalid_board_id_raises_404(self):
        with pytest.raises(Http404):
            create_age_rating(board_id=uuid.uuid4(), value="E")


@pytest.mark.django_db
class TestUpdateAgeRating:
    def test_update_value(self):
        rating = AgeRatingFactory(value="E")
        updated = update_age_rating(instance=rating, data={"value": "M"})
        assert updated.value == "M"

    def test_update_board_id(self):
        rating = AgeRatingFactory()
        new_board = AgeRatingBoardFactory(name="New Board")
        updated = update_age_rating(
            instance=rating, data={"board_id": new_board.pk}
        )
        assert updated.board == new_board

    def test_update_descriptors(self):
        rating = AgeRatingFactory()
        d1 = ContentDescriptorFactory(name="Desc X")
        d2 = ContentDescriptorFactory(name="Desc Y")
        updated = update_age_rating(
            instance=rating, data={"descriptor_ids": [d1.pk, d2.pk]}
        )
        assert updated.descriptors.count() == 2

    def test_clear_descriptors_with_empty_list(self):
        d1 = ContentDescriptorFactory(name="Desc Clear")
        rating = AgeRatingFactory(descriptors=[d1])
        assert rating.descriptors.count() == 1
        updated = update_age_rating(
            instance=rating, data={"descriptor_ids": []}
        )
        assert updated.descriptors.count() == 0

    def test_invalid_board_id_raises_404(self):
        rating = AgeRatingFactory()
        with pytest.raises(Http404):
            update_age_rating(
                instance=rating, data={"board_id": uuid.uuid4()}
            )


# ═══════════════════════════════════════════════════════════════════════
# Game (the most critical)
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestCreateGame:
    def test_base_game_creation_minimal(self):
        game = create_game(
            title="Half-Life 3",
            slug="half-life-3",
            short_description="A great game",
            description="The long-awaited sequel.",
        )
        assert game.pk is not None
        assert game.title == "Half-Life 3"
        assert game.game_type == Game.GameType.BASE_GAME
        assert game.base_game is None
        assert game.is_active is True
        assert game.release_status == Game.ReleaseStatus.ANNOUNCED

    def test_base_game_with_m2m_ids(self):
        dev = DeveloperFactory()
        pub = PublisherFactory()
        genre = GenreFactory()
        platform = PlatformFactory(name="windows")
        tag = TagFactory()
        feature = FeatureFactory()

        game = create_game(
            title="Full Game",
            slug="full-game",
            short_description="Short",
            description="Long",
            developer_ids=[dev.pk],
            publisher_ids=[pub.pk],
            genre_ids=[genre.pk],
            tag_ids=[tag.pk],
            feature_ids=[feature.pk],
            platform_ids=[platform.pk],
        )
        assert game.developers.count() == 1
        assert game.publishers.count() == 1
        assert game.genres.count() == 1
        assert game.tags.count() == 1
        assert game.features.count() == 1
        assert game.platforms.count() == 1

    def test_base_game_with_franchise(self):
        franchise = FranchiseFactory()
        game = create_game(
            title="Franchise Game",
            slug="franchise-game",
            short_description="Short",
            description="Long",
            franchise_id=franchise.pk,
        )
        assert game.franchise == franchise

    def test_base_game_with_age_rating(self):
        rating = AgeRatingFactory()
        game = create_game(
            title="Rated Game",
            slug="rated-game",
            short_description="Short",
            description="Long",
            age_rating_id=rating.pk,
        )
        assert game.age_rating == rating

    def test_dlc_requires_base_game_id(self):
        with pytest.raises(ValidationError, match="must reference a base_game"):
            create_game(
                title="Orphan DLC",
                slug="orphan-dlc",
                game_type=Game.GameType.DLC,
                short_description="Short",
                description="Long",
            )

    def test_expansion_requires_base_game_id(self):
        with pytest.raises(ValidationError, match="must reference a base_game"):
            create_game(
                title="Orphan Expansion",
                slug="orphan-expansion",
                game_type=Game.GameType.EXPANSION,
                short_description="Short",
                description="Long",
            )

    def test_soundtrack_requires_base_game_id(self):
        with pytest.raises(ValidationError, match="must reference a base_game"):
            create_game(
                title="Orphan Soundtrack",
                slug="orphan-soundtrack",
                game_type=Game.GameType.SOUNDTRACK,
                short_description="Short",
                description="Long",
            )

    def test_demo_requires_base_game_id(self):
        with pytest.raises(ValidationError, match="must reference a base_game"):
            create_game(
                title="Orphan Demo",
                slug="orphan-demo",
                game_type=Game.GameType.DEMO,
                short_description="Short",
                description="Long",
            )

    def test_base_game_cannot_have_base_game_id(self):
        parent = GameFactory()
        with pytest.raises(
            ValidationError, match="base game cannot have a base_game"
        ):
            create_game(
                title="Bad Base",
                slug="bad-base",
                game_type=Game.GameType.BASE_GAME,
                base_game_id=parent.pk,
                short_description="Short",
                description="Long",
            )

    def test_dlc_with_valid_base_game(self):
        parent = GameFactory()
        dlc = create_game(
            title="DLC Pack",
            slug="dlc-pack",
            game_type=Game.GameType.DLC,
            base_game_id=parent.pk,
            short_description="Short",
            description="Long",
        )
        assert dlc.base_game == parent
        assert dlc.game_type == Game.GameType.DLC

    def test_invalid_franchise_id_raises_404(self):
        with pytest.raises(Http404):
            create_game(
                title="Bad FK",
                slug="bad-fk-franchise",
                short_description="Short",
                description="Long",
                franchise_id=uuid.uuid4(),
            )

    def test_invalid_age_rating_id_raises_404(self):
        with pytest.raises(Http404):
            create_game(
                title="Bad FK",
                slug="bad-fk-rating",
                short_description="Short",
                description="Long",
                age_rating_id=uuid.uuid4(),
            )

    def test_invalid_base_game_id_raises_404(self):
        with pytest.raises(Http404):
            create_game(
                title="Bad FK",
                slug="bad-fk-base",
                game_type=Game.GameType.DLC,
                base_game_id=uuid.uuid4(),
                short_description="Short",
                description="Long",
            )

    def test_duplicate_slug_raises_validation_error(self):
        create_game(
            title="First",
            slug="dup-game",
            short_description="Short",
            description="Long",
        )
        with pytest.raises(ValidationError):
            create_game(
                title="Second",
                slug="dup-game",
                short_description="Short",
                description="Long",
            )


@pytest.mark.django_db
class TestUpdateGame:
    def test_update_scalar_fields(self):
        game = GameFactory()
        updated = update_game(
            instance=game,
            data={"title": "Updated Title", "release_status": Game.ReleaseStatus.RELEASED},
        )
        assert updated.title == "Updated Title"
        assert updated.release_status == Game.ReleaseStatus.RELEASED

    def test_update_m2m_developers(self):
        game = GameFactory()
        dev1 = DeveloperFactory()
        dev2 = DeveloperFactory()
        updated = update_game(
            instance=game, data={"developer_ids": [dev1.pk, dev2.pk]}
        )
        assert updated.developers.count() == 2

    def test_update_m2m_genres_replaces_existing(self):
        genre1 = GenreFactory()
        genre2 = GenreFactory()
        game = GameFactory(genres=[genre1])
        assert game.genres.count() == 1
        updated = update_game(
            instance=game, data={"genre_ids": [genre2.pk]}
        )
        assert updated.genres.count() == 1
        assert updated.genres.first() == genre2

    def test_update_franchise_fk(self):
        game = GameFactory()
        franchise = FranchiseFactory()
        updated = update_game(
            instance=game, data={"franchise_id": franchise.pk}
        )
        assert updated.franchise == franchise

    def test_clear_franchise_fk(self):
        franchise = FranchiseFactory()
        game = GameFactory(franchise=franchise)
        updated = update_game(instance=game, data={"franchise_id": None})
        assert updated.franchise is None

    def test_update_age_rating_fk(self):
        game = GameFactory()
        rating = AgeRatingFactory()
        updated = update_game(
            instance=game, data={"age_rating_id": rating.pk}
        )
        assert updated.age_rating == rating

    def test_business_rule_dlc_without_base_game_raises(self):
        game = GameFactory(game_type=Game.GameType.BASE_GAME)
        with pytest.raises(ValidationError, match="must reference a base_game"):
            update_game(
                instance=game,
                data={"game_type": Game.GameType.DLC},
            )

    def test_business_rule_base_game_with_base_game_raises(self):
        parent = GameFactory()
        game = GameFactory()
        with pytest.raises(
            ValidationError, match="base game cannot have a base_game"
        ):
            update_game(
                instance=game,
                data={"base_game_id": parent.pk, "game_type": Game.GameType.BASE_GAME},
            )

    def test_update_to_dlc_with_base_game_succeeds(self):
        parent = GameFactory()
        game = GameFactory()
        updated = update_game(
            instance=game,
            data={
                "game_type": Game.GameType.DLC,
                "base_game_id": parent.pk,
            },
        )
        assert updated.game_type == Game.GameType.DLC
        assert updated.base_game == parent

    def test_invalid_franchise_id_raises_404(self):
        game = GameFactory()
        with pytest.raises(Http404):
            update_game(
                instance=game, data={"franchise_id": uuid.uuid4()}
            )


@pytest.mark.django_db
class TestSoftDeleteGame:
    def test_sets_is_active_false(self):
        game = GameFactory(is_active=True)
        result = soft_delete_game(instance=game)
        assert result.is_active is False
        game.refresh_from_db()
        assert game.is_active is False

    def test_does_not_delete_from_db(self):
        game = GameFactory(is_active=True)
        soft_delete_game(instance=game)
        assert Game.objects.filter(pk=game.pk).exists()

    def test_already_inactive_stays_inactive(self):
        game = GameFactory(is_active=False)
        result = soft_delete_game(instance=game)
        assert result.is_active is False


# ═══════════════════════════════════════════════════════════════════════
# GameLanguageSupport
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestCreateGameLanguageSupport:
    def test_basic_creation(self):
        game = GameFactory()
        lang = LanguageFactory()
        support = create_game_language_support(
            game_id=game.pk,
            language_id=lang.pk,
            interface=True,
            audio=True,
            subtitles=False,
        )
        assert support.pk is not None
        assert support.game == game
        assert support.language == lang
        assert support.interface is True
        assert support.audio is True
        assert support.subtitles is False

    def test_defaults_are_false(self):
        game = GameFactory()
        lang = LanguageFactory()
        support = create_game_language_support(
            game_id=game.pk, language_id=lang.pk
        )
        assert support.interface is False
        assert support.audio is False
        assert support.subtitles is False

    def test_invalid_game_id_raises_404(self):
        lang = LanguageFactory()
        with pytest.raises(Http404):
            create_game_language_support(
                game_id=uuid.uuid4(), language_id=lang.pk
            )

    def test_invalid_language_id_raises_404(self):
        game = GameFactory()
        with pytest.raises(Http404):
            create_game_language_support(
                game_id=game.pk, language_id=uuid.uuid4()
            )


# ═══════════════════════════════════════════════════════════════════════
# SystemRequirement
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestCreateSystemRequirement:
    def test_basic_creation(self):
        game = GameFactory()
        platform = PlatformFactory(name="windows")
        req = create_system_requirement(
            game_id=game.pk,
            platform_id=platform.pk,
            tier=SystemRequirement.Tier.MINIMUM,
            os_version="Windows 10",
            cpu="Intel i5",
            gpu="GTX 1060",
            ram_gb=8,
            storage_gb=50,
        )
        assert req.pk is not None
        assert req.game == game
        assert req.platform == platform
        assert req.tier == SystemRequirement.Tier.MINIMUM
        assert req.ram_gb == 8
        assert req.storage_gb == 50

    def test_minimal_params(self):
        game = GameFactory()
        platform = PlatformFactory(name="linux")
        req = create_system_requirement(
            game_id=game.pk,
            platform_id=platform.pk,
            tier=SystemRequirement.Tier.RECOMMENDED,
        )
        assert req.os_version == ""
        assert req.cpu == ""
        assert req.ram_gb is None

    def test_invalid_game_id_raises_404(self):
        platform = PlatformFactory()
        with pytest.raises(Http404):
            create_system_requirement(
                game_id=uuid.uuid4(),
                platform_id=platform.pk,
                tier=SystemRequirement.Tier.MINIMUM,
            )

    def test_invalid_platform_id_raises_404(self):
        game = GameFactory()
        with pytest.raises(Http404):
            create_system_requirement(
                game_id=game.pk,
                platform_id=uuid.uuid4(),
                tier=SystemRequirement.Tier.MINIMUM,
            )


# ═══════════════════════════════════════════════════════════════════════
# GameMedia
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestCreateGameMedia:
    def test_basic_creation(self):
        game = GameFactory()
        media = create_game_media(
            game_id=game.pk,
            media_type=GameMedia.MediaType.SCREENSHOT,
            url="https://cdn.example.com/shot1.jpg",
        )
        assert media.pk is not None
        assert media.game == game
        assert media.media_type == GameMedia.MediaType.SCREENSHOT
        assert media.url == "https://cdn.example.com/shot1.jpg"
        assert media.thumbnail_url == ""
        assert media.order == 0

    def test_with_thumbnail_and_order(self):
        game = GameFactory()
        media = create_game_media(
            game_id=game.pk,
            media_type=GameMedia.MediaType.TRAILER,
            url="https://cdn.example.com/trailer.mp4",
            thumbnail_url="https://cdn.example.com/trailer_thumb.jpg",
            order=5,
        )
        assert media.thumbnail_url == "https://cdn.example.com/trailer_thumb.jpg"
        assert media.order == 5

    def test_invalid_game_id_raises_404(self):
        with pytest.raises(Http404):
            create_game_media(
                game_id=uuid.uuid4(),
                media_type=GameMedia.MediaType.SCREENSHOT,
                url="https://cdn.example.com/shot.jpg",
            )

    def test_invalid_media_type_raises_validation_error(self):
        game = GameFactory()
        with pytest.raises(ValidationError):
            create_game_media(
                game_id=game.pk,
                media_type="invalid_type",
                url="https://cdn.example.com/shot.jpg",
            )


# ═══════════════════════════════════════════════════════════════════════
# Bundle
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestCreateBundle:
    def test_without_games(self):
        bundle = create_bundle(name="Summer Sale", slug="summer-sale")
        assert bundle.pk is not None
        assert bundle.name == "Summer Sale"
        assert bundle.is_active is True
        assert bundle.bundleitem_set.count() == 0

    def test_with_game_ids(self):
        g1 = GameFactory()
        g2 = GameFactory()
        bundle = create_bundle(
            name="Bundle Pack",
            slug="bundle-pack",
            game_ids=[g1.pk, g2.pk],
        )
        assert bundle.bundleitem_set.count() == 2
        bundle_game_ids = set(
            bundle.bundleitem_set.values_list("game_id", flat=True)
        )
        assert bundle_game_ids == {g1.pk, g2.pk}

    def test_with_description(self):
        bundle = create_bundle(
            name="Deluxe",
            slug="deluxe",
            description="All DLCs included.",
        )
        assert bundle.description == "All DLCs included."

    def test_duplicate_slug_raises_validation_error(self):
        create_bundle(name="A", slug="dup-bundle")
        with pytest.raises(ValidationError):
            create_bundle(name="B", slug="dup-bundle")


@pytest.mark.django_db
class TestUpdateBundle:
    def test_update_name(self):
        from apps.games.tests.factories import BundleFactory

        bundle = BundleFactory()
        updated = update_bundle(instance=bundle, data={"name": "Renamed"})
        assert updated.name == "Renamed"

    def test_game_ids_replacement(self):
        from apps.games.tests.factories import BundleFactory, BundleItemFactory

        g1 = GameFactory()
        g2 = GameFactory()
        g3 = GameFactory()
        bundle = BundleFactory()
        BundleItemFactory(bundle=bundle, game=g1)
        BundleItemFactory(bundle=bundle, game=g2)
        assert bundle.bundleitem_set.count() == 2

        updated = update_bundle(
            instance=bundle, data={"game_ids": [g3.pk]}
        )
        assert updated.bundleitem_set.count() == 1
        assert updated.bundleitem_set.first().game == g3

    def test_game_ids_empty_clears_all(self):
        from apps.games.tests.factories import BundleFactory, BundleItemFactory

        g1 = GameFactory()
        bundle = BundleFactory()
        BundleItemFactory(bundle=bundle, game=g1)
        assert bundle.bundleitem_set.count() == 1

        updated = update_bundle(instance=bundle, data={"game_ids": []})
        assert updated.bundleitem_set.count() == 0

    def test_omitting_game_ids_does_not_touch_items(self):
        from apps.games.tests.factories import BundleFactory, BundleItemFactory

        g1 = GameFactory()
        bundle = BundleFactory()
        BundleItemFactory(bundle=bundle, game=g1)

        updated = update_bundle(instance=bundle, data={"name": "NewName"})
        assert updated.bundleitem_set.count() == 1


# ═══════════════════════════════════════════════════════════════════════
# Membership services
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestCreateDeveloperMembership:
    def test_basic_creation(self):
        user = make_developer_user()
        dev = DeveloperFactory()
        membership = create_developer_membership(
            user_id=user.pk,
            developer_id=dev.pk,
            role=DeveloperMembership.MemberRole.MEMBER,
        )
        assert membership.pk is not None
        assert membership.user == user
        assert membership.developer == dev
        assert membership.role == DeveloperMembership.MemberRole.MEMBER

    def test_owner_role(self):
        user = make_developer_user()
        dev = DeveloperFactory()
        membership = create_developer_membership(
            user_id=user.pk,
            developer_id=dev.pk,
            role=DeveloperMembership.MemberRole.OWNER,
        )
        assert membership.role == DeveloperMembership.MemberRole.OWNER

    def test_default_role_is_member(self):
        user = make_developer_user()
        dev = DeveloperFactory()
        membership = create_developer_membership(
            user_id=user.pk, developer_id=dev.pk
        )
        assert membership.role == DeveloperMembership.MemberRole.MEMBER

    def test_duplicate_membership_raises_validation_error(self):
        user = make_developer_user()
        dev = DeveloperFactory()
        create_developer_membership(user_id=user.pk, developer_id=dev.pk)
        with pytest.raises(ValidationError):
            create_developer_membership(user_id=user.pk, developer_id=dev.pk)


@pytest.mark.django_db
class TestCreatePublisherMembership:
    def test_basic_creation(self):
        user = make_developer_user()
        pub = PublisherFactory()
        membership = create_publisher_membership(
            user_id=user.pk,
            publisher_id=pub.pk,
            role=PublisherMembership.MemberRole.MEMBER,
        )
        assert membership.pk is not None
        assert membership.user == user
        assert membership.publisher == pub
        assert membership.role == PublisherMembership.MemberRole.MEMBER

    def test_owner_role(self):
        user = make_developer_user()
        pub = PublisherFactory()
        membership = create_publisher_membership(
            user_id=user.pk,
            publisher_id=pub.pk,
            role=PublisherMembership.MemberRole.OWNER,
        )
        assert membership.role == PublisherMembership.MemberRole.OWNER

    def test_default_role_is_member(self):
        user = make_developer_user()
        pub = PublisherFactory()
        membership = create_publisher_membership(
            user_id=user.pk, publisher_id=pub.pk
        )
        assert membership.role == PublisherMembership.MemberRole.MEMBER

    def test_duplicate_membership_raises_validation_error(self):
        user = make_developer_user()
        pub = PublisherFactory()
        create_publisher_membership(user_id=user.pk, publisher_id=pub.pk)
        with pytest.raises(ValidationError):
            create_publisher_membership(user_id=user.pk, publisher_id=pub.pk)
