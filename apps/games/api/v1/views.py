"""
ViewSets for apps.games API v1.

Views are thin — they parse the request, check permissions,
call a selector or service, and serialize the result. All business
logic lives in services.py and selectors.py.
"""

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.games.models import GameLanguageSupport, GameMedia, SystemRequirement

from apps.core.permissions import (
    IsAdminRole,
    IsDeveloperOrAdmin,
    IsEndUserOrAbove,
    IsOwnerOrAdmin,
)
from apps.games.api.v1.filters import BundleFilterSet, GameFilterSet
from apps.games.api.v1.serializers import (
    AgeRatingBoardSerializer,
    AgeRatingSerializer,
    BundleSerializer,
    BundleWriteSerializer,
    ContentDescriptorSerializer,
    DeveloperSerializer,
    FeatureSerializer,
    FranchiseSerializer,
    GameDetailSerializer,
    GameLanguageSupportSerializer,
    GameListSerializer,
    GameMediaSerializer,
    GameWriteSerializer,
    GenreSerializer,
    LanguageSerializer,
    PlatformSerializer,
    PublisherSerializer,
    SystemRequirementSerializer,
    TagSerializer,
)
from apps.games.selectors import (
    get_age_rating_boards,
    get_age_ratings,
    get_bundles,
    get_content_descriptors,
    get_developers,
    get_features,
    get_franchises,
    get_game_by_id,
    get_game_language_support,
    get_game_media,
    get_game_related_content,
    get_game_system_requirements,
    get_games,
    get_games_for_user,
    get_genres,
    get_languages,
    get_platforms,
    get_publishers,
    get_tags,
)
from apps.games.services import (
    approve_tag,
    create_age_rating,
    create_age_rating_board,
    create_bundle,
    create_content_descriptor,
    create_developer,
    create_feature,
    create_franchise,
    create_game,
    create_game_language_support,
    create_game_media,
    create_genre,
    create_language,
    create_platform,
    create_publisher,
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
    update_game_language_support,
    update_game_media,
    update_genre,
    update_language,
    update_platform,
    update_publisher,
    update_system_requirement,
    update_tag,
)


# ── Helpers ──────────────────────────────────────────────────────────


def _validation_error_response(exc: DjangoValidationError) -> Response:
    """Convert Django ValidationError to DRF-style error response."""
    if hasattr(exc, "message_dict"):
        errors = [
            {"field": field, "message": msg}
            for field, messages in exc.message_dict.items()
            for msg in messages
        ]
    else:
        errors = [
            {"field": "non_field_errors", "message": str(msg)}
            for msg in exc.messages
        ]
    return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)


# ── Catalog reference model ViewSets (admin-write, public-read) ──────

