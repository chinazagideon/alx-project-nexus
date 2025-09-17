from django.db import models
from django.core.validators import FileExtensionValidator, ValidationError
from user.models import User

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

# Create your models here.
class Upload(models.Model):
    """
    Upload model for the job portal
    """

    file_path = models.FileField(
        upload_to="uploads/", null=False, blank=False, validators=[validate_file_size]
    )
    name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "pdf",
                    "doc",
                    "docx",
                    "txt",
                    "csv",
                    "xls",
                    "xlsx",
                    "ppt",
                    "pptx",
                ]
            )
        ],
    )
    thumbnail = models.ImageField(
        upload_to="thumbnails/", null=True, blank=True, validators=[validate_file_size]
    )
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    type = models.CharField(choices=UploadType.choices, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self

    
