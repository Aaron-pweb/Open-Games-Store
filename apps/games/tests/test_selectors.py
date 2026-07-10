"""
Tests for apps.games.selectors — read-only query functions.
"""

import pytest
from django.http import Http404

from apps.games.selectors import (
    get_age_rating_boards,
    get_age_rating_by_id,
    get_age_ratings,
    get_bundle_by_id,
    get_bundles,
    get_content_descriptors,
    get_developer_by_id,
    get_developers,
    get_feature_by_id,
    get_features,
    get_franchise_by_id,
    get_franchises,
    get_game_by_id,
    get_game_language_support,
    get_game_media,
    get_game_related_content,
    get_game_system_requirements,
    get_games,
    get_games_for_user,
    get_genre_by_id,
    get_genres,
    get_language_by_id,
    get_languages,
    get_platform_by_id,
    get_platforms,
    get_publisher_by_id,
    get_publishers,
    get_tag_by_id,
    get_tags,
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
    SystemRequirementFactory,
    TagFactory,
    UserFactory,
    make_developer_user,
)


@pytest.mark.django_db
class TestDeveloperSelectors:
    def test_get_developers_returns_all(self):
        DeveloperFactory.create_batch(3)
        result = get_developers()
        assert result.count() == 3

    def test_get_developers_ordered_by_name(self):
        DeveloperFactory(name="Zebra Studio")
        DeveloperFactory(name="Alpha Studio")
        result = list(get_developers().values_list("name", flat=True))
        assert result == ["Alpha Studio", "Zebra Studio"]

    def test_get_developers_filter_verified(self):
        DeveloperFactory(verified=True)
        DeveloperFactory(verified=False)
        assert get_developers(is_verified=True).count() == 1
        assert get_developers(is_verified=False).count() == 1
        assert get_developers().count() == 2

    def test_get_developer_by_id(self):
        dev = DeveloperFactory()
        result = get_developer_by_id(developer_id=dev.id)
        assert result.id == dev.id

    def test_get_developer_by_id_not_found(self):
        import uuid

        with pytest.raises(Http404):
            get_developer_by_id(developer_id=uuid.uuid4())


@pytest.mark.django_db
class TestPublisherSelectors:
    def test_get_publishers_returns_all(self):
        PublisherFactory.create_batch(2)
        assert get_publishers().count() == 2

    def test_get_publisher_by_id(self):
        pub = PublisherFactory()
        assert get_publisher_by_id(publisher_id=pub.id).id == pub.id


@pytest.mark.django_db
class TestFranchiseSelectors:
    def test_get_franchises_returns_all(self):
        FranchiseFactory.create_batch(2)
        assert get_franchises().count() == 2

    def test_get_franchise_by_id(self):
        f = FranchiseFactory()
        assert get_franchise_by_id(franchise_id=f.id).id == f.id


@pytest.mark.django_db
class TestGenreSelectors:
    def test_get_genres_returns_all(self):
        GenreFactory.create_batch(2)
        assert get_genres().count() == 2

    def test_get_genre_by_id(self):
        g = GenreFactory()
        assert get_genre_by_id(genre_id=g.id).id == g.id


@pytest.mark.django_db
class TestTagSelectors:
    def test_get_tags_returns_all(self):
        TagFactory(is_approved=True)
        TagFactory(is_approved=False)
        assert get_tags().count() == 2

    def test_get_tags_filter_approved(self):
        TagFactory(is_approved=True)
        TagFactory(is_approved=False)
        assert get_tags(is_approved=True).count() == 1
        assert get_tags(is_approved=False).count() == 1

    def test_get_tag_by_id(self):
        t = TagFactory()
        assert get_tag_by_id(tag_id=t.id).id == t.id


@pytest.mark.django_db
class TestFeatureSelectors:
    def test_get_features(self):
        FeatureFactory.create_batch(3)
        assert get_features().count() == 3

    def test_get_feature_by_id(self):
        f = FeatureFactory()
        assert get_feature_by_id(feature_id=f.id).id == f.id


@pytest.mark.django_db
class TestPlatformSelectors:
    def test_get_platforms(self):
        PlatformFactory(name="windows")
        PlatformFactory(name="linux")
        assert get_platforms().count() == 2

    def test_get_platform_by_id(self):
        p = PlatformFactory(name="mac")
        assert get_platform_by_id(platform_id=p.id).id == p.id


@pytest.mark.django_db
class TestLanguageSelectors:
    def test_get_languages(self):
        LanguageFactory.create_batch(2)
        assert get_languages().count() == 2

    def test_get_language_by_id(self):
        lang = LanguageFactory()
        assert get_language_by_id(language_id=lang.id).id == lang.id


@pytest.mark.django_db
class TestAgeRatingBoardSelectors:
    def test_get_age_rating_boards(self):
        AgeRatingBoardFactory.create_batch(2)
        assert get_age_rating_boards().count() == 2