class _AdminWriteViewSet(viewsets.ModelViewSet):
    """
    Base for catalog reference models: public read, admin-only write.
    Subclasses set serializer_class, override get_queryset(), and define
    _create_service / _update_service class attributes.
    """

    _create_service = None  # set in subclass: e.g. staticmethod(create_developer)
    _update_service = None  # set in subclass: e.g. staticmethod(update_developer)

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminRole()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            instance = self._create_service(**serializer.validated_data)
        except DjangoValidationError as exc:
            return _validation_error_response(exc)
        output = self.get_serializer(instance).data
        return Response(output, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            updated = self._update_service(
                instance=instance, data=serializer.validated_data
            )
        except DjangoValidationError as exc:
            return _validation_error_response(exc)
        output = self.get_serializer(updated).data
        return Response(output)


@extend_schema_view(
    list=extend_schema(tags=["Developers"]),
    retrieve=extend_schema(tags=["Developers"]),
    create=extend_schema(tags=["Developers"]),
    update=extend_schema(tags=["Developers"]),
    partial_update=extend_schema(tags=["Developers"]),
    destroy=extend_schema(tags=["Developers"]),
)
class DeveloperViewSet(_AdminWriteViewSet):
    serializer_class = DeveloperSerializer
    search_fields = ["name", "slug"]
    ordering_fields = ["name", "created_at"]
    _create_service = staticmethod(create_developer)
    _update_service = staticmethod(update_developer)

    def get_queryset(self):
        return get_developers()


@extend_schema_view(
    list=extend_schema(tags=["Publishers"]),
    retrieve=extend_schema(tags=["Publishers"]),
    create=extend_schema(tags=["Publishers"]),
    update=extend_schema(tags=["Publishers"]),
    partial_update=extend_schema(tags=["Publishers"]),
    destroy=extend_schema(tags=["Publishers"]),
)
class PublisherViewSet(_AdminWriteViewSet):
    serializer_class = PublisherSerializer
    search_fields = ["name", "slug"]
    ordering_fields = ["name", "created_at"]
    _create_service = staticmethod(create_publisher)
    _update_service = staticmethod(update_publisher)

    def get_queryset(self):
        return get_publishers()


@extend_schema_view(
    list=extend_schema(tags=["Franchises"]),
    retrieve=extend_schema(tags=["Franchises"]),
    create=extend_schema(tags=["Franchises"]),
    update=extend_schema(tags=["Franchises"]),
    partial_update=extend_schema(tags=["Franchises"]),
    destroy=extend_schema(tags=["Franchises"]),
)
class FranchiseViewSet(_AdminWriteViewSet):
    serializer_class = FranchiseSerializer
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]
    _create_service = staticmethod(create_franchise)
    _update_service = staticmethod(update_franchise)

    def get_queryset(self):
        return get_franchises()


@extend_schema_view(
    list=extend_schema(tags=["Genres"]),
    retrieve=extend_schema(tags=["Genres"]),
    create=extend_schema(tags=["Genres"]),
    update=extend_schema(tags=["Genres"]),
    partial_update=extend_schema(tags=["Genres"]),
    destroy=extend_schema(tags=["Genres"]),
)
class GenreViewSet(_AdminWriteViewSet):
    serializer_class = GenreSerializer
    search_fields = ["name"]
    ordering_fields = ["name"]
    _create_service = staticmethod(create_genre)
    _update_service = staticmethod(update_genre)

    def get_queryset(self):
        return get_genres()


@extend_schema_view(
    list=extend_schema(tags=["Features"]),
    retrieve=extend_schema(tags=["Features"]),
    create=extend_schema(tags=["Features"]),
    update=extend_schema(tags=["Features"]),
    partial_update=extend_schema(tags=["Features"]),
    destroy=extend_schema(tags=["Features"]),
)
class FeatureViewSet(_AdminWriteViewSet):
    serializer_class = FeatureSerializer
    search_fields = ["name"]
    ordering_fields = ["name"]
    _create_service = staticmethod(create_feature)
    _update_service = staticmethod(update_feature)

    def get_queryset(self):
        return get_features()


@extend_schema_view(
    list=extend_schema(tags=["Platforms"]),
    retrieve=extend_schema(tags=["Platforms"]),
    create=extend_schema(tags=["Platforms"]),
    update=extend_schema(tags=["Platforms"]),
    partial_update=extend_schema(tags=["Platforms"]),
    destroy=extend_schema(tags=["Platforms"]),
)
class PlatformViewSet(_AdminWriteViewSet):
    serializer_class = PlatformSerializer
    _create_service = staticmethod(create_platform)
    _update_service = staticmethod(update_platform)

    def get_queryset(self):
        return get_platforms()


@extend_schema_view(
    list=extend_schema(tags=["Languages"]),
    retrieve=extend_schema(tags=["Languages"]),
    create=extend_schema(tags=["Languages"]),
    update=extend_schema(tags=["Languages"]),
    partial_update=extend_schema(tags=["Languages"]),
    destroy=extend_schema(tags=["Languages"]),
)
class LanguageViewSet(_AdminWriteViewSet):
    serializer_class = LanguageSerializer
    search_fields = ["name", "code"]
    ordering_fields = ["name"]
    _create_service = staticmethod(create_language)
    _update_service = staticmethod(update_language)

    def get_queryset(self):
        return get_languages()


