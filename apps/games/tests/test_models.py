"""
Comprehensive model tests for apps.games and related apps.accounts models.

Uses pytest-django + factory-boy. All DB-touching tests are decorated with
``@pytest.mark.django_db``.
"""

import pytest
from decimal import Decimal

from django.db import IntegrityError, transaction

from apps.accounts.models import Role
from apps.games.models import (
    Bundle,
    BundleItem,
    Developer,
    DeveloperMembership,
    Game,
    GameLanguageSupport,
    GameMedia,
    Platform,
    Publisher,
    PublisherMembership,
    SystemRequirement,
    Tag,
)

from apps.games.tests.factories import (
    AgeRatingBoardFactory,
    AgeRatingFactory,
    BundleFactory,
    BundleItemFactory,
    ContentDescriptorFactory,
    DeveloperFactory,
    DeveloperMembershipFactory,
    FeatureFactory,
    FranchiseFactory,
    GameFactory,
    GameLanguageSupportFactory,
    GameMediaFactory,
    GenreFactory,
    LanguageFactory,
    PlatformFactory,
    PublisherFactory,
    PublisherMembershipFactory,
    RoleFactory,
    SystemRequirementFactory,
    TagFactory,
    UserFactory,
    make_admin_user,
    make_developer_user,
    make_end_user,
)


# ═══════════════════════════════════════════════════════════════════════
# Role model (apps.accounts)
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestRoleModel:
    def test_str_returns_display_name(self):
        role = RoleFactory(name=Role.RoleType.ADMIN)
        assert str(role) == "Admin"

    def test_str_end_user_display(self):
        role = RoleFactory(name=Role.RoleType.END_USER)
        assert str(role) == "End User"

    def test_name_is_unique(self):
        RoleFactory(name=Role.RoleType.DEVELOPER)
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Role.objects.create(name=Role.RoleType.DEVELOPER)

    def test_role_type_choices(self):
        values = {choice.value for choice in Role.RoleType}
        assert values == {"admin", "owner", "developer", "end_user"}

    def test_uuid_primary_key(self):
        role = RoleFactory(name=Role.RoleType.OWNER)
        assert role.pk is not None
        assert isinstance(str(role.pk), str)
        assert len(str(role.pk)) == 36  # UUID format


# ═══════════════════════════════════════════════════════════════════════
# Developer
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestDeveloperModel:
    def test_str_returns_name(self):
        dev = DeveloperFactory(name="Naughty Dog")
        assert str(dev) == "Naughty Dog"

    def test_slug_is_unique(self):
        DeveloperFactory(slug="naughty-dog")
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                DeveloperFactory(slug="naughty-dog")

    def test_verified_defaults_to_false_in_model(self):
        """The factory sets verified=True, but the model default is False."""
        dev = Developer.objects.create(name="Test", slug="test-dev-default")
        assert dev.verified is False

    def test_blank_website_allowed(self):
        dev = DeveloperFactory(website="")
        assert dev.website == ""

    def test_blank_country_allowed(self):
        dev = DeveloperFactory(country="")
        assert dev.country == ""


# ═══════════════════════════════════════════════════════════════════════
# Publisher
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestPublisherModel:
    def test_str_returns_name(self):
        pub = PublisherFactory(name="Electronic Arts")
        assert str(pub) == "Electronic Arts"

    def test_slug_is_unique(self):
        PublisherFactory(slug="ea")
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                PublisherFactory(slug="ea")

    def test_revenue_share_percent_default(self):
        pub = Publisher.objects.create(name="Default Pub", slug="default-pub")
        assert pub.revenue_share_percent == Decimal("70.00")

    def test_revenue_share_percent_custom(self):
        pub = PublisherFactory(revenue_share_percent=Decimal("80.50"))
        assert pub.revenue_share_percent == Decimal("80.50")


# ═══════════════════════════════════════════════════════════════════════
# DeveloperMembership
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestDeveloperMembershipModel:
    def test_str_format(self):
        user = UserFactory(username="alice")
        dev = DeveloperFactory(name="Studio X")
        membership = DeveloperMembershipFactory(
            user=user, developer=dev, role=DeveloperMembership.MemberRole.OWNER
        )
        assert str(membership) == "alice → Studio X (owner)"

    def test_default_role_is_member(self):
        membership = DeveloperMembershipFactory()
        assert membership.role == DeveloperMembership.MemberRole.MEMBER

    def test_unique_together_user_developer(self):
        membership = DeveloperMembershipFactory()
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                DeveloperMembershipFactory(
                    user=membership.user, developer=membership.developer
                )

    def test_member_role_choices(self):
        values = {c.value for c in DeveloperMembership.MemberRole}
        assert values == {"owner", "member"}


