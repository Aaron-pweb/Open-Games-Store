from django.db import models

# Create your models here.
# apps/games/models.py
import uuid
from django.db import models


class TimeStampedUUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Developer(TimeStampedUUIDModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    website = models.URLField(blank=True)
    country = models.CharField(max_length=2, blank=True)
    verified = models.BooleanField(default=False)   

    def __str__(self):
        return self.name


class Publisher(TimeStampedUUIDModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    website = models.URLField(blank=True)
    revenue_share_percent = models.DecimalField(max_digits=5, decimal_places=2, default=70.00)

    def __str__(self):
        return self.name


class Franchise(TimeStampedUUIDModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)


class Genre(TimeStampedUUIDModel):
    """Curated, small, controlled vocabulary — Action, RPG, Strategy. Admin-managed."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)


class Tag(TimeStampedUUIDModel):
    """Folksonomy-style discovery tags (Steam-style). Can be community-suggested → needs moderation."""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    is_approved = models.BooleanField(default=True)


class Feature(TimeStampedUUIDModel):
    """Not a genre, not a vibe-tag — a factual capability: Single-player,
    Co-op, Achievements, Cloud Saves, Controller Support, VR Support."""
    name = models.CharField(max_length=100, unique=True)
    icon_key = models.CharField(max_length=100, blank=True)


class Platform(TimeStampedUUIDModel):
    class OS(models.TextChoices):
        WINDOWS = "windows", "Windows"
        MAC = "mac", "macOS"
        LINUX = "linux", "Linux"

    name = models.CharField(max_length=20, choices=OS.choices, unique=True)


class Language(TimeStampedUUIDModel):
    code = models.CharField(max_length=10, unique=True)  # ISO 639-1
    name = models.CharField(max_length=100)


class AgeRatingBoard(TimeStampedUUIDModel):
    """ESRB, PEGI, USK, CERO — these differ per region, don't hardcode one scale."""
    name = models.CharField(max_length=50, unique=True)
    region = models.CharField(max_length=100)


class ContentDescriptor(TimeStampedUUIDModel):
    """Violence, Gambling, Nudity, Drug Use — attached to a rating, not the game directly."""
    name = models.CharField(max_length=100, unique=True)


class AgeRating(TimeStampedUUIDModel):
    board = models.ForeignKey(AgeRatingBoard, on_delete=models.PROTECT, related_name="ratings")
    value = models.CharField(max_length=20)  # "M", "18", "PEGI 16"
    descriptors = models.ManyToManyField(ContentDescriptor, blank=True)


class Game(TimeStampedUUIDModel):
    class GameType(models.TextChoices):
        BASE_GAME = "base_game", "Base Game"
        DLC = "dlc", "DLC / Add-on"
        EXPANSION = "expansion", "Expansion"
        SOUNDTRACK = "soundtrack", "Soundtrack"
        DEMO = "demo", "Demo"

    class ReleaseStatus(models.TextChoices):
        ANNOUNCED = "announced", "Announced"
        COMING_SOON = "coming_soon", "Coming Soon"
        EARLY_ACCESS = "early_access", "Early Access"
        RELEASED = "released", "Released"
        DELISTED = "delisted", "Delisted"

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)

    game_type = models.CharField(max_length=20, choices=GameType.choices, default=GameType.BASE_GAME)
    base_game = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE,
        related_name="related_content",
        help_text="Set for DLC/expansions/soundtracks; null for standalone base games.",
    )

    developers = models.ManyToManyField(Developer, related_name="games")
    publishers = models.ManyToManyField(Publisher, related_name="games")
    franchise = models.ForeignKey(Franchise, null=True, blank=True, on_delete=models.SET_NULL, related_name="games")

    short_description = models.CharField(max_length=500)
    description = models.TextField()

    genres = models.ManyToManyField(Genre, related_name="games")
    tags = models.ManyToManyField(Tag, blank=True, related_name="games")
    features = models.ManyToManyField(Feature, blank=True, related_name="games")
    platforms = models.ManyToManyField(Platform, related_name="games")
    languages = models.ManyToManyField(Language, through="GameLanguageSupport", related_name="games")

    age_rating = models.ForeignKey(AgeRating, null=True, blank=True, on_delete=models.SET_NULL)

    release_status = models.CharField(max_length=20, choices=ReleaseStatus.choices, default=ReleaseStatus.ANNOUNCED)
    release_date = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)  # soft-delete / delist — never hard delete

    class Meta:
        indexes = [models.Index(fields=["slug"]), models.Index(fields=["release_status"])]

    def __str__(self):
        return self.title


class GameLanguageSupport(TimeStampedUUIDModel):
    """A language can support interface text without audio, or audio without subtitles — track separately."""
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    interface = models.BooleanField(default=False)
    audio = models.BooleanField(default=False)
    subtitles = models.BooleanField(default=False)

    class Meta:
        unique_together = ("game", "language")


class SystemRequirement(TimeStampedUUIDModel):
    class Tier(models.TextChoices):
        MINIMUM = "minimum", "Minimum"
        RECOMMENDED = "recommended", "Recommended"

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="system_requirements")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    tier = models.CharField(max_length=20, choices=Tier.choices)
    os_version = models.CharField(max_length=255, blank=True)
    cpu = models.CharField(max_length=255, blank=True)
    gpu = models.CharField(max_length=255, blank=True)
    ram_gb = models.PositiveSmallIntegerField(null=True, blank=True)
    storage_gb = models.PositiveSmallIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("game", "platform", "tier")


class GameMedia(TimeStampedUUIDModel):
    class MediaType(models.TextChoices):
        SCREENSHOT = "screenshot", "Screenshot"
        TRAILER = "trailer", "Trailer"
        ARTWORK = "artwork", "Artwork"
        HEADER = "header", "Header / Banner"

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="media")
    media_type = models.CharField(max_length=20, choices=MediaType.choices)
    url = models.URLField()  # object storage (S3/R2/MinIO) URL — keep the DB light
    thumbnail_url = models.URLField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]


class Bundle(TimeStampedUUIDModel):
    """Also where you model 'Deluxe/GOTY Editions' — an edition is really just
    base game + selected DLC packaged at one price, not a separate game type."""
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    games = models.ManyToManyField(Game, through="BundleItem", related_name="bundles")
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)


class BundleItem(TimeStampedUUIDModel):
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("bundle", "game")