@extend_schema_view(
    list=extend_schema(tags=["Age Ratings"]),
    retrieve=extend_schema(tags=["Age Ratings"]),
    create=extend_schema(tags=["Age Ratings"]),
    update=extend_schema(tags=["Age Ratings"]),
    partial_update=extend_schema(tags=["Age Ratings"]),
    destroy=extend_schema(tags=["Age Ratings"]),
)
class AgeRatingBoardViewSet(_AdminWriteViewSet):
    serializer_class = AgeRatingBoardSerializer
    search_fields = ["name"]
    _create_service = staticmethod(create_age_rating_board)
    _update_service = staticmethod(update_age_rating_board)

    def get_queryset(self):
        return get_age_rating_boards()


@extend_schema_view(
    list=extend_schema(tags=["Age Ratings"]),
    retrieve=extend_schema(tags=["Age Ratings"]),
    create=extend_schema(tags=["Age Ratings"]),
    update=extend_schema(tags=["Age Ratings"]),
    partial_update=extend_schema(tags=["Age Ratings"]),
    destroy=extend_schema(tags=["Age Ratings"]),
)
class ContentDescriptorViewSet(_AdminWriteViewSet):
    serializer_class = ContentDescriptorSerializer
    search_fields = ["name"]
    _create_service = staticmethod(create_content_descriptor)
    _update_service = staticmethod(update_content_descriptor)

    def get_queryset(self):
        return get_content_descriptors()


@extend_schema_view(
    list=extend_schema(tags=["Age Ratings"]),
    retrieve=extend_schema(tags=["Age Ratings"]),
    create=extend_schema(tags=["Age Ratings"]),
    update=extend_schema(tags=["Age Ratings"]),
    partial_update=extend_schema(tags=["Age Ratings"]),
    destroy=extend_schema(tags=["Age Ratings"]),
)
class AgeRatingViewSet(_AdminWriteViewSet):
    serializer_class = AgeRatingSerializer
    _create_service = staticmethod(create_age_rating)
    _update_service = staticmethod(update_age_rating)

    def get_queryset(self):
        return get_age_ratings()


# ── Tag ViewSet (special: end-users can suggest) ─────────────────────


