from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone

from job_portal.settings import AUTH_USER_MODEL


# Promotion type choices
class PromotionType(models.TextChoices):
    """
    Promotion type choices
    """

    JOB = "job", "Job"
    TALENT = "talent", "Talent"
    COMPANY = "company", "Company"
    PORTFOLIO = "portfolio", "Portfolio"

# Promotion placement choices
class PromotionPlacement(models.TextChoices):
    """
    Promotion placement choices
    """

    FEED = "feed", "Feed"
    HOMEPAGE = "homepage", "Homepage"
    LIST = "list", "List"


# Promotion status choices
class PromotionStatus(models.TextChoices):
    """
    Promotion status choices
    """

    PENDING = "pending", "Pending"
    ACTIVE = "active", "Active"
    EXPIRED = "expired", "Expired"
    CANCELLED = "cancelled", "Cancelled"


# Promotion package model
class PromotionPackage(models.Model):
    """
    Promotion package model
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration_days = models.PositiveIntegerField(default=7)
    priority_weight = models.PositiveIntegerField(default=1)
    placement = models.CharField(
        max_length=20,
        choices=PromotionPlacement.choices,
        default=PromotionPlacement.LIST,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta class for the promotion package model
        """

        ordering = ["-priority_weight", "name"]

    def __str__(self) -> str:
        """
        String representation of the promotion package model
        """
        return f"{self.name} ({self.placement})"


# Promotion query set
class PromotionQuerySet(models.QuerySet):
    """
    Query set for the promotion package model
    """

    def active(self, now=None):
        """
        Active promotions
        """
        current_time = now or timezone.now()
        return self.filter(
            status=PromotionStatus.ACTIVE,
            start_at__lte=current_time,
            end_at__gte=current_time,
        )

    def for_jobs(self):
        """
        Promotions for jobs
        """
        return self.filter(type=PromotionType.JOB)

    def for_talents(self):
        """
        Promotions for talents
        """
        return self.filter(type=PromotionType.TALENT)

    def visible(self, now=None):
        return self.active(now=now)



# Promotion model
class Promotion(models.Model):
    """
    Promotion model
    """

    # Owner of promotion
    owner = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="promotions",
    )

    # Generic target to promote (Job, User profile, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    # Type of promotion (Job, Talent)
    type = models.CharField(max_length=20, choices=PromotionType.choices)

    # Package of promotion
    package = models.ForeignKey(
        PromotionPackage,
        on_delete=models.PROTECT,
        related_name="promotions",
    )

    # Placement of promotion
    placement = models.CharField(
        max_length=20,
        choices=PromotionPlacement.choices,
        default=PromotionPlacement.LIST,
    )

    # Start date of promotion
    start_at = models.DateTimeField()
    # End date of promotion
    end_at = models.DateTimeField()

    # Status of promotion
    status = models.CharField(
        max_length=20,
        choices=PromotionStatus.choices,
        default=PromotionStatus.PENDING,
    )

    # Payment reference of promotion
    payment_reference = models.CharField(max_length=100, blank=True, null=True)

    # Approved by of promotion
    approved_by = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_promotions",
    )

    # Created at of promotion
    created_at = models.DateTimeField(auto_now_add=True)
    # Updated at of promotion
    updated_at = models.DateTimeField(auto_now=True)

    # Objects manager for the promotion model
    objects = PromotionQuerySet.as_manager()

    class Meta:
        """
        Meta class for the promotion model
        """

        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["type", "status"]),
            models.Index(fields=["start_at", "end_at"]),
        ]
        constraints = [
            # Only one ACTIVE promotion per object at a time
            models.UniqueConstraint(
                fields=["content_type", "object_id", "status"],
                condition=models.Q(status=PromotionStatus.ACTIVE),
                name="unique_active_promotion_per_object",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """
        String representation of the promotion model
        """
        return f"Promotion[{self.id}] {self.type} -> {self.content_type.app_label}.{self.content_type.model}:{self.object_id}"

    def activate(self, when=None):
        """
        Activate the promotion
        """
        self.status = PromotionStatus.ACTIVE
        if not self.start_at:
            self.start_at = when or timezone.now()
        if not self.end_at:
            self.end_at = self.start_at
        self.save(update_fields=["status", "start_at", "end_at", "updated_at"])

    def expire(self):
        """
        Expire the promotion
        """
        self.status = PromotionStatus.EXPIRED
        self.save(update_fields=["status", "updated_at"])

# Decorator to register promotable models
def register_promotable(promotion_type, app_label, model_name):
    """Decorator to register promotable models"""

    def decorator(model_class):
        if not hasattr(model_class, "_promotion_types"):
            model_class._promotion_types = set()
        model_class._promotion_types.add((promotion_type, app_label, model_name))
        return model_class

    return decorator
