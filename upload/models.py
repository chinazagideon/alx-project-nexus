from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import FileExtensionValidator, ValidationError
from django.conf import settings


def validate_file_size(value):
    """
    Validate the file size
    """
    if value.size > 1024 * 1024 * 5:
        raise ValidationError("File size must be less than 5MB")


class UploadType(models.TextChoices):
    """
    Upload type for the job portal
    """
    RESUME = 'resume', 'Resume'
    COVER_LETTER = 'cover_letter', 'Cover Letter'
    PROFILE_PICTURE = 'profile_picture', 'Profile Picture'
    PROFILE_COVER = 'profile_cover', 'Profile Cover'
    CERTIFICATE = 'certificate', 'Certificate'
    KYC = 'kyc', 'KYC'

# Create your models here.
class Upload(models.Model):
    """
    Upload model for the job portal
    """

    # File path of the upload
    file_path = models.FileField(
        upload_to="public/uploads/", null=False, blank=False, validators=[validate_file_size]
    )
    # Name of the upload
    name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
    )
    # Thumbnail of the upload
    thumbnail = models.ImageField(
        upload_to="public/thumbnails/", null=True, blank=True, validators=[validate_file_size]
    )

    # User that uploaded the upload
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, blank=False, related_name="uploads")

    # Generic target uploaded to (Job, User profile, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # Object ID of the upload
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    # Type of upload (Resume, Cover Letter, Profile Picture, Profile Cover, Certificate, KYC)
    type = models.CharField(choices=UploadType.choices, null=False, blank=False)
    # Created at of the upload
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        String representation of the upload model
        """
        return f"{self.name} ({self.type})"

    
