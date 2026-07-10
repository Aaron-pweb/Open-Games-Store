"""
URL routing for apps.games API v1.

All endpoints are mounted under /api/v1/games/ via config/api_router.py.
"""

from rest_framework.routers import DefaultRouter

from apps.games.api.v1.views import (
    AgeRatingBoardViewSet,
    AgeRatingViewSet,
    BundleViewSet,
    ContentDescriptorViewSet,
    DeveloperViewSet,
    FeatureViewSet,
    FranchiseViewSet,
    GameLanguageSupportViewSet,
    GameMediaViewSet,
    GameViewSet,
    GenreViewSet,
    LanguageViewSet,
    PlatformViewSet,
    PublisherViewSet,
    SystemRequirementViewSet,
    TagViewSet,
)

router = DefaultRouter()

# Main game catalog
router.register("games", GameViewSet, basename="game")

# Catalog reference models
router.register("developers", DeveloperViewSet, basename="developer")
router.register("publishers", PublisherViewSet, basename="publisher")
router.register("franchises", FranchiseViewSet, basename="franchise")
router.register("genres", GenreViewSet, basename="genre")
router.register("tags", TagViewSet, basename="tag")
router.register("features", FeatureViewSet, basename="feature")
router.register("platforms", PlatformViewSet, basename="platform")
router.register("languages", LanguageViewSet, basename="language")

# Age rating system
router.register("age-rating-boards", AgeRatingBoardViewSet, basename="age-rating-board")
router.register("content-descriptors", ContentDescriptorViewSet, basename="content-descriptor")
router.register("age-ratings", AgeRatingViewSet, basename="age-rating")

# Game child objects
router.register("system-requirements", SystemRequirementViewSet, basename="system-requirement")
router.register("game-media", GameMediaViewSet, basename="game-media")
router.register("language-support", GameLanguageSupportViewSet, basename="language-support")

# Bundles and editions
router.register("bundles", BundleViewSet, basename="bundle")

urlpatterns = router.urls
