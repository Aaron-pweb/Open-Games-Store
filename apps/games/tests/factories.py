"""
Factory-boy factories for apps.games tests.

Every model gets a factory with realistic defaults. M2M relations
use post_generation hooks. All factories inherit lazy_attribute or
Faker providers for slug/URL generation.
"""

import factory
from factory.django import DjangoModelFactory

from apps.accounts.models import Role, User
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


# ── Account factories ────────────────────────────────────────────────


class RoleFactory(DjangoModelFactory):
    class Meta:
        model = Role
        django_get_or_create = ("name",)

    name = Role.RoleType.END_USER
    description = factory.LazyAttribute(lambda o: f"Role: {o.name}")


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")

    @factory.post_generation
    def roles(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for role in extracted:
                self.roles.add(role)


def make_admin_user(**kwargs):
    """Convenience: create a user with the 'admin' role."""
    admin_role = RoleFactory(name=Role.RoleType.ADMIN)
    user = UserFactory(**kwargs)
    user.roles.add(admin_role)
    return user


def make_developer_user(**kwargs):
    """Convenience: create a user with the 'developer' role."""
    dev_role = RoleFactory(name=Role.RoleType.DEVELOPER)
    user = UserFactory(**kwargs)
    user.roles.add(dev_role)
    return user


def make_owner_user(**kwargs):
    """Convenience: create a user with the 'owner' role."""
    owner_role = RoleFactory(name=Role.RoleType.OWNER)
    user = UserFactory(**kwargs)
    user.roles.add(owner_role)
    return user


def make_end_user(**kwargs):
    """Convenience: create a user with the 'end_user' role."""
    end_user_role = RoleFactory(name=Role.RoleType.END_USER)
    user = UserFactory(**kwargs)
    user.roles.add(end_user_role)
    return user


# ── Leaf model factories ─────────────────────────────────────────────


class DeveloperFactory(DjangoModelFactory):
    class Meta:
        model = Developer

    name = factory.Sequence(lambda n: f"Developer Studio {n}")
    slug = factory.Sequence(lambda n: f"developer-studio-{n}")
    website = factory.LazyAttribute(lambda o: f"https://{o.slug}.example.com")
    country = "US"
    verified = True


class PublisherFactory(DjangoModelFactory):
    class Meta:
        model = Publisher

    name = factory.Sequence(lambda n: f"Publisher Corp {n}")
    slug = factory.Sequence(lambda n: f"publisher-corp-{n}")
    website = factory.LazyAttribute(lambda o: f"https://{o.slug}.example.com")
    revenue_share_percent = factory.LazyFunction(lambda: 70.00)


class FranchiseFactory(DjangoModelFactory):
    class Meta:
        model = Franchise

    name = factory.Sequence(lambda n: f"Franchise {n}")
    slug = factory.Sequence(lambda n: f"franchise-{n}")


class GenreFactory(DjangoModelFactory):
    class Meta:
        model = Genre

    name = factory.Sequence(lambda n: f"Genre {n}")
    slug = factory.Sequence(lambda n: f"genre-{n}")


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: f"Tag {n}")
    slug = factory.Sequence(lambda n: f"tag-{n}")
    is_approved = True


class FeatureFactory(DjangoModelFactory):
    class Meta:
        model = Feature

    name = factory.Sequence(lambda n: f"Feature {n}")
    icon_key = factory.Sequence(lambda n: f"icon-{n}")


class PlatformFactory(DjangoModelFactory):
    class Meta:
        model = Platform
        django_get_or_create = ("name",)

    name = Platform.OS.WINDOWS


class LanguageFactory(DjangoModelFactory):
    class Meta:
        model = Language

    code = factory.Sequence(lambda n: f"l{n}")
    name = factory.Sequence(lambda n: f"Language {n}")


class AgeRatingBoardFactory(DjangoModelFactory):
    class Meta:
        model = AgeRatingBoard

    name = factory.Sequence(lambda n: f"Board {n}")
    region = "North America"