# ═══════════════════════════════════════════════════════════════════════
# PublisherMembership
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestPublisherMembershipModel:
    def test_str_format(self):
        user = UserFactory(username="bob")
        pub = PublisherFactory(name="Big Pub")
        membership = PublisherMembershipFactory(
            user=user, publisher=pub, role=PublisherMembership.MemberRole.OWNER
        )
        assert str(membership) == "bob → Big Pub (owner)"

    def test_default_role_is_member(self):
        membership = PublisherMembershipFactory()
        assert membership.role == PublisherMembership.MemberRole.MEMBER

    def test_unique_together_user_publisher(self):
        membership = PublisherMembershipFactory()
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                PublisherMembershipFactory(
                    user=membership.user, publisher=membership.publisher
                )

    def test_member_role_choices(self):
        values = {c.value for c in PublisherMembership.MemberRole}
        assert values == {"owner", "member"}


# ═══════════════════════════════════════════════════════════════════════
# Franchise
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestFranchiseModel:
    def test_creation(self):
        franchise = FranchiseFactory(name="The Elder Scrolls")
        assert franchise.name == "The Elder Scrolls"

    def test_slug_is_unique(self):
        FranchiseFactory(slug="elder-scrolls")
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                FranchiseFactory(slug="elder-scrolls")

    def test_uuid_pk(self):
        franchise = FranchiseFactory()
        assert franchise.pk is not None


# ═══════════════════════════════════════════════════════════════════════
# Genre
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestGenreModel:
    def test_creation(self):
        genre = GenreFactory(name="RPG")
        assert genre.name == "RPG"

    def test_name_is_unique(self):
        GenreFactory(name="Action")
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                GenreFactory(name="Action")

    def test_slug_is_unique(self):
        GenreFactory(slug="action")
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                GenreFactory(slug="action")


# ═══════════════════════════════════════════════════════════════════════
# Tag
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestTagModel:
    def test_creation(self):
        tag = TagFactory(name="Open World")
        assert tag.name == "Open World"

    def test_is_approved_defaults_true(self):
        tag = Tag.objects.create(name="New Tag", slug="new-tag")
        assert tag.is_approved is True

    def test_name_is_unique(self):
        TagFactory(name="Roguelike")
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                TagFactory(name="Roguelike")

    def test_slug_is_unique(self):
        TagFactory(slug="roguelike")
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                TagFactory(slug="roguelike")


# ═══════════════════════════════════════════════════════════════════════
# Feature
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestFeatureModel:
    def test_creation(self):
        feat = FeatureFactory(name="Cloud Saves", icon_key="cloud-save")
        assert feat.name == "Cloud Saves"
        assert feat.icon_key == "cloud-save"

    def test_name_is_unique(self):
        FeatureFactory(name="Co-op")
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                FeatureFactory(name="Co-op")

    def test_icon_key_can_be_blank(self):
        feat = FeatureFactory(icon_key="")
        assert feat.icon_key == ""


# ═══════════════════════════════════════════════════════════════════════
# Platform
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestPlatformModel:
    def test_creation(self):
        platform = PlatformFactory(name=Platform.OS.LINUX)
        assert platform.name == "linux"

    def test_os_choices(self):
        values = {c.value for c in Platform.OS}
        assert values == {"windows", "mac", "linux"}

    def test_name_is_unique(self):
        PlatformFactory(name=Platform.OS.WINDOWS)
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Platform.objects.create(name=Platform.OS.WINDOWS)


# ═══════════════════════════════════════════════════════════════════════
# Language
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestLanguageModel:
    def test_creation(self):
        lang = LanguageFactory(code="en", name="English")
        assert lang.code == "en"
        assert lang.name == "English"

    def test_code_is_unique(self):
        LanguageFactory(code="fr")
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                LanguageFactory(code="fr")