@pytest.mark.django_db
class TestContentDescriptorSelectors:
    def test_get_content_descriptors(self):
        ContentDescriptorFactory.create_batch(2)
        assert get_content_descriptors().count() == 2


@pytest.mark.django_db
class TestAgeRatingSelectors:
    def test_get_age_ratings_prefetches(self):
        desc = ContentDescriptorFactory()
        rating = AgeRatingFactory(descriptors=[desc])
        result = get_age_ratings()
        assert result.count() == 1
        assert rating.descriptors.count() == 1

    def test_get_age_rating_by_id(self):
        rating = AgeRatingFactory()
        result = get_age_rating_by_id(rating_id=rating.id)
        assert result.id == rating.id


@pytest.mark.django_db
class TestGameSelectors:
    def test_get_games_returns_all(self):
        GameFactory.create_batch(3)
        assert get_games().count() == 3

    def test_get_games_ordered_by_release_date_desc(self):
        from datetime import date

        g1 = GameFactory(release_date=date(2024, 1, 1), title="Old Game")
        g2 = GameFactory(release_date=date(2025, 6, 1), title="New Game")
        result = list(get_games().values_list("title", flat=True))
        assert result[0] == "New Game"
        assert result[1] == "Old Game"

    def test_get_game_by_id_with_full_prefetch(self):
        dev = DeveloperFactory()
        genre = GenreFactory()
        game = GameFactory(developers=[dev], genres=[genre])
        result = get_game_by_id(game_id=game.id)
        assert result.id == game.id
        assert result.developers.count() == 1
        assert result.genres.count() == 1

    def test_get_game_by_id_not_found(self):
        import uuid

        with pytest.raises(Http404):
            get_game_by_id(game_id=uuid.uuid4())

    def test_get_games_for_user_via_developer_membership(self):
        user = make_developer_user()
        dev = DeveloperFactory()
        DeveloperMembershipFactory(user=user, developer=dev)
        game = GameFactory(developers=[dev])
        GameFactory()  # unrelated game

        result = get_games_for_user(user=user)
        assert result.count() == 1
        assert result.first().id == game.id

    def test_get_games_for_user_via_publisher_membership(self):
        user = UserFactory()
        pub = PublisherFactory()
        PublisherMembershipFactory(user=user, publisher=pub)
        game = GameFactory(publishers=[pub])

        result = get_games_for_user(user=user)
        assert result.count() == 1
        assert result.first().id == game.id

    def test_get_games_for_user_no_duplicates(self):
        """User linked via both dev and publisher to same game gets it once."""
        user = UserFactory()
        dev = DeveloperFactory()
        pub = PublisherFactory()
        DeveloperMembershipFactory(user=user, developer=dev)
        PublisherMembershipFactory(user=user, publisher=pub)
        GameFactory(developers=[dev], publishers=[pub])

        result = get_games_for_user(user=user)
        assert result.count() == 1

    def test_get_game_related_content(self):
        base = GameFactory()
        dlc = GameFactory(
            game_type="dlc", base_game=base, title="DLC 1"
        )
        GameFactory()  # unrelated

        result = get_game_related_content(game_id=base.id)
        assert result.count() == 1
        assert result.first().id == dlc.id

    def test_get_game_related_content_excludes_inactive(self):
        base = GameFactory()
        GameFactory(game_type="dlc", base_game=base, is_active=False)

        result = get_game_related_content(game_id=base.id)
        assert result.count() == 0


@pytest.mark.django_db
class TestGameChildSelectors:
    def test_get_game_system_requirements(self):
        game = GameFactory()
        SystemRequirementFactory(game=game)
        SystemRequirementFactory(game=game, tier="recommended")

        result = get_game_system_requirements(game_id=game.id)
        assert result.count() == 2

    def test_get_game_media(self):
        game = GameFactory()
        GameMediaFactory(game=game, order=1)
        GameMediaFactory(game=game, order=0)

        result = list(get_game_media(game_id=game.id))
        assert result[0].order == 0
        assert result[1].order == 1

    def test_get_game_language_support(self):
        game = GameFactory()
        GameLanguageSupportFactory(game=game)

        result = get_game_language_support(game_id=game.id)
        assert result.count() == 1


@pytest.mark.django_db
class TestBundleSelectors:
    def test_get_bundles(self):
        BundleFactory.create_batch(2)
        assert get_bundles().count() == 2

    def test_get_bundle_by_id_with_items(self):
        bundle = BundleFactory()
        BundleItemFactory(bundle=bundle)
        BundleItemFactory(bundle=bundle)

        result = get_bundle_by_id(bundle_id=bundle.id)
        assert result.id == bundle.id
        assert result.bundleitem_set.count() == 2
