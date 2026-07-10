import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import TimeStampedUUIDModel


class Role(TimeStampedUUIDModel):
    """
    System-wide roles. Seeded via data migration:
    admin, owner, developer, end_user.

    A user can hold multiple roles simultaneously (M2M).
    """

    class RoleType(models.TextChoices):
        ADMIN = "admin", "Admin"
        OWNER = "owner", "Owner"
        DEVELOPER = "developer", "Developer"
        END_USER = "end_user", "End User"

    name = models.CharField(
        max_length=20, choices=RoleType.choices, unique=True
    )
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.get_name_display()


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    roles = models.ManyToManyField(Role, blank=True, related_name="users")

    def __str__(self):
        return self.username

    # ── Helper properties for permission checks ──────────────────────

    @property
    def is_admin_role(self) -> bool:
        """True if the user holds the 'admin' role."""
        return self.roles.filter(name=Role.RoleType.ADMIN).exists()

    @property
    def is_owner_role(self) -> bool:
        """True if the user holds the 'owner' role."""
        return self.roles.filter(name=Role.RoleType.OWNER).exists()

    @property
    def is_developer_role(self) -> bool:
        """True if the user holds the 'developer' role."""
        return self.roles.filter(name=Role.RoleType.DEVELOPER).exists()

    @property
    def is_end_user_role(self) -> bool:
        """True if the user holds the 'end_user' role."""
        return self.roles.filter(name=Role.RoleType.END_USER).exists()

    def has_game_access(self, game) -> bool:
        """
        Returns True if this user is an admin, OR owns the game
        through a Developer or Publisher membership.

        Ownership is determined by:
        1. The user has a DeveloperMembership linking them to a Developer
           that is in game.developers.
        2. The user has a PublisherMembership linking them to a Publisher
           that is in game.publishers.
        """
        if self.is_admin_role:
            return True

        # Check Developer membership path
        user_developer_ids = self.developer_memberships.values_list(
            "developer_id", flat=True
        )
        if game.developers.filter(id__in=user_developer_ids).exists():
            return True

        # Check Publisher membership path
        user_publisher_ids = self.publisher_memberships.values_list(
            "publisher_id", flat=True
        )
        if game.publishers.filter(id__in=user_publisher_ids).exists():
            return True

        return False