# ═══════════════════════════════════════════════════════════════════════
# AgeRatingBoard
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestAgeRatingBoardModel:
    def test_creation(self):
        board = AgeRatingBoardFactory(name="ESRB", region="North America")
        assert board.name == "ESRB"
        assert board.region == "North America"

    def test_name_is_unique(self):
        AgeRatingBoardFactory(name="PEGI")
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                AgeRatingBoardFactory(name="PEGI")


# ═══════════════════════════════════════════════════════════════════════
# ContentDescriptor
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestContentDescriptorModel:
    def test_creation(self):
        desc = ContentDescriptorFactory(name="Violence")
        assert desc.name == "Violence"

    def test_name_is_unique(self):
        ContentDescriptorFactory(name="Nudity")
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                ContentDescriptorFactory(name="Nudity")


# ═══════════════════════════════════════════════════════════════════════
# AgeRating
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestAgeRatingModel:
    def test_creation(self):
        rating = AgeRatingFactory(value="T")
        assert rating.value == "T"

    def test_board_fk_protect(self):
        """Deleting a board with ratings must raise ProtectedError."""
        rating = AgeRatingFactory()
        board = rating.board
        with pytest.raises(models.ProtectedError):
            board.delete()

    def test_m2m_descriptors(self):
        d1 = ContentDescriptorFactory(name="Blood")
        d2 = ContentDescriptorFactory(name="Language")
        rating = AgeRatingFactory(descriptors=[d1, d2])
        assert set(rating.descriptors.all()) == {d1, d2}

    def test_descriptors_can_be_blank(self):
        rating = AgeRatingFactory()
        assert rating.descriptors.count() == 0


# Need the models import for ProtectedError
from django.db import models


# ═══════════════════════════════════════════════════════════════════════
# Game (most thorough)
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestGameModel:
    def test_str_returns_title(self):
        game = GameFactory(title="Elden Ring")
        assert str(game) == "Elden Ring"

    def test_slug_is_unique(self):
        GameFactory(slug="elden-ring")
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                GameFactory(slug="elden-ring")

    def test_is_active_default_true(self):
        game = Game.objects.create(
            title="Test Game",
            slug="test-game-active-default",
            short_description="Short",
            description="Long",
        )
        assert game.is_active is True

    def test_game_type_default_base_game(self):
        game = Game.objects.create(
            title="Default Type",
            slug="default-type",
            short_description="Short",
            description="Long",
        )
        assert game.game_type == Game.GameType.BASE_GAME

    def test_release_status_default_announced(self):
        game = Game.objects.create(
            title="Default Status",
            slug="default-status",
            short_description="Short",
            description="Long",
        )
        assert game.release_status == Game.ReleaseStatus.ANNOUNCED

    def test_game_type_choices(self):
        values = {c.value for c in Game.GameType}
        assert values == {"base_game", "dlc", "expansion", "soundtrack", "demo"}

    def test_release_status_choices(self):
        values = {c.value for c in Game.ReleaseStatus}
        assert values == {
            "announced",
            "coming_soon",
            "early_access",
            "released",
            "delisted",
        }

    def test_self_referencing_fk_base_game(self):
        base = GameFactory(title="Base Game")
        dlc = GameFactory(
            title="DLC Pack 1",
            game_type=Game.GameType.DLC,
            base_game=base,
        )
        assert dlc.base_game == base
        assert base.related_content.first() == dlc

    def test_base_game_null_for_standalone(self):
        game = GameFactory()
        assert game.base_game is None

    def test_m2m_developers(self):
        d1 = DeveloperFactory()
        d2 = DeveloperFactory()
        game = GameFactory(developers=[d1, d2])
        assert set(game.developers.all()) == {d1, d2}

    def test_m2m_publishers(self):
        p1 = PublisherFactory()
        game = GameFactory(publishers=[p1])
        assert game.publishers.count() == 1

    def test_m2m_genres(self):
        g1 = GenreFactory(name="Action")
        g2 = GenreFactory(name="RPG")
        game = GameFactory(genres=[g1, g2])
        assert set(game.genres.all()) == {g1, g2}

    def test_m2m_tags(self):
        t1 = TagFactory()
        game = GameFactory(tags=[t1])
        assert game.tags.count() == 1

    def test_m2m_features(self):
        f1 = FeatureFactory(name="Multiplayer")
        game = GameFactory(features=[f1])
        assert f1 in game.features.all()

    def test_m2m_platforms(self):
        p1 = PlatformFactory(name=Platform.OS.WINDOWS)
        p2 = PlatformFactory(name=Platform.OS.LINUX)
        game = GameFactory(platforms=[p1, p2])
        assert game.platforms.count() == 2

    def test_franchise_fk_set_null(self):
        franchise = FranchiseFactory()
        game = GameFactory(franchise=franchise)
        franchise.delete()
        game.refresh_from_db()
        assert game.franchise is None

    def test_age_rating_fk_set_null(self):
        rating = AgeRatingFactory()
        game = GameFactory(age_rating=rating)
        rating.delete()
        game.refresh_from_db()
        assert game.age_rating is None

    def test_release_date_can_be_null(self):
        game = GameFactory(release_date=None)
        assert game.release_date is None

    def test_uuid_primary_key(self):
        game = GameFactory()
        assert game.pk is not None
        assert len(str(game.pk)) == 36