@extend_schema_view(
    list=extend_schema(tags=["Tags"]),
    retrieve=extend_schema(tags=["Tags"]),
    create=extend_schema(tags=["Tags"]),
    update=extend_schema(tags=["Tags"]),
    partial_update=extend_schema(tags=["Tags"]),
    destroy=extend_schema(tags=["Tags"]),
)
class TagViewSet(viewsets.ModelViewSet):
    """
    Tags: folksonomy-style discovery labels.

    Permissions:
    - GET: public (returns only approved tags by default)
    - POST: any authenticated user (auto is_approved=False for non-admins)
    - PUT/PATCH/DELETE: admin only
    - POST /{id}/approve/: admin only
    """

    serializer_class = TagSerializer
    search_fields = ["name"]
    ordering_fields = ["name"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        if self.action == "create":
            return [IsEndUserOrAbove()]
        return [IsAdminRole()]

    def get_queryset(self):
        # Non-admin users only see approved tags
        if (
            self.request.user.is_authenticated
            and self.request.user.is_admin_role
        ):
            return get_tags()
        return get_tags(is_approved=True)

    def perform_create(self, serializer):
        create_tag(
            **serializer.validated_data,
            created_by_user=self.request.user,
        )

    def perform_update(self, serializer):
        update_tag(instance=self.get_object(), data=serializer.validated_data)

    @extend_schema(tags=["Tags"], request=None, responses={200: TagSerializer})
    @action(detail=True, methods=["post"], permission_classes=[IsAdminRole])
    def approve(self, request, pk=None):
        """Admin action: approve a community-suggested tag."""
        tag = self.get_object()
        approve_tag(instance=tag)
        return Response(TagSerializer(tag).data)


# ── Game ViewSet ─────────────────────────────────────────────────────


@extend_schema_view(
    list=extend_schema(tags=["Games"]),
    retrieve=extend_schema(tags=["Games"]),
    create=extend_schema(tags=["Games"]),
    update=extend_schema(tags=["Games"]),
    partial_update=extend_schema(tags=["Games"]),
    destroy=extend_schema(tags=["Games"]),
)
class GameViewSet(viewsets.ModelViewSet):
    """
    Game catalog CRUD.

    Permissions:
    - GET: public (browse the catalog)
    - POST: developer/owner/admin (create new games)
    - PUT/PATCH: owner/admin (must own the game — object-level check)
    - DELETE: owner/admin (soft-delete — sets is_active=False)
    """

    filterset_class = GameFilterSet
    search_fields = ["title", "short_description"]
    ordering_fields = ["release_date", "title", "created_at"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        if self.action == "my_games":
            return [IsAuthenticated()]
        if self.action in (
            "related_content", "system_requirements",
            "game_media", "language_support",
        ):
            return [AllowAny()]
        if self.action == "create":
            return [IsDeveloperOrAdmin()]
        # update, partial_update, destroy
        return [IsOwnerOrAdmin()]

    def get_serializer_class(self):
        if self.action == "list":
            return GameListSerializer
        if self.action == "retrieve":
            return GameDetailSerializer
        return GameWriteSerializer

    def get_queryset(self):
        return get_games()

    def get_object(self):
        """Override to use the detail selector with full prefetching."""
        game_id = self.kwargs[self.lookup_field]
        obj = get_game_by_id(game_id=game_id)
        self.check_object_permissions(self.request, obj)
        return obj

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            game = create_game(**serializer.validated_data)
        except DjangoValidationError as exc:
            return _validation_error_response(exc)
        output = GameDetailSerializer(game).data
        return Response(output, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            game = update_game(instance=instance, data=serializer.validated_data)
        except DjangoValidationError as exc:
            return _validation_error_response(exc)
        output = GameDetailSerializer(game).data
        return Response(output)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        soft_delete_game(instance=instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ── Custom actions ──

    @extend_schema(tags=["Games"], responses={200: GameListSerializer(many=True)})
    @action(
        detail=False,
        methods=["get"],
        url_path="my-games",
        permission_classes=[IsAuthenticated],
    )
    def my_games(self, request):
        """List only games owned by the requesting user."""
        games = get_games_for_user(user=request.user)
        page = self.paginate_queryset(games)
        if page is not None:
            serializer = GameListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = GameListSerializer(games, many=True)
        return Response(serializer.data)

    @extend_schema(tags=["Games"], responses={200: GameListSerializer(many=True)})
    @action(detail=True, methods=["get"], url_path="related-content")
    def related_content(self, request, pk=None):
        """List DLC, expansions, soundtracks, and demos for this game."""
        qs = get_game_related_content(game_id=pk)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = GameListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = GameListSerializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=["Games"],
        responses={200: SystemRequirementSerializer(many=True)},
    )
    @action(detail=True, methods=["get"], url_path="system-requirements")
    def system_requirements(self, request, pk=None):
        """List system requirements for this game."""
        qs = get_game_system_requirements(game_id=pk)
        serializer = SystemRequirementSerializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=["Games"],
        responses={200: GameMediaSerializer(many=True)},
    )
    @action(detail=True, methods=["get"], url_path="media")
    def game_media(self, request, pk=None):
        """List media (screenshots, trailers, artwork) for this game."""
        qs = get_game_media(game_id=pk)
        serializer = GameMediaSerializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=["Games"],
        responses={200: GameLanguageSupportSerializer(many=True)},
    )
    @action(detail=True, methods=["get"], url_path="language-support")
    def language_support(self, request, pk=None):
        """List language support details for this game."""
        qs = get_game_language_support(game_id=pk)
        serializer = GameLanguageSupportSerializer(qs, many=True)
        return Response(serializer.data)


# ── Game child object ViewSets ───────────────────────────────────────


@extend_schema_view(
    list=extend_schema(tags=["System Requirements"]),
    retrieve=extend_schema(tags=["System Requirements"]),
    create=extend_schema(tags=["System Requirements"]),
    update=extend_schema(tags=["System Requirements"]),
    partial_update=extend_schema(tags=["System Requirements"]),
    destroy=extend_schema(tags=["System Requirements"]),
)
class SystemRequirementViewSet(viewsets.ModelViewSet):
    """System requirements CRUD. Ownership checked via parent game."""

    serializer_class = SystemRequirementSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsOwnerOrAdmin()]

    def get_queryset(self):
        return (
            SystemRequirement.objects
            .select_related("platform")
            .order_by("game_id", "platform__name", "tier")
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            obj = create_system_requirement(**serializer.validated_data)
        except DjangoValidationError as exc:
            return _validation_error_response(exc)
        output = SystemRequirementSerializer(obj).data
        return Response(output, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        update_system_requirement(
            instance=self.get_object(), data=serializer.validated_data
        )


@extend_schema_view(
    list=extend_schema(tags=["Game Media"]),
    retrieve=extend_schema(tags=["Game Media"]),
    create=extend_schema(tags=["Game Media"]),
    update=extend_schema(tags=["Game Media"]),
    partial_update=extend_schema(tags=["Game Media"]),
    destroy=extend_schema(tags=["Game Media"]),
)
class GameMediaViewSet(viewsets.ModelViewSet):
    """Game media CRUD. Ownership checked via parent game."""

    serializer_class = GameMediaSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsOwnerOrAdmin()]

    def get_queryset(self):
        return GameMedia.objects.order_by("game_id", "order")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            obj = create_game_media(**serializer.validated_data)
        except DjangoValidationError as exc:
            return _validation_error_response(exc)
        output = GameMediaSerializer(obj).data
        return Response(output, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        update_game_media(
            instance=self.get_object(), data=serializer.validated_data
        )


@extend_schema_view(
    list=extend_schema(tags=["Language Support"]),
    retrieve=extend_schema(tags=["Language Support"]),
    create=extend_schema(tags=["Language Support"]),
    update=extend_schema(tags=["Language Support"]),
    partial_update=extend_schema(tags=["Language Support"]),
    destroy=extend_schema(tags=["Language Support"]),
)
class GameLanguageSupportViewSet(viewsets.ModelViewSet):
    """Language support CRUD. Ownership checked via parent game."""

    serializer_class = GameLanguageSupportSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsOwnerOrAdmin()]

    def get_queryset(self):
        return (
            GameLanguageSupport.objects
            .select_related("language")
            .order_by("game_id", "language__name")
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            obj = create_game_language_support(**serializer.validated_data)
        except DjangoValidationError as exc:
            return _validation_error_response(exc)
        output = GameLanguageSupportSerializer(obj).data
        return Response(output, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        update_game_language_support(
            instance=self.get_object(), data=serializer.validated_data
        )


# ── Bundle ViewSet ───────────────────────────────────────────────────


@extend_schema_view(
    list=extend_schema(tags=["Bundles"]),
    retrieve=extend_schema(tags=["Bundles"]),
    create=extend_schema(tags=["Bundles"]),
    update=extend_schema(tags=["Bundles"]),
    partial_update=extend_schema(tags=["Bundles"]),
    destroy=extend_schema(tags=["Bundles"]),
)
class BundleViewSet(viewsets.ModelViewSet):
    """Bundles/editions. Admin-only write, public read."""

    filterset_class = BundleFilterSet
    search_fields = ["name"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminRole()]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return BundleWriteSerializer
        return BundleSerializer

    def get_queryset(self):
        return get_bundles()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            bundle = create_bundle(**serializer.validated_data)
        except DjangoValidationError as exc:
            return _validation_error_response(exc)
        output = BundleSerializer(bundle).data
        return Response(output, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            bundle = update_bundle(instance=instance, data=serializer.validated_data)
        except DjangoValidationError as exc:
            return _validation_error_response(exc)
        output = BundleSerializer(bundle).data
        return Response(output)