class ContentDescriptorFactory(DjangoModelFactory):
    class Meta:
        model = ContentDescriptor

    name = factory.Sequence(lambda n: f"Descriptor {n}")


class AgeRatingFactory(DjangoModelFactory):
    class Meta:
        model = AgeRating

    board = factory.SubFactory(AgeRatingBoardFactory)
    value = "M"

    @factory.post_generation
    def descriptors(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for descriptor in extracted:
                self.descriptors.add(descriptor)


# ── Membership factories ─────────────────────────────────────────────


class DeveloperMembershipFactory(DjangoModelFactory):
    class Meta:
        model = DeveloperMembership

    user = factory.SubFactory(UserFactory)
    developer = factory.SubFactory(DeveloperFactory)
    role = DeveloperMembership.MemberRole.MEMBER


class PublisherMembershipFactory(DjangoModelFactory):
    class Meta:
        model = PublisherMembership

    user = factory.SubFactory(UserFactory)
    publisher = factory.SubFactory(PublisherFactory)
    role = PublisherMembership.MemberRole.MEMBER


# ── Game factory ─────────────────────────────────────────────────────


class GameFactory(DjangoModelFactory):
    class Meta:
        model = Game

    title = factory.Sequence(lambda n: f"Game Title {n}")
    slug = factory.Sequence(lambda n: f"game-title-{n}")
    game_type = Game.GameType.BASE_GAME
    short_description = factory.LazyAttribute(
        lambda o: f"A short description for {o.title}."
    )
    description = factory.LazyAttribute(
        lambda o: f"A detailed description for {o.title}. Lots of content here."
    )
    release_status = Game.ReleaseStatus.RELEASED
    release_date = factory.LazyFunction(lambda: None)
    is_active = True

    @factory.post_generation
    def developers(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for dev in extracted:
                self.developers.add(dev)

    @factory.post_generation
    def publishers(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for pub in extracted:
                self.publishers.add(pub)

    @factory.post_generation
    def genres(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for genre in extracted:
                self.genres.add(genre)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for tag in extracted:
                self.tags.add(tag)

    @factory.post_generation
    def features(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for feature in extracted:
                self.features.add(feature)

    @factory.post_generation
    def platforms(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for platform in extracted:
                self.platforms.add(platform)


# ── Game child object factories ──────────────────────────────────────


class GameLanguageSupportFactory(DjangoModelFactory):
    class Meta:
        model = GameLanguageSupport

    game = factory.SubFactory(GameFactory)
    language = factory.SubFactory(LanguageFactory)
    interface = True
    audio = False
    subtitles = True


class SystemRequirementFactory(DjangoModelFactory):
    class Meta:
        model = SystemRequirement

    game = factory.SubFactory(GameFactory)
    platform = factory.SubFactory(PlatformFactory)
    tier = SystemRequirement.Tier.MINIMUM
    os_version = "Windows 10"
    cpu = "Intel i5"
    gpu = "NVIDIA GTX 1060"
    ram_gb = 8
    storage_gb = 50


class GameMediaFactory(DjangoModelFactory):
    class Meta:
        model = GameMedia

    game = factory.SubFactory(GameFactory)
    media_type = GameMedia.MediaType.SCREENSHOT
    url = factory.Sequence(lambda n: f"https://cdn.example.com/media/{n}.jpg")
    thumbnail_url = factory.Sequence(
        lambda n: f"https://cdn.example.com/media/{n}_thumb.jpg"
    )
    order = factory.Sequence(lambda n: n)


# ── Bundle factories ─────────────────────────────────────────────────


class BundleFactory(DjangoModelFactory):
    class Meta:
        model = Bundle

    name = factory.Sequence(lambda n: f"Bundle {n}")
    slug = factory.Sequence(lambda n: f"bundle-{n}")
    description = "A great bundle deal."
    is_active = True


class BundleItemFactory(DjangoModelFactory):
    class Meta:
        model = BundleItem

    bundle = factory.SubFactory(BundleFactory)
    game = factory.SubFactory(GameFactory)