# ═══════════════════════════════════════════════════════════════════════
# GameLanguageSupport
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestGameLanguageSupportModel:
    def test_creation(self):
        gls = GameLanguageSupportFactory(interface=True, audio=True, subtitles=False)
        assert gls.interface is True
        assert gls.audio is True
        assert gls.subtitles is False

    def test_unique_together_game_language(self):
        gls = GameLanguageSupportFactory()
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                GameLanguageSupportFactory(game=gls.game, language=gls.language)

    def test_cascade_on_game_delete(self):
        gls = GameLanguageSupportFactory()
        game_pk = gls.game.pk
        gls.game.delete()
        assert not GameLanguageSupport.objects.filter(game_id=game_pk).exists()

    def test_cascade_on_language_delete(self):
        gls = GameLanguageSupportFactory()
        lang_pk = gls.language.pk
        gls.language.delete()
        assert not GameLanguageSupport.objects.filter(language_id=lang_pk).exists()


# ═══════════════════════════════════════════════════════════════════════
# SystemRequirement
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestSystemRequirementModel:
    def test_creation(self):
        sr = SystemRequirementFactory(ram_gb=16, storage_gb=100)
        assert sr.ram_gb == 16
        assert sr.storage_gb == 100

    def test_tier_choices(self):
        values = {c.value for c in SystemRequirement.Tier}
        assert values == {"minimum", "recommended"}

    def test_unique_together_game_platform_tier(self):
        sr = SystemRequirementFactory()
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                SystemRequirementFactory(
                    game=sr.game, platform=sr.platform, tier=sr.tier
                )

    def test_two_tiers_same_game_platform(self):
        """A game can have both minimum and recommended for the same platform."""
        game = GameFactory()
        platform = PlatformFactory(name=Platform.OS.WINDOWS)
        sr1 = SystemRequirementFactory(
            game=game, platform=platform, tier=SystemRequirement.Tier.MINIMUM
        )
        sr2 = SystemRequirementFactory(
            game=game, platform=platform, tier=SystemRequirement.Tier.RECOMMENDED
        )
        assert sr1.pk != sr2.pk

    def test_cascade_on_game_delete(self):
        sr = SystemRequirementFactory()
        game_pk = sr.game.pk
        sr.game.delete()
        assert not SystemRequirement.objects.filter(game_id=game_pk).exists()


# ═══════════════════════════════════════════════════════════════════════
# GameMedia
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestGameMediaModel:
    def test_creation(self):
        media = GameMediaFactory(media_type=GameMedia.MediaType.TRAILER)
        assert media.media_type == "trailer"

    def test_media_type_choices(self):
        values = {c.value for c in GameMedia.MediaType}
        assert values == {"screenshot", "trailer", "artwork", "header"}

    def test_ordering_by_order_field(self):
        game = GameFactory()
        m3 = GameMediaFactory(game=game, order=3)
        m1 = GameMediaFactory(game=game, order=1)
        m2 = GameMediaFactory(game=game, order=2)
        ordered = list(GameMedia.objects.filter(game=game))
        assert ordered == [m1, m2, m3]

    def test_cascade_on_game_delete(self):
        media = GameMediaFactory()
        game_pk = media.game.pk
        media.game.delete()
        assert not GameMedia.objects.filter(game_id=game_pk).exists()

    def test_thumbnail_url_can_be_blank(self):
        media = GameMediaFactory(thumbnail_url="")
        assert media.thumbnail_url == ""


