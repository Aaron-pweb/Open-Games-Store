from django.contrib import admin

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


# ── Inlines (used inside GameAdmin) ──────────────────────────────────


class GameLanguageSupportInline(admin.TabularInline):
    model = GameLanguageSupport
    extra = 1


class SystemRequirementInline(admin.TabularInline):
    model = SystemRequirement
    extra = 1


class GameMediaInline(admin.TabularInline):
    model = GameMedia
    extra = 1


class BundleItemInline(admin.TabularInline):
    model = BundleItem
    extra = 1


# ── Leaf model admins ────────────────────────────────────────────────


@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "country", "verified", "created_at")
    list_filter = ("verified", "country")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "revenue_share_percent", "created_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(DeveloperMembership)
class DeveloperMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "developer", "role", "created_at")
    list_filter = ("role",)
    raw_id_fields = ("user", "developer")


@admin.register(PublisherMembership)
class PublisherMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "publisher", "role", "created_at")
    list_filter = ("role",)
    raw_id_fields = ("user", "publisher")


@admin.register(Franchise)
class FranchiseAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_approved")
    list_filter = ("is_approved",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("name", "icon_key")
    search_fields = ("name",)


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("name", "code")


@admin.register(AgeRatingBoard)
class AgeRatingBoardAdmin(admin.ModelAdmin):
    list_display = ("name", "region")
    search_fields = ("name",)


@admin.register(ContentDescriptor)
class ContentDescriptorAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(AgeRating)
class AgeRatingAdmin(admin.ModelAdmin):
    list_display = ("board", "value")
    list_filter = ("board",)


# ── Game admin ───────────────────────────────────────────────────────


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("title", "game_type", "release_status", "release_date", "is_active")
    list_filter = ("game_type", "release_status", "is_active")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = (
        "developers",
        "publishers",
        "genres",
        "tags",
        "features",
        "platforms",
    )
    raw_id_fields = ("base_game", "franchise", "age_rating")
    inlines = [GameLanguageSupportInline, SystemRequirementInline, GameMediaInline]


# ── Bundle admin ─────────────────────────────────────────────────────


@admin.register(Bundle)
class BundleAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "starts_at", "ends_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [BundleItemInline]
