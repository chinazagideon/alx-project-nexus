from enum import Enum

class NotificationChannel(Enum):
    """
    Notification channel
    """
    IN_APP = "in_app"
    EMAIL = "email"
    PUSH = "push"


class CustomMessage(Enum):
    """
    Message
    """

    # Custom messages

    JOB_POSTED_TXT = "Job {job_title} was posted by {company_name}"
    JOB_CREATED_TXT = "Job {job_title} was created by {company_name}"
    COMPANY_CREATED_TXT = "Company {company_name} was created"
    PROMOTION_ACTIVE_TXT = "Promotion {promotion_name} is now active"