# ═══════════════════════════════════════════════════════════════════════
# Bundle
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestBundleModel:
    def test_creation(self):
        bundle = BundleFactory(name="GOTY Edition")
        assert bundle.name == "GOTY Edition"

    def test_slug_is_unique(self):
        BundleFactory(slug="goty")
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                BundleFactory(slug="goty")

    def test_is_active_default_true(self):
        bundle = Bundle.objects.create(name="Test", slug="test-bundle-default")
        assert bundle.is_active is True

    def test_m2m_games_through_bundle_item(self):
        bundle = BundleFactory()
        game1 = GameFactory()
        game2 = GameFactory()
        BundleItemFactory(bundle=bundle, game=game1)
        BundleItemFactory(bundle=bundle, game=game2)
        assert set(bundle.games.all()) == {game1, game2}


# ═══════════════════════════════════════════════════════════════════════
# BundleItem
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestBundleItemModel:
    def test_creation(self):
        item = BundleItemFactory()
        assert item.bundle is not None
        assert item.game is not None

    def test_unique_together_bundle_game(self):
        item = BundleItemFactory()
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                BundleItemFactory(bundle=item.bundle, game=item.game)

    def test_cascade_on_bundle_delete(self):
        item = BundleItemFactory()
        bundle_pk = item.bundle.pk
        item.bundle.delete()
        assert not BundleItem.objects.filter(bundle_id=bundle_pk).exists()

    def test_cascade_on_game_delete(self):
        item = BundleItemFactory()
        game_pk = item.game.pk
        item.game.delete()
        assert not BundleItem.objects.filter(game_id=game_pk).exists()


# ═══════════════════════════════════════════════════════════════════════
# User.has_game_access()
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestUserGameAccess:
    def test_admin_always_has_access(self):
        admin = make_admin_user()
        game = GameFactory()
        assert admin.has_game_access(game) is True

    def test_developer_member_has_access(self):
        dev = DeveloperFactory()
        user = make_developer_user()
        DeveloperMembershipFactory(user=user, developer=dev)
        game = GameFactory(developers=[dev])
        assert user.has_game_access(game) is True

    def test_publisher_member_has_access(self):
        pub = PublisherFactory()
        user = UserFactory()
        PublisherMembershipFactory(user=user, publisher=pub)
        game = GameFactory(publishers=[pub])
        assert user.has_game_access(game) is True

    def test_unrelated_user_has_no_access(self):
        user = make_end_user()
        game = GameFactory()
        assert user.has_game_access(game) is False

    def test_developer_member_no_access_to_other_game(self):
        """A user who is a member of Developer A cannot access games of Developer B."""
        dev_a = DeveloperFactory()
        dev_b = DeveloperFactory()
        user = UserFactory()
        DeveloperMembershipFactory(user=user, developer=dev_a)
        game_b = GameFactory(developers=[dev_b])
        assert user.has_game_access(game_b) is False

    def test_publisher_member_no_access_to_other_game(self):
        """A user who is a member of Publisher A cannot access games of Publisher B."""
        pub_a = PublisherFactory()
        pub_b = PublisherFactory()
        user = UserFactory()
        PublisherMembershipFactory(user=user, publisher=pub_a)
        game_b = GameFactory(publishers=[pub_b])
        assert user.has_game_access(game_b) is False

    def test_access_via_developer_even_without_developer_role(self):
        """has_game_access checks membership, not the global 'developer' role."""
        dev = DeveloperFactory()
        user = make_end_user()  # end_user role, but has a dev membership
        DeveloperMembershipFactory(user=user, developer=dev)
        game = GameFactory(developers=[dev])
        assert user.has_game_access(game) is True

    def test_access_via_both_developer_and_publisher(self):
        """User linked through both dev and pub still gets access."""
        dev = DeveloperFactory()
        pub = PublisherFactory()
        user = UserFactory()
        DeveloperMembershipFactory(user=user, developer=dev)
        PublisherMembershipFactory(user=user, publisher=pub)
        game = GameFactory(developers=[dev], publishers=[pub])
        assert user.has_game_access(game) is True
